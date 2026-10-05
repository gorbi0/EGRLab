"""P11 R2 silkscreen (4.10.2026; steps 1-2 and the reference placement copied from P10 R2 silkscreen.py, chain of P03 R6). Run after
run_layout.py; changes only F.SilkS (and hides values), never copper. Steps: footprint silk that would break DRC dropped at file
level; board texts (title, J_P12 pin 1, panel-edge marker, one label per wire-field column with the panel contact it goes to, the R1
variant note); references placed at the first free candidate. Every drop is listed in routing/silkscreen.json.
User 4.10: P11 is the wiring board of the panel, so every field column carries the name of its contact; legend >= 1.0 mm / 0.15 mm.
FIELD_LABELS is the drawing table only: verify_pcb.py resolves every printed label against the schematic (parts.json contacts
X11-X17 / X6, docs/PORTY.csv cavities), so a wrong or swapped label fails there.
"""
from pathlib import Path
import pcbnew as p, json, math, sys
from sexpr import parse, dump, sub, one
P = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(P / 'src'))
from board import NAME, REV, JBP, JSV, PIN_MARKS, HOLES, HOLE_ZONE_D
TYTUL = f'{REV} PANEL'
fn = P / f'eda/{NAME}.kicad_pcb'
from build_board import W, Hh as H, holes
STREFY = [(hx, hy) for hx, hy in holes()]; RZ_M3 = HOLE_ZONE_D / 2   # P09 1.10: text in a D7 zone hides under the standoff washer
MIN_H, MIN_T = 1.0, .15   # 2.10 (independent reviews of P05 R3 / P06 R2): JLCPCB legend minimum, character 1.0 mm, line 0.15 mm
EDGE = .3
# One label per column of a wire field, left-justified on the inner side of the pads (the wires leave towards the panel edge x = 0).
# J11 columns = R1 pairs (P11-R1 docs/WIAZKI.md W8): Xnn.a-b = the two functional terminals of one panel contact.
FIELD_LABELS = {
    'J11': {('1', '2'): 'X15.1-2 KLUCZ', ('3', '4'): 'X12.1-2 L1 NC', ('5', '6'): 'X12.3-4 L1 NC', ('7', '8'): 'X13.1-2 L2 NC',
            ('9', '10'): 'X13.3-4 L2 NC', ('11', '12'): 'X16.1-2 STOP', ('13', '14'): 'X11.1-2 ARM', ('15', '16'): 'X14.1-2 MARK',
            ('17', '18'): 'X17.1-2 TEST'},
    'J8': {('1',): 'TEST kom.10', ('2',): 'TEST kom.11'},
    'J6': {('1',): 'SCOPE srodek', ('2',): 'SCOPE ekran'},
}
VARIANT = ['R1 100R', 'LOGGER: LUTOWAC', 'Z P04: DNP']   # P11-3: R1 only without P04 (the only PANEL_3V3 source then)


def bbox_of(item):
    r = item.GetBoundingBox(); return (p.ToMM(r.GetLeft()), p.ToMM(r.GetTop()), p.ToMM(r.GetRight()), p.ToMM(r.GetBottom()))


def hit(a, c, m=0.0):
    return a[0] - m < c[2] and c[0] - m < a[2] and a[1] - m < c[3] and c[1] - m < a[3]


# ---- 1. drop footprint silk that breaks DRC (file level) ----
b = p.LoadBoard(str(fn))
padboxes = [(f.GetReference(), bbox_of(a)) for f in b.GetFootprints() for a in f.Pads() if a.IsOnLayer(p.F_Cu) or a.GetAttribute() == p.PAD_ATTRIB_NPTH]
botpads = [(f.GetReference(), bbox_of(a)) for f in b.GetFootprints() for a in f.Pads() if a.IsOnLayer(p.B_Cu)]
drop = set(); drop_by = {}
area = {}
for f in b.GetFootprints():
    f.BuildCourtyardCaches(); c = f.GetCourtyard(p.B_CrtYd if f.IsFlipped() else p.F_CrtYd); area[f.GetReference()] = c.Area() if c.OutlineCount() else 0
