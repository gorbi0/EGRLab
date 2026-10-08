#include "board.h"
#include "control.h"
#include "sdkconfig.h"
#include <math.h>
#include <string.h>
#include <stdatomic.h>
#include "driver/gpio.h"
#include "driver/spi_master.h"
#include "driver/ledc.h"
#include "driver/rmt_tx.h"
#include "driver/sdspi_host.h"
#include "esp_timer.h"
#include "esp_rom_sys.h"
#include "esp_vfs_fat.h"
#include "esp_system.h"
#include "esp_task_wdt.h"
#include "esp_attr.h"
#include "hal/gpio_ll.h"
#include "hal/wdt_hal.h"
#include "soc/rtc.h"
#include "sdmmc_cmd.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"

/* --- AD7606B: dostep do rejestrow --------------------------------------
 * ZWERYFIKUJ z datasheetem swojej rewizji przed pierwszym uruchomieniem.
 * Ramka 16-bit: bity 15:14 = 01 dla odczytu, 00 dla zapisu; bity 13:8 =
 * szesciobitowy adres; bity 7:0 = dane. Odczyt wymaga drugiej ramki.
 * Wejscie w tryb rejestrow wymaga OS[2:0] = 111 na plytce (M1: na stale, M-02); samo SPI
 * go nie wlaczy. Zapis pod adres 0x00 wraca do strumienia danych.
 * Kazdy zapis jest weryfikowany odczytem, a niepowodzenie JEST BLEDEM:
 * blokuje TEST i trafia do kazdego rekordu jako adc_config_ok = false. */
enum { ADC_REG_EXIT = 0x00, ADC_REG_STATUS = 0x01, ADC_REG_CONFIG = 0x02,
       ADC_REG_RANGE_12 = 0x03, ADC_REG_RANGE_34 = 0x04, ADC_REG_RANGE_56 = 0x05,
       ADC_REG_RANGE_78 = 0x06, ADC_REG_BANDWIDTH = 0x07, ADC_REG_OVERSAMPLE = 0x08 };
#define ADC_READ_FLAG    0x4000
#define ADC_CONFIG_VALUE 0x00   /* jedna linia DOUTA, bez statusu w ramce */
#define ADC_OVERSAMPLE_X8 0x03

/* Kod zakresu w nibble kanalu: 0 = +-2,5 V, 1 = +-5 V, 2 = +-10 V. */
static const uint8_t RANGE_CODE[3] = {0, 1, 2};

static spi_device_handle_t adc, tc[2];
static SemaphoreHandle_t adc_lock;
static portMUX_TYPE gate_mux = portMUX_INITIALIZER_UNLOCKED;
static bool inhibited = true;
static uint32_t gate_epoch;
static bool software_mode;
static _Atomic bool config_ok, drive_ok = true, sens_on;
static volatile bool acquisition_running;
static uint8_t applied_range[8];
static int current_sign;
static uint64_t reverse_until;
/* F-04/F-05: po bledzie odczytu konfiguracja jest niewazna, a nastepna konfiguracja zaczyna od
 * pelnego RESET i 2100 ms (zanik zasilania AD7606B = nowe pierwsze uruchomienie). */
static _Atomic bool adc_reset_needed;
static _Atomic uint32_t convst_count, adc_errors, adc_resets;
static rmt_channel_handle_t led_chan;
static rmt_encoder_handle_t led_encoder;
static wdt_hal_context_t rtc_wdt = RWDT_HAL_CONTEXT_DEFAULT();
static bool rtc_wdt_on;
/* 6.3.1-m1 (recenzja M1-03): true dopiero po pelnym uruchomieniu TWDT i RTC WDT; bez tego bramka napedu sie nie zwalnia. */
static _Atomic bool watchdogs_ok;

