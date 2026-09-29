"""Rebuild/review gate. Stops on native violations or failed independent checks."""
from pathlib import Path
import subprocess,sys,os,json
P=Path(__file__).resolve().parents[1];PY=sys.executable
CLI=os.environ.get('KICAD_CLI',str(Path(PY).with_name('kicad-cli.exe')))
def run(*args):
 print('>',*args,flush=True);subprocess.run([str(a) for a in args],cwd=P,check=True)
if '--rebuild' in sys.argv:run(PY,'src/build_schematic.py')
# A fresh .kicad_pro is required before ERC, otherwise KiCad ignores project-local library tables.
run(PY,'src/set_rules.py')
run(PY,'src/make_shopping.py')
run(CLI,'sch','export','netlist','--format','kicadxml','-o','verification/P09.xml','eda/P09.kicad_sch')
run(CLI,'sch','erc','--format','json','--severity-all','-o','verification/erc.json','eda/P09.kicad_sch')
run(PY,'src/verify_schematic.py');run(PY,'src/verify_electrical.py')
run(PY,'src/make_firmware_patch.py');run(PY,'src/test_temperature.py')
if '--rebuild' in sys.argv:
 run(PY,'src/run_layout.py','--reuse-ses');run(PY,'src/silkscreen.py')
run(PY,'src/verify_pcb.py');run(PY,'src/tools/ground_islands.py')
run(PY,'src/package_manifest.py','--paths-only')
from provenance import run_fresh_drc
d,r=run_fresh_drc(P/'eda/P09.kicad_pcb',P/'verification/drc.json')
assert all(v==0 for v in r['counts'].values()),r['counts']
run(PY,'src/board_fingerprint.py')
if '--no-pdf' not in sys.argv:
 run(CLI,'sch','export','pdf','-o','output/pdf/P09-R1-schemat.pdf','eda/P09.kicad_sch')
 run(PY,'src/make_pdf.py')
 print('Re-render and visually inspect both final PDFs before freezing the package.')
print('PASS: native ERC/DRC, parity, electrical/PCB contracts and negative controls.')
