"""P04 R3 placement (format S1, class L, slots S1-S3 of level 6). Writes src/placement.json: ref -> [x, y, rotation(, 'B')];
origin = footprint origin (pin 1 for THT library parts, centre for SMD). Board x 0..160 (x = 0: panel side), y 0..100 (0 = edge A,
P12; 100 = edge B, service side). Run with KiCad Python. Machinery (geo, put, free, place_near, place_dec, anchor) from P05 R3 placement.py.

Fixed by S1 (SPECYFIKACJA-FORMATU-S1.md sections 4-7) and docs/MECHANIKA.md:
- J_BP1 (IDC 2x8, slot S1), J_BP2 and J_BP3 (IDC 2x10, slots S2 / S3): mating face at y = 0, pin centre x = 26.5 / 80.0 / 133.5,
  pin 1 at the smaller x;
- J_SV1 (1x13), J_SV2 / J_SV3 (1x7), right angle: pins in x 10..43 of their slot, pin 1 at the larger x, ~6 mm beyond edge B;
- 12 M3 holes (x 4 / 49 per slot, y 14 / 86) with the D7 standoff zones; reserved strips of edge A (y 0..10, x 10..43 per slot).
Blocks (by the connector their signals use): slot S1 = panel side of the logic (U5 SENSOR / MOTOR permits and SUP_OK, U4 output gates,
U3 ARM latch, U11 local supervisor); slot S2 = SAFE_N node (U2 with C18 / R5 at U2.11, Q1-Q3, R4) right under J_BP2.16, the
interlock gates U7 / U6 and the DRIVE / SENSOR / PG input buffer U10 under J_BP2; slot S3 = P03 interface: U9 under J_BP3 with
pin 5 (SUP_N_OUT) straight below J_BP3.12 (short reset line, README), U8 (PWM, HEARTBEAT, MCU_ARM, SENSOR_ENABLE), watchdog U1 with
C1 / R1 at U1.15 / U1.14 (MECHANIKA: short, away from PWM), LED1, bulk C3.
Decoupling capacitors at the supply pin of their part (place_dec: supply pad <= 5.5 mm, GND pad as close as possible to the GND pin).
All parts on the top side (S1-2 allows SMD <= 1.5 mm on the bottom; the board has room, one-sided assembly).
"""
import pcbnew as p, json, math, sys, os
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
from pathlib import Path
P = Path(__file__).resolve().parents[1]
S1 = json.loads((P.parents[0] / 'Format-S1/format-s1.json').read_text(encoding='utf-8'))
parts = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
W, H = S1['klasy']['L']['W'], S1['klasy']['L']['H']
STEP = S1['rozstaw_slotow']
HOLES = [(x + STEP * k, y) for k in range(3) for x in S1['otwory_M3']['x_w_slocie'] for y in S1['otwory_M3']['y']]
RZ = S1['otwory_M3']['strefa_dystansu_srednica'] / 2
STRIPS_A = [(STEP * k + 10.0, S1['krawedz_A']['strefa_y'][0], STEP * k + 43.0, S1['krawedz_A']['strefa_y'][1]) for k in range(3)]
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
    return [(*pad(r, n), g[3]) for r in L for n, g in geo(r)[0].items() if g[2] > 0]


def is_tht(ref):
    return any(g[2] > 0 for g in geo(ref)[0].values())


RESERVED = []   # (side, box): copper reserved for route_critical.py, silk labels above the service headers


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
    for zs, z in RESERVED:
        if zs == side and b[0] < z[2] and z[0] < b[2] and b[1] < z[3] and z[1] < b[3]:
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