/* M-05: oba PWM w jednym miejscu; kanal 0 = RPWM (GPIO1), kanal 1 = LPWM (GPIO21). */
static void pwm_set(uint32_t r, uint32_t l) {
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, r); ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_1, l); ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_1);
}
void board_inhibit(bool stop) {
    portENTER_CRITICAL(&gate_mux);
    inhibited = stop;
    if (stop) gpio_set_level(GPIO_DRIVE_EN, 0);
    portEXIT_CRITICAL(&gate_mux);
}
uint32_t board_stop_token(void) {
    portENTER_CRITICAL(&gate_mux); uint32_t v=gate_epoch; portEXIT_CRITICAL(&gate_mux); return v;
}
void board_emergency_stop(void) {
    portENTER_CRITICAL(&gate_mux); gate_epoch++; inhibited=true; gpio_set_level(GPIO_DRIVE_EN,0); portEXIT_CRITICAL(&gate_mux);
    board_kill();
}
bool board_release(uint32_t token) {
    portENTER_CRITICAL(&gate_mux); bool ok=token==gate_epoch && watchdogs_ok;
    if(ok) inhibited=false;
    portEXIT_CRITICAL(&gate_mux); return ok;
}
void board_adc_counters(uint32_t *convst, uint32_t *errors, uint32_t *resets) {
    *convst = convst_count; *errors = adc_errors; *resets = adc_resets;
}
/* Najpierw DRIVE_EN (R_EN + L_EN modulu), potem oba PWM: mostek wylaczony nawet, gdy LEDC by nie odpowiedzial. */
void board_kill(void) {
    portENTER_CRITICAL(&gate_mux);
    gpio_set_level(GPIO_DRIVE_EN, 0);
    portEXIT_CRITICAL(&gate_mux);
    pwm_set(0, 0);
}
void board_overcurrent_trip(void) { drive_ok = false; board_emergency_stop(); }
bool board_button(void) { return !gpio_get_level(GPIO_BTN); }
bool board_sensor_fault(void) { return !gpio_get_level(GPIO_SENS_FAULT_N); }
bool board_sensor_enabled(void) { return sens_on; }
bool board_adc_software_mode(void) { return software_mode; }
bool board_adc_config_ok(void) { return config_ok; }
bool board_drive_ok(void) { return drive_ok; }
void board_adc_set_running(bool running) { acquisition_running = running; }
void board_adc_current_ranges(uint8_t out[8]) { memcpy(out, applied_range, 8); }
void board_scope_trigger(void) {
    gpio_set_level(GPIO_SCOPE, 1); esp_rom_delay_us(20); gpio_set_level(GPIO_SCOPE, 0);
}
/* M-12: WS2812 modulu DEV-KIT (kolejnosc GRB), RMT 10 MHz: 0 = 0,3/0,9 us, 1 = 0,9/0,3 us. Bez pamieci led_strip
 * (komponent zewnetrzny; budowanie bez sieci). Wolac z jednego zadania (safety). */
void board_led(uint32_t rgb) {
    static uint8_t grb[3];
    if (!led_chan) return;
    grb[0] = (uint8_t)(rgb >> 8); grb[1] = (uint8_t)(rgb >> 16); grb[2] = (uint8_t)rgb;
    rmt_transmit_config_t tx = {.loop_count = 0};
    rmt_transmit(led_chan, led_encoder, grb, sizeof grb, &tx);
}
static void led_init(void) {
    rmt_tx_channel_config_t ch = {.gpio_num = GPIO_LED_RGB, .clk_src = RMT_CLK_SRC_DEFAULT,
        .resolution_hz = 10000000, .mem_block_symbols = 48, .trans_queue_depth = 2};
    rmt_bytes_encoder_config_t enc = {
        .bit0 = {.level0 = 1, .duration0 = 3, .level1 = 0, .duration1 = 9},
        .bit1 = {.level0 = 1, .duration0 = 9, .level1 = 0, .duration1 = 3},
        .flags.msb_first = 1};
    /* Dioda to tylko sygnalizacja: blad RMT nie zatrzymuje przyrzadu. */
    if (rmt_new_tx_channel(&ch, &led_chan) != ESP_OK) { led_chan = NULL; return; }
    if (rmt_new_bytes_encoder(&enc, &led_encoder) != ESP_OK || rmt_enable(led_chan) != ESP_OK) {
        rmt_del_channel(led_chan); led_chan = NULL;
    }
}
/* M-05: kierunek = ktory PWM pracuje, drugi w stanie niskim. Zmiana kierunku: oba w dol i DRIVE_EN niski
 * na 5 ms (jak przerwa po zmianie INA/INB w 6.2-s1). PWM <= 25 kHz (BTS7960), wypelnienie <= 90 %. */
