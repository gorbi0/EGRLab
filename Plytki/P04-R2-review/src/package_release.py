"""Package final artifacts only, after fresh checks and visual/clean-build signoff."""
from pathlib import Path
import json,hashlib,zipfile
from provenance import inputs,sha
P=Path(__file__).resolve().parents[1]
def read(rel):return json.loads((P/rel).read_text(encoding='utf-8'))
sch=read('verification/schematic-check.json');assert not sch['errors'] and not sch['extra'] and sch['erc_violations']==0
for name in ['pcb','electrical']:
 r=read('verification/'+name+'-checks.json');assert all(c['pass'] for c in r['checks']) and all(c['detected'] for c in r['negative_controls'])
assert read('verification/drc.provenance.json')['inputs']==inputs(),'Stale verification: rerun verify_pcb.py after changing sources.'
clean=read('verification/clean-rebuild.json');assert clean['geometry_equal'] and clean['pcb_checks_pass'] and clean['electrical_checks_pass']
visual=read('verification/visual-qa.json');assert visual['schematic_pages']==6 and visual['pcb_pages']==4 and visual['pass']
for rel,digest in visual['pdf_sha256'].items():assert sha(P/rel)==digest,'PDF changed after visual inspection'
skip={'__pycache__','tmp'}
def include(f):
 rel=f.relative_to(P)
 if any(v in skip for v in rel.parts) or f.suffix in ['.pyc','.lck','.kicad_prl','.zip'] or f.name=='release-manifest.json':return False
 if rel.parts[0]=='routing' and f.name not in ['P04.ses','P04.dsn','prerouted.kicad_pcb','completion-routes.json','postclean-drc.json','stitching.json','solid-pads.json','attempts.json']:return False
 if rel.parts[:2]==('output','previews') and not (f.name.startswith(('exported-pcb-','sch-1-')) or f.name=='render-top.png'):return False
 if rel.parts[0]=='verification' and f.name in ['silk-free-debug.png','build.log','python-warnings.log']:return False
 return True
files=sorted(f for f in P.rglob('*') if f.is_file() and include(f))
manifest={'package':'P04-R2-review','status':'Independent review and physical fit pending; no manufacturing release','files':{f.relative_to(P).as_posix():sha(f) for f in files}}
(P/'release-manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
z=P.parent/'P04-R2-review.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as archive:
 for f in files+[P/'release-manifest.json']:archive.write(f,'P04-R2-review/'+f.relative_to(P).as_posix())
with zipfile.ZipFile(z) as archive:
 for rel,digest in manifest['files'].items():assert hashlib.sha256(archive.read('P04-R2-review/'+rel)).hexdigest()==digest
z.with_suffix('.zip.sha256').write_text(sha(z)+'  '+z.name+'\n')
print('Verified package:',len(files),'files;',round(z.stat().st_size/1024/1024,1),'MiB;',z)
