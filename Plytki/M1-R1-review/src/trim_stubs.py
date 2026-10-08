"""P05 R3 (1.10): trim the unused ends of the pre-routed copper (route_critical.py escapes and stubs the router reached elsewhere:
DRC track_dangling). A track end that touches no pad, via or other copper of its net is free. A free track whose other copper touches
it only at its far end (or a pad there) goes; one joined in the middle (T-junction of the locked 5VA bar, 1.10 first try with
cleanup.py --trim-locked cut the whole bar) is shortened to the junction nearest its free end. Repeated until nothing changes; the
board is saved only if connectivity is unchanged (otherwise restored, exit 3). Deletion at file level (pcbnew Remove() breaks SWIG).
Report: routing/trimmed.json."""
from pathlib import Path
import pcbnew as p, json, sys, math
from sexpr import parse, dump
sys.path.insert(0, str(Path(__file__).resolve().parent))
from board import NAME
P = Path(__file__).resolve().parents[1]; fn = P / f'eda/{NAME}.kicad_pcb'; BACKUP = fn.read_bytes()
b = p.LoadBoard(str(fn)); b.BuildConnectivity(); before = b.GetConnectivity().GetUnconnectedCount(True)
mm = lambda v: (p.ToMM(v.x), p.ToMM(v.y))
pads = {}
for f in b.GetFootprints():
    for a in f.Pads():
        pads.setdefault(a.GetNetCode(), []).append(a)
p.ZONE_FILLER(b).Fill(b.Zones())
zones = {}
for z in b.Zones():
    if not z.GetIsRuleArea():
        zones.setdefault(z.GetNetCode(), []).append(z)
dead, shortened = set(), []


def on_copper(t, pt, others):
    v = p.VECTOR2I(p.FromMM(pt[0]), p.FromMM(pt[1]))
    return (any(a.IsOnLayer(t.GetLayer()) and a.HitTest(v) for a in pads.get(t.GetNetCode(), []))
            or any((isinstance(u, p.PCB_VIA) or u.GetLayer() == t.GetLayer()) and u.HitTest(v) for u in others)
            or any(z.GetFilledPolysList(t.GetLayer()).Contains(v) for z in zones.get(t.GetNetCode(), []) if z.IsOnLayer(t.GetLayer())))   # M1: tap from a force pour


while True:
    live = [t for t in b.GetTracks() if t.m_Uuid.AsString() not in dead]; changed = False
    for t in live:
        if isinstance(t, p.PCB_VIA) or t.GetNetname() == 'GND':
            continue
        others = [u for u in live if u is not t and u.GetNetCode() == t.GetNetCode()]
        s, e = mm(t.GetStart()), mm(t.GetEnd())
        free = [k for k, pt in ((0, s), (1, e)) if not on_copper(t, pt, others)]
        if not free:
            continue
        if len(free) == 2:   # floating piece
            dead.add(t.m_Uuid.AsString()); changed = True; continue
        k = free[0]; fr, fx = (s, e) if k == 0 else (e, s)   # free end, fixed end
        L = math.dist(fr, fx)
        # junctions along the track: ends of other copper lying on it, vias on it, pads touching it (not at the fixed end)
        js = []
        for u in others:
            for q in ((mm(u.GetPosition()),) if isinstance(u, p.PCB_VIA) else (mm(u.GetStart()), mm(u.GetEnd()))):
                if (isinstance(u, p.PCB_VIA) or u.GetLayer() == t.GetLayer()) and t.HitTest(p.VECTOR2I(p.FromMM(q[0]), p.FromMM(q[1]))):
                    d = math.dist(fr, q)
                    if .01 < d < L - .01:
                        js.append(d)
        if not js:
            dead.add(t.m_Uuid.AsString()); changed = True; continue
        d = min(js); nx = (fr[0] + (fx[0] - fr[0]) * d / L, fr[1] + (fx[1] - fr[1]) * d / L)
        v = p.VECTOR2I(p.FromMM(nx[0]), p.FromMM(nx[1]))
        (t.SetStart if k == 0 else t.SetEnd)(v); shortened.append({'net': t.GetNetname(), 'from': [round(c, 3) for c in fr], 'to': [round(c, 3) for c in nx]})
        changed = True
    if not changed:
        break
info = [{'net': t.GetNetname(), 'start': [round(c, 3) for c in mm(t.GetStart())], 'end': [round(c, 3) for c in mm(t.GetEnd())], 'locked': t.IsLocked()}
        for t in b.GetTracks() if t.m_Uuid.AsString() in dead]
p.SaveBoard(str(fn), b)   # shortened ends; deletions at file level
tree = parse(fn.read_text(encoding='utf-8')); n0 = len(tree)
uid = lambda g: next((x[1] for x in g if isinstance(x, list) and x and x[0] == 'uuid'), None)
tree = [g for g in tree if not (isinstance(g, list) and g and g[0] == 'segment' and uid(g) in dead)]
assert n0 - len(tree) == len(dead), (n0 - len(tree), len(dead))
fn.write_text(dump(tree) + chr(10), encoding='utf-8')
b = p.LoadBoard(str(fn)); p.ZONE_FILLER(b).Fill(b.Zones()); b.BuildConnectivity(); after = b.GetConnectivity().GetUnconnectedCount(True)
if after > before:
    fn.write_bytes(BACKUP); print(f'trim aborted: unconnected {before} -> {after}; input board restored'); print(json.dumps({'removed': info, 'shortened': shortened})); sys.exit(3)
p.SaveBoard(str(fn), b)
# phase 2: what native DRC still calls track_dangling (it matches exact anchor points; phase 1 tests shapes), one piece at a time
import os, subprocess
CLI = os.environ.get('KICAD_CLI', str(Path(sys.executable).with_name('kicad-cli.exe'))); rep = P / 'routing/trim-drc.json'
for _ in range(10):
    subprocess.run([CLI, 'pcb', 'drc', '--format', 'json', '--severity-all', '--refill-zones', '-o', str(rep), str(fn)], check=True, stdout=subprocess.DEVNULL)
    hang = [i['uuid'] for v in json.loads(rep.read_text())['violations'] if v['type'] in ('track_dangling', 'via_dangling') for i in v['items']]   # P04 R3: an escape via the router did not use (copper on B.Cu only)
    if not hang:
        break
    keep = fn.read_bytes(); tree = parse(fn.read_text(encoding='utf-8'))
    tree = [g for g in tree if not (isinstance(g, list) and g and g[0] in ('segment', 'via') and uid(g) == hang[0])]
    fn.write_text(dump(tree) + chr(10), encoding='utf-8')
    bb = p.LoadBoard(str(fn)); p.ZONE_FILLER(bb).Fill(bb.Zones()); bb.BuildConnectivity()
    if bb.GetConnectivity().GetUnconnectedCount(True) > before:
        fn.write_bytes(keep); print('phase 2: removing', hang[0], 'would disconnect; kept'); break
    info.append({'drc_dangling_removed': hang[0]}); p.SaveBoard(str(fn), bb)
(P / 'routing/trimmed.json').write_text(json.dumps({'removed': info, 'shortened': shortened}, indent=1) + '\n')
print(f'trimmed: {len(info)} unused track pieces removed, {len(shortened)} shortened; unconnected {before} -> {after}')
