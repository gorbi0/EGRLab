"""Zamknięcie paczki: wiąże DRC, kontrolę CAM, próby ujemne i oględziny z niezmienionym źródłem,
buduje ZIP dla producenta, sumę SHA-256, status wydania i manifest. Uruchomić po oględzinach podglądów.
Nie przypisuje wyniku PASS przymiarce ani próbom sprzętu.
"""
from pathlib import Path
import datetime, hashlib, json, zipfile

R = Path(__file__).resolve().parents[1]
CFG = json.loads((R/'src'/'config.json').read_text(encoding='utf-8'))
N, REV = CFG['name'], CFG['revision']
V, G = R/'verification', R/'gerber'
sha = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
read = lambda f: json.loads(f.read_text(encoding='utf-8'))


def write(f, data):
    f.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
board = R/'projekt'/'eda'/f'{N}.kicad_pcb'
counts = read(V/'drc-counts.json')
assert all(v == 0 for v in counts.values()), counts
receipt = read(V/'export-receipt.json')
assert receipt['board_sha256'] == sha(board) and receipt['drc_sha256'] == sha(V/'drc.json')
cam = read(V/'cam-checks.json')
assert cam['pass'] and cam['board_sha256'] == sha(board)
files = {f.name: sha(f) for f in sorted(G.iterdir()) if f.is_file()}
assert cam['files'] == files == receipt['files'], 'Pliki CAM zmieniły się po kontroli'
neg = read(V/'cam-negative-controls.json')
assert all(x['ok'] for x in neg) and any(x['plik'] is None for x in neg)
visual = read(V/'visual-review.json')
assert visual['pass'] and visual['cam_files'] == files
assert all(sha(R/f) == h for f, h in visual['images'].items()), 'Oględziny dotyczą innych obrazów'

snap = read(V/'source-snapshot.json')
S = Path(snap['source'])
now = {f.relative_to(S).as_posix(): sha(f) for f in S.rglob('*') if f.is_file() and not any(p in ('tmp', '__pycache__') for p in f.relative_to(S).parts) and not f.name.endswith('.lck')}
assert now == snap['sha256'], 'Wydanie źródłowe zmieniło się w trakcie pracy'
assert sha(board) == snap['sha256'][f'eda/{N}.kicad_pcb']
write(V/'source-unchanged.json', {'pass': True, 'source': str(S), 'source_files': len(now), 'board_bytes_identical': True, 'time_utc': stamp})

zip_path = R/f'DO-ZAMOWIENIA_{N}-PCB-{REV}.zip'
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for name in sorted(files):
        z.write(G/name, name)
with zipfile.ZipFile(zip_path) as z:
    assert z.testzip() is None and set(z.namelist()) == set(files)
    assert all(hashlib.sha256(z.read(n)).hexdigest() == h for n, h in files.items())
zip_sha = sha(zip_path)
zip_path.with_suffix('.zip.sha256').write_text(zip_sha + '  ' + zip_path.name + '\n', encoding='ascii')
data = read(V/'board-fabrication-data.json')
write(V/'release-status.json', {
    'state': 'FABRICATION_FILES_VERIFIED', 'release_date': datetime.date.today().isoformat(), 'time_utc': stamp,
    'scope': 'Pliki do wykonania gołej płytki prototypowej; bez odbioru sprzętu',
    'source_revision': CFG['source'], 'board_sha256': sha(board), 'board_unchanged': True, 'drc': counts,
    'drc_accepted': read(V/'drc-accepted.json') if (V/'drc-accepted.json').exists() else None,
    'cam_checks_passed': len(cam['checks']), 'cam_negative_controls': f"{sum(1 for x in neg if x['plik'])}/{sum(1 for x in neg if x['plik'])} wykrytych + próba zerowa",
    'visual_review': 'PASS', 'physical_fit': 'NIE ZBADANO', 'electrical_hardware': 'NIE ZBADANO',
    'manufacturing_zip': zip_path.name, 'manufacturing_zip_sha256': zip_sha, 'manufacturing_files': len(files),
    'board_mm': CFG['board_mm'], 'copper_um_each_side': CFG['copper_um'], 'silk': CFG.get('silk', 'obie strony'),
    'PTH_count': sum(1 for h in data['holes'] if h['plated']), 'NPTH_count': sum(1 for h in data['holes'] if not h['plated']),
    'min_track_mm': data['min_track_mm']})


def included(f):
    rel = f.relative_to(R)
    return f.is_file() and rel.as_posix() != 'MANIFEST.sha256.json' and '__pycache__' not in rel.parts and f.suffix not in ('.pyc', '.kicad_prl') and not f.name.endswith('.lck')


write(R/'MANIFEST.sha256.json', {f.relative_to(R).as_posix(): sha(f) for f in sorted(R.rglob('*')) if included(f)})
print(json.dumps({'state': 'FABRICATION_FILES_VERIFIED', 'zip': zip_path.name, 'zip_sha256': zip_sha, 'files': len(files)}))
