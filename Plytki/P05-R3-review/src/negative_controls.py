"""Negative controls: working copies of the finished P05 R3 board with one deliberate defect each (plus a null control: an unchanged
copy). verify_pcb.py must fail the named check on every defective copy and pass everything on the null control.
eda/P10.kicad_pcb is never modified; copies and their reports stay in verification/negative-controls/ (not production files).
Each copy gets the project, the schematic sheets and absolute library tables, so DRC and parity run as on the release board.
(Pattern of P03 R6 / P09 R2 / P10 R2 negative_controls.py; defects chosen for the P05 checks; the custom rules file eda/P05.kicad_dru
is copied with every board.)
"""
from pathlib import Path
import pcbnew as p, json, subprocess, sys, shutil, os, math
from sexpr import parse, dump
sys.path.insert(0, str(Path(__file__).resolve().parent))
from board import NAME, REV, CLASS, SLOTS
TYTUL = f"{REV} S1-{CLASS} {SLOTS[0] if len(SLOTS) == 1 else SLOTS[0] + '-' + SLOTS[-1]}"   # as verify_pcb.py
P = Path(__file__).resolve().parents[1]; src = P / f'eda/{NAME}.kicad_pcb'; root = P / 'verification/negative-controls'
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


def on_net(b, r, ur, un):
    """Pad of part r on the net of pin ur.un."""
    n = pad(b, ur, un).GetNetname(); return next(a for a in fp(b, r).Pads() if a.GetNetname() == n)


def away_net(b, r, ur, un, d=10):
    away(b, r, on_net(b, r, ur, un).GetNumber(), ur, un, d)


def track(b, layer, x0, y0, x1, y1, netname, w=.3):
    t = p.PCB_TRACK(b); t.SetLayer(layer); t.SetWidth(mm(w)); t.SetStart(xy(x0, y0)); t.SetEnd(xy(x1, y1)); t.SetNet(b.FindNet(netname)); b.Add(t)


def mount_shift(b): move(b, 'H1', .5, 0)                                            # hole 0.5 mm off the S1 grid
def jbp_shift(b): move(b, 'J_BP1', 1.0, 0)                                          # edge-A connector off x = 26.5
def sv_no_gnd_end(b): pad(b, 'J_SV1', '13').SetNet(pad(b, 'J_SV1', '12').GetNet())  # last pin not GND
def sv_pin_without_resistor(b): pad(b, 'J_SV1', '4').SetNet(pad(b, 'R36', '1').GetNet())   # 5V_SYS straight to the pin
def sv_resistor_far(b): away_net(b, 'R45', 'U9', '9', 12)                           # ADC_CS service resistor 12 mm away from its node
def refcap_far(b): move(b, 'C13', -5.0, 0)                                          # REFCAP 22 uF 5 mm further (R2 README: "C13 + 5 mm")
def regcap_far(b): move(b, 'C10', 0, -3.0)                                          # REGCAP_D 1 uF 3 mm up: path > 3 mm


def refcap_via(b):                                                                  # a via in the REFCAP copper
    c = pad(b, 'C13', '1').GetPosition(); v = p.PCB_VIA(b); v.SetPosition(xy(p.ToMM(c.x) - 2.2, p.ToMM(c.y))); v.SetWidth(mm(.9)); v.SetDrill(mm(.4))
    v.SetNet(pad(b, 'C13', '1').GetNet()); b.Add(v); track(b, p.F_Cu, p.ToMM(c.x), p.ToMM(c.y), p.ToMM(c.x) - 2.2, p.ToMM(c.y), 'REFCAP')


def dout_under(b):                                                                  # DOUT on B.Cu under U1 (review P5-01)
    c = pad(b, 'U1', '24').GetPosition(); x, y = p.ToMM(c.x), p.ToMM(c.y); track(b, p.B_Cu, x - 6.0, y, x - 2.0, y, 'AD_DOUT_LOCAL')


def u1_gnd_thermal(b): pad(b, 'U1', '50').SetLocalZoneConnection(p.ZONE_CONNECTION_THERMAL)   # V1GND not solid on the inner pour
def foreign_in_u1(b): track(b, p.F_Cu, 56.0, 53.6, 58.6, 53.6, '5V_SYS')               # 5V_SYS across the inner GND pour of U1
def narrow_track(b):                                                                # longest signal track outside U1 / U3 thinned to 0.25 mm
    t = max((t for t in b.GetTracks() if not isinstance(t, p.PCB_VIA) and t.GetNetname() != 'GND' and p.ToMM(t.GetWidth()) >= .3), key=lambda t: t.GetLength())
    t.SetWidth(mm(.25))


