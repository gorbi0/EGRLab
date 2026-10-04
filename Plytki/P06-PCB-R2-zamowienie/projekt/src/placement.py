"""P06 R2 placement (format S1, class 2/3, slots S1-S2 of level 4). Writes src/placement.json: ref -> [x, y, rotation(, 'B')];
origin = footprint origin (pin 1 for THT library parts and the tails, centre for SMD; J3 numbered from the far end: origin = pad 2).
Board x 0..106.5 (x = 0: panel side - ISERIES J3, BYPASS J4 / J5, S1 section 7), y 0..100 (0 = edge A, P12; 100 = edge B, service).
Run with KiCad Python. Machinery (geo, place_near, bottom side, strip A, reserved areas) from P05 R3 placement.py.

Fixed by S1 (SPECYFIKACJA-FORMATU-S1.md sections 4-7) and the README layout requirements:
- J_BP (IDC 2x8, slot S2): mating face at y = 0, pin centre x = 80.0, pin 1 at the smaller x; edge-A strip only along it (x 63.5..96.5);
- J_SV1 (1x7, x 10..43) and J_SV2 (1x13, x 63.5..96.5), right angle, pin 1 at the larger x, ~6 mm beyond edge B;
- 8 M3 holes (x 4 / 49 / 57.5 / 102.5, y 14 / 86) with the D7 standoff zones;
- J3, J4, J5 at x = 0 (soldered tails: anchors 12 mm from the pad row towards the wall, the cable lies on the board between them).
Blocks: left column = the three tails, J3 (ISERIES) at the top with RSH1 right of it: the measuring loop J3.1 -> RSH1 -> J3.2 is one
pad pitch long; J4 (BYPASS) under J3 with EGR_P1 next to EGR_P1 (J3 numbered from the far end), ECU_P1 of J3 and J4 joined by a
strip between the anchors and the pads (route_critical.py). RSH1 turned 270: ECU force pad up, EGR force pad down, sense pads on the
diagonal; K_PLUS runs under the body between the force pads to the right, K_MINUS leaves to the right below it, both straight into
R1 / R2 and U1 (INA240, turned 90: IN+ pin 8 top left, IN- pin 1 bottom left). Analog chain to the right of U1 (U2 MCP6022, U3
MCP3201, reference U10 with C5 within 5 mm); buffers U5 under J_BP; READY logic (U6, U7, U8, U9) and supply (R6, C3, U4, D1) right;
J5 with the hot R21 (0.7 W, PR02 lying) bottom left, far from RSH1, U1 and U10, above J_SV1 only at its left end.
Service resistors R25-R38 on the bottom at their nodes where room allows (S1-2: SMD <= 1.5 mm, >= 1 mm from THT pads).
"""
import pcbnew as p, json, math, sys, os
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
from pathlib import Path
P = Path(__file__).resolve().parents[1]
S1 = json.loads((P.parents[0] / 'Format-S1/format-s1.json').read_text(encoding='utf-8'))
parts = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
W, H = S1['klasy']['2/3']['W'], S1['klasy']['2/3']['H']
STEP = S1['rozstaw_slotow']
HOLES = [(x + STEP * k, y) for k in range(2) for x in S1['otwory_M3']['x_w_slocie'] for y in S1['otwory_M3']['y']]
RZ = S1['otwory_M3']['strefa_dystansu_srednica'] / 2
STRIPS_A = [(63.5, S1['krawedz_A']['strefa_y'][0], 96.5, S1['krawedz_A']['strefa_y'][1])]   # README: only along J_BP (slot S1 has none)
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


def is_tht(ref):
    return any(g[2] > 0 for g in geo(ref)[0].values())


PENDING = {}


def free(b, m=.5, own=None, side='F'):
    if b[0] < .6 or b[1] < .6 or b[2] > W - .6 or b[3] > H - .6:
        return False
    for z in STRIPS_A:   # the edge-A strip of slot S2 holds only J_BP (put() directly)
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
    for zs, z in RESERVED:   # copper reserved for route_critical.py (force pours, Kelvin pair) and the cables of the tails
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
                                      for px, py, pr in PENDING.get(own, [])):
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
        PENDING[ref] = [(*tf(g[0], g[1], x, y, r, side), g[3]) for g in geo(ref)[0].values() if g[2] > 0]
        if free(box(ref, (x, y, r), side), m, own=ref, side=side):
            put(ref, x, y, r, side); REPORT[ref] = round(d, 2); return
    raise SystemExit(f'no place for {ref} near {target} ({side})')


