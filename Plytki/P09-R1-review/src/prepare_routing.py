"""Freeze pre-route. Ground pads remain obstacles and receive copper pours plus audited completion tracks."""
from pathlib import Path
import re,shutil,subprocess,sys
P=Path(__file__).resolve().parents[1];f=P/'routing/P09.dsn';d=f.read_text()
# P09: route GND pins too; independent copper check will still audit the filled plane.
f.write_text(d);shutil.copy2(P/'eda/P09.kicad_pcb',P/'routing/prerouted.kicad_pcb')
subprocess.run([sys.executable,str(P/'src/set_rules.py')],check=True)
