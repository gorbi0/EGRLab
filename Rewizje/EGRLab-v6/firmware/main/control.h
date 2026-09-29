#pragma once
#include <stdbool.h>
#include <stdint.h>

/* Czysta logika: bez ESP-IDF, testowalna na PC (tests/test_control.c). */

#define EGR_PROFILE_MAGIC 0x36524745u /* "EGR6" */
#define EGR_PROFILE_VERSION 6

/* Kanały ADC w v[]: 0 = pin1, 1 = pin3, 2 = pin4, 3 = pin5, 4 = pin6,
 * 5 = prąd aktywnego banku, 6 = VBAT, 7 = AUX.
 * Które z 2/3/4 jest zasilaniem, masą i sygnałem — ustala IDENTIFY. */
#define CH_MOTOR_A 0
#define CH_MOTOR_B 1
#define CH_SENSOR_FIRST 2
#define CH_CURRENT 5
#define CH_VBAT 6
#define CH_AUX 7

/* Kody zakresu AD7606B; wartość FS w control_full_scale(). */
#define RANGE_2V5 0
#define RANGE_5V  1
#define RANGE_10V 2
#define RANGE_UNKNOWN 255

/* Pozycja zworki JP_AUX. Kalibracja jest osobna dla każdej pozycji, bo to
 * dwa różne dzielniki, a nie jeden dzielnik z przełączanym zakresem. */
#define AUX_HI 0
#define AUX_LO 1

typedef enum { SAFE, LOGGER, IDENTIFY, SENSOR_CHECK, READY, MANUAL,
               GOTO, SWEEP, FRICTION, CYCLE, THERMAL, FAULT } state_t;

typedef struct {
    uint32_t magic;
    uint16_t version, reserved;
    int8_t ch_supply, ch_ground, ch_feedback, opening_sign;
    float closed, open;
    float max_duty, current_limit, temp_limit;
    /* Osobna kalibracja na bank: [0] = LOGGER, [1] = TEST. Rezystory
     * ograniczające siedzą przy złączach adapterów, więc tory są różne.
     * Kanał AUX ma dodatkowo osobną kalibrację na pozycję zworki. */
    float gain[2][8], offset[2][8], current_zero[2];
    float aux_gain[2], aux_offset[2];
    uint8_t aux_position;
    /* Zakresy ŻĄDANE. Zakresy faktycznie zastosowane przez sprzęt trzyma
     * session_config_t — i tylko one wolno użyć do przeliczeń. */
    uint8_t range[8];
    bool qualified, learned;
    bool current_window_qualified; /* bench acceptance of 20 ms sampled-current metric */
    /* Prąd banku LOGGER jest nieważny, gdy adapter ma założony mostek
     * bocznikujący albo gdy pracujesz sondami back-probe (wariant L2). */
    bool current_valid[2];
    char valve[24], adapter[24];
    /* Per physical current module. IDs are deliberately entered by the operator. */
    char current_module[2][24];
    float current_volts_per_amp[2], current_adc_gain[2], current_adc_offset[2];
    bool current_calibrated[2];
    char vehicle_id[24], session_note[24];
    char daq_module[24];
    bool voltage_calibrated[2];
} profile_t;

/* Migawka konfiguracji, z którą powstała dana próbka. Każdy rekord w pliku
 * niesie jej `id`, więc analiza offline stosuje dokładnie tę kalibrację,
 * która obowiązywała w tej chwili — a nie ostatnią z sesji. */
typedef struct {
    uint16_t id;
    int8_t ch_supply, ch_ground, ch_feedback, bank;
    uint8_t range[8];
    float gain[8], offset[8];
    float current_zero, closed, open;
    float current_volts_per_amp, current_adc_gain, current_adc_offset;
    char current_module[24], valve[24], adapter[24], vehicle_id[24], session_note[24];
    bool local_current, current_calibrated;
    char daq_module[24];
    bool voltage_calibrated;
    int8_t opening_sign;
    uint8_t aux_position;
    bool learned, current_valid, adc_software_mode, adc_config_ok;
    bool current_window_qualified;
} session_config_t;

typedef struct {
    uint64_t now, sample_time;
    float v[8], t1, t2;
    float current_mean, current_rms;
    bool current_window_valid;
    uint16_t config_id;
    uint8_t saturation_mask;
    bool interlock, hw_armed, storage_ok, sensor_fault, tc_ok;
    bool log_present, test_present;
    bool adc_ok;      /* konfiguracja przetwornika potwierdzona odczytem */
    bool drive_ok;    /* ostatnie sterowanie kierunkiem potwierdzone sprzętowo */
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
/* Ustawia ŻĄDANE zakresy z mapowania kanałów. W hardware mode wszystkie
 * kanały zostają na ±10 V, bo sprzęt nie potrafi inaczej. */
void control_apply_ranges(profile_t *p, bool software_mode);
/* Buduje migawkę konfiguracji dla aktywnego banku i pozycji zworki AUX. */
void control_build_config(const control_t *c, session_config_t *out, uint16_t id,
                          const uint8_t applied_range[8], bool software_mode, bool config_ok);

bool profile_valid(const profile_t *p);
bool profile_command(profile_t *p, const char *line);
