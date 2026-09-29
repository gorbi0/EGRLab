"""Niezależne punkty pracy P00-R2 (recenzja Claude, 27.09.2026).

Czyta natywną netlistę P00 (eksport kicad-cli) i netlistę P04-R2.1 (docs/parts.json), nie korzysta z verify_electrical.py.
Arytmetyka DC z jawnymi założeniami; to nie symulacja ani pomiar.
Źródła liczb:
  TLC555: TI SLFS043K (rev. 01.2026) - VOH min 1,5 V przy VDD 2 V / IOH -300 uA, typ 1,9 V;
          VOH min 4,1 V przy VDD 5 V / IOH -1 mA, typ 4,8 V; IDD max 500 uA przy 5 V (TLC555C, pełny zakres).
  74LVC125A: VIH 2,0 V dla VCC 2,7..3,6 V (karta Nexperia). 74HC08 przy 3,3 V: ok. 2,36 V (interpolacja tabel TI, jak w P04-R2.1).
  LM2937-3.3 (SNVS015F wg cytatów Astry, niezweryfikowane lokalnie): VIN >= 4,75 V, IOUT >= 5 mA, RthJA 77,9 K/W, IG budżet 20 mA.
  Diody LED przy ok. 1 mA: VF 1,6..2,1 V - założenie (karty Kingbright podają VF przy 20 mA).
"""
from pathlib import Path
import json, re, sys, xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
NET = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / 'work/verification/P00.xml'
P04 = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE.parents[1] / 'P04-R2.1-review/docs/parts.json'


def val(v):
    t = v.split('/')[0].strip().upper()
    m = re.fullmatch(r'(\d+)([RKM]?)(\d*)', t)
    return float(m[1] + ('.' + m[3] if m[3] else '')) * {'': 1, 'R': 1, 'K': 1e3, 'M': 1e6}[m[2]]


root = ET.parse(NET).getroot()
V = {c.get('ref'): c.findtext('value') for c in root.findall('./components/comp')}
PIN = {n.get('ref') + '.' + n.get('pin'): net.get('name').lstrip('/') for net in root.findall('./nets/net') for n in net.findall('node')}
p04 = json.loads(P04.read_text(encoding='utf-8'))
p04 = p04 if isinstance(p04, dict) else {x['ref']: x for x in p04}

V33 = (3.14, 3.46)                      # LM2937-3.3 over temperature
TOL, TCR, DT = 0.01, 100e-6, 15         # 1 %, 100 ppm/K, |10..40 C - 25 C|
RMIN, RMAX = (1 - TOL) * (1 - TCR * DT), (1 + TOL) * (1 + TCR * DT)
VF_MIN, VF_MAX = 1.6, 2.1
out = {}

# 1. zasilanie
out['U2_VIN_przy_J10_6V_i_D1_0V6'] = 6.0 - 0.6
r5, rl10 = val(V['R5']), val(V['RL10'])
i_min_noU1 = V33[0] / (r5 * RMAX) + (V33[0] - VF_MAX) / (rl10 * RMAX)
out['IOUT_min_bez_U1_mA'] = i_min_noU1 * 1e3
out['IOUT_min_R5_sam_mA'] = V33[0] / (r5 * RMAX) * 1e3


def led(r, vmax=V33[1]):
    return (vmax - VF_MIN) / (val(V[r]) * RMIN)