void board_drive(float duty, bool permit) {
    if (!drive_ok || !permit || !isfinite(duty)) { board_kill(); return; }
    int sign = duty > 0 ? 1 : duty < 0 ? -1 : 0;
    uint64_t now = esp_timer_get_time();
    if (sign && sign != current_sign) {
        board_kill(); current_sign = sign; reverse_until = now + 5000;
        return;                       /* pelne 5 ms przerwy */
    }
    if (now < reverse_until) { board_kill(); return; }
    /* Zezwolenie utrzymujemy w postoju przy duty 0 (oba PWM nisko = hamowanie); STOP zdejmuje DRIVE_EN. */
    portENTER_CRITICAL(&gate_mux);
    bool blocked = inhibited;
    if (!blocked) gpio_set_level(GPIO_DRIVE_EN, 1);
    portEXIT_CRITICAL(&gate_mux);
    if (blocked) { board_kill(); return; }
    uint32_t d = (uint32_t)(fminf(fabsf(duty), .9f) * 1023);
    pwm_set(current_sign > 0 ? d : 0, current_sign < 0 ? d : 0);
}
static esp_err_t adc_frame(uint16_t out, uint16_t *in) {
    spi_transaction_t t = {.length = 16, .flags = SPI_TRANS_USE_TXDATA | SPI_TRANS_USE_RXDATA};
    t.tx_data[0] = out >> 8; t.tx_data[1] = out & 0xff;
    esp_err_t e = spi_device_polling_transmit(adc, &t);
    if (e == ESP_OK && in) *in = ((uint16_t)t.rx_data[0] << 8) | t.rx_data[1];
    return e;
}
static esp_err_t adc_reg_write(uint8_t reg, uint8_t value) {
    return adc_frame((uint16_t)((reg & 0x3f) << 8) | value, NULL);
}
static esp_err_t adc_reg_read(uint8_t reg, uint8_t *value) {
    uint16_t back = 0;
    uint16_t cmd = ADC_READ_FLAG | (uint16_t)((reg & 0x3f) << 8);
    esp_err_t e = adc_frame(cmd, NULL);
    if (e == ESP_OK) e = adc_frame(cmd, &back);
    if (e == ESP_OK) *value = back & 0xff;
    return e;
}
static esp_err_t adc_reg_write_verified(uint8_t reg, uint8_t value) {
    uint8_t back = (uint8_t)~value;
    esp_err_t e = adc_reg_write(reg, value);
    if (e == ESP_OK) e = adc_reg_read(reg, &back);
    if (e == ESP_OK && back != value) e = ESP_ERR_INVALID_RESPONSE;
    return e;
}
/* M-02: RESET AD7606B wprost z GPIO10 (R9 10 k do GND trzyma go nisko w rozruchu ESP32). Impuls >= 3 us.
 * Karta Rev. B (tabela 3, przypis 2): po pierwszym RESET od zalaczenia ponad 2 s do pierwszej komunikacji -> 2100 ms. */
