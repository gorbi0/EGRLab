"""Independent checks of the finished P07 S1 PCB in format S1 (fresh native DRC + S1 and P07-specific rules); structure and the generic
checks of P05 R3 / P10 R2 / P09 R2 / P03 R6 verify_pcb.py (1.10.2026), board values from board.py.
usage: KiCad Python verify_pcb.py [alternative_board] [report_dir]
The alternative board is used by negative_controls.py (copies with one deliberate defect each).
Sources of the expected values: Plytki/Format-S1/format-s1.json and SPECYFIKACJA-FORMATU-S1.md (S1-3), the P12 contract docs/J_BP.csv,
docs/SERWIS.csv, the README layout requirements and the user decisions of 5.10 (10 A path and PGND pours on both layers, Kelvin pair, nothing under
the shunt, J1-J4 at x = 0, GND / PGND separate, decoupling); nothing is read from placement.py or route_critical.py (P07 S1 from P06 R2).
"""
from pathlib import Path
import pcbnew as p, json, sys, os, math, hashlib, csv, heapq, collections, re, xml.etree.ElementTree as ET
from sexpr import parse, one, sub
from provenance import run_fresh_drc
sys.path.insert(0, str(Path(__file__).resolve().parent))
from heights import height
from board import NAME, REV, CLASS, SLOTS, SIGNAL_W, JBP as JBP_ZL, JSV as JSV_ZL, PIN_MARKS, PWR, PWR_W, PWR_CLR, CORE, FORCE, KELVIN, SUPPORT_KEEPOUT
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
HMAX = S1['poziomy']['wys_max_gora_standard']              # level 5, standoffs 20 mm (S1 section 7: P07 on level 5)
HMAX_BOTTOM = 1.5                                          # S1-2: SMD <= 1.5 mm on the bottom
JBP = collections.defaultdict(dict); SERW = collections.defaultdict(dict)
with open(P / 'docs/J_BP.csv', encoding='utf-8-sig') as fh:
    for r in csv.DictReader(fh, delimiter=';'):
        JBP[r['zlacze']][int(r['pin'])] = r['siec']
with open(P / 'docs/SERWIS.csv', encoding='utf-8-sig') as fh:
    for r in csv.DictReader(fh, delimiter=';'):
        SERW[r['zlacze']][int(r['pin'])] = (r['siec'], r['rezystor'])
# S1 section 6 resistor class (format-s1.json krawedz_B): 1K logic and rails to 5 V, 4K7 pack rails (to 16.8 V), 10K the analog nodes (verify_s1.py OHM)
HIGHZ = {'I_T_OUT'}; CLASS_VAL = {}


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


def layer_bbox(f, L):
    bb = None
    for g in f.GraphicalItems():
        if g.GetLayer() == L:
            r = g.GetBoundingBox(); c = (p.ToMM(r.GetLeft()), p.ToMM(r.GetTop()), p.ToMM(r.GetRight()), p.ToMM(r.GetBottom()))
            bb = c if bb is None else (min(bb[0], c[0]), min(bb[1], c[1]), max(bb[2], c[2]), max(bb[3], c[3]))
    return bb


def courtyard(r):
    f = fmap[r]; f.BuildCourtyardCaches(); return f.GetCourtyard(p.B_CrtYd if f.IsFlipped() else p.F_CrtYd)


def cbox(r):
    bb = courtyard(r).BBox()
    return (p.ToMM(bb.GetLeft()), p.ToMM(bb.GetTop()), p.ToMM(bb.GetRight()), p.ToMM(bb.GetBottom()))


def touches(item, poly, L=None):
    """Copper shape of a track / via touches the polygon (KiCad's intersectsCourtyard on the item shape)."""
    ps = p.SHAPE_POLY_SET(); item.TransformShapeToPolygon(ps, L if L is not None else item.GetLayer(), 0, p.FromMM(.005), p.ERROR_INSIDE)
    ps.BooleanIntersection(poly); return ps.OutlineCount() > 0 and ps.Area() > 0


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
        pin[node.get('ref'), node.get('pin')] = n.get('name').replace('/', '{slash}') if n.get('name').startswith('unconnected-(') else n.get('name')
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
check('S1-2 section 4: parts on the bottom only SMD <= 1.5 mm (heights.py, BOM thickness note for the capacitors), no SOIC, >= 1 mm from THT pads',
      all(v['smd'] and v['height_mm'] <= HMAX_BOTTOM and not v['soic'] and v['min_gap_to_THT_mm'] >= 1.0 for v in bottom.values()), {'bottom_parts': bottom})
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
    cy = courtyard(f.GetReference())
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
# rules: S1 section 3 (as P02 R3 / R4) everywhere; no fine-pitch exception on P06 (no custom rule file)
pro = json.loads((P / f'eda/{NAME}.kicad_pro').read_text()); ds = pro['board']['design_settings']; rules = ds['rules']
cls = {c['name']: c for c in pro['net_settings']['classes']}
pats = {(q['netclass'], q['pattern']) for q in pro['net_settings'].get('netclass_patterns') or []}
dru_file = path.parent / f'{NAME}.kicad_dru'
check(f'Rules as P02 R3 / R4 (clearance >= 0.25, PWR {PWR_CLR:.2f} / {PWR_W:.1f} mm for {", ".join(PWR)}, track >= {SIGNAL_W:.2f}, edge 0.5), annular ring >= 0.25 mm '
      '(S1 section 3); no custom rule file, no DRC exclusions',
      rules['min_clearance'] >= .25 - 1e-9 and rules['min_track_width'] >= SIGNAL_W - 1e-9 and rules['min_copper_edge_clearance'] >= .5
      and rules['min_via_annular_width'] >= .25 and cls['Default']['track_width'] >= SIGNAL_W - 1e-9 and not ds['drc_exclusions']
      and all(c['clearance'] >= .25 for c in cls.values()) and cls['PWR']['clearance'] >= PWR_CLR - 1e-9 and cls['PWR']['track_width'] >= PWR_W - 1e-9
      and {('PWR', n) for n in PWR} <= pats and not dru_file.exists(),
      {'board_minimums': {k: rules[k] for k in ('min_clearance', 'min_track_width', 'min_copper_edge_clearance', 'min_via_annular_width')},
       'classes': {k: (v['track_width'], v['clearance']) for k, v in cls.items()}, 'patterns': sorted(pats), 'dru_file': dru_file.exists()})
