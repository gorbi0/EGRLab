"""P06-R1 reference and harness silkscreen. Labels avoid copper openings, holes and other courtyards. References may lie within their own bodies. TP3 uses an explicit leader in the dense LDO corner. Tented vias keep their drill holes clear. Repeated runs remove prior generated legends and leaders."""
from pathlib import Path
import pcbnew as p, math, json
import numpy as np
from PIL import Image, ImageDraw
from sexpr import parse, dump
P = Path(__file__).resolve().parents[1]; fn = P / 'eda/P06.kicad_pcb'; rep = P / 'verification/silkscreen-placement.json'
tree = parse(fn.read_text(encoding='utf-8'))
old = set(json.loads(rep.read_text(encoding='utf-8'))['legend_texts']) if rep.exists() else set()
def prior_leader(g):
    if not isinstance(g,list) or not g or g[0]!='gr_line':return False
    fields={a[0]:a[1:] for a in g[1:] if isinstance(a,list)}
    return fields.get('layer')==['F.SilkS'] and tuple(map(float,fields.get('start',[]))) in [(94.,28.),(95.,30.)]
tree = [g for g in tree if not prior_leader(g) and not (isinstance(g, list) and g and g[0] == 'gr_text' and (g[1] in old or g[1].startswith('EGRLab P06')))]
fn.write_text(dump(tree) + chr(10), encoding='utf-8')
b = p.LoadBoard(str(fn)); mm = p.FromMM
for f in b.GetFootprints():
    if f.GetReference()=='D2':
        for g in f.GraphicalItems():
            if isinstance(g,p.PCB_TEXT) and g.GetText()=='K' and g.GetLayer()==p.F_SilkS:
                g.SetPosition(p.VECTOR2I(mm(44.8),mm(84.3)))
BW, BH = 120, 100
R = 20; W, H = BW * R, BH * R
img = Image.new('1', (W, H), 0); d = ImageDraw.Draw(img)
HARNESS = {'J1','J2','J3','J4','J5'}


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
for t in b.GetTracks():  # tented vias: only the drill hole (silk is lost over a hole) is an obstacle
    if isinstance(t, p.PCB_VIA):
        c = t.GetPosition(); r = (p.ToMM(t.GetDrill()) / 2 + .1) * R
        d.ellipse([px(c.x) - r, px(c.y) - r, px(c.x) + r, px(c.y) + r], fill=1)
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
INSIDE = {'R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal', 'DIP-14_W7.62mm', 'DIP-16_W7.62mm', 'DIP-8_W7.62mm', 'R_Axial_DIN0617_L17.0mm_D6.0mm_P25.40mm_Horizontal', 'R_Axial_DIN0411_L9.9mm_D3.6mm_P15.24mm_Horizontal', 'Adapter_SO14_DIP14_W15.24_Kamami575068'}
COLUMN = set()
PREF = {'J1':[(67,14)],'J2':[(101.8,15)],'J3':[(30,14)],'J4':[(29,88)],'J5':[(66.5,87)]}
order = sorted(fps, key=lambda f: (f.GetFPIDAsString().split(':')[-1] not in INSIDE, f.GetReference()))
for f in order:
    r = f.GetReference(); ref = f.Reference()
    if r in COLUMN:
        ref.SetVisible(False)
    if not ref.IsVisible() or r.startswith('H'):
        continue
    small = 'C_0805' in f.GetFPIDAsString() or r.startswith('TP')
    ref.SetTextSize(xy(.8 if small else 1, .8 if small else 1)); ref.SetTextThickness(mm(.12 if small else .15)); ref.SetLayer(p.F_SilkS)
    fid = f.GetFPIDAsString().split(':')[-1]; pads = [a for a in f.Pads() if a.GetNumber()]
    k = index[r]; x0, y0, x1, y1 = cbox[k]; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if r=='TP3':
        # Dense LDO corner: explicit leader makes association unambiguous even
        # though the label centre is closer to an adjacent component courtyard.
        report['references'].append(place(ref, [(93,27)], 1, r, 0, frozenset(), 0))
        for a,c in [((94,28),(95,30)),((95,30),(95,32.2))]:
            t=p.PCB_SHAPE(b);t.SetShape(p.SHAPE_T_SEGMENT);t.SetStart(xy(*a));t.SetEnd(xy(*c));t.SetWidth(mm(.12));t.SetLayer(p.F_SilkS);b.Add(t)
            seg(xy(*a),xy(*c),.52)
        grid=np.array(img,dtype=bool)|grid
    elif fid in INSIDE:
        angle = 0
        if fid.startswith('R_Axial'):
            a, c = pads[0].GetPosition(), pads[1].GetPosition(); angle = 90 if abs(a.x - c.x) < abs(a.y - c.y) else 0
            cx, cy = p.ToMM(a.x + c.x) / 2, p.ToMM(a.y + c.y) / 2
        report['references'].append(place(ref, [(cx, cy)], 3, r, angle, frozenset({k}), k, .1))
    else:
        anchors = PREF.get(r, []) + [(cx, y0 - .8), (cx, y1 + .8), (x0 - 1.8, cy), (x1 + 1.8, cy)]
        report['references'].append(place(ref, anchors, 6, r, 90 if r=='TP3' else 0, frozenset({k}), k))

