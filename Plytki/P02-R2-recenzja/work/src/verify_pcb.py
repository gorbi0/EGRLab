"""Independent checks of the finished P02 R2 PCB (fresh native DRC + P02-specific rules).
usage: KiCad Python verify_pcb.py [alternative_board] [report_dir]
The alternative board is used by negative_controls.py (copies with a deliberate defect).
Rules come from docs/ZALOZENIA-P02-R2.md ('Wymagania rozmieszczenia') and the HOLD C1 contract.
"""
from pathlib import Path
import pcbnew as p, json, sys, math, hashlib, collections, heapq, xml.etree.ElementTree as ET
from sexpr import parse, one, sub
from provenance import run_fresh_drc
P = Path(__file__).resolve().parents[1]
path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else P / 'eda/P02.kicad_pcb'
out = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else P / 'verification'
b = p.LoadBoard(str(path)); b.BuildConnectivity()
root = ET.parse(P / 'verification/P02.xml').getroot(); parts = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
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


# ---------------- 1. native DRC, fresh, bound to the inputs ----------------
drc, receipt = run_fresh_drc(path, out / 'drc.json')
check('Fresh native DRC: 0 violations / 0 unconnected / 0 schematic parity (all severities)',
      not drc['violations'] and not drc['unconnected_items'] and not drc['schematic_parity'], receipt['counts'])
# ---------------- 2. netlist, parts, geometry ----------------
comps = {c.get('ref'): c for c in root.findall('./components/comp')}
onboard = {r for r, q in parts.items() if q.get('on_board', True)}
check('72 on-board parts + 4 mounting holes; R17 (R_CHARGE) stays off-board',
      len(onboard) == 72 and set(fmap) == onboard | {'H1', 'H2', 'H3', 'H4'} and 'R17' in comps and 'R17' not in fmap)
pin = {}
for n in root.findall('./nets/net'):
    for node in n.findall('node'):
        pin[node.get('ref'), node.get('pin')] = n.get('name')
errors = []; pads = 0
for r in onboard:
    f = fmap[r]; c = comps[r]
    if f.GetValue() != c.findtext('value') or f.GetFPIDAsString() != c.findtext('footprint'):
        errors.append(r + ' fields')
    for a in f.Pads():
        if a.GetNumber():
            pads += 1
            if a.GetNetname() != pin.get((r, a.GetNumber()), ''):
                errors.append(f'{r}.{a.GetNumber()} net')
check('Every value, footprint ID and pad net equals the exported schematic netlist', not errors, {'errors': errors, 'pads': pads})
check('2 copper layers, 1.6 mm board', b.GetCopperLayerCount() == 2 and abs(p.ToMM(b.GetDesignSettings().GetBoardThickness()) - 1.6) < 1e-6)
stack = one(one(parse(path.read_text(encoding='utf-8')), 'setup'), 'stackup')
cu = {x[1]: float(one(x, 'thickness')[1]) for x in sub(stack, 'layer') if x[1] in ['F.Cu', 'B.Cu']}
check('Both copper layers explicitly 70 um', cu == {'F.Cu': .07, 'B.Cu': .07})
edge = [g for g in b.GetDrawings() if g.GetLayer() == p.Edge_Cuts]
pts = {pos(g.GetStart()) for g in edge} | {pos(g.GetEnd()) for g in edge}
check('Closed rectangular outline 160 x 120 mm (P01 format)', len(edge) == 4 and pts == {(0, 0), (160, 0), (160, 120), (0, 120)})
holes = []
for r, q in zip(['H1', 'H2', 'H3', 'H4'], [(5, 5), (155, 5), (5, 115), (155, 115)]):
    a = list(fmap[r].Pads())[0]
    holes.append(pos(fmap[r].GetPosition()) == q and a.GetAttribute() == p.PAD_ATTRIB_NPTH and pos(a.GetDrillSize()) == (3.2, 3.2))
