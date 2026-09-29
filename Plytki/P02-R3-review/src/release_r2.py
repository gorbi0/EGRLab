"""Rebuild (optional), verify and export P02-R3 (script name kept from R2). No automatic fabrication release.
Run with KiCad Python. Set EGRLAB_PDF_PYTHON, EGRLAB_NODE, EGRLAB_SHARP, PDFTOPPM.
Default validates current reviewed CAD. --rebuild imports recorded SES; --new-route reroutes.
"""
from pathlib import Path
import sys,os,subprocess
P=Path(__file__).resolve().parents[1];PY=sys.executable;CLI=Path(PY).with_name('kicad-cli.exe')
dep=Path('C:/Users/tgorbacz/.cache/codex-runtimes/codex-primary-runtime/dependencies')
PDFPY=os.environ.get('EGRLAB_PDF_PYTHON',str(dep/'python/python.exe'))
NODE=os.environ.get('EGRLAB_NODE',str(dep/'node/bin/node.exe'));SHARP=os.environ.get('EGRLAB_SHARP',str(dep/'node/node_modules/sharp'))
RENDER=os.environ.get('PDFTOPPM',str(dep/'native/poppler/Library/bin/pdftoppm.exe'))
def run(name,*cmd):
 r=subprocess.run([str(x) for x in cmd],cwd=P,capture_output=True,text=True,encoding='utf-8',errors='replace')
 (P/'verification'/('run-'+name+'.log')).write_text(r.stdout+'\n'+r.stderr,encoding='utf-8')
 if r.returncode:raise RuntimeError(name+' FAILED; see verification/run-'+name+'.log')
 print(name,'PASS',flush=True)
if '--rebuild' in sys.argv or '--new-route' in sys.argv:
 run('schematic-build',PY,'src/build_schematic.py')
run('erc',CLI,'sch','erc','--severity-all','--format','json','-o','verification/erc.json','eda/P02.kicad_sch')
run('netlist',CLI,'sch','export','netlist','--format','kicadxml','-o','verification/P02.xml','eda/P02.kicad_sch')
run('schematic-check',PY,'src/verify_schematic.py')
run('electrical-check',PY,'src/check_electrical.py','--negative')
if '--rebuild' in sys.argv or '--new-route' in sys.argv:
 run('layout',PY,'src/run_layout.py',*([] if '--new-route' in sys.argv else ['--reuse-ses']))
 run('silk',PY,'src/silkscreen.py');run('rules',PY,'src/set_rules.py');run('models',PY,'src/add_models.py')
run('revision-check',PY,'src/check_revision.py')
run('pcb-check',PY,'src/verify_pcb.py');run('negative-controls',PY,'src/negative_controls.py')
run('views',PY,'src/export_views.py')
run('rasterize',NODE,'src/rasterize.mjs',str(P),SHARP)
run('schematic-pdf',CLI,'sch','export','pdf','-o','output/pdf/P02-R3-schemat.pdf','eda/P02.kicad_sch')
run('pcb-pdf',PDFPY,'src/make_pdf.py')
for name,stub in [('P02-R3-schemat','sch'),('P02-R3-PCB','pdf')]:
 run('render-'+stub,RENDER,'-scale-to','1800','-png','output/pdf/'+name+'.pdf','output/previews/'+stub)
print('Review exports ready. Inspect every final PDF page, then package_review.py.')
