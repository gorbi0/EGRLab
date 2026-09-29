"""P03 R4: seed the board with the R3 router result (routing/P03-R3.ses) as LOCKED copper, so the R4 layout is the R3
layout plus the explicit change laid by route_critical.py (Schmitt buffer U6/R41/C15 in the reset line to P04).
REPLACED lists the R3 router wires that route_critical.py lays again in changed form; they are not seeded. Every other
R3 wire is seeded. A net whose seeded copper collides with the change (KiCad DRC on the seeded board: clearance, shorts,
crossings, holes, rule areas) joins the re-route set: its R3 copper is dropped and Freerouting routes it again; the
seeding is repeated until no seeded copper collides.
Writes routing/seed.json (re-route set, replaced wires, signatures of the seeded copper) and re-exports routing/P03.dsn.
Run after route_critical.py and before prepare_routing.py.
"""
from pathlib import Path
import pcbnew as p, json, re, shutil, subprocess, sys, os, math
from sexpr import parse, one, sub
from seed_sig import sig
P = Path(__file__).resolve().parents[1]; path = P / 'eda/P03.kicad_pcb'
CLI = os.environ.get('KICAD_CLI', 'C:/Program Files/KiCad/10.0/bin/kicad-cli.exe')
FORCED = set()  # R4: nothing is re-routed on purpose; the change is laid by hand in route_critical.py
# (net, end point, end point) of the R3 router wires replaced by route_critical.py (mm, board coordinates)
REPLACED = [('SUP_N', (6.5, 83.37), (34.29, 51.73)),            # branch M1.J1-3 -> J4.15, now ends at U6.2
            ('HW_ARMED_CORE', (15.2, 82.48), (11.43, 38.97))]   # M1.J3-8 -> U12.3, crosses the U6/R41 site
COPPER = {'clearance', 'shorting_items', 'tracks_crossing', 'hole_clearance', 'copper_edge_clearance', 'items_not_allowed',
          'solder_mask_bridge', 'hole_to_hole', 'annular_width', 'via_diameter', 'track_width'}
base = P / 'routing/critical-routed.kicad_pcb'
shutil.copy2(path, base)  # board after route_critical.py, kept to restart the seeding
s = parse((P / 'routing/P03-R3.ses').read_text()); lib = one(one(s, 'routes'), 'library_out'); pads = {}
for item in sub(lib, 'padstack'):
    pads.setdefault(item[1], item)
wires = [(nn[1], item) for nn in sub(one(one(s, 'routes'), 'network_out'), 'net') for item in nn[2:]]


def mmxy(x, y):
    return (float(x) / 10000, -float(y) / 10000)


def point(x, y):
    return p.VECTOR2I(p.FromMM(mmxy(x, y)[0]), p.FromMM(mmxy(x, y)[1]))


def replaced(name, item):
    if item[0] != 'wire':
        return None
    pth = one(item, 'path'); ends = [mmxy(*pth[3:5]), mmxy(*pth[-2:])]
    for k, (n, a, c) in enumerate(REPLACED):
        if name.split('/')[-1] == n and sorted(math.dist(e, q) < .001 for e in ends for q in (a, c)).count(True) == 2:
            return k
    return None


hits = [k for name, item in wires for k in [replaced(name, item)] if k is not None]
assert sorted(hits) == list(range(len(REPLACED))), ('each replaced R3 wire must be found exactly once', hits)


