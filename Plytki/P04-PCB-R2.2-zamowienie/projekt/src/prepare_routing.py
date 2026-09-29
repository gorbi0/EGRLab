"""Freeze pre-route. Ground pads remain obstacles and receive copper pours plus audited completion tracks."""
from pathlib import Path
import re,shutil,subprocess,sys
P=Path(__file__).resolve().parents[1];f=P/'routing/P04.dsn';d=f.read_text()
d,k=re.subn(r'(\(net GND\s*\n\s*)\(pins [^)]*\)',r'\1(pins)',d);assert k==1
f.write_text(d);shutil.copy2(P/'eda/P04.kicad_pcb',P/'routing/prerouted.kicad_pcb')
subprocess.run([sys.executable,str(P/'src/set_rules.py')],check=True)
