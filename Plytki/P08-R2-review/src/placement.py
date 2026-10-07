"""P08 R2 placement (format S1, class 1/3, slot S1 of level 5). Writes src/placement.json: ref -> [x, y, rotation(, 'B')]; origin =
footprint origin (pin 1 for THT library parts and the wire field, centre for SMD). Board x 0..53 (x = 0: panel side of the enclosure,
where the TEST port is), y 0..100 (0 = edge A, P12; 100 = edge B, service side). Run with KiCad Python.
Machinery (geo, place_near, bottom-side support) from P09 R2 / P10 R2 placement.py (30.09-1.10.2026).

Fixed by S1 (SPECYFIKACJA-FORMATU-S1.md sections 4-7) and the BOM notes:
- J1 (J_BP, IDC 2x8 right angle): mating face at y = 0, pin centre x = 26.5, pin 1 at the smaller x (as P09 R2 J1);
- J2 (service header 1x13 right angle): pins in x 11.26..41.74, ~6 mm beyond edge B; pin 1 at the LARGER x (a right-angle header on
  the top side with its pins towards edge B cannot have it the other way; as P09 / P10 R2 J2);
- 4 M3 holes (x 4 / 49, y 14 / 86) with the D7 standoff zones; the reserved strip of edge A (y 0..10, x 10..43) holds J1 only;
- level 5 (S1-3): THT, SOIC, SOT-23 and the capacitors on the top; only the 1206 service resistors R19..R29 on the bottom (S1-2:
  SMD <= 1.5 mm, >= 1 mm from THT pads, outside the standoff zones; S1 section 9: "service resistors under the header").
Sensor block at the panel side: J4 (TSENSOR wire field, rotated 90: anchor holes 12 mm towards x = 0, the pair leaves through the panel
to the TEST port; pad 1 = 5V_SENSOR below pad 2 = AGND_SENSOR) and K1 right of it, rotated 270 so its NO contacts 4 / 5 face the J4 pads
(5V_SENSOR F.Cu, AGND_SENSOR B.Cu: the two short PTH-to-PTH lines cross on different layers, route_critical.py). U1 (TPS2553) above
K1 with OUT (pin 6) next to COM_A (K1.3); U2 (TBD62083, DIP18 lying along x) below K1 with O1 (pin 18) at the coil end K1.8; D1 beside
the coil pins. U8 / R15 / R16 (EN guard) right of U1. Logic: U5 (input / HEALTHY buffer) and U4 (supervisor / OK buffer) under J1
next to their J_BP pins, U3 (HC08) below them, supervisors U6 / U7 in the right column.
Passives: nearest free spot at the pin they belong to (decoupling: IC supply pin; pulls: the buffer pin; series: the driver pin;
service resistors: pin 1 at a pad of their node, S1 section 6).
"""
import pcbnew as p, json, math
from pathlib import Path
P = Path(__file__).resolve().parents[1]
S1 = json.loads((P.parents[0] / 'Format-S1/format-s1.json').read_text(encoding='utf-8'))
parts = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
W, H = S1['klasy']['1/3']['W'], S1['klasy']['1/3']['H']
HOLES = [(x, y) for x in S1['otwory_M3']['x_w_slocie'] for y in S1['otwory_M3']['y']]
RZ = S1['otwory_M3']['strefa_dystansu_srednica'] / 2
STRIP_A = (10.0, S1['krawedz_A']['strefa_y'][0], 43.0, S1['krawedz_A']['strefa_y'][1])   # S1 section 5, slot S1 = the whole board
JX, JY = 15.5, 62.5                       # J4 pad 1 (5V_SENSOR); pad 2 at JY - 3.5; anchor holes at (JX - 12, JY + 3.5 / JY - 7)
SUPPORT = [(JX - 12, JY + 3.5), (JX - 12, JY - 7.0)]   # anchor holes of J4 (cable tie)
SUPPORT_R = 3.0                           # board.SUPPORT_KEEPOUT['J4']
KX, KY = 27.1, 57.0                       # K1 pin 1 (coil +); NO contacts 4 / 5 at x = KX - 7.6
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
    for r, o in BOX.items():
        if r == own or SIDE[r] != side:
            continue   # courtyards of the other side do not block; THT pads are checked below for the bottom
        if b[0] - m < o[2] and o[0] < b[2] + m and b[1] - m < o[3] and o[1] < b[3] + m:
            return False
    if b[0] < STRIP_A[2] and STRIP_A[0] < b[2] and b[1] < STRIP_A[3] and STRIP_A[1] < b[3]:
        return False   # reserved strip of edge A (J1 is put() directly)
    for (hx, hy), rr in [(h, RZ) for h in HOLES] + [(h, SUPPORT_R) for h in SUPPORT]:
        dx = max(b[0] - hx, 0, hx - b[2]); dy = max(b[1] - hy, 0, hy - b[3])
        if math.hypot(dx, dy) < rr + .1:
            return False
    if side == 'B':   # S1-2: >= 1 mm from THT pads (copper to courtyard, conservative)
        for tx, ty, tr in tht_pads():
            dx = max(b[0] - tx, 0, tx - b[2]); dy = max(b[1] - ty, 0, ty - b[3])
            if math.hypot(dx, dy) < tr + 1.0:
                return False
    return True


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
        if free(box(ref, (x, y, r), side), m, own=ref, side=side):
            put(ref, x, y, r, side); REPORT[ref] = round(d, 2); return
    raise SystemExit(f'no place for {ref} near {target} ({side})')


