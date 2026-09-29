"""Rebuild the P05 R1 layout from the netlist: board, stackup, locked power paths, Freerouting,
import, rules, clean-up, DRC. Silkscreen and release steps run separately (see verification/QA.md).
usage: python src/run_layout.py [--reuse-ses]   (KiCad Python; Freerouting 2.1.0 + JRE 21 from the EGRLab toolchains)
--reuse-ses keeps routing/P05.ses (Freerouting is multi-threaded and not repeatable run to run).
"""
from pathlib import Path
import subprocess, sys, os, json, collections
P = Path(__file__).resolve().parents[1]; PY = sys.executable
FR = Path(os.environ.get('EGRLAB_FREEROUTING', '.'))
CLI = os.environ.get('KICAD_CLI', str(Path(PY).with_name('kicad-cli.exe')))


def run(*a, cwd=P / 'src', **k):
    print('>', ' '.join(str(x) for x in a)); subprocess.run([str(x) for x in a], cwd=cwd, check=True, **k)


def drc(out):
    run(CLI, 'pcb', 'drc', '--format', 'json', '--severity-all', '--schematic-parity', '--all-track-errors', '--refill-zones',
        '-o', out, 'eda/P05.kicad_pcb', cwd=P, stdout=subprocess.DEVNULL)
    d = json.loads((P / out).read_text())
    c = collections.Counter(v['type'] for v in d['violations'])
    print(out, dict(c), 'unconnected', len(d['unconnected_items']), 'parity', len(d['schematic_parity']))
    return d


for s in ['build_board.py', 'set_stackup.py', 'route_critical.py', 'prepare_routing.py']:
    run(PY, s)
run(CLI, 'pcb', 'drc', '--format', 'json', '--severity-all', '-o', 'routing/critical-drc.json', 'eda/P05.kicad_pcb', cwd=P, stdout=subprocess.DEVNULL)
ses = P / 'routing/P05.ses'
if '--reuse-ses' not in sys.argv:
    assert os.environ.get('EGRLAB_FREEROUTING'), 'Set EGRLAB_FREEROUTING for a new router run; not needed to reuse the bundled SES.'
    ses.unlink(missing_ok=True)
    with open(P / 'routing/freerouting-stdout.log', 'w') as log:
        run(FR / 'jdk-21.0.12.1+1-jre/bin/java.exe', '-Xmx4g', '-jar', FR / 'freerouting-2.1.0.jar', '-de', 'P05.dsn', '-do', 'P05.ses', '-da', '--router.max_passes=60', '--router.max_threads=4', '--router.job_timeout=00:03:00', '--router.optimizer.enabled=false',
            '--gui.enabled=false', cwd=P / 'routing', stdout=log, stderr=subprocess.STDOUT, timeout=240)
assert ses.exists()
run(PY, 'import_routing.py'); run(PY, 'set_rules.py')
run(PY, 'complete_routes.py', *(['--plan'] if '--reuse-ses' not in sys.argv else []))
run(PY, 'cleanup.py');run(PY, 'set_rules.py')
run(PY, 'prune_dangling.py');run(PY, 'set_rules.py')
drc('routing/postclean-drc.json')
