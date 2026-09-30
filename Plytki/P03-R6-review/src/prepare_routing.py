"""Prepare the Specctra DSN for Freerouting and freeze the pre-routed board (run once per DSN export, after route_critical.py).
P03 R6 has no power pours before routing (GND pours come after the import), so unlike P02 R4 nothing is turned from 'plane'
into a keepout: the locked 5 V copper is exported as fixed wiring and the router only adds the missing connections.
GND pins leave the net list (their pads stay obstacles): with GND in the list (the P02 R4 way) Freerouting routed ~120 GND pins
as tracks, a pass took up to 4 minutes and 48 signal connections stayed open after 15 passes (30.09, first run). GND is made
by the two pours after the import, the stitching vias and the completion planner (stitch.py stage 3, complete_routes.py).
Router-only keepouts 0.4 mm wide along the board edges (Freerouting does not know the copper-to-edge
clearance, P03 R2 lesson). The rule areas (M3 zones, ANTENNA M1, SD1 M2.5) are exported by KiCad as keepouts.
"""
from pathlib import Path
import shutil, subprocess, sys, json, re
P = Path(__file__).resolve().parents[1]; f = P / 'routing/P03.dsn'; d = f.read_text()
assert 'EDGE_STRIP' not in d, 'DSN already prepared; re-run route_critical.py first'
assert '(plane ' not in d, 'unexpected plane in the P03 DSN'
d, ng = re.subn(r'(\(net GND\s*\n\s*)\(pins [^)]*\)', r'\1(pins)', d); assert ng == 1, ng
S1 = json.loads((P.parents[0] / 'Format-S1/format-s1.json').read_text(encoding='utf-8')); W, H = S1['klasy']['L']['W'], S1['klasy']['L']['H']
e = .4; strips = [(0, 0, W, e), (0, H - e, W, H), (0, 0, e, H), (W - e, 0, W, H)]
add = ''.join(f'    (keepout "EDGE_STRIP" (polygon {L} 0  {x0 * 1000:.0f} {-y0 * 1000:.0f}  {x1 * 1000:.0f} {-y0 * 1000:.0f}  {x1 * 1000:.0f} {-y1 * 1000:.0f}  {x0 * 1000:.0f} {-y1 * 1000:.0f}))\n'
              for L in ('F.Cu', 'B.Cu') for x0, y0, x1, y1 in strips)
i = d.index('(keepout'); d = d[:i] + add.lstrip() + '    ' + d[i:]
f.write_text(d)
nk = d.count('(keepout ')
(P / 'routing/router-exclusions.json').write_text(json.dumps({'keepouts_in_dsn': nk, 'edge_strips': len(strips) * 2, 'gnd_pins_removed': True}, indent=1) + '\n')
shutil.copy2(P / 'eda/P03.kicad_pcb', P / 'routing/prerouted.kicad_pcb')
subprocess.run([sys.executable, str(P / 'src/set_rules.py')], check=True)
print('DSN:', nk, 'keepouts (rule areas + edge strips); pre-routed board frozen.')
