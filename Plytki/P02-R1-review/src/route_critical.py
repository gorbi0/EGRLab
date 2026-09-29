"""P02 R1: explicit power paths before signal autorouting (all locked).
- VPROT input node is an F.Cu zone joining J1.1 (SUPPLY), J2.1 (VMOTOR, up to 5 A), TP1 and R9.1;
  the 5 A return J2.2 -> J1.2 runs in the B.Cu GND pour, kept free of tracks/vias by a rule area.
- Branches from the VPROT node: D1.1 (1.5 mm), J13.1 to R_CHARGE (1.0 mm), F4.1 to VSENSE (1.2 mm).
- Charge path J13.2 -> D2 anodes; HOLD_FUSED D2.K / D1.A2 -> F1.1; HOLD_STORE F1.2 -> bank rail
  (2.5 mm, vertex at every stub: R1, R6, C1..C3, TP3); bank negative rail on F.Cu (2.5 mm).
- VLOG_RES D1.K -> C4 -> F2.1 / F3.1 (1.5 mm); converter inputs 1.0 mm; 5V_SYS and 3V3_IO trunks
  and the LV rails (1.5 mm, 5V_SYS above the row, 3V3_IO below), vertex at every connector stub.
Divider top resistors sit at their sources (R6 on the bank rail, R9 in the VPROT zone), so every
long sense track is behind 267k/348k and a short there cannot discharge the bank through thin copper.
"""
from pathlib import Path
import pcbnew as p
P = Path(__file__).resolve().parents[1]; path = P / 'eda/P02.kicad_pcb'; b = p.LoadBoard(str(path))
mm = p.FromMM
F = p.F_Cu; B = p.B_Cu


def xy(x, y):
    return p.VECTOR2I(mm(x), mm(y))


def net(n):
    for cand in (n, '/' + n, '/MON/' + n):
        v = b.FindNet(cand)
        if v is not None and v.GetNetCode() > 0:
            return v
    raise KeyError(n)


def tr(n, pts, w, layer=F):
    for a, c in zip(pts, pts[1:]):
        t = p.PCB_TRACK(b); t.SetStart(xy(*a)); t.SetEnd(xy(*c)); t.SetWidth(mm(w)); t.SetLayer(layer)
        t.SetNet(net(n)); t.SetLocked(True); b.Add(t)


def zone(n, points, layer, priority=10, connection=p.ZONE_CONNECTION_FULL, name=''):
    z = p.ZONE(b); z.SetLayer(layer); z.SetNet(net(n)); z.SetAssignedPriority(priority); z.SetZoneName(name)
    z.SetLocalClearance(mm(.3)); z.SetMinThickness(mm(.25)); z.SetPadConnection(connection)
    z.SetThermalReliefGap(mm(.3)); z.SetThermalReliefSpokeWidth(mm(.6)); z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
    o = z.Outline(); o.NewOutline()
    for x, y in points:
        o.Append(mm(x), mm(y))
    b.Add(z); return z


def keepout(points, layers, name):
    z = p.ZONE(b); z.SetIsRuleArea(True); ls = p.LSET()
    for l in layers:
        ls.AddLayer(l)
    z.SetLayerSet(ls); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True); z.SetDoNotAllowZoneFills(False)
    z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False); z.SetZoneName(name)
    o = z.Outline(); o.NewOutline()
    for x, y in points:
        o.Append(mm(x), mm(y))
    b.Add(z)


# --- VPROT input node (J1.1 SUPPLY, J2.1 VMOTOR, TP1, R9.1) -----------------------------------
zone('VPROT', [(8.3, 30.8), (21.2, 30.8), (21.2, 48.3), (8.3, 48.3)], F, name='VPROT input node')
keepout([(1, 21), (21.8, 21), (21.8, 56), (1, 56)], [B], 'B.Cu GND return J2.2-J1.2 (no tracks/vias)')
tr('VPROT', [(20.5, 46), (24, 46)], 1.5)                                   # -> D1.1 (D_OR A1)
tr('VPROT', [(20.5, 31.5), (21.6, 30.4), (21.6, 21), (26, 17)], 1.0)        # -> J13.1 (R_CHARGE)
tr('VPROT', [(14.2, 47.5), (14.2, 65), (8, 69)], 1.2)                        # -> F4.1 (VSENSE fuse)

