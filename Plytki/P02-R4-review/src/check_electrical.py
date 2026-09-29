"""P02 R4 electrical review checks on the exported KiCad netlist (verification/P02.xml) and docs/parts.json.
Analytic models only (declared assumptions below); no transistor-level simulation, no bench result is claimed.
  python src/check_electrical.py [--negative]
--negative applies deliberate value/topology mutations (plus a null control) and requires each to be detected.
Assumption sources: TL431B (2.483..2.507 V, drift <= 17 mV), LM2903 (Vos <= 15 mV full range, Ib <= 250 nA,
CM <= V+ - 2 V over temperature), LM2936-5.0 (+/-3 %), SUP53P06-20 gate model of P01 R3 dynamics.py
(Q2 input 10 nF nominal / 20 nF corner + 30 % Miller, Vth 1..3 V), STPS20100CT Vf, MFR-50 1 % / 100 ppm/K over 25 K.
"""
from pathlib import Path
import xml.etree.ElementTree as ET, json, itertools, math, sys, hashlib
P = Path(__file__).resolve().parents[1]
parts = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
xml = ET.parse(P / 'verification/P02.xml').getroot()
VALUES = {c.get('ref'): c.findtext('value') for c in xml.findall('./components/comp')}
PINS = {(x.get('ref'), x.get('pin')): n.get('name').split('/')[-1] for n in xml.findall('./nets/net') for x in n.findall('node')}
P01_SPICE = P.parents[0] / 'P01-R3-review/verification/dynamics.json'   # read-only calibration of the turn-off model

HV = {'P02_BAT_IN', 'P02_SW_COM', 'P02_VSW', 'P02_VLOG', 'P02_HOLD_C', 'P02_CH_A', 'P02_V_CTRL', 'P02_AUX_IN', 'VMOTOR',
      'P02_GATE', 'P02_OFF_G', 'P02_OFF_D', 'P02_REV_G', 'P02_PWR_A', 'P02_PWR_B', 'P02_REL_PB', 'P02_ON_COL', 'P02_REL_COL',
      'P02_VIN_DC5', 'P02_VIN_DC33', 'P02_LED_A', 'VBAT_CAR'}
CLAMP_EXEMPT = {'D3': 'TVS, VWM checked separately', 'D13': 'TVS, VWM checked separately', 'D4': 'Zener clamp, sees <= 15 V',
                'D9': 'Zener clamp, sees <= 15 V', 'D10': 'Zener clamp, sees <= 15 V', 'LED1': 'LED behind R29'}


def value(r, vv):
    s = vv[r].split(' / ')[0].upper().removesuffix('F')
    for k, m in [('K', 1e3), ('M', 1e6), ('R', 1), ('U', 1e-6), ('N', 1e-9), ('P', 1e-12)]:
        if k in s:
            a, b = s.split(k); return float((a or '0') + ('.' + b if b else '')) * m
    return float(s)


def rlim(r, vv):
    t = parts[r]['tolerance'] + parts[r]['tcr_ppm'] * 1e-6 * 25
    return [value(r, vv) * (1 - t), value(r, vv) * (1 + t)]


def members(pp, net):
    return sorted(f'{r}.{n}' for (r, n), m in pp.items() if m == net)


# ---------------------------------------------------------------- UVLO, OK, ENABLE, PFAIL_N
def ok_high(vv, aux5, beta=80, vbe=0.70, vf=0.70):
    """OK high level = AUX5 minus the R13 drop from its loads (R11, R6+R7, R14 -> D7/D8 -> Q6 base + R15). Iterated."""
    okh = aux5
    for _ in range(30):
        en = okh - 2 * vf - vbe
        loads = en / value('R16', vv)
        for rb, rp in (('R17', 'R18'), ('R19', 'R20'), ('R32', 'R33')):
            loads += max(0, (en - vbe) / value(rb, vv) - vbe / value(rp, vv))
        ibuf = loads / (beta + 1) + (en + vbe) / value('R15', vv)
        en = okh - ibuf * value('R14', vv) - 2 * vf - vbe
        iok = ibuf + okh / (value('R6', vv) + value('R7', vv)) + max(0, (okh - 2.5) / value('R11', vv))
        okh = aux5 - iok * value('R13', vv)
    return okh, en


