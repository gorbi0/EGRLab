"""P04-R3 (format S1): independent checks of the exported netlist (verification/P04.xml) against the S1 contract and the P12
contracts: edge-A connectors J_BP1..J_BP3, every net that waits for P04 on P12, names towards P07/P08 as in R2.2, edge-B service
strips J_SV1..J_SV3, part sources, and identity of the R2.2 circuit. Nothing is imported from parts.py: expected pinouts, resistor
classes and exceptions are declared here; the R2.2 circuit comes from its exported netlist (reference/P04-R2.2.xml), the
counterparts from reference/P12-kontrakty.json (P12-przygotowanie, generated from P02 R4 / P03 R6 / P05 R3 / P11 R2 sources),
reference/P03-R6-J_BP.csv, reference/P11-R2-J_P12.csv, reference/P04-R2.2-pinout.csv and reference/P08-R1-interfejsy.csv.
Every check has a netlist mutation that must fail exactly that check, plus a null control that must stay clean.
Output: verification/s1-checks.json."""
from pathlib import Path
import xml.etree.ElementTree as ET, json, copy, csv, re, sys
P = Path(__file__).resolve().parents[1]
G = 'GND'

# --- declared contract (task ZADANIE-P04-S1 2, 3) ---
JBP = {'J_BP1': {2: 'PANEL_3V3', 4: 'MECH_OK', 6: 'STOP_NC_OUT', 8: 'ARM_CONTACT', 10: 'SENSOR_PERMIT', 12: 'SENSOR_OK', 14: 'TEST_KEY', 16: 'DAQ_OK'},
       'J_BP2': {2: 'MOTOR_PERMIT', 4: 'PWM_OUT', 6: 'ARM_CLK', 8: 'DRIVE_OK', 10: '3V3_IO', 12: 'PSU_OK', 14: 'P04_3V3', 16: 'SAFE_N', 18: 'PG_LINK', 20: 'PG_SEND'},
       'J_BP3': {2: 'SENSOR_ENABLE', 4: 'CORE_LINK', 6: 'HW_ARMED', 8: '5V_SYS', 10: '3V3_IO', 12: 'SUP_N_OUT', 14: 'PWM', 16: 'HEARTBEAT', 18: 'MCU_ARM', 20: 'INTERLOCK'}}
for _j, _m in JBP.items(): _m.update({i: G for i in range(1, max(_m), 2)})
SIZE = {'J_BP1': 8, 'J_BP2': 10, 'J_BP3': 10}
JBP_FP = 'Connector_IDC:IDC-Header_2x{:02d}_P2.54mm_Horizontal'
DIRS = {'PANEL_3V3': 'zrodlo', 'MECH_OK': 'in', 'STOP_NC_OUT': 'in', 'ARM_CONTACT': 'in', 'SENSOR_PERMIT': 'out', 'SENSOR_OK': 'in', 'TEST_KEY': 'in',
        'DAQ_OK': 'in', 'MOTOR_PERMIT': 'out', 'PWM_OUT': 'out', 'ARM_CLK': 'out', 'DRIVE_OK': 'in', '3V3_IO': 'pwr', 'PSU_OK': 'in', 'P04_3V3': 'zrodlo',
        'SAFE_N': 'in', 'PG_LINK': 'petla', 'PG_SEND': 'petla', 'SENSOR_ENABLE': 'in', 'CORE_LINK': 'in', 'HW_ARMED': 'out', '5V_SYS': 'pwr',
        'SUP_N_OUT': 'in', 'PWM': 'in', 'HEARTBEAT': 'in', 'MCU_ARM': 'in', 'INTERLOCK': 'out'}
