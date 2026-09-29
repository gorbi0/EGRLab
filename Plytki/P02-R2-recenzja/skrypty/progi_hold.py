"""Niezależny rachunek progów HOLD_READY P02-R2 (recenzja Claude, 26.09.2026).
Wartości elementów czytane z eksportu netlisty (verification/P02.xml kopii roboczej), nie z parts.py.
Model: VS -- Rt -- X -- Rs -- Y(+) ; X -- Rb || C -- GND ; Y -- Rf -- OUT ; OUT -- Rp -- VIO ; (-) = Vt.
Na progu Y = Vt:  VS = A*Vt + S*((Vt - Vout)/Rf + Iin),  A = 1 + Rt/Rb,  S = A*Rs + Rt,
Iin = prąd wpływający do wejścia (+) (LM2903 z wejściem PNP: prąd wypływa, więc Iin <= 0).
Wzrost: wyjście L (Vout = VOL). Spadek: wyjście H, VOH = (VIO/Rp + Vt/Rf - Ileak) / (1/Rp + 1/Rf).
Tolerancje jak w deklaracji Astry (HOLD-ANALIZA.md), żeby sprawdzić jej liczby; wynik wypisany obok jej obwiedni.
"""
import itertools, math, json, re, sys
import xml.etree.ElementTree as ET
from pathlib import Path

W = Path(__file__).resolve().parents[1] / 'work'
root = ET.parse(W / 'verification/P02.xml').getroot()
val = {c.get('ref'): c.findtext('value') for c in root.findall('./components/comp')}


def ohm(ref):
    v = val[ref].split('/')[0].strip().upper().replace('R', '.') if not val[ref].upper().startswith('0R') else '0'
    m = re.match(r'([0-9.]+)([KM]?)([0-9]*)', val[ref].split('/')[0].strip().upper().replace('R', ''))
    s = val[ref].split('/')[0].strip().upper()
    for u, mul in (('K', 1e3), ('M', 1e6)):
        if u in s:
            a, b = s.split(u); return float(a + '.' + (b or '0')) * mul
    return float(s.replace('R', ''))


def thresholds(Rt, Rb, Rs, Rf, Rp, Vt, VIO, VOL, Iin, Ileak):
    A = 1 + Rt / Rb; S = A * Rs + Rt
    VOH = (VIO / Rp + Vt / Rf - Ileak) / (1 / Rp + 1 / Rf)
    up = A * Vt + S * ((Vt - VOL) / Rf + Iin)
    dn = A * Vt + S * ((Vt - VOH) / Rf + Iin)
    return up, dn


tracks = {'BANK': ('R6', 'R7', 'R18', 'R8', 'R12'), 'VPROT': ('R9', 'R10', 'R19', 'R11', 'R13')}
out = {'values': {r: val[r] for t in tracks.values() for r in t}}
dT = 25  # K od 25 °C do 0 lub 50 °C
for name, refs in tracks.items():
    Rt, Rb, Rs, Rf, Rp = (ohm(r) for r in refs)
    nom = thresholds(Rt, Rb, Rs, Rf, Rp, 2.495, 3.3, 0.15, 0.0, 0.0)
    tol_div = 0.001 + 25e-6 * dT   # 0,1 % + 25 ppm/K
    tol_1 = 0.01 + 100e-6 * dT     # 1 % + 100 ppm/K
    corners = []
    for sRt, sRb, sRs, sRf, sRp, vt, vio, vol, iin, ilk in itertools.product(
            (-1, 1), (-1, 1), (-1, 1), (-1, 1), (-1, 1),
            (2.483 - 0.034 - 0.004 - 0.015, 2.507 + 0.034 + 0.004 + 0.015),  # TL431B + dryft + IKA + Vos LM2903
            (3.135, 3.465), (0.0, 0.7), (-500e-9, 0.0), (0.0, 1e-6)):
        corners.append(thresholds(Rt * (1 + sRt * tol_div), Rb * (1 + sRb * tol_div), Rs * (1 + sRs * tol_1),
                                  Rf * (1 + sRf * tol_1), Rp * (1 + sRp * tol_1), vt, vio, vol, iin, ilk))
    ups = [c[0] for c in corners]; dns = [c[1] for c in corners]; hyst = [c[0] - c[1] for c in corners]
    out[name] = {'nominal_rise_V': round(nom[0], 3), 'nominal_fall_V': round(nom[1], 3),
                 'rise_envelope_V': [round(min(ups), 3), round(max(ups), 3)], 'fall_envelope_V': [round(min(dns), 3), round(max(dns), 3)],
                 'min_hysteresis_mV': round(1000 * min(hyst), 1), 'corners': len(corners)}

