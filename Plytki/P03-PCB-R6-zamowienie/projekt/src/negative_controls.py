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


def track(b, layer, x0, y0, x1, y1, netname, w=.3):
    t = p.PCB_TRACK(b); t.SetLayer(layer); t.SetWidth(mm(w)); t.SetStart(xy(x0, y0)); t.SetEnd(xy(x1, y1)); t.SetNet(b.FindNet(netname)); b.Add(t)


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


def spine_long(b):   # 1.10 (review): exercises the 50 mOhm limit itself (spine_neck breaks the path) - the longest 5V_M1 spine
    # segment without a via inside is bypassed by a detour 60 mm longer (~ +20 mOhm at 1.5 mm); the original drops to 0.3 mm (no Remove())
    vias = [(p.ToMM(v.GetPosition().x), p.ToMM(v.GetPosition().y)) for v in b.GetTracks() if isinstance(v, p.PCB_VIA)]
    def inner_via(t):
        a, c = (p.ToMM(t.GetStart().x), p.ToMM(t.GetStart().y)), (p.ToMM(t.GetEnd().x), p.ToMM(t.GetEnd().y)); ln = math.dist(a, c)
        return any(.01 < math.dist(a, v) < ln - .01 and abs(math.dist(a, v) + math.dist(v, c) - ln) < 1e-3 for v in vias)
    t = max((t for t in b.GetTracks() if not isinstance(t, p.PCB_VIA) and t.IsLocked() and t.GetNetname() == '5V_M1' and p.ToMM(t.GetWidth()) >= 1.2
             and not inner_via(t)), key=lambda t: t.GetLength())
    sx, sy, ex, ey = p.ToMM(t.GetStart().x), p.ToMM(t.GetStart().y), p.ToMM(t.GetEnd().x), p.ToMM(t.GetEnd().y); L = math.hypot(ex - sx, ey - sy)
    d = math.sqrt(((L + 60) / 2) ** 2 - (L / 2) ** 2); ux, uy = (ex - sx) / L, (ey - sy) / L; mx, my = (sx + ex) / 2 - uy * d, (sy + ey) / 2 + ux * d
    for (x0, y0), (x1, y1) in (((sx, sy), (mx, my)), ((mx, my), (ex, ey))):
        n = p.PCB_TRACK(b); n.SetLayer(t.GetLayer()); n.SetWidth(t.GetWidth()); n.SetStart(xy(x0, y0)); n.SetEnd(xy(x1, y1)); n.SetNet(t.GetNet())
        n.SetLocked(True); b.Add(n)
    t.SetWidth(mm(.3))


def ref_far(b):                                                                     # R1's reference printed on C9 (review 1.10)
    f = fp(b, 'R1'); f.Reference().SetVisible(True); f.Reference().SetPosition(fp(b, 'C9').GetPosition())


def strip_part(b): fp(b, 'C9').SetPosition(xy(12.0, 5.0))                           # C9 in the reserved strip of J_BP1 (edge A, slot S1)
def zone_copper(b): track(b, p.B_Cu, 6.0, 13.0, 6.0, 15.0, 'GND')                    # GND track 2 mm from the centre of H1 (D7 zone)
def r70_1k(b): fp(b, 'R70').SetValue('1K / 1%')                                     # SUP_N_OUT service resistor back to 1K (review 1.10)
def lib_pad_changed(b): pad(b, 'J_SV1', '5').SetDrillSize(xy(.8, .8))               # pad of a silk-trimmed header differs from the library


def ref_on_part(b):                                                                 # a visible reference inside U1's courtyard
    f = fp(b, 'R5'); c = fp(b, 'U1'); f.Reference().SetVisible(True)
    bb = c.GetBoundingBox(); f.Reference().SetPosition(bb.GetCenter())


def null_control(b): pass


CASES = [(null_control, None), (mount_shift, 'M3 holes'), (jbp_shift, 'J_BP1..3'), (sv_no_gnd_end, 'Service headers'),
         (sv_pin_without_resistor, 'Service headers'), ('too_tall', 'Every part <='), (usb_far, 'M1 Waveshare'), (sd_far, 'SD1 Adafruit'),
         (antenna_track, 'ANTENNA keepout'), (spine_neck, '5 V path'), (decap_far, 'Decoupling'), (term_far, 'Series / termination'),
         (r43_far, 'README layout requirements'), (supout_long, 'SUP_N_OUT copper'), ('label_missing', 'Service headers'),
         (ref_on_part, 'Every visible reference'), (spine_long, '5 V path'), (ref_far, 'Every visible reference nearer'),
         ('label_swap', 'Service headers'), ('gnd_label_missing', 'Service headers'), (strip_part, 'Reserved strip of edge A'),
         (zone_copper, 'Standoff zones D7'), (r70_1k, 'SUP_N_OUT copper'), ('title_wrong', 'Silkscreen: board name'),
         (lib_pad_changed, 'Fresh native DRC')]
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
    if name == 'label_swap':                                               # labels of J_SV1 pins 4 and 5 (MEAS_BANK / CS_ILOG_N) swapped
        t = parse(copy.read_text(encoding='utf-8')); l4, l5 = labels['J_SV1.4'], labels['J_SV1.5']; k = 0
        for g in t:
            if isinstance(g, list) and g and g[0] == 'gr_text' and g[1] in (l4, l5):
                g[1] = l5 if g[1] == l4 else l4; k += 1
        assert k == 2, k
        copy.write_text(dump(t) + '\n', encoding='utf-8')
    if name in ('gnd_label_missing', 'title_wrong'):                       # GND label at J_SV2 pin 1 deleted / board name without the slots
        c = pad(b, 'J_SV2', '1').GetPosition(); cx = p.ToMM(c.x); t = parse(copy.read_text(encoding='utf-8')); n0 = len(t)
        def at(g):
            return next(x for x in g if isinstance(x, list) and x and x[0] == 'at')
        if name == 'gnd_label_missing':
            t = [g for g in t if not (isinstance(g, list) and g and g[0] == 'gr_text' and g[1] == 'GND' and abs(float(at(g)[1]) - cx) < 1.3 and float(at(g)[2]) > 86)]
            assert len(t) == n0 - 1, n0 - len(t)
        else:
            k = 0
            for g in t:
                if isinstance(g, list) and g and g[0] == 'gr_text' and g[1] == 'P03 R6 S1-L S1-S3':
                    g[1] = 'P03 R6 S1-L'; k += 1
            assert k == 1, k
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