# ---- fixed by S1 ----
put('J1', 26.5 - 3.5 * 2.54, 13.33, 90)      # pin 1 (x 17.61) at the smaller x; mating face at y = 0 (as P09 R2 J1)
put('J2', 26.5 + 15.24, 95.96, 270)          # pin 1 at x 41.74 (larger x), pin 13 at 11.26; body front at y = 100
# ---- sensor block at the panel side ----
put('J4', JX, JY, 90)                         # courtyard x 1.47..17.03; anchors at x 3.5 (hole edge 1.9 mm from x = 0)
# (the pair between the anchor and the panel lies over the J4 courtyard, x 1.5..17: nothing else is placed there)
put('K1', KX, KY, 270)                        # 4 (5V_SENSOR) / 5 (AGND_SENSOR) at x 19.5, 3 (COM_A) / 6 (COM_B GND) at x 21.7, coil at x 27.1
put('U1', 24.5, KY - 3.9, 180)                # OUT 6 / ILIM 5 / FAULT 4 at x 23.36 (left), IN 1 / GND 2 / EN 3 at x 25.64; OUT bottom left
put('D1', KX + 3.5, KY - 1.0, 270)            # cathode (5V_SYS) at the coil + end, anode at the coil - end
put('U2', 21.0, KY + 17.5, 90)                # pins 1..9 at y KY + 17.5, 18..10 at y KY + 9.88; O1 (18) at x 21 under K1.8
put('U8', 34.0, KY - 4.0, 0)                  # EN guard (RESET = TPS_EN at pin 1) right of U1
put('C1', 29.6, KY - 3.9, 180)                # 5.10: input capacitor with its GND pad (2) 2.4 mm right of U1.2 (locked GND tie, route_critical.py)
# ---- logic under J1 ----
put('U5', 13.5, 23.5, 0)                      # SENSOR_PERMIT in (J1.6) / HEALTHY out (J1.10)
put('U4', 39.5, 23.5, 0)                      # SUP5 buffer, OK out (J1.8)
put('U3', 19.5, 38.0, 90)                     # HC08 lying along x: pins 1..7 at y 38.0, 14..8 at y 30.38
put('U7', 44.0, 33.0, 0)                      # 5 V supervisor
put('U6', 44.0, 41.5, 0)                      # 3.3 V supervisor
# 5.10: decoupling of the TO-92 supervisors right under VDD (2) / VSS (3): C pad 1 under pin 2, pad 2 under pin 3, joined by locked ties
# (route_critical.py; the router left U8.3 45 mm of GND copper away from C8 in one run)
for c, u in (('C6', 'U6'), ('C7', 'U7'), ('C8', 'U8')):
    x2, y2 = pad(u, '2'); x3, _ = pad(u, '3'); put(c, (x2 + x3) / 2, y2 + 3.75, 0)
