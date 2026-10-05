"""Negative controls: working copies of the finished P04 R3 board with one deliberate defect each (plus a null control: an unchanged
copy). verify_pcb.py must fail the named check on every defective copy and pass everything on the null control.
eda/P04.kicad_pcb is never modified; copies and their reports stay in verification/negative-controls/ (not production files).
Each copy gets the project, the schematic sheets and absolute library tables, so DRC and parity run as on the release board.
(Pattern of P05 R3 / P03 R6 negative_controls.py; defects chosen for the P04 checks.)
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


def netn(b, name):
    return next(q for q in b.GetNetsByNetcode().values() if q.GetNetname().split('/')[-1] == name)


def track(b, layer, x0, y0, x1, y1, netname, w=.3, locked=False):
    t = p.PCB_TRACK(b); t.SetLayer(layer); t.SetWidth(mm(w)); t.SetStart(xy(x0, y0)); t.SetEnd(xy(x1, y1)); t.SetNet(netn(b, netname)); t.SetLocked(locked); b.Add(t)


def from_pad(b, r, n, dx, dy, netname, layer=p.F_Cu, w=.3, locked=False):
    c = pad(b, r, n).GetPosition(); x, y = p.ToMM(c.x), p.ToMM(c.y); track(b, layer, x, y, x + dx, y + dy, netname, w, locked)


def mount_shift(b): move(b, 'H5', .5, 0)                                            # hole 0.5 mm off the S1 grid
def jbp_shift(b): move(b, 'J_BP3', 1.0, 0)                                          # edge-A connector off x = 133.5
def jbp_flip(b): fp(b, 'J_BP2').SetOrientationDegrees(270)                          # J_BP2 turned: pin 1 at the larger x
def sv_no_gnd_end(b): pad(b, 'J_SV1', '13').SetNet(pad(b, 'J_SV1', '12').GetNet())  # last pin not GND
def sv_pin_without_resistor(b): pad(b, 'J_SV3', '3').SetNet(pad(b, 'R58', '1').GetNet())   # 3V3_IO straight to the pin
def sv_resistor_far(b): away(b, 'R49', '1', 'U1', '13', 12)                         # WD_Q service resistor 12 mm away from its node
def too_tall(b): pass                                                               # EGRLAB_HEIGHT_OVERRIDE C1 = 17 mm
def bottom_soic(b):                                                                 # U9 (SOIC-14) flipped to the bottom
    f = fp(b, 'U9')
    try:
        f.Flip(f.GetPosition(), p.FLIP_DIRECTION_LEFT_RIGHT)
    except (AttributeError, TypeError):
        f.Flip(f.GetPosition(), True)


def narrow_track(b):                                                                # longest signal track thinned to 0.25 mm
    t = max((t for t in b.GetTracks() if not isinstance(t, p.PCB_VIA) and t.GetNetname() != 'GND' and abs(p.ToMM(t.GetWidth()) - .3) < 1e-6), key=lambda t: t.GetLength())
    t.SetWidth(mm(.25))


def narrow_supply(b):                                                               # one P04_3V3 track at 0.3 mm (signal width)
    t = max((t for t in b.GetTracks() if not isinstance(t, p.PCB_VIA) and t.GetNetname().split('/')[-1] == 'P04_3V3'), key=lambda t: t.GetLength())
    t.SetWidth(mm(.3))


def wd_via(b):                                                                      # a via (and its stub) on WD_C
    c = pad(b, 'C1', '2').GetPosition(); v = p.PCB_VIA(b); v.SetPosition(xy(p.ToMM(c.x) + 2.5, p.ToMM(c.y) + 2.5)); v.SetWidth(mm(.9)); v.SetDrill(mm(.4))
    v.SetNet(pad(b, 'C1', '2').GetNet()); b.Add(v); from_pad(b, 'C1', '2', 2.5, 2.5, 'WD_C', locked=True)


def wd_unlocked(b):                                                                 # watchdog track left to the router (unlocked)
    next(t for t in b.GetTracks() if t.GetNetname().split('/')[-1] == 'WD_RC').SetLocked(False)


def c1_grounded(b): pad(b, 'C1', '2').SetNet(netn(b, 'GND'))                        # timing capacitor to GND
def c18_far(b): away(b, 'C18', '1', 'U2', '11', 8)                                  # SAFE_N filter 8 mm further from U2.11
def ser_detour(b): from_pad(b, 'R41', '1', 0, 20, 'TEST_KEY', p.B_Cu)               # 20 mm detour on TEST_KEY (R41 away from J_BP1.14)
def ser_extra_pad(b): pad(b, 'R24', '1').SetNet(netn(b, 'MECH_OK'))                 # pull-down on the connector side of R42
def supn_long(b): from_pad(b, 'R17', '1', 0, 15, 'SUP_N_OUT', p.B_Cu)               # 15 mm extra copper on SUP_N_OUT
def supn_r17_far(b): away(b, 'R17', '1', 'U9', '5', 8)                              # R17 8 mm away from U9.5
def decap_far(b): away(b, 'C12', '1', 'U9', '14', 8)                                # U9 decoupling 8 mm further (links stay where they were)
def default_far(b): away(b, 'R18', '1', 'U9', '9', 10)                              # PSU_OK default resistor 10 mm away from U9.9
def zone_copper(b): track(b, p.B_Cu, 156.0, 85.0, 156.0, 87.0, 'GND')               # GND track 1 mm from the centre of H12 (D7 zone)


def ref_on_part(b):                                                                 # a visible reference inside U2's courtyard
    f = fp(b, 'R6'); c = fp(b, 'U2'); f.Reference().SetVisible(True)
    bb = c.GetBoundingBox(); f.Reference().SetPosition(bb.GetCenter())


def ref_far(b):                                                                     # R1's reference printed on R12
    f = fp(b, 'R1'); f.Reference().SetVisible(True); f.Reference().SetPosition(fp(b, 'R12').GetPosition())


def strip_part(b): fp(b, 'R26').SetPosition(xy(140.0, 5.0))                         # R26 in the reserved strip of edge A (J_BP3 slot)


def silk_small(b):                                                                  # edge marker B at 0.8 / 0.12 mm
    t = next(t for t in b.GetDrawings() if isinstance(t, p.PCB_TEXT) and t.GetText().startswith('KRAWEDZ B'))
    t.SetTextSize(p.VECTOR2I(mm(.7), mm(.8))); t.SetTextThickness(mm(.12))


def null_control(b): pass


CASES = [(null_control, None), (mount_shift, 'M3 holes'), (jbp_shift, 'J_BP1..3'), (jbp_flip, 'J_BP1..3'), (sv_no_gnd_end, 'Service headers'),
         (sv_pin_without_resistor, 'Service headers'), (sv_resistor_far, 'Service headers'), ('label_missing', 'Service headers'),
         ('label_swap', 'Service headers'), (too_tall, 'Every part <='), (bottom_soic, 'S1-2 section 4'), (narrow_track, 'Every track >='),
         (narrow_supply, 'Supply nets'), (wd_via, 'Watchdog RC'), (wd_unlocked, 'Watchdog RC'), (c1_grounded, 'C1 lands'),
         (c18_far, 'SAFE_N ends at U2.11'), (ser_detour, 'Series resistors at their connector'), (ser_extra_pad, 'Series resistors at their connector'),
         (supn_long, 'SUP_N_OUT short'), (supn_r17_far, 'SUP_N_OUT short'), ('supn_no_ref', 'SUP_N_OUT short'), (decap_far, 'Decoupling at the IC'),
         (default_far, 'Default-state resistors'), ('gnd_pour_removed', 'GND pours'), (zone_copper, 'Standoff zones D7'), (ref_on_part, 'Every visible reference'),
         (ref_far, 'Every visible reference nearer'), (strip_part, 'Reserved strip of edge A'), ('mark_missing', 'Pin 1 of every connector'),
         ('title_wrong', 'Silkscreen: board name'), (silk_small, 'Silkscreen legible'), ('rules_dru', 'Rules as P02')]
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
    if name == 'supn_no_ref':                                              # the B.Cu pour cut out under the U9 / J_BP3 end of SUP_N_OUT
        z = p.ZONE(b); z.SetIsRuleArea(True); ls = p.LSET(); ls.AddLayer(p.B_Cu); z.SetLayerSet(ls); z.SetDoNotAllowZoneFills(True)
        z.SetDoNotAllowTracks(False); z.SetDoNotAllowVias(False); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False); z.SetZoneName('NC_SUPN')
        q = pad(b, 'U9', '5').GetPosition(); x, y = p.ToMM(q.x), p.ToMM(q.y); o = z.Outline(); o.NewOutline()
        for u, v in [(x - 3, y - 4.5), (x + 3, y - 4.5), (x + 3, y + 1), (x - 3, y + 1)]:
            o.Append(mm(u), mm(v))
        b.Add(z)
    b.BuildConnectivity(); p.ZONE_FILLER(b).Fill(b.Zones())
    copy = d / f'{NAME}.kicad_pcb'; p.SaveBoard(str(copy), b)
    if name == 'label_missing':                                            # silk label of J_SV1 pin 2 deleted at file level
        t = parse(copy.read_text(encoding='utf-8')); lab = labels['J_SV1.2']; n0 = len(t)
        t = [g for g in t if not (isinstance(g, list) and g and g[0] == 'gr_text' and g[1] == lab)]
        assert len(t) < n0, lab
        copy.write_text(dump(t) + '\n', encoding='utf-8')
    if name == 'gnd_pour_removed':                                         # the B.Cu GND pour deleted at file level (b.Remove() breaks SWIG)
        t = parse(copy.read_text(encoding='utf-8')); n0 = len(t)
        def gnd_b(g):
            return (isinstance(g, list) and g and g[0] == 'zone' and any(isinstance(x, list) and x[:2] == ['net', 'GND'] for x in g)
                    and any(isinstance(x, list) and x and x[0] == 'layer' and x[1] == 'B.Cu' for x in g))
        t = [g for g in t if not gnd_b(g)]
        assert len(t) == n0 - 1, n0 - len(t)
        copy.write_text(dump(t) + '\n', encoding='utf-8')
    if name == 'label_swap':                                               # labels of J_SV2 pins 3 and 4 (INTERLOCK / MOTOR_PERMIT) swapped
        t = parse(copy.read_text(encoding='utf-8')); l7, l8 = labels['J_SV2.3'], labels['J_SV2.4']; k = 0
        for g in t:
            if isinstance(g, list) and g and g[0] == 'gr_text' and g[1] in (l7, l8):
                g[1] = l8 if g[1] == l7 else l7; k += 1
        assert k == 2, k
        copy.write_text(dump(t) + '\n', encoding='utf-8')
    if name == 'mark_missing':                                             # pin-1 mark "1" of J_BP2 deleted
        t = parse(copy.read_text(encoding='utf-8')); n0 = len(t); q1 = pad(b, 'J_BP2', '1').GetPosition(); j1 = (p.ToMM(q1.x), p.ToMM(q1.y))
        def at_j(g):
            at = next((x for x in g if isinstance(x, list) and x and x[0] == 'at'), None)
            return at and math.dist((float(at[1]), float(at[2])), j1) <= 3.0
        t = [g for g in t if not (isinstance(g, list) and g and g[0] == 'gr_text' and g[1] == '1' and at_j(g))]
        assert len(t) == n0 - 1, n0 - len(t)
        copy.write_text(dump(t) + '\n', encoding='utf-8')
    if name == 'title_wrong':                                              # board name without the slots
        t = parse(copy.read_text(encoding='utf-8')); k = 0
        for g in t:
            if isinstance(g, list) and g and g[0] == 'gr_text' and g[1] == TYTUL:
                g[1] = TYTUL.rsplit(' ', 1)[0]; k += 1
        assert k == 1, k
        copy.write_text(dump(t) + '\n', encoding='utf-8')
    for f in (P / 'eda').glob('*.kicad_sch'):
        shutil.copy2(f, d / f.name)
    shutil.copy2(P / f'eda/{NAME}.kicad_pro', d / f'{NAME}.kicad_pro')
    if name == 'rules_dru':                                                # a custom rules file relaxing the clearance next to the board
        (d / f'{NAME}.kicad_dru').write_text('(version 1)\n(rule "x" (condition "A.Type == \'Track\'") (constraint clearance (min 0.15mm)))\n', encoding='utf-8')
    for tbl in ('fp-lib-table', 'sym-lib-table'):
        (d / tbl).write_text((P / 'eda' / tbl).read_text().replace('${KIPRJMOD}', (P / 'eda').as_posix()))
    subprocess.run([sys.executable, str(P / 'src/verify_pcb.py'), str(copy), str(d)], capture_output=True, text=True, env=env)
    rep = json.loads((d / 'pcb-checks.json').read_text(encoding='utf-8'))
    failed = [c['check'] for c in rep['checks'] if not c['pass']]
    hit = (not failed) if expected is None else any(c.startswith(expected) for c in failed)
    results.append({'control': name, 'expected_failing_check': expected or 'none (all PASS)', 'detected': hit, 'failed_checks': failed})
    print('OK ' if hit else 'BAD', name, '->', len(failed), 'failing checks', failed if not hit else '', flush=True)
(P / 'verification/negative-controls.json').write_text(json.dumps(results, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(sum(r['detected'] for r in results), '/', len(results), 'negative controls (with the null control)')
sys.exit(0 if all(r['detected'] for r in results) else 1)
