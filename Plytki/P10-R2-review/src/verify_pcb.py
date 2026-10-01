"""Independent checks of the finished P10 R2 PCB in format S1 (fresh native DRC + S1 and P10-specific rules); structure and the
generic checks of P09 R2 / P03 R6 verify_pcb.py (30.09.2026), board values from board.py.
usage: KiCad Python verify_pcb.py [alternative_board] [report_dir]
The alternative board is used by negative_controls.py (copies with one deliberate defect each).
Sources of the expected values: Plytki/Format-S1/format-s1.json and SPECYFIKACJA-FORMATU-S1.md (S1-3), the P12 contract docs/J_BP.csv,
docs/SERWIS.csv, docs/WIAZKI.md (W3 anchor), the BOM notes (docs/parts.json) and the README; nothing is read from placement.py.
"""
from pathlib import Path
import pcbnew as p, json, sys, os, math, hashlib, csv, xml.etree.ElementTree as ET
from sexpr import parse, one, sub
from provenance import run_fresh_drc
sys.path.insert(0, str(Path(__file__).resolve().parent))
from heights import height
from board import NAME, REV, CLASS, SLOTS, SIGNAL_W, SUPPORT_KEEPOUT, JBP as JBP_ZL, JSV as JSV_ZL, PIN_MARKS
import ast as _ast
TYTUL = f"{REV} S1-{CLASS} {SLOTS[0] if len(SLOTS) == 1 else SLOTS[0] + '-' + SLOTS[-1]}"   # S1 §9 (jak P02 R4)
P = Path(__file__).resolve().parents[1]
path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else P / f'eda/{NAME}.kicad_pcb'
out = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else P / 'verification'
b = p.LoadBoard(str(path)); b.BuildConnectivity()
S1 = json.loads((P.parents[0] / 'Format-S1/format-s1.json').read_text(encoding='utf-8'))
root = ET.parse(P / f'verification/{NAME}.xml').getroot(); parts = json.loads(Path(os.environ.get('EGRLAB_PARTS_JSON', P / 'docs/parts.json')).read_text(encoding='utf-8'))
checks = []; details = {}
KLASA, SLOTY = CLASS, SLOTS
W, H = S1['klasy'][KLASA]['W'], S1['klasy'][KLASA]['H']; STEP = S1['rozstaw_slotow']
HMAX = S1['poziomy']['wys_max_gora_standard']              # level 4, standoffs 20 mm (S1-3)
HMAX_BOTTOM = 1.5                                          # S1-2: SMD <= 1.5 mm on the bottom
JBP = {}
with open(P / 'docs/J_BP.csv', encoding='utf-8-sig') as fh:
    for r in csv.DictReader(fh, delimiter=';'):
        JBP[int(r['pin'])] = r['siec']
SERW = {}
with open(P / 'docs/SERWIS.csv', encoding='utf-8-sig') as fh:
    for r in csv.DictReader(fh, delimiter=';'):
        SERW[int(r['pin'])] = (r['siec'], r['rezystor'])


def check(name, ok, detail=None):
    checks.append({'check': name, 'pass': bool(ok)})
    if detail is not None:
        details[name] = detail


def pos(v):
    return (round(p.ToMM(v.x), 4), round(p.ToMM(v.y), 4))


def xy(x, y):
    return p.VECTOR2I(p.FromMM(x), p.FromMM(y))


def net(item):
    return item.GetNetname().split('/')[-1]


fmap = {f.GetReference(): f for f in b.GetFootprints()}


def pad(ref, num):
    return next(a for a in fmap[ref].Pads() if a.GetNumber() == str(num))


def pxy(ref, num):
    return pos(pad(ref, num).GetPosition())


def fp2board(f, x, y):
    a = math.radians(f.GetOrientationDegrees()); c = f.GetPosition()
    return (p.ToMM(c.x) + x * math.cos(a) + y * math.sin(a), p.ToMM(c.y) - x * math.sin(a) + y * math.cos(a))


def layer_bbox(f, L):
    bb = None
    for g in f.GraphicalItems():
        if g.GetLayer() == L:
            r = g.GetBoundingBox(); c = (p.ToMM(r.GetLeft()), p.ToMM(r.GetTop()), p.ToMM(r.GetRight()), p.ToMM(r.GetBottom()))
            bb = c if bb is None else (min(bb[0], c[0]), min(bb[1], c[1]), max(bb[2], c[2]), max(bb[3], c[3]))
    return bb


def cbox(r):
    f = fmap[r]; f.BuildCourtyardCaches(); bb = f.GetCourtyard(p.B_CrtYd if f.IsFlipped() else p.F_CrtYd).BBox()
    return (p.ToMM(bb.GetLeft()), p.ToMM(bb.GetTop()), p.ToMM(bb.GetRight()), p.ToMM(bb.GetBottom()))