# --- osiągalność progów i czasy ---
C_nom, C_max, C_min = 0.066, 0.066 * 1.2, 0.0528
R17 = 47.0; R1 = 4700.0; Rdiv = ohm('R6') + ohm('R7')
Rleak = 1 / (1 / R1 + 1 / Rdiv)


def bank_final(vprot, vd=0.35):
    """Ustalone napięcie banku przy ładowaniu przez R17 + D2, obciążenie R1 || dzielnik."""
    v = vprot - vd
    return v * Rleak / (Rleak + R17)


reach = {}
for vprot in (11.8, 12.2, 12.4, 12.6, 13.5, 14.2):
    vb = bank_final(vprot)
    tau = R17 * 1.05 * C_max
    t_bank = tau * math.log(vb / (vb - out['BANK']['rise_envelope_V'][1])) if vb > out['BANK']['rise_envelope_V'][1] else None
    reach[str(vprot)] = {'bank_final_V': round(vb, 2),
                         'bank_worst_rise_reached_s_(C+20%,R17+5%)': round(t_bank, 1) if t_bank else 'nigdy',
                         'VPROT_OK_nominal_unit': vprot >= out['VPROT']['nominal_rise_V'],
                         'VPROT_OK_worst_unit': vprot >= out['VPROT']['rise_envelope_V'][1],
                         'VPROT_OK_best_unit': vprot >= out['VPROT']['rise_envelope_V'][0]}
out['reachability_by_VPROT'] = reach
# przerwany F1: bank odcięty od ładowania, rozładowuje go R1 || dzielnik R6+R7
for v0 in (12.5, 13.5):
    tau = Rleak * C_nom
    out[f'F1_open_LED_off_after_s_from_{v0}V'] = {k: round(tau * math.log(v0 / thr), 0) for k, thr in
                                                   (('nominal_fall', out['BANK']['nominal_fall_V']), ('highest_fall', out['BANK']['fall_envelope_V'][1]))}
# podtrzymanie od najniższego progu wyłączenia BANK_OK (a nie od 9,5 V)
v0 = out['BANK']['fall_envelope_V'][0]
out['hold_ms_from_BANK_OK_min_fall'] = round(1000 * C_min * ((v0 - 1.2) ** 2 - 7 ** 2) / (2 * 6.15), 1)
out['hold_ms_from_9V5'] = round(1000 * C_min * ((9.5 - 1.2) ** 2 - 7 ** 2) / (2 * 6.15), 1)
# LED
for vf in (1.9, 2.1):
    out[f'LED_mA_at_Vf_{vf}'] = round((3.3 - 0.15 - vf) / ohm('R16') * 1000, 2)
# TP3 i energia
out['TP3_short_mA_32V'] = round(32 / (1000 * 0.95) * 1000, 2)
out['bank_energy_J_nominal_32V'] = round(0.5 * C_nom * 32 ** 2, 2)
out['bank_energy_J_C+20%_32V'] = round(0.5 * C_max * 32 ** 2, 2)
out['bleeder_to_1V_s_R1_only_slowest'] = round(R1 * 1.01 * C_max * math.log(32), 0)
out['bleeder_to_1V_s_with_divider'] = round(Rleak * C_max * math.log(32), 0)
print(json.dumps(out, indent=1, ensure_ascii=False))
(Path(__file__).with_suffix('.json')).write_text(json.dumps(out, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
