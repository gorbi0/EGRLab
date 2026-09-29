"""Negative controls: working copies of the finished board with one deliberate defect each.
verify_pcb.py must fail the named check on every copy. eda/P00.kicad_pcb is never modified.
Copies and their reports stay in verification/negative-controls/ (not production files).
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


CASES = [(sw_rotated, 'Wurth WS-SLTV switches'), (header_flipped, 'Headers J1..J9'), (mount_shift, 'Four NPTH 3.2 mm holes'),
         (ref_inside_other, 'Every visible reference'), (decap_far, 'Capacitors at their pins'), (label_swap, 'Channel numbers'),
         (thin_supply, 'Every pre-routed (locked) segment'), (dangling_lock, 'Fresh native DRC')]
shutil.rmtree(root, ignore_errors=True); root.mkdir(parents=True)
results = []
for fn, expected in CASES:
    d = root / fn.__name__; d.mkdir()
    b = p.LoadBoard(str(src)); fn(b)
    copy = d / 'P00.kicad_pcb'; p.SaveBoard(str(copy), b)
    shutil.copy2(P / 'eda/P00.kicad_pro', d / 'P00.kicad_pro')  # same rules as the release board
    subprocess.run([sys.executable, str(P / 'src/verify_pcb.py'), str(copy), str(d)], capture_output=True, text=True)
    rep = json.loads((d / 'pcb-checks.json').read_text(encoding='utf-8'))
    failed = [c['check'] for c in rep['checks'] if not c['pass']]
    hit = any(c.startswith(expected) for c in failed)
    results.append({'control': fn.__name__, 'expected_failing_check': expected, 'detected': hit, 'failed_checks': failed})
    print('DETECTED' if hit else 'MISSED  ', fn.__name__, '->', len(failed), 'failing checks')
(P / 'verification/negative-controls.json').write_text(json.dumps(results, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(sum(r['detected'] for r in results), '/', len(results), 'negative controls detected')
sys.exit(0 if all(r['detected'] for r in results) else 1)
