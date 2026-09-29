"""P00 R3: bench harness P00 -> P04-R2.1 checked against the frozen P04-R2.1 netlist data (review P0-01).

Inputs: requirements/harness-P04-R2.1.json (the map), reference/P04-R2.1-parts.json (frozen copy, hash in
reference/P04-R2.1-source.json), verification/P00.xml (P00 side) and the tables in docs/P00-P04-WIAZKA.md.
Every channel and every 1 k branch must land on a P04 input net that has exactly one pulldown, only IC inputs and no
IC output; the H level at the gate is computed from the real resistor values. Mutations must be detected.
Static arithmetic only; P04 ODBIOR E01-E22 remains the acceptance test.
"""
from pathlib import Path
import copy, hashlib, json, re, sys, xml.etree.ElementTree as ET

P = Path(__file__).resolve().parents[1]


def numeric(value):
    token = value.split('/')[0].strip().upper()
    m = re.fullmatch(r'(\d+)([RKM]?)(\d*)', token)
    return float(m[1] + ('.' + m[3] if m[3] else '')) * {'': 1, 'R': 1, 'K': 1e3, 'M': 1e6}[m[2]]


def load():
    req = json.loads((P / 'requirements/harness-P04-R2.1.json').read_text(encoding='utf-8'))
    src = json.loads((P / 'reference/P04-R2.1-source.json').read_text(encoding='utf-8'))
    for rel, meta in src['files'].items():
        assert hashlib.sha256((P / rel).read_bytes()).hexdigest() == meta['sha256'], 'frozen P04 copy changed: ' + rel
    parts = json.loads((P / req['p04_parts']).read_text(encoding='utf-8'))
    parts = parts if isinstance(parts, dict) else {x['ref']: x for x in parts}
    root = ET.parse(P / 'verification/P00.xml').getroot()
    p00 = {n.get('ref') + '.' + n.get('pin'): net.get('name').lstrip('/') for net in root.findall('./nets/net') for n in net.findall('node')}
    doc = (P / req['doc']).read_text(encoding='utf-8')
    return req, parts, p00, doc


def rows(doc):
    """Table rows of the harness document: first cell, then every J/TP designator and every NET_NAME of the row."""
    out = []
    for line in doc.splitlines():
        if not line.startswith('|') or set(line) <= set('|-: '):
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        out.append({'first': cells[0], 'pins': re.findall(r'\b(?:J\d+|TP\d+)\.?\d*\b', ' '.join(cells[1:])),
                    'nets': re.findall(r'\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b|\bHEARTBEAT\b|\bPWM\b|\bGND\b', ' '.join(cells[1:]))})
    return out


