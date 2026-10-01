
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
typedef int esp_err_t;
enum {ESP_OK=0,ESP_ERR_TIMEOUT=1,ESP_ERR_INVALID_STATE=2,ESP_ERR_INVALID_ARG=3};
enum {RANGE_2V5=0,RANGE_5V=1,RANGE_10V=2,RANGE_UNKNOWN=255};
enum {ADC_REG_CONFIG=2,ADC_REG_OVERSAMPLE=8,ADC_REG_RANGE_12=3,ADC_REG_EXIT=0};
#define ADC_CONFIG_VALUE 0
#define ADC_OVERSAMPLE_X8 3
#define pdMS_TO_TICKS(x) (x)
#define pdTRUE 1
static const uint8_t RANGE_CODE[]={0,1,2};
static bool software_mode=true,acquisition_running,config_ok=true;
static uint8_t applied_range[8];static int adc_lock,lock_ok=1,fail_at=-1,calls,exit_calls,releases,exit_error;
static int xSemaphoreTake(int a,int b){(void)a;(void)b;return lock_ok;}
static void xSemaphoreGive(int a){(void)a;releases++;}
static int adc_reg_write_verified(int a,int b){(void)a;(void)b;return ++calls==fail_at?1:0;}
static int adc_reg_write(int a,int b){(void)a;(void)b;exit_calls++;return exit_error;}
/* 6.2-s1 F-04: po bledzie odczytu konfiguracja zaczyna od pelnego RESET (adc_full_reset: MCP GPA0 + 2100 ms). */
static bool adc_reset_needed;static int resets,reset_error,calls_at_reset=-1;
static int adc_full_reset(void){resets++;calls_at_reset=calls;return reset_error;}
esp_err_t board_adc_ranges(const uint8_t requested[8], uint8_t applied[8]) {
    memset(applied, RANGE_UNKNOWN, 8);
    if (acquisition_running) { config_ok = false; return ESP_ERR_INVALID_STATE; }
    config_ok = false;
    if (adc_reset_needed) {                                 /* 6.2-s1 F-04: po bledzie odczytu nowy rozruch */
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
    } else memset(applied_range, RANGE_UNKNOWN, 8);
    xSemaphoreGive(adc_lock);
    return e;
}
#define CHECK(x) do{checks++;if(!(x)){printf("FAIL %d: %s\n",__LINE__,#x);return 1;}}while(0)
int main(void){int checks=0;uint8_t req[8]={2,2,1,2,0,1,2,2},out[8];
memset(out,42,8);lock_ok=0;CHECK(board_adc_ranges(req,out)!=ESP_OK);CHECK(!config_ok);
for(int j=0;j<8;j++)CHECK(out[j]==RANGE_UNKNOWN);
lock_ok=1;acquisition_running=true;config_ok=true;CHECK(board_adc_ranges(req,out)!=ESP_OK);CHECK(!config_ok);acquisition_running=false;
for(int fail=1;fail<=6;fail++){calls=exit_calls=0;fail_at=fail;config_ok=true;CHECK(board_adc_ranges(req,out)!=ESP_OK);CHECK(!config_ok);CHECK(exit_calls==1);for(int j=0;j<8;j++)CHECK(out[j]==RANGE_UNKNOWN);}
fail_at=-1;calls=0;exit_error=1;CHECK(board_adc_ranges(req,out)!=ESP_OK);CHECK(!config_ok);exit_error=0;
calls=0;CHECK(board_adc_ranges(req,out)==ESP_OK);CHECK(config_ok);CHECK(!memcmp(req,out,8));CHECK(calls==6);
CHECK(resets==0);
adc_reset_needed=true;calls=0;CHECK(board_adc_ranges(req,out)==ESP_OK);CHECK(resets==1);CHECK(calls_at_reset==0);CHECK(!adc_reset_needed);CHECK(config_ok);
adc_reset_needed=true;reset_error=1;calls=0;config_ok=true;CHECK(board_adc_ranges(req,out)!=ESP_OK);CHECK(!config_ok);CHECK(calls==0);CHECK(adc_reset_needed);
for(int j=0;j<8;j++)CHECK(out[j]==RANGE_UNKNOWN);reset_error=0;adc_reset_needed=false;
software_mode=false;CHECK(board_adc_ranges(req,out)==ESP_OK);for(int j=0;j<8;j++)CHECK(out[j]==RANGE_10V);
printf("ADC fault injection: %d assertions OK\n",checks);return 0;}
