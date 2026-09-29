"""Independent checks of the finished P02 R4 PCB in format S1 (fresh native DRC + S1 and P02-specific rules).
usage: KiCad Python verify_pcb.py [alternative_board] [report_dir]
The alternative board is used by negative_controls.py (copies with one deliberate defect each).
Sources of the expected values: Plytki/Format-S1/format-s1.json and SPECYFIKACJA-FORMATU-S1.md (S1-1) and
Plytki/P02-R4-specyfikacja/ZADANIE-P02-R4-ETAP2.md (v2); nothing is read from placement.json or route_critical.py.
"""
from pathlib import Path
import pcbnew as p, json, sys, os, math, hashlib, collections, xml.etree.ElementTree as ET
from sexpr import parse, one, sub
from provenance import run_fresh_drc
P = Path(__file__).resolve().parents[1]
path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else P / 'eda/P02.kicad_pcb'
out = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else P / 'verification'
b = p.LoadBoard(str(path)); b.BuildConnectivity()
S1 = json.loads((P.parents[0] / 'Format-S1/format-s1.json').read_text(encoding='utf-8'))
root = ET.parse(P / 'verification/P02.xml').getroot(); parts = json.loads(Path(os.environ.get('P02_PARTS_JSON', P / 'docs/parts.json')).read_text(encoding='utf-8'))
checks = []; details = {}
KLASA, SLOTY = 'L', ['S1', 'S2', 'S3']                       # ZADANIE etap 2, section 2: class 2/3, slots S2-S3 of level 1
W, H = S1['klasy'][KLASA]['W'], S1['klasy'][KLASA]['H']; STEP = S1['rozstaw_slotow']
HMAX = S1['poziomy']['wys_max_gora_wysoki']               # level 1 is the high level (25 mm standoffs)
# S1 section 8, table 'Pinout P02 R4 J_BP' (typed from the specification, independent of parts.py)
JBP = {1: 'GND', 2: '5V_SYS', 3: 'GND', 4: '5V_SYS', 5: 'GND', 6: '5V_SYS', 7: 'GND', 8: '3V3_IO', 9: 'GND', 10: '3V3_IO', 11: 'GND', 12: 'PSU_OK',
       13: 'GND', 14: 'PFAIL_N', 15: 'P04_3V3', 16: 'SAFE_N', 17: 'PG_SEND', 18: 'PG_LINK', 19: 'GND', 20: 'VBAT_SENSE'}
PACK = {'P02_BAT_IN', 'P02_SW_COM', 'P02_VSW', 'VMOTOR', 'P02_HOLD_C', 'P02_VLOG'}           # S1 section 6: 4.7 kOhm
HIGHZ = {'P02_GATE', 'P02_OFF_G', 'P02_UV_DIV', 'P02_UV_CMP', 'P02_REF', 'VBAT_SENSE'}        # 10 kOhm; everything else 1 kOhm


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
    return next(a for a in fmap[ref].Pads() if a.GetNumber() == num)


def pxy(ref, num):
    return pos(pad(ref, num).GetPosition())


def layer_bbox(f, L):
    bb = None
    for g in f.GraphicalItems():
        if g.GetLayer() == L:
            r = g.GetBoundingBox(); c = (p.ToMM(r.GetLeft()), p.ToMM(r.GetTop()), p.ToMM(r.GetRight()), p.ToMM(r.GetBottom()))
            bb = c if bb is None else (min(bb[0], c[0]), min(bb[1], c[1]), max(bb[2], c[2]), max(bb[3], c[3]))
    return bb


