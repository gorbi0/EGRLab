"""Independent checks of the finished P00 R1 PCB (fresh native DRC + P00-specific rules).
usage: KiCad Python verify_pcb.py [alternative_board] [report_dir]
The alternative board is used by negative_controls.py (copies with a deliberate defect).
Rules come from docs/ZALOZENIA-P00-R1.md; generic parts taken over from the P02 R1 checks.
"""
from pathlib import Path
import pcbnew as p, json, sys, math, hashlib, collections, xml.etree.ElementTree as ET
from sexpr import parse, one, sub
from provenance import run_fresh_drc
P = Path(__file__).resolve().parents[1]
path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else P / 'eda/P00.kicad_pcb'
out = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else P / 'verification'
b = p.LoadBoard(str(path)); b.BuildConnectivity()
root = ET.parse(P / 'verification/P00.xml').getroot(); parts = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
W, H = 115, 70; HOLES = [(5, 5), (W - 5, 5), (5, H - 5), (W - 5, H - 5)]
checks = []; details = {}


def check(name, ok, detail=None):
    checks.append({'check': name, 'pass': bool(ok)})
    if detail is not None:
        details[name] = detail


def pos(v):
    return (round(p.ToMM(v.x), 4), round(p.ToMM(v.y), 4))


def xy(x, y):
    return p.VECTOR2I(p.FromMM(x), p.FromMM(y))


def sha(f):
    return hashlib.sha256(Path(f).read_bytes()).hexdigest()


def net(item):
    return item.GetNetname().split('/')[-1]


fmap = {f.GetReference(): f for f in b.GetFootprints()}


def pad(ref, num):
    return next(a for a in fmap[ref].Pads() if a.GetNumber() == num)


def pxy(ref, num):
    return pos(pad(ref, num).GetPosition())


# ---------------- 1. native DRC ----------------
drc, receipt = run_fresh_drc(path, out / 'drc.json')
check('Fresh native DRC: 0 violations / 0 unconnected / 0 schematic parity (all severities)',
      not drc['violations'] and not drc['unconnected_items'] and not drc['schematic_parity'], receipt['counts'])
# ---------------- 2. netlist, parts, geometry ----------------
comps = {c.get('ref'): c for c in root.findall('./components/comp')}
check('64 parts + 4 mounting holes, nothing else', len(comps) == 64 and set(fmap) == set(comps) | {'H1', 'H2', 'H3', 'H4'} and set(parts) == set(comps))
pin = {}
for n in root.findall('./nets/net'):
    for node in n.findall('node'):
        pin[node.get('ref'), node.get('pin')] = n.get('name')
errors = []; npads = 0
for r, c in comps.items():
    f = fmap[r]
    if f.GetValue() != c.findtext('value') or f.GetFPIDAsString() != c.findtext('footprint'):
        errors.append(r + ' fields')
    for a in f.Pads():
        if a.GetNumber():
            npads += 1
            if a.GetNetname() != pin.get((r, a.GetNumber()), ''):
                errors.append(f'{r}.{a.GetNumber()} net')
check('Every value, footprint ID and pad net equals the exported schematic netlist', not errors, {'errors': errors, 'pads': npads})
check('2 copper layers, 1.6 mm board', b.GetCopperLayerCount() == 2 and abs(p.ToMM(b.GetDesignSettings().GetBoardThickness()) - 1.6) < 1e-6)
stack = one(one(parse(path.read_text(encoding='utf-8')), 'setup'), 'stackup')
cu = {x[1]: float(one(x, 'thickness')[1]) for x in sub(stack, 'layer') if x[1] in ['F.Cu', 'B.Cu']}
check('Both copper layers explicitly 35 um', cu == {'F.Cu': .035, 'B.Cu': .035})
edge = [g for g in b.GetDrawings() if g.GetLayer() == p.Edge_Cuts]
pts = {pos(g.GetStart()) for g in edge} | {pos(g.GetEnd()) for g in edge}
check('Closed rectangular outline 115 x 70 mm', len(edge) == 4 and pts == {(0, 0), (W, 0), (W, H), (0, H)})
holes = []
for r, q in zip(['H1', 'H2', 'H3', 'H4'], HOLES):
    a = list(fmap[r].Pads())[0]
    holes.append(pos(fmap[r].GetPosition()) == q and a.GetAttribute() == p.PAD_ATTRIB_NPTH and pos(a.GetDrillSize()) == (3.2, 3.2))
