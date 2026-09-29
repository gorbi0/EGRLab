#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <inttypes.h>
#include "sdkconfig.h"
#include "board.h"
#include "control.h"
#include "storage.h"
#include "trigger.h"
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

static control_t ctrl;
static inputs_t latest;
static portMUX_TYPE data_mux = portMUX_INITIALIZER_UNLOCKED;
static SemaphoreHandle_t control_mutex;
static TaskHandle_t acquisition_handle, config_handle;
static esp_timer_handle_t timer;

/* Migawka konfiguracji jest podwojnie buforowana: piszemy do nieaktywnej
 * kopii przy zatrzymanej akwizycji i dopiero potem przelaczamy indeks.
 * Zadanie akwizycji czyta indeks raz na probke i nie potrzebuje blokady. */
static session_config_t cfg_buffer[2];
static volatile int cfg_index;
static uint16_t cfg_next_id = 1;

/* Wejscia publikowane przez zadanie bezpieczenstwa, widoczne dla konsoli,
 * strony WWW i polityki radia. v2 trzymalo je w zmiennej lokalnej taska,
 * przez co SoftAP nigdy nie dostawal warunku startu. */
static volatile bool in_test_present, in_log_present, in_sensor_fault;
static volatile bool run_permission, sensor_flag;
static volatile bool acquisition_healthy = true;
static volatile uint32_t lost_ticks, trigger_count;
static bool tc_valid;
static uint64_t tc_time;
static summary_t last_summary;
static bool have_summary;
static nvs_handle_t nvs;
static const char *TAG = "EGRLab";

static inputs_t snapshot(void) {
    portENTER_CRITICAL(&data_mux);
    inputs_t i = latest;
    portEXIT_CRITICAL(&data_mux);
    i.now = esp_timer_get_time();
    i.interlock = board_interlock();
    i.hw_armed = board_armed();
    i.storage_ok = storage_ok() && acquisition_healthy;
    i.adc_ok = board_adc_config_ok();
    i.drive_ok = board_drive_ok();
    i.test_present = in_test_present;
    i.log_present = in_log_present;
    i.sensor_fault = in_sensor_fault;
    portENTER_CRITICAL(&data_mux);
    i.tc_ok = tc_valid && i.now - tc_time < 1000000;
    portEXIT_CRITICAL(&data_mux);
    return i;
}
static void tick(void *arg) { (void)arg; xTaskNotifyGive(acquisition_handle); }
static void config_request(void) { if (config_handle) xTaskNotifyGive(config_handle); }

static void acquisition(void *arg) {
    (void)arg;
    uint32_t seq = 0;
    while (true) {
        uint32_t ticks = ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
        const session_config_t *cfg = &cfg_buffer[cfg_index];
        sample_t s = {.sequence = seq++, .config_id = cfg->id};
        if (ticks > 1) {
            s.flags |= SAMPLE_GAP; lost_ticks += ticks - 1;
            acquisition_healthy = false; board_kill();
        }
        esp_err_t e = board_adc(s.raw, &s.t_us);
        if (e != ESP_OK) {
            acquisition_healthy = false; board_kill();
            storage_event("{\"type\":\"adc_error\",\"code\":%d}", e);
            continue;
        }
        if (cfg->bank) s.flags |= SAMPLE_TEST;
        if (run_permission) s.flags |= SAMPLE_PERMIT;
        if (sensor_flag) s.flags |= SAMPLE_SENSOR;
        float v[8];
        /* Przeliczenie idzie z migawki, a nie z zadanych zakresow profilu:
         * jesli sprzet nie potwierdzil zmiany, w migawce jest to, co
         * naprawde ustawiono. */
        for (int j = 0; j < 8; j++) {
            float fs = control_full_scale(cfg->range[j]);
            v[j] = s.raw[j] * (fs / 32768.0f) * cfg->gain[j] + cfg->offset[j];
        }
        uint32_t fired = trigger_sample(v, s.t_us);
        if (fired && cfg->ch_ground >= CH_SENSOR_FIRST && cfg->ch_supply >= CH_SENSOR_FIRST
                  && cfg->ch_feedback >= CH_SENSOR_FIRST) {
            s.flags |= SAMPLE_TRIGGER;
            trigger_count++;
            board_scope_trigger();
            float gnd = v[cfg->ch_ground];
            float current = cfg->current_valid ? (v[CH_CURRENT] - cfg->current_zero) / .25f : NAN;
            for (int bit = 0; bit < TRIG_COUNT; bit++) {
                if (!(fired & (1u << bit))) continue;
                storage_event("{\"type\":\"trigger\",\"t_us\":%" PRIu64 ",\"config_id\":%u,"
                    "\"name\":\"%s\",\"ground\":%.5f,\"ref\":%.5f,\"fb\":%.5f,\"i\":%.4f}",
                    s.t_us, (unsigned)cfg->id, trigger_name(bit), gnd,
                    v[cfg->ch_supply] - gnd, v[cfg->ch_feedback] - gnd, current);
            }
        }
        portENTER_CRITICAL(&data_mux);
        latest.sample_time = s.t_us;
        memcpy(latest.v, v, sizeof v);
        portEXIT_CRITICAL(&data_mux);
        storage_push(&s);
    }
}

