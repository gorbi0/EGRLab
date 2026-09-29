"""P03 R4 silkscreen: references, connector names, KEY marks and legends; placed without collisions.
Collision model and rules taken over from the P00/P02 R1 scripts (raster + courtyard owners):
- a reference lies outside every other footprint's courtyard and its own footprint is the nearest one;
  resistors, DIPs and the two plug-in modules (M1, SD1) carry their reference inside their own outline;
- a connector name ('SAFE P04' ...) sits beside its connector on the board side and nearer to it than to any other connector;
- 'KEY n' sits in line with the key position of every IDC box header, just outside the box on the board side (pin
  removed at assembly, v6.1); placed before the connector names, which may then shift along the edge;
- a legend lies outside all courtyards, so it stays visible after assembly; legends on the bare board under the
  M1 / SD1 modules (USB-C, microSD) are read before the modules are plugged in.
Idempotent: board-level legends of a previous run are dropped at file level first.
"""
from pathlib import Path
import pcbnew as p, math, json
import numpy as np
from PIL import Image, ImageDraw
from sexpr import parse, dump
P = Path(__file__).resolve().parents[1]; fn = P / 'eda/P03.kicad_pcb'; rep = P / 'verification/silkscreen-placement.json'
tree = parse(fn.read_text(encoding='utf-8'))
old = set(json.loads(rep.read_text(encoding='utf-8'))['legend_texts']) if rep.exists() else set()
tree = [g for g in tree if not (isinstance(g, list) and g and g[0] == 'gr_text' and (g[1] in old or g[1].startswith('EGRLab P03')))]
fn.write_text(dump(tree) + chr(10), encoding='utf-8')
b = p.LoadBoard(str(fn)); mm = p.FromMM
BW, BH = 160, 120
R = 20; W, H = BW * R, BH * R
img = Image.new('1', (W, H), 0); d = ImageDraw.Draw(img)
HOLES = [(5, 5), (155, 5), (5, 115), (155, 115), (155, 38)]
MODULES = {'M1', 'SD1'}


def xy(x, y):
    return p.VECTOR2I(mm(x), mm(y))


def px(v):
    return p.ToMM(v) * R


def seg(a, c, w):
    d.line([px(a.x), px(a.y), px(c.x), px(c.y)], fill=1, width=max(1, int(round(w * R))))
    for q in (a, c):
        r = w * R / 2; d.ellipse([px(q.x) - r, px(q.y) - r, px(q.x) + r, px(q.y) + r], fill=1)


for box in [(0, 0, BW, 1), (0, BH - 1, BW, BH), (0, 0, 1, BH), (BW - 1, 0, BW, BH)]:
    d.rectangle([v * R for v in box], fill=1)
for hx, hy in HOLES:
    d.ellipse([(hx - 4.5) * R, (hy - 4.5) * R, (hx + 4.5) * R, (hy + 4.5) * R], fill=1)
