"""P11-R2 electrical checks on the EXPORTED netlist (verification/P11.xml) and the variant column of docs/parts.json.
1. R1 contact logic carried over 1:1 (reference/P11-R1-parts.json), no motor / TAP / sensor nets left on P11, single PANEL_3V3 feed.
2. Variant sources (P11-3): LOGGER = R1 fitted, P04 absent; FULL = P04 present (R40 100R from 3V3_IO), R1 DNP. Exactly one source each.
3. Resistive nodal model of all 2^8 = 256 contact states (key, L1, L2, TEST bridge, STOP, TEST plug, ARM, MARK) in both variants with
   the receivers' real loads: P03 R6 (R27/R6/R8 10k pull-downs, R5 10k MARK pull-up; reference/P03-R6-parts-panel.json) and, for FULL,
   P04-R2.1 (R41/R23, R42/R24, R4/R5 SAFE_N, R2/R3 ARM; reference/P04-R2.1-parts.json - P04 in S1 does not exist yet). Corners: rail
   3.18 V (R1 assumption) for H, 3.42 V for L; loads -1 %, series resistors +1 %.
4. R1 topology checks (open wire kills MECH), contact currents for the gold-contact requirement, R1 dissipation on a PANEL_3V3 short.
Negative controls mutate the netlist / variant and must be detected. Static model only: no contact bounce, timing or leakage budget."""
from pathlib import Path
import xml.etree.ElementTree as ET, json, copy, itertools
import numpy as np
P = Path(__file__).resolve().parents[1]
def read(path):
    root = ET.parse(path).getroot(); c = {x.get('ref'): {'pins': {}, 'value': x.findtext('value')} for x in root.findall('./components/comp')}
    for n in root.findall('./nets/net'):
        name = n.get('name').split('/')[-1]
        for x in n.findall('node'): c[x.get('ref')]['pins'][x.get('pin')] = 'NC' if name.startswith('unconnected-') else name
    return c
def ohms(s):
    s = s.split(' / ')[0].upper(); m = 1000 if 'K' in s else 1
    return float(s.replace('K', '').replace('R', '')) * m
R1P = json.loads((P / 'reference/P11-R1-parts.json').read_text(encoding='utf-8'))
CORE = json.loads((P / 'reference/P03-R6-parts-panel.json').read_text(encoding='utf-8'))
SAFE = json.loads((P / 'reference/P04-R2.1-parts.json').read_text(encoding='utf-8'))
SWITCHES = ['X11', 'X12', 'X13', 'X14', 'X15', 'X16', 'X17']
# Functional contact pairs (terminal numbers as in R1) and the state that closes them.
PAIRS = [('X15', 1, 2, lambda s: s['key']), ('X12', 1, 2, lambda s: not s['l1']), ('X12', 3, 4, lambda s: not s['l1']),
         ('X13', 1, 2, lambda s: not s['l2']), ('X13', 3, 4, lambda s: not s['l2']), ('X8', 10, 11, lambda s: s['loop']),
         ('X16', 1, 2, lambda s: not s['stop']), ('X17', 1, 2, lambda s: s['test']), ('X11', 1, 2, lambda s: s['arm']), ('X14', 1, 2, lambda s: s['mark'])]
STATE_KEYS = ['key', 'l1', 'l2', 'loop', 'stop', 'test', 'arm', 'mark']
RAIL_H, RAIL_L, RCONT = 3.18, 3.42, 0.05
VIH = {'LVC': 2.0, 'MCP23017': 0.8 * 3.3, 'P04_HC08': 2.4, 'SAFE_N': 2.7, 'HC14': 2.4}; VIL = 0.8
def variant_sources(c, parts, variant):
    """Sources feeding PANEL_3V3 from 3V3_IO in a variant: list of (name, ohms)."""
    src = []
    r = c.get('R1')
    if r and parts.get('R1', {}).get('variant', {}).get(variant) == 'fitted' and sorted(r['pins'].values()) == ['3V3_IO', 'PANEL_3V3']:
        src.append(('P11 R1', ohms(r['value'])))
    if variant == 'FULL':
        assert SAFE['R40']['pins'] == {'1': '3V3_IO', '2': 'PANEL_3V3'}
        if 'PANEL_3V3' in c['J_P12']['pins'].values(): src.append(('P04 R40', ohms(SAFE['R40']['value'])))
    return src
