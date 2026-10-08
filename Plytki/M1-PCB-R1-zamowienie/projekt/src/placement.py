"""M1-R1 placement. Writes src/placement.json: ref -> [x, y, rotation(, 'B')]; origin = footprint origin (pin 1 for THT parts and the
wire-pad footprints, centre for SMD). Board x 0..150, y 0..80 (board.W / board.H; outline chosen for the layout, the enclosure follows).
Run with KiCad Python. Helpers (geo, tf, put, place_near, place_dec, free) from P07 S1 placement.py.

Edges:
- top (y = 0): wire pads to X1 in screw order, anchors 12 mm towards the edge (wires leave upwards to the strip): J1 (X1.1 BAT+, X1.2 GND),
  J2 (X1.3 VMOTOR), J5 (X1.5 P1_ECU, X1.6 P1_EGR), J6 (X1.7-16: P3, P4, P5, P6, SENS_5V, GND, VBAT_CAR, CAN_H, CAN_L, GND).
- right: ESP32-S3 DEV-KIT standing on its headers, USB-C at the bottom edge, antenna end at the top-right corner (ANTENNA rule area,
  build_board.py); J3 (button) left of the module next to GPIO15.
- bottom: J4 (IBT-2 logic, anchors towards the edge), TC1 / TC2 (thermocouple terminals at the edge, own gland), SD1 (card slot at the edge).
Inside: power corner under J1 / J2 (F1, TSR 5 V / 3.3 V), shunt RSH1 under J5 with the INA240 below it (Kelvin pair locked, route_critical.py),
AD7606B turned 90 deg (analog inputs left towards the dividers, references up, SPI down / right towards the ESP32), CAN and TPS2553 under
the right half of J6, the 3.3 -> 5 V buffer U7 above J4, the MISO buffer U5 above the thermocouple modules."""
import pcbnew as p, json, math, sys, os
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
from pathlib import Path
import board
P = Path(__file__).resolve().parents[1]
parts = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
W, H = board.W, board.H
HOLES = board.HOLES
RZ = board.HOLE_ZONE_D / 2
GEO = {}
MARG = 1.4


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
    return (X, 2 * cy - Y) if side == 'B' else (X, Y)


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
    return [(*pad(r, n), g[3]) for r in L for n, g in geo(r)[0].items() if g[2] > 0]


def is_tht(ref):
    return any(g[2] > 0 for g in geo(ref)[0].values())


PENDING = {}
RESERVED = []


def free(b, m=.5, own=None, side='F'):
    if b[0] < .6 or b[1] < .6 or b[2] > W - .6 or b[3] > H - .6:
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
    for zs, z in RESERVED:
        if zs == side and b[0] < z[2] and z[0] < b[2] and b[1] < z[3] and z[1] < b[3]:
            return False
    if side == 'B':   # no bottom part under a top IC / module / connector; >= 1 mm from THT pads
        for r, o in BOX.items():
            if SIDE[r] == 'F' and r.startswith(('U', 'J', 'M', 'SD', 'TC', 'D', 'F')) and b[0] < o[2] and o[0] < b[2] and b[1] < o[3] and o[1] < b[3]:
                return False
        for tx, ty, tr in tht_pads():
            dx = max(b[0] - tx, 0, tx - b[2]); dy = max(b[1] - ty, 0, ty - b[3])
            if math.hypot(dx, dy) < tr + 1.0:
                return False
    return True


REPORT = {}


def place_near(ref, target, own=None, radius=16.0, rots=(0, 90, 180, 270), m=None, side='F'):
    """Nearest legal position: pad `own` (default: the pad on the target's net, else '1') as close as possible to the target."""
    m = MARG if m is None else m
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
        if free(box(ref, (x, y, r), side), m, own=ref, side=side):
            put(ref, x, y, r, side); REPORT[ref] = round(d, 2); return
    raise SystemExit(f'no place for {ref} near {target} ({side})')


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
                if ds > 5.5 or (best and ds + dg >= best[0]):
                    continue
                if free(box(ref, (x, y, r), side), MARG, own=ref, side=side):
                    best = (ds + dg, x, y, r, ds)
    if not best:
        raise SystemExit(f'no place for {ref} near {target} ({side})')
    put(ref, best[1], best[2], best[3], side); REPORT[ref] = round(best[4], 2)