# ---- fixed by S1 ----
put('J_BP', 80.0 - 3.5 * 2.54, 13.33, 90)       # pin 1 (x 71.11) at the smaller x; mating face at y = 0 (as P05 R3 J_BP2)
put('J_SV1', 26.5 + 15.24, 95.96, 270)          # 1x7: pin 1 at x 41.74 (larger x), pin 7 at 26.5 - right part of slot S1, away from R21
put('J_SV2', 80.0 + 15.24, 95.96, 270)          # 1x13: pin 1 at x 95.24, pin 13 at 64.76
# ---- panel side (x = 0): the three tails in one column between the M3 zones (y 17.5..82.5); pad rows at x 15, anchors at x 3 ----
TX = 15.0
put('J3', TX, 31.12, 90)                        # numbered from the far end: J3.1 (ECU_P1) y 23.5, J3.2 (EGR_P1) y 31.12; courtyard y 18.0..36.6
put('J4', TX, 52.62, 90)                        # J4.2 (EGR_P1) y 45.0 next to J3.2, J4.1 (ECU_P1) y 52.62; courtyard y 39.5..58.1
put('J5', TX, 73.5, 90)                         # J5.3 GND y 66.5, J5.2 SW_RAW y 70.0, J5.1 5VA y 73.5; courtyard y 61.0..79.0
# ---- shunt, Kelvin pair and INA240 (README: Kelvin from the sense pads, as a pair, symmetric, U1 close to the shunt) ----
SX, SY = 22.0, 31.12 - 2.985                    # RSH1 turned 270: EGR force pad level with J3.2, ECU force pad 6 mm above it
put('RSH1', SX, SY, 270)
KP_Y, KM_Y = SY, pad('RSH1', '3')[1]            # K_PLUS leaves under the body at the shunt centre line, K_MINUS level with its sense pad
put('R1', 29.0, KP_Y, 0); put('R2', 29.0, KM_Y, 0)   # pad 1 = K_PLUS / K_MINUS towards the shunt, pad 2 = INA_PLUS / INA_MINUS
put('U1', 36.6, (KP_Y + KM_Y) / 2, 90)          # IN+ (8) top left, IN- (1) bottom left, VS (6) / REF1 (7) / OUT (5) top row
# ---- hot R21 (PR02, 17.78 mm, 0.7 W) at J5, bottom left; 8 mm right of the M3 zone at (4, 86) ----
put('R21', 10.5, 82.5, 0)                       # pad 1 SW_RAW (x 10.5), pad 2 GND (x 28.28)
# ---- supply: 5V_SYS from J_BP.10/12 -> R6 1 Ohm (1 W lying) -> 5VA_P06 at C3; LDO U4 -> 3V3_P06 ----
put('R6', 84.5, 20.0, 180)                      # pad 1 5V_SYS (x 84.5) under J_BP.10/12, pad 2 5VA (x 69.26) towards the consumers on the left
put('C3', 62.5, 21.5, 0)                        # 220 uF at R6.2, 4.3 mm from the M3 zone at (57.5, 14)
put('U4', 62.0, 41.0, 0)                        # MCP1702 TO-92: 1 GND, 2 VIN (5VA), 3 VOUT (3V3) between the analog block and the logic
put('D1', 60.0, 50.5, 0)                        # 1N5819: cathode (pad 1, 5VA) left, anode (pad 2, 3V3) right; 2.10: 3.5 mm lower, the
                                                # input / output capacitors of U4 fit between it and U4 at the GND pin (return-path check)
