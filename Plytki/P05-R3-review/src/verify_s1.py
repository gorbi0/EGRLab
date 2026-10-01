"""P05-R3 (format S1): independent checks of the exported netlist (verification/P05.xml) against the S1 contract:
edge-A connectors J_BP1/J_BP2, edge-B service strips J_SV1/J_SV2, part sources/footprints and identity of the R2 circuit.
Nothing is imported from parts.py: expected pinouts, resistor classes and exceptions are declared here; the old connector nets
come from the exported R2 netlist (reference/P05-R2.xml), the P03 DAQ pins from reference/P03-R6-J_BP.csv (branch p03-r6-pcb,
commit b094fa7). Every check has a netlist mutation that must fail exactly that check, plus a null control that must stay clean.
Output: verification/s1-checks.json."""
from pathlib import Path
import xml.etree.ElementTree as ET, json, copy, csv, re, sys
P = Path(__file__).resolve().parents[1]
G = 'GND'

# --- declared contract (task ZADANIE-P05-S1 2, 5, 6) ---
JBP1 = {1: G, 2: '5V_SYS', 3: G, 4: '5V_SYS', 5: G, 6: 'DAQ_OK', 7: G, 8: G, 9: G, 10: 'VBAT_SENSE'}
JBP2 = {1: G, 2: 'ADC_SCLK', 3: G, 4: 'ADC_DOUTA', 5: G, 6: 'ADC_SDI', 7: G, 8: 'ADC_CS', 9: G, 10: 'ADC_CONVST', 11: G, 12: 'ADC_BUSY',
        13: G, 14: 'MEAS_EN', 15: G, 16: G, 17: G, 18: 'ADC_RESET', 19: G, 20: G}
FP = {'J_BP1': 'Connector_IDC:IDC-Header_2x05_P2.54mm_Horizontal', 'J_BP2': 'Connector_IDC:IDC-Header_2x10_P2.54mm_Horizontal'}
DAQ = {'ADC_SCLK', 'ADC_DOUTA', 'ADC_SDI', 'ADC_CS', 'ADC_CONVST', 'ADC_BUSY', 'MEAS_EN', 'ADC_RESET'}
GND_BOTH_SIDES = {'ADC_SCLK', 'MEAS_EN'}
OLD_CONNECTORS = ('J1', 'J2', 'J3', 'J5')          # R2: B2B DAQ, LV05, DAQOK, VSENSE
DROPPED = {'3V3_IO'}                                 # LV05.3 was a test point only; P05 logic has its own 3V3_DAQ
TWICE = {'5V_SYS'}
WIRES = ('J4', 'J6')                                 # TAPS and AUX stay wires (S1 5)
# service strip classes (S1 6): 1K rails up to 5 V and logic, 4.7K pack-level rail, 10K high-impedance nodes
OHM = {**{n: 1000 for n in ['5V_SYS', '5VA_P05', '3V3_DAQ', 'MEAS_COIL_LOW', 'ADC_CS', 'ADC_CONVST', 'ADC_BUSY', 'ADC_DOUTA', 'ADC_RESET',
                            'MEAS_EN', 'MEAS_PERMIT', 'DAQ_OK', 'P05_SUP5_N']},
       'VBAT_SENSE': 4700, **{n: 10000 for n in ['REF_2V5', 'RAIL_SENSE', 'RAIL_LOW', 'RAIL_HIGH', 'DAQ_RAIL_N', 'P05_SUP3_N']}}
ODBIOR_MIN = {'5V_SYS', '5VA_P05', '3V3_DAQ', 'REF_2V5', 'DAQ_OK', 'MEAS_PERMIT', 'MEAS_EN', 'ADC_RESET', 'ADC_BUSY', 'ADC_CONVST', 'ADC_CS',
              'MEAS_COIL_LOW', 'VBAT_SENSE'}
GROUP = {'J_SV1': {'5V_SYS', '5VA_P05', '3V3_DAQ', 'REF_2V5', 'RAIL_SENSE', 'RAIL_LOW', 'RAIL_HIGH', 'VBAT_SENSE', 'MEAS_COIL_LOW'},
         'J_SV2': {'ADC_CS', 'ADC_CONVST', 'ADC_BUSY', 'ADC_DOUTA', 'ADC_RESET', 'MEAS_EN', 'MEAS_PERMIT', 'DAQ_OK', 'DAQ_RAIL_N', 'P05_SUP3_N', 'P05_SUP5_N'}}