fsilk = [(f.GetReference(), g.GetLayer(), bbox_of(g), g) for f in b.GetFootprints() for g in f.GraphicalItems()
         if g.GetLayer() in (p.F_SilkS, p.B_SilkS) and not isinstance(g, p.PCB_TEXT)]
for f in b.GetFootprints():
    for g in f.GraphicalItems():
        if g.GetLayer() not in (p.F_SilkS, p.B_SilkS):
            continue
        bb = bbox_of(g); r0 = f.GetReference()
        outside = bb[0] < EDGE or bb[1] < EDGE or bb[2] > W - EDGE or bb[3] > H - EDGE
        if isinstance(g, p.PCB_TEXT):   # footprint user text (not the reference / value fields): only beyond the edge
            over = False
        else:
            over = any(r != r0 and hit(bb, pb, .15) for r, pb in (botpads if g.GetLayer() == p.B_SilkS else padboxes))
            # silk line on the silk of another part of the same side: the smaller part gives way (exact shape test)
            if not over:
                for r, L, sb, g2 in fsilk:
                    if r == r0 or L != g.GetLayer() or not hit(bb, sb, .15) or area.get(r0, 0) > area.get(r, 0):
                        continue
                    a1, a2 = p.SHAPE_POLY_SET(), p.SHAPE_POLY_SET()
                    g.TransformShapeToPolygon(a1, L, p.FromMM(.075), p.FromMM(.01), p.ERROR_OUTSIDE)
                    g2.TransformShapeToPolygon(a2, L, p.FromMM(.075), p.FromMM(.01), p.ERROR_OUTSIDE)
                    a1.BooleanIntersection(a2)
                    if a1.OutlineCount():
                        over = True; break
        if outside or over:
            drop.add(g.m_Uuid.AsString()); drop_by[r0] = drop_by.get(r0, 0) + 1
tree = parse(fn.read_text(encoding='utf-8'))
n_drop = 0
for fp in sub(tree, 'footprint'):
    for g in list(fp):
        if isinstance(g, list) and g and g[0] in ('fp_line', 'fp_rect', 'fp_circle', 'fp_arc', 'fp_poly', 'fp_text'):
            u = next((x[1] for x in g if isinstance(x, list) and x and x[0] == 'uuid'), None)
            if u in drop:
                fp.remove(g); n_drop += 1
tree = [g for g in tree if not (isinstance(g, list) and g and g[0] == 'gr_text' and any(isinstance(x, list) and x and x[0] == 'layer' and x[1] == 'F.SilkS' for x in g))]
fn.write_text(dump(tree) + '\n', encoding='utf-8')
# ---- 2. references ----
b = p.LoadBoard(str(fn)); mm = p.FromMM
fps = {f.GetReference(): f for f in b.GetFootprints()}
yards = {}
for r, f in fps.items():
    f.BuildCourtyardCaches(); c = f.GetCourtyard(p.B_CrtYd if f.IsFlipped() else p.F_CrtYd); yards[r] = c
silk = []  # boxes of silk already on the board (footprint graphics and footprint texts, own part included) + placed texts
for f in b.GetFootprints():
    for g in f.GraphicalItems():
        if g.GetLayer() == p.F_SilkS:
            silk.append((f.GetReference(), bbox_of(g)))
