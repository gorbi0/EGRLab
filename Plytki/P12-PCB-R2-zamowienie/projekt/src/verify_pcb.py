"""Independent checks of the finished P12 R2 PCB (full variant) (fresh native DRC with schematic parity + P12 rules). Structure of P10 R2 verify_pcb.py.
usage: KiCad Python verify_pcb.py [alternative_board] [report_dir]   (negative_controls.py passes copies with one defect each)
Expected values are NOT read from placement.py / silkscreen.py output:
- connector positions: Plytki/P12-przygotowanie/wyniki/zlacza-P12.csv (x of the stack, z of the board bottom) + 1.6 mm board + 4.45 mm
  axis of the angled IDC (README); J10 (P11) at the position fixed in the README (x 26.5, z 14.05);
- pin nets: docs/kontrakt-P12.json (generated from the board pinouts) and the schematic netlist;
- holes: board.py HOLES_XZ (README table), sizes from Plytki/Format-S1/format-s1.json;
- silkscreen texts: rebuilt here from the contract (label format of the README).
"""
from pathlib import Path
import pcbnew as p, json, sys, os, math, hashlib, csv, xml.etree.ElementTree as ET
from sexpr import parse, one, sub
from provenance import run_fresh_drc
sys.path.insert(0, str(Path(__file__).resolve().parent))
from board import NAME, REV, W, H, HOLES_XZ, kxy, xz, WIDTHS, SIGNAL_W
P = Path(__file__).resolve().parents[1]
path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else P / f'eda/{NAME}.kicad_pcb'
out = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else P / 'verification'
b = p.LoadBoard(str(path)); b.BuildConnectivity()
S1 = json.loads((P.parents[0] / 'Format-S1/format-s1.json').read_text(encoding='utf-8'))
K = json.loads((P / 'docs/kontrakt-P12.json').read_text(encoding='utf-8')); ZL = {z['ref']: z for z in K['zlacza']}
root = ET.parse(P / f'verification/{NAME}.xml').getroot(); parts = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
H_OSI, GR = 4.45, 1.6
GEO = {}
with open(P.parents[0] / 'P12-przygotowanie/wyniki/zlacza-P12.csv', encoding='utf-8-sig') as fh:
    for r in csv.DictReader(fh, delimiter=';'):
        if r['x_stos_mm']:
            GEO[(r['plytka'], r['zlacze'])] = (float(r['x_stos_mm']), float(r['z_spodu_plytki_mm']) + GR + H_OSI)
GEO[('P11 R2', 'J_P12')] = (26.5, 14.05)
TPW = {'TP1': 'GND', 'TP2': '5V_SYS', 'TP3': '3V3_IO', 'TP4': 'GND'}
checks = []; details = {}


def check(name, ok, detail=None):
    checks.append({'check': name, 'pass': bool(ok)})
    if detail is not None:
        details[name] = detail


def pos(v):
    return (round(p.ToMM(v.x), 4), round(p.ToMM(v.y), 4))


def xy(x, y):
    return p.VECTOR2I(p.FromMM(x), p.FromMM(y))


fmap = {f.GetReference(): f for f in b.GetFootprints()}
holes_ref = {r for r in fmap if r.startswith('H') and r[1:].isdigit()}


def pads(ref):
    return {a.GetNumber(): xz(*pos(a.GetPosition())) for a in fmap[ref].Pads() if a.GetNumber()}


# 1. DRC
drc, receipt = run_fresh_drc(path, out / 'drc.json')
check('Fresh native DRC: 0 violations / 0 unconnected / 0 schematic parity (all severities, zones refilled)',
      not drc['violations'] and not drc['unconnected_items'] and not drc['schematic_parity'],
      dict(receipt['counts'], types=sorted({v['type'] for v in drc['violations']})))
# 2. netlist
comps = {c.get('ref'): c for c in root.findall('./components/comp')}; pin = {}
for n in root.findall('./nets/net'):
    for q in n.findall('node'):
        pin[q.get('ref'), q.get('pin')] = n.get('name')