narrow = [{'net': net(t), 'width': round(p.ToMM(t.GetWidth()), 3), 'start': pos(t.GetStart())} for t in b.GetTracks()
          if not isinstance(t, p.PCB_VIA) and p.ToMM(t.GetWidth()) < SIGNAL_W - 1e-6]
pwr_thin = [{'net': net(t), 'width': round(p.ToMM(t.GetWidth()), 3), 'start': pos(t.GetStart())} for t in b.GetTracks()
            if not isinstance(t, p.PCB_VIA) and net(t) in PWR and p.ToMM(t.GetWidth()) < PWR_W - 1e-6]
check(f'Every track >= {SIGNAL_W:.2f} mm (S1 section 3) and every track of {", ".join(PWR)} >= {PWR_W:.1f} mm (class PWR)', not narrow and not pwr_thin,
      {'narrow': narrow[:20], 'pwr_thin': pwr_thin[:20]})
ring = [f'{f.GetReference()}.{a.GetNumber()}' for f in b.GetFootprints() for a in f.Pads() if a.GetAttribute() == p.PAD_ATTRIB_PTH
        and (min(p.ToMM(a.GetSize().x), p.ToMM(a.GetSize().y)) - p.ToMM(a.GetDrillSize().x)) / 2 < .25 - 1e-6]
