"""Package the verified REVIEW artifact; no Gerbers and no production approval."""
from pathlib import Path
import json,hashlib,zipfile
from provenance import inputs,sha
P=Path(__file__).resolve().parents[1]
c=json.loads((P/'verification/pcb-checks.json').read_text());assert c['passed']==c['total'] and c['board_sha256']==sha(P/'eda/P02.kicad_pcb')
receipt=json.loads((P/'verification/drc.provenance.json').read_text());assert receipt['inputs']==inputs(P/'eda/P02.kicad_pcb'),'DRC inputs stale'
assert receipt['drc_sha256']==sha(P/'verification/drc.json')
for n in ['electrical-checks','revision-checks']:assert json.loads((P/f'verification/{n}.json').read_text())['passed']
for n in ['negative-controls','electrical-negative-controls']:assert all(x['detected'] for x in json.loads((P/f'verification/{n}.json').read_text()))
v=json.loads((P/'verification/visual-review.json').read_text())
assert v['status']=='PASS' and v['pages_reviewed']=={'P02-R2-schemat.pdf':4,'P02-R2-PCB.pdf':5}
assert set(v['pdf_sha256'])=={'P02-R2-schemat.pdf','P02-R2-PCB.pdf'}
assert all(v['pdf_sha256'][n]==sha(P/'output/pdf'/n) for n in v['pdf_sha256'])
s=json.loads((P/'verification/schematic-check.json').read_text())
assert not s['errors'] and not s['extra'] and s['erc_violations']==0 and s['pin_checks']==208
e=json.loads((P/'verification/electrical-checks.json').read_text())
assert all(sha(P/n)==h for n,h in e['inputs_sha256'].items()),'Electrical inputs stale'
files=sorted(f for f in P.rglob('*') if f.is_file() and not any(n in f.parts for n in ['__pycache__','negative-controls','tool-config']) and f.suffix not in ['.pyc','.lck','.kicad_prl'] and f.name not in ['release-manifest.json','silk-free-debug.png'])
manifest={'package':'P02-R2-review','status':'FOR_OPUS_REVIEW; not fabrication release; F2/F3/F4 and physical acceptance OPEN','files':{f.relative_to(P).as_posix():sha(f) for f in files}}
(P/'release-manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
z=P.parent/'P02-R2-review.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as zz:
 for f in files+[P/'release-manifest.json']:zz.write(f,P.name+'/'+f.relative_to(P).as_posix())
print('Files:',len(files),'ZIP:',z,'SHA256:',sha(z))
