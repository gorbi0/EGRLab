"""Independent checks of the finished P11 R2 PCB (fresh native DRC + the requirements of the user 4.10 for the panel wiring board).
Structure and the generic checks (DRC receipt, netlist, D7 zones, rings, references) from P10 R2 verify_pcb.py; the board-specific
checks are new: outline limit, M3 corners, J_P12 on the wall-A edge, wire fields at the panel edge with their anchors, one silk label
per field column resolved against the schematic, R1 variant note, legend size, 0.4 mm supplies.
usage: KiCad Python verify_pcb.py [alternative_board] [report_dir]
The alternative board is used by negative_controls.py (copies with one deliberate defect each).
Sources of the expected values: board.py (outline and holes as decided), docs/J_P12.csv (P12 contract), docs/parts.json (contacts
X11-X17 / X6 and the R1 variant), docs/PORTY.csv (TEST cavities), the user's requirements (README "Decyzje", "PCB"); the silk label
table of silkscreen.py is NOT used: every printed label is parsed and resolved to nets independently.
"""
from pathlib import Path
import pcbnew as p, json, sys, os, math, hashlib, csv, re, xml.etree.ElementTree as ET
from sexpr import parse, one, sub
from provenance import run_fresh_drc
sys.path.insert(0, str(Path(__file__).resolve().parent))
from board import NAME, REV, W, H, LIMIT, R_CORNER, THICKNESS, CU_UM, HOLES, HOLE_D, HOLE_ZONE_D, JBP as JBP_ZL, FIELDS, WIDE, SIGNAL_W, SUPPORT_KEEPOUT
TYTUL = f'{REV} PANEL'
P = Path(__file__).resolve().parents[1]
path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else P / f'eda/{NAME}.kicad_pcb'
out = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else P / 'verification'
b = p.LoadBoard(str(path)); b.BuildConnectivity()
root = ET.parse(P / f'verification/{NAME}.xml').getroot(); parts = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
checks = []; details = {}
JP = {}
with open(P / 'docs/J_P12.csv', encoding='utf-8-sig') as fh:
    for r in csv.DictReader(fh, delimiter=';'):
        JP[int(r['pin'])] = r['siec']
PORT_TEST = {}
with open(P / 'docs/PORTY.csv', encoding='utf-8-sig') as fh:
    for r in csv.DictReader(fh, delimiter=';'):
        if r['port'] == 'TEST':
            PORT_TEST[int(r['komora'])] = r['siec']


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
check(f'Parts: the {len(onboard)} on-board parts of the schematic + 4 mounting holes, nothing else', set(fmap) == onboard | holes_ref and len(holes_ref) == 4,
      {'board': sorted(fmap)})
pin = {}
for n in root.findall('./nets/net'):
    for node in n.findall('node'):
        pin[node.get('ref'), node.get('pin')] = n.get('name')
errors = []; npads = 0
for r in sorted(onboard & set(fmap)):
    f = fmap[r]; c = comps[r]
    if f.GetValue() != c.findtext('value') or f.GetFPIDAsString() != c.findtext('footprint'):
        errors.append(r + ' fields')
    for a in f.Pads():
        if a.GetNumber():
            npads += 1
            if a.GetNetname() != pin.get((r, a.GetNumber()), ''):
                errors.append(f'{r}.{a.GetNumber()} net')
check('Netlist: every value, footprint ID and pad net equals the exported schematic netlist', not errors and npads > 0, {'errors': errors, 'pads': npads})
stack = one(one(parse(path.read_text(encoding='utf-8')), 'setup'), 'stackup')
cu = {x[1]: float(one(x, 'thickness')[1]) for x in sub(stack, 'layer') if x[1] in ['F.Cu', 'B.Cu']}
check(f'Board stack: 2 copper layers of {CU_UM} um, FR4 {THICKNESS} mm', b.GetCopperLayerCount() == 2 and abs(p.ToMM(b.GetDesignSettings().GetBoardThickness()) - THICKNESS) < 1e-6
      and cu == {'F.Cu': CU_UM / 1000, 'B.Cu': CU_UM / 1000}, cu)
check('All parts on the top side (wire fields and the header are soldered from the top; nothing under the board lying on the panel-zone floor)',
      not [f.GetReference() for f in b.GetFootprints() if f.IsFlipped()], [f.GetReference() for f in b.GetFootprints() if f.IsFlipped()])
