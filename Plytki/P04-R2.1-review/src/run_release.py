"""Rebuild P04-R2 from this package alone plus documented tools.

Default: reuse the bundled SES; --new-route requires EGRLAB_FREEROUTING.
--no-package performs every generation/check but leaves archive creation to caller.
"""
from pathlib import Path
import subprocess,sys,os,json
P=Path(__file__).resolve().parents[1]; PY=sys.executable
CLI=os.environ.get('KICAD_CLI',str(Path(PY).with_name('kicad-cli.exe')))
PDFTOPPM=os.environ.get('PDFTOPPM')
DOC_PY=os.environ.get('EGRLAB_DOC_PYTHON',PY)
if os.environ.get('KICAD_LIBRARY_ROOT'):
    os.environ.setdefault('KICAD10_3DMODEL_DIR',str(Path(os.environ['KICAD_LIBRARY_ROOT'])/'3dmodels'))

def run(*args,cwd=P/'src',quiet=False):
    print('>', ' '.join(str(a) for a in args),flush=True)
    opts={'stdout':subprocess.DEVNULL,'stderr':subprocess.DEVNULL} if quiet else {}
    subprocess.run([str(a) for a in args],cwd=cwd,check=True,**opts)

for folder in ('verification','routing','output/pdf','output/previews','output/fabrication'):
    (P/folder).mkdir(parents=True,exist_ok=True)
run(DOC_PY,'-c','import reportlab, PIL')
for old in ('verification/clean-rebuild.json','verification/release-check.json'):
    (P/old).unlink(missing_ok=True)
run(PY,'build_schematic.py');run(PY,'set_rules.py');run(PY,'make_tables.py')
run(CLI,'sch','erc','--severity-all','--format','json','-o','verification/erc.json','eda/P04.kicad_sch',cwd=P,quiet=True)
run(CLI,'sch','export','netlist','--format','kicadxml','-o','verification/P04.xml','eda/P04.kicad_sch',cwd=P,quiet=True)
run(PY,'verify_schematic.py');run(PY,'verify_electrical.py');run(PY,'verify_values.py')
run(CLI,'sch','export','pdf','-o','output/pdf/P04-R2-schemat.pdf','eda/P04.kicad_sch',cwd=P,quiet=True)
if PDFTOPPM:
    run(PDFTOPPM,'-png','-scale-to','2200','output/pdf/P04-R2-schemat.pdf','output/previews/sch-1',cwd=P,quiet=True)
run(PY,'run_layout.py',* ([] if '--new-route' in sys.argv else ['--reuse-ses']))
(P/'verification/silkscreen-placement.json').unlink(missing_ok=True)
run(PY,'silkscreen.py');run(PY,'set_rules.py')
run(PY,'verify_pcb.py');run(PY,'board_fingerprint.py');run(PY,'tools/ground_islands.py')
for side in ('top',):
    run(CLI,'pcb','render','--side',side,'--width','2400','--height','1800','--quality','basic',
        '-o',f'output/previews/render-{side}.png','eda/P04.kicad_pcb',cwd=P,quiet=True)
run(PY,'make_pdf.py')
if PDFTOPPM:
    run(PDFTOPPM,'-png','-scale-to','1800','output/pdf/P04-R2-PCB.pdf','output/previews/exported-pcb',cwd=P,quiet=True)
if '--no-package' not in sys.argv:run(PY,'package_release.py')
print('P04-R2 generation and automated checks complete. Physical fit and bench acceptance remain pending.')