def place_dec(ref, target, gnd, radius=8.0, side='F', sup_max=5.5):
    """P05 R3 (review 2.10): decoupling capacitor at the free position with the smallest (supply pad -> pin) + (GND pad -> GND pin)."""
    tref, tpad = target; tx, ty = pad(tref, tpad); tnet = parts[tref]['pins'][str(tpad)]
    own = next(k for k, n in parts[ref]['pins'].items() if n == tnet); gown = next(k for k, n in parts[ref]['pins'].items() if n == 'GND')
    gx, gy = pad(*gnd); (lx, ly, *_), (mx, my, *_) = geo(ref)[0][own], geo(ref)[0][gown]; step = .25; n = int(radius / step); best = None
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            if math.hypot(i, j) * step > radius:
                continue
            for r in (0, 90, 180, 270):
                ox, oy = tf(lx, ly, 0, 0, r)
                x, y = tx + i * step - ox, ty + j * step - oy
                ds = math.dist(tf(lx, ly, x, y, r, side), (tx, ty)); dg = math.dist(tf(mx, my, x, y, r, side), (gx, gy))
                if ds > sup_max or (best and ds + .3 * dg >= best[0]):
                    continue
                if free(box(ref, (x, y, r), side), .5, own=ref, side=side):
                    best = (ds + .3 * dg, x, y, r, ds)
    if not best:
        raise SystemExit(f'no place for {ref} near {target} ({side})')
    put(ref, best[1], best[2], best[3], side); REPORT[ref] = round(best[4], 2)


# ---- fixed by S1 ----
put('J_BP1', 26.5 - 3.5 * 2.54, 13.33, 90)      # IDC 2x8: pin 1 x 17.61 (smaller x), odd row y 13.33, even row 10.79, face y = 0
put('J_BP2', 80.0 - 4.5 * 2.54, 13.33, 90)      # IDC 2x10: pin 1 x 68.57
put('J_BP3', 133.5 - 4.5 * 2.54, 13.33, 90)     # pin 1 x 122.07
put('J_SV1', 26.5 + 6 * 2.54, 95.96, 270)       # 1x13: pin 1 x 41.74 (larger x), pin 13 x 11.26; body front y = 100
put('J_SV2', 80.0 + 3 * 2.54, 95.96, 270)       # 1x7: pin 1 x 87.62, pin 7 x 72.38
put('J_SV3', 133.5 + 3 * 2.54, 95.96, 270)      # pin 1 x 141.12, pin 7 x 125.88
# service labels above the headers (silkscreen.py: vertical, up to 7 characters of 1.0 mm from y 93.9 up)
RESERVED += [('F', (9.5, 86.0, 43.5, 95.5)), ('F', (70.6, 86.0, 89.4, 95.5)), ('F', (124.1, 86.0, 142.9, 95.5))]
# copper of route_critical.py (supply escapes of the even-row J_BP pins on B.Cu, vias just below the odd row at y 16.6): no part there
RESERVED += [('F', (14.6, 10.0, 16.2, 17.2)), ('F', (66.1, 10.0, 67.7, 17.4)), ('F', (92.3, 10.0, 93.9, 17.4)),
             ('F', (118.7, 10.0, 121.5, 17.4))]
