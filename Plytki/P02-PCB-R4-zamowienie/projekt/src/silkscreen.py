"""P02 R4 silkscreen (format S1). Run after run_layout.py; changes only F.SilkS (and hides values), never copper.
1. Footprint silk graphics that would break DRC are dropped at file level (sexpr; pcbnew Remove() breaks SWIG, P03 lesson):
   silk beyond the board edge (connectors whose body or pins stand over edge A, B or the input wall) and silk lines over the
   exposed copper of other parts. F.Fab keeps every outline for the assembly drawing.
2. Every reference is placed at the first candidate position (inside its own courtyard, then around it, horizontal or vertical,
   1.0 mm, then 0.8 mm) that is inside the board, off every pad (0.25 mm), off other courtyards and off already placed silk.
3. Board texts: name 'P02 R4 S1-L S1–S3', edge markers A and B, pin 1 of every connector, service-pin labels read from edge B.
Klasa L (29.09, lokalnie): KiCad 10 reports a reference over its own footprint silk and over footprint texts (cathode 'K'),
so references avoid all silk; service labels are placed first (fixed positions) and references avoid them; footprint silk
lines over another footprint's silk and footprint texts beyond the edge clearance are dropped too. Every drop is listed per
part in routing/silkscreen.json: verify_pcb.py accepts a DRC lib_footprint_mismatch only for these parts. The board name
keeps out of the service-label zones (y > 86 above the headers), where verify_pcb.py counts one label per pin.
"""
from pathlib import Path
import pcbnew as p, json, math, sys
from sexpr import parse, dump, sub, one
P = Path(__file__).resolve().parents[1]; fn = P / 'eda/P02.kicad_pcb'
sys.path.insert(0, str(P / 'src'))
from build_board import W, Hh as H
EDGE = .3   # silk-to-edge clearance used by DRC (board setting min_silk... edge 0.3 is KiCad default for silk_edge_clearance)
LABEL = {'P02_ENABLE': 'ENABLE', 'P02_SUP5_N': 'SUP5N', 'PSU_OK': 'PSU_OK', 'SAFE_N': 'SAFE_N', 'P04_3V3': 'P04_3V', 'P02_UV_CMP': 'UV_CMP',
         'P02_OK': 'OK', 'P02_AUX5': 'AUX5', 'PFAIL_N': 'PFAIL', 'P02_REF': 'REF', 'P02_UV_DIV': 'UV_DIV', 'P02_GATE': 'GATE', 'VBAT_SENSE': 'VBAT',
         'VMOTOR': 'VMOTOR', 'P02_BAT_IN': 'BAT_IN', '3V3_IO': '3V3', 'P02_OFF_G': 'OFF_G', 'P02_SW_COM': 'SW_COM', 'P02_VSW': 'VSW', 'P02_VLOG': 'VLOG',
         '5V_SYS': '5V', 'P02_HOLD_C': 'HOLD_C', 'GND': 'GND'}


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
for _, g in ftexts:   # 2.10: footprint user texts up to the legend minimum
    if p.ToMM(g.GetTextHeight()) < 1.0 or p.ToMM(g.GetTextThickness()) < .15:
        k = 1.0 / p.ToMM(g.GetTextHeight()); g.SetTextSize(p.VECTOR2I(mm(p.ToMM(g.GetTextWidth()) * k), mm(1.0))); g.SetTextThickness(mm(.15))
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


def text_box(t):
    return bbox_of(t)


# service labels, vertical, read from edge B
MIN_H, MIN_T = 1.0, .15   # 2.10 (independent reviews of P05 R3 / P06 R2): JLCPCB legend minimum, character 1.0 mm, line 0.15 mm
labels = {}
for hdr in ('J_SV1', 'J_SV2'):
    for a in fps[hdr].Pads():
        n = a.GetNetname().split('/')[-1]; x = p.ToMM(a.GetPosition().x)
        node = n if n == 'GND' else next(q.GetNetname().split('/')[-1] for f in b.GetFootprints() if f.GetReference().startswith('R') for q in f.Pads()
                                          if q.GetNetname() == a.GetNetname() and not any(z is q for z in [])) and None
        if n != 'GND':  # node = the net on the other side of the series resistor
            r = next(f for f in b.GetFootprints() if f.GetReference() != hdr for q in f.Pads() if q.GetNetname() == a.GetNetname())
            node = next(q.GetNetname().split('/')[-1] for q in r.Pads() if q.GetNetname() != a.GetNetname())
        t = LABEL[node]
        tx = p.PCB_TEXT(b); tx.SetText(t); tx.SetTextSize(p.VECTOR2I(mm(.9 * MIN_H), mm(MIN_H))); tx.SetTextThickness(mm(MIN_T)); tx.SetLayer(p.F_SilkS)
        tx.SetTextAngle(p.EDA_ANGLE(90, p.DEGREES_T)); tx.SetHorizJustify(p.GR_TEXT_H_ALIGN_LEFT); tx.SetPosition(p.VECTOR2I(mm(x), mm(93.9)))
        b.Add(tx); placed.append(text_box(tx)); labels[f'{hdr}.{a.GetNumber()}'] = t