placed = []; placed_b = []
# 30.09: a footprint text (the cathode 'K' of the DO-35 / DO-15 vertical diodes) that touches silk of its own or another part
# moves to the nearest free spot (0.2 mm grid, up to 3 mm); DRC reports these as silk_overlap inside one footprint. Listed per part.
moved_by = {}
ftexts = [(f.GetReference(), g) for f in b.GetFootprints() for g in f.GraphicalItems() if g.GetLayer() == p.F_SilkS and isinstance(g, p.PCB_TEXT)]
for r0, g in ftexts:
    ob = bbox_of(g); others = [sb for r, sb in silk if sb != ob]
    if not any(hit(ob, sb, .2) for sb in others):
        continue
    x0, y0 = p.ToMM(g.GetPosition().x), p.ToMM(g.GetPosition().y); done = False
    offs = sorted(((i * .2, j * .2) for i in range(-15, 16) for j in range(-15, 16) if (i, j) != (0, 0)), key=lambda q: (math.hypot(*q), q))
    for ddx, ddy in offs:
        g.SetPosition(p.VECTOR2I(mm(x0 + ddx), mm(y0 + ddy))); bx = bbox_of(g)
        if not any(hit(bx, sb, .2) for sb in others) and not any(hit(bx, pb, .25) for r, pb in padboxes) \
                and EDGE + .2 < bx[0] and bx[2] < W - EDGE - .2 and EDGE + .2 < bx[1] and bx[3] < H - EDGE - .2 \
                and not any(r != r0 and not fps[r].IsFlipped() and cy.Contains(p.VECTOR2I(mm((bx[0] + bx[2]) / 2), mm((bx[1] + bx[3]) / 2))) for r, cy in yards.items()):
            done = True; break
    if not done:
        g.SetPosition(p.VECTOR2I(mm(x0), mm(y0))); continue
    silk = [(r, sb) for r, sb in silk if not (r == r0 and sb == ob)] + [(r0, bbox_of(g))]
    moved_by[r0] = moved_by.get(r0, 0) + 1


def free(box, own, bottom=False):
    if any(math.hypot(max(box[0] - hx, 0, hx - box[2]), max(box[1] - hy, 0, hy - box[3])) < RZ_M3 for hx, hy in STREFY):
        return False
    if box[0] < EDGE + .2 or box[1] < EDGE + .2 or box[2] > W - EDGE - .2 or box[3] > H - EDGE - .2:
        return False
    if any(hit(box, pb, .25) for r, pb in (botpads if bottom else padboxes)):
        return False
    if not bottom and (any(hit(box, sb, .2) for r, sb in silk) or any(hit(box, tb, .2) for tb in placed)):
        return False
    if bottom and any(hit(box, tb, .2) for tb in placed_b):
        return False
    corners = [(box[0] + (box[2] - box[0]) * i / 4, box[1] + (box[3] - box[1]) * j / 2) for i in range(5) for j in range(3)]
    return not any(r != own and fps[r].IsFlipped() == bottom and cy.Contains(p.VECTOR2I(mm(x), mm(y))) for r, cy in yards.items() for x, y in corners)


def najblizej_wlasnej(box, own, bottom=False):
    """1.10 (recenzja): oznaczenie musi być wyraźnie bliżej własnego obrysu niż każdego innego (było: R1 1 mm od R5, 4,9 mm od R1)."""
    c = p.VECTOR2I(mm((box[0] + box[2]) / 2), mm((box[1] + box[3]) / 2))
    d = lambda poly: 0.0 if poly.Contains(c) else math.sqrt(poly.SquaredDistance(c)) / 1e6
    mine = d(yards[own])
    return all(mine + .3 < d(cy) for r, cy in yards.items() if r != own and fps[r].IsFlipped() == bottom)


def text_box(t):
    return bbox_of(t)


placed_fixed = []
extra = []


def place_text(t, spots, size=1.0, angle=0, just=None, own=None):
    size = max(size, MIN_H)
    for x, y in spots:
        a = p.PCB_TEXT(b); a.SetText(t); a.SetPosition(p.VECTOR2I(mm(x), mm(y))); a.SetTextSize(p.VECTOR2I(mm(size * .9), mm(size)))
        a.SetTextThickness(mm(MIN_T)); a.SetLayer(p.F_SilkS); a.SetTextAngle(p.EDA_ANGLE(angle, p.DEGREES_T))
        if just == 'left': a.SetHorizJustify(p.GR_TEXT_H_ALIGN_LEFT)
        if just == 'right': a.SetHorizJustify(p.GR_TEXT_H_ALIGN_RIGHT)
        if free(text_box(a), own):
            b.Add(a); placed.append(text_box(a)); return (round(x, 3), round(y, 3))
    extra.append(t); return None


