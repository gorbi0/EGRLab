"""P03 R6 (from P02 R4, which took it from P04 R2; reference GND pad J_BP2.1 instead of P02 J1.2): GND stitching vias between the two pours (run after cleanup.py, before the silkscreen).
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
Third stage (P02 R4, 29.09, klasa L): a kept pour piece can carry GND pads and still have no copper path to the rest of GND
(one such B.Cu piece under U9/C27 in the first class-L runs, and one in the router attempt that closed all signal nets).
GND pads that KiCad connectivity does not join to J1.2 (pack GND) mark such pieces; each gets one via where the piece has
room and a pour piece of the other layer that is joined to J1.2 has room (same margins as the rescue).
Review 2.10 (P06 R2 F2, P05 R3 MAJOR-1 / -2): stage 4 places the targeted GND vias of board.EXTRA_GND_VIAS (capacitor GND pads, IC GND pins).
Klasa L (29.09): the grid covers the whole board (x < 158; the 2/3 pilot stopped at 104.5) and vias keep out of the
courtyards of the parts on the bottom too.
"""
from pathlib import Path
import pcbnew as p, json, math
P = Path(__file__).resolve().parents[1]
from board import NAME, GND_REF
try:
    from board import EXTRA_GND_VIAS   # review 2.10 (P06 R2): targeted GND vias, stage 4
except ImportError:
    EXTRA_GND_VIAS = []
from build_board import W as BW, Hh as BH
fn = P / f'eda/{NAME}.kicad_pcb'; b = p.LoadBoard(str(fn)); mm = p.FromMM
GRID, EDGE_MIN, PAD_MIN, RESCUE_MIN, RESCUE_PAD = 10.0, .7, 3.0, 10.0, 1.5


def xy(x, y):
    return p.VECTOR2I(mm(x), mm(y))