# ================= M1-R1 =================
# ---- top edge: X1 wire pads (pads at y 15, anchors at y 3) ----
PY = 15.0
put('J1', 14.0, PY, 0)      # BAT+ 14.0, GND 21.62
put('J2', 33.0, PY, 0)      # VMOTOR (F1 out) to X1.3
put('J5', 45.0, PY, 0)      # P1_ECU 45.0, P1_EGR 52.62
put('J6', 64.0, PY, 0)      # X1.7 .. X1.16 at 64.0 .. 109.72 (pitch 5.08)
# ---- right edge: ESP32 DEV-KIT (pin J1-1 origin; antenna end at y ~15, USB-C at the bottom edge y = 80) ----
put('M1', 117.5, 23.25, 0)
put('J3', 38.0, 53.0, 0)    # button wires (no anchors) in the free area above TC1; BTN runs to GPIO15 (slow, RC at the pads)
# ---- bottom edge: IBT-2 logic pads (anchors towards the edge), thermocouple modules (terminals at the edge), microSD (slot at the edge) ----
put('J4', 30.0, 65.0, 180)  # pad 1 RPWM at x 30 .. pad 6 GND at 17.3; anchors y 77
put('TC1', 59.5, 59.5, 0)
put('TC2', 86.0, 59.5, 0)
put('SD1', 112.4, 56.4, 180)
# ---- power corner: F1 under J1 (BAT_P pour J1.1 -> F1.1, VBUS pour F1.2 -> J2), TSRs under F1 on the VBUS trunk (route_critical.py) ----
put('F1', 14.0, 21.0, 0)
put('U1', 13.0, 34.0, 0)    # TSR 2-2450: VIN 34.0, GND 36.54, 5V 39.08
put('U2', 27.0, 34.0, 0)    # TSR 2-2433
put('C1', 19.85, 30.56, 270)  # VBUS cap on the trunk (pad 1 at y 29.0, GND pad 32.12)
# ---- shunt under J5 (force pads 1 / 4 into the P1_ECU / P1_EGR lanes from J5.1 / J5.2), INA240 below (route_critical.py) ----
SX, SY = 46.0, 24.0
put('RSH1', SX, SY, 0)
put('R22', 46.0, 32.5, 0)   # K_PLUS (pad 1, left) -> INA_PLUS
put('R23', 46.0, 40.5, 0)   # K_MINUS -> INA_MINUS
put('U4', 52.0, 37.0, 90)   # IN+ (8) top left, IN- (1) bottom left; OUT (5) top right
# ---- ADC: AD7606B turned 90 (V1..V8 down the left side, refs on top, pins 1-16 at the bottom, 17-32 on the right) ----
put('U3', 95.0, 39.0, 90)
# ---- logic ----
put('U6', 108.0, 27.0, 0)   # TCAN1051V under J6.9 / J6.10
put('U8', 64.0, 24.0, 0)    # TPS2553 under J6.1 (SENS_5V runs along the J6 row)
put('U5', 55.5, 50.5, 0)    # 74LVC125 MISO buffer above the module headers
put('U7', 24.0, 53.0, 0)    # 74AHCT125 above J4
# ---- AD7606B neighbourhood transplanted from P05 R3 (same package turned 90, U1 at (58, 54) there; here +37 / -15 mm): decoupling on
# top and bottom, input filter column, test pad; route_critical.route_u3() locks the P05 R3 copper with the same offset ----
DX, DY = 95.0 - 58.0, 39.0 - 54.0
for ref, (x, y, r, *s) in {'C6': (-4.4, 9.25, 270), 'C8': (2.6, -1.438, 90, 'B'), 'C5': (-.7, -15.3, 90), 'C9': (-2.1, -1.438, 90, 'B'),
                           'C10': (3.9, 3.562, 90, 'B'), 'C11': (3.45, -9.3, 90), 'C12': (.8, -9.3, 90), 'C13': (.25, -1.438, 90, 'B'),
                           'C14': (-2.05, -9.25, 90), 'C15': (-5.6, -9.25, 90), 'TP8': (-3.825, -15.4, 0),
                           'C16': (-15.062, -9.6, 180), 'C17': (-15.062, -6.95, 180), 'C18': (-15.062, -4.3, 180), 'C19': (-15.062, -1.65, 180),
                           'C20': (-15.062, 1.0, 180), 'C23': (-13.5, 3.95, 180), 'C21': (-15.062, 6.9, 180), 'C22': (-15.062, 9.55, 180)}.items():
    put(ref, 95.0 + x, 39.0 + y, r, *s)
