#pragma once
#include <stdbool.h>
#include <stdint.h>
typedef struct { uint64_t t; float i; } current_point_t;
/* 6.2-s1 F-05: 256 punktow = okno 20 ms do 12,8 kS/s (v6.1: 96 punktow, tylko do ok. 4,8 kS/s). */
#define CURRENT_WINDOW_N 256
typedef struct { current_point_t p[CURRENT_WINDOW_N]; unsigned head,count; } current_window_t;
void current_window_reset(current_window_t *w);
bool current_window_add(current_window_t *w, uint64_t t, float i, float *mean, float *rms);
uint8_t measurement_saturation(const int16_t raw[8]);
/* 6.3-m1 M-06: programowe ograniczenie prądu z CH6 (zamiast okna OC i zatrzasku P07, D-M1-4).
 * Prąd liczony z surowej próbki i AKTYWNEJ konfiguracji (zakres, gain/offset CH6, zero, V/A) - także przed
 * akceptacją kalibracji (wartości nominalne), bo ochrona nie może czekać na odbiór. Nasycenie CH6, nieznany
 * zakres albo niepoprawne współczynniki liczą się jak przekroczenie (stan bezpieczny). Zadziałanie po
 * `consecutive` kolejnych próbkach ponad limitem; licznik zeruje próbka poniżej limitu. */
typedef struct { unsigned over; } overcurrent_t;
float overcurrent_amps(int16_t raw, float full_scale, float gain, float offset, float zero, float volts_per_amp);
bool overcurrent_sample(overcurrent_t *o, float amps, float limit_a, unsigned consecutive);
