
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
    portENTER_CRITICAL(&gate_mux); bool ok=token==gate_epoch;
    if(ok) inhibited=false;
    portEXIT_CRITICAL(&gate_mux); return ok;
}
void board_kill(void) {
    portENTER_CRITICAL(&gate_mux);
    gpio_set_level(GPIO_DRIVE_EN, 0);
    portEXIT_CRITICAL(&gate_mux);
    pwm_set(0, 0);
}
void board_overcurrent_trip(void) { drive_ok = false; board_emergency_stop(); }
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
static uint32_t led_colour(state_t st, bool alive) {
    if(st==FAULT) return 0x200000;
    if(bench_mode) return 0x100010;
    if(!alive) return 0x200000;
    if(st==LOGGER || st==IDENTIFY) return 0x002000;
    if(st==SAFE) return 0x000020;
    return control_moving(&ctrl) ? 0x181818 : 0x181000;
}
static void button_tick(uint64_t now, state_t st) {
    static bool raw_prev, stable, long_done; static uint64_t changed, down_at;
    bool raw=board_button();
    if(raw!=raw_prev) { raw_prev=raw; changed=now; }
    bool test_states=st!=SAFE && st!=LOGGER && st!=IDENTIFY;
    if(now-changed>=20000 && raw!=stable) {
        stable=raw;
        if(stable) {
            down_at=now; long_done=false;
            if(test_states) {          /* TEST, READY, ruch, FAULT: STOP bez czekania */
                long_done=true; request_stop();
                storage_event("{\"type\":\"button\",\"t_us\":%" PRIu64 ",\"press\":\"stop\"}",now);
            }
        } else if(!long_done) {
            storage_event("{\"type\":\"button\",\"t_us\":%" PRIu64 ",\"press\":\"short\"}",now); storage_mark(now);
        }
    }
    if(stable && !long_done && now-down_at>=1000000) {
        long_done=true; storage_event("{\"type\":\"button\",\"t_us\":%" PRIu64 ",\"press\":\"long\"}",now);
        enqueue(st==SAFE ? "logger" : "stop");
    }
}
static void safety(void *unused) {
    (void)unused; TickType_t wake=xTaskGetTickCount(); uint64_t last_beat=0; state_t prior=SAFE;
    bool heart_ok=false, blink=false, sens_warned=false;
    /* M-06: to zadanie karmi TWDT i RTC WDT; zawieszenie = panika (DRIVE_EN w dol) albo reset systemu. */
    if(board_watchdogs_start()!=ESP_OK) { ESP_LOGE(TAG,"watchdog: start nieudany - TEST zablokowany"); board_emergency_stop(); }
    while(true) {
        board_watchdogs_feed();
        inputs_t i=snapshot();
        if(xSemaphoreTake(control_mutex,0)==pdTRUE) {
            i=snapshot(); /* fresh AFTER acquiring the lock */
            if(!transitioning && !stop_pending) {
                int8_t map[3]={ctrl.profile.ch_supply,ctrl.profile.ch_ground,ctrl.profile.ch_feedback};
                control_step(&ctrl,&i);
                if(map[0]!=ctrl.profile.ch_supply || map[1]!=ctrl.profile.ch_ground || map[2]!=ctrl.profile.ch_feedback) {
                    transitioning=true; config_pending=true; board_inhibit(true);
                }
                bool moving=control_moving(&ctrl) && !transitioning;
#if !CONFIG_EGR_ACTIVE_TEST
                moving=false;
#endif
                run_permission=moving; board_drive(ctrl.duty,moving);
                if(ctrl.state==FAULT && prior!=FAULT) {
                    board_inhibit(true); transitioning=true; config_pending=true;
                }
                log_campaign_locked();
            }
            if(ctrl.state!=prior) {
                storage_event("{\"type\":\"state\",\"t_us\":%" PRIu64 ",\"state\":\"%s\",\"fault\":\"%s\"}",
                    i.now,control_name(ctrl.state),ctrl.fault?ctrl.fault:""); prior=ctrl.state;
            }
            heart_ok=ctrl.state!=FAULT;
            /* Bez detekcji adaptera (M-01): radio tylko w banku TEST poza LOGGER / IDENTIFY / FAULT. */
            radio_allowed=ctrl.test_bank && !transitioning && ctrl.state!=LOGGER
                && ctrl.state!=IDENTIFY && ctrl.state!=FAULT;
            /* M-07 / D-M1-5: SENS_5V nigdy poza bankiem TEST; CH8 > 1 V w LOGGER = ostrzezenie i ponowne wylaczenie. */
            if(!ctrl.test_bank && board_sensor_enabled()) board_sensor_off();
            bool sens_high=!ctrl.test_bank && isfinite(i.v[CH_SENS5V]) && i.v[CH_SENS5V]>1;
            if(sens_high && !sens_warned) storage_event("{\"type\":\"sens5v_in_logger\",\"t_us\":%" PRIu64 "}",i.now);
            sens_warned=sens_high;
            button_tick(i.now,ctrl.state);
            xSemaphoreGive(control_mutex);
        }
        if(stop_pending || transitioning) { board_kill(); run_permission=false; }
        if(i.now-last_beat>=250000) {
            bool alive=heart_ok && !stop_pending && acquisition_healthy && i.now>=i.sample_time && i.now-i.sample_time<10000;
            blink=alive ? !blink : true;
            board_led(blink ? led_colour(ctrl.state,alive) : 0); last_beat=i.now;
        }
        vTaskDelayUntil(&wake,pdMS_TO_TICKS(1));
    }
}

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
static void print_profile(void) {
    printf("bind %s %s\ndaqmodule %s\nsession %s %s\n",ctrl.profile.valve,ctrl.profile.adapter,
        ctrl.profile.daq_module,ctrl.profile.vehicle_id,ctrl.profile.session_note);
    for(int b=0;b<2;b++) {
        for(int j=0;j<8;j++) printf("cal %d %d %.9g %.9g\n",b,j,ctrl.profile.gain[b][j],ctrl.profile.offset[b][j]);
        printf("currentcal %d %.9g\n",b,ctrl.profile.current_zero[b]);
    }
    /* 6.3-m1: bez auxcal (brak AUX) i iscal (brak MCP3201); skala pradu CH6 = ivpa (V/A). */
    for(int b=0;b<2;b++) printf("imodule %d %s\nivpa %d %.9g\nicalok %d %d\n",b,ctrl.profile.current_module[b],b,
        ctrl.profile.current_volts_per_amp[b],b,ctrl.profile.current_calibrated[b]);
    printf("vcalok 0 %d\nvcalok 1 %d\nlimits %.9g %.9g %.9g\nmetric %d\n",ctrl.profile.voltage_calibrated[0],ctrl.profile.voltage_calibrated[1],ctrl.profile.max_duty,ctrl.profile.current_limit,ctrl.profile.temp_limit,ctrl.profile.current_window_qualified);
}

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
