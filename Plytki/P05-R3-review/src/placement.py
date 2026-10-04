"""P05 R3 placement (format S1, class 2/3, slots S1-S2 of level 3). Writes src/placement.json: ref -> [x, y, rotation(, 'B')];
origin = footprint origin (pin 1 for THT library parts and the pigtails, centre for SMD). Board x 0..106.5 (x = 0: panel side - TAPS,
AUX and SW1 there, S1 section 7), y 0..100 (0 = edge A, P12; 100 = edge B, service side). Run with KiCad Python.
Machinery (geo, place_near, bottom-side support, strip A) from P09 R2 placement.py (1.10.2026).

Fixed by S1 (SPECYFIKACJA-FORMATU-S1.md sections 4-7) and the README layout requirements:
- J_BP1 (IDC 2x5, slot S1) and J_BP2 (IDC 2x10, slot S2): mating face at y = 0, pin centre x = 26.5 / 80.0, pin 1 at the smaller x;
- J_SV1 / J_SV2 (1x13 right angle): pins in x 10..43 of their slot, pin 1 at the larger x, ~6 mm beyond edge B;
- 8 M3 holes (x 4 / 49 per slot, y 14 / 86) with the D7 standoff zones; reserved strips of edge A (y 0..10, x 10..43 per slot);
- J4 (TAPS), J6 (AUX) and SW1 at x = 0 (wires and lever through the panel).
Blocks: left column = TAPS J4 with the relays K1-K3, their driver U4 and flyback diodes; bottom left = AUX J6 and SW1 (E-Switch M6,
lever towards x = 0); top left under J_BP1 = supply (R1, C1, U12) and the DAQ_OK window (U2, U3, R3-R8, C23-C26) with the supervisors
and gate (U5-U8); centre = U1 (AD7606B) turned 90 so its inputs (pins 49-63) face the relays and the AUX divider, its supply and
reference pins (33-48) face edge A (decoupling there) and its serial pins face the buffers U9-U11 on the right towards J_BP2.
Decoupling and filter parts at their pins (R2 pattern P5-01 adapted to 1206: distances checked in verify_pcb.py).
Service resistors R36-R55 on the bottom at their nodes where room allows (S1-2: SMD <= 1.5 mm, >= 1 mm from THT pads).
"""
import pcbnew as p, json, math, sys, os
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
from board import PLANNER_KEEPOUT
from pathlib import Path
P = Path(__file__).resolve().parents[1]
S1 = json.loads((P.parents[0] / 'Format-S1/format-s1.json').read_text(encoding='utf-8'))
parts = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
W, H = S1['klasy']['2/3']['W'], S1['klasy']['2/3']['H']
STEP = S1['rozstaw_slotow']
HOLES = [(x + STEP * k, y) for k in range(2) for x in S1['otwory_M3']['x_w_slocie'] for y in S1['otwory_M3']['y']]
RZ = S1['otwory_M3']['strefa_dystansu_srednica'] / 2
STRIPS_A = [(STEP * k + 10.0, S1['krawedz_A']['strefa_y'][0], STEP * k + 43.0, S1['krawedz_A']['strefa_y'][1]) for k in range(2)]
GEO = {}


def geo(ref):
    """Local pads {num: (x, y, drill_radius, pad_radius)} and courtyard box of the footprint of `ref` (library copy in eda/libraries)."""
    fid = parts[ref]['footprint']
    if fid not in GEO:
        lib, name = fid.split(':'); f = p.FootprintLoad(str(P / 'eda/libraries' / (lib + '.pretty')), name); assert f, fid
        ls = p.LSET(); ls.AddLayer(p.F_CrtYd); r = f.GetLayerBoundingBox(ls)
        GEO[fid] = ({a.GetNumber(): (p.ToMM(a.GetPosition().x), p.ToMM(a.GetPosition().y), p.ToMM(a.GetDrillSize().x) / 2,
                                     max(p.ToMM(a.GetSize(p.F_Cu).x), p.ToMM(a.GetSize(p.F_Cu).y)) / 2) for a in f.Pads() if a.GetNumber()},
                    (p.ToMM(r.GetLeft()), p.ToMM(r.GetTop()), p.ToMM(r.GetRight()), p.ToMM(r.GetBottom())))
    return GEO[fid]


