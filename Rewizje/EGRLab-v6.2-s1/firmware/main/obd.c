#include "obd.h"
#include <math.h>
#include <string.h>

void obd_rpm_init(obd_rpm_t *s) { memset(s, 0, sizeof *s); s->rpm = NAN; }

obd_result_t obd_rpm_frame(obd_rpm_t *s, uint32_t id, bool ext, bool rtr, uint8_t dlc,
                           const uint8_t data[8], uint64_t now_us, float *rpm) {
    if (rpm) *rpm = NAN;
    if (ext || rtr || id < 0x7e8 || id > 0x7ef || dlc < 3 || dlc > 8) return OBD_NOT_RPM;
    if ((data[0] & 0xf0) != 0) return OBD_NOT_RPM;              /* nie Single Frame (FF / CF / FC) */
    if (data[1] != 0x41 || data[2] != 0x0c) return OBD_NOT_RPM; /* inna usluga albo PID */
    unsigned len = data[0] & 0x0f;                              /* 41 0C A B [kolejne PID-y] */
    if (len < 4 || 1u + len > dlc) { s->bad_length++; return OBD_BAD_LENGTH; }
    if (s->ecu && id != s->ecu) {
        if (id > s->ecu) { s->other_ecu++; return OBD_OTHER_ECU; }
        s->ecu_changes++;                                       /* nizszy identyfikator (0x7E8 silnik) wygrywa */
    }
    s->ecu = id;
    float r = ((unsigned)data[3] * 256u + data[4]) / 4.0f;
    s->rpm = r; s->last_us = now_us; s->accepted++; s->stale_reported = false;
    if (rpm) *rpm = r;
    return OBD_RPM_OK;
}

float obd_rpm_now(const obd_rpm_t *s, uint64_t now_us) {
    if (!s->accepted || now_us < s->last_us || now_us - s->last_us > OBD_RPM_STALE_US) return NAN;
    return s->rpm;
}