def rect_hits_copper(rc):
    """Tracks, vias, pads (other than of the modules' own mounting) and filled pours that touch the rectangle rc."""
    shape = p.SHAPE_POLY_SET(); shape.NewOutline()
    for x, y in [(rc[0], rc[1]), (rc[2], rc[1]), (rc[2], rc[3]), (rc[0], rc[3])]:
        shape.Append(p.FromMM(x), p.FromMM(y))
    return shape_hits_copper(shape)


MIN_HIT = 1e-3   # mm2


def shape_hits_copper(shape):
    """As rect_hits_copper for any outline (P03 R6 30.09: the SD1 keepouts are circles; their bounding squares caught the pour
    and two tracks in the corners, outside the rule area). A hit needs more than MIN_HIT mm2 of common area: a pour filled up to
    a circular rule area shares only polygonisation slivers with it (1e-7 mm2 measured on SD1)."""
    hits = []
    for L in (p.F_Cu, p.B_Cu):
        for t in b.GetTracks():
            if isinstance(t, p.PCB_VIA) or t.GetLayer() == L:
                ps = p.SHAPE_POLY_SET(); t.TransformShapeToPolygon(ps, L, 0, p.FromMM(.005), p.ERROR_INSIDE); ps.BooleanIntersection(shape)
                if ps.OutlineCount() and ps.Area() / 1e12 > MIN_HIT:
                    hits.append(('via ' if isinstance(t, p.PCB_VIA) else 'track ') + net(t))
        for z in b.Zones():
            if not z.GetIsRuleArea() and z.IsOnLayer(L):
                ps = p.SHAPE_POLY_SET(z.GetFilledPolysList(L)); ps.BooleanIntersection(shape)
                if ps.OutlineCount() and ps.Area() / 1e12 > MIN_HIT:
                    hits.append(f'pour {net(z)} {b.GetLayerName(L)}')
        for f in b.GetFootprints():
            for a in f.Pads():
                if a.IsOnLayer(L) and a.GetAttribute() != p.PAD_ATTRIB_NPTH:
                    ps = p.SHAPE_POLY_SET(); a.TransformShapeToPolygon(ps, L, 0, p.FromMM(.005), p.ERROR_INSIDE); ps.BooleanIntersection(shape)
                    if ps.OutlineCount() and ps.Area() / 1e12 > MIN_HIT:
                        hits.append(f'pad {f.GetReference()}.{a.GetNumber()}')
    return sorted(set(hits))


# ---------------- 1. native DRC, fresh, bound to the inputs ----------------
drc, receipt = run_fresh_drc(path, out / 'drc.json')
_silk = json.loads((P / 'routing/silkscreen.json').read_text(encoding='utf-8'))
trimmed = set(_silk.get('dropped_by_part', {})) | set(_silk.get('moved_texts_by_part', {}))
fp_uuid = {f.m_Uuid.AsString(): f.GetReference() for f in b.GetFootprints()}
lib_ok = [v for v in drc['violations'] if v['type'] == 'lib_footprint_mismatch' and all(fp_uuid.get(i['uuid']) in trimmed for i in v['items'])]
rest = [v for v in drc['violations'] if v not in lib_ok]
check('Fresh native DRC: 0 violations / 0 unconnected / 0 schematic parity (all severities; lib_footprint_mismatch only for parts '
      'whose silk silkscreen.py trimmed)',
      not rest and not drc['unconnected_items'] and not drc['schematic_parity'],
      dict(receipt['counts'], other_violations=len(rest), other_types=sorted({v['type'] for v in rest}),
           accepted_lib_mismatch=sorted(fp_uuid.get(i['uuid']) for v in lib_ok for i in v['items'])))
# ---------------- 2. netlist, parts, board ----------------
comps = {c.get('ref'): c for c in root.findall('./components/comp')}
onboard = {r for r, q in parts.items() if q.get('on_board', True)}
holes_ref = {r for r in fmap if r.startswith('H') and r[1:].isdigit()}
check(f'{len(onboard)} on-board parts + {4 * len(SLOTY)} mounting holes, nothing else', set(fmap) == onboard | holes_ref and len(holes_ref) == 4 * len(SLOTY))
pin = {}
for n in root.findall('./nets/net'):
    for node in n.findall('node'):
        pin[node.get('ref'), node.get('pin')] = n.get('name')
errors = []; npads = 0
for r in onboard:
    f = fmap[r]; c = comps[r]
    if f.GetValue() != c.findtext('value') or f.GetFPIDAsString() != c.findtext('footprint'):
        errors.append(r + ' fields')
    for a in f.Pads():
        if a.GetNumber():
            npads += 1
            if a.GetNetname() != pin.get((r, a.GetNumber()), ''):
                errors.append(f'{r}.{a.GetNumber()} net')
