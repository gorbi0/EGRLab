"""P12-R1 (format S1, wariant LOGGER), łańcuch schematu: kontrakt -> budowa -> ERC -> netlista -> kontrola pin po pinie (parts.json) ->
netlista wobec kontraktów + próby ujemne -> PDF/PNG -> QA.md + manifest. Uruchamiać Pythonem KiCada
(scripts/egrlab-docker python3 src/run_schematic.py). Wzorzec: P10-R2-review/src/run_schematic.py."""
from pathlib import Path
import os, subprocess, sys, json, hashlib
P = Path(__file__).resolve().parents[1]; PY = sys.executable
CLI = os.environ.get('KICAD_CLI', str(Path(PY).with_name('kicad-cli.exe')))
PDFTOPPM = os.environ.get('PDFTOPPM', 'pdftoppm')
(P / 'verification').mkdir(exist_ok=True); (P / 'output/pdf').mkdir(parents=True, exist_ok=True); (P / 'output/previews').mkdir(parents=True, exist_ok=True)


def run(name, *cmd):
    r = subprocess.run([str(x) for x in cmd], cwd=P, capture_output=True, text=True, encoding='utf-8', errors='replace')
    (P / 'verification' / ('run-' + name + '.log')).write_text(r.stdout + '\n' + r.stderr, encoding='utf-8')
    if r.returncode: raise SystemExit(name + ' FAILED; see verification/run-' + name + '.log')
    print(name, 'PASS', flush=True)


run('kontrakt', PY, 'src/kontrakt.py')
run('schematic-build', PY, 'src/build_schematic.py')
run('erc', CLI, 'sch', 'erc', '--severity-all', '--format', 'json', '-o', 'verification/erc.json', 'eda/P12.kicad_sch')
run('netlist', CLI, 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', 'verification/P12.xml', 'eda/P12.kicad_sch')
run('schematic-check', PY, 'src/verify_schematic.py')
run('electrical-check', PY, 'src/verify_kontrakt.py')
run('schematic-pdf', CLI, 'sch', 'export', 'pdf', '-o', 'output/pdf/P12-R1-schemat.pdf', 'eda/P12.kicad_sch')
run('render-sch', PDFTOPPM, '-scale-to', '2400', '-png', 'output/pdf/P12-R1-schemat.pdf', 'output/previews/sch')
sc = json.loads((P / 'verification/schematic-check.json').read_text()); el = json.loads((P / 'verification/electrical-checks.json').read_text(encoding='utf-8'))
k12 = json.loads((P / 'docs/kontrakt-P12.json').read_text(encoding='utf-8')); neg = el['negative_controls']
qa = ['# P12-R1 — QA schematu (plik generowany przez src/run_schematic.py)', '',
      f"ERC: {sc['erc_violations']} naruszeń na {sc['erc_sheets']} arkuszu. Netlista: {sc['components']} części, {sc['pin_checks']} pinów sprawdzonych pin po pinie "
      f"względem `parts.py`, {len(sc['errors'])} błędów, {sc['nets']} sieci.", '',
      f"Kontrakt (`src/kontrakt.py`): {len(k12['zlacza'])} złączy, {sum(z['n'] for z in k12['zlacza'])} pinów, źródła zgodne z blobami w `kontrakty.json`: "
      f"{sum(v['zgodny'] for v in k12['zrodla'].values())}/{len(k12['zrodla'])}; sieci niepodłączone (P04 / P07 / P08): {len(k12['niepodlaczone'])}; "
      f"łączone mimo stanu „czeka”: {', '.join(k12['laczone_mimo_czeka'])}.", '',
      f"Netlista wobec kontraktów: {sum(c['pass'] for c in el['checks'])}/{len(el['checks'])} PASS. Próby ujemne: "
      f"{sum(t['ok'] for t in neg)}/{len(neg)} (w tym zerowa: {'czysta' if neg[0]['ok'] else 'NIECZYSTA'}).", '',
      '| Kontrola | Opis | Wynik |', '|---|---|---|'] + [f"| {c['id']} | {c['opis']} | {'PASS' if c['pass'] else 'FAIL'} |" for c in el['checks']] + \
     ['', '## Próby ujemne', '', '| Mutacja | Oczekiwana kontrola | Wynik | Zgłosiły kontrole |', '|---|---|---|---|'] + \
     [f"| {t['mutation']} | {t['expected_check'] or 'żadna'} | {'OK' if t['ok'] else 'ZŁE'} | {', '.join(t['failed_checks']) or '—'} |" for t in neg] + \
     ['', 'Kontrole nie zastępują odbioru na sprzęcie (NIE ZBADANO).']
(P / 'verification/QA.md').write_text('\n'.join(qa) + '\n', encoding='utf-8')
print('Gotowe: output/pdf/P12-R1-schemat.pdf, verification/QA.md')