SV_FP = 'Connector_PinHeader_2.54mm:PinHeader_1x{:02d}_P2.54mm_Horizontal'
# 1.10 (local review; rule decided for P03 R6): a rail pin only next to GND or another rail; the pack-level VBAT_SENSE only next to GND
RAILS = {'5V_SYS', '5VA_P05', '3V3_DAQ'}; PACK = {'VBAT_SENSE'}
NEW_PARTS = {'J_BP1', 'J_BP2', 'J_SV1', 'J_SV2', *[f'TP{i}' for i in range(1, 6)], *[f'R{i}' for i in range(36, 56)]}
SW1_R3 = {'4': 'NC', '6': G}                         # pole B mirrored for the JS202011AQN footprint (verify_electrical: geometry)
# part sources (S1 1/4/9 + exceptions named in the task)
R_SMD = 'Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder'; C_SMD = 'Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder'
R_STAND = 'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P5.08mm_Vertical'
EXC_FP = {'R1': 'Resistor_THT:R_Axial_DIN0411_L9.9mm_D3.6mm_P15.24mm_Horizontal', 'C1': 'Capacitor_THT:CP_Radial_D8.0mm_P3.50mm',
          'C12': 'Capacitor_SMD:C_1210_3225Metric', 'C13': 'Capacitor_SMD:C_1210_3225Metric'}
OWNED_THT_C = {'P05:C_TDK_B32529_L7.3_W2.5_P5', 'P05:C_WIMA_MKS2_1u100V_L7.2_W7.2_P5', 'Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm'}
WINDOW = ['R3', 'R4', 'R5', 'R6', 'R7', 'R8']; DIVIDERS = ['R28', 'R29', 'R31', 'R32', 'R33', 'R34', 'R35']


def read(path):
    root = ET.parse(path).getroot(); c = {}
    for x in root.findall('./components/comp'):
        f = {a.get('name'): a.text for a in x.findall('./fields/field')}
        c[x.get('ref')] = {'pins': {}, 'value': x.findtext('value'), 'mpn': f.get('MPN', '') or '', 'fp': x.findtext('footprint') or ''}
    for n in root.findall('./nets/net'):
        name = n.get('name').split('/')[-1]
        for x in n.findall('node'): c[x.get('ref')]['pins'][x.get('pin')] = 'NC' if name.startswith('unconnected-') else name
    return c


def rows(name):
    with (P / 'docs' / name).open(encoding='utf-8-sig', newline='') as f: return list(csv.DictReader(f, delimiter=';'))


def ohms(v):
    m = re.fullmatch(r'(\d+)(?:\.(\d+))?([RKM]?)', v.strip().upper())
    return float(m[1] + ('.' + m[2] if m[2] else '')) * {'': 1, 'R': 1, 'K': 1e3, 'M': 1e6}[m[3]]


R2 = read(P / 'reference/P05-R2.xml')
OLD = {}
for j in OLD_CONNECTORS:
    for n in R2[j]['pins'].values():
        if n not in (G, 'NC'): OLD[n] = OLD.get(n, 0) + 1
P03 = {r['siec']: int(r['pin']) for r in csv.DictReader((P / 'reference/P03-R6-J_BP.csv').open(encoding='utf-8-sig'), delimiter=';') if r['zlacze'] == 'J_BP2'}