ring += [f'via {pos(t.GetPosition())}' for t in b.GetTracks() if isinstance(t, p.PCB_VIA) and (p.ToMM(t.GetWidth(p.F_Cu)) - p.ToMM(t.GetDrill())) / 2 < .25 - 1e-6]
check('Every PTH pad and via has an annular ring >= 0.25 mm (measured on the copper)', not ring, ring[:20])
# ---------------- 3. edge A: J_BP (contract docs/J_BP.csv) ----------------
jd = {}; ok = True
for r in JBP_ZL:
    f = fmap.get(r)
    if not f:
        ok = False; jd[r] = 'missing'; continue
    pads1 = {a.GetNumber(): pos(a.GetPosition()) for a in f.Pads()}; fab = layer_bbox(f, p.F_Fab)
    xs = [v[0] for v in pads1.values()]; cx = (min(xs) + max(xs)) / 2; k = int(cx // STEP)
    nets = {int(n): net(pad(r, n)) for n in pads1}
    good = (k < len(SLOTY) and abs(cx - (STEP * k + S1['krawedz_A']['srodek_x_w_slocie'])) < .05 and pads1['1'][0] == min(xs) and nets == JBP[r]
            and fab and abs(fab[1]) < .3 and len(pads1) == 16 and 'IDC-Header_2x08' in f.GetFPIDAsString())
    jd[r] = {'centre_x': round(cx, 3), 'slot': SLOTY[k], 'pin1': pads1['1'], 'fab_front_y': fab and round(fab[1], 3), 'pinout_equals_J_BP.csv': nets == JBP[r], 'ok': good}
    ok &= good
check('J_BP (edge A): J_BP1 / J_BP2 IDC 2x8 angled in slots S2 / S3, body front at y = 0, pin centres x = 26.5 / 80.0, pin 1 at the smaller x, pinout = docs/J_BP.csv (P12 contract)', ok, jd)
# ---------------- 4. edge B: service headers (contract docs/SERWIS.csv) ----------------
LABEL = next(_ast.literal_eval(n.value) for n in _ast.parse((P / 'src/silkscreen.py').read_text(encoding='utf-8')).body
             if isinstance(n, _ast.Assign) and any(getattr(t, 'id', '') == 'LABEL' for t in n.targets))   # tables independent of the result
texts = [(t.GetText(), t) for t in b.GetDrawings() if isinstance(t, p.PCB_TEXT) and t.GetLayer() == p.F_SilkS]
svd = {}; sv_ok = True
for k, hdr in enumerate(JSV_ZL):
    f = fmap.get(hdr); problems = []
    x0 = STEP * int(min(p.ToMM(a.GetPosition().x) for a in f.Pads()) // STEP) if f else 0   # slot of the strip (P07: one strip, slot S3)
    if not f:
        sv_ok = False; svd[hdr] = 'missing'; continue
    pd = sorted(((int(a.GetNumber()), a) for a in f.Pads()), key=lambda q: q[0]); fab = layer_bbox(f, p.F_Fab)
    xs = [p.ToMM(a.GetPosition().x) for _, a in pd]; lo, hi = S1['krawedz_B']['zakres_x_w_slocie']
    if len(pd) > S1['krawedz_B']['max_pinow_na_slot']: problems.append('too many pins')
    if min(xs) - .85 < x0 + lo - 1e-6 or max(xs) + .85 > x0 + hi + 1e-6: problems.append(f'pins outside x {x0 + lo}..{x0 + hi}')
    if not fab or fab[3] - H < 5.0: problems.append(f'pins not ~6 mm beyond edge B (fab {fab})')
    if net(pd[0][1]) != 'GND' or net(pd[-1][1]) != 'GND': problems.append('GND not on both ends')
    if pd[0][1].GetPosition().x <= pd[-1][1].GetPosition().x: problems.append('pin 1 not at the larger x (read from edge B, S1 section 6)')
    for n, a in (pd[0], pd[-1]):
        if len([t for s_, t in texts if s_ == LABEL['GND'] and abs(p.ToMM(t.GetPosition().x) - p.ToMM(a.GetPosition().x)) < 1.3 and 80 < p.ToMM(t.GetPosition().y) < H]) != 1:
            problems.append(f'pin {n}: no single GND label')
    rows = []
    for n, a in pd[1:-1]:
        want_net, want_res = SERW[hdr][n]
        if want_net == 'GND':
            if net(a) != 'GND': problems.append(f'pin {n}: SERWIS.csv GND, board {net(a)}')
            continue
        members = [(ff.GetReference(), q) for ff in b.GetFootprints() for q in ff.Pads() if q.GetNetname() == a.GetNetname() and ff.GetReference() != hdr]
        if len(members) != 1 or not members[0][0].startswith('R'):
            problems.append(f'pin {n}: not exactly one series resistor ({[m[0] for m in members]})'); continue
        r, q = members[0]; other = next(x for x in fmap[r].Pads() if x.GetNumber() != q.GetNumber()); node = net(other)
        val = fmap[r].GetValue().upper(); want_val = CLASS_VAL.get(node, '10K' if node in HIGHZ else '1K')
        others = [x for ff in b.GetFootprints() for x in ff.Pads() if x.GetNetname() == other.GetNetname() and ff.GetReference() != r]
        dist = min((math.dist(pos(other.GetPosition()), pos(x.GetPosition())) for x in others), default=99)
        if node != want_net or not want_res.startswith(f'{r} {fmap[r].GetValue()} '): problems.append(f'pin {n}: {r} {val} on {node}, SERWIS.csv {want_net} {want_res}')
        if val != want_val: problems.append(f'pin {n}: {r} {val}, class S1 §6 wants {want_val}')
        if dist > 10: problems.append(f'pin {n}: {r} not at its node ({dist:.1f} mm)')
        lab = LABEL.get(node)
        tx = [t for s, t in texts if lab and s == lab and abs(p.ToMM(t.GetPosition().x) - p.ToMM(a.GetPosition().x)) < 1.3 and 80 < p.ToMM(t.GetPosition().y) < H]
        if len(tx) != 1: problems.append(f'pin {n}: {len(tx)} silk labels')
        rows.append({'pin': n, 'node': node, 'resistor': r, 'value': val, 'node_dist_mm': round(dist, 1), 'label': lab, 'side': 'B' if fmap[r].IsFlipped() else 'F'})
    svd[hdr] = {'problems': problems, 'pins': rows}; sv_ok &= not problems
check('Service header J_SV2 (edge B, S1 section 6; one strip, simplification 6.10): <= 13 pins in x 10..43 of the slot, pin 1 at the larger x, pins out ~6 mm, GND on both '
      'ends, one series resistor per pin as docs/SERWIS.csv and of its S1 class (1K rails / logic, 10K analog node) '
      '<= 10 mm from its node, one silk label per pin with the name of its node (LABEL in silkscreen.py), GND at both ends', sv_ok, svd)
# ---------------- 4b. reserved strip of edge A (S1 §5, README: only along J_BP) ----------------
pasy = {}
for zl in JBP_ZL:
    xs_ = [p.ToMM(a.GetPosition().x) for a in fmap[zl].Pads() if a.GetNumber()]; x0 = STEP * int(((min(xs_) + max(xs_)) / 2) // STEP)
    y0, y1 = S1['krawedz_A']['strefa_y']; pas = (x0 + 10.0, y0, x0 + 43.0, y1); T_ = .1
    pasy[zl] = {'pas': pas, 'czesci': sorted(r for r in fmap if r not in holes_ref and r != zl
                                             and cbox(r)[0] < pas[2] - T_ and pas[0] + T_ < cbox(r)[2] and cbox(r)[1] < pas[3] - T_ and pas[1] + T_ < cbox(r)[3])}
check('Reserved strip of edge A (S1 §5: y 0-10 along J_BP1 / J_BP2, x 10-43 / 63.5-96.5): no other part on either side', not any(v['czesci'] for v in pasy.values()), pasy)
# ---------------- 5. heights ----------------
hh = {r: height(r, parts) for r in onboard}
check(f'Every part <= {HMAX} mm above the board (level 5, S1 section 4; src/heights.py; K1 15.7 mm)', all(v <= HMAX for v in hh.values()),
      {'max': max(hh.items(), key=lambda q: q[1]), 'over': {r: v for r, v in hh.items() if v > HMAX}})


# ---------------- 6. force path, shunt and Kelvin pair (README layout requirements) ----------------
def path_mm(netname, a, c):
    """Shortest copper path pad centre -> pad centre over the net's tracks and vias (P05 R3): graph nodes are track ends, points where a
    track end lies on another track, vias (both layers) and the two pads (joined to every node inside them)."""
    items = [t for t in b.GetTracks() if net(t) == netname]
    g = collections.defaultdict(list); segs = []
    for t in items:
        if isinstance(t, p.PCB_VIA):
            q = pos(t.GetPosition()); g[('F', q)].append((('B', q), 0)); g[('B', q)].append((('F', q), 0))
        else:
            L = 'F' if t.GetLayer() == p.F_Cu else 'B'; s, e = pos(t.GetStart()), pos(t.GetEnd()); d = math.dist(s, e)
            g[(L, s)].append(((L, e), d)); g[(L, e)].append(((L, s), d)); segs.append((L, s, e, t))
    for L, s, e, t in segs:
        for n in list(g):
            if n[0] == L and n[1] not in (s, e) and t.HitTest(xy(*n[1])):
                for q in (s, e):
                    d = math.dist(n[1], q); g[n].append(((L, q), d)); g[(L, q)].append((n, d))
    for r, num in (a, c):
        pd_ = pad(r, num); key = ('PAD', r, num); cp = pos(pd_.GetPosition())
        for n in list(g):
            if n[0] in ('F', 'B') and pd_.IsOnLayer(p.F_Cu if n[0] == 'F' else p.B_Cu) and pd_.HitTest(xy(*n[1])):
                d = math.dist(cp, n[1]); g[key].append((n, d)); g[n].append((key, d))
    start, goal = ('PAD',) + a, ('PAD',) + c; todo = [(0, start)]; seen = set()
    while todo:
        dd, q = heapq.heappop(todo)
        if q == goal:
            return round(dd, 3)
        if q in seen:
            continue
        seen.add(q)
        for v, w in g[q]:
            heapq.heappush(todo, (dd + w, v))
    return None


# P07 S1: the 10 A path J1 -> K1 -> J2 (B+), J3 (M+) -> RSH1 -> J4 and the PGND return, pours on both layers (README layout requirements)
TAIL_PADS = {('J1', '1'), ('J1', '2'), ('J2', '1'), ('J2', '2'), ('J3', '1'), ('J3', '2'), ('J4', '1'), ('J4', '2')}
FORCE_PADS = {'VMOTOR': [('J1', '1'), ('K1', '11'), ('D1', '1'), ('C1', '1'), ('R4', '1')], 'MOD_BP': [('J2', '1'), ('K1', '14'), ('R4', '2')],
              'PGND': [('J1', '2'), ('J2', '2'), ('D1', '2'), ('C1', '2')], 'MOD_MP': [('J3', '1'), ('RSH1', '1')],
              'T_EGR_P1': [('J4', '1'), ('RSH1', '4')], 'T_EGR_P3': [('J3', '2'), ('J4', '2')]}
pours = {(n, L): [z for z in b.Zones() if not z.GetIsRuleArea() and net(z) == n and z.IsOnLayer(L)] for n in FORCE for L in (p.F_Cu, p.B_Cu)}
gndprio = max((z.GetAssignedPriority() for z in b.Zones() if not z.GetIsRuleArea() and net(z) == 'GND'), default=0)
pinfo = {}; pok = True
for n in FORCE:
    for L in (p.F_Cu, p.B_Cu):
        zs = pours[(n, L)]; ln = b.GetLayerName(L)
        good = len(zs) == 1 and zs[0].GetAssignedPriority() > gndprio and zs[0].GetPadConnection() == p.ZONE_CONNECTION_FULL
        fl = zs[0].GetFilledPolysList(L) if zs else p.SHAPE_POLY_SET()
        cov, conn = {}, {}
        for r, q in FORCE_PADS[n]:
            for a_ in [x for x in fmap[r].Pads() if x.GetNumber() == q]:
                if not a_.IsOnLayer(L):
                    continue
                key = f'{r}.{q}@{pos(a_.GetPosition())}'
                if (r, q) not in TAIL_PADS:   # relay pins, shunt, TVS, bulk, R4: solid, inside the fill
                    cov[key] = bool(fl.Contains(a_.GetPosition())); conn[key] = a_.GetLocalZoneConnection() in (p.ZONE_CONNECTION_FULL, p.ZONE_CONNECTION_INHERITED)
                else:             # wire pads on >= 4 spokes >= 2 mm (pieces of the fill in a ring round the pad; P06 R2 review F5)
                    rp = max(p.ToMM(a_.GetSize(L).x), p.ToMM(a_.GetSize(L).y)) / 2; ring = p.SHAPE_POLY_SET(); ring.NewOutline()
                    c_ = a_.GetPosition()
                    for k in range(64):
                        ring.Append(c_.x + p.FromMM((rp + .35) * math.cos(k * math.tau / 64)), c_.y + p.FromMM((rp + .35) * math.sin(k * math.tau / 64)))
                    inner = p.SHAPE_POLY_SET(); inner.NewOutline()
                    for k in range(64):
                        inner.Append(c_.x + p.FromMM((rp + .15) * math.cos(k * math.tau / 64)), c_.y + p.FromMM((rp + .15) * math.sin(k * math.tau / 64)))
                    ring.BooleanSubtract(inner); x_ = p.SHAPE_POLY_SET(fl); x_.BooleanIntersection(ring)
                    widths = sorted(round(x_.Outline(i).Area() / 1e12 / .2, 2) for i in range(x_.OutlineCount()))
                    cov[key] = x_.OutlineCount() >= 4 and all(w >= 1.8 for w in widths[-4:])
                    conn[key] = a_.GetLocalZoneConnection() == p.ZONE_CONNECTION_THERMAL and p.ToMM(zs[0].GetThermalReliefSpokeWidth()) >= 2.0 if zs else False
        pinfo[f'{n} {ln}'] = {'zones': len(zs), 'area_mm2': round(fl.Area() / 1e12, 1), 'pads_joined': cov, 'connection_ok': conn}
        pok &= good and all(cov.values()) and all(conn.values()) and fl.OutlineCount() >= 1
check('Force pours VMOTOR / MOD_BP / PGND / MOD_MP / T_EGR_P1 / T_EGR_P3: one zone per net on F.Cu and on B.Cu, priority above GND; relay contact '
      'pins (both of each pair), RSH1 force pads, D1 / C1 / R4 solid inside the fill; J1-J4 wire pads on >= 4 spokes >= 2 mm on every layer', pok, pinfo)


def shrunk_near(n, L, at, r_mm=2.0):
    """Pieces of the fill of n on L shrunk by r_mm (a corridor >= 2 r_mm survives) within 7.5 mm of `at` (pads on spokes / small pads)."""
    zs_ = pours[(n, L)]; fl = p.SHAPE_POLY_SET(zs_[0].GetFilledPolysList(L)) if zs_ else p.SHAPE_POLY_SET()
    fl.Deflate(p.FromMM(r_mm), p.CORNER_STRATEGY_ROUND_ALL_CORNERS, p.FromMM(.02)); out_ = []
    for k in range(fl.OutlineCount()):
        pc = p.SHAPE_POLY_SET(); pc.AddOutline(fl.Outline(k))
        d_ = 0.0 if pc.Contains(xy(*at)) else math.sqrt(pc.SquaredDistance(xy(*at))) / 1e6
        out_.append((k, round(d_, 2)))
    return out_


wid = {}; wok = True
PATHS = {'VMOTOR': (('J1', '1'), ('K1', '11')), 'MOD_BP': (('J2', '1'), ('K1', '14')), 'PGND': (('J2', '2'), ('J1', '2')),
         'MOD_MP': (('J3', '1'), ('RSH1', '1')), 'T_EGR_P1': (('J4', '1'), ('RSH1', '4')), 'T_EGR_P3': (('J3', '2'), ('J4', '2'))}
for n, (a, c) in PATHS.items():
    for L in (p.F_Cu, p.B_Cu):
        pa, pc_ = shrunk_near(n, L, pxy(*a)), shrunk_near(n, L, pxy(*c))
        da = {k: d for k, d in pa if d <= 7.5}; dc = {k: d for k, d in pc_ if d <= 3.5}   # the far end: corridor within 3.5 mm of the pin / force pad centre
        joined = bool(set(da) & set(dc))
        wid[f'{n} {b.GetLayerName(L)} {a[0]}.{a[1]}-{c[0]}.{c[1]}'] = {'joined_4mm': joined, 'end_gap_mm': min(dc.values()) if dc else None}; wok &= joined
check('Force path >= 4 mm wide on both layers (fill shrunk by 2 mm stays one piece): J1.1-K1 COM (VMOTOR), J2.1-K1 NO (MOD_BP), J2.2-J1.2 (PGND), '
      'J3.1-RSH1.1 (MOD_MP), J4.1-RSH1.4 (T_EGR_P1), J3.2-J4.2 (T_EGR_P3); the 4 mm corridor reaches <= 3.5 mm from the relay pin / shunt force pad '
      'centre (the shunt pad itself is 2.03 mm wide)', wok, wid)
fvias = {n: [t for t in b.GetTracks() if isinstance(t, p.PCB_VIA) and net(t) == n] for n in FORCE}
in_pad = [pos(v.GetPosition()) for n in FORCE for v in fvias[n] for q in ('1', '2', '3', '4')
          if math.dist(pos(v.GetPosition()), pxy('RSH1', q)) < 3.0 and pad('RSH1', q).HitTest(v.GetPosition(), p.FromMM(.45 + .3))]
check('Force pours stitched: >= 8 vias per net (plus the PTH pads); no via in or within 0.3 mm of an RSH1 pad',
      all(len(v) >= 8 for v in fvias.values()) and not in_pad, {'vias': {n: len(v) for n, v in fvias.items()}, 'vias_at_RSH1_pads': in_pad})
shc = courtyard('RSH1'); sh_nets = {net(a) for a in fmap['RSH1'].Pads()}
under = sorted({f'{net(t)} {"via" if isinstance(t, p.PCB_VIA) else b.GetLayerName(t.GetLayer())}' for t in b.GetTracks()
                if (isinstance(t, p.PCB_VIA) and touches(t, shc, p.B_Cu)) or (not isinstance(t, p.PCB_VIA) and t.GetLayer() == p.B_Cu and touches(t, shc))})
zfill = []
for z in b.Zones():
    if z.GetIsRuleArea() or not z.IsOnLayer(p.B_Cu):
        continue
    x = p.SHAPE_POLY_SET(z.GetFilledPolysList(p.B_Cu)); x.BooleanIntersection(shc)
    if x.OutlineCount() and x.Area() > 0:
        zfill.append(f'{net(z)} B.Cu {round(x.Area() / 1e12, 2)} mm2')
top_foreign = sorted({net(t) for t in b.GetTracks() if net(t) not in sh_nets and not isinstance(t, p.PCB_VIA) and t.GetLayer() == p.F_Cu and touches(t, shc)})
for z in b.Zones():
    if not z.GetIsRuleArea() and z.IsOnLayer(p.F_Cu) and net(z) not in sh_nets:
        x = p.SHAPE_POLY_SET(z.GetFilledPolysList(p.F_Cu)); x.BooleanIntersection(shc)
        if x.OutlineCount() and x.Area() > 0:
            top_foreign.append(f'zone {net(z)}')
check('Nothing under the shunt: no copper of any net on B.Cu in the RSH1 courtyard (tracks, vias, pours) and on F.Cu only the RSH1 nets '
      '(MOD_MP, T_EGR_P1, K_PLUS, K_MINUS)', not under and not zfill and not top_foreign, {'b_cu_items': under, 'b_cu_fill': zfill, 'f_cu_foreign': top_foreign})
KPATH = {'K_PLUS': (('RSH1', '2'), ('R6', '1'), 12.0), 'K_MINUS': (('RSH1', '3'), ('R7', '1'), 8.0),
         'INA_PLUS': (('R6', '2'), ('U1', '8'), 6.0), 'INA_MINUS': (('R7', '2'), ('U1', '1'), 6.0)}
kd = {}; kok = True
for n, (a, c, lim) in KPATH.items():
    its = [t for t in b.GetTracks() if net(t) == n]
    vias = [t for t in its if isinstance(t, p.PCB_VIA)]; bcu = [t for t in its if not isinstance(t, p.PCB_VIA) and t.GetLayer() != p.F_Cu]
    d = path_mm(n, a, c); kd[n] = {'path_mm': d, 'limit_mm': lim, 'vias': len(vias), 'b_cu_tracks': len(bcu)}
    kok &= d is not None and d <= lim and not vias and not bcu
zn = [z for z in b.Zones() if not z.GetIsRuleArea() and net(z) in KPATH]
kd['zones_on_kelvin_nets'] = len(zn)


def polyline(*nets_):
    return [(pos(t.GetStart()), pos(t.GetEnd())) for t in b.GetTracks() if net(t) in nets_ and not isinstance(t, p.PCB_VIA)]


def seg_dist(q, s):
    (x1, y1), (x2, y2) = s; dx, dy = x2 - x1, y2 - y1; L2 = dx * dx + dy * dy
    u = 0 if L2 == 0 else max(0, min(1, ((q[0] - x1) * dx + (q[1] - y1) * dy) / L2)); return math.dist(q, (x1 + u * dx, y1 + u * dy))


plus, minus = polyline('K_PLUS', 'INA_PLUS'), polyline('K_MINUS', 'INA_MINUS')
samples = [(s[0][0] + (s[1][0] - s[0][0]) * k / 10, s[0][1] + (s[1][1] - s[0][1]) * k / 10) for s in minus for k in range(11)]
spread = max((min(seg_dist(q, s) for s in plus) for q in samples), default=99)
kd['max_spacing_mm'] = round(spread, 2)
check('Kelvin pair from the sense pads (README): K_PLUS RSH1.2 -> R6 <= 12 mm, K_MINUS RSH1.3 -> R7 <= 8 mm, R6 / R7 -> U1.8 / U1.1 <= 6 mm, '
      'F.Cu only, no via, no pour on these nets; the two lines run as a pair (every point of K_MINUS / INA_MINUS <= 5 mm from K_PLUS / INA_PLUS)',
      kok and not zn and spread <= 5.0, kd)
xs_k = [q for s in plus + minus for q in s]; kx0, kx1 = min(x for x, _ in xs_k), max(x for x, _ in xs_k)
between = p.SHAPE_POLY_SET(); between.NewOutline()
for x, y in [(kx0, min(y for _, y in xs_k)), (kx1, min(y for _, y in xs_k)), (kx1, max(y for _, y in xs_k)), (kx0, max(y for _, y in xs_k))]:
    between.Append(*[p.FromMM(v) for v in (x, y)])
foreign_k = sorted({f'{net(t)} {"via" if isinstance(t, p.PCB_VIA) else b.GetLayerName(t.GetLayer())}' for t in b.GetTracks()
                    if net(t) not in set(KPATH) | sh_nets and (touches(t, between, p.F_Cu) if isinstance(t, p.PCB_VIA) or t.GetLayer() == p.F_Cu else touches(t, between))})
check('No track or via of another net in the box spanned by the Kelvin pair (shunt to U1, both layers; pours allowed)', not foreign_k,
      {'box_mm': [round(kx0, 2), round(min(y for _, y in xs_k), 2), round(kx1, 2), round(max(y for _, y in xs_k), 2)], 'foreign': foreign_k})
loop = {f'{j}.{k}-RSH1.{s}': round(math.dist(pxy(j, k), pxy('RSH1', s)), 2) for j, k, s in (('J3', '1', '1'), ('J4', '1', '4'))}
u1_rsh = round(math.dist(pxy('U1', '8'), pxy('RSH1', '2')), 2)
check('Measuring loop short: J3.1 -> RSH1.1 and RSH1.4 -> J4.1 pad centres <= 14 mm apart; U1 (INA240) <= 20 mm from the shunt sense pads (README)',
      all(v <= 14 for v in loop.values()) and u1_rsh <= 20, {'tails_to_shunt_mm': loop, 'U1.8_to_RSH1.2_mm': u1_rsh})
# ---------------- 7. panel side (x = 0): the four tails J1-J4 (decision 5.10 (6)) ----------------
panel = {}; pan_ok = True
for r in ('J1', 'J2', 'J3', 'J4'):
    anchors = sorted(pos(a.GetPosition()) for a in fmap[r].Pads() if a.GetAttribute() == p.PAD_ATTRIB_NPTH)
    solder = [pos(a.GetPosition()) for a in fmap[r].Pads() if a.GetAttribute() == p.PAD_ATTRIB_PTH]
    cyb = cbox(r); band = (0.0, cyb[1], min(q[0] for q in solder) - 2.0, cyb[3])   # the cable lies on the board between the wall and the pads
    inside_band = sorted(o for o in fmap if o not in holes_ref and o != r and not fmap[o].IsFlipped()
                         and cbox(o)[0] < band[2] and band[0] < cbox(o)[2] and cbox(o)[1] < band[3] and band[1] < cbox(o)[3])
    zones_ = [z for z in b.Zones() if z.GetIsRuleArea() and z.GetZoneName().startswith(f'{r} support')]
    cu_near = sorted({net(t) for t in b.GetTracks() for (ax, ay) in anchors if t.HitTest(xy(ax, ay), p.FromMM(SUPPORT_KEEPOUT[r]))})
    good = (len(anchors) == 2 and all(1.0 <= a[0] - S1['otwory_M3']['srednica'] / 2 <= 9.0 for a in anchors) and max(q[0] for q in solder) <= 22.0
            and len({q[0] for q in solder}) == 1 and not inside_band and len(zones_) == 2 and not cu_near and not fmap[r].IsFlipped()
            and all(math.dist(a, h) >= RZ + S1['otwory_M3']['srednica'] / 2 for a in anchors for h in want_h))
    panel[r] = {'anchor_hole_edge_to_x0_mm': [round(a[0] - S1['otwory_M3']['srednica'] / 2, 2) for a in anchors], 'pad_row_x': sorted({q[0] for q in solder}),
                'parts_on_the_cable': inside_band, 'anchor_rule_areas': len(zones_), f'tracks_within_{SUPPORT_KEEPOUT[r]}_mm_of_anchors': cu_near, 'ok': good}
    pan_ok &= good
order = [net(pad(r, q)) for r, q in sorted([(r, a.GetNumber()) for r in ('J1', 'J2', 'J3', 'J4') for a in fmap[r].Pads() if a.GetNumber()], key=lambda t: pxy(*t)[1])]
panel['column_order_top_down'] = order
check('Panel side x = 0: J1-J4 pad rows in one column <= 22 mm from x = 0, anchor holes 1-9 mm from x = 0 and outside the D7 zones of the '
      'M3 holes, with their 3 mm rule areas and no track in them, no part on the cable between the anchors and the pads; column PGND, MOD_BP, '
      'VMOTOR, PGND, MOD_MP, T_EGR_P3, T_EGR_P3, T_EGR_P1 (decision 5.10 (6))',
      pan_ok and order == ['PGND', 'MOD_BP', 'VMOTOR', 'PGND', 'MOD_MP', 'T_EGR_P3', 'T_EGR_P3', 'T_EGR_P1'], panel)
# ---------------- 8. ground separation and analog distance (README: PGND separate, GND logic / analog away from the power path) ----------------


def box_gap(a, c):
    A, C = cbox(a), cbox(c); dx = max(A[0] - C[2], C[0] - A[2], 0); dy = max(A[1] - C[3], C[1] - A[3], 0); return round(math.hypot(dx, dy), 2)


pg_pads = sorted(f'{f.GetReference()}.{a.GetNumber()}' for f in b.GetFootprints() for a in f.Pads() if net(a) == 'PGND')
gnd_on_pg = sorted({f.GetReference() for f in b.GetFootprints() for a in f.Pads() if net(a) == 'GND'} & {x.split('.')[0] for x in pg_pads})
gap_pg = None
for L in (p.F_Cu, p.B_Cu):
    g_ = p.SHAPE_POLY_SET(); pg_ = p.SHAPE_POLY_SET()
    for z in b.Zones():
        if not z.GetIsRuleArea() and z.IsOnLayer(L):
            if net(z) == 'GND':
                g_.BooleanAdd(z.GetFilledPolysList(L))
            elif net(z) == 'PGND':
                pg_.BooleanAdd(z.GetFilledPolysList(L))
    x_ = p.SHAPE_POLY_SET(g_); x_.Inflate(p.FromMM(.29), p.CORNER_STRATEGY_ROUND_ALL_CORNERS, p.FromMM(.005)); x_.BooleanIntersection(pg_)
    gap_pg = (gap_pg or []) + [{'layer': b.GetLayerName(L), 'overlap_within_0.29_mm2': round(x_.Area() / 1e12, 3), 'pgnd_pieces': pg_.OutlineCount()}]
ANALOG = ('U2', 'U3', 'U4', 'U5', 'U6', 'U7')
far_ = {}
for u in ANALOG:
    cy_ = courtyard(u); best = 99.0
    for n in FORCE:
        for L in (p.F_Cu, p.B_Cu):
            for z in pours[(n, L)]:
                fl = z.GetFilledPolysList(L)
                for k in range(fl.OutlineCount()):
                    pc = p.SHAPE_POLY_SET(); pc.AddOutline(fl.Outline(k))
                    for i in range(cy_.OutlineCount()):
                        o = cy_.Outline(i)
                        for j in range(o.PointCount()):
                            best = min(best, 0.0 if pc.Contains(o.CPoint(j)) else math.sqrt(pc.SquaredDistance(o.CPoint(j))) / 1e6)
    far_[u] = round(best, 2)
coil = {k: [n_ for n_ in ('PGND', 'VMOTOR', 'MOD_BP') for L in (p.F_Cu, p.B_Cu) for z in pours[(n_, L)] if z.GetFilledPolysList(L).Contains(pad('K1', k).GetPosition())] for k in ('A1', 'A2')}
check('Ground separation (README): GND and PGND not joined on P07 (no part on both; GND fill keeps >= 0.3 mm from the PGND fill on both layers; '
      'PGND one piece per layer); analog ICs U2-U7 >= 3 mm from every force pour; the 5 V KPWR coil pins (GND domain) outside the power pours',
      not gnd_on_pg and all(g['overlap_within_0.29_mm2'] == 0 and g['pgnd_pieces'] == 1 for g in gap_pg) and all(v >= 3.0 for v in far_.values())
      and not any(coil.values()), {'parts_on_GND_and_PGND': gnd_on_pg, 'gnd_pgnd': gap_pg, 'analog_to_force_pours_mm': far_, 'coil_pins_in_power_pours': coil})
# ---------------- 9. decoupling at the pins (README; MCP1525: load capacitor within 5 mm) ----------------
from board import DEC_CAPS, RETURN_PAIRS
try:
    from board import RETURN_ACCEPT as ACCEPT
except ImportError:
    ACCEPT = {}
DEC = {c: (u, v, 6) for c, (u, v, g) in DEC_CAPS.items()}
DEC.update({'C5': ('U2', '2', 5), 'C9': ('K1', 'A1', 8), 'C16': ('R50', '2', 8), 'C18': ('U18', '2', 6), 'C19': ('U18', '3', 6), 'C13': ('J5', '7', 8), 'C21': ('J_BP2', '14', 10)})
dd = {}
for c, (u, n, lim) in DEC.items():
    q = next(a for a in fmap[c].Pads() if a.GetNetname() == pad(u, n).GetNetname()); dd[f'{c}-{u}.{n}'] = (round(math.dist(pos(q.GetPosition()), pxy(u, n)), 2), lim)
check('Decoupling at the pins: 100 nF pad <= 6 mm from the supply pin of every IC, C5 4.7 uF <= 5 mm from U2.2 (MCP1525 data sheet), LDO in / out '
      'capacitors <= 6 mm, C9 10 uF <= 8 mm from the KPWR coil (decision 5.10), C16 at R50, C13 at J5.7, C21 at J_BP2.14', all(v <= lim for v, lim in dd.values()), dd)
# ---------------- 10. GND ----------------
isl = {b.GetLayerName(L): sum(z.GetFilledPolysList(L).OutlineCount() for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND' and z.IsOnLayer(L)) for L in (p.F_Cu, p.B_Cu)}
cov = {b.GetLayerName(L): round(sum(z.GetFilledPolysList(L).Area() for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND' and z.IsOnLayer(L)) / 1e12 / (W * H) * 100, 1)
       for L in (p.F_Cu, p.B_Cu)}
pw_area = round(sum(z.GetFilledPolysList(p.B_Cu).Area() for z in b.Zones() if not z.GetIsRuleArea() and net(z) in FORCE and z.IsOnLayer(p.B_Cu)) / 1e12, 0)
check('GND pours on both layers: B.Cu GND >= 45 % of the board (the power pours take the rest of the left part on both layers); island removal always',
      cov['B.Cu'] >= 45 and all(z.GetIslandRemovalMode() == p.ISLAND_REMOVAL_MODE_ALWAYS
      for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND') and len([z for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND']) == 2,
      {'cover_percent': cov, 'islands': isl, 'force_pours_b_cu_mm2': pw_area})
# ---------------- 10b. return paths ----------------
import gndpath
# Return path: GND copper (pours, tracks, pads, vias, both layers) from each decoupling capacitor's GND pad to the GND pin of its IC
# (gndpath.py, 0.2 mm raster) <= 1.3 x the straight distance + 3 mm: the return follows the capacitor, no detour around a cut plane.
cu_, via_ = gndpath.copper(b, 'GND', W, H); ret = {}
for c, (u, n) in RETURN_PAIRS.items():
    cp = next(a for a in fmap[c].Pads() if net(a) == 'GND'); src = gndpath.pad_point(b, c, cp.GetNumber()); dst = gndpath.pad_point(b, u, n)
    d_ = gndpath.distances(cu_, via_, src, {'d': dst}, limit_mm=120)['d']; st = round(math.dist(src[:2], dst[:2]), 1)
    ret[f'{c}.{cp.GetNumber()}-{u}.{n}'] = {'path_mm': d_, 'straight_mm': st, 'limit_mm': ACCEPT.get(c, round(1.3 * st + 3, 1)), **({'accepted': True} if c in ACCEPT else {})}
check('Decoupling return through GND copper: capacitor GND pad -> GND pin of its IC <= 1.3 x straight + 3 mm (both layers, gndpath.py; P06 R2 review F2)'
      + (f'; accepted exceptions {sorted(ACCEPT)}' if ACCEPT else ''), all(v['path_mm'] is not None and v['path_mm'] <= v['limit_mm'] for v in ret.values()), ret)
# ---------------- 11. silkscreen ----------------
cour = {}; side = {}
for f in b.GetFootprints():
    if f.GetReference() not in holes_ref:
        cour[f.GetReference()] = courtyard(f.GetReference()); side[f.GetReference()] = f.IsFlipped()


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
for r_, zn_ in PIN_MARKS.items():
    for num, t_ in zn_.items():
        qx, qy = pxy(r_, num); lim = max(p.ToMM(pad(r_, num).GetSize().x), p.ToMM(pad(r_, num).GetSize().y)) / 2 + 3.0
        znaki[f'{r_}.{num} {t_}'] = [s_ for s_, t in texts if s_ == t_ and math.dist((p.ToMM(t.GetPosition().x), p.ToMM(t.GetPosition().y)), (qx, qy)) <= lim]
check('Net marks of the tails J3 / J4 (ECU / EGR) and J5 (5VA / SW / GND) on the silkscreen next to their pads (text centre <= pad edge + 3 mm; S1 §9)',
      all(len(v) == 1 for v in znaki.values()), znaki)
small = []
for t in [x for x in b.GetDrawings() if isinstance(x, p.PCB_TEXT)] + [x for f in b.GetFootprints() for x in [f.Reference(), f.Value()] + list(f.GraphicalItems()) if isinstance(x, p.PCB_TEXT)]:
    if t.GetLayer() in (p.F_SilkS, p.B_SilkS) and t.IsVisible() and (p.ToMM(t.GetTextHeight()) < 1.0 - 1e-6 or p.ToMM(t.GetTextThickness()) < .15 - 1e-6):
        small.append({'text': t.GetShownText(False), 'height': round(p.ToMM(t.GetTextHeight()), 3), 'line': round(p.ToMM(t.GetTextThickness()), 3), 'at': pos(t.GetPosition())})
check('Silkscreen legible: every visible text on F.SilkS / B.SilkS >= 1.0 mm high with a >= 0.15 mm line (JLCPCB legend minimum; review 2.10 F1: '
      'service labels, edge markers, pin marks and six references were 0.8-0.9 / 0.12 mm)', not small, small)
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
