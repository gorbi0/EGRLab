"""P02 R4 silkscreen (format S1). Run after run_layout.py; changes only F.SilkS (and hides values), never copper.
1. Footprint silk graphics that would break DRC are dropped at file level (sexpr; pcbnew Remove() breaks SWIG, P03 lesson):
   silk beyond the board edge (connectors whose body or pins stand over edge A, B or the input wall) and silk lines over the
   exposed copper of other parts. F.Fab keeps every outline for the assembly drawing.
2. Every reference is placed at the first candidate position (inside its own courtyard, then around it, horizontal or vertical,
   1.0 mm, then 0.8 mm) that is inside the board, off every pad (0.25 mm), off other courtyards and off already placed silk.
3. Board texts: name 'P02 R4 S1-2/3 S2–S3', edge markers A and B, pin 1 of every connector, service-pin labels read from edge B.
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
drop = set()
for f in b.GetFootprints():
    for g in f.GraphicalItems():
        if g.GetLayer() not in (p.F_SilkS, p.B_SilkS) or isinstance(g, p.PCB_TEXT):
            continue
        bb = bbox_of(g)
        outside = bb[0] < EDGE or bb[1] < EDGE or bb[2] > W - EDGE or bb[3] > H - EDGE
        over = any(r != f.GetReference() and hit(bb, pb, .15) for r, pb in (botpads if g.GetLayer() == p.B_SilkS else padboxes))
        if outside or over:
            drop.add(g.m_Uuid.AsString())
tree = parse(fn.read_text(encoding='utf-8'))
n_drop = 0
for fp in sub(tree, 'footprint'):
    for g in list(fp):
        if isinstance(g, list) and g and g[0] in ('fp_line', 'fp_rect', 'fp_circle', 'fp_arc', 'fp_poly'):
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
silk = []  # boxes of silk already on the board (footprint graphics) + placed texts
for f in b.GetFootprints():
    for g in f.GraphicalItems():
        if g.GetLayer() == p.F_SilkS and not isinstance(g, p.PCB_TEXT):
            silk.append((f.GetReference(), bbox_of(g)))
placed = []; placed_b = []


def free(box, own, bottom=False):
    if box[0] < EDGE + .2 or box[1] < EDGE + .2 or box[2] > W - EDGE - .2 or box[3] > H - EDGE - .2:
        return False
    if any(hit(box, pb, .25) for r, pb in (botpads if bottom else padboxes)):
        return False
    if not bottom and (any(hit(box, sb, .2) for r, sb in silk if r != own) or any(hit(box, tb, .2) for tb in placed)):
        return False
    if bottom and any(hit(box, tb, .2) for tb in placed_b):
        return False
    corners = [(box[0] + (box[2] - box[0]) * i / 4, box[1] + (box[3] - box[1]) * j / 2) for i in range(5) for j in range(3)]
    return not any(r != own and fps[r].IsFlipped() == bottom and cy.Contains(p.VECTOR2I(mm(x), mm(y))) for r, cy in yards.items() for x, y in corners)


def text_box(t):
    return bbox_of(t)


missing = []
for r in sorted(fps, key=lambda r: yards[r].BBox().GetArea()):
    f = fps[r]; ref = f.Reference(); f.Value().SetVisible(False)
    if r.startswith('H'):
        ref.SetVisible(False); continue
    cb = yards[r].BBox(); x0, y0, x1, y1 = p.ToMM(cb.GetLeft()), p.ToMM(cb.GetTop()), p.ToMM(cb.GetRight()), p.ToMM(cb.GetBottom())
    cx, cy_ = (x0 + x1) / 2, (y0 + y1) / 2
    ok = False
    for size in (1.0, .8):
        cands = [(cx, cy_, 0), (cx, cy_, 90), (cx, y0 - size * .8, 0), (cx, y1 + size * .8, 0), (x0 - size * .8, cy_, 90), (x1 + size * .8, cy_, 90)]
        for dx in (-3, 3, -6, 6):
            cands += [(cx + dx, y0 - size * .8, 0), (cx + dx, y1 + size * .8, 0)]
        for dy in (-3, 3):
            cands += [(x0 - size * .8, cy_ + dy, 90), (x1 + size * .8, cy_ + dy, 90)]
        for x, y, a in cands:
            ref.SetTextSize(p.VECTOR2I(mm(size), mm(size))); ref.SetTextThickness(mm(.15 if size == 1.0 else .12))
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
    for x, y in spots:
        a = p.PCB_TEXT(b); a.SetText(t); a.SetPosition(p.VECTOR2I(mm(x), mm(y))); a.SetTextSize(p.VECTOR2I(mm(size * .9), mm(size)))
        a.SetTextThickness(mm(.15 if size >= 1 else .12)); a.SetLayer(p.F_SilkS); a.SetTextAngle(p.EDA_ANGLE(angle, p.DEGREES_T))
        if just == 'left': a.SetHorizJustify(p.GR_TEXT_H_ALIGN_LEFT)
        if just == 'right': a.SetHorizJustify(p.GR_TEXT_H_ALIGN_RIGHT)
        if free(text_box(a), None):
            b.Add(a); placed.append(text_box(a)); return (x, y)
    extra.append(t); return None


# ---- 3. board texts ----
res = {}
res['title'] = place_text('P02 R4 S1-2/3 S2–S3', [(x, y) for y in (88.5, 87.5, 16.5, 12, 90.5) for x in (53, 55, 50, 60, 30, 20)], 1.2)
res['edge_A'] = place_text('KRAWEDZ A (P12)', [(x, y) for y in (1.3, 2, 9.5, 11) for x in (62, 55, 60, 35, 20, 12)], .9)
res['edge_B'] = place_text('KRAWEDZ B (SERWIS)', [(x, y) for y in (98.6, 98, 92.5, 91.5) for x in (53, 55, 50, 58, 5, 101)], .9)
# pin 1 of every connector
for r in ('J_BP', 'J_SV1', 'J_SV2', 'J1', 'J2', 'J14'):
    a = next(q for q in fps[r].Pads() if q.GetNumber() == '1'); ax, ay = p.ToMM(a.GetPosition().x), p.ToMM(a.GetPosition().y); s = max(p.ToMM(a.GetSize().x), p.ToMM(a.GetSize().y)) / 2 + .9
    res['pin1_' + r] = place_text('1', [(ax + dx, ay + dy) for dx, dy in [(-s, 0), (s, 0), (0, -s), (0, s), (-s, -s), (s, -s), (-s, s), (s, s)]], .9)
# service labels, vertical, read from edge B
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
        tx = p.PCB_TEXT(b); tx.SetText(t); tx.SetTextSize(p.VECTOR2I(mm(.7), mm(.8))); tx.SetTextThickness(mm(.12)); tx.SetLayer(p.F_SilkS)
        tx.SetTextAngle(p.EDA_ANGLE(90, p.DEGREES_T)); tx.SetHorizJustify(p.GR_TEXT_H_ALIGN_LEFT); tx.SetPosition(p.VECTOR2I(mm(x), mm(93.9)))
        b.Add(tx); placed.append(text_box(tx)); labels[f'{hdr}.{a.GetNumber()}'] = t
p.SaveBoard(str(fn), b)
rep = {'dropped_footprint_silk': n_drop, 'hidden_references': missing, 'board_texts': res, 'unplaced_texts': extra, 'service_labels': labels}
(P / 'routing/silkscreen.json').write_text(json.dumps(rep, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
print('silk: dropped', n_drop, 'footprint graphics; hidden references', missing, '; unplaced texts', extra)
