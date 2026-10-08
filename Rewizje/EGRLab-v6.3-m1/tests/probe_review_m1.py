"""6.3.1-m1: regressions for the M1-R1 reviews (Plytki/M1-R1-recenzja-Astra M1-01..07, -Ultra M1-08..12). Each scenario uses the
reviewers' stimulus (their probes in evidence/ were the model) on the ACTUAL firmware functions with a stubbed platform, and asserts
the corrected behaviour. Run on the 6.3-m1 sources (--src DIR with firmware/main and tools of R1) the same stimuli must fail;
run on 6.3.1-m1 they must pass. No electronics or ESP-IDF scheduling are simulated.
python tests/probe_review_m1.py --cc gcc --out verification [--src DIR]
"""
import argparse, csv, json, math, subprocess, sys, tempfile
from pathlib import Path
from probe_storage import function

SAFETY_PRE = r'''
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>
#include <setjmp.h>
#include <stdarg.h>
#include <inttypes.h>
#include "control.h"
typedef int esp_err_t; typedef int portMUX_TYPE; typedef unsigned TickType_t;
#define ESP_OK 0
#define ESP_ERR_INVALID_STATE 2
#define pdTRUE 1
#define CONFIG_EGR_ACTIVE_TEST 1
#define CONTROL_STALE_US 20000
#define pdMS_TO_TICKS(x) (x)
#define portENTER_CRITICAL(m) ((void)(m))
#define portEXIT_CRITICAL(m) ((void)(m))
#define ESP_LOGE(...) ((void)0)
enum {GPIO_RPWM=1,GPIO_LPWM=21,GPIO_DRIVE_EN=39,GPIO_SENS_EN=40};
enum {LEDC_LOW_SPEED_MODE=0,LEDC_CHANNEL_0=0,LEDC_CHANNEL_1=1};
static control_t ctrl; static int shown_state;
static bool transitioning,stop_pending,config_pending,run_permission,radio_allowed,bench_mode,acquisition_healthy=true;
static int control_mutex,gate_mux,level[64],wdt_feeds,button_reads;
static uint32_t duty_set[2],duty_out[2],gate_epoch;
static bool inhibited=true,drive_ok=true,sens_on,acquisition_running,watchdogs_ok;
static int current_sign; static uint64_t reverse_until,now_us,end_us; static bool mutex_available; static int start_result;
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
static bool board_button(void){button_reads++;return false;}
static int board_watchdogs_start(void){if(!start_result)watchdogs_ok=true;return start_result;}
static bool board_watchdogs_ok(void){return watchdogs_ok;}
static void board_watchdogs_feed(void){wdt_feeds++;}
static void board_led(uint32_t rgb){(void)rgb;}
static void log_campaign_locked(void){}
static bool storage_event(const char *fmt,...){(void)fmt;return true;}
static void storage_mark(uint64_t t){(void)t;}
static bool enqueue(const char *s){(void)s;return true;}
void board_kill(void); void board_emergency_stop(void); esp_err_t board_sensor_off(void);
static void request_stop(void){board_emergency_stop();stop_pending=true;}
static inputs_t snapshot(void){
    inputs_t in={0}; in.now=in.sample_time=now_us; in.storage_ok=in.adc_ok=in.drive_ok=in.tc_ok=true;
    in.v[2]=5;in.v[3]=0;in.v[4]=2.5f;in.v[5]=2.5f;in.v[6]=12;in.v[7]=5;in.t1=in.t2=20;return in;
}
'''
SAFETY_POST = r'''
#define CHECK(x) do{checks++;if(!(x)){printf("FAIL %s: %s\n",scenario,#x);fails++;}}while(0)
static int checks,fails; static const char *scenario;
static void setup(void){
 control_init(&ctrl);ctrl.profile.ch_supply=2;ctrl.profile.ch_ground=3;ctrl.profile.ch_feedback=4;
 ctrl.profile.qualified=ctrl.profile.voltage_calibrated[1]=true;ctrl.profile.current_valid[1]=ctrl.profile.current_calibrated[1]=true;
 ctrl.test_bank=ctrl.sensor_on=true;ctrl.state=READY;transitioning=stop_pending=config_pending=false;acquisition_healthy=true;
 current_sign=0;reverse_until=0;inhibited=false;drive_ok=true;watchdogs_ok=true;now_us=100000;
 wdt_feeds=button_reads=0;start_result=ESP_OK;mutex_available=false;level[GPIO_DRIVE_EN]=0;duty_out[0]=duty_out[1]=0;run_permission=false;
}
static void start_manual(int ms){
 control_command(&ctrl,"manual",.3f,ms,now_us); inputs_t in=snapshot(); control_step(&ctrl,&in);
 board_drive(ctrl.duty,true);now_us+=5000;board_drive(ctrl.duty,true);run_permission=true;
}
int main(void){
 /* M1-08 (Ultra): MANUAL, manager holds control_mutex for 400 ms (e.g. a slow "profile" print). */
 scenario="M1-08 mutex blocked 400 ms in MANUAL"; setup(); start_manual(200);
 CHECK(level[GPIO_DRIVE_EN] && duty_out[0]==306);
 uint64_t t0=now_us; end_us=now_us+400000; if(!setjmp(finished)) safety(NULL);
 printf("%s: DRIVE_EN=%d RPWM=%u stop_pending=%d button_reads=%d watchdog_feeds=%d\n",scenario,level[GPIO_DRIVE_EN],duty_out[0],stop_pending,button_reads,wdt_feeds);
 CHECK(!level[GPIO_DRIVE_EN] && !duty_out[0]); CHECK(stop_pending); CHECK(button_reads>=390); CHECK(now_us-t0>=400000);
 /* control: the same loop with the lock available keeps a valid MANUAL running (no false stale stop) */
 scenario="M1-08 control: lock available"; setup(); start_manual(200); mutex_available=true; end_us=now_us+50000;
 if(!setjmp(finished)) safety(NULL);
 printf("%s: DRIVE_EN=%d state=%s stop_pending=%d feeds=%d\n",scenario,level[GPIO_DRIVE_EN],control_name(ctrl.state),stop_pending,wdt_feeds);
 CHECK(level[GPIO_DRIVE_EN] && ctrl.state==MANUAL && !stop_pending && wdt_feeds>=49);
 /* M1-03 (Astra): watchdog start fails -> a later valid commit must not release the drive gate */
 scenario="M1-03 watchdog start failure"; setup(); watchdogs_ok=false; ctrl.state=SAFE; start_result=1; mutex_available=true; end_us=now_us+1000;
 if(!setjmp(finished)) safety(NULL);
 uint32_t token=board_stop_token(); board_mode(true,true); bool released=board_release(token);
 board_drive(.3f,true); now_us+=5000; board_drive(.3f,true);
 printf("%s: released=%d DRIVE_EN=%d RPWM=%u\n",scenario,released,level[GPIO_DRIVE_EN],duty_out[0]);
 CHECK(!released && !level[GPIO_DRIVE_EN] && !duty_out[0]);
 printf("safety probe: %d checks, %d failed\n",checks,fails); return fails!=0;
}
'''
ADC_PRE = r'''
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
static bool acquisition_running=true,config_ok=true,adc_reset_needed,adc_recover_pending;
static bool pause_requested,run_permission,sensor_enabled,acquisition_healthy=true;
static int adc_lock,data_mux,pause_ack,resume_sem,zero_summary,summaries,first_sample;
static uint32_t lost_ticks,overcurrent_count,sample_count,adc_errors;
static session_config_t active_cfg; static inputs_t latest; static uint64_t now_us;
static unsigned notify_count,reads,pushed; static sample_t captured[4]; static jmp_buf finish;
static int xSemaphoreTake(int h,int ticks){(void)h;(void)ticks;return pdTRUE;}
static void xSemaphoreGive(int h){(void)h;}
static bool board_adc_config_ok(void){return config_ok;}
static void board_adc_set_running(bool v){acquisition_running=v;}
static void board_emergency_stop(void){run_permission=false;}
static void board_kill(void){}
static void board_overcurrent_trip(void){}
static uint32_t ulTaskNotifyTake(int c,int ticks){(void)c;(void)ticks;if(++notify_count>4)longjmp(finish,1);now_us+=500;return 1;}
static esp_err_t adc_read_owned(int16_t raw[8],uint64_t *ts){
    *ts=now_us;reads++; if(reads==2)return ESP_ERR_TIMEOUT;
    for(int j=0;j<8;j++)raw[j]=1000; raw[5]=16384;return ESP_OK;
}
bool storage_event(const char *fmt,...){(void)fmt;return true;}
void storage_push(const sample_t *s){captured[pushed++]=*s;}
uint32_t trigger_sample(const float v[8],uint64_t t){(void)v;(void)t;return 0;}
bool trigger_take_summary(summary_t *s){(void)s;return false;}
static void log_triggers(const session_config_t *c,const sample_t *s,const float v[8],uint32_t m){(void)c;(void)s;(void)v;(void)m;}
static void xQueueOverwrite(int q,void *p){(void)q;(void)p;}
static int xQueueSend(int q,void *p,int t){(void)q;(void)p;(void)t;return pdTRUE;}
'''
ADC_POST = r'''
int main(void){
 control_t ctrl;control_init(&ctrl);ctrl.state=LOGGER;
 ctrl.profile.voltage_calibrated[0]=ctrl.profile.current_calibrated[0]=ctrl.profile.current_valid[0]=true;
 uint8_t range[8];memset(range,RANGE_10V,sizeof range);range[5]=RANGE_5V;
 control_build_config(&ctrl,&active_cfg,17,range,true,true); now_us=100000;
 if(!setjmp(finish))acquisition(NULL);
 printf("M1-09 TIMEOUT then two good transfers: pushed=%u board_config_ok=%d recover_pending=%d\n",pushed,config_ok,adc_recover_pending);
 for(unsigned k=0;k<pushed;k++)printf("  record[%u] seq=%u config_id=%u INVALID=%d\n",k,captured[k].sequence,captured[k].config_id,!!(captured[k].flags&SAMPLE_INVALID));
 int fails=0;
 if(pushed!=3 || (captured[0].flags&SAMPLE_INVALID)) {printf("FAIL M1-09: first record before the error must be valid\n");fails++;}
 if(!(captured[1].flags&SAMPLE_INVALID) || !(captured[2].flags&SAMPLE_INVALID)) {printf("FAIL M1-09: records after the error must stay INVALID until reconfiguration\n");fails++;}
 if(isfinite(latest.v[5])) {printf("FAIL M1-09: no physical value from an unconfirmed ADC\n");fails++;}
 if(!adc_recover_pending) {printf("FAIL M1-09: recovery (reconfiguration with a new config_id) not requested\n");fails++;}
 printf("adc probe: 4 checks, %d failed\n",fails); return fails!=0;
}
'''
PRODUCER = r'''
#include "control.h"
#include "jsonlog.h"
#include "trigger.h"
#include <stdio.h>
#include <string.h>
#include <math.h>
static int fails,checks;
#define CHECK(n,x) do{checks++;if(!(x)){printf("FAIL %s: %s\n",n,#x);fails++;}}while(0)
static int supply_case(float vbat){
    control_t c; control_init(&c); c.profile.ch_supply=2; c.profile.ch_ground=4; c.profile.ch_feedback=3; c.profile.qualified=true;
    inputs_t in={0}; in.now=in.sample_time=1000000; in.adc_ok=in.storage_ok=in.drive_ok=in.tc_ok=true;
    in.t1=30; in.v[CH_CURRENT]=2.5f; in.v[CH_VBAT]=vbat;
    control_command(&c,"test",0,0,in.now); in.v[2]=in.v[7]=5; in.v[3]=2.5f;
    control_step(&c,&in); in.now=in.sample_time=1250000; control_step(&c,&in);
    printf("M1-02 TEST CH7=%.1f V: state=%s fault=%s\n",vbat,control_name(c.state),c.fault?c.fault:"none");
    return c.state==FAULT && c.fault && !strcmp(c.fault,"SUPPLY");
}
int main(void){
  /* M1-02 (Astra): TEST bank supply window 9,0-17,3 V (X1.13 jumpered to VMOTOR) */
  CHECK("M1-02 0 V",supply_case(0)); CHECK("M1-02 8.9 V",supply_case(8.9f)); CHECK("M1-02 13.5 V",!supply_case(13.5f));
  CHECK("M1-02 16.8 V (full 4S)",!supply_case(16.8f)); CHECK("M1-02 17.4 V",supply_case(17.4f));
  control_t ctrl; control_init(&ctrl); profile_t *p=&ctrl.profile;
  p->ch_supply=2;p->ch_ground=4;p->ch_feedback=3; p->current_valid[0]=p->current_calibrated[0]=p->voltage_calibrated[0]=true;
  p->learned=true;p->closed=.15f;p->open=.85f; strcpy(p->daq_module,"M1_SYNTHETIC");strcpy(p->current_module[0],"M1_SYNTHETIC");
  control_apply_ranges(p,true); session_config_t config; control_build_config(&ctrl,&config,1,p->range,true,true);
  char line[2048]; if(!json_config(line,sizeof line,&config,0))return 1; puts(line);
  /* M1-12 (Ultra): no valid measurement (NaN) with a known map must not raise REF / FEEDBACK; a real 4 V REF still must */
  float invalid[8]; for(int i=0;i<8;i++)invalid[i]=NAN;
  config.voltage_calibrated=false; trigger_configure(&config,2000); unsigned f=trigger_sample(invalid,1000);
  printf("M1-12 NaN vector mask=%u\n",f); CHECK("M1-12 NaN",!(f&TRIG_REF) && !(f&TRIG_FB));
  config.voltage_calibrated=true; trigger_configure(&config,2000);
  float low_ref[8]={0,0,4.0f,2.0f,0,2.5f,13.5f,0}; f=trigger_sample(low_ref,1000);
  printf("M1-12 real 4 V REF mask=%u\n",f); CHECK("M1-12 real low REF",(f&TRIG_REF) && !(f&TRIG_FB));
  /* M1-11 (Ultra): a new CH6 scale invalidates the current acceptance and the metric qualification of that bank */
  p->current_calibrated[1]=p->voltage_calibrated[1]=p->current_valid[1]=true; p->current_window_qualified=p->qualified=true;
  strcpy(p->current_module[1],"M1_SYNTHETIC");
  int ok=profile_command(p,"cal 1 5 0.8 0.5");
  printf("M1-11 after cal 1 5: accepted=%d vcal=%d ical=%d metric=%d\n",ok,p->voltage_calibrated[1],p->current_calibrated[1],p->current_window_qualified);
  CHECK("M1-11 CH6 cal",ok && !p->current_calibrated[1] && !p->current_window_qualified);
  ok=profile_command(p,"vcalok 1 1");
  CHECK("M1-11 qualify needs a new current acceptance",ok && !(p->voltage_calibrated[1] && p->current_calibrated[1] && p->current_window_qualified));
  p->current_calibrated[1]=true; p->current_window_qualified=true; ok=profile_command(p,"cal 1 2 1.0 0");
  CHECK("M1-11 other channel keeps the current acceptance",ok && p->current_calibrated[1] && p->current_window_qualified);
  printf("producer probe: %d checks, %d failed\n",checks,fails); return fails!=0;
}
'''


