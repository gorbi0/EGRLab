#pragma once
#include <stdbool.h>
#include <stdint.h>
#include "esp_err.h"
#include "driver/twai.h"

esp_err_t board_init(void);
esp_err_t board_sd_mount(void);

/* --- Przetwornik ---------------------------------------------------------
 * Jeden właściciel: zadanie akwizycji. Konfigurację wolno zmieniać wyłącznie
 * przy zatrzymanej akwizycji — board_adc_ranges() odmówi, dopóki
 * board_adc_set_running(false) nie potwierdzi, że nikt nie czyta. */
typedef struct { uint16_t raw, begin_us, end_us, status; } local_current_t;
enum { CURRENT_OK=1, CURRENT_ABSENT=2, CURRENT_BUS_ERROR=4, CURRENT_SATURATED=8, CURRENT_TIMING=16 };
esp_err_t board_adc(int16_t values[8], uint64_t *t_us, local_current_t *current);
bool board_local_current_present(bool test);
void board_adc_set_running(bool running);
/* Ustawia zakresy i zwraca w `applied` to, co sprzęt faktycznie potwierdził
 * odczytem rejestrów. W hardware mode zwraca ±10 V na wszystkich kanałach. */
esp_err_t board_adc_ranges(const uint8_t requested[8], uint8_t applied[8]);
void board_adc_current_ranges(uint8_t applied[8]);
bool board_adc_software_mode(void);
bool board_adc_config_ok(void);

/* --- Wyjścia i wejścia --------------------------------------------------- */
esp_err_t board_mode(bool test, bool sensor);
esp_err_t board_inputs(bool *sensor_fault, bool *log_present, bool *test_present);
esp_err_t board_temperature(int ch, float *value, uint8_t *fault);
void board_drive(float duty, bool permit);
bool board_drive_ok(void);
void board_kill(void);
void board_heartbeat(bool enabled);
void board_scope_trigger(void);
bool board_interlock(void);
bool board_armed(void);
bool board_mark(void);

/* Latched software gate, safe against concurrent board_drive(). */
void board_inhibit(bool stop);
uint32_t board_stop_token(void);
void board_emergency_stop(void);
bool board_release(uint32_t token);
