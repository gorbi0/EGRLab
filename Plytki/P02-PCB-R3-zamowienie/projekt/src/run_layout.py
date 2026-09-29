"""Rebuild the P02 R2 layout from the netlist: board, stackup, locked power paths, Freerouting,
import, rules, clean-up, DRC. Silkscreen and release steps run separately (see verification/QA.md).
usage: python src/run_layout.py [--reuse-ses]   (KiCad Python; Freerouting 2.1.0 + JRE 21 from the EGRLab toolchains)
--reuse-ses keeps routing/P02.ses (Freerouting is multi-threaded and not repeatable run to run).
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
        '-o', out, 'eda/P02.kicad_pcb', cwd=P, stdout=subprocess.DEVNULL)
    d = json.loads((P / out).read_text())
    c = collections.Counter(v['type'] for v in d['violations'])
    print(out, dict(c), 'unconnected', len(d['unconnected_items']), 'parity', len(d['schematic_parity']))
    return d


for s in ['build_board.py', 'set_stackup.py', 'route_critical.py', 'prepare_routing.py']:
    run(PY, s)
run(CLI, 'pcb', 'drc', '--format', 'json', '--severity-all', '-o', 'routing/critical-drc.json', 'eda/P02.kicad_pcb', cwd=P, stdout=subprocess.DEVNULL)
ses = P / 'routing/P02.ses'
if '--reuse-ses' not in sys.argv:
    ses.unlink(missing_ok=True)
    with open(P / 'routing/freerouting-stdout.log', 'w') as log:
        run(FR / 'jdk-21.0.12.1+1-jre/bin/java.exe', '-Xmx3g', '-jar', FR / 'freerouting-2.1.0.jar', '-de', 'P02.dsn', '-do', 'P02.ses', '-mp', '40', '-mt', '1', '-oit', '2', '--router.max_passes=40', '--router.max_threads=1', '-da',
            '--gui.enabled=false', cwd=P / 'routing', stdout=log, stderr=subprocess.STDOUT)
assert ses.exists()
run(PY, 'import_routing.py'); run(PY, 'set_rules.py')
drc('routing/postroute-drc.json')
# R3: starved pads matched by UUID from the DRC report (R2 parsed the English text 'PTH pad n ... of Ref',
# which a Polish KiCad reports as 'Pole PTH n ... na Ref': U5.9/U5.12 then stayed starved).
import pcbnew
ids={i['uuid'] for v in json.loads((P/'routing/postroute-drc.json').read_text())['violations'] if v['type']=='starved_thermal' for i in v['items']}
brd=pcbnew.LoadBoard(str(P/'eda/P02.kicad_pcb'))
starved=sorted({f'{f.GetReference()}.{a.GetNumber()}' for f in brd.GetFootprints() for a in f.Pads() if a.m_Uuid.AsString() in ids})
print('starved thermals (solid connection):', starved)
run(PY, 'cleanup.py', *starved); run(PY, 'set_rules.py')
drc('routing/postclean-drc.json')