def trip(vc, vok, ib, rt, rb, ri, rh):
    """Pack (SW_COM) voltage at which UV_CMP = vc. ib: current injected into UV_CMP by the comparator input."""
    d = vc - ((vok - vc) / rh + ib) * ri
    return d + (d / rb + (d - vc) / ri) * rt


def uvlo(vv):
    rt_lim = [a + b for a, b in zip(rlim('R5', vv), rlim('R9', vv))]
    on, off, hyst = [], [], []
    for rt, rb, ri, rh, vref, vos, ib, vol, aux in itertools.product(rt_lim, rlim('R10', vv), rlim('R12', vv), rlim('R11', vv),
                                                                     [2.483 - .017 - .004, 2.507 + .017 + .004], [-.015, .015],
                                                                     [0, 250e-9], [0, .4], [4.85, 5.15]):
        okh = ok_high(vv, aux)[0]
        u = trip(vref + vos, vol, ib, rt, rb, ri, rh); l = trip(vref + vos, okh, ib, rt, rb, ri, rh)
        on.append(u); off.append(l); hyst.append(u - l)
    n = [value(r, vv) for r in ('R5', 'R9', 'R10', 'R12', 'R11')]
    okn = ok_high(vv, 5.0)[0]
    non = trip(2.495, 0.15, 0, n[0] + n[1], n[2], n[3], n[4]); noff = trip(2.495, okn, 0, n[0] + n[1], n[2], n[3], n[4])
    div_r = 1 / (1 / n[2] + 1 / (n[0] + n[1]) + 1 / (n[3] + n[4]))
    return {'on_V': [min(on), max(on)], 'off_V': [min(off), max(off)], 'hysteresis_V': [min(hyst), max(hyst)],
            'nominal_on_V': non, 'nominal_off_V': noff, 'corners': len(on), 'ok_high_nominal_V': okn,
            'enable_nominal_V': ok_high(vv, 5.0)[1], 'div_filter_tau_us': div_r * value('C13', vv) * 1e6,
            'pwr_open_to_trip_us': div_r * value('C13', vv) * 1e6 * math.log(16.8 * n[2] / (n[0] + n[1] + n[2]) / 2.45),
            'divider_mA_at_16V8': 16.8 / (n[0] + n[1] + n[2]) * 1e3}


def pfail(vv):
    k_lo = rlim('R7', vv)[0] / (rlim('R7', vv)[0] + rlim('R6', vv)[1]); k_hi = rlim('R7', vv)[1] / (rlim('R7', vv)[1] + rlim('R6', vv)[0])
    rpar = 1 / (1 / value('R6', vv) + 1 / value('R7', vv))
    okh_min = ok_high(vv, 4.85, beta=80, vbe=.75, vf=.75)[0]
    pf_high_min = okh_min * k_lo - 250e-9 * rpar
    pf_low_max = 0.4 * k_hi + 250e-9 * rpar
    thr_max = 2.507 + .017 + .004 + .015; thr_min = 2.483 - .017 - .004 - .015
    cm_top = 4.85 - 2.0
    return {'PF_IN_high_min_V': pf_high_min, 'PF_IN_low_max_V': pf_low_max, 'threshold_V': [thr_min, thr_max],
            'margin_high_V': pf_high_min - thr_max, 'margin_low_V': thr_min - pf_low_max, 'REF_max_V': 2.507 + .021, 'CM_top_V': cm_top,
            'ok_high_min_V': okh_min,
            'edge_us': 1.3 + 2.2 * (value('R36', vv) + value('R37', vv)) * 170e-12 * 1e6}


