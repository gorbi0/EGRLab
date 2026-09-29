#pragma once
#include <stdbool.h>
#include <stdint.h>
#include "control.h"

/* Rekord 32 B. W v3 pole `reserved` stalo sie `config_id`: kazda probka
 * niesie numer migawki konfiguracji, ktora ja opisuje. Dzieki temu analiza
 * offline stosuje wlasciwe zakresy, wzmocnienia i zero pradu nawet wtedy,
 * gdy w trakcie sesji zmienil sie bank, zakres albo kalibracja. */
typedef struct __attribute__((packed)) {
    uint64_t t_us;
    uint32_t sequence;
    int16_t raw[8];
    uint16_t flags, config_id;
} sample_t;

enum {
    SAMPLE_GAP     = 1 << 0,
    SAMPLE_TEST    = 1 << 1,
    SAMPLE_SENSOR  = 1 << 2,
    SAMPLE_PERMIT  = 1 << 3,
    SAMPLE_MARK    = 1 << 4,
    SAMPLE_TRIGGER = 1 << 5,
    SAMPLE_SATURATED = 1 << 6,
    SAMPLE_INVALID = 1 << 7
};

#include "jsonlog.h"
#define STORAGE_EVENT_MAX JSON_EVENT_MAX

bool storage_init(uint32_t session, uint32_t rate);
void storage_push(const sample_t *s);
/* Zwraca false, gdy linia nie zmiescila sie w limicie albo kolejka jest
 * pelna â€” i w obu wypadkach oznacza zapis jako niezdrowy. Cicha utrata
 * zdarzenia jest gorsza niz jawny blad. */
bool storage_event(const char *fmt, ...);
bool storage_config(const session_config_t *cfg);
void storage_mark(uint64_t t_us);
bool storage_ok(void);
uint32_t storage_lost_events(void);
void storage_writer(void *arg);
uint32_t egr_crc32(const void *data, unsigned length);
