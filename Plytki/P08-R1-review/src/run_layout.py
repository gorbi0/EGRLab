"""P08-R1 layout pipeline: native netlist, locked paths, saved SES, clean-up, rules, GND stitching and fresh DRC. --reuse-ses replays the reviewed routing, --replan is only a candidate-routing aid. New routing still requires DRC and visual review. Freerouting 2.1.0 / JRE21 are needed only without --reuse-ses."""
from pathlib import Path
import subprocess, sys, os, json, collections, shutil
import pcbnew as p
P = Path(__file__).resolve().parents[1]; PY = sys.executable
FR = Path(os.environ.get('EGRLAB_FREEROUTING', '.'))
CLI = os.environ.get('KICAD_CLI', str(Path(PY).with_name('kicad-cli.exe')))


def run(*a, cwd=P / 'src', check=True, **k):
    print('>', ' '.join(str(x) for x in a), flush=True); return subprocess.run([str(x) for x in a], cwd=cwd, check=check, **k)


def drc(out):
    run(CLI, 'pcb', 'drc', '--format', 'json', '--severity-all', '--schematic-parity', '--all-track-errors', '--refill-zones',
        '-o', out, 'eda/P08.kicad_pcb', cwd=P, stdout=subprocess.DEVNULL)
    d = json.loads((P / out).read_text())
    c = collections.Counter(v['type'] for v in d['violations'])
    print(out, dict(c), 'unconnected', len(d['unconnected_items']), 'parity', len(d['schematic_parity']), flush=True)
    return d


def starved(d):
    """Pads named by DRC starved_thermal, matched by UUID (independent of the KiCad UI language)."""
    ids = {i['uuid'] for v in d['violations'] if v['type'] == 'starved_thermal' for i in v['items']}
    b = p.LoadBoard(str(P / 'eda/P08.kicad_pcb'))
    return {f'{f.GetReference()}.{a.GetNumber()}' for f in b.GetFootprints() for a in f.Pads() if a.m_Uuid.AsString() in ids}


for s in ['build_board.py', 'set_stackup.py', 'route_critical.py', 'prepare_routing.py']:
    run(PY, s)
run(CLI, 'pcb', 'drc', '--format', 'json', '--severity-all', '-o', 'routing/critical-drc.json', 'eda/P08.kicad_pcb', cwd=P, stdout=subprocess.DEVNULL)
ses = P / 'routing/P08.ses'; reuse = '--reuse-ses' in sys.argv; attempts = []
if not reuse:
    assert os.environ.get('EGRLAB_FREEROUTING'), 'Set EGRLAB_FREEROUTING for a new router run; not needed to reuse the bundled SES.'
for attempt in range(1, 2 if reuse else 7):
    if not reuse:
        ses.unlink(missing_ok=True)
        with open(P / 'routing/freerouting-stdout.log', 'w') as log:
            run(FR / 'jdk-21.0.12.1+1-jre/bin/java.exe', '-Xmx4g', '-jar', FR / 'freerouting-2.1.0.jar', '-de', 'P08.dsn', '-do', 'P08.ses', '-mp', '25', '-da',
                '--gui.enabled=false', cwd=P / 'routing', stdout=log, stderr=subprocess.STDOUT, timeout=180)
    assert ses.exists()
    if not reuse:  # every router result is kept for replay/debugging (routing/attempt-N.ses, not packaged)
        shutil.copy2(ses, P / f'routing/attempt-{attempt}.ses')
    run(PY, 'import_routing.py'); run(PY, 'set_rules.py')
    rc = run(PY, 'complete_routes.py', *([] if reuse and '--replan' not in sys.argv else ['--plan']), check=reuse).returncode
    assert rc in (0, 3), 'complete_routes.py failed (script error, not a routing gap)'
    if rc == 0:
        run(PY, 'set_rules.py'); d = drc('routing/postroute-drc.json'); solid = starved(d)
        if any(x.startswith('J') for x in solid):  # harness / connector GND pads keep thermals (soldered wires): route again
            print('starved connector pad(s):', sorted(x for x in solid if x.startswith('J')), flush=True); rc = 1
        else:
            rc = run(PY, 'cleanup.py', *sorted(solid), check=reuse).returncode
            assert rc in (0, 3), 'cleanup.py failed (script error, not a routing gap)'
    attempts.append({'attempt': attempt, 'completion_and_cleanup_ok': rc == 0})
    assert rc == 0 or not reuse, 'bundled SES no longer gives a complete board'
    if rc == 0:
        break
    print(f'attempt {attempt}: no completion path or clean-up left a gap -> new Freerouting run', flush=True)
else:
    sys.exit('no complete routing: ' + json.dumps(attempts))
if not reuse:
    (P / 'routing/attempts.json').write_text(json.dumps(attempts, indent=1) + chr(10))
run(PY, 'set_rules.py'); run(PY, 'stitch.py'); run(PY, 'set_rules.py')
for k in range(4):  # a pad can become starved only after the clean-up or the stitching (changed fill): solidify and refill again
    d = drc('routing/postclean-drc.json'); more = starved(d) - solid
    if not more:
        break
    assert not any(x.startswith('J') for x in more), ('connector GND pad starved after stitching', sorted(more))
    solid |= more; run(PY, 'cleanup.py', *sorted(solid)); run(PY, 'set_rules.py')
else:
    sys.exit('starved thermals remain after 4 rounds')
(P / 'routing/solid-pads.json').write_text(json.dumps(sorted(solid)) + chr(10))
run(PY, 'trim_dangling.py')
