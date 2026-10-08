"""Execute the unmodified acquisition loop and board_adc wrapper through error->success.
The injection does NOT assume an error resets the ADC: it tests metadata validity only.
"""
from pathlib import Path
import subprocess, hashlib, json, os
OUT=Path(__file__).resolve().parent
MAIN=Path(os.environ['EGR_REVIEW_SOURCE'])/'Rewizje/EGRLab-v6.3-m1/firmware/main'
CC=Path(os.environ['EGR_REVIEW_TCC'])
def function(text, signature):
    start=text.index(signature); brace=text.index('{',start); depth=0
    for i in range(brace,len(text)):
        if text[i]=='{':depth+=1
        elif text[i]=='}':
            depth-=1
            if not depth:return text[start:i+1]+'\n'
    raise ValueError(signature)
app=(MAIN/'app_main.c').read_text(encoding='utf-8')
board=(MAIN/'board.c').read_text(encoding='utf-8')
PRE=r'''
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>
#include <setjmp.h>
#include <inttypes.h>
#include "control.h"
#include "measure.h"
#define _Static_assert(c,m) typedef char review_static_assert[(c)?1:-1]
#include "storage.h"
#include "trigger.h"
#define ESP_OK 0
#define ESP_ERR_INVALID_STATE 2
#define ESP_ERR_TIMEOUT 3
#define pdTRUE 1
#define portMAX_DELAY 9999
#define pdMS_TO_TICKS(x) (x)
#define CONFIG_EGR_SW_CURRENT_LIMIT 1
#define CONFIG_EGR_SW_CURRENT_LIMIT_MA 8000
#define portENTER_CRITICAL(m) ((void)(m))
#define portEXIT_CRITICAL(m) ((void)(m))
#define atomic_fetch_add(p,n) (*(p)+=(n))
typedef int esp_err_t;
static bool acquisition_running=true,config_ok=true,adc_reset_needed;
static bool pause_requested,run_permission,sensor_enabled,acquisition_healthy=true;
static int adc_lock,data_mux,pause_ack,resume_sem,zero_summary,summaries,first_sample;
static uint32_t lost_ticks,overcurrent_count,sample_count,adc_errors;
static session_config_t active_cfg;
static inputs_t latest;
static uint64_t now_us;
static unsigned notify_count,reads,pushed,error_events;
static sample_t captured[4];
static jmp_buf finish;
static int xSemaphoreTake(int h,int ticks){(void)h;(void)ticks;return pdTRUE;}
static void xSemaphoreGive(int h){(void)h;}
static void board_adc_set_running(bool v){acquisition_running=v;}
static void board_emergency_stop(void){run_permission=false;}
static void board_kill(void){}
static void board_overcurrent_trip(void){}
static uint32_t ulTaskNotifyTake(int c,int ticks){(void)c;(void)ticks;if(++notify_count>4)longjmp(finish,1);now_us+=500;return 1;}
static esp_err_t adc_read_owned(int16_t raw[8],uint64_t *ts){
    *ts=now_us;reads++;
    if(reads==2)return ESP_ERR_TIMEOUT;
    for(int j=0;j<8;j++)raw[j]=1000;
    raw[5]=16384;return ESP_OK;
}
static bool storage_event(const char *fmt,...){(void)fmt;error_events++;return true;}
static void storage_push(const sample_t *s){captured[pushed++]=*s;}
static uint32_t trigger_sample(const float v[8],uint64_t t){(void)v;(void)t;return 0;}
static bool trigger_take_summary(summary_t *s){(void)s;return false;}
static void log_triggers(const session_config_t *c,const sample_t *s,const float v[8],uint32_t m){(void)c;(void)s;(void)v;(void)m;}
static void xQueueOverwrite(int q,void *p){(void)q;(void)p;}
static int xQueueSend(int q,void *p,int t){(void)q;(void)p;(void)t;return pdTRUE;}
'''
# Header declarations are external; definitions below must match linkage.
PRE=PRE.replace('static bool storage_event(', 'bool storage_event(').replace('static void storage_push(', 'void storage_push(')
PRE=PRE.replace('static uint32_t trigger_sample(', 'uint32_t trigger_sample(').replace('static bool trigger_take_summary(', 'bool trigger_take_summary(')
POST=r'''
int main(void){
 control_t ctrl;control_init(&ctrl);ctrl.state=LOGGER;
 ctrl.profile.voltage_calibrated[0]=ctrl.profile.current_calibrated[0]=ctrl.profile.current_valid[0]=true;
 uint8_t range[8];memset(range,RANGE_10V,sizeof range);range[5]=RANGE_5V;
 control_build_config(&ctrl,&active_cfg,17,range,true,true);
 now_us=100000;
 if(!setjmp(finish))acquisition(NULL);
 inputs_t in=latest;in.now=now_us;in.adc_ok=config_ok;in.storage_ok=acquisition_healthy;
 control_step(&ctrl,&in);
 printf("after_error_then_two_successes: reads=%u adc_errors=%u board_config_ok=%d adc_reset_needed=%d acquisition_healthy=%d active_cfg_id=%u active_cfg_ok=%d state=%s pushed=%u\n",
 reads,adc_errors,config_ok,adc_reset_needed,acquisition_healthy,active_cfg.id,active_cfg.adc_config_ok,control_name(ctrl.state),pushed);
 for(unsigned k=0;k<pushed;k++)printf("record[%u]: sequence=%u config_id=%u flags=%u SAMPLE_INVALID=%d SAMPLE_GAP=%d\n",
 k,captured[k].sequence,captured[k].config_id,captured[k].flags,!!(captured[k].flags&SAMPLE_INVALID),!!(captured[k].flags&SAMPLE_GAP));
 printf("latest_voltage_CH6_finite=%d value=%.6f\n",isfinite(latest.v[5]),latest.v[5]);
 return !(adc_errors==1 && !config_ok && adc_reset_needed && !acquisition_healthy && active_cfg.adc_config_ok &&
          pushed==3 && !(captured[1].flags&SAMPLE_INVALID) && !(captured[2].flags&SAMPLE_INVALID) && ctrl.state==LOGGER);
}
'''
c=OUT/'adc_metadata_probe.c';exe=OUT/'adc_metadata_probe.exe'
c.write_text(PRE+function(board,'esp_err_t board_adc(')+function(app,'static void acquisition(')+POST,encoding='utf-8')
cmd=[str(CC),'-std=c11','-I',str(OUT/'include'),'-I',str(MAIN),str(c),str(MAIN/'control.c'),str(MAIN/'measure.c'),str(MAIN/'jsonlog.c'),'-o',str(exe)]
subprocess.run(cmd,check=True)
run=subprocess.run([str(exe)],capture_output=True,text=True)
(OUT/'adc_metadata_probe-results.txt').write_text(run.stdout+run.stderr,encoding='utf-8')
(OUT/'adc-metadata-probe-manifest.json').write_text(json.dumps({'command':cmd,'returncode':run.returncode,'source_sha256':{f:hashlib.sha256((MAIN/f).read_bytes()).hexdigest() for f in ['app_main.c','board.c','control.c','measure.c','jsonlog.c']},'scope':'unmodified acquisition and board_adc; error then successful reads injected in adc_read_owned; no assumption that ADC ranges changed'},indent=2),encoding='utf-8')
print(run.stdout+run.stderr,end='');raise SystemExit(run.returncode)
