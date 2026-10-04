"""Kopia wydania źródłowego do projekt/ i zapis source-snapshot.json (przed src/export_production.py).
Uruchomienie: python src/copy_source.py. Kopiuje eda, routing, output, docs, src, verification i README wydania
(bez verification/negative-controls/ — kopie robocze płytek z prób ujemnych; wyniki są w negative-controls.json).
"""
from pathlib import Path
import datetime, hashlib, json, shutil

R = Path(__file__).resolve().parents[1]
CFG = json.loads((R/'src'/'config.json').read_text(encoding='utf-8'))
S = (R.parent/CFG['source']).resolve()
P = R/'projekt'
skip = lambda rel: any(p in ('tmp', '__pycache__') for p in rel.parts) or rel.name.endswith('.lck')
if P.exists():
    shutil.rmtree(P)
for d in ('eda', 'routing', 'output', 'docs', 'src', 'verification'):
    if (S/d).exists():
        shutil.copytree(S/d, P/d, ignore=shutil.ignore_patterns('__pycache__', '*.lck', 'tmp'))
shutil.rmtree(P/'verification'/'negative-controls', ignore_errors=True)
shutil.copy2(S/'README.md', P/'README.md')
sha = {q.relative_to(S).as_posix(): hashlib.sha256(q.read_bytes()).hexdigest()
       for q in sorted(S.rglob('*')) if q.is_file() and not skip(q.relative_to(S))}
bad = [k for k in sha if not k.startswith('verification/negative-controls/') and k.split('/')[0] in ('eda', 'routing', 'output', 'docs', 'src', 'verification', 'README.md')
       and hashlib.sha256((P/k).read_bytes()).hexdigest() != sha[k]]
assert not bad, bad
V = R/'verification'; V.mkdir(exist_ok=True)
(V/'source-snapshot.json').write_text(json.dumps({'source': str(S), 'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'files': len(sha), 'sha256': sha,
    'copy_excludes': 'verification/negative-controls/ (kopie robocze płytek z prób ujemnych wydania; wyniki są w verification/negative-controls.json)'}, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
print('kopia', S.name, len(sha), 'plików')
