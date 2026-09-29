#include "board.h"
#include "control.h"
#include <math.h>
#include <string.h>
#include "driver/gpio.h"
#include "driver/spi_master.h"
#include "driver/i2c.h"
#include "driver/ledc.h"
#include "driver/sdspi_host.h"
#include "esp_timer.h"
#include "esp_rom_sys.h"
#include "esp_vfs_fat.h"
#include "sdmmc_cmd.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"

enum { PWM = 1, ADC_SDI = 2, SCOPE = 38, ARM = 39, HW_ARM = 40, MARK = 41,
       INTERLOCK = 42, HEART = 21, CONVST = 13, BUSY = 14 };

/* MCP23017 port A (wyjścia) */
enum { A_ADC_RESET = 1 << 0, A_MEAS_EN = 1 << 1, A_MEAS_BANK = 1 << 2,
       A_SENSOR_EN = 1 << 3, A_SPARE = 1 << 4, A_INA = 1 << 5, A_INB = 1 << 6,
       A_LED = 1 << 7 };
/* MCP23017 port B (wejścia) */
enum { B_TEST_KEY = 1 << 0, B_SENSOR_FAULT_N = 1 << 1, B_ENA_DIAG = 1 << 2,
       B_ENB_DIAG = 1 << 3, B_LOG_PRESENT_N = 1 << 4, B_TEST_PRESENT = 1 << 5 };

/* --- Rejestry AD7606B w software mode ------------------------------------
 * ZWERYFIKUJ adresy i układ bitów z datasheetem swojej rewizji przed
 * pierwszym uruchomieniem. Sterownik czyta rejestry z powrotem i przy
 * niezgodności przechodzi do hardware mode — to siatka bezpieczeństwa,
 * nie dowód poprawności. Ramka: bit15 = R/W (1 = odczyt), bity 14:8 =
 * adres, bity 7:0 = dane; odczyt wymaga drugiej ramki.                    */
enum { ADC_REG_CONFIG = 0x02, ADC_REG_RANGE_12 = 0x03, ADC_REG_RANGE_34 = 0x04,
       ADC_REG_RANGE_56 = 0x05, ADC_REG_RANGE_78 = 0x06, ADC_REG_BANDWIDTH = 0x07,
       ADC_REG_OVERSAMPLE = 0x08 };
/* Kod zakresu w nibble kanału: 0 = ±2,5 V, 1 = ±5 V, 2 = ±10 V. */
static const uint8_t RANGE_CODE[3] = {0, 1, 2};

static spi_device_handle_t adc, tc[2];
static SemaphoreHandle_t io_lock;
static uint8_t porta;
static bool software_mode;
static int current_sign;
static uint64_t reverse_until;
static bool prev_sensor, prev_test, mcp_ready;

