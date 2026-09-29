import pcbnew, sys, math, collections
b = pcbnew.LoadBoard(sys.argv[1]); MM = pcbnew.ToMM
def seg(t): return ((MM(t.GetStart().x), MM(t.GetStart().y)), (MM(t.GetEnd().x), MM(t.GetEnd().y)), MM(t.GetWidth())/2, t.GetLayer())
def dps(p, a, bb):
    dx, dy = bb[0]-a[0], bb[1]-a[1]; L2 = dx*dx+dy*dy
    t = 0 if L2 == 0 else max(0, min(1, ((p[0]-a[0])*dx+(p[1]-a[1])*dy)/L2))
    return math.hypot(p[0]-(a[0]+t*dx), p[1]-(a[1]+t*dy))
def sd(s1, s2):
    (a,b1,_,_),(c,d,_,_) = s1, s2
    return min(dps(a,c,d), dps(b1,c,d), dps(c,a,b1), dps(d,a,b1))
tr = [t for t in b.GetTracks() if t.Type() != pcbnew.PCB_VIA_T]
sens = ('/AUX/P01_OV_REF', 'P01_OK', '/AUX/P01_OV_SENSE', '/AUX/P01_UV_SENSE', '/AUX/P01_REF')
aggr = ('BAT_FUSED', 'P01_VS', '/P01_Q1_DRAIN', '/VPROT', '/P01_OFF_COL', '/P01_GATE')
for n in sens:
    S1 = [seg(t) for t in tr if t.GetNetname() == n]
    near = collections.defaultdict(lambda: [0.0, 99.0])
    for s in S1:
        for t in tr:
            if t.GetNetname() not in aggr: continue
            s2 = seg(t)
            same_layer = s[3] == s2[3]
            gap = sd(s, s2) - s[2] - s2[2]
            if gap < 2.0:
                k = (t.GetNetname(), 'ta sama warstwa' if same_layer else 'druga warstwa')
                near[k][1] = min(near[k][1], gap)
    L = sum(math.hypot(a[0]-c[0], a[1]-c[1]) for a, c, _, _ in S1)
    ys = [p[1] for a, c, _, _ in S1 for p in (a, c)]
    print(f"{n:20s} dł. {L:6.1f} mm, zakres y {min(ys):5.1f}..{max(ys):5.1f} | blisko mocy: " + (', '.join(f"{k[0]} ({k[1]}) min {v[1]:.2f} mm" for k, v in near.items()) or '—'))
