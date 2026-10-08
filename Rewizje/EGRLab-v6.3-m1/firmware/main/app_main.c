#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdatomic.h>
#include <inttypes.h>
#include <stdarg.h>
#include "sdkconfig.h"
#include "board.h"
#include "control.h"
#include "storage.h"
#include "trigger.h"
#include "measure.h"
#include "jsonlog.h"
#include "webui.h"
#include "commissioning.h"
#include "obd.h"
#include "esp_timer.h"
#include "esp_rom_sys.h"
#include "esp_psram.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "nvs.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "freertos/queue.h"
#ifndef CONFIG_EGR_SW_CURRENT_LIMIT
#define CONFIG_EGR_SW_CURRENT_LIMIT 0
#endif
#ifndef CONFIG_EGR_SW_CURRENT_LIMIT_MA
#define CONFIG_EGR_SW_CURRENT_LIMIT_MA 8000
#endif
#ifndef CONFIG_EGR_CAN_PRESENT
#define CONFIG_EGR_CAN_PRESENT 0
#endif

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
/* 6.3-m1 (M-10/M-11): brak PFAIL_N. Tryb bez karty: SD niezamontowana (np. tylko USB - peryferia 3,3 V bez
 * zasilania, D-M1-6) -> bez plikow i bez TEST, konsola i podglad dzialaja. Zastepuje tryb stolowy F-02. */
static bool bench_mode;
static _Atomic uint32_t stop_epoch, lost_ticks, trigger_count, sample_count, overcurrent_count;
static bool adc_paused; /* command manager only */
static bool tc_valid;
static uint64_t tc_time, inputs_time;
static const char *TAG="EGRLab-6.3.1-m1";
/* 6.3.1-m1 (recenzja M1-08): konsola nie wypisuje pod control_mutex. execute_locked() sklada odpowiedz w out_buf,
 * manager wypisuje ja po zwolnieniu blokady (UART 115200: 575 B profilu = ok. 50 ms). Tylko zadanie manager. */
static char out_buf[2048]; static size_t out_len;
static void outf(const char *fmt,...) {
    va_list ap; va_start(ap,fmt); size_t room=sizeof out_buf-out_len;
    int n=vsnprintf(out_buf+out_len,room,fmt,ap); va_end(ap);
    if(n>0) out_len+=(size_t)n<room ? (size_t)n : room-1;
}
/* M1-08: przycisk STOP i granica czasu ruchu niezalezne od dostepnosci managera (zadanie safety). */
#define CONTROL_STALE_US 20000
static _Atomic int shown_state=SAFE;
/* M1-09: po bledzie odczytu ADC probki sa niewazne do ponownej konfiguracji z nowym config_id (manager). */
static _Atomic bool adc_recover_pending;
static uint64_t recover_after;

static inputs_t snapshot(void) {
    portENTER_CRITICAL(&data_mux); inputs_t i=latest; bool valid=tc_valid;
    uint64_t tt=tc_time, it=inputs_time; portEXIT_CRITICAL(&data_mux);
    i.now=esp_timer_get_time();
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
            adc_failing=true; adc_recover_pending=true; continue;
        }
        adc_failing=false;
        /* 6.3.1-m1 (recenzja M1-09): migawka active_cfg nie wystarcza - po bledzie driver ma config_ok=false do udanej
         * rekonfiguracji (nowy config_id). Do tego czasu probki INVALID, bez wartosci fizycznych i bez triggerow. */
        bool cfg_ok=c.adc_config_ok && board_adc_config_ok();
        memcpy(s.raw,raw,sizeof raw); s.t_us=sample_time;
        /* M-04: rekord v5 bez zmian; pola MCP3201 puste (65535 / status 2 = ABSENT), prad jest w raw[5]. */
        s.current_raw=65535; s.current_begin_us=0; s.current_end_us=0; s.current_status=2;