def fills(netname, layers=(p.F_Cu, p.B_Cu)):
    """Filled copper of one net (zones) per layer, plus pads and tracks of the net, as SHAPE_POLY_SET per layer."""
    res = {}
    for L in layers:
        ps = p.SHAPE_POLY_SET()
        for z in b.Zones():
            if not z.GetIsRuleArea() and net(z) == netname and z.IsOnLayer(L):
                ps.BooleanAdd(z.GetFilledPolysList(L))
        for f in b.GetFootprints():
            for a in f.Pads():
                if net(a) == netname and a.IsOnLayer(L):
                    a.TransformShapeToPolygon(ps, L, 0, p.FromMM(.005), p.ERROR_INSIDE)
        for t in b.GetTracks():
            if net(t) == netname and (isinstance(t, p.PCB_VIA) or t.GetLayer() == L):
                t.TransformShapeToPolygon(ps, L, 0, p.FromMM(.005), p.ERROR_INSIDE)
        ps.Simplify(); res[L] = ps
    return res


# ---------------- 1. native DRC, fresh, bound to the inputs ----------------
drc, receipt = run_fresh_drc(path, out / 'drc.json')
# Klasa L (29.09): silkscreen.py drops footprint silk at file level (off the board, over other pads or over other silk) and lists
# every drop per part; KiCad then reports lib_footprint_mismatch for exactly those parts. Only these are accepted, by UUID.
trimmed = set(json.loads((P / 'routing/silkscreen.json').read_text(encoding='utf-8')).get('dropped_by_part', {}))
fp_uuid = {f.m_Uuid.AsString(): f.GetReference() for f in b.GetFootprints()}
lib_ok = [v for v in drc['violations'] if v['type'] == 'lib_footprint_mismatch' and all(fp_uuid.get(i['uuid']) in trimmed for i in v['items'])]
rest = [v for v in drc['violations'] if v not in lib_ok]
check('Fresh native DRC: 0 violations / 0 unconnected / 0 schematic parity (all severities; lib_footprint_mismatch only for parts '
      'whose silk silkscreen.py trimmed)',
      not rest and not drc['unconnected_items'] and not drc['schematic_parity'],
      dict(receipt['counts'], other_violations=len(rest), accepted_lib_mismatch=sorted(fp_uuid.get(i['uuid']) for v in lib_ok for i in v['items'])))
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
for f in b.GetFootprints():
    if not f.IsFlipped():
        continue
    r = f.GetReference(); smd = all(a.GetAttribute() == p.PAD_ATTRIB_SMD for a in f.Pads()); hgt = parts.get(r, {}).get('height_mm') or 99
    soic = 'SOIC' in f.GetFPIDAsString()
    tht = [a for g in b.GetFootprints() for a in g.Pads() if a.GetAttribute() == p.PAD_ATTRIB_PTH]
    rad = lambda a: max(p.ToMM(a.GetSize().x), p.ToMM(a.GetSize().y)) / 2
    gap = min((math.dist(pos(a.GetPosition()), pos(q.GetPosition())) - rad(a) - rad(q) for a in tht for q in f.Pads()), default=99)
    bottom[r] = {'smd': smd, 'height_mm': hgt, 'soic': soic, 'min_gap_to_THT_mm': round(gap, 2)}
check('S1-2 section 4: parts on the bottom only SMD <= 1.5 mm (SOIC allowed on level 1), >= 1 mm from THT pads (standoff zones: check below)',
      all(v['smd'] and (v['height_mm'] <= 1.5 or v['soic']) and v['min_gap_to_THT_mm'] >= 1.0 for v in bottom.values()), {'bottom_parts': bottom})
