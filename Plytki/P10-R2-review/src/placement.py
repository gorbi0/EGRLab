"""P10 R2 placement (format S1, class 1/3, slot S3 of level 4; S1-3). Writes src/placement.json: ref -> [x, y, rotation(, 'B')];
origin = footprint origin (pin 1 for THT library parts and the OBD tail, centre for SMD). Board x 0..53 (x = 53: input wall of the
enclosure, where the cables from the car leave), y 0..100 (0 = edge A, P12; 100 = edge B, service side). Run with KiCad Python.
Machinery (geo, place_near, bottom-side support) from P09 R2 placement.py (30.09.2026).

Fixed by S1 (SPECYFIKACJA-FORMATU-S1.md sections 4-7) and the BOM notes:
- J1 (J_BP, IDC 2x5 right angle): mating face at y = 0, pin centre x = 26.5, pin 1 at the smaller x;
- J2 (service header 1x9 right angle): pins in x 16.34..36.66, ~6 mm beyond edge B; pin 1 at the LARGER x (a right-angle header on
  the top side with its pins towards edge B cannot have it the other way; as P09 R2 J2 and P03 R6 J_SV);
- 4 M3 holes (x 4 / 49, y 14 / 86) with the D7 standoff zones;
- level 4 (S1-3): all parts on the top side (no SOIC on the bottom; the board is 27 % full, so nothing needs the bottom).
J3 (OBD tail, harness W3, docs/WIAZKI.md): not on edge A or B but at the input wall (S1 section 7: P10 in S3 next to it). Rotated 270:
the cable-tie anchor (two 3.2 mm holes, 12 mm from the solder row) is towards the wall, the cable lies straight in along y = JY + 1.75
and nothing else may stand under it (CABLE box). D1 (PESD2CAN) between the pads and U1 ("at cable entry"), turned so its CANH / CANL
pins face the pads in the same order (CAN_H at the smaller y); U1 (TCAN1051V) with CANH / CANL towards J3; U2 (RX buffer with Ioff)
left of U1, input 1A next to U1 RXD; R1 at U2.3 (driver); the buffered CAN_RX runs up to J1.8.
Passives: nearest free spot at the pin they belong to (decoupling: IC supply pin; pull-up: the buffer input; series: the driver pin;
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
JX, JY = 35.0, 55.0                       # J3 pad 1 (CAN_H); pad 2 (CAN_L) at JY + 3.5; anchor holes at (JX + 12, JY - 3.5 / JY + 7)
SUPPORT = [(JX + 12, JY - 3.5), (JX + 12, JY + 7.0)]   # anchor holes of J3 (cable tie)
SUPPORT_R = 3.0                           # board.SUPPORT_KEEPOUT['J3']
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
put('J1', 26.5 - 2 * 2.54, 13.33, 90)        # pin 1 (x 21.42) at the smaller x; mating face at y = 0 (as P09 R2 J1)
put('J2', 26.5 + 4 * 2.54, 95.96, 270)       # pin 1 at x 36.66 (larger x), pin 9 at 16.34; body front at y = 100
# ---- CAN input at the input wall ----
put('J3', JX, JY, 270)                        # courtyard x 33.48..49.03, y 49.47..64.03; anchors at x 47 (4.4 mm hole edge to the edge)
BOX['CABLE'] = (JX + 14.03, JY - 2.0, W, JY + 5.5); SIDE['CABLE'] = 'F'   # the cable between the anchor and the wall: keep clear
put('D1', 31.0, JY + 1.75, 180)               # pins 2 (CAN_H) / 1 (CAN_L) face J3.1 / J3.2, GND pin towards U1
put('U1', 24.8, JY + 1.75, 0)                 # CANH (7) / CANL (6) towards D1 and J3; VCC (3) and RXD (4) on the left
put('U2', 13.0, JY + 1.0, 180)                # 1A (2) next to U1 RXD (4), 1Y (3) above it; VCC (14) on the left
for a, c in [(r, o) for r in list(BOX) for o in list(BOX) if r < o]:
    ba, bc = BOX[a], BOX[c]
    assert not (ba[0] < bc[2] and bc[0] < ba[2] and ba[1] < bc[3] and bc[1] < ba[3]), ('fixed parts overlap', a, c)
# ---- decoupling and bulk ----
for c, (u, n) in {'C1': ('U1', 3), 'C2': ('U1', 5), 'C3': ('U2', 14), 'C4': ('J1', 2), 'C5': ('J1', 4)}.items():
    place_near(c, (u, str(n)))
# ---- series resistor at its driver, pull-up at the buffer input ----
place_near('R1', ('U2', '3'))
place_near('R2', ('U2', '2'), radius=20)
# ---- service resistors: node side (pin 1) next to a pad of the node ----
NODE = {'R3': ('C1', 1), 'R4': ('C2', 1), 'R5': ('U1', 4), 'R6': ('R1', 2), 'R7': ('J1', 6), 'R8': ('J3', 1), 'R9': ('J3', 2)}
for r, (u, n) in NODE.items():
    place_near(r, (u, str(n)), own='1', radius=14)
missing = sorted(set(r for r, v in parts.items() if v.get('on_board', True)) - set(L)); assert not missing, missing
(P / 'src/placement.json').write_text(json.dumps(L, indent=1) + '\n')
far = {r: d for r, d in REPORT.items() if d > 6}
print(len(L), 'placed; search distance > 6 mm:', far)
