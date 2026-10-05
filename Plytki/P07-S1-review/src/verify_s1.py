"""P07-S1: independent checks of the exported netlist (verification/P07.xml) against the S1 format and the P12 contracts.
Nothing is imported from parts.py: expected pinouts, classes and exceptions are declared here; partner pins come from
reference/P12-kontrakty.json (P12 przygotowanie, nets waiting for P07), reference/P03-R6-J_BP.csv and reference/P04-R3-J_BP.csv
(git show origin/p04-r3-pcb, 702732a7). Every check has a netlist mutation that must fail exactly that check, plus a null control.
Output: verification/s1-checks.json."""
from pathlib import Path
import xml.etree.ElementTree as ET, json, copy, csv, re, sys
P = Path(__file__).resolve().parents[1]
G = 'GND'
JBP = {'J_BP1': {2: 'ADC_SCLK', 4: 'ADC_DOUTA', 6: 'CS_ITEST_N', 8: 'MOTOR_INA', 10: 'MOTOR_INB', 12: 'ENA_DIAG', 14: 'ENB_DIAG', 16: G},
       'J_BP2': {2: 'MOTOR_PERMIT', 4: 'PWM_OUT', 6: 'ARM_CLK', 8: 'DRIVE_OK', 10: '5V_SYS', 12: '5V_SYS', 14: '3V3_IO', 16: 'SAFE_N'}}
for j in JBP.values(): j.update({i: G for i in range(1, 16, 2)})
JBP_FP = 'Connector_IDC:IDC-Header_2x08_P2.54mm_Horizontal'
POWER = {'5V_SYS': 2, '3V3_IO': 1}                    # S1 5: 5V_SYS on >= 2 pins, 3V3_IO on >= 1
MOTOR = {'VMOTOR', 'PGND', 'MOD_BP', 'MOD_MP', 'T_EGR_P1', 'T_EGR_P3', 'K_PLUS', 'K_MINUS', 'KPWR_COIL_LOW'}   # S1 5: by wires, never on the tape
P04_NETS = ('MOTOR_PERMIT', 'PWM_OUT', 'ARM_CLK', 'DRIVE_OK', 'SAFE_N')
OPP = {'in': 'out', 'out': 'in'}
WIRES = {'J1': {'1': 'VMOTOR', '2': 'PGND'}, 'J2': {'1': 'MOD_BP', '2': 'PGND'}, 'J3': {'1': 'MOD_MP', '2': 'T_EGR_P3'}, 'J4': {'1': 'T_EGR_P1', '2': 'T_EGR_P3'}}
JMOD = {'1': 'RPWM', '2': 'LPWM', '3': 'R_EN', '4': 'L_EN', '5': 'R_IS', '6': 'L_IS', '7': '5V_MOD', '8': 'MOD_GND'}
ANALOG = {'I_T_OUT', 'ADC_AIN', 'REF_BUF', 'REF25', 'OC_HIGH', 'OC_LOW'}
PACK = {'VMOTOR', 'MOD_BP', 'KPWR_COIL_LOW', 'T_EGR_P1'}
RAILS = {'5V_SYS', '5VA_P07', '3V3A_P07', '3V3_IO', '5V_MOD'}
LOGIC = {'RAILS_OK', 'OC_LOCAL_N', 'OC_GOOD', 'NO_TRIP', 'DRIVE_EN'}
OHM = {**{n: 10000 for n in ANALOG}, **{n: 4700 for n in PACK}, **{n: 1000 for n in RAILS | LOGIC}}
GROUP = {'J_SV1': ANALOG | PACK, 'J_SV2': RAILS | LOGIC}
SV_FP = 'Connector_PinHeader_2.54mm:PinHeader_1x{:02d}_P2.54mm_Horizontal'
R_SMD = 'Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder'; C_SMD = 'Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder'
EXC_FP = {'R4': 'Resistor_SMD:R_2512_6332Metric_Pad1.40x3.35mm_HandSolder', 'C1': 'Capacitor_THT:CP_Radial_D8.0mm_P3.50mm',
          'RSH1': 'P07:R_Shunt_Vishay_WSK2512_T1.19mm_SenseE1.70'}
IC_FP = ('Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', 'Package_SO:SOIC-14_3.9x8.7mm_P1.27mm', 'Package_DIP:DIP-8_W7.62mm', 'Package_TO_SOT_THT:TO-92_Inline_Wide',
         'Package_TO_SOT_SMD:SOT-23-6')
