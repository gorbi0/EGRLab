"""P07 S1 (user decision 6.10, 4 layers): supply zones on In2.Cu after the routing (run_layout.py, last copper step). In2.Cu carries router
signals; the free area round them is filled with the local supplies in three disjoint regions: 3V3A_P07 under the ADC chain (top middle),
5VA_P07 under INA240 / OC window / LDO (bottom middle), 3V3_IO under the logic (right). Nothing on In2 under the power block (rule area of
route_critical.py). Island removal: always (a piece stays only where a pad or via of its net touches it). Idempotent: old In2 zones of these
nets are replaced. Report: routing/inner-zones.json."""
from pathlib import Path
import pcbnew as p, json, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from board import NAME
P = Path(__file__).resolve().parents[1]; fn = P / f'eda/{NAME}.kicad_pcb'; mm = p.FromMM
REGIONS = {'3V3A_P07': (37.5, 14.8, 66.5, 51.0), '5VA_P07': (34.0, 51.5, 66.5, 95.0), '3V3_IO': (67.0, 14.8, 106.0, 95.0)}
b = p.LoadBoard(str(fn))
for z in list(b.Zones()):
    if not z.GetIsRuleArea() and z.IsOnLayer(p.In2_Cu) and z.GetNetname() in REGIONS:
        b.Remove(z)
for net, (x0, y0, x1, y1) in REGIONS.items():
    z = p.ZONE(b); z.SetLayer(p.In2_Cu); z.SetNet(b.FindNet(net)); z.SetZoneName(f'{net} In2.Cu'); z.SetAssignedPriority(1)
    z.SetLocalClearance(mm(.3)); z.SetMinThickness(mm(.25)); z.SetPadConnection(p.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(mm(.25)); z.SetThermalReliefSpokeWidth(mm(.4)); z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
    o = z.Outline(); o.NewOutline()
    for x, y in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]:
        o.Append(mm(x), mm(y))
    b.Add(z)
p.ZONE_FILLER(b).Fill(b.Zones()); b.BuildConnectivity(); p.SaveBoard(str(fn), b)
rep = {z.GetNetname(): round(z.GetFilledPolysList(p.In2_Cu).Area() / 1e12, 1) for z in b.Zones() if not z.GetIsRuleArea() and z.IsOnLayer(p.In2_Cu)}
(P / 'routing/inner-zones.json').write_text(json.dumps(rep, indent=1) + '\n')
print('In2.Cu supply zones (mm2 filled):', rep)
