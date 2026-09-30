"""P03 R6 placement (format S1, class L, level 2). Writes src/placement.json: ref -> [x, y, rotation(, 'B')]; origin = footprint
origin (pin 1 for THT library parts and the modules, centre for SMD). Board x 0..160 (0 = panel side), y 0..100 (0 = edge A, P12;
100 = edge B, service side). Run with KiCad Python (footprint geometry is read from eda/libraries).

Fixed by S1 (SPECYFIKACJA-FORMATU-S1.md §4-§6) and the README layout requirements:
- J_BP1/2/3: IDC 2x10 right angle, mating face at y = 0, pin 1 at the smaller x, pin centre x = 26.5 / 80.0 / 133.5;
- J_SV1/2/3: 1x13 right angle, pins in x 10..43 of the slot, plastic body front at y = 100, pins ~6 mm beyond edge B;
- 12 M3 holes (x 4 / 49 in each slot, y 14 / 86) with the D7 standoff zones.
Modules (decision 30.09, marked in the README as disputed): M1 USB-C towards edge B and antenna towards edge A, SD1 card towards
edge B. Both modules are 26 mm wide and the gaps between the service headers are 19.4 mm (courtyards), so neither can stand
at the edge; they stop at the J_SV courtyards (y 94.17): USB-C face and card tip about 6 mm inside edge B, reachable with the
service wall removed (the plug passes over the 3 mm high service headers, below the level above).
Blocks: S1 = panel inputs (U13, U14), MCP23017 U1, decoder U2; column S1/S2 = DAQ buffers U21, U22 (near J_BP2), input
buffer U11, reset U3/U4; S2 = M1 with the antenna keepout under J_BP2; column S2/S3 = supply U5/Q1 (next to J_BP2.17-20),
U12 (SAFE inputs next to M1 J3); S3 = U23 (SPI3 near J_BP3), U6/R41/C15 at J_BP3.12, SD1.
Passives are placed by a search (place_near): nearest free spot (courtyards + 0.5 mm, holes, keepouts, board) to the pin
they belong to (decoupling: IC supply pin; pull-ups/downs: buffer input; series/termination: driver output; service
resistors: a pad of their node).
"""
import pcbnew as p, json, math
from pathlib import Path
P = Path(__file__).resolve().parents[1]
S1 = json.loads((P.parents[0] / 'Format-S1/format-s1.json').read_text(encoding='utf-8'))
parts = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
W, H = S1['klasy']['L']['W'], S1['klasy']['L']['H']
HOLES = [(x + S1['rozstaw_slotow'] * k, y) for k in range(3) for x in S1['otwory_M3']['x_w_slocie'] for y in S1['otwory_M3']['y']]
RZ = S1['otwory_M3']['strefa_dystansu_srednica'] / 2
GEO = {}


def geo(ref):
    """Local pads {num: (x, y)} and courtyard box of the footprint of `ref` (library copy in eda/libraries)."""
    fid = parts[ref]['footprint']
    if fid not in GEO:
        lib, name = fid.split(':'); f = p.FootprintLoad(str(P / 'eda/libraries' / (lib + '.pretty')), name); assert f, fid
        ls = p.LSET(); ls.AddLayer(p.F_CrtYd); r = f.GetLayerBoundingBox(ls)
        GEO[fid] = ({a.GetNumber(): (p.ToMM(a.GetPosition().x), p.ToMM(a.GetPosition().y)) for a in f.Pads() if a.GetNumber()},
                    (p.ToMM(r.GetLeft()), p.ToMM(r.GetTop()), p.ToMM(r.GetRight()), p.ToMM(r.GetBottom())))
    return GEO[fid]


def tf(x, y, cx, cy, rot):
    a = math.radians(rot); c, s = round(math.cos(a)), round(math.sin(a))
    return (cx + x * c + y * s, cy - x * s + y * c)


L = {}; BOX = {}


def put(ref, x, y, r=0):
    L[ref] = [round(x, 3), round(y, 3), r % 360]; BOX[ref] = box(ref)


def pad(ref, num):
    x, y, r = L[ref][:3]; return tf(*geo(ref)[0][str(num)], x, y, r)


def box(ref, at=None):
    x, y, r = at or L[ref][:3]; x0, y0, x1, y1 = geo(ref)[1]
    q = [tf(u, v, x, y, r) for u, v in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]]
    return (min(a for a, _ in q), min(b for _, b in q), max(a for a, _ in q), max(b for _, b in q))


