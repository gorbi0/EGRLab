"""P11 R2 placement (4.10.2026). Writes src/placement.json: ref -> [x, y, rotation]; origin = footprint origin (pin 1 for the THT
library parts and the wire fields, centre for the 1206). Board x 0..W (x = 0: long edge facing the panel), y 0..H (y = 0: short
edge facing wall A, P12). Run with KiCad Python. Only 5 parts, so the positions are explicit (no search as in P10 R2).

Requirements (user 4.10, README "Decyzje"):
- J_P12 (IDC 2x10 right angle): on the short edge y = 0, mating face flush with the edge (body front at y = 0.05 as P10 J1),
  pin 1 at the smaller x, centred on the width;
- wire fields J11 (18), J8 (2), J6 (2) along the panel edge x = 0, one after the other in y; each turned 90 deg so that the cable-tie
  anchor (2 x 3.2 mm NPTH, 10.5 mm in front of the first pad row) lies between the pads and the panel edge and the wires leave
  straight towards the panel; anchor centre x = 4.5 (hole edge 2.9 mm from the edge);
- R1 (100R, LOGGER fitted / DNP with P04) between J_P12 pin 20 (3V3_IO) and the PANEL_3V3 pads, in the free strip behind the
  header between the two upper M3 zones, pad 1 (3V3_IO) towards pin 20;
- 4 M3 holes from board.HOLES; no courtyard in their D7 zones (checked here and in verify_pcb.py).
"""
import pcbnew as p, json, math, sys
from pathlib import Path
P = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(P / 'src'))
from board import W, H, HOLES, HOLE_ZONE_D, SUPPORT_KEEPOUT
parts = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
PITCH = 22.86                                # J_P12 pin 1 to pin 19 (x)
XJ = round((W - PITCH) / 2, 3)               # pin 1 of J_P12; pins centred on the width
XF = 15.0                                    # first pad row of every field (anchor centre at XF - 10.5 = 4.5)
L = {
    'J_P12': [XJ, 13.33, 90],                # front face y = 13.33 - 13.28 = 0.05; odd pins y 13.33, even 10.79
    'R1': [25.5, 17.6, 180],                 # pad 1 (3V3_IO) at +x, towards J_P12.20; the variant note left of it (silkscreen.py)
    'J11': [XF, 56.5, 90],                   # pad 1 column at y 56.5, column 9 (pads 17 / 18) at y 28.5; courtyard y 23.0..62.0
    'J8': [XF, 71.5, 90],                    # pad 1 (LOOP_OUT, TEST cavity 10) y 71.5, pad 2 y 68.0; courtyard y 62.5..77.0
    'J6': [XF, 86.5, 90],                    # pad 1 (SCOPE core) y 86.5, pad 2 (shield) y 83.0; courtyard y 77.5..92.0
}


def courtyard(ref):
    lib, name = parts[ref]['footprint'].split(':')
    f = p.FootprintLoad(str(P / 'eda/libraries' / (lib + '.pretty')), name); assert f, ref
    x, y, r = L[ref]; f.SetPosition(p.VECTOR2I(p.FromMM(x), p.FromMM(y))); f.SetOrientationDegrees(r)
    ls = p.LSET(); ls.AddLayer(p.F_CrtYd); bb = f.GetLayerBoundingBox(ls)
    anchors = [(p.ToMM(a.GetPosition().x), p.ToMM(a.GetPosition().y)) for a in f.Pads() if a.GetAttribute() == p.PAD_ATTRIB_NPTH]
    return (p.ToMM(bb.GetLeft()), p.ToMM(bb.GetTop()), p.ToMM(bb.GetRight()), p.ToMM(bb.GetBottom())), anchors


box = {}; anchors = {}
for r in L:
    box[r], anchors[r] = courtyard(r)
onboard = sorted(r for r, v in parts.items() if v.get('on_board', True))
assert sorted(L) == onboard, (sorted(L), onboard)
for a in L:
    for c in L:
        if a < c:
            ba, bc = box[a], box[c]
            assert not (ba[0] < bc[2] and bc[0] < ba[2] and ba[1] < bc[3] and bc[1] < ba[3]), ('courtyards overlap', a, c)
rz = HOLE_ZONE_D / 2
for r, b in box.items():
    for hx, hy in HOLES:
        d = math.hypot(max(b[0] - hx, 0, hx - b[2]), max(b[1] - hy, 0, hy - b[3]))
        assert d > rz, ('courtyard in a D7 zone', r, (hx, hy), round(d, 2))
    if r != 'J_P12':   # the header body front lies on the edge (its courtyard passes it by 0.5 mm, as P10 J1)
        assert b[0] > 0 and b[1] > 0 and b[2] < W and b[3] < H, ('courtyard outside the board', r, b)
for r, a in anchors.items():
    for x, y in a:
        assert all(math.hypot(x - hx, y - hy) > 1.6 + rz for hx, hy in HOLES), ('anchor hole in a D7 zone', r, (x, y))
assert set(anchors) - {'J_P12', 'R1'} == set(SUPPORT_KEEPOUT)
(P / 'src/placement.json').write_text(json.dumps(L, indent=1) + '\n')
print(len(L), 'placed; courtyards:', {r: [round(v, 2) for v in b] for r, b in box.items()})
