"""P07 S1 silkscreen (from P06 R2; format S1, class 2/3; the P03 R6 script via P09 R2 / P10 R2 / P05 R3, board values from board.py). Run after run_layout.py; changes
only F.SilkS (and hides values), never copper. Steps as P03 R6: footprint silk that would break DRC dropped at file level,
references placed at the first free candidate, board texts (name, edge markers, pin 1 of J1 / J2, PIN_MARKS) and one label per
service pin of J2 (LABEL: the net name, shortened only where it does not fit; vertical, read from edge B). Every drop is listed in routing/silkscreen.json."""
from pathlib import Path
import pcbnew as p, json, math, sys
from sexpr import parse, dump, sub, one
P = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(P / 'src'))
from board import NAME, REV, JBP, JSV, CLASS, SLOTS, PIN_MARKS
TYTUL = f"{REV} S1-{CLASS} {SLOTS[0] if len(SLOTS) == 1 else SLOTS[0] + '-' + SLOTS[-1]}"   # S1 §9: nazwa, rewizja, klasa i sloty (jak P02 R4)
fn = P / f'eda/{NAME}.kicad_pcb'
from build_board import W, Hh as H, holes
STREFY = [(hx, hy) for hx, hy in holes()]; RZ_M3 = 3.5   # 1.10 (recenzja P09): tekst w strefie Ø7 przykrywa dystans M3 z podkładką
FULL = set(JSV)   # P09 / P10: one service header with room above it -> full names on every pin (P03: only J_SV1)
MIN_H, MIN_T = 1.0, .15   # review 2.10 (F1): JLCPCB legend minimum (character height 1.0 mm, line 0.15 mm); was 0.8 / 0.12 for labels and marks
EDGE = .3   # silk-to-edge clearance used by DRC (board setting min_silk... edge 0.3 is KiCad default for silk_edge_clearance)
LABEL = {  # J_SV1: full names, vertical
    'GND': 'GND', '5V_SYS': '5V_SYS', '5V_M1': '5V_M1', '3V3_CORE': '3V3', '3V3_IO': '3V3_IO', 'SUP_RAW_N': 'SUPRAW', 'SUP_N': 'SUP_N',
    'SUP_N_OUT': 'SUPOUT', 'PFAIL_N': 'PFAIL', 'I2C_SCL': 'SCL', 'I2C_SDA': 'SDA', 'SCOPE_TRIG': 'SCOPE',
    # 30.09 evening: J_SV1 holds the S1 nodes since the regrouping by node position (and LOGGER_CURRENT_OK since the gate swap)
    'MOTOR_INB': 'MOT_INB', 'MOTOR_INA': 'MOT_INA', 'MEAS_BANK': 'MBANK', 'CS_ITEST_N': 'ITEST_N', 'CS_ILOG_N': 'ILOG_N',
    'LOGGER_CURRENT_OK': 'LCUR_OK',
    # P09 R2 J2 (docs/SERWIS.csv)
    'TC1_VIN': 'TC1_VIN', 'TC2_VIN': 'TC2_VIN', 'TC1_3VO': 'TC1_3VO', 'TC2_3VO': 'TC2_3VO', 'CS1_BUF': 'CS1_BUF', 'CS2_BUF': 'CS2_BUF',
    'OE1_N': 'OE1_N', 'OE2_N': 'OE2_N', 'SPI3_MISO': 'MISO',   # 1.10 (recenzja P09): pełne nazwy sieci; SPI3_MISO skrócone (jedyne MISO na P09)
    # P10 R2 J2 (docs/SERWIS.csv)
    'RX_RAW': 'RX_RAW', 'CAN_RX': 'CAN_RX', 'CAN_TX': 'CAN_TX', 'CAN_H': 'CAN_H', 'CAN_L': 'CAN_L',
    # P05 R3 J_SV1 / J_SV2 (docs/SERWIS.csv): at most 7 characters (1.10: 10-character labels reached the copper and the silk above
    # the headers); ODBIOR and SERWIS.csv keep the full net names
    'VBAT_SENSE': 'VBAT', '5VA_P05': '5VA', '3V3_DAQ': '3V3', 'REF_2V5': 'REF_2V5', 'RAIL_SENSE': 'R_SENSE',
    'RAIL_LOW': 'R_LOW', 'RAIL_HIGH': 'R_HIGH', 'MEAS_COIL_LOW': 'COIL_LO', 'ADC_CS': 'ADC_CS', 'ADC_CONVST': 'CONVST',
    'ADC_BUSY': 'BUSY', 'ADC_DOUTA': 'DOUTA', 'ADC_RESET': 'ADC_RST', 'MEAS_EN': 'MEAS_EN', 'MEAS_PERMIT': 'PERMIT',
    'DAQ_OK': 'DAQ_OK', 'DAQ_RAIL_N': 'RAIL_N', 'P05_SUP3_N': 'SUP3_N', 'P05_SUP5_N': 'SUP5_N',
    # P06 R2 J_SV1 / J_SV2 (docs/SERWIS.csv): at most 7 characters as P05 R3
    'I_L_OUT': 'I_L_OUT', 'ADC_AIN': 'ADC_AIN', 'REF_BUF': 'REF_BUF', 'REF25': 'REF25', '5VA_P06': '5VA', '3V3_P06': '3V3',
    'SUP3_N': 'SUP3_N', 'SUP5_N': 'SUP5_N', 'SHUNT_ENABLED': 'SHNT_EN', 'CS_LOCAL_N': 'CS_LOC', 'CLK_LOCAL': 'CLK_LOC',
    # P07 S1 J_SV1 / J_SV2 (docs/SERWIS.csv): at most 7 characters as P05 R3 / P06 R2
    'I_T_OUT': 'I_T_OUT', 'OC_HIGH': 'OC_HIGH', 'OC_LOW': 'OC_LOW', 'VMOTOR': 'VMOTOR', 'MOD_BP': 'MOD_BP', 'KPWR_COIL_LOW': 'COIL_LO',
    'T_EGR_P1': 'TEGR_P1', '5VA_P07': '5VA', '3V3A_P07': '3V3A', '5V_MOD': '5V_MOD', 'RAILS_OK': 'RAIL_OK', 'OC_LOCAL_N': 'OC_LOC',
    'OC_GOOD': 'OC_GOOD', 'NO_TRIP': 'NO_TRIP', 'DRIVE_EN': 'DRV_EN'}
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


