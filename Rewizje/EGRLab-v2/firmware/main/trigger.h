#pragma once
#include <stdbool.h>
#include <stdint.h>
#include "control.h"

/* Detektory zdarzeń liczone z każdej próbki. Próg oznacza podejrzenie,
 * nie kod P0404 — kalibracja ECU zależy od wersji i jej nie znamy. */
enum {
    TRIG_REF   = 1 << 0,  /* referencja czujnika poza 4,5–5,5 V */
    TRIG_GND   = 1 << 1,  /* masa czujnika ponad progiem względem B− */
    TRIG_FB    = 1 << 2,  /* sygnał pozycji poza 0,2–4,8 V */
    TRIG_JUMP  = 1 << 3,  /* skok ratio między kolejnymi próbkami */
    TRIG_STALL = 1 << 4,  /* prąd płynie, pozycja stoi */
    TRIG_OPEN  = 1 << 5,  /* napięcie na uzwojeniu, prąd znikomy */
    TRIG_COUNT = 6
};

typedef struct {
    uint64_t t_us;
    uint32_t count;
    float min[8], max[8], mean[8];
} summary_t;

void trigger_configure(const profile_t *p, int bank, uint32_t sample_hz);
/* Zwraca maskę zdarzeń wyzwolonych tą próbką (zwykle 0). */
uint32_t trigger_sample(const float v[8], uint64_t t_us);
bool trigger_take_summary(summary_t *out);
const char *trigger_name(int bit);
