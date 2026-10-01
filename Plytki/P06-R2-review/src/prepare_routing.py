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
  anchors, B.Cu under RSH1) are exported by KiCad as keepouts.
"""
from pathlib import Path
import shutil, subprocess, sys, json, re, os
import pcbnew as p
P = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(Path(__file__).resolve().parent))
from board import NAME, CLASS, ROUTER_KEEPOUT, FORCE, KELVIN
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
d, k = re.subn(r'\(plane ', '(keepout ', d); assert k == 2 * len(FORCE), k   # each force pour on F.Cu and B.Cu
if GND_MODE == 'out':
    d, ng = re.subn(r'(\(net GND\s*\n\s*)\(pins [^)]*\)', r'\1(pins)', d); assert ng == 1, ng
S1 = json.loads((P.parents[0] / 'Format-S1/format-s1.json').read_text(encoding='utf-8')); W, H = S1['klasy'][CLASS]['W'], S1['klasy'][CLASS]['H']
e = .4; strips = [(0, 0, W, e), (0, H - e, W, H), (0, 0, e, H), (W - e, 0, W, H)]
add = ''.join(f'    (keepout "EDGE_STRIP" (polygon {L} 0  {x0 * 1000:.0f} {-y0 * 1000:.0f}  {x1 * 1000:.0f} {-y0 * 1000:.0f}  {x1 * 1000:.0f} {-y1 * 1000:.0f}  {x0 * 1000:.0f} {-y1 * 1000:.0f}))\n'
              for L in ('F.Cu', 'B.Cu') for x0, y0, x1, y1 in strips)
add += ''.join(f'    (keepout "SHUNT_KELVIN" (polygon {L} 0  {x0 * 1000:.0f} {-y0 * 1000:.0f}  {x1 * 1000:.0f} {-y0 * 1000:.0f}  {x1 * 1000:.0f} {-y1 * 1000:.0f}  {x0 * 1000:.0f} {-y1 * 1000:.0f}))\n'
               for L, x0, y0, x1, y1 in ROUTER_KEEPOUT)
i = d.index('(keepout'); d = d[:i] + add.lstrip() + '    ' + d[i:]
if GND_MODE == 'plane':   # the router joins every GND pin to this B.Cu plane (SMD pins: short stub + via where it finds room)
    m = .5; pl = f'    (plane GND (polygon B.Cu 0  {m * 1000:.0f} {-m * 1000:.0f}  {(W - m) * 1000:.0f} {-m * 1000:.0f}  {(W - m) * 1000:.0f} {-(H - m) * 1000:.0f}  {m * 1000:.0f} {-(H - m) * 1000:.0f}))\n'
    i = d.index('(keepout'); d = d[:i] + pl.lstrip() + '    ' + d[i:]
f.write_text(d)
nk = d.count('(keepout ')
(P / 'routing/router-exclusions.json').write_text(json.dumps({'pours_as_keepouts': k, 'removed_pins': removed, 'router_keepouts': ROUTER_KEEPOUT,
                                                             'keepouts_in_dsn': nk, 'edge_strips': len(strips) * 2, 'gnd_mode': GND_MODE}, indent=1) + '\n')
shutil.copy2(P / f'eda/{NAME}.kicad_pcb', P / 'routing/prerouted.kicad_pcb')
subprocess.run([sys.executable, str(P / 'src/set_rules.py')], check=True)
print('DSN:', k, 'force pours as keepouts;', nk, 'keepouts in all; pins removed from', len(removed), 'nets; pre-routed board frozen.')