/* Jedyne miejsce, w ktorym zmienia sie konfiguracja przetwornika i migawka.
 * Akwizycja jest na ten czas zatrzymana, wiec nie ma wyscigu ani probek
 * przeliczonych polowa starej, polowa nowej kalibracji. */
static void config_task(void *arg) {
    (void)arg;
    while (true) {
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
        if (xSemaphoreTake(control_mutex, pdMS_TO_TICKS(500)) != pdTRUE) continue;
        esp_timer_stop(timer);
        board_adc_set_running(false);
        vTaskDelay(pdMS_TO_TICKS(20));
        bool software = board_adc_software_mode();
        control_apply_ranges(&ctrl.profile, software);
        uint8_t applied[8];
        esp_err_t re = board_adc_ranges(ctrl.profile.range, applied);
        if (re != ESP_OK && re != ESP_ERR_NOT_SUPPORTED)
            storage_event("{\"type\":\"adc_config_error\",\"code\":%d}", re);
        int next = 1 - cfg_index;
        control_build_config(&ctrl, &cfg_buffer[next], cfg_next_id++, applied,
                             software, board_adc_config_ok());
        trigger_configure(&cfg_buffer[next], CONFIG_EGR_SAMPLE_HZ);
        cfg_index = next;
        storage_config(&cfg_buffer[next]);
        board_adc_set_running(true);
        esp_timer_start_periodic(timer, 1000000 / CONFIG_EGR_SAMPLE_HZ);
        xSemaphoreGive(control_mutex);
    }
}

static void log_campaign_point(const campaign_t *s, int index) {
    storage_event("{\"type\":\"hotsoak_point\",\"t_us\":%" PRIu64 ",\"index\":%d,"
        "\"tc1\":%.2f,\"tc2\":%.2f,\"vbat\":%.3f,"
        "\"i_break_open\":%.4f,\"i_break_close\":%.4f,"
        "\"ms_10_90\":%.1f,\"ms_90_10\":%.1f}",
        (uint64_t)esp_timer_get_time(), index, s->t1, s->t2, s->vbat,
        s->i_break_open, s->i_break_close, s->ms_open, s->ms_close);
}

/* Polityka radia: SoftAP tylko poza LOGGER/IDENTIFY, tylko przy wpietym
 * adapterze TEST i tylko gdy aktywny TEST jest w ogole skompilowany. */
static void webui_policy(const inputs_t *i) {
#if CONFIG_EGR_WIFI_UI
    bool allowed = i->test_present && !i->log_present
        && ctrl.state != LOGGER && ctrl.state != IDENTIFY && ctrl.state != FAULT;
    if (allowed && !webui_running()) webui_start();
    else if (!allowed && webui_running()) webui_stop();
#else
    (void)i;
#endif
}

