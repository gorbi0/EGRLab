"""P06-R2 (format S1): independent checks of the exported netlist (verification/P06.xml) against the S1 contract:
edge-A connector J_BP, edge-B service strips J_SV1/J_SV2, Kelvin shunt RSH1 (from the footprint geometry), C3, part sources and
identity of the R1 circuit. Nothing is imported from parts.py: expected pinouts, resistor classes and exceptions are declared here;
the old connector and test-pad nets come from the exported R1 netlist (reference/P06-R1.xml), the bus pins of the neighbours from
reference/P03-R6-J_BP.csv (branch p03-r6-pcb, commit b094fa7) and reference/P05-R3-J_BP.csv (main). Every check has a netlist
mutation that must fail exactly that check, plus a null control that must stay clean. Output: verification/s1-checks.json."""
from pathlib import Path
import xml.etree.ElementTree as ET, json, copy, csv, re, sys
P = Path(__file__).resolve().parents[1]
G = 'GND'

# --- declared contract (task ZADANIE-P06-S1 2, 3, 4, 6, 7) ---
JBP = {1: G, 2: 'ADC_SCLK', 3: G, 4: 'ADC_DOUTA', 5: G, 6: 'CS_ILOG_N', 7: G, 8: 'LOGGER_CURRENT_OK', 9: G, 10: '5V_SYS', 11: G,
       12: '5V_SYS', 13: G, 14: '3V3_IO', 15: G, 16: G}
JBP_FP = 'Connector_IDC:IDC-Header_2x08_P2.54mm_Horizontal'
BUS = ('ADC_SCLK', 'ADC_DOUTA')                       # same pin numbers as J_BP2 of P03 R6 and P05 R3
DIRS = {'ADC_SCLK': 'in', 'CS_ILOG_N': 'in', 'ADC_DOUTA': 'out', 'LOGGER_CURRENT_OK': 'out'}
OPPOSITE = {'in': 'out', 'out': 'in'}
OLD_CONNECTORS = ('J1', 'J2')                         # R1: LV06, ILOG
TWICE = {'5V_SYS'}
WIRES = ('J3', 'J4', 'J5')                            # ISERIES, BYPASS force, BYPASS status stay wires (S1 5)
RAILS = {'5V_SYS', '5VA_P06', '3V3_P06', '3V3_IO'}
ANALOG = {'I_L_OUT', 'ADC_AIN', 'REF25', 'REF_BUF'}
OHM = {**{n: 1000 for n in ['5V_SYS', '5VA_P06', '3V3_P06', '3V3_IO', 'SHUNT_ENABLED', 'LOGGER_CURRENT_OK', 'CS_LOCAL_N', 'CLK_LOCAL']},
       **{n: 10000 for n in ['REF25', 'REF_BUF', 'ADC_AIN', 'I_L_OUT', 'SUP3_N', 'SUP5_N']}}
GROUP = {'J_SV1': ANALOG, 'J_SV2': RAILS | {'SUP3_N', 'SUP5_N', 'SHUNT_ENABLED', 'LOGGER_CURRENT_OK', 'CS_LOCAL_N', 'CLK_LOCAL'}}
SV_FP = 'Connector_PinHeader_2.54mm:PinHeader_1x{:02d}_P2.54mm_Horizontal'
NEW_PARTS = {'J_BP', 'J_SV1', 'J_SV2', *[f'R{i}' for i in range(25, 39)], 'C17'}   # C17: 100 nF on 5VA at J5 (2.10, review F7)
R_SMD = 'Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder'; C_SMD = 'Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder'
R_STAND = 'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P5.08mm_Vertical'
EXC_FP = {'R6': 'Resistor_THT:R_Axial_DIN0411_L9.9mm_D3.6mm_P15.24mm_Horizontal', 'R21': 'P06:R_PR02_P17.78',
          'C3': 'Capacitor_THT:CP_Radial_D6.3mm_P2.50mm', 'RSH1': 'P06:R_Shunt_Vishay_WSK2512_T1.19mm_SenseE1.70'}   # 1.10: sense pads per data sheet (parts.py shunt_fp)
PRECISION = ['R1', 'R2', 'R3', 'R4']
SHUNT_SIDE = {'ECU_P1': 'K_PLUS', 'EGR_P1': 'K_MINUS'}   # force net -> sense net on the same end of the shunt (R1 functions)


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


