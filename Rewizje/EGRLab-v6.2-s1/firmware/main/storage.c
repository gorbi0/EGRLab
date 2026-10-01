#include "storage.h"
#include <stdio.h>
#include <stdarg.h>
#include <string.h>
#include <inttypes.h>
#include <sys/stat.h>
#include <unistd.h>
#include <stdatomic.h>
#include "sdkconfig.h"
#include "esp_heap_caps.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "freertos/ringbuf.h"

/* Bufor zapisu 8 MiB w PSRAM: okolo 104,8 s przy 2 kS/s. To odpornosc na
 * zadlawienie karty, niezalezna od formatu pliku â€” v2 scielo go do 1 MiB
 * (16 s) przy okazji usuwania pretriggera, choc to dwie osobne decyzje.
 * Pretrigger nadal nie jest potrzebny: historia jest w ciaglym pliku. */
#define RING_BYTES (8 * 1024 * 1024)
#define RING_COUNT (RING_BYTES / sizeof(sample_t))
#define BLOCK_COUNT 64
/* Variable-length FIFO: short events do not reserve a full 2048-byte slot.
 * Only task-context callers are allowed; the payload lives in PSRAM. */
#define EVENT_BUFFER_BYTES (256 * 1024)

static sample_t *ring;
static volatile uint64_t head, tail;
static volatile bool healthy;
static atomic_uint lost_events, soft_drops;
/* 6.2-s1: pliki ma writer albo (po PFAIL_N) zadanie zamykajace - nigdy oba naraz. */
static SemaphoreHandle_t file_lock;
static volatile bool closing, closed, sink;
static portMUX_TYPE mux = portMUX_INITIALIZER_UNLOCKED;
static QueueHandle_t configurations;
static RingbufHandle_t events;
static StaticRingbuffer_t event_control; /* internal RAM, not PSRAM */
static uint8_t *event_storage;
static SemaphoreHandle_t config_ack;
static volatile bool config_written;
static uint32_t session_id, sample_rate, segment;
static uint64_t segment_bytes, event_bytes;
static unsigned event_segment;
#define SEGMENT_LIMIT (1024ULL*1024*1024)
#ifndef CONFIG_EGR_CAN_PRESENT
#define CONFIG_EGR_CAN_PRESENT 0
#endif
#if CONFIG_EGR_CAN_PRESENT   /* 6.2-s1 F-08: metadane sesji (P10 R2 docs/INTEGRACJA.md) */
#define CAN_META "{\"present\":true,\"bitrate\":500000,\"mode\":\"listen_only\",\"time_source\":\"rx_task_esp_timer_us\"," \
                 "\"profile\":\"obd2_m01_pid0c_sf_7e8_7ef\"}"
#else
#define CAN_META "{\"present\":false}"
#endif
static FILE *samples, *eventfile;
static char directory[96];
static uint32_t crc_table[256];

static void crc_init(void) {
    for (unsigned i = 0; i < 256; i++) {
        uint32_t c = i;
        for (unsigned j = 0; j < 8; j++) c = (c >> 1) ^ ((c & 1) ? 0xedb88320 : 0);
        crc_table[i] = c;
    }
}
uint32_t egr_crc32(const void *data, unsigned length) {
    const uint8_t *p = data; uint32_t c = 0xffffffff;
    for (unsigned i = 0; i < length; i++) c = crc_table[(c ^ p[i]) & 255] ^ (c >> 8);
    return c ^ 0xffffffff;
}
static void unhealthy(void) { portENTER_CRITICAL(&mux); healthy = false; portEXIT_CRITICAL(&mux); }
bool storage_ok(void) { portENTER_CRITICAL(&mux); bool h = healthy; portEXIT_CRITICAL(&mux); return h; }
uint32_t storage_lost_events(void) { return lost_events; }
uint32_t storage_soft_drops(void) { return soft_drops; }
bool storage_bench(void) { return sink; }