static void safety(void *arg) {
    (void)arg;
    TickType_t wake = xTaskGetTickCount();
    uint64_t last_beat = 0, last_io = 0, last_policy = 0;
    bool sensor_fault = false, log_present = false, test_present = false, was_mark = false;
    state_t prior = SAFE;
    int8_t applied_map[3] = {-1, -1, -1};
    while (true) {
        inputs_t i = snapshot();
        if (i.now - last_io >= 20000) {
            if (board_inputs(&sensor_fault, &log_present, &test_present) != ESP_OK) sensor_fault = true;
            in_sensor_fault = sensor_fault; in_log_present = log_present; in_test_present = test_present;
            last_io = i.now;
            i.sensor_fault = sensor_fault; i.log_present = log_present; i.test_present = test_present;
        }
        if (xSemaphoreTake(control_mutex, pdMS_TO_TICKS(2)) == pdTRUE) {
            control_step(&ctrl, &i);
            bool moving = control_moving(&ctrl);
#if !CONFIG_EGR_ACTIVE_TEST
            moving = false;
#endif
            run_permission = moving;
            sensor_flag = ctrl.sensor_on;
            board_drive(ctrl.duty, moving);
            bool entered_fault = ctrl.state == FAULT && prior != FAULT;
            if (ctrl.state != prior) {
                storage_event("{\"type\":\"state\",\"t_us\":%" PRIu64 ",\"state\":\"%s\",\"fault\":\"%s\"}",
                    i.now, control_name(ctrl.state), ctrl.fault ? ctrl.fault : "");
                prior = ctrl.state;
            }
            /* IDENTIFY zmienia mapowanie w tym tasku; przeliczenie zakresow
             * i nowa migawka to juz robota zadania konfiguracyjnego. */
            if (ctrl.profile.ch_supply != applied_map[0] || ctrl.profile.ch_ground != applied_map[1]
                    || ctrl.profile.ch_feedback != applied_map[2]) {
                applied_map[0] = ctrl.profile.ch_supply;
                applied_map[1] = ctrl.profile.ch_ground;
                applied_map[2] = ctrl.profile.ch_feedback;
                config_request();
            }
            if (ctrl.soak.point_ready) {
                log_campaign_point(&ctrl.soak, ctrl.soak.done);
                ctrl.soak.point_ready = false;
            }
            bool beat = ctrl.state != FAULT && i.now - i.sample_time < 10000 && acquisition_healthy;
            if (i.now - last_beat >= 10000) { board_heartbeat(beat); last_beat = i.now; }
            if (entered_fault) { board_kill(); board_mode(ctrl.test_bank, false); }
            if (i.now - last_policy >= 200000) { webui_policy(&i); last_policy = i.now; }
            xSemaphoreGive(control_mutex);
        } else { board_kill(); run_permission = false; }
        bool mark = board_mark();
        if (mark && !was_mark) storage_mark(i.now);
        was_mark = mark;
        vTaskDelayUntil(&wake, pdMS_TO_TICKS(1));
    }
}

