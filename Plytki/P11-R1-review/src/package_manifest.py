"""Freeze or check exact delivered package content; manifest itself is excluded."""
from pathlib import Path
import json,hashlib,sys
P=Path(__file__).resolve().parents[1];fn=P/'manifest.sha256.json'
reserved={'CON','PRN','AUX','NUL'}|{s+str(n) for s in ['COM','LPT'] for n in range(1,10)}
bad=[str(f.relative_to(P)) for f in P.rglob('*') if any(a.split('.')[0].upper() in reserved or a.endswith((' ','.')) for a in f.relative_to(P).parts)]
assert not bad,('Nonportable Windows filenames',bad)
if '--paths-only' in sys.argv:
 print('Windows filename portability PASS');sys.exit(0)
def files():
 return {f.relative_to(P).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(P.rglob('*')) if f.is_file() and f!=fn and '__pycache__' not in f.parts and f.suffix not in ['.pyc','.kicad_prl'] and not f.name.endswith('.lck')}
data=files()
if '--check' in sys.argv:
 old=json.loads(fn.read_text());assert data==old,{'missing':sorted(set(old)-set(data)),'extra':sorted(set(data)-set(old)),'changed':[k for k in old.keys()&data.keys() if old[k]!=data[k]]}
 print('Manifest PASS:',len(data),'files')
else:fn.write_text(json.dumps(data,indent=2)+'\n');print('Manifest written:',len(data),'files')