def pads(fp):
    """SMD pad centres and areas from the footprint copied into the project (eda/libraries/<lib>.pretty)."""
    lib, name = fp.split(':'); f = P / 'eda/libraries' / (lib + '.pretty') / (name + '.kicad_mod')
    if not f.exists(): return {}                      # footprint not in the project library: check fails
    t = f.read_text()
    out = {}
    for m in re.finditer(r'\(pad "(\d+)" smd \w+\s*\(at ([-\d.]+) ([-\d.]+)[^)]*\)\s*\(size ([-\d.]+) ([-\d.]+)\)', t):
        out[m[1]] = (float(m[2]), float(m[3]), float(m[4]) * float(m[5]))
    return out


R1 = read(P / 'reference/P06-R1.xml')
OLD = {}
for j in OLD_CONNECTORS:
    for n in R1[j]['pins'].values():
        if n not in (G, 'NC'): OLD[n] = OLD.get(n, 0) + 1
TP_R1 = {x['pins']['1'] for r, x in R1.items() if r.startswith('TP')} - {G}
NB = {}
for name in ('P03-R6-J_BP.csv', 'P05-R3-J_BP.csv'):
    NB[name] = {r['siec']: (r['zlacze'], int(r['pin']), r['kierunek']) for r in rows(P / 'reference' / name)}