keep = [z for z in b.Zones() if z.GetIsRuleArea()]
mount = [z for z in keep if z.GetZoneName().startswith('M3 ')]
check('Four NPTH 3.2 mm holes 5 mm from the corners, copper keepouts on both layers', all(holes) and len(mount) == 4 and len(keep) == 4 and
      all(set(z.GetLayerSet().Seq()) == {p.F_Cu, p.B_Cu} and z.GetDoNotAllowTracks() and z.GetDoNotAllowVias() and z.GetDoNotAllowZoneFills() for z in mount))
near = set()
for f in b.GetFootprints():
    if f.GetReference().startswith('H'):
        continue
    f.BuildCourtyardCaches(); cy = f.GetCourtyard(p.F_CrtYd)
    for i in range(cy.OutlineCount()):
        ol = cy.Outline(i)
        for k in range(ol.PointCount()):
            if any(math.dist(pos(ol.CPoint(k)), h) < 4.5 for h in HOLES):
                near.add(f.GetReference())
check('No courtyard within 4.5 mm of a mounting-hole centre (screw head + washer)', not near, sorted(near))
pro = json.loads((P / 'eda/P00.kicad_pro').read_text()); ds = pro['board']['design_settings']; rules = ds['rules']
check('Explicit DRC rules active (P01/P02 set); no DRC exclusions', rules['min_clearance'] >= .25 and rules['min_track_width'] >= .3 and rules['min_silk_clearance'] >= .15
      and rules['min_copper_edge_clearance'] >= .5 and not ds['drc_exclusions'] and pro['net_settings']['classes'][0]['clearance'] >= .3)


def sig(t):
    if isinstance(t, p.PCB_VIA):
        return ('via', t.GetNetname(), pos(t.GetPosition()), p.ToMM(t.GetWidth(p.F_Cu)), p.ToMM(t.GetDrill()))
    return ('track', t.GetNetname(), tuple(sorted([pos(t.GetStart()), pos(t.GetEnd())])), p.ToMM(t.GetWidth()), int(t.GetLayer()))


pre = p.LoadBoard(str(P / 'routing/prerouted.kicad_pcb'))
need = collections.Counter(sig(t) for t in pre.GetTracks()); have = collections.Counter(sig(t) for t in b.GetTracks())
missing = list((need - have).elements())
check('Every pre-routed (locked) segment and via retained with its width and layer (supply, 3V3 rail, channels)', not missing,
      {'missing': [list(map(str, m)) for m in missing], 'locked_items': sum(need.values())})

# ---------------- 3. P00 function ----------------
sw = {}
for n in range(1, 10):
    r = f'SW{n}'; com = 'P00_RESET' if n == 9 else f'P00_S{n}'
    nets = {k: net(pad(r, k)) for k in '123'}; y2, y3 = pxy(r, '2')[1], pxy(r, '3')[1]
    sw[r] = {'nets': nets, 'pin3_above_pin2': y3 < y2, 'ok': nets == {'1': com, '2': 'P00_V33', '3': 'GND'} and y3 < y2}
check('Wurth WS-SLTV switches: COM = middle pin 1, pin 2 = 3V3, pin 3 = GND, pin 3 above pin 2 on all nine (opposite-side contact: slider up = H/RUN, as printed)',
      all(v['ok'] for v in sw.values()), sw)
series = {}
for n in range(1, 9):
    nodes = sorted(f"{a.GetParentFootprint().GetReference()}.{a.GetNumber()}" for f in b.GetFootprints() for a in f.Pads() if net(a) == f'P00_OUT{n}')
    series[f'J{n}'] = nodes