edge = [g for g in b.GetDrawings() if g.GetLayer() == p.Edge_Cuts]
arcs = [g for g in edge if g.GetShape() == p.SHAPE_T_ARC]; segs = [g for g in edge if g.GetShape() == p.SHAPE_T_SEGMENT]
bb = b.GetBoardEdgesBoundingBox(); hw = max(p.ToMM(g.GetWidth()) for g in edge) / 2
ext = [p.ToMM(bb.GetLeft()) + hw, p.ToMM(bb.GetTop()) + hw, p.ToMM(bb.GetRight()) - hw, p.ToMM(bb.GetBottom()) - hw]
dims = (round(ext[2] - ext[0], 3), round(ext[3] - ext[1], 3))
check(f'Outline: {W:g} x {H:g} mm within the limit {LIMIT[0]:g} x {LIMIT[1]:g} mm (user 4.10), long side along y (the panel wall), 4 corner arcs R {R_CORNER:g}',
      len(segs) == 4 and len(arcs) == 4 and all(abs(p.ToMM(a.GetRadius()) - R_CORNER) < 1e-4 for a in arcs) and all(abs(v) < 1e-3 for v in ext[:2])
      and abs(dims[0] - W) < 1e-3 and abs(dims[1] - H) < 1e-3 and dims[0] <= LIMIT[0] and dims[1] <= LIMIT[1] and dims[1] > dims[0],
      {'outline_mm': dims, 'arcs': len(arcs), 'segments': len(segs)})
# ---------------- 3. M3 holes in the corners, D7 zones ----------------
got_h = sorted(pos(fmap[r].GetPosition()) for r in holes_ref)
hole_ok = all(list(fmap[r].Pads())[0].GetAttribute() == p.PAD_ATTRIB_NPTH and pos(list(fmap[r].Pads())[0].GetDrillSize()) == (HOLE_D, HOLE_D) for r in holes_ref)
jcy = None
if 'J_P12' in fmap:
    fmap['J_P12'].BuildCourtyardCaches(); jcy = p.ToMM(fmap['J_P12'].GetCourtyard(p.F_CrtYd).BBox().GetBottom())
quad = sorted((x < W / 2, y < H / 2) for x, y in got_h)
corner = [(x, y) for x, y in got_h if abs(min(x, W - x) - 4.0) < .01 and (min(y, H - y) <= 4.5 or (y < H / 2 and jcy is not None and 0 <= y - HOLE_ZONE_D / 2 - jcy <= 6.0))]
check('M3 holes: 4 NPTH 3.2 mm, one per corner, 4 mm from the long edges; bottom pair <= 4.5 mm from the short edge, top pair directly behind '
      'J_P12 (D7 zone edge 0-6 mm beyond its courtyard: the header fills the short edge)',
      hole_ok and len(got_h) == 4 and quad == sorted({(a, c) for a in (True, False) for c in (True, False)}) and len(corner) == 4
      and all(math.dist(a, c) < .005 for a, c in zip(got_h, sorted(HOLES))), {'holes': got_h, 'J_P12_courtyard_bottom': jcy})
RZ = HOLE_ZONE_D / 2
near = set(); cop = []
for f in b.GetFootprints():
    if f.GetReference() in holes_ref:
        continue
    f.BuildCourtyardCaches(); cy = f.GetCourtyard(p.B_CrtYd if f.IsFlipped() else p.F_CrtYd)
    for hx, hy in got_h:
        circ = p.SHAPE_POLY_SET(); circ.NewOutline()
        for k in range(64):
            circ.Append(p.FromMM(hx + RZ * math.cos(k * math.tau / 64)), p.FromMM(hy + RZ * math.sin(k * math.tau / 64)))
        x = p.SHAPE_POLY_SET(cy); x.BooleanIntersection(circ)
        if x.Area() > 0:
            near.add((f.GetReference(), (hx, hy)))
for hx, hy in got_h:
    circ = p.SHAPE_POLY_SET(); circ.NewOutline()
    for k in range(64):
        circ.Append(p.FromMM(hx + (RZ - .01) * math.cos(k * math.tau / 64)), p.FromMM(hy + (RZ - .01) * math.sin(k * math.tau / 64)))
    cop += [(h, (hx, hy)) for h in shape_hits_copper(circ)]
