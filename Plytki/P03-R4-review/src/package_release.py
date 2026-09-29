"""P03 R4 release packaging (split from run_release.py): checks that the reports belong to the final files, then writes
release-manifest.json and ../P03-R4-review.zip (+ .sha256). The negative-control copies and caches stay out.
"""
from pathlib import Path
import hashlib, json, zipfile
from provenance import inputs
P = Path(__file__).resolve().parents[1]


def read(rel):
    return json.loads((P / rel).read_text(encoding='utf-8'))


pcb = read('verification/pcb-checks.json'); fn = read('verification/function-checks.json'); rev = read('verification/revision-checks.json')
assert pcb['passed'] == pcb['total'] and all(c['pass'] for c in fn) and rev['passed']
assert all(m['detected'] for m in read('verification/function-mutations.json')) and all(c['detected'] for c in read('verification/negative-controls.json'))
assert read('verification/table-checks.json')['pass']
assert read('verification/drc.provenance.json')['inputs'] == inputs(), 'Checks are stale: rerun verify_pcb.py'
vis = read('verification/visual-review.json')
for name, meta in vis['reports'].items():
    assert hashlib.sha256((P / 'output/pdf' / name).read_bytes()).hexdigest() == meta['sha256'], 'visual review stale: ' + name
skip = ('verification/negative-controls/', 'src/__pycache__/', 'src/tools/__pycache__/')
files = sorted(f for f in P.rglob('*') if f.is_file() and not any(f.relative_to(P).as_posix().startswith(s) for s in skip)
               and f.suffix not in ('.lck', '.kicad_prl', '.zip') and f.name != 'release-manifest.json'
               and not (f.parent.name == 'pdf' and not f.name.startswith('P03-R4-')))  # PDFs of earlier revisions never go in
man = {'package': 'P03-R4-review', 'date': '2026-09-27', 'status': 'R4: Schmitt buffer U6 in the reset to P04 (copper = R3 + local change at J4); layout review, B2B cross-section, fit and hardware NOT EXAMINED',
       'files': {f.relative_to(P).as_posix(): hashlib.sha256(f.read_bytes()).hexdigest() for f in files}}
(P / 'release-manifest.json').write_text(json.dumps(man, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
z = P.parent / 'P03-R4-review.zip'
with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
    for f in files + [P / 'release-manifest.json']:
        zf.write(f, 'P03-R4-review/' + f.relative_to(P).as_posix())
with zipfile.ZipFile(z) as zf:
    for rel, digest in man['files'].items():
        assert hashlib.sha256(zf.read('P03-R4-review/' + rel)).hexdigest() == digest
h = hashlib.sha256(z.read_bytes()).hexdigest(); z.with_name(z.name + '.sha256').write_text(f'{h}  {z.name}' + chr(10))
print('manifest', len(man['files']), 'files; archive', z, h)