fps = sorted(b.GetFootprints(), key=lambda f: f.GetReference())
owner_img = Image.new('I', (W, H), 0); od = ImageDraw.Draw(owner_img)
index, cbox = {}, {}
for k, f in enumerate(fps, 1):
    f.BuildCourtyardCaches(); index[f.GetReference()] = k
    cy = f.GetCourtyard(p.F_CrtYd)
    if cy.OutlineCount():
        bb = cy.BBox(); cbox[k] = (p.ToMM(bb.GetLeft()), p.ToMM(bb.GetTop()), p.ToMM(bb.GetRight()), p.ToMM(bb.GetBottom()))
        for i in range(cy.OutlineCount()):
            ol = cy.Outline(i); od.polygon([(px(ol.CPoint(j).x), px(ol.CPoint(j).y)) for j in range(ol.PointCount())], fill=k)
    for a in f.Pads():
        bb = a.GetBoundingBox(); m = .35
        e = [px(bb.GetLeft()) - m * R, px(bb.GetTop()) - m * R, px(bb.GetRight()) + m * R, px(bb.GetBottom()) + m * R]
        (d.ellipse if a.GetShape() in (p.PAD_SHAPE_CIRCLE, p.PAD_SHAPE_OVAL) else d.rectangle)(e, fill=1)
    for g in f.GraphicalItems():
        if g.GetLayer() != p.F_SilkS or not isinstance(g, p.PCB_SHAPE):
            continue
        w = p.ToMM(g.GetWidth()) + .4; s = g.GetShape()
        if s == p.SHAPE_T_SEGMENT:
            seg(g.GetStart(), g.GetEnd(), w)
        elif s == p.SHAPE_T_RECT:
            c = g.GetCorners()
            for j in range(4):
                seg(c[j], c[(j + 1) % 4], w)
        elif s == p.SHAPE_T_CIRCLE:
            c = g.GetCenter(); r = px(g.GetRadius()); hw = w * R / 2
            d.ellipse([px(c.x) - r - hw, px(c.y) - r - hw, px(c.x) + r + hw, px(c.y) + r + hw], outline=1, width=int(2 * hw) + 1)
        elif s == p.SHAPE_T_ARC:
            c = g.GetCenter(); r = p.ToMM(g.GetRadius()); a0 = g.GetArcAngleStart().AsDegrees(); da = g.GetArcAngle().AsDegrees()
            pts = [(p.ToMM(c.x) + r * math.cos(math.radians(a0 + da * j / 24)), p.ToMM(c.y) + r * math.sin(math.radians(a0 + da * j / 24))) for j in range(25)]
            for u, v in zip(pts, pts[1:]):
                seg(xy(*u), xy(*v), w)
        elif s == p.SHAPE_T_POLY:
            ps = g.GetPolyShape()
            for i in range(ps.OutlineCount()):
                ol = ps.Outline(i); q = [ol.CPoint(j) for j in range(ol.PointCount())]
                for j in range(len(q)):
                    seg(q[j], q[(j + 1) % len(q)], w)
        else:
            raise ValueError((f.GetReference(), s))
for t in b.GetTracks():  # vias (routed and GND stitching) are copper openings in the mask area: keep text off them
    if isinstance(t, p.PCB_VIA):
        c = t.GetPosition(); r = (p.ToMM(t.GetWidth(p.F_Cu)) / 2 + .3) * R
        d.ellipse([px(c.x) - r, px(c.y) - r, px(c.x) + r, px(c.y) + r], fill=1)
grid = np.array(img, dtype=bool); owners = np.array(owner_img, dtype=np.int32)
for f in fps:  # harness anchor note: short 'TIE' on silk; the 12.5 mm geometry stays on F.Fab and in MECHANIKA
    for g in f.GraphicalItems():
        if isinstance(g, p.PCB_TEXT) and g.GetLayer() == p.F_SilkS and g.GetText().startswith('TIE'):
            g.SetText('TIE'); g.SetTextSize(xy(.8, .8)); g.SetTextThickness(mm(.12))


def pix(bb):
    return [int(round(v * R)) for v in bb]


def tbox(t, extra=.2):
    q = t.GetBoundingBox()
    return (p.ToMM(q.GetLeft()) - extra, p.ToMM(q.GetTop()) - extra, p.ToMM(q.GetRight()) + extra, p.ToMM(q.GetBottom()) + extra)


for f in fps:
    for g in f.GraphicalItems():
        if isinstance(g, p.PCB_TEXT) and g.GetLayer() == p.F_SilkS:
            x0, y0, x1, y1 = pix(tbox(g)); grid[max(0, y0):y1 + 1, max(0, x0):x1 + 1] = True


def bdist(k, x, y):
    x0, y0, x1, y1 = cbox[k]
    return math.hypot(max(x0 - x, 0, x - x1), max(y0 - y, 0, y - y1))


