"""Bind checks, immutable CAD, CAM, ZIP and document manifest; run after visual review.
No new PASS is inferred for hardware or physical fit.
"""
from pathlib import Path
import datetime, hashlib, json, sys, zipfile

R=Path(__file__).resolve().parents[1]
P=R/'projekt'
sys.path.insert(0,str(P/'src'))
from provenance import current_receipt
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def read(f):return json.loads(f.read_text(encoding='utf-8'))
def write(f,data):f.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
pcb=P/'eda/P01.kicad_pcb'
pcb_sha=sha(pcb)
receipt=read(P/'verification/drc.provenance.json')
assert current_receipt(receipt) and all(n==0 for n in receipt['counts'].values()),'DRC no longer current'
checks=read(P/'verification/pcb-checks.json')
negative=read(P/'verification/negative-controls.json')
cam=read(R/'verification/cam-checks.json')
assert checks['pass'] and all(c['pass'] for c in checks['checks'])
assert all(c['detected'] for c in negative)
assert cam['pass'] and all(c['pass'] for c in cam['checks'])
assert cam['board_sha256']==pcb_sha
assert cam['files']=={f.name:sha(f) for f in (R/'gerber').iterdir() if f.is_file()}
visual=read(R/'verification/visual-review.json')
assert visual['pass'] and visual['cam_files']==cam['files']
assert all(sha(R/f)==h for f,h in visual['images'].items()),'Visual review outdated'

source=read(R/'verification/source-snapshot.json')
S=Path(source['source'])
source_now={f.relative_to(S).as_posix():sha(f) for f in S.rglob('*') if f.is_file() and '__pycache__' not in f.parts and not f.name.endswith('.lck')}
assert source_now==source['sha256'],'Original R3.1 changed during work'
assert pcb_sha==source_now['eda/P01.kicad_pcb']
write(R/'verification/source-unchanged.json',{'pass':True,'source_files':len(source_now),'board_bytes_identical':True,'time_utc':stamp})

zip_path=R/'DO-ZAMOWIENIA_P01-PCB-R3.1.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for name in sorted(cam['files']):z.write(R/'gerber'/name,name)
with zipfile.ZipFile(zip_path) as z:
    assert z.testzip() is None
    assert len(z.namelist())==9 and set(z.namelist())==set(cam['files'])
    assert all(hashlib.sha256(z.read(name)).hexdigest()==digest for name,digest in cam['files'].items())
zip_sha=sha(zip_path)
zip_path.with_suffix('.zip.sha256').write_text(zip_sha+'  '+zip_path.name+'\n',encoding='ascii')
write(R/'verification/release-status.json',{
    'state':'FABRICATION_FILES_VERIFIED','release_date':'2026-09-27','time_utc':stamp,
    'scope':'Bare PCB prototype manufacturing data; no hardware acceptance',
    'source_revision':'P01-PCB-R3.1-review','geometry_revision':'PCB-R3','assembly_variant':'A1',
    'board_sha256':pcb_sha,'board_unchanged':True,'drc':receipt['counts'],
    'design_checks_passed':len(checks['checks']),'negative_controls_detected':len(negative),
    'cam_checks_passed':len(cam['checks']),'visual_review':'PASS',
    'physical_fit':'NOT_TESTED','electrical_hardware':'NOT_TESTED','thermal_hardware':'NOT_TESTED',
    'manufacturing_zip':zip_path.name,'manufacturing_zip_sha256':zip_sha,'manufacturing_files':9,
    'board_mm':[160,120],'board_thickness_mm':1.6,'copper_um_each_side':70,'PTH_count':202,'NPTH_count':8})

def included(f):
    rel=f.relative_to(R)
    return f.is_file() and rel.as_posix()!='MANIFEST.sha256.json' and not any(x in rel.parts for x in ['__pycache__','negative-controls','tool-config']) and f.suffix not in ['.pyc','.kicad_prl'] and not f.name.endswith('.lck')
manifest={f.relative_to(R).as_posix():sha(f) for f in sorted(R.rglob('*')) if included(f)}
write(R/'MANIFEST.sha256.json',manifest)
print(json.dumps({'state':'FABRICATION_FILES_VERIFIED','package_files':len(manifest),'zip':str(zip_path),'zip_sha256':zip_sha,'zip_bytes':zip_path.stat().st_size}))