# service labels, read from edge B: J_SV1 vertical full names (as P02 R4), J_SV2 / J_SV3 horizontal abbreviations under the modules
labels = {}; used = {}
for hdr in JSV:
    for a in fps[hdr].Pads():
        n = a.GetNetname().split('/')[-1]; x = p.ToMM(a.GetPosition().x); node = n
        if n != 'GND':  # node = the net on the other side of the series resistor
            r = next(f for f in b.GetFootprints() if f.GetReference() != hdr for q in f.Pads() if q.GetNetname() == a.GetNetname())
            node = next(q.GetNetname().split('/')[-1] for q in r.Pads() if q.GetNetname() != a.GetNetname())
        tx = p.PCB_TEXT(b); tx.SetTextThickness(mm(MIN_T)); tx.SetLayer(p.F_SilkS)
        if hdr in FULL:
            t = LABEL[node]; tx.SetText(t); tx.SetTextSize(p.VECTOR2I(mm(.9 * MIN_H), mm(MIN_H)))
            tx.SetTextAngle(p.EDA_ANGLE(90, p.DEGREES_T)); tx.SetHorizJustify(p.GR_TEXT_H_ALIGN_LEFT); tx.SetPosition(p.VECTOR2I(mm(x), mm(93.9)))
        else:
            if node == 'GND':   # 30.09: GND on pins 1 and 13 is in the legend; the pin-1 label overlapped the header's pin-1 mark
                continue
            t = ABBR[node]; tx.SetText(t); tx.SetTextSize(p.VECTOR2I(mm(.9 * MIN_H), mm(MIN_H))); tx.SetPosition(p.VECTOR2I(mm(x), mm(94.25)))
        b.Add(tx); placed.append(text_box(tx)); labels[f'{hdr}.{a.GetNumber()}'] = t
        if hdr not in FULL and node != 'GND':   # 30.09: was hdr != 'J_SV1' (P03 names): P09 asked for a legend of full names
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
    for size in (MIN_H,):   # review 2.10: no 0.8 mm fallback; a reference without room is hidden (F.Fab, assembly drawing)
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
    size = max(size, MIN_H)   # review 2.10 (F1): the edge markers (0.8) and pin marks (0.9) were below the fab minimum
    for x, y in spots:
        a = p.PCB_TEXT(b); a.SetText(t); a.SetPosition(p.VECTOR2I(mm(x), mm(y))); a.SetTextSize(p.VECTOR2I(mm(size * .9), mm(size)))
        a.SetTextThickness(mm(MIN_T)); a.SetLayer(p.F_SilkS); a.SetTextAngle(p.EDA_ANGLE(angle, p.DEGREES_T))
        if just == 'left': a.SetHorizJustify(p.GR_TEXT_H_ALIGN_LEFT)
        if just == 'right': a.SetHorizJustify(p.GR_TEXT_H_ALIGN_RIGHT)
        if free(text_box(a), own):   # own: the connector of a pin-1 mark (30.09: its own courtyard covers pin 1, so no mark was placed)
            b.Add(a); placed.append(text_box(a)); return (x, y)
    extra.append(t); return None


