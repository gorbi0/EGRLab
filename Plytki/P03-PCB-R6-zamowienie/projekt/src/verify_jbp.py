"""R6 (format S1): checks of the edge-A connectors J_BP1..3, the PFAIL_N input and the edge-B service headers J_SV1..3,
run on the EXPORTED netlist (verification/P03.xml). Independent of the generator: the old connector nets come from the
exported R5 netlist (reference/P03-R5.xml), signal classes, allowed exceptions and forbidden module pins are declared here.
Every check has at least one negative control (netlist mutation that must fail exactly that check) and a null control.
Output: verification/jbp-checks.json, verification/jbp-negative-controls.json.
"""
from pathlib import Path
import xml.etree.ElementTree as ET, json, sys, copy, re
P = Path(__file__).resolve().parents[1]

# Signal classes for the ribbon rules (task §2). CLOCK: GND on both ribbon neighbours. EDGE: at least one GND neighbour.
# STATIC/SUPPLY: may sit on an odd pin (exception) and needs no GND neighbour.
CLOCK = {'ADC_SCLK', 'SPI3_SCLK', 'MEAS_EN'}
EDGE = {'ADC_DOUTA', 'ADC_SDI', 'ADC_CS', 'ADC_CONVST', 'ADC_BUSY', 'SPI3_MOSI', 'SPI3_MISO', 'TC1_CS', 'TC2_CS', 'CS_ILOG_N', 'CS_ITEST_N',
        'CAN_TX', 'CAN_RX', 'N_J_SCOPE_HOT', 'PWM', 'HEARTBEAT', 'SUP_N_OUT', 'PFAIL_N'}
STATIC = {'ADC_RESET', 'LOGGER_CURRENT_OK', 'SENSOR_HEALTHY', 'MARK', 'TEST_KEY', 'LOGGER_CLEAR', 'TEST_PRESENT', 'MCU_ARM', 'HW_ARMED',
          'INTERLOCK', 'SENSOR_ENABLE', 'CORE_LINK', 'MOTOR_INA', 'MOTOR_INB', 'ENA_DIAG', 'ENB_DIAG'}
SUPPLY = {'5V_SYS': ('J_BP2', 3), '3V3_IO': ('J_BP3', 1)}  # net: (connector, exact pin count)
# Odd pins allowed to carry a non-GND net (reasons: src/jbp_pinout.py EXCEPTIONS, README). Anything else odd must be GND.
EXC = {('J_BP1', 11), ('J_BP1', 13), ('J_BP1', 15), ('J_BP1', 17), ('J_BP1', 19), ('J_BP2', 17), ('J_BP2', 19), ('J_BP3', 5), ('J_BP3', 9), ('J_BP3', 13), ('J_BP3', 17)}
OLD_CONNECTORS = [f'J{i}' for i in range(1, 11)]  # R5: J1 DAQ B2B, J2..J8 IDC, J9 PANELCORE, J10 LV03
# Waveshare N32R16V header pins not usable for PFAIL_N (reference/DevKitC-1-headers.md, Waveshare schematic, ESP32-S3 datasheet):
FORBIDDEN = {'J3-11': 'GPIO37 octal PSRAM', 'J3-12': 'GPIO36 octal PSRAM', 'J3-13': 'GPIO35 octal PSRAM', 'J3-16': 'GPIO48 1.8 V domain',
             'J3-17': 'GPIO47 1.8 V domain', 'J3-14': 'GPIO0 boot strap', 'J3-15': 'GPIO45 VDD_SPI strap', 'J1-14': 'GPIO46 boot strap',
             'J3-2': 'GPIO43 U0TXD (CH343P)', 'J3-3': 'GPIO44 U0RXD (CH343P)', 'J3-19': 'GPIO20 USB1_P', 'J3-20': 'GPIO19 USB1_N'}
PFAIL_GPIO = ('M1', 'J1-13')  # GPIO3: strapping only for the JTAG source when EFUSE_STRAP_JTAG_SEL = 1 (unburnt default) - documented choice
RAILS = {'5V_SYS', '5V_M1', '3V3_CORE', '3V3_IO'}
HIGH_Z = {'SUP_RAW_N', 'SUP_N', 'PFAIL_N', 'I2C_SCL', 'I2C_SDA', 'CORE_LINK'}  # defined only by a pull resistor / open drain -> 10K (S1 §6)
EDGE_10K = {'SUP_N_OUT'}  # 1.10 (review, user decision): driven, but 10K so the service branch stays off the reset edge (verify_reset.py)
ODBIOR_MIN = {'5V_SYS', '3V3_CORE', '3V3_IO', 'SUP_N', 'SUP_RAW_N', 'SUP_N_OUT', 'PFAIL_N', 'MEAS_EN', 'ADC_RESET', 'ADC_CONVST', 'CORE_LINK', 'HW_ARMED'}


