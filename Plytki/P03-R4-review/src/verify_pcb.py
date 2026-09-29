"""Independent checks of the finished P03 R4 PCB (fresh native DRC + P03-specific rules).
usage: KiCad Python verify_pcb.py [alternative_board] [report_dir]
The alternative board is used by negative_controls.py (copies with a deliberate defect).
Rules come from docs/ZALOZENIA-P03-R2.md and docs/MECHANIKA.md; generic parts taken over from P02/P00 R1.
"""
from pathlib import Path
import pcbnew as p, json, sys, math, hashlib, collections, heapq, xml.etree.ElementTree as ET
from sexpr import parse, one, sub
from provenance import run_fresh_drc
P = Path(__file__).resolve().parents[1]
path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else P / 'eda/P03.kicad_pcb'
out = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else P / 'verification'
b = p.LoadBoard(str(path)); b.BuildConnectivity()
root = ET.parse(P / 'verification/P03.xml').getroot(); parts = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
W, H = 160, 120; HOLES = [(5, 5), (W - 5, 5), (5, H - 5), (W - 5, H - 5), (W - 5, 38)]
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


def fp2board(f, x, y):
    a = math.radians(f.GetOrientationDegrees()); c = f.GetPosition()
    return (p.ToMM(c.x) + x * math.cos(a) + y * math.sin(a), p.ToMM(c.y) - x * math.sin(a) + y * math.cos(a))


def cbox(r):
    f = fmap[r]; f.BuildCourtyardCaches(); bb = f.GetCourtyard(p.F_CrtYd).BBox()
    return (p.ToMM(bb.GetLeft()), p.ToMM(bb.GetTop()), p.ToMM(bb.GetRight()), p.ToMM(bb.GetBottom()))


def rdist(c, bx):
    return math.hypot(max(bx[0] - c[0], 0, c[0] - bx[2]), max(bx[1] - c[1], 0, c[1] - bx[3]))


def overlap(a, c):
    return min(a[2], c[2]) > max(a[0], c[0]) and min(a[3], c[3]) > max(a[1], c[1])


def zone_rect(z):
    bb = z.Outline().BBox(); return (p.ToMM(bb.GetLeft()), p.ToMM(bb.GetTop()), p.ToMM(bb.GetRight()), p.ToMM(bb.GetBottom()))


def edge_dist(bx):
    return {'T': bx[1], 'B': H - bx[3], 'L': bx[0], 'R': W - bx[2]}


# ---------------- 1. native DRC ----------------
drc, receipt = run_fresh_drc(path, out / 'drc.json')
check('Fresh native DRC: 0 violations / 0 unconnected / 0 schematic parity (all severities)',
      not drc['violations'] and not drc['unconnected_items'] and not drc['schematic_parity'], receipt['counts'])
# ---------------- 2. netlist, parts, geometry ----------------
comps = {c.get('ref'): c for c in root.findall('./components/comp')}
check('91 parts + 5 mounting holes, nothing else', len(comps) == 91 and set(fmap) == set(comps) | {f'H{i}' for i in range(1, 6)} and set(parts) == set(comps))
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
check('Closed rectangular outline 160 x 120 mm (P01/P02 format)', len(edge) == 4 and pts == {(0, 0), (W, 0), (W, H), (0, H)})
holes = []
for i, q in enumerate(HOLES, 1):
    a = list(fmap[f'H{i}'].Pads())[0]
    holes.append(pos(fmap[f'H{i}'].GetPosition()) == q and a.GetAttribute() == p.PAD_ATTRIB_NPTH and pos(a.GetDrillSize()) == (3.2, 3.2))
keep = [z for z in b.Zones() if z.GetIsRuleArea()]
mount = [z for z in keep if z.GetZoneName().startswith('M3 ')]


def full_keepout(z):
    return set(z.GetLayerSet().Seq()) == {p.F_Cu, p.B_Cu} and z.GetDoNotAllowTracks() and z.GetDoNotAllowVias() and z.GetDoNotAllowZoneFills()


