"""P11-R2 (format S1, schematic only): build -> tables -> ERC -> netlist -> pin-by-pin check -> electrical checks (256 contact states x
two variants, negative controls) -> P12 contract (negative controls + null control) -> PDF/PNG -> verification/QA.md + manifest.
No PCB here (layout: local session). Run with KiCad Python (cloud: scripts/egrlab-docker python3 src/run_schematic.py).
kicad-cli: KICAD_CLI or next to the Python."""
from pathlib import Path
import os, subprocess, sys, json, hashlib
P = Path(__file__).resolve().parents[1]; PY = sys.executable
CLI = os.environ.get('KICAD_CLI', str(Path(PY).with_name('kicad-cli.exe')))
PDFTOPPM = os.environ.get('PDFTOPPM', 'pdftoppm')
for d in ('verification', 'output/pdf', 'output/previews'): (P / d).mkdir(parents=True, exist_ok=True)
def run(name, *cmd):
    r = subprocess.run([str(x) for x in cmd], cwd=P, capture_output=True, text=True, encoding='utf-8', errors='replace')
    (P / 'verification' / ('run-' + name + '.log')).write_text(r.stdout + '\n' + r.stderr, encoding='utf-8')
    if r.returncode: raise SystemExit(name + ' FAILED; see verification/run-' + name + '.log')
    print(name, 'PASS', flush=True)
run('schematic-build', PY, 'src/build_schematic.py')
run('tables', PY, 'src/make_tables.py')
run('erc', CLI, 'sch', 'erc', '--severity-all', '--format', 'json', '-o', 'verification/erc.json', 'eda/P11.kicad_sch')
run('netlist', CLI, 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', 'verification/P11.xml', 'eda/P11.kicad_sch')
run('schematic-check', PY, 'src/verify_schematic.py')
run('electrical-check', PY, 'src/verify_electrical.py')
run('p12-check', PY, 'src/verify_p12.py')
run('schematic-pdf', CLI, 'sch', 'export', 'pdf', '-o', 'output/pdf/P11-R2-schemat.pdf', 'eda/P11.kicad_sch')
for old in (P / 'output/previews').glob('sch-*.png'): old.unlink()
run('render-sch', PDFTOPPM, '-scale-to', '2200', '-png', 'output/pdf/P11-R2-schemat.pdf', 'output/previews/sch')
prl = P / 'eda/P11.kicad_prl'
if prl.exists(): prl.unlink()                                  # created by kicad-cli, not part of the project
sc = json.loads((P / 'verification/schematic-check.json').read_text())
el = json.loads((P / 'verification/electrical-checks.json').read_text(encoding='utf-8'))
pc = json.loads((P / 'verification/p12-checks.json').read_text(encoding='utf-8'))
w = el['analysis']['worst_case']; n1 = pc['negative_controls']
def fmt(d): return ', '.join(f'{k} {v:.3f} V' for k, v in sorted(d.items()))
qa = ['# P11-R2 — QA schematu (plik generowany przez src/run_schematic.py)', '',
      f"ERC: {sc['erc_violations']} naruszeń na {sc['erc_sheets']} arkuszach. Netlista: {sc['components']} części, {sc['pin_checks']} pinów sprawdzonych pin po pinie względem `parts.py`, {len(sc['errors'])} błędów.", '',
      f"Kontrole elektryczne (`verify_electrical.py`): {sum(c['pass'] for c in el['checks'])}/{len(el['checks'])} PASS; mutacje {sum(t['caught'] for t in el['negative_controls'])}/{len(el['negative_controls'])} wykrytych. "
      f"Model: 256 stanów styków × 2 warianty, szyna {el['analysis']['rail_V']['H_check']} V dla H i {el['analysis']['rail_V']['L_check']} V dla L, obciążenia −1 %, rezystory szeregowe +1 %.", '',
      f"LOGGER (R1 obsadzony, bez P04): minimalne H {fmt(w['LOGGER']['V_H_min'])}; prąd z 3V3_IO maks. {w['LOGGER']['I_source_max_mA']} mA; prąd zamkniętego styku {w['LOGGER']['I_contact_min_uA']} µA – {w['LOGGER']['I_contact_max_mA']} mA.",
      f"Pełny (P04 R40, R1 DNP; obciążenia P04-R2.1): minimalne H {fmt(w['FULL']['V_H_min'])}; prąd maks. {w['FULL']['I_source_max_mA']} mA; prąd styku {w['FULL']['I_contact_min_uA']} µA – {w['FULL']['I_contact_max_mA']} mA.",
      f"Zwarcie PANEL_3V3–GND przy R1: {el['analysis']['R1_short_W'] * 1000:.0f} mW w R1 (1206, 0,25 W).", '',
      f"Kontrakt P12 (`verify_p12.py`): {sum(c['pass'] for c in pc['checks'])}/{len(pc['checks'])} PASS; mutacje {sum(t['detected'] for t in n1[:-1])}/{len(n1) - 1} wykrytych przez kontrolę docelową; próba zerowa: {'czysta' if not n1[-1]['detected'] else 'NIECZYSTA'}.", '',
      '| Kontrola P12 | Wynik | Uwagi |', '|---|---|---|'] + [f"| {c['id']} | {'PASS' if c['pass'] else 'FAIL'} | {c['note']} |" for c in pc['checks']] + \
     ['', '| Kontrola elektryczna | Wynik | Uwagi |', '|---|---|---|'] + [f"| {c['id']} | {'PASS' if c['pass'] else 'FAIL'} | {c['note']} |" for c in el['checks']] + \
     ['', '## Próby ujemne P12', '', '| Mutacja | Kontrola docelowa | Wykryta | Zgłosiły |', '|---|---|---|---|'] + \
     [f"| {t['mutation']} | {t['target'] or '—'} | {'tak' if t['detected'] else 'nie'} | {', '.join(t['by']) or '—'} |" for t in n1] + \
     ['', '## Próby ujemne elektryczne', '', '| Mutacja | Wykryta | Zgłosiły |', '|---|---|---|'] + \
     [f"| {t['mutation']} | {'tak' if t['caught'] else 'nie'} | {', '.join(t['checks'])} |" for t in el['negative_controls']] + \
     ['', 'Tylko schemat: PCB nie powstało (layout robi sesja lokalna). Kontrole plików nie zastępują odbioru na sprzęcie.',
      'Model pełnego wariantu używa zamrożonego P04-R2.1 (P04 w S1 jeszcze nie istnieje) — do powtórzenia przy P04 w S1.',
      'Ostrzeżenie kicad-cli „schemat posiada błędy numeracji” dotyczy oznaczenia `J_P12` bez numeru (jak `J_BP` w P02 R4 i P06 R2); ERC go nie zgłasza.']
(P / 'verification/QA.md').write_text('\n'.join(qa) + '\n', encoding='utf-8')
files = sorted(p for d in ('eda', 'src', 'docs', 'output', 'reference') for p in (P / d).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
files += sorted(p for p in (P / 'verification').glob('*') if p.is_file() and p.name != 'manifest.json') + [P / 'README.md']
(P / 'verification/manifest.json').write_text(json.dumps({p.relative_to(P).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.exists()}, indent=1) + '\n')
print('Gotowe: przejrzyj output/pdf/P11-R2-schemat.pdf i verification/QA.md.')
