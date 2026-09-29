"""P00 R2 silkscreen: references, channel numbers and legends; placed without collisions.
Collision model and rules taken over from the P02 R1 script (raster + courtyard owners):
- a reference lies outside every other footprint's courtyard and its own footprint is the nearest one;
  resistors and the DIP carry their reference inside their own body outline (visible before assembly);
- in the dense channel columns the switch, LED and header references are not printed: the channel number
  next to each LED names the whole column (SWn, LEDn, RLn, RSn, Jn); the references stay on F.Fab and in the PDF;
- a legend lies outside all courtyards, so it stays visible after assembly.
Idempotent: board-level legends of a previous run are dropped at file level first.
"""
from pathlib import Path
import pcbnew as p, math, json
import numpy as np
from PIL import Image, ImageDraw
from sexpr import parse, dump
P = Path(__file__).resolve().parents[1]; fn = P / 'eda/P00.kicad_pcb'; rep = P / 'verification/silkscreen-placement.json'
tree = parse(fn.read_text(encoding='utf-8'))
old = set(json.loads(rep.read_text(encoding='utf-8'))['legend_texts']) if rep.exists() else set()
tree = [g for g in tree if not (isinstance(g, list) and g and g[0] == 'gr_text' and (g[1] in old or g[1].startswith('EGRLab P00')))]
fn.write_text(dump(tree) + chr(10), encoding='utf-8')
b = p.LoadBoard(str(fn)); mm = p.FromMM
BW, BH = 115, 70
R = 20; W, H = BW * R, BH * R
img = Image.new('1', (W, H), 0); d = ImageDraw.Draw(img)
HARNESS = set()


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
for hx, hy in [(5, 5), (BW - 5, 5), (5, BH - 5), (BW - 5, BH - 5)]:
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
grid = np.array(img, dtype=bool); owners = np.array(owner_img, dtype=np.int32)
for f in fps:  # harness anchor notes: short 'TIE' on silk; the 12.5 mm geometry stays on F.Fab and in MECHANIKA
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


def ok(bb, allow, own, q):
    x0, y0, x1, y1 = pix(bb)
    if x0 < 0 or y0 < 0 or x1 >= W or y1 >= H or grid[y0:y1 + 1, x0:x1 + 1].any():
        return False
    under = set(np.unique(owners[y0:y1 + 1, x0:x1 + 1]).tolist()) - {0}
    if not under <= allow:
        return False
    if own:  # the own footprint must be the nearest courtyard to the text centre
        mine = bdist(own, *q)
        return all(bdist(k, *q) >= mine + .3 for k in cbox if k != own)
    return True