def bottom_soic(b):                                                                 # U9 (SOIC-14) flipped to the bottom
    f = fp(b, 'U9')
    try:
        f.Flip(f.GetPosition(), p.FLIP_DIRECTION_LEFT_RIGHT)
    except (AttributeError, TypeError):
        f.Flip(f.GetPosition(), True)


def sw1_inside(b): move(b, 'SW1', 6.0, 0)                                           # SW1 bushing no longer through the panel at x = 0
def taps_turned(b): fp(b, 'J4').SetOrientationDegrees(270)                          # TAPS anchors away from x = 0
def decap_far(b): away_net(b, 'C20', 'U9', '14')                                    # 100 nF 10 mm further from U9.14
def driver_far(b): away_net(b, 'R26', 'U11', '3')                                   # DOUT series resistor away from U11.3
def diode_far(b): move(b, 'D1', 0, -8)                                              # flyback diode 8 mm away from K1 pin 8
def filter_far(b): move(b, 'C29', -9.0, 0)                                          # CH3 filter 9 mm further from U1.53
def zone_copper(b): track(b, p.B_Cu, 6.0, 13.0, 6.0, 15.0, 'GND')                    # GND track 2 mm from the centre of H1 (D7 zone)


def ref_on_part(b):                                                                 # a visible reference inside U5's courtyard
    f = fp(b, 'R12'); c = fp(b, 'U5'); f.Reference().SetVisible(True)
    bb = c.GetBoundingBox(); f.Reference().SetPosition(bb.GetCenter())


def ref_far(b):                                                                     # R1's reference printed on R12
    f = fp(b, 'R1'); f.Reference().SetVisible(True); f.Reference().SetPosition(fp(b, 'R12').GetPosition())


def strip_part(b): fp(b, 'C25').SetPosition(xy(12.0, 5.0))                           # C25 in the reserved strip of edge A
def silk_small(b):                                                                  # review 2.10 MINOR-5: edge marker B back to 0.8 / 0.12 mm
    t = next(t for t in b.GetDrawings() if isinstance(t, p.PCB_TEXT) and t.GetText().startswith('KRAWEDZ B'))
    t.SetTextSize(p.VECTOR2I(mm(.7), mm(.8))); t.SetTextThickness(mm(.12))


def bar_back(b): track(b, p.B_Cu, 50.6, 47.0, 62.9, 47.0, '5V_SYS', .5)              # review 2.10 MAJOR-1: a B.Cu bar between the top caps and U1 again
def fan_track(b): track(b, p.B_Cu, 46.0, 55.0, 51.0, 55.0, '5V_SYS')                 # review 2.10 MAJOR-2: a B.Cu track under the input fan


def vbat_near(b):                                                                   # review 2.10 MINOR-2: TAP_P6 0.3 mm beside the longest VBAT track
    t = max((t for t in b.GetTracks() if not isinstance(t, p.PCB_VIA) and t.GetNetname().split('/')[-1] == 'VBAT_SENSE'), key=lambda t: t.GetLength())
    a, c = t.GetStart(), t.GetEnd(); dx, dy = p.ToMM(c.x - a.x), p.ToMM(c.y - a.y); k = math.hypot(dx, dy); nx, ny = -dy / k * .6, dx / k * .6
    n = next(q.GetNetname() for q in b.GetNetsByNetcode().values() if q.GetNetname().split('/')[-1] == 'TAP_P6')
    track(b, t.GetLayer(), p.ToMM(a.x) + nx + dx * .3, p.ToMM(a.y) + ny + dy * .3, p.ToMM(a.x) + nx + dx * .7, p.ToMM(a.y) + ny + dy * .7, n)


def null_control(b): pass


