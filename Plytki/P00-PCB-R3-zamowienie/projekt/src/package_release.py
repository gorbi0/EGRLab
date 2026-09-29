"""Package only final files, checking fresh provenance and results first."""
from pathlib import Path
import hashlib,json,zipfile
from provenance import inputs
P=Path(__file__).resolve().parents[1]
def read(rel):return json.loads((P/rel).read_text(encoding='utf-8'))
sch=read('verification/schematic-check.json');pcb=read('verification/pcb-checks.json');elec=read('verification/electrical-checks.json')
har=read('verification/harness-checks.json');rev=read('verification/revision-checks.json');vis=read('verification/pdf-visual-review.json')
assert not sch['errors'] and not sch['extra'] and not sch['erc_violations']
assert pcb['passed']==pcb['total'] and elec['passed']==elec['total'] and har['passed']==har['total'] and rev['passed']
for rel in ('verification/negative-controls.json','verification/electrical-negative-controls.json','verification/harness-negative-controls.json'):
    assert all(c['detected'] for c in read(rel))
assert read('verification/drc.provenance.json')['inputs']==inputs(), 'Checks are stale: rerun verify_pcb.py'
assert hashlib.sha256((P/'eda/P00.kicad_pcb').read_bytes()).hexdigest()==pcb['board_sha256']
for name,meta in vis['pdfs'].items():  # visual review must name the exact final PDFs
    assert hashlib.sha256((P/'output/pdf'/name).read_bytes()).hexdigest()==meta['sha256'], 'visual review stale: '+name
fabrication=P/'output/fabrication'
assert len(list(fabrication.glob('*.g??')))==7, 'Seven Gerber layers expected'
assert len(list(fabrication.glob('*.drl')))==2, 'Separate PTH / NPTH drills expected'
skip={'tmp','__pycache__','negative-controls'}
files=sorted(f for f in P.rglob('*') if f.is_file() and not any(x in skip for x in f.relative_to(P).parts)
             and f.suffix not in ('.lck','.kicad_prl','.pyc','.zip') and f.name!='release-manifest.json'
             and not f.name.endswith('-run.log') and f.name!='sch-new.png'
             and not (f.parent.name=='pdf' and f.name.startswith('P00-R2-')))  # stale R2 PDFs from the copied folder
manifest={'package':'P00-R3-review','date':'2026-09-27','status':'closing revision (copper = R2); hardware/fit pending','files':
    {f.relative_to(P).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in files}}
(P/'release-manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
z=P.parent/'P00-R3-review.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as archive:
    for f in files+[P/'release-manifest.json']:archive.write(f,'P00-R3-review/'+f.relative_to(P).as_posix())
with zipfile.ZipFile(z) as archive:
    for rel,digest in manifest['files'].items():
        assert hashlib.sha256(archive.read('P00-R3-review/'+rel)).hexdigest()==digest
print('Release manifest and ZIP verified:',len(files),'files;',z)