SHUNT_SIDE = {'MOD_MP': 'K_PLUS', 'T_EGR_P1': 'K_MINUS'}


def read(path):
    root = ET.parse(path).getroot(); c = {}
    for x in root.findall('./components/comp'):
        f = {a.get('name'): a.text for a in x.findall('./fields/field')}
        c[x.get('ref')] = {'pins': {}, 'value': x.findtext('value'), 'mpn': f.get('MPN', '') or '', 'fp': x.findtext('footprint') or ''}
    for n in root.findall('./nets/net'):
        name = n.get('name').split('/')[-1]
        for x in n.findall('node'): c[x.get('ref')]['pins'][x.get('pin')] = 'NC' if name.startswith('unconnected-') else name
    return c


def rows(path):
    with path.open(encoding='utf-8-sig', newline='') as f: return list(csv.DictReader(f, delimiter=';'))


def ohms(v):
    v = v.split()[0].upper(); m = re.fullmatch(r'(\d+)([RKM])(\d*)', v)
    return float(m[1] + '.' + (m[3] or '0')) * {'R': 1, 'K': 1e3, 'M': 1e6}[m[2]] if m else None


def pads(fp):
    lib, name = fp.split(':'); f = P / 'eda/libraries' / (lib + '.pretty') / (name + '.kicad_mod')
    if not f.exists(): return {}
    out = {}
    for m in re.finditer(r'\(pad "(\d+)" smd \w+\s*\(at ([-\d.]+) ([-\d.]+)[^)]*\)\s*\(size ([-\d.]+) ([-\d.]+)\)', f.read_text()):
        out[m[1]] = (float(m[2]), float(m[3]), float(m[4]) * float(m[5]))
    return out


K12 = json.loads((P / 'reference/P12-kontrakty.json').read_text(encoding='utf-8'))
WAIT = {n: v for n, v in K12['sieci'].items() if 'P07' in v.get('czeka_na', [])}
P03 = {r['siec']: (r['zlacze'], int(r['pin']), r['kierunek']) for r in rows(P / 'reference/P03-R6-J_BP.csv')}
P04 = {r['siec']: (r['zlacze'], int(r['pin']), r['kierunek'], r['plytka_docelowa']) for r in rows(P / 'reference/P04-R3-J_BP.csv')}


