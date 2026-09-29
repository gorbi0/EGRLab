#include "trigger.h"
#include <math.h>
#include <string.h>

#define JUMP_THRESHOLD  0.05f   /* skok ratio w oknie JUMP_WINDOW_US */
#define JUMP_WINDOW_US  1000    /* 1 ms, niezaleznie od czestotliwosci probkowania */
#define JUMP_MAX_DELAY  32      /* max probek w oknie; przy 2 kS/s wystarczy 2 */
#define STALL_CURRENT   0.30f   /* A */
#define STALL_RATIO     0.01f
#define OPEN_VOLTS      2.00f
#define OPEN_CURRENT    0.10f
#define REARM_US        250000  /* jedno zdarzenie danego typu na 250 ms */

static struct {
    int8_t supply, ground, feedback;
    float zero;
    uint32_t hz;
    uint32_t delay;             /* ile probek wstecz to 1 ms */
    bool ready, current_valid;
    uint16_t id; int8_t bank;
} cfg;

static struct {
    uint64_t last[TRIG_COUNT];
    bool armed[TRIG_COUNT];     /* false = zatrzask trzyma do uplywu REARM_US */
    float history[JUMP_MAX_DELAY];
    uint64_t history_time[JUMP_MAX_DELAY];
    uint32_t written;
    float stall_ratio;
    uint64_t stall_since, open_since, second_start;
    float min[8], max[8], sum[8];
    uint32_t count, valid_count[8];
    summary_t pending;
    bool has_summary;
} st;

const char *trigger_name(int bit) {
    static const char *names[TRIG_COUNT] = {"ref", "ground", "ground_warn", "feedback",
                                            "jump", "stall", "open"};
    return bit >= 0 && bit < TRIG_COUNT ? names[bit] : "?";
}
void trigger_configure(const session_config_t *c, uint32_t sample_hz) {
    memset(&st, 0, sizeof st);
    st.stall_ratio = NAN;
    for (uint32_t i = 0; i < JUMP_MAX_DELAY; i++) st.history[i] = NAN;
    for (int i = 0; i < TRIG_COUNT; i++) st.armed[i] = true;
    cfg.id=c->id; cfg.bank=c->bank;
    cfg.supply = c->ch_supply; cfg.ground = c->ch_ground; cfg.feedback = c->ch_feedback;
    cfg.zero = c->current_zero;
    cfg.hz = sample_hz ? sample_hz : 2000;
    cfg.current_valid = c->current_valid;
    cfg.ready = c->ch_supply >= CH_SENSOR_FIRST && c->ch_ground >= CH_SENSOR_FIRST
             && c->ch_feedback >= CH_SENSOR_FIRST;
    /* Okno skoku wyrazone w czasie, nie w sasiednich probkach: przy 2 kS/s
     * to 2 probki, przy 20 kS/s â€” 20. v2 porownywalo zawsze sasiednie. */
    uint32_t delay = (cfg.hz * JUMP_WINDOW_US) / 1000000u;
    if (delay < 1) delay = 1;
    if (delay > JUMP_MAX_DELAY - 1) delay = JUMP_MAX_DELAY - 1;
    cfg.delay = delay;
    for (int i = 0; i < 8; i++) { st.min[i] = INFINITY; st.max[i] = -INFINITY; }
}
/* Zatrzask trzyma przez pelne REARM_US niezaleznie od tego, czy warunek w
 * miedzyczasie ustapil. W v2 ustapienie warunku kasowalo zatrzask, wiec
 * seria naprzemiennych glitchy obchodzila limit. */