#if CONFIG_EGR_SW_CURRENT_LIMIT
        /* M-06: przed czymkolwiek innym - ograniczenie pradu dziala na kazdej probce, takze bez kalibracji. */
        float i_oc=overcurrent_amps(raw[CH_CURRENT],control_full_scale(c.range[CH_CURRENT]),c.gain[CH_CURRENT],
            c.offset[CH_CURRENT],c.current_zero,c.current_volts_per_amp);
        if(cfg_ok && overcurrent_sample(&oc,i_oc,CONFIG_EGR_SW_CURRENT_LIMIT_MA/1000.0f,2)) {
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
        if(!cfg_ok) s.flags|=SAMPLE_INVALID;
        float v[8];
        for(int j=0;j<8;j++) v[j]=cfg_ok && c.voltage_calibrated && !(sat&(1u<<j))
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
    /* F-04: najpierw konfiguracja AD7606B z odczytem kontrolnym, dopiero po niej tryb (M1: tylko SENS_EN,
     * bez MEAS_EN i przekaznikow). Blad konfiguracji = zasilanie czujnika wylaczone. */
    bool sw=board_adc_software_mode(); control_apply_ranges(&ctrl.profile,sw);
    uint8_t applied[8]; memset(applied,RANGE_UNKNOWN,sizeof applied);
    bool adc_ok=board_adc_ranges(ctrl.profile.range,applied)==ESP_OK && board_adc_config_ok();
    bool ok=adc_ok && board_mode(ctrl.test_bank,ctrl.sensor_on)==ESP_OK;
    sensor_enabled=ok && ctrl.sensor_on;
    if(next_id>UINT16_MAX) ok=false;
    session_config_t candidate;
    if(ok) {
        control_build_config(&ctrl,&candidate,(uint16_t)next_id,applied,sw,true);
        ok=storage_config(&candidate); /* persistent metadata before ID publication */
    }
    if(!ok || stop_epoch!=epoch || stop_pending) {
        if(adc_ok) board_mode(ctrl.test_bank,false); else board_sensor_off();
        sensor_enabled=false;
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
    if((ctrl.state!=SAFE && ctrl.state!=READY) || !ctrl.profile.current_valid[ctrl.test_bank?1:0]) return false;
    /* M-04: zero (VS/2) mierzone przy wylaczonym mostku i bez pradu ECU - nie stala 2,5 V. Bez detekcji adaptera
     * (M-01) warunek "bez ECU" sprawdza control_zero_ok(): linie silnika CH1/CH2 bez napiecia przez cala sekunde. */
    if(!commit_locked("zero_begin")) return false;
    transitioning=true; board_inhibit(true); board_kill();
    uint32_t epoch=stop_epoch; uint16_t id=active_cfg.id; int bank=active_cfg.bank;
    summary_t s; bool got=xQueueReceive(zero_summary,&s,pdMS_TO_TICKS(1800))==pdTRUE;
    bool ok=got && s.config_id==id && s.bank==bank && s.t_us-s.start_us>=1000000
        && s.valid_count[5]==s.count && s.valid_count[0]==s.count && s.valid_count[1]==s.count
        && s.count>=(unsigned)CONFIG_EGR_SAMPLE_HZ*9/10 && control_zero_ok(s.mean,s.min,s.max)
        && stop_epoch==epoch && !stop_pending && acquisition_healthy;
    if(ok) ctrl.profile.current_zero[bank]=s.mean[5];
    if(stop_pending) return false;
    return commit_locked(ok?"zero_commit":"zero_rejected") && ok;
}
static void log_campaign_locked(void) {
    campaign_t *p=&ctrl.soak; if(!p->point_ready) return;
    char n[7][32];
    storage_event("{\"type\":\"hotsoak_point\",\"t_us\":%" PRIu64 ",\"index\":%d,\"config_id\":%u,"
        "\"tc1\":%s,\"tc2\":%s,\"vbat\":%s,\"vbat_source\":\"vmotor_x1_3\",\"i_break_open\":%s,\"i_break_close\":%s,"
        "\"ms_10_90\":%s,\"ms_90_10\":%s,\"current_metric\":\"sample_mean_20ms\",\"metric_qualified\":%s}",
        (uint64_t)esp_timer_get_time(),p->done,active_cfg.id,json_number(n[0],p->t1),json_number(n[1],p->t2),
        json_number(n[2],p->vbat),json_number(n[3],p->i_break_open),json_number(n[4],p->i_break_close),
        json_number(n[5],p->ms_open),json_number(n[6],p->ms_close),ctrl.profile.current_window_qualified?"true":"false");
    p->point_ready=false;
}
/* M-12: dioda RGB modulu zamiast HEART (GPIO21 to teraz LPWM). Miga 2 Hz, gdy probki ida; stala = akwizycja stoi.
 * Kolor: zielony LOGGER, niebieski SAFE, zolty TEST (bez ruchu), bialy ruch, czerwony FAULT, fioletowy bez karty. */
static uint32_t led_colour(state_t st, bool alive) {
    if(st==FAULT) return 0x200000;
    if(bench_mode) return 0x100010;
    if(!alive) return 0x200000;
    if(st==LOGGER || st==IDENTIFY) return 0x002000;
    if(st==SAFE) return 0x000020;
    return control_moving(&ctrl) ? 0x181818 : 0x181000;
}
/* M-12: START / STOP (GPIO15, aktywny L). Filtr 20 ms. W stanach TEST kazde nacisniecie = STOP natychmiast.
 * Poza TEST: krotkie (< 1 s) = znacznik mark; dlugie (>= 1 s) = SAFE -> LOGGER albo LOGGER -> STOP. */
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
    (void)unused; TickType_t wake=xTaskGetTickCount(); uint64_t last_beat=0, last_eval=0; state_t prior=SAFE;
    bool heart_ok=false, blink=false, sens_warned=false;
    /* M-06: to zadanie karmi TWDT i RTC WDT; zawieszenie = panika (DRIVE_EN w dol) albo reset systemu.
     * 6.3.1-m1 (recenzja M1-03): nieudany start = trwala blokada - board_release() odmawia bez board_watchdogs_ok(),
     * "test" jest odrzucany; nic poza restartem tego nie kasuje. */
    if(board_watchdogs_start()!=ESP_OK) {
        ESP_LOGE(TAG,"watchdog: start nieudany - TEST zablokowany do restartu"); board_emergency_stop();
        storage_event("{\"type\":\"watchdog_failed\",\"t_us\":%" PRIu64 "}",(uint64_t)esp_timer_get_time());
    }
    while(true) {
        inputs_t i=snapshot(); bool evaluated=false;
        if(xSemaphoreTake(control_mutex,0)==pdTRUE) {
            i=snapshot(); /* fresh AFTER acquiring the lock */
            if(!transitioning && !stop_pending) {
                int8_t map[3]={ctrl.profile.ch_supply,ctrl.profile.ch_ground,ctrl.profile.ch_feedback};
                control_step(&ctrl,&i); evaluated=true; last_eval=i.now;
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
            shown_state=ctrl.state;
            xSemaphoreGive(control_mutex);
        }
        /* 6.3.1-m1 (recenzja M1-08): przycisk czytany w kazdym obiegu, takze gdy manager trzyma blokade; STOP nie czeka. */
        button_tick(i.now,(state_t)shown_state);
        /* M1-08: ruch tylko przy biezacej ocenie sterowania (koniec impulsu, limity pradu i temperatury profilu).
         * Bez oceny dluzej niz CONTROL_STALE_US napedu nie wolno trzymac - STOP i zdarzenie. */
        if(run_permission && !evaluated && i.now-last_eval>CONTROL_STALE_US) {
            request_stop(); board_kill(); run_permission=false;
            storage_event("{\"type\":\"control_stale\",\"t_us\":%" PRIu64 ",\"age_us\":%" PRIu64 "}",i.now,i.now-last_eval);
        }
        if(stop_pending || transitioning) { board_kill(); run_permission=false; }
        /* M1-08: watchdog karmiony tylko przy postepie oceny sterowania albo w stanie bez napedu. */
        if(evaluated || !run_permission) board_watchdogs_feed();
        if(i.now-last_beat>=250000) {
            bool alive=heart_ok && !stop_pending && acquisition_healthy && i.now>=i.sample_time && i.now-i.sample_time<10000;
            blink=alive ? !blink : true;
            board_led(blink ? led_colour((state_t)shown_state,alive) : 0); last_beat=i.now;
        }
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
    (void)unused; uint64_t last_tc=0,last_io=0,last_stats=0;
    while(true) {
        uint64_t now=esp_timer_get_time();
        if(now-last_io>=20000) {
            /* M-07: SENS_FAULT_N wprost z GPIO42 (bez MCP23017); przy wylaczonym TPS2553 linia jest wysoko. */
            bool fault=board_sensor_fault();
            portENTER_CRITICAL(&data_mux); latest.sensor_fault=fault; inputs_time=esp_timer_get_time();
            portEXIT_CRITICAL(&data_mux); last_io=now;
        }
        /* F-08: odbior CAN ma wlasne zadanie (can_rx); temperatury i SD go nie zatrzymuja. */
        vTaskDelay(pdMS_TO_TICKS(2));
        if(now-last_stats>=10000000) {   /* F-05: CONVST, probki, bledy - co 10 s */
            uint32_t cv,er,rs; board_adc_counters(&cv,&er,&rs);
            uint32_t pend,age,dur; storage_backlog(&pend,&age,&dur);   /* 6.3.1-m1 (M1-04): niezapisana kolejka i ostatni fsync */
            storage_event("{\"type\":\"daq_stats\",\"t_us\":%" PRIu64 ",\"convst\":%" PRIu32 ",\"samples\":%" PRIu32
                ",\"adc_errors\":%" PRIu32 ",\"adc_resets\":%" PRIu32 ",\"lost_ticks\":%" PRIu32 ",\"sample_hz\":%d,\"adc_spi_hz\":%d,"
                "\"soft_event_drops\":%" PRIu32 ",\"overcurrent_samples\":%" PRIu32 ",\"pending_samples\":%" PRIu32
                ",\"since_sync_ms\":%" PRIu32 ",\"sync_ms\":%" PRIu32 "}",now,cv,(uint32_t)atomic_load(&sample_count),er,rs,(uint32_t)lost_ticks,
                CONFIG_EGR_SAMPLE_HZ,CONFIG_EGR_ADC_SPI_HZ,storage_soft_drops(),(uint32_t)atomic_load(&overcurrent_count),pend,age,dur);
            last_stats=now;
        }
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
        }
    }
}
#if CONFIG_EGR_CAN_PRESENT
/* F-08 (P10 R2 docs/INTEGRACJA.md; M1: M-09): osobne zadanie oproznia kolejke TWAI (listen-only, 500 kbit/s).
 * Ramki i RPM to zdarzenia "miekkie": przy pelnej kolejce zdarzen licznik straty, nie bledny zapis DAQ.
 * Co 1 s, gdy cos sie zmienilo: can_stats (zgubione w RX, przepelnienia, bledy magistrali, straty logu).
 * t_us = czas obslugi ramki w tym zadaniu (esp_timer), nie znacznik sprzetowy poczatku ramki. */
static void can_rx(void *unused) {
    (void)unused; obd_rpm_t obd; obd_rpm_init(&obd);
    uint32_t frames=0, logged_drops=0, missed=0, overrun=0, bus=0; uint64_t last=0;
    storage_event("{\"type\":\"can_config\",\"bitrate\":500000,\"mode\":\"listen_only\",\"rx_queue\":128,"
        "\"time_source\":\"rx_task_esp_timer_us\",\"profile\":\"%s\",\"rpm_stale_us\":%u}",OBD_PROFILE,(unsigned)OBD_RPM_STALE_US);
    while(true) {
        twai_message_t m;
        esp_err_t e=twai_receive(&m,pdMS_TO_TICKS(100));
        uint64_t now=esp_timer_get_time();
        if(e==ESP_OK) {
            frames++;
            char hex[17]={0}; unsigned len=m.data_length_code>8?8:m.data_length_code;
            for(unsigned j=0;j<len;j++) snprintf(hex+j*2,3,"%02x",m.data[j]);
            storage_event_soft("{\"type\":\"can\",\"t_us\":%" PRIu64 ",\"id\":%" PRIu32 ",\"ext\":%d,\"rtr\":%d,\"dlc\":%u,\"data\":\"%s\"}",
                now,m.identifier,m.extd,m.rtr,(unsigned)m.data_length_code,hex);
            float rpm; obd_result_t r=obd_rpm_frame(&obd,m.identifier,m.extd,m.rtr,m.data_length_code,m.data,now,&rpm);
            if(r==OBD_RPM_OK)
                storage_event_soft("{\"type\":\"rpm_obd\",\"t_us\":%" PRIu64 ",\"rpm\":%.2f,\"ecu\":%" PRIu32 ",\"profile\":\"%s\"}",
                    now,rpm,obd.ecu,OBD_PROFILE);
            else if(r==OBD_BAD_LENGTH)
                storage_event_soft("{\"type\":\"rpm_rejected\",\"t_us\":%" PRIu64 ",\"id\":%" PRIu32 ",\"reason\":\"isotp_length_vs_dlc\"}",now,m.identifier);
        }
        if(obd.accepted && !obd.stale_reported && !isfinite(obd_rpm_now(&obd,now))) {
            obd.stale_reported=true;   /* brak RPM to brak danych, nie 0 rpm */
            storage_event_soft("{\"type\":\"rpm_stale\",\"t_us\":%" PRIu64 ",\"last_us\":%" PRIu64 ",\"ecu\":%" PRIu32 "}",now,obd.last_us,obd.ecu);
        }
        if(now-last>=1000000) {
            twai_status_info_t st; uint32_t drops=storage_soft_drops();
            if(twai_get_status_info(&st)==ESP_OK && (st.rx_missed_count!=missed || st.rx_overrun_count!=overrun
                    || st.bus_error_count!=bus || drops!=logged_drops)) {
                missed=st.rx_missed_count; overrun=st.rx_overrun_count; bus=st.bus_error_count; logged_drops=drops;
                storage_event("{\"type\":\"can_stats\",\"t_us\":%" PRIu64 ",\"frames\":%" PRIu32 ",\"rx_missed\":%" PRIu32
                    ",\"rx_overrun\":%" PRIu32 ",\"bus_errors\":%" PRIu32 ",\"rx_error_counter\":%" PRIu32 ",\"state\":%d,"
                    "\"log_dropped\":%" PRIu32 ",\"rpm_bad_length\":%" PRIu32 ",\"rpm_other_ecu\":%" PRIu32 "}",
                    now,frames,missed,overrun,bus,st.rx_error_counter,(int)st.state,drops,obd.bad_length,obd.other_ecu);
            }
            last=now;
        }
    }
}
#endif
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
    outf("bind %s %s\ndaqmodule %s\nsession %s %s\n",ctrl.profile.valve,ctrl.profile.adapter,
        ctrl.profile.daq_module,ctrl.profile.vehicle_id,ctrl.profile.session_note);
    for(int b=0;b<2;b++) {
        for(int j=0;j<8;j++) outf("cal %d %d %.9g %.9g\n",b,j,ctrl.profile.gain[b][j],ctrl.profile.offset[b][j]);
        outf("currentcal %d %.9g\n",b,ctrl.profile.current_zero[b]);
    }
    /* 6.3-m1: bez auxcal (brak AUX) i iscal (brak MCP3201); skala pradu CH6 = ivpa (V/A). */
    for(int b=0;b<2;b++) outf("imodule %d %s\nivpa %d %.9g\nicalok %d %d\n",b,ctrl.profile.current_module[b],b,
        ctrl.profile.current_volts_per_amp[b],b,ctrl.profile.current_calibrated[b]);
    outf("vcalok 0 %d\nvcalok 1 %d\nlimits %.9g %.9g %.9g\nmetric %d\n",ctrl.profile.voltage_calibrated[0],ctrl.profile.voltage_calibrated[1],ctrl.profile.max_duty,ctrl.profile.current_limit,ctrl.profile.temp_limit,ctrl.profile.current_window_qualified);
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
            /* 6.3.1-m1 (recenzja M1-11): AD7606B jest teraz czescia toru pradu (CH6) - wymiana DAQ uniewaznia tez odbior pradu. */
            ctrl.profile.current_calibrated[0]=ctrl.profile.current_calibrated[1]=false;
            ctrl.profile.current_window_qualified=false;
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
        inputs_t i=snapshot(); uint32_t pend,age,dur; storage_backlog(&pend,&age,&dur);
        outf("queue=%u since_sync_ms=%u sync_ms=%u wdt=%d\n",(unsigned)pend,(unsigned)age,(unsigned)dur,board_watchdogs_ok());
        outf("%s fault=%s cfg=%u bank=%d map(s,g,f)=%d,%d,%d adc=%d I=%.5g ratio=%.5g pos=%.5g T1=%.5g lost=%u/%u\n",
            control_name(ctrl.state),ctrl.fault?ctrl.fault:"",active_cfg.id,active_cfg.bank,
            active_cfg.ch_supply,active_cfg.ch_ground,active_cfg.ch_feedback,i.adc_ok,
            control_current(&ctrl,&i),control_ratio(&ctrl,&i),control_position(&ctrl,&i),i.t1,
            (unsigned)lost_ticks,(unsigned)storage_lost_events()); return true;
    }
    if(!strcmp(cmd,"mark")) { storage_mark(esp_timer_get_time()); return true; }
    if(!strcmp(cmd,"zero")) return zero_locked();
    if(!strcmp(cmd,"save") && ctrl.state==SAFE && profile_valid(&ctrl.profile)) {
        if(!pause_adc()) return false;
        esp_err_t e=nvs_set_blob(nvs,"profile_m1",&ctrl.profile,sizeof ctrl.profile);
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
    /* bypass 1 = prad nieważny (np. LOGGER na sondach back-probe, P1 nie idzie przez bocznik); M1 nie ma zworki AUX. */
    if((ctrl.state==SAFE || ctrl.state==LOGGER) && !strcmp(cmd,"bypass")) {
        if(a!=0 && a!=1) return false;
        int bank=ctrl.test_bank?1:0;
        if(a==0 && !ctrl.profile.current_calibrated[bank]) return false;
        ctrl.profile.current_valid[bank]=a==0;
        return commit_locked(cmd);
    }
    if(!strcmp(cmd,"bank") && ctrl.state==SAFE && (a==0 || a==1)) {
        ctrl.test_bank=a!=0; ctrl.sensor_on=false; return commit_locked("bank");
    }
#if !CONFIG_EGR_ACTIVE_TEST
    if(strcmp(cmd,"logger") && strcmp(cmd,"identify") && strcmp(cmd,"stop")) return false;
#endif
    if(bench_mode && !strcmp(cmd,"test")) return false;   /* M-11: bez karty SD (np. tylko USB) bez TEST */
    if(!strcmp(cmd,"test") && !board_watchdogs_ok()) { outf("TEST odrzucony: watchdogi nieuruchomione (M1-03)\n"); return false; }
    if(!strcmp(cmd,"test")) {
        /* Bez detekcji adaptera (M-01, D-M1-7): przed SENS_5V linie silnika i czujnika musza byc bez napiecia. */
        inputs_t in=snapshot(); const char *why=control_test_wiring(&in);
        if(why) {
            outf("TEST odrzucony: %s (ECU podpiete? zaplon? przepiecie X1.5 / X1.7-X1.10 / X1.11-X1.13)\n",why);
            storage_event("{\"type\":\"test_rejected\",\"t_us\":%" PRIu64 ",\"reason\":\"%s\"}",in.now,why);
            return false;
        }
    }
    if(!control_command(&ctrl,cmd,a,b,esp_timer_get_time())) return false;
    if(!strcmp(cmd,"test") || !strcmp(cmd,"logger") || !strcmp(cmd,"stop") || !strcmp(cmd,"hotsoak_stop"))
        return commit_locked(cmd);
    return true;
}
/* 6.3.1-m1 (recenzja M1-09): odzyskanie AD7606B po bledzie odczytu w LOGGER / SAFE. Udana rekonfiguracja = commit z nowym
 * config_id (dopiero wtedy probki znow wazne); nieudana = akwizycja dalej z probkami INVALID, ponowna proba za 1 s.
 * W banku TEST control_step konczy sie FAULT ADC_CONFIG i zwykly commit. */