static esp_err_t mcp_write(uint8_t reg, uint8_t value) {
    uint8_t tx[] = {reg, value};
    return i2c_master_write_to_device(I2C_NUM_0, 0x20, tx, 2, pdMS_TO_TICKS(5));
}
static esp_err_t mcp_read(uint8_t reg, uint8_t *value) {
    return i2c_master_write_read_device(I2C_NUM_0, 0x20, &reg, 1, value, 1, pdMS_TO_TICKS(5));
}
static esp_err_t porta_set(uint8_t mask, bool on) {
    uint8_t next = on ? (porta | mask) : (uint8_t)(porta & ~mask);
    if (next == porta && mcp_ready) return ESP_OK;
    esp_err_t e = mcp_write(0x14, next);
    if (e == ESP_OK) porta = next;
    return e;
}
void board_kill(void) {
    gpio_set_level(ARM, 0);
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, 0);
    ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
}
bool board_interlock(void) { return gpio_get_level(INTERLOCK); }
bool board_armed(void) { return gpio_get_level(HW_ARM); }
bool board_mark(void) { return !gpio_get_level(MARK); }
bool board_adc_software_mode(void) { return software_mode; }
void board_heartbeat(bool enabled) {
    static bool level;
    level = enabled ? !level : false;
    gpio_set_level(HEART, level);
}
void board_scope_trigger(void) {
    gpio_set_level(SCOPE, 1); esp_rom_delay_us(20); gpio_set_level(SCOPE, 0);
}
void board_drive(float duty, bool permit) {
    if (!permit || !isfinite(duty) || !board_interlock() || !board_armed()) { board_kill(); return; }
    int sign = duty > 0 ? 1 : duty < 0 ? -1 : 0;
    uint64_t now = esp_timer_get_time();
    if (sign && sign != current_sign) {
        /* Kierunek idzie przez ekspander; zmiana tylko przy zerowym napędzie. */
        board_kill(); current_sign = sign; reverse_until = now + 5000;
        if (xSemaphoreTake(io_lock, pdMS_TO_TICKS(5)) == pdTRUE) {
            uint8_t next = (uint8_t)((porta & ~(A_INA | A_INB)) | (sign > 0 ? A_INA : A_INB));
            if (mcp_write(0x14, next) == ESP_OK) porta = next;
            xSemaphoreGive(io_lock);
        }
    }
    if (now < reverse_until) { board_kill(); return; }
    /* Zezwolenie utrzymujemy w postoju przy duty 0; STOP zdejmuje oba EN. */
    gpio_set_level(ARM, 1);
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0,
                  (uint32_t)(fminf(fabsf(duty), .9f) * 1023));
    ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
}
static esp_err_t adc_frame(uint16_t out, uint16_t *in) {
    spi_transaction_t t = {.length = 16, .flags = SPI_TRANS_USE_TXDATA | SPI_TRANS_USE_RXDATA};
    t.tx_data[0] = out >> 8; t.tx_data[1] = out & 0xff;
    esp_err_t e = spi_device_polling_transmit(adc, &t);
    if (e == ESP_OK && in) *in = ((uint16_t)t.rx_data[0] << 8) | t.rx_data[1];
    return e;
}
static esp_err_t adc_reg_write(uint8_t reg, uint8_t value) {
    return adc_frame((uint16_t)(reg & 0x7f) << 8 | value, NULL);
}
static esp_err_t adc_reg_read(uint8_t reg, uint8_t *value) {
    uint16_t back = 0;
    esp_err_t e = adc_frame(0x8000 | (uint16_t)(reg & 0x7f) << 8, NULL);
    if (e == ESP_OK) e = adc_frame(0x8000 | (uint16_t)(reg & 0x7f) << 8, &back);
    if (e == ESP_OK) *value = back & 0xff;
    return e;
}
esp_err_t board_adc_ranges(const uint8_t range[8]) {
    if (!software_mode) return ESP_ERR_NOT_SUPPORTED;
    static const uint8_t reg[4] = {ADC_REG_RANGE_12, ADC_REG_RANGE_34,
                                   ADC_REG_RANGE_56, ADC_REG_RANGE_78};
    if (xSemaphoreTake(io_lock, pdMS_TO_TICKS(20)) != pdTRUE) return ESP_ERR_TIMEOUT;
    esp_err_t e = ESP_OK;
    for (int pair = 0; pair < 4 && e == ESP_OK; pair++) {
        uint8_t lo = RANGE_CODE[range[pair * 2] % 3], hi = RANGE_CODE[range[pair * 2 + 1] % 3];
        uint8_t want = (uint8_t)(lo | (hi << 4)), back = 0xff;
        e = adc_reg_write(reg[pair], want);
        if (e == ESP_OK) e = adc_reg_read(reg[pair], &back);
        if (e == ESP_OK && back != want) e = ESP_ERR_INVALID_RESPONSE;
    }
    xSemaphoreGive(io_lock);
    return e;
}
/* Próba software mode: zapis i odczyt rejestru oversamplingu. Nieudana
 * weryfikacja zostawia układ w hardware mode z zakresem ±10 V. */
