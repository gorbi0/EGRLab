"""P07 S1 (user decision 6.10, 4 layers): supply zones on In2.Cu after the routing (run_layout.py, last copper step). In2.Cu carries router
signals; the free area round them is filled with the local supplies in disjoint regions (REGIONS below; 6.10 evening layout). Nothing on In2 under the power block (rule area of
route_critical.py). Island removal: always (a piece stays only where a pad or via of its net touches it). Idempotent: old In2 zones of these
nets are replaced. Report: routing/inner-zones.json."""
from pathlib import Path
import pcbnew as p, json, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from board import NAME
P = Path(__file__).resolve().parents[1]; fn = P / f'eda/{NAME}.kicad_pcb'; mm = p.FromMM
from board import IN2_SUPPLY as REGIONS   # 6.10 evening: shared with prepare_routing.py (DSN planes)
b = p.LoadBoard(str(fn))
# 6.10 evening: no supply fill on In2 under the motor lanes (MOD_MP / T_EGR_P3 / T_EGR_P1 pours + 0.3 mm); signals may cross there.
# Made here, after the routing, because KiCad exports every rule area to the DSN as a router keepout. Idempotent (old one replaced).
LANE_NETS = ('MOD_MP', 'T_EGR_P3', 'T_EGR_P1'); NAME_R = 'In2: bez wylewek pod pasami silnika'
ZS = list(b.Zones())   # 7.10: one snapshot; iterating b.Zones() again after b.Remove() crashed KiCad (stale proxy) on the second run
gone = [z for z in ZS if z.GetIsRuleArea() and z.GetZoneName() == NAME_R]
for z in gone:
    b.Remove(z)
ZS = [z for z in ZS if all(z is not g for g in gone)]
lanes = p.SHAPE_POLY_SET()
for z in ZS:
    if not z.GetIsRuleArea() and z.IsOnLayer(p.F_Cu) and z.GetNetname().split('/')[-1] in LANE_NETS:
        lanes.BooleanAdd(z.Outline())
lanes.Inflate(mm(.7), p.CORNER_STRATEGY_CHAMFER_ALL_CORNERS, mm(.01)); lanes.Deflate(mm(.4), p.CORNER_STRATEGY_CHAMFER_ALL_CORNERS, mm(.01)); lanes.Simplify()
assert lanes.OutlineCount() >= 1, 'motor lane pours missing (route_critical.py)'
r3 = p.ZONE(b); r3.SetIsRuleArea(True); ls = p.LSET(); ls.AddLayer(p.In2_Cu); r3.SetLayerSet(ls); r3.SetDoNotAllowTracks(False); r3.SetDoNotAllowVias(False)
r3.SetDoNotAllowZoneFills(True); r3.SetDoNotAllowPads(False); r3.SetDoNotAllowFootprints(False); r3.SetZoneName(NAME_R)
o = r3.Outline()
for k in range(lanes.OutlineCount()):
    o.NewOutline(); src = lanes.Outline(k)
    for i in range(src.PointCount()):
        o.Append(src.CPoint(i).x, src.CPoint(i).y, o.OutlineCount() - 1)
b.Add(r3)
for z in [z for z in ZS if not z.GetIsRuleArea() and z.IsOnLayer(p.In2_Cu) and z.GetNetname() in REGIONS]:
    b.Remove(z)
for net, rects in REGIONS.items():   # 7.10: one zone per net (union of its rectangles; two touching zones of one net were a DRC zones_intersect)
    u = p.SHAPE_POLY_SET()
    for (x0, y0, x1, y1) in rects:
        one = p.SHAPE_POLY_SET(); one.NewOutline()
        for x, y in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]:
            one.Append(mm(x), mm(y))
        u.BooleanAdd(one)
    u.Simplify()
    z = p.ZONE(b); z.SetLayer(p.In2_Cu); z.SetNet(b.FindNet(net)); z.SetZoneName(f'{net} In2.Cu'); z.SetAssignedPriority(1)
    z.SetLocalClearance(mm(.3)); z.SetMinThickness(mm(.25)); z.SetPadConnection(p.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(mm(.25)); z.SetThermalReliefSpokeWidth(mm(.4)); z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
    o = z.Outline()
    for k in range(u.OutlineCount()):
        o.NewOutline(); src = u.Outline(k)
        for i in range(src.PointCount()):
            o.Append(src.CPoint(i).x, src.CPoint(i).y, o.OutlineCount() - 1)
    b.Add(z)
p.ZONE_FILLER(b).Fill(b.Zones()); b.BuildConnectivity(); p.SaveBoard(str(fn), b)
rep = {}
for z in b.Zones():
    if not z.GetIsRuleArea() and z.IsOnLayer(p.In2_Cu):
        rep[z.GetNetname()] = round(rep.get(z.GetNetname(), 0) + z.GetFilledPolysList(p.In2_Cu).Area() / 1e12, 1)
(P / 'routing/inner-zones.json').write_text(json.dumps(rep, indent=1) + '\n')
print('In2.Cu supply zones (mm2 filled):', rep)
