#include "board.h"
#include "control.h"
#include "sdkconfig.h"
#ifndef CONFIG_EGR_TEST_CURRENT_PRESENT
#define CONFIG_EGR_TEST_CURRENT_PRESENT 0
#endif
#ifndef CONFIG_EGR_LOG_CURRENT_PRESENT
#define CONFIG_EGR_LOG_CURRENT_PRESENT 0
#endif
#include <math.h>
#include <string.h>
#include <stdatomic.h>
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

enum { PWM = 1, ADC_SDI = 2, SCOPE = 41, ARM = 39, HW_ARM = 40, CURRENT_CS = 38,
       INTERLOCK = 42, HEART = 21, CONVST = 13, BUSY = 14 };

/* MCP23017 port A (wyjscia) */
enum { A_ADC_RESET = 1 << 0, A_MEAS_EN = 1 << 1, A_MEAS_BANK = 1 << 2,
       A_SENSOR_EN = 1 << 3, A_LOGGER_CURRENT_OK = 1 << 4, A_INA = 1 << 5, A_INB = 1 << 6,
       A_LED = 1 << 7 };
/* MCP23017 port B (wejscia) */
enum { B_TEST_KEY = 1 << 0, B_SENSOR_FAULT_N = 1 << 1, B_ENA_DIAG = 1 << 2,
       B_ENB_DIAG = 1 << 3, B_LOG_PRESENT_N = 1 << 4, B_TEST_PRESENT = 1 << 5, B_MARK_N = 1 << 6 };

/* --- AD7606B: dostep do rejestrow --------------------------------------
 * ZWERYFIKUJ z datasheetem swojej rewizji przed pierwszym uruchomieniem.
 * Ramka 16-bit: bity 15:14 = 01 dla odczytu, 00 dla zapisu; bity 13:8 =
 * szesciobitowy adres; bity 7:0 = dane. Odczyt wymaga drugiej ramki.
 * Wejscie w tryb rejestrow wymaga ZWOREK OS[2:0] = 111 na plytce; samo SPI
 * go nie wlaczy. Zapis pod adres 0x00 wraca do strumienia danych.
 * Kazdy zapis jest weryfikowany odczytem, a niepowodzenie JEST BLEDEM:
 * blokuje TEST i trafia do kazdego rekordu jako adc_config_ok = false.
 * v2 mialo w tym miejscu cichy fallback, ktory zostawial bledna skale. */
enum { ADC_REG_EXIT = 0x00, ADC_REG_STATUS = 0x01, ADC_REG_CONFIG = 0x02,
       ADC_REG_RANGE_12 = 0x03, ADC_REG_RANGE_34 = 0x04, ADC_REG_RANGE_56 = 0x05,
       ADC_REG_RANGE_78 = 0x06, ADC_REG_BANDWIDTH = 0x07, ADC_REG_OVERSAMPLE = 0x08 };
#define ADC_READ_FLAG    0x4000
#define ADC_CONFIG_VALUE 0x00   /* jedna linia DOUTA, bez statusu w ramce */
#define ADC_OVERSAMPLE_X8 0x03

/* Kod zakresu w nibble kanalu: 0 = +-2,5 V, 1 = +-5 V, 2 = +-10 V. */
static const uint8_t RANGE_CODE[3] = {0, 1, 2};