def check(c):
    out = []
    def ok(k, v, d=None): out.append({'id': k, 'pass': bool(v), 'detail': d})
    def pinmap(r): return {int(p): n for p, n in c[r]['pins'].items()} if r in c else {}
    def members(net): return {(r, p) for r, x in c.items() for p, n in x['pins'].items() if n == net}
    jb = {j: pinmap(j) for j in JBP}
    for j, want in JBP.items():
        ok(j + '-PINOUT', jb[j] == want, jb[j])
        ok(j + '-FOOTPRINT', c.get(j, {}).get('fp') == JBP_FP, c.get(j, {}).get('fp'))
        ok(j + '-ODD-PINS-GND', bool(jb[j]) and all(jb[j][p] == G for p in jb[j] if p % 2))
    allj = [(j, p, n) for j in jb for p, n in jb[j].items()]
    on = {}
    for j, p, n in allj:
        if n != G: on[n] = on.get(n, 0) + 1
    ok('JBP-POWER-PINS', all(on.get(n, 0) >= k for n, k in POWER.items()), {n: on.get(n, 0) for n in POWER})
    # bus pins as the neighbours (P03 R6 J_BP2, P06 R2 J_BP): ADC_SCLK 2, ADC_DOUTA 4 on J_BP1
    ok('JBP1-SPI-PINS-AS-P03R6', all(jb['J_BP1'].get(P03[n][1]) == n and P03[n][0] == 'J_BP2' for n in ('ADC_SCLK', 'ADC_DOUTA')), {n: P03[n] for n in ('ADC_SCLK', 'ADC_DOUTA')})
    ok('JBP2-PINS-AS-P04R3', all(P04[n][0] == 'J_BP2' and jb['J_BP2'].get(P04[n][1]) == n for n in P04_NETS), {n: P04[n][:2] for n in P04_NETS})
    # P12 contract: every net waiting for P07 ends on P07 exactly once; after joining, one transmitter (or a CS-selected bus)
    csvr = rows(P / 'docs/J_BP.csv'); kd = {r['siec']: r['kierunek'] for r in csvr}
    bad = []
    for n, v in WAIT.items():
        if on.get(n, 0) != 1: bad.append((n, 'ends', on.get(n, 0))); continue
        dirs = [e.split()[-1].lower() for e in v['konce']] + [kd.get(n)]
        outs = dirs.count('out')
        if outs != 1 and not (v.get('magistrala') and outs >= 1 and kd.get(n) == 'out'): bad.append((n, 'drivers', dirs))
        p03 = P03.get(n)
        if p03 and kd.get(n) != OPP.get(p03[2]): bad.append((n, 'direction vs P03', kd.get(n), p03[2]))
    ok('P12-WAITING-NETS-END-ON-P07', not bad and len(WAIT) == 7, {'waiting': sorted(WAIT), 'bad': bad})
    bad = [(n, kd.get(n), P04[n][2]) for n in P04_NETS if n != 'SAFE_N' and kd.get(n) != OPP.get(P04[n][2])]
    bad += [] if kd.get('SAFE_N') == 'in' and 'P07' in P04['SAFE_N'][3] else [('SAFE_N', kd.get('SAFE_N'), P04['SAFE_N'][3])]
    ok('P04-NETS-DIRECTIONS', not bad, bad)
    allowed = set(WAIT) | set(P04_NETS) | set(POWER)
    ok('JBP-NO-FOREIGN-NETS', set(on) <= allowed and not (set(on) & MOTOR), sorted(set(on) - allowed))
    ok('CSV-J_BP', {(r['zlacze'], int(r['pin'])): r['siec'] for r in csvr} == {(j, p): n for j, p, n in allj}
       and all(r['kierunek'] in ('gnd', 'pwr', 'in', 'out') for r in csvr) and all((r['siec'] == G) == (r['kierunek'] == 'gnd') for r in csvr))
    # wires and module harness
    ok('WIRES-MOTOR-PATH', all(c.get(j, {}).get('pins') == w for j, w in WIRES.items()), {j: c.get(j, {}).get('pins') for j in WIRES})
    ok('JMOD-PINOUT', c.get('J5', {}).get('pins') == JMOD and 'IDC-Header_2x04' in c.get('J5', {}).get('fp', ''), c.get('J5', {}).get('pins'))
    # service strips (S1 6)
    seen = {}
    for j in ('J_SV1', 'J_SV2'):
        s = pinmap(j); n = max(s) if s else 0
        ok(j + '-MAX-13-PINS', s and sorted(s) == list(range(1, n + 1)) and n <= 13 and c[j]['fp'] == SV_FP.format(n))
        ok(j + '-GND-ENDS', s and s[1] == G and s[n] == G)
        good = True; nodes = []; at = {}
        for p in range(2, n):
            net = s.get(p, 'NC')
            if net == G: continue
            m = members(net); rr = [r for r, q in m if r.startswith('R')]
            if len(rr) != 1 or len(m) != 2 or not net.startswith('SRV_'): good = False; continue
            node = c[rr[0]]['pins'].get('1') if c[rr[0]]['pins'].get('2') == net else c[rr[0]]['pins'].get('2')
            nodes.append(node); at[p] = node; seen[node] = seen.get(node, 0) + 1
            if node != net[4:] or node not in OHM or ohms(c[rr[0]]['value']) != OHM[node] or len(members(node)) < 2: good = False
        ok(j + '-SERIES-R-AT-NODE-CLASS', good)
        ok(j + '-GROUP', set(nodes) <= GROUP[j], sorted(set(nodes) - GROUP[j]))
        def nb(q): return G if s.get(q) == G else at.get(q)
        bad = []
        for p, x in at.items():
            for q in (p - 1, p + 1):
                y = nb(q)
                if y is None: continue
                if x in RAILS and not (y == G or y in RAILS or y in LOGIC): bad.append((p, x, q, y))
                if x in ANALOG and not (y == G or y in ANALOG): bad.append((p, x, q, y))
                if x in PACK and not (y == G or y in PACK): bad.append((p, x, q, y))
        ok(j + '-NEIGHBOURS', not bad, bad)
    ok('SRV-EACH-NODE-ONCE', seen and all(v == 1 for v in seen.values()), {k: v for k, v in seen.items() if v != 1})
    sv = {(r['zlacze'], int(r['pin'])): r['siec'] for r in rows(P / 'docs/SERWIS.csv')}
    ok('CSV-SERWIS', sv == {(j, p): (n[4:] if n.startswith('SRV_') else n) for j in ('J_SV1', 'J_SV2') for p, n in pinmap(j).items()})
    # Kelvin shunt from the footprint geometry, in the motor line
    sp = pads(c['RSH1']['fp']); net = c['RSH1']['pins']
    good = len(sp) == 4 and set(net) == set(sp) and '2512' in c['RSH1']['fp']
    if good:
        force = sorted(sp, key=lambda k: -sp[k][2])[:2]; sense = [k for k in sp if k not in force]; side = lambda k: sp[k][0] > 0
        good = ({net[k] for k in force} == set(SHUNT_SIDE) and all(net[s] == SHUNT_SIDE[net[f]] for f in force for s in sense if side(s) == side(f))
                and len({side(k) for k in force}) == 2)
    ok('RSH1-KELVIN-MOTOR-LINE', good and c['RSH1']['value'].split()[0] == '5m', {k: (sp.get(k), net.get(k)) for k in sorted(set(sp) | set(net))})
    ina = [r for r, x in c.items() if x['value'] == 'INA240A2']
    k_ok = len(ina) == 1
    if k_ok:
        u = c[ina[0]]['pins']
        def via(n):
            return {x['pins'][q] for r, x in c.items() if r.startswith('R') for p, m in x['pins'].items() if m == n for q in x['pins'] if q != p}
        k_ok = 'K_PLUS' in via(u['8']) and 'K_MINUS' in via(u['1'])
    ok('INA240-KELVIN-INPUTS', k_ok)
    # part types (S1 1/4/9): new R/C SMD 1206, named power exceptions, ICs in SOIC/DIP/TO-92/SOT-23-6, nothing in QFN/BGA
    bad = []
    for r, x in c.items():
        if r in EXC_FP:
            if x['fp'] != EXC_FP[r]: bad.append(r)
        elif re.fullmatch(r'R\d+', r):
            if x['fp'] != R_SMD: bad.append(r)
        elif re.fullmatch(r'C\d+', r):
            if x['fp'] != C_SMD: bad.append(r)
        elif re.fullmatch(r'U\d+', r):
            if x['fp'] not in IC_FP: bad.append(r)
        if re.search(r'QFN|BGA|DFN', x['fp']): bad.append(r)
    ok('PART-TYPES-S1', not bad, bad)
    return out


