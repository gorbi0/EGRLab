"""Freeze pre-route. Ground pads remain obstacles and receive copper pours plus audited completion tracks."""
from pathlib import Path
import re,shutil,subprocess,sys
P=Path(__file__).resolve().parents[1];f=P/'routing/P11.dsn';d=f.read_text()
# Python board loading does not automatically import .kicad_pro netclass settings.
# Audit actual router input, independently of the final KiCad design rules.
assert re.findall(r'\(width\s+(\d+)\)',d)==['300','300'],'DSN width'
assert re.findall(r'\(clearance\s+(\d+)\)',d)==['250','250'],'DSN net clearance'
assert re.findall(r'\(use_via\s+"([^"]+)"\)',d)==['Via[0-1]_800:400_um'],'DSN via'
# P11: route GND pins too; independent copper check will still audit the filled plane.
f.write_text(d);shutil.copy2(P/'eda/P11.kicad_pcb',P/'routing/prerouted.kicad_pcb')
subprocess.run([sys.executable,str(P/'src/set_rules.py')],check=True)