rules_ok = sum(1 for z in b.Zones() if z.GetIsRuleArea() and z.GetZoneName().startswith('M3 ') and z.GetDoNotAllowTracks() and z.GetDoNotAllowVias() and z.GetDoNotAllowZoneFills()
               and set(z.GetLayerSet().Seq()) == {p.F_Cu, p.B_Cu})
check('Standoff zones D7: no courtyard and no copper (pads, tracks, vias, pours) within 3.5 mm of a hole centre; rule areas on both layers',
      not near and not cop and rules_ok == 4, {'courtyards': sorted(map(str, near)), 'copper': sorted(map(str, cop)), 'rule_areas': rules_ok})
# ---------------- 4. rules, widths, rings ----------------
pro = json.loads((path.parent / f'{NAME}.kicad_pro').read_text()); ds = pro['board']['design_settings']; rules = ds['rules']
cls = {c['name']: c for c in pro['net_settings']['classes']}
pats = {q['pattern']: q['netclass'] for q in pro['net_settings'].get('netclass_patterns') or []}
check('Rules: clearance >= 0.25, track >= 0.3, copper to edge 0.5, ring >= 0.25, DRC legend minimum 1.0 / 0.15 mm (JLCPCB), class P3V3 0.4 mm '
      'for PANEL_3V3 / 3V3_IO; no DRC exclusions',
      rules['min_clearance'] >= .25 and rules['min_track_width'] >= .3 - 1e-9 and rules['min_copper_edge_clearance'] >= .5 and rules['min_via_annular_width'] >= .25
      and rules.get('min_text_height', 0) >= 1.0 - 1e-9 and rules.get('min_text_thickness', 0) >= .15 - 1e-9 and cls['Default']['track_width'] >= .3 - 1e-9
      and not ds['drc_exclusions'] and all(c['clearance'] >= .25 for c in cls.values())
      and all(pats.get(n) == 'P3V3' for n in WIDE) and cls.get('P3V3', {}).get('track_width', 0) >= max(WIDE.values()) - 1e-9,
      {k: rules.get(k) for k in ('min_clearance', 'min_track_width', 'min_text_height', 'min_text_thickness')})
narrow = sorted({(net(t), round(p.ToMM(t.GetWidth()), 3)) for t in b.GetTracks() if not isinstance(t, p.PCB_VIA)
                 and p.ToMM(t.GetWidth()) < WIDE.get(net(t), SIGNAL_W) - 1e-6})
widths = {}
for t in b.GetTracks():
    if not isinstance(t, p.PCB_VIA):
        widths.setdefault(net(t), set()).add(round(p.ToMM(t.GetWidth()), 3))
check('Track widths: every track >= 0.3 mm; PANEL_3V3 and 3V3_IO >= 0.4 mm (user 4.10)', not narrow and all(n in widths for n in WIDE),
      {'too_narrow': narrow, 'widths': {k: sorted(v) for k, v in sorted(widths.items())}})
ring = [f'{f.GetReference()}.{a.GetNumber()}' for f in b.GetFootprints() for a in f.Pads() if a.GetAttribute() == p.PAD_ATTRIB_PTH
        and (min(p.ToMM(a.GetSize().x), p.ToMM(a.GetSize().y)) - p.ToMM(a.GetDrillSize().x)) / 2 < .25 - 1e-6]
ring += [f'via {pos(t.GetPosition())}' for t in b.GetTracks() if isinstance(t, p.PCB_VIA) and (p.ToMM(t.GetWidth(p.F_Cu)) - p.ToMM(t.GetDrill())) / 2 < .25 - 1e-6]
check('Every PTH pad and via has an annular ring >= 0.25 mm (measured on the copper)', not ring, ring[:20])
# ---------------- 5. J_P12 on the short edge facing wall A (contract docs/J_P12.csv) ----------------
texts = [(t.GetText(), t) for t in b.GetDrawings() if isinstance(t, p.PCB_TEXT) and t.GetLayer() == p.F_SilkS]


def tpos(t):
    c = t.GetBoundingBox().GetCenter(); return (p.ToMM(c.x), p.ToMM(c.y))