# ---- analog chain right of U1 ----
put('U2', 45.0, 27.0, 0)                        # MCP6022 DIP8: 3 (I_DIV) and 1/2 (ADC_BUF) left, 5..8 right (REF25, REF_BUF, 3V3)
put('U3', 57.0, 27.0, 0)                        # MCP3201 DIP8: 1 VREF, 2 IN+, 3 IN-, 4 VSS left; 8 VDD, 7 CLK, 6 DOUT, 5 CS right
put('U10', 50.0, 41.0, 0)                       # MCP1525 TO-92: 1 GND, 2 REF25, 3 VIN (3V3); C5 within 5 mm (verify_pcb.py)
put('D2', 40.0, 41.0, 0)                        # BAT85: cathode 3V3 (pad 1), anode REF25 (pad 2) towards U10.2
put('R11', 67.5, 33.0, 90)                      # owned MF0207 47k standing: 3V3 -> ADC_DOUT pull-up between U3.6 and U5.9
# ---- serial buffers U5 under J_BP; READY logic right ----
put('U5', 75.0, 28.5, 270)                      # LVC125: top row 7..1 faces J_BP (SCLK pin 5 under J_BP.2, CS_ILOG pin 2 under J_BP.6)
put('U6', 93.0, 34.0, 270)                      # LVC125 (READY): LOGGER_OK_TX (8) -> R19 -> J_BP.8
put('U7', 76.0, 40.0, 0)                        # HC08 DIP14
put('U8', 89.0, 45.0, 0); put('U9', 89.0, 52.0, 0)   # MCP120-300 (3V3) / -450 (5VA), D bondout
# review 2.10 re-route: R10 (100k pull-down of ADC_SCLK at U5.5) on the bottom under U5. DEC put it on top right under U5.10
# (CS_LOCAL_N, the OE of the DOUT buffer): with the analog keepouts five router attempts in six left U5.10 walled in.
put('R10', 75.5, 28.5, 90, 'B')
# ---- reserved areas (no parts): force pours and Kelvin corridor (both layers), cables of the tails (wall .. pad rows) ----
RESERVED = [('F', (5.5, 18.0, 27.5, 58.2)), ('B', (5.5, 18.0, 27.5, 58.2)),
            ('F', (23.6, 26.5, 33.6, 33.3)), ('B', (17.0, 24.0, 35.0, 35.0)),
            ('F', (0.0, 18.0, 12.75, 79.0)), ('B', (0.0, 18.0, 12.75, 79.0)),
            ('F', (71.9, 31.9, 75.3, 37.5))]   # review 2.10 re-route: escapes of U5.9 (ADC_DOUT) / U5.10 (CS_LOCAL_N) downwards, no part there
# passives at the pin they serve: (anchor ref, anchor pad); the part's pad on the same net goes next to it. Order = priority.
DEC = {'C6': ('U1', '6'), 'C1': ('U2', '3'), 'R4': ('U2', '3'), 'R3': ('U1', '5'), 'R5': ('U2', '1'), 'C2': ('U3', '2'),
       'C5': ('U10', '2'), 'C16': ('U3', '1'), 'C7': ('U2', '8'), 'C8': ('U3', '8'), 'C15': ('U10', '3'),
       'C4': ('U4', '3'), 'C9': ('U4', '2'), 'C10': ('U5', '14'), 'C11': ('U6', '14'), 'C12': ('U7', '14'), 'C13': ('U8', '2'),
       'C14': ('U9', '2'), 'R7': ('U3', '5'), 'R9': ('U3', '7'), 'R8': ('U5', '2'), 'R12': ('U5', '8'),
       'R13': ('U9', '1'), 'R14': ('U8', '1'), 'R15': ('U6', '3'), 'R16': ('U6', '6'), 'R17': ('U7', '3'), 'R18': ('U7', '6'),
       'R19': ('U6', '8'), 'R20': ('J_BP', '8'), 'R22': ('R21', '1'), 'R23': ('U6', '5'), 'R24': ('U4', '3'),
       'C17': ('J5', '1')}   # 2.10: 100 nF on 5VA at the J5 tail
