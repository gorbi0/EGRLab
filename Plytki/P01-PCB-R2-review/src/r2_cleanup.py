"""R2 post-routing clean-up. Run once after import_routing.py and set_rules.py.
1. Safety net: remove autorouted P01_VS chains that start and end inside the locked VS copper
   (rail, stubs, vias) and touch no pad or via on the way; they only duplicate a connection
   that the locked copper already makes. Since the rails have a vertex at every stub,
   Freerouting should add none; the count is printed. The board is saved only if
   connectivity stays complete.
2. Pads listed in SOLID_PADS get a solid zone connection (a thermal starved by neighbouring
   tracks, reported by DRC as starved_thermal). Test pads only, no soldered wire there.
"""
from pathlib import Path
import pcbnew as p, sys, collections
P = Path(__file__).resolve().parents[1]; fn = P / 'eda/P01.kicad_pcb'; b = p.LoadBoard(str(fn))
SOLID_PADS = [a.split('.') for a in sys.argv[1:]]  # e.g. J4.3


def key(v):
    return (round(p.ToMM(v.x), 4), round(p.ToMM(v.y), 4))


vs = [t for t in b.GetTracks() if t.GetNetname().split('/')[-1] == 'P01_VS']
locked = [t for t in vs if t.IsLocked()]
free = [t for t in vs if not t.IsLocked() and not isinstance(t, p.PCB_VIA)]
free_vias = [t for t in vs if not t.IsLocked() and isinstance(t, p.PCB_VIA)]
pads = [a for f in b.GetFootprints() for a in f.Pads() if a.GetNetname().split('/')[-1] == 'P01_VS']


def anchored(pt, layer):
    return any((isinstance(t, p.PCB_VIA) or t.GetLayer() == layer) and t.HitTest(pt) for t in locked)


def blocked(pt, layer):  # a real branch point: pad or unlocked via
    return any(a.IsOnLayer(layer) and a.HitTest(pt) for a in pads) or any(v.HitTest(pt) for v in free_vias)


adj = collections.defaultdict(list)
for t in free:
    for e in (t.GetStart(), t.GetEnd()):
        adj[(t.GetLayer(), key(e))].append(t)
redundant = set()
for t in free:
    for start in (t.GetStart(), t.GetEnd()):
        node = (t.GetLayer(), key(start))
        if not anchored(start, t.GetLayer()):
            continue
        chain, cur, pt = [t], t, (t.GetEnd() if start == t.GetStart() else t.GetStart())
        while True:
            node = (cur.GetLayer(), key(pt))
            if anchored(pt, cur.GetLayer()):
                redundant.update(id(x) for x in chain)
                break
            nxt = [x for x in adj[node] if x is not cur]
            if blocked(pt, cur.GetLayer()) or len(nxt) != 1 or len(chain) > 50:
                break
            cur = nxt[0]; chain.append(cur)
            pt = cur.GetEnd() if key(cur.GetStart()) == node[1] else cur.GetStart()
victims = [t for t in free if id(t) in redundant]
for t in victims:
    b.Remove(t)
b.BuildConnectivity()
left = b.GetConnectivity().GetUnconnectedCount(True)
if left:
    sys.exit(f'aborted: {left} unconnected after removal; board not saved')
for ref, num in SOLID_PADS:
    pad = next(a for f in b.GetFootprints() if f.GetReference() == ref for a in f.Pads() if a.GetNumber() == num)
    pad.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
p.ZONE_FILLER(b).Fill(b.Zones()); p.SaveBoard(str(fn), b, True)
print('removed', len(victims), 'redundant VS segments; unconnected 0; solid zone connection:', ['.'.join(x) for x in SOLID_PADS] or 'none')