KIND = {'zrodlo': 'ZRODLO', 'pwr': 'PWR', 'petla': 'PETLA', 'out': 'OUT', 'in': 'IN', 'gnd': 'GND'}
SAME_PIN = {'J_BP1': ('P11 R2', 'J_P12', [2, 4, 6, 8, 14]), 'J_BP2': ('P02 R4', 'J_BP', [12, 16, 18]), 'J_BP3': ('P03 R6', 'J_BP3', [12, 14, 16, 18, 20])}
RENAME = {'PG_3V3': 'P04_3V3', 'SUP_N': 'SUP_N_OUT'}          # R2.2 -> R3 (P12 names); nothing else may change
OLD_CONNECTORS = ('J1', 'J2', 'J3', 'J4', 'J5', 'J6', 'J7', 'J8')
TWICE = {'3V3_IO'}
POWER = {'3V3_IO', '5V_SYS'}
# service strips (S1 6): node -> series resistor; rails 1K, gate-driven logic 1K, passive high-impedance nodes 10K, Q1_B 1K (E21)
RAILS = {'5V_SYS', '3V3_IO', 'PANEL_3V3', 'P04_3V3', 'PG_SEND'}
GUARDED = {'SAFE_N', 'ARM_BUTTON_N'}                       # passive nodes: only GND next to them
OHM = {**{n: 1000 for n in RAILS | {'ARM_CLK', 'HW_ARMED', 'SAFE_OK', 'SAFE_WD', 'WD_Q', 'Q1_B', 'LOCAL_SUP_N', 'SUP_OK', 'INTERLOCK',
                                     'MOTOR_PERMIT', 'PWM_OUT', 'SENSOR_PERMIT'}}, **{n: 10000 for n in GUARDED}}
TP_EXTRA = {'PANEL_3V3', 'P04_3V3', 'PG_SEND', 'ARM_BUTTON_N', 'PWM_OUT'}   # R3: E05/E15/E19/E22 points formerly on the connectors
SV_FP = 'Connector_PinHeader_2.54mm:PinHeader_1x{:02d}_P2.54mm_Horizontal'
STRIPS = ('J_SV1', 'J_SV2', 'J_SV3')
NEW_PARTS = {'J_BP1', 'J_BP2', 'J_BP3', *STRIPS, *[f'R{i}' for i in range(43, 62)]}
R_SMD = 'Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder'; C_SMD = 'Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder'
EXC_FP = {'C1': 'P04:C_WIMA_MKS2_1u100V_L7.2_W7.2_P5', 'C2': 'Capacitor_THT:C_Rect_L7.2mm_W5.0mm_P5.00mm',
          'C3': 'Capacitor_THT:CP_Radial_D5.0mm_P2.00mm', 'C18': 'Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm'}
SOIC = {'U8', 'U9', 'U10'}


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
    m = re.fullmatch(r'(\d+)(?:\.(\d+))?([RKM]?)', v.strip().upper())
    return float(m[1] + ('.' + m[2] if m[2] else '')) * {'': 1, 'R': 1, 'K': 1e3, 'M': 1e6}[m[3]]


R22 = read(P / 'reference/P04-R2.2.xml')
OLD = {}
for j in OLD_CONNECTORS:
    for n in R22[j]['pins'].values():
        if n not in (G, 'NC'): n = RENAME.get(n, n); OLD[n] = OLD.get(n, 0) + 1
TP_R22 = {x['pins']['1'] for r, x in R22.items() if r.startswith('TP')} - {G}
K12 = json.loads((P / 'reference/P12-kontrakty.json').read_text(encoding='utf-8'))['sieci']
def ends(net):
    out = []
    for e in K12.get(net, {}).get('konce', []):
        m = re.fullmatch(r'(P\d\d R\d+) (\S+)\.(\d+) (\w+)', e); out.append((m[1], m[2], int(m[3]), m[4]))
    return out