# ---- 3. board texts ----
res = {}
# 1/3 board (53 mm wide): title in a free area (P10: the empty middle, then the lower third), short edge markers in the corners next to J1 / J2
# P05 R3 (2/3 board): title in the free lower right quarter (between U6 / U7 and J_SV2), then the lower left
res['title'] = place_text(TYTUL, [(x, y) for y in (21, 23, 25, 19, 27, 88, 90) for x in (50, 47, 53, 56, 44, 60)], 1.2)   # P07: free top middle under J_BP1 / J_BP2
res['edge_A'] = place_text('KRAWEDZ A (P12)', [(x, y) for y in (3.0, 4.5, 6.0, 7.5) for x in (53.0, 52.0, 54.0, 51.0, 55.0)], MIN_H)   # P07: between J_BP1 and J_BP2
if res['edge_A'] is None:   # 30.09: on 53 mm the long marker does not fit beside J1 -> the short one in a corner
    extra.remove('KRAWEDZ A (P12)'); res['edge_A'] = place_text('KRAWEDZ A', [(x, y) for y in (2.5, 4, 5.5, 7) for x in (6.0, 5.5, 47.0, 47.5)], MIN_H)
res['edge_B'] = place_text('KRAWEDZ B', [(x, y) for y in (97.5, 98.2, 96.5, 95.5) for x in (53.0, 52.0, 54.0, 5.0, 101.5)], MIN_H)   # P05: between J_SV1 and J_SV2
yy = None
for y0 in ((64, 60, 56, 68, 44, 40, 36) if used else ()):   # legend of the abbreviations (none on P09 / P10): one block, first free place
    for x0 in (118, 122, 9, 12, 100):
        spots = [(x0, y0 + 1.8 * i) for i in range(len(LEGEND))]   # 30.09: 1.25 mm let the 0.8 mm lines overlap (text box ~1.7 x size); 2.10: 1.0 mm text
        trial = []
        for (x, y), t in zip(spots, LEGEND):
            a_ = p.PCB_TEXT(b); a_.SetText(t); a_.SetPosition(p.VECTOR2I(mm(x), mm(y))); a_.SetTextSize(p.VECTOR2I(mm(.9 * MIN_H), mm(MIN_H)))
            a_.SetTextThickness(mm(MIN_T)); a_.SetLayer(p.F_SilkS); a_.SetHorizJustify(p.GR_TEXT_H_ALIGN_LEFT); trial.append(a_)
        if all(free(text_box(a_), None) for a_ in trial):
            for a_ in trial:
                b.Add(a_); placed.append(text_box(a_))
            yy = (x0, y0); break
    if yy:
        break
res['legend'] = yy
if used and not yy:
    extra.append('LEGEND')
# pin 1 of every connector
for r in JBP + JSV:
    a = next(q for q in fps[r].Pads() if q.GetNumber() == '1'); ax, ay = p.ToMM(a.GetPosition().x), p.ToMM(a.GetPosition().y); s_ = max(p.ToMM(a.GetSize().x), p.ToMM(a.GetSize().y)) / 2 + .9
    res['pin1_' + r] = place_text('1', [(ax + dx * k, ay + dy * k) for k in (1, 1.5) for dx, dy in [(-s_, 0), (s_, 0), (0, -s_), (0, s_), (-s_, -s_), (s_, -s_), (-s_, s_), (s_, s_)]], MIN_H, own=r)
for r, znaki in PIN_MARKS.items():   # 1.10 (recenzja): biegunowość / pin 1 złączy modułów i wiązek (S1 §9: pin 1 każdego złącza)
    for num, t in znaki.items():
        a = next(q for q in fps[r].Pads() if q.GetNumber() == num); ax, ay = p.ToMM(a.GetPosition().x), p.ToMM(a.GetPosition().y)
        s_ = max(p.ToMM(a.GetSize().x), p.ToMM(a.GetSize().y)) / 2 + .9
        res[f'znak_{r}.{num}'] = place_text(t, [(ax + dx * k, ay + dy * k) for k in (1, 1.5) for dx, dy in [(-s_, 0), (s_, 0), (0, -s_), (0, s_), (-s_, -s_), (s_, -s_), (-s_, s_), (s_, s_)]], MIN_H, own=r)
p.SaveBoard(str(fn), b)
rep = {'dropped_footprint_silk': n_drop, 'dropped_by_part': dict(sorted(drop_by.items())), 'moved_texts_by_part': dict(sorted(moved_by.items())),
       'hidden_references': missing, 'board_texts': res, 'unplaced_texts': extra, 'service_labels': labels}
(P / 'routing/silkscreen.json').write_text(json.dumps(rep, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
print('silk: dropped', n_drop, 'footprint graphics; hidden references', missing, '; unplaced texts', extra)