# ---- ICs (DIP rot 0: pin 1 top left, pins 1-7 down at x, 8-14 up at x + 7.62; DIP-16 pin 16 top right) ----
Y0 = 34.0
put('U5', 6.0, Y0); put('U4', 23.0, Y0); put('U3', 40.0, Y0)            # slot S1
put('U7', 60.0, Y0); put('U2', 78.0, Y0); put('U6', 96.0, Y0)           # slot S2: U2.11 (SAFE_N) at x 85.62, under J_BP2.16 (x 86.35)
put('U1', 122.0, Y0)                                                    # slot S3: watchdog
# SOIC-14 buffers (origin = centre). U10 rot 0 under J_BP2 (pin 2 DRIVE_OK under J_BP2.8). U9 / U8 rot 270: pins 1-7 in the top row
# (y - 2.475), pin 5 of U9 at x 134.77 = J_BP3.12 (SUP_N_OUT).
put('U10', 80.0, 23.5, 0)
put('U9', 134.77 + 1.27, 22.5, 270)
put('U8', 148.0, 28.5, 270)                                          # run 2: at y 22.5 HEARTBEAT (J_BP3.16 -> U8.5) found no path
# watchdog timing: C1 (MKS2 1 uF) pad 1 level with U1.15, pad 2 5 mm lower (rot 270); R1 220 k above C1.1 (pad 2 = WD_RC over C1.1)
u15 = pad('U1', '15'); put('C1', u15[0] + 5.6, u15[1], 270)
put('R1', pad('C1', '1')[0] - 1.55, u15[1] - 4.3, 0)
# SAFE_N node: Q1-Q3 (TO-92, pin 3 = collector on SAFE_N) in a column right of U2, bases (pin 2) facing the U2 outputs; C18 at U2.11
u11 = pad('U2', '11')
put('Q1', 90.6, 56.0, 0); put('Q2', 90.6, 61.5, 0); put('Q3', 90.6, 67.0, 0)
put('U11', 10.0, 60.0, 0)                                               # MCP100 below U5 (LOCAL_SUP_N -> U5.10)
put('C3', 64.0, 24.5, 0)                                                # 10 uF bulk at the 3V3_IO entry of J_BP2.10 (escape via x 66.9)
put('LED1', 150.0, 62.0, 0)                                             # power LED, slot S3, visible from above
# ends of the supply escapes (route_critical.py): P04_3V3 via (93.1, 16.6) -> R39.2 -> R60.1; 5V_SYS via (120.7, 16.6) -> R57.1
put('R39', 95.5, 19.0, 180)                                             # pad 2 (P04_3V3) x 93.95, pad 1 (3V3_IO) x 97.05
put('R60', 93.95, 22.9, 270)                                            # pad 1 (P04_3V3) y 21.35 under R39.2, pad 2 (SRV) y 24.45
put('R40', 17.61, 17.9, 90)                                            # PANEL_3V3: pad 2 y 16.35 under J_BP1.1, F.Cu escape of J_BP1.2 round pin 1
put('R57', 120.7, 19.85, 270)                                           # pad 1 (5V_SYS) y 18.3 under the escape via
RESERVED += [('F', (132.6, 14.8, 135.6, 18.6))]                         # SUP_N_OUT: B.Cu escape of J_BP3.12, via (133.5, 16.4), F.Cu to U9.5
# passives at the pin they serve: (anchor ref, anchor pad); the part's pad on the same net goes next to it. Order = priority.
DEC = {'C18': ('U2', '11'), 'R5': ('U2', '11'), 'R4': ('U2', '11'),
       'R2': ('U2', '3'), 'C2': ('U2', '3'), 'R6': ('U2', '2'), 'R7': ('U2', '6'), 'R8': ('U2', '8'),
       'R9': ('Q1', '2'), 'R10': ('Q2', '2'), 'R11': ('Q3', '2'),
       'R42': ('J_BP1', '4'), 'R3': ('J_BP1', '8'), 'R41': ('J_BP1', '14'),
       'R24': ('R42', '2'), 'R23': ('R41', '2'),
       'R38': ('J_BP2', '20'),
       'R17': ('U9', '5'), 'R16': ('U9', '2'), 'R18': ('U9', '9'), 'R19': ('U9', '12'),
       'R30': ('U9', '6'), 'R29': ('U9', '3'), 'R31': ('U9', '8'), 'R32': ('U9', '11'),
       'R12': ('U8', '2'), 'R13': ('U8', '5'), 'R14': ('U8', '9'), 'R15': ('U8', '12'),
       'R25': ('U8', '3'), 'R26': ('U8', '6'), 'R27': ('U8', '8'), 'R28': ('U8', '11'),
       'R20': ('U10', '2'), 'R21': ('U10', '5'), 'R22': ('U10', '9'), 'R33': ('U10', '3'), 'R34': ('U10', '6'), 'R35': ('U10', '8'),
       'R36': ('U7', '6'), 'R37': ('LED1', '2')}
GND_PIN = {}
from board import DEC_CAPS
for c, (u, v, g) in DEC_CAPS.items():
    GND_PIN[c] = (u, g)
from board import DIP_SPINES
for c, u in DIP_SPINES.items():   # run 3: DIP 100 nF above the body, rot 180: pad 1 (3V3_IO) x + 7.15 by pin 14 / 16, pad 2 (GND) x + 4.05
    put(c, L[u][0] + 5.6, L[u][1] - 3.2, 180)   # over the body centre line, where the GND spine of route_critical.py starts
