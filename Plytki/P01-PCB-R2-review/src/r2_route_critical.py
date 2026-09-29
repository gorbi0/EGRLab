"""R2: explicit high-current paths and local gate/Kelvin/probe paths, before signal routing.
Differences vs route_critical.py (R1):
- no F.Cu under the heatsink profiles (PCB1-01): BAT_FUSED enters the HS1 bay from below,
  Q1 DRAIN and GATE leave the HS2 bay straight down; power under the profiles only on B.Cu,
- C6 sits in the HS2 bay between Q1 G and S (PCB1-05); TP1/TP2 moved inside the bay,
- local VS stubs to the rail for R1, C1, C2, D9, D4, Q2 and R22; C5 VPROT branch on its own track
  to D3 so no signal ever lands on the Kelvin sense pads,
- the rails are split at every stub/via so the stubs end on a rail vertex.
"""
from pathlib import Path
import pcbnew as p
P = Path(__file__).resolve().parents[1]; path = P / 'eda/P01.kicad_pcb'; b = p.LoadBoard(str(path))
mm = p.FromMM


def xy(x, y):
    return p.VECTOR2I(mm(x), mm(y))


net = {n.GetNetname().split('/')[-1]: n for n in b.GetNetInfo().NetsByNetcode().values()}


def tr(n, pts, w, layer):
    for a, c in zip(pts, pts[1:]):
        t = p.PCB_TRACK(b); t.SetStart(xy(*a)); t.SetEnd(xy(*c)); t.SetWidth(mm(w)); t.SetLayer(layer); t.SetNet(net[n]); t.SetLocked(True); b.Add(t)


F = p.F_Cu; B = p.B_Cu
# Battery input: J7 island -> D1, then under the HS1 envelope keepout (y <= 31.3) into the bay.
tr('BAT_FUSED', [(15, 31.5), (12, 37)], 3, F)
tr('BAT_FUSED', [(17.5, 33.05), (48.5, 33.05)], 3, F)
tr('BAT_FUSED', [(48.5, 33.05), (48.5, 26.5)], 2.5, F)
tr('BAT_FUSED', [(48.5, 26.5), (52.46, 26.5), (52.46, 22.3)], 2, F)
tr('BAT_FUSED', [(52.46, 26.5), (57.54, 26.5), (57.54, 22.3)], 2, F)
# VS rail: D2 cathode -> Q1 source; F.Cu part stops at x=94 (well left of the HS2 bay).
# Each rail has a vertex at every stub and via: Freerouting treats a stub ending in the middle
# of a rail segment as unconnected and duplicates it (R2 first pass: 11 redundant segments).
tr('P01_VS', [(55, 22.3), (55, 34)], 2, B)
tr('P01_VS', [(55, 34), (70, 34), (94, 34), (110.54, 34)], 5, B)
tr('P01_VS', [(55, 34), (57.5, 34), (62.5, 34), (68.5, 34), (70, 34), (80.2, 34), (89.58, 34), (93.8, 34), (94, 34)], 5, F)
tr('P01_VS', [(110.54, 34), (110.54, 22.3)], 2, B)
for x in [55, 70, 94]:
    v = p.PCB_VIA(b); v.SetPosition(xy(x, 34)); v.SetWidth(mm(1.2)); v.SetDrill(mm(.6)); v.SetViaType(p.VIATYPE_THROUGH)
    v.SetLayerPair(F, B); v.SetNet(net['P01_VS']); v.SetLocked(True); b.Add(v)