# ---------------------------------------------------------------- Q1 turn-off (R23) and turn-on (VSW slew)
def turn_off_us(vv, vs, cin, vth_need, storage_us, c6f=1.0, rf=1.0):
    """ENABLE lost -> Q5, Q4 released (storage) -> OFF_G falls towards VS*R23/(R23+R24) (tau = R23||R24 * Cin)
    until Q2 has VSG = vth_need -> C6 (+Ciss Q1) discharged through R27 from VSG_on to 0.5 V."""
    r23, r24 = value('R23', vv) * rf, value('R24', vv) / rf
    vsg_inf = min(vs * r24 / (r23 + r24), 15.0)          # D9 clamps at 15 V
    tau = r23 * r24 / (r23 + r24) * cin
    if vsg_inf <= vth_need: return float('inf'), {}
    t_g = tau * math.log(vsg_inf / (vsg_inf - vth_need))
    vsg_on = min((vs - 0.1) * value('R22', vv) / (value('R21', vv) + value('R22', vv)), 15.0)
    t_c6 = (value('R27', vv) * 1.01 + 0.5) * (value('C6', vv) * c6f + 3.2e-9) * math.log(vsg_on / 0.5)
    return (storage_us * 1e-6 + t_g + t_c6) * 1e6, {'tau_OFF_G_us': tau * 1e6, 't_OFF_G_us': t_g * 1e6, 't_C6_us': t_c6 * 1e6, 'VSG_on_V': vsg_on}


def turn_off(vv):
    rows = {}
    for vs in (12.5, 16.8):
        rows[f'{vs} V, Ciss typ 3.5 nF (datasheet), Vth 1.5 V'] = turn_off_us(vv, vs, 3.5e-9, 1.5, 2)[0]
        rows[f'{vs} V, P01 model nominal (13 nF, 1.5 V, 2 us)'] = turn_off_us(vv, vs, 13e-9, 1.5, 2)[0]
        rows[f'{vs} V, P01 model corner (26 nF, 3.5 V, 6 us, C6 +10 %, R +1 %)'] = turn_off_us(vv, vs, 26e-9, 3.5, 6, 1.1, 1.01)[0]
    return rows


def calibration(vv):
    """Same analytic model with P01 R3 values (R23 = 2K2) against P01 R3 ngspice off_0 / off_1 (17 V)."""
    v2 = dict(vv); v2['R23'] = '2K2'
    model = {'off_0': turn_off_us(v2, 17, 13e-9, 1.5, 2)[0], 'off_1': turn_off_us(v2, 17, 26e-9, 3.5, 6, 1.05, 1.01)[0]}
    spice = {}
    if P01_SPICE.exists():
        d = json.loads(P01_SPICE.read_text(encoding='utf-8'))
        spice = {r['id']: r['off_to_0p5_us'] for r in d['results'] if r['id'] in model}
    return {'model_us': model, 'p01_spice_us': spice, 'ratio': {k: model[k] / spice[k] for k in spice}}


def inrush(vv, c_budget=220e-6):
    rows = {}
    for name, vs, vpl, crss, c5f, rf in [('nominal, 16.8 V', 16.8, 4.0, .29e-9, 1, 1), ('fast corner, 16.8 V', 16.8, 2.0, .29e-9, .95, .99),
                                        ('slow corner, 13.2 V', 13.2, 5.0, 2e-9, 1.05, 1.01)]:
        i_net = (vs - vpl - 0.1) / (value('R21', vv) * rf) - vpl / (value('R22', vv) / rf)
        slew = i_net / (value('C5', vv) * c5f + crss)                  # V/s, Miller plateau
        T = vs / slew; ch = value('C12', vv) * 1.2; tau = value('R40', vv) * 0.95 * ch
        i_cap = c_budget * slew
        i_ch = slew * ch * (1 - math.exp(-T / tau))                     # ramp into R40 + C_H (diode drop neglected)
        i_load = 6.0 / (vs - 0.45)                                      # 6 W logic already running at the end of the ramp
        u1, u2 = 7.0, vs - 0.45
        e_cap = 0.5 * c_budget * vs ** 2
        e_ch = vs ** 3 / (6 * slew * value('R40', vv) * 0.95)
        e_load = 6.0 / slew * ((vs - 0.45) * math.log(u2 / u1) - (u2 - u1))
        rows[name] = {'slew_V_per_ms': slew / 1e3, 'ramp_ms': T * 1e3, 'I_cap_A': i_cap, 'I_CH_end_A': i_ch, 'I_load_A': i_load,
                      'I_peak_A': i_cap + i_ch + i_load, 'E_Q1_mJ': (e_cap + e_ch + e_load) * 1e3,
                      'E_parts_mJ': {'C_VSW': e_cap * 1e3, 'C_H': e_ch * 1e3, 'load': e_load * 1e3}}
    return rows