check('Every value, footprint ID and pad net equals the exported schematic netlist', not errors, {'errors': errors, 'pads': npads})
bottom = {}
tht = [a for g in b.GetFootprints() for a in g.Pads() if a.GetAttribute() == p.PAD_ATTRIB_PTH]
for f in b.GetFootprints():
    if not f.IsFlipped():
        continue
    r = f.GetReference(); smd = all(a.GetAttribute() == p.PAD_ATTRIB_SMD for a in f.Pads()); hgt = height(r, parts)
    rad = lambda a: max(p.ToMM(a.GetSize().x), p.ToMM(a.GetSize().y)) / 2
    gap = min((math.dist(pos(a.GetPosition()), pos(q.GetPosition())) - rad(a) - rad(q) for a in tht for q in f.Pads()), default=99)
    bottom[r] = {'smd': smd, 'height_mm': hgt, 'soic': 'SOIC' in f.GetFPIDAsString(), 'min_gap_to_THT_mm': round(gap, 2)}
check('S1-2 section 4: parts on the bottom only SMD <= 1.5 mm, no SOIC (level 4), >= 1 mm from THT pads',
      all(v['smd'] and v['height_mm'] <= 1.5 and not v['soic'] and v['min_gap_to_THT_mm'] >= 1.0 for v in bottom.values()), {'bottom_parts': bottom})
check('2 copper layers, 1.6 mm board (S1: FR4 1.6 mm)', b.GetCopperLayerCount() == S1['obrys']['warstwy'] and abs(p.ToMM(b.GetDesignSettings().GetBoardThickness()) - S1['obrys']['grubosc_pcb']) < 1e-6)
stack = one(one(parse(path.read_text(encoding='utf-8')), 'setup'), 'stackup')
cu = {x[1]: float(one(x, 'thickness')[1]) for x in sub(stack, 'layer') if x[1] in ['F.Cu', 'B.Cu']}
check('Both copper layers 35 um (S1)', cu == {'F.Cu': S1['obrys']['miedz_um'] / 1000, 'B.Cu': S1['obrys']['miedz_um'] / 1000}, cu)
edge = [g for g in b.GetDrawings() if g.GetLayer() == p.Edge_Cuts]
arcs = [g for g in edge if g.GetShape() == p.SHAPE_T_ARC]; segs = [g for g in edge if g.GetShape() == p.SHAPE_T_SEGMENT]
bb = b.GetBoardEdgesBoundingBox(); R = S1['obrys']['promien_naroza']
hw = max(p.ToMM(g.GetWidth()) for g in edge) / 2
check(f'Outline class {KLASA}: {W} x {H} mm, 4 corner arcs R {R} mm (format-s1.json)',
      len(segs) == 4 and len(arcs) == 4 and all(abs(p.ToMM(a.GetRadius()) - R) < 1e-4 for a in arcs)
      and abs(p.ToMM(bb.GetLeft()) + hw) < 1e-3 and abs(p.ToMM(bb.GetTop()) + hw) < 1e-3 and abs(p.ToMM(bb.GetRight()) - hw - W) < 1e-3
      and abs(p.ToMM(bb.GetBottom()) - hw - H) < 1e-3,
      {'bbox_line_centres': [p.ToMM(bb.GetLeft()) + hw, p.ToMM(bb.GetTop()) + hw, p.ToMM(bb.GetRight()) - hw, p.ToMM(bb.GetBottom()) - hw],
       'arcs': len(arcs), 'segments': len(segs)})
want_h = sorted((x + STEP * k, y) for k in range(len(SLOTY)) for x in S1['otwory_M3']['x_w_slocie'] for y in S1['otwory_M3']['y'])
got_h = sorted(pos(fmap[r].GetPosition()) for r in holes_ref)
hole_ok = all(list(fmap[r].Pads())[0].GetAttribute() == p.PAD_ATTRIB_NPTH and pos(list(fmap[r].Pads())[0].GetDrillSize()) == (S1['otwory_M3']['srednica'],) * 2 for r in holes_ref)
check(f'M3 holes: {4 * len(SLOTY)} NPTH 3.2 mm exactly at the S1 positions (x_w_slocie + 53.5 k, y 14 / 86)',
      hole_ok and len(got_h) == len(want_h) and all(math.dist(a, c) < .005 for a, c in zip(got_h, want_h)), {'want': want_h, 'got': got_h})