static void adc_reset_pulse(void) {
    gpio_set_level(GPIO_ADC_RESET, 1); esp_rom_delay_us(20); gpio_set_level(GPIO_ADC_RESET, 0);
    adc_resets++;
}
static esp_err_t adc_full_reset(void) {
    adc_reset_pulse();
    vTaskDelay(pdMS_TO_TICKS(2100));
    return ESP_OK;
}
esp_err_t board_adc_ranges(const uint8_t requested[8], uint8_t applied[8]) {
    memset(applied, RANGE_UNKNOWN, 8);
    if (acquisition_running) { config_ok = false; return ESP_ERR_INVALID_STATE; }
    config_ok = false;
    if (adc_reset_needed) {                                 /* F-04: po bledzie odczytu nowy rozruch */
        esp_err_t r = adc_full_reset();
        if (r != ESP_OK) return r;
        adc_reset_needed = false;
    }
    if (!software_mode) {
        memset(applied_range, RANGE_10V, 8); memcpy(applied, applied_range, 8);
        config_ok = true; return ESP_OK;
    }
    if (xSemaphoreTake(adc_lock, pdMS_TO_TICKS(50)) != pdTRUE) return ESP_ERR_TIMEOUT;
    esp_err_t e = adc_reg_write_verified(ADC_REG_CONFIG, ADC_CONFIG_VALUE);
    if (e == ESP_OK) e = adc_reg_write_verified(ADC_REG_OVERSAMPLE, ADC_OVERSAMPLE_X8);
    for (int pair = 0; pair < 4 && e == ESP_OK; pair++) {
        uint8_t a = requested[2*pair], z = requested[2*pair+1];
        if (a > RANGE_10V || z > RANGE_10V) { e = ESP_ERR_INVALID_ARG; break; }
        e = adc_reg_write_verified((uint8_t)(ADC_REG_RANGE_12 + pair),
                                   RANGE_CODE[a] | (RANGE_CODE[z] << 4));
    }
    esp_err_t leave = adc_reg_write(ADC_REG_EXIT, 0);
    if (e == ESP_OK) e = leave;
    if (e == ESP_OK) {
        memcpy(applied_range, requested, 8); memcpy(applied, requested, 8); config_ok = true;
    } else {
        memset(applied_range, RANGE_UNKNOWN, 8);
        adc_reset_needed = true;      /* M-11: brak 3,3 V / AD7606B - nastepna proba od pelnego rozruchu */
    }
    xSemaphoreGive(adc_lock);
    return e;
}
/* Wejscie w tryb rejestrow zalezy od OS[2:0] = 111. Sprawdzamy to
 * zapisem i odczytem; wynik jest jawny, nie zgadywany. */
