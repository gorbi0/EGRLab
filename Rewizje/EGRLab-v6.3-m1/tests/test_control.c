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

/* Zdrowe wejscia: swieze dane, zapis i przetwornik sprawne (6.3-m1: bez interlock / ARM / adapterow, M-01). */
static inputs_t healthy(uint64_t now) {
    inputs_t in = {0};
    in.now = now; in.sample_time = now;
    in.storage_ok = true;
    in.tc_ok = true; in.t1 = 40; in.t2 = 60;
    in.adc_ok = true; in.drive_ok = true;
    in.v[CH_VBAT] = 13.5f;
    in.v[CH_CURRENT] = 2.5f;
    return in;
}
static void set_sensor(inputs_t *in, int s, int g, int f, float ratio) {
    in->v[g] = 0.02f;
    in->v[s] = in->v[g] + 5.0f;
    in->v[f] = in->v[g] + 0.2f + ratio * 4.5f;
    in->v[CH_SENS5V] = in->v[s];          /* M-07: w TEST zasilanie czujnika z TPS2553, widoczne na CH8 */
}
static void ready_profile(control_t *c) {
    control_init(c);
    c->profile.ch_supply = 2; c->profile.ch_ground = 4; c->profile.ch_feedback = 3;
    c->profile.closed = .1f; c->profile.open = .9f; c->profile.learned = true;
    c->profile.qualified = true;
    c->profile.current_valid[1]=true;c->profile.current_calibrated[1]=true;
    c->profile.voltage_calibrated[1]=true;
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
    /* 6.3-m1: CH8 = SENS_5V zawsze +-10 V; dawna zworka AUX nie ma wplywu. */
    c.profile.aux_position = AUX_LO;
    control_apply_ranges(&c.profile, true);
    CHECK(c.profile.range[CH_SENS5V] == RANGE_10V);
    control_apply_ranges(&c.profile, false);
    CHECK(c.profile.range[CH_SENS5V] == RANGE_10V);
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
    CHECK(cfg.gain[CH_SENS5V] == 1.02f);  /* M-03: CH8 z gain[bank][7], nie z aux_gain */
    CHECK(!cfg.current_valid);
    CHECK(!cfg.local_current);            /* M-04: prad z CH6, nie z MCP3201 */
    /* Zakres masy w migawce to +-10 V, bo tyle sprzet potwierdzil, choc
     * profil zadal +-2,5 V. To jest sedno poprawki F06. */
    CHECK(cfg.range[4] == RANGE_10V);
    c.profile.aux_position = AUX_LO;
    control_build_config(&c, &cfg, 8, applied, true, false);
    CHECK(cfg.gain[CH_SENS5V] == 1.02f);
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
    for(int b=0;b<2;b++){c.profile.current_valid[b]=true;c.profile.current_calibrated[b]=true;}
    c.profile.current_zero[0] = 2.44f; c.profile.current_zero[1] = 2.61f;
    inputs_t in = healthy(1000);
    in.v[CH_CURRENT] = 2.94f;
    c.test_bank = false;
    CHECK(isfinite(control_current(&c,&in)) && fabsf(control_current(&c, &in) - 2.0f) < 1e-3f);
    c.test_bank = true;
    CHECK(isfinite(control_current(&c,&in)) && fabsf(control_current(&c, &in) - 1.32f) < 1e-3f);
    /* Zalozony mostek bocznikujacy: prad jest nieznany, a nie rowny zeru. */
    c.profile.current_valid[1] = false;
    CHECK(isnan(control_current(&c, &in)));
    return 0;
}
static int test_guards(void) {
    control_t base; ready_profile(&base);
    base.state = SAFE;
    for (int variant = 0; variant < 10; variant++) {
        control_t c = base;
        c.state = READY;
        inputs_t in = healthy(1000);
        set_sensor(&in, 2, 4, 3, .5f);
        switch (variant) {
        case 0: in.drive_ok = false; break;                  /* M-06: ograniczenie pradu zadzialalo */
        case 1: in.v[CH_SENS5V] = 4.2f; break;               /* M-07: SENS_5V za nisko */
        case 2: in.v[CH_SENS5V] = 5.6f; in.v[2] = 5.5f; break; /* M-07: za wysoko */
        case 3: in.storage_ok = false; break;
        case 4: in.v[CH_VBAT] = 8.0f; break;
        case 5: in.sample_time = 0; in.now = 100000; break;  /* nieswieze dane */
        case 6: in.adc_ok = false; break;                    /* nowe w v3 */
        case 7: in.sensor_fault = true; break;
        case 8: in.v[CH_SENS5V] = in.v[2] - .5f; break;      /* zasilanie czujnika nie z TPS2553 */
        case 9: in.v[CH_SENS5V] = NAN; break;
        }
        control_step(&c, &in);
        CHECK(c.state == FAULT);
        CHECK(c.duty == 0.0f);
        CHECK(!c.sensor_on);
    }
    /* M-06: zadzialanie ograniczenia pradu w ruchu konczy sie FAULT OVERCURRENT. */
    {
        control_t c = base;
        c.state = READY;
        inputs_t in = healthy(1000); set_sensor(&in, 2, 4, 3, .5f);
        control_step(&c, &in);
        CHECK(c.state == READY);
        CHECK(control_command(&c, "goto", .5f, 0, 1000));
        in.drive_ok = false;
        control_step(&c, &in);
        CHECK(c.state == FAULT && !strcmp(c.fault, "OVERCURRENT") && c.duty == 0.0f);
    }
    /* Bank LOGGER nie sprawdza CH8 (SENS_5V wylaczone, D-M1-5). */
    {
        control_t c; control_init(&c);
        CHECK(control_command(&c, "logger", 0, 0, 0));
        inputs_t in = healthy(1000); set_sensor(&in, 2, 4, 3, .5f); in.v[CH_SENS5V] = 0;
        control_step(&c, &in);
        CHECK(c.state == LOGGER);
    }
    return 0;
}
/* 6.3-m1: bez detekcji adaptera TEST wymaga linii bez napiecia i wylaczonego SENS_5V. */
static int test_test_wiring(void) {
    inputs_t in = healthy(1000);
    for (int j = 0; j < 8; j++) in.v[j] = 0.01f;
    CHECK(control_test_wiring(&in) == NULL);
    inputs_t x = in; x.v[CH_MOTOR_A] = 6.0f;  CHECK(!strcmp(control_test_wiring(&x), "MOTOR_LINES_LIVE"));
    x = in; x.v[CH_MOTOR_B] = -0.8f;          CHECK(!strcmp(control_test_wiring(&x), "MOTOR_LINES_LIVE"));
    for (int j = 2; j <= 4; j++) { x = in; x.v[j] = 5.0f; CHECK(!strcmp(control_test_wiring(&x), "SENSOR_LINES_LIVE")); }
    x = in; x.v[CH_SENS5V] = 5.0f;            CHECK(!strcmp(control_test_wiring(&x), "SENS_5V_ON"));
    x = in; x.v[3] = NAN;                     CHECK(!strcmp(control_test_wiring(&x), "VOLTAGE_UNKNOWN"));
    x = in; x.adc_ok = false;                 CHECK(!strcmp(control_test_wiring(&x), "ADC_CONFIG"));
    x = in; x.now = 100000;                   CHECK(!strcmp(control_test_wiring(&x), "ADC_STALE"));
    x = in; x.v[CH_VBAT] = NAN; x.v[CH_CURRENT] = NAN;
    CHECK(control_test_wiring(&x) == NULL);   /* VBAT i prad nie decyduja o okablowaniu */
    return 0;
}
/* M-04: zero pradu tylko przy stabilnym CH6 i liniach silnika bez napiecia. */
static int test_zero_window(void) {
    float mean[8] = {0}, mn[8] = {0}, mx[8] = {0};
    mean[CH_CURRENT] = 2.49f; mn[CH_CURRENT] = 2.485f; mx[CH_CURRENT] = 2.495f;
    CHECK(control_zero_ok(mean, mn, mx));
    float m2[8]; memcpy(m2, mx, sizeof m2); m2[CH_MOTOR_A] = 0.9f; CHECK(!control_zero_ok(mean, mn, m2));
    memcpy(m2, mn, sizeof m2); m2[CH_MOTOR_B] = -0.7f; CHECK(!control_zero_ok(mean, m2, mx));
    memcpy(m2, mx, sizeof m2); m2[CH_CURRENT] = 2.51f; CHECK(!control_zero_ok(mean, mn, m2));  /* 25 mV p-p */
    memcpy(m2, mean, sizeof m2); m2[CH_CURRENT] = 0.5f; CHECK(!control_zero_ok(m2, mn, mx));
    memcpy(m2, mean, sizeof m2); m2[CH_CURRENT] = NAN; CHECK(!control_zero_ok(m2, mn, mx));
    memcpy(m2, mx, sizeof m2); m2[CH_MOTOR_A] = NAN; CHECK(!control_zero_ok(mean, mn, m2));
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
    broken.drive_ok = false;
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
        {"TEST: okablowanie bez napiec", test_test_wiring},
        {"zero pradu: okno", test_zero_window},
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
