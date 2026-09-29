"""Negative controls: working copies of the finished board with one deliberate defect each.
verify_pcb.py must fail the named check on every copy. eda/P03.kicad_pcb is never modified.
Copies and their reports stay in verification/negative-controls/ (not production files).
R3 (review P3-03, a defect of the R1 script): every copy gets a library table pointing at the release libraries, so the
native DRC of a copy is clean unless the defect breaks it, and a null control (unmodified copy) must pass every check.
"""
from pathlib import Path
import pcbnew as p, json, subprocess, sys, shutil
P = Path(__file__).resolve().parents[1]; src = P / 'eda/P03.kicad_pcb'; root = P / 'verification/negative-controls'
mm = p.FromMM


def xy(x, y):
    return p.VECTOR2I(mm(x), mm(y))


def fp(b, r):
    return next(f for f in b.GetFootprints() if f.GetReference() == r)


def text(b, s):
    return [x for x in b.GetDrawings() if isinstance(x, p.PCB_TEXT) and x.GetText() == s]


def m1_rotated(b):  # Waveshare board turned by 180 deg: USB-C inside the board, antenna at the edge, J1 row at the left
    fp(b, 'M1').SetOrientationDegrees(0)


def j1_inward(b):  # DAQ socket 3 mm away from the right edge: P05 header cannot reach it
    f = fp(b, 'J1'); f.SetPosition(f.GetPosition() + xy(-3, 0))


def hole_shift(b):  # H5 moved 5 mm left
    fp(b, 'H5').SetPosition(xy(150, 38))


def ref_inside_other(b):  # R1 reference placed inside the outline of U2
    fp(b, 'R1').Reference().SetPosition(fp(b, 'U2').GetPosition() + xy(-3.8, -6))


def decap_far(b):  # C9 (U21 decoupling) moved 12 mm away
    f = fp(b, 'C9'); f.SetPosition(f.GetPosition() + xy(0, 12))


def key_swap(b):  # KEY marks of J2 (KEY 2) and J6 (KEY 3) exchanged
    a, c = text(b, 'KEY2'), text(b, 'KEY3'); pa, pc = a[0].GetPosition(), c[0].GetPosition(); a[0].SetPosition(pc); c[0].SetPosition(pa)


def name_swap(b):  # connector names CAN and SFAULT exchanged
    a, c = text(b, 'CAN P10')[0], text(b, 'SFAULT P08')[0]; pa, pc = a.GetPosition(), c.GetPosition(); a.SetPosition(pc); c.SetPosition(pa)


def thin_supply(b):  # a locked 5V_SYS segment narrowed to 0.6 mm
    for t in b.GetTracks():
        if not isinstance(t, p.PCB_VIA) and t.GetNetname().endswith('5V_SYS') and t.IsLocked():
            t.SetWidth(mm(.6)); break


def antenna_track(b):  # a 3V3_CORE track drawn through the antenna keepout
    n = b.FindNet('3V3_CORE'); z = next(z for z in b.Zones() if z.GetZoneName() == 'ANTENNA M1'); c = z.Outline().BBox().GetCenter()
    t = p.PCB_TRACK(b); t.SetStart(c + xy(-5, 0)); t.SetEnd(c + xy(5, 0)); t.SetWidth(mm(.6)); t.SetLayer(p.B_Cu); t.SetNet(n); b.Add(t)


def sd_off_edge(b):  # SD1 (with its pull-up) moved 3 mm into the board: card end no longer at the edge
    for r in ('SD1', 'R11'):
        f = fp(b, r); f.SetPosition(f.GetPosition() + xy(0, -3))


def idc_rotated(b):  # J6 turned by 180 deg: signal row on the edge side, key position moves
    f = fp(b, 'J6'); f.SetOrientationDegrees(f.GetOrientationDegrees() + 180)


def tp_swap(b):  # TP3 (3V3_IO) and TP4 (GND) exchanged: the legend under LV03 pad 3 would read GND
    a, c = fp(b, 'TP3'), fp(b, 'TP4'); pa, pc = a.GetPosition(), c.GetPosition(); a.SetPosition(pc); c.SetPosition(pa)


