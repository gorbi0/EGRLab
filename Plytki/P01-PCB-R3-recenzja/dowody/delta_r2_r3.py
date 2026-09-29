import pcbnew as p, sys, collections
mm = p.ToMM
def load(fn):
    b = p.LoadBoard(fn)
    fp = {f.GetReference(): (round(mm(f.GetPosition().x), 3), round(mm(f.GetPosition().y), 3), round(f.GetOrientationDegrees(), 1), f.GetLayer()) for f in b.GetFootprints()}
    tr = collections.Counter(); vi = collections.Counter()
    for t in b.GetTracks():
        n = t.GetNetname().split('/')[-1]
        if isinstance(t, p.PCB_VIA):
            vi[(n, round(mm(t.GetPosition().x), 3), round(mm(t.GetPosition().y), 3), round(mm(t.GetWidth(p.F_Cu)), 2), round(mm(t.GetDrillValue()), 2), t.IsLocked())] += 1
        else:
            a = (round(mm(t.GetStart().x), 3), round(mm(t.GetStart().y), 3)); c = (round(mm(t.GetEnd().x), 3), round(mm(t.GetEnd().y), 3))
            tr[(n, b.GetLayerName(t.GetLayer()), tuple(sorted([a, c])), round(mm(t.GetWidth()), 3), t.IsLocked())] += 1
    zones = collections.Counter()
    for z in b.Zones():
        o = z.Outline(); pts = tuple((round(mm(o.CVertex(i).x), 2), round(mm(o.CVertex(i).y), 2)) for i in range(o.TotalVertices()))
        zones[(z.GetNetname(), tuple(b.GetLayerName(l) for l in z.GetLayerSet().Seq()), z.GetIsRuleArea(), z.GetZoneName(), pts)] += 1
    dr = collections.Counter()
    for d in b.GetDrawings():
        kind = type(d).__name__
        txt = d.GetText() if hasattr(d, 'GetText') else ''
        bb = d.GetBoundingBox()
        dr[(kind, b.GetLayerName(d.GetLayer()), txt, round(mm(bb.GetCenter().x), 1), round(mm(bb.GetCenter().y), 1))] += 1
    return b, fp, tr, vi, zones, dr
b2, f2, t2, v2, z2, d2 = load(sys.argv[1]); b3, f3, t3, v3, z3, d3 = load(sys.argv[2])
print('FOOTPRINT MOVES:')
for r in sorted(set(f2) | set(f3)):
    if f2.get(r) != f3.get(r): print('  ', r, f2.get(r), '->', f3.get(r))
rem = t2 - t3; add = t3 - t2
print('TRACKS R2', sum(t2.values()), 'R3', sum(t3.values()), 'removed', sum(rem.values()), 'added', sum(add.values()))
for k in sorted(rem): print('  -', k)
for k in sorted(add): print('  +', k)
print('VIAS removed', dict(v2 - v3), 'added', dict(v3 - v2))
zr = z2 - z3; za = z3 - z2
print('ZONES removed', len(zr), 'added', len(za))
for k in zr: print('  -', k[:4], k[4][:6])
for k in za: print('  +', k[:4], k[4][:6])
dr_ = d2 - d3; da = d3 - d2
print('DRAWINGS removed', sum(dr_.values()), 'added', sum(da.values()))
for k in sorted(dr_, key=str)[:40]: print('  -', k)
for k in sorted(da, key=str)[:60]: print('  +', k)
