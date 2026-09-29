#pragma once
#include <stdbool.h>
#include <stdint.h>

/* Czysta logika: bez ESP-IDF, testowalna na PC (tests/test_control.c). */

#define EGR_PROFILE_MAGIC 0x32524745u /* "EGR2" */
#define EGR_PROFILE_VERSION 2

/* Kanały ADC w v[]: 0 = pin1, 1 = pin3, 2 = pin4, 3 = pin5, 4 = pin6,
 * 5 = prąd aktywnego banku, 6 = VBAT, 7 = AUX.
 * Które z 2/3/4 jest zasilaniem, masą i sygnałem — ustala IDENTIFY. */
#define CH_MOTOR_A 0
#define CH_MOTOR_B 1
#define CH_SENSOR_FIRST 2
#define CH_CURRENT 5
#define CH_VBAT 6
#define CH_AUX 7

/* Kody zakresu AD7606B; FS w control_full_scale(). */
#define RANGE_2V5 0
#define RANGE_5V  1
#define RANGE_10V 2

typedef enum { SAFE, LOGGER, IDENTIFY, SENSOR_CHECK, READY, MANUAL,
               GOTO, SWEEP, FRICTION, CYCLE, THERMAL, FAULT } state_t;

typedef struct {
    uint32_t magic;
    uint16_t version, reserved;
    int8_t ch_supply, ch_ground, ch_feedback, opening_sign;
    float closed, open;
    float max_duty, current_limit, temp_limit;
    /* Osobna kalibracja na bank: [0] = LOGGER, [1] = TEST. Rezystory
     * ograniczające siedzą przy złączach adapterów, więc tory są różne. */
    float gain[2][8], offset[2][8], current_zero[2];
    uint8_t range[8];
    bool qualified, learned;
    char valve[24], adapter[24];
} profile_t;

typedef struct {
    uint64_t now, sample_time;
    float v[8], t1, t2;
    bool interlock, hw_armed, storage_ok, sensor_fault, tc_ok;
    bool log_present, test_present;
} inputs_t;

/* Kampania HOT-SOAK: powtarzane serie pomiarowe na stygnącym silniku. */
typedef struct {
    bool active, point_ready;
    uint64_t period, next_at;
    int left, step, done;
    float i_break_open, i_break_close, ms_open, ms_close, t1, t2, vbat;
} campaign_t;

typedef struct {
    state_t state;
    profile_t profile;
    campaign_t soak;
    uint64_t started, deadline, stable_since, dwell_since;
    uint64_t identify_since, identify_deadline, move_started;
    float duty, target, start_position, manual_duty;
    float breakaway_current, breakaway_duty, move_ms;
    int index, cycles, cycle_done, friction_sign, identify_candidate;
    bool test_bank, sensor_on, identified, thermal;
    const char *fault;
} control_t;

void control_init(control_t *c);
void control_stop(control_t *c);
bool control_command(control_t *c, const char *cmd, float a, int b, uint64_t now);
void control_step(control_t *c, const inputs_t *in);
float control_ratio(const control_t *c, const inputs_t *in);
float control_position(const control_t *c, const inputs_t *in);
float control_current(const control_t *c, const inputs_t *in);
float control_full_scale(uint8_t range);
bool control_moving(const control_t *c);
const char *control_name(state_t state);
/* Zwraca numer permutacji 0..5 albo -1; wypełnia {supply, ground, feedback}. */
int control_permutation(const inputs_t *in, int8_t out[3]);
/* Ustawia zakresy ADC z mapowania kanałów: masa czujnika dostaje ±2,5 V. */
void control_apply_ranges(profile_t *p);
