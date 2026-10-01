"""P09-R2 (format S1, schematic only): build -> docs -> ERC -> netlist -> pin-by-pin check -> electrical checks + negative controls -> PDF/PNG -> QA.md + manifest.
Run with KiCad Python (cloud: scripts/egrlab-docker python3 src/run_schematic.py). kicad-cli: KICAD_CLI or next to the Python. No PCB is built or checked here."""
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
run('docs', PY, 'src/make_docs.py')
run('erc', CLI, 'sch', 'erc', '--severity-all', '--format', 'json', '-o', 'verification/erc.json', 'eda/P09.kicad_sch')
run('netlist', CLI, 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', 'verification/P09.xml', 'eda/P09.kicad_sch')
run('schematic-check', PY, 'src/verify_schematic.py')
run('electrical-check', PY, 'src/verify_electrical.py')
run('schematic-pdf', CLI, 'sch', 'export', 'pdf', '-o', 'output/pdf/P09-R2-schemat.pdf', 'eda/P09.kicad_sch')
run('render-sch', PDFTOPPM, '-scale-to', '2400', '-png', 'output/pdf/P09-R2-schemat.pdf', 'output/previews/sch')
sc = json.loads((P / 'verification/schematic-check.json').read_text()); el = json.loads((P / 'verification/electrical-checks.json').read_text(encoding='utf-8'))
neg = el['negative_controls']
qa = ['# P09-R2 — QA schematu (plik generowany przez src/run_schematic.py)', '',
      f"ERC: {sc['erc_violations']} naruszeń na {sc['erc_sheets']} arkuszach. Netlista: {sc['components']} części, {sc['pin_checks']} pinów sprawdzonych pin po pinie względem `parts.py`, {len(sc['errors'])} błędów, {sc['nets']} sieci.", '',
      f"Kontrole elektryczne: {sum(c['pass'] for c in el['checks'])}/{len(el['checks'])} PASS. Próby ujemne: {sum(t['detected'] for t in neg if t['expected']=='detected')}/{sum(1 for t in neg if t['expected']=='detected')} mutacji wykrytych; próba zerowa (bez zmiany): {'czysta' if not neg[-1]['detected'] else 'NIECZYSTA'}.", '',
      '| Kontrola | Wynik |', '|---|---|'] + [f"| {c['id']} | {'PASS' if c['pass'] else 'FAIL'} |" for c in el['checks']] + ['', '## Próby ujemne', '', '| Mutacja | Oczekiwane | Wykryta | Zgłosiły kontrole |', '|---|---|---|---|'] + \
     [f"| {t['mutation']} | {t['expected']} | {'tak' if t['detected'] else 'nie'} | {', '.join(t['by']) or '—'} |" for t in neg] + ['', 'Schemat; PCB w README, sekcja „PCB” (layout 30.09–1.10.2026). Kontrole nie zastępują odbioru na sprzęcie.']
(P / 'verification/QA.md').write_text('\n'.join(qa) + '\n', encoding='utf-8')
files = sorted(p for d in ('eda', 'src', 'docs', 'output', 'reference') for p in (P / d).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
files += sorted(p for p in (P / 'verification').glob('*') if p.is_file() and p.name != 'manifest.json') + [P / 'README.md']
(P / 'verification/manifest.json').write_text(json.dumps({p.relative_to(P).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.exists()}, indent=1) + '\n')
print('Gotowe: przejrzyj output/pdf/P09-R2-schemat.pdf i verification/QA.md.')
