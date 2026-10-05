"""P04-R3 (format S1, schematic only): build -> tables -> ERC -> netlist -> pin-by-pin check -> electrical checks (R2.2, truth tables)
-> values -> reset budget with P03 R6 -> S1 / P12 contract checks (with negative controls and a null control) -> PDF/PNG ->
verification/QA.md + manifest. No PCB is built or checked here (layout: local session). Run with KiCad Python
(cloud: scripts/egrlab-docker python3 src/run_schematic.py). kicad-cli: KICAD_CLI or next to the Python."""
from pathlib import Path
import os, subprocess, sys, json, hashlib
P = Path(__file__).resolve().parents[1]; PY = sys.executable
CLI = os.environ.get('KICAD_CLI', str(Path(PY).with_name('kicad-cli.exe')))
PDFTOPPM = os.environ.get('PDFTOPPM', 'pdftoppm')
for d in ('verification', 'output/pdf', 'output/previews', 'docs'): (P / d).mkdir(parents=True, exist_ok=True)


def run(name, *cmd):
    r = subprocess.run([str(x) for x in cmd], cwd=P, capture_output=True, text=True, encoding='utf-8', errors='replace')
    (P / 'verification' / ('run-' + name + '.log')).write_text(r.stdout + '\n' + r.stderr, encoding='utf-8')
    if r.returncode: raise SystemExit(name + ' FAILED; see verification/run-' + name + '.log')
    print(name, 'PASS', flush=True)


run('schematic-build', PY, 'src/build_schematic.py')
run('tables', PY, 'src/make_tables.py')
run('erc', CLI, 'sch', 'erc', '--severity-all', '--format', 'json', '-o', 'verification/erc.json', 'eda/P04.kicad_sch')
run('netlist', CLI, 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', 'verification/P04.xml', 'eda/P04.kicad_sch')
run('schematic-check', PY, 'src/verify_schematic.py')
run('electrical-check', PY, 'src/verify_electrical.py')
run('value-check', PY, 'src/verify_values.py')
run('reset-check', PY, 'src/verify_reset.py')
run('s1-check', PY, 'src/verify_s1.py')
run('schematic-pdf', CLI, 'sch', 'export', 'pdf', '-o', 'output/pdf/P04-R3-schemat.pdf', 'eda/P04.kicad_sch')
for old in (P / 'output/previews').glob('sch-*.png'): old.unlink()
run('render-sch', PDFTOPPM, '-scale-to', '2200', '-png', 'output/pdf/P04-R3-schemat.pdf', 'output/previews/sch')
prl = P / 'eda/P04.kicad_prl'
if prl.exists(): prl.unlink()                                  # created by kicad-cli, not part of the project
sc = json.loads((P / 'verification/schematic-check.json').read_text())
el = json.loads((P / 'verification/electrical-checks.json').read_text(encoding='utf-8'))
va = json.loads((P / 'verification/value-checks.json').read_text(encoding='utf-8'))
rs = json.loads((P / 'verification/reset-budget.json').read_text(encoding='utf-8'))
s1 = json.loads((P / 'verification/s1-checks.json').read_text(encoding='utf-8'))
n1 = s1['negative_controls']
qa = ['# P04-R3 — QA schematu (plik generowany przez src/run_schematic.py)', '',
      f"ERC: {sc['erc_violations']} naruszeń na {sc['erc_sheets']} arkuszach. Netlista: {sc['components']} części, {sc['pin_checks']} pinów sprawdzonych pin po pinie względem `parts.py`, {len(sc['errors'])} błędów, {sc['nets']} sieci.", '',
      f"Kontrole elektryczne R2.2 (`verify_electrical.py`, tabele prawdy {el['truth_table_rows']} wierszy): {sum(c['pass'] for c in el['checks'])}/{len(el['checks'])} PASS; mutacje {sum(t['detected'] for t in el['negative_controls'])}/{len(el['negative_controls'])} wykrytych.",
      f"Wartości i MPN (`verify_values.py`): {sum(c['pass'] for c in va['checks'])}/{len(va['checks'])} PASS; mutacje {sum(t['detected'] for t in va['negative_controls'])}/{len(va['negative_controls'])} wykrytych.",
      f"Budżet resetu z P03 R6 (`verify_reset.py`): {sum(c['pass'] for c in rs['checks'])}/{len(rs['checks'])} PASS; mutacje {sum(t['detected'] for t in rs['negative_controls'])}/{len(rs['negative_controls'])} wykrytych.", '',
      f"Kontrakt S1 i P12 (`verify_s1.py`): {sum(c['pass'] for c in s1['checks'])}/{len(s1['checks'])} PASS; mutacje {sum(t['detected'] for t in n1[:-1])}/{len(n1) - 1} wykrytych przez kontrolę docelową; próba zerowa: {'czysta' if not n1[-1]['detected'] else 'NIECZYSTA'}.", '',
      '| Kontrola S1 / P12 | Wynik |', '|---|---|'] + [f"| {c['id']} | {'PASS' if c['pass'] else 'FAIL'} |" for c in s1['checks']] + \
     ['', '| Kontrola elektryczna | Wynik |', '|---|---|'] + [f"| {c['name']} | {'PASS' if c['pass'] else 'FAIL'} |" for c in el['checks']] + \
     ['', '## Próby ujemne S1 / P12', '', '| Mutacja | Kontrola docelowa | Wykryta | Zgłosiły |', '|---|---|---|---|'] + \
     [f"| {t['mutation']} | {t['target'] or '—'} | {'tak' if t['detected'] else 'nie'} | {', '.join(t['by']) or '—'} |" for t in n1] + \
     ['', '## Próby ujemne elektryczne', '', '| Mutacja | Kontrola docelowa | Wykryta |', '|---|---|---|'] + \
     [f"| {t['mutation']} | {t['target_check']} | {'tak' if t['detected'] else 'nie'} |" for t in el['negative_controls']] + \
     ['', 'PCB: `verification/QA-PCB.md` (łańcuch `src/run_release.py`). Kontrole plików nie zastępują odbioru na sprzęcie (`docs/ODBIOR.md`).',
      'Ostrzeżenie kicad-cli „schemat posiada błędy numeracji” dotyczy oznaczeń `J_BP1…3` i `J_SV1…3` (nazwy z formatu S1, jak w P03 R6 / P06 R2); ERC go nie zgłasza.']
(P / 'verification/QA.md').write_text('\n'.join(qa) + '\n', encoding='utf-8')
files = sorted(p for d in ('eda', 'src', 'docs', 'output', 'reference', 'input') for p in (P / d).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
files += sorted(p for p in (P / 'verification').glob('*') if p.is_file() and p.name != 'manifest.json') + [P / 'README.md']
(P / 'verification/manifest.json').write_text(json.dumps({p.relative_to(P).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.exists()}, indent=1) + '\n')
print('Gotowe: przejrzyj output/pdf/P04-R3-schemat.pdf i verification/QA.md.')
