"""Reviewable patch against the frozen baseline; never edits an existing project revision."""
from pathlib import Path
import hashlib,json,difflib
P=Path(__file__).resolve().parents[1];out=P/'firmware';out.mkdir(exist_ok=True)
old=(P/'reference/board.c').read_text(encoding='utf-8');s=old
start=s.index('esp_err_t board_temperature(');end=s.index('\n}',start)+2
function='''esp_err_t board_temperature(int ch, float *value, uint8_t *fault) {
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
}'''
s=s[:start]+function+s[end:]
s=s.replace('.spics_io_num = i ? 16 : 8, .queue_size = 1};','.spics_io_num = i ? 16 : 8, .queue_size = 1,\n            .cs_ena_pretrans = 2, .cs_ena_posttrans = 2};')
needle='        ESP_ERROR_CHECK(spi_device_polling_transmit(tc[i], &w));\n    }\n    #endif\n    #if CONFIG_EGR_CAN_PRESENT'
assert needle in s
s=s.replace(needle,'        ESP_ERROR_CHECK(spi_device_polling_transmit(tc[i], &w));\n    }\n    /* First 50 Hz conversion plus open-circuit check; no valid sample before this. */\n    vTaskDelay(pdMS_TO_TICKS(300));\n    #endif\n    #if CONFIG_EGR_CAN_PRESENT')
(out/'board.c').write_text(s,encoding='utf-8')
(out/'P09-temperature.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='a/firmware/main/board.c',tofile='b/firmware/main/board.c')),encoding='utf-8')
(out/'baseline.json').write_text(json.dumps({'baseline':'EGRLab-v6.1-rc1/firmware/main/board.c','sha256':hashlib.sha256((P/'reference/board.c').read_bytes()).hexdigest(),'changes':'Temperature register map, configuration readback, invalid-value initialization, signed conversion, SPI CS timing and startup delay only. Does not integrate P05/P08 pending changes.'},indent=2))
print('P09 temperature patch written; baseline untouched')
