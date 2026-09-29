"""P08-R1 routing clean-up inherited from the earlier board toolchain. Remove duplicates, free dead ends and rounding gaps; retain locked paths. Change starved thermal pads to solid only when named by native DRC (never soldered-wire pads). Delete by UUID in file text because pcbnew Remove() invalidates SWIG wrappers. Refill and reject any result with missing connections."""
from pathlib import Path
import pcbnew as p, sys, collections, math
from sexpr import parse, dump
P = Path(__file__).resolve().parents[1]; fn = P / 'eda/P08.kicad_pcb'; BACKUP = fn.read_bytes(); b = p.LoadBoard(str(fn))
SOLID_PADS = [a.split('.') for a in sys.argv[1:]]


def key(v):
    return (round(p.ToMM(v.x), 4), round(p.ToMM(v.y), 4))


def uid(t):
    return t.m_Uuid.AsString()


tracks = list(b.GetTracks()); dead = set()  # UUIDs to delete
by_net = collections.defaultdict(list)
for t in tracks:
    by_net[t.GetNetCode()].append(t)
pads_by_net = collections.defaultdict(list)
for f in b.GetFootprints():
    for a in f.Pads():
        pads_by_net[a.GetNetCode()].append(a)
# 1. redundant chains between locked copper
redundant_nets = set()
for code, items in by_net.items():
    locked = [t for t in items if t.IsLocked()]
    if not locked:
        continue
    free = [t for t in items if not t.IsLocked() and not isinstance(t, p.PCB_VIA)]
    free_vias = [t for t in items if not t.IsLocked() and isinstance(t, p.PCB_VIA)]

    def anchored(pt, layer):
        return any((isinstance(t, p.PCB_VIA) or t.GetLayer() == layer) and t.HitTest(pt) for t in locked)

    def blocked(pt, layer):
        return any(a.IsOnLayer(layer) and a.HitTest(pt) for a in pads_by_net[code]) or any(v.HitTest(pt) for v in free_vias)

    adj = collections.defaultdict(list)
    for t in free:
        for e in (t.GetStart(), t.GetEnd()):
            adj[(t.GetLayer(), key(e))].append(t)
    for t in free:
        for start in (t.GetStart(), t.GetEnd()):
            if not anchored(start, t.GetLayer()) or blocked(start, t.GetLayer()):
                continue
            chain, cur, pt = [t], t, (t.GetEnd() if start == t.GetStart() else t.GetStart())
            while True:
                node = (cur.GetLayer(), key(pt))
                if blocked(pt, cur.GetLayer()):
                    break
                if anchored(pt, cur.GetLayer()):
                    dead.update(uid(x) for x in chain); redundant_nets.add(t.GetNetname()); break
                nxt = [x for x in adj[node] if x is not cur]
                if len(nxt) != 1 or len(chain) > 50:
                    break
                cur = nxt[0]; chain.append(cur)
                pt = cur.GetEnd() if key(cur.GetStart()) == node[1] else cur.GetStart()
n_redundant = len(dead)
# 2. SES rounding
free = [t for t in tracks if not t.IsLocked() and not isinstance(t, p.PCB_VIA) and uid(t) not in dead]
# Deterministic geometric order, so the end that moves in a join does not depend on the random UUID order of the file (clean rebuild)
free.sort(key=lambda t: (t.GetNetname(), t.GetLayer(), sorted([key(t.GetStart()), key(t.GetEnd())])))
tiny = {uid(t) for t in free if p.ToMM(t.GetLength()) < .005}; dead |= tiny
free = [t for t in free if uid(t) not in tiny]
ends = [(t, i, (t.GetStart() if i == 0 else t.GetEnd())) for t in free for i in (0, 1)]
joined = 0
for k, (t, i, e) in enumerate(ends):
    for u, j, g in ends[k + 1:]:
        if u is t or u.GetNetCode() != t.GetNetCode() or u.GetLayer() != t.GetLayer():
            continue
        if 0 < math.hypot(p.ToMM(e.x - g.x), p.ToMM(e.y - g.y)) < .005:
            (u.SetStart if j == 0 else u.SetEnd)(e); joined += 1
# 3. duplicates and dead ends
seen = {}; dup = 0
for t in sorted(tracks, key=lambda t: (t.GetNetname(), t.GetLayer(), sorted([key(t.GetStart()), key(t.GetEnd())]))):
    if t.IsLocked() or isinstance(t, p.PCB_VIA) or uid(t) in dead:
        continue
    k = (t.GetNetCode(), t.GetLayer(), frozenset([key(t.GetStart()), key(t.GetEnd())]))
    if k in seen:
        dead.add(uid(t)); dup += 1
    else:
        seen[k] = t
n_dead_end = 0
while True:
    live = [t for t in tracks if uid(t) not in dead]; gone = []
    for t in live:
        if t.IsLocked():
            continue
        same = [u for u in live if u is not t and u.GetNetCode() == t.GetNetCode()]
        pads = pads_by_net[t.GetNetCode()]
        if isinstance(t, p.PCB_VIA):
            links = [u for u in same if not isinstance(u, p.PCB_VIA) and u.HitTest(t.GetPosition())]
            if len(links) + sum(a.HitTest(t.GetPosition()) for a in pads) < 2:
                gone.append(uid(t))
            continue
        for e in (t.GetStart(), t.GetEnd()):
            on = any(a.IsOnLayer(t.GetLayer()) and a.HitTest(e) for a in pads) or any(
                (isinstance(u, p.PCB_VIA) and u.HitTest(e)) or (not isinstance(u, p.PCB_VIA) and u.GetLayer() == t.GetLayer() and u.HitTest(e)) for u in same)
            if not on:
                gone.append(uid(t)); break
    if not gone:
        break
    dead |= set(gone); n_dead_end += len(gone)
p.SaveBoard(str(fn), b)  # joined ends; nothing removed through pcbnew
tree = parse(fn.read_text(encoding='utf-8')); before = len(tree)


def item_uuid(g):
    return next((x[1] for x in g if isinstance(x, list) and x and x[0] == 'uuid'), None)


tree = [g for g in tree if not (isinstance(g, list) and g and g[0] in ('segment', 'via') and item_uuid(g) in dead)]
assert before - len(tree) == len(dead), (before - len(tree), len(dead))
fn.write_text(dump(tree) + chr(10), encoding='utf-8')
b = p.LoadBoard(str(fn))
for ref, num in SOLID_PADS:
    pad = next(a for f in b.GetFootprints() if f.GetReference() == ref for a in f.Pads() if a.GetNumber() == num)
    pad.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
p.ZONE_FILLER(b).Fill(b.Zones()); b.BuildConnectivity()
left = b.GetConnectivity().GetUnconnectedCount(True)
if left:  # e.g. a GND pad enclosed by routed tracks on both layers: the pours cannot reach it
    fn.write_bytes(BACKUP); print(f'aborted: {left} unconnected after clean-up (solid pads and refill included); input board restored'); sys.exit(3)
p.SaveBoard(str(fn), b, True)
print('removed', n_redundant, 'redundant free items', sorted(redundant_nets), '; dropped', len(tiny), 'tiny; joined', joined, 'near-miss ends;',
      dup, 'duplicate and', n_dead_end, 'dead-end items; unconnected 0; solid zone connection:', ['.'.join(x) for x in SOLID_PADS] or 'none')