# --- charge path and HOLD_FUSED ------------------------------------------------------------------
tr('CHARGE_D', [(31.08, 17), (31.08, 21.2), (29.08, 21.2), (24, 21.2), (24, 25)], 1.0)
tr('CHARGE_D', [(29.08, 21.2), (29.08, 25)], 1.0)
tr('HOLD_FUSED', [(26.54, 25), (26.54, 28.8), (31.5, 33.76), (31.5, 46), (31.5, 50.6), (37.5, 50.6)], 1.5)
tr('HOLD_FUSED', [(29.08, 46), (31.5, 46)], 1.5)                             # D1.3 (D_OR A2)

# --- HOLD_STORE bank rail and bank negative rail ---------------------------------------------------
tr('HOLD_STORE', [(37.5, 28), (38, 27.5), (61.5, 27.5), (81, 27.5), (100.5, 27.5), (120, 27.5), (139.5, 27.5)], 2.5)
tr('HOLD_STORE', [(81, 27.5), (81, 29)], 1.0)                                # R1 bleeder
tr('HOLD_STORE', [(120, 27.5), (120, 29)], 0.6)                              # R6 bank divider top
tr('HOLD_STORE', [(38, 22.5), (37.5, 28)], 0.8)                              # TP3
tr('GND', [(61.5, 17.5), (100.5, 17.5), (139.5, 17.5)], 2.5)

# --- VLOG_RES and converter inputs -----------------------------------------------------------------
tr('VLOG_RES', [(26.54, 46), (26.54, 49.6), (25.5, 50.6), (25.5, 52)], 1.5)
tr('VLOG_RES', [(25.5, 52), (22, 55.5), (22, 60), (22, 76)], 1.5)
tr('VLOG_RES', [(25.5, 52), (21.5, 51.5)], 0.8)                              # TP2
tr('P02_VIN_DC5', [(44.6, 60), (46.6, 58), (55, 58), (62.5, 58)], 1.0)
tr('P02_VIN_DC33', [(44.6, 76), (46.6, 74), (55, 74), (62.5, 74)], 1.0)

# --- 5V_SYS: U1.3 -> C6 -> trunk x=66.5 -> LV rail y=99 (stubs to every J.1) -------------------------
LV = [48, 61, 74, 87, 100, 113, 126, 139]
tr('5V_SYS', [(55, 63.08), (61.5, 63.08), (62.5, 64), (66.5, 64), (66.5, 68.66), (66.5, 90), (66.5, 99)], 1.5)
tr('5V_SYS', [(66.5, 68.66), (68.5, 68.66)], 1.0)                            # R3.2
tr('5V_SYS', [(66.5, 64), (66.5, 52.46), (66.5, 47.5), (65, 46)], 0.8)       # up to C10.1 (U4 decoupling)
tr('5V_SYS', [(66.5, 52.46), (69, 52.46)], 0.8)                              # U4.2 VDD
tr('5V_SYS', [(66.5, 90), (62, 90)], 0.8)                                    # TP4
rail = sorted(set(LV + [66.5]))
tr('5V_SYS', [(x, 99) for x in rail], 1.5)
for x in LV:
    tr('5V_SYS', [(x, 99), (x, 104)], 1.2)

# --- 3V3_IO: U2.3 -> C8, trunk left of J3 -> LV rail y=115.5 (stubs to every J.3) ---------------------
tr('3V3_IO', [(55, 79.08), (56, 80), (62.5, 80)], 1.5)
tr('3V3_IO', [(55, 79.08), (55, 86), (54, 86), (43.4, 86), (43.4, 115.5)], 1.5)
tr('3V3_IO', [(54, 86), (54, 90)], 0.8)                                      # TP5
tr('3V3_IO', [(x, 115.5) for x in [43.4] + LV], 1.5)
for x in LV:
    tr('3V3_IO', [(x, 115.5), (x, 109.5)], 1.2)

nc = b.GetDesignSettings().m_NetSettings.GetDefaultNetclass(); nc.SetClearance(mm(.3)); nc.SetTrackWidth(mm(.5)); nc.SetViaDiameter(mm(1)); nc.SetViaDrill(mm(.5))
b.BuildConnectivity(); p.ZONE_FILLER(b).Fill(b.Zones()); p.SaveBoard(str(path), b)
(P / 'routing').mkdir(exist_ok=True)
assert p.ExportSpecctraDSN(b, str(P / 'routing/P02.dsn'))
print('P02 critical power paths locked; VPROT node zone filled; DSN exported.')