f = fmap.get('J_P12'); jd = {}; ok = False
if f is not None:
    pads1 = {a.GetNumber(): pos(a.GetPosition()) for a in f.Pads() if a.GetNumber()}; fab = layer_bbox(f, p.F_Fab)
    xs = [v[0] for v in pads1.values()]; nets = {int(n): net(pad('J_P12', n)) for n in pads1}
    one_ = [t for s_, t in texts if s_ == '1' and math.dist(tpos(t), pads1['1']) <= 2.6]
    farther = all(math.dist(tpos(t), pads1['1']) < min(math.dist(tpos(t), pads1[k]) for k in pads1 if k != '1') for t in one_)
    ok = ('IDC-Header_2x10_P2.54mm_Horizontal' in f.GetFPIDAsString() and len(pads1) == 20 and nets == JP and fab is not None and abs(fab[1]) < .3
          and min(v[1] for v in pads1.values()) > fab[1] and pads1['1'][0] == min(xs) and abs((min(xs) + max(xs)) / 2 - W / 2) < .05
          and len(one_) == 1 and farther and not f.IsFlipped())
    jd = {'body_front_y': fab and round(fab[1], 3), 'pin1': pads1['1'], 'pins_centre_x': round((min(xs) + max(xs)) / 2, 3), 'pinout_equals_J_P12.csv': nets == JP,
          'pin1_marks': [tpos(t) for t in one_]}
check('J_P12: IDC 2x10 right-angle box header on the short edge y = 0 (wall A, ribbon to P12): mating face within 0.3 mm of the edge, '
      'pins centred on the width, pin 1 at the smaller x with one silk "1" next to it, pinout = docs/J_P12.csv', ok, jd)
# ---------------- 6. wire fields at the panel edge x = 0 ----------------
fd = {}; okf = True
for r in FIELDS:
    f = fmap.get(r)
    if f is None:
        okf = False; fd[r] = 'missing'; continue
    q = [a for a in f.Pads() if a.GetNumber()]; anc = [a for a in f.Pads() if a.GetAttribute() == p.PAD_ATTRIB_NPTH]
    drills = sorted({round(p.ToMM(a.GetDrillSize().x), 3) for a in q}); sizes = sorted({round(min(p.ToMM(a.GetSize().x), p.ToMM(a.GetSize().y)), 3) for a in q})
    ap = sorted(pos(a.GetPosition()) for a in anc); px = [pos(a.GetPosition())[0] for a in q]; py = [pos(a.GetPosition())[1] for a in q]
    rz = [z for z in b.Zones() if z.GetIsRuleArea() and z.GetZoneName().startswith(f'{r} support')]
    cu_ = [h for z in rz for h in shape_hits_copper(z.Outline())]
    strip = (0.0, min(py) - 1.75, min(px), max(py) + 1.75)   # where the wires lie: from the pads to the panel edge
    inside = sorted(o for o in fmap if o not in holes_ref and o != r and cbox(o)[0] < strip[2] and strip[0] < cbox(o)[2] and cbox(o)[1] < strip[3] and strip[1] < cbox(o)[3])
    edge_gap = [round(x - HOLE_D / 2, 2) for x, _ in ap]
    span = (min(y for _, y in ap), max(y for _, y in ap)) if ap else (0, 0)
    good = (all(1.0 - 1e-6 <= d <= 1.1 + 1e-6 for d in drills) and all(s_ >= 2.0 - 1e-6 for s_ in sizes) and len(anc) == 2
            and all(pos(a.GetDrillSize()) == (HOLE_D, HOLE_D) for a in anc) and all(2.0 <= g <= 6.0 for g in edge_gap)
            and all(x < min(px) - 8.0 for x, _ in ap) and span[0] < min(py) and max(py) < span[1] and min(px) < W / 2
            and len(rz) == 2 and not cu_ and not inside and all({p.F_Cu, p.B_Cu} <= set(z.GetLayerSet().Seq()) and z.GetDoNotAllowTracks()
                                                               and z.GetDoNotAllowVias() and z.GetDoNotAllowZoneFills() for z in rz))
    okf &= good
    fd[r] = {'drill_mm': drills, 'pad_mm': sizes, 'anchors': ap, 'anchor_hole_edge_to_panel_edge_mm': edge_gap, 'pads_x': sorted(set(px)),
             'copper_in_anchor_keepouts': cu_, 'parts_in_wire_strip': inside, 'ok': good}
