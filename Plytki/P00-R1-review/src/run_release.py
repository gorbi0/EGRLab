"""Rebuild and check the whole P00 R1 package in the order given in verification/QA.md.
usage (KiCad Python): python src/run_release.py [--new-route]
Without --new-route the recorded router result routing/P00.ses is imported again, so the board is
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
run(CLI, 'sch', 'erc', '--severity-all', '--format', 'json', '-o', 'verification/erc.json', 'eda/P00.kicad_sch', cwd=P, **quiet)
run(CLI, 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', 'verification/P00.xml', 'eda/P00.kicad_sch', cwd=P, **quiet)
run(PY, 'verify_schematic.py')
run(CLI, 'sch', 'export', 'pdf', '-o', 'output/pdf/P00-R1-schemat.pdf', 'eda/P00.kicad_sch', cwd=P, **quiet)
if Path(PDFTOPPM).exists():
    run(PDFTOPPM, '-png', '-r', '60', 'output/pdf/P00-R1-schemat.pdf', 'output/previews/sch', cwd=P)
# 2. layout and silkscreen
run(PY, 'run_layout.py', *([] if '--new-route' in sys.argv else ['--reuse-ses']))
(P / 'verification/silkscreen-placement.json').unlink(missing_ok=True)
run(PY, 'silkscreen.py'); run(PY, 'set_rules.py')
# 3. checks
run(PY, 'verify_pcb.py'); run(PY, 'negative_controls.py')
# 4. views and document
for side in ('top', 'bottom'):
    run(CLI, 'pcb', 'render', '--side', side, '--width', '2400', '--height', '1800', '--quality', 'basic', '-o', f'output/previews/render-{side}.png',
        'eda/P00.kicad_pcb', cwd=P, **quiet)
run(PY, 'make_pdf.py')
# 5. manifest and archive (working copies of the negative controls stay out of the archive)
skip = {'verification/negative-controls', 'src/__pycache__', 'src/tools/__pycache__'}
files = sorted(f for f in P.rglob('*') if f.is_file() and not any(f.relative_to(P).as_posix().startswith(s) for s in skip)
               and f.suffix not in ('.lck', '.kicad_prl', '.zip') and f.name != 'release-manifest.json')
man = {'package': 'P00-R1-review', 'date': '2026-09-25', 'status': 'schematic + PCB R1 for review; hardware and fit NOT EXAMINED',
       'files': {f.relative_to(P).as_posix(): hashlib.sha256(f.read_bytes()).hexdigest() for f in files}}
(P / 'release-manifest.json').write_text(json.dumps(man, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
z = P.parent / 'P00-R1-review.zip'
with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
    for f in files + [P / 'release-manifest.json']:
        zf.write(f, 'P00-R1-review/' + f.relative_to(P).as_posix())
print('manifest', len(man['files']), 'files; archive', z, hashlib.sha256(z.read_bytes()).hexdigest())