def hotplug(vv, vstep=25.0):
    c5, c6 = value('C5', vv) * 1.05, value('C6', vv) * 0.9
    return vstep * c5 / (c5 + c6 + 2e-9)


def hold(vv, off_nom, off_min):
    c = value('C12', vv); rows = {}
    for name, cap, v, vf_ch, vf_or in [('nominal (C, V_off nom, Vf 0.25+0.45)', c, off_nom, .25, .45),
                                      ('worst (C -20 %, V_off min, Vf 0.30+0.50)', .8 * c, off_min, .30, .50),
                                      ('Z-08 spec method (C -20 %, V_off nom, one diode 0.45)', .8 * c, off_nom, 0, .45),
                                      ('PWR off at 16.8 V (C -20 %)', .8 * c, 16.8, .30, .50)]:
        v0 = v - vf_ch - vf_or; e = 0.5 * cap * (v0 ** 2 - 7.0 ** 2)
        rows[name] = {'V0_V': v0, 'E_mJ': e * 1e3, 'ms_3W': e / 3 * 1e3, 'ms_6W': e / 6 * 1e3}
    return rows


# ---------------------------------------------------------------- evaluation
def evaluate(vv, pp):
    checks = []
    def ck(n, v, info=''): checks.append({'check': n, 'pass': bool(v), 'info': info})
    mismatch = [(r, n, net, pp.get((r, n), '')) for r, p in parts.items() for n, net in p['pins'].items() if net != 'NC' and pp.get((r, n), '') != net]
    ck('C01 Every exported functional pin agrees with parts.py', not mismatch, f'{len(mismatch)} mismatches')
    g = lambda r, n: pp.get((r, str(n)))
    # --- topology, written independently of parts.py
    ck('T01 Q9 and Q1 back-to-back: Q9 D=BAT_IN S=SW_COM, Q1 S=SW_COM D=VSW (reverse polarity blocked by Q9 body diode)',
       g('Q9', 2) == 'P02_BAT_IN' and g('Q9', 3) == 'P02_SW_COM' and g('Q1', 3) == 'P02_SW_COM' and g('Q1', 2) == 'P02_VSW' and g('Q9', 1) == 'P02_REV_G'
       and g('R35', 1) == 'P02_REV_G' and g('R35', 2) == 'GND')
    ck('T02 BAT_IN reaches only J1.1, Q9 drain and TP1', members(pp, 'P02_BAT_IN') == ['J1.1', 'Q9.2', 'TP1.1'], ', '.join(members(pp, 'P02_BAT_IN')))
    ck('T03 Zener clamps D10/D4/D9: cathode SW_COM, anode on the gate of Q9/Q1/Q2',
       all(g(d, 1) == 'P02_SW_COM' and g(d, 2) == gate for d, gate in [('D10', 'P02_REV_G'), ('D4', 'P02_GATE'), ('D9', 'P02_OFF_G')]))
    ck('T04 Gate block as P01 R3: C5 GATE-VSW, C6 GATE-SW_COM, Q2 S=SW_COM D->R27->GATE, Q4 E=SW_COM C=OFF_G, R23 OFF_G-GND',
       {g('C5', 1), g('C5', 2)} == {'P02_GATE', 'P02_VSW'} and {g('C6', 1), g('C6', 2)} == {'P02_GATE', 'P02_SW_COM'}
       and g('Q2', 3) == 'P02_SW_COM' and g('Q2', 2) == 'P02_OFF_D' and {g('R27', 1), g('R27', 2)} == {'P02_OFF_D', 'P02_GATE'}
       and g('Q4', 1) == 'P02_SW_COM' and g('Q4', 3) == 'P02_OFF_G' and {g('R23', 1), g('R23', 2)} == {'P02_OFF_G', 'GND'})
    ck('T05 PWR switch in the UVLO top branch: SW_COM-R5-J14-R9-UV_DIV, R10 to GND (open = UV_DIV at 0 V = off)',
       g('R5', 1) == 'P02_SW_COM' and g('R5', 2) == g('J14', 1) == 'P02_PWR_A' and g('J14', 2) == g('R9', 1) == 'P02_PWR_B'
       and g('R9', 2) == 'P02_UV_DIV' and {g('R10', 1), g('R10', 2)} == {'P02_UV_DIV', 'GND'} and members(pp, 'P02_PWR_B') == ['J14.2', 'R9.1'])
    ck('T06 Filter C13 on UV_DIV before R12; hysteresis R11 from OK into UV_CMP; U2B + = UV_CMP, - = REF, out = OK',
       g('C13', 1) == 'P02_UV_DIV' and {g('R12', 1), g('R12', 2)} == {'P02_UV_DIV', 'P02_UV_CMP'} and {g('R11', 1), g('R11', 2)} == {'P02_OK', 'P02_UV_CMP'}
       and g('U2', 5) == 'P02_UV_CMP' and g('U2', 6) == 'P02_REF' and g('U2', 7) == 'P02_OK' and 'C13.1' not in members(pp, 'P02_UV_CMP'))
    ck('T07 PFAIL_N buffers OK: U2A + = OK x R7/(R6+R7), - = REF; pull-up to 3V3_IO; R37 to PFAIL_N at J16.1 and J12.3',
       g('U2', 3) == 'P02_PF_IN' and g('U2', 2) == 'P02_REF' and g('R6', 1) == 'P02_OK' and g('R6', 2) == 'P02_PF_IN' and g('R7', 2) == 'GND'
       and g('U2', 1) == 'P02_PFAIL_OC' and g('R36', 1) == '3V3_IO' and g('R37', 2) == 'PFAIL_N' and g('J16', 1) == 'PFAIL_N' and g('J12', 3) == 'PFAIL_N')
    ck('T08 SAFE_N as P01: Q7 base fed only from J13.1 (P04 3V3, separate from local 3V3_IO); Q8 released by ENABLE',
       members(pp, g('J13', 1)) == ['J13.1', 'R30.1'] and g('J13', 1) != '3V3_IO' and g('Q7', 3) == 'SAFE_N' == g('J13', 2)
       and g('Q8', 3) == g('Q7', 2) and g('R32', 1) == 'P02_ENABLE' and {g('R34', 1), g('R34', 2)} == {'PG_SEND', 'PG_LINK'})
    ck('T09 C_H: charged only via R40 + D2 (K = HOLD_C), discharged only via D1 A2; D1 A1 = VSW, K = VLOG',
       {g('R40', 1), g('R40', 2)} == {'P02_VSW', 'P02_CH_A'} and g('D2', 1) == g('D2', 3) == 'P02_CH_A' and g('D2', 2) == 'P02_HOLD_C'
       and g('D1', 1) == 'P02_VSW' and g('D1', 3) == 'P02_HOLD_C' and g('D1', 2) == 'P02_VLOG'
       and set(members(pp, 'P02_HOLD_C')) == {'C12.1', 'D1.3', 'D2.2', 'R41.1', 'TP4.1'})
    ck('T10 VMOTOR only from VSW through F1; nothing else on VMOTOR', g('F1', 1) == 'P02_VSW' and members(pp, 'VMOTOR') == ['F1.2', 'J2.1'])
    ck('T11 TSR inputs from VLOG through F2/F3', g('F2', 1) == g('F3', 1) == 'P02_VLOG' and g('U5', 1) == g('F2', 2) and g('U6', 1) == g('F3', 2))
    ck('T12 AUX5 supply V_CTRL = SW_COM (D11) OR VLOG (D12)', g('D11', 2) == 'P02_SW_COM' and g('D12', 2) == 'P02_VLOG' and g('D11', 1) == g('D12', 1) == g('R1', 1))
    ck('T13 VBAT: J15 - R38 - VBAT_SENSE (D13 bidirectional TVS to GND) - J11.1; no GND wire from the car',
       members(pp, 'VBAT_CAR') == ['J15.1', 'R38.1'] and set(members(pp, 'VBAT_SENSE')) == {'D13.1', 'J11.1', 'R38.2', 'TP16.1'} and g('D13', 2) == 'GND')
    ck('T14 TVS on VSW with VWM >= 16.8 V (5KP18A: 18 V)', g('D3', 1) == 'P02_VSW' and g('D3', 2) == 'GND' and '5KP18A' in vv['D3'].upper() + parts['D3']['mpn'])
    # --- UVLO
    u = uvlo(vv)
    ck('U01 Nominal UVLO matches spec 13.53 / 12.51 V within 0.05 V', abs(u['nominal_on_V'] - 13.53) <= .05 and abs(u['nominal_off_V'] - 12.51) <= .05,
       f"{u['nominal_on_V']:.3f} / {u['nominal_off_V']:.3f} V")
    ck('U02 Z-03: no start at 12.6 V (3S full) in any corner (on_min > 12.6 V)', u['on_V'][0] > 12.6, f"on_min {u['on_V'][0]:.2f} V")
    ck('U03 Rested 4S at 3.6 V/cell (14.4 V) always starts (on_max < 14.4 V)', u['on_V'][1] < 14.4, f"on_max {u['on_V'][1]:.2f} V")
    ck('U04 Off threshold >= 11.6 V in all corners (2.9 V/cell, above the BMS cut-off 2.5..2.8 V/cell); on > off per corner is U05',
       u['off_V'][0] >= 11.6, f"off {u['off_V'][0]:.2f}..{u['off_V'][1]:.2f} V")
    ck('U05 Hysteresis >= 0.7 V in all corners (D-05)', u['hysteresis_V'][0] >= .7, f"{u['hysteresis_V'][0]:.2f} V")
    # --- PFAIL_N
    pf = pfail(vv)
    ck('P01 PFAIL_N follows OK with >= 0.2 V margin both ways (U2A)', pf['margin_high_V'] >= .2 and pf['margin_low_V'] >= .2,
       f"high {pf['margin_high_V']:.2f} V, low {pf['margin_low_V']:.2f} V")
    ck('P02 U2 inputs: REF inside the LM2903 CM range over temperature (one input in range)', pf['REF_max_V'] <= pf['CM_top_V'])
    ck('P03 Z-09: PFAIL_N edge <= 100 us after OK/ENABLE change', pf['edge_us'] <= 100, f"{pf['edge_us']:.1f} us")
    # --- switch dynamics
    off = turn_off(vv); tmax = max(off.values())
    ck('S01 Q1 turn-off after ENABLE loss <= 1 ms in all declared cases (R23 = 22k)', tmax <= 1000, f'max {tmax:.0f} us')
    hp = hotplug(vv)
    ck('S02 Hot plug 25 V: VSG(Q1) step C5/(C5+C6+Ciss) <= 0.8 V (P01 R1 blocker rule)', hp <= .8, f'{hp:.2f} V')
    ir = inrush(vv)
    ck('S03 Z-07: capacitive inrush at the 220 uF budget <= 3.0 A (nominal)', ir['nominal, 16.8 V']['I_cap_A'] <= 3.0, f"{ir['nominal, 16.8 V']['I_cap_A']:.2f} A")
    ck('S04 O-04: VSW slew 5..15 V/ms in all corners', all(5 <= r['slew_V_per_ms'] <= 15 for r in ir.values()),
       ', '.join(f"{r['slew_V_per_ms']:.1f}" for r in ir.values()))
    ck('S05 Start: Q1 peak <= 5 A and energy <= 50 mJ (P01 R3 accepted 137 mJ)', all(r['I_peak_A'] <= 5 and r['E_Q1_mJ'] <= 50 for r in ir.values()),
       ', '.join(f"{r['I_peak_A']:.2f} A / {r['E_Q1_mJ']:.0f} mJ" for r in ir.values()))
    onboard = value('C3', vv) + value('C20', vv) + value('C21', vv) + value('C23', vv)
    ck('S06 Z-06: VSW cap <= 100 uF and switched on-board C <= 120 uF (>= 100 uF left for P07 within 220 uF)', value('C3', vv) <= 100e-6 and onboard <= 120e-6,
       f'C3 {value("C3", vv) * 1e6:.0f} uF, on-board {onboard * 1e6:.0f} uF, P07 allowance {220 - onboard * 1e6:.0f} uF')
    # --- hold-up
    h = hold(vv, u['nominal_off_V'], u['off_V'][0]); w = h['worst (C -20 %, V_off min, Vf 0.30+0.50)']
    ck('H01 Hold-up after PFAIL_N >= 10 ms at 6 W in the worst corner (firmware closes the file in <= 10 ms, spec section 9)', w['ms_6W'] >= 10,
       f"{w['ms_6W']:.1f} ms")
    # --- losses, ratings
    q = {i: i ** 2 * .030 for i in (3.5, 5.0)}
    ck('L01 Z-13: Q1 and Q9 each <= 1 W and Tj <= 110 C at 5 A, 50 C ambient, no heatsink (62 K/W)', q[5.0] <= 1 and 50 + q[5.0] * 62 <= 110,
       f'{q[3.5]:.2f} W at 3.5 A, {q[5.0]:.2f} W at 5 A')
    p5 = 16.8 ** 2 / rlim('R5', vv)[0]
    ck('L02 PWR wire shorted to GND: R5 <= 60 % of 0.5 W', p5 <= .3, f'{p5 * 1e3:.0f} mW')
    p23 = 16.8 ** 2 / rlim('R23', vv)[0]
    ck('L03 R23 static loss (Q4 on, OFF_G at SW_COM) <= 10 % of 0.5 W', p23 <= .05, f'{p23 * 1e3:.1f} mW')
    iaux = (5 - 2.495) / value('R3', vv) + 5 / value('R13', vv) + 2e-3 + 1.5e-3
    ck('L04 AUX5 regulates down to V_CTRL: LM2936 input >= 5.5 V at VLOG = 7 V', 7 - .7 - iaux * value('R1', vv) >= 5.5, f'{7 - .7 - iaux * value("R1", vv):.2f} V at {iaux * 1e3:.1f} mA')
    bad = []
    for r, p in parts.items():
        if r.startswith('TP') or r in CLAMP_EXEMPT or r in ('J1', 'J14', 'J15', 'R34'): continue
        if any(pp.get((r, n)) in HV for n in p['pins']):
            if p.get('v_rating') is None or p['v_rating'] < 25: bad.append(r)
    ck('R01 Z-14: every part on the pack-side nets rated >= 25 V (clamps and wire terminations listed as exempt)', not bad, ', '.join(bad))
    spec = [
        {'id': 'Z-02', 'text': 'UVLO 13.53 / 12.51 V, spread +/-0.34 V', 'result': f"on {u['on_V'][0]:.2f}..{u['on_V'][1]:.2f} V, off {u['off_V'][0]:.2f}..{u['off_V'][1]:.2f} V",
         'met': u['on_V'][0] >= 13.53 - .34 and u['on_V'][1] <= 13.53 + .34 and u['off_V'][0] >= 12.51 - .34 and u['off_V'][1] <= 12.51 + .34},
        {'id': 'Z-08', 'text': 'after PFAIL_N >= 14 ms at 6 W and >= 28 ms at 3 W (C_H -20 %)',
         'result': f"worst {w['ms_6W']:.1f} / {w['ms_3W']:.1f} ms; nominal {h['nominal (C, V_off nom, Vf 0.25+0.45)']['ms_6W']:.1f} / {h['nominal (C, V_off nom, Vf 0.25+0.45)']['ms_3W']:.1f} ms",
         'met': w['ms_6W'] >= 14 and w['ms_3W'] >= 28},
        {'id': 'Z-01', 'text': 'no damage at 0..25 V', 'result': '5KP18A on VSW: VBR min 20 V; a steady 25 V source drives the TVS into breakdown',
         'met': False},
    ]
    return {'checks': checks, 'uvlo': u, 'pfail': pf, 'turn_off_us': off, 'turn_off_calibration': calibration(vv), 'inrush': ir, 'hotplug_VSG_V': hp,
            'hold_up': h, 'q_loss_W': q, 'spec_conformance': spec, 'pin_mismatches': mismatch,
            'limits': '0..50 C; analytic models; LM2903/TL431/LM2936 data-sheet limits; SUP53P06 gate model of P01 R3; NOT_TESTED hardware'}