hb = sorted(f"{a.GetParentFootprint().GetReference()}.{a.GetNumber()}" for f in b.GetFootprints() for a in f.Pads() if net(a) == 'P00_HEART')
check('Every header signal pin is reached only through its 1 k (OUTn = RSn.2 + Jn.1; HEART = R3.2 + J9.1)',
      all(v == sorted([f'J{k[1:]}.1', f'RS{k[1:]}.2']) for k, v in series.items()) and hb == ['J9.1', 'R3.2'] and
      all(parts[f'RS{n}']['display'].startswith('1K') for n in range(1, 9)) and parts['R3']['display'].startswith('1K'), {**series, 'J9': hb})
hdr = {f'J{n}': {'gnd_x': pxy(f'J{n}', '2')[0], 'sig_x': pxy(f'J{n}', '1')[0], 'gnd_net': net(pad(f'J{n}', '2'))} for n in range(1, 10)}
check('Headers J1..J9: left pin GND, right pin signal (as printed), same row', all(v['gnd_x'] < v['sig_x'] and v['gnd_net'] == 'GND' for v in hdr.values())
      and len({pxy(f'J{n}', '1')[1] for n in range(1, 10)}) == 1, hdr)
led = {f'LED{n}': (net(pad(f'LED{n}', '1')), net(pad(f'LED{n}', '2'))) for n in range(1, 11)}
check('LEDs: cathode GND; channel LEDs fed from the switch node (not from the output), HB LED from the 555 output, power LED from 3V3',
      all(v[0] == 'GND' for v in led.values()) and all(net(pad(f'RL{n}', '1')) == f'P00_S{n}' for n in range(1, 9))
      and net(pad('RL9', '1')) == 'P00_OSC' and net(pad('RL10', '1')) == 'P00_V33', led)
pw = {k: net(pad(*k.split('.'))) for k in ['J10.1', 'J10.2', 'D1.2', 'D1.1', 'U2.1', 'U2.2', 'U2.3']}
check('Supply: J10.1 +VIN -> D1 anode, D1 cathode -> LM2937 IN; LM2937 GND/OUT; reverse polarity blocked by D1',
      pw == {'J10.1': 'P00_VIN', 'J10.2': 'GND', 'D1.2': 'P00_VIN', 'D1.1': 'P00_VIN_P', 'U2.1': 'P00_VIN_P', 'U2.2': 'GND', 'U2.3': 'P00_V33'}, pw)
dec = {k: round(math.dist(pxy(*k.split('-')[0].split('.')), pxy(*k.split('-')[1].split('.'))), 2) for k in ['C5.1-U2.1', 'C6.1-U2.3', 'C7.1-U2.3', 'C3.1-U1.8', 'C2.1-U1.5']}
lim = {'C5.1-U2.1': 10, 'C6.1-U2.3': 10, 'C7.1-U2.3': 10, 'C3.1-U1.8': 8, 'C2.1-U1.5': 8}
check('Capacitors at their pins: LM2937 in/out <= 10 mm, 555 VCC and CTRL <= 8 mm', all(dec[k] <= lim[k] for k in dec), dec)
j10 = fmap['J10']; j10.BuildCourtyardCaches(); bb = j10.GetCourtyard(p.F_CrtYd).BBox()
check('J10 screw terminal at the left edge, wire entry facing the edge (rot 90, courtyard <= 2 mm from x = 0)',
      j10.GetOrientationDegrees() == 90 and p.ToMM(bb.GetLeft()) <= 2, {'orientation': j10.GetOrientationDegrees(), 'courtyard_left_mm': round(p.ToMM(bb.GetLeft()), 2)})
