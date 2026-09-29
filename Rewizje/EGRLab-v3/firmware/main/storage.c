#include "storage.h"
#include <stdio.h>
#include <stdarg.h>
#include <string.h>
#include <inttypes.h>
#include <sys/stat.h>
#include "sdkconfig.h"
#include "esp_heap_caps.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"

/* Bufor zapisu 8 MiB w PSRAM: okolo 131 s przy 2 kS/s. To odpornosc na
 * zadlawienie karty, niezalezna od formatu pliku — v2 scielo go do 1 MiB
 * (16 s) przy okazji usuwania pretriggera, choc to dwie osobne decyzje.
 * Pretrigger nadal nie jest potrzebny: historia jest w ciaglym pliku. */
#define RING_BYTES (8 * 1024 * 1024)
#define RING_COUNT (RING_BYTES / sizeof(sample_t))
#define BLOCK_COUNT 64
#define EVENT_QUEUE_DEPTH 64

static sample_t *ring;
static volatile uint64_t head, tail;
static volatile bool healthy;
static volatile uint32_t lost_events;
static portMUX_TYPE mux = portMUX_INITIALIZER_UNLOCKED;
static QueueHandle_t events;
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

static bool header(FILE *f, uint32_t session, uint32_t rate) {
    struct __attribute__((packed)) {
        char magic[8]; uint16_t version, bytes;
        uint32_t rate, record, flags; uint64_t session;
    } h = {"EGRLOG1", 3, 32, rate, 32, 0, session};
    return fwrite(&h, 1, sizeof h, f) == sizeof h;
}
bool storage_init(uint32_t session, uint32_t rate) {
    crc_init();
    ring = heap_caps_malloc(RING_COUNT * sizeof(sample_t), MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    events = xQueueCreate(EVENT_QUEUE_DEPTH, STORAGE_EVENT_MAX);
    if (!ring || !events) return false;
    snprintf(directory, sizeof directory, "/sd/session_%" PRIu32, session);
    /* Istniejacej sesji nigdy nie nadpisujemy, nawet po przywroceniu NVS. */
    if (mkdir(directory, 0777) != 0) return false;
    char path[160];
    snprintf(path, sizeof path, "%s/samples.egr", directory); samples = fopen(path, "wb");
    snprintf(path, sizeof path, "%s/events.ndjson", directory); eventfile = fopen(path, "w");
    if (!samples || !eventfile || !header(samples, session, rate)) return false;
    /* meta.json opisuje tylko sesje. Kalibracja, zakresy, bank i mapowanie
     * zyja w zdarzeniach `config`, bo moga sie zmieniac w trakcie. */
    snprintf(path, sizeof path, "%s/meta.json", directory);
    FILE *meta = fopen(path, "w");
    if (!meta) return false;
    fprintf(meta, "{\n\"schema\":3,\"firmware\":\"EGRLab-v3\",\"synthetic\":false,\"utc\":null,\n"
        "\"vehicle\":\"Kia Sportage 1.7 CRDi 2013\",\"valve_part\":\"28410-2A850\",\n"
        "\"sample_rate\":%" PRIu32 ",\"session\":%" PRIu32 ",\n"
        "\"note\":\"Kalibracja i zakresy w events.ndjson jako zdarzenia config; "
        "kazdy rekord niesie config_id.\"}\n", rate, session);
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
bool storage_event(const char *fmt, ...) {
    if (!events) return false;
    char line[STORAGE_EVENT_MAX];
    va_list args; va_start(args, fmt);
    int n = vsnprintf(line, sizeof line, fmt, args);
    va_end(args);
    /* Obciecie dawaloby niepoprawna linie NDJSON, ktora czytnik odrzuci jako
     * uszkodzona — a zapis raportowalby zdrowie. Zglaszamy blad. */
    if (n < 0 || n >= (int)sizeof line) { lost_events++; unhealthy(); return false; }
    if (xQueueSend(events, line, 0) != pdTRUE) { lost_events++; unhealthy(); return false; }
    return true;
}
bool storage_config(const session_config_t *c) {
    char gains[200] = {0}, offsets[200] = {0}, ranges[40] = {0};
    int g = 0, o = 0, r = 0;
    for (int i = 0; i < 8; i++) {
        g += snprintf(gains + g, sizeof gains - g, "%s%.9g", i ? "," : "", c->gain[i]);
        o += snprintf(offsets + o, sizeof offsets - o, "%s%.9g", i ? "," : "", c->offset[i]);
        r += snprintf(ranges + r, sizeof ranges - r, "%s%.4g", i ? "," : "",
                      control_full_scale(c->range[i]));
        if (g >= (int)sizeof gains || o >= (int)sizeof offsets || r >= (int)sizeof ranges) {
            lost_events++; unhealthy(); return false;
        }
    }
    return storage_event(
        "{\"type\":\"config\",\"t_us\":%" PRIu64 ",\"config_id\":%u,\"bank\":%d,"
        "\"ch_supply\":%d,\"ch_ground\":%d,\"ch_feedback\":%d,"
        "\"full_scale\":[%s],\"gain\":[%s],\"offset\":[%s],"
        "\"current_zero\":%.9g,\"current_volts_per_amp\":0.25,\"current_valid\":%s,"
        "\"closed\":%.9g,\"open\":%.9g,\"opening_sign\":%d,\"learned\":%s,"
        "\"aux_position\":\"%s\",\"adc_software_mode\":%s,\"adc_config_ok\":%s}",
        (uint64_t)esp_timer_get_time(), (unsigned)c->id, (int)c->bank,
        (int)c->ch_supply, (int)c->ch_ground, (int)c->ch_feedback,
        ranges, gains, offsets,
        c->current_zero, c->current_valid ? "true" : "false",
        c->closed, c->open, (int)c->opening_sign, c->learned ? "true" : "false",
        c->aux_position ? "LO" : "HI",
        c->adc_software_mode ? "true" : "false", c->adc_config_ok ? "true" : "false");
}
void storage_mark(uint64_t t_us) {
    storage_event("{\"type\":\"mark\",\"t_us\":%" PRIu64 "}", t_us);
}
void storage_writer(void *arg) {
    (void)arg;
    static sample_t batch[BLOCK_COUNT];
    static char line[STORAGE_EVENT_MAX];
    while (true) {
        unsigned n = 0;
        portENTER_CRITICAL(&mux);
        while (n < BLOCK_COUNT && tail < head) batch[n++] = ring[tail++ % RING_COUNT];
        portEXIT_CRITICAL(&mux);
        if (n) {
            /* Kopia pod krotkim spinlockiem, zapis juz poza sekcja krytyczna. */
            struct __attribute__((packed)) { char magic[4]; uint32_t count, bytes, crc; } blk =
                {{'B','L','K','1'}, n, (uint32_t)(n * sizeof(sample_t)), 0};
            blk.crc = egr_crc32(batch, blk.bytes);
            if (fwrite(&blk, 1, sizeof blk, samples) != sizeof blk
                || fwrite(batch, 1, blk.bytes, samples) != blk.bytes) unhealthy();
        }
        while (xQueueReceive(events, line, 0) == pdTRUE) {
            if (fprintf(eventfile, "%s\n", line) < 0) unhealthy();
        }
        if (n < BLOCK_COUNT) {
            static uint64_t last_flush;
            uint64_t now = esp_timer_get_time();
            if (now - last_flush > 2000000) {
                last_flush = now;
                if (fflush(samples) != 0 || fflush(eventfile) != 0) unhealthy();
            }
            vTaskDelay(pdMS_TO_TICKS(5));
        }
    }
}
