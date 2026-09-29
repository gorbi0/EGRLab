"""P02 R4 — obliczenia do specyfikacji zasilania z pakietu Li-ion 4S.
Uruchomienie: python src/obliczenia.py  (wynik: obliczenia.json i tabela na ekranie).
Wartości elementów są kandydatami do schematu, nie decyzją wykonawczą.
"""
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]
out = {}

# --- pakiet 4S -----------------------------------------------------------------------------
CELLS, V_FULL, V_NOM, V_EMPTY = 4, 4.20, 3.60, 3.00
out['pakiet'] = {'ogniwa': CELLS, 'V_pelny': CELLS * V_FULL, 'V_nominalny': CELLS * V_NOM, 'V_rozladowany': CELLS * V_EMPTY}
runtime = {}
for mah in (3500, 1500):
    wh = CELLS * V_NOM * mah / 1000
    runtime[f'{mah} mAh'] = {'Wh': round(wh, 1), 'h_przy_3W': round(wh * 0.9 / 3, 1), 'h_przy_6W': round(wh * 0.9 / 6, 1)}
out['czas_pracy'] = runtime

# --- UVLO: LM2903 + TL431 (2,495 V); topologia z P01/P02 R3: dzielnik -> DIV (filtr C) -> R_iso -> CMP,
#     histereza Rh z wyjścia OK podciągniętego do AUX5 = 5 V (LM2936Z-5.0), więc OK przełącza 0 / 5 V.
#     Przełącznik PWR (J14) leży w górnej gałęzi dzielnika: rozwarty = DIV do masy = wyłączone.
VREF, V_AUX = 2.495, 5.0
V_ON, V_OFF = 13.4, 12.4
R_T1, R_B, R_ISO = 1.0e3, 10.0e3, 10.0e3      # R_T1: przy płytce, ogranicza prąd przewodu do przełącznika

def thresholds(R_T, R_H):
    Rs = R_ISO + R_H; k = R_ISO / Rs; G = 1 / R_T + 1 / R_B + 1 / Rs
    on = R_T * VREF * G / (1 - k)                                  # OK = 0 (pakiet za niski)
    off = R_T * ((VREF - V_AUX * k) * G / (1 - k) - V_AUX / Rs)    # OK = AUX5
    return on, off

def solve():
    lo_h, hi_h = 20e3, 50e6
    for _ in range(200):
        R_H = (lo_h * hi_h) ** 0.5
        lo, hi = 1e3, 1e6
        for _ in range(200):
            R_T = (lo + hi) / 2
            if thresholds(R_T, R_H)[0] < V_ON: lo = R_T
            else: hi = R_T
        on, off = thresholds(R_T, R_H)
        if on - off > V_ON - V_OFF: lo_h = R_H
        else: hi_h = R_H
    return R_T, R_H

E96 = [1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30, 1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54,
       1.58, 1.62, 1.65, 1.69, 1.74, 1.78, 1.82, 1.87, 1.91, 1.96, 2.00, 2.05, 2.10, 2.15, 2.21, 2.26, 2.32, 2.37, 2.43,
       2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09, 3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83,
       3.92, 4.02, 4.12, 4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49, 5.62, 5.76, 5.90, 6.04,
       6.19, 6.34, 6.49, 6.65, 6.81, 6.98, 7.15, 7.32, 7.50, 7.68, 7.87, 8.06, 8.25, 8.45, 8.66, 8.87, 9.09, 9.31, 9.53,
       9.76]

def e96(x):
    dec = 10 ** int(f'{x:e}'.split('e')[1])
    return min((m * dec for m in E96 + [10.0]), key=lambda v: abs(v - x))

R_T, R_H = solve()
R_T2 = round(e96(R_T - R_T1)); R_He = round(e96(R_H))
von, voff = thresholds(R_T1 + R_T2, R_He)
# rozrzut najgorszy: TL431B ±0,5 %, rezystory 1 % (przybliżenie: suma względnych)
spread_on = von * (0.005 + 2 * 0.01)
out['uvlo'] = {'topologia': 'jak P02 R3/P01: DIV -> R_iso -> CMP, Rh z OK (0/5 V, AUX5)', 'R_T1_przy_plytce': R_T1,
               'R_T2_E96': R_T2, 'R_B': R_B, 'R_iso': R_ISO, 'Rh_E96': R_He, 'R_T_obl': round(R_T), 'Rh_obl': round(R_H),
               'V_on': round(von, 2), 'V_off': round(voff, 2), 'V_on_na_ogniwo': round(von / CELLS, 3),
               'V_off_na_ogniwo': round(voff / CELLS, 3), 'rozrzut_V': round(spread_on, 2),
               'prad_dzielnika_mA_przy_16V8': round(16.8 / (R_T1 + R_T2 + R_B) * 1000, 3),
               'ogniwo_odwrocone_V': round((CELLS - 2) * V_NOM, 1), 'pakiet_3S_pelny_V': round(3 * V_FULL, 1)}

