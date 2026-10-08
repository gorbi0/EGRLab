"""Prepare the Specctra DSN for Freerouting and freeze the pre-routed board (run once per DSN export, after route_critical.py).
P06 R2 (1.10.2026): P05 R3 version (GND plane mode, edge strips, board.ROUTER_KEEPOUT) with the power-pour handling of P02 R4:
- the force pours ECU_P1 / EGR_P1 (route_critical.py) become router keepouts: Freerouting 2.1 routes other nets through an exported
  'plane' and splits the pour (P02 R3 lesson). Their pins lie inside their own pours and the nets are complete, so they leave the net
  list, as do the Kelvin nets (locked RSH1 -> R1 / R2 -> U1): their pins stay obstacles. The P05 lesson (keepouts holding pins of
  nets the router still has to route leave it 20-105 connections open) does not apply: no routable pin lies in these keepouts;
- GND plane mode (P03 R6, 30.09): the DSN gets a GND plane on B.Cu and keeps the GND pins, the router joins each SMD GND pin to it;
  the real B.Cu pour is cut by B.Cu tracks, so stitch.py and the completion planner tie the islands;
- router-only keepouts 0.4 mm wide along the board edges (Freerouting does not know the copper-to-edge clearance, P03 R2 lesson) and
  board.ROUTER_KEEPOUT (pin-free areas: the RSH1 courtyard, the strip between the Kelvin lines). The rule areas (M3 zones, cable-tie
  anchors, B.Cu under RSH1) are exported by KiCad as keepouts;
- review 2.10: board.TOP_ONLY nets in a DSN class limited to F.Cu (top_only below).
"""
from pathlib import Path
import shutil, subprocess, sys, json, re, os
import pcbnew as p
P = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(Path(__file__).resolve().parent))
from board import NAME, W, H, ROUTER_KEEPOUT, FORCE, KELVIN, TOP_ONLY, GND_INNER
try:
    from board import IN2_SUPPLY
except ImportError:
    IN2_SUPPLY = {}
f = P / f'routing/{NAME}.dsn'; d = f.read_text()
assert 'EDGE_STRIP' not in d, 'DSN already prepared; re-run route_critical.py first'
GND_MODE = os.environ.get('EGRLAB_GND_MODE', 'plane')   # 'plane' (default since 30.09) or 'out' (GND pins out of the net list)
b = p.LoadBoard(str(P / f'eda/{NAME}.kicad_pcb'))
pours = [z for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() != 'GND']
assert {z.GetNetname().split('/')[-1] for z in pours} == set(FORCE), 'force pours missing (route_critical.py)'
inside = set()
for fp in b.GetFootprints():
    for a in fp.Pads():
        if any(z.GetNetCode() == a.GetNetCode() and z.Outline().Contains(a.GetPosition()) for z in pours):
            inside.add(f'{fp.GetReference()}-{a.GetNumber()}')
LOCKED_ONLY = set(FORCE) | set(KELVIN)
removed = {}


def fix(m):
    name, pins = m.group(2).strip('"'), m.group(3).split()
    keep = [] if name.split('/')[-1] in LOCKED_ONLY else [x for x in pins if x not in inside]
    if len(keep) != len(pins):
        removed[name] = sorted(set(pins) - set(keep))
    return m.group(1) + '(pins ' + ' '.join(keep) + ')'


d = re.sub(r'(\(net ("[^"]+"|\S+)\s*\n\s*)\(pins ([^)]*)\)', fix, d)
d, k = re.subn(r'\(plane ', '(keepout ', d); assert k >= 2 * len(FORCE), k   # each force pour on F.Cu and B.Cu (+ PGND on In1.Cu, P07 S1 4 layers)
d, kp = re.subn(r'\(layer In1\.Cu\s*\n\s*\(type signal\)', '(layer In1.Cu\n      (type power)', d); assert kp == 1, kp   # 6.10: In1 = GND plane, no routing
# M1 (P05 R3): the GND pins of U3 (LQFP-64) are tied inwards to the F.Cu pour inside the pad ring and its vias (route_u3): out of the GND net
m_ = re.search(r'(\(net GND\s*\n\s*\(pins )([^)]*)\)', d); assert m_
d = d[:m_.start(2)] + ' '.join(q for q in m_.group(2).split() if not any(q.startswith(r + '-') for r in GND_INNER)) + d[m_.end(2):]
if GND_MODE == 'out':
    d, ng = re.subn(r'(\(net GND\s*\n\s*)\(pins [^)]*\)', r'\1(pins)', d); assert ng == 1, ng