static void adc_probe_software_mode(void) {
    gpio_set_level(GPIO_ADC_SDI, 0);
#if CONFIG_EGR_ADC_SOFTWARE_MODE
    software_mode = true;
    esp_err_t e = adc_reg_write_verified(ADC_REG_CONFIG, ADC_CONFIG_VALUE);
    if (e == ESP_OK) e = adc_reg_write_verified(ADC_REG_OVERSAMPLE, ADC_OVERSAMPLE_X8);
    if (e == ESP_OK) e = adc_reg_write(ADC_REG_EXIT, 0);
    config_ok = (e == ESP_OK);
    if (!config_ok) adc_reset_needed = true;
#else
    software_mode = false;
    config_ok = true;                 /* tryb sprzetowy nie ma czego potwierdzac */
#endif
    for (int i = 0; i < 8; i++) applied_range[i] = RANGE_10V;
}
/* esp_restart(): mostek i zasilanie czujnika w dol przed resetem. */
static void board_shutdown(void) { gpio_set_level(GPIO_DRIVE_EN, 0); gpio_set_level(GPIO_SENS_EN, 0); pwm_set(0, 0); }
esp_err_t board_init(void) {
    /* M-05/M-07: stany bezpieczne zanim wyjscia zostana wlaczone (pull-downy w resecie: DRIVE_EN 4,7 k przeciw WPU MTCK, reszta 100 k). */
    const int low[] = {GPIO_DRIVE_EN, GPIO_SENS_EN, GPIO_RPWM, GPIO_LPWM, GPIO_ADC_RESET, GPIO_ADC_CONVST,
                       GPIO_SCOPE, GPIO_ADC_SDI};
    uint64_t mask = 0;
    for (unsigned k = 0; k < sizeof low / sizeof low[0]; k++) { gpio_set_level(low[k], 0); mask |= 1ULL << low[k]; }
    gpio_config_t out = {.pin_bit_mask = mask, .mode = GPIO_MODE_OUTPUT};
    ESP_ERROR_CHECK(gpio_config(&out));
    for (unsigned k = 0; k < sizeof low / sizeof low[0]; k++) gpio_set_level(low[k], 0);
    /* BTN: 10 k do 3V3 + 100 nF; SENS_FAULT_N: 10 k do 3V3; BUSY: wyjscie AD7606B. Bez wewnetrznych podciagniec. */
    gpio_config_t inp = {.pin_bit_mask = (1ULL << GPIO_BTN) | (1ULL << GPIO_SENS_FAULT_N) | (1ULL << GPIO_ADC_BUSY),
                         .mode = GPIO_MODE_INPUT};
    ESP_ERROR_CHECK(gpio_config(&inp));
    ESP_ERROR_CHECK(esp_register_shutdown_handler(board_shutdown));
    ledc_timer_config_t lt = {.speed_mode = LEDC_LOW_SPEED_MODE, .duty_resolution = LEDC_TIMER_10_BIT,
        .timer_num = LEDC_TIMER_0, .freq_hz = CONFIG_EGR_PWM_HZ, .clk_cfg = LEDC_AUTO_CLK};
    ESP_ERROR_CHECK(ledc_timer_config(&lt));
    ledc_channel_config_t lr = {.gpio_num = GPIO_RPWM, .speed_mode = LEDC_LOW_SPEED_MODE,
        .channel = LEDC_CHANNEL_0, .timer_sel = LEDC_TIMER_0, .duty = 0};
    ESP_ERROR_CHECK(ledc_channel_config(&lr));
    ledc_channel_config_t ll = {.gpio_num = GPIO_LPWM, .speed_mode = LEDC_LOW_SPEED_MODE,
        .channel = LEDC_CHANNEL_1, .timer_sel = LEDC_TIMER_0, .duty = 0};
    ESP_ERROR_CHECK(ledc_channel_config(&ll));
    current_sign = 0;
    adc_lock = xSemaphoreCreateMutex(); if (!adc_lock) return ESP_ERR_NO_MEM;
    led_init(); board_led(0x000010);
    /* F-04 (AD7606B Rev. B, s. 27): >= 10 ms od stabilnego AVCC/VDRIVE do RESET, RESET >= 3 us,
     * po pierwszym RESET od zalaczenia 2100 ms przed SPI. M-02: RESET z GPIO10, bez ekspandera. */
    vTaskDelay(pdMS_TO_TICKS(10));
    adc_reset_pulse(); vTaskDelay(pdMS_TO_TICKS(2100));
    spi_bus_config_t ab = {.mosi_io_num = GPIO_ADC_SDI, .miso_io_num = GPIO_ADC_DOUTA, .sclk_io_num = GPIO_ADC_SCLK,
        .quadwp_io_num = -1, .quadhd_io_num = -1, .max_transfer_sz = 32};
    ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST, &ab, SPI_DMA_CH_AUTO));
    spi_device_interface_config_t ad = {.clock_speed_hz = CONFIG_EGR_ADC_SPI_HZ, .mode = 2, .spics_io_num = GPIO_ADC_CS,
        .queue_size = 1, .cs_ena_pretrans = 2, .cs_ena_posttrans = 1};
    ESP_ERROR_CHECK(spi_bus_add_device(SPI2_HOST, &ad, &adc));
#if !CONFIG_EGR_CORE_ONLY
    adc_probe_software_mode();