check('Wire fields J11 / J8 / J6 at the panel edge x = 0: holes 1.0-1.1 mm, pads >= 2.0 mm (AWG24); 2 cable-tie anchors Ø3.2 NPTH between '
      'the pads and the panel edge (hole edge 2-6 mm from it, spanning the pad rows), no copper within 3 mm of the anchors, no other part '
      'in the strip where the wires lie', okf, fd)
# ---------------- 7. one silk label per field column, resolved against the schematic ----------------
LBL = re.compile(r'^(X\d+)\.(\d+)-(\d+) \S')


def resolve(t):
    """Nets a printed label stands for (from the schematic data), or None if the text is not a field label."""
    m = LBL.match(t)
    if m and m.group(1) in parts:
        pp = parts[m.group(1)]['pins']; return {pp.get(m.group(2)), pp.get(m.group(3))}
    m = re.match(r'^TEST kom\.(\d+)$', t)
    if m:
        return {PORT_TEST.get(int(m.group(1)))}
    if t in ('SCOPE srodek', 'SCOPE ekran'):
        return {parts['X6']['pins']['1' if t.endswith('srodek') else '2']}
    return None


lab = {}; okl = True
for r in FIELDS:
    if r not in fmap:
        okl = False; continue
    cols = {}
    for a in fmap[r].Pads():
        if a.GetNumber():
            cols.setdefault(pos(a.GetPosition())[1], []).append(a)
    for y, q in sorted(cols.items()):
        xr = max(pos(a.GetPosition())[0] + p.ToMM(a.GetSize().x) / 2 for a in q)
        cand = [(s_, t) for s_, t in texts if resolve(s_) is not None and abs(tpos(t)[1] - y) <= .6 and xr < p.ToMM(t.GetBoundingBox().GetLeft()) < xr + 3.0]
        nets_ = {net(a) for a in q}; got = [s_ for s_, _ in cand]
        good = len(cand) == 1 and resolve(cand[0][0]) == nets_
        okl &= good; lab[f"{r} {'/'.join(sorted((a.GetNumber() for a in q), key=int))}"] = {'label': got, 'nets': sorted(nets_), 'ok': good}
allf = [s_ for s_, _ in texts if resolve(s_) is not None]
check('Field labels: every column of J11 / J8 / J6 has exactly one silk label beside it naming the panel contact; the label resolves '
      '(parts.json X11-X17 / X6 pins, docs/PORTY.csv TEST cavities) to exactly the nets of the column pads',
      okl and len(allf) == len(set(allf)) == len(lab), lab)
# ---------------- 8. R1 variant note ----------------
r1 = fmap.get('R1'); vd = {}; okv = False
if r1 is not None:
    c1 = pos(r1.GetPosition()); var = parts['R1'].get('variant', {})
    want = {'LOGGER: LUTOWAC': var.get('LOGGER') == 'fitted', 'Z P04: DNP': var.get('FULL') == 'DNP'}
    found = {w: [round(math.dist(tpos(t), c1), 1) for s_, t in texts if s_ == w and math.dist(tpos(t), c1) <= 12.0] for w in want}
    okv = all(want.values()) and all(len(v) == 1 for v in found.values())
    vd = {'variant_in_parts.json': var, 'notes_mm_from_R1': found}
check('R1 variant note on the silkscreen next to R1 (<= 12 mm): "LOGGER: LUTOWAC" and "Z P04: DNP", matching the variant in parts.json', okv, vd)
# ---------------- 9. legend size ----------------
small = []
for s_, t in texts:
    if p.ToMM(t.GetTextHeight()) < 1.0 - 1e-6 or p.ToMM(t.GetTextThickness()) < .15 - 1e-6:
        small.append((s_, round(p.ToMM(t.GetTextHeight()), 2), round(p.ToMM(t.GetTextThickness()), 3)))
for f in b.GetFootprints():
    for t in [f.Reference()] + [g for g in f.GraphicalItems() if isinstance(g, p.PCB_TEXT)]:
        if t.GetLayer() == p.F_SilkS and t.IsVisible() and (p.ToMM(t.GetTextHeight()) < 1.0 - 1e-6 or p.ToMM(t.GetTextThickness()) < .15 - 1e-6):
            small.append((f.GetReference() + ':' + t.GetText(), round(p.ToMM(t.GetTextHeight()), 2), round(p.ToMM(t.GetTextThickness()), 3)))
