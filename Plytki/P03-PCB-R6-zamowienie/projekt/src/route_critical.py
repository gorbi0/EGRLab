"""P03 R6: locked 5 V path, then the Specctra DSN for Freerouting (the P02 R4 pattern, without power pours).
M1 takes its 5 V on J1-21 at the USB end (edge B side); P02 R4 delivers 5V_SYS on J_BP2.17/19/20 at edge A. The path is drawn
here, 1.5 mm wide, so its copper resistance is fixed and checked (verify_pcb.py) instead of left to the router:
- 5V_SYS (F.Cu): J_BP2.20 - J_BP2.19 - J_BP2.17, J_BP2.19 -> C13.1 -> Q1 D (drain of the USB back-feed blocker);
- 5V_M1: Q1 S -> F.Cu to two vias -> B.Cu spine x = SPINE_X along the right side of M1 (outside the antenna keepout)
  -> y = 93 under the USB end of M1 -> x = 71 -> M1 J1-21 (THT) -> F.Cu to C14.1 (local bypass);
- U5.6 (SENSE of the LTC4412) -> spine, 0.3 mm stub.
ZASILANIE-RESET.md budget: <= 50 mOhm of copper in the main path (verify_pcb.py computes it from these tracks).
The remaining 5 V pins (U5.1, R44, R45, TP1, TP7) are routed by Freerouting (class PWR, 0.6 mm) to this copper.
"""
from pathlib import Path
import pcbnew as p
P = Path(__file__).resolve().parents[1]; path = P / 'eda/P03.kicad_pcb'
mm = p.FromMM; F, B = p.F_Cu, p.B_Cu
SPINE_X, Y_LOW, X_TURN, WIDE = 97.4, 93.0, 71.0, 1.5


def xy(x, y):
    return p.VECTOR2I(mm(x), mm(y))


if __name__ == '__main__':
    b = p.LoadBoard(str(path)); fp = {f.GetReference(): f for f in b.GetFootprints()}

    def pad(r, n):
        a = next(q for q in fp[r].Pads() if q.GetNumber() == str(n)); return (p.ToMM(a.GetPosition().x), p.ToMM(a.GetPosition().y))

    def track(net, pts, layer, w=WIDE):
        for a, c in zip(pts, pts[1:]):
            t = p.PCB_TRACK(b); t.SetStart(xy(*a)); t.SetEnd(xy(*c)); t.SetWidth(mm(w)); t.SetLayer(layer); t.SetNet(b.FindNet(net)); t.SetLocked(True); b.Add(t)

    def via(net, q):
        v = p.PCB_VIA(b); v.SetPosition(xy(*q)); v.SetWidth(mm(.9)); v.SetDrill(mm(.4)); v.SetViaType(p.VIATYPE_THROUGH)
        v.SetLayerPair(F, B); v.SetNet(b.FindNet(net)); v.SetLocked(True); b.Add(v)

    j17, j19, j20 = pad('J_BP2', 17), pad('J_BP2', 19), pad('J_BP2', 20)
    d, s = pad('Q1', 3), pad('Q1', 2)
    assert abs(s[0] - SPINE_X) < 1e-3, ('Q1 source must lie on the spine line', s)
    track('5V_SYS', [j20, j19, j17], F); track('5V_SYS', [j19, pad('C13', 1), d], F)
    v1, v2 = (SPINE_X, s[1] + 2.8), (SPINE_X, s[1] + 4.1)
    track('5V_M1', [s, v2], F); via('5V_M1', v1); via('5V_M1', v2)
    j21 = pad('M1', 'J1-21')
    track('5V_M1', [v1, (SPINE_X, Y_LOW), (X_TURN, Y_LOW), (X_TURN, j21[1]), j21], B)
    track('5V_M1', [j21, pad('C14', 1)], F, 1.0)
    u6 = pad('U5', 6); track('5V_M1', [u6, (SPINE_X, u6[1])], F, .3)
    b.BuildConnectivity(); p.SaveBoard(str(path), b)
    (P / 'routing').mkdir(exist_ok=True)
    assert p.ExportSpecctraDSN(b, str(P / 'routing/P03.dsn'))
    print('5 V path locked (J_BP2 -> Q1 -> spine -> M1 J1-21); DSN exported.')