FAILED = []
for c, (u, v, g) in DEC_CAPS.items():   # decoupling first (supply pin), then the rest
    if c in L:
        continue
    try:
        place_dec(c, (u, v), (u, g))
    except SystemExit:
        place_near(c, (u, v), radius=10); print('decoupling fallback', c)
for c, t in DEC.items():
    for rad in (8, 16):
        try:
            place_near(c, t, radius=rad); break
        except SystemExit as e:
            last = e
    else:
        FAILED.append(c); print(last)
SERVICE = sorted((r for r, v in parts.items() if v['source_ref'].startswith('ADDED_SERVICE')), key=lambda r: int(r[1:]))
ANCHOR_ORDER = ('U1', 'U2', 'U3', 'U4', 'U5', 'U6', 'U7', 'U8', 'U9', 'U10', 'U11', 'Q', 'J_BP', 'C', 'R', 'LED')


def anchor(ref, nets=None):
    """First placed pad (in ANCHOR_ORDER) sharing a net with `ref` (GND and service-pin nets ignored): (anchor ref, pad, own pad)."""
    own = {k: n for k, n in parts[ref]['pins'].items() if n not in ('GND', 'NC') and not n.split('/')[-1].startswith('SRV_') and (nets is None or n in nets)}
    for pref in ANCHOR_ORDER:
        for r in sorted(L, key=lambda q: (len(q), q)):
            if not r.startswith(pref) or r == ref or r.startswith('J_SV'):
                continue
            for n, net in parts[r]['pins'].items():
                k = next((k for k, m in own.items() if m == net), None)
                if k is not None and n in geo(r)[0]:
                    return r, n, k
    return None


# service resistors (node side = pin 1) at a pad of their node; explicit where the node has a preferred end
SERVICE_ANCHOR = {'R43': ('Q1', '3'), 'R58': ('C3', '1'), 'R59': ('R40', '2'), 'R61': ('R38', '2'),
                  'R53': ('U7', '6'), 'R49': ('U1', '13'), 'R50': ('Q1', '2'), 'R52': ('U5', '8'), 'R47': ('U2', '12'), 'R48': ('U3', '1')}   # run 4: at U7.11 the nearest free spot was 10.3 mm away
for r in [r for r in SERVICE if r not in L]:
    a = SERVICE_ANCHOR.get(r) or anchor(r, {parts[r]['pins']['1']})
    assert a, ('no node', r)
    place_near(r, (a[0], a[1]), own='1', radius=16)
rest = [r for r in parts if parts[r].get('on_board', True) and r not in L]
for r in rest:   # anything left: next to the first pad sharing a net
    a = anchor(r); assert a, ('no anchor', r)
    place_near(r, (a[0], a[1]), own=a[2], radius=16); print('auto', r, 'at', a[:2])
missing_fixed = [r for r in ('J_BP1', 'J_BP2', 'J_BP3', 'J_SV1', 'J_SV2', 'J_SV3', 'U1', 'U9') if r not in L]
assert not missing_fixed, missing_fixed
for a, c in [(r, o) for r in list(BOX) for o in list(BOX) if r < o and SIDE[r] == SIDE[o]]:
    ba, bc = BOX[a], BOX[c]
    if ba[0] < bc[2] and bc[0] < ba[2] and ba[1] < bc[3] and bc[1] < ba[3]:
        print('OVERLAP', a, c, [round(v, 1) for v in ba], [round(v, 1) for v in bc])
(P / 'src/placement.json').write_text(json.dumps(L, indent=1) + '\n')
if os.environ.get('P04_BOXES'):   # development preview only (courtyard boxes and pads)
    Path(os.environ['P04_BOXES']).write_text(json.dumps({'boxes': BOX, 'side': SIDE, 'pads': {r: {n: pad(r, n) for n in geo(r)[0]} for r in L}}))
far = {r: d for r, d in REPORT.items() if d > 6}
print(len(L), 'placed; search distance > 6 mm:', far, '; failed:', FAILED)
