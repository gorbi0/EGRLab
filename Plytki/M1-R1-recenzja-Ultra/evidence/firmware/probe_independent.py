"""Independent probes: extract actual functions, stub only platform and scheduling.
No write is made to the package under review. Output is confined to this directory.
"""
from pathlib import Path
import hashlib, json, subprocess, shutil, os

OUT = Path(__file__).resolve().parent
PKG = Path(os.environ['EGR_REVIEW_SOURCE'])/'Rewizje/EGRLab-v6.3-m1'
CWD = OUT.parents[1]
CC = Path(os.environ['EGR_REVIEW_TCC'])
MAIN = PKG/'firmware/main'

def function(text, signature):
    start = text.index(signature)
    brace = text.index('{', start)
    depth = 0
    for i in range(brace, len(text)):
        if text[i] == '{': depth += 1
        elif text[i] == '}':
            depth -= 1
            if not depth: return text[start:i+1]+'\n'
    raise ValueError(signature)

app=(MAIN/'app_main.c').read_text(encoding='utf-8')
board=(MAIN/'board.c').read_text(encoding='utf-8')
inc=OUT/'include'; inc.mkdir(exist_ok=True)
shutil.copyfile(PKG/'verification/host-tcc-include/math.h',inc/'math.h')
with (inc/'math.h').open('a',encoding='utf-8') as f:
    f.write('\n/* Review-local helpers for the author host regression suites. */\n'
            'static long lroundf(float x) { return (long)(x >= 0 ? x + .5f : x - .5f); }\n'
            '#define isinf(x) ((x) == INFINITY || (x) == -INFINITY)\n')

