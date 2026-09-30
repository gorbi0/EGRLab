"""Negative controls: working copies of the finished P03 R6 board with one deliberate defect each (plus a null control: an unchanged
copy). verify_pcb.py must fail the named check on every defective copy and pass everything on the null control.
eda/P03.kicad_pcb is never modified; copies and their reports stay in verification/negative-controls/ (not production files).
Each copy gets the project, the schematic sheets and absolute library tables, so DRC and parity run as on the release board.
(Pattern of P02 R4 negative_controls.py; defects chosen for the P03 checks.)
"""
from pathlib import Path
import pcbnew as p, json, subprocess, sys, shutil, os, math
from sexpr import parse, dump
P = Path(__file__).resolve().parents[1]; src = P / 'eda/P03.kicad_pcb'; root = P / 'verification/negative-controls'
mm = p.FromMM


def xy(x, y):
    return p.VECTOR2I(mm(x), mm(y))


def fp(b, r):
    return next(f for f in b.GetFootprints() if f.GetReference() == r)


def pad(b, r, n):
    return next(a for a in fp(b, r).Pads() if a.GetNumber() == n)


def move(b, r, dx, dy):
    f = fp(b, r); f.SetPosition(xy(p.ToMM(f.GetPosition().x) + dx, p.ToMM(f.GetPosition().y) + dy))


def away(b, r, n, ur, un, d=10):
    """Move part r by d mm along the line from pin ur.un to its pad n (further from that pin)."""
    u, c = pad(b, ur, un).GetPosition(), pad(b, r, n).GetPosition()
    dx, dy = p.ToMM(c.x - u.x), p.ToMM(c.y - u.y); k = math.hypot(dx, dy) or 1
    move(b, r, d * dx / k, d * dy / k)


def mount_shift(b): move(b, 'H1', .5, 0)                                            # hole 0.5 mm off the S1 grid
def jbp_shift(b): move(b, 'J_BP2', 1.0, 0)                                          # edge-A connector off x = 80.0
def sv_no_gnd_end(b): pad(b, 'J_SV1', '13').SetNet(pad(b, 'J_SV1', '12').GetNet())  # last pin not GND
def sv_pin_without_resistor(b): pad(b, 'J_SV3', '2').SetNet(b.FindNet('MCU_ARM'))   # MCU_ARM straight to the pin
def usb_far(b): move(b, 'M1', 0, -2.0)                                              # USB-C face 8 mm inside edge B
def sd_far(b): move(b, 'SD1', 0, -2.0)                                              # card tip 8 mm inside edge B
def decap_far(b): away(b, 'C9', '1', 'U21', '14')                                   # 100 nF 10 mm further from U21.14
def term_far(b): away(b, 'R36', '1', 'U21', '6')                                    # ADC_SCLK source termination away from U21
def r43_far(b): away(b, 'R43', '1', 'J_BP2', '16', 12)                              # PFAIL_N pull-up away from J_BP2.16


def antenna_track(b):                                                               # GND track under the antenna
    z = next(z for z in b.Zones() if z.GetZoneName() == 'ANTENNA M1'); bb = z.Outline().BBox()
    y = p.ToMM(bb.GetCenter().y); x0, x1 = p.ToMM(bb.GetLeft()) + 3, p.ToMM(bb.GetRight()) - 3
    t = p.PCB_TRACK(b); t.SetLayer(p.B_Cu); t.SetWidth(mm(.3)); t.SetStart(xy(x0, y)); t.SetEnd(xy(x1, y)); t.SetNet(b.FindNet('GND')); b.Add(t)


def spine_neck(b):                                                                  # one segment of the 5 V spine thinned to 0.6 mm
    t = max((t for t in b.GetTracks() if not isinstance(t, p.PCB_VIA) and t.IsLocked() and t.GetNetname() == '5V_M1'), key=lambda t: t.GetLength())
    t.SetWidth(mm(.6))


def supout_long(b):                                                                 # 40 mm extra SUP_N_OUT copper
    a = pad(b, 'R41', '2').GetPosition(); x, y = p.ToMM(a.x), p.ToMM(a.y)
    t = p.PCB_TRACK(b); t.SetLayer(p.B_Cu); t.SetWidth(mm(.3)); t.SetStart(xy(x, y)); t.SetEnd(xy(x, y + 40)); t.SetNet(b.FindNet('SUP_N_OUT')); b.Add(t)


def ref_on_part(b):                                                                 # a visible reference inside U1's courtyard
    f = fp(b, 'R5'); c = fp(b, 'U1'); f.Reference().SetVisible(True)
    bb = c.GetBoundingBox(); f.Reference().SetPosition(bb.GetCenter())


def null_control(b): pass


CASES = [(null_control, None), (mount_shift, 'M3 holes'), (jbp_shift, 'J_BP1..3'), (sv_no_gnd_end, 'Service headers'),
         (sv_pin_without_resistor, 'Service headers'), ('too_tall', 'Every part <='), (usb_far, 'M1 Waveshare'), (sd_far, 'SD1 Adafruit'),
         (antenna_track, 'ANTENNA keepout'), (spine_neck, '5 V path'), (decap_far, 'Decoupling'), (term_far, 'Series / termination'),
         (r43_far, 'README layout requirements'), (supout_long, 'SUP_N_OUT copper'), ('label_missing', 'Service headers'),
         (ref_on_part, 'Every visible reference')]
assert root.resolve().is_relative_to(P.resolve()) and root.name == 'negative-controls'
shutil.rmtree(root, ignore_errors=True); root.mkdir(parents=True)
labels = json.loads((P / 'routing/silkscreen.json').read_text(encoding='utf-8'))['service_labels']
results = []
for fn, expected in CASES:
    name = fn if isinstance(fn, str) else fn.__name__; d = root / name; d.mkdir()
    b = p.LoadBoard(str(src)); env = dict(os.environ)
    if callable(fn):
        fn(b)
    if name == 'too_tall':
        env['P03_HEIGHT_OVERRIDE'] = 'M1=17.5'
    b.BuildConnectivity(); p.ZONE_FILLER(b).Fill(b.Zones())
    copy = d / 'P03.kicad_pcb'; p.SaveBoard(str(copy), b)
    if name == 'label_missing':                                            # silk label of J_SV3 pin 2 deleted at file level
        t = parse(copy.read_text(encoding='utf-8')); lab = labels['J_SV3.2']; n0 = len(t)
        t = [g for g in t if not (isinstance(g, list) and g and g[0] == 'gr_text' and g[1] == lab)]
        assert len(t) < n0, lab
        copy.write_text(dump(t) + '\n', encoding='utf-8')
    for f in (P / 'eda').glob('*.kicad_sch'):
        shutil.copy2(f, d / f.name)
    shutil.copy2(P / 'eda/P03.kicad_pro', d / 'P03.kicad_pro')
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
