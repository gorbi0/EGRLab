#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdatomic.h>
#include <inttypes.h>
#include "sdkconfig.h"
#include "board.h"
#include "control.h"
#include "storage.h"
#include "trigger.h"
#include "measure.h"
#include "jsonlog.h"
#include "webui.h"
#include "commissioning.h"
#include "esp_timer.h"
#include "esp_psram.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "nvs.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "freertos/queue.h"

typedef struct { char line[160]; uint32_t epoch; } request_t;
static control_t ctrl;
static inputs_t latest;
static session_config_t active_cfg;
static uint32_t next_id=1;
static portMUX_TYPE data_mux=portMUX_INITIALIZER_UNLOCKED;
static SemaphoreHandle_t control_mutex, pause_ack, resume_sem, first_sample;
static QueueHandle_t requests, summaries, zero_summary;
static TaskHandle_t adc_task;
static esp_timer_handle_t timer;
static nvs_handle_t nvs;
static _Atomic bool pause_requested, transitioning=true, stop_pending, config_pending;
static _Atomic bool acquisition_healthy=true, run_permission, sensor_enabled, radio_allowed;
static _Atomic uint32_t stop_epoch, lost_ticks, trigger_count;
static bool adc_paused; /* command manager only */
static bool tc_valid;
static uint64_t tc_time, inputs_time;
static const char *TAG="EGRLab-v6";