PRE=r'''
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>
#include <setjmp.h>
#include <stdarg.h>
#include <inttypes.h>
#include "control.h"
typedef int esp_err_t;
typedef int portMUX_TYPE;
typedef unsigned TickType_t;
#define ESP_OK 0
#define ESP_ERR_INVALID_STATE 2
#define pdTRUE 1
#define CONFIG_EGR_ACTIVE_TEST 1
#define pdMS_TO_TICKS(x) (x)
#define portENTER_CRITICAL(m) ((void)(m))
#define portEXIT_CRITICAL(m) ((void)(m))
#define ESP_LOGE(...) ((void)0)
enum {GPIO_RPWM=1,GPIO_LPWM=21,GPIO_DRIVE_EN=39,GPIO_SENS_EN=40};
enum {LEDC_LOW_SPEED_MODE=0,LEDC_CHANNEL_0=0,LEDC_CHANNEL_1=1};
static control_t ctrl;
static bool transitioning,stop_pending,config_pending,run_permission,radio_allowed;
static bool bench_mode,acquisition_healthy=true;
static int control_mutex,gate_mux,level[64],wdt_feeds,button_reads,drive_writes;
static uint32_t duty_set[2],duty_out[2],gate_epoch;
static bool inhibited=true,drive_ok=true,sens_on,acquisition_running;
static int current_sign;
static uint64_t reverse_until,now_us,end_us;
static bool mutex_available;
static int start_result;
static jmp_buf finished;
static int gpio_set_level(int p,int v){level[p]=v;return 0;}
static int ledc_set_duty(int mode,int ch,uint32_t d){(void)mode;duty_set[ch]=d;return 0;}
static int ledc_update_duty(int mode,int ch){(void)mode;duty_out[ch]=duty_set[ch];return 0;}
static uint64_t esp_timer_get_time(void){return now_us;}
static TickType_t xTaskGetTickCount(void){return (TickType_t)(now_us/1000);}
static void vTaskDelay(int t){now_us+=1000ull*t;}
static void vTaskDelayUntil(TickType_t *w,TickType_t n){*w+=n;now_us+=1000*n;if(now_us>=end_us)longjmp(finished,1);}
static int xSemaphoreTake(int s,int t){(void)s;(void)t;return mutex_available;}
static void xSemaphoreGive(int s){(void)s;}
static bool board_sensor_enabled(void){return sens_on;}
static bool board_button(void){button_reads++;return true;}
static int board_watchdogs_start(void){return start_result;}
static void board_watchdogs_feed(void){wdt_feeds++;}
static void board_led(uint32_t rgb){(void)rgb;}
static void log_campaign_locked(void){}
static bool storage_event(const char *fmt,...){(void)fmt;return true;}
static void storage_mark(uint64_t t){(void)t;}
static bool enqueue(const char *s){(void)s;return true;}
void board_kill(void);
void board_emergency_stop(void);
esp_err_t board_sensor_off(void);
static void request_stop(void){board_emergency_stop();stop_pending=true;}
static inputs_t snapshot(void){
    inputs_t in={0}; in.now=in.sample_time=now_us;
    in.storage_ok=in.adc_ok=in.drive_ok=in.tc_ok=true;
    in.v[2]=5;in.v[3]=0;in.v[4]=2.5f;in.v[5]=2.5f;in.v[6]=12;in.v[7]=5;
    in.t1=in.t2=20; return in;
}
'''
FUN=''.join(function(board,s) for s in ['static void pwm_set(','void board_inhibit(',
'uint32_t board_stop_token(','void board_emergency_stop(','bool board_release(',
'void board_kill(','void board_overcurrent_trip(','void board_drive(',
'esp_err_t board_mode(','esp_err_t board_sensor_off('])
FUN+=''.join(function(app,s) for s in ['static uint32_t led_colour(','static void button_tick(','static void safety('])
POST=r'''
static void setup(void){
 control_init(&ctrl);ctrl.profile.ch_supply=2;ctrl.profile.ch_ground=3;ctrl.profile.ch_feedback=4;
 ctrl.profile.qualified=ctrl.profile.voltage_calibrated[1]=true;
 ctrl.profile.current_valid[1]=ctrl.profile.current_calibrated[1]=true;
 ctrl.test_bank=ctrl.sensor_on=true;ctrl.state=READY;
 transitioning=stop_pending=config_pending=false;acquisition_healthy=true;
 current_sign=0;reverse_until=0;inhibited=false;drive_ok=true;now_us=100000;
 wdt_feeds=button_reads=0;start_result=ESP_OK;mutex_available=false;
}
static unsigned output_bytes,newlines;
static int count_printf(const char *fmt,...){char s[4096];va_list ap;va_start(ap,fmt);int n=vsnprintf(s,sizeof s,fmt,ap);va_end(ap);output_bytes+=n;for(int i=0;i<n;i++)if(s[i]=='\n')newlines++;return n;}
#define printf count_printf
'''+function(app,'static void print_profile(')+r'''
#undef printf
int main(void){
 setup();
 if(!control_command(&ctrl,"manual",.3f,10,now_us))return 10;
 inputs_t in=snapshot();control_step(&ctrl,&in);
 board_drive(ctrl.duty,true);now_us+=5000;board_drive(ctrl.duty,true);run_permission=true;
 if(!level[GPIO_DRIVE_EN]||duty_out[0]!=306)return 11;
 uint64_t started=now_us;end_us=now_us+400000;
 if(!setjmp(finished))safety(NULL);
 printf("mutex_blocked: elapsed_us=%llu deadline=%llu now=%llu state=%s DRIVE_EN=%d RPWM=%u LPWM=%u watchdog_feeds=%d physical_button_reads=%d\n",
 (unsigned long long)(now_us-started),(unsigned long long)ctrl.deadline,(unsigned long long)now_us,
 control_name(ctrl.state),level[GPIO_DRIVE_EN],duty_out[0],duty_out[1],wdt_feeds,button_reads);
 if(ctrl.state!=MANUAL||!level[GPIO_DRIVE_EN]||button_reads||wdt_feeds!=400)return 12;
 /* Once safety can take the lock, the same stale deadline is correctly honored. */
 mutex_available=true;end_us=now_us+1000;if(!setjmp(finished))safety(NULL);
 printf("mutex_released: state=%s DRIVE_EN=%d RPWM=%u\n",control_name(ctrl.state),level[GPIO_DRIVE_EN],duty_out[0]);
 if(ctrl.state!=READY||level[GPIO_DRIVE_EN])return 13;
 setup(); print_profile();
 printf("actual_print_profile: bytes=%u CRLF_bytes=%u conservative_UART_min_us=%.1f\n",output_bytes,output_bytes+newlines,
 10.0e6*(output_bytes+newlines-128)/115200.0);
 /* Software scheduling limit independent of ADC or power-stage simulation. */
 setup();ctrl.state=SAFE;start_result=1;end_us=now_us+1000;
 if(!setjmp(finished))safety(NULL);
 uint32_t token=board_stop_token();board_mode(true,true);board_release(token);
 board_drive(.3f,true);now_us+=5000;board_drive(.3f,true);
 printf("watchdog_init_failure_then_commit_gate: token=%u DRIVE_EN=%d RPWM=%u\n",token,level[GPIO_DRIVE_EN],duty_out[0]);
 if(!level[GPIO_DRIVE_EN])return 14;
 setup(); ctrl.state=SENSOR_CHECK;ctrl.deadline=now_us+2000000;
 in=snapshot();in.v[6]=0;control_step(&ctrl,&in);
 printf("standalone_TEST_X1_13_unpowered: state=%s fault=%s\n",control_name(ctrl.state),ctrl.fault?ctrl.fault:"");
 if(ctrl.state!=FAULT||strcmp(ctrl.fault,"SUPPLY"))return 15;
 return 0;
}
'''
source=PRE+FUN+POST
c=OUT/'independent_firmware_probe.c';c.write_text(source,encoding='utf-8')
exe=OUT/'independent_firmware_probe.exe'
cmd=[str(CC),'-std=c11','-I',str(inc),'-I',str(MAIN),str(c),str(MAIN/'control.c'),'-o',str(exe)]
subprocess.run(cmd,check=True)
run=subprocess.run([str(exe)],text=True,capture_output=True)
(OUT/'independent_firmware_probe-results.txt').write_text(run.stdout+run.stderr,encoding='utf-8')
hashes={str(MAIN/f):hashlib.sha256((MAIN/f).read_bytes()).hexdigest() for f in ['app_main.c','board.c','control.c','control.h']}
(OUT/'probe-manifest.json').write_text(json.dumps({'source_sha256':hashes,'command':cmd,'returncode':run.returncode,'scope':'actual extracted functions; mocked platform scheduling and GPIO/LEDC; no physical hardware timing claim'},indent=2),encoding='utf-8')
print(run.stdout+run.stderr,end='');raise SystemExit(run.returncode)
