"""P03 R5 release packaging (split from run_release.py): checks that the reports belong to the final files, then writes
release-manifest.json and ../P03-R5-review.zip (+ .sha256). The negative-control copies and caches stay out.
"""
from pathlib import Path
import hashlib, json, zipfile
from provenance import inputs
P = Path(__file__).resolve().parents[1]


def read(rel):
    return json.loads((P / rel).read_text(encoding='utf-8'))


reset = read('verification/reset-budget.json'); assert all(c['pass'] for c in reset['checks']) and all(c['detected'] for c in reset['negative_controls'])
pcb = read('verification/pcb-checks.json'); fn = read('verification/function-checks.json'); rev = read('verification/revision-checks.json')
assert pcb['passed'] == pcb['total'] and all(c['pass'] for c in fn) and rev['passed']
assert all(m['detected'] for m in read('verification/function-mutations.json')) and all(c['detected'] for c in read('verification/negative-controls.json'))
assert read('verification/table-checks.json')['pass']
clean=read('verification/standalone-rebuild.json');assert clean['all_equal'] and clean['schematic_reexport_preserves_project']
for rel,digest in clean['source_sha256'].items():
    assert hashlib.sha256((P/rel).read_bytes()).hexdigest()==digest,'Source changed after independent rebuild: '+rel
assert read('verification/drc.provenance.json')['inputs'] == inputs(), 'Checks are stale: rerun verify_pcb.py'
vis = read('verification/visual-review.json')
assert set(vis['reports']) == {'P03-R5-schemat.pdf', 'P03-R5-PCB.pdf'}
for name, meta in vis['reports'].items():
    assert meta['all_pages_visually_reviewed'] and meta['pages'] == (5 if 'schemat' in name else 4)
    assert hashlib.sha256((P / 'output/pdf' / name).read_bytes()).hexdigest() == meta['sha256'], 'visual review stale: ' + name
skip = ('verification/negative-controls/', 'src/__pycache__/', 'src/tools/__pycache__/')
files = sorted(f for f in P.rglob('*') if f.is_file() and not any(f.relative_to(P).as_posix().startswith(s) for s in skip)
               and f.suffix not in ('.lck', '.kicad_prl', '.zip') and f.name != 'release-manifest.json'
               and not (f.parent.name == 'pdf' and not f.name.startswith('P03-R5-')))  # PDFs of earlier revisions never go in
man = {'package': 'P03-R5-review', 'date': '2026-09-28', 'status': 'R5: U4 Schmitt open-drain; paired with P04 R2.2 R17=10k; unchanged tracks/pads/zone boundaries vs R4, fill-equivalence checked; B2B fit and hardware acceptance pending',
       'files': {f.relative_to(P).as_posix(): hashlib.sha256(f.read_bytes()).hexdigest() for f in files}}
(P / 'release-manifest.json').write_text(json.dumps(man, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
z = P.parent / 'P03-R5-review.zip'
with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
    for f in files + [P / 'release-manifest.json']:
        zf.write(f, 'P03-R5-review/' + f.relative_to(P).as_posix())
with zipfile.ZipFile(z) as zf:
    for rel, digest in man['files'].items():
        assert hashlib.sha256(zf.read('P03-R5-review/' + rel)).hexdigest() == digest
h = hashlib.sha256(z.read_bytes()).hexdigest(); z.with_name(z.name + '.sha256').write_text(f'{h}  {z.name}' + chr(10))
print('manifest', len(man['files']), 'files; archive', z, h)