put('R8', 104.9, 39.25, 0)    # DOUTA 24: the P05 stub ends at x 103.2 on pad 1
# series resistors in the rows of the P05 source stubs (stub at the capacitor row + 1.325 mm, ends at x 76.0); CH1: R11 at the P1_EGR lane
SRC_ROW = {'R13': 32.05, 'R15': 34.7, 'R16': 37.35, 'R17': 40.0, 'R21': 42.95 + .05, 'R18': 45.9, 'R20': 48.55}
for ref, cy in SRC_ROW.items():
    put(ref, 67.5, cy + 1.325, 0)
put('R11', 59.0, 26.6, 0)     # P1_EGR (pad 1) on a locked stub from the lane (route_critical.py), ADC_CH1 by the router
put('TP3', 29.0, 22.6, 0)     # VBUS test pad standing in the locked VBUS pour
# ---- CAN corner (U6 pins 1-4 left x 105.5, 5-8 right x 110.5; antenna rule area from x 113.2 above y 21.8) ----
put('C26', 107.5, 22.2, 0)    # VCC 3 (105.5, 27.6)
put('C27', 113.6, 31.0, 270)  # VIO 5 (110.5, 28.9)
put('D1', 102.6, 19.4, 0)     # at the bus pads J6.8 / J6.9
put('R30', 109.0, 33.6, 0)    # RXD 4 -> GPIO18 (J1-11, y 48.7)
put('R8', 104.6, 39.25, 0)    # DOUTA 24 (39.25): 33 R at the pin
# ---- reserved copper (route_critical.py): force pours, VBUS trunk, Kelvin corridor (no parts on that side) ----
RESERVED = [(s, z) for s in ('F', 'B') for z in [(11.0, 15.0, 17.0, 25.5), (21.4, 18.6, 35.6, 26.0), (30.6, 15.0, 35.6, 23.0),   # BAT_P, VBUS
                                                  (41.4, 15.0, 47.0, 24.9), (47.4, 15.0, 55.4, 28.1)]]                            # P1_ECU, P1_EGR lanes
