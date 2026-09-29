"""P06-R1 GND stitching. Add vias where both filled layers have clearance, outside rule areas and courtyards. A second pass ties otherwise removed islands to an already connected pour. All candidates undergo native DRC; the final geometric GND graph must have exactly one connected component."""
from pathlib import Path
import pcbnew as p, json, math
P = Path(__file__).resolve().parents[1]; fn = P / 'eda/P06.kicad_pcb'; b = p.LoadBoard(str(fn)); mm = p.FromMM
GRID, EDGE_MIN, PAD_MIN, RESCUE_MIN, RESCUE_PAD = 10.0, .7, 3.0, 10.0, 1.5


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
for j in range(int(100 / GRID) + 1):
    for i in range(int(120 / GRID) + 1):
        q = (i * GRID + (GRID / 2 if j % 2 else 0), j * GRID)
        if not (2 < q[0] < 118 and 2 < q[1] < 98):
            continue
        if any(z.Outline().Contains(xy(*q)) for z in rules) or any(math.dist(q, o) < PAD_MIN for o in obst) or any(c.Contains(xy(*q)) for c in yards):
            continue
        if inside(p.F_Cu, q) and inside(p.B_Cu, q):
            v = p.PCB_VIA(b); v.SetPosition(xy(*q)); v.SetWidth(mm(.8)); v.SetDrill(mm(.4)); v.SetViaType(p.VIATYPE_THROUGH)
            v.SetLayerPair(p.F_Cu, p.B_Cu); v.SetNet(gnd); v.SetLocked(True); b.Add(v); added.append(q); obst.append(q)
p.ZONE_FILLER(b).Fill(b.Zones()); after = islands()
# ---- stage 2: rescue enclosed pour pieces ----
pours = [z for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND']


def pieces(L):
    out = []
    for z in pours:
        if not z.IsOnLayer(L):
            continue
        ps = z.GetFilledPolysList(L)
        for i in range(ps.OutlineCount()):
            one = p.SHAPE_POLY_SET(); one.AddOutline(ps.Outline(i))
            for h in range(ps.HoleCount(i)):
                one.AddHole(ps.Hole(i, h))
            out.append(one)
    return out


def area(L):
    return round(sum(q.Area() for q in pieces(L)) / 1e12, 1)


kept = {L: pieces(L) for L in (p.F_Cu, p.B_Cu)}; area_before = {b.GetLayerName(L): area(L) for L in (p.F_Cu, p.B_Cu)}
for z in pours:
    z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_NEVER)
p.ZONE_FILLER(b).Fill(b.Zones()); raw = {L: pieces(L) for L in (p.F_Cu, p.B_Cu)}
for z in pours:
    z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)


def disc(q):
    return [xy(*q)] + [xy(q[0] + EDGE_MIN * math.cos(k * math.pi / 8), q[1] + EDGE_MIN * math.sin(k * math.pi / 8)) for k in range(16)]


rescued = []
for L, O in ((p.F_Cu, p.B_Cu), (p.B_Cu, p.F_Cu)):
    for piece in sorted(raw[L], key=lambda q: (p.ToMM(q.BBox().GetLeft()), p.ToMM(q.BBox().GetTop()), q.Area())):  # geometric order (clean rebuild)
        if piece.Area() / 1e12 < RESCUE_MIN:
            continue
        bb = piece.BBox(); x0, y0, x1, y1 = p.ToMM(bb.GetLeft()), p.ToMM(bb.GetTop()), p.ToMM(bb.GetRight()), p.ToMM(bb.GetBottom())
        pts = [(x0 + i * .5, y0 + j * .5) for i in range(int((x1 - x0) / .5) + 1) for j in range(int((y1 - y0) / .5) + 1)]
        inside = [q for q in pts if piece.Contains(xy(*q))]
        if not inside or any(k.Contains(xy(*inside[0])) for k in kept[L]):
            continue  # piece survives the normal fill: nothing to rescue
        c = ((x0 + x1) / 2, (y0 + y1) / 2)
        for q in sorted(inside, key=lambda q: math.dist(q, c)):
            d = disc(q)
            if not all(piece.Contains(v) for v in d) or not any(all(k.Contains(v) for v in d) for k in kept[O]):
                continue
            if any(z.Outline().Contains(xy(*q)) for z in rules) or any(cy.Contains(xy(*q)) for cy in yards) or any(math.dist(q, o) < RESCUE_PAD for o in obst):
                continue
            v = p.PCB_VIA(b); v.SetPosition(xy(*q)); v.SetWidth(mm(.8)); v.SetDrill(mm(.4)); v.SetViaType(p.VIATYPE_THROUGH)
            v.SetLayerPair(p.F_Cu, p.B_Cu); v.SetNet(gnd); v.SetLocked(True); b.Add(v); obst.append(q)
            rescued.append({'layer': b.GetLayerName(L), 'at': [round(q[0], 2), round(q[1], 2)], 'piece_mm2': round(piece.Area() / 1e12, 1)}); break
p.ZONE_FILLER(b).Fill(b.Zones()); final = islands(); area_after = {b.GetLayerName(L): area(L) for L in (p.F_Cu, p.B_Cu)}
p.SaveBoard(str(fn), b, True)
(P / 'routing/stitching.json').write_text(json.dumps({'grid_mm': GRID, 'vias': len(added), 'islands_before': before, 'islands_after': after,
                                                       'rescue_vias': len(rescued), 'rescued': rescued, 'islands_final': final,
                                                       'pour_mm2_before_rescue': area_before, 'pour_mm2_after_rescue': area_after,
                                                       'positions': [[round(x, 2), round(y, 2)] for x, y in added]}, indent=1) + '\n')
print('GND stitching:', len(added), 'grid vias, pour islands', before, '->', after, '| rescue:', len(rescued), 'vias, pour mm2', area_before, '->', area_after, 'islands', final)