e = .4; strips = [(0, 0, W, e), (0, H - e, W, H), (0, 0, e, H), (W - e, 0, W, H)]
add = ''.join(f'    (keepout "EDGE_STRIP" (polygon {L} 0  {x0 * 1000:.0f} {-y0 * 1000:.0f}  {x1 * 1000:.0f} {-y0 * 1000:.0f}  {x1 * 1000:.0f} {-y1 * 1000:.0f}  {x0 * 1000:.0f} {-y1 * 1000:.0f}))\n'
              for L in ('F.Cu', 'In2.Cu', 'B.Cu') for x0, y0, x1, y1 in strips)
add += ''.join(f'    (keepout "SHUNT_KELVIN" (polygon {L} 0  {x0 * 1000:.0f} {-y0 * 1000:.0f}  {x1 * 1000:.0f} {-y0 * 1000:.0f}  {x1 * 1000:.0f} {-y1 * 1000:.0f}  {x0 * 1000:.0f} {-y1 * 1000:.0f}))\n'
               for L, x0, y0, x1, y1 in ROUTER_KEEPOUT + [('In2.Cu', *r[1:]) for r in ROUTER_KEEPOUT if r[0] == 'F.Cu' and r in __import__('board').KELVIN_KEEPOUT])
i = d.index('(keepout'); d = d[:i] + add.lstrip() + '    ' + d[i:]
if GND_MODE == 'plane':   # the router joins every GND pin to this B.Cu plane (SMD pins: short stub + via where it finds room)
    m = .5; pl = f'    (plane GND (polygon In1.Cu 0  {m * 1000:.0f} {-m * 1000:.0f}  {(W - m) * 1000:.0f} {-m * 1000:.0f}  {(W - m) * 1000:.0f} {-(H - m) * 1000:.0f}  {m * 1000:.0f} {-(H - m) * 1000:.0f}))\n'
    i = d.index('(keepout'); d = d[:i] + pl.lstrip() + '    ' + d[i:]
# 6.10 evening (P07 4 layers): the In2 supply regions as planes (board.IN2_SUPPLY); not obstacles for the other nets (P02 lesson), so
# the router still uses In2 for signals; inner_zones.py then fills the real zones round those tracks and the planner ties the pieces
nets_dsn = {m.strip('"').split('/')[-1]: m for m in re.findall(r'\(net ("[^"]+"|[^\s()]+)\s*\n\s*\(pins', d)}
# 7.10: off by default. With the planes the router joined each supply pin to its plane by a via and left the rest; the real In2 zones
# (inner_zones.py) were then cut into pieces by the In2 signal tracks: 12 of the 25 open connections of the first 7.10 run were
# 3V3A_P07 / 5VA_P07 / 3V3_IO / 5V_SYS pieces (the 6.10 run without the planes had 4). The supplies are routed as nets of the PWR class.
for n_, rects in (IN2_SUPPLY.items() if os.environ.get('EGRLAB_IN2_PLANES') == '1' else []):
    for x0, y0, x1, y1 in rects:
        pl = f'    (plane {nets_dsn[n_]} (polygon In2.Cu 0  {x0 * 1000:.0f} {-y0 * 1000:.0f}  {x1 * 1000:.0f} {-y0 * 1000:.0f}  {x1 * 1000:.0f} {-y1 * 1000:.0f}  {x0 * 1000:.0f} {-y1 * 1000:.0f}))\n'
        i = d.index('(keepout'); d = d[:i] + pl.lstrip() + '    ' + d[i:]


