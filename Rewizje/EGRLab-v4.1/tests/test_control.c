/* Testy czystej logiki sterowania, do uruchomienia na PC:
 *   gcc -std=c11 -I firmware/main -o test_control tests/test_control.c firmware/main/control.c -lm
 *   ./test_control
 * Wyniki uruchomienia testow i kompilacji ESP-IDF: docs/06-weryfikacja.md. */
#include "control.h"
#include <math.h>
#include <stdio.h>
#include <string.h>

static int checks;
#define CHECK(cond) do { checks++; if (!(cond)) { \
    printf("FAIL %s:%d  %s\n", __FILE__, __LINE__, #cond); return 1; } } while (0)

/* Zdrowe wejscia: swieze dane, wszystkie blokady zamkniete, TEST wpiety. */
static inputs_t healthy(uint64_t now) {
    inputs_t in = {0};
    in.now = now; in.sample_time = now;
    in.interlock = true; in.hw_armed = true; in.storage_ok = true;
    in.tc_ok = true; in.t1 = 40; in.t2 = 60;
    in.test_present = true; in.log_present = false;
    in.adc_ok = true; in.drive_ok = true;
    in.v[CH_VBAT] = 13.5f;
    in.v[CH_CURRENT] = 2.5f;
    return in;
}
static void set_sensor(inputs_t *in, int s, int g, int f, float ratio) {
    in->v[g] = 0.02f;
    in->v[s] = in->v[g] + 5.0f;
    in->v[f] = in->v[g] + 0.2f + ratio * 4.5f;
}
static void ready_profile(control_t *c) {
    control_init(c);
    c->profile.ch_supply = 2; c->profile.ch_ground = 4; c->profile.ch_feedback = 3;
    c->profile.closed = .1f; c->profile.open = .9f; c->profile.learned = true;
    c->profile.qualified = true;
    c->state = READY; c->test_bank = true;
}

static int test_permutations(void) {
    static const int8_t perm[6][3] = {{2,3,4},{2,4,3},{3,2,4},{3,4,2},{4,2,3},{4,3,2}};
    for (int i = 0; i < 6; i++) {
        inputs_t in = healthy(1000);
        set_sensor(&in, perm[i][0], perm[i][1], perm[i][2], .5f);
        int8_t out[3] = {0};
        CHECK(control_permutation(&in, out) == i);
        CHECK(out[0] == perm[i][0] && out[1] == perm[i][1] && out[2] == perm[i][2]);
    }
    inputs_t dead = healthy(1000);
    CHECK(control_permutation(&dead, NULL) == -1);
    return 0;
}
static int test_identify_needs_two_seconds_and_times_out(void) {
    control_t c; control_init(&c);
    CHECK(control_command(&c, "logger", 0, 0, 0));
    CHECK(control_command(&c, "identify", 0, 0, 0));
    inputs_t in = healthy(100000);
    set_sensor(&in, 2, 4, 3, .5f);              /* pinout ze schematu Monolith */
    control_step(&c, &in);
    CHECK(c.state == IDENTIFY && !c.identified);
    in = healthy(1500000); set_sensor(&in, 2, 4, 3, .5f);
    control_step(&c, &in);
    CHECK(c.state == IDENTIFY);                 /* jeszcze nie minely 2 s */
    in = healthy(2200000); set_sensor(&in, 2, 4, 3, .5f);
    control_step(&c, &in);
    CHECK(c.identified && c.state == LOGGER);
    CHECK(c.profile.ch_supply == 2 && c.profile.ch_ground == 4 && c.profile.ch_feedback == 3);

    control_t t; control_init(&t);
    control_command(&t, "logger", 0, 0, 0);
    control_command(&t, "identify", 0, 0, 0);
    inputs_t bad = healthy(1000);
    control_step(&t, &bad);
    bad = healthy(31000000);
    control_step(&t, &bad);
    CHECK(t.state == LOGGER && !t.identified);  /* timeout nie zapisuje niczego */
    CHECK(t.profile.ch_supply == -1);
    return 0;
}
/* Zakresy sa ZADANE przez profil, a ich zastosowanie potwierdza sprzet.
 * W hardware mode nie wolno zadac +-2,5 V, bo uklad tego nie zrobi. */
static int test_ranges_follow_mode(void) {
    control_t c; control_init(&c);
    c.profile.ch_supply = 2; c.profile.ch_ground = 4; c.profile.ch_feedback = 3;
    control_apply_ranges(&c.profile, true);
    CHECK(c.profile.range[4] == RANGE_2V5);
    CHECK(c.profile.range[2] == RANGE_10V && c.profile.range[3] == RANGE_5V);
    CHECK(c.profile.range[CH_MOTOR_A] == RANGE_10V);
    CHECK(c.profile.range[CH_CURRENT] == RANGE_5V);
    control_apply_ranges(&c.profile, false);
    for (int i = 0; i < 8; i++) CHECK(c.profile.range[i] == RANGE_10V);
    /* Zworka AUX w pozycji LO daje najczulszy zakres tylko w software mode. */
    c.profile.aux_position = AUX_LO;
    control_apply_ranges(&c.profile, true);
    CHECK(c.profile.range[CH_AUX] == RANGE_2V5);
    control_apply_ranges(&c.profile, false);
    CHECK(c.profile.range[CH_AUX] == RANGE_10V);
    return 0;
}
/* Migawka musi nieść to, co sprzet POTWIERDZIL, i wspolczynniki wlasciwego
 * banku oraz wlasciwej pozycji zworki AUX. */
static int test_build_config(void) {
    control_t c; ready_profile(&c);
    c.profile.gain[0][0] = 4.00f; c.profile.gain[1][0] = 4.10f;
    c.profile.current_zero[0] = 2.40f; c.profile.current_zero[1] = 2.60f;
    c.profile.aux_gain[AUX_HI] = 4.06f; c.profile.aux_gain[AUX_LO] = 1.02f;
    c.profile.current_valid[1] = false;
    uint8_t applied[8] = {RANGE_10V, RANGE_10V, RANGE_10V, RANGE_10V,
                          RANGE_10V, RANGE_5V, RANGE_10V, RANGE_10V};
    session_config_t cfg;
    control_build_config(&c, &cfg, 7, applied, true, true);
    CHECK(cfg.id == 7 && cfg.bank == 1);
    CHECK(cfg.gain[0] == 4.10f);
    CHECK(cfg.current_zero == 2.60f);
    CHECK(cfg.gain[CH_AUX] == 4.06f);
    CHECK(!cfg.current_valid);
    /* Zakres masy w migawce to +-10 V, bo tyle sprzet potwierdzil, choc
     * profil zadal +-2,5 V. To jest sedno poprawki F06. */
    CHECK(cfg.range[4] == RANGE_10V);
    c.profile.aux_position = AUX_LO;
    control_build_config(&c, &cfg, 8, applied, true, false);
    CHECK(cfg.gain[CH_AUX] == 1.02f);
    CHECK(!cfg.adc_config_ok);
    return 0;
}
static int test_ratio_and_position(void) {
    control_t c; control_init(&c);
    c.profile.ch_supply = 2; c.profile.ch_ground = 4; c.profile.ch_feedback = 3;
    inputs_t in = healthy(1000);
    set_sensor(&in, 2, 4, 3, .5f);
    float r = control_ratio(&c, &in);
    CHECK(fabsf(r - (0.2f + 0.5f * 4.5f) / 5.0f) < 1e-4f);
    CHECK(isnan(control_position(&c, &in)));    /* bez LEARN nie ma pozycji */
    c.profile.closed = .8f; c.profile.open = .3f; c.profile.learned = true;
    float p = control_position(&c, &in);
    CHECK(isfinite(p));
    CHECK(fabsf(p - (r - .8f) / (.3f - .8f)) < 1e-4f);
    return 0;
}
static int test_current_uses_measured_zero_and_validity(void) {
    control_t c; control_init(&c);
    c.profile.current_zero[0] = 2.44f; c.profile.current_zero[1] = 2.61f;
    inputs_t in = healthy(1000);
    in.v[CH_CURRENT] = 2.94f;
    c.test_bank = false;
    CHECK(fabsf(control_current(&c, &in) - 2.0f) < 1e-3f);
    c.test_bank = true;
    CHECK(fabsf(control_current(&c, &in) - 1.32f) < 1e-3f);
    /* Zalozony mostek bocznikujacy: prad jest nieznany, a nie rowny zeru. */
    c.profile.current_valid[1] = false;
    CHECK(isnan(control_current(&c, &in)));
    return 0;
}
static int test_guards(void) {
    control_t base; ready_profile(&base);
    base.state = SAFE;
    for (int variant = 0; variant < 8; variant++) {
        control_t c = base;
        c.state = READY;
        inputs_t in = healthy(1000);
        set_sensor(&in, 2, 4, 3, .5f);
        switch (variant) {
        case 0: in.interlock = false; break;
        case 1: in.test_present = false; break;
        case 2: in.log_present = true; break;
        case 3: in.storage_ok = false; break;
        case 4: in.v[CH_VBAT] = 8.0f; break;
        case 5: in.sample_time = 0; in.now = 100000; break;  /* nieswieze dane */
        case 6: in.adc_ok = false; break;                    /* nowe w v3 */
        case 7: in.sensor_fault = true; break;
        }
        control_step(&c, &in);
        CHECK(c.state == FAULT);
        CHECK(c.duty == 0.0f);
        CHECK(!c.sensor_on);
    }
    /* Brak sprzetowego ARM i blad zapisu kierunku blokuja sam ruch. */
    const char *expected[2] = {"HARDWARE_NOT_ARMED", "DRIVE_IO"};
    for (int variant = 0; variant < 2; variant++) {
        control_t c = base;
        c.state = READY;
        inputs_t in = healthy(1000); set_sensor(&in, 2, 4, 3, .5f);
        control_step(&c, &in);
        CHECK(c.state == READY);
        CHECK(control_command(&c, "goto", .5f, 0, 1000));
        if (variant == 0) in.hw_armed = false; else in.drive_ok = false;
        control_step(&c, &in);
        CHECK(c.state == FAULT && !strcmp(c.fault, expected[variant]));
    }
    return 0;
}
static int test_friction_records_breakaway(void) {
    control_t c; ready_profile(&c);
    CHECK(control_command(&c, "friction", 0, 1, 0));
    for (uint64_t t = 0; t < 400000; t += 50000) {
        inputs_t in = healthy(t);
        set_sensor(&in, 2, 4, 3, .5f);
        control_step(&c, &in);
        CHECK(c.state == FRICTION);
    }
    CHECK(c.duty > 0.05f);
    inputs_t moved = healthy(420000);
    set_sensor(&moved, 2, 4, 3, .52f);
    moved.v[CH_CURRENT] = 2.5f + 0.8f * 0.25f;
    moved.current_window_valid = true; moved.current_mean = .8f;
    control_step(&c, &moved);
    CHECK(fabsf(c.breakaway_current - 0.8f) < 1e-2f);
    CHECK(c.breakaway_duty > 0.0f);
    return 0;
}
static int test_hotsoak_campaign(void) {
    control_t c; ready_profile(&c);
    CHECK(!control_command(&c, "hotsoak", 5, 3, 0));      /* okres ponizej 10 s odrzucony */
    CHECK(control_command(&c, "hotsoak", 180, 3, 0));
    CHECK(c.soak.active && c.soak.left == 3);
    inputs_t in = healthy(1000);
    set_sensor(&in, 2, 4, 3, .5f);
    control_step(&c, &in);
    CHECK(c.state == GOTO);                                /* kampania wydala rozkaz */
    inputs_t broken = healthy(2000);
    set_sensor(&broken, 2, 4, 3, .5f);
    broken.interlock = false;
    control_step(&c, &broken);
    CHECK(c.state == FAULT && !c.soak.active);
    return 0;
}
static int test_stop_and_fault_recovery(void) {
    control_t c; control_init(&c);
    c.state = FAULT; c.fault = "CURRENT"; c.sensor_on = true;
    inputs_t in = healthy(1000);
    control_step(&c, &in);
    CHECK(c.state == FAULT);                               /* FAULT sam nie ustepuje */
    control_stop(&c);
    CHECK(c.state == SAFE && !c.sensor_on && c.fault == NULL);
    return 0;
}
static int test_command_limits(void) {
    control_t c; control_init(&c);
    c.state = READY;
    CHECK(!control_command(&c, "manual", 0.9f, 50, 0));     /* ponad max_duty */
    CHECK(!control_command(&c, "manual", 0.1f, 400, 0));    /* ponad 250 ms */
    CHECK(control_command(&c, "manual", 0.1f, 50, 0));
    c.state = READY;
    CHECK(!control_command(&c, "goto", .5f, 0, 0));         /* bez LEARN */
    c.profile.learned = true; c.profile.closed = .1f; c.profile.open = .9f;
    CHECK(!control_command(&c, "goto", .95f, 0, 0));        /* poza 10-90 % */
    CHECK(control_command(&c, "goto", .5f, 0, 0));
    c.state = READY;
    CHECK(!control_command(&c, "cycle", 0, 500, 0));
    CHECK(control_command(&c, "cycle", 0, 20, 0));
    return 0;
}

int main(void) {
    struct { const char *name; int (*fn)(void); } tests[] = {
        {"permutacje pinow", test_permutations},
        {"IDENTIFY: 2 s i timeout", test_identify_needs_two_seconds_and_times_out},
        {"zakresy zalezne od trybu ADC", test_ranges_follow_mode},
        {"migawka konfiguracji", test_build_config},
        {"ratio i pozycja", test_ratio_and_position},
        {"prad: zero i waznosc", test_current_uses_measured_zero_and_validity},
        {"blokady", test_guards},
        {"FRICTION zapisuje prad zerwania", test_friction_records_breakaway},
        {"kampania HOT-SOAK", test_hotsoak_campaign},
        {"STOP i wyjscie z FAULT", test_stop_and_fault_recovery},
        {"limity rozkazow", test_command_limits},
    };
    int failures = 0;
    for (unsigned i = 0; i < sizeof tests / sizeof tests[0]; i++) {
        int r = tests[i].fn();
        printf("%-36s %s\n", tests[i].name, r ? "FAIL" : "ok");
        failures += r != 0;
    }
    printf("%d asercji, %d nieudanych testow\n", checks, failures);
    return failures != 0;
}
