"""Recenzja P04-R1: długość równoległego biegu (<= 1,2 mm, ta sama warstwa) SAFE_N i węzłów czasowych z liniami PWM/HB/ARM.
Uruchomienie (Python z KiCad 10): python sprzezenia.py ../../P04-R1-review/eda/P04.kicad_pcb"""
import pcbnew as p, math, sys, collections
b = p.LoadBoard(sys.argv[1])
segs = collections.defaultdict(list)
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA): continue
    n = t.GetNetname().split('/')[-1]
    segs[n].append((t.GetLayer(), (p.ToMM(t.GetStart().x), p.ToMM(t.GetStart().y)), (p.ToMM(t.GetEnd().x), p.ToMM(t.GetEnd().y))))
def sample(a, c, step=.25):
    L = math.dist(a, c); k = max(1, int(L / step))
    return [(a[0] + (c[0] - a[0]) * i / k, a[1] + (c[1] - a[1]) * i / k) for i in range(k + 1)], L / k
def pd(q, a, c):
    dx, dy = c[0] - a[0], c[1] - a[1]; L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / L2))
    return math.dist(q, (a[0] + t * dx, a[1] + t * dy))
def coupled(victim, aggr, dmax=1.2):
    tot = 0.0
    for L, a, c in segs[victim]:
        pts, dl = sample(a, c)
        for q in pts:
            if any(L2 == L and pd(q, a2, c2) <= dmax for L2, a2, c2 in segs[aggr]):
                tot += dl
    return round(tot, 1)
for v in ['SAFE_N', 'HEARTBEAT_P04', 'ARM_CONTACT', 'WD_RC', 'WD_C', 'ARM_BUTTON_N']:
    res = {a: coupled(v, a) for a in ['PWM', 'PWM_P04', 'PWM_OUT', 'HEARTBEAT', 'HEARTBEAT_P04', 'ARM_CLK', 'MOTOR_PERMIT', '5V_SYS'] if a != v}
    print(v, {k: x for k, x in res.items() if x > 0})