gnd_isl = {b.GetLayerName(L): sum(z.GetFilledPolysList(L).OutlineCount() for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND' and z.IsOnLayer(L)) for L in (p.F_Cu, p.B_Cu)}
gfill = {b.GetLayerName(L): round(sum(z.GetFilledPolysList(L).Area() for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND' and z.IsOnLayer(L)) / 1e12 / (W * H) * 100, 1) for L in (p.F_Cu, p.B_Cu)}
check('GND pours on both layers, island removal on (every island tied to a GND pad)', all(v > 0 for v in gnd_isl.values()) and
      all(z.GetIslandRemovalMode() == p.ISLAND_REMOVAL_MODE_ALWAYS for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND'),
      {'islands': gnd_isl, 'filled_percent': gfill})
# ---------------- 4. silkscreen ----------------
texts = [(t.GetText(), t) for t in b.GetDrawings() if isinstance(t, p.PCB_TEXT) and t.GetLayer() == p.F_SilkS]


def tcentre(t):
    bb = t.GetBoundingBox(); return (p.ToMM(bb.GetCenter().x), p.ToMM(bb.GetCenter().y))


cour, cbb = {}, {}
for f in b.GetFootprints():
    if not f.GetReference().startswith('H'):
        f.BuildCourtyardCaches(); cour[f.GetReference()] = f.GetCourtyard(p.F_CrtYd); q = cour[f.GetReference()].BBox()
        cbb[f.GetReference()] = (p.ToMM(q.GetLeft()), p.ToMM(q.GetTop()), p.ToMM(q.GetRight()), p.ToMM(q.GetBottom()))


def rdist(c, bx):
    return math.hypot(max(bx[0] - c[0], 0, c[0] - bx[2]), max(bx[1] - c[1], 0, c[1] - bx[3]))


def inside_other(t, own):
    bb = t.GetBoundingBox(); x0, y0, x1, y1 = p.ToMM(bb.GetLeft()), p.ToMM(bb.GetTop()), p.ToMM(bb.GetRight()), p.ToMM(bb.GetBottom())
    samples = [(x0 + (x1 - x0) * i / 4, y0 + (y1 - y0) * j / 2) for i in range(5) for j in range(3)]
    return sorted({r for r, cy in cour.items() if r not in own for q in samples if cy.Contains(xy(*q))})


amb = {}
for f in b.GetFootprints():
    r = f.GetReference(); ref = f.Reference()
    if r.startswith('H') or not ref.IsVisible():
        continue
    c = tcentre(ref); mine = rdist(c, cbb[r])
    closer = [o for o in cbb if o != r and rdist(c, cbb[o]) < mine + .3]; other = inside_other(ref, {r})
    if closer or other:
        amb[r] = {'nearer': closer, 'inside': other}
check('Every visible reference outside other courtyards and nearest to its own part', not amb, amb)
hidden = {txt: inside_other(t, set()) for txt, t in texts if inside_other(t, set())}
check('Every board legend outside all courtyards (visible after assembly)', not hidden, hidden)
led_xy = {n: pxy(f'LED{n}', '2') for n in range(1, 10)}
num = {}
for n in range(1, 10):
    label = 'HB' if n == 9 else str(n); c = [tcentre(t) for s, t in texts if s == label]
    if c:
        d = {m: math.dist(c[0], led_xy[m]) for m in led_xy}; num[label] = {'to_own_led_mm': round(d[n], 2), 'nearest_led': min(d, key=d.get)}
check('Channel numbers 1..8 and HB beside their own LED (<= 5 mm, nearest LED is their own)',
      len(num) == 9 and all(v['to_own_led_mm'] <= 5 and v['nearest_led'] == (9 if k == 'HB' else int(k)) for k, v in num.items()), num)
need_txt = ['SUWAK W GORE = H (3V3), W DOL = L (GND); LED SWIECI = H', 'J1-J9: LEWY PIN = GND, PRAWY = SYGNAL PRZEZ 1 k',
            'HB: SUWAK W GORE = RUN, W DOL = STOP (wyjscie L)', '+VIN 5-15V']
have_txt = {s for s, _ in texts}
vin = [math.dist(tcentre(t), pxy('J10', '1')) for s, t in texts if s == '+VIN 5-15V']
check('Operating legends present (slider sense, header pinout, heartbeat run/stop, +VIN next to J10 pin 1 <= 12 mm)',
      all(s in have_txt for s in need_txt) and vin and min(vin) <= 12, {'missing': [s for s in need_txt if s not in have_txt], '+VIN_to_J10.1_mm': round(min(vin), 2) if vin else None})
report = {'board': path.name, 'board_sha256': sha(path), 'checks': checks, 'details': details, 'passed': sum(c['pass'] for c in checks), 'total': len(checks)}
(out / 'pcb-checks.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
for c in checks:
    print('PASS' if c['pass'] else 'FAIL', c['check'])
print(f"{report['passed']}/{report['total']} checks")
sys.exit(0 if report['passed'] == report['total'] else 1)