check('Five NPTH 3.2 mm holes: the four P01/P02 corners + H5 (155, 38) next to the DAQ socket; copper keepouts on both layers',
      all(holes) and len(mount) == 5 and all(full_keepout(z) for z in mount), {'holes_ok': holes})
near = {}
for f in b.GetFootprints():
    if f.GetReference().startswith('H'):
        continue
    f.BuildCourtyardCaches(); cy = f.GetCourtyard(p.F_CrtYd)
    for h in HOLES:
        d = p.ToMM(cy.SquaredDistance(xy(*h)) ** .5) if not cy.Contains(xy(*h)) else 0
        if d < 4.5:
            near[f.GetReference()] = round(d, 2)
check('No courtyard within 4.5 mm of a mounting-hole centre (screw head + washer)', not near, near)
pro = json.loads((P / 'eda/P03.kicad_pro').read_text()); ds = pro['board']['design_settings']; rules = ds['rules']
cls = {c['name']: c for c in pro['net_settings']['classes']}; pats = {x['pattern']: x['netclass'] for x in pro['net_settings']['netclass_patterns']}
check('Explicit DRC rules and net classes active (Default 0.30/0.25, Power 0.60/0.30 for 5V_SYS, 3V3_CORE, 3V3_IO); no DRC exclusions',
      rules['min_clearance'] >= .25 and rules['min_track_width'] >= .3 and rules['min_silk_clearance'] >= .15 and rules['min_copper_edge_clearance'] >= .5
      and not ds['drc_exclusions'] and cls['Default']['clearance'] >= .25 and cls['Default']['track_width'] >= .3 and cls['Power']['track_width'] >= .6
      and cls['Power']['clearance'] >= .3 and pats == {'5V_SYS': 'Power', '5V_M1': 'Power', '3V3_CORE': 'Power', '3V3_IO': 'Power'}, {'classes': list(cls), 'patterns': pats})


def sig(t):
    if isinstance(t, p.PCB_VIA):
        return ('via', t.GetNetname(), pos(t.GetPosition()), p.ToMM(t.GetWidth(p.F_Cu)), p.ToMM(t.GetDrill()))
    return ('track', t.GetNetname(), tuple(sorted([pos(t.GetStart()), pos(t.GetEnd())])), p.ToMM(t.GetWidth()), int(t.GetLayer()))


# R4: the copper locked by route_critical.py (routing/critical-routed.kicad_pcb); the R3 copper seeded after it is unlocked
# again before the clean-up (as router copper in R3) and compared with R3 by check_revision.py.
pre = p.LoadBoard(str(P / 'routing/critical-routed.kicad_pcb'))
need = collections.Counter(sig(t) for t in pre.GetTracks()); have = collections.Counter(sig(t) for t in b.GetTracks())
missing = list((need - have).elements())
check('Every pre-routed (locked) segment and via retained with its width and layer (5V_SYS feed 1.0 mm, decoupling stubs, capacitor GND vias, R4 buffer copper)', not missing and need,
      {'missing': [list(map(str, m)) for m in missing], 'locked_items': sum(need.values())})
widths = collections.defaultdict(lambda: 99.0)
for t in b.GetTracks():
    if not isinstance(t, p.PCB_VIA):
        widths[net(t)] = min(widths[net(t)], p.ToMM(t.GetWidth()))
pw = {n: widths[n] for n in ('5V_SYS', '5V_M1', '3V3_CORE', '3V3_IO')}
check('Supply nets: branches >= 0.6 mm; locked main feed remains 1.0 mm', all(w >= .6 for w in pw.values()), pw)


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
    for L, s, e, t in segs:
        for n in list(g):
            if n[0] == L and n[1] not in (s, e) and t.HitTest(xy(*n[1])):
                for q in (s, e):
                    d = math.dist(n[1], q); g[n].append(((L, q), d)); g[(L, q)].append((n, d))
    for f in b.GetFootprints():
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


