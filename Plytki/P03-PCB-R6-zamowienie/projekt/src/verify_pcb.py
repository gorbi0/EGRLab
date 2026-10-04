"""Independent checks of the finished P03 R6 PCB in format S1 (fresh native DRC + S1 and P03-specific rules).
usage: KiCad Python verify_pcb.py [alternative_board] [report_dir]
The alternative board is used by negative_controls.py (copies with one deliberate defect each).
Sources of the expected values: Plytki/Format-S1/format-s1.json and SPECYFIKACJA-FORMATU-S1.md (S1-3), the P12 contracts
docs/J_BP.csv and docs/SERWIS.csv, the README layout requirements and ZASILANIE-RESET.md (5 V budget); nothing is read from
placement.py or route_critical.py.
"""
from pathlib import Path
import pcbnew as p, json, sys, os, math, hashlib, csv, ast, xml.etree.ElementTree as ET
from sexpr import parse, one, sub
from provenance import run_fresh_drc
sys.path.insert(0, str(Path(__file__).resolve().parent))
from heights import height
P = Path(__file__).resolve().parents[1]
path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else P / 'eda/P03.kicad_pcb'
out = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else P / 'verification'
b = p.LoadBoard(str(path)); b.BuildConnectivity()
S1 = json.loads((P.parents[0] / 'Format-S1/format-s1.json').read_text(encoding='utf-8'))
root = ET.parse(P / 'verification/P03.xml').getroot(); parts = json.loads(Path(os.environ.get('P03_PARTS_JSON', P / 'docs/parts.json')).read_text(encoding='utf-8'))
checks = []; details = {}
KLASA, SLOTY = 'L', ['S1', 'S2', 'S3']
W, H = S1['klasy'][KLASA]['W'], S1['klasy'][KLASA]['H']; STEP = S1['rozstaw_slotow']
HMAX = S1['poziomy']['wys_max_gora_standard']              # level 2, standoffs 20 mm
JBP = {}
with open(P / 'docs/J_BP.csv', encoding='utf-8-sig') as fh:
    for r in csv.DictReader(fh, delimiter=';'):
        JBP.setdefault(r['zlacze'], {})[int(r['pin'])] = r['siec']
SERW = {}
with open(P / 'docs/SERWIS.csv', encoding='utf-8-sig') as fh:
    for r in csv.DictReader(fh, delimiter=';'):
        SERW.setdefault(r['zlacze'], {})[int(r['pin'])] = (r['siec'], r['rezystor'])