def extract(root):
    pins = {}; vals = {c.get('ref'): c.findtext('value', '') for c in root.findall('./components/comp')}
    for n in root.findall('./nets/net'):
        name = n.get('name').split('/')[-1]
        for node in n.findall('node'): pins[node.get('ref'), node.get('pin')] = 'NC' if name.startswith('unconnected-') else name
    return pins, vals


def ohms(v):
    m = re.fullmatch(r'(\d+)([RKM]?)(\d*)', v.split('/')[0].strip().upper())
    return float(m[1] + ('.' + m[3] if m[3] else '')) * {'': 1, 'R': 1, 'K': 1e3, 'M': 1e6}[m[2]] if m else None


OLD, _ = extract(ET.parse(P / 'reference/P03-R5.xml').getroot())
OLD_NETS = {n for (r, p), n in OLD.items() if r in OLD_CONNECTORS and n not in {'GND', 'NC'} | RAILS}


def checks(root):
    pins, vals = extract(root); out = []
    def check(name, ok, detail=None): out.append({'check': name, 'pass': bool(ok), 'detail': detail})
    def nodes(n): return sorted(k for k, v in pins.items() if v == n)
    jbp = {j: {int(p): n for (r, p), n in pins.items() if r == j} for j in ('J_BP1', 'J_BP2', 'J_BP3')}
    # C1 old connector signals + PFAIL_N exactly once on J_BP; nothing else except GND and supplies
    where = {}
    for j, m in jbp.items():
        for p, n in m.items(): where.setdefault(n, []).append(f'{j}.{p}')
    want = OLD_NETS | {'PFAIL_N'}
    bad = {n: where.get(n) for n in want if len(where.get(n, [])) != 1}
    extra = sorted(n for n in where if n not in want | {'GND'} | set(SUPPLY))
    check('C1 every R5 connector signal (J1..J10) and PFAIL_N exactly once on J_BP1..3, no other signals', not bad and not extra, {'bad': bad, 'extra': extra, 'signals': len(want)})
    # C2 supplies
    sup = {n: where.get(n, []) for n in SUPPLY}
    check('C2 5V_SYS three times on J_BP2, 3V3_IO once on J_BP3', all(len(v) == SUPPLY[n][1] and all(x.startswith(SUPPLY[n][0] + '.') for x in v) for n, v in sup.items()), sup)
    check('C0 three 2x10 edge-A connectors, 20 connected pins each', all(sorted(m) == list(range(1, 21)) and 'NC' not in m.values() for m in jbp.values()), {j: len(m) for j, m in jbp.items()})
    # C3 odd pins GND except the listed exceptions, and exceptions only static or supply
    odd = [(j, p, n) for j, m in jbp.items() for p, n in m.items() if p % 2 and n != 'GND']
    wrong = [x for x in odd if (x[0], x[1]) not in EXC or x[2] not in STATIC | set(SUPPLY)]
    check('C3 odd pins are GND except the justified exceptions (static signals or supplies only)', not wrong, {'non_gnd_odd': odd, 'not_allowed': wrong})
    # C4 clocks and MEAS_EN: both ribbon neighbours (pin-1, pin+1) exist and are GND
    def nb(m, p): return [m.get(p - 1), m.get(p + 1)]
    ck = {n: (j, p, nb(m, p)) for j, m in jbp.items() for p, n in m.items() if n in CLOCK}
    check('C4 ADC_SCLK, SPI3_SCLK and MEAS_EN have GND on both ribbon sides', set(ck) == CLOCK and all(v[2] == ['GND', 'GND'] for v in ck.values()), ck)
    # C5 every edge signal has at least one GND neighbour; every J_BP net is classified
    lone = [(j, p, n) for j, m in jbp.items() for p, n in m.items() if n in EDGE and 'GND' not in nb(m, p)]
    unclassified = sorted({n for m in jbp.values() for n in m.values()} - CLOCK - EDGE - STATIC - set(SUPPLY) - {'GND'})
    check('C5 every edge signal has a GND ribbon neighbour; every J_BP net classified', not lone and not unclassified, {'lone': lone, 'unclassified': unclassified})
    # C6/C7 PFAIL_N input
    pf = nodes('PFAIL_N'); pfc = nodes('PFAIL_N_CORE')
    ser = [r for r, p in pf if r.startswith('R') and {pins.get((r, '1')), pins.get((r, '2'))} == {'PFAIL_N', 'PFAIL_N_CORE'}]
    pu = [r for r, p in pf if r.startswith('R') and {pins.get((r, '1')), pins.get((r, '2'))} == {'PFAIL_N', '3V3_CORE'}]
    gpio = [k for k in pfc if k[0] == 'M1']
    ok_series = len(ser) == 1 and vals[ser[0]].startswith('1K') and set(pfc) == {(ser[0], p) for r, p in pfc if r == ser[0]} | set(gpio) and len(pfc) == 2
    ok_pull = len(pu) == 1 and vals[pu[0]].startswith('100K') and not any(r.startswith('R') and '3V3_CORE' in (pins.get((r, '1')), pins.get((r, '2'))) for r, _ in pfc)
    check('C6 PFAIL_N: J_BP2.16 -> 1K series -> module GPIO; 100K pull-up to 3V3_CORE on the connector side (HIGH with J_BP2 open; 30.09: 10K gave 0.95 V > VIL at LM2903 VOL 0.7 V)',
          ok_series and ok_pull and ('J_BP2', '16') in pf, {'series': ser, 'pullup': pu, 'PFAIL_N': pf, 'PFAIL_N_CORE': pfc})
    check('C7 PFAIL_N GPIO is GPIO3 (J1-13), not PSRAM, 1.8 V, boot strap, UART0 or USB', [k[1] for k in gpio] == [PFAIL_GPIO[1]] and not any(k[1] in FORBIDDEN for k in gpio),
          {'gpio': gpio, 'forbidden': FORBIDDEN})
    # C8..C11 service headers
    sv = {j: {int(p): n for (r, p), n in pins.items() if r == j} for j in sorted({r for r, _ in pins if r.startswith('J_SV')})}
    check('C8 at most 3 service headers, <= 13 pins, GND on first and last pin', 0 < len(sv) <= 3 and all(len(m) <= 13 and m[1] == 'GND' and m[max(m)] == 'GND' for m in sv.values()),
          {j: [m.get(1), m.get(max(m))] for j, m in sv.items()})
    series, bad_sv = {}, []
    for j, m in sv.items():
        for p, n in m.items():
            if n == 'GND': continue
            nn = nodes(n); rs = [r for r, q in nn if r.startswith('R')]
            ok = len(nn) == 2 and len(rs) == 1 and (ohms(vals[rs[0]]) or 0) >= 1000
            node = None
            if ok:
                node = pins.get((rs[0], '1')) if pins.get((rs[0], '2')) == n else pins.get((rs[0], '2'))
                ok = node not in ('GND', 'NC', None) and len(nodes(node)) >= 2  # a real circuit node, not a dead end
            if ok: series[(j, p)] = (rs[0], node)
            else: bad_sv.append((j, p, n, nn))
    check('C9 every service pin except GND reaches its node through one series resistor >= 1K', not bad_sv, bad_sv)
    covered = {v[1] for v in series.values()}
    dup = [n for n in covered if sum(v[1] == n for v in series.values()) > 1]
    check('C10 service headers cover the ODBIOR minimum (rails, reset, EN = SUP_N, PFAIL_N, start states), no node twice', ODBIOR_MIN <= covered and not dup,
          {'missing': sorted(ODBIOR_MIN - covered), 'duplicates': dup})
    cls = [(k, r, node, vals[r]) for k, (r, node) in series.items() if (node in RAILS and not vals[r].startswith('1K'))
           or (node in HIGH_Z | EDGE_10K and not vals[r].startswith('10K'))]
    check('C11 series value class (S1 §6): rails 1K, high-impedance nodes 10K, SUP_N_OUT 10K (reset edge, exception 1.10)', not cls, cls)
    # C12 (1.10, review + user decision): a rail pin only next to GND, another rail or a 10K high-impedance line, so a slipped probe
    # cannot drive a logic input from a rail through 2 kOhm (30.09: 3V3_IO was next to LOGGER_CURRENT_OK, 5V_SYS next to CURRENT_CS_N)
    sas = []
    for (j, p), (r, node) in series.items():
        if node not in RAILS: continue
        for q in (p - 1, p + 1):
            nb_ = sv[j].get(q) if sv[j].get(q) == 'GND' else series.get((j, q), (None, None))[1]
            if not (nb_ == 'GND' or nb_ in RAILS or (nb_ in HIGH_Z and vals[series[(j, q)][0]].startswith('10K'))):
                sas.append((f'{j}.{p}', node, f'{j}.{q}', nb_))
    check('C12 rails on the service headers only next to GND, another rail or a 10K high-impedance line', not sas, sas)
    # C13 (1.10): the pin references in docs/ODBIOR.md ("NET (J_SVn.p)" and "J_SVn: NET (.p), A/B (.p/.q)") name the node of that pin
    odb = (P / 'docs/ODBIOR.md').read_text(encoding='utf-8'); refs = [(n_, j, int(p)) for n_, j, p in re.findall(r'\b([A-Z0-9_]+) \((J_SV[123])\.(\d+)', odb)]
    for j, seg in re.findall(r'(J_SV[123]): ([^;|]*)', odb):
        for name, a, b in re.findall(r'([A-Z0-9_]+(?:/[A-Z0-9_]+)?) \(\.(\d+)(?:/\.(\d+))?\)', seg):
            nm = name.split('/'); nm = nm[:1] + [nm[0][:nm[0].rfind('_') + 1] + x for x in nm[1:]]
            refs += [(x, j, int(y)) for x, y in zip(nm, [a] + ([b] if b else []))]
    wrong = [x for x in refs if series.get((x[1], x[2]), (None, None))[1] != x[0]]
    check('C13 docs/ODBIOR.md: every service pin reference J_SVn.p names the node of that pin', len(refs) >= 15 and not wrong, {'references': len(refs), 'wrong': wrong})
    return out


