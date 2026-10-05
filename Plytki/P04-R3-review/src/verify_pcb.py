"""Independent checks of the finished P04 R3 PCB in format S1 (fresh native DRC + S1 and P04-specific rules). Structure and the generic
checks of P05 R3 / P03 R6 verify_pcb.py; the P04 checks come from P04 R2.2 verify_pcb.py (watchdog RC, C1 on the timing nodes, SAFE_N end
at U2.11, series resistors at the connector pins) and from the task of 5.10.2026 (supply widths, SUP_N_OUT, decoupling).
usage: KiCad Python verify_pcb.py [alternative_board] [report_dir]
The alternative board is used by negative_controls.py (copies with one deliberate defect each).
Sources of the expected values: Plytki/Format-S1/format-s1.json and SPECYFIKACJA-FORMATU-S1.md (S1-3), the P12 contract docs/J_BP.csv,
docs/SERWIS.csv, docs/MECHANIKA.md, docs/KONTRAKT-RESET.md, README (decisions); nothing is read from placement.py or route_critical.py.
"""
from pathlib import Path
import pcbnew as p, json, sys, os, math, hashlib, csv, heapq, collections, xml.etree.ElementTree as ET
from sexpr import parse, one, sub
from provenance import run_fresh_drc
sys.path.insert(0, str(Path(__file__).resolve().parent))
from heights import height
from board import NAME, REV, CLASS, SLOTS, SIGNAL_W, JBP as JBP_ZL, JSV as JSV_ZL, PWR, PWR_W
import ast as _ast
TYTUL = f"{REV} S1-{CLASS} {SLOTS[0] if len(SLOTS) == 1 else SLOTS[0] + '-' + SLOTS[-1]}"   # S1 §9 (as P02 R4 / P03 R6)
P = Path(__file__).resolve().parents[1]
path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else P / f'eda/{NAME}.kicad_pcb'
out = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else P / 'verification'
b = p.LoadBoard(str(path)); b.BuildConnectivity()
S1 = json.loads((P.parents[0] / 'Format-S1/format-s1.json').read_text(encoding='utf-8'))
root = ET.parse(P / f'verification/{NAME}.xml').getroot(); parts = json.loads(Path(os.environ.get('EGRLAB_PARTS_JSON', P / 'docs/parts.json')).read_text(encoding='utf-8'))
checks = []; details = {}
KLASA, SLOTY = CLASS, SLOTS
W, H = S1['klasy'][KLASA]['W'], S1['klasy'][KLASA]['H']; STEP = S1['rozstaw_slotow']
HMAX = S1['poziomy']['wys_max_gora_standard']              # level 6 under the lid: 16.5 mm (user decision 5.10.2026)
HMAX_BOTTOM = 1.5                                          # S1-2: SMD <= 1.5 mm on the bottom
JBP = collections.defaultdict(dict); SERW = collections.defaultdict(dict)
with open(P / 'docs/J_BP.csv', encoding='utf-8-sig') as fh:
    for r in csv.DictReader(fh, delimiter=';'):
        JBP[r['zlacze']][int(r['pin'])] = r['siec']
with open(P / 'docs/SERWIS.csv', encoding='utf-8-sig') as fh:
    for r in csv.DictReader(fh, delimiter=';'):
        SERW[r['zlacze']][int(r['pin'])] = (r['siec'], r['rezystor'])
# S1 section 6 resistor class: 1K logic and rails; 10K the passive nodes SAFE_N (R4 10k / R5 100k) and ARM_BUTTON_N (R2 10k);
# Q1_B 1K on purpose (README decision 6: probe E21 shorts the pin to GND and must turn Q1 off)
CLASS_VAL = {'SAFE_N': '10K', 'ARM_BUTTON_N': '10K'}


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


def tracks(netname, vias=False):
    return [t for t in b.GetTracks() if net(t) == netname and isinstance(t, p.PCB_VIA) == vias]


def cu_len(netname):
    return round(sum(p.ToMM(t.GetLength()) for t in tracks(netname)), 2)


