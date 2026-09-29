"""P04 R2 (review R4-06): GND stitching vias between the two pours (run after cleanup.py, before the silkscreen).
R1 had 2 GND vias: F.Cu 28 islands (largest 88 %), B.Cu 39 (largest 77 %), joined mostly through THT pads.
On a 10 mm grid (offset half a step on alternate rows) a via 0.8/0.4 mm is placed
where its centre lies inside the filled GND of BOTH layers with at least 0.7 mm to the fill edge (the fill already
keeps 0.3 mm from other nets), outside every rule area and every courtyard (not under parts or their silk), and at
least 3 mm from any pad or other via. Vias are locked,
so a later clean-up keeps them. The board is refilled and saved; islands before/after go to routing/stitching.json.
Second stage (R2, island rescue): pour pieces that tracks enclose on one layer are removed by KiCad as isolated islands
(white areas on the copper pages). With island removal switched off for one fill, every such piece of at least
RESCUE_MIN mm2 gets one via where the piece has room (0.7 mm to its edge) and the kept pour of the other layer also
has room (same margin), outside rule areas and courtyards, at least 1.5 mm from pads and vias. The via ties the piece to
a pour that is already connected, so the normal fill keeps it; pieces that fail these conditions stay removed.
"""
from pathlib import Path
import pcbnew as p, json, math
P = Path(__file__).resolve().parents[1]; fn = P / 'eda/P04.kicad_pcb'; b = p.LoadBoard(str(fn)); mm = p.FromMM
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
