"""R2 (review P5-01): copper path length from each AD7606B supply/reference pin to its own capacitor pad.
Graph over the net's own copper: track ends, points where a track end lies on another track, vias, and pads
(pad centre joined to every copper node inside the pad). Shortest path pad centre -> pad centre (Dijkstra).
Adapted from review script Plytki/P05-R1-recenzja/skrypty/odsprzeganie_U1.py. Used by verify_pcb.py."""
import pcbnew as p, math, heapq, collections
# (U1 pin, capacitor, limit mm): 0603/0805 <= 3 mm, 1210 <= 6 mm (review P5-01, task P05 R2). C4/C8 kept from R1.
LIMITS = [('1', 'C4', 3.0), ('48', 'C7', 3.0), ('37', 'C5', 3.0), ('38', 'C5', 3.0), ('23', 'C8', 4.0), ('36', 'C9', 3.0),
          ('39', 'C10', 3.0), ('42', 'C11', 3.0), ('42', 'C12', 6.0), ('44', 'C13', 6.0), ('45', 'C13', 6.0)]


def pos(v): return (round(p.ToMM(v.x), 4), round(p.ToMM(v.y), 4))


def net(i): return i.GetNetname().split('/')[-1]


def path(b, netname, a, c):
    fmap = {f.GetReference(): f for f in b.GetFootprints()}
    items = [t for t in b.GetTracks() if net(t) == netname]
    g = collections.defaultdict(list); segs = []
    for t in items:
        if isinstance(t, p.PCB_VIA):
            q = pos(t.GetPosition()); g[('F', q)].append((('B', q), 0)); g[('B', q)].append((('F', q), 0))
        else:
            L = 'F' if t.GetLayer() == p.F_Cu else 'B'; s, e = pos(t.GetStart()), pos(t.GetEnd()); d = math.dist(s, e)
            g[(L, s)].append(((L, e), d)); g[(L, e)].append(((L, s), d)); segs.append((L, s, e, t))
    for L, s, e, t in segs:
        for n in list(g):
            if n[0] == L and n[1] not in (s, e) and t.HitTest(p.VECTOR2I(p.FromMM(n[1][0]), p.FromMM(n[1][1]))):
                for q in (s, e):
                    d = math.dist(n[1], q); g[n].append(((L, q), d)); g[(L, q)].append((n, d))
    for r, num in (a, c):
        pd = next(x for x in fmap[r].Pads() if x.GetNumber() == num); key = ('PAD', r, num); cp = pos(pd.GetPosition())
        for n in list(g):
            if n[0] in ('F', 'B') and pd.IsOnLayer(p.F_Cu if n[0] == 'F' else p.B_Cu) and pd.HitTest(p.VECTOR2I(p.FromMM(n[1][0]), p.FromMM(n[1][1]))):
                d = math.dist(cp, n[1]); g[key].append((n, d)); g[n].append((key, d))
    start, goal = ('PAD',) + a, ('PAD',) + c; todo = [(0, start)]; seen = set()
    while todo:
        dd, q = heapq.heappop(todo)
        if q == goal: return round(dd, 3)
        if q in seen: continue
        seen.add(q)
        for v, w in g[q]: heapq.heappush(todo, (dd + w, v))
    return None


def measure(b):
    fmap = {f.GetReference(): f for f in b.GetFootprints()}; out = []
    for pin, cap, lim in LIMITS:
        pu = next(x for x in fmap['U1'].Pads() if x.GetNumber() == pin); n = net(pu)
        cp = next(x for x in fmap[cap].Pads() if net(x) == n)
        d = path(b, n, ('U1', pin), (cap, cp.GetNumber()))
        out.append({'pin': 'U1.' + pin, 'net': n, 'capacitor': cap, 'path_mm': d, 'limit_mm': lim, 'pass': d is not None and d <= lim})
    return out


if __name__ == '__main__':
    import sys, json
    b = p.LoadBoard(sys.argv[1] if len(sys.argv) > 1 else 'eda/P05.kicad_pcb')
    for r in measure(b): print(json.dumps(r))