check('2 copper layers, 1.6 mm board (S1: FR4 1.6 mm)', b.GetCopperLayerCount() == S1['obrys']['warstwy'] and abs(p.ToMM(b.GetDesignSettings().GetBoardThickness()) - S1['obrys']['grubosc_pcb']) < 1e-6)
stack = one(one(parse(path.read_text(encoding='utf-8')), 'setup'), 'stackup')
cu = {x[1]: float(one(x, 'thickness')[1]) for x in sub(stack, 'layer') if x[1] in ['F.Cu', 'B.Cu']}
check('Both copper layers 35 um (S1)', cu == {'F.Cu': S1['obrys']['miedz_um'] / 1000, 'B.Cu': S1['obrys']['miedz_um'] / 1000}, cu)
edge = [g for g in b.GetDrawings() if g.GetLayer() == p.Edge_Cuts]
arcs = [g for g in edge if g.GetShape() == p.SHAPE_T_ARC]; segs = [g for g in edge if g.GetShape() == p.SHAPE_T_SEGMENT]
bb = b.GetBoardEdgesBoundingBox(); R = S1['obrys']['promien_naroza']
hw = max(p.ToMM(g.GetWidth()) for g in edge) / 2   # klasa L (29.09): the bounding box includes half the Edge.Cuts line width
check(f'Outline class {KLASA}: {W} x {H} mm, 4 corner arcs R {R} mm (format-s1.json)',
      len(segs) == 4 and len(arcs) == 4 and all(abs(p.ToMM(a.GetRadius()) - R) < 1e-4 for a in arcs)
      and abs(p.ToMM(bb.GetLeft()) + hw) < 1e-3 and abs(p.ToMM(bb.GetTop()) + hw) < 1e-3 and abs(p.ToMM(bb.GetRight()) - hw - W) < 1e-3
      and abs(p.ToMM(bb.GetBottom()) - hw - H) < 1e-3,
      {'bbox_line_centres': [p.ToMM(bb.GetLeft()) + hw, p.ToMM(bb.GetTop()) + hw, p.ToMM(bb.GetRight()) - hw, p.ToMM(bb.GetBottom()) - hw],
       'arcs': len(arcs), 'segments': len(segs)})
