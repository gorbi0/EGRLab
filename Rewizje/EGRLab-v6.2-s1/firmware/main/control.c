#include "control.h"
#include <math.h>
#include <string.h>

static float clamp(float x, float lo, float hi) { return fmaxf(lo, fminf(x, hi)); }

float control_full_scale(uint8_t range) {
    return range == RANGE_2V5 ? 2.5f : range == RANGE_5V ? 5.0f : range == RANGE_10V ? 10.0f : NAN;
}
const char *control_name(state_t s) {
    static const char *names[] = {"SAFE","LOGGER","IDENTIFY","SENSOR_CHECK","READY",
        "MANUAL","GOTO","SWEEP","FRICTION","CYCLE","THERMAL","FAULT"};
    return (unsigned)s < sizeof(names)/sizeof(names[0]) ? names[s] : "INVALID";
}
bool control_moving(const control_t *c) { return c->state >= MANUAL && c->state <= THERMAL; }

static void fail(control_t *c, const char *reason) {
    c->state = FAULT; c->duty = 0; c->sensor_on = false; c->fault = reason;
    c->soak.active = false;
}
void control_init(control_t *c) {
    memset(c, 0, sizeof(*c));
    c->profile.magic = EGR_PROFILE_MAGIC;
    c->profile.version = EGR_PROFILE_VERSION;
    c->profile.max_duty = .35f; c->profile.current_limit = 1.5f;
    c->profile.temp_limit = 60; c->profile.opening_sign = 1;
    strcpy(c->profile.daq_module,"UNBOUND");
    c->profile.ch_supply = c->profile.ch_ground = c->profile.ch_feedback = -1;
    /* Nominalne wzmocnienia torów — punkt wyjścia do kalibracji, nie wynik. */
    const float nominal[8] = {4.06f, 4.06f, 1.02f, 1.02f, 1.02f, 1, 6.0898f, 4.06f};
    for (int bank = 0; bank < 2; bank++) {
        memcpy(c->profile.gain[bank], nominal, sizeof nominal);
        c->profile.current_zero[bank] = 2.5f; /* do zmierzenia w etapie 6 */
        c->profile.current_valid[bank] = false;
        c->profile.current_volts_per_amp[bank] = .25f;
        c->profile.current_adc_gain[bank] = 5.0f/4096.0f;
        strcpy(c->profile.current_module[bank], "UNBOUND");
    }
    /* Zworka AUX startuje w pozycji HI: tak samo jak nominalne wzmocnienie
     * kanału. v2 miało tu niespójność — zakres LO z wzmocnieniem HI. */
    c->profile.aux_position = AUX_HI;
    c->profile.aux_gain[AUX_HI] = 4.06f;
    c->profile.aux_gain[AUX_LO] = 1.02f;
    control_apply_ranges(&c->profile, false);
}
void control_apply_ranges(profile_t *p, bool software_mode) {
    for (int ch = 0; ch < 8; ch++) p->range[ch] = RANGE_10V;
    if (!software_mode) return;   /* hardware mode: wszystko na ±10 V, bez wyjątków */
    p->range[CH_CURRENT] = RANGE_5V;
    p->range[CH_AUX] = p->aux_position == AUX_LO ? RANGE_2V5 : RANGE_10V;
    if (p->ch_ground >= CH_SENSOR_FIRST) {
        /* Masa czujnika na ±2,5 V: 76 µV/LSB zamiast 305 µV — o to chodzi w H2. */
        p->range[p->ch_supply] = RANGE_10V; /* retain headroom above the 5.5 V alarm */
        p->range[p->ch_feedback] = RANGE_5V;
        p->range[p->ch_ground] = RANGE_2V5;
    }
}
void control_build_config(const control_t *c, session_config_t *out, uint16_t id,
                          const uint8_t applied_range[8], bool software_mode, bool config_ok) {
    const profile_t *p = &c->profile;
    int bank = c->test_bank ? 1 : 0;
    memset(out, 0, sizeof(*out));
    out->id = id;
    out->ch_supply = p->ch_supply; out->ch_ground = p->ch_ground;
    out->ch_feedback = p->ch_feedback; out->bank = (int8_t)bank;
    memcpy(out->range, applied_range, 8);
    memcpy(out->gain, p->gain[bank], sizeof out->gain);
    memcpy(out->offset, p->offset[bank], sizeof out->offset);
    /* Kanał AUX ma własną parę współczynników na pozycję zworki. */
    out->gain[CH_AUX] = p->aux_gain[p->aux_position ? AUX_LO : AUX_HI];
    out->offset[CH_AUX] = p->aux_offset[p->aux_position ? AUX_LO : AUX_HI];
    out->current_zero = p->current_zero[bank];
    out->closed = p->closed; out->open = p->open;
    out->opening_sign = p->opening_sign;
    out->aux_position = p->aux_position;
    out->learned = p->learned;
    out->current_valid = p->current_valid[bank] && p->current_calibrated[bank];
    out->local_current = true;
    out->current_calibrated = p->current_calibrated[bank];
    out->voltage_calibrated=p->voltage_calibrated[bank];
    memcpy(out->daq_module,p->daq_module,sizeof out->daq_module);
    out->current_volts_per_amp = p->current_volts_per_amp[bank];
    out->current_adc_gain = p->current_adc_gain[bank];
    out->current_adc_offset = p->current_adc_offset[bank];
    memcpy(out->current_module,p->current_module[bank],sizeof out->current_module);
    memcpy(out->valve,p->valve,sizeof out->valve); memcpy(out->adapter,p->adapter,sizeof out->adapter);
    memcpy(out->vehicle_id,p->vehicle_id,sizeof out->vehicle_id); memcpy(out->session_note,p->session_note,sizeof out->session_note);
    out->adc_software_mode = software_mode;
    out->adc_config_ok = config_ok;
    out->current_window_qualified = p->current_window_qualified;
}
void control_stop(control_t *c) {
    c->state = SAFE; c->duty = 0; c->sensor_on = false; c->fault = NULL;
    c->stable_since = 0; c->dwell_since = 0; c->soak.active = false;
}
static bool mapped(const profile_t *p) {
    return p->ch_supply >= CH_SENSOR_FIRST && p->ch_ground >= CH_SENSOR_FIRST
        && p->ch_feedback >= CH_SENSOR_FIRST;
}
/* Kryterium akceptacji trójki, wspólne dla IDENTIFY i bieżącej kontroli. */
static bool triple_ok(const inputs_t *in, int s, int g, int f) {
    float ref = in->v[s] - in->v[g], fb = in->v[f] - in->v[g];
    return isfinite(ref) && isfinite(fb)
        && in->v[g] >= -.2f && in->v[g] <= .3f
        && ref >= 4.5f && ref <= 5.5f && fb >= .2f && fb <= 4.8f;
}
int control_permutation(const inputs_t *in, int8_t out[3]) {
    static const int8_t perm[6][3] = {{2,3,4},{2,4,3},{3,2,4},{3,4,2},{4,2,3},{4,3,2}};
    int found = -1;
    for (int i = 0; i < 6; i++) {
        if (!triple_ok(in, perm[i][0], perm[i][1], perm[i][2])) continue;
        if (found >= 0) return -1;  /* dwie pasujące = wynik niejednoznaczny */
        found = i;
    }
    if (found >= 0 && out) memcpy(out, perm[found], 3);
    return found;
}
static bool sensor_valid(const control_t *c, const inputs_t *in) {
    const profile_t *p = &c->profile;
    return mapped(p) && (!c->test_bank || !in->sensor_fault)
        && triple_ok(in, p->ch_supply, p->ch_ground, p->ch_feedback);
}
float control_ratio(const control_t *c, const inputs_t *in) {
    if (!sensor_valid(c, in)) return NAN;
    const profile_t *p = &c->profile;
    return (in->v[p->ch_feedback] - in->v[p->ch_ground])
         / (in->v[p->ch_supply] - in->v[p->ch_ground]);
}
float control_position(const control_t *c, const inputs_t *in) {
    float span = c->profile.open - c->profile.closed;
    return c->profile.learned && fabsf(span) > .2f
        ? (control_ratio(c, in) - c->profile.closed) / span : NAN;
}
float control_current(const control_t *c, const inputs_t *in) {
    int bank = c->test_bank ? 1 : 0;
    if (!c->profile.current_valid[bank] || !c->profile.current_calibrated[bank]) return NAN;
    return (in->v[CH_CURRENT] - c->profile.current_zero[bank]) / c->profile.current_volts_per_amp[bank];
}

