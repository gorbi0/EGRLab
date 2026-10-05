"""Rebuild the layout of the board in board.py (P10 R2; chain written for P03 R6, format S1) from the netlist: board, stackup, rules, locked power pours and anchors, Freerouting,
import, completion routes from DRC, clean-up, GND stitching, DRC. Chain and scripts from P04 R2 (complete_routes, cleanup, stitch).
usage: python src/run_layout.py [--reuse-ses] [--replan]
--reuse-ses keeps routing/<NAME>.ses and replays routing/completion-routes.json (--replan: plans them again from DRC).
Without it Freerouting runs again (up to 6 times) while no completion path is found or the clean-up would leave a gap.
Freerouting 2.1.0 stops after 30 passes (--router.stop_pass_no; the unrouted count stops falling after ~6 passes here).
30.09 (Ubuntu): fanout_gnd.py after route_critical.py (locked GND bars under the SOICs, SOT-23 stubs, J_BP GND combs), and
cleanup.py --tidy right after the SES import: Freerouting 2.1 leaves pieces of unfinished connections that blocked the
completion planner (P03 R6: 81-112 dead-end items per run).
EGRLAB_ROUTER_THREADS sets --router.max_threads (Freerouting default 1): with N threads each pass routes N boards and keeps
the best (BatchAutorouter.autoroute_pass_multi_thread -> BoardHistory.restoreBestBoard). Default 4 = the setting of the runs
that converged (30.09, with the GND plane); its own effect was not isolated (one earlier pair: 13.0 vs 12.7 open, no gain shown).
"""
from pathlib import Path
import subprocess, sys, os, json, collections, shutil
import pcbnew as p
P = Path(__file__).resolve().parents[1]; PY = sys.executable
sys.path.insert(0, str(P / 'src'))
from board import NAME
FR = Path(os.environ.get('EGRLAB_FREEROUTING', '.'))
CLI = os.environ.get('KICAD_CLI', str(Path(PY).with_name('kicad-cli.exe')))


def run(*a, cwd=P / 'src', check=True, **k):
    print('>', ' '.join(str(x) for x in a), flush=True); return subprocess.run([str(x) for x in a], cwd=cwd, check=check, **k)


def drc(out):
    run(CLI, 'pcb', 'drc', '--format', 'json', '--severity-all', '--schematic-parity', '--all-track-errors', '--refill-zones',
        '-o', out, f'eda/{NAME}.kicad_pcb', cwd=P, stdout=subprocess.DEVNULL)
    d = json.loads((P / out).read_text())
    c = collections.Counter(v['type'] for v in d['violations'])
    print(out, dict(c), 'unconnected', len(d['unconnected_items']), 'parity', len(d['schematic_parity']), flush=True)
    return d


def starved(d):
    """Pads named by DRC starved_thermal, matched by UUID (independent of the KiCad UI language)."""
    ids = {i['uuid'] for v in d['violations'] if v['type'] == 'starved_thermal' for i in v['items']}
    b = p.LoadBoard(str(P / f'eda/{NAME}.kicad_pcb'))
    return {f'{f.GetReference()}.{a.GetNumber()}' for f in b.GetFootprints() for a in f.Pads() if a.m_Uuid.AsString() in ids}


for s in ['build_board.py', 'set_stackup.py', 'set_rules.py', 'route_critical.py', 'fanout_gnd.py', 'prepare_routing.py']:
    run(PY, s)
ses = P / f'routing/{NAME}.ses'; reuse = '--reuse-ses' in sys.argv; attempts = []
if not reuse:
    assert os.environ.get('EGRLAB_FREEROUTING'), 'Set EGRLAB_FREEROUTING for a new router run; not needed to reuse the bundled SES.'
