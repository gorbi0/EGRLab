"""P03 R6 post-routing clean-up (the P02 R4 script, board file name changed; P02 R4 copied it from P04 R2). Taken over from P03 R1 (Claude); replaces the R1 script, which deleted through pcbnew
(see the SWIG note below) and had no dead-end removal. Run after import_routing.py, set_rules.py and complete_routes.py.
1. Remove autorouted chains that start and end on locked copper of the same net and touch no pad or free via on
   the way: they only duplicate locked copper. P02 R4 (30.09): both ends must lie on the same connected group of locked
   copper (locked tracks and vias joined end to end or through a pad of the net); the completion planner leaves separate
   locked pieces, and a chain between two of them is the only link (P02_OK after the tab-pour change).
2. SES rounding: drop free segments shorter than 5 um; join free track ends that miss each other by < 5 um.
3. Router dead ends (P03 R1: MOTOR_INA ran 5 mm out and back on both layers; P04 R2 trials: F.Cu and B.Cu stubs meeting where no via was emitted): drop duplicate
   free segments, then free segments with an end that touches no pad, via or other segment of the net, and free vias
   left with fewer than two connections; repeated until nothing changes.
3a. P02 R4 (29.09, klasa L): vias whose centre lies on a THT pad of the same net (DRC hole_to_hole), free or locked:
   the completion planner may change layers on its own THT pad and emit a via there. The pad already joins both
   layers and the track ends stay on its copper. Free vias of nets without a pour that touch copper on one layer only
   (DRC via_dangling) go as dead ends.
4. Pads given on the command line (e.g. U9.13) get a solid zone connection: pads whose thermal relief is starved
   by neighbouring tracks (DRC starved_thermal). Never used for soldered wires.
--tidy (P03 R6, 30.09): the same steps right after the SES import, saved even with gaps left. Freerouting 2.1 leaves pieces of
connections it did not finish (PFAIL_N in three pieces, a floating middle one); the completion planner took them as
items to join and they blocked its paths. The final clean-up (no --tidy) still requires complete connectivity.
pcbnew's Remove() leaves the SWIG wrappers of the whole process unusable (GetTracks / LoadBoard return SwigPyObject),
so victims are chosen by UUID on the loaded board and deleted at file level; the board is then reloaded, the solid pads
set and the pours refilled; it is saved only if connectivity is complete (otherwise the input file is restored, exit 1).
"""
from pathlib import Path
import pcbnew as p, sys, collections, math
from sexpr import parse, dump
P = Path(__file__).resolve().parents[1]; fn = P / 'eda/P03.kicad_pcb'; BACKUP = fn.read_bytes(); b = p.LoadBoard(str(fn))
TIDY = '--tidy' in sys.argv   # P03 R6 (30.09, Ubuntu): right after the SES import, before the completion planner (see below)
SOLID_PADS = [a.split('.') for a in sys.argv[1:] if a != '--tidy']


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

    # connected groups of locked copper: tracks/vias joined end to end, or through a pad of the net
    grp = {uid(t): uid(t) for t in locked}

    def root(u):
        while grp[u] != u:
            grp[u] = grp[grp[u]]; u = grp[u]
        return u

    def ends(t):
        return [t.GetPosition()] if isinstance(t, p.PCB_VIA) else [t.GetStart(), t.GetEnd()]

    for t in locked:
        for u in locked:
            if u is t or root(uid(u)) == root(uid(t)):
                continue
            if any((isinstance(u, p.PCB_VIA) or isinstance(t, p.PCB_VIA) or u.GetLayer() == t.GetLayer()) and u.HitTest(e) for e in ends(t)):
                grp[root(uid(u))] = root(uid(t))
    for a in pads_by_net[code]:
        on = [t for t in locked if any(a.HitTest(e) and (isinstance(t, p.PCB_VIA) or a.IsOnLayer(t.GetLayer())) for e in ends(t))]
        for t in on[1:]:
            grp[root(uid(t))] = root(uid(on[0]))

    def anchored(pt, layer):
        return {root(uid(t)) for t in locked if (isinstance(t, p.PCB_VIA) or t.GetLayer() == layer) and t.HitTest(pt)}

    def blocked(pt, layer):
        return any(a.IsOnLayer(layer) and a.HitTest(pt) for a in pads_by_net[code]) or any(v.HitTest(pt) for v in free_vias)

    adj = collections.defaultdict(list)
    for t in free:
        for e in (t.GetStart(), t.GetEnd()):
            adj[(t.GetLayer(), key(e))].append(t)
    for t in free:
        for start in (t.GetStart(), t.GetEnd()):
            g0 = anchored(start, t.GetLayer())
            if not g0 or blocked(start, t.GetLayer()):
                continue
            chain, cur, pt = [t], t, (t.GetEnd() if start == t.GetStart() else t.GetStart())
            while True:
                node = (cur.GetLayer(), key(pt))
                if blocked(pt, cur.GetLayer()):
                    break
                g1 = anchored(pt, cur.GetLayer())
                if g1:
                    if g0 & g1:   # same locked group at both ends: the chain duplicates it
                        dead.update(uid(x) for x in chain); redundant_nets.add(t.GetNetname())
                    break
                nxt = [x for x in adj[node] if x is not cur]
                if len(nxt) != 1 or len(chain) > 50:
                    break
                cur = nxt[0]; chain.append(cur)
                pt = cur.GetEnd() if key(cur.GetStart()) == node[1] else cur.GetStart()
