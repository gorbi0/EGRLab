"""Independent checks of the finished P05 R3 PCB in format S1 (fresh native DRC + S1 and P05-specific rules); structure and the
generic checks of P10 R2 / P09 R2 / P03 R6 verify_pcb.py (1.10.2026), board values from board.py.
usage: KiCad Python verify_pcb.py [alternative_board] [report_dir]
The alternative board is used by negative_controls.py (copies with one deliberate defect each).
Sources of the expected values: Plytki/Format-S1/format-s1.json and SPECYFIKACJA-FORMATU-S1.md (S1-3), the P12 contract docs/J_BP.csv,
docs/SERWIS.csv, the README layout requirements (decoupling limits of review P5-01, R2 table), docs/MECHANIKA.md; nothing is read
from placement.py or route_critical.py.
"""
from pathlib import Path
import pcbnew as p, json, sys, os, math, hashlib, csv, heapq, collections, re, xml.etree.ElementTree as ET
from sexpr import parse, one, sub
from provenance import run_fresh_drc
sys.path.insert(0, str(Path(__file__).resolve().parent))
from heights import height
from board import NAME, REV, CLASS, SLOTS, SIGNAL_W, JBP as JBP_ZL, JSV as JSV_ZL, PIN_MARKS, PWR, FINE, FINE_CLEARANCE, FINE_TRACK
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
HMAX = S1['poziomy']['wys_max_gora_standard']              # level 3, standoffs 20 mm (S1 section 7: P05 on level 3)
HMAX_BOTTOM = 1.5                                          # S1-2: SMD <= 1.5 mm on the bottom
JBP = collections.defaultdict(dict); SERW = collections.defaultdict(dict)
with open(P / 'docs/J_BP.csv', encoding='utf-8-sig') as fh:
    for r in csv.DictReader(fh, delimiter=';'):
        JBP[r['zlacze']][int(r['pin'])] = r['siec']
with open(P / 'docs/SERWIS.csv', encoding='utf-8-sig') as fh:
    for r in csv.DictReader(fh, delimiter=';'):
        SERW[r['zlacze']][int(r['pin'])] = (r['siec'], r['rezystor'])
# S1 section 6 resistor class: 1K logic and rails, 10K high-impedance / pull-up nodes, 4.7K the owned MF0207 on VBAT_SENSE (README P05 R3)
HIGHZ = {'REF_2V5', 'RAIL_SENSE', 'RAIL_LOW', 'RAIL_HIGH', 'DAQ_RAIL_N', 'P05_SUP3_N'}; CLASS_VAL = {'VBAT_SENSE': '4.7K'}


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
# rules: S1 section 3 (as P02 R3 / R4) everywhere; the fine-pitch exception only inside the courtyards of U1 / U3 (README P05 R3)
pro = json.loads((P / f'eda/{NAME}.kicad_pro').read_text()); ds = pro['board']['design_settings']; rules = ds['rules']
cls = {c['name']: c for c in pro['net_settings']['classes']}
_dru = path.parent / f'{NAME}.kicad_dru'   # the rules DRC uses for this board (negative controls carry their own copy)
dru = _dru.read_text(encoding='utf-8') if _dru.exists() else ''
dru_rules = re.findall(r'\(rule "([^"]*)"\s*\(condition "([^"]*)"\)\s*\(constraint (\w+) \(min ([\d.]+)mm\)\)\)', dru)
want_cond = {'track_width': [f"A.Type == 'Track' && !({' || '.join(f'A.intersectsCourtyard({chr(39)}{r}{chr(39)})' for r in FINE)})",
                             f"A.Type == 'Track' && ({' || '.join(f'A.intersectsCourtyard({chr(39)}{r}{chr(39)})' for r in FINE)})"],
             'clearance': [' || '.join(f"(A.intersectsCourtyard('{r}') && B.intersectsCourtyard('{r}'))" for r in FINE)]}