static bool header(FILE *f, uint32_t session, uint32_t rate) {
    struct __attribute__((packed)) {
        char magic[8]; uint16_t version, bytes;
        uint32_t rate, record, flags; uint64_t session;
    } h = {"EGRLOG1", 5, 32, rate, sizeof(sample_t), 0, session};
    return fwrite(&h, 1, sizeof h, f) == sizeof h;
}
static bool queues(void) {
    configurations=xQueueCreate(1, STORAGE_EVENT_MAX);
    config_ack=xSemaphoreCreateBinary(); file_lock=xSemaphoreCreateMutex();
    ring = heap_caps_malloc(RING_COUNT * sizeof(sample_t), MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    event_storage = heap_caps_malloc(EVENT_BUFFER_BYTES, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    if (event_storage) events = xRingbufferCreateStatic(EVENT_BUFFER_BYTES,
        RINGBUF_TYPE_NOSPLIT, event_storage, &event_control);
    return ring && events && configurations && config_ack && file_lock;
}
bool storage_init_bench(uint32_t rate) {
    crc_init(); sample_rate=rate; sink=true;
    if (!queues()) return false;
    healthy = true; return true;
}
bool storage_init(uint32_t session, uint32_t rate) {
    crc_init();
    session_id=session; sample_rate=rate;
    if (!queues()) return false;
    snprintf(directory, sizeof directory, "/sd/session_%" PRIu32, session);
    /* Istniejacej sesji nigdy nie nadpisujemy, nawet po przywroceniu NVS. */
    if (mkdir(directory, 0777) != 0) return false;
    char path[160];
    snprintf(path, sizeof path, "%s/samples_000.egr", directory); samples = fopen(path, "wb");
    snprintf(path, sizeof path, "%s/events_000.ndjson", directory); eventfile = fopen(path, "w");
    if (!samples || !eventfile || !header(samples, session, rate)) return false;
    segment_bytes=32;
    /* meta.json opisuje tylko sesje. Kalibracja, zakresy, bank i mapowanie
     * zyja w zdarzeniach `config`, bo moga sie zmieniac w trakcie. */
    snprintf(path, sizeof path, "%s/meta.json", directory);
    FILE *meta = fopen(path, "w");
    if (!meta) return false;
    fprintf(meta, "{\n\"schema\":5,\"firmware\":\"EGRLab-6.2-s1\",\"synthetic\":false,\"utc\":null,\n"
        "\"identity_source\":\"config events and session manifest\",\"record_bytes\":40,\n"
        "\"sample_rate\":%" PRIu32 ",\"session\":%" PRIu32 ",\"adc_spi_hz\":%d,\n"
        "\"hardware\":\"S1: P02 R4, P03 R6, P05 R3, P06 R2, P09 R2, P10 R2\",\n"
        "\"channels\":\"CH7 (indeks 6) = VBAT_SENSE: akumulator auta przez P02 R4, dzielnik 499k/100k na P05 R3; nie pakiet 4S\",\n"
        "\"power_fail\":{\"input\":\"GPIO3 PFAIL_N (P02 R4 -> P03 R6)\",\"event\":\"power_fail\",\"close_target_ms\":10},\n"
        "\"can\":%s,\n"
        "\"note\":\"Kalibracja i zakresy w events.ndjson jako zdarzenia config; "
        "kazdy rekord niesie config_id.\"}\n", rate, session, CONFIG_EGR_ADC_SPI_HZ,
        CAN_META);
    bool good = !ferror(meta);
    if (fclose(meta) != 0) good = false;
    healthy = good;
    return good;
}
void storage_push(const sample_t *s) {
    portENTER_CRITICAL(&mux);
    if (head - tail >= RING_COUNT) { healthy = false; portEXIT_CRITICAL(&mux); return; }
    ring[head % RING_COUNT] = *s;
    head++;
    portEXIT_CRITICAL(&mux);
}
bool storage_event_soft(const char *fmt, ...) {
    if (!events || closing) { soft_drops++; return false; }
    char line[STORAGE_EVENT_MAX];
    va_list args; va_start(args, fmt);
    int n = vsnprintf(line, sizeof line, fmt, args);
    va_end(args);
    if (n < 0 || n >= (int)sizeof line || xRingbufferSend(events, line, (size_t)n + 1, 0) != pdTRUE) {
        soft_drops++; return false;
    }
    return true;
}
bool storage_event(const char *fmt, ...) {
    if (!events) return false;
    char line[STORAGE_EVENT_MAX];
    va_list args; va_start(args, fmt);
    int n = vsnprintf(line, sizeof line, fmt, args);
    va_end(args);
    /* Obciecie dawaloby niepoprawna linie NDJSON, ktora czytnik odrzuci jako
     * uszkodzona â€” a zapis raportowalby zdrowie. Zglaszamy blad. */
    if (n < 0 || n >= (int)sizeof line) { lost_events++; unhealthy(); return false; }
    if (xRingbufferSend(events, line, (size_t)n + 1, 0) != pdTRUE) {
        lost_events++; unhealthy(); return false;
    }
    return true;
}
/* Only the command manager calls this, with acquisition acknowledged paused.
 * Writer fsyncs the configuration BEFORE the manager publishes its ID. */
bool storage_config(const session_config_t *c) {
    char line[STORAGE_EVENT_MAX];
    if (!storage_ok() || !json_config(line,sizeof line,c,esp_timer_get_time())) {
        unhealthy(); return false;
    }
    if (sink) return true;                       /* tryb stolowy: brak pliku, konfiguracja obowiazuje od razu */
    config_written=false;
    if (xQueueSend(configurations,line,pdMS_TO_TICKS(100))!=pdTRUE ||
        xSemaphoreTake(config_ack,pdMS_TO_TICKS(3000))!=pdTRUE || !config_written) {
        unhealthy(); return false;
    }
    return storage_ok();
}
static bool sync_file(FILE *f) { return fflush(f)==0 && fsync(fileno(f))==0; }
bool storage_power_fail(uint64_t edge_us, uint64_t stop_us) {
    if (sink || closed) return true;
    closing = true;                              /* writer: bez nowych blokow i zdarzen */
    /* Writer konczy biezacy blok (zwykle kilka ms). Po wylaczeniu napedu obciazenie P02 spada, wiec podtrzymanie
     * trwa dluzej niz 10 ms z karty P02 R4 dla 6 W; czekamy do 200 ms - po zaniku i tak nic nie tracimy. */
    if (!file_lock || xSemaphoreTake(file_lock, pdMS_TO_TICKS(200)) != pdTRUE) { unhealthy(); return false; }
    uint32_t pending = (uint32_t)(head - tail);
    bool ok = samples && sync_file(samples);
    if (samples && fclose(samples) != 0) ok = false;
    samples = NULL;
    if (eventfile) {
        if (fprintf(eventfile, "{\"type\":\"power_fail\",\"t_us\":%" PRIu64 ",\"stop_us\":%" PRIu64
                    ",\"source\":\"PFAIL_N\",\"reason\":\"UVLO\",\"samples_not_written\":%" PRIu32 "}\n",
                    edge_us, stop_us, pending) < 0) ok = false;
        if (!sync_file(eventfile)) ok = false;
        if (fclose(eventfile) != 0) ok = false;
        eventfile = NULL;
    } else ok = false;
    closed = true; unhealthy();
    xSemaphoreGive(file_lock);
    return ok;
}
static bool rotate(void) {
    if(!sync_file(samples) || fclose(samples)!=0) return false;
    char path[160]; snprintf(path,sizeof path,"%s/samples_%03" PRIu32 ".egr",directory,++segment);
    struct stat st; if(stat(path,&st)==0) return false;
    samples=fopen(path,"wb"); segment_bytes=32;
    return samples && header(samples,session_id,sample_rate);
}
static bool write_event(const char *line) {
    size_t bytes=strlen(line)+1;
    if(event_bytes+bytes>SEGMENT_LIMIT) {
        if(!sync_file(eventfile) || fclose(eventfile)!=0) return false;
        char path[160]; snprintf(path,sizeof path,"%s/events_%03u.ndjson",directory,++event_segment);
        struct stat st; if(stat(path,&st)==0) return false;
        eventfile=fopen(path,"w"); event_bytes=0;
        if(!eventfile) return false;
    }
    if(!eventfile || fprintf(eventfile,"%s\n",line)<0) return false;
    event_bytes+=bytes; return true;
}
/* Return every received item, including the SD error path. A bad length/NUL
 * must never allow write_event()/strlen() to read beyond the received item. */
static bool drain_events(unsigned limit) {
    for (unsigned n = 0; n < limit; n++) {
        size_t bytes = 0;
        char *item = xRingbufferReceive(events, &bytes, 0);
        if (!item) break;
        bool ok = bytes > 0 && bytes <= STORAGE_EVENT_MAX && item[bytes - 1] == 0;
        if (ok && !sink) ok = write_event(item);
        vRingbufferReturnItem(events, item);
        if (!ok) { unhealthy(); return false; }
    }
    return true;
}
void storage_mark(uint64_t t_us) {
    storage_event("{\"type\":\"mark\",\"t_us\":%" PRIu64 "}", t_us);
}
/* 6.2-s1: kazda operacja na plikach pod file_lock; po PFAIL_N (closing / closed) writer juz ich nie dotyka.
 * W trybie stolowym (sink) kolejki sa oprozniane bez zapisu. Zdarzenia: do 64 na obieg (ramki CAN, F-08). */
static void writer_stop(void) { xSemaphoreGive(file_lock); while (true) vTaskDelay(portMAX_DELAY); }
void storage_writer(void *arg) {
    (void)arg;
    static sample_t batch[BLOCK_COUNT];
    static char line[STORAGE_EVENT_MAX];
    while (true) {
        if (closing) { while (true) vTaskDelay(portMAX_DELAY); }
        xSemaphoreTake(file_lock, portMAX_DELAY);
        if (closing || closed) writer_stop();
        if(xQueueReceive(configurations,line,0)==pdTRUE) {
            config_written=sink || (write_event(line) && sync_file(eventfile));
            if(!config_written) unhealthy();
            xSemaphoreGive(config_ack);
            if(!config_written) writer_stop();
        }
        unsigned n = 0;
        static uint64_t last_batch;
        uint64_t batch_time=esp_timer_get_time();
        portENTER_CRITICAL(&mux);
        if(head-tail>=BLOCK_COUNT || batch_time-last_batch>=100000)
            while (n < BLOCK_COUNT && tail < head) batch[n++] = ring[tail++ % RING_COUNT];
        portEXIT_CRITICAL(&mux);
        if (n && !sink) {
            last_batch=batch_time;
            /* Kopia pod krotkim spinlockiem, zapis juz poza sekcja krytyczna. */
            struct __attribute__((packed)) { char magic[4]; uint32_t count, bytes, crc; } blk =
                {{'B','L','K','1'}, n, (uint32_t)(n * sizeof(sample_t)), 0};
            blk.crc = egr_crc32(batch, blk.bytes);
            if(segment_bytes+sizeof blk+blk.bytes>SEGMENT_LIMIT && !rotate()) {
                unhealthy(); writer_stop();
            }
            if (fwrite(&blk, 1, sizeof blk, samples) != sizeof blk
                || fwrite(batch, 1, blk.bytes, samples) != blk.bytes) unhealthy();
            segment_bytes+=sizeof blk+blk.bytes;
        } else if (n) last_batch=batch_time;
        if (!drain_events(64)) writer_stop();
        {
            static uint64_t last_flush;
            uint64_t now = esp_timer_get_time();
            if (!sink && now - last_flush > 2000000) {
                last_flush = now;
                if (!sync_file(samples) || !sync_file(eventfile)) unhealthy();
            }
        }
        xSemaphoreGive(file_lock);
        if(n < BLOCK_COUNT) vTaskDelay(pdMS_TO_TICKS(5));
    }
}