chan = [f'RS{i}' for i in range(1, 9)]
worst = {
    'R5': V33[1] / (r5 * RMIN), 'LED10': led('RL10'), 'LED1-8': sum(led(f'RL{i}') for i in range(1, 9)),
    'zwarcia J1-J8': sum(V33[1] / (val(V[r]) * RMIN) for r in chan),
    'U1 IDD': 0.5e-3,
    # wyjscie 555 w H (DIS wyłączony): LED9 + zwarcie J9; w L płynie tylko R1 -> DIS (mniej)
    'U1 wyjscie H: LED9 + zwarcie J9': led('RL9') + V33[1] / (val(V['R3']) * RMIN),
    'R4 (STOP)': V33[1] / (val(V['R4']) * RMIN),
}
out['IOUT_max_skladniki_mA'] = {k: round(v * 1e3, 2) for k, v in worst.items()}
out['IOUT_max_mA'] = sum(worst.values()) * 1e3
# typowo z P04: kanały H na 10 k (KEY/MECH 12 k), LED zielone świecą, HB pracuje
typ = 3.3 / r5 + (3.3 - 1.9) / rl10 + 8 * (3.3 - 1.9) / 1e3 + 6 * 3.3 / 11e3 + 2 * 3.3 / 12e3 + 0.2e-3 + 0.52 * ((3.3 - 1.9) / 1e3 + 3.0 / 11e3) + 0.48 * 3.3 / 4.7e3
out['IOUT_typ_z_P04_mA'] = typ * 1e3


def pd(vin, iout, ig=0.020):
    return (vin - V33[0]) * iout + vin * ig


out['U2_PD_W_i_TJ_C_przy_TA40_RthJA77.9'] = {
    f'{vin} V': {'max': [round(pd(vin, out['IOUT_max_mA'] / 1e3), 3), round(40 + 77.9 * pd(vin, out['IOUT_max_mA'] / 1e3), 1)],
                 'typ_P04': [round(pd(vin, typ), 3), round(40 + 77.9 * pd(vin, typ), 1)]} for vin in (6, 9, 12, 15)}
out['budzet_R2_65mA_pokrywa_max'] = 65 > out['IOUT_max_mA']

# 2. kanały -> wejścia P04-R2.1
def pins(net):
    return sorted(f'{r}.{k}' for r, x in p04.items() for k, v in (x.get('pins') or {}).items() if v == net)


def h(src, rs, rpd):
    return src * rpd / (rs + rpd)


lo = V33[0]
out['kanal_H_na_wejsciu_LVC_min_V'] = h(lo, 1e3 * RMAX, 10e3 * RMIN)
out['kanal_H_KEY_MECH_na_bramce_HC08_min_V'] = h(lo, 2e3 * RMAX, 10e3 * RMIN)
out['H_SUP_na_SUP_N_100k_min_V'] = h(lo, 1e3 * RMAX, 100e3 * RMIN)
out['progi'] = {'LVC125A_VIH': 2.0, 'HC08_VIH_3V3_interp': 2.36}
out['P04_obciazenia'] = {n: pins(n) for n in ('HEARTBEAT', 'TEST_KEY_P04', 'MECH_OK_P04', 'SUP_N')}

# 3. heartbeat: wyjście TLC555 jako VDD - Ro * I; obciążenie LED9 (RL9 + VF) i J9 (R3 + 10 k P04)
def hb(vdd, ro, rl9=val(V['RL9']), vf=VF_MIN, r3=val(V['R3']), rpd=10e3):
    # Vout = vdd - ro*((Vout - vf)/rl9 + Vout/(r3 + rpd))
    vout = (vdd + ro * vf / rl9) / (1 + ro / rl9 + ro / (r3 + rpd))
    return vout, vout * rpd / (r3 + rpd), (vout - vf) / rl9


ro = {'typ (5 V: 0,2 k)': 200, 'typ (2 V: 0,33 k)': 333, 'min VOH przy 5 V (0,9 k)': 900, 'min VOH przy 2 V (1,67 k)': 1667}
out['HB_H_na_wejsciu_P04_V'] = {k: {f'VDD {v}': round(hb(v, r)[1], 3) for v in V33} for k, r in ro.items()}
out['HB_H_RL9_2k2_pesymistycznie_V'] = round(hb(V33[0], 1667, rl9=2200)[1], 3)
out['LED9_prad_typ_mA'] = round(hb(3.3, 270, vf=1.9)[2] * 1e3, 2)

print(json.dumps(out, indent=2, ensure_ascii=False))
(HERE / 'punkty_pracy.json').write_text(json.dumps(out, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
