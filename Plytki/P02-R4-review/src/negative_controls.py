"""Negative controls: working copies of the finished board with one deliberate defect each (plus a null control: an unchanged copy).
verify_pcb.py must fail the named check on every defective copy and pass everything on the null control.
eda/P02.kicad_pcb is never modified; copies and their reports stay in verification/negative-controls/ (not production files).
Each copy gets the project, the schematic sheets and absolute library tables, so DRC and parity run as on the release board.
"""
from pathlib import Path
import pcbnew as p, json, subprocess, sys, shutil, os
from sexpr import parse, dump, sub
P = Path(__file__).resolve().parents[1]; src = P / 'eda/P02.kicad_pcb'; root = P / 'verification/negative-controls'
mm = p.FromMM


def xy(x, y):
    return p.VECTOR2I(mm(x), mm(y))


def fp(b, r):
    return next(f for f in b.GetFootprints() if f.GetReference() == r)


def pad(b, r, n):
    return next(a for a in fp(b, r).Pads() if a.GetNumber() == n)


def move(b, r, dx, dy):
    f = fp(b, r); f.SetPosition(xy(p.ToMM(f.GetPosition().x) + dx, p.ToMM(f.GetPosition().y) + dy))


def mount_shift(b): move(b, 'H1', .5, 0)                                  # hole 0.5 mm off the S1 grid
def jbp_shift(b): move(b, 'J_BP', 1.0, 0)                                 # edge-A connector off x = 133.5
def sv_no_gnd_end(b): pad(b, 'J_SV1', '13').SetNet(pad(b, 'J_SV1', '12').GetNet())   # last pin not GND
def sv_pin_without_resistor(b): pad(b, 'J_SV2', '2').SetNet(b.FindNet('P02_GATE'))   # GATE straight to the pin
def neck_5a(b):                                                           # BAT_IN pour squeezed to a 2.4 mm strip
    z = next(z for z in b.Zones() if z.GetZoneName().startswith('PWR P02_BAT_IN')); o = z.Outline(); o.RemoveAllContours(); o.NewOutline()
    for x, y in [(75.4, 22.8), (93.6, 22.8), (93.6, 25.2), (75.4, 25.2)]:
        o.Append(mm(x), mm(y))
def decap_far(b): move(b, 'C28', 10, 5)                                   # 100 nF 10 mm away from U9
def tab_foreign(b):                                                       # GND track under the tab of Q1
    t = p.PCB_TRACK(b); t.SetLayer(p.F_Cu); t.SetWidth(mm(.3)); t.SetStart(xy(71.5, 33.5)); t.SetEnd(xy(71.5, 41.0)); t.SetNet(b.FindNet('GND')); b.Add(t)
def corridor_track(b):                                                    # signal track in the B.Cu GND return corridor
    t = p.PCB_TRACK(b); t.SetLayer(p.B_Cu); t.SetWidth(mm(.3)); t.SetStart(xy(104, 45)); t.SetEnd(xy(104, 55)); t.SetNet(b.FindNet('PSU_OK')); b.Add(t)
def hold_far(b): move(b, 'C12', -25, 0)                                   # C_H 25 mm away from D1/D2
def null_control(b): pass


CASES = [(null_control, None), (mount_shift, 'M3 holes'), (jbp_shift, 'J_BP (edge A)'), (sv_no_gnd_end, 'Service headers'),
         (sv_pin_without_resistor, 'Service headers'), ('too_tall', 'Every part <='), (neck_5a, '5 A path'), (decap_far, 'Decoupling'),
         (tab_foreign, 'TO-220'), (corridor_track, 'GND return corridor'), (hold_far, 'C_H, D2 and D1'), ('label_missing', 'Service headers')]
assert root.resolve().is_relative_to(P.resolve()) and root.name == 'negative-controls'
shutil.rmtree(root, ignore_errors=True); root.mkdir(parents=True)
results = []
for fn, expected in CASES:
    name = fn if isinstance(fn, str) else fn.__name__; d = root / name; d.mkdir()
    b = p.LoadBoard(str(src)); env = dict(os.environ)
    if callable(fn):
        fn(b)
    if name == 'too_tall':
        parts = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8')); parts['D3']['height_mm'] = 23.0
        (d / 'parts.json').write_text(json.dumps(parts), encoding='utf-8'); env['P02_PARTS_JSON'] = str(d / 'parts.json')
    b.BuildConnectivity(); p.ZONE_FILLER(b).Fill(b.Zones())
    copy = d / 'P02.kicad_pcb'; p.SaveBoard(str(copy), b)
    if name == 'label_missing':                                            # silk label of J_SV2 pin 4 (VMOTOR) deleted at file level
        t = parse(copy.read_text(encoding='utf-8'))
        t = [g for g in t if not (isinstance(g, list) and g and g[0] == 'gr_text' and g[1] == 'VMOTOR')]
        copy.write_text(dump(t) + '\n', encoding='utf-8')
    for f in (P / 'eda').glob('*.kicad_sch'):
        shutil.copy2(f, d / f.name)
    shutil.copy2(P / 'eda/P02.kicad_pro', d / 'P02.kicad_pro')
    for tbl in ('fp-lib-table', 'sym-lib-table'):
        (d / tbl).write_text((P / 'eda' / tbl).read_text().replace('${KIPRJMOD}', (P / 'eda').as_posix()))
    subprocess.run([sys.executable, str(P / 'src/verify_pcb.py'), str(copy), str(d)], capture_output=True, text=True, env=env)
    rep = json.loads((d / 'pcb-checks.json').read_text(encoding='utf-8'))
    failed = [c['check'] for c in rep['checks'] if not c['pass']]
    hit = (not failed) if expected is None else any(c.startswith(expected) for c in failed)
    results.append({'control': name, 'expected_failing_check': expected or 'none (all PASS)', 'detected': hit, 'failed_checks': failed})
    print('OK ' if hit else 'BAD', name, '->', len(failed), 'failing checks', flush=True)
(P / 'verification/negative-controls.json').write_text(json.dumps(results, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(sum(r['detected'] for r in results), '/', len(results), 'negative controls (with the null control)')
sys.exit(0 if all(r['detected'] for r in results) else 1)
