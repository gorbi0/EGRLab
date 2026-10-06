"""P07 S1 placement (format S1, class 2/3, slots S2-S3 of level 5). Writes src/placement.json: ref -> [x, y, rotation(, 'B')];
origin = footprint origin (pin 1 for THT library parts and the tails, centre for SMD). Board x 0..106.5 (x = 0: panel side, the four wire
tails J1-J4, decision 5.10 (6)), y 0..100 (0 = edge A, P12; 100 = edge B, service). Run with KiCad Python. Machinery (geo, place_near,
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
put('J_SV2', 80.0 + 15.24, 95.96, 270)
# ---- panel side x = 0 (decision 5.10 (6)): the four tails in one column, pad row x = TX, anchors 12 mm towards the wall (x 9.7: the anchor
# holes keep 5.1 mm from the M3 centres at x 4, so the column may run past y 14 / 86); courtyards 18.62 mm, 0.5 mm apart.
# Order top-down: J2.2 PGND, J2.1 MOD_BP | J1.1 VMOTOR, J1.2 PGND | J3.1 MOD_MP, J3.2 T_EGR_P3 | J4.2 T_EGR_P3, J4.1 T_EGR_P1
# (J1 / J3 numbered from the far end): MOD_BP and VMOTOR face the KPWR contacts, PGND joins round them along a strip between the
# anchors and the pads, T_EGR_P3 is one block between J3 and J4, the shunt loop MOD_MP -> RSH1 -> T_EGR_P1 runs right of it.
TX = 21.7
put('J2', TX, 28.42, 90)       # pad 2 (PGND) y 20.80, pad 1 (MOD_BP) y 28.42; courtyard y 15.30..33.92
put('J1', TX, 47.54, 90)       # rev: pad 1 (VMOTOR) y 39.92, pad 2 (PGND) y 47.54; courtyard 34.42..53.04
put('J3', TX, 66.66, 90)       # rev: pad 1 (MOD_MP) y 59.04, pad 2 (T_EGR_P3) y 66.66; courtyard 53.54..72.16
put('J4', TX, 85.78, 90)       # pad 2 (T_EGR_P3) y 78.16, pad 1 (T_EGR_P1) y 85.78; courtyard 72.66..91.28
# ---- KPWR K1 (G2RL-1-E, turned 180): contact pins in two columns x 27.8 / 35.3; NO (MOD_BP) y 29.5 level with J2.1, COM (VMOTOR) y 34.5
# above J1.1, NC y 39.5 (unused, inside the VMOTOR pour), coil A1 (5V_SYS) x 35.3 / A2 (KPWR_COIL_LOW) x 27.8 at y 54.5 ----
put('K1', 35.3, 54.5, 180)
# ---- VMOTOR / PGND parts right of K1 on the VMOTOR (y <= 43.0) / PGND (y >= 43.6) boundary ----
put('D1', 42.3, 43.3, 270)     # SMCJ18A: cathode (VMOTOR) y 39.9, anode (PGND) y 46.7
put('C1', 50.6, 41.2, 270)     # 220 uF: + (VMOTOR) y 41.2, - (PGND) y 44.7
# ---- shunt, Kelvin pair, INA240 (as P06 R2, RSH1 turned 270: MOD_MP force pad up, T_EGR_P1 force pad down, sense pads on the diagonal) ----
SX, SY = 28.5, (59.04 + 85.78) / 2
put('RSH1', SX, SY, 270)
KP_Y, KM_Y = SY, pad('RSH1', '3')[1]
RX = 36.6
put('R6', RX, KP_Y, 0); put('R7', RX, KM_Y, 0)   # pad 1 K_PLUS / K_MINUS towards the shunt, pad 2 INA_PLUS / INA_MINUS
put('U1', RX + 7.6, (KP_Y + KM_Y) / 2, 90)       # IN+ (8) top left, IN- (1) bottom left
# ---- ADC chain (ITEST over SPI to P03) next to J_BP1 (top middle): SPI to J_BP1 short, I_T_OUT / REF_BUF run down to U1 ----
put('U7', 44.5, 25.0, 0)       # 74LVC125 SPI buffer (3V3A): CS / SCLK in from J_BP1, DOUT out; SUP5 level shift
put('U6', 57.5, 33.5, 0)       # MCP3201 DIP8: 1 VREF, 2 IN+, 3 IN-, 4 VSS left; 8 VDD, 7 CLK, 6 DOUT, 5 CS right
put('U3', 61.0, 47.0, 0)       # MCP6022: A = ADC driver (I_DIV -> ADC_BUF), B = REF_BUF follower (right of the VMOTOR pour)
put('U2', 57.0, 53.0, 0)       # MCP1525 TO-92: 1 GND, 2 REF25, 3 VIN
# ---- OC window and local supplies (bottom middle, right of U1) ----
put('U5', 52.0, 61.0, 0)       # TLV1702 window comparator (5VA): I_FILT vs OC_HIGH / OC_LOW
put('U4', 62.0, 61.0, 0)       # MCP6022: OC_HIGH = REF_BUF x 1.806 (5VA)
put('U18', 51.0, 69.0, 0)      # MCP1702 TO-92: 1 GND, 2 VIN (5VA), 3 VOUT (3V3A)
put('U9', 60.0, 70.0, 0)       # MCP120-450 (5VA)
put('U8', 60.0, 77.0, 0)       # MCP120-300 (3V3A)
# ---- logic (3V3_IO) under J_BP2 and towards J5 ----
put('U10', 72.0, 27.0, 0)      # LVC125 receivers: MOTOR_INA / INB (J_BP1), MOTOR_PERMIT / PWM_OUT (J_BP2)
put('U11', 83.5, 27.0, 0)      # LVC14
put('U15', 95.0, 27.0, 0)      # HC74 latch
put('U12', 72.0, 44.0, 0)      # HC08 RAILS_OK / LOCAL_CLEAR_N / PERMIT_ARMED / LOCAL_PERMIT
put('U13', 83.5, 44.0, 0)      # HC08 DRIVE_EN / DRIVE_OK / PWM_EN / RPWM
put('U16', 82.0, 60.0, 0)      # AHCT125 3.3 -> 5 V with OE (5V_MOD) next to J5
put('U14', 74.0, 76.0, 0)      # HC08 LPWM (gates 2-4 unused)
# ---- J5 (module harness, angled box header) at the edge x = 106.5, between the M3 zones: odd row x 93.17, front at the edge ----
put('J5', 106.5 - 13.33, 54.0, 0)
# ---- reserved areas (no parts on that side): power pours (both layers), cables of the tails (top), Kelvin corridor ----
RESERVED = [(s, z) for s in ('F', 'B') for z in [(12.7, 15.3, 37.2, 50.8), (36.6, 33.0, 55.6, 50.8),   # VMOTOR / MOD_BP / PGND (top block)
                                                  (12.7, 55.6, 33.6, 91.0),                         # MOD_MP / T_EGR_P3 / T_EGR_P1
                                                  (SX - 2.0, SY - 0.6, RX - 2.4, KM_Y + 0.9)]]      # Kelvin corridor
RESERVED += [('F', (0.0, 15.3, TX - 2.25, 91.3))]                                                   # cables of the tails
# ---- power block passives at fixed spots (both pours under them belong to their nets; bottom side >= 1 mm from THT pads) ----
put('R4', 31.55, 32.8, 270, 'B')    # 1 k 2512 between the K1 pin columns: VMOTOR pad y 35.85 (COM side), MOD_BP pad y 29.75 (NO side)
put('R5', 27.0, 24.0, 270, 'B')     # MOD_BP / PGND boundary y 24.0 (PGND above)
put('C4', 31.6, 24.0, 270, 'B')
put('C2', 39.5, 43.3, 90, 'B')     # VMOTOR / PGND boundary y 43.3 under D1 / C1
put('C3', 53.3, 43.3, 90, 'B')
put('R1', 46.0, 43.3, 90, 'B')
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
       'R26': ('U10', '2'), 'R27': ('U10', '5'), 'R28': ('U10', '9'), 'R29': ('U10', '12'), 'R30': ('U15', '3'),
       'R31': ('U11', '5'), 'R51': ('U11', '5'), 'Q2': ('R31', '1'), 'R33': ('Q2', '1'), 'R34': ('Q2', '1'), 'R32': ('U13', '6'),
       'F1': ('U16', '14'), 'C12': ('U16', '14'), 'C13': ('J5', '7'), 'R35': ('U16', '1'), 'R36': ('U13', '11'), 'R37': ('U14', '3'), 'R38': ('U13', '3'),
       'R39': ('U16', '3'), 'R40': ('U16', '6'), 'R41': ('U16', '8'), 'R42': ('U16', '11'), 'R43': ('J5', '8'),
       'R44': (53.0, 19.0), 'R45': ('R44', '2'), 'C14': ('R44', '2'), 'D5': ('R44', '2'), 'R46': (53.0, 27.0), 'R47': ('R46', '2'), 'C15': ('R46', '2'),
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
    tries = [('F', 8), ('F', 16), ('B', 8), ('B', 16)] if not is_tht(c) else [('F', 8), ('F', 16)]
    if c.startswith(('Q', 'D', 'F')) or (parts[c].get('farads', 0) >= 4e-6):   # SOT-23 / SOD-123 / PTC / 4.7-10 uF (1.6 mm) on top only
        tries = [('F', 8), ('F', 16)]
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
SERVICE_ANCHOR = {'R60': ('Q1', '3')}
for r in SERVICE:   # node side (pin 1) next to a pad of the node; bottom first (S1-2), top if no room
    a = SERVICE_ANCHOR.get(r) or anchor(r, {parts[r]['pins']['1']})
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
