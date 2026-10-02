#pragma once
#include <stdbool.h>
#include <stdint.h>

/* 6.2-s1 (F-08, P10 R2 docs/INTEGRACJA.md): RPM z odpowiedzi OBD-II Mode 01 PID 0C, ECU 0x7E8..0x7EF,
 * ISO-TP Single Frame. Czysta logika bez ESP-IDF; testy hosta w tests/test_obd.c.
 * P10 tylko slucha (listen-only): odpowiedz pojawia sie, gdy pyta inny tester. Brak danych to brak
 * liczby (NAN), nigdy 0 rpm. Jeden ECU na sesje: pierwszy odpowiadajacy, a 0x7E8 (silnik) wypiera
 * pozniej kazdy inny (nizszy identyfikator wygrywa). */
#define OBD_PROFILE "obd2_m01_pid0c_sf_7e8_7ef"
#define OBD_RPM_STALE_US 1000000u

typedef enum { OBD_NOT_RPM = 0, OBD_RPM_OK, OBD_BAD_LENGTH, OBD_OTHER_ECU } obd_result_t;

typedef struct {
    uint32_t ecu;          /* wybrany ECU (0 = jeszcze zaden) */
    uint64_t last_us;      /* czas ostatniego waznego RPM */
    float rpm;             /* ostatni wazny RPM */
    uint32_t accepted, bad_length, other_ecu, ecu_changes;
    bool stale_reported;   /* zdarzenie rpm_stale juz zapisane dla tej przerwy */
} obd_rpm_t;

void obd_rpm_init(obd_rpm_t *s);
/* Klasyfikuje ramke; przy OBD_RPM_OK zwraca rpm (inaczej NAN). */
obd_result_t obd_rpm_frame(obd_rpm_t *s, uint32_t id, bool ext, bool rtr, uint8_t dlc,
                           const uint8_t data[8], uint64_t now_us, float *rpm);
/* Ostatni RPM albo NAN: brak odpowiedzi albo odpowiedz starsza niz OBD_RPM_STALE_US. */
float obd_rpm_now(const obd_rpm_t *s, uint64_t now_us);