# ---- Optional keyed-header marks: in line with the key pin, board side of the box --------------------------------------
KEYS = {}
for r, key in KEYS.items():
    f = next(q for q in fps if q.GetReference() == r); k = index[r]; x0, y0, x1, y1 = cbox[k]
    kp = next(a for a in f.Pads() if a.GetNumber() == key).GetPosition(); kx, ky = p.ToMM(kp.x), p.ToMM(kp.y)
    ed = {'T': y0, 'B': BH - y1, 'L': x0, 'R': BW - x1}; e = min(ed, key=ed.get)
    anc = {'T': (kx, y1 + .9), 'B': (kx, y0 - .9), 'L': (x1 + 1.2, ky), 'R': (x0 - 1.2, ky)}[e]
    t = p.PCB_TEXT(b); t.SetText(f'KEY {key}'); t.SetTextSize(xy(.8, .8)); t.SetTextThickness(mm(.12)); t.SetLayer(p.F_SilkS)
    report['legends'].append(place(t, [anc], 1.8, f'{r} KEY {key}', 90 if e in 'LR' else 0, frozenset(), 0, .1)); b.Add(t)
# ---- legends (text, x, y, size, angle, max shift) ------------------------------------------------------
LEG = [('EGRLab P06 I-LOGGER / R1',70,97,1,0,1),
 ('ILOG K2',103,3,1,0,2),('LV06',67,3,1,0,2),('ISERIES',30,3,1,0,2),
 ('SW1 A',27,77,1,0,1),('SW1 B',67,77,1,0,1),('PBV 5m',30,36,1,0,1),
 ('ECU',18,25,1,0,1),('EGR',30,25,1,0,1),('WARM',94,87,1,0,1)]
for r in ['J1','J2','J3','J4','J5']:
 fp=next(f for f in fps if f.GetReference()==r)
 for pad in fp.Pads():
  if pad.GetNumber() and (r!='J2' or pad.GetNumber() in ['1','2']):
   pt=pad.GetPosition();LEG.append((pad.GetNumber(),p.ToMM(pt.x),p.ToMM(pt.y)+ (-3.5 if r in ['J3','J4'] else -2 if r=='J5' else -2 if r=='J2' and int(pad.GetNumber())%2 else 2),.8,0,.6))

exempt = frozenset(index[r] for r in HARNESS)
for text, x, y, size, angle, lim in LEG:
    t = p.PCB_TEXT(b); t.SetText(text); t.SetTextSize(xy(size, size)); t.SetTextThickness(mm(.15 if size >= 1 else .12)); t.SetLayer(p.F_SilkS)
    report['legends'].append(place(t, [(x, y)], lim, text, angle, exempt)); b.Add(t)
report['legend_texts'] = sorted({x[0] for x in LEG} | {f'KEY {k}' for k in KEYS.values()})
p.SaveBoard(str(fn), b, True)
rep.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print('references', len(report['references']), 'max shift', max(r['shift_mm'] for r in report['references']),
      '| legends', len(report['legends']), 'max shift', max(r['shift_mm'] for r in report['legends']))



