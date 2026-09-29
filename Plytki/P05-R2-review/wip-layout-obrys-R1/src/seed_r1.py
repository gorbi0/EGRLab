"""P05 R2: seed the board after route_critical.py with the copper of the closed R1 layout
(reference/P05-R1.kicad_pcb = Plytki/P05-R1-review/eda/P05.kicad_pcb), so R2 differs from R1 only locally.
Not seeded:
  - copper of RESET nets (all re-laid in R2: decoupling, test pads, DOUT outside the U1 outline);
  - every R1 item that touches a CHANGE rectangle (U1 right side, column A/B, the AVCC spine under the body);
  - items identical to copper already laid by route_critical.py;
  - items that collide with R2 copper or rule areas (native DRC, repeated until no seeded item collides).
Free ends left by the cut stay: complete_r2.py joins them (short links), prune_dangling.py removes the rest.
Seeded items are UNLOCKED (router copper, as in R1). Missing links are closed by complete_r2.py.
Writes routing/seed.json (counts and the list of dropped R1 items)."""
from pathlib import Path
import pcbnew as p, json, subprocess, os, sys, collections
P = Path(__file__).resolve().parents[1]; fn = P / 'eda/P05.kicad_pcb'
CLI = os.environ.get('KICAD_CLI', str(Path(sys.executable).with_name('kicad-cli.exe')))
RESET = {'REFCAP', 'ADC_REF', 'REGCAP_A', 'REGCAP_D', 'AD_DOUT_LOCAL'}
CHANGE = [(112.6, 33.2, 127.0, 58.5, 'right side, columns A/B, test pads'),
          (103.0, 40.35, 112.9, 46.0, 'AVCC spine and ground vias under U1'),
          (100.3, 40.3, 101.6, 41.6, 'pin 2 ground via')]
RENAME = {'VPROT_SENSE': 'VBAT_SENSE'}
COPPER = {'clearance', 'shorting_items', 'tracks_crossing', 'hole_clearance', 'copper_edge_clearance', 'items_not_allowed',
          'hole_to_hole', 'annular_width', 'via_diameter', 'track_width', 'solder_mask_bridge'}


def short(n): return RENAME.get(n.split('/')[-1], n.split('/')[-1])


def sig(t):
    if isinstance(t, p.PCB_VIA):
        return ('via', short(t.GetNetname()), round(p.ToMM(t.GetPosition().x), 4), round(p.ToMM(t.GetPosition().y), 4))
    e = sorted([(round(p.ToMM(t.GetStart().x), 4), round(p.ToMM(t.GetStart().y), 4)), (round(p.ToMM(t.GetEnd().x), 4), round(p.ToMM(t.GetEnd().y), 4))])
    return ('track', short(t.GetNetname()), t.GetLayer(), round(p.ToMM(t.GetWidth()), 4), *e)


def touches(t):
    bb = t.GetBoundingBox(); a = [p.ToMM(bb.GetLeft()), p.ToMM(bb.GetTop()), p.ToMM(bb.GetRight()), p.ToMM(bb.GetBottom())]
    return next((r[4] for r in CHANGE if a[0] <= r[2] and a[2] >= r[0] and a[1] <= r[3] and a[3] >= r[1]), None)


def drc(path):
    rep = P / 'routing/seed-drc.json'
    subprocess.run([CLI, 'pcb', 'drc', '--format', 'json', '--severity-all', '--all-track-errors', '--refill-zones', '-o', str(rep), str(path)], check=True, capture_output=True)
    return json.loads(rep.read_text())


b = p.LoadBoard(str(fn)); r1 = p.LoadBoard(str(P / 'reference/P05-R1.kicad_pcb'))
nets = collections.defaultdict(list)
for code, n in b.GetNetsByNetcode().items():
    if code: nets[short(n.GetNetname())].append(n)