static inputs_t snapshot(void) {
    portENTER_CRITICAL(&data_mux); inputs_t i=latest; bool valid=tc_valid;
    uint64_t tt=tc_time, it=inputs_time; portEXIT_CRITICAL(&data_mux);
    i.now=esp_timer_get_time(); i.interlock=board_interlock(); i.hw_armed=board_armed();
    i.storage_ok=storage_ok() && acquisition_healthy;
    i.adc_ok=board_adc_config_ok(); i.drive_ok=board_drive_ok();
    i.tc_ok=valid && i.now>=tt && i.now-tt<1000000;
    control_guard_io(&i,it);
    return i;
}
static void tick(void *unused) { (void)unused; if(!pause_requested) xTaskNotifyGive(adc_task); }
static void fault_locked(const char *reason) {
    control_stop(&ctrl); ctrl.state=FAULT; ctrl.fault=reason;
    board_inhibit(true); board_kill(); run_permission=false; radio_allowed=false;
}
static void request_stop(void) {
    /* Epoch invalidates previously queued motion commands. Hardware ARM cannot
     * be reasserted by a concurrent board_drive after this gate is latched. */
    board_emergency_stop();
    atomic_fetch_add(&stop_epoch,1); stop_pending=true; radio_allowed=false;
}
static bool enqueue(const char *line) {
    if(!strcmp(line,"stop")) { request_stop(); return true; }
    request_t r={.epoch=atomic_load(&stop_epoch)};
    if(strlen(line)>=sizeof r.line) return false;
    strcpy(r.line,line); return xQueueSend(requests,&r,0)==pdTRUE;
}
static void log_triggers(const session_config_t *c,const sample_t *s,const float v[8],uint32_t mask) {
    if(!mask || c->ch_supply<2 || c->ch_ground<2 || c->ch_feedback<2) return;
    board_scope_trigger(); atomic_fetch_add(&trigger_count,1);
    float ground=v[c->ch_ground];
    float amps=c->current_valid ? (v[5]-c->current_zero)/c->current_volts_per_amp : NAN;
    for(int bit=0;bit<TRIG_COUNT;bit++) if(mask&(1u<<bit)) {
        char g[32],r[32],f[32],i[32];
        storage_event("{\"type\":\"trigger\",\"t_us\":%" PRIu64 ",\"config_id\":%u,\"name\":\"%s\","
            "\"ground\":%s,\"ref\":%s,\"fb\":%s,\"i\":%s,\"current_valid\":%s}",
            s->t_us,c->id,trigger_name(bit),json_number(g,ground),
            json_number(r,v[c->ch_supply]-ground),json_number(f,v[c->ch_feedback]-ground),
            json_number(i,amps),c->current_valid?"true":"false");
    }
}
static void acquisition(void *unused) {
    (void)unused; uint32_t seq=0; bool gap=true; current_window_t window; current_window_reset(&window);
    while(true) {
        uint32_t ticks=ulTaskNotifyTake(pdTRUE,portMAX_DELAY);
        if(pause_requested) {
            /* ACK comes from the actual owner, after its last conversion and
             * all uses of active_cfg/trigger state have completed. */
            board_adc_set_running(false); xSemaphoreGive(pause_ack);
            xSemaphoreTake(resume_sem,portMAX_DELAY);
            ulTaskNotifyTake(pdTRUE,0); /* discard pre-pause notifications */
            board_adc_set_running(true); gap=true; current_window_reset(&window); continue;
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
        local_current_t cur;
        esp_err_t e=board_adc(raw,&sample_time,&cur);
        if(e!=ESP_OK) {
            acquisition_healthy=false; board_emergency_stop(); board_kill();
            storage_event("{\"type\":\"adc_error\",\"code\":%d}",e); continue;
        }
        memcpy(s.raw,raw,sizeof raw); s.t_us=sample_time;
        s.current_raw=cur.raw; s.current_begin_us=cur.begin_us; s.current_end_us=cur.end_us; s.current_status=cur.status;
        if(c.bank) s.flags|=SAMPLE_TEST;
        if(run_permission) s.flags|=SAMPLE_PERMIT;
        if(sensor_enabled) s.flags|=SAMPLE_SENSOR;
        uint8_t sat=measurement_saturation(raw);
        if(sat) s.flags|=SAMPLE_SATURATED;
        if(!c.adc_config_ok) s.flags|=SAMPLE_INVALID;
        float v[8];
        for(int j=0;j<8;j++) v[j]=c.adc_config_ok && c.voltage_calibrated && !(sat&(1u<<j))
            ? s.raw[j]*(control_full_scale(c.range[j])/32768.0f)*c.gain[j]+c.offset[j] : NAN;
        /* v[5] is a semantic current-output voltage; raw[5] remains the unused AD input. */
        v[CH_CURRENT]=cur.status==CURRENT_OK ? cur.raw*c.current_adc_gain+c.current_adc_offset : NAN;
        uint32_t fired=trigger_sample(v,s.t_us);
        if(fired) { s.flags|=SAMPLE_TRIGGER; log_triggers(&c,&s,v,fired); }
        float mean,rms,amps=c.current_valid?(v[5]-c.current_zero)/c.current_volts_per_amp:NAN;
        bool valid=current_window_add(&window,s.t_us+(cur.begin_us+cur.end_us)/2,amps,&mean,&rms);
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
        storage_push(&s); xSemaphoreGive(first_sample);
    }
}

/* Command manager is the only caller of mode/range/profile commits. */
static bool pause_adc(void) {
    if(adc_paused) return true;
    transitioning=true; board_inhibit(true); board_kill(); run_permission=false;
    pause_requested=true; esp_timer_stop(timer); xTaskNotifyGive(adc_task);
    if(xSemaphoreTake(pause_ack,pdMS_TO_TICKS(500))!=pdTRUE) return false;
    adc_paused=true; return true;
}
static bool resume_adc(void) {
    while(xSemaphoreTake(first_sample,0)==pdTRUE) {}
    pause_requested=false; xSemaphoreGive(resume_sem); adc_paused=false;
    if(esp_timer_start_periodic(timer,1000000/CONFIG_EGR_SAMPLE_HZ)!=ESP_OK) return false;
    return xSemaphoreTake(first_sample,pdMS_TO_TICKS(100))==pdTRUE;
}
static bool commit_locked(const char *reason) {
    uint64_t start=esp_timer_get_time(); uint32_t epoch=atomic_load(&stop_epoch);
    uint32_t gate=board_stop_token();
    if(!pause_adc()) { fault_locked("PAUSE_TIMEOUT"); return false; }
    bool ok=board_mode(ctrl.test_bank,ctrl.sensor_on)==ESP_OK;
    sensor_enabled=ok && ctrl.sensor_on;
    bool sw=board_adc_software_mode(); control_apply_ranges(&ctrl.profile,sw);
    uint8_t applied[8]; memset(applied,RANGE_UNKNOWN,sizeof applied);
    if(ok) ok=board_adc_ranges(ctrl.profile.range,applied)==ESP_OK && board_adc_config_ok();
    if(next_id>UINT16_MAX) ok=false;
    session_config_t candidate;
    if(ok) {
        control_build_config(&ctrl,&candidate,(uint16_t)next_id,applied,sw,true);
        ok=storage_config(&candidate); /* persistent metadata before ID publication */
    }
    if(!ok || stop_epoch!=epoch || stop_pending) {
        board_mode(ctrl.test_bank,false); sensor_enabled=false;
        fault_locked(!ok?"CONFIG_COMMIT":"STOP_DURING_CONFIG");
        return false; /* remain paused; stop can retry, storage errors require reboot */
    }
    active_cfg=candidate; next_id++;
    trigger_configure(&active_cfg,CONFIG_EGR_SAMPLE_HZ); xQueueReset(zero_summary);
    storage_event("{\"type\":\"config_gap\",\"start_us\":%" PRIu64 ",\"end_us\":%" PRIu64
        ",\"config_id\":%u,\"reason\":\"%s\"}",start,(uint64_t)esp_timer_get_time(),active_cfg.id,reason);
    if(!resume_adc()) { fault_locked("ADC_RESTART"); return false; }
    if(ctrl.state==SENSOR_CHECK) { ctrl.started=esp_timer_get_time(); ctrl.deadline=ctrl.started+2000000; }
    transitioning=false;
    if(stop_epoch==epoch && !stop_pending && acquisition_healthy && storage_ok() && ctrl.state!=FAULT)
        board_release(gate);
    return true;
}
static bool zero_locked(void) {
    inputs_t in=snapshot();
    if((ctrl.state!=SAFE && ctrl.state!=READY) || in.log_present ||
       !ctrl.profile.current_valid[ctrl.test_bank?1:0]) return false;
    /* No LOGGER plug: the ECU must be physically absent from the zero-current
     * fixture. TEST motor is inhibited throughout the new full-second window. */
    if(!commit_locked("zero_begin")) return false;
    transitioning=true; board_inhibit(true); board_kill();
    uint32_t epoch=stop_epoch; uint16_t id=active_cfg.id; int bank=active_cfg.bank;
    summary_t s; bool got=xQueueReceive(zero_summary,&s,pdMS_TO_TICKS(1800))==pdTRUE;
    bool ok=got && s.config_id==id && s.bank==bank && s.t_us-s.start_us>=1000000
        && s.valid_count[5]==s.count && s.count>=(unsigned)CONFIG_EGR_SAMPLE_HZ*9/10 && isfinite(s.mean[5])
        && isfinite(s.min[5]) && isfinite(s.max[5]) && s.max[5]-s.min[5]<.02f
        && s.mean[5]>1 && s.mean[5]<4 && stop_epoch==epoch && !stop_pending && acquisition_healthy;
    if(ok) ctrl.profile.current_zero[bank]=s.mean[5];
    if(stop_pending) return false;
    return commit_locked(ok?"zero_commit":"zero_rejected") && ok;
}
static void log_campaign_locked(void) {
    campaign_t *p=&ctrl.soak; if(!p->point_ready) return;
    char n[7][32];
    storage_event("{\"type\":\"hotsoak_point\",\"t_us\":%" PRIu64 ",\"index\":%d,\"config_id\":%u,"
        "\"tc1\":%s,\"tc2\":%s,\"vbat\":%s,\"i_break_open\":%s,\"i_break_close\":%s,"
        "\"ms_10_90\":%s,\"ms_90_10\":%s,\"current_metric\":\"sample_mean_20ms\",\"metric_qualified\":%s}",
        (uint64_t)esp_timer_get_time(),p->done,active_cfg.id,json_number(n[0],p->t1),json_number(n[1],p->t2),
        json_number(n[2],p->vbat),json_number(n[3],p->i_break_open),json_number(n[4],p->i_break_close),
        json_number(n[5],p->ms_open),json_number(n[6],p->ms_close),ctrl.profile.current_window_qualified?"true":"false");
    p->point_ready=false;
}
static void safety(void *unused) {
    (void)unused; TickType_t wake=xTaskGetTickCount(); uint64_t last_beat=0; state_t prior=SAFE;
    bool was_mark=false, heart_ok=false;
    while(true) {
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
            radio_allowed=i.test_present && !i.log_present && !transitioning && ctrl.state!=LOGGER
                && ctrl.state!=IDENTIFY && ctrl.state!=FAULT;
            xSemaphoreGive(control_mutex);
        }
        if(stop_pending || transitioning) { board_kill(); run_permission=false; }
        if(i.now-last_beat>=10000) {
            board_heartbeat(heart_ok && !stop_pending && acquisition_healthy && i.now>=i.sample_time
                && i.now-i.sample_time<10000); last_beat=i.now;
        }
        bool mark=board_mark(); if(mark && !was_mark) storage_mark(i.now); was_mark=mark;
        vTaskDelayUntil(&wake,pdMS_TO_TICKS(1));
    }
}
static void log_summary(const summary_t *s) {
    char line[JSON_EVENT_MAX]; json_buf_t b; json_init(&b,line,sizeof line);
    json_add(&b,"{\"type\":\"summary\",\"t_us\":%" PRIu64 ",\"config_id\":%u,\"bank\":%d,\"n\":%u,\"ch\":[",
        s->t_us,s->config_id,s->bank,(unsigned)s->count);
    for(int j=0;j<8;j++) { char a[32],m[32],z[32];
        json_add(&b,"%s[%s,%s,%s]",j?",":"",json_number(a,s->min[j]),json_number(m,s->mean[j]),json_number(z,s->max[j])); }
    json_add(&b,"]}"); if(b.ok) storage_event("%s",line);
}
static void auxiliary(void *unused) {
    (void)unused; uint64_t last_tc=0,last_io=0; uint32_t drops=0; (void)drops;
    while(true) {
        uint64_t now=esp_timer_get_time();
        if(now-last_io>=20000) {
            bool fault=true,log=true,test=false;
            bool io_ok=board_inputs(&fault,&log,&test)==ESP_OK;
            if(!io_ok) { fault=true; log=true; test=false; }
            uint64_t completed=io_ok?esp_timer_get_time():0;
            portENTER_CRITICAL(&data_mux); latest.sensor_fault=fault; latest.log_present=log; latest.test_present=test;
            inputs_time=completed;
            portEXIT_CRITICAL(&data_mux); last_io=now;
        }
        #if CONFIG_EGR_CAN_PRESENT
        twai_message_t m;
        if(twai_receive(&m,pdMS_TO_TICKS(2))==ESP_OK) {
            now=esp_timer_get_time();
            char hex[17]={0}; unsigned len=m.data_length_code>8?8:m.data_length_code;
            for(unsigned j=0;j<len;j++) snprintf(hex+j*2,3,"%02x",m.data[j]);
            storage_event("{\"type\":\"can\",\"t_us\":%" PRIu64 ",\"id\":%" PRIu32 ",\"ext\":%d,\"rtr\":%d,\"data\":\"%s\"}",
                now,m.identifier,m.extd,m.rtr,hex);
            if(!m.extd && !m.rtr && m.identifier>=0x7e8 && m.identifier<=0x7ef && len>=5
                && m.data[0]>=4 && m.data[0]<=7 && m.data[1]==0x41 && m.data[2]==0x0c)
                storage_event("{\"type\":\"rpm_obd\",\"t_us\":%" PRIu64 ",\"rpm\":%.2f}",now,((unsigned)m.data[3]*256+m.data[4])/4.0);
        }
        #endif
        #if !CONFIG_EGR_CAN_PRESENT
        vTaskDelay(pdMS_TO_TICKS(2));
        #endif
        summary_t s; while(xQueueReceive(summaries,&s,0)==pdTRUE) log_summary(&s);
        if(now-last_tc>=200000) {
            float t[2]={NAN,NAN}; uint8_t fault[2]={255,255};
            for(int j=0;j<2;j++) {
                if(board_temperature(j,&t[j],&fault[j])!=ESP_OK) { t[j]=NAN; fault[j]=255; }
                char n[32]; storage_event("{\"type\":\"temperature\",\"t_us\":%" PRIu64 ",\"channel\":%d,\"celsius\":%s,\"fault\":%u}",
                    now,j+1,json_number(n,t[j]),fault[j]);
            }
            portENTER_CRITICAL(&data_mux); latest.t1=t[0]; latest.t2=t[1]; tc_valid=!fault[0]; tc_time=now; portEXIT_CRITICAL(&data_mux);
            last_tc=now;
            #if CONFIG_EGR_CAN_PRESENT
            twai_status_info_t status;
            if(twai_get_status_info(&status)==ESP_OK && status.rx_missed_count!=drops) {
                drops=status.rx_missed_count; storage_event("{\"type\":\"can_drop\",\"count\":%" PRIu32 "}",drops);
            }
            #endif
        }
    }
}
static void radio(void *unused) {
    (void)unused;
    while(true) {
        if(radio_allowed && !webui_running()) { webui_start(); if(!webui_running()) vTaskDelay(pdMS_TO_TICKS(5000)); }
        if(!radio_allowed && webui_running()) webui_stop();
        vTaskDelay(pdMS_TO_TICKS(200));
    }
}
static bool valid_id(const char *s) {
    if(!*s) return false;
    for(;*s;s++) if(!((*s>='a'&&*s<='z') || (*s>='A'&&*s<='Z') || (*s>='0'&&*s<='9') || *s=='_' || *s=='-')) return false;
    return true;
}
static void print_profile(void) {
    printf("bind %s %s\ndaqmodule %s\nsession %s %s\n",ctrl.profile.valve,ctrl.profile.adapter,
        ctrl.profile.daq_module,ctrl.profile.vehicle_id,ctrl.profile.session_note);
    for(int b=0;b<2;b++) {
        for(int j=0;j<8;j++) printf("cal %d %d %.9g %.9g\n",b,j,ctrl.profile.gain[b][j],ctrl.profile.offset[b][j]);
        printf("auxcal %d %.9g %.9g\ncurrentcal %d %.9g\n",b,ctrl.profile.aux_gain[b],ctrl.profile.aux_offset[b],b,ctrl.profile.current_zero[b]);
    }
    for(int b=0;b<2;b++) printf("imodule %d %s\niscal %d %.9g %.9g %.9g\nicalok %d %d\n",b,ctrl.profile.current_module[b],b,
        ctrl.profile.current_adc_gain[b],ctrl.profile.current_adc_offset[b],ctrl.profile.current_volts_per_amp[b],b,ctrl.profile.current_calibrated[b]);
    printf("vcalok 0 %d\nvcalok 1 %d\nlimits %.9g %.9g %.9g\nmetric %d\n",ctrl.profile.voltage_calibrated[0],ctrl.profile.voltage_calibrated[1],ctrl.profile.max_duty,ctrl.profile.current_limit,ctrl.profile.temp_limit,ctrl.profile.current_window_qualified);
}
static bool execute_locked(const char *line) {
    char cmd[24]; float a=0,z=0; int b=0; if(sscanf(line,"%23s %f %f",cmd,&a,&z)<1) return false;
    if(!isfinite(a) || !isfinite(z) || fabsf(a)>10000 || fabsf(z)>10000) return false;
    b=(int)z; if(!strcmp(cmd,"cycle") || !strcmp(cmd,"friction")) b=(int)a;
    if(!strcmp(cmd,"imodule") && ctrl.state==SAFE) {
        int bank; char id[24],extra;
        if(sscanf(line,"%*s %d %23s %c",&bank,id,&extra)!=2 || bank<0 || bank>1 || !valid_id(id)) return false;
        if(strcmp(ctrl.profile.current_module[bank],id)) {
            strcpy(ctrl.profile.current_module[bank],id);
            ctrl.profile.current_calibrated[bank]=false; ctrl.profile.current_valid[bank]=false;
            ctrl.profile.current_window_qualified=false; ctrl.profile.qualified=false;
        }
        return commit_locked("current_module");
    }
    if(!strcmp(cmd,"daqmodule") && ctrl.state==SAFE) {
        char id[24],extra;
        if(sscanf(line,"%*s %23s %c",id,&extra)!=1 || !valid_id(id)) return false;
        if(strcmp(ctrl.profile.daq_module,id)) {
            strcpy(ctrl.profile.daq_module,id);
            ctrl.profile.voltage_calibrated[0]=ctrl.profile.voltage_calibrated[1]=false;
            ctrl.profile.qualified=false;
        }
        return commit_locked("daq_module");
    }
    if(!strcmp(cmd,"session") && ctrl.state==SAFE) {
        char v[24],n[24],extra;
        if(sscanf(line,"%*s %23s %23s %c",v,n,&extra)!=2 || !valid_id(v) || !valid_id(n)) return false;
        strcpy(ctrl.profile.vehicle_id,v);strcpy(ctrl.profile.session_note,n);return commit_locked("session");
    }
    if(!strcmp(cmd,"qualify") && ctrl.state==SAFE) {
        if(a!=1 || !EGR_HARDWARE_ACCEPTED || !ctrl.profile.voltage_calibrated[1] || !ctrl.profile.current_calibrated[1] || !ctrl.profile.current_window_qualified) return false;
        ctrl.profile.qualified=true;return commit_locked("hardware_acceptance");
    }
    if(!strcmp(cmd,"profile")) { print_profile(); return true; }
    if(!strcmp(cmd,"status")) {
        inputs_t i=snapshot();
        printf("%s fault=%s cfg=%u bank=%d map(s,g,f)=%d,%d,%d adc=%d I=%.5g ratio=%.5g pos=%.5g T1=%.5g lost=%u/%u\n",
            control_name(ctrl.state),ctrl.fault?ctrl.fault:"",active_cfg.id,active_cfg.bank,
            active_cfg.ch_supply,active_cfg.ch_ground,active_cfg.ch_feedback,i.adc_ok,
            control_current(&ctrl,&i),control_ratio(&ctrl,&i),control_position(&ctrl,&i),i.t1,
            (unsigned)lost_ticks,(unsigned)storage_lost_events()); return true;
    }
    if(!strcmp(cmd,"mark")) { storage_mark(esp_timer_get_time()); return true; }
    if(!strcmp(cmd,"zero")) return zero_locked();
    if(!strcmp(cmd,"save") && ctrl.state==SAFE && profile_valid(&ctrl.profile)) {
        if(!pause_adc()) return false;
        esp_err_t e=nvs_set_blob(nvs,"profile5",&ctrl.profile,sizeof ctrl.profile);
        if(e==ESP_OK) e=nvs_commit(nvs);
        return commit_locked("save") && e==ESP_OK;
    }
    if(!strcmp(cmd,"bind") && ctrl.state==SAFE) {
        char v[24],h[24],extra;
        if(sscanf(line,"%*s %23s %23s %c",v,h,&extra)!=2 || !valid_id(v) || !valid_id(h)) return false;
        if(strcmp(v,ctrl.profile.valve) || strcmp(h,ctrl.profile.adapter)) {
            ctrl.profile.ch_supply=ctrl.profile.ch_ground=ctrl.profile.ch_feedback=-1;
            ctrl.profile.learned=false; ctrl.profile.closed=ctrl.profile.open=0;
            ctrl.profile.qualified=false;
            if(strcmp(h,ctrl.profile.adapter)) {
                ctrl.profile.voltage_calibrated[0]=ctrl.profile.voltage_calibrated[1]=false;
                ctrl.profile.current_calibrated[0]=ctrl.profile.current_calibrated[1]=false;
                ctrl.profile.current_valid[0]=ctrl.profile.current_valid[1]=false;
                ctrl.profile.current_window_qualified=false;
            }
        }
        strcpy(ctrl.profile.valve,v); strcpy(ctrl.profile.adapter,h); return commit_locked("bind");
    }
    if(!strcmp(cmd,"learn") && ctrl.state==READY) {
        profile_t p=ctrl.profile; int sign; char extra;
        if(sscanf(line,"%*s %f %f %d %c",&p.closed,&p.open,&sign,&extra)!=3) return false;
        p.opening_sign=sign; p.learned=true;
        if(!profile_valid(&p)) return false;
        ctrl.profile=p; return commit_locked("learn");
    }
    if(ctrl.state==SAFE && profile_command(&ctrl.profile,line)) return commit_locked("calibration");
    if((ctrl.state==SAFE || ctrl.state==LOGGER) && (!strcmp(cmd,"aux") || !strcmp(cmd,"bypass"))) {
        if(a!=0 && a!=1) return false;
        if(!strcmp(cmd,"aux")) ctrl.profile.aux_position=(uint8_t)a;
        else {
            int bank=ctrl.test_bank?1:0;
            if(a==0 && !ctrl.profile.current_calibrated[bank]) return false;
            ctrl.profile.current_valid[bank]=a==0;
        }
        return commit_locked(cmd);
    }
    if(!strcmp(cmd,"bank") && ctrl.state==SAFE && (a==0 || a==1)) {
        ctrl.test_bank=a!=0; ctrl.sensor_on=false; return commit_locked("bank");
    }
#if !CONFIG_EGR_ACTIVE_TEST
    if(strcmp(cmd,"logger") && strcmp(cmd,"identify") && strcmp(cmd,"stop")) return false;
#endif
    if(!control_command(&ctrl,cmd,a,b,esp_timer_get_time())) return false;
    if(!strcmp(cmd,"test") || !strcmp(cmd,"logger") || !strcmp(cmd,"stop") || !strcmp(cmd,"hotsoak_stop"))
        return commit_locked(cmd);
    return true;
}
static void manager(void *unused) {
    (void)unused;
    xSemaphoreTake(control_mutex,portMAX_DELAY); commit_locked("boot"); xSemaphoreGive(control_mutex);
    while(true) {
        if(atomic_exchange(&stop_pending,false)) {
            xSemaphoreTake(control_mutex,portMAX_DELAY); control_stop(&ctrl); commit_locked("stop"); xSemaphoreGive(control_mutex);
        }
        if(atomic_exchange(&config_pending,false)) {
            xSemaphoreTake(control_mutex,portMAX_DELAY); commit_locked("state_change"); xSemaphoreGive(control_mutex);
        }
        request_t r;
        if(xQueueReceive(requests,&r,pdMS_TO_TICKS(20))!=pdTRUE) continue;
        if(r.epoch!=stop_epoch || stop_pending) continue;
        xSemaphoreTake(control_mutex,portMAX_DELAY);
        bool ok=execute_locked(r.line);
        xSemaphoreGive(control_mutex);
        printf("%s: %s\n",ok?"OK":"REJECTED",r.line);
        storage_event("{\"type\":\"command_result\",\"t_us\":%" PRIu64 ",\"accepted\":%s}",
            (uint64_t)esp_timer_get_time(),ok?"true":"false");
    }
}
static void status_json(char *out,size_t len) {
    if(xSemaphoreTake(control_mutex,pdMS_TO_TICKS(5))!=pdTRUE) {
        snprintf(out,len,"{\"stan\":\"CONFIGURING\",\"fault\":\"\"}"); return;
    }
    inputs_t i=snapshot(); char p[32],r[32],a[32],v[32],t1[32],t2[32],vs[32],vg[32],vf[32];
    int cs=active_cfg.ch_supply,cg=active_cfg.ch_ground,cf=active_cfg.ch_feedback;
    bool mapped=cs>=2 && cs<=4 && cg>=2 && cg<=4 && cf>=2 && cf<=4;
    int written=snprintf(out,len,"{\"stan\":\"%s\",\"fault\":\"%s\",\"pozycja\":%s,\"ratio\":%s,\"prad_A\":%s,"
        "\"VBAT_V\":%s,\"TC1_C\":%s,\"TC2_C\":%s,\"uzbrojony\":%s,\"adapter\":\"%s\",\"config_id\":%u,"
        "\"pin_zasil_V\":%s,\"pin_masa_V\":%s,\"pin_sygnal_V\":%s}",
        control_name(ctrl.state),ctrl.fault?ctrl.fault:"",json_number(p,control_position(&ctrl,&i)),
        json_number(r,control_ratio(&ctrl,&i)),json_number(a,control_current(&ctrl,&i)),json_number(v,i.v[6]),
        json_number(t1,i.t1),json_number(t2,i.t2),i.hw_armed?"true":"false",i.test_present?"TEST":i.log_present?"LOGGER":"brak",active_cfg.id,
        json_number(vs,mapped?i.v[cs]:NAN),json_number(vg,mapped?i.v[cg]:NAN),json_number(vf,mapped?i.v[cf]:NAN));
    if(written<0 || (size_t)written>=len) snprintf(out,len,"{\"stan\":\"STATUS_ERROR\"}");
    xSemaphoreGive(control_mutex);
}
static bool web_command(const char *cmd,float a,int b) {
    if(!isfinite(a) || fabsf(a)>10000) return false;
    char line[96];
    if(!strcmp(cmd,"stop")) return enqueue("stop");
    if(!strcmp(cmd,"cycle") || !strcmp(cmd,"friction")) snprintf(line,sizeof line,"%s %d",cmd,b);
    else snprintf(line,sizeof line,"%s %.9g %d",cmd,a,b);
    return enqueue(line);
}
static void console(void *unused) {
    (void)unused; char line[160]; puts("EGRLab v6: commands are queued; STOP is immediate.");
    while(true) {
        if(!fgets(line,sizeof line,stdin)) { vTaskDelay(pdMS_TO_TICKS(20)); continue; }
        line[strcspn(line,"\r\n")]=0;
        if(!*line) continue;
        puts(enqueue(line)?"QUEUED":"QUEUE FULL / INVALID");
    }
}
void app_main(void) {
    ESP_ERROR_CHECK(nvs_flash_init()); ESP_ERROR_CHECK(nvs_open("egrlab",NVS_READWRITE,&nvs));
    control_init(&ctrl); profile_t saved; size_t bytes=sizeof saved;
    if(nvs_get_blob(nvs,"profile5",&saved,&bytes)==ESP_OK && bytes==sizeof saved && profile_valid(&saved)) ctrl.profile=saved;
    ctrl.profile.qualified=ctrl.profile.qualified && EGR_HARDWARE_ACCEPTED;
    uint32_t session=0; nvs_get_u32(nvs,"session",&session); session++;
    ESP_ERROR_CHECK(nvs_set_u32(nvs,"session",session)); ESP_ERROR_CHECK(nvs_commit(nvs));
    ESP_LOGI(TAG,"PSRAM=%u; hardware accepted=%d",(unsigned)esp_psram_get_size(),EGR_HARDWARE_ACCEPTED);
    ESP_ERROR_CHECK(board_init()); board_inhibit(true); ESP_ERROR_CHECK(board_sd_mount());
    #if CONFIG_EGR_CORE_ONLY
    puts("CORE: init, MCP, PSRAM and SD mount complete; acquisition disabled. Use bench_core.txt checklist.");
    FILE *probe=fopen("/sd/core_probe.tmp","wb");
    if(probe) { fputs("EGRLab-v6 CORE SD probe\n",probe); fclose(probe); }
    return;
#endif
    if(!storage_init(session,CONFIG_EGR_SAMPLE_HZ)) { board_kill(); ESP_LOGE(TAG,"storage init"); return; }
    control_mutex=xSemaphoreCreateMutex(); pause_ack=xSemaphoreCreateBinary(); resume_sem=xSemaphoreCreateBinary(); first_sample=xSemaphoreCreateBinary();
    requests=xQueueCreate(16,sizeof(request_t)); summaries=xQueueCreate(8,sizeof(summary_t)); zero_summary=xQueueCreate(1,sizeof(summary_t));
    configASSERT(control_mutex && pause_ack && resume_sem && first_sample && requests && summaries && zero_summary);
    latest.t1=latest.t2=NAN; latest.log_present=true; latest.sensor_fault=true;
    configASSERT(xTaskCreatePinnedToCore(acquisition,"adc",8192,NULL,23,&adc_task,1)==pdPASS);
    esp_timer_create_args_t ta={.callback=tick,.dispatch_method=ESP_TIMER_TASK,.name="sample"};
    ESP_ERROR_CHECK(esp_timer_create(&ta,&timer)); webui_init(status_json,web_command);
    configASSERT(xTaskCreatePinnedToCore(storage_writer,"writer",8192,NULL,8,NULL,0)==pdPASS);
    configASSERT(xTaskCreatePinnedToCore(auxiliary,"aux",8192,NULL,5,NULL,0)==pdPASS);
    configASSERT(xTaskCreatePinnedToCore(safety,"safety",8192,NULL,20,NULL,0)==pdPASS);
    configASSERT(xTaskCreatePinnedToCore(manager,"manager",12288,NULL,6,NULL,0)==pdPASS);
    configASSERT(xTaskCreatePinnedToCore(radio,"radio",6144,NULL,3,NULL,0)==pdPASS);
    configASSERT(xTaskCreatePinnedToCore(console,"console",4096,NULL,3,NULL,0)==pdPASS);
}
