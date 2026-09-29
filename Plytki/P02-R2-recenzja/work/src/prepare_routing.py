"""Prepare the Specctra DSN for Freerouting and freeze the pre-routed board.
- The VPROT input zone becomes an F.Cu keepout for the router (Freerouting 2.1 routed other nets
  through the exported 'plane'); in KiCad it stays a VPROT copper zone.
- GND and VPROT pins are taken out of the router's net list, so their pads are obstacles: every VPROT
  connection is already made by locked copper, GND is made by the two pours after import.
  (Freerouting 2.1 '-inc' keeps ignored nets in the unrouted count and runs to pass 999.)
Run once per DSN export (route_critical.py): it refuses an already prepared DSN.
"""
from pathlib import Path
import re, shutil, subprocess, sys
P = Path(__file__).resolve().parents[1]; f = P / 'routing/P02.dsn'; d = f.read_text()
assert 'VPROT_NODE' not in d, 'DSN already prepared; re-run route_critical.py first'
d, n = re.subn(r'\(plane VPROT \(polygon F\.Cu 0 ', '(keepout "VPROT_NODE" (polygon F.Cu 0 ', d); assert n == 1
for name in ('GND', 'VPROT'):
    d, k = re.subn(r'(\(net ' + name + r'\s*\n\s*)\(pins [^)]*\)', r'\1(pins)', d); assert k == 1, name
f.write_text(d)
shutil.copy2(P / 'eda/P02.kicad_pcb', P / 'routing/prerouted.kicad_pcb')
subprocess.run([sys.executable, str(P / 'src/set_rules.py')], check=True)
print('DSN: VPROT node is a router keepout; GND/VPROT pins removed from the router net list; pre-routed board frozen.')
