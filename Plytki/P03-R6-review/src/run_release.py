"""Rebuild and check the P03 R6 package (schematic stage only; no PCB - layout is done locally, docs/CHMURA.md rule 6).
usage (KiCad Python, in the cloud: scripts/egrlab-docker python3 src/run_release.py)
Order: schematic -> ERC -> netlist -> pin-by-pin check -> v6.1 map -> functions/mutations -> reset budget -> J_BP/PFAIL/service
checks with negative controls -> tables -> table cross-check -> PDF and previews.
"""
from pathlib import Path
import subprocess, sys, os, shutil
P = Path(__file__).resolve().parents[1]; PY = sys.executable
CLI = os.environ.get('KICAD_CLI', str(Path(PY).with_name('kicad-cli.exe')))
PDFTOPPM = os.environ.get('PDFTOPPM', 'C:/Users/tgorbacz/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe')
if not Path(PDFTOPPM).exists() and shutil.which('pdftoppm'): PDFTOPPM = shutil.which('pdftoppm')


def run(*a, cwd=P / 'src', **k):
    print('>', ' '.join(str(x) for x in a), flush=True); subprocess.run([str(x) for x in a], cwd=cwd, check=True, **k)


quiet = dict(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
run(PY, 'build_schematic.py')
run(CLI, 'sch', 'erc', '--severity-all', '--format', 'json', '-o', 'verification/erc.json', 'eda/P03.kicad_sch', cwd=P, **quiet)
run(CLI, 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', 'verification/P03.xml', 'eda/P03.kicad_sch', cwd=P, **quiet)
run(PY, 'verify_schematic.py'); run(PY, 'compare_v61.py'); run(PY, 'verify_function.py'); run(PY, 'verify_reset.py'); run(PY, 'verify_jbp.py')
run(PY, 'write_tables.py'); run(PY, str(P / 'verification/check_tables.py'))
run(CLI, 'sch', 'export', 'pdf', '-o', 'output/pdf/P03-R6-schemat.pdf', 'eda/P03.kicad_sch', cwd=P, **quiet)
if Path(PDFTOPPM).exists():
    for f in (P / 'output/previews').glob('sch-*.png'): f.unlink()
    run(PDFTOPPM, '-png', '-r', '60', 'output/pdf/P03-R6-schemat.pdf', 'output/previews/sch', cwd=P)
print('P03-R6 schematic stage: generation and checks complete. PCB: local session (layout requirements in README).')