# ---- 3. board texts (before the references, which then avoid them) ----
res = {}; labels = {}
for fld, cols in FIELD_LABELS.items():   # one label per column: left-justified 0.6 mm right of the innermost pad of the column
    for pads, t in cols.items():
        q = [a for a in fps[fld].Pads() if a.GetNumber() in pads]; assert len(q) == len(pads), (fld, pads)
        ys = {round(p.ToMM(a.GetPosition().y), 3) for a in q}; assert len(ys) == 1, (fld, pads, ys)   # one column = one y
        x0 = max(p.ToMM(a.GetPosition().x) + p.ToMM(a.GetSize().x) / 2 for a in q) + .6; y0 = ys.pop()
        res[f'{fld}:{"/".join(pads)}'] = place_text(t, [(x0 + dx, y0) for dx in (0, .2, .4)], 1.0, just='left', own=fld)
        labels['/'.join(f'{fld}.{n}' for n in pads)] = t
# J_P12 pin 1: '1' next to the pad, outside the header body (body front towards y = 0)
for r in JBP:
    a = next(q for q in fps[r].Pads() if q.GetNumber() == '1'); ax, ay = p.ToMM(a.GetPosition().x), p.ToMM(a.GetPosition().y)
    s_ = max(p.ToMM(a.GetSize().x), p.ToMM(a.GetSize().y)) / 2 + .9
    res['pin1_' + r] = place_text('1', [(ax + dx * k, ay + dy * k) for k in (1, 1.5) for dx, dy in [(-s_, 0), (0, s_), (-s_, s_), (s_, s_), (s_, 0)]], 1.0, own=r)
# R1 variant note: three lines beside R1 (left of it first: free strip between the upper M3 zones)
r1 = yards['R1'].BBox(); rx0, ry0, rx1, ry1 = p.ToMM(r1.GetLeft()), p.ToMM(r1.GetTop()), p.ToMM(r1.GetRight()), p.ToMM(r1.GetBottom())
res['variant'] = None
for x0, y0, just in [(rx0 - .4, ry0 + .2, 'right'), (rx0 - .4, ry0 - .6, 'right'), (rx1 + .4, ry1 + .9, 'left'), ((rx0 + rx1) / 2 - 6, ry1 + .9, 'left')]:
    trial = []
    for i, t in enumerate(VARIANT):
        a_ = p.PCB_TEXT(b); a_.SetText(t); a_.SetPosition(p.VECTOR2I(mm(x0), mm(y0 + 1.7 * i))); a_.SetTextSize(p.VECTOR2I(mm(.9 * MIN_H), mm(MIN_H)))
        a_.SetTextThickness(mm(MIN_T)); a_.SetLayer(p.F_SilkS)
        a_.SetHorizJustify(p.GR_TEXT_H_ALIGN_RIGHT if just == 'right' else p.GR_TEXT_H_ALIGN_LEFT); trial.append(a_)
    if all(free(text_box(a_), 'R1') for a_ in trial):
        for a_ in trial:
            b.Add(a_); placed.append(text_box(a_))
        res['variant'] = (round(x0, 3), round(y0, 3), just); break
if res['variant'] is None:
    extra.append('VARIANT')
# title and the panel-edge marker in the free inner strip
res['title'] = place_text(TYTUL, [(x, y) for y in (62.0, 63.0, 61.0, 79.0, 80.0, 90.0) for x in (27.5, 28.0, 27.0, 26.0)], 1.2)
res['title2'] = place_text('EGRLab 10.2026', [(x, y) for y in (64.2, 65.2, 81.2, 82.2, 92.2) for x in (27.5, 28.0, 27.0, 26.0)], 1.0)
res['panel'] = place_text('STRONA PANELU', [(x, y) for x in (1.5, 1.7) for y in (69.5, 70.0, 69.0, 68.0, 71.0)], 1.0, angle=90)
missing = []
# P11 (4.10): preferred spots first. J_P12: behind the pins, not on the box header body (the generic search put it on the body,
# hidden after assembly); R1: under its own pads (the first generic candidates hit its silk or the M3 zone and it ended 5 mm away).
PREF = {'J_P12': [(11.0, 15.45), (12.0, 15.45), (10.0, 15.5), (13.0, 15.45)], 'R1': [(25.5, 20.4), (25.5, 20.8), (24.8, 20.6)]}
done = set()
for r, spots in PREF.items():
    ref = fps[r].Reference(); fps[r].Value().SetVisible(False)
    for x, y in spots:
        ref.SetTextSize(p.VECTOR2I(mm(MIN_H), mm(MIN_H))); ref.SetTextThickness(mm(MIN_T)); ref.SetTextAngle(p.EDA_ANGLE(0, p.DEGREES_T))
        ref.SetPosition(p.VECTOR2I(mm(x), mm(y))); bx = text_box(ref)
        if free(bx, r) and najblizej_wlasnej(bx, r):
            placed.append(bx); ref.SetVisible(True); done.add(r); break
