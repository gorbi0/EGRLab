"""P03 R6 silkscreen (format S1; the P02 R4 script with the P03 texts). Run after run_layout.py; changes only F.SilkS (and hides
values), never copper.
1. Footprint silk graphics that would break DRC are dropped at file level (sexpr; pcbnew Remove() breaks SWIG, P03 lesson):
   silk beyond the board edge (connectors whose body or pins stand over edge A or B) and silk lines over the exposed copper of
   other parts or over the silk of a larger part. F.Fab keeps every outline for the assembly drawing.
2. Every reference is placed at the first candidate position (inside its own courtyard, then around it, horizontal or vertical,
   1.0 mm, then 0.8 mm) that is inside the board, off every pad (0.25 mm), off other courtyards and off already placed silk.
3. Board texts: name 'P03 R6 S1-L', edge markers A and B, pin 1 of every connector, service-pin labels read from edge B.
Service labels (30.09, disputed, README): M1 stands over J_SV2 and SD1 over J_SV3 (both modules stop at the header courtyards),
so only 1.5 mm is left between the module silk and the pins. J_SV1 gets full names (vertical, as P02 R4); J_SV2 and J_SV3 get
three-letter abbreviations (horizontal, one per pin) and a legend block elsewhere on the board.
Every drop is listed per part in routing/silkscreen.json: verify_pcb.py accepts a DRC lib_footprint_mismatch only for these parts.
"""
from pathlib import Path
import pcbnew as p, json, math, sys
from sexpr import parse, dump, sub, one
P = Path(__file__).resolve().parents[1]; fn = P / 'eda/P03.kicad_pcb'
sys.path.insert(0, str(P / 'src'))
from build_board import W, Hh as H
EDGE = .3   # silk-to-edge clearance used by DRC (board setting min_silk... edge 0.3 is KiCad default for silk_edge_clearance)
LABEL = {  # J_SV1: full names, vertical
    'GND': 'GND', '5V_SYS': '5V_SYS', '5V_M1': '5V_M1', '3V3_CORE': '3V3', '3V3_IO': '3V3_IO', 'SUP_RAW_N': 'SUPRAW', 'SUP_N': 'SUP_N',
    'SUP_N_OUT': 'SUPOUT', 'PFAIL_N': 'PFAIL', 'I2C_SCL': 'SCL', 'I2C_SDA': 'SDA', 'SCOPE_TRIG': 'SCOPE',
    # 30.09 evening: J_SV1 holds the S1 nodes since the regrouping by node position (and LOGGER_CURRENT_OK since the gate swap)
    'MOTOR_INB': 'MOT_INB', 'MOTOR_INA': 'MOT_INA', 'MEAS_BANK': 'MBANK', 'CS_ITEST_N': 'ITEST_N', 'CS_ILOG_N': 'ILOG_N',
    'LOGGER_CURRENT_OK': 'LCUR_OK'}
ABBR = {  # J_SV2 / J_SV3: three letters, horizontal, with a legend
    'MEAS_EN': 'MEN', 'ADC_RESET': 'RST', 'ADC_CONVST': 'CNV', 'ADC_CS': 'ACS', 'ADC_BUSY': 'BSY', 'CS_ILOG_N': 'ILG', 'CS_ITEST_N': 'ITS',
    'CURRENT_CS_N': 'CCS', 'MEAS_BANK': 'MBK', 'SD_CS': 'SDC', 'TC1_CS': 'TC1', 'TC2_CS': 'TC2', 'PWM': 'PWM', 'HEARTBEAT': 'HBT',
    'MCU_ARM': 'ARM', 'HW_ARMED': 'HWA', 'INTERLOCK': 'ILK', 'SENSOR_ENABLE': 'SEN', 'CORE_LINK': 'LNK', 'MOTOR_INA': 'INA',
    'MOTOR_INB': 'INB', 'LOGGER_CURRENT_OK': 'LCO', 'GND': 'GND',
    '5V_SYS': '5VS', '5V_M1': '5VM', 'PFAIL_N': 'PFL', 'SUP_RAW_N': 'SRW', 'SUP_N_OUT': 'SPO', 'SUP_N': 'SUP'}   # 30.09: J_SV2/J_SV3 content
LEGEND = []   # built from the abbreviations actually used on J_SV2 / J_SV3 (after the service labels, below)


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


# service labels, read from edge B: J_SV1 vertical full names (as P02 R4), J_SV2 / J_SV3 horizontal abbreviations under the modules
labels = {}; used = {}
for hdr in ('J_SV1', 'J_SV2', 'J_SV3'):
    for a in fps[hdr].Pads():
        n = a.GetNetname().split('/')[-1]; x = p.ToMM(a.GetPosition().x); node = n
        if n != 'GND':  # node = the net on the other side of the series resistor
            r = next(f for f in b.GetFootprints() if f.GetReference() != hdr for q in f.Pads() if q.GetNetname() == a.GetNetname())
            node = next(q.GetNetname().split('/')[-1] for q in r.Pads() if q.GetNetname() != a.GetNetname())
        tx = p.PCB_TEXT(b); tx.SetTextThickness(mm(.12)); tx.SetLayer(p.F_SilkS)
        if hdr == 'J_SV1':
            t = LABEL[node]; tx.SetText(t); tx.SetTextSize(p.VECTOR2I(mm(.7), mm(.8)))
            tx.SetTextAngle(p.EDA_ANGLE(90, p.DEGREES_T)); tx.SetHorizJustify(p.GR_TEXT_H_ALIGN_LEFT); tx.SetPosition(p.VECTOR2I(mm(x), mm(93.9)))
        else:
            if node == 'GND':   # 30.09: GND on pins 1 and 13 is in the legend; the pin-1 label overlapped the header's pin-1 mark
                continue
            t = ABBR[node]; tx.SetText(t); tx.SetTextSize(p.VECTOR2I(mm(.7), mm(.8))); tx.SetPosition(p.VECTOR2I(mm(x), mm(94.25)))   # 0.8 mm: DRC text height
        b.Add(tx); placed.append(text_box(tx)); labels[f'{hdr}.{a.GetNumber()}'] = t
        if hdr != 'J_SV1' and node != 'GND':
            used[t] = node
