"""Prepare the Specctra DSN for Freerouting and freeze the pre-routed board.
GND pins are taken out of the router's net list (their pads stay obstacles): GND is made by the two pours
after import. Freerouting 2.1 '-inc' would keep them in the unrouted count and run to pass 999 (P02 lesson).
Run once per DSN export (route_critical.py): it refuses an already prepared DSN.
"""
from pathlib import Path
import re, shutil, subprocess, sys
P = Path(__file__).resolve().parents[1]; f = P / 'routing/P03.dsn'; d = f.read_text()
assert not re.search(r'\(net GND\s*\n\s*\(pins\)', d), 'DSN already prepared; re-run route_critical.py first'
d, k = re.subn(r'(\(net GND\s*\n\s*)\(pins [^)]*\)', r'\1(pins)', d); assert k == 1
f.write_text(d)
shutil.copy2(P / 'eda/P03.kicad_pcb', P / 'routing/prerouted.kicad_pcb')
subprocess.run([sys.executable, str(P / 'src/set_rules.py')], check=True)
print('DSN: GND pins removed from the router net list; pre-routed board frozen.')