WAITING = {n for n, v in K12.items() if 'P04' in v.get('czeka_na', [])}
P22 = rows(P / 'reference/P04-R2.2-pinout.csv')
DRIVE = {r['net'] for r in P22 if r['ref'] == 'J3'} - {G, 'NC'}
SENSOR = {r['net'] for r in P22 if r['ref'] == 'J4'} - {G, 'NC'}
W2 = next(r for r in rows(P / 'reference/P08-R1-interfejsy.csv') if r['ID'].startswith('W2'))
SENSOR_P08 = {kv.split('=')[1] for kv in W2['piny'].split(';') if '=' in kv and '/' not in kv.split('=')[1] and kv.split('=')[1] not in (G, 'NC')}


def check(c):
    out = []
    def ok(k, v, d=None): out.append({'id': k, 'pass': bool(v), 'detail': d})
    def pinmap(r): return {int(p): n for p, n in c[r]['pins'].items()}
    def members(net): return {(r, p) for r, x in c.items() for p, n in x['pins'].items() if n == net}
    jb = {j: pinmap(j) for j in JBP}
    # --- J_BP1..J_BP3 ---
    for j in JBP:
        ok(j + '-PINOUT', jb[j] == JBP[j], jb[j])
        ok(j + '-FOOTPRINT', c[j]['fp'] == JBP_FP.format(SIZE[j]), c[j]['fp'])
    ok('JBP-ODD-PINS-GND', all(n == G for j in jb for p, n in jb[j].items() if p % 2))
    on = {}
    for j in jb:
        for n in jb[j].values():
            if n != G: on[n] = on.get(n, 0) + 1
    want = {n: (2 if n in TWICE else 1) for n in OLD}
    ok('JBP-R22-CONNECTOR-NETS-EXACTLY-ONCE', on == want, {'on_jbp': on, 'expected': want})
    same = {}
    for j, (board, conn, pins) in SAME_PIN.items():
        for p in pins:
            n = jb[j].get(p); e = [x for x in ends(n) if x[0] == board and x[1] == conn] if n in K12 else []
            if [x[2] for x in e] != [p]: same[f'{j}.{p}'] = (n, e)
    if ('P03 R6', 'J_BP1', 14, 'IN') not in ends(jb['J_BP1'].get(14)): same['P03 J_BP1.14'] = jb['J_BP1'].get(14)   # TEST_KEY: same pin on P11 and P03
    ok('JBP-PINS-AS-COUNTERPARTS', not same, same)
    # --- P12 contracts: every net waiting for P04 ends on P04 exactly once; one transmitter per net after P04 joins ---
    miss = sorted(n for n in WAITING if on.get(n, 0) != (2 if n in TWICE else 1))
    ok('P12-WAITING-NETS-ON-JBP', not miss and WAITING, {'missing_or_duplicated': miss, 'waiting': sorted(WAITING)})
    csvr = rows(P / 'docs/J_BP.csv'); kind = {r['siec']: KIND.get(r['kierunek']) for r in csvr if r['siec'] != G}
    bad = {}
    for n in WAITING:
        e = [x[3] for x in ends(n)] + [kind.get(n)]
        tx = e.count('OUT') + e.count('ZRODLO'); petla = 'PETLA' in e
        fine = (petla and set(e) <= {'PETLA'}) or (tx == 1 and not petla)
        if not fine: bad[n] = e
    ok('P12-ONE-TRANSMITTER', not bad, bad)
    known = set(WAITING) | DRIVE | SENSOR | POWER
    ok('P12-NO-FOREIGN-NAMES', set(on) <= known and not (set(on) - known - POWER), sorted(set(on) - known))
    ok('P12-POWER-NOT-SOURCED', all(kind.get(n) == 'PWR' for n in POWER), {n: kind.get(n) for n in POWER})
    # --- P07 / P08: names exactly as R2.2 J3 / J4 (and P08 R1 W2), P12 joins by name ---
    ok('P07-DRIVE-NAMES-AS-R22', DRIVE and DRIVE <= set(on), {'R2.2 J3': sorted(DRIVE), 'missing': sorted(DRIVE - set(on))})
    ok('P08-SENSOR-NAMES-AS-R22-AND-P08R1', SENSOR and SENSOR == SENSOR_P08 and SENSOR <= set(on), {'R2.2 J4': sorted(SENSOR), 'P08 R1 W2': sorted(SENSOR_P08)})
    # --- CSV contract for P12 ---
    ok('CSV-J_BP', {(r['zlacze'], int(r['pin'])): r['siec'] for r in csvr} == {(j, p): n for j in jb for p, n in jb[j].items()})
    ok('CSV-DIRECTIONS', {r['siec']: r['kierunek'] for r in csvr if r['siec'] != G} == DIRS and all(r['plytka_docelowa'] for r in csvr),
       {r['siec']: r['kierunek'] for r in csvr if r['siec'] != G and DIRS.get(r['siec']) != r['kierunek']})
    # --- service strips ---
    seen = {}
    for j in STRIPS:
        s = pinmap(j); n = max(s)
        ok(j + '-MAX-13-PINS', sorted(s) == list(range(1, n + 1)) and n <= 13 and c[j]['fp'] == SV_FP.format(n))
        ok(j + '-GND-ENDS', s[1] == G and s[n] == G)
        good = True; node_at = {}
        for p in range(2, n):
            net = s.get(p, 'NC')
            if net == G: continue
            m = members(net); rr = [r for r, q in m if r.startswith('R')]
            if len(rr) == 1:
                raw = c[rr[0]]['pins'].get('1') if (rr[0], '2') in m else c[rr[0]]['pins'].get('2')
                seen[raw] = seen.get(raw, 0) + 1; node_at[p] = raw
            if not net.startswith('SRV_') or len(m) != 2 or len(rr) != 1 or (j, str(p)) not in m or (rr[0], '2') not in m: good = False; continue
            node = c[rr[0]]['pins'].get('1')
            if node != net[4:] or node not in OHM or abs(ohms(c[rr[0]]['value']) - OHM[node]) > 1e-6: good = False; continue
            if len(members(node)) < 2: good = False
        ok(j + '-SERIES-R-AT-NODE-CLASS', good)
        def nb(q): return G if s.get(q) == G else node_at.get(q, 'NC')
        bad = [(p, node_at[p], q, nb(q)) for p in node_at for q in (p - 1, p + 1)
               if (node_at[p] in GUARDED and nb(q) != G) or (node_at[p] in RAILS and nb(q) not in RAILS | {G})]
        ok(j + '-NEIGHBOURS', not bad, bad)
    ok('SRV-EACH-NODE-ONCE', all(v == 1 for v in seen.values()), {k: v for k, v in seen.items() if v != 1})
    covered = {RENAME.get(n, n) for n in TP_R22} | TP_EXTRA
    ok('SRV-COVERS-R22-TESTPADS', set(seen) == covered, {'missing': sorted(covered - set(seen)), 'extra': sorted(set(seen) - covered)})
    sv = {(r['zlacze'], int(r['pin'])): r['siec'] for r in rows(P / 'docs/SERWIS.csv')}
    rz = {(r['zlacze'], int(r['pin'])): r['rezystor'].split()[:2] for r in rows(P / 'docs/SERWIS.csv') if r['rezystor'] != '-'}
    def res_on(j, p):
        rr = [r for r, q in members(pinmap(j)[p]) if r.startswith('R')]
        return [rr[0], c[rr[0]]['value']] if len(rr) == 1 else None
    ok('CSV-SERWIS', sv == {(j, p): (n[4:] if n.startswith('SRV_') else n) for j in STRIPS for p, n in pinmap(j).items()}
       and all(res_on(j, p) == v for (j, p), v in rz.items()) and set(rz) == {(j, p) for j in STRIPS for p, n in pinmap(j).items() if n != G})
    # --- part sources (S1 1/4/9 + named exceptions) ---
    bad = []
    for r, x in c.items():
        if r in EXC_FP:
            if x['fp'] != EXC_FP[r]: bad.append(r)
        elif re.fullmatch(r'R\d+', r):
            if x['fp'] != R_SMD or not x['mpn'].startswith('RC1206'): bad.append(r)
        elif re.fullmatch(r'C\d+', r):
            if x['fp'] != C_SMD: bad.append(r)
        if r in SOIC and x['fp'] != 'Package_SO:SOIC-14_3.9x8.7mm_P1.27mm': bad.append(r)
        if re.search(r'_0603_|_0805_|Adapter|TestPad', x['fp']): bad.append(r)
    ok('PARTS-S1-SOURCES', not bad, bad)
    # --- R2.2 circuit kept (everything except the replaced connectors and test pads; two nets renamed to the P12 names) ---
    diff = []
    for r, x in R22.items():
        if r in OLD_CONNECTORS or r.startswith('TP'): continue
        if r not in c: diff.append((r, 'missing')); continue
        for p, n in x['pins'].items():
            if c[r]['pins'].get(p) != RENAME.get(n, n): diff.append((r, p, n, c[r]['pins'].get(p)))
        if c[r]['value'] != x['value']: diff.append((r, 'value', x['value'], c[r]['value']))
    extra = sorted(set(c) - set(R22) - NEW_PARTS) + sorted(NEW_PARTS - set(c))
    ok('R22-CIRCUIT-KEPT', not diff and not extra, {'diff': diff[:10], 'extra_or_missing': extra})
    return out


