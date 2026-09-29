import pcbnew, math, collections, sys
b = pcbnew.LoadBoard(sys.argv[1]); MM = pcbnew.ToMM
L = {pcbnew.F_Cu: 'F', pcbnew.B_Cu: 'B'}
per = collections.defaultdict(lambda: {'len': collections.Counter(), 'w': set(), 'vias': 0, 'segs': 0})
for t in b.GetTracks():
    n = t.GetNetname()
    if t.Type() == pcbnew.PCB_VIA_T:
        per[n]['vias'] += 1
        continue
    per[n]['len'][L.get(t.GetLayer(), '?')] += MM(t.GetLength())
    per[n]['w'].add(round(MM(t.GetWidth()), 3)); per[n]['segs'] += 1
print(f"{'net':32s} {'F mm':>7s} {'B mm':>7s} {'vias':>4s} widths")
for n, d in sorted(per.items(), key=lambda kv: -(sum(kv[1]['len'].values()))):
    print(f"{n:32s} {d['len']['F']:7.1f} {d['len']['B']:7.1f} {d['vias']:4d} {sorted(d['w'])}")
print("\nZONES")
for z in b.Zones():
    lays = [L.get(l, str(l)) for l in z.GetLayerSet().Seq()]
    area = 0.0
    for l in z.GetLayerSet().Seq():
        if z.HasFilledPolysForLayer(l):
            area += z.GetFilledPolysList(l).Area() / 1e12
    print(f"net={z.GetNetname():22s} layers={lays} prio={z.GetAssignedPriority()} minw={MM(z.GetMinThickness()):.2f} clr={MM(z.GetLocalClearance() or 0):.2f} "
          f"conn={z.GetPadConnection()} gap={MM(z.GetThermalReliefGap()):.2f} spoke={MM(z.GetThermalReliefSpokeWidth()):.2f} filled_mm2={area:.0f} keepout={z.GetIsRuleArea()} "
          f"bbox={tuple(round(MM(v),1) for v in (z.GetBoundingBox().GetX(), z.GetBoundingBox().GetY(), z.GetBoundingBox().GetRight(), z.GetBoundingBox().GetBottom()))}")
