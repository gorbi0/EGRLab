#pragma once
#include <stdbool.h>
#include <stdint.h>
#include "control.h"

/* Detektory zdarzen liczone z kazdej probki. Prog oznacza podejrzenie,
 * nie kod P0404 — kalibracja ECU zalezy od wersji i jej nie znamy. */
enum {
    TRIG_REF      = 1 << 0,  /* referencja czujnika poza 4,5-5,5 V */
    TRIG_GND      = 1 << 1,  /* masa czujnika ponad progiem zdarzenia */
    TRIG_GND_WARN = 1 << 2,  /* masa czujnika ponad progiem ostrzegawczym */
    TRIG_FB       = 1 << 3,  /* sygnal pozycji poza 0,2-4,8 V */
    TRIG_JUMP     = 1 << 4,  /* skok ratio w oknie 1 ms */
    TRIG_STALL    = 1 << 5,  /* prad plynie, pozycja stoi */
    TRIG_OPEN     = 1 << 6,  /* napiecie na uzwojeniu, prad znikomy */
    TRIG_COUNT    = 7
};

/* Progi domyslne. Prog zdarzenia dla masy jest tym samym, ktory ma Krok 2
 * procedury v3; prog ostrzegawczy trzeba dobrac PO pomiarze szumu wlasnego
 * toru w etapie 5 odbioru — 76 uV rozdzielczosci samo z siebie nie znaczy,
 * ze 50 mV jest wykrywalne w aucie. */
#define TRIG_GND_EVENT_V  0.30f
#define TRIG_GND_WARN_V   0.05f

typedef struct {
    uint64_t t_us;
    uint32_t count;
    float min[8], max[8], mean[8];
} summary_t;

/* Konfiguracja bierze sie z tej samej migawki, ktora opisuje probki w pliku.
 * Wolno ja wolac tylko przy zatrzymanej akwizycji. */
void trigger_configure(const session_config_t *cfg, uint32_t sample_hz);
/* Zwraca maske zdarzen wyzwolonych ta probka (zwykle 0). */
uint32_t trigger_sample(const float v[8], uint64_t t_us);
bool trigger_take_summary(summary_t *out);
const char *trigger_name(int bit);
