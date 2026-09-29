"""Rebuild schematic and PCB in a fresh folder; reuse recorded routing, no PDFs."""
from pathlib import Path
import tempfile,shutil,subprocess,sys,os,json,hashlib
P=Path(__file__).resolve().parents[1]
dst=Path(tempfile.mkdtemp(prefix='P03-R5-clean-',dir=P.parent))
for folder in ['src','reference','docs']:
    shutil.copytree(P/folder,dst/folder,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
for folder in ['routing','verification']:(dst/folder).mkdir()
for f in ['P03.ses','P03-R3.ses']:shutil.copyfile(P/'routing'/f,dst/'routing'/f)
shutil.copyfile(P/'verification/rebuild-compare.py',dst/'verification/rebuild-compare.py')
cli=os.environ.get('KICAD_CLI',str(Path(sys.executable).with_name('kicad-cli.exe')))
with (dst/'rebuild.log').open('w',encoding='utf-8') as log:
    def run(*args):subprocess.run(list(map(str,args)),cwd=dst/'src',stdout=log,stderr=subprocess.STDOUT,check=True)
    run(sys.executable,'build_schematic.py')
    run(cli,'sch','erc','--severity-all','--format','json','-o',dst/'verification/erc.json',dst/'eda/P03.kicad_sch')
    run(cli,'sch','export','netlist','--format','kicadxml','-o',dst/'verification/P03.xml',dst/'eda/P03.kicad_sch')
    for f in ['verify_schematic.py','verify_function.py','verify_reset.py']:run(sys.executable,f)
    run(sys.executable,'run_layout.py','--reuse-ses')
    for f in ['silkscreen.py','set_rules.py','verify_pcb.py','check_revision.py']:run(sys.executable,f)
    # Regression: another schematic export used to wipe all PCB project settings.
    project=dst/'eda/P03.kicad_pro'
    project_before=project.read_bytes()
    run(sys.executable,'build_schematic.py')
    assert project.read_bytes()==project_before,'Schematic re-export erased/changed PCB settings'
    run(sys.executable,dst/'verification/rebuild-compare.py',P,dst)
report=json.loads((dst/'verification/standalone-rebuild.json').read_text())
report['method']='Fresh src/reference/docs + recorded SES; schematic, netlist, PCB rebuilt. ERC/DRC and functional/reset/revision checks rerun; PDFs not regenerated.'
report['schematic_reexport_preserves_project']=True
files=[f for folder in ['src','reference'] for f in (P/folder).rglob('*') if f.is_file() and f.suffix!='.pyc' and '__pycache__' not in f.parts]
files += [P/'routing/P03.ses',P/'routing/P03-R3.ses',P/'verification/rebuild-compare.py']
report['source_sha256']={f.relative_to(P).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(files)}
(P/'verification/standalone-rebuild.json').write_text(json.dumps(report,indent=2)+'\n')
shutil.copyfile(dst/'rebuild.log',P/'verification/standalone-run.log')
assert report['all_equal']
print('Independent schematic/PCB rebuild PASS:',dst)
