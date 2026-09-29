#pragma once
#include <stdbool.h>
#include <stdint.h>
#include "control.h"
typedef struct {
    uint64_t t_us;
    uint32_t sequence;
    int16_t raw[8];
    uint16_t flags,reserved;
} sample_t;
_Static_assert(sizeof(sample_t)==32,"Log ABI must be 32 bytes");
bool storage_init(uint32_t session, const profile_t *profile);
void storage_push(const sample_t *sample);
void storage_mark(uint64_t t_us);
void storage_event(const char *format,...);
bool storage_ok(void);
void storage_writer(void *arg);
uint32_t egr_crc32(const void *data,unsigned length);
