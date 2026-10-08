"""P08 R2: locked switched sensor path through K1 (task 5.10: plus and return >= 0.5 mm, short), then the DSN export.
- SENSOR_LIMITED: U1.6 (TPS2553 OUT) -> 45 deg -> K1.3 (COM_A), F.Cu;
- 5V_SENSOR: K1.4 (NO_A) -> J4.1, F.Cu, passing right of the J4.2 pad;
- AGND_SENSOR: K1.5 (NO_B) -> J4.2, B.Cu (crosses the F.Cu 5V_SENSOR line on the other layer; all four ends are PTH pads);
- GND tie U1.2 -> C1.2 (0.5 mm, F.Cu): the input capacitor's return straight to the TPS2553 GND pin, with a GND via 1.2 mm from
  U1.2 to the B.Cu plane (return of the output capacitor C2 through its own via);
- C6 / C7 / C8 pads to VDD / VSS of the TO-92 supervisors U6 / U7 / U8 (0.6 mm, 3.75 mm);
- K1.6 (COM_B, GND): solid connection to both GND pours (no thermal spokes in the return path).
Width: the PWR class of board.py (0.6 mm, clearance 0.3). R18 / C2 / R17 / R28 hang on these nets and are routed by the router (PWR class).
"""
from pathlib import Path
import pcbnew as p, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from board import NAME
P = Path(__file__).resolve().parents[1]; path = P / f'eda/{NAME}.kicad_pcb'
WIDTH = .6


def xy(x, y):
    return p.VECTOR2I(p.FromMM(x), p.FromMM(y))


def pad(b, ref, num):
    f = next(f for f in b.GetFootprints() if f.GetReference() == ref); return next(a for a in f.Pads() if a.GetNumber() == num)


def poz(b, ref, num):
    a = pad(b, ref, num); return p.ToMM(a.GetPosition().x), p.ToMM(a.GetPosition().y), a.GetNet()


def trasa(b, pts, net, layer, w=WIDTH):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if (round(x0, 4), round(y0, 4)) == (round(x1, 4), round(y1, 4)):
            continue
        t = p.PCB_TRACK(b); t.SetLayer(layer); t.SetWidth(p.FromMM(w)); t.SetStart(xy(x0, y0)); t.SetEnd(xy(x1, y1)); t.SetNet(net)
        t.SetLocked(True); b.Add(t)


if __name__ == '__main__':
    b = p.LoadBoard(str(path))
    ux, uy, n_lim = poz(b, 'U1', '6'); kx3, ky3, _ = poz(b, 'K1', '3')
    assert n_lim.GetNetname() == 'SENSOR_LIMITED' and kx3 < ux and ky3 > uy
    d = ux - kx3; trasa(b, [(ux, uy), (kx3, uy + d), (kx3, ky3)], n_lim, p.F_Cu)
    jx1, jy1, n5 = poz(b, 'J4', '1'); kx4, ky4, _ = poz(b, 'K1', '4'); jx2, jy2, nag = poz(b, 'J4', '2'); kx5, ky5, _ = poz(b, 'K1', '5')
    assert n5.GetNetname() == '5V_SENSOR' and nag.GetNetname() == 'AGND_SENSOR' and abs(jx1 - jx2) < 1e-6 and jy2 < jy1 and abs(kx4 - kx5) < 1e-6 and ky4 < ky5
    xm = jx1 + 2.1   # vertical leg between the J4 pad column and the K1 NO column (2.1 mm right of the J4 pads)
    trasa(b, [(jx1, jy1), (xm, jy1 - 2.1), (xm, ky4 + (kx4 - xm)), (kx4, ky4)], n5, p.F_Cu)
    trasa(b, [(jx2, jy2), (jx2 + (ky5 - jy2), ky5), (kx5, ky5)], nag, p.B_Cu)
    gx, gy, ng = poz(b, 'U1', '2'); cx2, cy2, _ = poz(b, 'C1', '2')   # 5.10: C1 return straight to the TPS2553 GND pin (verify_pcb.py return path)
    assert ng.GetNetname() == 'GND' and abs(gy - cy2) < 1e-6 and cx2 > gx
    trasa(b, [(gx, gy), (cx2, cy2)], ng, p.F_Cu, .5)
    v = p.PCB_VIA(b); v.SetPosition(xy(gx + 1.2, gy)); v.SetWidth(p.FromMM(.9)); v.SetDrill(p.FromMM(.4)); v.SetViaType(p.VIATYPE_THROUGH)
    v.SetLayerPair(p.F_Cu, p.B_Cu); v.SetNet(ng); v.SetLocked(True); b.Add(v)   # the tie to the B.Cu GND plane (C2 output capacitor returns through it)
    for c, u in (('C6', 'U6'), ('C7', 'U7'), ('C8', 'U8')):   # 5.10: supervisor decoupling (placement.py: C right under VDD / VSS)
        for up, cp in (('2', '1'), ('3', '2')):
            x0, y0, n0 = poz(b, u, up); x1, y1, n1 = poz(b, c, cp); assert n0.GetNetCode() == n1.GetNetCode() and abs(x1 - x0) < .5 and 3 < y1 - y0 < 4.5
            trasa(b, [(x0, y0), (x1, y1)], n0, p.F_Cu)
    g = pad(b, 'K1', '6'); assert g.GetNetname() == 'GND'; g.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
    b.BuildConnectivity(); p.SaveBoard(str(path), b)
    (P / 'routing').mkdir(exist_ok=True)
    assert p.ExportSpecctraDSN(b, str(P / f'routing/{NAME}.dsn'))
    print(f'{NAME}: SENSOR_LIMITED / 5V_SENSOR (F.Cu) and AGND_SENSOR (B.Cu) locked at {WIDTH} mm, K1.6 solid; DSN exported.')
