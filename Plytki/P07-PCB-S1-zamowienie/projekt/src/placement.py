"""P07 S1 placement (format S1, class 2/3, slots S2-S3 of level 5). Writes src/placement.json: ref -> [x, y, rotation(, 'B')];
origin = footprint origin (pin 1 for THT library parts and the tails, centre for SMD). Board x 0..106.5 (x = 106.5: side of the inputs, stack x 160;
wire tails J1 / J2 / J4 there and J3 at edge B next to them, user decisions 6.10 evening / 7.10), y 0..100 (0 = edge A, P12; 100 = edge B, service). Run with KiCad Python. Machinery (geo, place_near,
place_dec, bottom side, edge-A strips, reserved areas) from P06 R2 / P05 R3 placement.py.

Fixed by S1 and the README layout requirements: J_BP1 / J_BP2 (IDC 2x8, centres x 26.5 / 80.0, mating face at y = 0, pin 1 at the
smaller x), J_SV1 / J_SV2 (1x13, x 10..43 / 63.5..96.5, pin 1 at the larger x), 8 M3 holes (x 4 / 49 / 57.5 / 102.5, y 14 / 86, D7 zones),
J5 (angled IDC 2x4 box header, decision 5.10 (3)) at the edge x = 106.5 towards the off-stack module, bottom side only SMD <= 1.5 mm (no SOIC).
Blocks: left column = tails; KPWR K1 with the VMOTOR / MOD_BP / PGND pours right of J1 / J2 (top), shunt RSH1 with the MOD_MP / T_EGR_P3 /
T_EGR_P1 pours right of J3 / J4 (bottom); INA240 and the ITEST / OC chain in the bottom middle towards the analog pins of J_SV1; local
supplies and supervisors in the middle; logic under J_BP2; the module buffer U16 at J5; the IS dividers (6.10, no Schmitt) next to J_BP1.
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
STRIPS_A = [(x0, S1['krawedz_A']['strefa_y'][0], x1, S1['krawedz_A']['strefa_y'][1]) for x0, x1 in ((10.0, 43.0), (63.5, 96.5))]   # S1 section 5: along J_BP1 / J_BP2
GEO = {}
MARG = 1.4   # courtyard gap kept by place_near / place_dec (routing room; .6 as the fallback)


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
    for z in STRIPS_A:   # the edge-A strips hold only J_BP1 / J_BP2 (put() directly)
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
    if side == 'B':   # P07 S1 (6.10): no bottom part under a top IC / connector (a via to its pad would land in the IC pad: planner gaps)
        for r, o in BOX.items():
            if SIDE[r] == 'F' and r.startswith(('U', 'J', 'K', 'Q', 'D')) and b[0] < o[2] and o[0] < b[2] and b[1] < o[3] and o[1] < b[3]:
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
        PENDING[ref] = [(*tf(g[0], g[1], x, y, r, side), g[3]) for g in geo(ref)[0].values() if g[2] > 0]
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
                if ds > SUP_MAX.get(ref, 5.5) or (best and ds + dg >= best[0]):
                    continue
                if free(box(ref, (x, y, r), side), MARG, own=ref, side=side):
                    best = (ds + dg, x, y, r, ds)
    if not best:
        raise SystemExit(f'no place for {ref} near {target} ({side})')
    put(ref, best[1], best[2], best[3], side); REPORT[ref] = round(best[4], 2)




# ================= P07 S1 =================
# ---- fixed by S1: edge A (J_BP1 S2 x 26.5, J_BP2 S3 x 80.0, mating face at y = 0, pin 1 at the smaller x), edge B (J_SV1 x 10..43,
# J_SV2 x 63.5..96.5, pin 1 at the larger x, pins ~6 mm beyond the edge) ----
put('J_BP1', 26.5 - 3.5 * 2.54, 13.33, 90)
put('J_BP2', 80.0 - 3.5 * 2.54, 13.33, 90)
put('J_SV2', 26.5 + 15.24, 95.96, 270)   # 7.10: slot S2 (x 13.8..41.7; S1 allows 10..43 of either slot): the bottom right holds J3
# ---- user decisions 6.10 evening / 7.10 (stack review MAJOR-1): ALL wire tails on the side of the inputs (stack x 160), no cable over
# P08. Right column (pad row x = TXR, anchors 12 mm towards the edge, x 96.8): J1 (pad 2 PGND 20.80, pad 1 VMOTOR 28.42), J2 (pad 1
# MOD_BP 39.92, pad 2 PGND 47.54), J5 (module harness), J4 TEST (pad 1 T_EGR_P1 78.43, pad 2 T_EGR_P3 86.05). The column holds four
# tails / headers only, so J3 (module M+ / M-) stands at edge B next to it (anchors towards y = 100, wires out at the back): pad 2
# T_EGR_P3 (75.5, 85.0) next to J4.2, pad 1 MOD_MP (67.88, 85.0) under the shunt. Motor loop in the bottom right corner:
# J3.1 -> RSH1 (above J3.1) -> T_EGR_P1 band -> J4.1, and J3.2 -> J4.2 below it; nothing crosses the board (7.10: the lanes of 6.10
# evening walled off J_SV2 and U1, 79 open connections after the router).
TXR = W - 21.7
put('J1', TXR, 20.8, 270)      # courtyard y 15.30..33.92
put('J2', TXR, 39.92, 270)     # courtyard y 34.42..53.04
put('J5', W - 13.33, 59.14, 0) # angled IDC 2x4 at the edge, courtyard y 53.54..72.36 (body 0.45 mm past the edge as before)
put('J4', TXR, 78.43, 270)     # courtyard y 72.90..91.57, anchors (96.8, 74.93 / 89.55)
put('J3', 75.5, 85.0, 180)     # courtyard x 62.36..81.03, y 82.23..99.03, anchors (79.0 / 64.38, 97.0): 1.4 mm from edge B
# ---- KPWR K1 (G2RL-1-E) lying (90): coil A1 (5V_SYS) 54 / 40.5, A2 (KPWR_COIL_LOW) 54 / 33 on the left (GND domain, away from the
# power pours), contacts in columns x 69 (NC), 74 (COM, VMOTOR), 79 (NO, MOD_BP), rows y 33 / 40.5; NO next to J2.1, the VMOTOR band
# from J1.1 runs above the contact rows (y 25.4..31.4) and down the COM column ----
put('K1', 54.0, 40.5, 90)
# ---- VMOTOR / PGND parts below the relay on the boundary y 48.9 between the VMOTOR foot (y <= 48.6, from the COM column to the left) and
# the PGND strip (y >= 49.2) that runs to J2.2; the area under the left half of J_BP2 (x 52..72, y 15..30) stays free for the logic ----
put('D1', 73.0, 48.9, 270)     # SMCJ18A: cathode (VMOTOR) y 45.5, anode (PGND) y 52.3 (7.10: +0.5, courtyard clear of C1)
put('C1', 65.0, 46.9, 270)     # 220 uF: + (VMOTOR) y 46.9, - (PGND) y 50.4
# ---- shunt (turned 90, the 2-layer block turned by 180): MOD_MP force pad down onto J3.1, T_EGR_P1 force pad up into the band to J4.1,
# sense pads on the diagonal (K_PLUS bottom right, K_MINUS top left); Kelvin pair to the left into R6 / R7 (pad 1 at the shunt) and U1 ----
SX, SY = 67.9, 76.0
put('RSH1', SX, SY, 90)
KP_Y, KM_Y = SY, pad('RSH1', '3')[1]
RX = SX - 6.45
put('R6', RX, KP_Y, 180); put('R7', RX, KM_Y, 180)   # pad 1 K_PLUS / K_MINUS towards the shunt (right), pad 2 INA_PLUS / INA_MINUS
put('U1', RX - 6.85, (KP_Y + KM_Y) / 2, 270)          # IN- (1) top right, IN+ (8) bottom right
# ---- ADC chain (ITEST over SPI to P03) under J_BP1 (top left), analog in the middle left / bottom left, logic under J_BP2 left half
# and in the middle under the relay ----
put('U7', 19.0, 28.0, 0)       # 74LVC125 SPI buffer (3V3A): CS / SCLK in from J_BP1, DOUT out; SUP5 level shift
put('U6', 5.5, 31.0, 0)        # MCP3201 DIP8: 1 VREF, 2 IN+, 3 IN-, 4 VSS left; 8 VDD, 7 CLK, 6 DOUT, 5 CS right
put('U3', 23.0, 42.0, 0)       # MCP6022: A = ADC driver (I_DIV -> ADC_BUF), B = REF_BUF follower
put('U2', 7.0, 46.5, 0)        # MCP1525 TO-92: 1 GND, 2 REF25, 3 VIN
put('U5', 38.0, 72.0, 0)       # TLV1702 window comparator (5VA): I_FILT vs OC_HIGH / OC_LOW (towards U1)
put('U4', 24.0, 72.0, 0)       # MCP6022: OC_HIGH = REF_BUF x 1.806 (5VA)
put('U18', 33.0, 55.0, 0)      # MCP1702 TO-92: 1 GND, 2 VIN (5VA), 3 VOUT (3V3A)
put('U9', 9.0, 19.5, 0)        # MCP120-450 (5VA); 7.10: next to U7 (SUP5_RAW -> U7.12; at (8, 72) it was 47 mm away)
put('U8', 20.0, 58.0, 0)       # MCP120-300 (3V3A) (7.10: next to U9 at (9, 24) it crowded the IS dividers at J_BP1)
put('U10', 48.0, 63.6, 180)   # 180: outputs 1Y / 2Y face U13 / U14      # LVC125 receivers: MOTOR_INA / INB (J_BP1) -> INA_P07 / INB_P07 at U13 / U14; 7.10: next to them (INA_P07 from (34, 28) stayed open in most router attempts)
put('U11', 45.0, 24.5, 0)      # LVC14 (MOTOR_PERMIT, SAFE_N from J_BP2: under the gap between J_BP1 and J_BP2)
put('U15', 55.5, 24.5, 0)      # 7.10: U15 next to U11 (PERMIT_N), U12 right of it; HC74 latch (ARM_CLK, OC_LOCAL_N) under the left half of J_BP2 (7.10: a logic column at x 44 jammed the channel left of the relay)
put('U12', 66.0, 23.0, 0)      # HC08 RAILS_OK / LOCAL_CLEAR_N / PERMIT_ARMED / LOCAL_PERMIT (left of the relay block)
put('U13', 58.0, 63.6, 0)      # 7.10: bottom row 1.6 mm lower (corridor under the relay foot 5.1 mm); HC08 DRIVE_EN / DRIVE_OK / PWM_EN / RPWM (7.10: in the top band next to U15 the band jammed, 15 gaps)
put('U14', 68.0, 63.6, 0)      # HC08 LPWM (gates 2-4 unused)
put('U16', 81.0, 63.6, 0)      # AHCT125 3.3 -> 5 V with OE (5V_MOD) next to J5
# ---- reserved areas (no parts on that side): power pours (both layers), cables of the tails (top), Kelvin corridor ----
MOTOR = [(61.8, 68.3, 87.8, 92.6)]    # 7.10: the whole motor block (MOD_MP, T_EGR_P1 band and drop, T_EGR_P3); a part between its
                                      # pours (R39 in the first 7.10 run) has no way out
RESERVED = [(s, z) for s in ('F', 'B') for z in [(72.0, 24.8, 95.5, 43.4), (82.0, 15.3, 95.5, 24.8), (56.3, 43.4, 95.5, 53.9),   # relay block pours
                                                  *MOTOR, (RX - 2.5, KM_Y - 1.2, SX - 1.9, KP_Y + 1.2)]]                    # motor block, Kelvin corridor
RESERVED += [('F', (TXR + 2.25, 15.3, W, 53.04)), ('F', (TXR + 2.25, 72.9, W, 91.57)), ('F', (62.36, 87.25, 81.03, H))]   # cables of the tails
# ---- power block passives at fixed spots (both pours under them belong to their nets; bottom side >= 1 mm from THT pads, checked below) ----
put('R4', 76.6, 46.6, 0, 'B')       # 1 k 2512 below the relay across the COM (VMOTOR, x <= 76.1) / NO tongue (MOD_BP, x >= 76.7) boundary
put('R5', 78.0, 49.2, 270)          # top: MOD_BP tongue (y <= 48.6) / PGND (y >= 49.2)
put('C4', 80.7, 49.2, 270)
put('C2', 61.0, 48.9, 90, 'B')      # VMOTOR foot / PGND boundary y 48.9 (pad 1 VMOTOR up)
put('C3', 68.6, 48.9, 90, 'B')
put('R1', 57.9, 48.9, 90, 'B')
# passives at the pin they serve: (anchor ref, anchor pad); the part's pad on the same net goes next to it. Order = priority.
DEC = {'C5': ('U2', '2'), 'C37': ('U2', '3'), 'C22': ('U1', '6'), 'C23': ('U3', '8'), 'C26': ('U6', '8'), 'C6': ('U6', '1'),
       'C24': ('U4', '8'), 'C25': ('U5', '8'), 'C27': ('U7', '14'), 'C7': ('U3', '3'), 'C11': ('U6', '2'),
       'Q1': ('K1', 'A2'), 'D2': ('K1', 'A2'), 'C9': ('K1', 'A1'), 'D3': ('K1', 'A1'), 'R2': ('Q1', '1'), 'R3': ('Q1', '1'),
       'C22': ('U1', '6'), 'R10': ('U1', '5'), 'R8': ('U3', '3'), 'R9': ('U3', '3'), 'C7': ('U3', '3'), 'C8': ('U5', '3'),
       'R16': ('U6', '2'), 'C11': ('U6', '2'), 'C5': ('U2', '2'), 'C6': ('U6', '1'), 'D4': ('U2', '2'),
       'C23': ('U3', '8'), 'C24': ('U4', '8'), 'C25': ('U5', '8'), 'C26': ('U6', '8'), 'C27': ('U7', '14'), 'C28': ('U8', '2'), 'C29': ('U9', '2'),
       'R11': ('U4', '2'), 'R12': ('U4', '2'), 'R13': ('U5', '2'), 'R14': ('U5', '2'), 'C10': ('U5', '2'), 'R15': ('U5', '1'),
       'R17': ('U7', '2'), 'R18': ('U7', '3'), 'R19': ('U7', '6'), 'R20': ('U7', '5'), 'R21': ('U6', '6'), 'R22': ('U7', '8'), 'R23': ('U7', '11'),
       'R24': ('U8', '1'), 'R25': ('U9', '1'), 'C18': ('U18', '2'), 'C19': ('U18', '3'), 'D7': ('U18', '3'), 'R50': ('U18', '2'),
       'C16': ('R50', '2'), 'C17': ('U1', '6'),
              'C30': ('U10', '14'), 'C31': ('U11', '14'), 'C32': ('U12', '14'), 'C33': ('U13', '14'), 'C34': ('U14', '14'), 'C35': ('U15', '14'),
       'C36': ('U16', '14'),
       'R26': ('U10', '2'), 'R27': ('U10', '5'), 'R28': ('U10', '9'), 'R29': ('U13', '9'), 'R30': ('U15', '3'),
       'R31': ('U11', '5'), 'R51': ('U11', '5'), 'Q2': ('R31', '1'), 'R33': ('Q2', '1'), 'R34': ('Q2', '1'), 'R32': ('U13', '6'),
       'F1': ('U16', '14'), 'C12': ('U16', '14'), 'C13': ('J5', '7'), 'R35': ('U16', '1'), 'R36': ('U13', '11'), 'R37': ('U14', '3'), 'R38': ('U13', '3'),
       'R39': ('U16', '3'), 'R40': ('U16', '6'), 'R41': ('U16', '8'), 'R42': ('U16', '11'), 'R43': ('J5', '8'),
       'R44': (38.0, 19.5), 'R45': ('R44', '2'), 'C14': ('R44', '2'), 'D5': ('R44', '2'), 'R46': (38.0, 25.5), 'R47': ('R46', '2'), 'C15': ('R46', '2'),
       'D6': ('R46', '2'), 'C20': ('J_BP2', '14'), 'C21': ('J_BP2', '14')}
GND_PIN = {c: (u, g) for c, (u, v, g) in __import__('board').DEC_CAPS.items()}
GND_PIN.update({'C5': ('U2', '1'), 'C6': ('U6', '4'), 'C9': ('Q1', '2'), 'C17': ('U1', '2'), 'C18': ('U18', '1'),
                'C19': ('U18', '1'), 'C7': ('U3', '4'), 'C11': ('U6', '4'), 'C12': ('U16', '7'), 'C13': ('J5', '8')})
SUP_MAX = {'C5': 4.5}   # MCP1525 load capacitor <= 5 mm (verify_pcb.py); others <= 5.5


def dump_boxes():
    if os.environ.get('P07_BOXES'):   # development preview only (courtyard boxes and pads)
        Path(os.environ['P07_BOXES']).write_text(json.dumps({'boxes': BOX, 'side': SIDE, 'pads': {r: {n: pad(r, n) for n in geo(r)[0]} for r in L},
                                                             'reserved': RESERVED, 'holes': HOLES}))


dump_boxes()
FAILED = []
for c, t in DEC.items():
    if any(isinstance(g[0], str) and g[0] not in L for g in [t] + ([GND_PIN[c]] if c in GND_PIN else [])):
        FAILED.append(c); print('anchor not placed for', c); continue
    tries = [('F', 8), ('F', 16), ('B', 8), ('B', 16), ('F', 24), ('B', 24)] if not is_tht(c) else [('F', 8), ('F', 16)]   # 7.10: 24 mm last (R42 at U16)
    if c.startswith(('Q', 'D', 'F')) or (parts[c].get('farads', 0) >= 4e-6):   # SOT-23 / SOD-123 / PTC / 4.7-10 uF (1.6 mm) on top only
        tries = [('F', 8), ('F', 16), ('F', 24)]   # 7.10: 24 mm last (D6 after U8 moved)
    for MARG, side, rad in [(mg, s_, r_) for mg in (1.4, .6) for s_, r_ in tries]:   # routing room round the part first, then tight
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
SERVICE = sorted((r for r, v in parts.items() if v['source_ref'].startswith('ADDED_SERVICE') and r not in L), key=lambda r: int(r[1:]))
ANCHOR_ORDER = ('U1', 'U2', 'U3', 'U4', 'U5', 'U6', 'U7', 'U8', 'U9', 'U18', 'U10', 'U11', 'U12', 'U13', 'U14', 'U15', 'U16', 'Q', 'J_BP', 'C', 'R', 'D', 'F')


def anchor(ref, nets=None):
    """First placed pad (in ANCHOR_ORDER) sharing a net with `ref` (GND and service-pin nets ignored): (anchor ref, pad, own pad)."""
    own = {k: n for k, n in parts[ref]['pins'].items() if n not in ('GND', 'NC') and not n.startswith('SRV_') and (nets is None or n in nets)}
    for pref in ANCHOR_ORDER:
        for r in sorted(L, key=lambda q: (len(q), q)):
            if not r.startswith(pref) or r == ref or r.startswith('J_SV') or r in ('RSH1', 'R6', 'R7'):
                continue
            for n, net in parts[r]['pins'].items():
                k = next((k for k, m in own.items() if m == net), None)
                if k is not None and n in geo(r)[0]:
                    return r, n, k
    return None


rest = [r for r in parts if parts[r].get('on_board', True) and r not in L and r not in SERVICE]
print('unplaced', rest) if rest else None
SERVICE_ANCHOR = {'R60': ('U1', '5'), 'R52': ('K1', 'A1'), 'R59': ('R32', '2')}
def nearest_node_pad(r):
    """7.10: the pad of the node (pin 1 net of the service resistor) nearest to its J_SV2 pin (pin 2 net), among placed parts; a node
    reached at several parts (SAFE_OK at U11 and U13, OC_GOOD at U12 / U13 / U15) gets its resistor on the side of the strip, so the
    service line does not cross the board (first 7.10 runs: SRV_SAFE_OK / SRV_OC_GOOD / SRV_KPWR_COIL_LOW open from the top logic)."""
    node, srv = parts[r]['pins']['1'], parts[r]['pins']['2']
    sv = [pad(h, n) for h in L if h.startswith('J_SV') for n, m in parts[h]['pins'].items() if m == srv]
    cand = [(h, n) for h in L if not h.startswith('J_SV') and h not in ('RSH1', 'R6', 'R7') for n, m in parts[h]['pins'].items()
            if m == node and n in geo(h)[0] and h[0] in 'UQK']
    if not sv or not cand:
        return None
    return min(cand, key=lambda hn: math.dist(pad(*hn), sv[0]))


for r in SERVICE:   # node side (pin 1) next to a pad of the node; bottom first (S1-2), top if no room
    a = SERVICE_ANCHOR.get(r) or anchor(r, {parts[r]['pins']['1']})   # 7.10: nearest_node_pad() tried (run 8/9: worse, 11 / 17 / 29 gaps), not used
    assert a, ('no node', r)
    for MARG, side, rad in [(mg, s_, r_) for mg in (1.4, .6) for s_, r_ in (('F', 9), ('B', 9), ('F', 14), ('B', 14))]:   # node side (pin 1) <= 10 mm from the node
        try:
            place_near(r, (a[0], a[1]), own='1', radius=rad, side=side); break
        except SystemExit as e:
            last = e
    else:
        raise last
missing = [r for r in parts if parts[r].get('on_board', True) and r not in L]
dump_boxes()
assert not missing, missing
for r_, n_ in (('R4', '1'), ('R5', '1'), ('C4', '1'), ('C2', '1'), ('C3', '1'), ('R1', '1')):
    print('pad', r_, n_, [round(v, 2) for v in pad(r_, n_)])
for a, c in [(r, o) for r in list(BOX) for o in list(BOX) if r < o and SIDE[r] == SIDE[o]]:
    ba, bc = BOX[a], BOX[c]
    if ba[0] < bc[2] and bc[0] < ba[2] and ba[1] < bc[3] and bc[1] < ba[3]:
        print('OVERLAP', a, c, [round(v, 1) for v in ba], [round(v, 1) for v in bc])
(P / 'src/placement.json').write_text(json.dumps(L, indent=1) + '\n')
dump_boxes()
far = {r: d for r, d in REPORT.items() if d > 6}
print(len(L), 'placed; search distance > 6 mm:', far, 'failed:', FAILED)