for r in sorted(fps, key=lambda r: (yards[r].BBox().GetArea(), r)):   # 30.09: ties by reference (board order follows random UUIDs)
    f = fps[r]; ref = f.Reference(); f.Value().SetVisible(False)
    if r in done:
        continue
    if r.startswith('H'):
        ref.SetVisible(False); continue
    cb = yards[r].BBox(); x0, y0, x1, y1 = p.ToMM(cb.GetLeft()), p.ToMM(cb.GetTop()), p.ToMM(cb.GetRight()), p.ToMM(cb.GetBottom())
    cx, cy_ = (x0 + x1) / 2, (y0 + y1) / 2
    ok = False
    for size in (MIN_H,):   # 2.10: no 0.8 mm fallback (JLCPCB legend minimum); a reference without room is hidden (F.Fab)
        cands = [(cx, cy_, 0), (cx, cy_, 90), (cx, y0 - size * .8, 0), (cx, y1 + size * .8, 0), (x0 - size * .8, cy_, 90), (x1 + size * .8, cy_, 90)]
        for dx in (-3, 3, -6, 6):
            cands += [(cx + dx, y0 - size * .8, 0), (cx + dx, y1 + size * .8, 0)]
        for dy in (-3, 3):
            cands += [(x0 - size * .8, cy_ + dy, 90), (x1 + size * .8, cy_ + dy, 90)]
        # 30.09 second ring (tried only after the first): half steps, one and two text heights further out, text beside the part
        d = size * .8; half = len(ref.GetText()) * size * .45 + .3
        for dx in (-1.5, 1.5, -4.5, 4.5):
            cands += [(cx + dx, y0 - d, 0), (cx + dx, y1 + d, 0)]
        for dy in (-1.5, 1.5, -4.5, 4.5, -6, 6):
            cands += [(x0 - d, cy_ + dy, 90), (x1 + d, cy_ + dy, 90)]
        for k in (2, 3):
            cands += [(cx, y0 - k * d, 0), (cx, y1 + k * d, 0), (x0 - k * d, cy_, 90), (x1 + k * d, cy_, 90)]
        cands += [(x0 - half, cy_, 0), (x1 + half, cy_, 0), (cx, y0 - half, 90), (cx, y1 + half, 90)]
        for x, y, a in cands:
            ref.SetTextSize(p.VECTOR2I(mm(size), mm(size))); ref.SetTextThickness(mm(MIN_T))
            ref.SetTextAngle(p.EDA_ANGLE(a, p.DEGREES_T)); ref.SetPosition(p.VECTOR2I(mm(x), mm(y)))
            bx = text_box(ref)
            if free(bx, r, f.IsFlipped()) and najblizej_wlasnej(bx, r, f.IsFlipped()):
                (placed_b if f.IsFlipped() else placed).append(bx); ok = True; break
        if ok:
            break
    ref.SetVisible(ok)
    if not ok:
        missing.append(r)

p.SaveBoard(str(fn), b)
rep = {'dropped_footprint_silk': n_drop, 'dropped_by_part': dict(sorted(drop_by.items())), 'moved_texts_by_part': dict(sorted(moved_by.items())),
       'hidden_references': missing, 'board_texts': res, 'unplaced_texts': extra, 'field_labels': labels, 'variant_lines': VARIANT}
(P / 'routing/silkscreen.json').write_text(json.dumps(rep, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
print('silk: dropped', n_drop, 'footprint graphics; hidden references', missing, '; unplaced texts', extra)
sys.exit(1 if extra else 0)