def loads(variant):
    """(net_a, net_b_or_rail, ohms, kind) for the receivers; node names checked against the frozen parts lists."""
    out = []
    for r, n in [('R27', 'TEST_KEY'), ('R6', 'LOGGER_CLEAR'), ('R8', 'TEST_PRESENT')]:
        assert CORE[r]['pins'] == {'1': n, '2': 'GND'}; out.append((n, 'GND', ohms(CORE[r]['value']), 'load'))
    assert CORE['R5']['pins'] == {'1': '3V3_CORE', '2': 'MARK'}; out.append(('MARK', '3V3_CORE', ohms(CORE['R5']['value']), 'pullup'))
    if variant == 'FULL':
        for ser, pd, n, inner in [('R41', 'R23', 'TEST_KEY', 'TEST_KEY_P04'), ('R42', 'R24', 'MECH_OK', 'MECH_OK_P04')]:
            assert SAFE[ser]['pins'] == {'1': n, '2': inner} and SAFE[pd]['pins'] == {'1': inner, '2': 'GND'}
            out += [(n, inner, ohms(SAFE[ser]['value']), 'series'), (inner, 'GND', ohms(SAFE[pd]['value']), 'load')]
        assert SAFE['R4']['pins'] == {'1': 'STOP_NC_OUT', '2': 'SAFE_N'} and SAFE['R5']['pins'] == {'1': 'SAFE_N', '2': 'GND'}
        out += [('STOP_NC_OUT', 'SAFE_N', ohms(SAFE['R4']['value']), 'series'), ('SAFE_N', 'GND', ohms(SAFE['R5']['value']), 'load')]
        assert SAFE['R2']['pins'] == {'1': '3V3_IO', '2': 'ARM_BUTTON_N'} and SAFE['R3']['pins'] == {'1': 'ARM_BUTTON_N', '2': 'ARM_CONTACT'}
        out += [('ARM_BUTTON_N', '3V3_IO', ohms(SAFE['R2']['value']), 'pullup'), ('ARM_BUTTON_N', 'ARM_CONTACT', ohms(SAFE['R3']['value']), 'series')]
    return out
RECEIVERS = {'LOGGER': {'TEST_KEY': 'LVC', 'LOGGER_CLEAR': 'LVC', 'TEST_PRESENT': 'LVC', 'MARK': 'MCP23017'},
             'FULL': {'TEST_KEY': 'LVC', 'LOGGER_CLEAR': 'LVC', 'TEST_PRESENT': 'LVC', 'MARK': 'MCP23017',
                      'TEST_KEY_P04': 'P04_HC08', 'MECH_OK_P04': 'P04_HC08', 'SAFE_N': 'SAFE_N', 'ARM_BUTTON_N': 'HC14'}}
def expected(s):
    mech = s['key'] and not s['l1'] and not s['l2'] and s['loop']
    return {'TEST_KEY': s['key'], 'LOGGER_CLEAR': not s['l1'] and not s['l2'], 'TEST_PRESENT': s['test'], 'MARK': not s['mark'],
            'TEST_KEY_P04': s['key'], 'MECH_OK_P04': mech, 'SAFE_N': not s['stop'], 'ARM_BUTTON_N': not s['arm']}