static void adc_recover_locked(void) {
    adc_recover_pending=false;
    if(ctrl.test_bank || ctrl.state==FAULT || board_adc_config_ok()) return;
    if(!pause_adc()) { fault_locked("PAUSE_TIMEOUT"); return; }
    uint8_t applied[8]; memset(applied,RANGE_UNKNOWN,sizeof applied);
    control_apply_ranges(&ctrl.profile,board_adc_software_mode());
    if(board_adc_ranges(ctrl.profile.range,applied)==ESP_OK && board_adc_config_ok()) { commit_locked("adc_recovery"); return; }
    storage_event("{\"type\":\"adc_recovery_failed\",\"t_us\":%" PRIu64 "}",(uint64_t)esp_timer_get_time());
    resume_adc(); transitioning=false;
    recover_after=esp_timer_get_time()+1000000; adc_recover_pending=true;
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
        if(adc_recover_pending && esp_timer_get_time()>=recover_after) {
            xSemaphoreTake(control_mutex,portMAX_DELAY); adc_recover_locked(); xSemaphoreGive(control_mutex);
        }
        request_t r;
        if(xQueueReceive(requests,&r,pdMS_TO_TICKS(20))!=pdTRUE) continue;
        if(r.epoch!=stop_epoch || stop_pending) continue;
        xSemaphoreTake(control_mutex,portMAX_DELAY);
        out_len=0; bool ok=execute_locked(r.line);
        xSemaphoreGive(control_mutex);
        if(out_len) { fwrite(out_buf,1,out_len,stdout); out_len=0; }   /* M1-08: wydruk po zwolnieniu blokady */
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
        "\"VBAT_V\":%s,\"TC1_C\":%s,\"TC2_C\":%s,\"naped\":%s,\"tryb\":\"%s\",\"config_id\":%u,"
        "\"pin_zasil_V\":%s,\"pin_masa_V\":%s,\"pin_sygnal_V\":%s}",
        control_name(ctrl.state),ctrl.fault?ctrl.fault:"",json_number(p,control_position(&ctrl,&i)),
        json_number(r,control_ratio(&ctrl,&i)),json_number(a,control_current(&ctrl,&i)),json_number(v,i.v[6]),
        json_number(t1,i.t1),json_number(t2,i.t2),run_permission?"true":"false",active_cfg.bank?"TEST":"LOGGER",active_cfg.id,
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
    (void)unused; char line[160]; puts("EGRLab 6.3.1-m1 (M1-R1): commands are queued; STOP is immediate.");
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
    /* M-13: klucz NVS i wersja profilu 7 - kalibracja z 6.1 / 6.2-s1 (inny sprzet) nie przechodzi na M1. */
    if(nvs_get_blob(nvs,"profile_m1",&saved,&bytes)==ESP_OK && bytes==sizeof saved && profile_valid(&saved)) ctrl.profile=saved;
    ctrl.profile.qualified=ctrl.profile.qualified && EGR_HARDWARE_ACCEPTED;
    ESP_ERROR_CHECK(board_init()); board_inhibit(true);
    /* M-11 (D-M1-6): z samego USB karta SD, AD7606B (VDRIVE) i MAX31856 sa bez zasilania 3,3 V. Brak karty nie zatrzymuje
     * firmware: tryb bez karty (bez plikow, bez TEST, licznik sesji nie rosnie); konsola i podglad dzialaja. */
    esp_err_t sd=board_sd_mount(); bench_mode=sd!=ESP_OK;
    uint32_t session=0; nvs_get_u32(nvs,"session",&session);
    if(!bench_mode) { session++; ESP_ERROR_CHECK(nvs_set_u32(nvs,"session",session)); ESP_ERROR_CHECK(nvs_commit(nvs)); }
    ESP_LOGI(TAG,"PSRAM=%u; hardware accepted=%d; AD7606B config=%s; SD=%s",(unsigned)esp_psram_get_size(),EGR_HARDWARE_ACCEPTED,
        board_adc_config_ok()?"OK":"BRAK",bench_mode?esp_err_to_name(sd):"OK");
    if(bench_mode)
        puts("TRYB BEZ KARTY: SD niezamontowana (tylko USB? peryferia 3,3 V bez zasilania z pakietu) - bez zapisu sesji i bez TEST.");
    if(!board_adc_config_ok())
        puts("AD7606B: brak odpowiedzi (tylko USB? brak 3,3 V / 5 V) - dane oznaczone jako niewazne, ponowna proba przy konfiguracji.");
#if CONFIG_EGR_CORE_ONLY
    puts("CORE (M1): init, PSRAM and SD mount complete; acquisition disabled.");
    printf("SENS_FAULT_N=%d BTN=%d\n",!board_sensor_fault(),!board_button());
    FILE *probe=bench_mode?NULL:fopen("/sd/core_probe.tmp","wb");
    if(probe) { fputs("EGRLab 6.3.1-m1 CORE SD probe\n",probe); fclose(probe); }
    return;
#endif
    if(!(bench_mode ? storage_init_bench(CONFIG_EGR_SAMPLE_HZ) : storage_init(session,CONFIG_EGR_SAMPLE_HZ))) {
        board_kill(); ESP_LOGE(TAG,"storage init"); return;
    }
    control_mutex=xSemaphoreCreateMutex(); pause_ack=xSemaphoreCreateBinary(); resume_sem=xSemaphoreCreateBinary(); first_sample=xSemaphoreCreateBinary();
    requests=xQueueCreate(16,sizeof(request_t)); summaries=xQueueCreate(8,sizeof(summary_t)); zero_summary=xQueueCreate(1,sizeof(summary_t));
    configASSERT(control_mutex && pause_ack && resume_sem && first_sample && requests && summaries && zero_summary);
    latest.t1=latest.t2=NAN; latest.sensor_fault=true;
    configASSERT(xTaskCreatePinnedToCore(acquisition,"adc",8192,NULL,23,&adc_task,1)==pdPASS);
    esp_timer_create_args_t ta={.callback=tick,.dispatch_method=ESP_TIMER_TASK,.name="sample"};
    ESP_ERROR_CHECK(esp_timer_create(&ta,&timer)); webui_init(status_json,web_command);
    configASSERT(xTaskCreatePinnedToCore(storage_writer,"writer",8192,NULL,8,NULL,0)==pdPASS);
    configASSERT(xTaskCreatePinnedToCore(auxiliary,"aux",8192,NULL,5,NULL,0)==pdPASS);
    configASSERT(xTaskCreatePinnedToCore(safety,"safety",8192,NULL,20,NULL,0)==pdPASS);
    configASSERT(xTaskCreatePinnedToCore(manager,"manager",12288,NULL,6,NULL,0)==pdPASS);
    configASSERT(xTaskCreatePinnedToCore(radio,"radio",6144,NULL,3,NULL,0)==pdPASS);
    configASSERT(xTaskCreatePinnedToCore(console,"console",4096,NULL,3,NULL,0)==pdPASS);
#if CONFIG_EGR_CAN_PRESENT
    configASSERT(xTaskCreatePinnedToCore(can_rx,"can",6144,NULL,7,NULL,0)==pdPASS);   /* ponizej writera (8): DAQ ma pierwszenstwo */
#endif
}
