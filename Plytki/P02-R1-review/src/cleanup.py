"""P02 post-routing clean-up. Run once after import_routing.py and set_rules.py.
1. Remove autorouted chains that start and end on locked copper of the same net (track, via or the
   filled VPROT zone) and touch no pad or free via on the way: they only duplicate locked copper.
2. Join free track ends that miss each other by < 5 um (SES rounding), so no end is dangling.
3. Pads given on the command line (e.g. U5.12) get a solid zone connection: signal pads whose thermal
   relief is starved by neighbouring tracks (DRC starved_thermal). Never used for soldered wires.
The board is saved only if connectivity stays complete.
"""
from pathlib import Path
import pcbnew as p, sys, collections, math
P = Path(__file__).resolve().parents[1]; fn = P / 'eda/P02.kicad_pcb'; b = p.LoadBoard(str(fn))
SOLID_PADS = [a.split('.') for a in sys.argv[1:]]


def key(v):
    return (round(p.ToMM(v.x), 4), round(p.ToMM(v.y), 4))


tracks = list(b.GetTracks())
by_net = collections.defaultdict(list)
for t in tracks:
    by_net[t.GetNetCode()].append(t)
pads_by_net = collections.defaultdict(list)
for f in b.GetFootprints():
    for a in f.Pads():
        pads_by_net[a.GetNetCode()].append(a)
zones = [z for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'VPROT']
victims = []
for code, items in by_net.items():
    locked = [t for t in items if t.IsLocked()]
    if not locked:
        continue
    free = [t for t in items if not t.IsLocked() and not isinstance(t, p.PCB_VIA)]
    free_vias = [t for t in items if not t.IsLocked() and isinstance(t, p.PCB_VIA)]

    def anchored(pt, layer):
        if any((isinstance(t, p.PCB_VIA) or t.GetLayer() == layer) and t.HitTest(pt) for t in locked):
            return True
        return any(z.GetNetCode() == code and z.IsOnLayer(layer) and z.HitTestFilledArea(layer, pt) for z in zones)

    def blocked(pt, layer):
        return any(a.IsOnLayer(layer) and a.HitTest(pt) for a in pads_by_net[code]) or any(v.HitTest(pt) for v in free_vias)

    adj = collections.defaultdict(list)
    for t in free:
        for e in (t.GetStart(), t.GetEnd()):
            adj[(t.GetLayer(), key(e))].append(t)
    redundant = set()
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
                    redundant.update(id(x) for x in chain); break
                nxt = [x for x in adj[node] if x is not cur]
                if len(nxt) != 1 or len(chain) > 50:
                    break
                cur = nxt[0]; chain.append(cur)
                pt = cur.GetEnd() if key(cur.GetStart()) == node[1] else cur.GetStart()
    victims += [t for t in free if id(t) in redundant]
for t in victims:
    b.Remove(t)
# 2. SES rounding: drop free segments shorter than 5 um, then join free ends that miss by < 5 um
joined = 0
free = [t for t in b.GetTracks() if not t.IsLocked() and not isinstance(t, p.PCB_VIA)]
tiny = [t for t in free if p.ToMM(t.GetLength()) < .005]
for t in tiny:
    b.Remove(t)
free = [t for t in free if all(t is not u for u in tiny)]
ends = [(t, i, (t.GetStart() if i == 0 else t.GetEnd())) for t in free for i in (0, 1)]
for k, (t, i, e) in enumerate(ends):
    for u, j, g in ends[k + 1:]:
        if u is t or u.GetNetCode() != t.GetNetCode() or u.GetLayer() != t.GetLayer():
            continue
        dist = math.hypot(p.ToMM(e.x - g.x), p.ToMM(e.y - g.y))
        if 0 < dist < .005:
            (u.SetStart if j == 0 else u.SetEnd)(e); joined += 1
b.BuildConnectivity()
left = b.GetConnectivity().GetUnconnectedCount(True)
if left:
    sys.exit(f'aborted: {left} unconnected after clean-up; board not saved')
for ref, num in SOLID_PADS:
    pad = next(a for f in b.GetFootprints() if f.GetReference() == ref for a in f.Pads() if a.GetNumber() == num)
    pad.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
p.ZONE_FILLER(b).Fill(b.Zones()); p.SaveBoard(str(fn), b, True)
print('removed', len(victims), 'redundant free segments', sorted({t.GetNetname() for t in victims}), '; dropped', len(tiny), 'tiny; joined', joined,
      'near-miss ends; unconnected 0; solid zone connection:', ['.'.join(x) for x in SOLID_PADS] or 'none')
