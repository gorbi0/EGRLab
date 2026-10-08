"""M1-R1 (schematic stage): build -> tables -> ERC -> netlist -> pin-by-pin check -> M1 checks (with negative / null controls) -> PDF/PNG ->
verification/QA.md + manifest. Cloud / local: scripts/egrlab-docker python3 src/run_schematic.py (KICAD_CLI or next to Python)."""
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
run('erc', CLI, 'sch', 'erc', '--severity-all', '--format', 'json', '-o', 'verification/erc.json', 'eda/M1.kicad_sch')
run('netlist', CLI, 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', 'verification/M1.xml', 'eda/M1.kicad_sch')
run('schematic-check', PY, 'src/verify_schematic.py')
run('m1-check', PY, 'src/verify_m1.py')
run('schematic-pdf', CLI, 'sch', 'export', 'pdf', '-o', 'output/pdf/M1-R1-schemat.pdf', 'eda/M1.kicad_sch')
for old in (P / 'output/previews').glob('sch-*.png'): old.unlink()
run('render-sch', PDFTOPPM, '-scale-to', '2200', '-png', 'output/pdf/M1-R1-schemat.pdf', 'output/previews/sch')
prl = P / 'eda/M1.kicad_prl'
if prl.exists(): prl.unlink()
run('qa', PY, 'src/make_qa.py')
files = sorted(p for d in ('eda', 'src', 'docs', 'output', 'reference') for p in (P / d).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
files += sorted(p for p in (P / 'verification').glob('*') if p.is_file() and p.name != 'manifest.json') + [P / 'README.md']
(P / 'verification/manifest.json').write_text(json.dumps({p.relative_to(P).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.exists()}, indent=1) + '\n')
print('Gotowe: output/pdf/M1-R1-schemat.pdf, verification/QA.md.')