def move(root, r, p, target):
    node = None
    for n in root.findall('./nets/net'):
        for q in list(n):
            if q.tag == 'node' and q.get('ref') == r and q.get('pin') == str(p): node = q; n.remove(q)
    assert node is not None, (r, p)
    dest = next((n for n in root.findall('./nets/net') if n.get('name').split('/')[-1] == target), None)
    if dest is None: dest = ET.SubElement(root.find('nets'), 'net', {'code': '999', 'name': target})
    dest.append(node)


def swap(root, r, a, b):
    pins, _ = extract(root); na, nbb = pins[(r, str(a))], pins[(r, str(b))]; move(root, r, a, nbb); move(root, r, b, na)


def value(root, r, v): root.find(f"./components/comp[@ref='{r}']/value").text = v


def ref_of(root, net_a, net_b):
    pins, _ = extract(root)
    return next(r for (r, p), n in pins.items() if r.startswith('R') and p == '1' and {n, pins.get((r, '2'))} == {net_a, net_b})


def run():
    root = ET.parse(P / 'verification/P03.xml').getroot(); out = checks(root)
    (P / 'verification/jbp-checks.json').write_text(json.dumps(out, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    for c in out: print('PASS' if c['pass'] else 'FAIL', c['check'])
    M = [('null control (no defect)', None, lambda m: None),
         ('J_BP3 pin 7 unconnected', 'C0', lambda m: move(m, 'J_BP3', 7, 'NC')),
         ('CAN_RX lost from J_BP1.8', 'C1', lambda m: move(m, 'J_BP1', 8, 'NC')),
         ('CAN_TX duplicated on J_BP1.9', 'C1', lambda m: move(m, 'J_BP1', 9, 'CAN_TX')),
         ('foreign net I2C_SDA on J_BP1.20', 'C1', lambda m: move(m, 'J_BP1', 20, 'I2C_SDA')),
         ('only one 5V_SYS pin', 'C2', lambda m: move(m, 'J_BP2', 19, 'GND')),
         ('CAN_TX on odd pin (swap 6/7)', 'C3', lambda m: swap(m, 'J_BP1', 6, 7)),
         ('edge TC2_CS on exception pin (swap 9/10)', 'C3', lambda m: swap(m, 'J_BP3', 9, 10)),
         ('ADC_SCLK loses GND neighbour (swap 3/4)', 'C4', lambda m: swap(m, 'J_BP2', 3, 4)),
         ('MEAS_EN loses GND neighbour (swap 15/16)', 'C4', lambda m: swap(m, 'J_BP2', 15, 16)),
         ('SPI3_SCLK at ribbon end (swap 2/1 -> pin 1)', 'C4', lambda m: swap(m, 'J_BP3', 1, 2)),
         ('HEARTBEAT without GND neighbour (swap 13/15)', 'C5', lambda m: swap(m, 'J_BP3', 13, 15)),
         ('PFAIL_N between the 5V_SYS pins (swap 16/18)', 'C5', lambda m: swap(m, 'J_BP2', 16, 18)),
         ('PFAIL_N pull-up back to 10K (29.09)', 'C6', lambda m: value(m, ref_of(m, 'PFAIL_N', '3V3_CORE'), '10K / 1% 1206')),
         ('pull-up on GPIO side', 'C6', lambda m: move(m, ref_of(m, 'PFAIL_N', '3V3_CORE'), 1, 'PFAIL_N_CORE')),
         ('series resistor 0R', 'C6', lambda m: value(m, ref_of(m, 'PFAIL_N', 'PFAIL_N_CORE'), '0R / 1% 1206')),
         ('PFAIL_N wired straight to the GPIO', 'C6', lambda m: move(m, 'M1', 'J1-13', 'PFAIL_N')),
         ('PFAIL_N on GPIO37 PSRAM', 'C7', lambda m: (move(m, 'M1', 'J1-13', 'NC'), move(m, 'M1', 'J3-11', 'PFAIL_N_CORE'))),
         ('PFAIL_N on GPIO46 strap', 'C7', lambda m: (move(m, 'M1', 'J1-13', 'NC'), move(m, 'M1', 'J1-14', 'PFAIL_N_CORE'))),
         ('service header without GND at the end', 'C8', lambda m: move(m, 'J_SV2', 13, 'NC')),
         ('service pin straight on 3V3_CORE', 'C9', lambda m: move(m, 'J_SV1', 4, '3V3_CORE')),
         ('service resistor 100R', 'C9', lambda m: value(m, ref_of(m, 'MEAS_EN', 'SV_MEAS_EN'), '100R / 1% 1206')),
         ('SUP_N (EN) not on a service header', 'C10', lambda m: move(m, ref_of(m, 'SUP_N', 'SV_SUP_N'), 1, 'SUP_RAW_N')),
         ('5V_SYS service resistor 10K', 'C11', lambda m: value(m, ref_of(m, '5V_SYS', 'SV_5V_SYS'), '10K / 1%')),
         ('SUP_RAW_N service resistor 1K', 'C11', lambda m: value(m, ref_of(m, 'SUP_RAW_N', 'SV_SUP_RAW_N'), '1K / 1% 1206')),
         ('SUP_N_OUT service resistor back to 1K (R70)', 'C11', lambda m: value(m, ref_of(m, 'SUP_N_OUT', 'SV_SUP_N_OUT'), '1K / 1% 1206')),
         ('3V3_CORE between CS_ILOG_N and CS_ITEST_N (swap J_SV1 pins 10/6)', 'C12', lambda m: swap(m, 'J_SV1', 10, 6)),
         ('5V_SYS and 5V_M1 swapped on J_SV2 (ODBIOR names J_SV2.2 = 5V_SYS)', 'C13', lambda m: swap(m, 'J_SV2', 2, 12))]
    rep = []
    for name, exp, f in M:
        m = copy.deepcopy(root); f(m); failed = [c['check'] for c in checks(m) if not c['pass']]
        hit = not failed if exp is None else any(c.startswith(exp + ' ') for c in failed)
        rep.append({'control': name, 'expected': exp or 'all pass', 'detected': hit, 'failed': failed})
        print('OK    ' if hit else 'MISSED', name, '->', [c.split(' ')[0] for c in failed])
    (P / 'verification/jbp-negative-controls.json').write_text(json.dumps(rep, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    covered = {r['expected'] for r in rep}
    print(f'{len(out)} checks; {sum(r["detected"] for r in rep)}/{len(rep)} controls as expected (1 null); checks without control: {sorted({c["check"].split(" ")[0] for c in out} - covered)}')
    return all(c['pass'] for c in out) and all(r['detected'] for r in rep)


if __name__ == '__main__': sys.exit(0 if run() else 1)