assert all(len(v) == 1 for v in nets.values()), [k for k, v in nets.items() if len(v) > 1]
have = {sig(t) for t in b.GetTracks()}
report = {'reset_nets': sorted(RESET), 'change_rectangles': CHANGE, 'dropped': collections.Counter(), 'seeded': 0}
dropped = []
for t in sorted(r1.GetTracks(), key=lambda t: json.dumps(sig(t))):
    n = short(t.GetNetname()); why = 'reset net' if n in RESET else touches(t) or ('same as R2 critical copper' if sig(t) in have else None)
    if why:
        report['dropped'][why] += 1; continue
    if isinstance(t, p.PCB_VIA):
        c = p.PCB_VIA(b); c.SetPosition(t.GetPosition()); c.SetWidth(t.GetWidth(p.F_Cu)); c.SetDrill(t.GetDrill())
        c.SetViaType(p.VIATYPE_THROUGH); c.SetLayerPair(p.F_Cu, p.B_Cu)
    else:
        c = p.PCB_TRACK(b); c.SetStart(t.GetStart()); c.SetEnd(t.GetEnd()); c.SetWidth(t.GetWidth()); c.SetLayer(t.GetLayer())
    c.SetNet(nets[n][0]); c.SetLocked(False); b.Add(c); report['seeded'] += 1
# GND pours on both faces exactly as R1 import_routing.py (fine-pitch SMD ground pads solid), so ground
# copper that ends in the pour is not taken for a free end.
gnd = b.FindNet('GND')
for layer in [p.F_Cu, p.B_Cu]:
    z = p.ZONE(b); z.SetLayer(layer); z.SetNet(gnd)
    z.SetLocalClearance(p.FromMM(.3)); z.SetMinThickness(p.FromMM(.25)); z.SetPadConnection(p.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(p.FromMM(.2)); z.SetThermalReliefSpokeWidth(p.FromMM(.35)); z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
    o = z.Outline(); o.NewOutline()
    for x, y in [(1, 1), (159, 1), (159, 119), (1, 119)]: o.Append(p.FromMM(x), p.FromMM(y))
    b.Add(z)
for f in b.GetFootprints():
    for a in f.Pads():
        if a.GetNetname() == 'GND' and a.GetAttribute() == p.PAD_ATTRIB_SMD: a.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
b.BuildConnectivity(); p.ZONE_FILLER(b).Fill(b.Zones())
p.SaveBoard(str(fn), b)
# collisions: drop seeded (unlocked) items only; locked R2 copper is never touched.
rounds = []
for k in range(30):
    d = drc(fn); bad = collections.Counter()
    ids = set()
    for v in d['violations']:
        if v['type'] in COPPER:
            for i in v['items']: ids.add(i['uuid'])
    b = p.LoadBoard(str(fn)); victims = [t for t in b.GetTracks() if t.m_Uuid.AsString() in ids and not t.IsLocked()]
    if not victims: break
    for t in victims:
        bad['via' if isinstance(t, p.PCB_VIA) else 'track'] += 1
        dropped.append({'round': k, 'net': short(t.GetNetname()), 'sig': list(map(str, sig(t)))})
    # remove on file level (pcbnew Remove() can break SWIG, see kicad-pipeline-quirks)
    uu = {t.m_Uuid.AsString() for t in victims}
    from sexpr import parse, dump
    tree = parse(fn.read_text(encoding='utf-8'))
    def keep(g):
        if not (isinstance(g, list) and g and g[0] in ('segment', 'via')): return True
        u = next((x for x in g if isinstance(x, list) and x and x[0] == 'uuid'), None)
        return not (u and u[1] in uu)
    tree = [g for g in tree if keep(g)]; fn.write_text(dump(tree) + '\n', encoding='utf-8')
    rounds.append(dict(bad))
report['collision_rounds'] = rounds; report['dropped'] = dict(report['dropped']); report['dropped_after_seeding'] = dropped
(P / 'routing/seed.json').write_text(json.dumps(report, indent=1) + '\n')
print('seeded', report['seeded'], 'not seeded', report['dropped'], 'rounds', rounds)