def ok(bb, allow, own, q, near=None):
    x0, y0, x1, y1 = pix(bb)
    if x0 < 0 or y0 < 0 or x1 >= W or y1 >= H or grid[y0:y1 + 1, x0:x1 + 1].any():
        return False
    under = set(np.unique(owners[y0:y1 + 1, x0:x1 + 1]).tolist()) - {0}
    if not under <= allow:
        return False
    if own:  # the own footprint must be the nearest courtyard to the text centre
        mine = bdist(own, *q)
        return all(bdist(k, *q) >= mine + .3 for k in (near or cbox) if k != own)
    return True


def place(t, anchors, limit, name, angle=0, allow=frozenset(), own=0, step=.25, near=None, extra=.2, max_own_distance=None):
    t.SetTextAngle(p.EDA_ANGLE(angle, p.DEGREES_T))
    n = int(limit / step)
    for x0, y0 in anchors:
        cands = sorted({(round(x0 + i * step, 3), round(y0 + j * step, 3)) for i in range(-n, n + 1) for j in range(-n, n + 1)},
                       key=lambda q: (math.dist(q, (x0, y0)), q))
        for q in cands:
            if math.dist(q, (x0, y0)) > limit:
                break
            t.SetPosition(xy(*q)); bb = tbox(t, extra)
            if max_own_distance is not None and bdist(own, *q) > max_own_distance:
                continue
            if ok(bb, allow, own, q, near):
                x0b, y0b, x1b, y1b = pix(bb); grid[y0b:y1b + 1, x0b:x1b + 1] = True
                return {'text': name, 'preferred': list(anchors[0]), 'placed': list(q), 'angle': angle, 'shift_mm': round(math.dist(q, anchors[0]), 2)}
    Image.fromarray(~grid).convert('L').resize((W // 4, H // 4)).save(P / 'verification/silk-free-debug.png')
    raise SystemExit(f'No clear position within {limit} mm for {name} near {anchors[0]}; free map: verification/silk-free-debug.png')


fmap = {f.GetReference(): f for f in fps}


def pad(ref, num):
    return next(a for a in fmap[ref].Pads() if a.GetNumber() == num)


def pmm(ref, num):
    v = pad(ref, num).GetPosition(); return (p.ToMM(v.x), p.ToMM(v.y))


report = {'references': [], 'legends': [], 'legend_texts': []}
leg = []; exempt = frozenset(index[r] for r in MODULES)
# ---- connector names and KEY marks ------------------------------------------------------------------------
NAMES = {'J1': 'DAQ P05', 'J2': 'ILOG P06', 'J3': 'ITEST P07', 'J4': 'SAFE P04', 'J5': 'DIR P07', 'J6': 'SFAULT P08', 'J7': 'TEMP P09',
         'J8': 'CAN P10', 'J9': 'PANELCORE P11', 'J10': 'LV03 z P02'}
KEYS = {'J2': '2', 'J3': '2', 'J4': '4', 'J5': '4', 'J6': '3', 'J7': '4', 'J8': '4'}
conn = {index[r] for r in NAMES}
kset = {index[r] for r in KEYS}
for r, key in KEYS.items():
    k = index[r]; kx, ky = pmm(r, key); x0, y0, x1, y1 = cbox[k]
    ed = {'T': y0, 'B': BH - y1, 'L': x0, 'R': BW - x1}; e = min(ed, key=ed.get)
    anc = {'T': [(kx, y1 + .9)], 'B': [(kx, y0 - .9)], 'L': [(x1 + 1.2, ky)], 'R': [(x0 - 1.2, ky)]}[e]  # in line with the key pin, board side
    t = p.PCB_TEXT(b); t.SetText(f'KEY{key}'); t.SetTextSize(xy(.8, .8)); t.SetTextThickness(mm(.12)); t.SetLayer(p.F_SilkS)
    # search radius 1.8 mm: clears the pin-1 arrow of the footprint when the key position shares its column (KEY 2)
    angles = [90 if e in 'LR' else 0]
    if r == 'J3':
        angles.append(90)  # fit beside the pin-1 arrow and R15; still aligned with key pin 2
    for angle in angles:
        try:
            anchors = [(kx - .8, y1 + 2.9)] if r == 'J3' and angle == 90 else anc
            placed = place(t, anchors, .1 if anchors is not anc else 1.8, f'{r} KEY{key}', angle, frozenset(), 0, .05, None, .1)
            break
        except SystemExit:
            if angle == angles[-1]:
                raise
    report['legends'].append(placed); b.Add(t); leg.append(f'KEY{key}')
for r, text in NAMES.items():
    k = index[r]; x0, y0, x1, y1 = cbox[k]; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    ed = {'T': y0, 'B': BH - y1, 'L': x0, 'R': BW - x1}; e = min(ed, key=ed.get)
    anc = {'T': [(cx, y1 + 1.2), (x1 + 4, cy), (x0 - 4, cy)], 'B': [(cx, y0 - 1.2), (x1 + 4, cy), (x0 - 4, cy)],
           'L': [(x1 + 1.3, cy)], 'R': [(x0 - 1.3, cy)]}[e]
    t = p.PCB_TEXT(b); t.SetText(text); t.SetLayer(p.F_SilkS)
    side = [(x0 - 1.3, cy), (x1 + 1.3, cy)]
    for size, angle, cand in [(1.2, 90 if e in 'LR' else 0, anc), (1.0, 90 if e in 'LR' else 0, anc), (1.0, 90, side)]:
        t.SetTextSize(xy(size, size)); t.SetTextThickness(mm(.2 if size > 1 else .15))
        try:
            report['legends'].append(place(t, cand, 5, text, angle, frozenset(), k, .25, conn, max_own_distance=4)); break
        except SystemExit:
            if size == 1.0 and angle == 90 and cand is side:
                raise
    b.Add(t); leg.append(text)
# test-pad net legends before the references. TP1/TP4/TP3/TP6 sit right under LV03 pads 1-4 with the same nets, so
# the legends also read as the LV03 pinout; TP2 (3V3_CORE) is left of the row, under no LV03 pad
TPL = [('5V', 'TP1', 2.6), ('GND', 'TP4', 2.6), ('3V3IO', 'TP3', 2.6), ('GND', 'TP6', 2.6), ('3V3', 'TP2', 2.6), ('SUP_N', 'TP5', 0), ('5V_M1', 'TP7', 0), ('RAW_RST', 'TP8', 0)]
for text, r, dy in TPL:
    x, y = pmm(r, '1'); t = p.PCB_TEXT(b); t.SetText(text); t.SetTextSize(xy(.8, .8)); t.SetTextThickness(mm(.12)); t.SetLayer(p.F_SilkS)
    report['legends'].append(place(t, [(x, y + dy)], 2 if dy else 3, f'{r} {text}', 0, exempt)); b.Add(t); leg.append(text)
INSIDE = {'R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal', 'DIP-28_W7.62mm', 'DIP-16_W7.62mm'}
GAP = {'R41': ('J4', 'U12')}  # part in a gap between two bodies -> the two bodies of the gap
order = sorted(fps, key=lambda f: (f.GetFPIDAsString().split(':')[-1] not in INSIDE and f.GetReference() not in MODULES, f.GetReference()))
for f in order:
    r = f.GetReference(); ref = f.Reference()
    if r.startswith('TP'):  # test pads: net legend instead of the reference (refs stay on F.Fab and in the PDF)
        ref.SetVisible(False)
    if not ref.IsVisible() or r.startswith('H'):
        continue
    ref.SetTextSize(xy(1, 1)); ref.SetTextThickness(mm(.15)); ref.SetLayer(p.F_SilkS)
    if r in ('C13', 'C14', 'Q1', 'U5'):
        ref.SetTextSize(xy(.8, .8)); ref.SetTextThickness(mm(.12))
    fid = f.GetFPIDAsString().split(':')[-1]; pads = [a for a in f.Pads() if a.GetNumber()]
    k = index[r]; x0, y0, x1, y1 = cbox[k]; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if fid in INSIDE or r in MODULES:
        angle = 0
        if fid.startswith('R_Axial'):
            a, c = pads[0].GetPosition(), pads[1].GetPosition(); angle = 90 if abs(a.x - c.x) < abs(a.y - c.y) else 0
            cx, cy = p.ToMM(a.x + c.x) / 2, p.ToMM(a.y + c.y) / 2
        elif fid.startswith('DIP'):
            angle = 90 if (y1 - y0) > (x1 - x0) else 0
        report['references'].append(place(ref, [(cx, cy)], 6 if r in MODULES else 3, r, angle, frozenset({k}), k, .1))
    elif r in GAP:  # R4: R41 stands alone in the 2.95 mm gap between the J4 and U12 bodies, so no text position outside
        # its courtyard is nearer to it than to them. Its reference goes vertical into the same gap right below it; the
        # nearest-courtyard test then ignores only the two bodies that form the gap.
        ref.SetTextSize(xy(.8, .8)); ref.SetTextThickness(mm(.12))
        report['references'].append(place(ref, [(cx, y1 + 1.4)], 1.5, r, 90, frozenset({k}), k, .1, set(cbox) - {index[g] for g in GAP[r]}))
    else:
        anchors = [(cx, y0 - .8), (cx, y1 + .8), (x0 - 1.8, cy), (x1 + 1.8, cy)]
        report['references'].append(place(ref, anchors, 7, r, 0, frozenset({k}), k))

# ---- board legends (text, anchor, size, max shift) -----------------------------------------------------------
m1 = fmap['M1']; a = math.radians(m1.GetOrientationDegrees()); c = m1.GetPosition()


def m1xy(x, y):
    return (p.ToMM(c.x) + x * math.cos(a) + y * math.sin(a), p.ToMM(c.y) - x * math.sin(a) + y * math.cos(a))


zk = next(z for z in b.Zones() if z.GetIsRuleArea() and z.GetZoneName() == 'ANTENNA M1'); zb = zk.Outline().BBox()
akx, aky = p.ToMM(zb.GetCenter().x), (p.ToMM(zb.GetBottom()) + m1xy(0, -8.25)[1]) / 2
sd = fmap['SD1']; sa = math.radians(sd.GetOrientationDegrees()); sc = sd.GetPosition()
sdx = lambda x, y: (p.ToMM(sc.x) + x * math.cos(sa) + y * math.sin(sa), p.ToMM(sc.y) - x * math.sin(sa) + y * math.cos(sa))
LEG = [('USB-C', *m1xy(11.43, 53.5), 1.0, 2), ('ANTENA: BEZ MIEDZI', akx, aky, .9, 3), ('microSD', *sdx(10.16, -18), 1.0, 3),
       ('EGRLab P03 CORE / PCB R4 / 2026-09', 138, 90, 1.0, 14)]
for text, x, y, size, lim in LEG:
    t = p.PCB_TEXT(b); t.SetText(text); t.SetTextSize(xy(size, size)); t.SetTextThickness(mm(.15 if size >= 1 else .12)); t.SetLayer(p.F_SilkS)
    report['legends'].append(place(t, [(x, y)], lim, text, 0, exempt)); b.Add(t); leg.append(text)
report['legend_texts'] = sorted(set(leg))
p.SaveBoard(str(fn), b, True)
rep.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print('references', len(report['references']), 'max shift', max(r['shift_mm'] for r in report['references']),
      '| legends', len(report['legends']), 'max shift', max(r['shift_mm'] for r in report['legends']))