def evaluate(req, parts, p00, doc):
    checks = []

    def check(name, ok, detail=None):
        checks.append({'check': name, 'pass': bool(ok), **({'detail': detail} if detail is not None else {})})

    pin_net = {f'{r}.{k}': v for r, x in parts.items() for k, v in (x.get('pins') or {}).items()}
    nodes = {}
    for k, v in pin_net.items():
        nodes.setdefault(v, []).append(k)
    # device type = the ic_pins key that prefixes the first word of the P04 value ('74LVC125AD / adapter' -> '74LVC125A')
    kind = {}
    for r, x in parts.items():
        word = x.get('display', '').split(' ')[0]
        kind[r] = next((k for k in req['ic_pins'] if word.startswith(k)), word)

    def role(node):
        ref, num = node.split('.')
        table = req['ic_pins'].get(kind.get(ref, ''))
        if ref.startswith('U') or ref.startswith('Q'):
            if not table:
                return 'ic?'
            return 'in' if num in table['in'] else 'out' if num in table['out'] else 'other'
        return ref[0]  # J, R, C, T(P)

    def pulldowns(net):
        return [n for n in nodes.get(net, []) if n.startswith('R') and pin_net[n.split('.')[0] + '.' + ('2' if n.endswith('.1') else '1')] == 'GND']

    def gate_side(net, series):
        """Net where the gate inputs sit: the net itself or the far side of a series resistor."""
        if not series:
            return net, 0.0
        far = [v for k, v in pin_net.items() if k.split('.')[0] == series and v != net]
        return far[0], numeric(parts[series]['display'])

    def input_net_ok(net, series, src_v, src_r):
        gnet, rser = gate_side(net, series)
        roles = [role(n) for n in nodes.get(gnet, [])]
        pds = pulldowns(gnet)
        gates = [n for n in nodes.get(gnet, []) if role(n) == 'in']
        thr = max(req['thresholds_V'].get(kind[g.split('.')[0]], 9) for g in gates) if gates else 9
        tol = req['resistor_tolerance']
        rpd = numeric(parts[pds[0].split('.')[0]]['display']) * (1 - tol) if len(pds) == 1 else 0
        h = src_v * rpd / (rpd + (src_r + rser) * (1 + tol)) if rpd else 0
        ok = ('out' not in roles and 'ic?' not in roles and len(pds) == 1 and gates and h >= thr + req['margin_V'])
        return ok, {'gate_net': gnet, 'gates': gates, 'pulldown': pds, 'H_min_V': round(h, 3), 'threshold_V': thr}

    # --- P00 side ---
    check('P00 side: every channel pin carries its 1 k output net and the next pin is GND',
          all(p00.get(c['p00']) == c['p00_net'] and p00.get(c['p00'][:-1] + '2') == 'GND' for c in req['channels']))
    # --- channels ---
    det = {}
    for c in req['channels']:
        same = pin_net.get(c['p04']) == c['net']
        conn = [n for n in nodes.get(c['net'], []) if n.startswith('J')]
        ok, d = input_net_ok(c['net'], c.get('series'), req['p00_rail_min_V'], req['p00_series_ohm'])
        det[c['name']] = {'p04': c['p04'], 'net': pin_net.get(c['p04']), 'connectors': conn, **d}
        c['_ok'] = same and conn == [c['p04']] and ok
    check('Channels J1..J9: P04 pin carries the named input, one connector, one pulldown, only IC inputs, H >= VIH + 0.2 V',
          all(c.pop('_ok') for c in req['channels']), det)
    # --- 1 k branches from P04 TP1 ---
    src = req['branch_source']
    check('Branch source is P04 ' + src['p04'] + ' = ' + src['net'] + ' (not PANEL_3V3 behind R40)', pin_net.get(src['p04'] + '.1') == src['net'] == '3V3_IO')
    det = {}
    for b in req['branches']:
        ok, d = input_net_ok(b['net'], None, req['p04_rail_min_V'], req['branch_ohm'])
        det[b['name']] = {'p04': b['p04'], 'net': pin_net.get(b['p04']), **d}
        b['_ok'] = pin_net.get(b['p04']) == b['net'] and ok
    names = sorted(b['name'] for b in req['branches'])
    check('Five 1 k branches H_SUP/H_MCU/H_HB/H_PWM/H_SENSOR on P04 input nets with H >= VIH + 0.2 V',
          all(b.pop('_ok') for b in req['branches']) and names == ['H_HB', 'H_MCU', 'H_PWM', 'H_SENSOR', 'H_SUP'], det)
    hb = [b for b in req['branches'] if b.get('exclusive_with')]
    check('H_HB and P00 J9.1 drive the same P04 pin and are declared mutually exclusive',
          len(hb) == 1 and hb[0]['exclusive_with'] == 'J9.1' and hb[0]['p04'] == next(c['p04'] for c in req['channels'] if c['p00'] == 'J9.1'))
    # --- contacts, power, outputs, grounds, keys ---
    check('Contacts STOP / ARM / SAFE_N test on the named P04 nets', all(pin_net.get(k['a']) == k['net_a'] and pin_net.get(k['b']) == k['net_b'] for k in req['contacts']),
          {k['name']: [pin_net.get(k['a']), pin_net.get(k['b'])] for k in req['contacts']})
    pw = req['power']
    check('P04 supply pins: 3V3_IO on J1.3, GND on J1.2/J1.4, J1.1 left open', pin_net.get(pw['v33']) == pw['v33_net'] and all(pin_net.get(g) == 'GND' for g in pw['gnd'])
          and all(pin_net.get(x) not in ('GND', '3V3_IO') for x in pw['leave_open']))
    used = {c['p04'] for c in req['channels']} | {b['p04'] for b in req['branches']} | {k['a'] for k in req['contacts']}
    outs = {m['p04']: [n for n in nodes.get(m['net'], []) if role(n) == 'out'] for m in req['measure_only']}
    check('Measure-only pins are driven by an IC output or open collector and are never used as a source target',
          all(pin_net.get(m['p04']) == m['net'] and outs[m['p04']] for m in req['measure_only']) and not used & set(outs), outs)
    check('Listed ground pins are GND; key positions are NC', all(pin_net.get(g) == 'GND' for g in req['gnd_pins']) and all(pin_net.get(k) == 'NC' for k in req['key_pins_nc']))
    # --- the document tables say the same ---
    tab = rows(doc); bad = []
    for c in req['channels']:
        r = [x for x in tab if x['first'].startswith(c['p00'])]
        if not r or c['p04'] not in r[0]['pins'] or c['net'] not in r[0]['nets']:
            bad.append(c['p00'])
    for b in req['branches']:
        r = [x for x in tab if x['first'].startswith(b['name'])]
        if not r or b['p04'] not in r[0]['pins'] or b['net'] not in r[0]['nets']:
            bad.append(b['name'])
    for k in req['contacts']:
        r = [x for x in tab if x['first'].startswith(k['name'].replace('_', ' ')) or x['first'].startswith(k['name'])]
        if not r or not {k['a'], k['b']} <= set(r[0]['pins']):
            bad.append(k['name'])
    stale = sorted(set(re.findall(r'\bJ1[3-9]\.\d+|\bJ20\.\d+', doc)))
    check('Harness document tables match the checked map; no v6.1 designators (J13..J20)', not bad and not stale, {'mismatch': bad, 'v6.1_refs': stale})
    return {'p04_revision': req['p04_revision'], 'checks': checks, 'passed': sum(c['pass'] for c in checks), 'total': len(checks)}


