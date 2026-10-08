#pragma once
#include <stdbool.h>
#include <stdint.h>

/* Czysta logika: bez ESP-IDF, testowalna na PC (tests/test_control.c). */

#define EGR_PROFILE_MAGIC 0x36524745u /* "EGR6" */
/* 6.3-m1 (M-13): wersja 7 - profil z NVS wersji 6 (6.1 / 6.2-s1, kalibracja innego sprzetu) jest odrzucany. */
#define EGR_PROFILE_VERSION 7

/* Kanały ADC w v[] (6.3-m1, M-03/M-04, Plytki/M1-R1-review/docs/parts.json):
 * 0 = CH1 P1_EGR, 1 = CH2 P3 (300k/100k), 2..4 = CH3..CH5 P4/P5/P6 (100k szeregowo),
 * 5 = CH6 prąd silnika (INA240A2 x50, bocznik 5 mOhm, U = VS/2 + 0,25 V/A, 1k/1n) - ten sam tor w LOGGER i TEST,
 * 6 = CH7 VBAT_CAR (499k/100k), 7 = CH8 SENS_5V (100k szeregowo; wyjście TPS2553).
 * Wejście AD7606B 5 MOhm: nominalnie 4,06 / 1,02 / 1,0002 / 6,0898 (control_init).
 * CH7 to akumulator auta, nie pakiet 4S (warunek 9-16,5 V w control.c).
 * Które z 2/3/4 jest zasilaniem, masą i sygnałem — ustala IDENTIFY. */
#define CH_MOTOR_A 0
#define CH_MOTOR_B 1
#define CH_SENSOR_FIRST 2
#define CH_CURRENT 5
#define CH_VBAT 6
#define CH_SENS5V 7

/* Kody zakresu AD7606B; wartość FS w control_full_scale(). */
#define RANGE_2V5 0
#define RANGE_5V  1
#define RANGE_10V 2
#define RANGE_UNKNOWN 255

/* 6.3-m1: M1 nie ma zworki JP_AUX ani kanału AUX (CH8 = SENS_5V). Pola aux_* profilu zostają w strukturze
 * (zgodność układu), ale firmware ich nie używa. */
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
    /* 6.3-m1 (M-01): bez interlock / hw_armed / log_present / test_present - M1 nie ma P04 SAFE ani
     * detekcji adapterów; tryb LOGGER / TESTER to przepięcie przewodów na listwie X1 (D-M1-7). */
    bool storage_ok, sensor_fault, tc_ok, io_stale;
    bool adc_ok;      /* konfiguracja przetwornika potwierdzona odczytem */
    bool drive_ok;    /* M-06: false = zadziałało programowe ograniczenie prądu (zatrzask do następnej konfiguracji) */
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
/* Timestamp and cached input values must come from the same protected snapshot. */
void control_guard_io(inputs_t *in, uint64_t inputs_time);
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

/* 6.3-m1: warunki wejścia w TEST bez detekcji adaptera - zwraca NULL albo powód odmowy.
 * Linie silnika i czujnika muszą być bez napięcia (ECU odpięte albo bez zapłonu), SENS_5V wyłączone. */
const char *control_test_wiring(const inputs_t *in);
/* 6.3-m1 (M-04): okno zera prądu - CH6 stabilne w 1..4 V, linie silnika bez napięcia (mostek i ECU nie sterują). */
bool control_zero_ok(const float mean[8], const float min[8], const float max[8]);

bool profile_valid(const profile_t *p);
bool profile_command(profile_t *p, const char *line);
