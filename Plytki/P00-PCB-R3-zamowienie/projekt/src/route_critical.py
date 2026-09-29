"""P00 R2: supply path and the eight source channels locked before autorouting.
- Supply (1.0 mm, F.Cu): J10.1 (+VIN) -> D1 anode; D1 cathode (VIN_P) -> C5, C4 -> U2.1; U2.3 (3V3) -> C7, C6 -> RL10.
- 3V3 to the switches: F.Cu feed down the gap between channels 4 and 5, one via, B.Cu rail under the switch
  row (pad 2 of SW1..SW9) - Freerouting alone left two 3V3 connections open in the dense column pattern.
- Each channel on F.Cu: switch COM -> 'H' path under the two resistor bodies to RLn (bottom pad) and RSn (top
  pad); RLn -> LED anode; RSn -> header pin 1. GND (switch pad 3, LED cathode, header pin 2) by the pours.
Every stub ends on a rail vertex (Freerouting does not see a stub ending in the middle of a segment).
Freerouting routes the rest (555 block, heartbeat column, test pads); GND is made by the two pours after import.
"""
from pathlib import Path
import pcbnew as p
P = Path(__file__).resolve().parents[1]; path = P / 'eda/P00.kicad_pcb'; b = p.LoadBoard(str(path))
mm = p.FromMM; F = p.F_Cu


def xy(x, y):
    return p.VECTOR2I(mm(x), mm(y))


def net(n):
    for cand in (n, '/' + n):
        v = b.FindNet(cand)
        if v is not None and v.GetNetCode() > 0:
            return v
    raise KeyError(n)


def tr(n, pts, w=1.0, layer=F):
    for a, c in zip(pts, pts[1:]):
        t = p.PCB_TRACK(b); t.SetStart(xy(*a)); t.SetEnd(xy(*c)); t.SetWidth(mm(w)); t.SetLayer(layer); t.SetNet(net(n)); t.SetLocked(True); b.Add(t)


tr('P00_VIN', [(7, 20), (15.84, 20)])
tr('P00_VIN_P', [(26, 20), (29, 20), (33, 20), (37, 20)])
tr('P00_VIN_P', [(33, 20), (33, 13.5)]); tr('P00_VIN_P', [(29, 20), (29, 26)])
tr('P00_V33', [(42.08, 20), (45, 20), (47, 20), (53, 20)])
tr('P00_V33', [(45, 20), (45, 13.5)]); tr('P00_V33', [(47, 20), (47, 26)])
# R2 permanent preload and defined COUT series resistance.
tr('P00_V33', [(53, 20), (53, 13.5), (67, 13.5)], .6)
tr('P00_COUT_RET', [(49, 26), (49, 29.5), (47.5, 31), (42.16, 31)], .6)
CX = [14 + 11 * k for k in range(8)]
tr('P00_V33', [(53, 20), (53, 36), (52.5, 36.5), (52.5, 51.54)], .6)
v = p.PCB_VIA(b); v.SetPosition(xy(52.5, 51.54)); v.SetWidth(mm(1.0)); v.SetDrill(mm(.5)); v.SetViaType(p.VIATYPE_THROUGH)
v.SetLayerPair(F, p.B_Cu); v.SetNet(net('P00_V33')); v.SetLocked(True); b.Add(v)
tr('P00_V33', [(x, 51.54) for x in sorted(CX[:4] + [52.5] + CX[4:] + [102])], .8, p.B_Cu)
for n, cx in enumerate(CX, 1):
    tr(f'P00_S{n}', [(cx - 3.5, 54.08), (cx - 3.5, 49), (cx, 49), (cx + 3.5, 49), (cx + 3.5, 43.92)], .5)
    tr(f'P00_LED{n}', [(cx - 3.5, 43.92), (cx - 1.27, 41.65), (cx - 1.27, 40)], .5)
    tr(f'P00_OUT{n}', [(cx + 3.5, 54.08), (cx + 3.5, 56.3), (cx + 1.27, 58.53), (cx + 1.27, 59)], .5)
tr('P00_LED_HB', [(98.5, 43.92), (100.73, 41.69), (100.73, 40)], .5)
tr('P00_HEART', [(105.5, 54.08), (105.5, 56.3), (103.27, 58.53), (103.27, 59)], .5)
nc = b.GetDesignSettings().m_NetSettings.GetDefaultNetclass(); nc.SetClearance(mm(.3)); nc.SetTrackWidth(mm(.5)); nc.SetViaDiameter(mm(1)); nc.SetViaDrill(mm(.5))
b.BuildConnectivity(); p.SaveBoard(str(path), b)
(P / 'routing').mkdir(exist_ok=True)
assert p.ExportSpecctraDSN(b, str(P / 'routing/P00.dsn'))
print('P00 supply path, 3V3 rail and channels locked; DSN exported.')