pairs = [f'{k} {used[k]}' for k in sorted(used)]
LEGEND = ['J_SV2/J_SV3 (skroty; GND: kolki 1 i 13):'] + ['  '.join(pairs[i:i + 2]) for i in range(0, len(pairs), 2)]
missing = []
for r in sorted(fps, key=lambda r: (yards[r].BBox().GetArea(), r)):   # 30.09: ties by reference (board order follows random UUIDs)
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
def place_text(t, spots, size=1.0, angle=0, just=None, own=None):
    for x, y in spots:
        a = p.PCB_TEXT(b); a.SetText(t); a.SetPosition(p.VECTOR2I(mm(x), mm(y))); a.SetTextSize(p.VECTOR2I(mm(size * .9), mm(size)))
        a.SetTextThickness(mm(.15 if size >= 1 else .12)); a.SetLayer(p.F_SilkS); a.SetTextAngle(p.EDA_ANGLE(angle, p.DEGREES_T))
        if just == 'left': a.SetHorizJustify(p.GR_TEXT_H_ALIGN_LEFT)
        if just == 'right': a.SetHorizJustify(p.GR_TEXT_H_ALIGN_RIGHT)
        if free(text_box(a), own):   # own: the connector of a pin-1 mark (30.09: its own courtyard covers pin 1, so no mark was placed)
            b.Add(a); placed.append(text_box(a)); return (x, y)
    extra.append(t); return None


# ---- 3. board texts ----
res = {}
LABEL_ZONES = [(9.0, 44.5), (62.5, 97.5), (116.0, 151.5)]   # x ranges of the service labels (y > 86): the title stays out of them
res['title'] = place_text('P03 R6 S1-L', [(x, y) for y in (66, 70, 75, 80, 62, 58) for x in (26, 20, 32, 14, 38)], 1.2)
res['edge_A'] = place_text('KRAWEDZ A (P12)', [(x, y) for y in (2.2, 3.5, 5, 7) for x in (53, 54, 52, 107, 108, 106)], .9)
res['edge_B'] = place_text('KRAWEDZ B (SERWIS)', [(x, y) for y in (98.4, 97.8, 92.5) for x in (107, 106.5, 107.5, 5)], .9)
yy = None
for y0 in (64, 60, 56, 68, 44, 40, 36):          # legend of the abbreviations: one block, first free place
    for x0 in (118, 122, 9, 12, 100):
        spots = [(x0, y0 + 1.5 * i) for i in range(len(LEGEND))]   # 30.09: 1.25 mm let the 0.8 mm lines overlap (text box ~1.7 x size)
        trial = []
        for (x, y), t in zip(spots, LEGEND):
            a_ = p.PCB_TEXT(b); a_.SetText(t); a_.SetPosition(p.VECTOR2I(mm(x), mm(y))); a_.SetTextSize(p.VECTOR2I(mm(.7), mm(.8)))
            a_.SetTextThickness(mm(.12)); a_.SetLayer(p.F_SilkS); a_.SetHorizJustify(p.GR_TEXT_H_ALIGN_LEFT); trial.append(a_)
        if all(free(text_box(a_), None) for a_ in trial):
            for a_ in trial:
                b.Add(a_); placed.append(text_box(a_))
            yy = (x0, y0); break
    if yy:
        break
res['legend'] = yy
if not yy:
    extra.append('LEGEND')
# pin 1 of every connector
for r in ('J_BP1', 'J_BP2', 'J_BP3', 'J_SV1', 'J_SV2', 'J_SV3'):
    a = next(q for q in fps[r].Pads() if q.GetNumber() == '1'); ax, ay = p.ToMM(a.GetPosition().x), p.ToMM(a.GetPosition().y); s_ = max(p.ToMM(a.GetSize().x), p.ToMM(a.GetSize().y)) / 2 + .9
    res['pin1_' + r] = place_text('1', [(ax + dx * k, ay + dy * k) for k in (1, 1.5) for dx, dy in [(-s_, 0), (s_, 0), (0, -s_), (0, s_), (-s_, -s_), (s_, -s_), (-s_, s_), (s_, s_)]], .9, own=r)
p.SaveBoard(str(fn), b)
rep = {'dropped_footprint_silk': n_drop, 'dropped_by_part': dict(sorted(drop_by.items())), 'moved_texts_by_part': dict(sorted(moved_by.items())),
       'hidden_references': missing, 'board_texts': res, 'unplaced_texts': extra, 'service_labels': labels}
(P / 'routing/silkscreen.json').write_text(json.dumps(rep, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
print('silk: dropped', n_drop, 'footprint graphics; hidden references', missing, '; unplaced texts', extra)