def tf(x, y, cx, cy, rot, side='F'):
    a = math.radians(rot); c, s = round(math.cos(a)), round(math.sin(a))
    X, Y = cx + x * c + y * s, cy - x * s + y * c
    return (X, 2 * cy - Y) if side == 'B' else (X, Y)   # build_board.py flips top/bottom about the part's own position


L = {}; BOX = {}; SIDE = {}


def put(ref, x, y, r=0, side='F'):
    L[ref] = [round(x, 3), round(y, 3), r % 360] + (['B'] if side == 'B' else []); SIDE[ref] = side; BOX[ref] = box(ref)


def pad(ref, num):
    x, y, r = L[ref][:3]; lx, ly, *_ = geo(ref)[0][str(num)]; return tf(lx, ly, x, y, r, SIDE[ref])


def box(ref, at=None, side=None):
    x, y, r = at or L[ref][:3]; side = side or SIDE.get(ref, 'F'); x0, y0, x1, y1 = geo(ref)[1]
    q = [tf(u, v, x, y, r, side) for u, v in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]]
    return (min(a for a, _ in q), min(b for _, b in q), max(a for a, _ in q), max(b for _, b in q))


def tht_pads():
    """(x, y, copper radius) of every THT pad placed so far (pads with a drill)."""
    return [(*pad(r, n), g[3]) for r in L for n, g in geo(r)[0].items() if g[2] > 0]


def free(b, m=.5, own=None, side='F'):
    if b[0] < .6 or b[1] < .6 or b[2] > W - .6 or b[3] > H - .6:
        return False
    for z in STRIPS_A:   # reserved strips of edge A hold only the J_BP (put() directly)
        if b[0] < z[2] and z[0] < b[2] and b[1] < z[3] and z[1] < b[3]:
            return False
    for r, o in BOX.items():
        if r == own or SIDE[r] != side:
            continue
        if b[0] - m < o[2] and o[0] < b[2] + m and b[1] - m < o[3] and o[1] < b[3] + m:
            return False
    for hx, hy in HOLES:
        dx = max(b[0] - hx, 0, hx - b[2]); dy = max(b[1] - hy, 0, hy - b[3])
        if math.hypot(dx, dy) < RZ + .1:
            return False
    for zs, z in RESERVED:   # copper reserved for route_critical.py (input fan, U1 escapes, 5VA bar, the B side under U1)
        if zs == side and b[0] < z[2] and z[0] < b[2] and b[1] < z[3] and z[1] < b[3]:
            return False
    if side == 'B':   # S1-2: >= 1 mm from THT pads (copper to courtyard, conservative)
        for tx, ty, tr in tht_pads():
            dx = max(b[0] - tx, 0, tx - b[2]); dy = max(b[1] - ty, 0, ty - b[3])
            if math.hypot(dx, dy) < tr + 1.0:
                return False
    elif own and is_tht(own):   # a THT part on top puts its pads through the bottom too: same 1 mm from bottom parts
        for r, o in BOX.items():
            if SIDE[r] == 'B' and any(o[0] - 1.0 - pr < px < o[2] + 1.0 + pr and o[1] - 1.0 - pr < py < o[3] + 1.0 + pr
                                      for px, py, pr in pending_pads(own, b)):
                return False
    return True


def is_tht(ref):
    return any(g[2] > 0 for g in geo(ref)[0].values())


PENDING = {}


def pending_pads(ref, b):
    """THT pads of `ref` at the candidate being tested (set by place_near before free())."""
    return PENDING.get(ref, [])


REPORT = {}


