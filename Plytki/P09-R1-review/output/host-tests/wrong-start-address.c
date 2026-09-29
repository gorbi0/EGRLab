
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#define NAN (0.0f/0.0f)
static float fabsf(float x){return x<0?-x:x;}
static void esp_rom_delay_us(unsigned x){(void)x;}
#include <assert.h>
#include <stdlib.h>
#undef assert
#define assert(x) do { if (!(x)) { fprintf(stderr,"check failed at line %d\n",__LINE__); exit(2); } } while (0)
typedef int esp_err_t;
#define ESP_OK 0
#define ESP_ERR_INVALID_ARG 1
#define ESP_ERR_NOT_FOUND 2
#define ESP_ERR_INVALID_RESPONSE 3
typedef struct {int length; const void *tx_buffer;void *rx_buffer;} spi_transaction_t;
static int tc[2]={1,2}, fail_at=0,calls=0;
static uint8_t cfg0=0x91,cfg1=3,data[4]={1,0x90,0,0};
int spi_device_polling_transmit(int device,spi_transaction_t *t){
 const uint8_t *tx=t->tx_buffer;uint8_t *rx=t->rx_buffer;
 assert(device==1||device==2);calls++;
 if(calls==fail_at)return 99;
 if(t->length==24){assert(tx[0]==0x00);rx[1]=cfg0;rx[2]=cfg1;}
 else {assert(t->length==40);assert(tx[0]==0x0c);memcpy(rx+1,data,4);}
 return 0;
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
    uint8_t tx[5] = {0x0b, 0, 0, 0, 0}, rx[5] = {0};
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
static int tests=0;
static void check(int ch,int expected,float temp,int flt){
 float value=123;uint8_t fault=88;calls=0;
 int rc=board_temperature(ch,&value,&fault);
 assert(rc==expected);assert(fault==flt);
 if(flt || rc)assert(value!=value);else assert(fabsf(value-temp)<0.00001f);
 tests++;
}
int main(void){
 check(0,0,25,0);check(1,0,25,0);
 data[0]=0xff;data[1]=0x58;data[2]=0;check(0,0,-10.5f,0);
 data[0]=0;data[1]=0;data[2]=0;check(0,0,0,0);
 data[2]=0x20;check(0,0,0.0078125f,0);
 data[0]=0x7f;data[1]=0xff;data[2]=0xe0;check(0,0,2047.9921875f,0);
 data[0]=0x80;data[1]=0;data[2]=0;check(0,0,-2048,0);
 data[0]=1;data[1]=0x90;data[2]=0;
 for(int i=0;i<8;i++){data[3]=(uint8_t)(1u<<i);check(0,0,0,data[3]);}
 data[3]=0;cfg0=0;cfg1=0;check(0,3,0,255);
 cfg0=0xff;cfg1=0xff;check(0,3,0,255);
 cfg0=0;cfg1=3;check(0,3,0,255);
 cfg0=0x91;cfg1=2;check(0,3,0,255);cfg1=3;
 data[2]=1;check(0,3,0,255);data[2]=0;
 fail_at=1;check(0,99,0,255);fail_at=2;check(0,99,0,255);fail_at=0;
 check(-1,1,0,255);check(2,1,0,255);tc[1]=0;check(1,2,0,255);
 uint8_t f;float v;assert(board_temperature(0,0,&f)==1);assert(board_temperature(0,&v,0)==1);tests+=2;
 printf("PASS %d actual-function cases\n",tests);return 0;
}
