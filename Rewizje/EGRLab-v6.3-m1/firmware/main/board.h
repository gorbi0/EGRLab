#pragma once
#include <stdbool.h>
#include <stdint.h>
#include "esp_err.h"
#include "driver/twai.h"

/* 6.3-m1: plytka M1-R1 (Plytki/M1-R1-review/docs/GPIO.csv). Bez MCP23017, I2C, dekodera CS, P04 SAFE,
 * przekaznikow P05 i MCP3201 (M-01). Wszystkie wyjscia wprost z GPIO ESP32-S3. */
enum {
    GPIO_RPWM = 1, GPIO_ADC_SDI = 2, GPIO_TP3 = 3, GPIO_SPI3_SCK = 4, GPIO_SPI3_MOSI = 5, GPIO_SPI3_MISO = 6,
    GPIO_SD_CS = 7, GPIO_TC1_CS = 8, GPIO_ADC_SCLK = 9, GPIO_ADC_RESET = 10, GPIO_ADC_DOUTA = 11,
    GPIO_ADC_CS = 12, GPIO_ADC_CONVST = 13, GPIO_ADC_BUSY = 14, GPIO_BTN = 15, GPIO_TC2_CS = 16,
    GPIO_CAN_TX = 17, GPIO_CAN_RX = 18, GPIO_LPWM = 21, GPIO_LED_RGB = 38, GPIO_DRIVE_EN = 39,
    GPIO_SENS_EN = 40, GPIO_SCOPE = 41, GPIO_SENS_FAULT_N = 42
};

esp_err_t board_init(void);
esp_err_t board_sd_mount(void);

/* --- Przetwornik ---------------------------------------------------------
 * Jeden wlasciciel: zadanie akwizycji. Konfiguracje wolno zmieniac wylacznie
 * przy zatrzymanej akwizycji - board_adc_ranges() odmowi, dopoki
 * board_adc_set_running(false) nie potwierdzi, ze nikt nie czyta.
 * M-04: prad silnika jest kanalem CH6 (indeks 5) AD7606B, probkowanym razem z napieciami. */
esp_err_t board_adc(int16_t values[8], uint64_t *t_us);
void board_adc_set_running(bool running);
/* Ustawia zakresy i zwraca w `applied` to, co sprzet faktycznie potwierdzil
 * odczytem rejestrow. W hardware mode zwraca +-10 V na wszystkich kanalach. */
esp_err_t board_adc_ranges(const uint8_t requested[8], uint8_t applied[8]);
void board_adc_current_ranges(uint8_t applied[8]);
bool board_adc_software_mode(void);
bool board_adc_config_ok(void);
/* Liczniki od startu - impulsy CONVST, bledy odczytu, pelne resety AD7606B (F-05). */
void board_adc_counters(uint32_t *convst, uint32_t *errors, uint32_t *resets);

/* --- Wyjscia i wejscia --------------------------------------------------- */
/* M-07: SENS_5V (TPS2553, GPIO40) tylko w TEST; w LOGGER zawsze wylaczone (D-M1-5). */
esp_err_t board_mode(bool test, bool sensor);
esp_err_t board_sensor_off(void);
bool board_sensor_enabled(void);
/* SENS_FAULT_N (GPIO42, otwarty dren TPS2553, 10 k do 3V3): true = blad zasilania czujnika. */
bool board_sensor_fault(void);
esp_err_t board_temperature(int ch, float *value, uint8_t *fault);
/* M-05: IBT-2 przez 74AHCT125 - kierunek = ktory PWM (RPWM GPIO1 / LPWM GPIO21), DRIVE_EN GPIO39 osobno. */
void board_drive(float duty, bool permit);
/* M-06: false po zadzialaniu programowego ograniczenia pradu (zatrzask do nastepnego board_mode). */
bool board_drive_ok(void);
void board_overcurrent_trip(void);
void board_kill(void);
void board_scope_trigger(void);
/* M-12: przycisk START / STOP (GPIO15, aktywny L) - surowy poziom; filtracja w zadaniu safety. */
bool board_button(void);
/* M-12: dioda RGB modulu DEV-KIT (GPIO38, WS2812 przez RMT); kolor 0xRRGGBB, 0 = zgaszona. */
void board_led(uint32_t rgb);

/* Latched software gate, safe against concurrent board_drive(). */
void board_inhibit(bool stop);
uint32_t board_stop_token(void);
void board_emergency_stop(void);
bool board_release(uint32_t token);

/* --- M-06 / D-M1-4: brak sprzetowego okna OC i zatrzasku ------------------
 * Mostek wylacza firmware i watchdogi ESP32: zadaniowy (TWDT, panika) i RTC (reset systemu).
 * Przy panice DRIVE_EN i SENS_EN ida w dol jeszcze przed zrzutem (owiniety esp_panic_handler);
 * w resecie trzymaja je pull-downy R2-R5 (DRIVE_EN 4,7 k przeciw podciaganiu MTCK, reszta 100 k). */
esp_err_t board_watchdogs_start(void);
void board_watchdogs_feed(void);
/* 6.3.1-m1 (M1-03): false do pelnego startu obu watchdogow; board_release() odmawia, TEST jest odrzucany. */
bool board_watchdogs_ok(void);