check('Legend size: every visible silk text >= 1.0 mm high with a line >= 0.15 mm (JLCPCB minimum)', not small, small)
# ---------------- 10. GND ----------------
cov = {b.GetLayerName(L): round(sum(z.GetFilledPolysList(L).Area() for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND' and z.IsOnLayer(L)) / 1e12 / (W * H) * 100, 1)
       for L in (p.F_Cu, p.B_Cu)}
gv = sum(1 for t in b.GetTracks() if isinstance(t, p.PCB_VIA) and net(t) == 'GND')
pours = [z for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND']
check('GND pours on both layers (each >= 50 % of the board), island removal always, >= 20 GND stitching vias',
      len(pours) == 2 and {z.GetLayer() for z in pours} == {p.F_Cu, p.B_Cu} and all(v >= 50 for v in cov.values()) and gv >= 20
      and all(z.GetIslandRemovalMode() == p.ISLAND_REMOVAL_MODE_ALWAYS for z in pours), {'cover_percent': cov, 'gnd_vias': gv})
# ---------------- 11. references and board texts ----------------
cour = {}; side = {}
for f in b.GetFootprints():
    if f.GetReference() not in holes_ref:
        f.BuildCourtyardCaches(); cour[f.GetReference()] = f.GetCourtyard(p.B_CrtYd if f.IsFlipped() else p.F_CrtYd); side[f.GetReference()] = f.IsFlipped()


def inside_other(t, own):
    r = t.GetBoundingBox(); x0, y0, x1, y1 = p.ToMM(r.GetLeft()), p.ToMM(r.GetTop()), p.ToMM(r.GetRight()), p.ToMM(r.GetBottom())
    smp = [(x0 + (x1 - x0) * i / 4, y0 + (y1 - y0) * j / 2) for i in range(5) for j in range(3)]
    bot = t.GetLayer() == p.B_SilkS
    return sorted({r_ for r_, cy in cour.items() if r_ not in own and side[r_] == bot for q in smp if cy.Contains(xy(*q))})


amb = {}; hidden = []
for f in b.GetFootprints():
    r = f.GetReference(); ref = f.Reference()
    if r in holes_ref:
        continue
    if not ref.IsVisible():
        hidden.append(r); continue
    o = inside_other(ref, {r})
    if o:
        amb[r] = o
check('Every visible reference outside the courtyards of other parts; every part has a visible reference', not amb and not hidden, {'inside_other': amb, 'hidden': hidden})
blisko = {}
for f in b.GetFootprints():
    r = f.GetReference(); t = f.Reference()
    if r in holes_ref or not t.IsVisible() or r not in cour:
        continue
    c_ = t.GetBoundingBox().GetCenter(); dist_ = lambda poly: 0.0 if poly.Contains(c_) else math.sqrt(poly.SquaredDistance(c_)) / 1e6
    mine = dist_(cour[r]); inne = sorted((dist_(cy), o) for o, cy in cour.items() if o != r and side[o] == side[r])
    if (inne and inne[0][0] <= mine) or mine > 3.0:
        blisko[r] = {'own_mm': round(mine, 2), 'nearest_other': inne[0][1] if inne else None, 'other_mm': round(inne[0][0], 2) if inne else None}
check('Every visible reference nearer its own part than any other and <= 3 mm from its courtyard (text centre)', not blisko, blisko)
title = [s_ for s_, t in texts if s_ == TYTUL]
mark = [tpos(t) for s_, t in texts if s_ == 'STRONA PANELU' and tpos(t)[0] < 3.0]
check(f'Silkscreen: board name "{TYTUL}" and the marker "STRONA PANELU" along the panel edge x = 0', len(title) == 1 and len(mark) == 1, {'title': title, 'panel_marker': mark})

res = {'board': str(path), 'board_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'checks': checks, 'details': details,
       'passed': sum(c['pass'] for c in checks), 'total': len(checks)}
out.mkdir(parents=True, exist_ok=True)
(out / 'pcb-checks.json').write_text(json.dumps(res, indent=2, ensure_ascii=False, default=str) + '\n', encoding='utf-8')
for c in checks:
    print('PASS' if c['pass'] else 'FAIL', c['check'])
print(f"{res['passed']}/{res['total']} PCB checks passed")
sys.exit(0 if res['passed'] == res['total'] else 1)
