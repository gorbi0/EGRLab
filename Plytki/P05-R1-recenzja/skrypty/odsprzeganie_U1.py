import pcbnew as p, math, heapq, collections
b = p.LoadBoard('eda/P05.kicad_pcb')
def pos(v): return (round(p.ToMM(v.x), 4), round(p.ToMM(v.y), 4))
def xy(x, y): return p.VECTOR2I(p.FromMM(x), p.FromMM(y))
fmap = {f.GetReference(): f for f in b.GetFootprints()}
def pad(r, n): return next(a for a in fmap[r].Pads() if a.GetNumber() == n)
def net(i): return i.GetNetname().split('/')[-1]
def route(netname, a, c):
    items = [t for t in b.GetTracks() if net(t) == netname]
    g = collections.defaultdict(list); segs = []; vias = set()
    for t in items:
        if isinstance(t, p.PCB_VIA):
            q = pos(t.GetPosition()); g[('F', q)].append((('B', q), 0, 1)); g[('B', q)].append((('F', q), 0, 1))
        else:
            L = 'F' if t.GetLayer() == p.F_Cu else 'B'; s, e = pos(t.GetStart()), pos(t.GetEnd()); d = math.dist(s, e)
            g[(L, s)].append(((L, e), d, 0)); g[(L, e)].append(((L, s), d, 0)); segs.append((L, s, e, t))
    for L, s, e, t in segs:
        for n in list(g):
            if n[0] == L and n[1] not in (s, e) and t.HitTest(xy(*n[1])):
                for q in (s, e):
                    d = math.dist(n[1], q); g[n].append(((L, q), d, 0)); g[(L, q)].append((n, d, 0))
    for f in b.GetFootprints():
        for pd in f.Pads():
            if net(pd) != netname or not pd.GetNumber(): continue
            key = ('PAD', f.GetReference(), pd.GetNumber()); cpos = pos(pd.GetPosition())
            for n in list(g):
                if n[0] in ('F', 'B') and pd.HitTest(xy(*n[1])) and pd.IsOnLayer(p.F_Cu if n[0] == 'F' else p.B_Cu):
                    d = math.dist(cpos, n[1]); g[key].append((n, d, 0)); g[n].append((key, d, 0))
    start, goal = ('PAD',) + a, ('PAD',) + c; todo = [(0, 0, start)]; seen = set()
    while todo:
        dd, nv, q = heapq.heappop(todo)
        if q == goal: return round(dd, 1), nv
        if q in seen: continue
        seen.add(q)
        for v, w, isvia in g[q]: heapq.heappush(todo, (dd + w, nv + isvia, v))
    return None, None
pairs = [('C4', 'U1', '1', '5VA_P05'), ('C7', 'U1', '48', '5VA_P05'), ('C5', 'U1', '37', '5VA_P05'), ('C6', 'U1', '38', '5VA_P05'),
         ('C9', 'U1', '36', 'REGCAP_A'), ('C10', 'U1', '39', 'REGCAP_D'), ('C11', 'U1', '42', 'ADC_REF'), ('C12', 'U1', '42', 'ADC_REF'),
         ('C13', 'U1', '44', 'REFCAP'), ('C13', 'U1', '45', 'REFCAP'), ('C8', 'U1', '23', '3V3_DAQ'), ('C2', 'U12', '2', '5VA_P05'), ('C3', 'U12', '3', '3V3_DAQ')]
for c, u, un, n in pairs:
    cp = [a for a in fmap[c].Pads() if net(a) == n][0]
    straight = math.dist(pos(pad(u, un).GetPosition()), pos(cp.GetPosition()))
    r, nv = route(n, (u, un), (c, cp.GetNumber()))
    print(f'{c:4} -> {u}.{un:3} {n:9} straight {straight:5.1f} mm  routed {r} mm  vias {nv}')
for n in ('24', '14', '42', '44', '45', '36', '39', '23', '1', '48', '37', '38'):
    print('U1 pin', n, pad('U1', n).GetNetname(), pos(pad('U1', n).GetPosition()))