keep = [z for z in b.Zones() if z.GetIsRuleArea()]
mount = [z for z in keep if z.GetZoneName().startswith('M3 ')]
check('Four NPTH 3.2 mm holes at the P01 positions with copper keepouts on both layers', all(holes) and len(mount) == 4 and
      all(set(z.GetLayerSet().Seq()) == {p.F_Cu, p.B_Cu} and z.GetDoNotAllowTracks() and z.GetDoNotAllowVias() and z.GetDoNotAllowZoneFills() for z in mount))
near = []
for f in b.GetFootprints():
    if f.GetReference().startswith('H'):
        continue
    f.BuildCourtyardCaches(); cy = f.GetCourtyard(p.F_CrtYd)
    for hx, hy in [(5, 5), (155, 5), (5, 115), (155, 115)]:
        for i in range(cy.OutlineCount()):
            ol = cy.Outline(i)
            for k in range(ol.PointCount()):
                q = pos(ol.CPoint(k))
                if math.dist(q, (hx, hy)) < 4.5:
                    near.append((f.GetReference(), (hx, hy)))
check('No courtyard within 4.5 mm of a mounting-hole centre (screw head + washer)', not near, sorted(set(map(str, near))))
pro = json.loads((P / 'eda/P02.kicad_pro').read_text()); ds = pro['board']['design_settings']; rules = ds['rules']
check('Explicit DRC rules active (P01 set); no DRC exclusions', rules['min_clearance'] >= .25 and rules['min_track_width'] >= .3 and rules['min_silk_clearance'] >= .15
      and rules['min_copper_edge_clearance'] >= .5 and not ds['drc_exclusions'] and pro['net_settings']['classes'][0]['clearance'] >= .3)


def sig(t):
    if isinstance(t, p.PCB_VIA):
        return ('via', t.GetNetname(), pos(t.GetPosition()), p.ToMM(t.GetWidth(p.F_Cu)), p.ToMM(t.GetDrill()))
    return ('track', t.GetNetname(), tuple(sorted([pos(t.GetStart()), pos(t.GetEnd())])), p.ToMM(t.GetWidth()), int(t.GetLayer()))


pre = p.LoadBoard(str(P / 'routing/prerouted.kicad_pcb'))
need = collections.Counter(sig(t) for t in pre.GetTracks()); have = collections.Counter(sig(t) for t in b.GetTracks())
missing = list((need - have).elements())
check('Every pre-routed (locked) power segment retained with its width and layer', not missing and all(t.IsLocked() for t in b.GetTracks() if sig(t) in need),
      {'missing': [list(map(str, m)) for m in missing], 'locked_segments': sum(need.values())})

# ---------------- 3. power paths (HOLD C1, v6.1) ----------------
vz = [z for z in b.Zones() if not z.GetIsRuleArea() and z.GetZoneName() == 'VPROT input node']
node = {}
if len(vz) == 1:
    z = vz[0]; fill = z.GetFilledPolysList(p.F_Cu)
    conn = sorted(f"{a.GetParentFootprint().GetReference()}.{a.GetNumber()}" for a in b.GetConnectivity().GetConnectedPads(z))
    (x1, y1), (x2, y2) = pxy('J1', '1'), pxy('J2', '1'); L = math.dist((x1, y1), (x2, y2)); ux, uy = (x2 - x1) / L, (y2 - y1) / L
    chords = []
    for k in range(int((L - 7.5) / .5) + 1):  # from 4.5 mm off J1.1 (thermal ring) to 3 mm off J2.1
        s = 4.5 + .5 * k; mx, my = x1 + ux * s, y1 + uy * s
        chords.append(all(fill.Contains(xy(mx - uy * o, my + ux * o)) for o in [-2, -1, 0, 1, 2]))
    node = {'outlines': fill.OutlineCount(), 'area_mm2': round(fill.Area() / 1e12, 1), 'connected_pads': conn, 'chords_4mm_filled': f'{sum(chords)}/{len(chords)}'}
    ok = fill.OutlineCount() == 1 and set(conn) >= {'J1.1', 'J2.1', 'TP1.1', 'R9.1'} and all(chords) and fill.Area() / 1e12 >= 150