def islands():
    return {b.GetLayerName(L): sum(z.GetFilledPolysList(L).OutlineCount() for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND' and z.IsOnLayer(L))
            for L in (p.F_Cu, p.B_Cu)}


# 30.09: one release run found no GND pours here (204 unconnected, cause not reproduced); stop loudly instead of stitching nothing
assert sum(1 for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND') >= 2, 'GND pours missing (import_routing.py makes them)'
# P07 S1 (6.10, 4 layers): a new GND via must also keep clear of the In2.Cu copper of other nets (router tracks / vias / THT pads)
_inner = p.SHAPE_POLY_SET()
for _t in b.GetTracks():   # 7.10: tracks / vias of other nets on EVERY copper layer (a rescue via accepted through In1 shorted F.Cu tracks)
    if _t.GetNetname() == 'GND':
        continue
    for _L in (p.F_Cu, p.In2_Cu, p.B_Cu):
        if _t.IsOnLayer(_L):
            _s = p.SHAPE_POLY_SET(); _t.TransformShapeToPolygon(_s, _L, mm(.25 + .45 + .05), mm(.01), p.ERROR_OUTSIDE); _inner.BooleanAdd(_s)
for _f in b.GetFootprints():   # 7.10: pads of other nets on the outer layers too (RESCUE_PAD from the pad centre let a via touch a 1206 pad end)
    for _a in _f.Pads():
        for _L in (p.F_Cu, p.B_Cu):
            if _a.GetNetname() != 'GND' and _a.IsOnLayer(_L):
                _s = p.SHAPE_POLY_SET(); _a.TransformShapeToPolygon(_s, _L, mm(.25 + .45 + .05), mm(.01), p.ERROR_OUTSIDE); _inner.BooleanAdd(_s)
for _f in b.GetFootprints():
    for _a in _f.Pads():
        if _a.GetNetname() != 'GND' and _a.IsOnLayer(p.In2_Cu):
            _s = p.SHAPE_POLY_SET(); _a.TransformShapeToPolygon(_s, p.In2_Cu, mm(.25 + .45 + .05), mm(.01), p.ERROR_OUTSIDE); _inner.BooleanAdd(_s)


def blocked_inner(q):
    return _inner.OutlineCount() > 0 and _inner.Contains(p.VECTOR2I(mm(q[0]), mm(q[1])))
gnd = b.FindNet('GND'); p.ZONE_FILLER(b).Fill(b.Zones()); before = islands()
fills = {L: [z.GetFilledPolysList(L) for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND' and z.IsOnLayer(L)] for L in (p.F_Cu, p.B_Cu)}
rules = [z for z in b.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowVias()]   # P07 S1: the In2 area under the power block allows vias
yards = []
for f in b.GetFootprints():
    f.BuildCourtyardCaches(); yards.append(f.GetCourtyard(p.F_CrtYd)); yards.append(f.GetCourtyard(p.B_CrtYd))
obst = [(p.ToMM(a.GetPosition().x), p.ToMM(a.GetPosition().y)) for f in b.GetFootprints() for a in f.Pads()]
obst += [(p.ToMM(t.GetPosition().x), p.ToMM(t.GetPosition().y)) for t in b.GetTracks() if isinstance(t, p.PCB_VIA)]


def inside(L, q):
    """Centre and 16 points on a circle of EDGE_MIN radius inside one filled GND polygon of layer L."""
    pts = [xy(*q)] + [xy(q[0] + EDGE_MIN * math.cos(k * math.pi / 8), q[1] + EDGE_MIN * math.sin(k * math.pi / 8)) for k in range(16)]
    return any(all(ps.Contains(v) for v in pts) for ps in fills[L])


added = []
for j in range(int(BH / GRID) + 1):
    for i in range(int(BW / GRID) + 1):
        q = (i * GRID + (GRID / 2 if j % 2 else 0), j * GRID)
        if not (2 < q[0] < BW - 2 and 2 < q[1] < BH - 2):
            continue
        if (any(z.Outline().Contains(xy(*q)) for z in rules) or blocked_inner(q)) or any(math.dist(q, o) < PAD_MIN for o in obst) or any(c.Contains(xy(*q)) for c in yards):
            continue
        if inside(p.F_Cu, q) and inside(p.B_Cu, q):
            v = p.PCB_VIA(b); v.SetPosition(xy(*q)); v.SetWidth(mm(.9)); v.SetDrill(mm(.4)); v.SetViaType(p.VIATYPE_THROUGH)
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


def in1_main():
    """P07 S1 (6.10, 4 layers): the largest In1.Cu GND fill piece (the plane). A GND via standing inside it joins the plane, so an outer
    pour piece needs only room for a via there, not on the other outer layer."""
    if b.GetCopperLayerCount() < 4:
        return []
    q = pieces(p.In1_Cu); return [max(q, key=lambda x: x.Area())] if q else []


kept = {L: pieces(L) for L in (p.F_Cu, p.B_Cu)}; IN1 = in1_main(); area_before = {b.GetLayerName(L): area(L) for L in (p.F_Cu, p.B_Cu)}
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
            if not all(piece.Contains(v) for v in d) or not any(all(k.Contains(v) for v in d) for k in kept[O] + IN1):
                continue
            if (any(z.Outline().Contains(xy(*q)) for z in rules) or blocked_inner(q)) or any(cy.Contains(xy(*q)) for cy in yards) or any(math.dist(q, o) < RESCUE_PAD for o in obst):
                continue
            v = p.PCB_VIA(b); v.SetPosition(xy(*q)); v.SetWidth(mm(.9)); v.SetDrill(mm(.4)); v.SetViaType(p.VIATYPE_THROUGH)
            v.SetLayerPair(p.F_Cu, p.B_Cu); v.SetNet(gnd); v.SetLocked(True); b.Add(v); obst.append(q)
            rescued.append({'layer': b.GetLayerName(L), 'at': [round(q[0], 2), round(q[1], 2)], 'piece_mm2': round(piece.Area() / 1e12, 1)}); break
p.ZONE_FILLER(b).Fill(b.Zones())
# ---- stage 3: kept pieces with GND pads but no path to the pack GND (J1.2) ----


def main_items():
    b.BuildConnectivity(); con = b.GetConnectivity()
    ref = next(a for f in b.GetFootprints() if f.GetReference() == GND_REF[0] for a in f.Pads() if a.GetNumber() == GND_REF[1] and a.GetNetname() == 'GND')
    ids = {x.m_Uuid.AsString() for x in con.GetConnectedItems(ref)} | {ref.m_Uuid.AsString()}
    pads = [a for f in b.GetFootprints() for a in f.Pads() if a.GetNetname() == 'GND']
    copper = pads + [t for t in b.GetTracks() if t.GetNetname() == 'GND']
    return [x for x in copper if x.m_Uuid.AsString() in ids], [a for a in pads if a.m_Uuid.AsString() not in ids]


def touches(piece, item, L):
    if (isinstance(item, p.PAD) and not item.IsOnLayer(L)) or (not isinstance(item, (p.PAD, p.PCB_VIA)) and item.GetLayer() != L):
        return False
    sh = p.SHAPE_POLY_SET(); item.TransformShapeToPolygon(sh, L, mm(.03), mm(.01), p.ERROR_OUTSIDE)
    if not sh.BBox().Intersects(piece.BBox()):
        return False
    t = p.SHAPE_POLY_SET(piece); t.BooleanIntersection(sh); return t.OutlineCount() > 0


tied = []
for _ in range(3):
    good, orphans = main_items()
    if not orphans:
        break
    pcs = {L: pieces(L) for L in (p.F_Cu, p.B_Cu)}
    joined = {L: [q for q in pcs[L] if any(touches(q, x, L) for x in good)] for L in (p.F_Cu, p.B_Cu)}
    progress = False
    for a in sorted(orphans, key=lambda a: (a.GetParentFootprint().GetReference(), a.GetNumber())):
        ax, ay = p.ToMM(a.GetPosition().x), p.ToMM(a.GetPosition().y); done = False
        for L, O in ((p.F_Cu, p.B_Cu), (p.B_Cu, p.F_Cu)):
            for piece in [q for q in pcs[L] if touches(q, a, L)]:
                bb = piece.BBox(); x0, y0, x1, y1 = p.ToMM(bb.GetLeft()), p.ToMM(bb.GetTop()), p.ToMM(bb.GetRight()), p.ToMM(bb.GetBottom())
                pts = sorted(((x0 + i * .25, y0 + j * .25) for i in range(int((x1 - x0) / .25) + 1) for j in range(int((y1 - y0) / .25) + 1)),
                             key=lambda q: math.dist(q, (ax, ay)))
                for q in pts:
                    d = disc(q)
                    if not all(piece.Contains(v) for v in d) or not any(all(k.Contains(v) for v in d) for k in joined[O] + in1_main()):
                        continue
                    if (any(z.Outline().Contains(xy(*q)) for z in rules) or blocked_inner(q)) or any(cy.Contains(xy(*q)) for cy in yards) or any(math.dist(q, o) < RESCUE_PAD for o in obst):
                        continue
                    v = p.PCB_VIA(b); v.SetPosition(xy(*q)); v.SetWidth(mm(.9)); v.SetDrill(mm(.4)); v.SetViaType(p.VIATYPE_THROUGH)
                    v.SetLayerPair(p.F_Cu, p.B_Cu); v.SetNet(gnd); v.SetLocked(True); b.Add(v); obst.append(q)
                    tied.append({'pad': f'{a.GetParentFootprint().GetReference()}.{a.GetNumber()}', 'layer': b.GetLayerName(L), 'at': [round(q[0], 2), round(q[1], 2)]})
                    done = progress = True; break
                if done:
                    break
            if done:
                break
        if done:
            break   # one via per round: the next round sees the joined piece
    p.ZONE_FILLER(b).Fill(b.Zones())
    if not progress:
        break
# ---- stage 4 (review 2.10, F2): targeted GND vias (board.EXTRA_GND_VIAS) ----
# ('pad', ref, num, r): nearest spot within r mm of the pad centre inside the pour piece the pad sits in (its layer) and inside the
# other layer's pour; ('at', x, y, r): nearest spot within r mm inside both pours. Margin 0.55 mm to the fill edge (the fill keeps the
# clearance to other nets), >= 0.6 mm from any pad (no via in a pad), hole to hole >= 0.3 mm, outside rule areas; courtyards allowed
# (the vias are tented). Idempotent: a target that already has a GND via in reach (same piece for 'pad') gets none.
EM = .55
targeted = []


def disc_r(q, r):
    return [xy(*q)] + [xy(q[0] + r * math.cos(k * math.pi / 8), q[1] + r * math.sin(k * math.pi / 8)) for k in range(16)]


if EXTRA_GND_VIAS and '--targeted' in __import__('sys').argv:   # run_layout.py: only in the call after the completion planner
    padpolys = []
    for fp_ in b.GetFootprints():
        for a in fp_.Pads():
            for L in (p.F_Cu, p.B_Cu):
                if a.IsOnLayer(L):
                    sh = p.SHAPE_POLY_SET(); a.TransformShapeToPolygon(sh, L, mm(.6), mm(.01), p.ERROR_OUTSIDE); padpolys.append(sh)
    holes = [(p.ToMM(a.GetPosition().x), p.ToMM(a.GetPosition().y), p.ToMM(a.GetDrillSize().x) / 2) for fp_ in b.GetFootprints() for a in fp_.Pads() if a.GetDrillSize().x > 0]
    holes += [(p.ToMM(t.GetPosition().x), p.ToMM(t.GetPosition().y), p.ToMM(t.GetDrillValue()) / 2) for t in b.GetTracks() if isinstance(t, p.PCB_VIA)]
    pcs = {L: pieces(L) for L in (p.F_Cu, p.B_Cu)}
    gvias = [t for t in b.GetTracks() if isinstance(t, p.PCB_VIA) and t.GetNetname() == 'GND']
    for tg in EXTRA_GND_VIAS:
        if tg[0] == 'pad':
            _, ref, num, rad = tg; a = next(q for fp_ in b.GetFootprints() if fp_.GetReference() == ref for q in fp_.Pads() if q.GetNumber() == num)
            assert a.GetNetname() == 'GND', (ref, num)
            c = (p.ToMM(a.GetPosition().x), p.ToMM(a.GetPosition().y)); L = p.B_Cu if a.IsOnLayer(p.B_Cu) and not a.IsOnLayer(p.F_Cu) else p.F_Cu
            O = p.F_Cu if L == p.B_Cu else p.B_Cu; own = [q for q in pcs[L] if touches(q, a, L)]; name = f'{ref}.{num}'
        else:
            _, x, y, rad = tg; c = (x, y); L, O, own, name = p.F_Cu, p.B_Cu, pcs[p.F_Cu], f'({x}, {y})'
        have = [v for v in gvias if math.dist((p.ToMM(v.GetPosition().x), p.ToMM(v.GetPosition().y)), c) <= rad and any(q.Contains(v.GetPosition()) for q in own)]
        if have:
            targeted.append({'target': name, 'via': [round(p.ToMM(have[0].GetPosition().x), 2), round(p.ToMM(have[0].GetPosition().y), 2)], 'new': False}); continue
        n = int(rad / .1); done = None
        for q in sorted(((c[0] + i * .1, c[1] + j * .1) for i in range(-n, n + 1) for j in range(-n, n + 1) if math.hypot(i, j) * .1 <= rad), key=lambda q: math.dist(q, c)):
            dd = disc_r(q, EM)
            if not any(all(k.Contains(v) for v in dd) for k in own) or not any(all(k.Contains(v) for v in dd) for k in pcs[O] + in1_main()):
                continue
            if (any(z.Outline().Contains(xy(*q)) for z in rules) or blocked_inner(q)) or any(sh.Contains(xy(*q)) for sh in padpolys):
                continue
            if any(math.dist(q, (hx, hy)) < .2 + hr + .3 for hx, hy, hr in holes):
                continue
            v = p.PCB_VIA(b); v.SetPosition(xy(*q)); v.SetWidth(mm(.9)); v.SetDrill(mm(.4)); v.SetViaType(p.VIATYPE_THROUGH)
            v.SetLayerPair(p.F_Cu, p.B_Cu); v.SetNet(gnd); v.SetLocked(True); b.Add(v); obst.append(q); holes.append((*q, .2)); gvias.append(v)
            done = q; break
        targeted.append({'target': name, 'via': [round(done[0], 2), round(done[1], 2)] if done else None, 'new': bool(done)})
    p.ZONE_FILLER(b).Fill(b.Zones())
left = [f'{a.GetParentFootprint().GetReference()}.{a.GetNumber()}' for a in main_items()[1]]
final = islands(); area_after = {b.GetLayerName(L): area(L) for L in (p.F_Cu, p.B_Cu)}
p.SaveBoard(str(fn), b, True)
(P / 'routing/stitching.json').write_text(json.dumps({'grid_mm': GRID, 'vias': len(added), 'islands_before': before, 'islands_after': after,
                                                       'rescue_vias': len(rescued), 'rescued': rescued, 'islands_final': final,
                                                       'pour_mm2_before_rescue': area_before, 'pour_mm2_after_rescue': area_after,
                                                       'positions': [[round(x, 2), round(y, 2)] for x, y in added],
                                                       'tied_gnd_clusters': tied, 'gnd_pads_not_joined': left, 'targeted_vias': targeted}, indent=1) + '\n')
print('GND stitching:', len(added), 'grid vias, pour islands', before, '->', after, '| rescue:', len(rescued), 'vias, pour mm2', area_before, '->', area_after, 'islands', final,
      '| tied GND clusters:', len(tied), f'| GND pads not joined to {GND_REF[0]}.{GND_REF[1]}:', left or 'none',
      '| targeted vias:', sum(t['new'] for t in targeted), 'new,', sum(t['via'] is None for t in targeted), 'without a legal spot')