RESERVED += [(s, (113.0, 0.0, W, 22.0)) for s in ('F', 'B')]   # ANTENNA M1 rule area (build_board.antenna_rect)
RESERVED += [('F', (54.5, 25.4, 57.0, 27.8))]                      # locked P1_EGR stub to R11
RESERVED += [('F', (66.0, y + 1.325 - .7, 76.0, y + 1.325 + .7)) for y in (32.05, 34.7, 37.35, 40.0, 43.0, 45.9, 48.55)]   # locked source stubs to the series resistors
RESERVED += [('F', (75.5, 22.0, 103.6, 50.2)), ('B', (86.0, 30.0, 104.0, 47.0))]   # P05 R3 copper round U3 (route_u3)
RESERVED += [('F', (12.0, 28.4, 28.0, 29.6)), ('F', (41.5, 25.0, 44.0, 41.5)), ('F', (47.6, 19.8, 50.3, 22.0))]   # VBUS trunk, K_PLUS, K_MINUS via
DEC = {'C2': ('U1', '3'), 'C3': ('U2', '3'), 'C24': ('U4', '6'), 'R12': ('C16', '1'), 'R14': ('C17', '1'), 'R19': ('C21', '1'),
         # references first (P05 R3)
       'R7': ('C5', '1'), 'C7': ('C5', '1'), 'R9': ('U3', '11'),
       'R10': ('U3', '13'),
      
      
      
      
       'C29': ('U8', '1'), 'C30': ('U8', '6'), 'R31': ('U8', '5'), 'R32': ('U8', '4'), 'R5': ('U8', '3'),
       'C25': ('U5', '14'), 'R28': ('U5', '1'), 'R29': ('U5', '4'), 'R24': ('TC1', '1'), 'R25': ('TC1', '1'), 'R26': ('TC2', '1'), 'R27': ('TC2', '1'),
       'C28': ('U7', '14'), 'R2': ('U7', '9'), 'R3': ('U7', '2'), 'R4': ('U7', '5'),
       'R1': ('SD1', '6'), 'R6': ('J3', '1'), 'C4': ('J3', '1')}
GND_PIN = {c: (u, g) for c, (u, v, g) in board.DEC_CAPS.items()}
GND_PIN.update({'C2': ('U1', '2'), 'C3': ('U2', '2'), 'C11': ('U3', '35'), 'C12': ('U3', '40'), 'C13': ('U3', '43'), 'C14': ('U3', '43'),
                'C15': ('U3', '46'), 'C5': ('U3', '2'), 'C29': ('U8', '2'), 'C30': ('U8', '2')})
FAILED = []
for c, t in DEC.items():
    tries = [('F', 8), ('F', 16), ('F', 24), ('F', 32)]   # hand assembly: top side only
    for MARG, side, rad in [(mg, s_, r_) for mg in (1.4, .8) for s_, r_ in tries]:
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
MARG = 1.4
# test pads: next to a pad of their net (TP4 / TP10 GND at the supply corner and at the ADC)
TPA = {'TP1': ('U1', '3'), 'TP2': ('U2', '3'), 'TP4': ('U1', '2'), 'TP5': ('U4', '5'), 'TP6': ('M1', 'J3-7'), 'TP7': ('M1', 'J1-13'),
       'TP9': ('U8', '6'), 'TP10': ('C5', '2')}
for t, a in TPA.items():
    for side, rad in (('F', 10), ('F', 20), ('F', 35)):
        try:
            place_near(t, a, own='1', radius=rad, side=side); break
        except SystemExit as e:
            last = e
    else:
        FAILED.append(t); print(last)
missing = [r for r in parts if r not in L]
print('MISSING', missing) if missing else None
for a, c in [(r, o) for r in list(BOX) for o in list(BOX) if r < o and SIDE[r] == SIDE[o]]:
    ba, bc = BOX[a], BOX[c]
    if ba[0] < bc[2] and bc[0] < ba[2] and ba[1] < bc[3] and bc[1] < ba[3]:
        print('OVERLAP', a, c, [round(v, 1) for v in ba], [round(v, 1) for v in bc])
L['_reserved'] = RESERVED
(P / 'src/placement.json').write_text(json.dumps(L, indent=1) + '\n')
if os.environ.get('M1_BOXES'):
    Path(os.environ['M1_BOXES']).write_text(json.dumps({'boxes': BOX, 'side': SIDE, 'reserved': RESERVED, 'holes': HOLES,
                                                        'pads': {r: {n: pad(r, n) for n in geo(r)[0]} for r in L if not r.startswith('_')}}))
far = {r: d for r, d in REPORT.items() if d > 6}
print(len(L) - 1, 'placed; bottom:', sorted(r for r in SIDE if SIDE[r] == 'B'), '; search distance > 6 mm:', far, 'failed:', FAILED)