def seed(skip):
    # Restore the route_critical board IN PLACE and load it there: only next to eda/P03.kicad_pro does pcbnew see the
    # project rules. Loaded from routing/, the board fell back to 0.2 mm / 0.6-0.3 mm defaults, which went into the DSN
    # and into the collision DRC (first R4 attempt).
    shutil.copy2(base, path); b = p.LoadBoard(str(path)); added = {}
    for name, item in wires:
        if name.split('/')[-1] in skip or replaced(name, item) is not None:
            continue
        n = b.FindNet(name); assert n is not None and n.GetNetCode() != 0, name
        if item[0] == 'wire':
            path_ = one(item, 'path'); layer = p.F_Cu if path_[1] == 'F.Cu' else p.B_Cu
            for k in range(3, len(path_) - 2, 2):
                t = p.PCB_TRACK(b); t.SetNet(n); t.SetLayer(layer); t.SetWidth(p.FromMM(float(path_[2]) / 10000))
                t.SetStart(point(*path_[k:k + 2])); t.SetEnd(point(*path_[k + 2:k + 4])); t.SetLocked(True); b.Add(t); added[t.m_Uuid.AsString()] = t
        elif item[0] == 'via':
            ps = pads[item[1]]; circ = one(sub(ps, 'shape')[0], 'circle'); drill = float(re.search(r':([0-9.]+)_um', item[1])[1]) / 1000
            v = p.PCB_VIA(b); v.SetPosition(point(*item[2:4])); v.SetWidth(p.FromMM(float(circ[2]) / 10000)); v.SetDrill(p.FromMM(drill))
            v.SetViaType(p.VIATYPE_THROUGH); v.SetLayerPair(p.F_Cu, p.B_Cu); v.SetNet(n); v.SetLocked(True); b.Add(v); added[v.m_Uuid.AsString()] = v
        else:
            raise ValueError(item)
    b.BuildConnectivity(); p.SaveBoard(str(path), b)
    return b, added


reroute = set(FORCED); rounds = []
for k in range(8):
    b, added = seed(reroute)
    out = P / 'routing/seed-drc.json'
    subprocess.run([CLI, 'pcb', 'drc', '--format', 'json', '--severity-all', '-o', str(out), str(path)], check=True, stdout=subprocess.DEVNULL)
    d = json.loads(out.read_text())
    hit = sorted({added[i['uuid']].GetNetname().split('/')[-1] for v in d['violations'] if v['type'] in COPPER for i in v['items'] if i['uuid'] in added})
    rounds.append({'round': k + 1, 'seeded_items': len(added), 'colliding_nets': hit})
    print('seed round', k + 1, 'seeded', len(added), 'colliding nets', hit)
    if not hit:
        break
    reroute |= set(hit)
else:
    sys.exit('seeding did not converge: ' + json.dumps(rounds))
seeded = sorted(sig(t) for t in added.values())
(P / 'routing/seed.json').write_text(json.dumps({'source': 'routing/P03-R3.ses', 'forced': sorted(FORCED),
                                                 'replaced': [{'net': n, 'ends': [a, c]} for n, a, c in REPLACED],
                                                 'reroute_nets': sorted(reroute), 'rounds': rounds, 'seeded_count': len(seeded),
                                                 'seeded': seeded}, indent=1) + '\n')
nc = b.GetDesignSettings().m_NetSettings.GetDefaultNetclass()
assert abs(p.ToMM(nc.GetTrackWidth()) - .3) < 1e-6 and abs(p.ToMM(nc.GetClearance()) - .25) < 1e-6, 'project rules not loaded'
assert p.ExportSpecctraDSN(b, str(P / 'routing/P03.dsn'))
# Freerouting does not know the KiCad board-edge clearance (0.5 mm): the first R4 route ran HW_ARMED_CORE at x = 0.43 mm.
# Router-only keepout strips 0.4 mm wide along the four edges (track centre >= 0.8 mm); the board itself gets no zone.
dsn = P / 'routing/P03.dsn'; text = dsn.read_text(); W = 400
strips = [(0, 0, W, -120000), (160000 - W, 0, 160000, -120000), (0, 0, 160000, -W), (0, -120000 + W, 160000, -120000)]
extra = ''.join(f'    (keepout "" (polygon {L} 0  {x0} {y0}  {x1} {y0}  {x1} {y1}  {x0} {y1}))' + chr(10) for L in ('F.Cu', 'B.Cu') for x0, y0, x1, y1 in strips)
k = text.index('    (keepout ""'); dsn.write_text(text[:k] + extra + text[k:])
print('R3 copper seeded (locked) except', len(REPLACED), 'replaced wires and the nets', sorted(reroute) or 'none', '; DSN exported.')
