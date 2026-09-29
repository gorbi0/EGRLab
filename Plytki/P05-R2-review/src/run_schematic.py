"""P05-R2, stage 1 (schematic): regenerate the schematic, tables, ERC, netlist and the electrical checks.
The layout stage moved to board format S1 (Plytki/Format-S1); the unfinished R1-outline layout work is kept in
wip-layout-obrys-R1/ as a decoupling pattern only. usage: python src/run_schematic.py  (KiCad Python)"""
from pathlib import Path
import subprocess, sys, os
P = Path(__file__).resolve().parents[1]; PY = sys.executable
CLI = os.environ.get('KICAD_CLI', str(Path(PY).with_name('kicad-cli.exe')))
PDFTOPPM = os.environ.get('PDFTOPPM')


def run(*a, cwd=P / 'src', quiet=False):
    print('>', ' '.join(str(x) for x in a), flush=True)
    subprocess.run([str(x) for x in a], cwd=cwd, check=True, **({'stdout': subprocess.DEVNULL, 'stderr': subprocess.DEVNULL} if quiet else {}))


for d in ('verification', 'output/pdf', 'output/previews'): (P / d).mkdir(parents=True, exist_ok=True)
run(PY, 'build_schematic.py'); run(PY, 'make_tables.py')
run(CLI, 'sch', 'erc', '--severity-all', '--format', 'json', '-o', 'verification/erc.json', 'eda/P05.kicad_sch', cwd=P, quiet=True)
run(CLI, 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', 'verification/P05.xml', 'eda/P05.kicad_sch', cwd=P, quiet=True)
run(PY, 'verify_schematic.py'); run(PY, 'verify_electrical.py')
run(CLI, 'sch', 'export', 'pdf', '-o', 'output/pdf/P05-R2-schemat.pdf', 'eda/P05.kicad_sch', cwd=P, quiet=True)
if PDFTOPPM:
    run(PDFTOPPM, '-png', '-scale-to', '2200', 'output/pdf/P05-R2-schemat.pdf', 'output/previews/sch-1', cwd=P, quiet=True)
print('P05-R2 schematic stage complete. Layout: format S1 (not in this package).')
