"""P10 R2: locked CAN_H / CAN_L from the OBD tail J3 through the pads of D1 (PESD2CAN) to U1 (TCAN1051V), then the DSN export.
1.10 (recenzja): Freerouting joined J3.1, D1.2 and U1.7 as a star, so D1 hung on a 3 mm stub of CAN_H; the protection must sit on
the path. Each line: J3 pad -> left to 0.8 mm before the D1 pad column -> 45 deg into the D1 pad -> 1.4 mm out of the D1 pad row
(above for CAN_H, below for CAN_L, leaving room for the GND via of the D1 GND pad) -> left -> 45 deg into the U1 pin. F.Cu, board.SIGNAL_W, locked.
The supplies of P10 (5V_SYS ~70 mA for TCAN1051V, 3V3_IO a few mA) are routed as signals (0.3 mm).
"""
from pathlib import Path
import pcbnew as p, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from board import NAME, SIGNAL_W
P = Path(__file__).resolve().parents[1]; path = P / f'eda/{NAME}.kicad_pcb'
TRASY = [('J3', '1', 'D1', '2', 'U1', '7', -1), ('J3', '2', 'D1', '1', 'U1', '6', +1)]   # (+1 / -1: obejście D1 od dołu / od góry)
OBEJSCIE = 1.4


def xy(x, y):
    return p.VECTOR2I(p.FromMM(x), p.FromMM(y))


def poz(b, ref, num):
    f = next(f for f in b.GetFootprints() if f.GetReference() == ref); a = next(a for a in f.Pads() if a.GetNumber() == num)
    return p.ToMM(a.GetPosition().x), p.ToMM(a.GetPosition().y), a.GetNet()


def trasa(b, pts, net):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if (round(x0, 4), round(y0, 4)) == (round(x1, 4), round(y1, 4)):
            continue
        t = p.PCB_TRACK(b); t.SetLayer(p.F_Cu); t.SetWidth(p.FromMM(SIGNAL_W)); t.SetStart(xy(x0, y0)); t.SetEnd(xy(x1, y1)); t.SetNet(net)
        t.SetLocked(True); b.Add(t)


if __name__ == '__main__':
    b = p.LoadBoard(str(path))
    for j, jn, d, dn, u, un, strona in TRASY:
        jx, jy, net = poz(b, j, jn); dx, dy, _ = poz(b, d, dn); ux, uy, _ = poz(b, u, un)
        yb = dy + strona * OBEJSCIE                 # tor obejścia nad / pod korpusem D1 (1.10: 0,6 mm zamykało pole GND D1.3 bez miejsca
                                                    # na przelotkę; 1,4 mm zostawia 1,9 mm nad / pod polem 3)
        k = abs(uy - yb)
        trasa(b, [(jx, jy), (dx + abs(jy - dy), jy), (dx, dy), (dx, yb), (ux + .685 + k, yb), (ux + .685, uy), (ux, uy)], net)
    b.BuildConnectivity(); p.SaveBoard(str(path), b)
    (P / 'routing').mkdir(exist_ok=True)
    assert p.ExportSpecctraDSN(b, str(P / f'routing/{NAME}.dsn'))
    print(f'{NAME}: CAN_H / CAN_L locked through D1; DSN exported.')