def check(c):
    out = []
    def ok(k, v, d=None): out.append({'id': k, 'pass': bool(v), 'detail': d})
    def pinmap(r): return {int(p): n for p, n in c[r]['pins'].items()}
    def members(net): return {(r, p) for r, x in c.items() for p, n in x['pins'].items() if n == net}
    j1, j2 = pinmap('J_BP1'), pinmap('J_BP2'); both = [('J_BP1', j1), ('J_BP2', j2)]
    # --- J_BP ---
    ok('JBP1-PINOUT', j1 == JBP1, j1); ok('JBP2-PINOUT', j2 == JBP2, j2)
    ok('JBP-FOOTPRINTS', all(c[r]['fp'] == f for r, f in FP.items()))
    ok('JBP2-DAQ-PINS-AS-P03R6', all(n in P03 and P03[n] == p for p, n in j2.items() if n in DAQ) and DAQ <= set(j2.values()),
       {n: (p, P03.get(n)) for p, n in j2.items() if n in DAQ})
    ok('JBP-ODD-PINS-GND', all(m[p] == G for _, m in both for p in m if p % 2))
    ok('JBP-GND-AROUND-SCLK-MEAS_EN', all(m.get(p - 1) == G and m.get(p + 1) == G for _, m in both for p, n in m.items() if n in GND_BOTH_SIDES)
       and all(any(n in GND_BOTH_SIDES for n in m.values()) for _, m in [both[1]]))
    on = {}
    for _, m in both:
        for n in m.values():
            if n != G: on[n] = on.get(n, 0) + 1
    want = {n: (2 if n in TWICE else 1) for n in OLD if n not in DROPPED}
    ok('JBP-OLD-NETS-EXACTLY-ONCE', on == want, {'on_jbp': on, 'expected': want})
    ok('JBP-3V3_IO-ABSENT', not any(n in DROPPED for x in c.values() for n in x['pins'].values()))
    wire = {n for r in WIRES for n in c[r]['pins'].values()} - {G, 'NC'}
    ok('JBP-NO-TAPS-AUX', not (set(on) & wire) and not any(n.startswith(('TAP_', 'AUX_', 'ADC_CH')) for n in on), sorted(wire))
    # --- service strips ---
    seen = {}
    for j in ('J_SV1', 'J_SV2'):
        s = pinmap(j); n = max(s)
        ok(j + '-MAX-13-PINS', sorted(s) == list(range(1, n + 1)) and n <= 13 and c[j]['fp'] == SV_FP.format(n))
        ok(j + '-GND-ENDS', s[1] == G and s[n] == G)   # 1.10: interior GND allowed (S1 6 asks for GND on the ends only)
        good = True; nodes = []; node_at = {}
        for p in range(2, n):
            net = s.get(p, 'NC')
            if net == G:
                continue                                       # 1.10: interior GND pin (probe ground next to rails)
            m = members(net); rr = [r for r, q in m if r.startswith('R')]
            if len(rr) == 1:                                   # the node actually probed through this pin (independent of net names)
                raw = c[rr[0]]['pins'].get('1') if (rr[0], '2') in m else c[rr[0]]['pins'].get('2')
                nodes.append(raw); seen[raw] = seen.get(raw, 0) + 1; node_at[p] = raw
            if not net.startswith('SRV_') or len(m) != 2 or len(rr) != 1 or (j, str(p)) not in m or (rr[0], '2') not in m: good = False; continue
            node = c[rr[0]]['pins'].get('1')
            if node != net[4:] or node not in OHM or abs(ohms(c[rr[0]]['value']) - OHM[node]) > 1e-6: good = False; continue
            if len(members(node)) < 3: good = False          # the node must exist beyond the service resistor
        ok(j + '-SERIES-R-AT-NODE-CLASS', good)
        ok(j + '-GROUP', set(nodes) <= GROUP[j], sorted(nodes))
        nb = lambda q: G if s.get(q) == G else node_at.get(q)
        bad_nb = [(p, node_at[p], q, nb(q)) for p in node_at for q in (p - 1, p + 1)
                  if (node_at[p] in RAILS and not (nb(q) == G or nb(q) in RAILS)) or (node_at[p] in PACK and nb(q) != G)]
        ok(j + '-RAILS-NEXT-TO-GND-OR-RAIL', not bad_nb, bad_nb)
    ok('SRV-EACH-NODE-ONCE', all(v == 1 for v in seen.values()), {k: v for k, v in seen.items() if v != 1})
    ok('SRV-COVERS-ODBIOR', ODBIOR_MIN <= set(seen), sorted(ODBIOR_MIN - set(seen)))
    # --- CSV contracts for P12 and the service strips ---
    jb = {(r['zlacze'], int(r['pin'])): r['siec'] for r in rows('J_BP.csv')}
    ok('CSV-J_BP', jb == {(j, p): n for j, m in both for p, n in m.items()})
    sv = {(r['zlacze'], int(r['pin'])): r['siec'] for r in rows('SERWIS.csv')}
    # 1.10 (local review): the resistor column too - reference and value of the resistor that the netlist puts on that pin
    rz = {(r['zlacze'], int(r['pin'])): r['rezystor'].split()[:2] for r in rows('SERWIS.csv') if r['rezystor'] != '-'}
    def res_on(j, p):
        rr = [r for r, q in members(pinmap(j)[p]) if r.startswith('R')]
        return [rr[0], c[rr[0]]['value']] if len(rr) == 1 else None
    ok('CSV-SERWIS', sv == {(j, p): (n[4:] if n.startswith('SRV_') else n) for j in ('J_SV1', 'J_SV2') for p, n in pinmap(j).items()}
       and all(res_on(j, p) == v for (j, p), v in rz.items()) and set(rz) == {(j, p) for j in ('J_SV1', 'J_SV2') for p, n in pinmap(j).items() if n != G})
    # --- part sources ---
    bad = []
    for r, x in c.items():
        if r in EXC_FP:
            if x['fp'] != EXC_FP[r]: bad.append(r)
        elif re.fullmatch(r'R\d+', r):
            if not (x['fp'] == R_SMD or (x['fp'] == R_STAND and x['mpn'].startswith('MF0207') and 'owned' in x['mpn'])): bad.append(r)
        elif re.fullmatch(r'C\d+', r):
            if not (x['fp'] == C_SMD or (x['fp'] in OWNED_THT_C and 'owned' in x['mpn'])): bad.append(r)
        if re.search(r'_0603_|_0805_', x['fp']): bad.append(r)
    ok('PARTS-S1-SOURCES', not bad, bad)
    ok('PARTS-PRECISION-SERIES', all(c[r]['mpn'].startswith('RT1206BRB07') for r in WINDOW) and all(c[r]['mpn'].startswith(('RT1206BRD07', 'RT1206BRB07')) for r in DIVIDERS),
       {r: c[r]['mpn'] for r in WINDOW + DIVIDERS})
    # --- R2 circuit kept (everything except the replaced connectors/test pads and the deliberate SW1 pole-B mirror) ---
    diff = []
    for r, x in R2.items():
        if r in OLD_CONNECTORS or r.startswith('TP'): continue
        if r not in c: diff.append((r, 'missing')); continue
        for p, n in x['pins'].items():
            want_n = SW1_R3.get(p, n) if r == 'SW1' else n
            if c[r]['pins'].get(p) != want_n: diff.append((r, p, want_n, c[r]['pins'].get(p)))
    extra = sorted(set(c) - set(R2) - NEW_PARTS) + sorted(NEW_PARTS - set(c))
    ok('R2-CIRCUIT-KEPT', not diff and not extra, {'diff': diff[:10], 'extra_or_missing': extra})
    return out


