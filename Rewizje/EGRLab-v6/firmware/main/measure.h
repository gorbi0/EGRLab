#pragma once
#include <stdbool.h>
#include <stdint.h>
typedef struct { uint64_t t; float i; } current_point_t;
typedef struct { current_point_t p[96]; unsigned head,count; } current_window_t;
void current_window_reset(current_window_t *w);
bool current_window_add(current_window_t *w, uint64_t t, float i, float *mean, float *rms);
uint8_t measurement_saturation(const int16_t raw[8]);
