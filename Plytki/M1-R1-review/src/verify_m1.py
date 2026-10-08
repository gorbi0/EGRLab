"""M1 checks on the EXPORTED netlist (verification/M1.xml), each with negative controls (mutations that the target check must catch) and
a null control (an unchanged copy must pass everything). Checks: X1 contract, GPIO map + forbidden pins, ADC channel scaling and RC,
current channel, safe start (pull-downs), shared MISO, supply budget, single-node nets."""
from pathlib import Path
import json, sys, copy, csv, xml.etree.ElementTree as ET, collections
P = Path(__file__).resolve().parents[1]
parts = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
root = ET.parse(P / 'verification/M1.xml').getroot()
NET = collections.defaultdict(dict)
for n in root.findall('./nets/net'):
    name = n.get('name').split('/')[-1]
    for node in n.findall('node'): NET[node.get('ref')][node.get('pin')] = 'NC' if name.startswith('unconnected-') else name
NET = dict(NET)
X1 = list(csv.DictReader((P / 'docs/X1.csv').open(encoding='utf-8-sig'), delimiter=';'))
GP = list(csv.DictReader((P / 'docs/GPIO.csv').open(encoding='utf-8-sig'), delimiter=';'))
FORBIDDEN = {0, 45, 46, 19, 20, 33, 34, 35, 36, 37, 43, 44, 47, 48}
SPEC = {9: 'ADC_SCLK', 11: 'ADC_DOUTA', 2: 'ADC_SDI', 12: 'ADC_CS', 13: 'ADC_CONVST', 14: 'ADC_BUSY', 10: 'ADC_RESET', 4: 'SPI3_SCK', 5: 'SPI3_MOSI',
        6: 'SPI3_MISO', 7: 'SD_CS', 8: 'TC1_CS', 16: 'TC2_CS', 18: 'CAN_RXD', 1: 'RPWM', 21: 'LPWM', 39: 'DRIVE_EN', 40: 'SENS_EN', 42: 'SENS_FAULT_N',
        15: 'BTN', 41: 'SCOPE_TRIG', 3: 'GPIO3_TP', 38: 'NC'}   # SPECYFIKACJA 3 (LPWM on 21, GPIO38 = module RGB LED)
R_IN = 1e6   # AD7606B analog input impedance (data sheet, +-10 V range)


def nodes(N):
    d = collections.defaultdict(list)
    for r, pins in N.items():
        for p, n in pins.items(): d[n].append((r, p))
    return d


def two_pin(N, kind):
    return [(r, N[r]['1'], N[r]['2']) for r in N if r.startswith(kind) and set(N[r]) == {'1', '2'}]


def res_between(N, a, b):
    return [parts[r]['ohms'] for r, x, y in two_pin(N, 'R') if {x, y} == {a, b} and not parts[r].get('dnp')]


def chk_x1(N):
    bad = []
    for row in X1:
        if row['pole_pcb'] == '-': continue
        ref, pin = row['pole_pcb'].split('.')
        if N.get(ref, {}).get(pin) != row['siec']: bad.append((row['x1'], row['siec'], N.get(ref, {}).get(pin)))
    pads = [r for r in N if r in ('J1', 'J2', 'J5', 'J6')]
    listed = {row['pole_pcb'] for row in X1}
    bad += [('pad not on X1', f'{r}.{p}') for r in pads for p in N[r] if f'{r}.{p}' not in listed]
    return not bad, f'{len(X1)} X1 rows, wire pads J1/J2/J5/J6 all listed', bad


def chk_gpio(N):
    bad = []
    for row in GP:
        g = int(row['gpio']); net = N['M1'].get(row['pin_modulu'])
        if g in FORBIDDEN and net != 'NC': bad.append(('forbidden', g, net))
        if g in SPEC and net != SPEC[g]: bad.append(('map', g, net, SPEC[g]))
        if g not in SPEC and g not in FORBIDDEN and net != 'NC': bad.append(('unlisted', g, net))
    pw = {p: n for p, n in N['M1'].items() if not p.startswith(('J1-4', 'J1-5'))}
    if N['M1']['J1-21'] != '5V' or N['M1']['J1-1'] != 'NC' or N['M1']['J1-2'] != 'NC': bad.append(('module supply', N['M1']['J1-21'], N['M1']['J1-1']))
    return not bad, f'{len(GP)} module GPIOs vs SPECYFIKACJA 3; forbidden {sorted(FORBIDDEN)} NC; 5 V in J1-21, module 3V3 not tied', bad


