"""Read-only checks against the published R2 and review; writes only beside this file."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
PROJECT = Path(r'C:\Users\tgorbacz\Documents\GORBI\Priv\Kia\Sportage\EGRLab')
P = PROJECT / 'Plytki/P01-R2-review'

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

manifest = json.loads((P / 'release-manifest.json').read_text(encoding='utf-8-sig'))
different = []
unreadable = []
for name, expected in manifest['files'].items():
    try:
        if digest(P / name) != expected:
            different.append(name)
    except OSError as exc:
        unreadable.append({'file': name, 'error': str(exc)})

review = PROJECT / 'Plytki/P01-R2-recenzja'
out = {
    'date': '2026-09-23',
    'published_root': str(P),
    'release_archive_sha256': digest(PROJECT / 'Plytki/P01-R2-review.zip'),
    'release_files_checked': len(manifest['files']),
    'different': different,
    'unreadable': unreadable,
    'review_inputs_sha256': {
        str(p.relative_to(review)): digest(p)
        for p in sorted(review.rglob('*')) if p.is_file() and p.suffix in ('.md', '.py', '.txt')
    },
    'arithmetic': {
        'gate_RC_ms': (100000 * 470000 / (100000 + 470000)) * 1e-6 * 1000,
        'C220u_energy_14V_to_6p5V_mJ': .5 * 220e-6 * (14**2 - 6.5**2) * 1000,
        'ideal_hold_up_at_3W_ms': .5 * 220e-6 * (14**2 - 6.5**2) / 3 * 1000,
        'delta_Q_at_0p1V_220u_uC': .1 * 220e-6 * 1e6,
        'hotplug_bound_C5_C6_10percent_V': 48 * (11 + 2) / (11 + 2 + 900),
    },
    'limitations': [
        'Repeated reviewer models, not independent hardware measurements.',
        '6.5 V is the model cutoff; no measured P02 UVLO threshold.',
        'No schematic, BOM, firmware or release file changed.',
    ],
}
(HERE / 'sprawdzenie.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: out[k] for k in ('release_archive_sha256', 'release_files_checked', 'different', 'unreadable', 'arithmetic')}, ensure_ascii=False, indent=2))