static bool fire(int bit, bool condition, uint64_t t_us) {
    if (!st.armed[bit] && t_us - st.last[bit] >= REARM_US) st.armed[bit] = true;
    if (!condition || !st.armed[bit]) return false;
    st.armed[bit] = false; st.last[bit] = t_us;
    return true;
}
static void accumulate(const float v[8], uint64_t t_us) {
    if (!st.second_start) st.second_start = t_us;
    for (int i = 0; i < 8; i++) {
        if (!isfinite(v[i])) continue;
        if (v[i] < st.min[i]) st.min[i] = v[i];
        if (v[i] > st.max[i]) st.max[i] = v[i];
        st.sum[i] += v[i]; st.valid_count[i]++;
    }
    st.count++;
    if (t_us - st.second_start >= 1000000 && !st.has_summary) {
        st.pending.t_us = t_us; st.pending.start_us=st.second_start;
        st.pending.config_id=cfg.id; st.pending.bank=cfg.bank; st.pending.count = st.count;
        for (int i = 0; i < 8; i++) {
            st.pending.min[i] = isfinite(st.min[i]) ? st.min[i] : NAN;
            st.pending.max[i] = isfinite(st.max[i]) ? st.max[i] : NAN;
            st.pending.valid_count[i]=st.valid_count[i];
            st.pending.mean[i] = st.valid_count[i] ? st.sum[i] / (float)st.valid_count[i] : NAN;
            st.valid_count[i]=0;
            st.min[i] = INFINITY; st.max[i] = -INFINITY; st.sum[i] = 0;
        }
        st.count = 0; st.second_start = t_us; st.has_summary = true;
    }
}
uint32_t trigger_sample(const float v[8], uint64_t t_us) {
    accumulate(v, t_us);
    if (!cfg.ready) return 0;
    uint32_t mask = 0;
    float gnd = v[cfg.ground];
    float ref = v[cfg.supply] - gnd;
    float fb  = v[cfg.feedback] - gnd;
    float drive = fabsf(v[CH_MOTOR_A] - v[CH_MOTOR_B]);
    /* Prad banku LOGGER bywa niewazny: sondy back-probe albo zalozony mostek
     * bocznikujacy. Wtedy kryteria oparte na pradzie musza milczec, zamiast
     * zglaszac przerwe w torze napedu na kanale bez informacji. */
    bool have_current = cfg.current_valid;
    float current = have_current ? (v[CH_CURRENT] - cfg.zero) / .25f : NAN;

    if (fire(0, !(ref >= 4.5f && ref <= 5.5f), t_us)) mask |= TRIG_REF;
    if (fire(1, fabsf(gnd) > TRIG_GND_EVENT_V, t_us)) mask |= TRIG_GND;
    if (fire(2, fabsf(gnd) > TRIG_GND_WARN_V, t_us)) mask |= TRIG_GND_WARN;
    if (fire(3, !(fb >= .2f && fb <= 4.8f), t_us)) mask |= TRIG_FB;

    float ratio = (ref > 1.0f) ? fb / ref : NAN;
    float past=NAN;
    unsigned count=st.written<JUMP_MAX_DELAY ? st.written : JUMP_MAX_DELAY;
    for(unsigned n=1;n<=count;n++) {
        unsigned idx=(st.written+JUMP_MAX_DELAY-n)%JUMP_MAX_DELAY;
        uint64_t age=t_us-st.history_time[idx];
        if(age>=JUMP_WINDOW_US) { if(age<=JUMP_WINDOW_US+1000) past=st.history[idx]; break; }
    }
    if (fire(4, isfinite(ratio) && isfinite(past) && fabsf(ratio-past)>JUMP_THRESHOLD,t_us)) mask|=TRIG_JUMP;
    st.history[st.written % JUMP_MAX_DELAY] = ratio;
    st.history_time[st.written % JUMP_MAX_DELAY] = t_us;
    st.written++;

    /* Prad plynie, a pozycja nie drgnela przez 200 ms â€” kandydat na zaciecie
     * albo na klamiacy sygnal pozycji. Uwaga przy interpretacji: to samo
     * widac przy normalnym utrzymywaniu pozycji pod obciazeniem. */
    if (have_current && fabsf(current) > STALL_CURRENT && isfinite(ratio)) {
        if (!st.stall_since || !isfinite(st.stall_ratio)
                || fabsf(ratio - st.stall_ratio) > STALL_RATIO) {
            st.stall_since = t_us; st.stall_ratio = ratio;
        } else if (t_us - st.stall_since >= 200000 && fire(5, true, t_us)) mask |= TRIG_STALL;
    } else { st.stall_since = 0; st.stall_ratio = NAN; }

    /* Napiecie na uzwojeniu bez pradu â€” przerwa w torze napedu. */
    if (have_current && drive > OPEN_VOLTS && fabsf(current) < OPEN_CURRENT) {
        if (!st.open_since) st.open_since = t_us;
        else if (t_us - st.open_since >= 50000 && fire(6, true, t_us)) mask |= TRIG_OPEN;
    } else st.open_since = 0;
    return mask;
}
bool trigger_take_summary(summary_t *out) {
    if (!st.has_summary) return false;
    *out = st.pending; st.has_summary = false;
    return true;
}