else:
    ok = False
check('VPROT input node: one F.Cu zone island joins J1.1 SUPPLY, J2.1 VMOTOR, TP1, R9.1; >= 4 mm copper along J1.1-J2.1 (5 A)', ok, node)
corr = [z for z in keep if z.GetZoneName().startswith('B.Cu GND return')]
bad = []
if len(corr) == 1:
    o = corr[0].Outline()
    for t in b.GetTracks():
        if isinstance(t, p.PCB_VIA):
            if o.Contains(t.GetPosition()):
                bad.append(('via', net(t), pos(t.GetPosition())))
        elif t.GetLayer() == p.B_Cu:
            a, c = t.GetStart(), t.GetEnd()
            if any(o.Contains(xy(p.ToMM(a.x) + (p.ToMM(c.x) - p.ToMM(a.x)) * k / 10, p.ToMM(a.y) + (p.ToMM(c.y) - p.ToMM(a.y)) * k / 10)) for k in range(11)):
                bad.append(('track', net(t), pos(a)))
gpads = sorted(f"{a.GetParentFootprint().GetReference()}.{a.GetNumber()}" for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND' and z.IsOnLayer(p.B_Cu)
               for a in b.GetConnectivity().GetConnectedPads(z) if a.GetParentFootprint().GetReference() in ('J1', 'J2'))
check('5 A return J2.2 -> J1.2 in the B.Cu GND pour: corridor rule area on B.Cu, no track or via inside, both pads on the pour',
      len(corr) == 1 and set(corr[0].GetLayerSet().Seq()) == {p.B_Cu} and corr[0].Outline().Contains(xy(*pxy('J1', '2'))) and corr[0].Outline().Contains(xy(*pxy('J2', '2')))
      and not bad and {'J1.2', 'J2.2'} <= set(gpads), {'intruders': bad, 'pour_pads': gpads})
