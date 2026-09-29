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
static TaskHandle_t acquisition_handle;
static esp_timer_handle_t timer;
static volatile bool test_bank, run_permission, sensor_flag;
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
    portENTER_CRITICAL(&data_mux);
    i.tc_ok = tc_valid && i.now - tc_time < 1000000;
    portEXIT_CRITICAL(&data_mux);
    return i;
}
static void tick(void *arg) { (void)arg; xTaskNotifyGive(acquisition_handle); }

static void acquisition(void *arg) {
    (void)arg;
    uint32_t seq = 0;
    while (true) {
        uint32_t ticks = ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
        sample_t s = {.sequence = seq++};
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
        int bank = test_bank ? 1 : 0;
        if (test_bank) s.flags |= SAMPLE_TEST;
        if (run_permission) s.flags |= SAMPLE_PERMIT;
        if (sensor_flag) s.flags |= SAMPLE_SENSOR;
        float v[8];
        /* Kalibracja jest stała w obrębie sesji; NVS nie jest zapisywany
         * podczas akwizycji, a zmiana banku wymaga przejścia przez SAFE. */
        for (int j = 0; j < 8; j++) {
            float fs = control_full_scale(ctrl.profile.range[j]);
            v[j] = s.raw[j] * (fs / 32768.0f) * ctrl.profile.gain[bank][j]
                 + ctrl.profile.offset[bank][j];
        }
        uint32_t fired = trigger_sample(v, s.t_us);
        /* Triggery odpalają tylko przy znanym mapowaniu, ale indeksy kanałów
         * przychodzą z profilu — sprawdzamy je, zamiast na to liczyć. */
        if (fired && ctrl.profile.ch_ground >= CH_SENSOR_FIRST
                  && ctrl.profile.ch_supply >= CH_SENSOR_FIRST
                  && ctrl.profile.ch_feedback >= CH_SENSOR_FIRST) {
            s.flags |= SAMPLE_TRIGGER;
            trigger_count++;
            board_scope_trigger();
            for (int bit = 0; bit < TRIG_COUNT; bit++) {
                if (!(fired & (1u << bit))) continue;
                storage_event("{\"type\":\"trigger\",\"t_us\":%" PRIu64 ",\"name\":\"%s\","
                    "\"ground\":%.5f,\"ref\":%.5f,\"fb\":%.5f,\"i\":%.4f}",
                    s.t_us, trigger_name(bit),
                    v[ctrl.profile.ch_ground], v[ctrl.profile.ch_supply] - v[ctrl.profile.ch_ground],
                    v[ctrl.profile.ch_feedback] - v[ctrl.profile.ch_ground],
                    (v[CH_CURRENT] - ctrl.profile.current_zero[bank]) / .25f);
            }
        }
        portENTER_CRITICAL(&data_mux);
        latest.sample_time = s.t_us;
        memcpy(latest.v, v, sizeof v);
        portEXIT_CRITICAL(&data_mux);
        storage_push(&s);
    }
}
static void log_campaign_point(const campaign_t *s, int index) {
    storage_event("{\"type\":\"hotsoak_point\",\"t_us\":%" PRIu64 ",\"index\":%d,"
        "\"tc1\":%.2f,\"tc2\":%.2f,\"vbat\":%.3f,"
        "\"i_break_open\":%.4f,\"i_break_close\":%.4f,"
        "\"ms_10_90\":%.1f,\"ms_90_10\":%.1f}",
        esp_timer_get_time(), index, s->t1, s->t2, s->vbat,
        s->i_break_open, s->i_break_close, s->ms_open, s->ms_close);
}
static void safety(void *arg) {
    (void)arg;
    TickType_t wake = xTaskGetTickCount();
    uint64_t last_beat = 0, last_io = 0;
    bool sensor_fault = false, log_present = false, test_present = false, was_mark = false;
    state_t prior = SAFE;
    int8_t applied[3] = {-1, -1, -1};
    while (true) {
        inputs_t i = snapshot();
        if (i.now - last_io >= 20000) {
            if (board_inputs(&sensor_fault, &log_present, &test_present) != ESP_OK) sensor_fault = true;
            last_io = i.now;
        }
        i.sensor_fault = sensor_fault; i.log_present = log_present; i.test_present = test_present;
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
            /* Nowe mapowanie pinów zmienia zakresy ADC i konfigurację triggerów. */
            if (ctrl.profile.ch_supply != applied[0] || ctrl.profile.ch_ground != applied[1]
                    || ctrl.profile.ch_feedback != applied[2]) {
                applied[0] = ctrl.profile.ch_supply; applied[1] = ctrl.profile.ch_ground;
                applied[2] = ctrl.profile.ch_feedback;
                control_apply_ranges(&ctrl.profile);
                esp_err_t re = board_adc_ranges(ctrl.profile.range);
                trigger_configure(&ctrl.profile, ctrl.test_bank ? 1 : 0, CONFIG_EGR_SAMPLE_HZ);
                storage_event("{\"type\":\"profile\",\"t_us\":%" PRIu64 ",\"ch_supply\":%d,"
                    "\"ch_ground\":%d,\"ch_feedback\":%d,\"closed\":%.7g,\"open\":%.7g,"
                    "\"sign\":%d,\"ranges_applied\":%d,\"software_mode\":%s}",
                    i.now, applied[0], applied[1], applied[2], ctrl.profile.closed,
                    ctrl.profile.open, (int)ctrl.profile.opening_sign, re,
                    board_adc_software_mode() ? "true" : "false");
            }
            if (ctrl.soak.point_ready) {
                log_campaign_point(&ctrl.soak, ctrl.soak.done);
                ctrl.soak.point_ready = false;
            }
            bool beat = ctrl.state != FAULT && i.now - i.sample_time < 10000 && acquisition_healthy;
            if (i.now - last_beat >= 10000) { board_heartbeat(beat); last_beat = i.now; }
            if (entered_fault) { board_kill(); board_mode(ctrl.test_bank, false); }
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
            char body[420]; int n = 0;
            n += snprintf(body + n, sizeof body - n,
                "{\"type\":\"summary\",\"t_us\":%" PRIu64 ",\"n\":%" PRIu32 ",\"ch\":[", sum.t_us, sum.count);
            for (int j = 0; j < 8 && n < (int)sizeof body - 48; j++)
                n += snprintf(body + n, sizeof body - n, "%s[%.5g,%.5g,%.5g]",
                    j ? "," : "", sum.min[j], sum.mean[j], sum.max[j]);
            snprintf(body + n, sizeof body - n, "],\"triggers\":%" PRIu32 "}", trigger_count);
            storage_event("%s", body);
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
/* Radio wolno podnieść tylko poza LOGGER i tylko przy adapterze TEST. */
static void webui_policy(const inputs_t *i) {
#if CONFIG_EGR_WIFI_UI
    bool allowed = CONFIG_EGR_ACTIVE_TEST && i->test_present && !i->log_present
        && ctrl.state != LOGGER && ctrl.state != IDENTIFY;
    if (allowed && !webui_running()) webui_start();
    else if (!allowed && webui_running()) webui_stop();
#else
    (void)i;
#endif
}
static void status_json(char *out, size_t len) {
    inputs_t i = snapshot();
    snprintf(out, len,
        "{\"stan\":\"%s\",\"fault\":\"%s\",\"pozycja\":\"%.3f\",\"ratio\":\"%.4f\","
        "\"prad_A\":\"%.3f\",\"pin_zasil_V\":\"%.3f\",\"pin_masa_V\":\"%.4f\","
        "\"pin_sygnal_V\":\"%.3f\",\"VBAT_V\":\"%.2f\",\"TC1_C\":\"%.1f\",\"TC2_C\":\"%.1f\","
        "\"uzbrojony\":\"%s\",\"adapter\":\"%s\"}",
        control_name(ctrl.state), ctrl.fault ? ctrl.fault : "",
        control_position(&ctrl, &i), control_ratio(&ctrl, &i), control_current(&ctrl, &i),
        ctrl.profile.ch_supply >= 0 ? i.v[ctrl.profile.ch_supply] : NAN,
        ctrl.profile.ch_ground >= 0 ? i.v[ctrl.profile.ch_ground] : NAN,
        ctrl.profile.ch_feedback >= 0 ? i.v[ctrl.profile.ch_feedback] : NAN,
        i.v[CH_VBAT], i.t1, i.t2, i.hw_armed ? "tak" : "NIE",
        i.test_present ? "TEST" : i.log_present ? "LOGGER" : "brak");
}
static bool web_command(const char *cmd, float a, int b) {
    if (!strcmp(cmd, "stop")) { board_kill(); }
    if (!strcmp(cmd, "mark")) { storage_mark(esp_timer_get_time()); return true; }
    if (xSemaphoreTake(control_mutex, pdMS_TO_TICKS(50)) != pdTRUE) return false;
    bool ok = control_command(&ctrl, cmd, a, b, esp_timer_get_time());
    if (ok) storage_event("{\"type\":\"command\",\"t_us\":%" PRIu64
        ",\"source\":\"web\",\"command\":\"%s\",\"a\":%.7g,\"b\":%d}",
        esp_timer_get_time(), cmd, a, b);
    xSemaphoreGive(control_mutex);
    return ok;
}
static void console(void *arg) {
    (void)arg;
    char line[160], cmd[32];
    puts("EGRLab v2: status logger identify bind aux test learn zero manual goto sweep"
         " friction cycle thermal hotsoak mark stop save");
    while (true) {
        if (!fgets(line, sizeof line, stdin)) { vTaskDelay(pdMS_TO_TICKS(20)); continue; }
        float a = 0, bf = 0; int b = 0; cmd[0] = 0;
        int fields = sscanf(line, "%31s %f %f", cmd, &a, &bf);
        if ((fields >= 2 && (!isfinite(a) || fabsf(a) > 10000))
            || (fields >= 3 && (!isfinite(bf) || fabsf(bf) > 10000))) { puts("INVALID NUMBER"); continue; }
        b = (int)bf;
        if (!strcmp(cmd, "stop")) board_kill();
        if (!strcmp(cmd, "mark")) { storage_mark(esp_timer_get_time()); continue; }
        if (xSemaphoreTake(control_mutex, pdMS_TO_TICKS(50)) != pdTRUE) { puts("BUSY"); continue; }
        inputs_t i = snapshot();
        bool ok = false;
        if (!strcmp(cmd, "status")) {
            printf("%s%s%s map(s,g,f)=%d,%d,%d Vs=%.4f Vg=%.5f Vf=%.4f I=%.3f ratio=%.4f pos=%.4f\n"
                   "  VBAT=%.2f AUX=%.4f TC1=%.1f TC2=%.1f adapter=%s arm=%d lost=%" PRIu32
                   " trig=%" PRIu32 " sw_adc=%d qualified=%d learned=%d soak=%d/%d\n",
                control_name(ctrl.state), ctrl.fault ? " fault=" : "", ctrl.fault ? ctrl.fault : "",
                ctrl.profile.ch_supply, ctrl.profile.ch_ground, ctrl.profile.ch_feedback,
                ctrl.profile.ch_supply >= 0 ? i.v[ctrl.profile.ch_supply] : NAN,
                ctrl.profile.ch_ground >= 0 ? i.v[ctrl.profile.ch_ground] : NAN,
                ctrl.profile.ch_feedback >= 0 ? i.v[ctrl.profile.ch_feedback] : NAN,
                control_current(&ctrl, &i), control_ratio(&ctrl, &i), control_position(&ctrl, &i),
                i.v[CH_VBAT], i.v[CH_AUX], i.t1, i.t2,
                i.test_present ? "TEST" : i.log_present ? "LOGGER" : "brak",
                (int)i.hw_armed, lost_ticks, trigger_count, (int)board_adc_software_mode(),
                (int)ctrl.profile.qualified, (int)ctrl.profile.learned,
                ctrl.soak.done, ctrl.soak.done + ctrl.soak.left);
            ok = true;
        } else if (!strcmp(cmd, "bind") && ctrl.state == SAFE) {
            char v[24] = {0}, h[24] = {0};
            if (sscanf(line, "%*s %23s %23s", v, h) == 2 && valid_id(v) && valid_id(h)) {
                /* Inny fizyczny zawór unieważnia mapowanie pinów i LEARN. */
                if (strcmp(v, ctrl.profile.valve) || strcmp(h, ctrl.profile.adapter)) {
                    ctrl.profile.ch_supply = ctrl.profile.ch_ground = ctrl.profile.ch_feedback = -1;
                    ctrl.profile.learned = false;
                }
                strcpy(ctrl.profile.valve, v); strcpy(ctrl.profile.adapter, h); ok = true;
            }
        } else if (!strcmp(cmd, "learn") && ctrl.state == READY) {
            float rc, ro; int sign;
            if (sscanf(line, "%*s %f %f %d", &rc, &ro, &sign) == 3 && isfinite(rc) && isfinite(ro)
                    && rc > .02f && rc < .98f && ro > .02f && ro < .98f
                    && fabsf(ro - rc) > .2f && (sign == 1 || sign == -1)) {
                ctrl.profile.closed = rc; ctrl.profile.open = ro;
                ctrl.profile.opening_sign = sign; ctrl.profile.learned = true; ok = true;
            }
        } else if (!strcmp(cmd, "zero") && (ctrl.state == SAFE || ctrl.state == READY)
                   && !control_moving(&ctrl)) {
            /* Zero toru prądowego z ostatniego podsumowania 1 Hz — mierzone,
             * nie zakładane 2,5 V. Rób to po rozgrzaniu i przy pewnym I = 0. */
            summary_t s; bool got;
            portENTER_CRITICAL(&data_mux); s = last_summary; got = have_summary; portEXIT_CRITICAL(&data_mux);
            if (got && isfinite(s.mean[CH_CURRENT])) {
                ctrl.profile.current_zero[ctrl.test_bank ? 1 : 0] = s.mean[CH_CURRENT];
                trigger_configure(&ctrl.profile, ctrl.test_bank ? 1 : 0, CONFIG_EGR_SAMPLE_HZ);
                printf("zero[%d] = %.5f V\n", ctrl.test_bank ? 1 : 0, s.mean[CH_CURRENT]);
                ok = true;
            }
        } else if (!strcmp(cmd, "aux") && (ctrl.state == SAFE || ctrl.state == LOGGER)) {
            /* Pozycja zworki JP_AUX jest fizyczna; firmware musi ją znać, bo od
             * niej zależy zakres ADC i nominalne wzmocnienie tego kanału. */
            bool lo = a >= .5f;
            ctrl.profile.range[CH_AUX] = lo ? RANGE_2V5 : RANGE_10V;
            for (int bank = 0; bank < 2; bank++) ctrl.profile.gain[bank][CH_AUX] = lo ? 1.01996f : 4.06f;
            ok = board_adc_ranges(ctrl.profile.range) != ESP_ERR_INVALID_RESPONSE;
            printf("AUX = %s (%s); wzmocnienie nominalne, skalibruj osobno dla tej pozycji
",
                   lo ? "LO +-2.5V" : "HI +-40V", board_adc_software_mode() ? "software mode" : "hardware mode: zakres bez zmian");
        } else if (!strcmp(cmd, "save") && ctrl.state == SAFE
                   && valid_id(ctrl.profile.valve) && valid_id(ctrl.profile.adapter)) {
            esp_timer_stop(timer); vTaskDelay(pdMS_TO_TICKS(20));
            esp_err_t e = nvs_set_blob(nvs, "profile", &ctrl.profile, sizeof ctrl.profile);
            if (e == ESP_OK) e = nvs_commit(nvs);
            ok = e == ESP_OK;
            esp_timer_start_periodic(timer, 1000000 / CONFIG_EGR_SAMPLE_HZ);
        } else {
#if !CONFIG_EGR_ACTIVE_TEST
            bool passive = !strcmp(cmd, "logger") || !strcmp(cmd, "identify") || !strcmp(cmd, "stop");
            if (!passive) { puts("ACTIVE_TEST wylaczone w menuconfig"); xSemaphoreGive(control_mutex); continue; }
#endif
            if (!strcmp(cmd, "cycle") || !strcmp(cmd, "friction")) b = (int)a;
            if (!strcmp(cmd, "hotsoak") && fields < 3) b = 12;
            ok = control_command(&ctrl, cmd, a, b, i.now);
            if (ok && (!strcmp(cmd, "test") || !strcmp(cmd, "logger") || !strcmp(cmd, "stop"))) {
                board_kill(); test_bank = ctrl.test_bank;
                trigger_configure(&ctrl.profile, ctrl.test_bank ? 1 : 0, CONFIG_EGR_SAMPLE_HZ);
                if (board_mode(ctrl.test_bank, ctrl.sensor_on) != ESP_OK) {
                    control_stop(&ctrl); ok = false;
                }
            }
        }
        if (ok) storage_event("{\"type\":\"command\",\"t_us\":%" PRIu64
            ",\"source\":\"console\",\"command\":\"%s\",\"a\":%.7g,\"b\":%d}", i.now, cmd, a, b);
        webui_policy(&i);
        xSemaphoreGive(control_mutex);
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
    /* qualified ustawia wyłącznie odbiór sprzętu, nigdy zapisany profil. */
    ctrl.profile.qualified = EGR_HARDWARE_ACCEPTED;
    control_apply_ranges(&ctrl.profile);
    uint32_t session = 0;
    nvs_get_u32(nvs, "session", &session); session++;
    ESP_ERROR_CHECK(nvs_set_u32(nvs, "session", session));
    ESP_ERROR_CHECK(nvs_commit(nvs));
    ESP_LOGI(TAG, "PSRAM=%u B; TEST domyslnie zablokowany", (unsigned)esp_psram_get_size());
    ESP_ERROR_CHECK(board_init());
    ESP_LOGI(TAG, "ADC: %s", board_adc_software_mode() ? "software mode" : "hardware mode (fallback)");
    board_adc_ranges(ctrl.profile.range);
    ESP_ERROR_CHECK(board_sd_mount());
    if (!storage_init(session, &ctrl.profile, CONFIG_EGR_SAMPLE_HZ, 0)) {
        board_kill(); ESP_LOGE(TAG, "Inicjalizacja zapisu nieudana"); return;
    }
    trigger_configure(&ctrl.profile, 0, CONFIG_EGR_SAMPLE_HZ);
    webui_init(status_json, web_command);
    control_mutex = xSemaphoreCreateMutex(); configASSERT(control_mutex);
    latest.t1 = NAN; latest.t2 = NAN;
    ESP_ERROR_CHECK(board_mode(false, false));
    configASSERT(xTaskCreatePinnedToCore(acquisition, "adc", 4096, NULL, 23, &acquisition_handle, 1) == pdPASS);
    configASSERT(xTaskCreatePinnedToCore(storage_writer, "writer", 8192, NULL, 8, NULL, 0) == pdPASS);
    configASSERT(xTaskCreatePinnedToCore(safety, "safety", 4096, NULL, 20, NULL, 0) == pdPASS);
    configASSERT(xTaskCreatePinnedToCore(auxiliary, "aux", 4096, NULL, 5, NULL, 0) == pdPASS);
    esp_timer_create_args_t ta = {.callback = tick, .dispatch_method = ESP_TIMER_TASK, .name = "sample"};
    ESP_ERROR_CHECK(esp_timer_create(&ta, &timer));
    ESP_ERROR_CHECK(esp_timer_start_periodic(timer, 1000000 / CONFIG_EGR_SAMPLE_HZ));
    configASSERT(xTaskCreatePinnedToCore(console, "console", 6144, NULL, 3, NULL, 0) == pdPASS);
}