c = read(P / 'verification/P07.xml')
res = check(c)


def mut_pin(r, p, n):
    def f(m): m[r]['pins'][str(p)] = n
    return f


def mut_val(r, v):
    def f(m): m[r]['value'] = v
    return f


def mut_fp(r, v):
    def f(m): m[r]['fp'] = v
    return f


MUT = [('J_BP1.6 CS_ITEST_N <-> 8 MOTOR_INA', lambda m: (mut_pin('J_BP1', 6, 'MOTOR_INA')(m), mut_pin('J_BP1', 8, 'CS_ITEST_N')(m)), 'J_BP1-PINOUT'),
       ('J_BP2.16 SAFE_N -> 15', lambda m: (mut_pin('J_BP2', 16, G)(m), mut_pin('J_BP2', 15, 'SAFE_N')(m)), 'J_BP2-ODD-PINS-GND'),
       ('J_BP1 vertical footprint', mut_fp('J_BP1', 'Connector_IDC:IDC-Header_2x08_P2.54mm_Vertical'), 'J_BP1-FOOTPRINT'),
       ('J_BP2 one 5V_SYS pin -> GND', mut_pin('J_BP2', 12, G), 'JBP-POWER-PINS'),
       ('ADC_SCLK on J_BP1.16', lambda m: (mut_pin('J_BP1', 2, G)(m), mut_pin('J_BP1', 16, 'ADC_SCLK')(m)), 'JBP1-SPI-PINS-AS-P03R6'),
       ('DRIVE_OK on J_BP2.10', lambda m: (mut_pin('J_BP2', 8, '5V_SYS')(m), mut_pin('J_BP2', 10, 'DRIVE_OK')(m)), 'JBP2-PINS-AS-P04R3'),
       ('ENB_DIAG missing (J_BP1.14 -> GND)', mut_pin('J_BP1', 14, G), 'P12-WAITING-NETS-END-ON-P07'),
       ('VMOTOR on the tape (J_BP2.14)', mut_pin('J_BP2', 14, 'VMOTOR'), 'JBP-NO-FOREIGN-NETS'),
       ('M+ wire to the TEST port directly (J3.1 -> T_EGR_P1)', mut_pin('J3', 1, 'T_EGR_P1'), 'WIRES-MOTOR-PATH'),
       ('J_MOD VCC/GND swapped', lambda m: (mut_pin('J5', 7, 'MOD_GND')(m), mut_pin('J5', 8, '5V_MOD')(m)), 'JMOD-PINOUT'),
       ('J_SV1 14 pins', mut_fp('J_SV1', SV_FP.format(14)), 'J_SV1-MAX-13-PINS'),
       ('J_SV2.13 not GND', mut_pin('J_SV2', 13, 'NC'), 'J_SV2-GND-ENDS'),
       ('service R of REF25 1K', mut_val('R55', '1K'), 'J_SV1-SERIES-R-AT-NODE-CLASS'),
       ('pack rail R 1K', mut_val('R60', '1K'), 'J_SV1-SERIES-R-AT-NODE-CLASS'),
       ('analog node on J_SV2 (SRV_RAILS_OK -> REF25 via R67)', lambda m: (mut_pin('R67', 1, 'REF25')(m), mut_val('R67', '10K')(m)), 'J_SV2-GROUP'),
       ('J_SV1 pin 8 GND -> pin 7 net (analog next to pack)', lambda m: (mut_pin('J_SV1', 8, 'SRV_OC_LOW')(m), mut_pin('J_SV1', 7, G)(m)), 'J_SV1-NEIGHBOURS'),
       ('node probed twice (R71 -> RAILS_OK)', lambda m: mut_pin('R71', 1, 'RAILS_OK')(m), 'SRV-EACH-NODE-ONCE'),
       ('SERWIS.csv stale (J_SV2.12 -> RAILS_OK)', lambda m: (mut_pin('J_SV2', 12, 'SRV_RAILS_OK')(m)), 'CSV-SERWIS'),
       ('shunt sense pads swapped', lambda m: (mut_pin('RSH1', 2, 'K_MINUS')(m), mut_pin('RSH1', 3, 'K_PLUS')(m)), 'RSH1-KELVIN-MOTOR-LINE'),
       ('INA240 IN+ on K_MINUS side', lambda m: (mut_pin('U1', 8, 'INA_MINUS')(m), mut_pin('U1', 1, 'INA_PLUS')(m)), 'INA240-KELVIN-INPUTS'),
       ('R15 in 0805', mut_fp('R15', 'Resistor_SMD:R_0805_2012Metric'), 'PART-TYPES-S1'),
       ('U5 in VSSOP (v6.1)', mut_fp('U5', 'Package_SO:VSSOP-8_3x3mm_P0.65mm'), 'PART-TYPES-S1'),
       ('J_BP.csv direction of DRIVE_OK flipped', None, 'P04-NETS-DIRECTIONS'),
       ('J_BP.csv stale (CSV-J_BP)', None, 'CSV-J_BP')]