static void auxiliary(void *arg) {
    (void)arg;
    uint64_t last_tc = 0;
    while (true) {
        twai_message_t m;
        if (twai_receive(&m, pdMS_TO_TICKS(5)) == ESP_OK) {
            uint64_t now = esp_timer_get_time();
            char hex[17] = {0};
            unsigned len = m.data_length_code > 8 ? 8 : m.data_length_code;
            for (unsigned j = 0; j < len; j++) snprintf(hex + j * 2, 3, "%02x", m.data[j]);
            storage_event("{\"type\":\"can\",\"t_us\":%" PRIu64 ",\"id\":%" PRIu32
                ",\"ext\":%d,\"rtr\":%d,\"data\":\"%s\"}", now, m.identifier, m.extd, m.rtr, hex);
            if (!m.extd && !m.rtr && m.identifier >= 0x7e8 && m.identifier <= 0x7ef && len >= 5
                    && m.data[0] >= 4 && m.data[0] <= 7 && m.data[1] == 0x41 && m.data[2] == 0x0c) {
                float rpm = ((unsigned)m.data[3] * 256 + m.data[4]) / 4.0f;
                storage_event("{\"type\":\"rpm_obd\",\"t_us\":%" PRIu64 ",\"rpm\":%.2f}", now, rpm);
            }
        }
        summary_t sum;
        if (trigger_take_summary(&sum)) {
            portENTER_CRITICAL(&data_mux); last_summary = sum; have_summary = true; portEXIT_CRITICAL(&data_mux);
            /* Bufor mniejszy niz limit zdarzenia, zeby linia nie mogla zostac
             * przycieta do niepoprawnego JSON-a (v2 skladalo 420 B w limit 254). */
            char body[STORAGE_EVENT_MAX - 32];
            int n = snprintf(body, sizeof body,
                "{\"type\":\"summary\",\"t_us\":%" PRIu64 ",\"config_id\":%u,\"n\":%" PRIu32 ",\"ch\":[",
                sum.t_us, (unsigned)cfg_buffer[cfg_index].id, sum.count);
            bool fits = n > 0 && n < (int)sizeof body;
            for (int j = 0; j < 8 && fits; j++) {
                int w = snprintf(body + n, sizeof body - n, "%s[%.5g,%.5g,%.5g]",
                                 j ? "," : "", sum.min[j], sum.mean[j], sum.max[j]);
                fits = w > 0 && n + w < (int)sizeof body;
                n += w;
            }
            if (fits) {
                int w = snprintf(body + n, sizeof body - n, "],\"triggers\":%" PRIu32 "}", trigger_count);
                fits = w > 0 && n + w < (int)sizeof body;
            }
            if (fits) storage_event("%s", body);
            else storage_event("{\"type\":\"summary_dropped\",\"t_us\":%" PRIu64 "}", sum.t_us);
        }
        uint64_t now = esp_timer_get_time();
        if (now - last_tc >= 200000) {
            float t[2] = {NAN, NAN}; uint8_t fault[2] = {255, 255};
            for (int j = 0; j < 2; j++)
                if (board_temperature(j, &t[j], &fault[j]) != ESP_OK) { fault[j] = 255; t[j] = NAN; }
            portENTER_CRITICAL(&data_mux);
            latest.t1 = t[0]; latest.t2 = t[1]; tc_valid = !fault[0]; tc_time = now;
            portEXIT_CRITICAL(&data_mux);
            for (int j = 0; j < 2; j++) {
                char value[32];
                if (isfinite(t[j])) snprintf(value, sizeof value, "%.4f", t[j]); else strcpy(value, "null");
                storage_event("{\"type\":\"temperature\",\"t_us\":%" PRIu64
                    ",\"channel\":%d,\"celsius\":%s,\"fault\":%u}", now, j + 1, value, fault[j]);
            }
            last_tc = now;
            twai_status_info_t info;
            if (twai_get_status_info(&info) == ESP_OK && info.rx_missed_count)
                storage_event("{\"type\":\"can_drop\",\"count\":%" PRIu32 "}", info.rx_missed_count);
        }
    }
}

static bool valid_id(const char *s) {
    if (!*s) return false;
    for (; *s; s++)
        if (!((*s >= 'a' && *s <= 'z') || (*s >= 'A' && *s <= 'Z')
              || (*s >= '0' && *s <= '9') || *s == '_' || *s == '-')) return false;
    return true;
}

/* JEDNA sciezka polecen dla konsoli i strony WWW. v2 mialo dwie, przez co
 * webowy STOP nie odlaczal zasilania czujnika. */
