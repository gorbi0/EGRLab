#pragma once
#include <stdbool.h>
#include <stdint.h>
#include "esp_err.h"
#include "driver/twai.h"

esp_err_t board_init(void);
esp_err_t board_sd_mount(void);
esp_err_t board_adc(int16_t values[8], uint64_t *t_us);
esp_err_t board_mode(bool test, bool sensor, int supply_pin);
esp_err_t board_inputs(bool *sensor_fault);
void board_drive(float duty, bool permit);
void board_kill(void);
void board_heartbeat(bool enabled);
bool board_interlock(void);
bool board_armed(void);
bool board_mark(void);
esp_err_t board_temperature(int channel,float *value,uint8_t *fault);