neg = []
for name, fn, target in MUT:
    m = copy.deepcopy(c)
    if fn is None:                                   # CSV mutations: temporarily rewrite docs/J_BP.csv
        f = P / 'docs/J_BP.csv'; orig = f.read_bytes(); t = orig.decode('utf-8-sig')
        t = t.replace('J_BP2;8;DRIVE_OK;out', 'J_BP2;8;DRIVE_OK;in') if 'DRIVE_OK' in name else t.replace('J_BP1;12;ENA_DIAG', 'J_BP1;12;ENB_DIAG')
        f.write_bytes(t.encode('utf-8-sig'))
        try: r = check(m)
        finally: f.write_bytes(orig)
    else:
        fn(m); r = check(m)
    by = [x['id'] for x in r if not x['pass']]
    neg.append({'mutation': name, 'target': target, 'detected': target in by, 'by': by})
r0 = check(copy.deepcopy(c)); neg.append({'mutation': 'null control (unchanged netlist)', 'target': None, 'detected': any(not x['pass'] for x in r0), 'by': [x['id'] for x in r0 if not x['pass']]})
(P / 'verification/s1-checks.json').write_text(json.dumps({'checks': res, 'negative_controls': neg}, indent=1, ensure_ascii=False, default=str) + '\n', encoding='utf-8')
for x in res: print(('PASS ' if x['pass'] else 'FAIL ') + x['id'], '' if x['pass'] else str(x['detail'])[:200])
for t in neg: print(('ok   ' if t['detected'] == (t['target'] is not None) else 'BAD  ') + t['mutation'], t['by'])
sys.exit(0 if all(x['pass'] for x in res) and all(t['detected'] for t in neg[:-1]) and not neg[-1]['detected'] else 1)