def place_near(ref, target, own=None, radius=16.0, rots=(0, 90, 180, 270), m=.5, side='F'):
    """Nearest legal position: pad `own` (default: the pad on the target's net, else '1') as close as possible to the target."""
    if isinstance(target, tuple) and isinstance(target[0], str):
        tref, tpad = target; tx, ty = pad(tref, tpad); tnet = parts[tref]['pins'][str(tpad)]
        own = own or next((k for k, n in parts[ref]['pins'].items() if n == tnet), '1')
    else:
        tx, ty = target; own = own or '1'
    lx, ly, *_ = geo(ref)[0][str(own)]; step = .25; n = int(radius / step)
    cand = sorted(((math.hypot(i * step, j * step), k, i, j) for i in range(-n, n + 1) for j in range(-n, n + 1) for k in range(len(rots))
                   if math.hypot(i * step, j * step) <= radius))
    for d, k, i, j in cand:
        r = rots[k]; ox, oy = tf(lx, ly, 0, 0, r); oy = -oy if side == 'B' else oy
        x, y = tx + i * step - ox, ty + j * step - oy
        PENDING[ref] = [(*tf(g[0], g[1], x, y, r, side), g[3]) for g in geo(ref)[0].values() if g[2] > 0]
        if free(box(ref, (x, y, r), side), m, own=ref, side=side):
            put(ref, x, y, r, side); REPORT[ref] = round(d, 2); return
    raise SystemExit(f'no place for {ref} near {target} ({side})')


# ---- fixed by S1 ----
put('J_BP1', 26.5 - 2 * 2.54, 13.33, 90)        # pin 1 (x 21.42) at the smaller x; mating face at y = 0 (as P03 R6 / P10 R2)
put('J_BP2', 80.0 - 4.5 * 2.54, 13.33, 90)      # pin 1 at x 68.57
put('J_SV1', 26.5 + 15.24, 95.96, 270)          # pin 1 at x 41.74 (larger x), pin 13 at 11.26; body front at y = 100
put('J_SV2', 80.0 + 15.24, 95.96, 270)          # pin 1 at x 95.24, pin 13 at 64.76
# ---- panel side (x = 0): TAPS, AUX and SW1 in one column; the cables and the lever leave towards x = 0 ----
put('J4', 15.0, 41.6, 90)                       # TAPS pads x 15 / 18.5, y 24.1..41.6 (pin 1 at the bottom); anchor zone x 1..15
put('J6', 15.0, 52.6, 90)                       # AUX coax tail under TAPS, next to SW1.2 (AUX_IN)
put('SW1', 16.6, 71.2, 180)                     # E-Switch M6: support legs at x 3.9, bushing and lever beyond x = 0 through the panel
# ---- relays right of TAPS (TAP_P* on pins 4 / 5 face J4, ADC_CH* on pins 3 / 6), flyback diodes beside the coil pins 1 / 8 ----
for i, k in enumerate(('K1', 'K2', 'K3')):
    y0 = 19.5 + 11.5 * i; put(k, 23.5, y0, 0)
    put(f'D{i + 1}', 31.6, y0 + 7.62, 90)      # anode (MEAS_COIL_LOW) level with K pin 8, cathode (5V_SYS) 7.62 mm lower