MUTATIONS = [  # (name, value overrides, pin overrides, expected failing check id)
    ('null_control', {}, {}, None),
    ('c5_220n_hotplug', {'C5': '220nF'}, {}, 'S02'), ('c6_100n_hotplug', {'C6': '100nF'}, {}, 'S02'),
    ('r23_220k_slow_off', {'R23': '220K'}, {}, 'S01'),
    ('pwr_bypassed', {}, {('R9', '1'): 'P02_SW_COM'}, 'T05'),
    ('safe_from_local_3v3', {}, {('R30', '1'): '3V3_IO', ('J13', '1'): '3V3_IO'}, 'T08'),
    ('r9_36k5_starts_on_3s', {'R9': '36K5'}, {}, 'U02'), ('r11_4m64_no_hysteresis', {'R11': '4M64'}, {}, 'U05'),
    ('dch_reversed', {}, {('D2', '1'): 'P02_HOLD_C', ('D2', '3'): 'P02_HOLD_C', ('D2', '2'): 'P02_CH_A'}, 'T09'),
    ('ch_1000u', {'C12': '1000u'}, {}, 'H01'),
    ('pfail_from_uv_cmp_literal_D06', {}, {('U2', '3'): 'P02_UV_CMP'}, 'T07'),
    ('qrev_swapped', {}, {('Q9', '2'): 'P02_SW_COM', ('Q9', '3'): 'P02_BAT_IN'}, 'T01'),
    ('vmotor_unswitched', {}, {('F1', '1'): 'P02_SW_COM'}, 'T10'),
    ('r5_100r', {'R5': '100R'}, {}, 'L02'), ('r7_47k_pfail_divider', {'R7': '47K'}, {}, 'P01'),
    ('c3_220u', {'C3': '220u'}, {}, 'S06'), ('c13_on_feedback', {}, {('C13', '1'): 'P02_UV_CMP'}, 'T06'),
    ('r1_1k_aux_dropout', {'R1': '1K'}, {}, 'L04'),
    ('r10_11k5_off_too_low', {'R10': '11K5'}, {}, 'U04'),
]

