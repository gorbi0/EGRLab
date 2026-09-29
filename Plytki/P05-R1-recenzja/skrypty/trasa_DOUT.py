import pcbnew as p, math
b = p.LoadBoard('eda/P05.kicad_pcb')
tot = {'F': 0, 'B': 0}
for t in b.GetTracks():
    if t.GetNetname().split('/')[-1] != 'AD_DOUT_LOCAL': continue
    if isinstance(t, p.PCB_VIA):
        print('via', round(p.ToMM(t.GetPosition().x), 2), round(p.ToMM(t.GetPosition().y), 2)); continue
    L = 'F' if t.GetLayer() == p.F_Cu else 'B'; s, e = t.GetStart(), t.GetEnd()
    a = (round(p.ToMM(s.x), 2), round(p.ToMM(s.y), 2)); c = (round(p.ToMM(e.x), 2), round(p.ToMM(e.y), 2))
    tot[L] += math.dist(a, c); print(L, a, c, round(p.ToMM(t.GetWidth()), 2))
print({k: round(v, 1) for k, v in tot.items()})
for z in b.Zones():
    if z.GetIsRuleArea(): pass
