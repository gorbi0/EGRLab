"""Independent CAD-only rebuild; does not regenerate the already inspected R2 PDFs."""
from pathlib import Path
import tempfile, shutil, subprocess, sys, os, json, hashlib
P=Path(__file__).resolve().parents[1]
dst=Path(tempfile.mkdtemp(prefix='P04-R22-clean-',dir=P.parent))
for folder in ('src','input','reference','requirements','audit'):
    shutil.copytree(P/folder,dst/folder,ignore=shutil.ignore_patterns('__pycache__','*.pyc','datasheets'))
for folder in ('docs','routing','verification'): (dst/folder).mkdir()
for file in ('P04.ses','completion-routes.json'): shutil.copy2(P/'routing'/file,dst/'routing'/file)
cli=os.environ.get('KICAD_CLI',str(Path(sys.executable).with_name('kicad-cli.exe')))
with (dst/'rebuild.log').open('w',encoding='utf-8') as log:
    def run(args):
        subprocess.run([str(v) for v in args],cwd=dst/'src',stdout=log,stderr=subprocess.STDOUT,check=True)
    for s in ('build_schematic.py','set_rules.py','make_tables.py'):run([sys.executable,s])
    run([cli,'sch','erc','--severity-all','--format','json','-o',dst/'verification/erc.json',dst/'eda/P04.kicad_sch'])
    run([cli,'sch','export','netlist','--format','kicadxml','-o',dst/'verification/P04.xml',dst/'eda/P04.kicad_sch'])
    for s in ('verify_schematic.py','verify_electrical.py','verify_values.py'):run([sys.executable,s])
    run([sys.executable,'run_layout.py','--reuse-ses'])
    for s in ('silkscreen.py','set_rules.py','verify_pcb.py','board_fingerprint.py','tools/ground_islands.py'):run([sys.executable,s])
def read(base,file):return json.loads((base/'verification'/file).read_text())
original=read(P,'geometry-fingerprint.json');regenerated=read(dst,'geometry-fingerprint.json')
result={'rebuilt_directory':str(dst),'geometry_equal':original['sha256']==regenerated['sha256'],'original':original,'regenerated':regenerated,
        'schematic':read(dst,'schematic-check.json'),'checks':{n:all(c['pass'] for c in read(dst,n+'-checks.json')['checks']) for n in ('pcb','electrical','value')},
        'GND_clusters':len(read(dst,'ground-islands.json')),'scope':'Fresh schematic, BOM, netlist, routing replay, fill and native ERC/DRC; PDF generation excluded. Geometry digest ignores UUIDs; 0 DRC and 1 GND cluster additionally required.'}
files=[f for folder in ('src','input','reference','requirements') for f in (P/folder).rglob('*') if f.is_file() and f.suffix!='.pyc' and '__pycache__' not in f.parts]
files += [P/'routing/P04.ses',P/'routing/completion-routes.json']
result['source_sha256']={f.relative_to(P).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(files)}
(P/'verification/independent-rebuild.json').write_text(json.dumps(result,indent=2)+'\n')
assert result['geometry_equal'] and all(result['checks'].values()) and result['GND_clusters']==1, result
print('Independent CAD rebuild PASS:',dst)