errors = []
for r in comps:
    if r not in fmap:
        errors.append(r + ' missing'); continue
    f = fmap[r]
    if f.GetFPIDAsString() != comps[r].findtext('footprint'):
        errors.append(r + ' footprint')
    for a in f.Pads():
        if a.GetNumber() and a.GetNetname() != pin.get((r, a.GetNumber()), ''):
            errors.append(f'{r}.{a.GetNumber()} net')
check(f'{len(comps)} parts of the netlist + {len(HOLES_XZ)} mounting holes, nothing else; every footprint ID and pad net equals the netlist',
      not errors and set(fmap) == set(comps) | holes_ref and len(holes_ref) == len(HOLES_XZ), errors[:20])
# 3. contract: pad nets of every connector, connector type
bad = []
for r, z in ZL.items():
    f = fmap.get(r)
    if f is None:
        bad.append(f'{r} missing'); continue
    n = z['n'] // 2
    if f.GetFPIDAsString() != f'Connector_IDC:IDC-Header_2x{n:02d}_P2.54mm_Vertical' or len([a for a in f.Pads() if a.GetNumber()]) != z['n'] or f.IsFlipped():
        bad.append(f'{r}: {f.GetFPIDAsString()} (contract {z["typ"]}, top side)')
    nc = {q['pin'] for q in K['niepodlaczone']}
    for a in f.Pads():
        k = f'{r}.{a.GetNumber()}'; want = z['piny'][a.GetNumber()]
        if (k in nc and not a.GetNetname().startswith('unconnected-')) or (k not in nc and a.GetNetname() != want):
            bad.append(f'{k}: {a.GetNetname()} (contract {want})')
check('Every connector: straight IDC of the contract type on the top side; every pad net = docs/kontrakt-P12.json (R2: no unconnected pin)', not bad and not K['niepodlaczone'], bad[:30])
# 4. geometry: centre of every connector (x, z) vs the geometry table, +-0.5 mm
geo = {}; bad = []
for r, z in ZL.items():
    q = pads(r); xs = [v[0] for v in q.values()]; zs = [v[1] for v in q.values()]
    c = ((min(xs) + max(xs)) / 2, (min(zs) + max(zs)) / 2); want = GEO[(z['plytka'], z['zlacze'])]
    d = math.dist(c, want); geo[r] = {'centre_xz': [round(c[0], 3), round(c[1], 3)], 'want_xz': [round(want[0], 3), round(want[1], 3)], 'error_mm': round(d, 3)}
    if d > .5:
        bad.append(r)
check('Connector centres (x of the stack, z above the floor) = zlacza-P12.csv x and z_bottom + 1.6 + 4.45 mm, within 0.5 mm (J10: x 26.5, z 14.05)', not bad, geo)
# 5. orientation: pin 1 at the smaller x, odd row lower, even row 2.54 above (straight ribbon, README)
bad = {}
for r, z in ZL.items():
    q = pads(r); m = z['n'] // 2
    odd = [q[str(2 * k + 1)] for k in range(m)]; even = [q[str(2 * k + 2)] for k in range(m)]
    ok = all(abs(odd[k][0] - (odd[0][0] + 2.54 * k)) < .01 and abs(odd[k][1] - odd[0][1]) < .01 for k in range(m)) and \
        all(abs(even[k][0] - odd[k][0]) < .01 and abs(even[k][1] - odd[k][1] - 2.54) < .01 for k in range(m))
    if not ok:
        bad[r] = {'pin1': odd[0], 'pin2': even[0], 'pin3': odd[1] if m > 1 else None}
check('Orientation of every connector: pin 1 at the smaller x, odd pins in one row along +x, pin 2k directly 2.54 mm ABOVE pin 2k-1 '
      '(odd row lower: mirror of the angled IDC on the boards, untwisted ribbon)', not bad, bad)