static bool dispatch(const char *cmd, float a, int b, const char *source) {
    bool ok = false, reconfigure = false;
    if (!strcmp(cmd, "mark")) { storage_mark(esp_timer_get_time()); return true; }
    if (!strcmp(cmd, "stop")) board_kill();
    if (xSemaphoreTake(control_mutex, pdMS_TO_TICKS(100)) != pdTRUE) return false;
    inputs_t i = snapshot();
    if (!strcmp(cmd, "aux") && (ctrl.state == SAFE || ctrl.state == LOGGER)) {
        /* Pozycja zworki JP_AUX jest fizyczna; firmware musi ja znac, bo od
         * niej zalezy i zakres, i ktora pare wspolczynnikow stosowac. */
        ctrl.profile.aux_position = a >= .5f ? AUX_LO : AUX_HI;
        ok = true; reconfigure = true;
    } else if (!strcmp(cmd, "bypass") && (ctrl.state == SAFE || ctrl.state == LOGGER)) {
        /* Mostek bocznikujacy albo sondy back-probe: prad tego banku jest
         * niewazny i kryteria oparte na pradzie maja milczec. */
        ctrl.profile.current_valid[ctrl.test_bank ? 1 : 0] = a < .5f;
        ok = true; reconfigure = true;
    } else if (!strcmp(cmd, "zero") && (ctrl.state == SAFE || ctrl.state == READY)
               && !control_moving(&ctrl)) {
        summary_t s; bool got;
        portENTER_CRITICAL(&data_mux); s = last_summary; got = have_summary; portEXIT_CRITICAL(&data_mux);
        if (got && isfinite(s.mean[CH_CURRENT])) {
            ctrl.profile.current_zero[ctrl.test_bank ? 1 : 0] = s.mean[CH_CURRENT];
            ok = true; reconfigure = true;
        }
    } else {
#if !CONFIG_EGR_ACTIVE_TEST
        bool passive = !strcmp(cmd, "logger") || !strcmp(cmd, "identify") || !strcmp(cmd, "stop");
        if (!passive) { xSemaphoreGive(control_mutex); return false; }
#endif
        ok = control_command(&ctrl, cmd, a, b, i.now);
        if (ok && (!strcmp(cmd, "test") || !strcmp(cmd, "logger") || !strcmp(cmd, "stop"))) {
            board_kill();
            if (board_mode(ctrl.test_bank, ctrl.sensor_on) != ESP_OK) {
                control_stop(&ctrl); board_mode(false, false); ok = false;
            }
            reconfigure = true;
        }
    }
    if (ok) storage_event("{\"type\":\"command\",\"t_us\":%" PRIu64
        ",\"source\":\"%s\",\"command\":\"%s\",\"a\":%.7g,\"b\":%d}", i.now, source, cmd, a, b);
    xSemaphoreGive(control_mutex);
    if (ok && reconfigure) config_request();
    return ok;
}

static void status_json(char *out, size_t len) {
    inputs_t i = snapshot();
    const session_config_t *cfg = &cfg_buffer[cfg_index];
    snprintf(out, len,
        "{\"stan\":\"%s\",\"fault\":\"%s\",\"pozycja\":\"%.3f\",\"ratio\":\"%.4f\","
        "\"prad_A\":\"%.3f\",\"pin_zasil_V\":\"%.3f\",\"pin_masa_V\":\"%.4f\","
        "\"pin_sygnal_V\":\"%.3f\",\"VBAT_V\":\"%.2f\",\"AUX_V\":\"%.4f\","
        "\"TC1_C\":\"%.1f\",\"TC2_C\":\"%.1f\",\"uzbrojony\":\"%s\",\"adapter\":\"%s\","
        "\"config_id\":\"%u\"}",
        control_name(ctrl.state), ctrl.fault ? ctrl.fault : "",
        control_position(&ctrl, &i), control_ratio(&ctrl, &i), control_current(&ctrl, &i),
        cfg->ch_supply >= 0 ? i.v[cfg->ch_supply] : NAN,
        cfg->ch_ground >= 0 ? i.v[cfg->ch_ground] : NAN,
        cfg->ch_feedback >= 0 ? i.v[cfg->ch_feedback] : NAN,
        i.v[CH_VBAT], i.v[CH_AUX], i.t1, i.t2, i.hw_armed ? "tak" : "NIE",
        i.test_present ? "TEST" : i.log_present ? "LOGGER" : "brak", (unsigned)cfg->id);
}
static bool web_command(const char *cmd, float a, int b) { return dispatch(cmd, a, b, "web"); }