dru_ok = (len(dru_rules) == 3 and sorted(c for _, c, k, v in dru_rules if k == 'track_width') == sorted(want_cond['track_width'])
          and [c for _, c, k, v in dru_rules if k == 'clearance'] == want_cond['clearance']
          and {(k, float(v)) for _, c, k, v in dru_rules} == {('track_width', SIGNAL_W), ('track_width', FINE_TRACK), ('clearance', FINE_CLEARANCE)}
          and all(float(v) == SIGNAL_W for _, c, k, v in dru_rules if k == 'track_width' and c.startswith("A.Type == 'Track' && !(")))
check(f'Rules as P02 R3 / R4 (net classes: clearance >= 0.25, PWR 0.30, track >= {SIGNAL_W:.2f}, edge 0.5), annular ring >= 0.25 mm (S1 section 3); '
      f'custom rules only: track >= {SIGNAL_W:.2f} outside, clearance {FINE_CLEARANCE} / track {FINE_TRACK} only for items touching the courtyard of '
      f'{" / ".join(FINE)} (fine pitch, README); no DRC exclusions',
      rules['min_clearance'] >= FINE_CLEARANCE - 1e-9 and rules['min_track_width'] >= FINE_TRACK - 1e-9 and rules['min_copper_edge_clearance'] >= .5
      and rules['min_via_annular_width'] >= .25 and cls['Default']['track_width'] >= .3 - 1e-9 and not ds['drc_exclusions']
      and all(c['clearance'] >= .25 for c in cls.values()) and cls['PWR']['clearance'] >= .3 and cls['PWR']['track_width'] >= .6 and dru_ok,
      {'board_minimums': {k: rules[k] for k in ('min_clearance', 'min_track_width', 'min_copper_edge_clearance', 'min_via_annular_width')},
       'classes': {k: (v['track_width'], v['clearance']) for k, v in cls.items()}, 'custom_rules': dru_rules})
fine_poly = {r: courtyard(r) for r in FINE}
narrow = []
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA) or p.ToMM(t.GetWidth()) >= SIGNAL_W - 1e-6:
        continue
    where = [r for r, poly in fine_poly.items() if touches(t, poly)]
    if not where or p.ToMM(t.GetWidth()) < FINE_TRACK - 1e-6:
        narrow.append({'net': net(t), 'width': round(p.ToMM(t.GetWidth()), 3), 'start': pos(t.GetStart()), 'end': pos(t.GetEnd())})
check(f'Every track >= {SIGNAL_W:.2f} mm (S1 section 3); narrower ones (>= {FINE_TRACK}) only where they touch the courtyard of {" / ".join(FINE)}', not narrow, narrow[:20])
ring = [f'{f.GetReference()}.{a.GetNumber()}' for f in b.GetFootprints() for a in f.Pads() if a.GetAttribute() == p.PAD_ATTRIB_PTH
        and (min(p.ToMM(a.GetSize().x), p.ToMM(a.GetSize().y)) - p.ToMM(a.GetDrillSize().x)) / 2 < .25 - 1e-6]
ring += [f'via {pos(t.GetPosition())}' for t in b.GetTracks() if isinstance(t, p.PCB_VIA) and (p.ToMM(t.GetWidth(p.F_Cu)) - p.ToMM(t.GetDrill())) / 2 < .25 - 1e-6]
check('Every PTH pad and via has an annular ring >= 0.25 mm (measured on the copper)', not ring, ring[:20])
# ---------------- 3. edge A: J_BP1 / J_BP2 (contract docs/J_BP.csv) ----------------
jd = {}; ok = True
for k, (r, npins) in enumerate([('J_BP1', 10), ('J_BP2', 20)]):
    f = fmap.get(r)
    if not f:
        ok = False; jd[r] = 'missing'; continue
    pads1 = {a.GetNumber(): pos(a.GetPosition()) for a in f.Pads()}; fab = layer_bbox(f, p.F_Fab)
    xs = [v[0] for v in pads1.values()]; cx = (min(xs) + max(xs)) / 2; x0 = STEP * k
    nets = {int(n): net(pad(r, n)) for n in pads1}
    good = (abs(cx - (x0 + S1['krawedz_A']['srodek_x_w_slocie'])) < .05 and pads1['1'][0] == min(xs) and nets == JBP[r] and fab and abs(fab[1]) < .3
            and len(pads1) == npins and f'IDC-Header_2x{npins // 2:02d}' in f.GetFPIDAsString())
    jd[r] = {'centre_x': round(cx, 3), 'pin1': pads1['1'], 'fab_front_y': fab and round(fab[1], 3), 'pinout_equals_J_BP.csv': nets == JBP[r], 'ok': good}
    ok &= good