#endif
    spi_bus_config_t sb = {.mosi_io_num = GPIO_SPI3_MOSI, .miso_io_num = GPIO_SPI3_MISO, .sclk_io_num = GPIO_SPI3_SCK,
        .quadwp_io_num = -1, .quadhd_io_num = -1, .max_transfer_sz = 8192};
    ESP_ERROR_CHECK(spi_bus_initialize(SPI3_HOST, &sb, SPI_DMA_CH_AUTO));
#if CONFIG_EGR_TEMP_PRESENT
    /* M-08: CS modulow MAX31856 wprost z GPIO8 / GPIO16 (10 k do 3V3); SDO przez 74LVC125 z OE = CS -
     * przezroczysty dla firmware. Bez zasilania 3,3 V (tylko USB, M-11) zapis po prostu nie trafia do ukladu. */
    for (int i = 0; i < 2; i++) {
        spi_device_interface_config_t t = {.clock_speed_hz = 1000000, .mode = 1,
            .spics_io_num = i ? GPIO_TC2_CS : GPIO_TC1_CS, .queue_size = 1,
            .cs_ena_pretrans = 2, .cs_ena_posttrans = 2};
        ESP_ERROR_CHECK(spi_bus_add_device(SPI3_HOST, &t, &tc[i]));
        spi_transaction_t w = {.length = 16, .flags = SPI_TRANS_USE_TXDATA};
        w.tx_data[0] = 0x81; w.tx_data[1] = 0x03;  /* CR1: typ K, bez usredniania */
        ESP_ERROR_CHECK(spi_device_polling_transmit(tc[i], &w));
        w.tx_data[0] = 0x80; w.tx_data[1] = 0x91;  /* CR0: ciagle, detekcja OC, 50 Hz */
        ESP_ERROR_CHECK(spi_device_polling_transmit(tc[i], &w));
    }
    /* First 50 Hz conversion plus open-circuit check; no valid sample before this. */
    vTaskDelay(pdMS_TO_TICKS(300));
#endif
#if CONFIG_EGR_CAN_PRESENT
    /* M-09: TCAN1051V z TXD i S na stale w 3V3 (cichy). GPIO17 niepodlaczony - TWAI i tak tylko slucha. */
    twai_general_config_t tg = TWAI_GENERAL_CONFIG_DEFAULT(GPIO_CAN_TX, GPIO_CAN_RX, TWAI_MODE_LISTEN_ONLY);
    tg.rx_queue_len = 128; tg.tx_queue_len = 0;
    twai_timing_config_t tt = TWAI_TIMING_CONFIG_500KBITS();
    twai_filter_config_t tf = TWAI_FILTER_CONFIG_ACCEPT_ALL();
    ESP_ERROR_CHECK(twai_driver_install(&tg, &tt, &tf));
    ESP_ERROR_CHECK(twai_start());
