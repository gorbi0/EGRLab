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

/* v1 miał ring 8 MiB z pretriggerem i osobnym plikiem wokół MARK. Przy
 * 2 kS/s ciągły plik i tak mieści 18,6 h do limitu FAT32, więc pretrigger
 * niczego nie ratował, a był jedynym miejscem, w którym dane mogły przepaść
 * przy zatrzymaniu karty. Zostaje zwykły bufor zapisu. */
#define RING_BYTES (1024 * 1024)
#define RING_COUNT (RING_BYTES / sizeof(sample_t))
#define BLOCK_COUNT 64

static sample_t *ring;
static volatile uint64_t head, tail;
static volatile bool healthy;
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

static bool header(FILE *f, uint32_t session, uint32_t rate) {
    struct __attribute__((packed)) {
        char magic[8]; uint16_t version, bytes;
        uint32_t rate, record, flags; uint64_t session;
    } h = {"EGRLOG1", 2, 32, rate, 32, 0, session};
    return fwrite(&h, 1, sizeof h, f) == sizeof h;
}
bool storage_init(uint32_t session, const profile_t *p, uint32_t rate, int bank) {
    crc_init();
    ring = heap_caps_malloc(RING_COUNT * sizeof(sample_t), MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    events = xQueueCreate(128, 256);
    if (!ring || !events) return false;
    snprintf(directory, sizeof directory, "/sd/session_%" PRIu32, session);
    /* Istniejącej sesji nigdy nie nadpisujemy, nawet po przywróceniu NVS. */
    if (mkdir(directory, 0777) != 0) return false;
    char path[160];
    snprintf(path, sizeof path, "%s/samples.egr", directory); samples = fopen(path, "wb");
    snprintf(path, sizeof path, "%s/events.ndjson", directory); eventfile = fopen(path, "w");
    if (!samples || !eventfile || !header(samples, session, rate)) return false;
    snprintf(path, sizeof path, "%s/meta.json", directory);
    FILE *meta = fopen(path, "w");
    if (!meta) return false;
    fprintf(meta, "{\n\"schema\":2,\"firmware\":\"EGRLab-v2\",\"synthetic\":false,\"utc\":null,\n"
        "\"vehicle\":\"Kia Sportage 1.7 CRDi 2013\",\"valve_part\":\"28410-2A850\",\n"
        "\"valve_id\":\"%s\",\"adapter_id\":\"%s\",\"bank\":%d,\n"
        "\"sample_rate\":%" PRIu32 ",\"shunt_bypass\":\"verify\",\n"
        "\"ch_supply\":%d,\"ch_ground\":%d,\"ch_feedback\":%d,\n",
        p->valve, p->adapter, bank, rate,
        (int)p->ch_supply, (int)p->ch_ground, (int)p->ch_feedback);
    fprintf(meta, "\"full_scale\":[");
    for (int i = 0; i < 8; i++) fprintf(meta, "%s%.4g", i ? "," : "", control_full_scale(p->range[i]));
    fprintf(meta, "],\n\"gain\":[");
    for (int i = 0; i < 8; i++) fprintf(meta, "%s%.9g", i ? "," : "", p->gain[bank][i]);
    fprintf(meta, "],\n\"offset\":[");
    for (int i = 0; i < 8; i++) fprintf(meta, "%s%.9g", i ? "," : "", p->offset[bank][i]);
    fprintf(meta, "],\n\"current_zero\":%.9g,\"current_volts_per_amp\":0.25,\n"
        "\"closed\":%.9g,\"open\":%.9g,\"opening_sign\":%d,\"qualified\":%s}\n",
        p->current_zero[bank], p->closed, p->open, (int)p->opening_sign,
        p->qualified ? "true" : "false");
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
void storage_event(const char *fmt, ...) {
    if (!events) return;
    char line[256];
    va_list args; va_start(args, fmt);
    int n = vsnprintf(line, sizeof line - 1, fmt, args);
    va_end(args);
    if (n < 0) return;
    if (xQueueSend(events, line, 0) != pdTRUE) unhealthy(); /* zdarzenia nie giną po cichu */
}
void storage_mark(uint64_t t_us) {
    storage_event("{\"type\":\"mark\",\"t_us\":%" PRIu64 "}", t_us);
}
void storage_writer(void *arg) {
    (void)arg;
    static sample_t batch[BLOCK_COUNT];
    char line[256];
    while (true) {
        unsigned n = 0;
        portENTER_CRITICAL(&mux);
        while (n < BLOCK_COUNT && tail < head) batch[n++] = ring[tail++ % RING_COUNT];
        portEXIT_CRITICAL(&mux);
        if (n) {
            /* Kopia pod krótkim spinlockiem, zapis już poza sekcją krytyczną. */
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