def place(t, anchors, limit, name, angle=0, allow=frozenset(), own=0, step=.25):
    t.SetTextAngle(p.EDA_ANGLE(angle, p.DEGREES_T))
    n = int(limit / step)
    for x0, y0 in anchors:
        cands = sorted({(round(x0 + i * step, 3), round(y0 + j * step, 3)) for i in range(-n, n + 1) for j in range(-n, n + 1)},
                       key=lambda q: (math.dist(q, (x0, y0)), q))
        for q in cands:
            if math.dist(q, (x0, y0)) > limit:
                break
            t.SetPosition(xy(*q)); bb = tbox(t)
            if ok(bb, allow, own, q):
                x0b, y0b, x1b, y1b = pix(bb); grid[y0b:y1b + 1, x0b:x1b + 1] = True
                return {'text': name, 'preferred': list(anchors[0]), 'placed': list(q), 'angle': angle, 'shift_mm': round(math.dist(q, anchors[0]), 2)}
    Image.fromarray(~grid).convert('L').resize((W // 4, H // 4)).save(P / 'verification/silk-free-debug.png')
    raise SystemExit(f'No clear position within {limit} mm for {name} near {anchors[0]}; free map: verification/silk-free-debug.png')


report = {'references': [], 'legends': [], 'legend_texts': []}
INSIDE = {'R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal', 'DIP-8_W7.62mm'}
COLUMN = {f'{k}{n}' for n in range(1, 10) for k in ('SW', 'LED', 'J')}  # named by the channel number
PREF = {}
order = sorted(fps, key=lambda f: (f.GetFPIDAsString().split(':')[-1] not in INSIDE, f.GetReference()))
for f in order:
    r = f.GetReference(); ref = f.Reference()
    if r.startswith('TP') or r in COLUMN:  # test pads: net legend; columns: channel number (refs stay on F.Fab)
        ref.SetVisible(False)
    if not ref.IsVisible() or r.startswith('H'):
        continue
    ref.SetTextSize(xy(1, 1)); ref.SetTextThickness(mm(.15)); ref.SetLayer(p.F_SilkS)
    fid = f.GetFPIDAsString().split(':')[-1]; pads = [a for a in f.Pads() if a.GetNumber()]
    k = index[r]; x0, y0, x1, y1 = cbox[k]; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if fid in INSIDE:
        angle = 0
        if fid.startswith('R_Axial'):
            a, c = pads[0].GetPosition(), pads[1].GetPosition(); angle = 90 if abs(a.x - c.x) < abs(a.y - c.y) else 0
            cx, cy = p.ToMM(a.x + c.x) / 2, p.ToMM(a.y + c.y) / 2
        report['references'].append(place(ref, [(cx, cy)], 3, r, angle, frozenset({k}), k, .1))
    else:
        anchors = PREF.get(r, []) + [(cx, y0 - .8), (cx, y1 + .8), (x0 - 1.8, cy), (x1 + 1.8, cy)]
        report['references'].append(place(ref, anchors, 6, r, 0, frozenset({k}), k))

# ---- legends (text, x, y, size, angle, max shift) ------------------------------------------------------
CX = [14 + 11 * k for k in range(8)]
LEG = [(str(n), cx - 4.1, 40, 1.0, 0, .6) for n, cx in enumerate(CX, 1)] + [('HB', 102 - 4.4, 40, .9, 0, .8)]
LEG += [('SUWAK W GORE = H (3V3), W DOL = L (GND); LED SWIECI = H', 57.5, 33.6, .9, 0, 1.2),
        ('J1-J9: LEWY PIN = GND, PRAWY = SYGNAL PRZEZ 1 k', 57.5, 63.4, .9, 0, 1.2),
        ('HB: SUWAK W GORE = RUN, W DOL = STOP (wyjscie L)', 83.5, 30.6, .8, 0, 2),
        ('+VIN 6-15V', 16.2, 25.4, .9, 0, 2), ('GND', 13.5, 11.2, .9, 0, 2),
        ('VIN', 22, 29.2, .8, 0, 1.5), ('3V3', 57, 29.2, .8, 0, 1.5), ('GND', 61, 29.2, .8, 0, 1.5), ('3V3', 69, 23.9, .8, 0, 1.5),
        ('EGRLab P00 FIXTURE / PCB R2 / 2026-09 - przyrzad stanowiskowy', 57.5, 66.4, .9, 0, 1.5)]
exempt = frozenset(index[r] for r in HARNESS)
for text, x, y, size, angle, lim in LEG:
    t = p.PCB_TEXT(b); t.SetText(text); t.SetTextSize(xy(size, size)); t.SetTextThickness(mm(.15 if size >= 1 else .12)); t.SetLayer(p.F_SilkS)
    report['legends'].append(place(t, [(x, y)], lim, text, angle, exempt)); b.Add(t)
report['legend_texts'] = sorted({x[0] for x in LEG})
p.SaveBoard(str(fn), b, True)
rep.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print('references', len(report['references']), 'max shift', max(r['shift_mm'] for r in report['references']),
      '| legends', len(report['legends']), 'max shift', max(r['shift_mm'] for r in report['legends']))