def mutate(c, fn):
    cc = copy.deepcopy(c); fn(cc); return [t['id'] for t in check(cc) if not t['pass']]


if __name__ == '__main__':
    c = read(P / 'verification/P05.xml'); base = check(c)
    def setp(r, pin, v): return lambda cc: cc[r]['pins'].__setitem__(str(pin), v)
    def setf(r, f, v): return lambda cc: cc[r].__setitem__(f, v)
    def swap(r, a, b):
        def f(cc): p = cc[r]['pins']; p[str(a)], p[str(b)] = p[str(b)], p[str(a)]
        return f
    def add_pin(r, pin, v): return lambda cc: cc[r]['pins'].__setitem__(str(pin), v)
    M = [('JBP1-PINOUT', 'DAQ_OK and VBAT_SENSE swapped', swap('J_BP1', 6, 10)),
         ('JBP2-PINOUT', 'reserve pin 16 carries PFAIL_N as on P03', setp('J_BP2', 16, 'PFAIL_N')),
         ('JBP-FOOTPRINTS', 'J_BP2 vertical header', setf('J_BP2', 'fp', 'Connector_IDC:IDC-Header_2x10_P2.54mm_Vertical')),
         ('JBP2-DAQ-PINS-AS-P03R6', 'SCLK and DOUTA swapped', swap('J_BP2', 2, 4)),
         ('JBP-ODD-PINS-GND', 'odd pin 3 of J_BP1 carries DAQ_OK', setp('J_BP1', 3, 'DAQ_OK')),
         ('JBP-GND-AROUND-SCLK-MEAS_EN', '5V_SYS next to MEAS_EN (pin 15)', setp('J_BP2', 15, '5V_SYS')),
         ('JBP-OLD-NETS-EXACTLY-ONCE', 'second 5V_SYS pin lost', setp('J_BP1', 4, G)),
         ('JBP-OLD-NETS-EXACTLY-ONCE', 'DAQ_OK duplicated on reserve pin 20', setp('J_BP2', 20, 'DAQ_OK')),
         ('JBP-3V3_IO-ABSENT', '3V3_IO brought back on reserve pin 8', setp('J_BP1', 8, '3V3_IO')),
         ('JBP-NO-TAPS-AUX', 'TAP_P1 routed to J_BP2 pin 16', setp('J_BP2', 16, 'TAP_P1')),
         ('J_SV2-MAX-13-PINS', '14th pin on J_SV2', add_pin('J_SV2', 14, G)),
         ('J_SV1-MAX-13-PINS', 'J_SV1 vertical header', setf('J_SV1', 'fp', 'Connector_PinHeader_2.54mm:PinHeader_1x13_P2.54mm_Vertical')),
         ('J_SV1-GND-ENDS', 'first pin of J_SV1 not GND', setp('J_SV1', 1, 'SRV_5V_SYS')),
         ('J_SV2-GND-ENDS', 'last pin of J_SV2 not GND', setp('J_SV2', 13, 'SRV_ADC_CS')),
         ('J_SV1-RAILS-NEXT-TO-GND-OR-RAIL', 'REF_2V5 next to 3V3_DAQ (pins 7 and 8 swapped)', swap('J_SV1', 7, 8)),
         ('J_SV1-RAILS-NEXT-TO-GND-OR-RAIL', 'VBAT_SENSE next to 5V_SYS (pins 2 and 3 swapped)', swap('J_SV1', 2, 3)),
         ('J_SV1-GROUP', 'DAQ node on the analog strip', setp('R40', 1, 'DAQ_RAIL_N')),
         ('J_SV2-SERIES-R-AT-NODE-CLASS', 'pin wired straight to the node (no resistor)', setp('J_SV2', 2, 'ADC_CS')),
         ('J_SV1-SERIES-R-AT-NODE-CLASS', 'REF_2V5 through 1K instead of 10K', setf('R39', 'value', '1K')),
         ('J_SV1-SERIES-R-AT-NODE-CLASS', 'VBAT_SENSE through 1K instead of 4.7K', setf('R43', 'value', '1K')),
         ('J_SV1-SERIES-R-AT-NODE-CLASS', 'service resistor shorted', setp('R37', 2, '5VA_P05')),
         ('J_SV2-GROUP', 'analog node on the DAQ strip', setp('R54', 1, 'RAIL_LOW')),
         ('SRV-EACH-NODE-ONCE', 'same node on both strips', setp('R54', 1, 'ADC_CS')),
         ('SRV-COVERS-ODBIOR', 'MEAS_COIL_LOW missing (resistor on a dead net)', setp('R44', 1, 'NC')),
         ('CSV-J_BP', 'J_BP.csv out of date (netlist moved MEAS_EN)', swap('J_BP2', 14, 18)),
         ('CSV-SERWIS', 'SERWIS.csv out of date (strip order changed)', swap('J_SV2', 2, 3)),
         ('CSV-SERWIS', 'resistor value differs from SERWIS.csv (R45 10K)', setf('R45', 'value', '10K')),
         ('PARTS-S1-SOURCES', 'new resistor as 0805', setf('R14', 'fp', 'Resistor_SMD:R_0805_2012Metric')),
         ('PARTS-S1-SOURCES', 'standing THT resistor not from the register', setf('R14', 'fp', R_STAND)),
         ('PARTS-S1-SOURCES', '1210 outside the C12/C13 exception', setf('C9', 'fp', 'Capacitor_SMD:C_1210_3225Metric')),
         ('PARTS-PRECISION-SERIES', 'window resistor R5 at 25 ppm/K', setf('R5', 'mpn', 'RT1206BRD076K04L')),
         ('R2-CIRCUIT-KEPT', 'comparator inputs swapped', swap('U3', 2, 3)),
         ('R2-CIRCUIT-KEPT', 'SW1 pole B as in R2 (C&K 7201 mapping)', lambda cc: cc['SW1']['pins'].update({'4': G, '6': 'NC'}))]
    neg = []
    for target, title, fn in M:
        by = mutate(c, fn); neg.append({'mutation': title, 'target': target, 'detected': target in by, 'by': by})
    zero = mutate(c, lambda cc: None); neg.append({'mutation': 'null control (no change)', 'target': None, 'detected': bool(zero), 'by': zero})
    (P / 'verification/s1-checks.json').write_text(json.dumps({'checks': base, 'negative_controls': neg, 'p03_reference': 'reference/P03-R6-J_BP.csv (p03-r6-pcb b094fa7)',
                                                               'scope': 'Netlist/BOM contract only; no PCB exists in this package.'}, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    fail = [t['id'] for t in base if not t['pass']]; miss = [t['mutation'] for t in neg[:-1] if not t['detected']]
    print('S1 checks', len(base) - len(fail), '/', len(base), '; mutations', len(M) - len(miss), '/', len(M), '; null control', 'clean' if not zero else zero)
    for t in base:
        if not t['pass']: print('  FAIL', t['id'], t['detail'])
    sys.exit(1 if fail or miss or zero else 0)