n_redundant = len(dead)
# 2. SES rounding
free = [t for t in tracks if not t.IsLocked() and not isinstance(t, p.PCB_VIA) and uid(t) not in dead]
# P04 R2: geometric order, so the end that moves in a join does not depend on the random UUID order of the file (clean rebuild)
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
# 3a. vias on THT pads of the same net
n_via_pad = 0
for t in tracks:
    if not isinstance(t, p.PCB_VIA) or uid(t) in dead:
        continue
    for a in pads_by_net[t.GetNetCode()]:
        if a.GetAttribute() != p.PAD_ATTRIB_PTH or not a.HitTest(t.GetPosition()):
            continue
        gap = math.hypot(p.ToMM(t.GetPosition().x - a.GetPosition().x), p.ToMM(t.GetPosition().y - a.GetPosition().y))
        if gap < p.ToMM(max(a.GetDrillSize().x, a.GetDrillSize().y)) / 2 + p.ToMM(t.GetDrillValue()) / 2 + .3:   # min hole-to-hole 0.3 mm
            dead.add(uid(t)); n_via_pad += 1; break
n_dead_end = 0
pour_nets = {z.GetNetCode() for z in b.Zones() if not z.GetIsRuleArea()}
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
            elif t.GetNetCode() not in pour_nets:   # P02 R4: copper on one layer only (DRC via_dangling)
                lay = {u.GetLayer() for u in links} | {L for a in pads if a.HitTest(t.GetPosition()) for L in (p.F_Cu, p.B_Cu) if a.IsOnLayer(L)}
                if len(lay) < 2:
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
if left and not TIDY:  # e.g. a GND pad enclosed by routed tracks on both layers: the pours cannot reach it
    fn.write_bytes(BACKUP); print(f'aborted: {left} unconnected after clean-up (solid pads and refill included); input board restored'); sys.exit(3)
p.SaveBoard(str(fn), b, True)
print(('tidy (unconnected %d left for the planner): ' % left) if TIDY else '', 'removed', n_redundant, 'redundant free items', sorted(redundant_nets), '; dropped', len(tiny), 'tiny; joined', joined, 'near-miss ends;',
      dup, 'duplicate,', n_via_pad, 'via-on-THT-pad and', n_dead_end, 'dead-end items; solid zone connection:', ['.'.join(x) for x in SOLID_PADS] or 'none')