def top_only(d):
    """Review 2.10 (F3): the nets of board.TOP_ONLY leave their DSN class for a copy limited to F.Cu ((circuit (use_layer F.Cu)), read by
    Freerouting 2.1 as the active routing layers of the class; its per-layer costs in (autoroute_settings) are ignored, tried 2.10)."""
    i0 = d.index('    (class '); i1 = d.index('  (wiring')
    out = ''; moved = []
    for name, nets, body in re.findall(r'    \(class (\S+)((?:\s+(?:"[^"]*"|[^\s()]+))*)\s*\n(.*?)\n    \)\n', d[i0:i1], re.S):
        toks = re.findall(r'"[^"]*"|[^\s()]+', nets); sel = [t for t in toks if t.strip('"').split('/')[-1] in TOP_ONLY]
        out += f'    (class {name} ' + ' '.join(t for t in toks if t not in sel) + '\n' + body + '\n    )\n'
        if sel:
            assert '(use_via' in body, body
            out += f'    (class TOP_{name} ' + ' '.join(sel) + '\n' + body.replace('(use_via', '(use_layer F.Cu)\n        (use_via', 1) + '\n    )\n'
            moved += sel
    assert sorted(t.strip('"').split('/')[-1] for t in moved) == sorted(TOP_ONLY), (moved, TOP_ONLY)
    return d[:i0] + out + '  )\n' + d[i1:], moved


d, top = top_only(d) if TOP_ONLY else (d, [])
# 6.10 evening (P07 4 layers): the stitching vias of the force nets (route_critical.py) leave the wiring: their nets have no pins in the DSN,
# yet Freerouting 2.1 tried to join the vias of a net to each other (124 'unrouted' via pairs, T_EGR_P3 tracks between lane vias on In2,
# an attempt with 93 open connections). Each becomes an octagonal keepout on In1 / In2 (an obstacle there; on F.Cu / B.Cu it stands in
# its own pour, already a keepout).
FORCE_VIA = re.compile(r'^\s*\(via "[^"]+"\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s+\(net ("[^"]+"|[^)\s]+)\)\(type fix\)\)\s*$', re.M)
fv = []


def drop_force_via(m):
    if m.group(3).strip('"').split('/')[-1] in FORCE:
        fv.append((float(m.group(1)), float(m.group(2)))); return ''
    return m.group(0)


d = FORCE_VIA.sub(drop_force_via, d)
d = re.sub(r'\n\s*\n', '\n', d)
r_ = 450 + 50   # um: via radius + 0.05 mm


def octagon(L, x, y):
    import math as _m
    pts = '  '.join(f'{x + r_ * _m.cos(k * _m.pi / 4 + _m.pi / 8):.0f} {y + r_ * _m.sin(k * _m.pi / 4 + _m.pi / 8):.0f}' for k in range(9))
    return f'    (keepout "FORCE_VIA" (polygon {L} 0  {pts}))\n'


i = d.index('(keepout'); d = d[:i] + ''.join(octagon(L, x, y) for x, y in fv for L in ('In2.Cu',)).lstrip() + '    ' + d[i:]
assert fv, 'no force stitching vias found in the DSN wiring'

f.write_text(d)
nk = d.count('(keepout ')
(P / 'routing/router-exclusions.json').write_text(json.dumps({'pours_as_keepouts': k, 'removed_pins': removed, 'router_keepouts': ROUTER_KEEPOUT,
                                                             'keepouts_in_dsn': nk, 'edge_strips': len(strips) * 2, 'gnd_mode': GND_MODE, 'top_only': top, 'force_vias_as_in2_keepouts': len(fv)}, indent=1) + '\n')
shutil.copy2(P / f'eda/{NAME}.kicad_pcb', P / 'routing/prerouted.kicad_pcb')
subprocess.run([sys.executable, str(P / 'src/set_rules.py')], check=True)
print('DSN:', k, 'force pours as keepouts;', len(fv), 'force stitching vias as In2 keepouts;', nk, 'keepouts in all; pins removed from', len(removed), 'nets;', len(top), 'nets on F.Cu only; pre-routed board frozen.')