def solve(c, parts, variant, s, rail):
    """Nodal analysis. Rails: GND 0 V, 3V3_IO and 3V3_CORE = rail. Returns node voltages, source current, contact currents."""
    hi = rail >= 3.3
    el = []   # (a, b, R)
    for name, r in variant_sources(c, parts, variant): el.append(('3V3_IO', 'PANEL_3V3', r * (1.01 if not hi else 0.99), name))
    for a, b, r, kind in loads(variant):
        f = (0.99 if kind == 'load' else 1.01) if not hi else (1.01 if kind == 'load' else 0.99)
        el.append((a, b, r * f, kind))
    for ref, pa, pb, on in PAIRS:
        if on(s) and ref in c:
            x, y = c[ref]['pins'].get(str(pa), 'NC'), c[ref]['pins'].get(str(pb), 'NC')
            if 'NC' not in (x, y): el.append((x, y, RCONT, f'{ref}.{pa}-{pb}'))
    # extra parts introduced by a mutation (two-pin, treated as 1 kOhm load)
    for ref, v in c.items():
        if ref.startswith('LED'): el.append((v['pins']['1'], v['pins']['2'], 1000.0, ref))
    fixed = {'GND': 0.0, '3V3_IO': rail, '3V3_CORE': rail}
    nodes = sorted({n for a, b, _, _ in el for n in (a, b)} - set(fixed))
    idx = {n: i for i, n in enumerate(nodes)}; G = np.zeros((len(nodes), len(nodes))); I = np.zeros(len(nodes))
    for n in nodes: G[idx[n], idx[n]] += 1e-9          # 1 GOhm leakage: floating nodes resolve to 0 V
    for a, b, r, _ in el:
        g = 1 / r
        for x, y in ((a, b), (b, a)):
            if x in idx:
                G[idx[x], idx[x]] += g
                if y in idx: G[idx[x], idx[y]] -= g
                else: I[idx[x]] += g * fixed[y]
    v = dict(fixed); v.update({n: float(x) for n, x in zip(nodes, np.linalg.solve(G, I))} if nodes else {})
    isrc = sum((v['3V3_IO'] - v['PANEL_3V3']) / r for a, b, r, k in el if (a, b) == ('3V3_IO', 'PANEL_3V3')) if 'PANEL_3V3' in v else 0.0
    icont = {k: abs(v[a] - v[b]) / r for a, b, r, k in el if k.startswith('X')}
    return v, isrc, icont
def contact_graph(c, s, broken=None):
    """R1 topology: which receiver nets are reachable from PANEL_3V3 through closed contacts (no resistors)."""
    g = {}
    for ref, pa, pb, on in PAIRS[:8]:
        if not on(s) or broken in [(ref, pa), (ref, pb)] or ref not in c: continue
        x, y = c[ref]['pins'].get(str(pa), 'NC'), c[ref]['pins'].get(str(pb), 'NC')
        if 'NC' in (x, y): continue
        g.setdefault(x, set()).add(y); g.setdefault(y, set()).add(x)
    seen = {'PANEL_3V3'}; todo = ['PANEL_3V3']
    while todo:
        for n in g.get(todo.pop(), []):
            if n not in seen: seen.add(n); todo.append(n)
    return {k: k in seen for k in ['MECH_OK', 'TEST_KEY', 'LOGGER_CLEAR', 'STOP_NC_OUT', 'TEST_PRESENT', 'GND']}