RZ = S1['otwory_M3']['strefa_dystansu_srednica'] / 2
near = set(); cop = []
for f in b.GetFootprints():
    if f.GetReference() in holes_ref:
        continue
    f.BuildCourtyardCaches(); cy = f.GetCourtyard(p.B_CrtYd if f.IsFlipped() else p.F_CrtYd)
    for hx, hy in want_h:
        circ = p.SHAPE_POLY_SET(); circ.NewOutline()
        for k in range(64):
            circ.Append(p.FromMM(hx + RZ * math.cos(k * math.tau / 64)), p.FromMM(hy + RZ * math.sin(k * math.tau / 64)))
        x = p.SHAPE_POLY_SET(cy); x.BooleanIntersection(circ)
        if x.Area() > 0:
            near.add((f.GetReference(), (hx, hy)))
for hx, hy in want_h:
    c = xy(hx, hy)
    for t in b.GetTracks():
        if t.HitTest(c, p.FromMM(RZ)):
            cop.append((net(t), (hx, hy)))
    for f in b.GetFootprints():
        if f.GetReference() in holes_ref:
            continue
        for a in f.Pads():
            if a.HitTest(c, p.FromMM(RZ)):
                cop.append((f'{f.GetReference()}.{a.GetNumber()}', (hx, hy)))
    for z in b.Zones():
        if z.GetIsRuleArea():
            continue
        for L in (p.F_Cu, p.B_Cu):
            if z.IsOnLayer(L):
                ps = z.GetFilledPolysList(L)
                if any(ps.Contains(xy(hx + (RZ - .01) * math.cos(k * math.tau / 32), hy + (RZ - .01) * math.sin(k * math.tau / 32))) for k in range(32)) or ps.Contains(c):
                    cop.append((f'zone {net(z)} {b.GetLayerName(L)}', (hx, hy)))
rules_ok = sum(1 for z in b.Zones() if z.GetIsRuleArea() and z.GetZoneName().startswith('M3 ') and z.GetDoNotAllowTracks() and z.GetDoNotAllowVias() and z.GetDoNotAllowZoneFills()
               and set(z.GetLayerSet().Seq()) == {p.F_Cu, p.B_Cu})
check('Standoff zones D7: no courtyard and no copper (pads, tracks, vias, pours) within 3.5 mm of a hole centre; rule areas on both layers',
      not near and not cop and rules_ok == len(want_h), {'courtyards': sorted(map(str, near)), 'copper': sorted(map(str, cop)), 'rule_areas': rules_ok})
pro = json.loads((P / f'eda/{NAME}.kicad_pro').read_text()); ds = pro['board']['design_settings']; rules = ds['rules']
cls = {c['name']: c for c in pro['net_settings']['classes']}
check(f'Rules as P02 R3 / R4 (clearance >= 0.25, track >= {SIGNAL_W:.2f}, edge 0.5) and annular ring >= 0.25 mm (S1 section 3); no DRC exclusions',
      rules['min_clearance'] >= .25 and rules['min_track_width'] >= SIGNAL_W - 1e-9 and rules['min_copper_edge_clearance'] >= .5 and rules['min_via_annular_width'] >= .25
      and cls['Default']['track_width'] >= .3 - 1e-9 and not ds['drc_exclusions'] and all(c['clearance'] >= .25 for c in cls.values()))
narrow = sorted({round(p.ToMM(t.GetWidth()), 3) for t in b.GetTracks() if not isinstance(t, p.PCB_VIA) and p.ToMM(t.GetWidth()) < SIGNAL_W - 1e-6})
check(f'Every track >= {SIGNAL_W:.2f} mm (S1 section 3)', not narrow, narrow)
ring = [f'{f.GetReference()}.{a.GetNumber()}' for f in b.GetFootprints() for a in f.Pads() if a.GetAttribute() == p.PAD_ATTRIB_PTH
        and (min(p.ToMM(a.GetSize().x), p.ToMM(a.GetSize().y)) - p.ToMM(a.GetDrillSize().x)) / 2 < .25 - 1e-6]
ring += [f'via {pos(t.GetPosition())}' for t in b.GetTracks() if isinstance(t, p.PCB_VIA) and (p.ToMM(t.GetWidth(p.F_Cu)) - p.ToMM(t.GetDrill())) / 2 < .25 - 1e-6]
check('Every PTH pad and via has an annular ring >= 0.25 mm (measured on the copper)', not ring, ring[:20])

# ---------------- 3. edge A: J1 = J_BP (contract docs/J_BP.csv) ----------------
f = fmap.get('J1'); jd = {}
pads1 = {a.GetNumber(): pos(a.GetPosition()) for a in f.Pads()}; fab = layer_bbox(f, p.F_Fab)
xs = [v[0] for v in pads1.values()]; cx = (min(xs) + max(xs)) / 2
nets = {int(n): net(pad('J1', n)) for n in pads1}
ok = (abs(cx - S1['krawedz_A']['srodek_x_w_slocie']) < .05 and pads1['1'][0] == min(xs) and nets == JBP and fab and abs(fab[1]) < .3
      and len(pads1) == 10 and 'IDC-Header_2x05' in f.GetFPIDAsString())