def build_and_run(cc, out, name, source, main, extra):
    c = out / (name + '.c'); c.write_text(source, encoding='utf-8'); exe = out / (name + '.exe')
    subprocess.run([cc, '-std=c11', '-w', '-I', str(main), str(c), *[str(main / e) for e in extra], '-lm', '-o', str(exe)], check=True)
    return subprocess.run([str(exe.resolve())], capture_output=True, text=True)


def reader_check(tools, producer_stdout, work):
    """M1-10 (Ultra): synthetic v5 session -1 / 0 / +1 A from the real config producer -> egrlog export must keep the CH6 current."""
    sys.path.insert(0, str(tools)); import importlib; egrlog = importlib.import_module('egrlog')
    cfg = json.loads(next(l for l in producer_stdout.splitlines() if l.startswith('{"type":"config"')))
    session = work / 'synthetic-m1-session'; session.mkdir(exist_ok=True)
    (session / 'events_000.ndjson').write_text(json.dumps(cfg) + '\n', encoding='utf-8')
    rows, expected = [], []
    for n, amps in enumerate([-1.0, 0.0, 1.0]):
        volts = [0, 0, 5, 2.5, 0, cfg['current_zero'] + amps * cfg['current_volts_per_amp'], 13.5, 0]
        raw = [round((v - o) / g * 32768 / fs) for v, o, g, fs in zip(volts, cfg['offset'], cfg['gain'], cfg['full_scale'])]
        expected.append((raw[5] * cfg['full_scale'][5] / 32768 * cfg['gain'][5] + cfg['offset'][5] - cfg['current_zero']) / cfg['current_volts_per_amp'])
        rows.append((1000 + n * 500, n, *raw, 65535, 0, 0, 2, 0, 1))
    egrlog.write_log(session / 'samples_000.egr', rows, version=5, synthetic=True)
    egrlog.export(session, work / 'm1-current-export.csv')
    with (work / 'm1-current-export.csv').open() as f: out = list(csv.DictReader(f))
    got = [float(x['current_a']) if x['current_a'] else math.nan for x in out]
    ok = all(math.isfinite(g) and abs(g - e) < 1e-4 for g, e in zip(got, expected)) and 'sens_5v_v' in out[0]
    print(f'M1-10 export current: expected {[round(e, 6) for e in expected]}, got {got}, CH8 column sens_5v_v: {"sens_5v_v" in out[0]}')
    print(f'reader probe: 1 check, {0 if ok else 1} failed' + ('' if ok else '\nFAIL M1-10: CH6 current lost in the export'))
    return ok