def mutate(c, fn):
    cc = copy.deepcopy(c); fn(cc); return [t['id'] for t in check(cc) if not t['pass']]


if __name__ == '__main__':
    c = read(P / 'verification/P04.xml'); base = check(c)
    def setp(r, pin, v): return lambda cc: cc[r]['pins'].__setitem__(str(pin), v)
    def setf(r, f, v): return lambda cc: cc[r].__setitem__(f, v)
    def swap(r, a, b):
        def f(cc): p = cc[r]['pins']; p[str(a)], p[str(b)] = p[str(b)], p[str(a)]
        return f
    def both(*fs):
        def f(cc):
            for g in fs: g(cc)
        return f
    def find(j, net): return next(p for p, n in c[j]['pins'].items() if n == 'SRV_' + net)
    def rof(net): return next(r for r, x in c.items() if r.startswith('R') and x['pins'].get('2') == 'SRV_' + net)
    M = [('J_BP1-PINOUT', 'SENSOR_PERMIT and SENSOR_OK swapped', swap('J_BP1', 10, 12)),
         ('J_BP2-PINOUT', 'MOTOR_PERMIT and PWM_OUT swapped', swap('J_BP2', 2, 4)),
         ('J_BP3-PINOUT', 'SENSOR_ENABLE and CORE_LINK swapped', swap('J_BP3', 2, 4)),
         ('J_BP2-FOOTPRINT', 'vertical IDC header', setf('J_BP2', 'fp', 'Connector_IDC:IDC-Header_2x10_P2.54mm_Vertical')),
         ('J_BP1-FOOTPRINT', 'J_BP1 as 2x10', setf('J_BP1', 'fp', 'Connector_IDC:IDC-Header_2x10_P2.54mm_Horizontal')),
         ('JBP-ODD-PINS-GND', 'odd pin 19 of J_BP3 carries 3V3_IO', setp('J_BP3', 19, '3V3_IO')),
         ('JBP-R22-CONNECTOR-NETS-EXACTLY-ONCE', 'second 3V3_IO pin lost', setp('J_BP3', 10, G)),
         ('JBP-R22-CONNECTOR-NETS-EXACTLY-ONCE', 'PWM duplicated on 5V_SYS pin', setp('J_BP3', 8, 'PWM')),
         ('JBP-PINS-AS-COUNTERPARTS', 'PSU_OK and P04_3V3 swapped (P02 J_BP.12)', swap('J_BP2', 12, 14)),
         ('JBP-PINS-AS-COUNTERPARTS', 'TEST_KEY and DAQ_OK swapped (P11 / P03 pin 14)', swap('J_BP1', 14, 16)),
         ('JBP-PINS-AS-COUNTERPARTS', 'HEARTBEAT and MCU_ARM swapped (P03 J_BP3.16/18)', swap('J_BP3', 16, 18)),
         ('P12-WAITING-NETS-ON-JBP', 'DAQ_OK missing (pin to GND)', setp('J_BP1', 16, G)),
         ('P12-WAITING-NETS-ON-JBP', 'reset net under the R2.2 name SUP_N', setp('J_BP3', 12, 'SUP_N')),
         ('P12-NO-FOREIGN-NAMES', 'P02 name PFAIL_N on a P04 pin', setp('J_BP3', 8, 'PFAIL_N')),
         ('P12-ONE-TRANSMITTER', 'HW_ARMED declared as input in J_BP.csv (no transmitter)', lambda cc: DIRS_OVERRIDE.update(HW_ARMED='in')),
         ('P12-ONE-TRANSMITTER', 'PSU_OK declared as output (two transmitters)', lambda cc: DIRS_OVERRIDE.update(PSU_OK='out')),
         ('P12-POWER-NOT-SOURCED', '3V3_IO declared as source', lambda cc: DIRS_OVERRIDE.update({'3V3_IO': 'zrodlo'})),
         ('P07-DRIVE-NAMES-AS-R22', 'ARM_CLK renamed on the connector', setp('J_BP2', 6, 'ARM_CLK_OUT')),
         ('P08-SENSOR-NAMES-AS-R22-AND-P08R1', 'SENSOR_OK renamed on the connector', setp('J_BP1', 12, 'SENSOR_READY')),
         ('CSV-J_BP', 'J_BP.csv out of date (netlist swapped PG_LINK / PG_SEND)', swap('J_BP2', 18, 20)),
         ('CSV-DIRECTIONS', 'direction word changed in J_BP.csv', lambda cc: DIRS_OVERRIDE.update(MECH_OK='wej')),
         ('J_SV1-MAX-13-PINS', '14th pin on J_SV1', setp('J_SV1', 14, G)),
         ('J_SV2-MAX-13-PINS', 'J_SV2 vertical header', setf('J_SV2', 'fp', 'Connector_PinHeader_2.54mm:PinHeader_1x07_P2.54mm_Vertical')),
         ('J_SV1-GND-ENDS', 'first pin of J_SV1 not GND', setp('J_SV1', 1, 'SRV_SAFE_N')),
         ('J_SV3-GND-ENDS', 'last pin of J_SV3 not GND', setp('J_SV3', 7, 'SRV_PG_SEND')),
         ('J_SV1-NEIGHBOURS', 'SAFE_N next to ARM_CLK (interior GND swapped)', swap('J_SV1', 3, find('J_SV1', 'ARM_CLK'))),
         ('J_SV1-NEIGHBOURS', 'ARM_BUTTON_N next to HW_ARMED', swap('J_SV1', 5, find('J_SV1', 'HW_ARMED'))),
         ('J_SV3-NEIGHBOURS', 'rail next to logic (PG_SEND resistor moved to INTERLOCK)', both(setp(rof('PG_SEND'), 1, 'INTERLOCK'), setp(rof('INTERLOCK'), 1, 'PG_SEND'))),
         ('J_SV1-SERIES-R-AT-NODE-CLASS', 'SAFE_N through 1K instead of 10K', setf(rof('SAFE_N'), 'value', '1K')),
         ('J_SV1-SERIES-R-AT-NODE-CLASS', 'Q1_B through 10K (E21 would fail)', setf(rof('Q1_B'), 'value', '10K')),
         ('J_SV2-SERIES-R-AT-NODE-CLASS', 'pin wired straight to the node (no resistor)', setp('J_SV2', find('J_SV2', 'MOTOR_PERMIT'), 'MOTOR_PERMIT')),
         ('J_SV3-SERIES-R-AT-NODE-CLASS', 'service resistor shorted', setp(rof('3V3_IO'), 2, '3V3_IO')),
         ('SRV-EACH-NODE-ONCE', 'same node on two strips', setp(rof('PWM_OUT'), 1, 'WD_Q')),
         ('SRV-COVERS-R22-TESTPADS', 'LOCAL_SUP_N missing (resistor on a dead net)', setp(rof('LOCAL_SUP_N'), 1, 'NC')),
         ('CSV-SERWIS', 'SERWIS.csv out of date (strip order changed)', swap('J_SV2', find('J_SV2', 'INTERLOCK'), find('J_SV2', 'SUP_OK'))),
         ('CSV-SERWIS', 'resistor value differs from SERWIS.csv', setf(rof('5V_SYS'), 'value', '4.7K')),
         ('PARTS-S1-SOURCES', 'new resistor as 0805', setf('R14', 'fp', 'Resistor_SMD:R_0805_2012Metric')),
         ('PARTS-S1-SOURCES', 'buffer back on the Kamami adapter', setf('U9', 'fp', 'P04:Adapter_SO14_DIP14_W15.24_Kamami575068')),
         ('PARTS-S1-SOURCES', 'electrolytic outside the C3 exception', setf('C4', 'fp', 'Capacitor_THT:CP_Radial_D5.0mm_P2.00mm')),
         ('R22-CIRCUIT-KEPT', 'watchdog CLR moved to SAFE_N', setp('U1', '3', 'SAFE_N')),
         ('R22-CIRCUIT-KEPT', 'R1 value changed (watchdog time)', setf('R1', 'value', '100K')),
         ('R22-CIRCUIT-KEPT', 'Q2 collector and emitter swapped', swap('Q2', 1, 3))]
    DIRS_OVERRIDE = {}
    _rows = rows
    def rows(path):                                   # J_BP.csv direction mutations are applied on read
        r = _rows(path)
        if path.name == 'J_BP.csv':
            for x in r:
                if x['siec'] in DIRS_OVERRIDE: x['kierunek'] = DIRS_OVERRIDE[x['siec']]
        return r
    neg = []
    for target, title, fn in M:
        DIRS_OVERRIDE.clear(); by = mutate(c, fn); DIRS_OVERRIDE.clear()
        neg.append({'mutation': title, 'target': target, 'detected': target in by, 'by': by})
    zero = mutate(c, lambda cc: None); neg.append({'mutation': 'null control (no change)', 'target': None, 'detected': bool(zero), 'by': zero})
    (P / 'verification/s1-checks.json').write_text(json.dumps({'checks': base, 'negative_controls': neg,
        'references': ['reference/P04-R2.2.xml (closed R2.2 export)', 'reference/P12-kontrakty.json (P12-przygotowanie, pelny-s1 1557f176)',
                       'reference/P04-R2.2-pinout.csv', 'reference/P08-R1-interfejsy.csv', 'reference/P03-R6-J_BP.csv', 'reference/P11-R2-J_P12.csv'],
        'scope': 'Netlist/BOM contract only; no PCB exists in this package.'}, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    fail = [t['id'] for t in base if not t['pass']]; miss = [t['mutation'] for t in neg[:-1] if not t['detected']]
    print('S1 checks', len(base) - len(fail), '/', len(base), '; mutations', len(M) - len(miss), '/', len(M), '; null control', 'clean' if not zero else zero)
    for t in base:
        if not t['pass']: print('  FAIL', t['id'], t['detail'])
    for m in miss: print('  MISSED', m)
    sys.exit(1 if fail or miss or zero else 0)