def check(c, parts):
    out = []
    def ok(k, v, note=''): out.append({'id': k, 'pass': bool(v), 'note': note})
    r1j = R1P['J11']['pins']
    ok('R1-CONTACT-FIELD', c.get('J11', {}).get('pins') == {k: v for k, v in r1j.items() if int(k) <= 18} and all(r1j[k] == 'NC' for k in ('19', '20')),
       'J11.1..18 = R1 J11.1..18 (R1 19/20 were NC)')
    for r in SWITCHES: ok('R1-CONTACT-' + r, c.get(r, {}).get('pins') == R1P[r]['pins'], 'functional terminals as R1')
    x8 = c.get('X8', {}).get('pins', {})
    ok('TEST-PORT-10-11', x8.get('10') == R1P['X8']['pins']['10'] == 'LOOP_OUT' and x8.get('11') == R1P['X8']['pins']['11'] == 'MECH_OK'
       and all(x8.get(str(i)) == 'NC' for i in range(1, 13) if i not in (10, 11)), 'X8 cavity 10/11 as R1, other cavities not on P11')
    ok('TEST-FIELD-J8', c.get('J8', {}).get('pins') == {'1': 'LOOP_OUT', '2': 'MECH_OK'})
    ok('PORTS-L1-L2-OFF-P11', all(set(c.get(r, {}).get('pins', {'x': 'x'}).values()) == {'NC'} for r in ('X2', 'X3')), 'P11-4/P11-5')
    old = {'ECU_P1', 'EGR_P1', 'T_EGR_P1', 'T_EGR_P3', '5V_SENSOR', 'AGND_SENSOR'} | {f'TAP_P{i}' for i in (1, 3, 4, 5, 6)}
    nets = {n for v in c.values() for n in v['pins'].values()}
    ok('NO-MOTOR-TAP-SENSOR-NETS', not (nets & old), 'decisions P11-4, P11-5')
    ok('SCOPE', all(c.get(r, {}).get('pins') == {'1': 'N_J_SCOPE_HOT', '2': 'GND'} for r in ('J6', 'X6')))
    ok('PARTS-SET', set(c) == {'J_P12', 'R1', 'J11', 'J8', 'J6', 'X6', 'X2', 'X3', 'X8'} | set(SWITCHES), 'no active parts, no LEDs, no added pulls on P11')
    def members(n): return sorted((r, p) for r, v in c.items() for p, net in v['pins'].items() if net == n)
    ok('3V3_IO-ONLY-TO-R1', members('3V3_IO') == [('J_P12', '20'), ('R1', '1')], 'the only path 3V3_IO -> PANEL_3V3 is R1')
    pan = members('PANEL_3V3')
    ok('PANEL_3V3-FEED', ('J_P12', '2') in pan and ('R1', '2') in pan and not any(r.startswith(('R', 'LED')) and r != 'R1' for r, _ in pan))
    ok('R1-VALUE', 'R1' in c and ohms(c['R1']['value']) == 100.0)
    # variants
    srcL, srcF = variant_sources(c, parts, 'LOGGER'), variant_sources(c, parts, 'FULL')
    ok('VARIANT-LOGGER-ONE-SOURCE', [n for n, _ in srcL] == ['P11 R1'], f'{srcL}')
    ok('VARIANT-FULL-ONE-SOURCE', [n for n, _ in srcF] == ['P04 R40'], f'{srcF} (R1 must be DNP with P04)')
    ok('BOM-R1-VARIANT', parts.get('R1', {}).get('variant') == {'LOGGER': 'fitted', 'FULL': 'DNP'}, 'DNP note in BOM')
    # nodal model, 256 states x 2 variants
    truth, worst = [], {}
    for variant in ('LOGGER', 'FULL'):
        bad = 0; vmin_h = {}; vmax_l = {}; imax = 0.0; icmax = 0.0; icmin = 9.0
        for bits in itertools.product([False, True], repeat=8):
            s = dict(zip(STATE_KEYS, bits)); e = expected(s)
            vh, isrc, ic = solve(c, parts, variant, s, RAIL_H); vl, _, _ = solve(c, parts, variant, s, RAIL_L)
            row = {'variant': variant, **{k: int(b) for k, b in s.items()}, 'levels': {}}
            for net, kind in RECEIVERS[variant].items():
                if e[net]: good = vh.get(net, 0.0) >= VIH[kind]; vmin_h[net] = min(vmin_h.get(net, 9), vh.get(net, 0.0))
                else: good = vl.get(net, 0.0) <= VIL; vmax_l[net] = max(vmax_l.get(net, -9), vl.get(net, 0.0))
                row['levels'][net] = {'expected': 'H' if e[net] else 'L', 'V': round(vh.get(net, 0.0) if e[net] else vl.get(net, 0.0), 3), 'ok': good}
                bad += not good
            imax = max(imax, isrc); live = [x for x in ic.values() if x > 1e-6]
            if live: icmax = max(icmax, max(live)); icmin = min(icmin, min(live))
            truth.append(row)
        worst[variant] = {'V_H_min': {k: round(v, 3) for k, v in vmin_h.items()}, 'V_L_max': {k: round(v, 3) for k, v in vmax_l.items()},
                          'I_source_max_mA': round(imax * 1e3, 3), 'I_contact_max_mA': round(icmax * 1e3, 3), 'I_contact_min_uA': round(icmin * 1e6, 1) if icmin < 9 else None}
        ok(f'NODAL-256-{variant}', bad == 0, f'{bad} receiver levels wrong; thresholds H {VIH}, L <= {VIL} V')
        ok(f'NO-SHORT-{variant}', imax < 5e-3, f'max source current {imax * 1e3:.2f} mA (no closed-contact path PANEL_3V3 -> GND)')
    # R1 topology checks (as R1 verify_electrical.py), now with ARM/MARK isolated from PANEL_3V3
    base = dict(key=1, l1=0, l2=0, loop=1, stop=0, test=1, arm=1, mark=1)
    tt = [contact_graph(c, dict(zip(STATE_KEYS, b))) for b in itertools.product([False, True], repeat=8)]
    ok('PANEL_3V3-NEVER-TO-GND', not any(t['GND'] for t in tt), 'ARM / MARK only to GND, never bridged to PANEL_3V3')
    for r, p in [('X15', 1), ('X12', 1), ('X12', 2), ('X13', 1), ('X13', 2), ('X8', 10), ('X8', 11)]:
        ok(f'OPEN-WIRE-KILLS-{r}.{p}', not contact_graph(c, base, (r, p))['MECH_OK'])
    ok('STOP-OPEN-WIRE', not contact_graph(c, base, ('X16', 1))['STOP_NC_OUT'])
    # R1 power on a PANEL_3V3 short and gold contact duty
    pr = RAIL_L ** 2 / (100 * 0.99); rated = parts.get('R1', {}).get('power_W', 0)
    ok('R1-SHORT-POWER', pr <= 0.5 * rated, f'{pr * 1e3:.0f} mW at {RAIL_L} V vs {rated} W rated (<= 50 %)')
    ok('BUTTONS-GOLD', all(parts.get(r, {}).get('gold') for r in SWITCHES), 'P11-7')
    return out, truth, worst
