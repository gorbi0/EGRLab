#pragma once
#include <stdbool.h>
#include <stdint.h>
#include "control.h"

/* Rekord 32 B, identyczny jak w v1 — zmieniło się znaczenie kanałów 6/7/8,
 * dlatego nagłówek ma wersję 2. */
typedef struct __attribute__((packed)) {
    uint64_t t_us;
    uint32_t sequence;
    int16_t raw[8];
    uint16_t flags, reserved;
} sample_t;

enum {
    SAMPLE_GAP     = 1 << 0,
    SAMPLE_TEST    = 1 << 1,
    SAMPLE_SENSOR  = 1 << 2,
    SAMPLE_PERMIT  = 1 << 3,
    SAMPLE_MARK    = 1 << 4,
    SAMPLE_TRIGGER = 1 << 5
};

bool storage_init(uint32_t session, const profile_t *p, uint32_t rate, int bank);
void storage_push(const sample_t *s);
void storage_event(const char *fmt, ...);
void storage_mark(uint64_t t_us);
bool storage_ok(void);
void storage_writer(void *arg);
uint32_t egr_crc32(const void *data, unsigned length);
