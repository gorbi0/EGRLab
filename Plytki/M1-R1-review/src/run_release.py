"""M1-R1 (chain of P07 S1): schematic chain, layout, silkscreen, PCB checks with negative controls (verify_pcb.py), views, review PDF, QA, manifest
(the P02 R4 release chain). Run with KiCad Python. Nothing for fabrication is produced here.
  (default)      replays routing/M1.ses and routing/completion-routes.json (identical board from the recorded router result)
  --new-route    runs Freerouting again (needs EGRLAB_FREEROUTING)
Env: KICAD_CLI, PDFTOPPM, EGRLAB_NODE / EGRLAB_SHARP (rasterize), EGRLAB_PDF_PYTHON (reportlab).
"""
from pathlib import Path
import sys, os, subprocess, json, hashlib
P = Path(__file__).resolve().parents[1]; PY = sys.executable
PDFPY = os.environ.get('EGRLAB_PDF_PYTHON', PY); NODE = os.environ.get('EGRLAB_NODE', 'node'); SHARP = os.environ.get('EGRLAB_SHARP', 'sharp')
RENDER = os.environ.get('PDFTOPPM', 'pdftoppm')


def run(name, *cmd):
    r = subprocess.run([str(x) for x in cmd], cwd=P, capture_output=True, text=True, encoding='utf-8', errors='replace')
    (P / 'verification' / ('run-' + name + '.log')).write_text(r.stdout + '\n' + r.stderr, encoding='utf-8')
    if r.returncode:
        raise SystemExit(name + ' FAILED; see verification/run-' + name + '.log')
    print(name, 'PASS', flush=True)


run('schematic', PY, 'src/run_schematic.py')
run('layout', PY, 'src/run_layout.py', *(['--reuse-ses'] if '--new-route' not in sys.argv else []))
run('silk', PY, 'src/silkscreen.py'); run('rules', PY, 'src/set_rules.py')
run('pcb-check', PY, 'src/verify_pcb.py')
run('views', PY, 'src/export_views.py'); run('rasterize', NODE, 'src/rasterize.mjs', str(P), SHARP)
run('pcb-pdf', PDFPY, 'src/make_pdf.py')
run('render-pdf', RENDER, '-scale-to', '1800', '-png', 'output/pdf/M1-R1-PCB.pdf', 'output/previews/pcb')
chk = json.loads((P / 'verification/pcb-checks.json').read_text(encoding='utf-8')); neg = json.loads((P / 'verification/negative-controls.json').read_text(encoding='utf-8'))
drc = json.loads((P / 'verification/drc.json').read_text()); silk = json.loads((P / 'routing/silkscreen.json').read_text(encoding='utf-8'))
qa = ['# M1-R1 — QA PCB (plik generowany przez src/run_release.py)', '',
      f"DRC (świeży, wszystkie poziomy): naruszenia {len(drc['violations'])}, niepołączone {len(drc['unconnected_items'])}, niezgodności ze schematem {len(drc['schematic_parity'])} "
      f"(naruszenia to wyłącznie lib_footprint_mismatch części z przyciętym nadrukiem, przyjęte przez verify_pcb.py; szczegóły w pcb-checks.json).",
      f"Kontrole PCB: {chk['passed']}/{chk['total']}. Próby ujemne: {sum(x['detected'] for x in neg)}/{len(neg)} (w tym próba zerowa).", '',
      '| Kontrola | Wynik |', '|---|---|'] + [f"| {c['check']} | {'PASS' if c['pass'] else 'FAIL'} |" for c in chk['checks']]
qa += ['', '## Próby ujemne', '', '| Wada | Oczekiwana kontrola | Wykryta | Zgłoszone |', '|---|---|---|---|']
qa += [f"| {x['control']} | {x['expected_failing_check']} | {'tak' if x['detected'] else 'NIE'} | {len(x['failed_checks'])} |" for x in neg]
qa += ['', f"Nadruk: ukryte oznaczenia (brak miejsca): {', '.join(silk['hidden_references']) or 'brak'}; nieumieszczone napisy: {', '.join(silk['unplaced_texts']) or 'brak'}."]
qa += ['', 'Oględziny PDF: wpis ręczny w README (sekcja „PCB”); render stron w output/previews/pcb-*.png.']
(P / 'verification/QA-PCB.md').write_text('\n'.join(qa) + '\n', encoding='utf-8')
files = sorted(q for d in ('eda', 'src', 'docs', 'output', 'routing', 'reference') for q in (P / d).rglob('*') if q.is_file() and '__pycache__' not in q.parts)
files += sorted(q for q in (P / 'verification').glob('*') if q.is_file() and q.name != 'manifest.json') + [P / 'README.md']
(P / 'verification/manifest.json').write_text(json.dumps({q.relative_to(P).as_posix(): hashlib.sha256(q.read_bytes()).hexdigest() for q in files}, indent=1) + '\n')
print('PCB gotowa: output/pdf/M1-R1-PCB.pdf, verification/QA-PCB.md')