if __name__ == '__main__':
    a = argparse.ArgumentParser(description=__doc__); a.add_argument('--cc', default='gcc'); a.add_argument('--out', type=Path, default=Path('verification'))
    a.add_argument('--src', type=Path, default=Path(__file__).resolve().parents[1]); args = a.parse_args()
    main, tools = args.src / 'firmware/main', args.src / 'tools'; args.out.mkdir(parents=True, exist_ok=True)
    app, board = (main / 'app_main.c').read_text(encoding='utf-8'), (main / 'board.c').read_text(encoding='utf-8')
    fn = lambda text, sigs: ''.join(function(text, s) for s in sigs)
    results = {}
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        r = build_and_run(args.cc, work, 'review_safety', SAFETY_PRE + fn(board, ['static void pwm_set(', 'void board_inhibit(', 'uint32_t board_stop_token(',
            'void board_emergency_stop(', 'bool board_release(', 'void board_kill(', 'void board_overcurrent_trip(', 'void board_drive(', 'esp_err_t board_mode(',
            'esp_err_t board_sensor_off(']) + fn(app, ['static uint32_t led_colour(', 'static void button_tick(', 'static void safety(']) + SAFETY_POST, main, ['control.c'])
        results['safety'] = r
        r = build_and_run(args.cc, work, 'review_adc', ADC_PRE + function(board, 'esp_err_t board_adc(') + function(app, 'static void acquisition(') + ADC_POST,
                          main, ['control.c', 'measure.c', 'jsonlog.c'])
        results['adc'] = r
        r = build_and_run(args.cc, work, 'review_producer', PRODUCER, main, ['control.c', 'jsonlog.c', 'trigger.c', 'profile.c', 'measure.c'])
        results['producer'] = r
        reader_ok = reader_check(tools, r.stdout, work)
    text = ''.join(r.stdout + r.stderr for r in results.values())
    print(text, end='')
    fails = [k for k, r in results.items() if r.returncode] + ([] if reader_ok else ['reader'])
    summary = {'source': str(args.src), 'failed_groups': fails, 'output': text.splitlines()}
    (args.out / 'review-regressions.json').write_text(json.dumps(summary, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    print('review regressions M1-02/03/08/09/10/11/12:', 'PASS' if not fails else 'FAIL ' + ', '.join(fails))
    sys.exit(1 if fails else 0)
