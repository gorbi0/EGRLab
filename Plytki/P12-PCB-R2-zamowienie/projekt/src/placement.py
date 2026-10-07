"""P12 R2 placement (as R1) from docs/kontrakt-P12.json (positions in docs/GEOMETRIA.csv). Writes src/placement.json: ref -> [X, Y, rotation]
(KiCad, footprint origin = pin 1). Plain Python (no pcbnew).
Straight IDC footprint (Connector_IDC:IDC-Header_2xNN_P2.54mm_Vertical): pin 1 at (0, 0), pin 2 at (2.54, 0), pin 3 at (0, 2.54).
Rotation 90 (KiCad, counter-clockwise): local (lx, ly) -> (X + ly, Y - lx): pins 1, 3, 5 ... along +x (pin 1 at the smaller x), the even
row 2.54 mm higher in z than the odd row. Reason (README, „Orientacja”): on the stack boards the angled IDC has the even row nearer
edge A, i.e. the even row is the LOWER row of the mating face and pin 1 is at the smaller x; a straight (untwisted) ribbon keeps x,
and the same socket seen from P12 (facing the other way) then has the odd row low -> on P12 the odd row is lower, pin 2 above pin 1.
"""
import json
from pathlib import Path
from board import kxy, TP_XZ
P = Path(__file__).resolve().parents[1]
K = json.loads((P / 'docs/kontrakt-P12.json').read_text(encoding='utf-8'))
L = {}
for z in K['zlacza']:
    m = z['n'] // 2
    x1 = z['x_mm'] - (m - 1) * 1.27          # pin 1 (odd row, smaller x)
    z1 = z['z_osi_mm'] - 1.27                # odd row 1.27 mm below the axis
    X, Y = kxy(x1, z1); L[z['ref']] = [X, Y, 90]
for r, (x, zz) in TP_XZ.items():
    X, Y = kxy(x, zz); L[r] = [X, Y, 0]
(P / 'src/placement.json').write_text(json.dumps(L, indent=1) + '\n')
print('placement:', len(L), 'parts')
