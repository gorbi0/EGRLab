"""Negative controls: working copies of the finished P08 R2 board with one deliberate defect each (plus a null control: an unchanged
copy). verify_pcb.py must fail the named check on every defective copy and pass everything on the null control.
eda/P08.kicad_pcb is never modified; copies and their reports stay in verification/negative-controls/ (not production files).
Each copy gets the project, the schematic sheets and absolute library tables, so DRC and parity run as on the release board.
(Pattern of P03 R6 / P09 R2 / P10 R2 negative_controls.py; defects chosen for the P08 checks.)
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
def jbp_shift(b): move(b, 'J1', 1.0, 0)                                             # edge-A connector off x = 26.5
def sv_no_gnd_end(b): pad(b, 'J2', '13').SetNet(pad(b, 'J2', '12').GetNet())        # last pin not GND
def sv_pin_without_resistor(b): pad(b, 'J2', '2').SetNet(pad(b, 'U1', '1').GetNet())   # 5V_SYS straight to the pin
def sv_resistor_far(b): away_net(b, 'R21', 'U6', '1', 12)                           # SUP3_N service resistor 12 mm away from its node
def decap_far(b): away_net(b, 'C4', 'U4', '14')                                     # 100 nF 10 mm further from U4.14 (VCC)
def driver_far(b): away_net(b, 'R11', 'U4', '6')                                    # 100R series resistor away from its driver U4.6
def j4_turned(b): fp(b, 'J4').SetOrientationDegrees(270)                            # TSENSOR wire field turned: anchor away from the panel


def anchor_track(b):                                                                # GND track across the keepout of anchor hole 1
    h = sorted((a for a in fp(b, 'J4').Pads() if a.GetAttribute() == p.PAD_ATTRIB_NPTH), key=lambda a: a.GetPosition().y)[0].GetPosition()
    x, y = p.ToMM(h.x), p.ToMM(h.y); track(b, p.B_Cu, x + 2.5, y - 2, x + 2.5, y + 2, 'GND')


def k1_thermal(b): pad(b, 'K1', '6').SetLocalZoneConnection(p.ZONE_CONNECTION_THERMAL)   # return contact on thermal spokes


def sensor_cut(b):                                                                  # the locked 5V_SENSOR line K1.4 -> J4.1 interrupted
    t = max((t for t in b.GetTracks() if not isinstance(t, p.PCB_VIA) and t.GetNetname() == '5V_SENSOR' and t.IsLocked()), key=lambda t: t.GetLength())
    t.SetEnd(t.GetStart())


def sensor_narrow(b):                                                               # one AGND_SENSOR track 0.4 mm
    t = next(t for t in b.GetTracks() if not isinstance(t, p.PCB_VIA) and t.GetNetname() == 'AGND_SENSOR'); t.SetWidth(mm(.4))


def supply_narrow(b):                                                               # the longest 5V_SYS track 0.4 mm
    t = max((t for t in b.GetTracks() if not isinstance(t, p.PCB_VIA) and t.GetNetname() == '5V_SYS'), key=lambda t: t.GetLength()); t.SetWidth(mm(.4))


def narrow_track(b):                                                                # longest signal track thinned to 0.25 mm
    t = max((t for t in b.GetTracks() if not isinstance(t, p.PCB_VIA) and t.GetNetname() not in ('GND', '5V_SYS')), key=lambda t: t.GetLength())
    t.SetWidth(mm(.25))


def bottom_soic(b):                                                                 # U4 (SOIC-14) flipped to the bottom: not allowed on level 5
    f = fp(b, 'U4')
    try:
        f.Flip(f.GetPosition(), p.FLIP_DIRECTION_LEFT_RIGHT)
    except (AttributeError, TypeError):
        f.Flip(f.GetPosition(), True)


def zone_copper(b): track(b, p.B_Cu, 6.0, 13.0, 6.0, 15.0, 'GND')                    # GND track 2 mm from the centre of H1 (D7 zone)


def ref_on_part(b):                                                                 # a visible reference inside U3's courtyard
    f = fp(b, 'R8'); c = fp(b, 'U3'); f.Reference().SetVisible(True)
    bb = c.GetBoundingBox(); f.Reference().SetPosition(bb.GetCenter())


def ref_far(b):                                                                     # R1's reference printed on R5
    f = fp(b, 'R1'); f.Reference().SetVisible(True); f.Reference().SetPosition(fp(b, 'R5').GetPosition())


def small_text(b):                                                                  # a reference shrunk to 0.8 / 0.12 mm (below the fab minimum)
    t = fp(b, 'U3').Reference(); t.SetTextSize(xy(.8, .8)); t.SetTextThickness(mm(.12))


def strip_part(b): fp(b, 'C4').SetPosition(xy(12.0, 5.0))                            # C4 in the reserved strip of edge A


def null_control(b): pass


CASES = [(null_control, None), (mount_shift, 'M3 holes'), (jbp_shift, 'J1 = J_BP'), (sv_no_gnd_end, 'Service header J2'),
         (sv_pin_without_resistor, 'Service header J2'), (sv_resistor_far, 'Service header J2'), ('label_missing', 'Service header J2'),
         ('too_tall', 'Every part <='), (j4_turned, 'J4 (TSENSOR'), (anchor_track, 'J4 (TSENSOR'), (k1_thermal, 'Sensor path through K1'),
         (sensor_cut, 'Sensor path through K1'), (sensor_narrow, 'Track widths of the supply'), (supply_narrow, 'Track widths of the supply'),
         (decap_far, 'Decoupling at the pins'), (driver_far, 'Series resistor at its driver'), (narrow_track, 'Every track >='),
         (bottom_soic, 'S1-2 section 4'), ('gnd_pour_removed', 'GND pours'), (ref_on_part, 'Every visible reference'),
         (ref_far, 'Every visible reference nearer'), ('label_swap', 'Service header J2'), (strip_part, 'Reserved strip of edge A'),
         ('mark_missing', 'Pin 1 mark of the TSENSOR'), (small_text, 'Silkscreen legible'), (zone_copper, 'Standoff zones D7'),
         ('title_wrong', 'Silkscreen: board name')]
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
        env['EGRLAB_HEIGHT_OVERRIDE'] = 'K1=17.0'
    b.BuildConnectivity(); p.ZONE_FILLER(b).Fill(b.Zones())
    copy = d / f'{NAME}.kicad_pcb'; p.SaveBoard(str(copy), b)
    if name == 'label_missing':                                            # silk label of J2 pin 2 deleted at file level
        t = parse(copy.read_text(encoding='utf-8')); lab = labels['J2.2']; n0 = len(t)
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
    if name == 'label_swap':                                               # labels of J2 pins 7 and 8 (SENSOR_HEALTHY / PERMIT_LOCAL) swapped
        t = parse(copy.read_text(encoding='utf-8')); l7, l8 = labels['J2.7'], labels['J2.8']; k = 0
        for g in t:
            if isinstance(g, list) and g and g[0] == 'gr_text' and g[1] in (l7, l8):
                g[1] = l8 if g[1] == l7 else l7; k += 1
        assert k == 2, k
        copy.write_text(dump(t) + '\n', encoding='utf-8')
    if name == 'mark_missing':                                             # pin 1 mark "1" at J4.1 deleted (not the marks of J1 / J2)
        t = parse(copy.read_text(encoding='utf-8')); n0 = len(t); q = pad(b, 'J4', '1').GetPosition(); qx, qy = p.ToMM(q.x), p.ToMM(q.y)
        def j4mark(g):
            at = next((x for x in g if isinstance(x, list) and x and x[0] == 'at'), None)
            return g[1] == '1' and at is not None and math.dist((float(at[1]), float(at[2])), (qx, qy)) <= 3.0
        t = [g for g in t if not (isinstance(g, list) and g and g[0] == 'gr_text' and j4mark(g))]
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