def chk_adc(N):
    bad = []; info = []; nd = nodes(N)
    need = {1: ('P1_EGR', 20), 2: ('P3', 20), 3: ('P4', 6), 4: ('P5', 6), 5: ('P6', 6), 7: ('VBAT_CAR', 20), 8: ('SENS_5V', 6)}
    for ch, (src, vmin) in need.items():
        n = f'ADC_CH{ch}'
        if N['U3'].get(str(49 + 2 * (ch - 1))) != n: bad.append((n, 'not on U3')); continue
        top = res_between(N, src, n); bot = res_between(N, n, 'GND'); caps = [r for r, x, y in two_pin(N, 'C') if {x, y} == {n, 'GND'}]
        if len(top) != 1 or len(bot) > 1 or not caps: bad.append((n, top, bot, caps)); continue
        rb = R_IN if not bot else 1 / (1 / bot[0] + 1 / R_IN); gain = rb / (rb + top[0]); fs = 10 / gain
        tol = all(parts[r]['tolerance'] <= .001 for r, x, y in two_pin(N, 'R') if {x, y} in ({src, n}, {n, 'GND'}))
        info.append(f'CH{ch} {src}: FS {fs:.1f} V'); (fs < vmin or not tol) and bad.append((n, round(fs, 1), vmin, tol))
        if len(nd[n]) != 2 + len(bot) + len(caps): bad.append((n, 'extra nodes', nd[n]))
    if N['U3'].get('59') != 'ADC_CH6' or not res_between(N, 'I_MOT', 'ADC_CH6'): bad.append(('CH6', 'INA path'))
    return not bad, '; '.join(info), bad


def chk_current(N):
    bad = []; u = N['U4']; s = N['RSH1']
    if (s['1'], s['4']) != ('P1_ECU', 'P1_EGR'): bad.append(('shunt force', s))
    if res_between(N, s['2'], u['8']) != [10] or res_between(N, s['3'], u['1']) != [10]: bad.append(('Kelvin', s['2'], s['3'], u['8'], u['1']))
    if (u['6'], u['7'], u['3'], u['2']) != ('5V', '5V', 'GND', 'GND'): bad.append(('INA240 ref/supply', u))
    # linear range must exceed the F1 rating (7.5 A) with the output 0.2 V away from both rails (INA240 swing, conservative)
    gain = 50 * parts['RSH1']['ohms']; mid = 2.5; need = 8.0; lin = (mid - .2) / gain
    if lin < need: bad.append(('range', gain, round(lin, 2)))
    return not bad, f'INA240A2: {gain:.3f} V/A around {mid} V; linear +-{lin:.1f} A (need +-{need} A > F1 7.5 A)', bad


def chk_safe(N):
    bad = []
    for n in ('DRIVE_EN', 'RPWM', 'LPWM', 'SENS_EN', 'ADC_RESET'):
        if not res_between(N, n, 'GND'): bad.append((n, 'no pull-down'))
    for n in ('SD_CS', 'TC1_CS', 'TC2_CS', 'ADC_CS'):
        if not res_between(N, n, '3V3'): bad.append((n, 'no pull-up'))
    u = N['U7']
    if any(u[p] != 'GND' for p in ('1', '4', '10', '13')) or u['14'] != '5V': bad.append(('U7 OE / VCC', u))
    if (u['2'], u['5'], u['9'], u['12']) != ('RPWM', 'LPWM', 'DRIVE_EN', 'DRIVE_EN'): bad.append(('U7 inputs', u))
    j = N['J4']
    if (j['1'], j['2'], j['3'], j['4']) != (u['3'], u['6'], u['8'], u['11']): bad.append(('J4 order', j))
    return not bad, 'bridge inputs and sensor supply off while the ESP32 is in reset; CS lines idle high', bad


def chk_miso(N):
    bad = []; nd = nodes(N)
    drv = [(r, p) for r, p in nd['SPI3_MISO'] if r != 'M1']
    for r, p in drv:
        if r == 'SD1': continue
        if r != 'U5': bad.append(('MISO driver', r, p)); continue
        oe = {'3': '1', '6': '4', '8': '10', '11': '13'}[p]; a = {'3': '2', '6': '5', '8': '9', '11': '12'}[p]
        cs = N['U5'][oe]; tc = N['U5'][a]
        mod = next((m for m in ('TC1', 'TC2') if N[m]['5'] == tc), None)
        if not mod or N[mod]['7'] != cs: bad.append(('buffer OE != module CS', p, cs, tc))
    for m in ('TC1', 'TC2'):
        if N[m]['5'] == 'SPI3_MISO': bad.append((m, 'SDO straight on MISO'))
    return not bad, f'{len(drv)} MISO sources: SD1 + U5 gates enabled by the matching module CS', bad


LOAD = {'5V': [('M1', 350), ('U3', 25), ('U4', 2), ('J4', 20), ('U7', 1), ('U8', 100), ('U6', 10)], '3V3': [('SD1', 100), ('TC1', 5), ('TC2', 5), ('U3', 1), ('U6', 1), ('U5', 1)]}
SRC = {'5V': ('U1', 2000), '3V3': ('U2', 2000)}