def check(c):
    out = []
    def ok(k, v, d=None): out.append({'id': k, 'pass': bool(v), 'detail': d})
    def pinmap(r): return {int(p): n for p, n in c[r]['pins'].items()}
    def members(net): return {(r, p) for r, x in c.items() for p, n in x['pins'].items() if n == net}
    jb = pinmap('J_BP')
    # --- J_BP ---
    ok('JBP-PINOUT', jb == JBP, jb)
    ok('JBP-FOOTPRINT', c['J_BP']['fp'] == JBP_FP, c['J_BP']['fp'])
    bus = {n: [p for p, x in jb.items() if x == n] for n in BUS}
    ok('JBP-BUS-PINS-AS-P03R6-P05R3', all(bus[n] == [NB[f][n][1]] and NB[f][n][0] == 'J_BP2' for n in BUS for f in NB), bus)
    ok('JBP-ODD-PINS-GND', all(jb[p] == G for p in jb if p % 2))
    on = {}
    for n in jb.values():
        if n != G: on[n] = on.get(n, 0) + 1
    want = {n: (2 if n in TWICE else 1) for n in OLD}
    ok('JBP-OLD-NETS-EXACTLY-ONCE', on == want, {'on_jbp': on, 'expected': want})
    wire = {n for r in WIRES for n in c[r]['pins'].values()} - {G, 'NC'}
    ok('JBP-NO-ISERIES-BYPASS', not (set(on) & (wire | {'K_PLUS', 'K_MINUS'})), sorted(wire))
    # --- CSV contract for P12, directions against the counterpart on P03 R6 ---
    csvr = rows(P / 'docs/J_BP.csv')
    ok('CSV-J_BP', {(r['zlacze'], int(r['pin'])): r['siec'] for r in csvr} == {('J_BP', p): n for p, n in jb.items()})
    d = {r['siec']: r['kierunek'] for r in csvr if r['siec'] in DIRS}
    p03 = NB['P03-R6-J_BP.csv']
    ok('CSV-DIRECTIONS-VS-P03R6', d == DIRS and all(n in p03 and p03[n][2] == OPPOSITE[k] for n, k in DIRS.items()),
       {n: (k, p03.get(n)) for n, k in d.items()})
    # --- service strips ---
    seen = {}
    for j in ('J_SV1', 'J_SV2'):
        s = pinmap(j); n = max(s)
        ok(j + '-MAX-13-PINS', sorted(s) == list(range(1, n + 1)) and n <= 13 and c[j]['fp'] == SV_FP.format(n))
        ok(j + '-GND-ENDS', s[1] == G and s[n] == G)
        good = True; nodes = []; node_at = {}
        for p in range(2, n):
            net = s.get(p, 'NC')
            if net == G: continue                         # interior GND allowed (probe ground)
            m = members(net); rr = [r for r, q in m if r.startswith('R')]
            if len(rr) == 1:                              # the node actually probed through this pin (independent of net names)
                raw = c[rr[0]]['pins'].get('1') if (rr[0], '2') in m else c[rr[0]]['pins'].get('2')
                nodes.append(raw); seen[raw] = seen.get(raw, 0) + 1; node_at[p] = raw
            if not net.startswith('SRV_') or len(m) != 2 or len(rr) != 1 or (j, str(p)) not in m or (rr[0], '2') not in m: good = False; continue
            node = c[rr[0]]['pins'].get('1')
            if node != net[4:] or node not in OHM or abs(ohms(c[rr[0]]['value']) - OHM[node]) > 1e-6: good = False; continue
            if len(members(node)) < 2: good = False       # the node must reach something besides its service resistor (3V3_IO: only J_BP.14)
        ok(j + '-SERIES-R-AT-NODE-CLASS', good)
        ok(j + '-GROUP', set(nodes) <= GROUP[j], sorted(nodes))
        def nb(q): return G if s.get(q) == G else node_at.get(q)
        def fine(x):  # neighbour allowed next to a rail: GND, another rail, or a 10K line that is not analog
            return x == G or x in RAILS or (x in OHM and OHM[x] == 10000 and x not in ANALOG)
        bad = [(p, node_at[p], q, nb(q)) for p in node_at for q in (p - 1, p + 1)
               if (node_at[p] in RAILS and not fine(nb(q))) or (node_at[p] in ANALOG and nb(q) in RAILS)]
        ok(j + '-NEIGHBOURS', not bad, bad)
    ok('SRV-EACH-NODE-ONCE', all(v == 1 for v in seen.values()), {k: v for k, v in seen.items() if v != 1})
    ok('SRV-COVERS-R1-TESTPADS', set(seen) == TP_R1, {'missing': sorted(TP_R1 - set(seen)), 'extra': sorted(set(seen) - TP_R1)})
    sv = {(r['zlacze'], int(r['pin'])): r['siec'] for r in rows(P / 'docs/SERWIS.csv')}
    rz = {(r['zlacze'], int(r['pin'])): r['rezystor'].split()[:2] for r in rows(P / 'docs/SERWIS.csv') if r['rezystor'] != '-'}
    def res_on(j, p):
        rr = [r for r, q in members(pinmap(j)[p]) if r.startswith('R')]
        return [rr[0], c[rr[0]]['value']] if len(rr) == 1 else None
    ok('CSV-SERWIS', sv == {(j, p): (n[4:] if n.startswith('SRV_') else n) for j in ('J_SV1', 'J_SV2') for p, n in pinmap(j).items()}
       and all(res_on(j, p) == v for (j, p), v in rz.items()) and set(rz) == {(j, p) for j in ('J_SV1', 'J_SV2') for p, n in pinmap(j).items() if n != G})
    # --- Kelvin shunt from the footprint geometry: 4 pads, force pads = two largest, sense pad on the same end as its force pad ---
    sp = pads(c['RSH1']['fp']); net = c['RSH1']['pins']
    good = len(sp) == 4 and set(net) == set(sp) and '2512' in c['RSH1']['fp']
    if good:
        force = sorted(sp, key=lambda k: -sp[k][2])[:2]; sense = [k for k in sp if k not in force]
        side = lambda k: sp[k][0] > 0
        good = ({net[k] for k in force} == set(SHUNT_SIDE) and all(net[s] == SHUNT_SIDE[net[f]] for f in force for s in sense if side(s) == side(f))
                and len({side(k) for k in force}) == 2 and len({side(k) for k in sense}) == 2)
    ok('RSH1-KELVIN-2512', good, {k: (sp.get(k), net.get(k)) for k in sorted(set(sp) | set(net))})
    ok('RSH1-5MOHM', c['RSH1']['value'].split()[0] == '5m')
    ok('C3-220U', c['C3']['value'].split()[0] == '220u' and set(c['C3']['pins'].values()) == {'5VA_P06', G}, c['C3']['value'])
    # --- part sources (S1 1/4/9 + exceptions named in the task / README) ---
    bad = []
    for r, x in c.items():
        if r in EXC_FP:
            if x['fp'] != EXC_FP[r]: bad.append(r)
        elif re.fullmatch(r'R\d+', r):
            if not (x['fp'] == R_SMD or (x['fp'] == R_STAND and x['mpn'].startswith('MF0207') and 'owned' in x['mpn'])): bad.append(r)
        elif re.fullmatch(r'C\d+', r):
            if x['fp'] != C_SMD: bad.append(r)
        if re.search(r'_0603_|_0805_', x['fp']): bad.append(r)
    ok('PARTS-S1-SOURCES', not bad, bad)
    ok('PARTS-PRECISION-SERIES', all(c[r]['mpn'].startswith('RT1206BRD07') for r in PRECISION), {r: c[r]['mpn'] for r in PRECISION})
    # --- R1 circuit kept (everything except the replaced connectors, the shunt part and the test pads) ---
    diff = []
    for r, x in R1.items():
        if r in OLD_CONNECTORS or r.startswith('TP') or r == 'RSH1': continue
        if r not in c: diff.append((r, 'missing')); continue
        for p, n in x['pins'].items():
            if c[r]['pins'].get(p) != n and not (r == 'J3' and n == 'NC' and p not in c[r]['pins']):   # 1.10: J3 pads 3/4 (empty) dropped
                diff.append((r, p, n, c[r]['pins'].get(p)))
    extra = sorted(set(c) - set(R1) - NEW_PARTS) + sorted(NEW_PARTS - set(c))
    ok('R1-CIRCUIT-KEPT', not diff and not extra, {'diff': diff[:10], 'extra_or_missing': extra})
    return out


