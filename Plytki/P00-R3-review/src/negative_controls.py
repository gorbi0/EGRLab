"""Negative controls: working copies of the finished board with one deliberate defect each.
verify_pcb.py must fail the named check on every copy. eda/P00.kicad_pcb is never modified.
Copies and their reports stay in verification/negative-controls/ (not production files).
R3 (review P0-05): every copy gets a project library table pointing at the release libraries, so the native DRC of a copy
is clean unless the defect itself breaks it; a null control (unmodified copy) must pass every check.
"""
from pathlib import Path
import pcbnew as p, json, subprocess, sys, shutil
P = Path(__file__).resolve().parents[1]; src = P / 'eda/P00.kicad_pcb'; root = P / 'verification/negative-controls'
mm = p.FromMM


def xy(x, y):
    return p.VECTOR2I(mm(x), mm(y))


def fp(b, r):
    return next(f for f in b.GetFootprints() if f.GetReference() == r)


def sw_rotated(b):  # SW3 turned by 180 deg: slider up would give L, against the printed legend
    f = fp(b, 'SW3'); f.SetOrientationDegrees(270)


def header_flipped(b):  # J4 turned by 180 deg: GND on the right, against the printed legend
    f = fp(b, 'J4'); f.SetOrientationDegrees(90)


def mount_shift(b):
    fp(b, 'H3').SetPosition(xy(6, 65))


def ref_inside_other(b):  # R4 reference placed inside the outline of U1
    fp(b, 'R4').Reference().SetPosition(fp(b, 'U1').GetPosition() + xy(3.8, 3.8))


def decap_far(b):  # C3 (U1 decoupling) moved 12 mm away
    f = fp(b, 'C3'); f.SetPosition(f.GetPosition() + xy(-12, 14))


def label_swap(b):  # channel numbers 3 and 4 swapped
    t = {x.GetText(): x for x in b.GetDrawings() if isinstance(x, p.PCB_TEXT) and x.GetText() in ('3', '4')}
    a, c = t['3'].GetPosition(), t['4'].GetPosition(); t['3'].SetPosition(c); t['4'].SetPosition(a)


def thin_supply(b):  # a locked VIN_P segment narrowed to 0.35 mm
    for t in b.GetTracks():
        if not isinstance(t, p.PCB_VIA) and t.GetNetname() == '/P00_VIN_P' and t.IsLocked():
            t.SetWidth(mm(.35)); break


def dangling_lock(b):  # the R1 slip caught by DRC: locked heartbeat stub ending 1.27 mm beside the J9 pad
    for t in b.GetTracks():
        if not isinstance(t, p.PCB_VIA) and t.GetNetname() == '/P00_HEART' and t.IsLocked() and abs(p.ToMM(t.GetEnd().y) - 59) < 1e-3:
            t.SetEnd(xy(p.ToMM(t.GetEnd().x) + 1.27, 59)); t.SetStart(xy(p.ToMM(t.GetStart().x) + 1.27, p.ToMM(t.GetStart().y))); break


def preload_wrong(b):
    fp(b, 'R5').SetValue('100K / 1%')


def cout_bypassed(b):
    a = next(a for a in fp(b, 'C6').Pads() if a.GetNumber() == '2')
    a.SetNet(b.FindNet('GND'))


def null_control(b):  # no defect: must pass every check
    pass


def vin_legend_at_tp3(b):  # R2 position of the supply legend, 2 mm from TP3 (review P0-07)
    t = next(x for x in b.GetDrawings() if isinstance(x, p.PCB_TEXT) and x.GetText() == '+VIN 6-15V')
    t.SetPosition(xy(15.95, 25.4))


CASES = [(sw_rotated, 'Wurth WS-SLTV switches'), (header_flipped, 'Headers J1..J9'), (mount_shift, 'Four NPTH 3.2 mm holes'),
         (ref_inside_other, 'Every visible reference'), (decap_far, 'Capacitors at their pins'), (label_swap, 'Channel numbers'),
         (thin_supply, 'Every pre-routed (locked) segment'), (dangling_lock, 'Fresh native DRC'),
         (preload_wrong, 'R5 permanent preload'), (cout_bypassed, 'C6 return through R6'), (vin_legend_at_tp3, 'Supply legend nearest to J10')]
LIBS = (P / 'eda/libraries').resolve().as_posix()
table = (P / 'eda/fp-lib-table').read_text().replace('${KIPRJMOD}/libraries', LIBS)
assert root.resolve().is_relative_to((P / 'verification').resolve()) and root.name == 'negative-controls'
shutil.rmtree(root, ignore_errors=True); root.mkdir(parents=True)
results = []
for fn, expected in [(null_control, None)] + CASES:
    d = root / fn.__name__; d.mkdir()
    b = p.LoadBoard(str(src)); fn(b)
    copy = d / 'P00.kicad_pcb'; p.SaveBoard(str(copy), b)
    shutil.copy2(P / 'eda/P00.kicad_pro', d / 'P00.kicad_pro')  # same rules as the release board
    (d / 'fp-lib-table').write_text(table)                       # same footprint libraries as the release board
    subprocess.run([sys.executable, str(P / 'src/verify_pcb.py'), str(copy), str(d)], capture_output=True, text=True)
    rep = json.loads((d / 'pcb-checks.json').read_text(encoding='utf-8'))
    failed = [c['check'] for c in rep['checks'] if not c['pass']]
    drc = json.loads((d / 'drc.json').read_text(encoding='utf-8'))
    hit = (not failed and not drc['violations']) if expected is None else any(c.startswith(expected) for c in failed)
    results.append({'control': fn.__name__, 'expected_failing_check': expected or 'none (null control: all checks pass, DRC clean)',
                    'detected': hit, 'failed_checks': failed, 'drc_violation_types': sorted({v['type'] for v in drc['violations']})})
    print('OK      ' if hit else 'MISSED  ', fn.__name__, '->', len(failed), 'failing checks', results[-1]['drc_violation_types'])
(P / 'verification/negative-controls.json').write_text(json.dumps(results, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(sum(r['detected'] for r in results), '/', len(results), 'controls as expected (1 null + defects detected)')
sys.exit(0 if all(r['detected'] for r in results) else 1)
