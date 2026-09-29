"""One fail-closed acceptance/export command, run with KiCad Python.
Run --rebuild to regenerate the local R2->R3 changes, models and assembly overlay.
No hardware acceptance is inferred from these checks.
"""
from pathlib import Path
import argparse,subprocess,sys,json,hashlib,datetime
from provenance import inputs,current_receipt
P=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--rebuild',action='store_true');a.add_argument('--docs-python',required=True);a.add_argument('--node',required=True);a.add_argument('--sharp-module',required=True);args=a.parse_args()
def run(py,script,*extra):
 r=subprocess.run([str(py),str(P/'src'/script),*map(str,extra)],capture_output=True,text=True)
 (P/'verification'/('run-'+script+'.log')).write_text(r.stdout+'\n'+r.stderr)
 if r.returncode:raise RuntimeError(script+' failed; see verification/run-'+script+'.log')
 print(script+' OK',flush=True)
status=P/'verification/release-status.json'
status.write_text(json.dumps({'state':'RUNNING','hardware':'NOT_TESTED'})+'\n')
try:
 if args.rebuild:
  for name in ['build_r3.py','add_models.py','assembly_bom.py']:run(sys.executable,name)
 run(sys.executable,'verify_pcb.py')
 receipt=json.loads((P/'verification/drc.provenance.json').read_text());assert current_receipt(receipt)
 before=inputs()
 run(sys.executable,'negative_controls.py')
 run(sys.executable,'export_views.py')
 run(args.node,'rasterize.mjs',P,args.sharp_module)
 run(args.docs_python,'make_pdf.py')
 assert before==inputs(),'Design inputs changed after DRC, abort export acceptance'
 assert current_receipt(receipt),'DRC report no longer matches inputs'
 products={f.relative_to(P).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in (P/'output').rglob('*') if f.is_file()}
 status.write_text(json.dumps({'state':'DIGITAL_CHECKS_PASS','hardware':'NOT_TESTED','physical_fit':'NOT_TESTED','production_export':'PENDING_PHYSICAL_FIT',
  'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'inputs':before,'outputs':products},indent=2)+'\n')
 print('Digital checks and exports PASS. Physical fit and bench tests remain NOT_TESTED.')
except Exception as exc:
 status.write_text(json.dumps({'state':'FAILED','error':str(exc),'hardware':'NOT_TESTED'},indent=2)+'\n');raise