HIGHZ = {'SUP_RAW_N', 'SUP_N', 'PFAIL_N', 'I2C_SCL', 'I2C_SDA', 'CORE_LINK'}   # S1 §6: 10 kOhm (pull-up / open drain nodes)
HIGHZ |= {'SUP_N_OUT'}   # 1.10 (review, user decision): R70 10K although driven, so the service branch stays off the reset edge
TYTUL = 'P03 R6 S1-L S1-S3'   # S1 §9: name, revision, class and slots (as P02 R4, P09 / P10 R2)
SILK = {n.targets[0].id: ast.literal_eval(n.value) for n in ast.parse((P / 'src/silkscreen.py').read_text(encoding='utf-8')).body
        if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') in ('LABEL', 'ABBR')}   # 1.10 (review): labels expected from the tables, not from the result
# Library F.Fab of PinHeader_1x13_P2.54mm_Horizontal starts 0.37 mm before the pin row (pin stubs); the pin row stands 4.04 mm inside
# edge B, so the plastic body front is at the edge and the pins stick out ~6 mm (S1 section 6). 1.10 (review): was an inline expression.
SV_FAB_TOP = S1['klasy'][KLASA]['H'] - 4.04 - .37
USB_MAX, CARD_MAX = 6.5, 6.5    # decision 30.09 (README): modules stop at the service-header courtyards, ~6.2 mm inside edge B


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
    """As rect_hits_copper for any outline (30.09: the SD1 keepouts are circles; their bounding squares caught the pour
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


def pads_equal_library(ref):
    """1.10 (review): an accepted lib_footprint_mismatch may differ from the library footprint only outside the copper - every pad
    (number, position in the footprint, size, drill, shape, type) equals the local library copy (eda/libraries)."""
    f = fmap.get(ref)
    if f is None or f.IsFlipped():
        return False
    lib, name = f.GetFPIDAsString().split(':'); g = p.FootprintLoad(str(P / 'eda/libraries' / (lib + '.pretty')), name)
    def sig(a, v):
        return (a.GetNumber(), round(p.ToMM(v.x), 3), round(p.ToMM(v.y), 3), round(p.ToMM(a.GetSize(p.F_Cu).x), 3), round(p.ToMM(a.GetSize(p.F_Cu).y), 3),
                round(p.ToMM(a.GetDrillSize().x), 3), int(a.GetShape(p.F_Cu)), int(a.GetAttribute()))
    return g is not None and sorted(sig(a, a.GetFPRelativePosition()) for a in f.Pads()) == sorted(sig(a, a.GetPosition()) for a in g.Pads())


lib_ok = [v for v in drc['violations'] if v['type'] == 'lib_footprint_mismatch'
          and all(fp_uuid.get(i['uuid']) in trimmed and pads_equal_library(fp_uuid.get(i['uuid'])) for i in v['items'])]
rest = [v for v in drc['violations'] if v not in lib_ok]
ignored = sorted(k for k, v in json.loads((P / 'eda/P03.kicad_pro').read_text(encoding='utf-8'))['board']['design_settings']['rule_severities'].items() if v == 'ignore')
no_yard = []
for f in b.GetFootprints():
    f.BuildCourtyardCaches()
    if not f.GetCourtyard(p.B_CrtYd if f.IsFlipped() else p.F_CrtYd).OutlineCount():
        no_yard.append(f.GetReference())
check('Fresh native DRC: 0 violations / 0 unconnected / 0 schematic parity (every rule the project does not set to ignore, list in the details; '
      'missing_courtyard ignored, so only the M3 holes may lack one; lib_footprint_mismatch only for parts whose silk silkscreen.py trimmed '
      'and whose pads equal the library)',
      not rest and not drc['unconnected_items'] and not drc['schematic_parity'] and all(r.startswith('H') and r[1:].isdigit() for r in no_yard),
      dict(receipt['counts'], other_violations=len(rest), other_types=sorted({v['type'] for v in rest}), ignored_rules=ignored, without_courtyard=sorted(no_yard),
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
check('S1-2 section 4: parts on the bottom only SMD <= 1.5 mm, no SOIC (level 2), >= 1 mm from THT pads',
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
pro = json.loads((P / 'eda/P03.kicad_pro').read_text()); ds = pro['board']['design_settings']; rules = ds['rules']
cls = {c['name']: c for c in pro['net_settings']['classes']}
check('Rules as P02 R3 / R4 (clearance >= 0.25, edge 0.5), annular ring >= 0.25 mm (S1); tracks >= 0.20 mm, 3V3_CORE class 0.30, PWR 0.60 '
      '(user decision 30.09: signals 0.2 mm on P03 R6 only); no DRC exclusions',
      rules['min_clearance'] >= .25 and rules['min_track_width'] >= .2 and rules['min_copper_edge_clearance'] >= .5 and rules['min_via_annular_width'] >= .25
      and cls.get('CORE3V3', {}).get('track_width') == .3 and cls.get('PWR', {}).get('track_width') == .6
      and not ds['drc_exclusions'] and all(c['clearance'] >= .25 for c in cls.values()))
ring = [f'{f.GetReference()}.{a.GetNumber()}' for f in b.GetFootprints() for a in f.Pads() if a.GetAttribute() == p.PAD_ATTRIB_PTH
        and (min(p.ToMM(a.GetSize().x), p.ToMM(a.GetSize().y)) - p.ToMM(a.GetDrillSize().x)) / 2 < .25 - 1e-6]
ring += [f'via {pos(t.GetPosition())}' for t in b.GetTracks() if isinstance(t, p.PCB_VIA) and (p.ToMM(t.GetWidth(p.F_Cu)) - p.ToMM(t.GetDrill())) / 2 < .25 - 1e-6]
check('Every PTH pad and via has an annular ring >= 0.25 mm (measured on the copper)', not ring, ring[:20])

# ---------------- 3. edge A: J_BP1..3 (contract docs/J_BP.csv) ----------------
jd = {}; ok = True
for k, r in enumerate(['J_BP1', 'J_BP2', 'J_BP3']):
    f = fmap.get(r)
    if not f:
        ok = False; jd[r] = 'missing'; continue
    pads1 = {a.GetNumber(): pos(a.GetPosition()) for a in f.Pads()}; fab = layer_bbox(f, p.F_Fab)
    xs = [v[0] for v in pads1.values()]; cx = (min(xs) + max(xs)) / 2; x0 = STEP * k
    nets = {int(n): net(pad(r, n)) for n in pads1}
    good = (abs(cx - (x0 + S1['krawedz_A']['srodek_x_w_slocie'])) < .05 and pads1['1'][0] == min(xs) and nets == JBP[r] and fab and abs(fab[1]) < .3
            and x0 + 10 - 1.5 <= fab[0] and fab[2] <= x0 + 43 + 1.5 and len(pads1) == 20 and 'IDC-Header_2x10' in f.GetFPIDAsString())
    jd[r] = {'centre_x': round(cx, 3), 'pin1': pads1['1'], 'fab_front_y': fab and round(fab[1], 3), 'fab_x': fab and (round(fab[0], 2), round(fab[2], 2)),
             'pinout_equals_J_BP.csv': nets == JBP[r], 'ok': good}
    ok &= good
check('J_BP1..3 (edge A): IDC 2x10 angled, body front at y = 0, pin centre x = 26.5 / 80 / 133.5, pin 1 at the smaller x, '
      'pinout = docs/J_BP.csv (P12 contract)', ok, jd)
# ---------------- 4. edge B: service headers (contract docs/SERWIS.csv) ----------------
svd = {}; sv_ok = True
texts = [(t.GetText(), t) for t in b.GetDrawings() if isinstance(t, p.PCB_TEXT) and t.GetLayer() == p.F_SilkS]
for k, hdr in enumerate(['J_SV1', 'J_SV2', 'J_SV3']):
    f = fmap.get(hdr); x0 = STEP * k; problems = []
    if not f:
        sv_ok = False; svd[hdr] = 'missing'; continue
    pd = sorted(((int(a.GetNumber()), a) for a in f.Pads()), key=lambda q: q[0]); fab = layer_bbox(f, p.F_Fab)
    xs = [p.ToMM(a.GetPosition().x) for _, a in pd]
    if len(pd) > S1['krawedz_B']['max_pinow_na_slot']: problems.append('too many pins')
    lo, hi = S1['krawedz_B']['zakres_x_w_slocie']
    if min(xs) - .85 < x0 + lo - 1e-6 or max(xs) + .85 > x0 + hi + 1e-6: problems.append(f'pins outside x {x0 + lo}..{x0 + hi}')
    if not fab or fab[3] - H < 5.0 or abs(fab[1] - SV_FAB_TOP) > 1.0 and fab[1] > H - 3.5: problems.append(f'body/pins not at edge B (fab {fab})')
    if net(pd[0][1]) != 'GND' or net(pd[-1][1]) != 'GND': problems.append('GND not on both ends')
    tab = SILK['LABEL'] if hdr == 'J_SV1' else SILK['ABBR']   # J_SV1 full names, J_SV2 / J_SV3 abbreviations (legend: sticker, 1.10)
    for n, a in (pd[0], pd[-1]):   # 1.10 (review): GND marked at both ends of every header
        if len([t for s_, t in texts if s_ == tab['GND'] and abs(p.ToMM(t.GetPosition().x) - p.ToMM(a.GetPosition().x)) < 1.3 and 86 < p.ToMM(t.GetPosition().y) < H]) != 1:
            problems.append(f'pin {n}: no single GND label')
    rows = []
    for n, a in pd[1:-1]:
        want_net, want_res = SERW[hdr][n]
        members = [(ff.GetReference(), q) for ff in b.GetFootprints() for q in ff.Pads() if q.GetNetname() == a.GetNetname() and ff.GetReference() != hdr]
        if len(members) != 1 or not members[0][0].startswith('R'):
            problems.append(f'pin {n}: not exactly one series resistor ({[m[0] for m in members]})'); continue
        r, q = members[0]; other = next(x for x in fmap[r].Pads() if x is not q and x.GetNumber() != q.GetNumber()); node = net(other)
        val = fmap[r].GetValue().split(' / ')[0].upper()
        want_val = '10K' if node in HIGHZ else '1K'
        others = [x for ff in b.GetFootprints() for x in ff.Pads() if x.GetNetname() == other.GetNetname() and ff.GetReference() != r]
        dist = min((math.dist(pos(other.GetPosition()), pos(x.GetPosition())) for x in others), default=99)
        if node != want_net or f'{r} {fmap[r].GetValue()}' != want_res: problems.append(f'pin {n}: {r} {val} on {node}, SERWIS.csv {want_net} {want_res}')
        if val != want_val: problems.append(f'pin {n}: {r} {val}, class S1 §6 wants {want_val}')
        if dist > 10: problems.append(f'pin {n}: {r} not at its node ({dist:.1f} mm)')
        lab = tab.get(node)
        tx = [t for s, t in texts if lab and s == lab and abs(p.ToMM(t.GetPosition().x) - p.ToMM(a.GetPosition().x)) < 1.3 and 86 < p.ToMM(t.GetPosition().y) < H]
        if len(tx) != 1: problems.append(f'pin {n}: {len(tx)} silk labels')
        rows.append({'pin': n, 'node': node, 'resistor': r, 'value': val, 'node_dist_mm': round(dist, 1), 'label': lab})
    svd[hdr] = {'problems': problems, 'pins': rows}; sv_ok &= not problems
check('Service headers J_SV1..3 (edge B, S1 section 6): <= 13 pins in x 10..43 of the slot, pins out ~6 mm, GND on both ends, one series '
      'resistor per pin as docs/SERWIS.csv and of its S1 class (1K, 10K for pull-up / open-drain nodes and SUP_N_OUT) <= 10 mm from its node, '
      'one silk label per pin with the name / abbreviation of its node (tables in silkscreen.py), GND at both ends',
      sv_ok, svd)
# ---------------- 4b. reserved strips of edge A (S1 §5) ----------------
pasy = {}
for k, zl in enumerate(['J_BP1', 'J_BP2', 'J_BP3']):
    x0 = STEP * k; y0, y1 = S1['krawedz_A']['strefa_y']; pas = (x0 + 10.0, y0, x0 + 43.0, y1)
    pasy[zl] = {'pas': pas, 'czesci': sorted(r for r in fmap if r not in holes_ref and r != zl
                                              and cbox(r)[0] < pas[2] and pas[0] < cbox(r)[2] and cbox(r)[1] < pas[3] and pas[1] < cbox(r)[3])}
check('Reserved strip of edge A (S1 §5: y 0-10, x 10-43 of each J_BP slot): no other part on either side (review 1.10)',
      not any(v['czesci'] for v in pasy.values()), pasy)
# ---------------- 5. heights ----------------
hh = {r: height(r, parts) for r in onboard}
check(f'Every part <= {HMAX} mm above the board (level 2, S1 section 4; src/heights.py)', all(v <= HMAX for v in hh.values()),
      {'max': max(hh.items(), key=lambda q: q[1]), 'over': {r: v for r, v in hh.items() if v > HMAX}})
# ---------------- 6. modules ----------------
m1 = fmap['M1']; j1r = [pxy('M1', f'J1-{i}') for i in range(1, 23)]; j3r = [pxy('M1', f'J3-{i}') for i in range(1, 23)]
usb = fp2board(m1, 11.43, 56.55); antend = fp2board(m1, 11.43, -8.05)
geo = {'row_distance_mm': round(math.dist(j1r[0], j3r[0]), 3), 'usb_face_y': round(usb[1], 2), 'usb_to_edge_B_mm': round(H - usb[1], 2),
       'antenna_end_y': round(antend[1], 2), 'pitch_ok': all(abs(math.dist(j1r[i], j1r[i + 1]) - 2.54) < 1e-3 and abs(math.dist(j3r[i], j3r[i + 1]) - 2.54) < 1e-3 for i in range(21))}
check(f'M1 Waveshare: two 1x22 rows 22.86 mm apart, USB-C end towards edge B (face <= {USB_MAX} mm inside it), antenna end towards edge A',
      abs(geo['row_distance_mm'] - 22.86) < 1e-3 and geo['pitch_ok'] and usb[1] > antend[1] and 0 <= H - usb[1] <= USB_MAX, geo)
keep = [z for z in b.Zones() if z.GetIsRuleArea()]


def full_keepout(z):
    return z.GetDoNotAllowTracks() and z.GetDoNotAllowVias() and z.GetDoNotAllowZoneFills() and set(z.GetLayerSet().Seq()) == {p.F_Cu, p.B_Cu}


def zone_rect(z):
    r = z.Outline().BBox(); return (p.ToMM(r.GetLeft()), p.ToMM(r.GetTop()), p.ToMM(r.GetRight()), p.ToMM(r.GetBottom()))


az = [z for z in keep if z.GetZoneName() == 'ANTENNA M1']
ant = [fp2board(m1, x, y) for x, y in [(-1.32, -8.0), (24.18, -1.5)]]
exp = (min(a[0] for a in ant) - 3, min(a[1] for a in ant) - 8, max(a[0] for a in ant) + 3, max(a[1] for a in ant))
ar = zone_rect(az[0]) if az else None
inside = sorted(r for r in fmap if r != 'M1' and not r.startswith('H') and ar and (lambda q: q[0] < ar[2] and ar[0] < q[2] and q[1] < ar[3] and ar[1] < q[3])(cbox(r)))
cu_in = rect_hits_copper(ar) if ar else ['no rule area']
check('ANTENNA keepout: M1 antenna end + 3 mm sides + 8 mm beyond, both layers, no track / via / pad / pour inside; no other part inside',
      len(az) == 1 and full_keepout(az[0]) and all(abs(u - v) < .01 for u, v in zip(ar, exp)) and not inside and not cu_in,
      {'rule_area': ar and [round(v, 2) for v in ar], 'expected': [round(v, 2) for v in exp], 'parts_inside': inside, 'copper_inside': cu_in})
sd = fmap['SD1']; card = [fp2board(sd, x, -22.86) for x in (0, 20.32)]
tip = min(H - q[1] for q in card); sdz = [z for z in keep if z.GetZoneName().startswith('SD1 M2.5')]
sdh = sorted(pos(a.GetPosition()) for a in sd.Pads() if a.GetAttribute() == p.PAD_ATTRIB_NPTH)
sdc = sorted(tuple(round(p.ToMM(v), 2) for v in (z.Outline().BBox().GetCenter().x, z.Outline().BBox().GetCenter().y)) for z in sdz)
sd_cu = [h for z in sdz for h in shape_hits_copper(z.Outline()) if not h.startswith('pad SD1.')]
check(f'SD1 Adafruit 4682: card towards edge B (tip <= {CARD_MAX} mm inside it), M2.5 keepouts r 3 mm around both holes, both layers, no copper',
      all(abs(q[1] - card[0][1]) < 1e-6 for q in card) and 0 <= tip <= CARD_MAX and len(sdz) == 2 and all(full_keepout(z) for z in sdz)
      and sdc == sorted(tuple(round(v, 2) for v in h) for h in sdh) and not sd_cu,
      {'card_tip_to_edge_B_mm': round(tip, 2), 'holes': sdh, 'keepout_centres': sdc, 'copper': sd_cu})
# ---------------- 7. 5 V path (ZASILANIE-RESET.md: <= 50 mOhm of copper in the main path) ----------------
RHO, T = 1.72e-8, S1['obrys']['miedz_um'] * 1e-6
b.BuildConnectivity(); con = b.GetConnectivity()


def path_res(netname, a_ref, a_pad, z_ref, z_pad, wmin=1.2):
    """Shortest locked-copper path (tracks >= wmin mm, vias) between two pads: Dijkstra over track ends; resistance in mOhm."""
    items = [t for t in b.GetTracks() if net(t) == netname and t.IsLocked() and (isinstance(t, p.PCB_VIA) or p.ToMM(t.GetWidth()) >= wmin)]
    nodes = {}; adj = {}

    def key(v):
        return (round(p.ToMM(v.x), 3), round(p.ToMM(v.y), 3))

    def link(u, v, r):
        adj.setdefault(u, []).append((v, r)); adj.setdefault(v, []).append((u, r))
    vias = [t for t in items if isinstance(t, p.PCB_VIA)]
    for t in items:
        if isinstance(t, p.PCB_VIA):
            link(('F',) + key(t.GetPosition()), ('B',) + key(t.GetPosition()), .001 / 2)   # ~1 mOhm per via, two in parallel on the spine
        else:   # 30.09: split the segment at every via lying on it (route_critical.py puts v1 inside the F.Cu stub, v2 on the B.Cu spine)
            L = 'F' if t.GetLayer() == p.F_Cu else 'B'; a0, a1 = key(t.GetStart()), key(t.GetEnd()); ln = math.dist(a0, a1)
            cuts = sorted({a0, a1} | {key(v.GetPosition()) for v in vias if ln and abs(math.dist(a0, key(v.GetPosition())) + math.dist(key(v.GetPosition()), a1) - ln) < 1e-3},
                          key=lambda q: math.dist(a0, q))
            for u, v in zip(cuts, cuts[1:]):
                link((L,) + u, (L,) + v, RHO * math.dist(u, v) * 1e-3 / (p.ToMM(t.GetWidth()) * 1e-3 * T))
    start = [n for n in adj if pad(a_ref, a_pad).HitTest(xy(n[1], n[2]))]; goal = {n for n in adj if pad(z_ref, z_pad).HitTest(xy(n[1], n[2]))}
    import heapq
    dist = {n: 0.0 for n in start}; hq = [(0.0, n) for n in start]; best = None
    while hq:
        d, n = heapq.heappop(hq)
        if d > dist.get(n, 1e9):
            continue
        if n in goal:
            best = d; break
        for m, r in adj.get(n, []):
            if d + r < dist.get(m, 1e9):
                dist[m] = d + r; heapq.heappush(hq, (d + r, m))
    return None if best is None else round(best * 1000, 1)


r_sys = path_res('5V_SYS', 'J_BP2', '19', 'Q1', '3'); r_m1 = path_res('5V_M1', 'Q1', '2', 'M1', 'J1-21')
widths = sorted({round(p.ToMM(t.GetWidth()), 2) for t in b.GetTracks() if not isinstance(t, p.PCB_VIA) and t.IsLocked() and net(t) in ('5V_SYS', '5V_M1')})
tot = None if r_sys is None or r_m1 is None else round(r_sys + r_m1, 1)
check('5 V path: continuous locked copper >= 1.2 mm J_BP2.19 -> Q1 D and Q1 S -> M1 J1-21; copper resistance <= 50 mOhm (20 C, 35 um)',
      tot is not None and tot <= 50, {'J_BP2.19->Q1.D_mOhm': r_sys, 'Q1.S->M1.J1-21_mOhm': r_m1, 'total_mOhm': tot,
                                      'total_60C_mOhm': tot and round(tot * (1 + .00393 * 40), 1), 'locked_widths_mm': widths})
# ---------------- 8. placement requirements (README R6, decoupling, drivers) ----------------
DEC = {'C1': ('U2', '16'), 'C2': ('U1', '9'), 'C3': ('U3', '6'), 'C5': ('U11', '14'), 'C6': ('U12', '14'), 'C7': ('U13', '14'), 'C8': ('U14', '14'),
       'C9': ('U21', '14'), 'C10': ('U22', '14'), 'C11': ('U23', '14'), 'C12': ('U4', '5'), 'C15': ('U6', '5'), 'C14': ('M1', 'J1-21')}
dd = {f'{c}.1-{u}.{n}': round(math.dist(pxy(c, '1'), pxy(u, n)), 2) for c, (u, n) in DEC.items()}
check('Decoupling at the pins: capacitor pad 1 <= 6 mm from its supply pin (C14 at M1 J1-21)', all(v <= 6 for v in dd.values()), dd)
DRV = {'R36': ('U21', '6'), 'R37': ('U21', '11'), 'R39': ('U21', '8'), 'R38': ('U23', '3'), 'R40': ('U23', '6'), 'R41': ('U6', '4'), 'R34': ('U4', '4')}
dv = {}
for r, (u, n) in DRV.items():
    q = next(a for a in fmap[r].Pads() if a.GetNetname() == pad(u, n).GetNetname()); dv[f'{r}-{u}.{n}'] = round(math.dist(pos(q.GetPosition()), pxy(u, n)), 2)
check('Series / termination resistors at their drivers: pad <= 6 mm from the driver pin (R36-R40 source termination, R41, R34)', all(v <= 6 for v in dv.values()), dv)


def centre(r):
    x0, y0, x1, y1 = cbox(r); return ((x0 + x1) / 2, (y0 + y1) / 2)


# U22 (30.09, disputed, README "Decyzje sporne" 2): in S1 by J_BP1 (CS_ILOG_N / CS_ITEST_N to J_BP1.2/4, inputs from U1/U2),
# not by J_BP2 as the README requirement said; MEAS_EN and ADC_RESET (static) take the longer way to J_BP2.
jc = {r: ((pxy(r, '1')[0] + pxy(r, '20')[0]) / 2, pxy(r, '1')[1]) for r in ('J_BP1', 'J_BP2', 'J_BP3')}
req = {'U21-J_BP2': round(math.dist(centre('U21'), jc['J_BP2']), 1), 'U22-J_BP1': round(math.dist(centre('U22'), jc['J_BP1']), 1),
       'U23-J_BP3': round(math.dist(centre('U23'), jc['J_BP3']), 1), 'U6.4-J_BP3.12': round(math.dist(pxy('U6', '4'), pxy('J_BP3', '12')), 1),
       'R41.2-J_BP3.12': round(math.dist(pxy('R41', '2'), pxy('J_BP3', '12')), 1), 'C15.1-U6.5': round(math.dist(pxy('C15', '1'), pxy('U6', '5')), 1),
       'R42.2-M1.J1-13': round(math.dist(pxy('R42', '2'), pxy('M1', 'J1-13')), 1), 'R43.1-J_BP2.16': round(math.dist(pxy('R43', '1'), pxy('J_BP2', '16')), 1)}
# 1.10 (review): the numbers are this check's reading of "blisko" / "przy" in README "Wymagania dla layoutu", not datasheet values:
# ribbon-end buffers within 30 mm of their connector centre (U23 25 mm, a smaller S3 cluster), U6 / R41 within 12 mm of J_BP3.12,
# R42 / R43 within 8 mm of their pin, C15 6 mm as every decoupling capacitor of P03 / P09 / P10.
lim = {'U21-J_BP2': 30, 'U22-J_BP1': 30, 'U23-J_BP3': 25, 'U6.4-J_BP3.12': 12, 'R41.2-J_BP3.12': 12, 'C15.1-U6.5': 6, 'R42.2-M1.J1-13': 8, 'R43.1-J_BP2.16': 8}
check('README layout requirements: U21 by J_BP2 (<= 30 mm), U22 by J_BP1 (<= 30 mm; decision 30.09, disputed: README asked J_BP2), '
      'U23 by J_BP3 (<= 25 mm), U6 / R41 / C15 at J_BP3.12, R42 at M1 J1-13, R43 at J_BP2.16',
      all(req[k] <= lim[k] for k in req), {'distance_mm': req, 'limit_mm': lim})
supo = round(sum(p.ToMM(t.GetLength()) for t in b.GetTracks() if not isinstance(t, p.PCB_VIA) and net(t) == 'SUP_N_OUT'), 1)
svb = round(sum(p.ToMM(t.GetLength()) for t in b.GetTracks() if not isinstance(t, p.PCB_VIA) and net(t) == 'SV_SUP_N_OUT'), 1)
r70 = next(r for r in fmap if r.startswith('R') and {net(a) for a in fmap[r].Pads()} == {'SUP_N_OUT', 'SV_SUP_N_OUT'})
check('SUP_N_OUT copper on P03 <= 30 mm and its service branch behind 10K (reset edge budget: local 3 pF of the 30 pF, README "Reset do P04"; '
      'review 1.10: the branch to J_SV3.6 is ~80 mm, bound for any branch length in verify_reset.py)',
      supo <= 30 and fmap[r70].GetValue().upper().startswith('10K'),
      {'track_mm': supo, 'service_branch_mm': svb, 'branch_resistor': f'{r70} {fmap[r70].GetValue()}'})
# ---------------- 9. GND ----------------
isl = {b.GetLayerName(L): sum(z.GetFilledPolysList(L).OutlineCount() for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND' and z.IsOnLayer(L)) for L in (p.F_Cu, p.B_Cu)}
cov = {b.GetLayerName(L): round(sum(z.GetFilledPolysList(L).Area() for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND' and z.IsOnLayer(L)) / 1e12 / (W * H) * 100, 1)
       for L in (p.F_Cu, p.B_Cu)}
check('GND pours on both layers: B.Cu >= 50 % of the board; island removal always (every island tied)', cov['B.Cu'] >= 50 and all(z.GetIslandRemovalMode() == p.ISLAND_REMOVAL_MODE_ALWAYS
      for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND') and len([z for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND']) == 2,
      {'cover_percent': cov, 'islands': isl})
# ---------------- 10. silkscreen ----------------
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
title = [s for s, t in texts if s == TYTUL]
marks = [s for s, t in texts if s.startswith('KRAWEDZ A') or s.startswith('KRAWEDZ B')]
check(f'Silkscreen: board name "{TYTUL}", edge markers A and B', bool(title) and any(m.startswith('KRAWEDZ A') for m in marks) and any(m.startswith('KRAWEDZ B') for m in marks), {'title': title, 'marks': marks})

# 1.10 (review): completion-planner routes - routed length against the straight line and the whole copper of the net (report only;
# README "PCB" lists them; the 30.09 board had 183-261 mm detours on _SRC nets that nobody checked)
cr = []
for rec in json.loads((P / 'routing/completion-routes.json').read_text(encoding='utf-8')):
    pts = rec['points_mm_layer']
    if rec['net'] == 'GND':
        continue
    cr.append({'net': rec['net'], 'from': rec['from'], 'to': rec['to'], 'routed_mm': round(sum(math.dist(u[:2], v[:2]) for u, v in zip(pts, pts[1:])), 1),
               'straight_mm': round(math.dist(pts[0][:2], pts[-1][:2]), 1), 'layer_changes': sum(u[2] != v[2] for u, v in zip(pts, pts[1:])),
               'net_copper_mm': round(sum(p.ToMM(t.GetLength()) for t in b.GetTracks() if not isinstance(t, p.PCB_VIA) and net(t) == rec['net']), 1)})
details['Completion-planner routes (report only, review 1.10)'] = cr
res = {'board': str(path), 'board_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'checks': checks, 'details': details,
       'passed': sum(c['pass'] for c in checks), 'total': len(checks)}
out.mkdir(parents=True, exist_ok=True)
(out / 'pcb-checks.json').write_text(json.dumps(res, indent=2, ensure_ascii=False, default=str) + '\n', encoding='utf-8')
for c in checks:
    print('PASS' if c['pass'] else 'FAIL', c['check'])
print(f"{res['passed']}/{res['total']} PCB checks passed")
sys.exit(0 if res['passed'] == res['total'] else 1)
