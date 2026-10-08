"""Compile the actual board_adc_ranges function with fault-injection stubs.
No ESP32 timing or electronics are simulated. Requires a host C compiler.
python tests/probe_adc.py --cc gcc --out verification
"""
import argparse,subprocess
from pathlib import Path

def function(text,name):
    start=text.index('esp_err_t '+name+'(');begin=text.index('{',start);depth=1;i=begin+1
    while depth:
        depth+=(text[i]=='{')-(text[i]=='}');i+=1
    return text[start:i]

PRE=r'''
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
/* F-04: po bledzie odczytu konfiguracja zaczyna od pelnego RESET (6.3-m1 M-02: adc_full_reset = GPIO10 + 2100 ms).
 * 6.3-m1 M-11: nieudana konfiguracja (np. AD7606B bez zasilania przy samym USB) tez wymaga pelnego RESET. */
static bool adc_reset_needed;static int resets,reset_error,calls_at_reset=-1;
static int adc_full_reset(void){resets++;calls_at_reset=calls;return reset_error;}
'''
POST=r'''
#define CHECK(x) do{checks++;if(!(x)){printf("FAIL %d: %s\n",__LINE__,#x);return 1;}}while(0)
int main(void){int checks=0;uint8_t req[8]={2,2,1,2,0,1,2,2},out[8];
memset(out,42,8);lock_ok=0;CHECK(board_adc_ranges(req,out)!=ESP_OK);CHECK(!config_ok);
for(int j=0;j<8;j++)CHECK(out[j]==RANGE_UNKNOWN);
lock_ok=1;acquisition_running=true;config_ok=true;CHECK(board_adc_ranges(req,out)!=ESP_OK);CHECK(!config_ok);acquisition_running=false;
for(int fail=1;fail<=6;fail++){calls=exit_calls=0;fail_at=fail;config_ok=true;adc_reset_needed=false;CHECK(board_adc_ranges(req,out)!=ESP_OK);CHECK(!config_ok);CHECK(exit_calls==1);CHECK(adc_reset_needed);for(int j=0;j<8;j++)CHECK(out[j]==RANGE_UNKNOWN);}
fail_at=-1;calls=0;exit_error=1;adc_reset_needed=false;CHECK(board_adc_ranges(req,out)!=ESP_OK);CHECK(!config_ok);CHECK(adc_reset_needed);exit_error=0;
adc_reset_needed=false;resets=0;
calls=0;CHECK(board_adc_ranges(req,out)==ESP_OK);CHECK(config_ok);CHECK(!memcmp(req,out,8));CHECK(calls==6);
CHECK(resets==0);
adc_reset_needed=true;calls=0;CHECK(board_adc_ranges(req,out)==ESP_OK);CHECK(resets==1);CHECK(calls_at_reset==0);CHECK(!adc_reset_needed);CHECK(config_ok);
adc_reset_needed=true;reset_error=1;calls=0;config_ok=true;CHECK(board_adc_ranges(req,out)!=ESP_OK);CHECK(!config_ok);CHECK(calls==0);CHECK(adc_reset_needed);
for(int j=0;j<8;j++)CHECK(out[j]==RANGE_UNKNOWN);reset_error=0;adc_reset_needed=false;
software_mode=false;CHECK(board_adc_ranges(req,out)==ESP_OK);for(int j=0;j<8;j++)CHECK(out[j]==RANGE_10V);
printf("ADC fault injection: %d assertions OK\n",checks);return 0;}
'''

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cc',default='gcc');p.add_argument('--out',type=Path,default=Path('verification'));a=p.parse_args()
    a.out.mkdir(exist_ok=True,parents=True);source=Path(__file__).parents[1]/'firmware/main/board.c'
    c=a.out/'adc_fault_probe.c';c.write_text(PRE+function(source.read_text(encoding='utf-8'),'board_adc_ranges')+POST,encoding='utf-8')
    exe=a.out/'adc_fault_probe.exe';subprocess.run([a.cc,str(c),'-o',str(exe)],check=True)
    result=subprocess.run([str(exe.resolve())],check=True,capture_output=True,text=True)
    (a.out/'adc-fault-results.txt').write_text(result.stdout,encoding='utf-8');print(result.stdout,end='')