# ---- fixed by S1 ----
for k, ref in enumerate(['J_BP1', 'J_BP2', 'J_BP3']):
    put(ref, S1['rozstaw_slotow'] * k + S1['krawedz_A']['srodek_x_w_slocie'] - 11.43, 13.33, 90)   # face y = 13.33 - 13.33
for k, ref in enumerate(['J_SV1', 'J_SV2', 'J_SV3']):
    put(ref, S1['rozstaw_slotow'] * k + 26.5 + 15.24, 95.96, 270)       # pin 1 at the larger x, body front at y = 100
# ---- modules ----
put('M1', 68.57, 37.3, 0)       # J1 row x 68.57, J3 row x 91.43 (centre 80.0); courtyard y 29.02..94.07 (J_SV2 from 94.17)
put('SD1', 148.5, 70.9, 180)    # header y 70.9 (pin 1 3V at x 148.5); card towards edge B, tip y 93.76; courtyard to 94.04
# ---- ICs ----
# S1 row under J_BP1 (fan-out band y 14.7..21.3): U22 (CS_ILOG/ITEST to J_BP1.2/4; inputs from U1/U2), U14 (TEST_KEY), U13 (J_BP1.15-18).
# U22 moved from the S1/S2 column to S1 (30.09, second router run): its inputs come from U1/U2 and two of its outputs go to J_BP1;
# MEAS_EN and ADC_RESET (static, J_BP2.14/18) take the longer way. README asked for U22 near J_BP2 (disputed, noted there).
# 30.09 evening (Ubuntu): S1 spread downwards into its free lower half (the P02 R4 lesson): SOIC row y 25 -> 28, U1 37 -> 45, U2 55 -> 66;
# the J_BP1 fan-out band and the space between the SOIC row and U1 were the densest part of the board in every router run.
put('U22', 11.0, 28.0, 90); put('U14', 22.0, 28.0, 90); put('U13', 33.5, 28.0, 90)
put('U1', 42.0, 45.0, 270)      # MCP23017: inputs 1-7 face the buffers, 15-28 face down; courtyard x 7.42..43.55
put('U2', 27.0, 66.0, 270)      # HC139 decoder
put('U21', 54.0, 24.0, 90)      # DAQ outputs next to J_BP2 (README, verify <= 30 mm; x 51 gave 30.9), left of the lane along the M1 J1 row
put('U11', 51.0, 62.0, 0)       # inputs to the M1 J1 row (DOUTA, BUSY, MISO, CAN_RX)
put('U12', 104.5, 50.0, 0)      # HW_ARMED / INTERLOCK to M1 J3-8 / J3-6
put('U23', 122.0, 27.0, 90)     # SPI3 to J_BP3.2-10 and SD1
put('LED1', 50.5, 95.5, 0)      # status LED at edge B between J_SV1 and J_SV2 (visible from the service side)
# ---- 5 V path (route_critical.py draws it locked, 1.5 mm): J_BP2.17/19/20 -> C13 -> Q1 D (F.Cu); Q1 S -> B.Cu spine x = SPINE_X
# down the right side of M1 -> y = 93 under the USB end of M1 -> J1-21 (5V of the module) -> C14. The spine channel is kept free of parts.
SPINE_X = 97.4
put('Q1', SPINE_X - .95, 19.3, 90)   # rot 90: D (96.45, 18.36) towards J_BP2, G (95.5, 20.24), S (97.4, 20.24) on the spine line
put('C13', 93.4, 17.3, 270)          # pad 1 (5V_SYS) at (93.4, 15.81) under the J_BP2.19 -> Q1 D diagonal (rot 90 put it at the bottom)
put('U5', 101.0, 21.2, 180)          # LTC4412: SENSE (6) at (99.86, 22.15) next to the spine; VIN, GATE by the router
put('C14', 64.45, 88.1, 180)         # pad 1 (5V_M1) at (66.01, 88.1), 2.56 mm from M1 J1-21

ANT = (68.57 - 1.32 - 3, 37.3 - 8.0 - 8, 68.57 + 24.18 + 3, 37.3 - 1.5)   # as P03 R5: antenna end + 3 mm sides + 8 mm beyond
SDH = [pad_ for pad_ in [tf(0, -17.78, 148.5, 70.9, 180), tf(20.32, -17.78, 148.5, 70.9, 180)]]
MARGIN = .5
CHANNEL = (SPINE_X - 1.6, 22.0, SPINE_X + 1.6, 94.2)   # 5 V spine (1.5 mm) + clearance: no parts
LANE = (56.5, 30.0, 66.4, 86.0)   # vertical lane along the M1 J1 row (SRC / DAQ / service lines): only parts that belong to a J1 pin