static void console(void *arg) {
    (void)arg;
    char line[160], cmd[32];
    puts("EGRLab v3: status logger identify bind aux bypass test learn zero manual goto");
    puts("           sweep friction cycle thermal hotsoak hotsoak_stop mark stop save");
    while (true) {
        if (!fgets(line, sizeof line, stdin)) { vTaskDelay(pdMS_TO_TICKS(20)); continue; }
        float a = 0, bf = 0; int b = 0; cmd[0] = 0;
        int fields = sscanf(line, "%31s %f %f", cmd, &a, &bf);
        if (fields < 1) continue;
        if ((fields >= 2 && (!isfinite(a) || fabsf(a) > 10000))
            || (fields >= 3 && (!isfinite(bf) || fabsf(bf) > 10000))) { puts("INVALID NUMBER"); continue; }
        b = (int)bf;
        if (!strcmp(cmd, "cycle") || !strcmp(cmd, "friction")) b = (int)a;
        if (!strcmp(cmd, "hotsoak") && fields < 3) b = 12;
        bool ok = false, handled = false;
        if (!strcmp(cmd, "status")) {
            inputs_t i = snapshot();
            const session_config_t *cfg = &cfg_buffer[cfg_index];
            printf("%s%s%s cfg=%u map(s,g,f)=%d,%d,%d bank=%d Vs=%.4f Vg=%.5f Vf=%.4f\n",
                control_name(ctrl.state), ctrl.fault ? " fault=" : "", ctrl.fault ? ctrl.fault : "",
                (unsigned)cfg->id, cfg->ch_supply, cfg->ch_ground, cfg->ch_feedback, cfg->bank,
                cfg->ch_supply >= 0 ? i.v[cfg->ch_supply] : NAN,
                cfg->ch_ground >= 0 ? i.v[cfg->ch_ground] : NAN,
                cfg->ch_feedback >= 0 ? i.v[cfg->ch_feedback] : NAN);
            printf("  I=%.3f (wazny=%d) ratio=%.4f pos=%.4f VBAT=%.2f AUX=%.4f(%s) TC1=%.1f TC2=%.1f\n",
                control_current(&ctrl, &i), (int)cfg->current_valid,
                control_ratio(&ctrl, &i), control_position(&ctrl, &i),
                i.v[CH_VBAT], i.v[CH_AUX], cfg->aux_position ? "LO" : "HI", i.t1, i.t2);
            printf("  adapter=%s arm=%d adc=%s/%s lost_ticks=%" PRIu32 " lost_events=%" PRIu32
                   " trig=%" PRIu32 " qualified=%d learned=%d soak=%d/%d\n",
                i.test_present ? "TEST" : i.log_present ? "LOGGER" : "brak", (int)i.hw_armed,
                board_adc_software_mode() ? "software" : "hardware",
                board_adc_config_ok() ? "ok" : "BLAD", lost_ticks, storage_lost_events(),
                trigger_count, (int)ctrl.profile.qualified, (int)ctrl.profile.learned,
                ctrl.soak.done, ctrl.soak.done + ctrl.soak.left);
            ok = true; handled = true;
        } else if (!strcmp(cmd, "bind")) {
            char v[24] = {0}, h[24] = {0};
            if (xSemaphoreTake(control_mutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                if (ctrl.state == SAFE && sscanf(line, "%*s %23s %23s", v, h) == 2
                        && valid_id(v) && valid_id(h)) {
                    /* Inny fizyczny zawor uniewaznia mapowanie pinow i LEARN. */
                    if (strcmp(v, ctrl.profile.valve) || strcmp(h, ctrl.profile.adapter)) {
                        ctrl.profile.ch_supply = -1;
                        ctrl.profile.ch_ground = -1;
                        ctrl.profile.ch_feedback = -1;
                        ctrl.profile.learned = false;
                    }
                    strcpy(ctrl.profile.valve, v); strcpy(ctrl.profile.adapter, h); ok = true;
                }
                xSemaphoreGive(control_mutex);
            }
            if (ok) config_request();
            handled = true;
        } else if (!strcmp(cmd, "learn")) {
            float rc, ro; int sign;
            if (xSemaphoreTake(control_mutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                if (ctrl.state == READY
                        && sscanf(line, "%*s %f %f %d", &rc, &ro, &sign) == 3
                        && isfinite(rc) && isfinite(ro)
                        && rc > .02f && rc < .98f && ro > .02f && ro < .98f
                        && fabsf(ro - rc) > .2f && (sign == 1 || sign == -1)) {
                    ctrl.profile.closed = rc; ctrl.profile.open = ro;
                    ctrl.profile.opening_sign = sign; ctrl.profile.learned = true; ok = true;
                }
                xSemaphoreGive(control_mutex);
            }
            if (ok) config_request();
            handled = true;
        } else if (!strcmp(cmd, "save")) {
            if (xSemaphoreTake(control_mutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                if (ctrl.state == SAFE && valid_id(ctrl.profile.valve)
                        && valid_id(ctrl.profile.adapter)) {
                    esp_timer_stop(timer); board_adc_set_running(false);
                    vTaskDelay(pdMS_TO_TICKS(20));
                    esp_err_t e = nvs_set_blob(nvs, "profile", &ctrl.profile, sizeof ctrl.profile);
                    if (e == ESP_OK) e = nvs_commit(nvs);
                    ok = e == ESP_OK;
                    board_adc_set_running(true);
                    esp_timer_start_periodic(timer, 1000000 / CONFIG_EGR_SAMPLE_HZ);
                }
                xSemaphoreGive(control_mutex);
            }
            handled = true;
        }
        if (!handled) ok = dispatch(cmd, a, b, "console");
        puts(ok ? "OK" : "REJECTED (stan/profil/limity)");
    }
}

void app_main(void) {
    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(nvs_open("egrlab", NVS_READWRITE, &nvs));
    control_init(&ctrl);
    size_t bytes = sizeof(profile_t); profile_t saved;
    if (nvs_get_blob(nvs, "profile", &saved, &bytes) == ESP_OK && bytes == sizeof saved
            && saved.magic == EGR_PROFILE_MAGIC && saved.version == EGR_PROFILE_VERSION) {
        ctrl.profile = saved;
    }
    /* qualified ustawia wylacznie odbior sprzetu, nigdy zapisany profil. */
    ctrl.profile.qualified = EGR_HARDWARE_ACCEPTED;
    uint32_t session = 0;
    nvs_get_u32(nvs, "session", &session); session++;
    ESP_ERROR_CHECK(nvs_set_u32(nvs, "session", session));
    ESP_ERROR_CHECK(nvs_commit(nvs));
    ESP_LOGI(TAG, "PSRAM=%u B; TEST domyslnie zablokowany", (unsigned)esp_psram_get_size());
    ESP_ERROR_CHECK(board_init());
    ESP_LOGI(TAG, "ADC: %s, konfiguracja %s",
             board_adc_software_mode() ? "software mode" : "hardware mode",
             board_adc_config_ok() ? "potwierdzona" : "NIEPOTWIERDZONA - TEST zablokowany");
    ESP_ERROR_CHECK(board_sd_mount());
    if (!storage_init(session, CONFIG_EGR_SAMPLE_HZ)) {
        board_kill(); ESP_LOGE(TAG, "Inicjalizacja zapisu nieudana"); return;
    }
    control_mutex = xSemaphoreCreateMutex(); configASSERT(control_mutex);
    latest.t1 = NAN; latest.t2 = NAN;
    ESP_ERROR_CHECK(board_mode(false, false));
    /* Migawka startowa: zakresy ustawione i potwierdzone przed pierwsza probka. */
    bool software = board_adc_software_mode();
    control_apply_ranges(&ctrl.profile, software);
    uint8_t applied[8];
    board_adc_ranges(ctrl.profile.range, applied);
    control_build_config(&ctrl, &cfg_buffer[0], cfg_next_id++, applied, software,
                         board_adc_config_ok());
    cfg_index = 0;
    trigger_configure(&cfg_buffer[0], CONFIG_EGR_SAMPLE_HZ);
    storage_config(&cfg_buffer[0]);
    webui_init(status_json, web_command);
    configASSERT(xTaskCreatePinnedToCore(acquisition, "adc", 4096, NULL, 23, &acquisition_handle, 1) == pdPASS);
    configASSERT(xTaskCreatePinnedToCore(storage_writer, "writer", 8192, NULL, 8, NULL, 0) == pdPASS);
    configASSERT(xTaskCreatePinnedToCore(safety, "safety", 4096, NULL, 20, NULL, 0) == pdPASS);
    configASSERT(xTaskCreatePinnedToCore(config_task, "config", 4096, NULL, 6, &config_handle, 0) == pdPASS);
    configASSERT(xTaskCreatePinnedToCore(auxiliary, "aux", 4096, NULL, 5, NULL, 0) == pdPASS);
    esp_timer_create_args_t ta = {.callback = tick, .dispatch_method = ESP_TIMER_TASK, .name = "sample"};
    ESP_ERROR_CHECK(esp_timer_create(&ta, &timer));
    board_adc_set_running(true);
    ESP_ERROR_CHECK(esp_timer_start_periodic(timer, 1000000 / CONFIG_EGR_SAMPLE_HZ));
    configASSERT(xTaskCreatePinnedToCore(console, "console", 6144, NULL, 3, NULL, 0) == pdPASS);
}