# 6. board, stackup, outline
check('2 copper layers, 1.6 mm', b.GetCopperLayerCount() == 2 and abs(p.ToMM(b.GetDesignSettings().GetBoardThickness()) - 1.6) < 1e-6)
stack = one(one(parse(path.read_text(encoding='utf-8')), 'setup'), 'stackup')
cu = {x[1]: float(one(x, 'thickness')[1]) for x in sub(stack, 'layer') if x[1] in ['F.Cu', 'B.Cu']}
check('Both copper layers 35 um', cu == {'F.Cu': .035, 'B.Cu': .035}, cu)
edge = [g for g in b.GetDrawings() if g.GetLayer() == p.Edge_Cuts]; arcs = [g for g in edge if g.GetShape() == p.SHAPE_T_ARC]
bb = b.GetBoardEdgesBoundingBox(); hw = max(p.ToMM(g.GetWidth()) for g in edge) / 2
box = [p.ToMM(bb.GetLeft()) + hw, p.ToMM(bb.GetTop()) + hw, p.ToMM(bb.GetRight()) - hw, p.ToMM(bb.GetBottom()) - hw]
check(f'Outline {W:g} x {H:g} mm (x 0..{W:g}, z {xz(0, H)[1]:g}..{xz(0, 0)[1]:g}), 4 corner arcs R 1', len(edge) == 8 and len(arcs) == 4 and all(abs(a - c) < 1e-3 for a, c in zip(box, [0, 0, W, H])), box)
# 7. holes and zones
want_h = sorted(kxy(x, z) for x, z in HOLES_XZ); got_h = sorted(pos(fmap[r].GetPosition()) for r in holes_ref)
hole_ok = all(list(fmap[r].Pads())[0].GetAttribute() == p.PAD_ATTRIB_NPTH and pos(list(fmap[r].Pads())[0].GetDrillSize()) == (3.2, 3.2) for r in holes_ref)
check(f'M3: {len(HOLES_XZ)} NPTH 3.2 mm at the README positions', hole_ok and len(got_h) == len(want_h) and all(math.dist(a, c) < .005 for a, c in zip(got_h, want_h)),
      {'want': want_h, 'got': got_h})
RZ = S1['otwory_M3']['strefa_dystansu_srednica'] / 2; near = set(); cop = []
for f in b.GetFootprints():
    if f.GetReference() in holes_ref:
        continue
    f.BuildCourtyardCaches(); cy = f.GetCourtyard(p.F_CrtYd)
    for hx, hy in want_h:
        circ = p.SHAPE_POLY_SET(); circ.NewOutline()
        for k in range(64):
            circ.Append(p.FromMM(hx + (RZ + 1.0) * math.cos(k * math.tau / 64)), p.FromMM(hy + (RZ + 1.0) * math.sin(k * math.tau / 64)))
        x_ = p.SHAPE_POLY_SET(cy); x_.BooleanIntersection(circ)
        if x_.Area() > 0:
            near.add((f.GetReference(), (hx, hy)))
for hx, hy in want_h:
    c = xy(hx, hy)
    for t in b.GetTracks():
        if t.HitTest(c, p.FromMM(RZ)):
            cop.append((t.GetNetname(), (hx, hy)))
    for f in b.GetFootprints():
        if f.GetReference() not in holes_ref:
            for a in f.Pads():
                if a.HitTest(c, p.FromMM(RZ)):
                    cop.append((f'{f.GetReference()}.{a.GetNumber()}', (hx, hy)))
    for z in b.Zones():
        if not z.GetIsRuleArea():
            for L in (p.F_Cu, p.B_Cu):
                if z.IsOnLayer(L):
                    ps = z.GetFilledPolysList(L)
                    if ps.Contains(c) or any(ps.Contains(xy(hx + (RZ - .01) * math.cos(k * math.tau / 32), hy + (RZ - .01) * math.sin(k * math.tau / 32))) for k in range(32)):
                        cop.append((f'zone {z.GetNetname()} {b.GetLayerName(L)}', (hx, hy)))
rules_ok = sum(1 for z in b.Zones() if z.GetIsRuleArea() and z.GetZoneName().startswith('M3 ') and z.GetDoNotAllowTracks() and z.GetDoNotAllowVias()
               and z.GetDoNotAllowZoneFills() and set(z.GetLayerSet().Seq()) == {p.F_Cu, p.B_Cu})