def free(b, m=MARGIN, own=None, lane_ok=False):
    if b[0] < .6 or b[1] < .6 or b[2] > W - .6 or b[3] > H - .6:
        return False
    for r, o in BOX.items():
        if r == own:
            continue
        if b[0] - m < o[2] and o[0] < b[2] + m and b[1] - m < o[3] and o[1] < b[3] + m:
            return False
    for (hx, hy), rr in [(h, RZ) for h in HOLES] + [(h, 3.0) for h in SDH]:
        dx = max(b[0] - hx, 0, hx - b[2]); dy = max(b[1] - hy, 0, hy - b[3])
        if math.hypot(dx, dy) < rr + .1:
            return False
    for z in [ANT, CHANNEL] + ([] if lane_ok else [LANE]):
        if b[0] < z[2] and z[0] < b[2] and b[1] < z[3] and z[1] < b[3]:
            return False
    return True


REPORT = {}


def place_near(ref, target, own=None, radius=16.0, rots=(0, 90, 180, 270), m=MARGIN, lane_ok=False):
    """Nearest legal position: pad `own` (default: the pad on the target's net, else '1') as close as possible to the target."""
    if isinstance(target, tuple) and isinstance(target[0], str):
        tref, tpad = target; tx, ty = pad(tref, tpad); tnet = parts[tref]['pins'][str(tpad)]
        own = own or next((k for k, n in parts[ref]['pins'].items() if n == tnet), '1')
    else:
        tx, ty = target; own = own or '1'
    lp = geo(ref)[0][str(own)]; step = .25; n = int(radius / step)
    cand = sorted(((math.hypot(i * step, j * step), k, i, j) for i in range(-n, n + 1) for j in range(-n, n + 1) for k in range(len(rots))
                   if math.hypot(i * step, j * step) <= radius))
    for d, k, i, j in cand:
        r = rots[k]; ox, oy = tf(*lp, 0, 0, r); x, y = tx + i * step - ox, ty + j * step - oy
        if free(box(ref, (x, y, r)), m, own=ref, lane_ok=lane_ok):
            put(ref, x, y, r); REPORT[ref] = round(d, 2); return
    raise SystemExit(f'no place for {ref} near {target}')


# ---- SOT-23 parts ----
place_near('U3', (54.0, 42.0), own='1')            # TPS3808 left of the lane, next to M1 J1-3 (SUP_N) / J1-1 (3V3)
place_near('U4', ('U3', '1'))                      # SUP_RAW_N
place_near('U6', ('J_BP3', '12'), own='4', radius=12)
# ---- decoupling first ----
for c, (u, n) in {'C1': ('U2', 16), 'C2': ('U1', 9), 'C3': ('U3', 6), 'C5': ('U11', 14), 'C6': ('U12', 14), 'C7': ('U13', 14), 'C8': ('U14', 14),
                  'C9': ('U21', 14), 'C10': ('U22', 14), 'C11': ('U23', 14), 'C12': ('U4', 5), 'C15': ('U6', 5)}.items():
    place_near(c, (u, str(n)))
# ---- series and termination at their drivers ----
for r, (u, n) in {'R36': ('U21', 6), 'R37': ('U21', 11), 'R39': ('U21', 8), 'R38': ('U23', 3), 'R40': ('U23', 6), 'R41': ('U6', 4),
                  'R34': ('U4', 4), 'R12': ('J_BP1', 10), 'R43': ('J_BP2', 16), 'R14': ('J_BP3', 13)}.items():
    place_near(r, (u, str(n)))