bool control_command(control_t *c, const char *cmd, float a, int b, uint64_t now) {
    if (!strcmp(cmd, "stop")) { control_stop(c); return true; }
    if (!strcmp(cmd, "logger")) {
        control_stop(c); c->state = LOGGER; c->test_bank = false; return true;
    }
    if (!strcmp(cmd, "identify") && c->state == LOGGER) {
        c->state = IDENTIFY; c->identify_since = 0; c->identify_candidate = -1;
        c->identify_deadline = now + 30000000; c->identified = false; return true;
    }
    if (!strcmp(cmd, "test") && c->state == SAFE && c->profile.qualified && mapped(&c->profile)) {
        c->test_bank = true; c->sensor_on = true; c->state = SENSOR_CHECK;
        c->started = now; c->deadline = now + 2000000; c->stable_since = 0; return true;
    }
    if (!strcmp(cmd, "hotsoak_stop")) { control_stop(c); return true; }
    if (c->state != READY) return false;
    if (!strcmp(cmd, "manual") && isfinite(a) && fabsf(a) <= c->profile.max_duty
            && b > 0 && b <= 250) {
        c->state = MANUAL; c->manual_duty = a; c->deadline = now + (uint64_t)b * 1000;
    } else if (c->profile.learned && !strcmp(cmd, "goto") && a >= .1f && a <= .9f) {
        c->state = GOTO; c->target = a; c->deadline = now + 2000000;
        c->move_started = now; c->move_ms = NAN;
    } else if (c->profile.learned && (!strcmp(cmd, "sweep") || !strcmp(cmd, "thermal"))) {
        c->thermal = !strcmp(cmd, "thermal"); c->state = c->thermal ? THERMAL : SWEEP;
        c->index = 0; c->target = .1f; c->deadline = now + 2000000;
    } else if (c->profile.learned && !strcmp(cmd, "cycle") && b > 0 && b <= 200) {
        c->state = CYCLE; c->cycles = b; c->cycle_done = 0; c->index = 0;
        c->target = .1f; c->deadline = now + 2000000;
    } else if (c->profile.learned && !strcmp(cmd, "friction") && (b == 1 || b == -1)) {
        c->state = FRICTION; c->friction_sign = b; c->start_position = NAN;
        c->breakaway_current = NAN; c->breakaway_duty = NAN; c->deadline = now + 2000000;
    } else if (!strcmp(cmd, "hotsoak")) {
        /* a = okres w sekundach, b = liczba serii. Kampania steruje tymi
         * samymi rozkazami co operator; każdy FAULT ją kasuje. */
        if (!c->profile.learned || !(a >= 10 && a <= 3600) || b < 1 || b > 200) return false;
        c->soak = (campaign_t){ .active = true, .period = (uint64_t)(a * 1e6f),
                                .next_at = now, .left = b, .step = 0 };
        return true;
    } else if (!strcmp(cmd, "hotsoak_stop")) {
        c->soak.active = false; return true;
    } else return false;
    c->started = now; c->stable_since = 0; c->dwell_since = 0; return true;
}