def pour_split(b):  # a B.Cu track across the whole board cuts the B.Cu GND pour in two
    t = p.PCB_TRACK(b); t.SetStart(xy(1.5, 57)); t.SetEnd(xy(158.5, 57)); t.SetWidth(mm(.3)); t.SetLayer(p.B_Cu); t.SetNet(b.FindNet('MARK')); b.Add(t)
    p.ZONE_FILLER(b).Fill(b.Zones())  # the check reads the saved fill


def dangling_lock(b):  # the P00 slip class: locked 5V stub ending beside the M1 pad
    # R3: 2.54 mm. The R2 offset of 1.27 mm still touched the 1.7 mm pad with the 1 mm track, so the copy was connected and
    # DRC-clean; R2 counted the case as detected only because every copy failed DRC on missing libraries (review P3-03).
    target = next(a for a in fp(b, 'M1').Pads() if a.GetNumber() == 'J1-21').GetPosition()
    for t in b.GetTracks():
        if not isinstance(t, p.PCB_VIA) and t.GetNetname().endswith('5V_M1') and t.IsLocked() and t.GetEnd() == target:
            t.SetEnd(target + xy(2.54, 0)); break


def c3_at_wrong_pin(b):
    # Reproduce the actual R1 error: C3 near MR(3), far from VDD(6).
    f=fp(b,'C3');f.SetPosition(xy(127.18,66.3));f.SetOrientationDegrees(180)

CASES = [(c3_at_wrong_pin, 'TPS3808 C3 is at VDD 6'), (m1_rotated, 'M1 Waveshare'), (j1_inward, 'J1 DAQ'), (hole_shift, 'Five NPTH 3.2 mm holes'), (ref_inside_other, 'Every visible reference'),
         (decap_far, '100 nF at every IC'), (key_swap, 'KEY n beside'), (name_swap, 'Connector names'), (thin_supply, 'Every pre-routed (locked) segment'),
         (antenna_track, 'ANTENNA keepout'), (sd_off_edge, 'SD1 Adafruit 4682'), (idc_rotated, 'IDC box headers'), (tp_swap, 'J10 LV03 pigtail'), (pour_split, 'GND pours'), (dangling_lock, 'Fresh native DRC')]
def null_control(b):  # no defect: every check must pass and the copy's DRC must be clean
    pass


LIBS = (P / 'eda/libraries').resolve().as_posix()
table = (P / 'eda/fp-lib-table').read_text().replace('${KIPRJMOD}/libraries', LIBS)
assert root.resolve().is_relative_to(P.resolve()) and root.name == 'negative-controls'
shutil.rmtree(root, ignore_errors=True); root.mkdir(parents=True)
results = []
for fn, expected in [(null_control, None)] + CASES:
    d = root / fn.__name__; d.mkdir()
    b = p.LoadBoard(str(src)); fn(b)
    copy = d / 'P03.kicad_pcb'; p.SaveBoard(str(copy), b)
    shutil.copy2(P / 'eda/P03.kicad_pro', d / 'P03.kicad_pro')  # same rules as the release board
    (d / 'fp-lib-table').write_text(table)                       # same footprint libraries as the release board
    result = subprocess.run([sys.executable, str(P / 'src/verify_pcb.py'), str(copy), str(d)], capture_output=True, text=True)
    (d / 'runner.log').write_text(result.stdout + '\n' + result.stderr, encoding='utf-8')
    assert (d / 'pcb-checks.json').exists(), 'Verification crashed (not a detected mutation): ' + str(d / 'runner.log')
    rep = json.loads((d / 'pcb-checks.json').read_text(encoding='utf-8'))
    failed = [c['check'] for c in rep['checks'] if not c['pass']]
    drc = json.loads((d / 'drc.json').read_text(encoding='utf-8'))
    hit = (not failed and not drc['violations'] and not drc['unconnected_items']) if expected is None else any(c.startswith(expected) for c in failed)
    results.append({'control': fn.__name__, 'expected_failing_check': expected or 'none (null control: all checks pass, DRC clean)', 'detected': hit,
                    'failed_checks': failed, 'drc_violation_types': sorted({v['type'] for v in drc['violations']})})
    print('OK      ' if hit else 'MISSED  ', fn.__name__, '->', len(failed), 'failing checks', results[-1]['drc_violation_types'])
(P / 'verification/negative-controls.json').write_text(json.dumps(results, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(sum(r['detected'] for r in results), '/', len(results), 'controls as expected (1 null + defects detected)')
sys.exit(0 if all(r['detected'] for r in results) else 1)