static void adc_try_software(void) {
    gpio_set_level(ADC_SDI, 0);
    uint8_t back = 0xff;
    if (adc_reg_write(ADC_REG_OVERSAMPLE, 0x03) == ESP_OK   /* OS x8 */
        && adc_reg_read(ADC_REG_OVERSAMPLE, &back) == ESP_OK && back == 0x03) {
        software_mode = true;
    }
}
esp_err_t board_init(void) {
    gpio_config_t out = {.pin_bit_mask = (1ULL << ARM) | (1ULL << HEART) | (1ULL << CONVST)
                                       | (1ULL << SCOPE) | (1ULL << ADC_SDI),
                         .mode = GPIO_MODE_OUTPUT};
    ESP_ERROR_CHECK(gpio_config(&out));
    gpio_set_level(ARM, 0); gpio_set_level(HEART, 0); gpio_set_level(CONVST, 0);
    gpio_set_level(SCOPE, 0); gpio_set_level(ADC_SDI, 0);
    gpio_config_t inp = {.pin_bit_mask = (1ULL << HW_ARM) | (1ULL << INTERLOCK) | (1ULL << BUSY),
                         .mode = GPIO_MODE_INPUT};
    ESP_ERROR_CHECK(gpio_config(&inp));
    inp.pin_bit_mask = 1ULL << MARK; inp.pull_up_en = GPIO_PULLUP_ENABLE;
    ESP_ERROR_CHECK(gpio_config(&inp));
    ledc_timer_config_t lt = {.speed_mode = LEDC_LOW_SPEED_MODE, .duty_resolution = LEDC_TIMER_10_BIT,
        .timer_num = LEDC_TIMER_0, .freq_hz = 1000, .clk_cfg = LEDC_AUTO_CLK};
    ESP_ERROR_CHECK(ledc_timer_config(&lt));
    ledc_channel_config_t lc = {.gpio_num = PWM, .speed_mode = LEDC_LOW_SPEED_MODE,
        .channel = LEDC_CHANNEL_0, .timer_sel = LEDC_TIMER_0, .duty = 0};
    ESP_ERROR_CHECK(ledc_channel_config(&lc));
    io_lock = xSemaphoreCreateMutex(); if (!io_lock) return ESP_ERR_NO_MEM;
    i2c_config_t ic = {.mode = I2C_MODE_MASTER, .sda_io_num = 10, .scl_io_num = 15,
        .sda_pullup_en = true, .scl_pullup_en = true, .master.clk_speed = 400000};
    ESP_ERROR_CHECK(i2c_param_config(I2C_NUM_0, &ic));
    ESP_ERROR_CHECK(i2c_driver_install(I2C_NUM_0, I2C_MODE_MASTER, 0, 0, 0));
    /* Zatrzaski portu A ustawiamy przed przełączeniem go na wyjścia. */
    porta = 0;
    ESP_ERROR_CHECK(mcp_write(0x14, 0));
    ESP_ERROR_CHECK(mcp_write(0x00, 0));      /* IODIRA = wyjścia */
    ESP_ERROR_CHECK(mcp_write(0x01, 0xff));   /* IODIRB = wejścia */
    ESP_ERROR_CHECK(mcp_write(0x0d, 0xff));   /* GPPUB  = pull-upy */
    mcp_ready = true;
    ESP_ERROR_CHECK(porta_set(A_ADC_RESET, true)); esp_rom_delay_us(20);
    ESP_ERROR_CHECK(porta_set(A_ADC_RESET, false)); vTaskDelay(pdMS_TO_TICKS(10));
    spi_bus_config_t ab = {.mosi_io_num = ADC_SDI, .miso_io_num = 11, .sclk_io_num = 9,
        .quadwp_io_num = -1, .quadhd_io_num = -1, .max_transfer_sz = 32};
    ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST, &ab, SPI_DMA_CH_AUTO));
    spi_device_interface_config_t ad = {.clock_speed_hz = 8000000, .mode = 2, .spics_io_num = 12,
        .queue_size = 1, .cs_ena_pretrans = 2, .cs_ena_posttrans = 1};
    ESP_ERROR_CHECK(spi_bus_add_device(SPI2_HOST, &ad, &adc));
    adc_try_software();
    spi_bus_config_t sb = {.mosi_io_num = 5, .miso_io_num = 6, .sclk_io_num = 4,
        .quadwp_io_num = -1, .quadhd_io_num = -1, .max_transfer_sz = 8192};
    ESP_ERROR_CHECK(spi_bus_initialize(SPI3_HOST, &sb, SPI_DMA_CH_AUTO));
    for (int i = 0; i < 2; i++) {
        spi_device_interface_config_t t = {.clock_speed_hz = 1000000, .mode = 1,
            .spics_io_num = i ? 16 : 8, .queue_size = 1};
        ESP_ERROR_CHECK(spi_bus_add_device(SPI3_HOST, &t, &tc[i]));
        spi_transaction_t w = {.length = 16, .flags = SPI_TRANS_USE_TXDATA};
        w.tx_data[0] = 0x81; w.tx_data[1] = 0x03;  /* CR1: typ K, bez uśredniania */
        ESP_ERROR_CHECK(spi_device_polling_transmit(tc[i], &w));
        w.tx_data[0] = 0x80; w.tx_data[1] = 0x91;  /* CR0: ciągłe, detekcja OC, 50 Hz */
        ESP_ERROR_CHECK(spi_device_polling_transmit(tc[i], &w));
    }
    twai_general_config_t tg = TWAI_GENERAL_CONFIG_DEFAULT(17, 18, TWAI_MODE_LISTEN_ONLY);
    tg.rx_queue_len = 128; tg.tx_queue_len = 0;
    twai_timing_config_t tt = TWAI_TIMING_CONFIG_500KBITS();
    twai_filter_config_t tf = TWAI_FILTER_CONFIG_ACCEPT_ALL();
    ESP_ERROR_CHECK(twai_driver_install(&tg, &tt, &tf));
    ESP_ERROR_CHECK(twai_start());
    return ESP_OK;
}
esp_err_t board_sd_mount(void) {
    sdmmc_host_t host = SDSPI_HOST_DEFAULT(); host.slot = SPI3_HOST; host.max_freq_khz = 10000;
    sdspi_device_config_t slot = SDSPI_DEVICE_CONFIG_DEFAULT();
    slot.gpio_cs = 7; slot.host_id = SPI3_HOST;
    esp_vfs_fat_sdmmc_mount_config_t mount = {.format_if_mount_failed = false,
        .max_files = 8, .allocation_unit_size = 32768};
    sdmmc_card_t *card = NULL;
    return esp_vfs_fat_sdspi_mount("/sd", &host, &slot, &mount, &card);
}
esp_err_t board_adc(int16_t values[8], uint64_t *t_us) {
    *t_us = esp_timer_get_time();
    gpio_set_level(CONVST, 1); esp_rom_delay_us(1); gpio_set_level(CONVST, 0);
    uint64_t until = *t_us + 200;
    while (gpio_get_level(BUSY)) {
        if ((uint64_t)esp_timer_get_time() > until) return ESP_ERR_TIMEOUT;
    }
    if (software_mode) {
        /* Jedna transakcja 128-bit — w hardware mode to byłby błąd. */
        uint8_t rx[16] = {0};
        spi_transaction_t t = {.length = 128, .rxlength = 128, .rx_buffer = rx};
        esp_err_t e = spi_device_polling_transmit(adc, &t);
        if (e != ESP_OK) return e;
        for (int i = 0; i < 8; i++)
            values[i] = (int16_t)(((uint16_t)rx[i * 2] << 8) | rx[i * 2 + 1]);
        return ESP_OK;
    }
    for (int i = 0; i < 8; i++) {  /* hardware mode: osiem ramek, CS między nimi */
        spi_transaction_t t = {.length = 16, .flags = SPI_TRANS_USE_RXDATA};
        esp_err_t e = spi_device_polling_transmit(adc, &t);
        if (e != ESP_OK) return e;
        values[i] = (int16_t)(((uint16_t)t.rx_data[0] << 8) | t.rx_data[1]);
    }
    return ESP_OK;
}
esp_err_t board_mode(bool test, bool sensor) {
    if (sensor && (!test || !board_interlock())) return ESP_ERR_INVALID_STATE;
    if (test == prev_test && sensor == prev_sensor && (porta & A_MEAS_EN)) return ESP_OK;
    board_kill();
    if (xSemaphoreTake(io_lock, pdMS_TO_TICKS(20)) != pdTRUE) return ESP_ERR_TIMEOUT;
    /* Wszystko w dół, przerwa, dopiero nowy stan — bank i zasilanie czujnika
     * nigdy nie przełączają się „na gorąco". */
    esp_err_t e = mcp_write(0x14, 0);
    if (e == ESP_OK) { porta = 0; vTaskDelay(pdMS_TO_TICKS(100));
        e = porta_set((uint8_t)(A_MEAS_EN | (test ? A_MEAS_BANK : 0)), true);
    }
    if (e == ESP_OK && sensor) { vTaskDelay(pdMS_TO_TICKS(100)); e = porta_set(A_SENSOR_EN, true); }
    xSemaphoreGive(io_lock);
    if (e == ESP_OK) { prev_test = test; prev_sensor = sensor; }
    else { porta = 0; board_kill(); }
    return e;
}
esp_err_t board_inputs(bool *sensor_fault, bool *log_present, bool *test_present) {
    if (xSemaphoreTake(io_lock, pdMS_TO_TICKS(5)) != pdTRUE) return ESP_ERR_TIMEOUT;
    uint8_t b = 0; esp_err_t e = mcp_read(0x13, &b);
    xSemaphoreGive(io_lock);
    if (e != ESP_OK) { *sensor_fault = true; *log_present = true; *test_present = false; return e; }
    *sensor_fault = !(b & B_SENSOR_FAULT_N);
    *log_present = !(b & B_LOG_PRESENT_N);   /* krańcówki NC rozwierane wtykiem */
    *test_present = (b & B_TEST_PRESENT) != 0;
    return ESP_OK;
}
esp_err_t board_temperature(int ch, float *value, uint8_t *fault) {
    if (ch < 0 || ch > 1) return ESP_ERR_INVALID_ARG;
    uint8_t tx[6] = {0x0a, 0, 0, 0, 0, 0}, rx[6] = {0};
    spi_transaction_t t = {.length = 48, .tx_buffer = tx, .rx_buffer = rx};
    esp_err_t e = spi_device_polling_transmit(tc[ch], &t);
    if (e != ESP_OK) return e;
    /* Rejestry 0A CJTL, 0B LTCBH, 0C LTCBM, 0D LTCBL, 0E SR. */
    int32_t raw = ((int32_t)rx[2] << 16) | ((int32_t)rx[3] << 8) | rx[4];
    if (raw & 0x800000) raw |= (int32_t)0xff000000;
    *fault = rx[5];
    *value = *fault ? NAN : (float)(raw >> 5) / 128.0f;
    return ESP_OK;
}