/* Kampania wykonuje się wyłącznie z poziomu READY i tylko rozkazami, które
 * operator mógłby wydać ręcznie. Odrzucony rozkaz przerywa kampanię. */
static void campaign_tick(control_t *c, const inputs_t *in) {
    campaign_t *s = &c->soak;
    if (!s->active || s->point_ready) return;
    if (s->step == 0 && in->now < s->next_at) return;
    bool ok = true;
    switch (s->step) {
    case 0: ok = control_command(c, "goto", .5f, 0, in->now); s->step = 1; break;
    case 1: ok = control_command(c, "friction", 0, 1, in->now); s->step = 2; break;
    case 2: s->i_break_open = c->breakaway_current;
            ok = control_command(c, "goto", .5f, 0, in->now); s->step = 3; break;
    case 3: ok = control_command(c, "friction", 0, -1, in->now); s->step = 4; break;
    case 4: s->i_break_close = c->breakaway_current;
            ok = control_command(c, "goto", .1f, 0, in->now); s->step = 5; break;
    case 5: ok = control_command(c, "goto", .9f, 0, in->now); s->step = 6; break;
    case 6: s->ms_open = c->move_ms;
            ok = control_command(c, "goto", .1f, 0, in->now); s->step = 7; break;
    default:
        s->ms_close = c->move_ms; s->t1 = in->t1; s->t2 = in->t2;
        s->vbat = in->v[CH_VBAT]; s->point_ready = true; s->done++;
        if (--s->left <= 0) s->active = false;
        else { s->next_at = in->now + s->period; s->step = 0; }
        break;
    }
    if (!ok) fail(c, "CAMPAIGN_REJECTED");
}

