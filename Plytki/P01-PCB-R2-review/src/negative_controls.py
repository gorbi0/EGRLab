"""Intentional errors in disposable copies; prove the checks can fail.
R1 cases (probe_open, mount_shift, lk1_bypass) adapted to the R2 geometry, plus three R2 cases
for the review items that DRC cannot see: copper under a heatsink (PCB1-01), a missing TO-220
tab marker (PCB1-02) and a comparator net pulled next to the power rail (PCB1-03).
"""
from pathlib import Path
import pcbnew as p, subprocess, sys, json, shutil
P = Path(__file__).resolve().parents[1]; out = P / 'verification/negative-controls'; out.mkdir(exist_ok=True)
(out / 'fp-lib-table').write_text((P / 'eda/fp-lib-table').read_text().replace('${KIPRJMOD}/libraries', '${KIPRJMOD}/../../eda/libraries'))
cli = Path(sys.executable).with_name('kicad-cli.exe'); results = []
mm = p.FromMM
WANT = {'probe_open': 'Every pre-routed critical segment and via retained',
        'mount_shift': 'Four NPTH 3.2 mm mounting holes at defined centres',
        'hs_copper': 'R2/PCB1-01: no F.Cu copper under the heatsink profiles (tracks, vias, pads, zone fill)',
        'q2_tab_marker': 'R2/PCB1-02: TO-220 tab side marked on silkscreen (Q1, Q2, D2); TAB text at Q2',
        'ovref_near_rail': 'R2/PCB1-03: OV_REF<=20, OV_SENSE/UV_SENSE<=40, REF<=70 mm routed; >=5 mm from power tracks on both layers'}


def netnamed(b, name):
    key = next(str(k) for k in b.GetNetInfo().NetsByName().keys() if str(k).split('/')[-1] == name.split('/')[-1])
    n = b.FindNet(key); assert n is not None and n.GetNetname() == key, key
    return n


def track(b, net, a, c, w, layer):
    t = p.PCB_TRACK(b); t.SetNet(netnamed(b, net)); t.SetWidth(mm(w)); t.SetLayer(layer)
    t.SetStart(p.VECTOR2I(mm(a[0]), mm(a[1]))); t.SetEnd(p.VECTOR2I(mm(c[0]), mm(c[1]))); b.Add(t)


for case in ['probe_open', 'mount_shift', 'lk1_bypass', 'hs_copper', 'q2_tab_marker', 'ovref_near_rail']:
    b = p.LoadBoard(str(P / 'eda/P01.kicad_pcb')); target = out / (case + '.kicad_pcb')
    if case == 'probe_open':
        t = next(t for t in b.GetTracks() if not isinstance(t, p.PCB_VIA) and t.GetNetname().split('/')[-1] == 'P01_GATE'
                 and p.VECTOR2I(mm(101.9), mm(25.6)) in (t.GetStart(), t.GetEnd()))
        t.SetWidth(mm(.3))  # changing the locked TP2 branch is as detectable as deleting it
    elif case == 'mount_shift':
        f = next(f for f in b.GetFootprints() if f.GetReference() == 'H3'); f.SetPosition(p.VECTOR2I(mm(6), mm(115)))
    elif case == 'lk1_bypass':
        track(b, '/VPROT', (126, 36), (136, 36), 2, p.F_Cu)
    elif case == 'hs_copper':
        track(b, '/P01_VS', (40, 12), (46, 12), .5, p.F_Cu)  # under the HS1 fins
    elif case == 'q2_tab_marker':
        q2 = next(f for f in b.GetFootprints() if f.GetReference() == 'Q2')
        for g in q2.GraphicalItems():
            if isinstance(g, p.PCB_SHAPE) and g.GetLayer() == p.F_SilkS and p.ToMM(g.GetWidth()) >= .35:
                g.SetWidth(mm(.15))
    else:
        # Drag one existing OV_REF segment end next to the VS rail (a new track would not keep its
        # net on save in KiCad 10 Python; an existing segment does).
        t = max((t for t in b.GetTracks() if not isinstance(t, p.PCB_VIA) and t.GetNetname().split('/')[-1] == 'P01_OV_REF'),
                key=lambda t: t.GetLength())
        t.SetEnd(p.VECTOR2I(mm(60), mm(38.5)))
    p.SaveBoard(str(target), b, True); shutil.copy2(P / 'eda/P01.kicad_pro', target.with_suffix('.kicad_pro'))
    if case != 'lk1_bypass':
        run = subprocess.run([sys.executable, str(P / 'src/verify_pcb.py'), str(target)], capture_output=True, text=True)
        report = json.loads(target.with_suffix('.checks.json').read_text())
        failed = [c['check'] for c in report['checks'] if not c['pass']]
        detected = run.returncode == 1 and WANT[case] in failed
    else:
        report_path = out / 'lk1_bypass-drc.json'
        run = subprocess.run([str(cli), 'pcb', 'drc', '--format', 'json', '--severity-all', '--all-track-errors', '--refill-zones', '-o', str(report_path), str(target)], capture_output=True, text=True)
        report = json.loads(report_path.read_text()); failed = [v['type'] for v in report['violations']]
        detected = run.returncode == 0 and 'shorting_items' in failed
    (out / (case + '.log')).write_text(run.stdout + '\n' + run.stderr)
    results.append({'mutation': case, 'detected': detected, 'failures': failed})
print(json.dumps(results, indent=2)); (P / 'verification/negative-controls.json').write_text(json.dumps(results, indent=2) + '\n')
assert all(r['detected'] for r in results)