missing = []
for r in sorted(fps, key=lambda r: yards[r].BBox().GetArea()):
    f = fps[r]; ref = f.Reference(); f.Value().SetVisible(False)
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
        for x, y, a in cands:
            ref.SetTextSize(p.VECTOR2I(mm(size), mm(size))); ref.SetTextThickness(mm(MIN_T))
            ref.SetTextAngle(p.EDA_ANGLE(a, p.DEGREES_T)); ref.SetPosition(p.VECTOR2I(mm(x), mm(y)))
            bx = text_box(ref)
            if free(bx, r, f.IsFlipped()):
                (placed_b if f.IsFlipped() else placed).append(bx); ok = True; break
        if ok:
            break
    ref.SetVisible(ok)
    if not ok:
        missing.append(r)


def txt(t, x, y, size=1.0, angle=0, thick=.15, just=None):
    a = p.PCB_TEXT(b); a.SetText(t); a.SetPosition(p.VECTOR2I(mm(x), mm(y))); a.SetTextSize(p.VECTOR2I(mm(size * .9), mm(size)))
    a.SetTextThickness(mm(thick)); a.SetLayer(p.F_SilkS); a.SetTextAngle(p.EDA_ANGLE(angle, p.DEGREES_T))
    if just == 'left':
        a.SetHorizJustify(p.GR_TEXT_H_ALIGN_LEFT)
    elif just == 'right':
        a.SetHorizJustify(p.GR_TEXT_H_ALIGN_RIGHT)
    b.Add(a); placed.append(text_box(a)); return a


extra = []
def place_text(t, spots, size=1.0, angle=0, just=None):
    size = max(size, MIN_H)   # 2.10: edge markers / pin marks were 0.9 mm
    for x, y in spots:
        a = p.PCB_TEXT(b); a.SetText(t); a.SetPosition(p.VECTOR2I(mm(x), mm(y))); a.SetTextSize(p.VECTOR2I(mm(size * .9), mm(size)))
        a.SetTextThickness(mm(MIN_T)); a.SetLayer(p.F_SilkS); a.SetTextAngle(p.EDA_ANGLE(angle, p.DEGREES_T))
        if just == 'left': a.SetHorizJustify(p.GR_TEXT_H_ALIGN_LEFT)
        if just == 'right': a.SetHorizJustify(p.GR_TEXT_H_ALIGN_RIGHT)
        if free(text_box(a), None):
            b.Add(a); placed.append(text_box(a)); return (x, y)
    extra.append(t); return None


# ---- 3. board texts ----
res = {}
LABEL_ZONES = [(9.0, 44.5), (116.0, 151.5)]   # x ranges of J_SV1 / J_SV2 labels (y > 86): the title stays out of them
res['title'] = place_text('P02 R4 S1-L S1–S3', [(x, y) for y in (88.5, 87.5, 90.5, 16.5, 12) for x in (80, 70, 90, 60, 100, 53, 30, 20)
                                                  if y < 86 or not any(a - 10 < x < c + 10 for a, c in LABEL_ZONES)], 1.2)
res['edge_A'] = place_text('KRAWEDZ A (P12)', [(x, y) for y in (1.3, 2, 9.5, 11) for x in (62, 55, 60, 35, 20, 12)], .9)
res['edge_B'] = place_text('KRAWEDZ B (SERWIS)', [(x, y) for y in (98.6, 98, 92.5, 91.5) for x in (53, 55, 50, 58, 5, 101)], .9)
# pin 1 of every connector
for r in ('J_BP', 'J_SV1', 'J_SV2', 'J1', 'J2', 'J14'):
    a = next(q for q in fps[r].Pads() if q.GetNumber() == '1'); ax, ay = p.ToMM(a.GetPosition().x), p.ToMM(a.GetPosition().y); s = max(p.ToMM(a.GetSize().x), p.ToMM(a.GetSize().y)) / 2 + .9
    res['pin1_' + r] = place_text('1', [(ax + dx, ay + dy) for dx, dy in [(-s, 0), (s, 0), (0, -s), (0, s), (-s, -s), (s, -s), (-s, s), (s, s)]], .9)
p.SaveBoard(str(fn), b)
rep = {'dropped_footprint_silk': n_drop, 'dropped_by_part': dict(sorted(drop_by.items())), 'moved_texts_by_part': dict(sorted(moved_by.items())),
       'hidden_references': missing, 'board_texts': res, 'unplaced_texts': extra, 'service_labels': labels}
(P / 'routing/silkscreen.json').write_text(json.dumps(rep, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
print('silk: dropped', n_drop, 'footprint graphics; hidden references', missing, '; unplaced texts', extra)