place_near('R42', ('M1', 'J1-13'), lane_ok=True)    # README: R42 at M1 J1-13 (GPIO3)
# ---- pull-ups / pull-downs at the receiver or source ----
PULL = {'R1': ('U2', 1), 'R2': ('U14', 5), 'R3': ('U12', 2), 'R5': ('U1', 7), 'C4': ('U1', 7), 'R6': ('U13', 9), 'R7': ('U14', 9),
        'R8': ('U13', 12), 'R9': ('U1', 12), 'R10': ('U1', 13), 'R11': ('SD1', 6), 'R13': ('U3', 1), 'R15': ('U21', 2), 'R16': ('U21', 5),
        'R17': ('U21', 9), 'R18': ('U21', 12), 'R19': ('U22', 2), 'R20': ('U22', 5), 'R21': ('U23', 2), 'R22': ('U23', 5), 'R23': ('U23', 9),
        'R24': ('U23', 12), 'R25': ('U2', 2), 'R26': ('U12', 5), 'R27': ('U14', 2), 'R28': ('U13', 2), 'R29': ('U13', 5), 'R30': ('U11', 12),
        'R31': ('U11', 5), 'R32': ('U11', 2), 'R33': ('U11', 9), 'R35': ('R34', 2), 'R4': ('LED1', 2)}
for r, (u, n) in PULL.items():
    place_near(r, (u, str(n)))
# ---- service resistors: node side (pin 1) next to a pad of the node; the node pad is chosen in the slot of the header ----
# 30.09 evening: taps closer to the header / out of the J_BP2 band: 5V_SYS at U5.1 (was C13.1), ADC_BUSY at U11.5 (was J_BP2.12),
# HEARTBEAT at M1 J3-18 (was J_BP3.16); SUP_N at U6.2 (was U1.18) since its pin moved to J_SV3.12 with the gate swap U12 -> U14.
NODE = {'MOTOR_INB': ('U1', 27), 'MOTOR_INA': ('U1', 26), '3V3_CORE': ('C1', 1), 'MEAS_BANK': ('R25', 1), 'SCOPE_TRIG': ('R12', 1),
        'CS_ITEST_N': ('U22', 11), 'CS_ILOG_N': ('U22', 8), '3V3_IO': ('U14', 13), 'SUP_N': ('U6', 2), 'I2C_SDA': ('R10', 2), 'I2C_SCL': ('R9', 2),
        '5V_SYS': ('U5', 1), 'CURRENT_CS_N': ('M1', 'J3-10'), 'ADC_RESET': ('J_BP2', 18), 'MEAS_EN': ('J_BP2', 14), 'ADC_BUSY': ('U11', 5),
        'ADC_CONVST': ('R37', 2), 'ADC_CS': ('U21', 3), 'PFAIL_N': ('R42', 1), 'SD_CS': ('M1', 'J1-7'), 'SUP_RAW_N': ('R13', 1), '5V_M1': ('C14', 1),
        'MCU_ARM': ('J_BP3', 18), 'HEARTBEAT': ('M1', 'J3-18'), 'PWM': ('J_BP3', 14), 'CORE_LINK': ('R14', 2), 'SUP_N_OUT': ('R41', 2),
        'SENSOR_ENABLE': ('J_BP3', 9), 'TC2_CS': ('U23', 11), 'TC1_CS': ('U23', 8), 'INTERLOCK': ('R26', 1), 'HW_ARMED': ('R3', 1),
        'LOGGER_CURRENT_OK': ('R2', 1)}
SERV = {r: NODE[parts[r]['pins']['1']] for r in parts if parts[r]['source_ref'] == 'ADDED_R6_SERVICE_SERIES'}
FIRST = ['R71']   # 30.09: SENSOR_ENABLE has one node pad (J_BP3.9) in the crowded J_BP3 cluster; placed last it ended 11.5 mm away
SERV = {r: SERV[r] for r in FIRST + [r for r in SERV if r not in FIRST]}
assert len(SERV) == 33, len(SERV)
for r, (u, n) in SERV.items():
    place_near(r, (u, str(n)), own='1', lane_ok=u in ('M1', 'R42'), radius=25)
# ---- test pads ----
for tp, t in {'TP1': ('C13', 1), 'TP2': ('C3', 1), 'TP3': ('J_BP3', 5), 'TP4': ('U1', 10), 'TP5': ('R35', 1), 'TP6': ('U11', 7),
              'TP7': ('C14', 1), 'TP8': ('R13', 1)}.items():
    place_near(tp, (t[0], str(t[1])), radius=30)
missing = sorted(set(r for r, v in parts.items() if v.get('on_board', True)) - set(L)); assert not missing, missing
(P / 'src/placement.json').write_text(json.dumps(L, indent=1) + '\n')
far = {r: d for r, d in REPORT.items() if d > 6}
print(len(L), 'placed; search distance > 6 mm:', far)