# ---------------- 3. P03 function and mechanics ----------------
m1 = fmap['M1']; j1r = [pxy('M1', f'J1-{i}') for i in range(1, 23)]; j3r = [pxy('M1', f'J3-{i}') for i in range(1, 23)]
usb_y = fp2board(m1, 11.43, 56.5)[1]; ant = [fp2board(m1, x, y) for x, y in [(-1.32, -8.0), (24.18, -1.5)]]
geo = {'row_distance_mm': round(math.dist(j1r[0], j3r[0]), 3), 'J1_column_x': j1r[0][0], 'J3_column_x': j3r[0][0], 'usb_end_y_mm': round(usb_y, 2),
       'pitch_ok': all(abs(math.dist(j1r[i], j1r[i + 1]) - 2.54) < 1e-3 and abs(math.dist(j3r[i], j3r[i + 1]) - 2.54) < 1e-3 for i in range(21))}
check('M1 Waveshare: two 1x22 rows 22.86 mm apart (J1 row towards the board, J3 row at the left), USB-C end at the top edge (<= 0.5 mm)',
      abs(geo['row_distance_mm'] - 22.86) < 1e-3 and geo['pitch_ok'] and geo['J1_column_x'] > geo['J3_column_x'] and 0 <= usb_y <= .5, geo)
az = [z for z in keep if z.GetZoneName() == 'ANTENNA M1']
exp = (min(a[0] for a in ant) - 3, min(a[1] for a in ant), max(a[0] for a in ant) + 3, max(a[1] for a in ant) + 8)
ar = zone_rect(az[0]) if az else None
inside = sorted(r for r in fmap if r not in ('M1',) and not r.startswith('H') and ar and overlap(cbox(r), ar))


def seg_rect(a, c, r):
    """Distance between segment a-c and the axis-aligned rectangle r (0 if they touch or cross)."""
    inside = lambda q: r[0] <= q[0] <= r[2] and r[1] <= q[1] <= r[3]
    if inside(a) or inside(c):
        return 0.0
    corners = [(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])]

    def cross(p1, p2, p3, p4):
        d = lambda u, v, w: (w[0] - u[0]) * (v[1] - u[1]) - (w[1] - u[1]) * (v[0] - u[0])
        return d(p3, p4, p1) * d(p3, p4, p2) < 0 and d(p1, p2, p3) * d(p1, p2, p4) < 0
    if any(cross(a, c, corners[i], corners[(i + 1) % 4]) for i in range(4)):
        return 0.0

    def pd(q, u, v):
        dx, dy = v[0] - u[0], v[1] - u[1]; L = dx * dx + dy * dy
        t = 0 if L == 0 else max(0, min(1, ((q[0] - u[0]) * dx + (q[1] - u[1]) * dy) / L))
        return math.dist(q, (u[0] + t * dx, u[1] + t * dy))
    return min([pd(q, a, c) for q in corners] + [pd(q, corners[i], corners[(i + 1) % 4]) for q in (a, c) for i in range(4)])


copper = []
for t in (b.GetTracks() if ar else []):
    if isinstance(t, p.PCB_VIA):
        q = pos(t.GetPosition())
        if seg_rect(q, q, ar) < p.ToMM(t.GetWidth(p.F_Cu)) / 2:
            copper.append(t)
    elif seg_rect(pos(t.GetStart()), pos(t.GetEnd()), ar) < p.ToMM(t.GetWidth()) / 2:
        copper.append(t)
fills = {b.GetLayerName(L): sum(1 for z in b.Zones() if not z.GetIsRuleArea() and z.IsOnLayer(L) and ar and
                                 z.GetFilledPolysList(L).Collide(p.SHAPE_RECT(xy(ar[0] + .05, ar[1] + .05), p.FromMM(ar[2] - ar[0] - .1), p.FromMM(ar[3] - ar[1] - .1))))
         for L in (p.F_Cu, p.B_Cu)}