# Short VS stubs straight up to the rail centre line (a rail vertex).
tr('P01_VS', [(57.5, 40.5), (57.5, 34)], 1, F)      # R1
tr('P01_VS', [(62.5, 39.8), (62.5, 34)], 1, F)      # C1
tr('P01_VS', [(68.5, 40.2), (68.5, 34)], 1, F)      # C2
tr('P01_VS', [(80.2, 40), (80.2, 34)], .8, F)       # D9 cathode
tr('P01_VS', [(89.58, 44), (89.58, 34)], 1, F)      # Q2 source (turn-off loop)
tr('P01_VS', [(93.8, 39.5), (93.8, 34)], .8, F)     # D4 cathode
tr('P01_VS', [(110.6, 40.8), (110.54, 34)], .8, B)  # R22 top, B.Cu under the DRAIN copper
# Q1 drain: straight down inside the bay between the C6 pads, then to LK1.
tr('P01_Q1_DRAIN', [(108, 22.3), (108, 35.5), (110, 35.5)], 2, F)
tr('P01_Q1_DRAIN', [(110, 35.5), (122, 35.5), (126, 36)], 4, F)
tr('VPROT', [(136, 36), (144, 36)], 5, F)
tr('VPROT', [(144, 36), (148, 32)], 2, F)
tr('VPROT', [(144, 36), (144, 44), (140, 48), (130, 48)], 3, F)
tr('VPROT', [(130, 48), (132, 54), (136, 58)], 1.5, F)
tr('VPROT', [(121, 44), (126, 44), (130, 48)], .6, B)  # C5 Miller branch to D3/VPROT force side
# Input/output power return on B.Cu (under the profiles is allowed: FR4 insulates).
tr('GND', [(32.32, 37), (28, 37), (22.62, 31)], 4, B)
tr('GND', [(22.62, 19), (31, 19), (34, 9.5), (146, 9.5), (153, 16.5), (153, 44), (150.32, 48)], 5, B)
tr('GND', [(153, 26.92), (148, 26.92)], 2, B)
# Probe branches terminate at the test pads and carry no load current (<= 5 mm).
tr('P01_VS', [(110.54, 22.3), (113.9, 25.6)], .5, F)
tr('P01_GATE', [(105.46, 22.3), (101.9, 25.6)], .5, F)
# Gate: Q1 G -> C6 (in the bay) -> spine down to D4 and R27 (turn-off path).
tr('P01_GATE', [(105.46, 22.3), (105.5, 30.0)], .8, F)
tr('P01_GATE', [(105.5, 30.0), (105.5, 48.5), (104.82, 48.5)], .8, F)
tr('P01_GATE', [(103.96, 39.5), (105.5, 39.5)], .8, F)
tr('P01_OFF_COL', [(87.04, 44), (87.04, 48.5)], 1, F)
# Kelvin sense branches of LK1, measurement only.
tr('P01_Q1_DRAIN', [(126, 36), (128.5, 39)], .4, F)
tr('VPROT', [(136, 36), (133.5, 39)], .4, F)


def zone(n, points, layer, priority=0, thermal=.5, gap=.3):
    z = p.ZONE(b); z.SetLayer(layer); z.SetNet(net[n]); z.SetAssignedPriority(priority)
    z.SetLocalClearance(mm(.3)); z.SetMinThickness(mm(.25)); z.SetPadConnection(p.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(mm(gap)); z.SetThermalReliefSpokeWidth(mm(thermal)); z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
    o = z.Outline(); o.NewOutline()
    for x, y in points:
        o.Append(mm(x), mm(y))
    b.Add(z)


for layer in [F, B]:
    zone('BAT_FUSED', [(10, 20.5), (19.5, 20.5), (19.5, 34), (10, 34)], layer, 10, 1.2)
nc = b.GetDesignSettings().m_NetSettings.GetDefaultNetclass(); nc.SetClearance(mm(.3)); nc.SetTrackWidth(mm(.5)); nc.SetViaDiameter(mm(1)); nc.SetViaDrill(mm(.5))
b.BuildConnectivity(); p.ZONE_FILLER(b).Fill(b.Zones()); p.SaveBoard(str(path), b)
assert p.ExportSpecctraDSN(b, str(P / 'routing/P01.dsn'))
print('R2 critical tracks locked; BAT thermal island filled; DSN exported.')