if __name__ == '__main__':
    rep = evaluate(VALUES, PINS)
    rep['inputs_sha256'] = {f: hashlib.sha256((P / f).read_bytes()).hexdigest() for f in ['verification/P02.xml', 'docs/parts.json', 'src/check_electrical.py']}
    rep['passed'] = all(c['pass'] for c in rep['checks'])
    (P / 'verification/electrical-checks.json').write_text(json.dumps(rep, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    for c in rep['checks']: print('PASS' if c['pass'] else 'FAIL', c['check'], ('| ' + c['info']) if c['info'] else '')
    for s in rep['spec_conformance']: print('SPEC', s['id'], 'spelnione' if s['met'] else 'NIESPELNIONE', '|', s['result'])
    if '--negative' in sys.argv:
        tests = []
        for name, rv, pv, target in MUTATIONS:
            r = evaluate({**VALUES, **rv}, {**PINS, **pv})
            failed = [c['check'].split()[0] for c in r['checks'] if not c['pass'] and not c['check'].startswith('C01')]
            ok = (not failed) if target is None else target in failed
            tests.append({'mutation': name, 'expected': target or 'all PASS', 'failed_checks': failed, 'detected': ok})
        (P / 'verification/electrical-negative-controls.json').write_text(json.dumps(tests, indent=2) + '\n')
        for t in tests: print('NEG', 'OK ' if t['detected'] else 'BAD', t['mutation'], '->', t['failed_checks'])
        print('Electrical negative controls:', sum(t['detected'] for t in tests), '/', len(tests))
        if not all(t['detected'] for t in tests): sys.exit(2)
    sys.exit(0 if rep['passed'] else 1)
