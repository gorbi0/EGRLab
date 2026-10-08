"""Builds Plytki/M1-R1-do-recenzji.zip for the reviewer (Astra): ZAKRES-RECENZJI-M1-R1.md at the top, the M1 directories under their
repository paths, MANIFEST-RECENZJI.json (commit, SHA-256 of every file). Deterministic order and timestamps (git commit time).
Run from the repository root: python3 Plytki/M1-specyfikacja/pakiet_recenzji.py"""
from pathlib import Path
import hashlib, json, subprocess, zipfile, time

ROOT = Path(__file__).resolve().parents[2]
DIRS = ['Plytki/M1-specyfikacja', 'Plytki/M1-R1-review', 'Plytki/M1-PCB-R1-zamowienie', 'Rewizje/EGRLab-v6.3-m1']
TOP = 'M1-R1-do-recenzji'
OUT = ROOT / 'Plytki/M1-R1-do-recenzji.zip'
commit = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
dirty = subprocess.run(['git', '-C', str(ROOT), 'status', '--porcelain', '--', *DIRS], capture_output=True, text=True, check=True).stdout.strip()
assert not dirty, 'commit the M1 directories first:\n' + dirty
ts = int(subprocess.run(['git', '-C', str(ROOT), 'log', '-1', '--format=%ct'], capture_output=True, text=True, check=True).stdout)
dt = time.gmtime(ts)[:6]
skip = lambda p: any(x in ('__pycache__', 'tmp') for x in p.parts) or p.name.endswith('.lck')
files = sorted(p for d in DIRS for p in (ROOT / d).rglob('*') if p.is_file() and not skip(p.relative_to(ROOT)))
sha = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
manifest = {'commit': commit, 'branch': 'm1', 'files': len(sha), 'sha256': sha}


def add(z, name, data):
    zi = zipfile.ZipInfo(f'{TOP}/{name}', dt); zi.compress_type = zipfile.ZIP_DEFLATED; zi.external_attr = 0o644 << 16
    z.writestr(zi, data, compresslevel=9)


with zipfile.ZipFile(OUT, 'w') as z:
    add(z, 'ZAKRES-RECENZJI-M1-R1.md', (ROOT / 'Plytki/M1-specyfikacja/ZAKRES-RECENZJI-M1-R1.md').read_bytes())
    add(z, 'MANIFEST-RECENZJI.json', (json.dumps(manifest, indent=1, ensure_ascii=False) + '\n').encode())
    for p in files:
        add(z, p.relative_to(ROOT).as_posix(), p.read_bytes())
with zipfile.ZipFile(OUT) as z:
    assert z.testzip() is None
digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
OUT.with_suffix('.zip.sha256').write_text(f'{digest}  {OUT.name}\n', encoding='ascii')
print(OUT.name, round(OUT.stat().st_size / 1e6, 1), 'MB,', len(sha), 'files, commit', commit[:7], 'sha256', digest[:16])