check('Standoff zones D7: no copper within 3.5 mm of a hole centre; courtyards >= 1 mm outside the zone (screw head, ribbon sockets); rule areas on both layers',
      not near and not cop and rules_ok == len(want_h), {'courtyards': sorted(map(str, near)), 'copper': sorted(map(str, cop)), 'rule_areas': rules_ok})
# 8. rules and widths
pro = json.loads((P / f'eda/{NAME}.kicad_pro').read_text()); ds = pro['board']['design_settings']; rules = ds['rules']
cls = {c['name']: c for c in pro['net_settings']['classes']}; pat = {q['pattern']: q['netclass'] for q in pro['net_settings']['netclass_patterns']}
check('Rules: clearance >= 0.25, edge 0.5, ring 0.25, silk text >= 1.0 / 0.15 mm, no DRC exclusions; class PWR (5V_SYS) 1.0 mm, P3V3 (3V3_IO) 0.5 mm',
      rules['min_clearance'] >= .25 and rules['min_copper_edge_clearance'] >= .5 and rules['min_via_annular_width'] >= .25 and rules['min_text_height'] >= 1.0
      and rules['min_text_thickness'] >= .15 and not ds['drc_exclusions'] and cls['PWR']['track_width'] >= 1.0 and cls['P3V3']['track_width'] >= .5
      and pat.get('5V_SYS') == 'PWR' and pat.get('3V3_IO') == 'P3V3')
wid = {}
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        continue
    wid.setdefault(t.GetNetname(), set()).add(round(p.ToMM(t.GetWidth()), 3))
low = {n: sorted(v) for n, v in wid.items() if min(v) < WIDTHS.get(n, .25) - 1e-6}
check('Track widths: 5V_SYS >= 1.0 mm, 3V3_IO >= 0.5 mm, every other track >= 0.25 mm', not low and '5V_SYS' in wid and '3V3_IO' in wid,
      {'too_narrow': low, '5V_SYS': sorted(wid.get('5V_SYS', [])), '3V3_IO': sorted(wid.get('3V3_IO', []))})
ring = [f'{f.GetReference()}.{a.GetNumber()}' for f in b.GetFootprints() for a in f.Pads() if a.GetAttribute() == p.PAD_ATTRIB_PTH
        and (min(p.ToMM(a.GetSize(p.F_Cu).x), p.ToMM(a.GetSize(p.F_Cu).y)) - p.ToMM(a.GetDrillSize().x)) / 2 < .25 - 1e-6]
ring += [f'via {pos(t.GetPosition())}' for t in b.GetTracks() if isinstance(t, p.PCB_VIA) and (p.ToMM(t.GetWidth(p.F_Cu)) - p.ToMM(t.GetDrill())) / 2 < .25 - 1e-6]
check('Every PTH pad and via has an annular ring >= 0.25 mm', not ring, ring[:20])
# 9. power separation: 5V_SYS / 3V3_IO / GND, P03 J_BP2 vs P05 J_BP2 pins 16/17/19/20 (connected by net only, never pin to pin)
con = b.GetConnectivity(); sep = {}
for n in ('16', '17', '19', '20'):
    a = next(q for q in fmap['J3'].Pads() if q.GetNumber() == n); c_ = next(q for q in fmap['J6'].Pads() if q.GetNumber() == n)
    ids = {x.m_Uuid.AsString() for x in con.GetConnectedItems(a)}
    sep[n] = {'J3': a.GetNetname(), 'J6': c_.GetNetname(), 'copper_path': c_.m_Uuid.AsString() in ids}
shorts = [v for v in drc['violations'] if v['type'] in ('shorting_items', 'tracks_crossing', 'clearance')]
check('5V_SYS, 3V3_IO and GND separate (no DRC short); P03 J_BP2 16/17/19/20 (PFAIL_N, 5V_SYS) and P05 J_BP2 16/17/19/20 (GND) without a copper path',
      not shorts and all(v['J3'] != v['J6'] and not v['copper_path'] for v in sep.values()) and sep['17']['J3'] == '5V_SYS' and sep['17']['J6'] == 'GND',
      {'pairs': sep, 'short_violations': len(shorts)})
