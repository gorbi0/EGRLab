"""Negative controls: working copies of the finished board with one deliberate defect each.
verify_pcb.py must fail the named check on every copy. eda/P02.kicad_pcb is never modified.
Copies and their reports stay in verification/negative-controls/ (not production files).
"""
from pathlib import Path
import pcbnew as p, json, subprocess, sys, shutil
P = Path(__file__).resolve().parents[1]; src = P / 'eda/P02.kicad_pcb'; root = P / 'verification/negative-controls'
mm = p.FromMM


def xy(x, y):
    return p.VECTOR2I(mm(x), mm(y))


def fp(b, r):
    return next(f for f in b.GetFootprints() if f.GetReference() == r)


def vprot_neck(b):  # VPROT node zone cut above J2.1: VMOTOR no longer on the input node
    z = next(z for z in b.Zones() if z.GetZoneName() == 'VPROT input node'); o = z.Outline(); o.RemoveAllContours(); o.NewOutline()
    for x, y in [(8.3, 30.8), (21.2, 30.8), (21.2, 41.0), (8.3, 41.0)]:
        o.Append(mm(x), mm(y))


def bcu_return(b):  # a signal track through the B.Cu GND return corridor J2.2-J1.2
    t = p.PCB_TRACK(b); t.SetLayer(p.B_Cu); t.SetWidth(mm(.5)); t.SetStart(xy(12, 30)); t.SetEnd(xy(12, 38)); t.SetNet(b.FindNet('/VPROT_SENSE')); b.Add(t)


def hold_free(b):  # extra unlocked HOLD_STORE copper (unfused bank side must stay locked and minimal)
    t = p.PCB_TRACK(b); t.SetLayer(p.F_Cu); t.SetWidth(mm(1)); t.SetStart(xy(81, 27.5)); t.SetEnd(xy(81, 24)); t.SetNet(b.FindNet('HOLD_STORE')); b.Add(t)


def decap_far(b):  # C13 (U7 decoupling) moved 12 mm away
    f = fp(b, 'C13'); f.SetPosition(xy(p.ToMM(f.GetPosition().x) + 12, p.ToMM(f.GetPosition().y) - 3))


def ref_inside_other(b):  # U2 reference placed inside the outline of U1
    f = fp(b, 'U2'); u1 = fp(b, 'U1'); f.Reference().SetPosition(u1.GetPosition())


def mount_shift(b):
    f = fp(b, 'H3'); f.SetPosition(xy(6, 115))


def lv_swap(b):  # LV03 and LV04 legends swapped
    t = {x.GetText(): x for x in b.GetDrawings() if isinstance(x, p.PCB_TEXT) and x.GetText() in ('LV03', 'LV04')}
    a, c = t['LV03'].GetPosition(), t['LV04'].GetPosition(); t['LV03'].SetPosition(c); t['LV04'].SetPosition(a)


def thin_vprot(b):  # VSENSE branch of VPROT narrowed to 0.4 mm
    for t in b.GetTracks():
        if not isinstance(t, p.PCB_VIA) and t.GetNetname() == 'VPROT' and abs(p.ToMM(t.GetWidth()) - 1.2) < 1e-6:
            t.SetWidth(mm(.4))


CASES = [(vprot_neck, 'VPROT input node'), (bcu_return, '5 A return J2.2'), (hold_free, 'HOLD_STORE (unfused bank side)'),
         (decap_far, '100 nF at every IC'), (ref_inside_other, 'Every visible reference'), (mount_shift, 'Four NPTH 3.2 mm holes'),
         (lv_swap, 'Legends at their parts'), (thin_vprot, 'Power nets: narrowest track')]
shutil.rmtree(root, ignore_errors=True); root.mkdir(parents=True)
results = []
for fn, expected in CASES:
    d = root / fn.__name__; d.mkdir()
    b = p.LoadBoard(str(src)); fn(b)
    copy = d / 'P02.kicad_pcb'; p.SaveBoard(str(copy), b)
    shutil.copy2(P / 'eda/P02.kicad_pro', d / 'P02.kicad_pro')  # same rules as the release board
    subprocess.run([sys.executable, str(P / 'src/verify_pcb.py'), str(copy), str(d)], capture_output=True, text=True)
    rep = json.loads((d / 'pcb-checks.json').read_text(encoding='utf-8'))
    failed = [c['check'] for c in rep['checks'] if not c['pass']]
    hit = any(c.startswith(expected) for c in failed)
    results.append({'control': fn.__name__, 'expected_failing_check': expected, 'detected': hit, 'failed_checks': failed})
    print('DETECTED' if hit else 'MISSED  ', fn.__name__, '->', len(failed), 'failing checks')
(P / 'verification/negative-controls.json').write_text(json.dumps(results, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(sum(r['detected'] for r in results), '/', len(results), 'negative controls detected')
sys.exit(0 if all(r['detected'] for r in results) else 1)