check('J_BP1 / J_BP2 (edge A): IDC 2x5 / 2x10 angled, body front at y = 0, pin centre x = 26.5 / 80.0 (slots S1 / S2), pin 1 at the smaller x, '
      'pinout = docs/J_BP.csv (P12 contract)', ok, jd)
# ---------------- 4. edge B: service headers (contract docs/SERWIS.csv) ----------------
LABEL = next(_ast.literal_eval(n.value) for n in _ast.parse((P / 'src/silkscreen.py').read_text(encoding='utf-8')).body
             if isinstance(n, _ast.Assign) and any(getattr(t, 'id', '') == 'LABEL' for t in n.targets))   # tables independent of the result
texts = [(t.GetText(), t) for t in b.GetDrawings() if isinstance(t, p.PCB_TEXT) and t.GetLayer() == p.F_SilkS]
svd = {}; sv_ok = True
for k, hdr in enumerate(JSV_ZL):
    f = fmap.get(hdr); x0 = STEP * k; problems = []
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
check('Service headers J_SV1 / J_SV2 (edge B, S1 section 6): <= 13 pins in x 10..43 of the slot, pin 1 at the larger x, pins out ~6 mm, GND on both '
      'ends, one series resistor per pin as docs/SERWIS.csv and of its S1 class (1K, 10K for high-impedance / pull-up nodes, 4.7K VBAT_SENSE) '
      '<= 10 mm from its node, one silk label per pin with the name of its node (LABEL in silkscreen.py), GND at both ends', sv_ok, svd)
