"""Order-independent signature of a track or via (net, geometry, width, layer), shared by seed_r3.py and unseed.py."""
import pcbnew as p


def sig(t):
    n = t.GetNetname()
    if isinstance(t, p.PCB_VIA):
        return ['via', n, round(p.ToMM(t.GetPosition().x), 4), round(p.ToMM(t.GetPosition().y), 4), round(p.ToMM(t.GetWidth(p.F_Cu)), 4)]
    a, c = sorted([(round(p.ToMM(t.GetStart().x), 4), round(p.ToMM(t.GetStart().y), 4)), (round(p.ToMM(t.GetEnd().x), 4), round(p.ToMM(t.GetEnd().y), 4))])
    return ['trk', n, *a, *c, round(p.ToMM(t.GetWidth()), 4), 'F.Cu' if t.GetLayer() == p.F_Cu else 'B.Cu']
