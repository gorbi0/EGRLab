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
/* 6.2-s1 (F-05): liczniki od startu - impulsy CONVST, bledy odczytu, pelne resety AD7606B. */
void board_adc_counters(uint32_t *convst, uint32_t *errors, uint32_t *resets);

/* --- Wyjścia i wejścia --------------------------------------------------- */
esp_err_t board_mode(bool test, bool sensor);
/* 6.2-s1 F-04: blad konfiguracji AD7606B - caly port A w dol (MEAS_EN = 0). */
esp_err_t board_meas_off(void);
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

/* --- 6.2-s1 (F-01/F-02, decyzje D-2/D-3): PFAIL_N z P02 R4 na GPIO3 (P03 R6: R42 1k, R43 100k do 3V3_CORE) ---
 * Wejscie bez wewnetrznych podciagniec (wewnetrzny pull-down ok. 45k wobec R43 100k dalby L). Aktywny niski.
 * Przerwanie na zbocze opadajace budzi zadanie podane w board_pfail_arm(); jedno zgloszenie na uzbrojenie. */
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
void board_pfail_init(void);
bool board_pfail_level(void);              /* true = H = zasilanie z P02 w porzadku */
void board_pfail_arm(TaskHandle_t task);     /* sprawdza tez poziom: L juz przy uzbrojeniu = zgloszenie */
void board_pfail_rearm(void);                /* po odrzuconym zakloceniu */
uint64_t board_pfail_edge_us(void);
/* Po PFAIL: naped trwale wylaczony (board_drive tylko gasi PWM), potem zamkniecie plikow. */
void board_power_fail_stop(void);
/* Wyjscie triggera oscyloskopu (GPIO41) jako znacznik czasu zamykania plikow (ODBIOR P02 R4 O-05). */
void board_scope_level(bool high);
