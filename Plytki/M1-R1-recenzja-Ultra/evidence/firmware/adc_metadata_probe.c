
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
bool storage_event(const char *fmt,...){(void)fmt;error_events++;return true;}
void storage_push(const sample_t *s){captured[pushed++]=*s;}
uint32_t trigger_sample(const float v[8],uint64_t t){(void)v;(void)t;return 0;}
bool trigger_take_summary(summary_t *s){(void)s;return false;}
static void log_triggers(const session_config_t *c,const sample_t *s,const float v[8],uint32_t m){(void)c;(void)s;(void)v;(void)m;}
static void xQueueOverwrite(int q,void *p){(void)q;(void)p;}
static int xQueueSend(int q,void *p,int t){(void)q;(void)p;(void)t;return pdTRUE;}
esp_err_t board_adc(int16_t values[8], uint64_t *t_us) {
    if (!acquisition_running) return ESP_ERR_INVALID_STATE;
    if (xSemaphoreTake(adc_lock, pdMS_TO_TICKS(5)) != pdTRUE) return ESP_ERR_TIMEOUT;
    esp_err_t e = adc_read_owned(values, t_us);
    if (e != ESP_OK) { config_ok = false; adc_reset_needed = true; adc_errors++; }   /* F-04: zanik AD7606B / BUSY */
    xSemaphoreGive(adc_lock); return e;
}
static void acquisition(void *unused) {
    (void)unused; uint32_t seq=0; bool gap=true, adc_failing=false; current_window_t window; current_window_reset(&window);
    overcurrent_t oc={0}; bool oc_logged=false;
    while(true) {
        uint32_t ticks=ulTaskNotifyTake(pdTRUE,portMAX_DELAY);
        if(pause_requested) {
            /* ACK comes from the actual owner, after its last conversion and
             * all uses of active_cfg/trigger state have completed. */
            board_adc_set_running(false); xSemaphoreGive(pause_ack);
            xSemaphoreTake(resume_sem,portMAX_DELAY);
            ulTaskNotifyTake(pdTRUE,0); /* discard pre-pause notifications */
            board_adc_set_running(true); gap=true; current_window_reset(&window); oc=(overcurrent_t){0}; continue;
        }
        session_config_t c=active_cfg;
        sample_t s={.sequence=seq++, .config_id=c.id};
        if(gap) { s.flags|=SAMPLE_GAP; gap=false; }
        if(ticks>1) {
            s.flags|=SAMPLE_GAP; atomic_fetch_add(&lost_ticks,ticks-1);
            acquisition_healthy=false; board_emergency_stop(); board_kill();
            current_window_reset(&window);
        }
        /* The on-disk record is packed. Pass naturally aligned destinations
         * to the peripheral driver, then copy into the serialization object. */
        int16_t raw[8]; uint64_t sample_time;
        esp_err_t e=board_adc(raw,&sample_time);
        if(e!=ESP_OK) {
            acquisition_healthy=false; board_emergency_stop(); board_kill();
            /* M-11: AD7606B bez zasilania (tylko USB) nie moze zalac logu - jedno zdarzenie na serie bledow;
             * pelna liczba w daq_stats (adc_errors). */
            if(!adc_failing) storage_event("{\"type\":\"adc_error\",\"code\":%d}",e);
            adc_failing=true; continue;
        }
        adc_failing=false;
        memcpy(s.raw,raw,sizeof raw); s.t_us=sample_time;
        /* M-04: rekord v5 bez zmian; pola MCP3201 puste (65535 / status 2 = ABSENT), prad jest w raw[5]. */
        s.current_raw=65535; s.current_begin_us=0; s.current_end_us=0; s.current_status=2;
#if CONFIG_EGR_SW_CURRENT_LIMIT
        /* M-06: przed czymkolwiek innym - ograniczenie pradu dziala na kazdej probce, takze bez kalibracji. */
        float i_oc=overcurrent_amps(raw[CH_CURRENT],control_full_scale(c.range[CH_CURRENT]),c.gain[CH_CURRENT],
            c.offset[CH_CURRENT],c.current_zero,c.current_volts_per_amp);
        if(c.adc_config_ok && overcurrent_sample(&oc,i_oc,CONFIG_EGR_SW_CURRENT_LIMIT_MA/1000.0f,2)) {
            bool driving=run_permission;
            board_overcurrent_trip(); atomic_fetch_add(&overcurrent_count,1);
            if(!oc_logged) {
                char a[32]; storage_event("{\"type\":\"overcurrent\",\"t_us\":%" PRIu64 ",\"config_id\":%u,\"amps\":%s,"
                    "\"limit_a\":%.3f,\"bank\":%d,\"drive_was_permitted\":%s}",s.t_us,c.id,json_number(a,i_oc),
                    CONFIG_EGR_SW_CURRENT_LIMIT_MA/1000.0f,c.bank,driving?"true":"false");
                oc_logged=true;
            }
        } else if(!oc.over) oc_logged=false;
#endif
        if(c.bank) s.flags|=SAMPLE_TEST;
        if(run_permission) s.flags|=SAMPLE_PERMIT;
        if(sensor_enabled) s.flags|=SAMPLE_SENSOR;
        uint8_t sat=measurement_saturation(raw);
        if(sat) s.flags|=SAMPLE_SATURATED;
        if(!c.adc_config_ok) s.flags|=SAMPLE_INVALID;
        float v[8];
        for(int j=0;j<8;j++) v[j]=c.adc_config_ok && c.voltage_calibrated && !(sat&(1u<<j))
            ? s.raw[j]*(control_full_scale(c.range[j])/32768.0f)*c.gain[j]+c.offset[j] : NAN;
        /* M-04: v[5] = napiecie wyjscia INA240 z CH6 (gain/offset jak kazdy kanal); prad = (v[5] - zero) / 0,25 V/A. */
        uint32_t fired=trigger_sample(v,s.t_us);
        if(fired) { s.flags|=SAMPLE_TRIGGER; log_triggers(&c,&s,v,fired); }
        float mean,rms,amps=c.current_valid?(v[5]-c.current_zero)/c.current_volts_per_amp:NAN;
        bool valid=current_window_add(&window,s.t_us,amps,&mean,&rms);   /* jednoczesnie z napieciami */
        portENTER_CRITICAL(&data_mux);
        latest.sample_time=s.t_us; latest.config_id=c.id; latest.saturation_mask=sat;
        memcpy(latest.v,v,sizeof v); latest.current_mean=mean; latest.current_rms=rms;
        latest.current_window_valid=valid && c.current_window_qualified;
        portEXIT_CRITICAL(&data_mux);
        summary_t sum;
        if(trigger_take_summary(&sum)) {
            xQueueOverwrite(zero_summary,&sum);
            if(xQueueSend(summaries,&sum,0)!=pdTRUE)
                storage_event("{\"type\":\"summary_dropped\",\"t_us\":%" PRIu64 "}",s.t_us);
        }
        storage_push(&s); atomic_fetch_add(&sample_count,1); xSemaphoreGive(first_sample);
    }
}

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
