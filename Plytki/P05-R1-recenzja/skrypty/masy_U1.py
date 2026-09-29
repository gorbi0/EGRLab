import pcbnew as p, math
b = p.LoadBoard('eda/P05.kicad_pcb')
b.BuildConnectivity()
def pos(v): return (p.ToMM(v.x), p.ToMM(v.y))
vias = [pos(t.GetPosition()) for t in b.GetTracks() if isinstance(t, p.PCB_VIA) and t.GetNetname() == 'GND']
u1 = next(f for f in b.GetFootprints() if f.GetReference() == 'U1')
for a in sorted(u1.Pads(), key=lambda a: int(a.GetNumber())):
    if a.GetNetname() != 'GND': continue
    q = pos(a.GetPosition()); d = min(math.dist(q, v) for v in vias)
    print(f'U1.{a.GetNumber():>2} {a.GetPinFunction()[:12]:12} ({q[0]:.2f},{q[1]:.2f}) nearest GND via {d:.1f} mm', 'zone-conn', a.GetZoneConnectionOverrides(None) if hasattr(a,'GetZoneConnectionOverrides') else '')
# F.Cu GND copper islands around U1: filled area of F.Cu GND zone within the U1 box
z = [z for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND' and z.IsOnLayer(p.F_Cu)][0]
ps = z.GetFilledPolysList(p.F_Cu)
box = p.SHAPE_POLY_SET(); box.NewOutline()
for x, y in [(99, 36), (118, 36), (118, 52), (99, 52)]: box.Append(p.FromMM(x), p.FromMM(y))
inter = p.SHAPE_POLY_SET(ps); inter.BooleanIntersection(box)
print('F.Cu GND pour pieces in 99-118 x 36-52:', inter.OutlineCount(), [round(inter.Outline(i).Area() / 1e12, 2) for i in range(inter.OutlineCount())])
