"""Rebuild and check the whole P03 R5 package in the order given in verification/QA.md.
usage (KiCad Python): python src/run_release.py [--new-route]; then inspect the PDFs, update verification/visual-review.json
and run python src/package_release.py (manifest + ZIP; refuses stale visual review or stale DRC provenance).
Without --new-route the recorded router result routing/P03.ses is imported again, so the board is
reproduced exactly; --new-route runs Freerouting 2.1.0 (multi-threaded, differs run to run).
"""
from pathlib import Path
import subprocess, sys, os, json, hashlib, zipfile, shutil
P = Path(__file__).resolve().parents[1]; PY = sys.executable
CLI = os.environ.get('KICAD_CLI', str(Path(PY).with_name('kicad-cli.exe')))
PDFTOPPM = os.environ.get('PDFTOPPM', 'C:/Users/tgorbacz/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe')


def run(*a, cwd=P / 'src', **k):
    print('>', ' '.join(str(x) for x in a), flush=True); subprocess.run([str(x) for x in a], cwd=cwd, check=True, **k)


quiet = dict(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for junk in ['verification/silk-free-debug.png', 'verification/place-drc.json']:
    (P / junk).unlink(missing_ok=True)
# 1. schematic
run(PY, 'build_schematic.py')
run(CLI, 'sch', 'erc', '--severity-all', '--format', 'json', '-o', 'verification/erc.json', 'eda/P03.kicad_sch', cwd=P, **quiet)
run(CLI, 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', 'verification/P03.xml', 'eda/P03.kicad_sch', cwd=P, **quiet)
run(PY, 'verify_schematic.py'); run(PY, 'compare_v61.py'); run(PY, 'verify_function.py'); run(PY, 'verify_reset.py')
run(CLI, 'sch', 'export', 'pdf', '-o', 'output/pdf/P03-R5-schemat.pdf', 'eda/P03.kicad_sch', cwd=P, **quiet)
if Path(PDFTOPPM).exists():
    run(PDFTOPPM, '-png', '-r', '60', 'output/pdf/P03-R5-schemat.pdf', 'output/previews/sch', cwd=P)
# 2. layout and silkscreen
run(PY, 'run_layout.py', *([] if '--new-route' in sys.argv else ['--reuse-ses']))
(P / 'verification/silkscreen-placement.json').unlink(missing_ok=True)
run(PY, 'silkscreen.py'); run(PY, 'set_rules.py')
# 3. checks
run(PY, 'verify_pcb.py'); run(PY, 'negative_controls.py'); run(PY, 'check_revision.py')
run(PY, str(P / 'verification/check_tables.py'))
# 4. views and document
for side in ('top', 'bottom'):
    run(CLI, 'pcb', 'render', '--side', side, '--width', '2400', '--height', '1800', '--quality', 'basic', '-o', f'output/previews/render-{side}.png',
        'eda/P03.kicad_pcb', cwd=P, **quiet)
run(PY, 'make_pdf.py')
print('P03-R5 generation and checks complete. Next: src/audit_rebuild.py, visual review of both PDFs, then src/package_release.py.')
