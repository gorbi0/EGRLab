#include "trigger.h"
#include <math.h>
#include <string.h>

#define GND_THRESHOLD   0.30f   /* V; procedura v3 Krok 2 używa tego progu */
#define JUMP_THRESHOLD  0.05f   /* skok ratio między kolejnymi próbkami */
#define STALL_CURRENT   0.30f   /* A */
#define STALL_RATIO     0.01f
#define OPEN_VOLTS      2.00f
#define OPEN_CURRENT    0.10f
#define REARM_US        250000  /* jedno zdarzenie danego typu na 250 ms */

static struct {
    int8_t supply, ground, feedback;
    float zero;
    uint32_t hz;
    bool ready;
} cfg;

static struct {
    uint64_t last[TRIG_COUNT];
    bool latched[TRIG_COUNT];
    float prev_ratio, stall_ratio;
    uint64_t stall_since, open_since, second_start;
    float min[8], max[8], sum[8];
    uint32_t count;
    summary_t pending;
    bool has_summary;
} st;

const char *trigger_name(int bit) {
    static const char *names[TRIG_COUNT] = {"ref", "ground", "feedback", "jump", "stall", "open"};
    return bit >= 0 && bit < TRIG_COUNT ? names[bit] : "?";
}
void trigger_configure(const profile_t *p, int bank, uint32_t sample_hz) {
    memset(&st, 0, sizeof st);
    st.prev_ratio = NAN; st.stall_ratio = NAN;
    cfg.supply = p->ch_supply; cfg.ground = p->ch_ground; cfg.feedback = p->ch_feedback;
    cfg.zero = p->current_zero[bank ? 1 : 0];
    cfg.hz = sample_hz ? sample_hz : 2000;
    cfg.ready = p->ch_supply >= CH_SENSOR_FIRST;
    for (int i = 0; i < 8; i++) { st.min[i] = INFINITY; st.max[i] = -INFINITY; }
}
/* Zdarzenie wymaga ustąpienia warunku albo upływu REARM_US — inaczej jedna
 * długa anomalia zalałaby NDJSON tysiącem linii na sekundę. */
static bool fire(int bit, bool condition, uint64_t t_us) {
    if (!condition) { st.latched[bit] = false; return false; }
    if (st.latched[bit] && t_us - st.last[bit] < REARM_US) return false;
    st.latched[bit] = true; st.last[bit] = t_us;
    return true;
}
static void accumulate(const float v[8], uint64_t t_us) {
    if (!st.second_start) st.second_start = t_us;
    for (int i = 0; i < 8; i++) {
        if (!isfinite(v[i])) continue;
        if (v[i] < st.min[i]) st.min[i] = v[i];
        if (v[i] > st.max[i]) st.max[i] = v[i];
        st.sum[i] += v[i];
    }
    st.count++;
    if (t_us - st.second_start >= 1000000 && !st.has_summary) {
        st.pending.t_us = t_us; st.pending.count = st.count;
        for (int i = 0; i < 8; i++) {
            st.pending.min[i] = isfinite(st.min[i]) ? st.min[i] : NAN;
            st.pending.max[i] = isfinite(st.max[i]) ? st.max[i] : NAN;
            st.pending.mean[i] = st.count ? st.sum[i] / (float)st.count : NAN;
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
    float current = (v[CH_CURRENT] - cfg.zero) / .25f;
    float drive = fabsf(v[CH_MOTOR_A] - v[CH_MOTOR_B]);

    if (fire(0, !(ref >= 4.5f && ref <= 5.5f), t_us)) mask |= TRIG_REF;
    if (fire(1, fabsf(gnd) > GND_THRESHOLD, t_us)) mask |= TRIG_GND;
    if (fire(2, !(fb >= .2f && fb <= 4.8f), t_us)) mask |= TRIG_FB;

    float ratio = (ref > 1.0f) ? fb / ref : NAN;
    if (isfinite(ratio) && isfinite(st.prev_ratio)
        && fire(3, fabsf(ratio - st.prev_ratio) > JUMP_THRESHOLD, t_us)) mask |= TRIG_JUMP;
    else if (!isfinite(ratio) || !isfinite(st.prev_ratio)) st.latched[3] = false;
    st.prev_ratio = ratio;

    /* Prąd płynie, a pozycja nie drgnęła przez 200 ms — kandydat na zacięcie
     * albo na kłamiący sygnał pozycji; rozdziela to dopiero obserwacja. */
    if (fabsf(current) > STALL_CURRENT && isfinite(ratio)) {
        if (!st.stall_since || !isfinite(st.stall_ratio)) {
            st.stall_since = t_us; st.stall_ratio = ratio;
        } else if (fabsf(ratio - st.stall_ratio) > STALL_RATIO) {
            st.stall_since = t_us; st.stall_ratio = ratio;
        } else if (t_us - st.stall_since >= 200000 && fire(4, true, t_us)) mask |= TRIG_STALL;
    } else { st.stall_since = 0; st.stall_ratio = NAN; st.latched[4] = false; }

    /* Napięcie na uzwojeniu bez prądu — przerwa w torze napędu. */
    if (drive > OPEN_VOLTS && fabsf(current) < OPEN_CURRENT) {
        if (!st.open_since) st.open_since = t_us;
        else if (t_us - st.open_since >= 50000 && fire(5, true, t_us)) mask |= TRIG_OPEN;
    } else { st.open_since = 0; st.latched[5] = false; }
    return mask;
}
bool trigger_take_summary(summary_t *out) {
    if (!st.has_summary) return false;
    *out = st.pending; st.has_summary = false;
    return true;
}