jd = {'centre_x': round(cx, 3), 'pin1': pads1['1'], 'fab_front_y': fab and round(fab[1], 3), 'pinout_equals_J_BP.csv': nets == JBP}
check('J1 = J_BP (edge A): IDC 2x5 angled, body front at y = 0, pin centre x = 26.5, pin 1 at the smaller x, pinout = docs/J_BP.csv (P12 contract)', ok, jd)
# ---------------- 4. edge B: service header J2 (contract docs/SERWIS.csv) ----------------
texts = [(t.GetText(), t) for t in b.GetDrawings() if isinstance(t, p.PCB_TEXT) and t.GetLayer() == p.F_SilkS]
LABEL = next(_ast.literal_eval(n.value) for n in _ast.parse((P / 'src/silkscreen.py').read_text(encoding='utf-8')).body
             if isinstance(n, _ast.Assign) and any(getattr(t, 'id', '') == 'LABEL' for t in n.targets))   # 1.10 (recenzja): wzorzec niezależny od wyniku
f = fmap['J2']; problems = []; rows = []
pd = sorted(((int(a.GetNumber()), a) for a in f.Pads()), key=lambda q: q[0]); fab = layer_bbox(f, p.F_Fab)
xs = [p.ToMM(a.GetPosition().x) for _, a in pd]; lo, hi = S1['krawedz_B']['zakres_x_w_slocie']
if len(pd) > S1['krawedz_B']['max_pinow_na_slot']: problems.append('too many pins')
if min(xs) - .85 < lo - 1e-6 or max(xs) + .85 > hi + 1e-6: problems.append(f'pins outside x {lo}..{hi}')
if not fab or fab[3] - H < 5.0: problems.append(f'pins not ~6 mm beyond edge B (fab {fab})')
if net(pd[0][1]) != 'GND' or net(pd[-1][1]) != 'GND': problems.append('GND not on both ends')
for n, a in (pd[0], pd[-1]):
    if len([t for s_, t in texts if s_ == LABEL['GND'] and abs(p.ToMM(t.GetPosition().x) - p.ToMM(a.GetPosition().x)) < 1.3 and 80 < p.ToMM(t.GetPosition().y) < H]) != 1:
        problems.append(f'pin {n}: no single GND label')
for n, a in pd[1:-1]:
    want_net, want_res = SERW[n]
    members = [(ff.GetReference(), q) for ff in b.GetFootprints() for q in ff.Pads() if q.GetNetname() == a.GetNetname() and ff.GetReference() != 'J2']
    if len(members) != 1 or not members[0][0].startswith('R'):
        problems.append(f'pin {n}: not exactly one series resistor ({[m[0] for m in members]})'); continue
    r, q = members[0]; other = next(x for x in fmap[r].Pads() if x.GetNumber() != q.GetNumber()); node = net(other)
    val = fmap[r].GetValue().split(' / ')[0].upper()
    others = [x for ff in b.GetFootprints() for x in ff.Pads() if x.GetNetname() == other.GetNetname() and ff.GetReference() != r]
    dist = min((math.dist(pos(other.GetPosition()), pos(x.GetPosition())) for x in others), default=99)
    if node != want_net or want_res.split()[0] != r: problems.append(f'pin {n}: {r} on {node}, SERWIS.csv {want_net} {want_res}')
    want_val = {'1 kΩ': '1K', '10 kΩ': '10K', '4,7 kΩ': '4K7'}[' '.join(want_res.split()[1:3])]
    if val != want_val: problems.append(f'pin {n}: {r} {val}, SERWIS.csv {want_val} (S1 section 6: 1K logic / rails, 10K CAN_H / CAN_L, README)')
    if dist > 10: problems.append(f'pin {n}: {r} not at its node ({dist:.1f} mm)')
    lab = LABEL.get(node)
    tx = [t for s, t in texts if lab and s == lab and abs(p.ToMM(t.GetPosition().x) - p.ToMM(a.GetPosition().x)) < 1.3 and 80 < p.ToMM(t.GetPosition().y) < H]
    if len(tx) != 1: problems.append(f'pin {n}: {len(tx)} silk labels')
    rows.append({'pin': n, 'node': node, 'resistor': r, 'value': val, 'node_dist_mm': round(dist, 1), 'label': lab, 'side': 'B' if fmap[r].IsFlipped() else 'F'})
check('Service header J2 (edge B, S1 section 6): <= 13 pins in x 10..43, pins out ~6 mm, GND on both ends, one series resistor per pin '
      'of the value in docs/SERWIS.csv, <= 10 mm from its node, one silk label per pin with the name of its node (LABEL in silkscreen.py), GND at the ends', not problems, {'problems': problems, 'pins': rows})
