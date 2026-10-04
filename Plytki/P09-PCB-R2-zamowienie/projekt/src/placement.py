"""P09 R2 placement (format S1, class 1/3, slot S3 of level 3). Writes src/placement.json: ref -> [x, y, rotation(, 'B')]; origin =
footprint origin (pin 1 for THT library parts and the module sockets, centre for SMD). Board x 0..53 (x = 53: input wall of the
enclosure, where the thermocouple sockets are), y 0..100 (0 = edge A, P12; 100 = edge B, service side). Run with KiCad Python.
Machinery (geo, place_near) from P03 R6 placement.py (30.09.2026), with bottom-side placement added.

Fixed by S1 (SPECYFIKACJA-FORMATU-S1.md sections 4-6) and the BOM notes:
- J1 (J_BP, IDC 2x8 right angle): mating face at y = 0, pin centre x = 26.5, pin 1 at the smaller x;
- J2 (service header 1x13 right angle): pins in x 11.26..41.74, ~6 mm beyond edge B. Pin 1 stands at the LARGER x: a right-angle
  header on the top side with its pins towards edge B cannot have it the other way (as P03 R6 J_SV1..3; the BOM note of J2 says so);
- 4 M3 holes (x 4 / 49, y 14 / 86) with the D7 standoff zones;
- the reserved strip of edge A (S1 section 5: y 0..10, x 10..43) holds J1 only, on both sides (review 1.10: C4 / R20 reached into it).
Modules J3 / J4 (MAX31856 XU soldered directly by their 1x9 header, user decision 1.10; outline provisional until the 1:1 fit, README):
rotated 90 so the thermocouple terminal ends face the input wall; header column at x = MX. J3 below J1 and clear of the H3 zone
(49, 14), J4 above the H4 zone (49, 86).
Logic in the left column: U1 (input buffers SCLK / MOSI / TC1_CS / TC2_CS) under J1 next to its signal pins, U2 (MISO buffers)
next to the module headers between J3 and J4, U3 (HC139 selecting the MISO buffer) left of U2, JP1 / JP2 7.5 mm below the VIN pins
of J3 / J4 (review 1.10: JP1 next to J3.1 pushed C6 beyond 6 mm from the pin).
Passives: nearest free spot at the pin they belong to (decoupling: IC supply pin; pulls: the buffer pin; series: the driver pin).
Service resistors R20-R30 on the bottom (README R2 plan; S1-2: SMD <= 1.5 mm, >= 1 mm from THT pads, outside the standoff zones).
"""
import pcbnew as p, json, math
from pathlib import Path
P = Path(__file__).resolve().parents[1]
S1 = json.loads((P.parents[0] / 'Format-S1/format-s1.json').read_text(encoding='utf-8'))
parts = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
W, H = S1['klasy']['1/3']['W'], S1['klasy']['1/3']['H']
HOLES = [(x, y) for x in S1['otwory_M3']['x_w_slocie'] for y in S1['otwory_M3']['y']]
RZ = S1['otwory_M3']['strefa_dystansu_srednica'] / 2
MX, J3Y, J4Y = 30.5, 22.5, 53.0          # module header column x; y of pin 1 (VIN) of J3 / J4
STRIP_A = (10.0, S1['krawedz_A']['strefa_y'][0], 43.0, S1['krawedz_A']['strefa_y'][1])   # S1 section 5, slot S3 = the whole board
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
    for (hx, hy), rr in [(h, RZ) for h in HOLES]:
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
put('J1', 26.5 - 3.5 * 2.54, 13.33, 90)      # pin 1 (x 17.61) at the smaller x; mating face at y = 0 (as P03 R6 J_BP)
put('J2', 26.5 + 15.24, 95.96, 270)          # pin 1 at x 41.74 (larger x), pin 13 at 11.26; body front at y = 100
# ---- modules: terminal ends towards the input wall (x = 53) ----
put('J3', MX, J3Y, 90)                        # courtyard x 28.0..50.0, y 20.0..45.32 (H3 zone ends at y 17.5)
put('J4', MX, J4Y, 90)                        # courtyard y 50.5..75.82 (H4 zone starts at y 82.5)
# ---- logic ----
put('U1', 12.0, 26.0, 0)                      # SOIC-14: inputs from J1.6/8/12/14, outputs down to R14-R17 and the modules
put('U2', 21.5, 50.0, 0)                      # MISO buffers between the module headers (J3.5 at y 32.66, J4.5 at y 63.16)
put('U3', 9.0, 62.0, 0)                       # HC139 below U2 (the lower third was empty): OE1_N / OE2_N up to U2.1 / U2.4; clear of the H3 zone
put('JP1', 25.0, 30.0, 0)                     # VIN select of J3, 7.5 mm below J3.1 like JP2 (the spot left of J3.1 is C6's)
put('JP2', 25.0, 60.5, 0)                     # VIN select of J4
for a, c in [(r, o) for r in list(BOX) for o in list(BOX) if r < o]:
    ba, bc = BOX[a], BOX[c]
    assert not (ba[0] < bc[2] and bc[0] < ba[2] and ba[1] < bc[3] and bc[1] < ba[3]), ('fixed parts overlap', a, c)
    # (standoff zones are checked by verify_pcb.py)
# ---- decoupling and bulk ----
for c, (u, n) in {'C1': ('U1', 14), 'C2': ('U2', 14), 'C3': ('U3', 16), 'C6': ('J3', 1), 'C7': ('J4', 1), 'C4': ('J1', 4), 'C5': ('J1', 2)}.items():
    place_near(c, (u, str(n)))
# ---- series resistors at their drivers ----
for r, (u, n) in {'R14': ('U1', 3), 'R15': ('U1', 6), 'R16': ('U1', 8), 'R17': ('U1', 11), 'R11': ('U2', 3), 'R12': ('U2', 6)}.items():
    place_near(r, (u, str(n)))
# ---- pull-ups / pull-downs at the buffer pins ----
PULL = {'R1': ('U1', 9), 'R2': ('U1', 12), 'R3': ('U1', 2), 'R4': ('U1', 5), 'R5': ('U1', 8), 'R6': ('U1', 11), 'R7': ('U1', 3), 'R8': ('U1', 6),
        'R9': ('U2', 2), 'R10': ('U2', 5), 'R13': ('R11', 2), 'R18': ('U2', 1), 'R19': ('U2', 4)}
for r, (u, n) in PULL.items():
    place_near(r, (u, str(n)), radius=20)
# ---- service resistors on the bottom: node side (pin 1) next to a pad of the node ----
NODE = {'R20': ('C4', 1), 'R21': ('C5', 1), 'R22': ('J3', 1), 'R23': ('J4', 1), 'R24': ('J3', 2), 'R25': ('J4', 2), 'R26': ('U1', 8),
        'R27': ('U1', 11), 'R28': ('U2', 1), 'R29': ('U2', 4), 'R30': ('R13', 1)}
for r, (u, n) in NODE.items():
    place_near(r, (u, str(n)), own='1', radius=12, side='B')
missing = sorted(set(r for r, v in parts.items() if v.get('on_board', True)) - set(L)); assert not missing, missing
(P / 'src/placement.json').write_text(json.dumps(L, indent=1) + '\n')
far = {r: d for r, d in REPORT.items() if d > 6}
print(len(L), 'placed; search distance > 6 mm:', far)