def mutate(c, fn):
    cc = copy.deepcopy(c); fn(cc); return [t['id'] for t in check(cc) if not t['pass']]


if __name__ == '__main__':
    c = read(P / 'verification/P06.xml'); base = check(c)
    def setp(r, pin, v): return lambda cc: cc[r]['pins'].__setitem__(str(pin), v)
    def setf(r, f, v): return lambda cc: cc[r].__setitem__(f, v)
    def swap(r, a, b):
        def f(cc): p = cc[r]['pins']; p[str(a)], p[str(b)] = p[str(b)], p[str(a)]
        return f
    def find(j, net): return next(p for p, n in c[j]['pins'].items() if n == 'SRV_' + net)
    def rof(net): return next(r for r, x in c.items() if r.startswith('R') and x['pins'].get('2') == 'SRV_' + net)
    M = [('JBP-PINOUT', 'CS_ILOG_N and LOGGER_CURRENT_OK swapped', swap('J_BP', 6, 8)),
         ('JBP-FOOTPRINT', 'vertical IDC header', setf('J_BP', 'fp', 'Connector_IDC:IDC-Header_2x08_P2.54mm_Vertical')),
         ('JBP-BUS-PINS-AS-P03R6-P05R3', 'ADC_SCLK and ADC_DOUTA swapped', swap('J_BP', 2, 4)),
         ('JBP-ODD-PINS-GND', 'odd pin 15 carries 3V3_IO', setp('J_BP', 15, '3V3_IO')),
         ('JBP-OLD-NETS-EXACTLY-ONCE', 'second 5V_SYS pin lost', setp('J_BP', 12, G)),
         ('JBP-OLD-NETS-EXACTLY-ONCE', 'CS_ILOG_N duplicated on reserve pin 16', setp('J_BP', 16, 'CS_ILOG_N')),
         ('JBP-NO-ISERIES-BYPASS', 'SW_RAW routed to reserve pin 16', setp('J_BP', 16, 'SW_RAW')),
         ('J_SV2-MAX-13-PINS', '14th pin on J_SV2', setp('J_SV2', 14, G)),
         ('J_SV1-MAX-13-PINS', 'J_SV1 vertical header', setf('J_SV1', 'fp', 'Connector_PinHeader_2.54mm:PinHeader_1x07_P2.54mm_Vertical')),
         ('J_SV1-GND-ENDS', 'first pin of J_SV1 not GND', setp('J_SV1', 1, 'SRV_I_L_OUT')),
         ('J_SV2-GND-ENDS', 'last pin of J_SV2 not GND', setp('J_SV2', 13, 'SRV_CLK_LOCAL')),
         ('J_SV2-NEIGHBOURS', '3V3_IO next to SHUNT_ENABLED (1K logic)', swap('J_SV2', find('J_SV2', 'SUP3_N'), find('J_SV2', 'SHUNT_ENABLED'))),
         ('J_SV2-NEIGHBOURS', 'interior GND pin 5 swapped with SHUNT_ENABLED (3V3_P06 next to 1K logic)', swap('J_SV2', 5, find('J_SV2', 'SHUNT_ENABLED'))),
         ('J_SV1-NEIGHBOURS', 'rail on the analog strip next to I_L_OUT (ADC_AIN resistor moved to 5VA_P06)', setp(rof('ADC_AIN'), 1, '5VA_P06')),
         ('J_SV1-GROUP', 'logic node on the analog strip', setp(rof('ADC_AIN'), 1, 'CS_ILOG_N')),
         ('J_SV2-GROUP', 'analog node on the rail/logic strip', setp(rof('CLK_LOCAL'), 1, 'I_DIV')),
         ('J_SV2-SERIES-R-AT-NODE-CLASS', 'pin wired straight to the node (no resistor)', setp('J_SV2', find('J_SV2', 'CS_LOCAL_N'), 'CS_LOCAL_N')),
         ('J_SV1-SERIES-R-AT-NODE-CLASS', 'REF25 through 1K instead of 10K', setf(rof('REF25'), 'value', '1K')),
         ('J_SV2-SERIES-R-AT-NODE-CLASS', 'SUP3_N through 1K instead of 10K', setf(rof('SUP3_N'), 'value', '1K')),
         ('J_SV2-SERIES-R-AT-NODE-CLASS', 'service resistor shorted', setp(rof('5V_SYS'), 2, '5V_SYS')),
         ('SRV-EACH-NODE-ONCE', 'same node on both strips', setp(rof('CLK_LOCAL'), 1, 'REF25')),
         ('SRV-COVERS-R1-TESTPADS', 'CLK_LOCAL missing (resistor on a dead net)', setp(rof('CLK_LOCAL'), 1, 'NC')),
         ('CSV-J_BP', 'J_BP.csv out of date (netlist moved 3V3_IO)', swap('J_BP', 14, 16)),
         ('CSV-SERWIS', 'SERWIS.csv out of date (strip order changed)', swap('J_SV2', find('J_SV2', 'CS_LOCAL_N'), find('J_SV2', 'CLK_LOCAL'))),
         ('CSV-SERWIS', 'resistor value differs from SERWIS.csv', setf(rof('5VA_P06'), 'value', '10K')),
         ('RSH1-KELVIN-2512', 'force and sense swapped on the ECU end', swap('RSH1', 1, 2)),
         ('RSH1-KELVIN-2512', 'Kelvin pair crossed', swap('RSH1', 2, 3)),
         ('RSH1-KELVIN-2512', 'shunt in a 2-pad 2512', setf('RSH1', 'fp', 'Resistor_SMD:R_2512_6332Metric')),
         ('RSH1-5MOHM', 'shunt 50 mOhm', setf('RSH1', 'value', '50m')),
         ('C3-220U', 'C3 back to 470 uF', setf('C3', 'value', '470u / 16V')),
         ('PARTS-S1-SOURCES', 'new resistor as 0805', setf('R14', 'fp', 'Resistor_SMD:R_0805_2012Metric')),
         ('PARTS-S1-SOURCES', 'standing THT resistor not from the register', setf('R14', 'fp', R_STAND)),
         ('PARTS-S1-SOURCES', 'electrolytic outside the C3 exception', setf('C4', 'fp', 'Capacitor_THT:CP_Radial_D5.0mm_P2.00mm')),
         ('PARTS-S1-SOURCES', 'R21 as 2512 without justification in the exception list', setf('R21', 'fp', 'Resistor_SMD:R_2512_6332Metric')),
         ('PARTS-PRECISION-SERIES', 'divider resistor R3 1 %', setf('R3', 'mpn', 'RC1206FR-075K11L')),
         ('R1-CIRCUIT-KEPT', 'INA240 inputs swapped', swap('U1', 1, 8)),
         ('R1-CIRCUIT-KEPT', 'BYPASS commons moved', swap('SW1', 2, 3))]
    neg = []
    for target, title, fn in M:
        by = mutate(c, fn); neg.append({'mutation': title, 'target': target, 'detected': target in by, 'by': by})
    zero = mutate(c, lambda cc: None); neg.append({'mutation': 'null control (no change)', 'target': None, 'detected': bool(zero), 'by': zero})
    (P / 'verification/s1-checks.json').write_text(json.dumps({'checks': base, 'negative_controls': neg,
        'references': ['reference/P06-R1.xml (R1 export)', 'reference/P03-R6-J_BP.csv (p03-r6-pcb b094fa7)', 'reference/P05-R3-J_BP.csv (main 1d4ff38)'],
        'scope': 'Netlist/BOM contract only; no PCB exists in this package.'}, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    fail = [t['id'] for t in base if not t['pass']]; miss = [t['mutation'] for t in neg[:-1] if not t['detected']]
    print('S1 checks', len(base) - len(fail), '/', len(base), '; mutations', len(M) - len(miss), '/', len(M), '; null control', 'clean' if not zero else zero)
    for t in base:
        if not t['pass']: print('  FAIL', t['id'], t['detail'])
    for m in miss: print('  MISSED', m)
    sys.exit(1 if fail or miss or zero else 0)
