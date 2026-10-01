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