gfill = {b.GetLayerName(L): round(sum(z.GetFilledPolysList(L).Area() for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND' and z.IsOnLayer(L)) / 1e12 / 192, 1)
         for L in (p.F_Cu, p.B_Cu)}
isl = {b.GetLayerName(L): sum(z.GetFilledPolysList(L).OutlineCount() for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND' and z.IsOnLayer(L))
       for L in (p.F_Cu, p.B_Cu)}
check('GND pours: B.Cu one continuous plane over >= 80 % of the board; F.Cu islands only where tied by GND pads (island removal: always)',
      gfill['B.Cu'] >= 80 and isl['B.Cu'] == 1 and all(z.GetIslandRemovalMode() == p.ISLAND_REMOVAL_MODE_ALWAYS for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND'),
      {'filled_percent': gfill, 'islands': isl})
hs = sorted(f"{a.GetParentFootprint().GetReference()}.{a.GetNumber()}" for f in b.GetFootprints() for a in f.Pads() if net(a) == 'HOLD_STORE')
hs_free = [pos(t.GetStart()) for t in b.GetTracks() if net(t) == 'HOLD_STORE' and not t.IsLocked()]
check('HOLD_STORE (unfused bank side) stays on the board: only C1..C3 +, F1.2, R1.1, R6.1, R20.1; all its copper locked',
      hs == sorted(['C1.1', 'C2.1', 'C3.1', 'F1.2', 'R1.1', 'R6.1', 'R20.1']) and not hs_free, {'pads': hs, 'free_tracks': hs_free})
widths = collections.defaultdict(lambda: 99.0)
for t in b.GetTracks():
    if not isinstance(t, p.PCB_VIA):
        widths[net(t)] = min(widths[net(t)], round(p.ToMM(t.GetWidth()), 2))
wlim = {'VPROT': 1.0, 'HOLD_STORE': .6, 'HOLD_FUSED': 1.5, 'CHARGE_D': 1.0, 'VLOG_RES': .8, 'P02_VIN_DC5': 1.0, 'P02_VIN_DC33': 1.0}
check('Power nets: narrowest track VPROT >= 1.0, HOLD_FUSED >= 1.5, CHARGE_D/VIN >= 1.0, HOLD_STORE >= 0.6, VLOG_RES >= 0.8 mm (no thin unfused sense track)',
      all(widths[n] >= v for n, v in wlim.items()), {n: widths[n] for n in wlim})


def route(netname, a, c):
    """Shortest routed copper path (tracks + vias) between two pads of one net, mm; None if only zones join them."""
    items = [t for t in b.GetTracks() if net(t) == netname]
    g = collections.defaultdict(list); segs = []
    for t in items:
        if isinstance(t, p.PCB_VIA):
            q = pos(t.GetPosition()); g[('F', q)].append((('B', q), 0)); g[('B', q)].append((('F', q), 0))
        else:
            L = 'F' if t.GetLayer() == p.F_Cu else 'B'; s, e = pos(t.GetStart()), pos(t.GetEnd()); d = math.dist(s, e)
            g[(L, s)].append(((L, e), d)); g[(L, e)].append(((L, s), d)); segs.append((L, s, e, t))
    for L, s, e, t in segs:  # T-junctions: an end lying on another segment of the same layer
        for n in list(g):
            if n[0] == L and n[1] not in (s, e) and t.HitTest(xy(*n[1])):
                for q in (s, e):
                    d = math.dist(n[1], q); g[n].append(((L, q), d)); g[(L, q)].append((n, d))
    for f in b.GetFootprints():  # every pad of the net is a node: a THT pad also joins F.Cu and B.Cu
        for pd in f.Pads():
            if net(pd) != netname or not pd.GetNumber():
                continue
            key = ('PAD', f.GetReference(), pd.GetNumber()); cpos = pos(pd.GetPosition())
            for n in list(g):
                if n[0] in ('F', 'B') and pd.HitTest(xy(*n[1])):
                    d = math.dist(cpos, n[1]); g[key].append((n, d)); g[n].append((key, d))
    start, goal = ('PAD',) + a, ('PAD',) + c; todo = [(0, start)]; seen = set()
    while todo:
        dd, q = heapq.heappop(todo)
        if q == goal:
            return round(dd, 1)
        if q in seen:
            continue
        seen.add(q)
        for v, w in g[q]:
            heapq.heappush(todo, (dd + w, v))
    return None


hold_run = route('HOLD_STORE', ('F1', '2'), ('C1', '1'))
check('Unfused run F1.2 -> bank C1 + <= 30 mm (F1 at the bank)', hold_run is not None and hold_run <= 30, {'F1.2-C1.1_mm': hold_run})
r6 = route('HOLD_STORE', ('R6', '1'), ('C2', '1')); r6s = route('HOLD_STORE', ('R6', '1'), ('C3', '1'))
check('Divider tops at their sources: R6.1 on the bank rail (<= 25 mm to C2/C3 +), R9.1 in the VPROT node zone',
      r6 is not None and r6s is not None and min(r6, r6s) <= 25 and 'R9.1' in node.get('connected_pads', []), {'R6.1-C2.1': r6, 'R6.1-C3.1': r6s})
dnet = {f'{r}.{n}': net(pad(r, n)) for r in ('D1', 'D2') for n in '123'}
check('D_OR separate anodes (D1: A1=VPROT, K=VLOG_RES, A2=HOLD_FUSED); D_CHARGE anodes tied, K=HOLD_FUSED',
      dnet == {'D1.1': 'VPROT', 'D1.2': 'VLOG_RES', 'D1.3': 'HOLD_FUSED', 'D2.1': 'CHARGE_D', 'D2.2': 'HOLD_FUSED', 'D2.3': 'CHARGE_D'}, dnet)
lv = {f'J{j}.{n}': net(pad(f'J{j}', n)) for j in range(3, 11) for n in '1234'}
check('LV03..LV10 (J3..J10): 1=5V_SYS 2=GND 3=3V3_IO 4=GND', all(v == {'1': '5V_SYS', '2': 'GND', '3': '3V3_IO', '4': 'GND'}[k[-1]] for k, v in lv.items()))

# ---------------- 4. local placement rules ----------------
dec = {('C9', '1', 'U3', '2', '3V3_IO'), ('C10', '1', 'U4', '2', '5V_SYS'), ('C11', '1', 'U5', '14', '3V3_IO'), ('C12', '1', 'U6', '14', '3V3_IO'), ('C13', '1', 'U7', '8', '5V_SYS')}
dd = {}
for c, cn, u, un, n in sorted(dec):
    dd[f'{c}-{u}.{un}'] = {'straight_mm': round(math.dist(pxy(c, cn), pxy(u, un)), 2), 'routed_mm': route(n, (c, cn), (u, un))}
check('100 nF at every IC: <= 8 mm straight and <= 20 mm routed to the supply pin', all(v['straight_mm'] <= 8 and v['routed_mm'] is not None and v['routed_mm'] <= 20 for v in dd.values()), dd)
flt = {'R18.2-U7.3': route('P02_BANK_CMP', ('R18', '2'), ('U7', '3')), 'R19.2-U7.5': route('P02_VPROT_CMP', ('R19', '2'), ('U7', '5'))}
check('Isolating resistors R18/R19 routed <=15mm to comparator; feedback after resistor', all(v is not None and v<=15 for v in flt.values()) and net(pad('R8','2'))=='P02_BANK_CMP' and net(pad('R11','2'))=='P02_VPROT_CMP', flt)
check('TP3 only after R20; no raw HOLD_STORE test pad', net(pad('TP3','1'))=='HOLD_TP' and net(pad('R20','1'))=='HOLD_STORE' and net(pad('R20','2'))=='HOLD_TP' and not any(net(pad(r,'1'))=='HOLD_STORE' for r in fmap if r.startswith('TP')))
cv = {k: round(math.dist(pxy(*k.split('-')[0].split('.')), pxy(*k.split('-')[1].split('.'))), 2) for k in ['C5.1-U1.1', 'C6.1-U1.3', 'C7.1-U2.1', 'C8.1-U2.3', 'C4.1-D1.2']}
check('Converter input/output capacitors and C_BUS at their pins (<= 10 mm)', all(v <= 10 for v in cv.values()), cv)
bank = [pos(fmap[r].GetPosition()) for r in ('C1', 'C2', 'C3')]
cen = [(x, y - 5) for x, y in bank]  # rot 90: body centre 5 mm above pad 1
gaps = [round(math.dist(cen[i], cen[i + 1]) - 35, 2) for i in range(2)]


def cbox(r):
    f = fmap[r]; f.BuildCourtyardCaches(); bb = f.GetCourtyard(p.F_CrtYd).BBox()
    return (p.ToMM(bb.GetLeft()), p.ToMM(bb.GetTop()), p.ToMM(bb.GetRight()), p.ToMM(bb.GetBottom()))


def rdist(c, bx):
    return math.hypot(max(bx[0] - c[0], 0, c[0] - bx[2]), max(bx[1] - c[1], 0, c[1] - bx[3]))


heat = {r: round(min(rdist(c, cbox(r)) for c in cen) - 17.5, 1) for r in ('D1', 'D2', 'U1', 'U2')}
check('Bank D35 cans: >= 3 mm apart; >= 10 mm from the TO-220 diodes and the converters',
      all(g >= 3 for g in gaps) and all(v >= 10 for v in heat.values()), {'gaps_mm': gaps, 'can_edge_to_courtyard_mm': heat})
front = p.ToMM(fmap['J2'].GetPosition().x) - 10.0  # GMSTBA body front at local y=+10, rot 270 -> towards -x
check('J2 VMOTOR (GMSTBA 7.62) at the left edge, mating face within 1 mm of the board edge',
      fmap['J2'].GetOrientationDegrees() in (270, -90) and 0 <= front <= 1.0, {'front_x_mm': round(front, 2)})
anc = {}
for r in ('J1', 'J12', 'J13'):
    f = fmap[r]; pw = [pos(a.GetPosition()) for a in f.Pads() if a.GetNumber()]; an = [pos(a.GetPosition()) for a in f.Pads() if not a.GetNumber()]
    dx, dy = pw[-1][0] - pw[0][0], pw[-1][1] - pw[0][1]; nn = math.hypot(dx, dy)
    dist = [round(abs(dx * (q[1] - pw[0][1]) - dy * (q[0] - pw[0][0])) / nn, 3) for q in an]
    edge_pad = min(min(q[0], 160 - q[0], q[1], 120 - q[1]) for q in pw); edge_anc = min(min(q[0], 160 - q[0], q[1], 120 - q[1]) for q in an)
    anc[r] = {'anchor_to_row_mm': dist, 'anchors_on_edge_side': edge_anc < edge_pad}
check('Harness anchors (J1 SUPPLY, J12 PSUOK, J13 R_CHARGE) 12.5 mm from the solder row, towards the nearest edge',
      all(len(v['anchor_to_row_mm']) == 2 and all(abs(x - 12.5) < .001 for x in v['anchor_to_row_mm']) and v['anchors_on_edge_side'] for v in anc.values()), anc)

# ---------------- 5. silkscreen: ownership and legends ----------------
texts = [(t.GetText(), t) for t in b.GetDrawings() if isinstance(t, p.PCB_TEXT) and t.GetLayer() == p.F_SilkS]


def tcentre(t):
    bb = t.GetBoundingBox(); return (p.ToMM(bb.GetCenter().x), p.ToMM(bb.GetCenter().y))


cour = {}
for f in b.GetFootprints():
    if not f.GetReference().startswith('H'):
        f.BuildCourtyardCaches(); cour[f.GetReference()] = f.GetCourtyard(p.F_CrtYd)


def inside_other(t, own):
    bb = t.GetBoundingBox(); x0, y0, x1, y1 = p.ToMM(bb.GetLeft()), p.ToMM(bb.GetTop()), p.ToMM(bb.GetRight()), p.ToMM(bb.GetBottom())
    samples = [(x0 + (x1 - x0) * i / 4, y0 + (y1 - y0) * j / 2) for i in range(5) for j in range(3)]
    return sorted({r for r, cy in cour.items() if r not in own for q in samples if cy.Contains(xy(*q))})


amb = {}
for f in b.GetFootprints():
    r = f.GetReference(); ref = f.Reference()
    if r.startswith('H') or r.startswith('TP') or not ref.IsVisible():
        continue
    c = tcentre(ref); mine = rdist(c, cbox(r))
    closer = [o for o in cour if o != r and rdist(c, cbox(o)) < mine + .3]
    other = inside_other(ref, {r})
    if closer or other:
        amb[r] = {'nearer': closer, 'inside': other}
check('Every visible reference outside other courtyards and nearest to its own part', not amb, amb)
HARN = {'J1', 'J12', 'J13'}
hidden = {txt: inside_other(t, HARN) for txt, t in texts if inside_other(t, HARN)}
check('Every board legend outside all courtyards (visible after assembly); harness pigtails J1/J12/J13 excepted', not hidden, hidden)


def centre(r):
    x0, y0, x1, y1 = cbox(r); return ((x0 + x1) / 2, (y0 + y1) / 2)


def pads_mid(r):
    q = [pos(a.GetPosition()) for a in fmap[r].Pads() if a.GetNumber()]; return (sum(x for x, _ in q) / len(q), sum(y for _, y in q) / len(q))


TPS = {f'TP{i}': pxy(f'TP{i}', '1') for i in range(1, 11)}
FUS = {r: pads_mid(r) for r in ('F1', 'F2', 'F3', 'F4')}
LVC = {f'J{j}': centre(f'J{j}') for j in range(3, 11)}
J12 = {n: pxy('J12', n) for n in '123456'}
want = {**{f'LV{j:02d}': (LVC[f'J{j}'], 8, [v for k, v in LVC.items() if k != f'J{j}']) for j in range(3, 11)},
        'BANK/1k': (TPS['TP3'], 10, [pxy('J13', '2'), pxy('D2', '2')]),
        'SUPPLY': (pads_mid('J1'), 8, [pads_mid('J2')]), 'R_CHARGE 47R/25W': (pads_mid('J13'), 8, [pads_mid('J1')]),
        '1 PSU_OK': (J12['1'], 6, [J12['2']]), '2 GND': (J12['2'], 6, [J12['1'], J12['3']]), '3 HOLD_RDY': (J12['3'], 7, [J12['2'], J12['4']]),
        'VLOG': (TPS['TP2'], 5, [v for k, v in TPS.items() if k != 'TP2']), '5V': (TPS['TP4'], 4, [TPS['TP5'], TPS['TP6']]),
        '3V3': (TPS['TP5'], 4, [TPS['TP4'], TPS['TP6']]), 'PSU_OK': (TPS['TP7'], 6, [TPS['TP8']]), 'HOLD_RDY': (TPS['TP8'], 6, [TPS['TP7'], TPS['TP9']]),
        'REF': (TPS['TP9'], 6, [TPS['TP8'], TPS['TP10']]), 'T2A': (FUS['F1'], 8, [FUS['F2'], FUS['F3'], FUS['F4']]),
        'F100mA': (FUS['F4'], 8, [FUS['F2'], FUS['F3'], FUS['F1']]), 'VSENSE 1=VPROT_S 2=GND': (centre('J11'), 16, [centre('J3')]),
        'VMOTOR': (centre('J2'), 16, [centre('J1')]), '1=VPROT': (pxy('J2', '1'), 5, [pxy('J2', '2')]), '2=GND': (pxy('J2', '2'), 5, [pxy('J2', '1'), pxy('J2', '3')]),
        '3=NC': (pxy('J2', '3'), 5, [pxy('J2', '2')]), 'VPROT': (TPS['TP1'], 5, [v for k, v in TPS.items() if k != 'TP1']), 'HOLD READY': (pxy('LED1', '1'), 6, [])}
got = {}
for k, (target, lim, rivals) in want.items():
    cands = [tcentre(t) for s, t in texts if s == k]
    best = min(cands, key=lambda c: math.dist(c, target)) if cands else None
    got[k] = None if best is None else {'mm': round(math.dist(best, target), 2), 'nearest_rival_mm': round(min([math.dist(best, r) for r in rivals], default=99), 2)}
f1a = sorted(round(min((math.dist(tcentre(t), FUS[r]) for s, t in texts if s == 'F1A'), default=999), 2) for r in ('F2', 'F3'))
ok = all(v is not None and v['mm'] <= want[k][1] and v['mm'] + .5 <= v['nearest_rival_mm'] for k, v in got.items())
ok = ok and len([1 for s, _ in texts if s == 'F1A']) == 2 and all(x <= 8 for x in f1a) and any(s.startswith('BANK do 41 J') for s, _ in texts)
got['F1A at F2/F3'] = f1a
check('Legends at their parts and nearer to them than to the neighbours: LV03..LV10, HOLD_STORE warning, J1/J2/J11/J12/J13 pins, test pads, fuse ratings, LED', ok, got)
report = {'board': path.name, 'board_sha256': sha(path), 'checks': checks, 'details': details, 'passed': sum(c['pass'] for c in checks), 'total': len(checks)}
(out / 'pcb-checks.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
for c in checks:
    print('PASS' if c['pass'] else 'FAIL', c['check'])
print(f"{report['passed']}/{report['total']} checks")
sys.exit(0 if report['passed'] == report['total'] else 1)