# review 2.10 (F2, return-path check of verify_pcb.py): a decoupling / filter capacitor also needs its GND pad at the GND pin of its part.
# With the supply pad alone nearest, C9 / C4 / C10 / C12 had their GND pads on the far side and returns of 40-63 mm through GND copper.
# These capacitors take the free position with the smallest (supply pad -> pin) + (GND pad -> GND pin), supply side <= SUP_MAX.
GND_PIN = {'C6': ('U1', '2'), 'C1': ('U2', '4'), 'C2': ('U3', '3'), 'C5': ('U10', '1'), 'C16': ('U3', '4'), 'C7': ('U2', '4'), 'C8': ('U3', '4'),
           'C15': ('U10', '1'), 'C4': ('U4', '1'), 'C9': ('U4', '1'), 'C10': ('U5', '7'), 'C11': ('U6', '7'), 'C12': ('U7', '7'), 'C13': ('U8', '3'),
           'C14': ('U9', '3'), 'C17': ('J5', '3')}
SUP_MAX = {'C5': 4.5}   # MCP1525 load capacitor <= 5 mm (verify_pcb.py); others <= 5.5 (check: 6)


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
    if c == 'C8':
        tries = [('B', 8), ('F', 8)]   # under U3 on the bottom as before (no room on top between the DIP rows)
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
ANCHOR_ORDER = ('U1', 'U2', 'U3', 'U10', 'U4', 'U5', 'U6', 'U7', 'U8', 'U9', 'J_BP', 'R6', 'C', 'R', 'D')


def anchor(ref, nets=None):
    """First placed pad (in ANCHOR_ORDER) sharing a net with `ref` (GND and service-pin nets ignored): (anchor ref, pad, own pad)."""
    own = {k: n for k, n in parts[ref]['pins'].items() if n not in ('GND', 'NC') and not n.startswith('SRV_') and (nets is None or n in nets)}
    for pref in ANCHOR_ORDER:
        for r in sorted(L, key=lambda q: (len(q), q)):
            if not r.startswith(pref) or r == ref or r.startswith('J_SV') or r in ('RSH1', 'R1', 'R2'):
                continue
            for n, net in parts[r]['pins'].items():
                k = next((k for k, m in own.items() if m == net), None)
                if k is not None and n in geo(r)[0]:
                    return r, n, k
    return None


rest = [r for r in parts if parts[r].get('on_board', True) and r not in L and r not in SERVICE]
print('unplaced', rest) if rest else None
# review 2.10 (F3): R30 (SRV_5VA_P06) sat at the INA240 supply (C6, the first 5VA pad in ANCHOR_ORDER) and its 131 mm track crossed
# the analog block; any 5VA pad serves the DC check, U9.2 (C14 / R13) is 40 mm above J_SV2.3
SERVICE_ANCHOR = {'R30': ('U9', '2')}
for r in SERVICE:   # node side (pin 1) next to a pad of the node; bottom first (S1-2), top if no room
    a = SERVICE_ANCHOR.get(r) or anchor(r, {parts[r]['pins']['1']})
    assert a, ('no node', r)
    try:
        place_near(r, (a[0], a[1]), own='1', radius=12, side='B')
    except SystemExit:
        place_near(r, (a[0], a[1]), own='1', radius=16)
missing = [r for r in parts if parts[r].get('on_board', True) and r not in L]
assert not missing, missing
for a, c in [(r, o) for r in list(BOX) for o in list(BOX) if r < o and SIDE[r] == SIDE[o]]:
    ba, bc = BOX[a], BOX[c]
    if ba[0] < bc[2] and bc[0] < ba[2] and ba[1] < bc[3] and bc[1] < ba[3]:
        print('OVERLAP', a, c, [round(v, 1) for v in ba], [round(v, 1) for v in bc])
(P / 'src/placement.json').write_text(json.dumps(L, indent=1) + '\n')
if os.environ.get('P06_BOXES'):   # development preview only (courtyard boxes and pads)
    Path(os.environ['P06_BOXES']).write_text(json.dumps({'boxes': BOX, 'side': SIDE, 'pads': {r: {n: pad(r, n) for n in geo(r)[0]} for r in L},
                                                         'reserved': RESERVED, 'holes': HOLES}))
far = {r: d for r, d in REPORT.items() if d > 6}
print(len(L), 'placed; search distance > 6 mm:', far, 'failed:', FAILED)