#endif
    return ESP_OK;
}
esp_err_t board_sd_mount(void) {
    sdmmc_host_t host = SDSPI_HOST_DEFAULT(); host.slot = SPI3_HOST; host.max_freq_khz = CONFIG_EGR_SD_KHZ;
    sdspi_device_config_t slot = SDSPI_DEVICE_CONFIG_DEFAULT();
    slot.gpio_cs = GPIO_SD_CS; slot.host_id = SPI3_HOST;
    esp_vfs_fat_sdmmc_mount_config_t mount = {.format_if_mount_failed = false,
        .max_files = 8, .allocation_unit_size = 32768};
    sdmmc_card_t *card = NULL;
    return esp_vfs_fat_sdspi_mount("/sd", &host, &slot, &mount, &card);
}
static esp_err_t adc_read_owned(int16_t values[8], uint64_t *t_us) {
    *t_us = esp_timer_get_time();
    gpio_set_level(GPIO_ADC_CONVST, 1); convst_count++;
    /* OS x8 in software mode leaves enough time to observe BUSY assertion.
     * A disconnected/stuck-low BUSY must not turn old SPI words into fresh data. */
    if(software_mode && !gpio_get_level(GPIO_ADC_BUSY)) { gpio_set_level(GPIO_ADC_CONVST,0); return ESP_ERR_INVALID_RESPONSE; }
    esp_rom_delay_us(1); gpio_set_level(GPIO_ADC_CONVST, 0);
    uint64_t until = *t_us + 200;
    while (gpio_get_level(GPIO_ADC_BUSY)) {
        if ((uint64_t)esp_timer_get_time() > until) return ESP_ERR_TIMEOUT;
    }
    if (software_mode) {
        /* Jedna transakcja 128-bit; w hardware mode byloby to bledem. */
        uint8_t rx[16] = {0};
        spi_transaction_t t = {.length = 128, .rxlength = 128, .rx_buffer = rx};
        esp_err_t e = spi_device_polling_transmit(adc, &t);
        if (e != ESP_OK) return e;
        for (int i = 0; i < 8; i++)
            values[i] = (int16_t)(((uint16_t)rx[i * 2] << 8) | rx[i * 2 + 1]);
        return ESP_OK;
    }
    for (int i = 0; i < 8; i++) {  /* hardware mode: osiem ramek, CS miedzy nimi */
        spi_transaction_t t = {.length = 16, .flags = SPI_TRANS_USE_RXDATA};
        esp_err_t e = spi_device_polling_transmit(adc, &t);
        if (e != ESP_OK) return e;
        values[i] = (int16_t)(((uint16_t)t.rx_data[0] << 8) | t.rx_data[1]);
    }
    return ESP_OK;
}
esp_err_t board_adc(int16_t values[8], uint64_t *t_us) {
    if (!acquisition_running) return ESP_ERR_INVALID_STATE;
    if (xSemaphoreTake(adc_lock, pdMS_TO_TICKS(5)) != pdTRUE) return ESP_ERR_TIMEOUT;
    esp_err_t e = adc_read_owned(values, t_us);
    if (e != ESP_OK) { config_ok = false; adc_reset_needed = true; adc_errors++; }   /* F-04: zanik AD7606B / BUSY */
    xSemaphoreGive(adc_lock); return e;
}
/* M-07 / D-M1-5: SENS_5V tylko razem z bankiem TEST. Bez przekaznikow P05 (M-01) nie ma MEAS_EN ani czekania 25 ms.
 * Przed wlaczeniem zasilania czujnika 100 ms przerwy z mostkiem w dol (jak 6.2-s1). */
esp_err_t board_mode(bool test, bool sensor) {
    if (acquisition_running) return ESP_ERR_INVALID_STATE;
    if (sensor && !test) { board_sensor_off(); return ESP_ERR_INVALID_STATE; }
    board_kill();
    current_sign = 0; reverse_until = 0; drive_ok = true;
    if (!sensor) return board_sensor_off();
    if (!sens_on) { vTaskDelay(pdMS_TO_TICKS(100)); gpio_set_level(GPIO_SENS_EN, 1); sens_on = true; }
    return ESP_OK;
}
esp_err_t board_sensor_off(void) {
    gpio_set_level(GPIO_SENS_EN, 0); sens_on = false;
    return ESP_OK;
}
esp_err_t board_temperature(int ch, float *value, uint8_t *fault) {
    if (!value || !fault) return ESP_ERR_INVALID_ARG;
    *value = NAN; *fault = 255;
    if (ch < 0 || ch > 1) return ESP_ERR_INVALID_ARG;
    if (!tc[ch]) return ESP_ERR_NOT_FOUND;
    /* Read back configuration on every call. Floating/stuck MISO=0 must not
     * become a valid 0 degC measurement; loss of module power resets CR0. */
    uint8_t cfg_tx[3] = {0x00, 0, 0}, cfg_rx[3] = {0};
    spi_transaction_t c = {.length = 24, .tx_buffer = cfg_tx, .rx_buffer = cfg_rx};
    /* A single TEMP task owns tc[0..1]; both CS high during this gap. */
    esp_rom_delay_us(1);
    esp_err_t e = spi_device_polling_transmit(tc[ch], &c);
    if (e != ESP_OK) return e;
    if (cfg_rx[1] != 0x91 || cfg_rx[2] != 0x03) return ESP_ERR_INVALID_RESPONSE;
    /* MAX31856 Rev0 pp18,24-26: 0C LTCBH, 0D LTCBM, 0E LTCBL, 0F SR.
     * Byte zero returned during the address phase is not register data. */
    uint8_t tx[5] = {0x0c, 0, 0, 0, 0}, rx[5] = {0};
    spi_transaction_t t = {.length = 40, .tx_buffer = tx, .rx_buffer = rx};
    esp_rom_delay_us(1);
    e = spi_device_polling_transmit(tc[ch], &t);
    if (e != ESP_OK) return e;
    if (rx[3] & 0x1f) return ESP_ERR_INVALID_RESPONSE;
    *fault = rx[4];
    uint32_t bits = ((uint32_t)rx[1] << 16) | ((uint32_t)rx[2] << 8) | rx[3];
    int32_t raw = (int32_t)(bits >> 5);
    if (raw & 0x40000) raw -= 0x80000;
    if (!*fault) *value = (float)raw / 128.0f;
    return ESP_OK;
}