# ---------------- 4b. reserved strips at the edges (S1 §5 / §6) ----------------
pasy = {}
for zl, kraw in [(z, 'A') for z in JBP_ZL] + [(z, 'B') for z in JSV_ZL]:
    xs_ = [p.ToMM(a.GetPosition().x) for a in fmap[zl].Pads() if a.GetNumber()]; x0 = STEP * int(((min(xs_) + max(xs_)) / 2) // STEP)
    y0, y1 = (S1['krawedz_A']['strefa_y'] if kraw == 'A' else S1['krawedz_B']['strefa_y']); lo_, hi_ = (10.0, 43.0) if kraw == 'A' else S1['krawedz_B']['zakres_x_w_slocie']
    pas = (x0 + lo_, y0, x0 + hi_, y1)
    pasy[f'{zl} ({kraw})'] = {'pas': pas, 'czesci': sorted(r for r in fmap if r not in holes_ref and r != zl
                                                        and cbox(r)[0] < pas[2] and pas[0] < cbox(r)[2] and cbox(r)[1] < pas[3] and pas[1] < cbox(r)[3])}
check('Reserved strip of edge A (S1 §5: y 0-10, x 10-43 of each J_BP slot): no other part on either side; '
      'the edge-B zone of the service headers is reported only (S1 §6 gives the header position, not a reserved strip)',
      not any(v['czesci'] for k, v in pasy.items() if k.endswith('(A)')), pasy)
# ---------------- 5. heights ----------------
hh = {r: height(r, parts) for r in onboard}
check(f'Every part <= {HMAX} mm above the board (level 4, S1 section 4; src/heights.py)', all(v <= HMAX for v in hh.values()),
      {'max': max(hh.items(), key=lambda q: q[1]), 'over': {r: v for r, v in hh.items() if v > HMAX}})
# ---------------- 6. J3: OBD tail of harness W3 at the input wall (docs/WIAZKI.md, S1 section 7) ----------------
f = fmap['J3']; p1, p2 = pxy('J3', '1'), pxy('J3', '2')
anchors = sorted(pos(a.GetPosition()) for a in f.Pads() if a.GetAttribute() == p.PAD_ATTRIB_NPTH)
rz = [z for z in b.Zones() if z.GetIsRuleArea() and z.GetZoneName().startswith('J3 support')]
cu = [h for z in rz for h in shape_hits_copper(z.Outline())]
cy = cbox('J3'); strip = (cy[2], min(p1[1], p2[1]) - 2.0, W, max(p1[1], p2[1]) + 2.0)   # cable between the anchor and the wall
inside = sorted(r for r in fmap if r not in holes_ref and r != 'J3' and not fmap[r].IsFlipped()
                and cbox(r)[0] < strip[2] and strip[0] < cbox(r)[2] and cbox(r)[1] < strip[3] and strip[1] < cbox(r)[3])
edge_gap = min(W - (a[0] + S1['otwory_M3']['srednica'] / 2) for a in anchors) if anchors else 0
d1 = {'CAN_H': math.dist(pxy('D1', '2'), p1), 'CAN_L': math.dist(pxy('D1', '1'), p2)}


def przez(siec, a, przez_, cel):
    """1.10 (recenzja): czy każda droga miedzi sieci od pola a do pola cel przechodzi przez pole przez_ (graf odcinków, podział na stykach)."""
    tr = [t for t in b.GetTracks() if net(t) == siec]; pola = {(ff.GetReference(), q.GetNumber()): q for ff in b.GetFootprints() for q in ff.Pads() if net(q) == siec and q.GetNumber()}
    pkt = {(round(p.ToMM(v.x), 3), round(p.ToMM(v.y), 3)) for t in tr for v in ((t.GetPosition(),) if isinstance(t, p.PCB_VIA) else (t.GetStart(), t.GetEnd()))}
    def wezel(xy_):
        v = xy(*xy_)
        return next((k for k, q in pola.items() if q.HitTest(v)), xy_)
    sas = {}
    for t in tr:
        if isinstance(t, p.PCB_VIA):
            continue
        a0 = (p.ToMM(t.GetStart().x), p.ToMM(t.GetStart().y)); a1 = (p.ToMM(t.GetEnd().x), p.ToMM(t.GetEnd().y)); L = math.dist(a0, a1) or 1e-9
        na = sorted({q for q in pkt if abs(math.dist(a0, q) + math.dist(q, a1) - L) < .005} | {a0, a1}, key=lambda q: math.dist(a0, q))
        for u, v in zip(na, na[1:]):
            u, v = wezel(u), wezel(v); sas.setdefault(u, set()).add(v); sas.setdefault(v, set()).add(u)
    def dojdzie(blok):
        seen, stos = {a}, [a]
        while stos:
            for m in sas.get(stos.pop(), ()):
                if m == cel:
                    return True
                if m not in seen and m != blok:
                    seen.add(m); stos.append(m)
        return False
    return dojdzie(None) and not dojdzie(przez_)


def odstep(q):
    """Najmniejszy odstęp pola q od miedzi innych sieci (ścieżki, przelotki, wylewki) w mm."""
    sh = q.GetEffectiveShape(p.F_Cu); dmin = 99.0
    for t in b.GetTracks():
        if t.GetNetCode() != q.GetNetCode():
            for L in (p.F_Cu, p.B_Cu):
                if t.IsOnLayer(L):
                    dmin = min(dmin, p.ToMM(sh.GetClearance(t.GetEffectiveShape(L))))
    for z in b.Zones():
        if z.GetIsRuleArea() or z.GetNetCode() == q.GetNetCode():
            continue
        for L in (p.F_Cu, p.B_Cu):
            if z.IsOnLayer(L):
                for k in range(10, 0, -1):   # 1,0 … 0,1 mm: największy pierścień, który nie dotyka wylewki
                    ps = p.SHAPE_POLY_SET(); q.TransformShapeToPolygon(ps, L, p.FromMM(k / 10), p.FromMM(.005), p.ERROR_INSIDE)
                    ps.BooleanIntersection(z.GetFilledPolysList(L))
                    if not ps.OutlineCount() or ps.Area() / 1e12 < 1e-4:
                        dmin = min(dmin, k / 10 if k < 10 else dmin); break
                else:
                    dmin = 0.0
    return round(dmin, 2)


d1_przez = {'CAN_H': przez('CAN_H', ('J3', '1'), ('D1', '2'), ('U1', '7')), 'CAN_L': przez('CAN_L', ('J3', '2'), ('D1', '1'), ('U1', '6'))}
odst = {f'J3.{n}': odstep(pad('J3', n)) for n in ('1', '2')}
jd = {'pad1_CAN_H': p1, 'pad2_CAN_L': p2, 'anchors': anchors, 'anchor_to_pads_mm': [round(a[0] - p1[0], 2) for a in anchors],
      'anchor_hole_edge_to_wall_mm': round(edge_gap, 2), 'keepouts': len(rz), 'copper_in_keepouts': cu, 'cable_strip': [round(v, 2) for v in strip],
      'parts_in_cable_strip': inside, 'D1_pad_to_J3_pad_mm': {k: round(v, 2) for k, v in d1.items()}, 'through_D1': d1_przez, 'other_net_copper_to_J3_pads_mm': odst}
ok = (net(pad('J3', '1')) == 'CAN_H' and net(pad('J3', '2')) == 'CAN_L' and len(anchors) == 2
      and all(a[0] - p1[0] > 11.9 for a in anchors) and p1[1] < p2[1] and abs(p1[0] - p2[0]) < .01
      and 2.0 <= edge_gap <= 6.0 and all(d1_przez.values()) and all(v >= .99 for v in odst.values()) and len(rz) == 2 and all(z.GetDoNotAllowTracks() and z.GetDoNotAllowVias() and z.GetDoNotAllowZoneFills()
                                                   and {p.F_Cu, p.B_Cu} <= set(z.GetLayerSet().Seq()) for z in rz)
      and not cu and not inside and 10 < min(p1[1], p2[1]) and max(p1[1], p2[1]) < 90 and all(v <= 6 for v in d1.values()))
check(f'J3 (OBD tail, W3) at the input wall: anchor holes towards x = {W} (12 mm from the solder row, hole edge 2-6 mm from the edge), '
      'pad 1 CAN_H at the smaller y, not in the edge A / B zones; no copper within 3 mm of the anchor-hole centres; no part under the cable '
      'between the anchor and the wall; D1 (PESD2CAN) pads <= 6 mm from the J3 pads and CAN_H / CAN_L pass through them to U1; '
      'other nets >= 1 mm from the J3 pads (hand-soldered wires)', ok, jd)
# ---------------- 7. placement requirements (decoupling, drivers) ----------------
DEC = {'C1': ('U1', '3'), 'C2': ('U1', '5'), 'C3': ('U2', '14')}
dd = {}
for c, (u, n) in DEC.items():
    q = next(a for a in fmap[c].Pads() if a.GetNetname() == pad(u, n).GetNetname()); dd[f'{c}-{u}.{n}'] = round(math.dist(pos(q.GetPosition()), pxy(u, n)), 2)
check('Decoupling at the IC pins: 100 nF pad <= 6 mm from its supply pin (C1 U1.3 VCC, C2 U1.5 VIO, C3 U2.14; limit as P03 R6 / P09 R2)',
      all(v <= 6 for v in dd.values()), dd)
q = next(a for a in fmap['R1'].Pads() if a.GetNetname() == pad('U2', '3').GetNetname()); dv = {'R1-U2.3': round(math.dist(pos(q.GetPosition()), pxy('U2', '3')), 2)}
check('Series resistor at its driver: R1 (100 R, CAN_RX to P03) pad <= 6 mm from U2.3', all(v <= 6 for v in dv.values()), dv)
# ---------------- 8. GND ----------------
isl = {b.GetLayerName(L): sum(z.GetFilledPolysList(L).OutlineCount() for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND' and z.IsOnLayer(L)) for L in (p.F_Cu, p.B_Cu)}
cov = {b.GetLayerName(L): round(sum(z.GetFilledPolysList(L).Area() for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND' and z.IsOnLayer(L)) / 1e12 / (W * H) * 100, 1)
       for L in (p.F_Cu, p.B_Cu)}
check('GND pours on both layers: B.Cu >= 50 % of the board; island removal always (every island tied)', cov['B.Cu'] >= 50 and all(z.GetIslandRemovalMode() == p.ISLAND_REMOVAL_MODE_ALWAYS
      for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND') and len([z for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND']) == 2,
      {'cover_percent': cov, 'islands': isl})
# ---------------- 9. silkscreen ----------------
cour = {}; side = {}
for f in b.GetFootprints():
    if f.GetReference() not in holes_ref:
        f.BuildCourtyardCaches(); cour[f.GetReference()] = f.GetCourtyard(p.B_CrtYd if f.IsFlipped() else p.F_CrtYd); side[f.GetReference()] = f.IsFlipped()


def inside_other(t, own):
    r = t.GetBoundingBox(); x0, y0, x1, y1 = p.ToMM(r.GetLeft()), p.ToMM(r.GetTop()), p.ToMM(r.GetRight()), p.ToMM(r.GetBottom())
    smp = [(x0 + (x1 - x0) * i / 4, y0 + (y1 - y0) * j / 2) for i in range(5) for j in range(3)]
    bot = t.GetLayer() == p.B_SilkS
    return sorted({r_ for r_, cy in cour.items() if r_ not in own and side[r_] == bot for q in smp if cy.Contains(xy(*q))})


amb = {}
for f in b.GetFootprints():
    r = f.GetReference(); ref = f.Reference()
    if r in holes_ref or not ref.IsVisible():
        continue
    o = inside_other(ref, {r})
    if o:
        amb[r] = o
check('Every visible reference outside the courtyards of other parts', not amb, amb)
blisko = {}
for f in b.GetFootprints():
    r = f.GetReference(); t = f.Reference()
    if r in holes_ref or not t.IsVisible() or r not in cour:
        continue
    c_ = t.GetBoundingBox().GetCenter(); dist_ = lambda poly: 0.0 if poly.Contains(c_) else math.sqrt(poly.SquaredDistance(c_)) / 1e6
    mine = dist_(cour[r]); inne = sorted((dist_(cy), o) for o, cy in cour.items() if o != r and side[o] == side[r])
    if inne and inne[0][0] <= mine:
        blisko[r] = {'own_mm': round(mine, 2), 'nearest_other': inne[0][1], 'other_mm': round(inne[0][0], 2)}
check('Every visible reference nearer its own part than any other (text centre to courtyard; review 1.10)', not blisko, blisko)
znaki = {}
for r_, zn in PIN_MARKS.items():
    for num, t_ in zn.items():
        q = pad(r_, num); qx, qy = pxy(r_, num)
        znaki[f'{r_}.{num} {t_}'] = [s_ for s_, t in texts if s_ == t_ and math.dist((p.ToMM(t.GetPosition().x), p.ToMM(t.GetPosition().y)), (qx, qy)) <= 3.0]
check('Pin 1 / polarity marks of module and wire connectors on the silkscreen, <= 3 mm from their pads (S1 §9; review 1.10)',
      all(len(v) == 1 for v in znaki.values()), znaki)
title = [s for s, t in texts if s == TYTUL]
marks = [s for s, t in texts if s.startswith('KRAWEDZ A') or s.startswith('KRAWEDZ B')]
check(f'Silkscreen: board name "{TYTUL}", edge markers A and B', bool(title) and any(m.startswith('KRAWEDZ A') for m in marks) and any(m.startswith('KRAWEDZ B') for m in marks), {'title': title, 'marks': marks})

res = {'board': str(path), 'board_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'checks': checks, 'details': details,
       'passed': sum(c['pass'] for c in checks), 'total': len(checks)}
out.mkdir(parents=True, exist_ok=True)
(out / 'pcb-checks.json').write_text(json.dumps(res, indent=2, ensure_ascii=False, default=str) + '\n', encoding='utf-8')
for c in checks:
    print('PASS' if c['pass'] else 'FAIL', c['check'])
print(f"{res['passed']}/{res['total']} PCB checks passed")
sys.exit(0 if res['passed'] == res['total'] else 1)