# --- podtrzymanie 2200 uF za diodami (tor ładowania R_ch + D_ch, wyjście przez D1b) --------------
VF = 0.45            # spadek Schottky przy ok. 0,5 A
V_MIN = 7.0          # VLOG minimalne dla TSR 2-2450 (6,5 V) z zapasem na F2/F3, jak w R3
C_SW = 220e-6        # limit pojemności za tranzystorem (P01: 220 uF, ok. 32 mJ przy 17 V)
hold = {}
for cn, C in (('2200 uF nominalnie', 2200e-6), ('2200 uF -20 %', 1760e-6)):
    for start_name, vstart in (('od progu UVLO (PFAIL_N)', voff), ('od pełnego pakietu', CELLS * V_FULL)):
        v0 = vstart - VF
        E = 0.5 * C * (v0 ** 2 - V_MIN ** 2)
        hold[f'{cn}, {start_name}'] = {'V_start': round(v0, 2), 'E_J': round(E, 3),
                                        'ms_przy_3W': round(E / 3 * 1000, 1), 'ms_przy_6W': round(E / 6 * 1000, 1)}
out['podtrzymanie'] = hold

R_CH = 22.0
out['ladowanie_C_H'] = {'R_ch_ohm': R_CH, 'tau_ms': round(R_CH * 2200e-6 * 1000, 1),
                        'prad_szczytowy_A': round(CELLS * V_FULL / R_CH, 2),
                        'energia_w_R_ch_J': round(0.5 * 2200e-6 * (CELLS * V_FULL) ** 2, 3),
                        'czas_do_95proc_ms': round(3 * R_CH * 2200e-6 * 1000, 0)}
out['zalaczenie_tranzystora'] = {'C_VSW_max_uF': C_SW * 1e6, 'energia_ladowania_mJ': round(0.5 * C_SW * (CELLS * V_FULL) ** 2 * 1000, 1),
                                 'uwaga': 'limit jak w P01 (220 uF, ok. 32 mJ przy 17 V); C_H ładowany osobno przez R_ch'}

# --- straty ---------------------------------------------------------------------------------
RDS_HOT, RTH_JA = 0.030, 62.0      # SUP53P06-20: 20 mOhm przy VGS -10 V, na gorąco ok. 30 mOhm; TO-220 bez radiatora
loss = {}
for I in (0.5, 3.5, 4.5, 5.0):
    P = I ** 2 * RDS_HOT
    loss[f'{I} A'] = {'P_Q1_W': round(P, 2), 'przyrost_K_bez_radiatora': round(P * RTH_JA, 0),
                      'Tj_przy_50C': round(50 + P * RTH_JA, 0)}
out['straty_Q1'] = loss
out['straty_uwaga'] = 'wartości na jeden tranzystor; w torze są dwa SUP53P06 szeregowo (Q_REV i Q_SW), każdy osobno bez radiatora'
I_LOG = 6.0 / 0.9 / (voff - VF)
out['straty_D1'] = {'I_logika_max_A': round(I_LOG, 2), 'P_W': round(I_LOG * VF, 2)}

# --- VBAT auta na CH7 P05 -------------------------------------------------------------------
R_TOP, R_BOT, R_ADC, R_SER = 499e3, 100e3, 5e6, 10e3
rb = R_BOT * R_ADC / (R_BOT + R_ADC)
m0 = (R_TOP + rb) / rb
m1 = (R_TOP + R_SER + rb) / rb
VC_TVS = 33.2                      # P6KE24CA, napięcie ograniczania katalogowe
out['vbat_ch7'] = {'mnoznik_P05': round(m0, 4), 'mnoznik_z_10k': round(m1, 4), 'zmiana_proc': round((m1 / m0 - 1) * 100, 2),
                   'zakres_V': round(10 * m1, 1), 'ADC_przy_ograniczeniu_TVS_V': round(VC_TVS / m1, 2)}

(R/'obliczenia.json').write_text(json.dumps(out, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
print(json.dumps(out, indent=1, ensure_ascii=False))