# ---------------- 4b. reserved strips of edge A (S1 §5) ----------------
pasy = {}
for zl in JBP_ZL:
    xs_ = [p.ToMM(a.GetPosition().x) for a in fmap[zl].Pads() if a.GetNumber()]; x0 = STEP * int(((min(xs_) + max(xs_)) / 2) // STEP)
    y0, y1 = S1['krawedz_A']['strefa_y']; pas = (x0 + 10.0, y0, x0 + 43.0, y1)
    T_ = .1   # courtyard outline tolerance (1.10: R43 MF0207 courtyard 0.02 mm into y 10, its body ends at y 10.3)
    pasy[zl] = {'pas': pas, 'czesci': sorted(r for r in fmap if r not in holes_ref and r != zl
                                             and cbox(r)[0] < pas[2] - T_ and pas[0] + T_ < cbox(r)[2] and cbox(r)[1] < pas[3] - T_ and pas[1] + T_ < cbox(r)[3])}
check('Reserved strip of edge A (S1 §5: y 0-10, x 10-43 of each J_BP slot): no other part on either side', not any(v['czesci'] for v in pasy.values()), pasy)
# ---------------- 5. heights ----------------
hh = {r: height(r, parts) for r in onboard}
check(f'Every part <= {HMAX} mm above the board (level 3, S1 section 4; src/heights.py)', all(v <= HMAX for v in hh.values()),
      {'max': max(hh.items(), key=lambda q: q[1]), 'over': {r: v for r, v in hh.items() if v > HMAX}})
# ---------------- 6. U1 (AD7606B): decoupling on the copper (README; review P5-01, R2 table) ----------------


def path_mm(netname, a, c, f_only=False):
    """Shortest copper path pad centre -> pad centre over the net's tracks and vias (R2 decoupling.py): graph nodes are track ends, points
    where a track end lies on another track, vias (both layers) and the two pads (joined to every node inside them)."""
    items = [t for t in b.GetTracks() if net(t) == netname and not (f_only and (isinstance(t, p.PCB_VIA) or t.GetLayer() != p.F_Cu))]
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


LIMITS = [('1', 'C4', 3.0), ('48', 'C7', 3.0), ('37', 'C5', 3.0), ('38', 'C5', 3.0), ('23', 'C8', 4.0), ('36', 'C9', 3.0), ('39', 'C10', 3.0),
          ('42', 'C11', 3.0), ('42', 'C12', 6.0), ('44', 'C13', 6.0), ('45', 'C13', 6.0)]
dec = []
for num, cap, lim in LIMITS:
    n_ = net(pad('U1', num)); cp = next(a for a in fmap[cap].Pads() if net(a) == n_)
    d = path_mm(n_, ('U1', num), (cap, cp.GetNumber())); dec.append({'pin': f'U1.{num}', 'net': n_, 'capacitor': cap, 'path_mm': d, 'limit_mm': lim, 'pass': d is not None and d <= lim})
check('U1 decoupling on the copper (R2 table, review P5-01): AVCC 1 / 48 / 37 / 38, REGCAP 36 / 39 and REFIN/OUT 42 (100 nF) <= 3 mm, '
      'VDRIVE 23 <= 4 mm, 22 uF on REFIN/OUT 42 and REFCAP 44 / 45 <= 6 mm (pad centre to pad centre)', all(x['pass'] for x in dec), dec)
via_nets = {n_: sum(1 for t in b.GetTracks() if isinstance(t, p.PCB_VIA) and net(t) == n_) for n_ in ('REGCAP_A', 'REGCAP_D', 'REFCAP', 'ADC_REF')}
top_caps = {c: not fmap[c].IsFlipped() for c in ('C9', 'C10', 'C12', 'C13')}
c12_path = path_mm('ADC_REF', ('U1', '42'), ('C12', '1'), f_only=True) if net(pad('C12', '1')) == 'ADC_REF' else None   # top copper only
c12_novia = c12_path is not None and c12_path <= 6.0
check('REGCAP_A, REGCAP_D and REFCAP without vias, their capacitors (and the 22 uF on ADC_REF) on top; ADC_REF has one via only (to C11 on '
      'the bottom, 100 nF <= 1.5 mm, README)', via_nets['REGCAP_A'] == via_nets['REGCAP_D'] == via_nets['REFCAP'] == 0 and via_nets['ADC_REF'] == 1
      and all(top_caps.values()) and c12_novia, {'vias': via_nets, 'top': top_caps, 'C12_path_mm': c12_path})
u1_poly = courtyard('U1')
dout_under = [pos(t.GetStart()) for t in b.GetTracks() if net(t) == 'AD_DOUT_LOCAL' and not isinstance(t, p.PCB_VIA) and t.GetLayer() == p.B_Cu and touches(t, u1_poly)]
dout_vias = [pos(t.GetPosition()) for t in b.GetTracks() if net(t) == 'AD_DOUT_LOCAL' and isinstance(t, p.PCB_VIA) and touches(t, u1_poly, p.F_Cu)]
check('DOUT (AD_DOUT_LOCAL) not under U1 on B.Cu and no via inside the U1 courtyard (review P5-01)', not dout_under and not dout_vias,
      {'b_cu_tracks_under_U1': dout_under, 'vias_in_courtyard': dout_vias})
gnd_u1 = [a for a in fmap['U1'].Pads() if net(a) == 'GND']; ring_ = cbox('U1')
inner = (ring_[0] + 2.4, ring_[1] + 2.4, ring_[2] - 2.4, ring_[3] - 2.4)   # inside the pad ring (pads end 4.9 mm from the centre)
gvias = [pos(t.GetPosition()) for t in b.GetTracks() if isinstance(t, p.PCB_VIA) and net(t) == 'GND' and inner[0] < p.ToMM(t.GetPosition().x) < inner[2]
         and inner[1] < p.ToMM(t.GetPosition().y) < inner[3]]
fpour = [z for z in b.Zones() if not z.GetIsRuleArea() and net(z) == 'GND' and z.IsOnLayer(p.F_Cu)]
allvias = [t.GetPosition() for t in b.GetTracks() if isinstance(t, p.PCB_VIA) and net(t) == 'GND']
cut, unstitched = [], []
pieces = []
for z in fpour:
    fl = z.GetFilledPolysList(p.F_Cu)
    for k in range(fl.OutlineCount()):
        pc = p.SHAPE_POLY_SET(); pc.AddOutline(fl.Outline(k))
        for h in range(fl.HoleCount(k)):
            pc.AddHole(fl.Hole(k, h))
        pieces.append(pc)
for a in gnd_u1:   # the pour piece each GND pin touches must hold a GND via (run 2: router copper split the inner pour, U1.2 alone)
    sh = p.SHAPE_POLY_SET(); a.TransformShapeToPolygon(sh, p.F_Cu, 0, p.FromMM(.005), p.ERROR_INSIDE)
    def meets(pc):
        x = p.SHAPE_POLY_SET(pc); x.BooleanIntersection(sh); return x.OutlineCount() > 0 and x.Area() > 0
    mine = [pc for pc in pieces if meets(pc)]
    if not mine:
        cut.append(a.GetNumber())
    elif not any(pc.Contains(v) for pc in mine for v in allvias):
        unstitched.append(a.GetNumber())
solid = [a.GetNumber() for a in gnd_u1 if a.GetLocalZoneConnection() != p.ZONE_CONNECTION_FULL]
check('U1 ground: every GND pin touches the F.Cu pour inside the pad ring (solid connection) on a piece that holds a GND via, '
      '>= 4 GND vias inside the ring to B.Cu', not cut and not unstitched and not solid and len(gvias) >= 4,
      {'pins_without_pour': cut, 'pins_on_unstitched_piece': unstitched, 'pins_not_solid': solid, 'inner_vias': gvias})
u1cy = courtyard('U1'); crit_nets = {net(a) for a in fmap['U1'].Pads()}
foreign = sorted({net(t) for t in b.GetTracks() if net(t) not in crit_nets and not isinstance(t, p.PCB_VIA) and touches(t, u1cy)}
                 | {net(t) for t in b.GetTracks() if isinstance(t, p.PCB_VIA) and net(t) not in crit_nets and touches(t, u1cy, p.F_Cu)})
check('No copper of other nets in the U1 courtyard (only the nets of U1 pins: escapes, decoupling, inner pour vias; README)', not foreign, foreign)
# ---------------- 7. panel side (x = 0): TAPS J4, AUX J6, SW1 (README, docs/MECHANIKA.md) ----------------
panel = {}
for r in ('J4', 'J6'):
    anchors = sorted(pos(a.GetPosition()) for a in fmap[r].Pads() if a.GetAttribute() == p.PAD_ATTRIB_NPTH)
    solder = [pos(a.GetPosition()) for a in fmap[r].Pads() if a.GetAttribute() == p.PAD_ATTRIB_PTH]
    panel[r] = {'anchor_hole_edge_to_x0_mm': [round(a[0] - S1['otwory_M3']['srednica'] / 2, 2) for a in anchors], 'solder_x_max': round(max(q[0] for q in solder), 2),
                'ok': len(anchors) == 2 and all(1.5 <= a[0] - 1.6 <= 6.0 for a in anchors) and max(q[0] for q in solder) <= 25.0}
sw = fmap['SW1']; sw_cy = cbox('SW1'); legs = [pos(a.GetPosition()) for a in sw.Pads() if not a.GetNumber()]
poles = [pos(a.GetPosition()) for a in sw.Pads() if a.GetNumber()]
panel['SW1'] = {'courtyard_x0': round(sw_cy[0], 2), 'legs': legs, 'poles_x': sorted({q[0] for q in poles}),
                'ok': sw_cy[0] < -2.0 and len(legs) == 2 and all(q[0] >= 2.5 for q in legs + poles) and not sw.IsFlipped()}
check('Panel side: TAPS J4 and AUX J6 anchor holes 1.5-6 mm from x = 0 (cables leave through the panel), solder rows <= 25 mm in; '
      'SW1 (E-Switch M6) bushing and lever beyond x = 0, support legs and poles on the board', all(v['ok'] for v in panel.values()), panel)
# ---------------- 8. placement requirements (decoupling, drivers, protection) ----------------
DEC = {'C15': ('U3', '8'), 'C14': ('U2', '2'), 'C24': ('U2', '6'), 'C16': ('U5', '14'), 'C17': ('U6', '2'), 'C18': ('U7', '2'), 'C19': ('U8', '14'),
       'C20': ('U9', '14'), 'C21': ('U10', '14'), 'C22': ('U11', '14'), 'C2': ('U12', '2'), 'C3': ('U12', '3'), 'C1': ('R1', '2')}
dd = {}
for c, (u, n) in DEC.items():
    q = next(a for a in fmap[c].Pads() if a.GetNetname() == pad(u, n).GetNetname()); dd[f'{c}-{u}.{n}'] = round(math.dist(pos(q.GetPosition()), pxy(u, n)), 2)
check('Decoupling at the IC pins: capacitor pad <= 6 mm from its supply / output pin (U2-U12; C1 220 uF at R1 pin 2 = 5VA_P05; limit as P03 R6 / P09 R2)',
      all(v <= 6 for v in dd.values()), dd)
drv = {}
for r_, (u, n) in {'R26': ('U11', '3'), 'R27': ('U11', '6')}.items():
    q = next(a for a in fmap[r_].Pads() if a.GetNetname() == pad(u, n).GetNetname()); drv[f'{r_}-{u}.{n}'] = round(math.dist(pos(q.GetPosition()), pxy(u, n)), 2)
for i in (1, 2, 3):   # flyback diode anode (MEAS_COIL_LOW) at the coil pin 8 of its relay
    drv[f'D{i}.2-K{i}.8'] = round(math.dist(pxy(f'D{i}', '2'), pxy(f'K{i}', '8')), 2)
check('Series resistors at the driver (R26 DOUT, R27 BUSY: pad <= 6 mm from U11.3 / U11.6) and flyback diodes at their coils (D1-D3 anode <= 6 mm from K1-K3 pin 8)',
      all(v <= 6 for v in drv.values()), drv)
filt = {}
for i in range(8):
    cap = f'C{27 + i}'; n_ = f'ADC_CH{i + 1}'; num = str(49 + 2 * i)
    filt[cap] = path_mm(n_, ('U1', num), (cap, next(a.GetNumber() for a in fmap[cap].Pads() if net(a) == n_)))
check('Input filters C27-C34 on the channel copper <= 12 mm from their U1 inputs (pins 49-63; 45 deg fan to the filter column)',
      all(v is not None and v <= 12 for v in filt.values()), filt)
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
for r_, zn in PIN_MARKS.items():
    for num, t_ in zn.items():
        qx, qy = pxy(r_, num)
        znaki[f'{r_}.{num} {t_}'] = [s_ for s_, t in texts if s_ == t_ and math.dist((p.ToMM(t.GetPosition().x), p.ToMM(t.GetPosition().y)), (qx, qy)) <= 3.0]
check('Pin 1 marks of the wire tails TAPS J4 and AUX J6 on the silkscreen, <= 3 mm from their pads (S1 §9)',
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