check('ANTENNA keepout: M1 antenna end + 3 mm sides + 8 mm beyond, both layers, no track / via / pour; no other part inside',
      len(az) == 1 and full_keepout(az[0]) and all(abs(u - v) < .01 for u, v in zip(ar, exp)) and not inside and not copper and not any(fills.values()),
      {'rule_area': ar and [round(v, 2) for v in ar], 'expected': [round(v, 2) for v in exp], 'parts_inside': inside, 'copper_items_inside': len(copper),
       'pour_inside': fills})
j1 = fmap['J1']; face = fp2board(j1, -12.63, 0)[0]; jc = (p.ToMM(j1.GetPosition().x), (pxy('J1', '1')[1] + pxy('J1', '15')[1]) / 2)
hd = {h: round(math.dist(jc, HOLES[i]), 1) for i, h in [(1, 'H2'), (4, 'H5')]}
jj = {'orientation': j1.GetOrientationDegrees(), 'face_x_mm': round(face, 2), 'pin1': pxy('J1', '1'), 'pin15': pxy('J1', '15'), 'holes_to_centre_mm': hd,
      'pin2_net': net(pad('J1', '2'))}
check('J1 DAQ (right-angle 2x8 socket to P05): mating face 0-0.5 mm inside the right edge; H2 and H5 on both sides within 25 mm; key position 2 NC',
      abs(abs(jj['orientation']) - 180) < 1e-6 and W - .5 <= face <= W and hd['H2'] <= 25 and hd['H5'] <= 25 and HOLES[1][1] < jc[1] < HOLES[4][1]
      and jj['pin2_net'].startswith('unconnected'), jj)
IDC = {'J2': ('ILOG', '2'), 'J3': ('ITEST', '2'), 'J4': ('SAFE', '4'), 'J5': ('DIR', '4'), 'J6': ('SFAULT', '3'), 'J7': ('TEMP', '4'), 'J8': ('CAN', '4')}
idc = {}
for r, (nm, key) in IDC.items():
    bx = cbox(r); ed = edge_dist(bx); e = min(ed, key=ed.get); odd = pxy(r, '1'); even = pxy(r, '2')
    along = (odd[0] != pxy(r, '3')[0]) if e in 'TB' else (odd[1] != pxy(r, '3')[1])
    inner = {'T': odd[1] > even[1], 'B': odd[1] < even[1], 'L': odd[0] > even[0], 'R': odd[0] < even[0]}[e]
    idc[r] = {'name': nm, 'edge': e, 'edge_gap_mm': round(ed[e], 2), 'long_axis_along_edge': along, 'signal_row_inner': inner,
              'key_pin_nc': net(pad(r, key)).startswith('unconnected')}
check('IDC box headers J2..J8: at an edge (courtyard <= 0.5 mm), long axis along it, odd (signal) row inside, key pin NC (v6.1 keys)',
      all(v['edge_gap_mm'] <= .5 and v['long_axis_along_edge'] and v['signal_row_inner'] and v['key_pin_nc'] for v in idc.values()), idc)
bx = cbox('J9'); ed = edge_dist(bx); j9 = {'edge': min(ed, key=ed.get), 'edge_gap_mm': round(min(ed.values()), 2), 'pin6': net(pad('J9', '6'))}
check('J9 PANELCORE (Mini-Fit Jr 8p) at an edge (<= 0.5 mm), position 6 NC', j9['edge_gap_mm'] <= .5 and j9['pin6'].startswith('unconnected'), j9)
sd = fmap['SD1']; card = [fp2board(sd, x, y) for x, y in [(0, -22.86), (20.32, -22.86)]]
cd = min(min(q[0], W - q[0], q[1], H - q[1]) for q in card); sdz = [z for z in keep if z.GetZoneName().startswith('SD1 M2.5')]
sdh = [pos(a.GetPosition()) for a in sd.Pads() if a.GetAttribute() == p.PAD_ATTRIB_NPTH]
check('SD1 Adafruit 4682: card end at a board edge (card tip <= 0.6 mm inside), M2.5 stand-off keepouts r 3 mm around both holes, both layers',
      cd <= .6 and len(sdz) == 2 and all(full_keepout(z) for z in sdz) and
      sorted(tuple(round(p.ToMM(v), 2) for v in (z.Outline().BBox().GetCenter().x, z.Outline().BBox().GetCenter().y)) for z in sdz) == sorted(tuple(round(v, 2) for v in h) for h in sdh),
      {'card_tip_to_edge_mm': round(cd, 2), 'holes': sdh})
