#pragma once
#include <stdbool.h>
#include <stdint.h>

typedef enum { SAFE, LOGGER, IDENTIFY, SENSOR_CHECK, READY, MANUAL,
               GOTO, SWEEP, FRICTION, CYCLE, THERMAL, FAULT } state_t;
typedef struct {
    uint32_t magic;
    int32_t supply_pin, opening_sign;
    float closed, open, max_duty, current_limit, temp_limit;
    float gain[8], offset[8];
    bool qualified, learned;
    char valve[32], adapter[32];
} profile_t;
typedef struct {
    uint64_t now, sample_time;
    float v[8], t1, t2;
    bool interlock, hw_armed, storage_ok, sensor_fault, tc_ok;
} inputs_t;
typedef struct {
    state_t state;
    profile_t profile;
    uint64_t started, deadline, stable_since, dwell_since;
    uint64_t identify_since, last_direction_change;
    float duty, target, start_position, manual_duty;
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
bool control_moving(const control_t *c);
const char *control_name(state_t state);
