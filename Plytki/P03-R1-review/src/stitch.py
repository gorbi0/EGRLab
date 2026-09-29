"""P03 R1: GND stitching vias between the two pours (run after cleanup.py, before the silkscreen).
The routed board leaves both GND pours split into islands that meet only at THT GND pads, which gives the fast
ADC/SPI lines long return paths. On a 10 mm grid (offset half a step on alternate rows) a via 0.8/0.4 mm is placed
where its centre lies inside the filled GND of BOTH layers with at least 0.7 mm to the fill edge (the fill already
keeps 0.3 mm from other nets), outside every rule area and every courtyard (not under parts or their silk), and at
least 3 mm from any pad or other via. Vias are locked,
so a later clean-up keeps them. The board is refilled and saved; islands before/after go to routing/stitching.json.
"""
from pathlib import Path
import pcbnew as p, json, math
P = Path(__file__).resolve().parents[1]; fn = P / 'eda/P03.kicad_pcb'; b = p.LoadBoard(str(fn)); mm = p.FromMM
GRID, EDGE_MIN, PAD_MIN = 10.0, .7, 3.0


def xy(x, y):
    return p.VECTOR2I(mm(x), mm(y))


def islands():
    return {b.GetLayerName(L): sum(z.GetFilledPolysList(L).OutlineCount() for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND' and z.IsOnLayer(L))
            for L in (p.F_Cu, p.B_Cu)}


gnd = b.FindNet('GND'); p.ZONE_FILLER(b).Fill(b.Zones()); before = islands()
fills = {L: [z.GetFilledPolysList(L) for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND' and z.IsOnLayer(L)] for L in (p.F_Cu, p.B_Cu)}
rules = [z for z in b.Zones() if z.GetIsRuleArea()]
yards = []
for f in b.GetFootprints():
    f.BuildCourtyardCaches(); yards.append(f.GetCourtyard(p.F_CrtYd))
obst = [(p.ToMM(a.GetPosition().x), p.ToMM(a.GetPosition().y)) for f in b.GetFootprints() for a in f.Pads()]
obst += [(p.ToMM(t.GetPosition().x), p.ToMM(t.GetPosition().y)) for t in b.GetTracks() if isinstance(t, p.PCB_VIA)]


def inside(L, q):
    """Centre and 16 points on a circle of EDGE_MIN radius inside one filled GND polygon of layer L."""
    pts = [xy(*q)] + [xy(q[0] + EDGE_MIN * math.cos(k * math.pi / 8), q[1] + EDGE_MIN * math.sin(k * math.pi / 8)) for k in range(16)]
    return any(all(ps.Contains(v) for v in pts) for ps in fills[L])


added = []
for j in range(int(120 / GRID) + 1):
    for i in range(int(160 / GRID) + 1):
        q = (i * GRID + (GRID / 2 if j % 2 else 0), j * GRID)
        if not (2 < q[0] < 158 and 2 < q[1] < 118):
            continue
        if any(z.Outline().Contains(xy(*q)) for z in rules) or any(math.dist(q, o) < PAD_MIN for o in obst) or any(c.Contains(xy(*q)) for c in yards):
            continue
        if inside(p.F_Cu, q) and inside(p.B_Cu, q):
            v = p.PCB_VIA(b); v.SetPosition(xy(*q)); v.SetWidth(mm(.8)); v.SetDrill(mm(.4)); v.SetViaType(p.VIATYPE_THROUGH)
            v.SetLayerPair(p.F_Cu, p.B_Cu); v.SetNet(gnd); v.SetLocked(True); b.Add(v); added.append(q); obst.append(q)
p.ZONE_FILLER(b).Fill(b.Zones()); after = islands()
p.SaveBoard(str(fn), b, True)
(P / 'routing/stitching.json').write_text(json.dumps({'grid_mm': GRID, 'vias': len(added), 'islands_before': before, 'islands_after': after,
                                                       'positions': [[round(x, 2), round(y, 2)] for x, y in added]}, indent=1) + '\n')
print('GND stitching:', len(added), 'vias; pour islands', before, '->', after)