for a, c in [(r, o) for r in list(BOX) for o in list(BOX) if r < o]:
    ba, bc = BOX[a], BOX[c]
    assert not (ba[0] < bc[2] and bc[0] < ba[2] and ba[1] < bc[3] and bc[1] < ba[3]), ('fixed parts overlap', a, c, ba, bc)
# 5.10: the locked GND via of the U1.2 -> C1.2 tie (route_critical.py, 1.2 mm right of U1.2) stays free of bottom parts (R19 sat on it)
gx, gy = pad('U1', '2'); BOX['GVIA'] = (gx + 1.2 - 1.0, gy - 1.0, gx + 1.2 + 1.0, gy + 1.0); SIDE['GVIA'] = 'B'
# 5.10: corridor of the locked sensor lines (route_critical.py) between the J4 pads and K1.4 / K1.5, kept free of passives
BOX['SENS'] = (pad('J4', '1')[0] - 1.2, pad('J4', '2')[1] - 1.2, pad('K1', '4')[0] + 1.0, pad('K1', '5')[1] + 1.2); SIDE['SENS'] = 'F'
# ---- discharge of the sensor output first (R18 across 5V_SENSOR / AGND_SENSOR, at the K1 NO contacts) ----
place_near('R18', ('K1', '4'), rots=(90, 270))
# ---- decoupling and bulk ----
for c, (u, n) in {'C2': ('U1', 6), 'C3': ('U3', 14), 'C4': ('U4', 14), 'C5': ('U5', 14), 'C9': ('K1', 1)}.items():
    place_near(c, (u, str(n)))
place_near('C10', ('U2', '10'), radius=20)
# ---- current limit, EN divider, discharge ----
place_near('R1', ('U1', '5'))
place_near('R16', ('U8', '1'))
place_near('R15', ('U8', '1'), own='2')
place_near('R17', ('C2', '1'))
# ---- series resistors at their drivers, pulls at the buffer / gate pins ----
for r, (u, n) in {'R11': ('U4', 6), 'R13': ('U5', 6)}.items():
    place_near(r, (u, str(n)), own='1')
PULL = {'R2': ('U1', 4), 'R3': ('U6', 1), 'R4': ('U7', 1), 'R5': ('U4', 3), 'R6': ('U5', 3), 'R7': ('U5', 2), 'R8': ('U3', 3),
        'R9': ('U3', 6), 'R10': ('U3', 8), 'R12': ('R11', 2), 'R14': ('R13', 2)}
for r, (u, n) in PULL.items():
    place_near(r, (u, str(n)), radius=20)
# ---- service resistors on the bottom: node side (pin 1) next to a pad of the node ----
NODE = {'R19': ('C1', 1), 'R20': ('C3', 1), 'R21': ('U6', 1), 'R22': ('U4', 3), 'R23': ('R12', 1), 'R24': ('R14', 1), 'R25': ('U5', 3),
        'R26': ('U2', 1), 'R27': ('U8', 1), 'R28': ('R17', 1), 'R29': ('R2', 2)}
for r, (u, n) in NODE.items():
    place_near(r, (u, str(n)), own='1', radius=12, side='B')
missing = sorted(set(r for r, v in parts.items() if v.get('on_board', True)) - set(L)); assert not missing, missing
(P / 'src/placement.json').write_text(json.dumps(L, indent=1) + '\n')
far = {r: d for r, d in REPORT.items() if d > 6}
print(len(L), 'placed; search distance > 6 mm:', far)