static spi_device_handle_t adc, tc[2], current_adc;
static _Atomic bool mark_pressed, logger_current_ok;
static _Atomic uint32_t last_inputs_time;
static SemaphoreHandle_t io_lock, adc_lock;
static portMUX_TYPE gate_mux = portMUX_INITIALIZER_UNLOCKED;
static bool inhibited = true;
static uint32_t gate_epoch;
static uint8_t porta;
static bool software_mode;
static _Atomic bool config_ok, drive_ok = true;
static volatile bool acquisition_running;
static uint8_t applied_range[8];
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
void board_inhibit(bool stop) {
    portENTER_CRITICAL(&gate_mux);
    inhibited = stop;
    if (stop) gpio_set_level(ARM, 0);
    portEXIT_CRITICAL(&gate_mux);
}
uint32_t board_stop_token(void) {
    portENTER_CRITICAL(&gate_mux); uint32_t v=gate_epoch; portEXIT_CRITICAL(&gate_mux); return v;
}
void board_emergency_stop(void) {
    portENTER_CRITICAL(&gate_mux); gate_epoch++; inhibited=true; gpio_set_level(ARM,0); portEXIT_CRITICAL(&gate_mux);
    board_kill();
}
bool board_release(uint32_t token) {
    portENTER_CRITICAL(&gate_mux); bool ok=token==gate_epoch;
    if(ok) inhibited=false;
    portEXIT_CRITICAL(&gate_mux); return ok;
}
void board_kill(void) {
    portENTER_CRITICAL(&gate_mux);
    gpio_set_level(ARM, 0);
    portEXIT_CRITICAL(&gate_mux);
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, 0);
    ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
}
bool board_interlock(void) { return gpio_get_level(INTERLOCK); }
bool board_armed(void) { return gpio_get_level(HW_ARM); }
bool board_mark(void) { return mark_pressed; }
bool board_local_current_present(bool test) {
    if (test) return CONFIG_EGR_TEST_CURRENT_PRESENT && board_interlock();
    uint32_t now=(uint32_t)esp_timer_get_time(), stamp=last_inputs_time;
    return CONFIG_EGR_LOG_CURRENT_PRESENT && logger_current_ok && (uint32_t)(now-stamp)<100000;
}
bool board_adc_software_mode(void) { return software_mode; }
bool board_adc_config_ok(void) { return config_ok; }
bool board_drive_ok(void) { return drive_ok; }
void board_adc_set_running(bool running) { acquisition_running = running; }
void board_adc_current_ranges(uint8_t out[8]) { memcpy(out, applied_range, 8); }
void board_heartbeat(bool enabled) {
    static bool level;
    level = enabled ? !level : false;
    gpio_set_level(HEART, level);
}
void board_scope_trigger(void) {
    gpio_set_level(SCOPE, 1); esp_rom_delay_us(20); gpio_set_level(SCOPE, 0);
}
/* Kierunek idzie przez ekspander. Stan zapamietujemy DOPIERO po potwierdzonym
 * zapisie; nieudany zapis zostawia drive_ok = false, co konczy proby FAULT-em
 * (v2 ustawialo znak przed zapisem i moglo jechac starym kierunkiem). */
void board_drive(float duty, bool permit) {
    if (!permit || !isfinite(duty) || !board_interlock() || !board_armed()) { board_kill(); return; }
    int sign = duty > 0 ? 1 : duty < 0 ? -1 : 0;
    uint64_t now = esp_timer_get_time();
    if (sign && sign != current_sign) {
        board_kill();
        if (xSemaphoreTake(io_lock, pdMS_TO_TICKS(5)) != pdTRUE) { drive_ok = false; return; }
        uint8_t next = (uint8_t)((porta & ~(A_INA | A_INB)) | (sign > 0 ? A_INA : A_INB));
        esp_err_t e = mcp_write(0x14, next);
        xSemaphoreGive(io_lock);
        if (e != ESP_OK) { drive_ok = false; board_kill(); return; }
        porta = next; current_sign = sign; reverse_until = esp_timer_get_time() + 5000;
        return;                       /* pelne 5 ms przerwy liczone od potwierdzenia */
    }
    if (now < reverse_until) { board_kill(); return; }
    /* Zezwolenie utrzymujemy w postoju przy duty 0; STOP zdejmuje oba EN. */
    portENTER_CRITICAL(&gate_mux);
    if (!inhibited) gpio_set_level(ARM, 1);
    portEXIT_CRITICAL(&gate_mux);
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
esp_err_t board_adc_ranges(const uint8_t requested[8], uint8_t applied[8]) {
    memset(applied, RANGE_UNKNOWN, 8);
    if (acquisition_running) { config_ok = false; return ESP_ERR_INVALID_STATE; }
    config_ok = false;
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
    } else memset(applied_range, RANGE_UNKNOWN, 8);
    xSemaphoreGive(adc_lock);
    return e;
}
/* Wejscie w tryb rejestrow zalezy od zworek OS[2:0] = 111. Sprawdzamy to
 * zapisem i odczytem; wynik jest jawny, nie zgadywany. */