f = fmap['J10']; pwp = [pos(a.GetPosition()) for a in f.Pads() if a.GetNumber()]; an = [pos(a.GetPosition()) for a in f.Pads() if not a.GetNumber()]
dx, dy = pwp[-1][0] - pwp[0][0], pwp[-1][1] - pwp[0][1]; nn = math.hypot(dx, dy)
dist = [round(abs(dx * (q[1] - pwp[0][1]) - dy * (q[0] - pwp[0][0])) / nn, 3) for q in an]
edge_pad = min(min(q[0], W - q[0], q[1], H - q[1]) for q in pwp); edge_anc = min(min(q[0], W - q[0], q[1], H - q[1]) for q in an)
tz = [z for z in keep if z.GetZoneName() == 'LV03 TIE']; tr_ = zone_rect(tz[0]) if tz else None
tie_ok = tz and full_keepout(tz[0]) and all(tr_[0] < q[0] < tr_[2] and tr_[1] < q[1] < tr_[3] for q in an)
lv = {k: net(pad('J10', k)) for k in '1234'}
under = {}
for k in '1234':  # the test pad right under each LV03 pad carries the same net (its legend reads as the LV03 pinout)
    q = pxy('J10', k); tp = min((r for r in fmap if r.startswith('TP')), key=lambda r: math.dist(pxy(r, '1'), q))
    under[k] = {'tp': tp, 'dx_mm': round(abs(pxy(tp, '1')[0] - q[0]), 2), 'same_net': net(pad(tp, '1')) == lv[k]}
check('J10 LV03 pigtail: 1=5V_SYS 2=GND 3=3V3_IO 4=GND; anchors 12.5 mm from the solder row towards the edge; no copper under the tie band; '
      'the test pad under each LV03 pad has its net',
      lv == {'1': '5V_SYS', '2': 'GND', '3': '3V3_IO', '4': 'GND'} and all(abs(x - 12.5) < .001 for x in dist) and edge_anc < edge_pad and tie_ok
      and all(v['dx_mm'] < .01 and v['same_net'] for v in under.values()),
      {'pins': lv, 'anchor_to_row_mm': dist, 'anchors_on_edge_side': edge_anc < edge_pad, 'tie_rule_area': tr_ and [round(v, 2) for v in tr_], 'test_pads': under})
DEC = [('C5', 'U11', '14'), ('C6', 'U12', '14'), ('C7', 'U13', '14'), ('C8', 'U14', '14'), ('C9', 'U21', '14'), ('C10', 'U22', '14'), ('C11', 'U23', '14'),
       ('C2', 'U1', '9'), ('C1', 'U2', '16'), ('C3', 'U3', '6'), ('C12', 'U4', '5'), ('C15', 'U6', '5')]
dd = {}
for c, u, un in DEC:
    dd[f'{c}-{u}.{un}'] = {'straight_mm': round(math.dist(pxy(c, '1'), pxy(u, un)), 2), 'routed_mm': route('3V3_CORE', (c, '1'), (u, un)),
                           'gnd_pad_mm': round(math.dist(pxy(c, '2'), pxy(u, {'U1': '10', 'U2': '8', 'U3': '2', 'U4': '3', 'U6': '3'}.get(u, '7'))), 2)}
