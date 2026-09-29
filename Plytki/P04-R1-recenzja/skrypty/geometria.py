"""Recenzja P04-R1: rozmieszczenie, długości sieci, wyspy GND, pady z pełnym połączeniem.
Uruchomienie (Python z KiCad 10): python geometria.py ../../P04-R1-review/eda/P04.kicad_pcb"""
import pcbnew as p, collections, math, sys
b = p.LoadBoard(sys.argv[1]); b.BuildConnectivity()
def mm(v): return round(p.ToMM(v), 2)
print('footprints:')
for f in sorted(b.GetFootprints(), key=lambda f: f.GetReference()):
    r = f.GetReference()
    if r[0] in 'JUQC' or r in ('LED1', 'R1', 'R4', 'R5'):
        bb = f.GetCourtyard(p.F_CrtYd).BBox() if (f.BuildCourtyardCaches() or True) and f.GetCourtyard(p.F_CrtYd).OutlineCount() else f.GetBoundingBox()
        print(f'  {r:5s} {f.GetFPIDAsString().split(":")[-1][:40]:40s} at ({mm(f.GetPosition().x)},{mm(f.GetPosition().y)}) rot {f.GetOrientationDegrees():6.1f} crtyd x {mm(bb.GetLeft())}..{mm(bb.GetRight())} y {mm(bb.GetTop())}..{mm(bb.GetBottom())}')
L = collections.defaultdict(float); vias = collections.Counter(); widths = collections.defaultdict(set)
for t in b.GetTracks():
    n = t.GetNetname().split('/')[-1]
    if isinstance(t, p.PCB_VIA): vias[n] += 1
    else: L[n] += p.ToMM(t.GetLength()); widths[n].add(round(p.ToMM(t.GetWidth()), 2))
for n in ['SAFE_N', 'STOP_NC_OUT', '3V3_IO', 'GND', 'PWM_OUT', 'PWM_P04', 'PWM', 'HEARTBEAT', 'HEARTBEAT_P04', 'ARM_CONTACT', 'ARM_BUTTON_N', 'ARM_CLK', 'WD_RC', 'WD_C', 'SAFE_OK', 'MOTOR_PERMIT', '5V_SYS', 'PG_SEND']:
    print(f'  net {n:14s} track {L[n]:7.1f} mm vias {vias[n]} widths {sorted(widths[n])}')
for L_ in (p.F_Cu, p.B_Cu):
    areas = []
    for z in b.Zones():
        if z.GetIsRuleArea() or z.GetNetname() != 'GND' or not z.IsOnLayer(L_): continue
        ps = z.GetFilledPolysList(L_)
        for i in range(ps.OutlineCount()):
            s1 = p.SHAPE_POLY_SET(); s1.AddOutline(ps.Outline(i))
            for h in range(ps.HoleCount(i)): s1.AddHole(ps.Hole(i, h))
            areas.append(s1.Area() / 1e12)
    areas.sort(reverse=True)
    print(' ', b.GetLayerName(L_), 'GND islands', len(areas), 'total', round(sum(areas)), 'largest %', round(100 * areas[0] / sum(areas), 1) if areas else 0, 'fill % of board', round(100 * sum(areas) / (160 * 120), 1))
print('rule areas:', [(z.GetZoneName(), [b.GetLayerName(l) for l in z.GetLayerSet().Seq()]) for z in b.Zones() if z.GetIsRuleArea()])
print('full-connection pads:', sorted(f"{f.GetReference()}.{a.GetNumber()}" for f in b.GetFootprints() for a in f.Pads() if a.GetLocalZoneConnection() == p.ZONE_CONNECTION_FULL))