static void adc_probe_software_mode(void) {
    gpio_set_level(ADC_SDI, 0);
#if CONFIG_EGR_ADC_SOFTWARE_MODE
    software_mode = true;
    esp_err_t e = adc_reg_write_verified(ADC_REG_CONFIG, ADC_CONFIG_VALUE);
    if (e == ESP_OK) e = adc_reg_write_verified(ADC_REG_OVERSAMPLE, ADC_OVERSAMPLE_X8);
    if (e == ESP_OK) e = adc_reg_write(ADC_REG_EXIT, 0);
    config_ok = (e == ESP_OK);
#else
    software_mode = false;
    config_ok = true;                 /* tryb sprzetowy nie ma czego potwierdzac */
#endif
    for (int i = 0; i < 8; i++) applied_range[i] = RANGE_10V;
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
    /* MARK moved to MCP GPB6. GPIO41 is now the scope output. */
    ledc_timer_config_t lt = {.speed_mode = LEDC_LOW_SPEED_MODE, .duty_resolution = LEDC_TIMER_10_BIT,
        .timer_num = LEDC_TIMER_0, .freq_hz = 1000, .clk_cfg = LEDC_AUTO_CLK};
    ESP_ERROR_CHECK(ledc_timer_config(&lt));
    ledc_channel_config_t lc = {.gpio_num = PWM, .speed_mode = LEDC_LOW_SPEED_MODE,
        .channel = LEDC_CHANNEL_0, .timer_sel = LEDC_TIMER_0, .duty = 0};
    ESP_ERROR_CHECK(ledc_channel_config(&lc));
    io_lock = xSemaphoreCreateMutex();
    adc_lock = xSemaphoreCreateMutex(); configASSERT(adc_lock); if (!io_lock) return ESP_ERR_NO_MEM;
    i2c_config_t ic = {.mode = I2C_MODE_MASTER, .sda_io_num = 10, .scl_io_num = 15,
        .sda_pullup_en = true, .scl_pullup_en = true, .master.clk_speed = 400000};
    ESP_ERROR_CHECK(i2c_param_config(I2C_NUM_0, &ic));
    ESP_ERROR_CHECK(i2c_driver_install(I2C_NUM_0, I2C_MODE_MASTER, 0, 0, 0));
    /* Zatrzaski portu A ustawiamy przed przelaczeniem go na wyjscia. */
    porta = 0; current_sign = 0;
    ESP_ERROR_CHECK(mcp_write(0x14, 0));
    ESP_ERROR_CHECK(mcp_write(0x00, 0x10));   /* GPA4 input; GPA7/GPB7 always outputs */
    ESP_ERROR_CHECK(mcp_write(0x01, 0x7f));   /* B7 output unused: avoid MCP23017 input erratum */
    ESP_ERROR_CHECK(mcp_write(0x0d, 0x4e));   /* only open-drain fault pins; B0/B4/B5/B6 external pull-downs */
    mcp_ready = true;
    ESP_ERROR_CHECK(porta_set(A_ADC_RESET, true)); esp_rom_delay_us(20);
    ESP_ERROR_CHECK(porta_set(A_ADC_RESET, false)); vTaskDelay(pdMS_TO_TICKS(10));
    spi_bus_config_t ab = {.mosi_io_num = ADC_SDI, .miso_io_num = 11, .sclk_io_num = 9,
        .quadwp_io_num = -1, .quadhd_io_num = -1, .max_transfer_sz = 32};
    ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST, &ab, SPI_DMA_CH_AUTO));
    spi_device_interface_config_t ad = {.clock_speed_hz = CONFIG_EGR_ADC_SPI_HZ, .mode = 2, .spics_io_num = 12,
        .queue_size = 1, .cs_ena_pretrans = 2, .cs_ena_posttrans = 1};
    ESP_ERROR_CHECK(spi_bus_add_device(SPI2_HOST, &ad, &adc));
    #if !CONFIG_EGR_CORE_ONLY
    adc_probe_software_mode();