check('100 nF at every IC: <= 8 mm straight and <= 20 mm routed to the VCC pin (74LVC125 pin 14, MCP23017 pin 9, 74HC139 pin 16, TPS3808 VDD, LVC1G07/1G17 pin 5)',
      all(v['straight_mm'] <= 8 and v['routed_mm'] is not None and v['routed_mm'] <= 20 for v in dd.values()), dd)
# R2: source termination must remain close to the active driver, before the long trace.
terms={}
for r,u,pn,n in [('R36','U21','6','ADC_SCLK_DRV'),('R37','U21','11','ADC_CONVST_DRV'),
                 ('R38','U23','3','SPI3_SCLK_DRV'),('R39','U21','8','ADC_SDI_DRV'),('R40','U23','6','SPI3_MOSI_DRV')]:
    terms[r]={'straight_mm':round(math.dist(pxy(r,'1'),pxy(u,pn)),2),'routed_mm':route(n,(r,'1'),(u,pn))}
check('Source termination: <=12 mm straight and <=20 mm routed from buffer',
      all(x['straight_mm']<=12 and x['routed_mm'] is not None and x['routed_mm']<=20 for x in terms.values()),terms)
# Independent physical-pin fact: TPS3808DBV VDD is pin 6, MR is pin 3 (TI SBVS050).
# Deliberately not loaded from generator route_critical.py or a shared DEC list.
vdd_dist=math.dist(pxy('U3','6'),pxy('C3','1'));mr_dist=math.dist(pxy('U3','3'),pxy('C3','1'))
check('TPS3808 C3 is at VDD 6, not MR 3',net(pad('U3','6'))=='3V3_CORE' and vdd_dist<=8 and vdd_dist<mr_dist,
      {'C3_to_VDD6_mm':round(vdd_dist,3),'C3_to_MR3_mm':round(mr_dist,3)})
# R4: the Schmitt buffer sits at J4, so SUP_N keeps its slow edge on the long run and only the last millimetres to J4.15
# (and the harness) carry the fast one; R41 is the series resistor right at the driver.
rst={'U6.2_to_J4.15_straight_mm':round(math.dist(pxy('U6','2'),pxy('J4','15')),2),'U6.4_R41.1_routed_mm':route('SUP_N_DRV',('U6','4'),('R41','1')),
     'R41.2_J4.15_routed_mm':route('SUP_N_OUT',('R41','2'),('J4','15')),'J4.15':net(pad('J4','15')),'U6.2':net(pad('U6','2'))}
check('R4 reset to P04: U6 (SN74LVC1G17) <= 15 mm from J4.15; U6.4 -> R41 <= 5 mm and R41 -> J4.15 <= 15 mm routed; J4.15 = SUP_N_OUT, U6.2 = SUP_N',
      rst['U6.2_to_J4.15_straight_mm']<=15 and rst['U6.4_R41.1_routed_mm'] is not None and rst['U6.4_R41.1_routed_mm']<=5
      and rst['R41.2_J4.15_routed_mm'] is not None and rst['R41.2_J4.15_routed_mm']<=15 and rst['J4.15']=='SUP_N_OUT' and rst['U6.2']=='SUP_N',rst)
power_paths={'input':route('5V_SYS',('J10','1'),('Q1','3')),'output':route('5V_M1',('Q1','2'),('M1','J1-21'))}
check('Power feed physically terminates on Q1 drain/source and M1',all(v is not None and v<100 for v in power_paths.values()),power_paths)
vcc = {u: net(pad(u, '14')) for u in ('U11', 'U12', 'U13', 'U14', 'U21', 'U22', 'U23')}
io = sorted(f"{a.GetParentFootprint().GetReference()}.{a.GetNumber()}" for g in b.GetFootprints() for a in g.Pads() if net(a) == '3V3_IO')
check('Supply domains (v6.1): every 74LVC125 VCC on 3V3_CORE; 3V3_IO only at J10.3, TP3 and the unused OE# of U14; 3V3_CORE never joins 3V3_IO',
      all(v == '3V3_CORE' for v in vcc.values()) and io == ['J10.3', 'TP3.1', 'U14.10', 'U14.13', 'U14.4'], {'vcc': vcc, '3V3_IO_pads': io})