put('U4', 23.5, 56.5, 0)                        # TBD62083A (DIP18): OUT 18 = MEAS_COIL_LOW up to the coils (pin 8), IN 1 = MEAS_PERMIT
# ---- supply under J_BP1 / J_BP2: 5V_SYS -> R1 1 Ohm -> C1 -> 5VA_P05 (U1 top side) and LDO U12 -> 3V3_DAQ ----
put('R1', 36.0, 20.0, 0)                        # 1 W axial, 15.24 mm (S1 section 1 exception); 3.9 mm below the M3 zone at (49, 14)
put('C1', 55.0, 21.6, 0)                        # 5VA_P05 at R1 pin 2; 4.2 mm below the M3 zone at (57.5, 14)
put('U12', 61.0, 27.5, 0)                       # MCP1700 (TO-92): pin 2 (5VA) at x 63.5, pin 3 (3V3_DAQ) at x 66.1 towards the buffers (run 5)
# ---- DAQ_OK window between J_BP1 and the input column ----
put('U2', 41.5, 28.5, 0)                        # REF5025 (SOIC8)
put('U3', 41.5, 35.5, 0)                        # TLV1702 window comparator (VSSOP8)
# ---- serial buffers: U9 (SCLK / SDI / CS / CONVST) and U11 (DOUT / BUSY) right of U1, U10 (RESET / MEAS_EN) at J_BP2 ----
# (run 3: with the buffers at J_BP2 the seven local lines had to round U1 through the busiest area and stayed open; now they are
# 4-15 mm long, the J_BP2 bus stubs ~35 mm - at these SPI rates well under the critical length, README)
put('U9', 73.0, 45.0, 0); put('U11', 73.0, 57.0, 0); put('U10', 83.0, 28.0, 0)
# ---- DAQ_OK gate, supervisors and SUP5 buffer (right, lower half) ----
put('U5', 88.0, 50.0, 0)                        # HC08 (DIP14): DAQ_OK = window & SUP3 & SUP5, MEAS_PERMIT = DAQ_OK & MEAS_EN
put('U8', 90.0, 72.0, 0)                        # SUP5 buffer (LVC125) below U5
put('U6', 82.0, 82.0, 0); put('U7', 90.0, 82.0, 0)   # MCP120 300 / 450 (TO-92)
# ---- U1 (AD7606B) and its decoupling: explicit (README layout requirements; R2 pattern P5-01 adapted to 1206 / 1210) ----
# U1 turned 90: pins 1-16 along the bottom (y 59.675), 17-32 up the right side (x 63.675), 33-48 along the top (y 48.325, x 61.75 ->
# 54.25), 49-64 down the left side (x 52.325, inputs). Pad tips 0.775 mm beyond the pad centres; courtyard x 51.275..64.725,
# y 47.275..60.725. Copper limits pin -> capacitor pad (src/route_critical.py draws it, verify_pcb.py measures): 100 nF and REGCAP
# <= 3 mm, 22 uF (1210) <= 6 mm, VDRIVE <= 4 mm (R2 table, review P5-01).
UX, UY = 58.0, 54.0
put('U1', UX, UY, 90)
# top side, above pins 33-48 (rot 90: pad 1 below the centre). C12 (ADC_REF 42) and C13 (REFCAP 44/45) are 1210 22 uF (2.5 mm thick,
# top only); C10 (REGCAP_D 39) and C9 (REGCAP_A 36) are 1 uF (up to 1.6 mm, top only). REFCAP runs left under C12 along the pad tips
# into C13; the 0.85 mm gaps C13|C12 and C10|C9 carry the test-pad stubs of TP2 (ADC_REF) and TP4 (REGCAP_D) upwards.
put('C13', 52.4, 44.75, 90); put('C12', 55.95, 44.75, 90); put('C10', 58.8, 44.7, 90); put('C9', 61.45, 44.7, 90)
put('TP5', 49.2, 44.9); put('TP2', 54.175, 38.6); put('TP4', 60.125, 38.6); put('TP3', 64.3, 45.0)
put('C4', 53.6, 63.25, 270)                     # AVCC pin 1 (bottom-left corner): top side below the corner, pad 1 up
# bottom side under the body (100 nF 1206, BOM: <= 1.5 mm thick, S1-2); rot 90 on the bottom puts pad 1 above the centre.
# Each one is fed through its own via inside the pad ring (route_critical.py): C7 = AVCC 48, C11 = REFIN/OUT 42, C5 = AVCC 37/38,
# C8 = VDRIVE 23.
# review 2.10 (MAJOR-1): moved right (pitch 2.35 mm, courtyards 0.05 apart) for the 5VA spine at x 54.65 and the GND via column at
# x 53.7 inside the left pins (route_critical.py); each gets a GND via between its pads
put('C7', 55.9, 52.5625, 90, 'B'); put('C11', 58.25, 52.5625, 90, 'B'); put('C5', 60.6, 52.5625, 90, 'B')
put('C8', 61.9, 57.5625, 90, 'B')
# ---- input filters C27-C34: one column left of U1 (rot 180: pad 1 = ADC_CHn towards U1 at x 44.5, pad 2 = GND), pitch 2.65 mm so
# a 0.3 mm source stub fits between two capacitors (route_critical.py: 45 deg fan from the pins, stubs to x 39 for the router).
# C32 (owned 1 nF disc, CH6) needs a taller slot.
COL = {'C27': 44.4, 'C28': 47.05, 'C29': 49.7, 'C30': 52.35, 'C31': 55.0, 'C32': 57.95, 'C33': 60.9, 'C34': 63.55}
for c, y in COL.items():
    put(c, 44.5 if c == 'C32' else 44.5 - 1.5625, y, 180)