#endif
    spi_device_interface_config_t ci = {.clock_speed_hz=500000,.mode=0,.spics_io_num=CURRENT_CS,
        .queue_size=1,.cs_ena_pretrans=1,.cs_ena_posttrans=1};
    ESP_ERROR_CHECK(spi_bus_add_device(SPI2_HOST,&ci,&current_adc));
    /* Local MCP1525 + 4.7uF settling budget; qualify VREF on the built module. */
    vTaskDelay(pdMS_TO_TICKS(100));
    spi_bus_config_t sb = {.mosi_io_num = 5, .miso_io_num = 6, .sclk_io_num = 4,
        .quadwp_io_num = -1, .quadhd_io_num = -1, .max_transfer_sz = 8192};
    ESP_ERROR_CHECK(spi_bus_initialize(SPI3_HOST, &sb, SPI_DMA_CH_AUTO));
    #if CONFIG_EGR_TEMP_PRESENT
    for (int i = 0; i < 2; i++) {
        spi_device_interface_config_t t = {.clock_speed_hz = 1000000, .mode = 1,
            .spics_io_num = i ? 16 : 8, .queue_size = 1};
        ESP_ERROR_CHECK(spi_bus_add_device(SPI3_HOST, &t, &tc[i]));
        spi_transaction_t w = {.length = 16, .flags = SPI_TRANS_USE_TXDATA};
        w.tx_data[0] = 0x81; w.tx_data[1] = 0x03;  /* CR1: typ K, bez usredniania */
        ESP_ERROR_CHECK(spi_device_polling_transmit(tc[i], &w));
        w.tx_data[0] = 0x80; w.tx_data[1] = 0x91;  /* CR0: ciagle, detekcja OC, 50 Hz */
        ESP_ERROR_CHECK(spi_device_polling_transmit(tc[i], &w));
    }
    #endif
    #if CONFIG_EGR_CAN_PRESENT
    twai_general_config_t tg = TWAI_GENERAL_CONFIG_DEFAULT(17, 18, TWAI_MODE_LISTEN_ONLY);
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
    slot.gpio_cs = 7; slot.host_id = SPI3_HOST;
    esp_vfs_fat_sdmmc_mount_config_t mount = {.format_if_mount_failed = false,
        .max_files = 8, .allocation_unit_size = 32768};
    sdmmc_card_t *card = NULL;
    return esp_vfs_fat_sdspi_mount("/sd", &host, &slot, &mount, &card);
}
static esp_err_t adc_read_owned(int16_t values[8], uint64_t *t_us) {
    *t_us = esp_timer_get_time();
    gpio_set_level(CONVST, 1);
    /* OS x8 in software mode leaves enough time to observe BUSY assertion.
     * A disconnected/stuck-low BUSY must not turn old SPI words into fresh data. */
    if(software_mode && !gpio_get_level(BUSY)) { gpio_set_level(CONVST,0); return ESP_ERR_INVALID_RESPONSE; }
    esp_rom_delay_us(1); gpio_set_level(CONVST, 0);
    uint64_t until = *t_us + 200;
    while (gpio_get_level(BUSY)) {
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
static void current_read(uint64_t origin, local_current_t *out) {
    *out=(local_current_t){.raw=65535,.status=CURRENT_ABSENT};
    if(!board_local_current_present(prev_test)) return;
    uint64_t begin=esp_timer_get_time();
    spi_transaction_t t={.length=16,.flags=SPI_TRANS_USE_RXDATA};
    esp_err_t e=spi_device_polling_transmit(current_adc,&t);
    uint64_t end=esp_timer_get_time();
    if(e!=ESP_OK) {out->status=CURRENT_BUS_ERROR;return;}
    uint16_t word=((uint16_t)t.rx_data[0]<<8)|t.rx_data[1];
    out->raw=(word>>1)&0x0fff;
    if(begin<origin || end<begin || end-origin>400 || end-begin>100) {out->status=CURRENT_TIMING;return;}
    out->begin_us=(uint16_t)(begin-origin);out->end_us=(uint16_t)(end-origin);
    if(word&0x2000) out->status=CURRENT_BUS_ERROR; /* NULL bit must be zero */
    else if(out->raw<4 || out->raw>4091) out->status=CURRENT_SATURATED;
    else out->status=CURRENT_OK;
}
esp_err_t board_adc(int16_t values[8], uint64_t *t_us, local_current_t *current) {
    if (!acquisition_running) return ESP_ERR_INVALID_STATE;
    if (xSemaphoreTake(adc_lock, pdMS_TO_TICKS(5)) != pdTRUE) return ESP_ERR_TIMEOUT;
    esp_err_t e = adc_read_owned(values, t_us);
    if(e==ESP_OK) current_read(*t_us,current);
    xSemaphoreGive(adc_lock); return e;
}
esp_err_t board_mode(bool test, bool sensor) {
    if (acquisition_running) return ESP_ERR_INVALID_STATE;
    if (sensor && (!test || !board_interlock())) return ESP_ERR_INVALID_STATE;
    if (test == prev_test && sensor == prev_sensor && (porta & A_MEAS_EN)) return ESP_OK;
    board_kill();
    if (xSemaphoreTake(io_lock, pdMS_TO_TICKS(20)) != pdTRUE) return ESP_ERR_TIMEOUT;
    /* Wszystko w dol, przerwa, dopiero nowy stan. Wyzerowanie portu kasuje
     * takze zapamietany kierunek — inaczej po STOP -> TEST to samo zadanie
     * znaku pominieto by ustawienie INA/INB i oba zostalyby nisko. */
    esp_err_t e = mcp_write(0x14, 0);
    if (e == ESP_OK) {
        porta = 0; current_sign = 0; reverse_until = 0; drive_ok = true;
        vTaskDelay(pdMS_TO_TICKS(100));
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
    uint8_t b=0,a=0; esp_err_t e=mcp_read(0x13,&b);
    if(e==ESP_OK) e=mcp_read(0x12,&a);
    logger_current_ok=e==ESP_OK && (a&A_LOGGER_CURRENT_OK);
    mark_pressed=e==ESP_OK && !(b&B_MARK_N);
    last_inputs_time=e==ESP_OK?(uint64_t)esp_timer_get_time():0;
    xSemaphoreGive(io_lock);
    if (e != ESP_OK) { *sensor_fault = true; *log_present = true; *test_present = false; return e; }
    *sensor_fault = !(b & B_SENSOR_FAULT_N);
    *log_present = !(b & B_LOG_PRESENT_N);   /* HIGH = empty NC diagnostic chain; external 10k pull-down */
    *test_present = (b & B_TEST_PRESENT) != 0;
    return ESP_OK;
}
esp_err_t board_temperature(int ch, float *value, uint8_t *fault) {
    if (ch < 0 || ch > 1) return ESP_ERR_INVALID_ARG;
    if(!tc[ch]) return ESP_ERR_NOT_FOUND;
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
