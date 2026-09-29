import pcbnew, sys, math
b = pcbnew.LoadBoard(sys.argv[1]); MM = pcbnew.ToMM
def segdist(p1, p2, q1, q2):
    def d_pt_seg(p, a, bb):
        ax, ay = a; bx, by = bb; px, py = p
        dx, dy = bx-ax, by-ay
        L2 = dx*dx+dy*dy
        t = 0 if L2 == 0 else max(0, min(1, ((px-ax)*dx+(py-ay)*dy)/L2))
        return math.hypot(px-(ax+t*dx), py-(ay+t*dy))
    return min(d_pt_seg(p1,q1,q2), d_pt_seg(p2,q1,q2), d_pt_seg(q1,p1,p2), d_pt_seg(q2,p1,p2))
def polyline(g, step=0.1):
    if g.GetShape() == pcbnew.SHAPE_T_SEGMENT:
        return [(MM(g.GetStart().x), MM(g.GetStart().y)), (MM(g.GetEnd().x), MM(g.GetEnd().y))]
    if g.GetShape() == pcbnew.SHAPE_T_ARC:
        c = g.GetCenter(); r = MM(g.GetRadius()); a0 = g.GetArcAngleStart().AsRadians(); da = g.GetArcAngle().AsRadians()
        n = max(2, int(abs(da)*r/step))
        return [(MM(c.x)+r*math.cos(a0+da*i/n), MM(c.y)+r*math.sin(a0+da*i/n)) for i in range(n+1)]
    return []
tracks = [t for t in b.GetTracks() if t.Type() != pcbnew.PCB_VIA_T and t.GetLayer() == pcbnew.F_Cu and t.GetNetname() not in ('GND',)]
for ref in ('HS1', 'HS2'):
    fp = b.FindFootprintByReference(ref)
    edges = []
    for g in fp.GraphicalItems():
        if isinstance(g, pcbnew.PCB_SHAPE) and g.GetLayer() == pcbnew.F_Fab:
            pl = polyline(g); edges += list(zip(pl, pl[1:]))
    worst = {}
    for t in tracks:
        a = (MM(t.GetStart().x), MM(t.GetStart().y)); e = (MM(t.GetEnd().x), MM(t.GetEnd().y)); hw = MM(t.GetWidth())/2
        for (p, q) in edges:
            d = segdist(p, q, a, e) - hw
            key = (t.GetNetname(), round(MM(t.GetWidth()),2), a, e)
            if d < 1.0 and (key not in worst or d < worst[key][0]): worst[key] = (d, p, q)
    print(ref)
    for (n, w, a, e), (d, p, q) in sorted(worst.items(), key=lambda kv: kv[1][0]):
        state = "NAKŁADA SIĘ" if d < 0 else f"odstęp {d:.2f} mm"
        print(f"   {n:14s} w={w} ({a[0]:.1f},{a[1]:.1f})->({e[0]:.1f},{e[1]:.1f}): krawędź profilu vs miedź = {d:+.2f} mm ({state}); krawędź przy ({p[0]:.1f},{p[1]:.1f})")