STUB_Y = {c: (y + (1.375 if c == 'C32' else 1.325)) for c, y in COL.items()}   # source stub rows (gap centres below each capacitor)
# input resistors at the stub ends (pad on the channel net at x 38.55): pull-downs R28 / R29 / R30, VBAT divider R31, AUX divider R33
put('R28', 37.0, STUB_Y['C27'], 180); put('R29', 37.0, STUB_Y['C28'], 180); put('R30', 35.9, STUB_Y['C32'], 180)
put('R31', 37.0, STUB_Y['C33'], 0); put('R33', 37.0, STUB_Y['C34'], 0)
# ---- reserved copper areas (no other parts): input fan, U1 escapes, the 5VA bar under the top capacitors, the B side under U1 ----
RESERVED = [('F', (44.4, 43.0, 51.3, 65.0)), ('B', (44.4, 43.0, 51.3, 65.0)),
            ('F', (55.0, 60.7, 63.5, 64.2)), ('F', (64.7, 50.5, 67.2, 55.5)), ('B', (62.8, 55.4, 67.2, 56.6)),
            ('B', (50.8, 41.0, 62.0, 47.3)), ('B', (51.275, 47.275, 64.725, 60.725)),   # 2.10: 5VA stubs and join, cap GND vias
            ('F', (51.5, 41.0, 62.5, 42.6)), ('B', (51.5, 41.0, 62.5, 42.6)),   # C6 via of the 5VA join
            ('F', (36.2, 33.9, 38.3, 37.8)), ('F', (44.7, 33.9, 45.9, 37.1))]   # U3 stubs and its GND via (route_critical.py, route_u3)
RESERVED += [(L[0], (x0 - .5, y0 - .5, x1 + .5, y1 + .5)) for L, x0, y0, x1, y1 in PLANNER_KEEPOUT]   # no part where the router may not go
RESERVED += [('F', (9.0, 86.3, 44.0, 95.5)), ('F', (62.5, 86.3, 97.5, 95.5))]   # 2.10: service labels (1.0 mm, up to 7 characters) above J_SV1 / J_SV2
# passives at the pin they serve: (anchor ref, anchor pad); the part's pad on the same net goes next to it. Order = priority:
# the window dividers and filters of U3 first (RAIL_* nodes stay short), then the decoupling, pull resistors and the rest.
# SMD parts go to the bottom when the top has no room near the anchor (S1-2: new SMD R and C fit the bottom best).
DEC = {'C15': ('U3', '8'), 'R3': ('U3', '3'), 'R4': ('U3', '6'), 'R5': ('U3', '2'), 'R6': ('U3', '2'), 'C25': ('U3', '2'),
       'R7': ('U3', '5'), 'R8': ('U3', '5'), 'C26': ('U3', '5'), 'R9': ('U3', '1'),
       'C14': ('U2', '2'), 'C23': ('U2', '2'), 'C24': ('U2', '6'),
       'C2': ('U12', '2'), 'C3': ('U12', '3'), 'R2': ('U12', '3'),
       'C16': ('U5', '14'), 'C17': ('U6', '2'), 'C18': ('U7', '2'), 'C19': ('U8', '14'),
       'R10': ('U6', '1'), 'R11': ('U7', '1'), 'R12': ('U5', '6'), 'R25': ('U5', '8'),
       'C20': ('U9', '14'), 'C21': ('U10', '14'), 'C22': ('U11', '14'),
       'R14': ('U9', '2'), 'R15': ('U9', '5'), 'R13': ('U9', '9'), 'R16': ('U9', '12'), 'R17': ('U10', '2'), 'R18': ('U10', '5'),
       'R20': ('U9', '3'), 'R21': ('U9', '6'), 'R19': ('U9', '8'), 'R22': ('U9', '11'), 'R23': ('U10', '3'), 'R24': ('U10', '6'),
       'R26': ('U11', '3'), 'R27': ('U11', '6'),
       'R32': ('R31', '2'), 'R34': ('R33', '2'), 'R35': ('R33', '2'), 'TP1': ('U1', '2')}
