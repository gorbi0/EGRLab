/* Testy czystej logiki sterowania, do uruchomienia na PC:
 *   gcc -std=c11 -I firmware/main -o test_control tests/test_control.c firmware/main/control.c -lm
 *   ./test_control
 * W środowisku, w którym powstał pakiet, nie było kompilatora C — te testy
 * są przygotowane, ale NIE zostały uruchomione. Patrz docs/06-weryfikacja.md. */
#include "control.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

static int checks;
#define CHECK(cond) do { checks++; if (!(cond)) { \
    printf("FAIL %s:%d  %s\n", __FILE__, __LINE__, #cond); return 1; } } while (0)

/* Zdrowe wejścia: świeże dane, wszystkie blokady zamknięte, TEST wpięty. */
static inputs_t healthy(uint64_t now) {
    inputs_t in = {0};
    in.now = now; in.sample_time = now;
    in.interlock = true; in.hw_armed = true; in.storage_ok = true;
    in.tc_ok = true; in.t1 = 40; in.t2 = 60;
    in.test_present = true; in.log_present = false;
    in.v[CH_VBAT] = 13.5f;
    in.v[CH_CURRENT] = 2.5f;
    return in;
}
static void set_sensor(inputs_t *in, int s, int g, int f, float ratio) {
    in->v[g] = 0.02f;
    in->v[s] = in->v[g] + 5.0f;
    in->v[f] = in->v[g] + 0.2f + ratio * 4.5f;
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
    /* Same zera: żadna trójka nie spełnia kryteriów. */
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
    CHECK(c.state == IDENTIFY);                 /* jeszcze nie minęły 2 s */
    in = healthy(2200000); set_sensor(&in, 2, 4, 3, .5f);
    control_step(&c, &in);
    CHECK(c.identified && c.state == LOGGER);
    CHECK(c.profile.ch_supply == 2 && c.profile.ch_ground == 4 && c.profile.ch_feedback == 3);
    /* Masa czujnika dostaje najczulszy zakres. */
    CHECK(c.profile.range[4] == RANGE_2V5);
    CHECK(c.profile.range[2] == RANGE_5V && c.profile.range[3] == RANGE_5V);
    CHECK(c.profile.range[CH_MOTOR_A] == RANGE_10V);

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
static int test_ratio_and_position(void) {
    control_t c; control_init(&c);
    c.profile.ch_supply = 2; c.profile.ch_ground = 4; c.profile.ch_feedback = 3;
    inputs_t in = healthy(1000);
    set_sensor(&in, 2, 4, 3, .5f);
    float r = control_ratio(&c, &in);
    CHECK(fabsf(r - (0.2f + 0.5f * 4.5f) / 5.0f) < 1e-4f);
    CHECK(isnan(control_position(&c, &in)));    /* bez LEARN nie ma pozycji */
    /* Ujemny zakres (otwarcie maleje) też musi działać. */
    c.profile.closed = .8f; c.profile.open = .3f; c.profile.learned = true;
    float p = control_position(&c, &in);
    CHECK(isfinite(p));
    CHECK(fabsf(p - (r - .8f) / (.3f - .8f)) < 1e-4f);
    return 0;
}
static int test_current_uses_measured_zero(void) {
    control_t c; control_init(&c);
    c.profile.current_zero[0] = 2.44f; c.profile.current_zero[1] = 2.61f;
    inputs_t in = healthy(1000);
    in.v[CH_CURRENT] = 2.94f;
    c.test_bank = false;
    CHECK(fabsf(control_current(&c, &in) - 2.0f) < 1e-3f);
    c.test_bank = true;
    CHECK(fabsf(control_current(&c, &in) - 1.32f) < 1e-3f);
    return 0;
}
static int test_guards(void) {
    control_t base; control_init(&base);
    base.profile.ch_supply = 2; base.profile.ch_ground = 4; base.profile.ch_feedback = 3;
    base.profile.qualified = true;

    /* Każdy warunek osobno musi wywrócić stan ruchu w FAULT. */
    for (int variant = 0; variant < 6; variant++) {
        control_t c = base;
        c.state = READY; c.test_bank = true;
        inputs_t in = healthy(1000);
        set_sensor(&in, 2, 4, 3, .5f);
        switch (variant) {
        case 0: in.interlock = false; break;
        case 1: in.test_present = false; break;
        case 2: in.log_present = true; break;
        case 3: in.storage_ok = false; break;
        case 4: in.v[CH_VBAT] = 8.0f; break;
        case 5: in.sample_time = 0; in.now = 100000; break;  /* nieświeże dane */
        }
        control_step(&c, &in);
        CHECK(c.state == FAULT);
        CHECK(c.duty == 0.0f);
        CHECK(!c.sensor_on);
    }
    /* Brak sprzętowego ARM blokuje sam ruch, nie sam stan READY. */
    control_t c = base; c.state = READY; c.test_bank = true;
    inputs_t in = healthy(1000); set_sensor(&in, 2, 4, 3, .5f);
    in.hw_armed = false;
    control_step(&c, &in);
    CHECK(c.state == READY);
    c.profile.learned = true; c.profile.closed = .1f; c.profile.open = .9f;
    CHECK(control_command(&c, "goto", .5f, 0, 1000));
    control_step(&c, &in);
    CHECK(c.state == FAULT && !strcmp(c.fault, "HARDWARE_NOT_ARMED"));
    return 0;
}
static int test_friction_records_breakaway(void) {
    control_t c; control_init(&c);
    c.profile.ch_supply = 2; c.profile.ch_ground = 4; c.profile.ch_feedback = 3;
    c.profile.closed = .1f; c.profile.open = .9f; c.profile.learned = true;
    c.profile.qualified = true;
    c.state = READY; c.test_bank = true;
    CHECK(control_command(&c, "friction", 0, 1, 0));
    /* Rampa rośnie o 1 pp co 50 ms; pozycja stoi. */
    for (uint64_t t = 0; t < 400000; t += 50000) {
        inputs_t in = healthy(t);
        set_sensor(&in, 2, 4, 3, .5f);
        control_step(&c, &in);
        CHECK(c.state == FRICTION);
    }
    CHECK(c.duty > 0.05f);
    /* Ruch o 2 % przy prądzie 0,8 A — zapisuje się prąd zerwania. */
    inputs_t moved = healthy(420000);
    set_sensor(&moved, 2, 4, 3, .52f);
    moved.v[CH_CURRENT] = 2.5f + 0.8f * 0.25f;
    control_step(&c, &moved);
    CHECK(fabsf(c.breakaway_current - 0.8f) < 1e-2f);
    CHECK(c.breakaway_duty > 0.0f);
    return 0;
}
static int test_hotsoak_campaign(void) {
    control_t c; control_init(&c);
    c.profile.ch_supply = 2; c.profile.ch_ground = 4; c.profile.ch_feedback = 3;
    c.profile.closed = .1f; c.profile.open = .9f; c.profile.learned = true;
    c.state = READY; c.test_bank = true;
    CHECK(!control_command(&c, "hotsoak", 5, 3, 0));      /* okres poniżej 10 s odrzucony */
    CHECK(control_command(&c, "hotsoak", 180, 3, 0));
    CHECK(c.soak.active && c.soak.left == 3);
    inputs_t in = healthy(1000);
    set_sensor(&in, 2, 4, 3, .5f);
    control_step(&c, &in);
    CHECK(c.state == GOTO);                                /* kampania wydała pierwszy rozkaz */
    /* FAULT w trakcie kasuje kampanię i nie ma automatycznego wznowienia. */
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
    CHECK(c.state == FAULT);                               /* FAULT sam nie ustępuje */
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
    CHECK(!control_command(&c, "goto", .95f, 0, 0));        /* poza 10–90 % */
    CHECK(control_command(&c, "goto", .5f, 0, 0));
    c.state = READY;
    CHECK(!control_command(&c, "cycle", 0, 500, 0));
    CHECK(control_command(&c, "cycle", 0, 20, 0));
    return 0;
}

int main(void) {
    struct { const char *name; int (*fn)(void); } tests[] = {
        {"permutacje pinów", test_permutations},
        {"IDENTIFY: 2 s i timeout", test_identify_needs_two_seconds_and_times_out},
        {"ratio i pozycja", test_ratio_and_position},
        {"prąd z mierzonego zera", test_current_uses_measured_zero},
        {"blokady", test_guards},
        {"FRICTION zapisuje prąd zerwania", test_friction_records_breakaway},
        {"kampania HOT-SOAK", test_hotsoak_campaign},
        {"STOP i wyjście z FAULT", test_stop_and_fault_recovery},
        {"limity rozkazów", test_command_limits},
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
