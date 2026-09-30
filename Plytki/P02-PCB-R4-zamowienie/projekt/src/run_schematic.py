"""P02-R4, schematic chain (etap 1, updated in etap 2 for format S1): build -> ERC -> netlist -> pin-by-pin check -> electrical checks + negative controls -> PDF/PNG.
Run with KiCad Python (cloud: scripts/egrlab-docker python3 src/run_schematic.py). kicad-cli: KICAD_CLI or next to the Python.
Every step writes verification/run-<step>.log and stops on the first failure.
"""
from pathlib import Path
import os, subprocess, sys, json, hashlib
P = Path(__file__).resolve().parents[1]; PY = sys.executable
CLI = os.environ.get('KICAD_CLI', str(Path(PY).with_name('kicad-cli.exe')))
PDFTOPPM = os.environ.get('PDFTOPPM', 'pdftoppm')


def run(name, *cmd):
    r = subprocess.run([str(x) for x in cmd], cwd=P, capture_output=True, text=True, encoding='utf-8', errors='replace')
    (P / 'verification' / ('run-' + name + '.log')).write_text(r.stdout + '\n' + r.stderr, encoding='utf-8')
    if r.returncode: raise SystemExit(name + ' FAILED; see verification/run-' + name + '.log')
    print(name, 'PASS', flush=True)


run('schematic-build', PY, 'src/build_schematic.py')
run('erc', CLI, 'sch', 'erc', '--severity-all', '--format', 'json', '-o', 'verification/erc.json', 'eda/P02.kicad_sch')
run('netlist', CLI, 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', 'verification/P02.xml', 'eda/P02.kicad_sch')
run('schematic-check', PY, 'src/verify_schematic.py')
run('electrical-check', PY, 'src/check_electrical.py', '--negative')
run('schematic-pdf', CLI, 'sch', 'export', 'pdf', '-o', 'output/pdf/P02-R4-schemat.pdf', 'eda/P02.kicad_sch')
run('render-sch', PDFTOPPM, '-scale-to', '2400', '-png', 'output/pdf/P02-R4-schemat.pdf', 'output/previews/sch')
sc = json.loads((P / 'verification/schematic-check.json').read_text()); el = json.loads((P / 'verification/electrical-checks.json').read_text(encoding='utf-8'))
neg = json.loads((P / 'verification/electrical-negative-controls.json').read_text())
qa = ['# P02-R4 — QA schematu (etap 2, format S1; plik generowany przez src/run_schematic.py)', '',
      f"ERC: {sc['erc_violations']} naruszeń na {sc['erc_sheets']} arkuszach. Netlista: {sc['components']} części, {sc['pin_checks']} pinów sprawdzonych, "
      f"{len(sc['errors'])} błędów, {sc['nets']} sieci.", '',
      f"Kontrole elektryczne: {sum(c['pass'] for c in el['checks'])}/{len(el['checks'])} PASS. "
      f"Próby ujemne: {sum(t['detected'] for t in neg)}/{len(neg)} (w tym próba zerowa).", '', '| Kontrola | Wynik | Wartość |', '|---|---|---|']
qa += [f"| {c['check']} | {'PASS' if c['pass'] else 'FAIL'} | {c['info']} |" for c in el['checks']]
qa += ['', '## Zgodność ze specyfikacją (informacyjnie, do decyzji)', '', '| Wymaganie | Treść | Wynik | Spełnione |', '|---|---|---|---|']
qa += [f"| {x['id']} | {x['text']} | {x['result']} | {'tak' if x['met'] else 'NIE'} |" for x in el['spec_conformance']]
qa += ['', '## Próby ujemne', '', '| Mutacja | Oczekiwana | Zgłoszone | Wykryta |', '|---|---|---|---|']
qa += [f"| {t['mutation']} | {t['expected']} | {', '.join(t['failed_checks']) or '—'} | {'tak' if t['detected'] else 'NIE'} |" for t in neg]
qa += ['', 'Oględziny PDF (5 stron A3): wykonane przy tworzeniu pakietu; etykiety czytelne, połączenia wyłącznie etykietami, sprawdzone pin po pinie.']
(P / 'verification/QA-schemat.md').write_text('\n'.join(qa) + '\n', encoding='utf-8')
files = sorted(p for d in ('eda', 'src', 'docs', 'output') for p in (P / d).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
files += sorted(p for p in (P / 'verification').glob('*') if p.is_file() and p.name != 'manifest.json') + [P / 'README.md']
(P / 'verification/manifest.json').write_text(json.dumps({p.relative_to(P).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}, indent=1) + '\n')
print('Schemat gotowy: przejrzyj output/pdf/P02-R4-schemat.pdf i verification/QA-schemat.md.')