if __name__ == '__main__':
    c = read(P / 'verification/P11.xml'); parts = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
    base, truth, worst = check(c, parts); neg = []
    def trial(name, fn, fp=None):
        cc = copy.deepcopy(c); pp = copy.deepcopy(parts); fn(cc)
        if fp: fp(pp)
        bad = [x['id'] for x in check(cc, pp)[0] if not x['pass']]; neg.append({'mutation': name, 'caught': bool(bad), 'checks': bad})
    def setpin(r, p, n): return lambda x: x[r]['pins'].__setitem__(p, n)
    trial('R1 brak (nieobsadzony w LOGGER)', lambda x: x.pop('R1'))
    trial('R1 obsadzony przy P04 (wariant FULL)', lambda x: None, lambda p: p['R1']['variant'].__setitem__('FULL', 'fitted'))
    trial('R1 DNP w LOGGER (BOM)', lambda x: None, lambda p: p['R1']['variant'].__setitem__('LOGGER', 'DNP'))
    trial('R1.1 -> 3V3_CORE', setpin('R1', '1', '3V3_CORE'))
    trial('R1 omijany: J_P12.20 -> PANEL_3V3', setpin('J_P12', '20', 'PANEL_3V3'))
    trial('R1 = 10R', lambda x: x['R1'].__setitem__('value', '10R'))
    for r, p, n in [('X13', '4', 'PANEL_3V3'), ('X12', '2', 'TEST_KEY'), ('X15', '2', 'PANEL_3V3'), ('X11', '1', 'PANEL_3V3'), ('X14', '1', 'PANEL_3V3'),
                    ('X16', '1', 'GND'), ('X17', '2', 'TEST_KEY'), ('J8', '1', 'MECH_OK'), ('X8', '10', 'MECH_OK'), ('J11', '12', 'GND'),
                    ('X2', '1', 'ECU_P1'), ('X8', '3', '5V_SENSOR'), ('J6', '2', 'PANEL_3V3'), ('X13', '2', 'MECH_OK')]:
        trial(f'{r}.{p} -> {n}', setpin(r, p, n))
    trial('dodatkowa LED PANEL_3V3-GND', lambda x: x.update(LED99={'pins': {'1': 'PANEL_3V3', '2': 'GND'}, 'value': 'LED'}))
    trial('przycisk bez zlocenia (X14)', lambda x: None, lambda p: p['X14'].__setitem__('gold', False))
    analysis = {'worst_case': worst, 'rail_V': {'H_check': RAIL_H, 'L_check': RAIL_L}, 'contact_R_ohm': RCONT, 'thresholds_V': {'VIH': VIH, 'VIL': VIL},
                'R1_short_W': RAIL_L ** 2 / 99}
    (P / 'verification/electrical-checks.json').write_text(json.dumps({'checks': base, 'analysis': analysis, 'negative_controls': neg, 'truth_table': truth,
        'hardware_tested': False, 'scope': 'Static resistive model of the frozen receivers (P03 R6, P04-R2.1). No contact bounce, timing, leakage budget or P04 in S1.'},
        indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    print('Electrical', sum(x['pass'] for x in base), '/', len(base), 'checks;', sum(t['caught'] for t in neg), '/', len(neg), 'mutations caught')
    print(json.dumps(worst))
    fails = [x for x in base if not x['pass']]; missed = [t['mutation'] for t in neg if not t['caught']]
    for f in fails: print('FAIL', f)
    for m in missed: print('MISSED', m)
    raise SystemExit(1 if fails or missed else 0)