CASES = [(null_control, None), (mount_shift, 'M3 holes'), (jbp_shift, 'J_BP1 / J_BP2'), (sv_no_gnd_end, 'Service headers'),
         (sv_pin_without_resistor, 'Service headers'), (sv_resistor_far, 'Service headers'), ('label_missing', 'Service headers'),
         ('label_swap', 'Service headers'), ('too_tall', 'Every part <='), (refcap_far, 'U1 decoupling'), (regcap_far, 'U1 decoupling'),
         (refcap_via, 'REGCAP_A, REGCAP_D and REFCAP'), (dout_under, 'DOUT'), (u1_gnd_thermal, 'U1 ground'), (foreign_in_u1, 'No copper of other nets in the U1'), ('fine_rule_everywhere', 'Rules as P02'),
         (narrow_track, 'Every track >='), (bottom_soic, 'S1-2 section 4'), (sw1_inside, 'Panel side'), (taps_turned, 'Panel side'),
         (decap_far, 'Decoupling at the IC pins'), (driver_far, 'Series resistors at the driver'), (diode_far, 'Series resistors at the driver'),
         (filter_far, 'Input filters'), ('gnd_pour_removed', 'GND pours'), (ref_on_part, 'Every visible reference'),
         (ref_far, 'Every visible reference nearer'), (strip_part, 'Reserved strip of edge A'), ('mark_missing', 'Pin 1 marks'),
         (zone_copper, 'Standoff zones D7'), ('title_wrong', 'Silkscreen: board name'),
         (silk_small, 'Silkscreen legible'), (bar_back, 'U1 decoupling, ground side'), (fan_track, 'B.Cu under the input fan'),
         (vbat_near, 'VBAT_SENSE copper')]
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
        env['EGRLAB_HEIGHT_OVERRIDE'] = 'C1=17.0'
    b.BuildConnectivity(); p.ZONE_FILLER(b).Fill(b.Zones())
    copy = d / f'{NAME}.kicad_pcb'; p.SaveBoard(str(copy), b)
    if name == 'label_missing':                                            # silk label of J_SV1 pin 2 deleted at file level
        t = parse(copy.read_text(encoding='utf-8')); lab = labels['J_SV1.2']; n0 = len(t)
        t = [g for g in t if not (isinstance(g, list) and g and g[0] == 'gr_text' and g[1] == lab)]
        assert len(t) < n0, lab
        copy.write_text(dump(t) + '\n', encoding='utf-8')
    if name == 'gnd_pour_removed':                                         # the B.Cu GND pour deleted at file level (1.10: b.Remove() broke
        t = parse(copy.read_text(encoding='utf-8')); n0 = len(t)              # SWIG in P09, the next LoadBoard returned a bare SwigPyObject)
        def gnd_b(g):
            return (isinstance(g, list) and g and g[0] == 'zone' and any(isinstance(x, list) and x[:2] == ['net', 'GND'] for x in g)
                    and any(isinstance(x, list) and x and x[0] == 'layer' and x[1] == 'B.Cu' for x in g))
        t = [g for g in t if not gnd_b(g)]
        assert len(t) == n0 - 1, n0 - len(t)
        copy.write_text(dump(t) + '\n', encoding='utf-8')
    if name == 'label_swap':                                               # labels of J_SV2 pins 2 and 3 (ADC_CS / ADC_CONVST) swapped
        t = parse(copy.read_text(encoding='utf-8')); l7, l8 = labels['J_SV2.2'], labels['J_SV2.3']; k = 0
        for g in t:
            if isinstance(g, list) and g and g[0] == 'gr_text' and g[1] in (l7, l8):
                g[1] = l8 if g[1] == l7 else l7; k += 1
        assert k == 2, k
        copy.write_text(dump(t) + '\n', encoding='utf-8')
    if name == 'mark_missing':                                             # pin-1 mark "1" of the TAPS tail J4 deleted
        t = parse(copy.read_text(encoding='utf-8')); n0 = len(t); q1 = pad(b, 'J4', '1').GetPosition(); j1 = (p.ToMM(q1.x), p.ToMM(q1.y))
        def at_j4(g):
            at = next((x for x in g if isinstance(x, list) and x and x[0] == 'at'), None)
            return at and math.dist((float(at[1]), float(at[2])), j1) <= 3.0
        t = [g for g in t if not (isinstance(g, list) and g and g[0] == 'gr_text' and g[1] == '1' and at_j4(g))]
        assert len(t) == n0 - 1, n0 - len(t)
        copy.write_text(dump(t) + '\n', encoding='utf-8')
    if name == 'title_wrong':                                              # board name without the slot (as R2 up to 30.09)
        t = parse(copy.read_text(encoding='utf-8')); k = 0
        for g in t:
            if isinstance(g, list) and g and g[0] == 'gr_text' and g[1] == TYTUL:
                g[1] = TYTUL.rsplit(' ', 1)[0]; k += 1
        assert k == 1, k
        copy.write_text(dump(t) + '\n', encoding='utf-8')
    for f in (P / 'eda').glob('*.kicad_sch'):
        shutil.copy2(f, d / f.name)
    shutil.copy2(P / f'eda/{NAME}.kicad_pro', d / f'{NAME}.kicad_pro')
    dru = (P / f'eda/{NAME}.kicad_dru').read_text(encoding='utf-8')   # P05: fine-pitch custom rules travel with every copy
    if name == 'fine_rule_everywhere':                                     # the 0.15 mm clearance rule widened to the whole board
        dru = dru.replace(dru[dru.index('(rule "drobny raster'):], dru[dru.index('(rule "drobny raster'):].replace(
            dru[dru.index('(rule "drobny raster'):].split('(condition "')[2].split('")')[0], "A.Type != 'Zone'", 1))
    (d / f'{NAME}.kicad_dru').write_text(dru, encoding='utf-8')
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
