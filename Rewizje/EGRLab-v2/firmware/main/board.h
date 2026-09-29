#pragma once
#include <stdbool.h>
#include <stdint.h>
#include "esp_err.h"
#include "driver/twai.h"

esp_err_t board_init(void);
esp_err_t board_sd_mount(void);
/* Jedna konwersja ośmiu kanałów; t_us to rzeczywisty start konwersji. */
esp_err_t board_adc(int16_t values[8], uint64_t *t_us);
/* Zakresy per kanał; działa tylko w software mode, inaczej ESP_ERR_NOT_SUPPORTED. */
esp_err_t board_adc_ranges(const uint8_t range[8]);
bool board_adc_software_mode(void);
/* test = bank TEST, sensor = własne zasilanie czujnika (tylko przy TEST). */
esp_err_t board_mode(bool test, bool sensor);
esp_err_t board_inputs(bool *sensor_fault, bool *log_present, bool *test_present);
esp_err_t board_temperature(int ch, float *value, uint8_t *fault);
void board_drive(float duty, bool permit);
void board_kill(void);
void board_heartbeat(bool enabled);
void board_scope_trigger(void);
bool board_interlock(void);
bool board_armed(void);
bool board_mark(void);