void control_guard_io(inputs_t *in, uint64_t inputs_time) {
    in->io_stale = !inputs_time || in->now < inputs_time || in->now-inputs_time > 100000;
    if (in->io_stale) {
        in->sensor_fault=true; in->log_present=true; in->test_present=false;
    }
}
void control_step(control_t *c, const inputs_t *in) {
    c->duty = 0;
    bool fresh = in->now >= in->sample_time && in->now - in->sample_time <= 10000;
    if (c->state == IDENTIFY) {
        int8_t triple[3];
        int k = fresh && in->adc_ok && !in->saturation_mask ? control_permutation(in, triple) : -1;
        if (k < 0 || k != c->identify_candidate) {
            c->identify_since = in->now; c->identify_candidate = k;
        }
        if (k >= 0 && in->now - c->identify_since >= 2000000) {
            if(c->profile.ch_supply!=triple[0] || c->profile.ch_ground!=triple[1] || c->profile.ch_feedback!=triple[2]) {
                c->profile.learned=false; c->profile.closed=c->profile.open=0;
            }
            c->profile.ch_supply = triple[0];
            c->profile.ch_ground = triple[1];
            c->profile.ch_feedback = triple[2];
            c->identified = true; c->state = LOGGER;
        } else if (in->now > c->identify_deadline) {
            c->identify_candidate = -1; c->state = LOGGER; /* UNKNOWN, nic nie zapisujemy */
        }
        return;
    }
    if (c->state == SAFE || c->state == LOGGER || c->state == FAULT) return;
    if (!fresh)            { fail(c, "ADC_STALE"); return; }
    if (in->io_stale)      { fail(c, "INPUTS_STALE"); return; }
    /* Niepotwierdzona konfiguracja przetwornika = nieznana skala napięć.
     * W v2 dane leciały dalej i wyglądały wiarygodnie. */
    if (!in->adc_ok)       { fail(c, "ADC_CONFIG"); return; }
    if (in->saturation_mask & 0x7f) { fail(c, "ADC_SATURATED"); return; }
    if (!in->interlock)    { fail(c, "INTERLOCK"); return; }
    if (!in->test_present) { fail(c, "TEST_ADAPTER"); return; }
    if (in->log_present)   { fail(c, "LOGGER_ADAPTER_PRESENT"); return; }
    if (!in->storage_ok)   { fail(c, "STORAGE"); return; }
    /* 6.2-s1 F-03: akumulator auta (VBAT_SENSE przez P02 R4), nie pakiet 4S zasilajacy przyrzad. */
    if (!isfinite(in->v[CH_VBAT]) || in->v[CH_VBAT] < 9 || in->v[CH_VBAT] > 16.5f) {
        fail(c, "SUPPLY"); return;
    }
    /* TPS fault is distinct from an analog sensor still settling at start-up. */
    if (in->sensor_fault) { fail(c, "SENSOR_HEALTH"); return; }
    if (c->state == SENSOR_CHECK) {
        if (sensor_valid(c, in)) {
            if (!c->stable_since) c->stable_since = in->now;
            if (in->now - c->stable_since >= 200000) c->state = READY;
        } else c->stable_since = 0;
        if (in->now > c->deadline) fail(c, "SENSOR_CHECK_TIMEOUT");
        return;
    }
    if (!sensor_valid(c, in)) { fail(c, "SENSOR"); return; }
    if (c->state == READY) { campaign_tick(c, in); return; }
    if (!in->hw_armed) { fail(c, "HARDWARE_NOT_ARMED"); return; }
    /* Nieudany zapis kierunku przez I²C nie może zostawić ruchu w toku. */
    if (!in->drive_ok) { fail(c, "DRIVE_IO"); return; }
    float current = control_current(c, in);
    if (!isfinite(current) || fabsf(current) > c->profile.current_limit) { fail(c, "CURRENT"); return; }
    if (!in->tc_ok || !isfinite(in->t1) || in->t1 > c->profile.temp_limit) { fail(c, "TEMPERATURE"); return; }
    if (c->state == MANUAL) {
        if (in->now >= c->deadline) { c->state = READY; return; }
        c->duty = c->manual_duty; return;
    }
    float pos = control_position(c, in);
    if (!isfinite(pos) || pos < -.05f || pos > 1.05f) { fail(c, "POSITION"); return; }
    if (in->now > c->deadline) { fail(c, "MOVE_TIMEOUT"); return; }
    if (c->state == FRICTION) {
        float ramp = .01f * (float)((in->now - c->started) / 50000);
        if (!isfinite(c->start_position)) c->start_position = pos;
        if (fabsf(pos - c->start_position) >= .01f) {
            if (!c->stable_since) {
                c->stable_since = in->now;
                c->breakaway_current = in->current_window_valid ? in->current_mean : NAN;
                c->breakaway_duty = ramp;
            }
            if (in->now - c->stable_since >= 20000) { c->state = READY; return; }
            c->duty = 0; return;
        } else c->stable_since = 0;
        if ((pos <= .1f && c->friction_sign < 0) || (pos >= .9f && c->friction_sign > 0)) {
            fail(c, "FRICTION_RANGE"); return;
        }
        if (ramp > c->profile.max_duty) { fail(c, "NO_BREAKAWAY"); return; }
        c->duty = ramp * c->friction_sign * c->profile.opening_sign; return;
    }
    float error = c->target - pos;
    if (fabsf(error) < .02f) {
        if (!c->stable_since) c->stable_since = in->now;
        if (in->now - c->stable_since >= 100000) {
            if (!c->dwell_since) c->dwell_since = in->now;
            uint64_t dwell = c->state == CYCLE ? 500000 : 300000;
            if (in->now - c->dwell_since >= dwell) {
                if (c->state == GOTO) {
                    c->move_ms = (float)(c->stable_since - c->move_started) / 1000.0f;
                    c->state = READY; return;
                }
                if (c->state == CYCLE) {
                    c->index++;
                    if (c->index >= 3 && c->index % 2 == 1) c->cycle_done++;
                    if (c->cycle_done >= c->cycles) { c->state = READY; return; }
                    c->target = c->index % 2 ? .9f : .1f;
                } else {
                    c->index++;
                    if (c->index >= 17) { c->state = READY; return; }
                    c->target = c->index <= 8 ? .1f + .1f * c->index : .9f - .1f * (c->index - 8);
                }
                c->deadline = in->now + 2000000; c->stable_since = 0; c->dwell_since = 0;
            }
        }
    } else { c->stable_since = 0; c->dwell_since = 0; }
    c->duty = fabsf(error) < .01f ? 0
        : clamp(.8f * error, -c->profile.max_duty, c->profile.max_duty) * c->profile.opening_sign;
}