NATT = int(os.environ.get('EGRLAB_ROUTER_ATTEMPTS', '6'))
for attempt in range(1, 2 if reuse else NATT + 1):
    if not reuse:
        ses.unlink(missing_ok=True)
        try:   # P03 R6 (30.09): a stuck Freerouting run (no SES after the time limit) counts as a failed attempt, not a crash
            with open(P / 'routing/freerouting-stdout.log', 'w') as log:
                run(FR / 'jdk-21.0.12.1+1-jre/bin/java.exe', '-Xmx4g', '-jar', FR / 'freerouting-2.1.0.jar', '-de', f'{NAME}.dsn', '-do', f'{NAME}.ses', '-mp', os.environ.get('EGRLAB_ROUTER_PASSES', '30'),
                    '--router.stop_pass_no=' + os.environ.get('EGRLAB_ROUTER_PASSES', '30'), '-da', '--gui.enabled=false',
                    '--router.max_threads=' + os.environ.get('EGRLAB_ROUTER_THREADS', '4'), cwd=P / 'routing', stdout=log, stderr=subprocess.STDOUT,
                    timeout=int(os.environ.get('EGRLAB_ROUTER_TIMEOUT', '1500')))
        except subprocess.TimeoutExpired:
            attempts.append({'attempt': attempt, 'completion_and_cleanup_ok': False, 'router_timeout': True})
            print(f'attempt {attempt}: Freerouting time limit -> new run', flush=True); continue
    assert ses.exists()
    if not reuse:  # every router result is kept for replay/debugging (routing/attempt-N.ses, not packaged)
        shutil.copy2(ses, P / f'routing/attempt-{attempt}.ses')
    run(PY, 'import_routing.py'); run(PY, 'set_rules.py'); run(PY, 'cleanup.py', '--tidy'); run(PY, 'set_rules.py')   # 30.09: debris out first
    run(PY, 'stitch.py'); run(PY, 'set_rules.py')   # P02 R4: stitch first, fewer GND islands
    if not reuse:   # P05 R3 (1.10): the raster planner needs 20+ min for a hopeless remainder; such an attempt fails at once
        d0 = drc('routing/preplan-drc.json'); gaps = [u for u in d0['unconnected_items'] if not all('[GND]' in i['description'] for i in u['items'])]
        if len(gaps) > int(os.environ.get('EGRLAB_PLAN_MAX', '12')):
            attempts.append({'attempt': attempt, 'completion_and_cleanup_ok': False, 'signal_gaps_after_router': len(gaps)})
            print(f'attempt {attempt}: {len(gaps)} signal gaps after the router -> new Freerouting run', flush=True); continue
    rc = run(PY, 'complete_routes.py', *([] if reuse and '--replan' not in sys.argv else ['--plan']), check=reuse).returncode
    assert rc in (0, 3), 'complete_routes.py failed (script error, not a routing gap)'
    solid = set()
    if rc == 0:  # P02 R4: GND stitching before the clean-up, so GND pour islands left by the router are tied first
        # review 2.10: the targeted GND vias (stitch.py stage 4, board.EXTRA_GND_VIAS) only now, after the completion routes (replayed exactly)
        run(PY, 'complete_routes.py', '--ties', *([] if reuse and '--replan' not in sys.argv else ['--plan']))   # 2.10: GND tracks for long decoupling returns
        run(PY, 'set_rules.py'); run(PY, 'stitch.py', '--targeted'); run(PY, 'set_rules.py'); d = drc('routing/postroute-drc.json'); solid = starved(d)
        # P03 R6 (30.09): no harness wires on this board (the P02 rule 'connector GND pads keep thermals, soldered wires' does not
        # apply); J_BP / J_SV / M1 GND pins starved by the even-row signals get a solid pour connection like any other pad
        rc = run(PY, 'cleanup.py', *sorted(solid), check=reuse).returncode
        assert rc in (0, 3), 'cleanup.py failed (script error, not a routing gap)'
        # 2.10 (P06): an attempt with copper conflicts after the router (11 x I_L_OUT / 5VA_P06 at U1 in one run) counts as failed
        COPPER = ('clearance', 'shorting_items', 'tracks_crossing', 'hole_clearance', 'copper_edge_clearance', 'hole_to_hole')
        bad = [v['type'] for v in drc('routing/postroute-drc.json')['violations'] if v['type'] in COPPER] if rc == 0 else []
        if bad:
            assert not reuse, f'bundled SES gives copper conflicts: {bad}'
            attempts.append({'attempt': attempt, 'completion_and_cleanup_ok': False, 'copper_conflicts': len(bad)})
            print(f'attempt {attempt}: {len(bad)} copper conflicts after the router -> new Freerouting run', flush=True); continue
    attempts.append({'attempt': attempt, 'completion_and_cleanup_ok': rc == 0})
    assert rc == 0 or not reuse, 'bundled SES no longer gives a complete board'
    if rc == 0:
        break
    print(f'attempt {attempt}: no completion path or clean-up left a gap -> new Freerouting run', flush=True)
else:
    sys.exit('no complete routing: ' + json.dumps(attempts))
if not reuse:
    (P / 'routing/attempts.json').write_text(json.dumps(attempts, indent=1) + chr(10))
run(PY, 'set_rules.py')
for k in range(4):  # a pad can become starved only after the clean-up or the stitching (changed fill): solidify and refill again
    d = drc('routing/postclean-drc.json'); more = starved(d) - solid
    if not more:
        break
    solid |= more; run(PY, 'cleanup.py', *sorted(solid)); run(PY, 'set_rules.py')
else:
    sys.exit('starved thermals remain after 4 rounds')
run(PY, 'trim_stubs.py'); run(PY, 'set_rules.py')   # P05 R3: unused ends of the locked escapes (DRC track_dangling)
d = drc('routing/postclean-drc.json')
assert not d['unconnected_items'] and not [v for v in d['violations'] if v['type'] in ('track_dangling', 'via_dangling', 'starved_thermal')], 'trim left a gap'
(P / 'routing/solid-pads.json').write_text(json.dumps(sorted(solid)) + chr(10))