def main():
    data = load()
    result = evaluate(*copy.deepcopy(data))
    (P / 'verification/harness-checks.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    muts = []

    def mut(name, target, fn):
        req, parts, p00, doc = copy.deepcopy(data); fn(req, parts, p00, doc) if name != 'doc_row' else None
        if name == 'doc_row':
            doc = doc.replace('| J6.1 | PSU_OK', '| J5.1 | PSU_OK', 1)
        if name == 'doc_v61':
            doc = doc + '\nJ16.1\n'
        bad = evaluate(req, parts, p00, doc)
        failed = [c['check'] for c in bad['checks'] if not c['pass']]
        muts.append({'case': name, 'expected_check': target, 'detected': any(c.startswith(target) for c in failed), 'failed_checks': failed})

    def ch(req, name):
        return next(c for c in req['channels'] if c['name'] == name)
    mut('drive_to_motor_permit', 'Channels J1..J9', lambda r, p, q, d: ch(r, 'DRIVE').update(p04='J3.1', net='MOTOR_PERMIT'))
    mut('hb_to_hw_armed', 'Channels J1..J9', lambda r, p, q, d: ch(r, 'HB').update(p04='J2.7', net='HW_ARMED'))
    mut('mech_double_pulldown_2k', 'Channels J1..J9', lambda r, p, q, d: p['R24'].update(display='2K / 1%'))
    mut('extra_pulldown_on_psu_ok', 'Channels J1..J9', lambda r, p, q, d: p.update(RX={'display': '10K / 1%', 'pins': {'1': 'PSU_OK', '2': 'GND'}}))
    mut('h_sup_to_core_link_pin', 'Five 1 k branches', lambda r, p, q, d: r['branches'][0].update(p04='J2.13'))
    mut('branches_from_panel_3v3', 'Branch source', lambda r, p, q, d: r['branch_source'].update(p04='J8', net='PANEL_3V3'))
    mut('stop_to_test_key', 'Contacts STOP', lambda r, p, q, d: r['contacts'][0].update(b='J8.3'))
    mut('key_pin_as_gnd', 'Listed ground pins', lambda r, p, q, d: r['gnd_pins'].append('J2.4'))
    mut('source_on_sensor_permit', 'Measure-only pins', lambda r, p, q, d: r['branches'][4].update(p04='J4.1', net='SENSOR_PERMIT'))
    mut('p00_heart_on_wrong_pin', 'P00 side', lambda r, p, q, d: q.update({'J9.1': 'P00_OSC'}))
    mut('doc_row', 'Harness document tables', lambda *a: None)
    mut('doc_v61', 'Harness document tables', lambda *a: None)
    (P / 'verification/harness-negative-controls.json').write_text(json.dumps(muts, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('Harness', result['passed'], '/', result['total'], '| mutations', sum(m['detected'] for m in muts), '/', len(muts))
    for c in result['checks']:
        if not c['pass']:
            print('FAIL', c['check'], json.dumps(c.get('detail'), ensure_ascii=False)[:400])
    for m in muts:
        if not m['detected']:
            print('MISSED', m['case'], m['failed_checks'])
    return 0 if result['passed'] == result['total'] and all(m['detected'] for m in muts) else 1


if __name__ == '__main__':
    sys.exit(main())