put('C6', 57.3, 38.7, 90)                       # 5VA_P05 100 nF between TP2 and TP4, above the ground vias of C12 / C10
put('C35', 57.3, 35.0125, 0)                    # 2.10: AVCC bulk 10 uF just above C6 (spot free of the copper of the reviewed routing, which is replayed)
# review 2.10 (MAJOR-2, return-path checks of verify_pcb.py): a decoupling / filter capacitor also needs its GND pad at the GND pin of its
# part (C20 -> U9 GND >= 62 mm, C15 -> U3.4 51, C16 -> U5.7 41 before). These take the free position with the smallest
# (supply pad -> pin) + (GND pad -> GND pin), supply side <= 5.5 mm (check: 6). The DAQ_OK window (C15, C25, C26 at
# U3) keeps the old rule: re-placed, it pushed C25 under U3 and the planner could not reach C25.1 through the U3 stub keepouts (2.10).
GND_PIN = {'C14': ('U2', '4'), 'C23': ('U2', '4'), 'C24': ('U2', '4'),
           'C2': ('U12', '1'), 'C3': ('U12', '1'), 'C16': ('U5', '7'), 'C17': ('U6', '3'), 'C18': ('U7', '3'), 'C19': ('U8', '7'),
           'C20': ('U9', '7'), 'C21': ('U10', '7'), 'C22': ('U11', '7')}
SUP_MAX = {}


def place_dec(ref, target, gnd, radius=8.0, side='F'):
    tref, tpad = target; tx, ty = pad(tref, tpad); tnet = parts[tref]['pins'][str(tpad)]
    own = next(k for k, n in parts[ref]['pins'].items() if n == tnet); gown = next(k for k, n in parts[ref]['pins'].items() if n == 'GND')
    gx, gy = pad(*gnd); (lx, ly, *_), (mx, my, *_) = geo(ref)[0][own], geo(ref)[0][gown]; step = .25; n = int(radius / step); best = None
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            if math.hypot(i, j) * step > radius:
                continue
            for r in (0, 90, 180, 270):
                ox, oy = tf(lx, ly, 0, 0, r); oy = -oy if side == 'B' else oy
                x, y = tx + i * step - ox, ty + j * step - oy
                ds = math.dist(tf(lx, ly, x, y, r, side), (tx, ty)); dg = math.dist(tf(mx, my, x, y, r, side), (gx, gy))
                if ds > SUP_MAX.get(ref, 5.5) or (best and ds + dg >= best[0]):
                    continue
                if free(box(ref, (x, y, r), side), .5, own=ref, side=side):
                    best = (ds + dg, x, y, r, ds)
    if not best:
        raise SystemExit(f'no place for {ref} near {target} ({side})')
    put(ref, best[1], best[2], best[3], side); REPORT[ref] = round(best[4], 2)