# 10. 5V_SYS path from the source: every 5V_SYS pad reaches P02 J_BP (J1.2/4/6) over copper
src = next(q for q in fmap['J1'].Pads() if q.GetNumber() == '2'); ids = {x.m_Uuid.AsString() for x in con.GetConnectedItems(src)}
miss = [f'{f.GetReference()}.{a.GetNumber()}' for f in b.GetFootprints() for a in f.Pads() if a.GetNetname() in ('5V_SYS',) and a.m_Uuid.AsString() not in ids and a is not src]
src3 = next(q for q in fmap['J1'].Pads() if q.GetNumber() == '8'); ids3 = {x.m_Uuid.AsString() for x in con.GetConnectedItems(src3)}
miss += [f'{f.GetReference()}.{a.GetNumber()}' for f in b.GetFootprints() for a in f.Pads() if a.GetNetname() == '3V3_IO' and a.m_Uuid.AsString() not in ids3 and a is not src3]
check('Every 5V_SYS / 3V3_IO pad joined over copper to the source P02 J_BP (J1.2 / J1.8)', not miss, miss)
# 10a. R2: 5V_SYS budget of the full stack (P12-przygotowanie/wyniki/kontrakty.json, budgets from the board documents) vs the source
KON = json.loads((P.parents[0] / 'P12-przygotowanie/wyniki/kontrakty.json').read_text(encoding='utf-8'))
I5 = KON['suma_5V_pelny_mA'] / 1000; w5 = min(wid.get('5V_SYS', {0}))
ipc = .048 * 10 ** .44 * (w5 / .0254 * .035 / .0254) ** .725      # IPC-2221 outer layer, 35 um, dT 10 K [A]
n5 = sum(1 for a in fmap['J1'].Pads() if a.GetNetname() == '5V_SYS')
check('5V_SYS budget of the full stack <= 1.8 A (90 % of TSR 2-2450), <= 1 A per source contact, narrowest 5V_SYS track carries it (IPC-2221, outer, 10 K)',
      I5 <= 1.8 and I5 <= n5 * 1.0 and ipc >= I5, {'budget_A': I5, 'per_board_mA': KON['budzet_5V_mA'], 'source_contacts': n5,
                                                 'narrowest_5V_SYS_mm': w5, 'ipc2221_A': round(ipc, 2)})