def chk_power(N):
    bad = []; info = []
    for rail, loads in LOAD.items():
        ref, cap = SRC[rail]
        if N[ref]['3'] != rail or N[ref]['1'] != 'VBUS': bad.append((ref, N[ref]))
        for r, _ in loads:
            if r == 'U3' and rail == '5V': ok = N['U3']['1'] == '5VA' and res_between(N, '5V', '5VA')
            else: ok = rail in N[r].values() or (r == 'TC1' or r == 'TC2') and N[r]['1'] in (f'{r}_VIN',) and res_between(N, '3V3', f'{r}_VIN')
            if not ok: bad.append((rail, r, 'not on rail'))
        tot = sum(i for _, i in loads); info.append(f'{rail}: {tot} mA / {cap} mA'); tot > .5 * cap and bad.append((rail, tot, cap))
    if N['F1'] != {'1': 'BAT_P', '2': 'VBUS'} or N['J2']['1'] != 'VBUS': bad.append(('F1 / VMOTOR', N['F1'], N['J2']))
    return not bad, '; '.join(info) + ' (peak, derated to 50 %)', bad


def chk_single(N):
    bad = [(n, v) for n, v in nodes(N).items() if n != 'NC' and len(v) < 2]
    return not bad, 'no net with a single pin', bad


CHECKS = [('X1', chk_x1), ('GPIO', chk_gpio), ('ADC', chk_adc), ('PRAD', chk_current), ('START', chk_safe), ('MISO', chk_miso), ('ZASILANIE', chk_power), ('SIECI', chk_single)]


def run(N):
    out = []
    for cid, f in CHECKS:
        try: ok, note, bad = f(N)
        except (KeyError, StopIteration) as e: ok, note, bad = False, 'exception', [repr(e)]
        out.append(dict(id=cid, ok=ok, note=note, bad=[str(b) for b in bad][:10]))
    return out


def mut(fn):
    N = copy.deepcopy(NET); fn(N); return N


def setp(N, r, p, n): N[r][p] = n


MUT = [('X1', 'J6.1 swapped with J6.2 (P3 / P4)', lambda N: (setp(N, 'J6', '1', 'P4'), setp(N, 'J6', '2', 'P3'))),
       ('GPIO', 'LPWM back on GPIO38 (module RGB LED)', lambda N: (setp(N, 'M1', 'J3-18', 'NC'), setp(N, 'M1', 'J3-10', 'LPWM'))),
       ('GPIO', 'GPIO0 (strap) used for BTN', lambda N: setp(N, 'M1', 'J3-14', 'BTN')),
       ('GPIO', 'module 3V3 tied to the board 3V3', lambda N: setp(N, 'M1', 'J1-1', '3V3')),
       ('ADC', 'CH1 divider bottom removed (100k only into 1M)', lambda N: [setp(N, r, '2', 'NC') for r, a, b in two_pin(N, 'R') if {a, b} == {'ADC_CH1', 'GND'}]),
       ('ADC', 'CH7 without RC', lambda N: [setp(N, r, '1', 'NC') for r, a, b in two_pin(N, 'C') if {a, b} == {'ADC_CH7', 'GND'}]),
       ('PRAD', 'Kelvin pins swapped', lambda N: (setp(N, 'RSH1', '2', 'K_MINUS'), setp(N, 'RSH1', '3', 'K_PLUS'))),
       ('PRAD', 'INA240 REF1 on GND (unidirectional)', lambda N: setp(N, 'U4', '7', 'GND')),
       ('START', 'DRIVE_EN pull-down removed', lambda N: [setp(N, r, '2', 'NC') for r, a, b in two_pin(N, 'R') if {a, b} == {'DRIVE_EN', 'GND'}]),
       ('START', 'U7 OE on 3V3', lambda N: setp(N, 'U7', '1', '3V3')),
       ('MISO', 'TC2 SDO straight on MISO', lambda N: setp(N, 'TC2', '5', 'SPI3_MISO')),
       ('MISO', 'buffer OE swapped (TC1 gate on TC2_CS)', lambda N: setp(N, 'U5', '1', 'TC2_CS')),
       ('ZASILANIE', 'F1 bypassed (VMOTOR on BAT_P)', lambda N: setp(N, 'J2', '1', 'BAT_P')),
       ('ZASILANIE', 'SD card on 5V', lambda N: setp(N, 'SD1', '1', '5V')),
       ('SIECI', 'button pull-up disconnected from BTN', lambda N: [setp(N, r, '1' if a == 'BTN' else '2', 'BTN_X') for r, a, b in two_pin(N, 'R') if {a, b} == {'BTN', '3V3'}])]
base = run(NET); neg = []
for target, what, fn in MUT:
    r = run(mut(fn)); by = [c['id'] for c in r if not c['ok']]; neg.append(dict(mutation=what, target=target, detected=target in by, by=by))
null = [c['id'] for c in run(copy.deepcopy(NET)) if not c['ok']]
res = dict(checks=base, negative_controls=neg, null_control_clean=not null)
(P / 'verification/m1-checks.json').write_text(json.dumps(res, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
for c in base: print(c['id'], 'PASS' if c['ok'] else 'FAIL', c['note'], c['bad'][:3])
print('mutations', sum(t['detected'] for t in neg), '/', len(neg), 'null clean' if not null else 'NULL FAIL')
[print('  MISSED', t) for t in neg if not t['detected']]
sys.exit(0 if all(c['ok'] for c in base) and all(t['detected'] for t in neg) and not null else 1)