# ---------------- 1. native DRC, fresh, bound to the inputs ----------------
drc, receipt = run_fresh_drc(path, out / 'drc.json')
_silk = json.loads((P / 'routing/silkscreen.json').read_text(encoding='utf-8'))
trimmed = set(_silk.get('dropped_by_part', {})) | set(_silk.get('moved_texts_by_part', {}))
fp_uuid = {f.m_Uuid.AsString(): f.GetReference() for f in b.GetFootprints()}


def pads_equal_library(ref):
    """P03 R6 (review 1.10): an accepted lib_footprint_mismatch may differ from the library footprint only outside the copper."""
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
check('Fresh native DRC: 0 violations / 0 unconnected / 0 schematic parity (all severities; lib_footprint_mismatch only for parts '
      'whose silk silkscreen.py trimmed and whose pads equal the library)',
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
check('S1-2 section 4: parts on the bottom only SMD <= 1.5 mm, no SOIC (level 6 is not level 1), >= 1 mm from THT pads (P04 R3: none on the bottom)',
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
pro = json.loads((P / f'eda/{NAME}.kicad_pro').read_text()); ds = pro['board']['design_settings']; rules = ds['rules']
cls = {c['name']: c for c in pro['net_settings']['classes']}
pats = {(q['netclass'], q['pattern']) for q in pro['net_settings'].get('netclass_patterns') or []}
check(f'Rules as P02 R3 / R4 (clearance >= 0.25, track >= {SIGNAL_W:.2f}, edge 0.5), annular ring >= 0.25 mm (S1 section 3); class PWR {PWR_W} mm for '
      f'{", ".join(PWR)}; no custom rules file, no DRC exclusions',
      rules['min_clearance'] >= .25 - 1e-9 and rules['min_track_width'] >= SIGNAL_W - 1e-9 and rules['min_copper_edge_clearance'] >= .5
      and rules['min_via_annular_width'] >= .25 and cls['Default']['track_width'] >= SIGNAL_W - 1e-9 and not ds['drc_exclusions']
      and all(c['clearance'] >= .25 for c in cls.values()) and cls['PWR']['track_width'] >= PWR_W - 1e-9 and pats == {('PWR', n) for n in PWR}
      and not (path.parent / f'{NAME}.kicad_dru').exists(),
      {'board_minimums': {k: rules[k] for k in ('min_clearance', 'min_track_width', 'min_copper_edge_clearance', 'min_via_annular_width')},
       'classes': {k: (v['track_width'], v['clearance']) for k, v in cls.items()}, 'patterns': sorted(pats)})
narrow = [{'net': net(t), 'width': round(p.ToMM(t.GetWidth()), 3), 'start': pos(t.GetStart())} for t in b.GetTracks()
          if not isinstance(t, p.PCB_VIA) and p.ToMM(t.GetWidth()) < SIGNAL_W - 1e-6]
check(f'Every track >= {SIGNAL_W:.2f} mm (S1 section 3)', not narrow, narrow[:20])
pw = {n: {'tracks': len(tracks(n)), 'min_width_mm': round(min((p.ToMM(t.GetWidth()) for t in tracks(n)), default=0), 3), 'copper_mm': cu_len(n)} for n in PWR}
check(f'Supply nets {", ".join(PWR)}: every track >= {PWR_W} mm (task 5.10: P04_3V3, 5V_SYS, PANEL_3V3 >= 0.4 mm; 3V3_IO in the same class)',
      all(v['tracks'] and v['min_width_mm'] >= PWR_W - 1e-6 for v in pw.values()), pw)
ring = [f'{f.GetReference()}.{a.GetNumber()}' for f in b.GetFootprints() for a in f.Pads() if a.GetAttribute() == p.PAD_ATTRIB_PTH
        and (min(p.ToMM(a.GetSize().x), p.ToMM(a.GetSize().y)) - p.ToMM(a.GetDrillSize().x)) / 2 < .25 - 1e-6]
ring += [f'via {pos(t.GetPosition())}' for t in b.GetTracks() if isinstance(t, p.PCB_VIA) and (p.ToMM(t.GetWidth(p.F_Cu)) - p.ToMM(t.GetDrill())) / 2 < .25 - 1e-6]
check('Every PTH pad and via has an annular ring >= 0.25 mm (measured on the copper)', not ring, ring[:20])
# ---------------- 3. edge A: J_BP1..3 (contract docs/J_BP.csv) ----------------
jd = {}; ok = True
for k, (r, npins) in enumerate([('J_BP1', 16), ('J_BP2', 20), ('J_BP3', 20)]):
    f = fmap.get(r)
    if not f:
        ok = False; jd[r] = 'missing'; continue
    pads1 = {a.GetNumber(): pos(a.GetPosition()) for a in f.Pads()}; fab = layer_bbox(f, p.F_Fab)
    xs = [v[0] for v in pads1.values()]; cx = (min(xs) + max(xs)) / 2; x0 = STEP * k
    nets = {int(n): net(pad(r, n)) for n in pads1}
    good = (abs(cx - (x0 + S1['krawedz_A']['srodek_x_w_slocie'])) < .05 and pads1['1'][0] == min(xs) and nets == JBP[r] and fab and abs(fab[1]) < .3
            and len(pads1) == npins and f'IDC-Header_2x{npins // 2:02d}_P2.54mm_Horizontal' in f.GetFPIDAsString() and not f.IsFlipped()
            and all(nets[n] == 'GND' for n in nets if n % 2))
    jd[r] = {'centre_x': round(cx, 3), 'pin1': pads1['1'], 'fab_front_y': fab and round(fab[1], 3), 'pinout_equals_J_BP.csv': nets == JBP[r], 'ok': good}
    ok &= good
check('J_BP1..3 (edge A): IDC 2x8 / 2x10 / 2x10 angled, body front at y = 0, pin centre x = 26.5 / 80.0 / 133.5 (slots S1-S3), pin 1 at the smaller x, '
      'odd pins GND, pinout = docs/J_BP.csv (P12 contract)', ok, jd)
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
    if len(pd) != len(SERW[hdr]): problems.append(f'{len(pd)} pins, SERWIS.csv {len(SERW[hdr])}')
    if min(xs) - .85 < x0 + lo - 1e-6 or max(xs) + .85 > x0 + hi + 1e-6: problems.append(f'pins outside x {x0 + lo}..{x0 + hi}')
    if not fab or fab[3] - H < 5.0: problems.append(f'pins not ~6 mm beyond edge B (fab {fab})')
    if net(pd[0][1]) != 'GND' or net(pd[-1][1]) != 'GND': problems.append('GND not on both ends')
    if pd[0][1].GetPosition().x <= pd[-1][1].GetPosition().x: problems.append('pin 1 not at the larger x (MECHANIKA: KiCad right-angle header)')
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
        val = fmap[r].GetValue().upper(); want_val = CLASS_VAL.get(node, '1K')
        others = [x for ff in b.GetFootprints() for x in ff.Pads() if x.GetNetname() == other.GetNetname() and ff.GetReference() != r]
        # node copper = its other pads and its locked vias (P04 R3: 5V_SYS reaches R57 through the locked escape round J_BP3, via at the resistor)
        others_xy = [pos(x.GetPosition()) for x in others] + [pos(v.GetPosition()) for v in tracks(node, True) if v.IsLocked()]
        dist = min((math.dist(pos(other.GetPosition()), q) for q in others_xy), default=99)
        if node != want_net or not want_res.startswith(f'{r} {fmap[r].GetValue()} '): problems.append(f'pin {n}: {r} {val} on {node}, SERWIS.csv {want_net} {want_res}')
        if val != want_val: problems.append(f'pin {n}: {r} {val}, class S1 §6 wants {want_val}')
        if dist > 10: problems.append(f'pin {n}: {r} not at its node ({dist:.1f} mm)')
        lab = LABEL.get(node)
        tx = [t for s, t in texts if lab and s == lab and abs(p.ToMM(t.GetPosition().x) - p.ToMM(a.GetPosition().x)) < 1.3 and 80 < p.ToMM(t.GetPosition().y) < H]
        if len(tx) != 1: problems.append(f'pin {n}: {len(tx)} silk labels')
        rows.append({'pin': n, 'node': node, 'resistor': r, 'value': val, 'node_dist_mm': round(dist, 1), 'label': lab, 'side': 'B' if fmap[r].IsFlipped() else 'F'})
    svd[hdr] = {'problems': problems, 'pins': rows}; sv_ok &= not problems
check('Service headers J_SV1..3 (edge B, S1 section 6): <= 13 pins in x 10..43 of the slot, pin 1 at the larger x, pins out ~6 mm, GND on both '
      'ends, one series resistor per pin as docs/SERWIS.csv and of its class (1K; 10K SAFE_N / ARM_BUTTON_N, README decision 6) <= 10 mm from '
      'its node (a pad or locked via of the node net), one silk label per pin with the name of its node (LABEL in silkscreen.py), GND at both ends', sv_ok, svd)
# ---------------- 4b. reserved strips of edge A (S1 §5) ----------------
pasy = {}
for zl in JBP_ZL:
    xs_ = [p.ToMM(a.GetPosition().x) for a in fmap[zl].Pads() if a.GetNumber()]; x0 = STEP * int(((min(xs_) + max(xs_)) / 2) // STEP)
    y0, y1 = S1['krawedz_A']['strefa_y']; pas = (x0 + 10.0, y0, x0 + 43.0, y1); T_ = .1
    pasy[zl] = {'pas': pas, 'czesci': sorted(r for r in fmap if r not in holes_ref and r != zl
                                             and cbox(r)[0] < pas[2] - T_ and pas[0] + T_ < cbox(r)[2] and cbox(r)[1] < pas[3] - T_ and pas[1] + T_ < cbox(r)[3])}
check('Reserved strip of edge A (S1 §5: y 0-10, x 10-43 of each J_BP slot): no other part', not any(v['czesci'] for v in pasy.values()), pasy)
# ---------------- 5. heights ----------------
hh = {r: height(r, parts) for r in onboard}
check(f'Every part <= {HMAX} mm above the board (limit above level 6, user decision 5.10; src/heights.py)', all(v <= HMAX for v in hh.values()),
      {'max': max(hh.items(), key=lambda q: q[1]), 'over': {r: v for r, v in hh.items() if v > HMAX}})


# ---------------- 6. P04 circuit on the copper ----------------
def path_mm(netname, a, c):
    """Shortest copper path pad centre -> pad centre over the net's tracks and vias (P05 R3 verify_pcb.py)."""
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


# watchdog (P04 R2.2, MECHANIKA: C1 between U1.15 and U1.14 as short as possible, away from PWM)
wd = {}
for n in ['WD_RC', 'WD_C']:
    tt = tracks(n)
    wd[n] = {'length_mm': cu_len(n), 'vias': len(tracks(n, True)), 'all_front_locked': bool(tt) and all(t.GetLayer() == p.F_Cu and t.IsLocked() for t in tt)}
check('Watchdog RC traces (WD_RC, WD_C) <= 15 mm each, locked, F.Cu only, without vias (P04 R2.2)', all(v['length_mm'] <= 15 and v['vias'] == 0 and v['all_front_locked'] for v in wd.values()), wd)
check('C1 lands on the U1 timing nodes (C1.1 = U1.15 = WD_RC, C1.2 = U1.14 = WD_C), not on ground (P04 R2.2)',
      net(pad('C1', 1)) == net(pad('U1', 15)) == 'WD_RC' and net(pad('C1', 2)) == net(pad('U1', 14)) == 'WD_C')
# SAFE_N end at U2.11 (P04 R2.2 R4-04, MECHANIKA)
u = pxy('U2', 11)
end = {'C18.1': round(math.dist(pxy('C18', 1), u), 2), 'R5.1': round(math.dist(pxy('R5', 1), u), 2), 'SAFE_N_copper_mm': cu_len('SAFE_N')}
check('SAFE_N ends at U2.11: C18 (1 nF) pad <= 5 mm, R5 (100 k) pad <= 16 mm, both SAFE_N / GND (P04 R2.2 R4-04)',
      net(pad('C18', 1)) == net(pad('R5', 1)) == 'SAFE_N' and net(pad('C18', 2)) == net(pad('R5', 2)) == 'GND' and end['C18.1'] <= 5 and end['R5.1'] <= 16, end)
# series resistors at their connector pins (P04 R2.2 R4-03 / R4-07; MECHANIKA): the connector-side net holds only the pin, the resistor pad
# and (where SERWIS.csv puts one) the service resistor; resistor pad <= 10 mm from the pin, copper of the net within the limit
# P04_3V3: J_BP2.14 is an even-row pin in the middle of the connector; its 0.4 mm escape rounds the connector end (route_critical.py), so R39
# stands 13 mm from the pin (limit 15) at the end of the locked escape
SER = [('PANEL_3V3', ('R40', 2), ('J_BP1', 2), 'R59', 25, 10), ('MECH_OK', ('R42', 1), ('J_BP1', 4), None, 15, 10), ('ARM_CONTACT', ('R3', 2), ('J_BP1', 8), None, 15, 10),
       ('TEST_KEY', ('R41', 1), ('J_BP1', 14), None, 15, 10), ('P04_3V3', ('R39', 2), ('J_BP2', 14), 'R60', 45, 15), ('PG_SEND', ('R38', 2), ('J_BP2', 20), 'R61', 30, 10)]
ser = {}
for n, (r, rp), (j, jp), sv, lim, dlim in SER:
    want = sorted([f'{r}.{rp}', f'{j}.{jp}'] + ([f'{sv}.1'] if sv else []))
    ser[n] = {'pads_on_net': sorted(f'{q.GetParentFootprint().GetReference()}.{q.GetNumber()}' for q in b.GetPads() if net(q) == n), 'want': want,
              'distance_mm': round(math.dist(pxy(r, rp), pxy(j, jp)), 2), 'distance_limit_mm': dlim, 'copper_mm': cu_len(n), 'limit_mm': lim}
check('Series resistors at their connector pins (P04 R2.2 R4-03 / R4-07, MECHANIKA): R40 PANEL_3V3, R42 MECH_OK, R3 ARM_CONTACT, R41 TEST_KEY at J_BP1, '
      'R39 P04_3V3 and R38 PG_SEND at J_BP2; the connector-side net holds only pin + resistor (+ its service resistor), pad <= 10 mm from the pin '
      '(R39 <= 15 mm: end of the P04_3V3 escape), copper within the limit',
      all(v['pads_on_net'] == v['want'] and v['distance_mm'] <= v['distance_limit_mm'] and v['copper_mm'] <= v['limit_mm'] for v in ser.values()), ser)
# SUP_N_OUT (reset from P03 R6, docs/KONTRAKT-RESET.md: edge <= 10 ns/V at U9.5; README): short, one via at most, GND pins beside it on J_BP3,
# GND reference under it (the other layer's GND pour under >= 70 % of its length), R17 at U9.5
gf = {L: [z.GetFilledPolysList(L) for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND' and z.IsOnLayer(L)] for L in (p.F_Cu, p.B_Cu)}
gref = [t for t in b.GetTracks() if net(t) == 'GND'] + [a for f_ in b.GetFootprints() for a in f_.Pads() if net(a) == 'GND']   # GND tracks / pads count as reference too (comb under J_BP3)
sn = tracks('SUP_N_OUT'); tot = 0.0; ref_ = 0.0
for t in sn:
    other = p.B_Cu if t.GetLayer() == p.F_Cu else p.F_Cu; s, e = pos(t.GetStart()), pos(t.GetEnd()); L_ = math.dist(s, e); n_ = max(1, int(L_ / .1))
    for k in range(n_):
        q = (s[0] + (e[0] - s[0]) * (k + .5) / n_, s[1] + (e[1] - s[1]) * (k + .5) / n_); tot += L_ / n_
        if any(ps.Contains(xy(*q)) for ps in gf[other]) or any(g.IsOnLayer(other) and g.HitTest(xy(*q)) for g in gref):
            ref_ += L_ / n_
supn = {'copper_mm': cu_len('SUP_N_OUT'), 'vias': len(tracks('SUP_N_OUT', True)), 'J_BP3.11/13': [net(pad('J_BP3', 11)), net(pad('J_BP3', 13))],
        'gnd_reference_percent': round(100 * ref_ / tot, 1) if tot else 0, 'U9.5_from_J_BP3.12_mm': round(math.dist(pxy('U9', 5), pxy('J_BP3', 12)), 2),
        'R17.1_from_U9.5_mm': round(math.dist(pxy('R17', 1), pxy('U9', 5)), 2), 'pads': sorted(f'{q.GetParentFootprint().GetReference()}.{q.GetNumber()}' for q in b.GetPads() if net(q) == 'SUP_N_OUT')}
check('SUP_N_OUT short and referenced to GND (KONTRAKT-RESET, README): copper <= 20 mm, <= 1 via, J_BP3.11 / .13 GND, GND pour on the other layer under >= 70 % '
      'of its length (pour, tracks or pads), U9.5 <= 10 mm and R17 <= 6 mm from it; net = J_BP3.12 + R17.1 + U9.5 only',
      supn['copper_mm'] <= 20 and supn['vias'] <= 1 and supn['J_BP3.11/13'] == ['GND', 'GND'] and supn['gnd_reference_percent'] >= 70
      and supn['U9.5_from_J_BP3.12_mm'] <= 10 and supn['R17.1_from_U9.5_mm'] <= 6 and supn['pads'] == ['J_BP3.12', 'R17.1', 'U9.5'], supn)
# decoupling: supply side on the copper, ground side through GND copper (P05 R3 review 2.10 method, src/gndpath.py)
from board import DEC_CAPS
dec = {}
for c, (u_, v_, g_) in DEC_CAPS.items():
    d = path_mm('3V3_IO', (u_, v_), (c, '1')) if net(pad(c, 1)) == '3V3_IO' else None
    dec[c] = {'ic_pin': f'{u_}.{v_}', 'supply_path_mm': d, 'straight_mm': round(math.dist(pxy(c, 1), pxy(u_, v_)), 2)}
check('Decoupling at the IC supply pins: 100 nF pad 1 (3V3_IO) <= 6 mm from the VCC pin on the copper (U1-U11, second 100 nF C15-C17 at U8-U10)',
      all(v['supply_path_mm'] is not None and v['supply_path_mm'] <= 6 for v in dec.values()), dec)
import gndpath
cu_, via_ = gndpath.copper(b, 'GND', W, H)
ret = {}
for c, (u_, v_, g_) in DEC_CAPS.items():
    src = gndpath.pad_point(b, c, '2'); dst = gndpath.pad_point(b, u_, g_)
    d = gndpath.distances(cu_, via_, src, {'d': dst}, limit_mm=150)['d']; st = round(math.dist(src[:2], dst[:2]), 1)
    ret[c] = {'to': f'{u_}.{g_}', 'path_mm': d, 'straight_mm': st, 'limit_mm': round(1.3 * st + 3, 1)}
check('Decoupling, ground side: capacitor GND pad -> GND pin of its IC through GND copper <= 1.3 x straight + 3 mm (gndpath.py; P05 R3 review 2.10 method)',
      all(v['path_mm'] is not None and v['path_mm'] <= v['limit_mm'] for v in ret.values()), ret)
# default-state resistors (MECHANIKA: R12-R22 on the connector side of the buffers, R25-R35 on the gate side)
DEF = {'R12': 'PWM', 'R13': 'HEARTBEAT', 'R14': 'MCU_ARM', 'R15': 'SENSOR_ENABLE', 'R16': 'CORE_LINK', 'R17': 'SUP_N_OUT', 'R18': 'PSU_OK', 'R19': 'DAQ_OK',
       'R20': 'DRIVE_OK', 'R21': 'SENSOR_OK', 'R22': 'PG_LINK'}
dfl = {}
for r, n in DEF.items():
    buf = next(q for f_ in b.GetFootprints() if f_.GetReference() in ('U8', 'U9', 'U10') for q in f_.Pads() if net(q) == n)
    dfl[r] = {'net': n, 'buffer_pin': f'{buf.GetParentFootprint().GetReference()}.{buf.GetNumber()}', 'mm': round(math.dist(pxy(r, 1), pos(buf.GetPosition())), 2)}
for r in [f'R{i}' for i in range(25, 36)]:
    n = net(pad(r, 1)); buf = next(q for f_ in b.GetFootprints() if f_.GetReference() in ('U8', 'U9', 'U10') for q in f_.Pads() if net(q) == n)
    dfl[r] = {'net': n, 'buffer_pin': f'{buf.GetParentFootprint().GetReference()}.{buf.GetNumber()}', 'mm': round(math.dist(pxy(r, 1), pos(buf.GetPosition())), 2)}
check('Default-state resistors at their buffers (MECHANIKA): R12-R22 (input side) and R25-R35 (output side) pad <= 12 mm from the U8-U10 pin',
      all(v['mm'] <= 12 for v in dfl.values()), dfl)
# ---------------- 7. GND ----------------
isl = {b.GetLayerName(L): sum(z.GetFilledPolysList(L).OutlineCount() for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND' and z.IsOnLayer(L)) for L in (p.F_Cu, p.B_Cu)}
cov = {b.GetLayerName(L): round(sum(z.GetFilledPolysList(L).Area() for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND' and z.IsOnLayer(L)) / 1e12 / (W * H) * 100, 1)
       for L in (p.F_Cu, p.B_Cu)}
check('GND pours on both layers: B.Cu >= 50 % of the board; island removal always (every island tied)', cov['B.Cu'] >= 50 and all(z.GetIslandRemovalMode() == p.ISLAND_REMOVAL_MODE_ALWAYS
      for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND') and len([z for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND']) == 2,
      {'cover_percent': cov, 'islands': isl})
# ---------------- 8. silkscreen ----------------
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
check('Every visible reference nearer its own part than any other (text centre to courtyard; P03 R6 review 1.10)', not blisko, blisko)
znaki = {}
for r_ in JBP_ZL + JSV_ZL:
    qx, qy = pxy(r_, '1')
    znaki[r_] = [s_ for s_, t in texts if s_ == '1' and math.dist((p.ToMM(t.GetPosition().x), p.ToMM(t.GetPosition().y)), (qx, qy)) <= 3.0]
check('Pin 1 of every connector (J_BP1..3, J_SV1..3) marked "1" on the silkscreen <= 3 mm from the pad (S1 §9)', all(len(v) == 1 for v in znaki.values()), znaki)
small = []
for t in [x for x in b.GetDrawings() if isinstance(x, p.PCB_TEXT)] + [x for f in b.GetFootprints() for x in [f.Reference(), f.Value()] + list(f.GraphicalItems()) if isinstance(x, p.PCB_TEXT)]:
    if t.GetLayer() in (p.F_SilkS, p.B_SilkS) and t.IsVisible() and (p.ToMM(t.GetTextHeight()) < 1.0 - 1e-6 or p.ToMM(t.GetTextThickness()) < .15 - 1e-6):
        small.append({'text': t.GetShownText(False), 'height': round(p.ToMM(t.GetTextHeight()), 3), 'line': round(p.ToMM(t.GetTextThickness()), 3), 'at': pos(t.GetPosition())})
check('Silkscreen legible: every visible text on F.SilkS / B.SilkS >= 1.0 mm high with a >= 0.15 mm line (JLCPCB legend minimum)', not small, small)
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