# 11. GND
gz = [z for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND']
cov = {b.GetLayerName(L): round(sum(z.GetFilledPolysList(L).Area() for z in gz if z.IsOnLayer(L)) / 1e12 / (W * H) * 100, 1) for L in (p.F_Cu, p.B_Cu)}
nst = sum(1 for t in b.GetTracks() if isinstance(t, p.PCB_VIA) and t.GetNetname() == 'GND')
check('GND pours on both layers (each >= 50 % of the board, island removal always) and >= 20 GND stitching vias', len(gz) == 2 and all(v >= 50 for v in cov.values())
      and all(z.GetIslandRemovalMode() == p.ISLAND_REMOVAL_MODE_ALWAYS for z in gz) and nst >= 20, {'cover_percent': cov, 'gnd_vias': nst})
# 12. test pads
ok = all(list(fmap[t].Pads())[0].GetNetname() == s for t, s in TPW.items())
check('Test pads TP1 / TP4 GND, TP2 5V_SYS, TP3 3V3_IO', ok, {t: list(fmap[t].Pads())[0].GetNetname() for t in TPW})
# 13. silkscreen
texts = [(t.GetText(), t) for t in b.GetDrawings() if isinstance(t, p.PCB_TEXT) and t.GetLayer() == p.F_SilkS]
small = [(s, round(p.ToMM(t.GetTextHeight()), 2), round(p.ToMM(t.GetTextThickness()), 2)) for s, t in
         [(t.GetText(), t) for t in b.GetDrawings() if isinstance(t, p.PCB_TEXT)] if p.ToMM(t.GetTextHeight()) < 1.0 - 1e-6 or p.ToMM(t.GetTextThickness()) < .15 - 1e-6]
check('Every silkscreen text >= 1.0 mm high and >= 0.15 mm stroke (JLCPCB)', not small and texts, small)


def want_label(z):
    if z['poziom'] == 'panel':
        return f"{z['ref']}  P11 J_P12 (panel, tasma z P11)"
    return f"{z['ref']}  {z['plytka'].split()[0]} {z['zlacze']} (poziom {z['poziom']}, {z['slot']})"


bad = {}; cour = {}
for f in b.GetFootprints():
    if f.GetReference() not in holes_ref:
        f.BuildCourtyardCaches(); cour[f.GetReference()] = f.GetCourtyard(p.F_CrtYd)
for r, z in ZL.items():
    q = pads(r); xs = [v[0] for v in q.values()]; cx = (min(xs) + max(xs)) / 2; ztop = max(v[1] for v in q.values())
    lab = [t for s, t in texts if s == want_label(z)]
    if len(lab) != 1:
        bad[r] = f'{len(lab)} labels "{want_label(z)}"'; continue
    lx, lz = xz(*pos(lab[0].GetPosition()))
    if abs(lx - cx) > 3 or not (ztop < lz < ztop + 9):
        bad[r] = f'label at x {lx:.1f}, z {lz:.1f} (connector x {cx:.1f}, top row z {ztop:.1f})'
    last = q[str(z['n'] - 1)]
    one_ = [t for s, t in texts if s == '1' and math.dist(xz(*pos(t.GetPosition())), q['1']) <= 7.5
            and math.dist(xz(*pos(t.GetPosition())), q['1']) < math.dist(xz(*pos(t.GetPosition())), last)]
    if len(one_) != 1:
        bad[r + ' pin1'] = f'{len(one_)} marks "1" near pin 1'
check('Every connector: one label "Jn  Pxx <connector> (poziom k, Sx)" centred above it and one "1" mark <= 7.5 mm from pin 1, nearer pin 1 than the last odd pin', not bad, bad)
ins = {}
alltexts = [(t.GetText(), t) for t in b.GetDrawings() if isinstance(t, p.PCB_TEXT) and t.GetLayer() in (p.F_SilkS, p.B_SilkS)]
for s, t in alltexts:
    r_ = t.GetBoundingBox(); x0, y0, x1, y1 = p.ToMM(r_.GetLeft()), p.ToMM(r_.GetTop()), p.ToMM(r_.GetRight()), p.ToMM(r_.GetBottom())
    smp = [(x0 + (x1 - x0) * i / 6, y0 + (y1 - y0) * j / 2) for i in range(7) for j in range(3)]
    hit = sorted({r for r, cy in cour.items() for q in smp if t.GetLayer() == p.F_SilkS and cy.Contains(xy(*q))})
    hit += [f'M3 zone {h}' for h in want_h if max(x0 - h[0], 0, h[0] - x1) ** 2 + max(y0 - h[1], 0, h[1] - y1) ** 2 < RZ ** 2]
    if hit or x0 < .3 or y0 < .3 or x1 > W - .3 or y1 > H - .3:
        ins[s] = hit or 'outside the board'
check('No silkscreen text (top or bottom) inside a connector / pad courtyard (stays visible next to a mated socket), in an M3 zone D7 or off the board', not ins, ins)
title = [s for s, t in texts if s == f'{REV} S1 PELNY']
check(f'Silkscreen: board name "{REV} S1 PELNY" and orientation marks (STRONA STOSU, x = 0 PANEL)', bool(title) and any('STRONA STOSU' in s for s, _ in texts)
      and any(s.startswith('x = 0') for s, _ in texts), title)

res = {'board': str(path), 'board_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'checks': checks, 'details': details,
       'passed': sum(c['pass'] for c in checks), 'total': len(checks)}
out.mkdir(parents=True, exist_ok=True)
(out / 'pcb-checks.json').write_text(json.dumps(res, indent=2, ensure_ascii=False, default=str) + '\n', encoding='utf-8')
for c in checks:
    print('PASS' if c['pass'] else 'FAIL', c['check'])
print(f"{res['passed']}/{res['total']} PCB checks passed")
sys.exit(0 if res['passed'] == res['total'] else 1)