gnd_isl = {b.GetLayerName(L): sum(z.GetFilledPolysList(L).OutlineCount() for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND' and z.IsOnLayer(L)) for L in (p.F_Cu, p.B_Cu)}
share = {}
for L in (p.F_Cu, p.B_Cu):
    areas = []
    for z in b.Zones():
        if z.GetIsRuleArea() or z.GetNetname() != 'GND' or not z.IsOnLayer(L):
            continue
        ps = z.GetFilledPolysList(L)
        for i in range(ps.OutlineCount()):
            s1 = p.SHAPE_POLY_SET(); s1.AddOutline(ps.Outline(i))
            for h in range(ps.HoleCount(i)):
                s1.AddHole(ps.Hole(i, h))
            areas.append(s1.Area() / 1e12)
    share[b.GetLayerName(L)] = round(100 * max(areas) / sum(areas), 1) if areas else 0
stitch = [t for t in b.GetTracks() if isinstance(t, p.PCB_VIA) and net(t) == 'GND' and t.IsLocked() and abs(p.ToMM(t.GetWidth(p.F_Cu)) - .8) < 1e-6]
gfill = {b.GetLayerName(L): round(sum(z.GetFilledPolysList(L).Area() for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND' and z.IsOnLayer(L)) / 1e12 / (W * H) * 100, 1) for L in (p.F_Cu, p.B_Cu)}
check('GND pours on both layers, island removal on; largest island >= 75 % of each pour; layers stitched by >= 40 GND vias (8 mm grid)',
      all(v > 0 for v in gnd_isl.values()) and all(v >= 75 for v in share.values()) and len(stitch) >= 40 and
      all(z.GetIslandRemovalMode() == p.ISLAND_REMOVAL_MODE_ALWAYS for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND'),
      {'islands': gnd_isl, 'largest_island_percent': share, 'filled_percent': gfill, 'stitching_vias': len(stitch)})
# ---------------- 4. silkscreen ----------------
texts = [(t.GetText(), t) for t in b.GetDrawings() if isinstance(t, p.PCB_TEXT) and t.GetLayer() == p.F_SilkS]


def tcentre(t):
    bb = t.GetBoundingBox(); return (p.ToMM(bb.GetCenter().x), p.ToMM(bb.GetCenter().y))


cour, cbb = {}, {}
for f in b.GetFootprints():
    if not f.GetReference().startswith('H'):
        f.BuildCourtyardCaches(); cour[f.GetReference()] = f.GetCourtyard(p.F_CrtYd); cbb[f.GetReference()] = cbox(f.GetReference())


def inside_other(t, own):
    bb = t.GetBoundingBox(); x0, y0, x1, y1 = p.ToMM(bb.GetLeft()), p.ToMM(bb.GetTop()), p.ToMM(bb.GetRight()), p.ToMM(bb.GetBottom())
    samples = [(x0 + (x1 - x0) * i / 4, y0 + (y1 - y0) * j / 2) for i in range(5) for j in range(3)]
    return sorted({r for r, cy in cour.items() if r not in own for q in samples if cy.Contains(xy(*q))})


GAP = {'R41': ('J4', 'U12')}  # R4: R41 alone in the gap between two bodies; its reference sits in the same gap below it
amb = {}
for f in b.GetFootprints():
    r = f.GetReference(); ref = f.Reference()
    if r.startswith('H') or not ref.IsVisible():
        continue
    c = tcentre(ref); mine = rdist(c, cbb[r])
    closer = [o for o in cbb if o != r and o not in GAP.get(r, ()) and rdist(c, cbb[o]) < mine + .3]; other = inside_other(ref, {r})
    if r in GAP:  # in the gap: between the two bodies and at most 2.5 mm below the part
        g0, g1 = cbb[GAP[r][0]], cbb[GAP[r][1]]
        if not (g0[2] < c[0] < g1[0] and cbb[r][3] < c[1] <= cbb[r][3] + 2.5):
            closer.append('outside the gap')
    if closer or other:
        amb[r] = {'nearer': closer, 'inside': other}
check('Every visible reference outside other courtyards and nearest to its own part (R41: in its gap between J4 and U12, right below it)', not amb, amb)
EXEMPT = {'M1', 'SD1'}  # modules on headers: their outline covers bare board; legends there are read before fitting
hidden = {txt: inside_other(t, EXEMPT) for txt, t in texts if inside_other(t, EXEMPT)}
check('Every board legend outside all courtyards (visible after assembly); the M1 / SD1 module outlines excepted', not hidden, hidden)
NAMES = {'J1': 'DAQ', 'J2': 'ILOG', 'J3': 'ITEST', 'J4': 'SAFE', 'J5': 'DIR', 'J6': 'SFAULT', 'J7': 'TEMP', 'J8': 'CAN', 'J9': 'PANELCORE', 'J10': 'LV03'}
lab = {}
for r, nm in NAMES.items():
    c = [tcentre(t) for s, t in texts if s.split(' ')[0] == nm]
    if c:
        d = {o: rdist(c[0], cbb[o]) for o in NAMES}; lab[nm] = {'to_own_mm': round(d[r], 2), 'nearest': min(d, key=d.get)}
check('Connector names DAQ, ILOG, ITEST, SAFE, DIR, SFAULT, TEMP, CAN, PANELCORE, LV03 next to their own connector (<= 4 mm, nearest connector)',
      len(lab) == len(NAMES) and all(v['to_own_mm'] <= 4 and v['nearest'] == r for (r, _), v in zip(NAMES.items(), lab.values())), lab)
keys = {}
for r, (nm, key) in IDC.items():
    kp = pxy(r, key); bx = cbb[r]; e = idc[r]['edge']; ax = 0 if e in 'TB' else 1  # along-edge coordinate of the key pin
    best = None
    for s, t in texts:
        if s != f'KEY{key}':
            continue
        c = tcentre(t); gap = rdist(c, bx)
        owner = min(IDC, key=lambda o: rdist(c, cbb[o]))
        cand = {'along_offset_mm': round(abs(c[ax] - kp[ax]), 2), 'gap_to_header_mm': round(gap, 2), 'nearest_header': owner}
        if owner == r and (best is None or cand['along_offset_mm'] < best['along_offset_mm']):
            best = cand
    keys[r] = {'key_pin': key, 'text': best}
check('KEY n beside every IDC header, in line with its key pin (<= 1.5 mm along the header), <= 3 mm outside the box, nearest to its own header',
      all(v['text'] and v['text']['along_offset_mm'] <= 1.5 and 0 < v['text']['gap_to_header_mm'] <= 3 for v in keys.values()), keys)
need_txt = ['USB-C', 'ANTENA: BEZ MIEDZI', 'microSD']
have_txt = {s for s, _ in texts}
check('Operating legends present (USB-C at the edge, antenna keepout, microSD card slot)', all(s in have_txt for s in need_txt), {'missing': [s for s in need_txt if s not in have_txt]})
report = {'board': path.name, 'board_sha256': sha(path), 'checks': checks, 'details': details, 'passed': sum(c['pass'] for c in checks), 'total': len(checks)}
(out / 'pcb-checks.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
for c in checks:
    print('PASS' if c['pass'] else 'FAIL', c['check'])
print(f"{report['passed']}/{report['total']} checks")
sys.exit(0 if report['passed'] == report['total'] else 1)