/* --- M-06: watchdogi -------------------------------------------------------
 * TWDT (esp_task_wdt) pilnuje zadania safety z czasem CONFIG_EGR_DRIVE_WDT_MS i wywoluje panike;
 * RTC WDT (etap 0, reset systemu po CONFIG_EGR_RTC_WDT_MS) dziala takze, gdy zawiedzie panika i MWDT.
 * Oba karmi wylacznie zadanie safety, w kazdym obiegu 1 ms. */
esp_err_t board_watchdogs_start(void) {
    esp_task_wdt_config_t c = {.timeout_ms = CONFIG_EGR_DRIVE_WDT_MS, .idle_core_mask = 0, .trigger_panic = true};
    esp_err_t e = esp_task_wdt_reconfigure(&c);
    if (e == ESP_ERR_INVALID_STATE) e = esp_task_wdt_init(&c);
    if (e == ESP_OK) e = esp_task_wdt_add(NULL);
    if (e != ESP_OK) return e;
    uint32_t ticks = (uint32_t)((uint64_t)CONFIG_EGR_RTC_WDT_MS * rtc_clk_slow_freq_get_hz() / 1000);
    wdt_hal_write_protect_disable(&rtc_wdt);
    wdt_hal_config_stage(&rtc_wdt, WDT_STAGE0, ticks, WDT_STAGE_ACTION_RESET_SYSTEM);
    wdt_hal_enable(&rtc_wdt);
    wdt_hal_write_protect_enable(&rtc_wdt);
    rtc_wdt_on = true;
    watchdogs_ok = true;
    return ESP_OK;
}
bool board_watchdogs_ok(void) { return watchdogs_ok; }
void board_watchdogs_feed(void) {
    esp_task_wdt_reset();
    if (!rtc_wdt_on) return;
    wdt_hal_write_protect_disable(&rtc_wdt); wdt_hal_feed(&rtc_wdt); wdt_hal_write_protect_enable(&rtc_wdt);
}
/* Owiniecie esp_panic_handler (-Wl,--wrap, main/CMakeLists.txt): DRIVE_EN i SENS_EN w dol rejestrami GPIO,
 * zanim panika wypisze zrzut (trwa to dziesiatki ms). PWM idzie przez matryce GPIO i zostaje, ale bez
 * R_EN / L_EN modul IBT-2 jest wylaczony. */
void __real_esp_panic_handler(void *info);
void IRAM_ATTR __wrap_esp_panic_handler(void *info) {
    gpio_ll_set_level(&GPIO, GPIO_DRIVE_EN, 0);
    gpio_ll_set_level(&GPIO, GPIO_SENS_EN, 0);
    __real_esp_panic_handler(info);
}