FAILED = []
for c, t in DEC.items():
    tries = [('F', 8), ('B', 8), ('F', 16), ('B', 16)] if not is_tht(c) else [('F', 8), ('F', 16)]
    for side, rad in tries:
        try:
            if c in GND_PIN and rad == 8:
                place_dec(c, t, GND_PIN[c], side=side)
            else:
                place_near(c, t, radius=rad, side=side)
            break
        except SystemExit as e:
            last = e
    else:
        FAILED.append(c); print(last)
SERVICE = sorted((r for r, v in parts.items() if v['source_ref'].startswith('ADDED_SERVICE')), key=lambda r: int(r[1:]))
ANCHOR_ORDER = ('U1', 'U2', 'U3', 'U5', 'U8', 'U9', 'U10', 'U11', 'U12', 'U6', 'U7', 'U4', 'K', 'J_BP', 'J4', 'J6', 'SW1', 'C', 'R', 'D')


def anchor(ref, nets=None):
    """First placed pad (in ANCHOR_ORDER) sharing a net with `ref` (GND and service-pin nets ignored): (anchor ref, pad, own pad)."""
    own = {k: n for k, n in parts[ref]['pins'].items() if n not in ('GND', 'NC') and not n.startswith('SRV_') and (nets is None or n in nets)}
    for pref in ANCHOR_ORDER:
        for r in sorted(L, key=lambda q: (len(q), q)):
            if not r.startswith(pref) or r == ref or r.startswith('J_SV'):
                continue
            for n, net in parts[r]['pins'].items():
                k = next((k for k, m in own.items() if m == net), None)
                if k is not None and n in geo(r)[0]:
                    return r, n, k
    return None


rest = [r for r in parts if parts[r].get('on_board', True) and r not in L and r not in SERVICE]
print('unplaced', rest) if rest else None
SERVICE_ANCHOR = {'R37': ('R3', '1', '1'), 'R38': ('R9', '2', '1')}   # 5VA / 3V3 nodes away from U1 (its pins sit in the router keepouts)
for r in SERVICE:   # node side (pin 1) next to a pad of the node; bottom first (S1-2), top if no room
    a = SERVICE_ANCHOR.get(r) or anchor(r, {parts[r]['pins']['1']})
    assert a, ('no node', r)
    if is_tht(r):   # owned MF0207 (R43) stands on top (S1-2: THT on the top side)
        place_near(r, (a[0], a[1]), own='1', radius=16); continue
    try:
        place_near(r, (a[0], a[1]), own='1', radius=12, side='B')
    except SystemExit:
        place_near(r, (a[0], a[1]), own='1', radius=16)
if os.environ.get('P05_BOXES'):
    Path(os.environ['P05_BOXES']).write_text(json.dumps({'boxes': BOX, 'side': SIDE, 'pads': {r: {n: pad(r, n) for n in geo(r)[0]} for r in L}}))
missing_fixed = [r for r in ('J_BP1', 'J_BP2', 'J_SV1', 'J_SV2', 'J4', 'J6', 'SW1', 'U1') if r not in L]
assert not missing_fixed, missing_fixed
for a, c in [(r, o) for r in list(BOX) for o in list(BOX) if r < o and SIDE[r] == SIDE[o]]:
    ba, bc = BOX[a], BOX[c]
    if ba[0] < bc[2] and bc[0] < ba[2] and ba[1] < bc[3] and bc[1] < ba[3]:
        print('OVERLAP', a, c, [round(v, 1) for v in ba], [round(v, 1) for v in bc])
(P / 'src/placement.json').write_text(json.dumps(L, indent=1) + '\n')
if os.environ.get('P05_BOXES'):   # development preview only (courtyard boxes and pads)
    Path(os.environ['P05_BOXES']).write_text(json.dumps({'boxes': BOX, 'side': SIDE, 'pads': {r: {n: pad(r, n) for n in geo(r)[0]} for r in L}}))
far = {r: d for r, d in REPORT.items() if d > 6}
print(len(L), 'placed; search distance > 6 mm:', far)
