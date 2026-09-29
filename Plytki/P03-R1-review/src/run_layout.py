"""Rebuild the P03 R1 layout from the netlist: board, rules, stackup, locked supply feed and decoupling stubs, Freerouting,
import, rules, clean-up, GND stitching, DRC. Silkscreen and release steps run separately (see verification/QA.md).
usage: python src/run_layout.py [--reuse-ses]   (KiCad Python; Freerouting 2.1.0 + JRE 21 from the EGRLab toolchains)
--reuse-ses keeps routing/P03.ses (Freerouting is multi-threaded and not repeatable run to run).
Without it Freerouting is run again (up to 8 times) while the clean-up finds a GND pad cut off from both pours.
"""
from pathlib import Path
import subprocess, sys, os, json, collections
P = Path(__file__).resolve().parents[1]; PY = sys.executable
FR = Path(os.environ.get('EGRLAB_FREEROUTING', 'C:/Users/tgorbacz/.codex/.chatgpt-projects/g-p-6a8827e57cc881919b26f761377a7bd3/.egrlab-toolchains/freerouting'))
CLI = os.environ.get('KICAD_CLI', 'C:/Program Files/KiCad/10.0/bin/kicad-cli.exe')


def run(*a, cwd=P / 'src', **k):
    print('>', ' '.join(str(x) for x in a)); subprocess.run([str(x) for x in a], cwd=cwd, check=True, **k)


def drc(out):
    run(CLI, 'pcb', 'drc', '--format', 'json', '--severity-all', '--schematic-parity', '--all-track-errors', '--refill-zones',
        '-o', out, 'eda/P03.kicad_pcb', cwd=P, stdout=subprocess.DEVNULL)
    d = json.loads((P / out).read_text())
    c = collections.Counter(v['type'] for v in d['violations'])
    print(out, dict(c), 'unconnected', len(d['unconnected_items']), 'parity', len(d['schematic_parity']))
    return d


for s in ['build_board.py', 'set_rules.py', 'set_stackup.py', 'route_critical.py', 'prepare_routing.py']:  # rules first: the DSN carries the Power class
    run(PY, s)
run(CLI, 'pcb', 'drc', '--format', 'json', '--severity-all', '-o', 'routing/critical-drc.json', 'eda/P03.kicad_pcb', cwd=P, stdout=subprocess.DEVNULL)
ses = P / 'routing/P03.ses'; reuse = '--reuse-ses' in sys.argv; attempts = []
for attempt in range(1, 2 if reuse else 9):
    if not reuse:
        ses.unlink(missing_ok=True)
        with open(P / 'routing/freerouting-stdout.log', 'w') as log:
            run(FR / 'jdk-21.0.12.1+1-jre/bin/java.exe', '-jar', FR / 'freerouting-2.1.0.jar', '-de', 'P03.dsn', '-do', 'P03.ses', '-mp', '100', '-da',
                '--gui.enabled=false', cwd=P / 'routing', stdout=log, stderr=subprocess.STDOUT)
    assert ses.exists()
    run(PY, 'import_routing.py'); run(PY, 'set_rules.py')
    d = drc('routing/postroute-drc.json')
    starved = sorted({i['description'].split(' na ')[-1] + '.' + i['description'].split('PTH ')[1].split(' ')[0]
                      for v in d['violations'] if v['type'] == 'starved_thermal' for i in v['items'] if 'Pole PTH' in i['description']})
    rc = subprocess.run([PY, 'cleanup.py', *starved], cwd=P / 'src').returncode
    attempts.append({'attempt': attempt, 'postroute_unconnected': len(d['unconnected_items']), 'cleanup_ok': rc == 0})
    if rc == 0:
        break
    print(f'attempt {attempt}: GND pad(s) cut off from the pours -> new Freerouting run')
else:
    sys.exit('no complete routing: ' + json.dumps(attempts))
(P / 'routing/attempts.json').write_text(json.dumps(attempts, indent=1) + chr(10))
run(PY, 'set_rules.py'); run(PY, 'stitch.py'); run(PY, 'set_rules.py')
for k in range(3):  # a pad can become starved only after the clean-up (freed or moved copper): solidify and refill again
    d = drc('routing/postclean-drc.json')
    more = sorted({i['description'].split(' na ')[-1] + '.' + i['description'].split('PTH ')[1].split(' ')[0]
                   for v in d['violations'] if v['type'] == 'starved_thermal' for i in v['items'] if 'Pole PTH' in i['description']})
    if not more:
        break
    starved = sorted(set(starved) | set(more)); run(PY, 'cleanup.py', *starved); run(PY, 'set_rules.py')
