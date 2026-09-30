"""Prepare the Specctra DSN for Freerouting and freeze the pre-routed board (run once per DSN export, after route_critical.py).
- Power pours (BAT_IN, SW_COM, VSW, VMOTOR and the tab pours) become router keepouts: Freerouting 2.1 routes other nets through an
  exported 'plane' (P02 R3 lesson) and splits the pour. Pins that lie inside a pour of their own net leave the net list (the pour
  joins them); nets joined only by locked copper (REV_G, OFF_D, HOLD_C) leave it completely. Remote SW_COM and VLOG pins are routed
  to the locked anchors (R22.2 stub, C20.1 / R68.1).
- GND pins leave the net list: their pads stay obstacles; GND is made by the two pours after import (+ completion routes).
- Router-only keepouts 0.4 mm wide along the board edges (Freerouting does not know the copper-to-edge clearance, P03 R2 lesson).
"""
from pathlib import Path
import re, shutil, subprocess, sys, json
import pcbnew as p
P = Path(__file__).resolve().parents[1]; f = P / 'routing/P02.dsn'; d = f.read_text()
assert 'EDGE_STRIP' not in d, 'DSN already prepared; re-run route_critical.py first'
# Lokalnie 29.09 (Claude): GND wraca do listy sieci routera. Gdy łączyły ją tylko wylewki, po trasowaniu zostawało
# 7 wysp GND, których planer dokańczania nie domykał (przebieg w chmurze i pierwsza próba lokalna).
LOCKED_ONLY = {'/P02_REV_G', '/P02_OFF_D', 'P02_HOLD_C', 'P02_BAT_IN', 'P02_VSW', 'VMOTOR'}
b = p.LoadBoard(str(P / 'eda/P02.kicad_pcb'))
pours = [z for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() != 'GND']
inside = set()
for fp in b.GetFootprints():
    for a in fp.Pads():
        if any(z.GetNetCode() == a.GetNetCode() and z.Outline().Contains(a.GetPosition()) for z in pours):
            inside.add(f'{fp.GetReference()}-{a.GetNumber()}')
removed = {}


def fix(m):
    name, pins = m.group(2).strip('"'), m.group(3).split()
    keep = [] if name in LOCKED_ONLY else [x for x in pins if x not in inside]
    if len(keep) != len(pins):
        removed[name] = sorted(set(pins) - set(keep))
    return m.group(1) + '(pins ' + ' '.join(keep) + ')'


d = re.sub(r'(\(net ("[^"]+"|\S+)\s*\n\s*)\(pins ([^)]*)\)', fix, d)
d, k = re.subn(r'\(plane ', '(keepout ', d); assert k >= 7, k
S1 = json.loads((P.parents[0] / 'Format-S1/format-s1.json').read_text(encoding='utf-8')); W, H = S1['klasy']['L']['W'], S1['klasy']['L']['H']
e = .4; strips = [(0, 0, W, e), (0, H - e, W, H), (0, 0, e, H), (W - e, 0, W, H)]
add = ''.join(f'    (keepout "EDGE_STRIP" (polygon {L} 0  {x0 * 1000:.0f} {-y0 * 1000:.0f}  {x1 * 1000:.0f} {-y0 * 1000:.0f}  {x1 * 1000:.0f} {-y1 * 1000:.0f}  {x0 * 1000:.0f} {-y1 * 1000:.0f}))\n'
              for L in ('F.Cu', 'B.Cu') for x0, y0, x1, y1 in strips)
i = d.index('(keepout'); d = d[:i] + add.lstrip() + '    ' + d[i:]
f.write_text(d)
(P / 'routing/router-exclusions.json').write_text(json.dumps({'pours_as_keepouts': k, 'removed_pins': removed}, indent=1) + '\n')
shutil.copy2(P / 'eda/P02.kicad_pcb', P / 'routing/prerouted.kicad_pcb')
subprocess.run([sys.executable, str(P / 'src/set_rules.py')], check=True)
print('DSN:', k, 'pours as keepouts; pins removed from', len(removed), 'nets; edge keepout strips; pre-routed board frozen.')
