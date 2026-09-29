"""Regenerate from source inputs in a new sibling directory and compare PCB semantics."""
from pathlib import Path
import tempfile,shutil,subprocess,sys,json,hashlib,datetime
P=Path(__file__).resolve().parents[1]
dst=Path(tempfile.mkdtemp(prefix='P05-clean-',dir=P.parent))
for folder in ['src','input','reference','requirements']:
 shutil.copytree(P/folder,dst/folder,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
(dst/'docs').mkdir();(dst/'routing').mkdir();(dst/'eda/libraries').mkdir(parents=True)
for rel in ['routing/P05.ses','routing/completion-routes.json','routing/completion-targets.json']:shutil.copy2(P/rel,dst/rel)
for f in (P/'docs').glob('*.md'):shutil.copy2(f,dst/'docs'/f.name)
with (dst/'clean-build.log').open('w') as log:
 run=subprocess.run([sys.executable,str(dst/'src/run_release.py'),'--no-package'],stdout=log,stderr=subprocess.STDOUT)
if run.returncode:raise SystemExit('Clean rebuild failed: '+str(dst/'clean-build.log'))
def read(base,rel):return json.loads((base/rel).read_text())
actual=read(dst,'verification/geometry-fingerprint.json');original=read(P,'verification/geometry-fingerprint.json')
ok=actual['sha256']==original['sha256']
record={'date_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'directory':str(dst),'exit_code':run.returncode,'geometry_equal':ok,
 'original':original,'regenerated':actual,'schematic':read(dst,'verification/schematic-check.json'),
 'pcb_checks_pass':all(c['pass'] for c in read(dst,'verification/pcb-checks.json')['checks']),
 'electrical_checks_pass':all(c['pass'] for c in read(dst,'verification/electrical-checks.json')['checks'])}
(P/'verification/clean-rebuild.json').write_text(json.dumps(record,indent=2)+'\n')
assert ok,'Clean rebuild geometry differs; inspect '+str(dst)
print('Clean rebuild passed, identical PCB semantics:',dst)