want_h = sorted((x + STEP * k, y) for k in range(len(SLOTY)) for x in S1['otwory_M3']['x_w_slocie'] for y in S1['otwory_M3']['y'])
got_h = sorted(pos(fmap[r].GetPosition()) for r in holes_ref)
hole_ok = all(list(fmap[r].Pads())[0].GetAttribute() == p.PAD_ATTRIB_NPTH and pos(list(fmap[r].Pads())[0].GetDrillSize()) == (S1['otwory_M3']['srednica'],) * 2 for r in holes_ref)
check('M3 holes: 8 NPTH 3.2 mm exactly at the S1 positions (x_w_slocie + 53.5 k, y 14 / 86)',
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
pro = json.loads((P / 'eda/P02.kicad_pro').read_text()); ds = pro['board']['design_settings']; rules = ds['rules']
cls = {c['name']: c for c in pro['net_settings']['classes']}
check('Rules as P02 R3 (clearance >= 0.25, track >= 0.30, edge 0.5) and annular ring >= 0.25 mm (S1); no DRC exclusions',
      rules['min_clearance'] >= .25 and rules['min_track_width'] >= .3 and rules['min_copper_edge_clearance'] >= .5 and rules['min_via_annular_width'] >= .25
      and not ds['drc_exclusions'] and all(c['clearance'] >= .25 for c in cls.values()))
ring = [f'{f.GetReference()}.{a.GetNumber()}' for f in b.GetFootprints() for a in f.Pads() if a.GetAttribute() == p.PAD_ATTRIB_PTH
        and (min(p.ToMM(a.GetSize().x), p.ToMM(a.GetSize().y)) - p.ToMM(a.GetDrillSize().x)) / 2 < .25 - 1e-6]
ring += [f'via {pos(t.GetPosition())}' for t in b.GetTracks() if isinstance(t, p.PCB_VIA) and (p.ToMM(t.GetWidth(p.F_Cu)) - p.ToMM(t.GetDrill())) / 2 < .25 - 1e-6]
check('Every PTH pad and via has an annular ring >= 0.25 mm (measured on the copper)', not ring, ring[:20])

# ---------------- 3. edge A: J_BP ----------------
jb = fmap.get('J_BP'); jd = {}
if jb:
    pads1 = {a.GetNumber(): pos(a.GetPosition()) for a in jb.Pads()}; fab = layer_bbox(jb, p.F_Fab); cy = layer_bbox(jb, p.F_CrtYd)
    xs = [v[0] for v in pads1.values()]; cx = (min(xs) + max(xs)) / 2
    s3 = S1['sloty'][2]; slot_x0 = STEP * 2                     # second slot of the board (level slot S3)
    nets_ok = {int(k): net(pad('J_BP', k)) for k in pads1} == JBP
    jd = {'centre_x': round(cx, 3), 'pin1': pads1['1'], 'pin20': pads1['20'], 'fab_front_y': fab[1] if fab else None, 'fab_x': fab and (fab[0], fab[2])}
    ok = (abs(cx - (slot_x0 + S1['krawedz_A']['srodek_x_w_slocie'])) < .05 and pads1['1'][0] == min(xs) and nets_ok and fab and abs(fab[1]) < .3
          and slot_x0 + 10 - 1.5 <= fab[0] and fab[2] <= slot_x0 + 43 + 1.5 and len(pads1) == 20)
else:
    ok = False
check('J_BP (edge A): IDC 2x10 angled, body front at y = 0, centre x = 133.5 (slot S3), pin 1 at smaller x, pinout = S1 section 8', ok, jd)
# ---------------- 4. edge B: service headers ----------------
svd = {}; sv_ok = True
texts = [(t.GetText(), t) for t in b.GetDrawings() if isinstance(t, p.PCB_TEXT) and t.GetLayer() == p.F_SilkS]
for k, hdr in [(0, 'J_SV1'), (2, 'J_SV2')]:   # klasa L: J_SV1 w S1, J_SV2 w S3
    f = fmap.get(hdr); x0 = STEP * k; problems = []
    if not f:
        sv_ok = False; svd[hdr] = 'missing'; continue
    pd = sorted(((int(a.GetNumber()), a) for a in f.Pads()), key=lambda q: q[0]); fab = layer_bbox(f, p.F_Fab)
    xs = [p.ToMM(a.GetPosition().x) for _, a in pd]
    if len(pd) > S1['krawedz_B']['max_pinow_na_slot']: problems.append('too many pins')
    lo, hi = S1['krawedz_B']['zakres_x_w_slocie']
    if min(xs) - .85 < x0 + lo - 1e-6 or max(xs) + .85 > x0 + hi + 1e-6: problems.append(f'pins outside x {x0 + lo}..{x0 + hi}')
    if not fab or abs(fab[1] - (H - 4.04 - 0.05)) > 1.0 or fab[3] - H < 5.0: problems.append(f'body/pins not at edge B (fab {fab})')
    if net(pd[0][1]) != 'GND' or net(pd[-1][1]) != 'GND': problems.append('GND not on both ends')
    rows = []
    for n, a in pd[1:-1]:
        members = [(ff.GetReference(), q) for ff in b.GetFootprints() for q in ff.Pads() if q.GetNetname() == a.GetNetname() and ff.GetReference() != hdr]
        if len(members) != 1 or not members[0][0].startswith('R'):
            problems.append(f'pin {n}: not exactly one series resistor ({[m[0] for m in members]})'); continue
        r, q = members[0]; other = next(x for x in fmap[r].Pads() if x is not q); node = net(other)
        want = 4700 if node in PACK else 10000 if node in HIGHZ else 1000
        val = fmap[r].GetValue().split(' / ')[0].upper(); mult = 1e3 if 'K' in val else 1; num = float(val.replace('K', '.').rstrip('.').replace('R', '.').rstrip('.')) * mult
        others = [x for ff in b.GetFootprints() for x in ff.Pads() if x.GetNetname() == other.GetNetname() and ff.GetReference() != r]
        dist = min((math.dist(pos(other.GetPosition()), pos(x.GetPosition())) for x in others), default=99)
        in_pour = any(z.GetNetname() == other.GetNetname() and not z.GetIsRuleArea() and z.IsOnLayer(p.F_Cu) and z.GetFilledPolysList(p.F_Cu).Contains(other.GetPosition())
                      for z in b.Zones())
        if node == 'GND' or abs(num - want) > 1: problems.append(f'pin {n}: {r} {val} on {node}, want {want}')
        if not (dist <= 10 or in_pour): problems.append(f'pin {n}: {r} not at its node ({dist:.1f} mm)')
        px = p.ToMM(a.GetPosition().x)
        lab = [t for s, t in texts if abs(p.ToMM(t.GetPosition().x) - px) < 1.3 and 86 < p.ToMM(t.GetPosition().y) < H]
        if len(lab) != 1: problems.append(f'pin {n}: {len(lab)} silk labels')
        rows.append({'pin': n, 'node': node, 'resistor': r, 'value': val, 'node_dist_mm': round(dist, 1), 'in_pour': in_pour, 'label': lab[0].GetText() if len(lab) == 1 else None})
    svd[hdr] = {'problems': problems, 'pins': rows}; sv_ok &= not problems
check('Service headers (edge B, S1 section 6): <= 13 pins in x 10..43 of the slot, pins out ~6 mm, GND on both ends, one series resistor '
      'of its class at the node (<= 10 mm or in its pour), one silk label per pin', sv_ok, svd)
# ---------------- 5. heights ----------------
hh = {r: parts[r]['height_mm'] for r in onboard}
check(f'Every part <= {HMAX} mm above the board (level 1, S1 section 4; heights in parts.py)', all(v is not None and v <= HMAX for v in hh.values()),
      {'max': max(hh.items(), key=lambda q: q[1] or 99), 'over': {r: v for r, v in hh.items() if v is None or v > HMAX}})
# ---------------- 6. 5 A path (IPC-2152, 35 um, <= 20 K: >= 4.0 mm) ----------------
PATHS = {  # net, waypoints (mm); sampled every 0.5 mm, chord +/-2 mm perpendicular must be copper of the net on F.Cu or B.Cu
    'BAT_IN J1.1-Q9.D': ('P02_BAT_IN', [(87.0, 24.0), (77.6, 24.0)]),
    'SW_COM Q9.S-Q1.S': ('P02_SW_COM', [(74.0, 27.9), (74.0, 33.1)]),
    'VSW Q1.D-F1.1': ('P02_VSW', [(71.5, 38.0), (69.8, 40.0), (69.8, 44.0), (65.3, 48.5), (65.3, 56.5), (69.5, 60.8), (73.4, 60.8)]),
    'VMOTOR F1.2-J2.1': ('VMOTOR', [(86.8, 62.7), (91.8, 66.5), (91.8, 74.0), (94.4, 76.0)]),
    'GND return J1.2-J2.2 (B.Cu)': ('GND', [(93.2, 31.62), (97.3, 31.8), (97.3, 39.5), (103.8, 42.5), (103.8, 63.0), (98.5, 68.38)]),
}
DX = 53.5   # klasa L (29.09): the power block moved with placement.py / route_critical.py; waypoints above are the 2/3 pilot ones
PATHS = {k: (n, [(x + DX, y) for x, y in wp]) for k, (n, wp) in PATHS.items()}
pw = {}
for name, (n, wp) in PATHS.items():
    fl = fills(n, (p.B_Cu,) if n == 'GND' else (p.F_Cu, p.B_Cu)); bad_pts = []; count = 0
    for (x1, y1), (x2, y2) in zip(wp, wp[1:]):
        L = math.dist((x1, y1), (x2, y2)); ux, uy = (x2 - x1) / L, (y2 - y1) / L
        for k in range(int(L / .5) + 1):
            mx, my = x1 + ux * .5 * k, y1 + uy * .5 * k; count += 1
            for o in [i * .25 - 2 for i in range(17)]:
                q = xy(mx - uy * o, my + ux * o)
                if not any(ps.Contains(q) for ps in fl.values()):
                    bad_pts.append((round(mx, 2), round(my, 2), o)); break
    pw[name] = {'samples': count, 'narrow': bad_pts[:10], 'narrow_count': len(bad_pts)}
check('5 A path J1 -> Q9 -> SW_COM -> Q1 -> VSW -> F1 -> J2 and the GND return: >= 4.0 mm of net copper across the path everywhere between the pads '
      '(IPC-2152, 35 um, 5 A, <= 20 K)', all(v['narrow_count'] == 0 for v in pw.values()), pw)
corr = [z for z in b.Zones() if z.GetIsRuleArea() and z.GetZoneName().startswith('B.Cu GND return')]; intr = []
if len(corr) == 1:
    o = corr[0].Outline()
    for t in b.GetTracks():
        if isinstance(t, p.PCB_VIA) and o.Contains(t.GetPosition()):
            intr.append(('via', net(t), pos(t.GetPosition())))
        elif not isinstance(t, p.PCB_VIA) and t.GetLayer() == p.B_Cu:
            a, c = t.GetStart(), t.GetEnd()
            if any(o.Contains(xy(p.ToMM(a.x) + (p.ToMM(c.x) - p.ToMM(a.x)) * k / 20, p.ToMM(a.y) + (p.ToMM(c.y) - p.ToMM(a.y)) * k / 20)) for k in range(21)):
                intr.append(('track', net(t), pos(a)))
check('GND return corridor on B.Cu: rule area contains J1.2 and J2.2, no track or via inside',
      len(corr) == 1 and corr[0].Outline().Contains(xy(*pxy('J1', '2'))) and corr[0].Outline().Contains(xy(*pxy('J2', '2'))) and not intr, intr)
isl = {b.GetLayerName(L): sum(z.GetFilledPolysList(L).OutlineCount() for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND' and z.IsOnLayer(L)) for L in (p.F_Cu, p.B_Cu)}
cov = {b.GetLayerName(L): round(sum(z.GetFilledPolysList(L).Area() for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND' and z.IsOnLayer(L)) / 1e12 / (W * H) * 100, 1)
       for L in (p.F_Cu, p.B_Cu)}
check('GND pours: B.Cu >= 50 % of the board; island removal always (every island tied)', cov['B.Cu'] >= 50 and all(z.GetIslandRemovalMode() == p.ISLAND_REMOVAL_MODE_ALWAYS
      for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND'), {'cover_percent': cov, 'islands': isl})
# ---------------- 7. TO-220 tabs only on copper of their own net ----------------
tabd = {}
for r in [x for x in fmap if parts.get(x, {}).get('footprint', '').endswith('TO220_3_P2.54_Drill1.4')]:
    f = fmap[r]; t = math.radians(f.GetOrientationDegrees()); ox, oy = pos(f.GetPosition())
    strip = p.SHAPE_POLY_SET(); strip.NewOutline()
    for lx, ly in [(-2.46, -3.15), (7.54, -3.15), (7.54, -1.85), (-2.46, -1.85)]:   # metal tab of a standing TO-220 (Vishay outline)
        strip.Append(p.FromMM(ox + lx * math.cos(t) + ly * math.sin(t)), p.FromMM(oy - lx * math.sin(t) + ly * math.cos(t)))
    own = net(pad(r, '2')); foreign = []
    for z in b.Zones():
        if not z.GetIsRuleArea() and z.IsOnLayer(p.F_Cu) and net(z) != own:
            x = p.SHAPE_POLY_SET(z.GetFilledPolysList(p.F_Cu)); x.BooleanIntersection(strip)
            if x.Area() > 0: foreign.append('zone ' + net(z))
    for tr in b.GetTracks():
        if net(tr) != own and (isinstance(tr, p.PCB_VIA) or tr.GetLayer() == p.F_Cu):
            ps = p.SHAPE_POLY_SET(); tr.TransformShapeToPolygon(ps, p.F_Cu, 0, p.FromMM(.005), p.ERROR_INSIDE); ps.BooleanIntersection(strip)
            if ps.Area() > 0: foreign.append(('via ' if isinstance(tr, p.PCB_VIA) else 'track ') + net(tr))
    for ff in b.GetFootprints():
        for a in ff.Pads():
            if net(a) != own and a.IsOnLayer(p.F_Cu):
                ps = p.SHAPE_POLY_SET(); a.TransformShapeToPolygon(ps, p.F_Cu, 0, p.FromMM(.005), p.ERROR_INSIDE); ps.BooleanIntersection(strip)
                if ps.Area() > 0: foreign.append(f'pad {ff.GetReference()}.{a.GetNumber()}')
    tabd[r] = {'tab_net': own, 'foreign': sorted(set(foreign))}
check('TO-220 (Q9, Q1, Q2, D1, D2): under each tab only copper of the tab net (pin 2) on F.Cu', len(tabd) == 5 and all(not v['foreign'] for v in tabd.values()), tabd)
# ---------------- 8. decoupling and local placement ----------------
DEC = [('C2', '1', 'Q1', '3'), ('C4', '1', 'Q1', '2'), ('C8', '1', 'U1', '3'), ('C10', '1', 'U1', '1'), ('C11', '1', 'U2', '8'), ('C13', '1', 'R12', '1'),
       ('C25', '1', 'U7', '2'), ('C26', '1', 'U8', '2'), ('C27', '1', 'U9', '14'), ('C28', '1', 'U9', '14'), ('C29', '1', 'U10', '14'),
       ('C21', '1', 'U5', '1'), ('C22', '1', 'U5', '3'), ('C23', '1', 'U6', '1'), ('C24', '1', 'U6', '3')]
dd = {f'{c}.{cn}-{u}.{un}': round(math.dist(pxy(c, cn), pxy(u, un)), 2) for c, cn, u, un in DEC}
check('Decoupling at the pins (task section 2): capacitor pad <= 8 mm from its pin', all(v <= 8 for v in dd.values()), dd)
hold = {'C12.1-D2.2': round(math.dist(pxy('C12', '1'), pxy('D2', '2')), 1), 'C12.1-D1.3': round(math.dist(pxy('C12', '1'), pxy('D1', '3')), 1),
        'D1.3-D2.2': round(math.dist(pxy('D1', '3'), pxy('D2', '2')), 1)}
check('C_H, D2 and D1 close together: HOLD_C pads within 20 mm of each other', all(v <= 20 for v in hold.values()), hold)
wall = {r: round(W - max(p.ToMM(a.GetPosition().x) for a in fmap[r].Pads()), 1) for r in ('J1', 'J2', 'J15')}
fab2 = layer_bbox(fmap['J2'], p.F_Fab)
check('J1 BAT, J2 VMOTOR, J15 VBAT_IN at the input wall x = 160 (pads/anchors <= 17 mm from it); J2 mating face at the edge',
      all(v <= 17 for v in wall.values()) and fab2 and abs(fab2[2] - W) < 1.0, {'pad_to_wall_mm': wall, 'J2_fab_right': fab2 and fab2[2]})

# ---------------- 9. silkscreen ----------------
cour = {}
side = {}
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
title = [s for s, t in texts if s.startswith('P02 R4 S1-L')]
marks = [s for s, t in texts if s.strip() in ('A', 'B') or s.startswith('KRAWEDZ A') or s.startswith('KRAWEDZ B')]
check('Silkscreen: board name "P02 R4 S1-L S1-S3", edge markers A and B', bool(title) and any('A' in m for m in marks) and any('B' in m for m in marks), {'title': title, 'marks': marks})

res = {'board': str(path), 'board_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'checks': checks, 'details': details,
       'passed': sum(c['pass'] for c in checks), 'total': len(checks)}
out.mkdir(parents=True, exist_ok=True)
(out / 'pcb-checks.json').write_text(json.dumps(res, indent=2, ensure_ascii=False, default=str) + '\n', encoding='utf-8')
for c in checks:
    print('PASS' if c['pass'] else 'FAIL', c['check'])
print(f"{res['passed']}/{res['total']} PCB checks passed")
sys.exit(0 if res['passed'] == res['total'] else 1)
