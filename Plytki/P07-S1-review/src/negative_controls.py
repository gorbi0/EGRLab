"""Negative controls: working copies of the finished P07 S1 board with one deliberate defect each (plus a null control: an unchanged
copy). verify_pcb.py must fail the named check on every defective copy and pass everything on the null control.
eda/P07.kicad_pcb is never modified; copies and their reports stay in verification/negative-controls/ (not production files).
Each copy gets the project, the schematic sheets and absolute library tables, so DRC and parity run as on the release board.
(Pattern of P06 R2 / P05 R3 negative_controls.py; defects chosen for the P07 checks: force pours of the 10 A path and PGND, shunt, Kelvin
pair, tails J1-J4 at x = 0, ground separation, decoupling, silkscreen size, decoupling return.)
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


def pxy(b, r, n):
    c = pad(b, r, n).GetPosition(); return p.ToMM(c.x), p.ToMM(c.y)


def move(b, r, dx, dy):
    f = fp(b, r); f.SetPosition(xy(p.ToMM(f.GetPosition().x) + dx, p.ToMM(f.GetPosition().y) + dy))


def away(b, r, n, ur, un, d=10):
    """Move part r by d mm along the line from pin ur.un to its pad n (further from that pin)."""
    u, c = pad(b, ur, un).GetPosition(), pad(b, r, n).GetPosition()
    dx, dy = p.ToMM(c.x - u.x), p.ToMM(c.y - u.y); k = math.hypot(dx, dy) or 1
    move(b, r, d * dx / k, d * dy / k)


def away_net(b, r, ur, un, d=10):
    n = pad(b, ur, un).GetNetname(); away(b, r, next(a for a in fp(b, r).Pads() if a.GetNetname() == n).GetNumber(), ur, un, d)


def track(b, layer, x0, y0, x1, y1, netname, w=.3):
    t = p.PCB_TRACK(b); t.SetLayer(layer); t.SetWidth(mm(w)); t.SetStart(xy(x0, y0)); t.SetEnd(xy(x1, y1)); t.SetNet(b.FindNet(netname)); b.Add(t)


def via(b, x, y, netname):
    v = p.PCB_VIA(b); v.SetPosition(xy(x, y)); v.SetWidth(mm(.9)); v.SetDrill(mm(.4)); v.SetNet(b.FindNet(netname)); b.Add(v)


def netname(b, short):
    return next(n.GetNetname() for n in b.GetNetsByNetcode().values() if n.GetNetname().split('/')[-1] == short)


def flip(f):
    try:
        f.Flip(f.GetPosition(), p.FLIP_DIRECTION_LEFT_RIGHT)
    except (AttributeError, TypeError):
        f.Flip(f.GetPosition(), True)


def mount_shift(b): move(b, 'H1', .5, 0)                                            # hole 0.5 mm off the S1 grid
def jbp_shift(b): move(b, 'J_BP2', 1.0, 0)                                          # edge-A connector off x = 80.0
def sv_no_gnd_end(b): pad(b, 'J_SV2', '12').SetNet(pad(b, 'J_SV2', '11').GetNet())  # last pin not GND
def srv_r(b, node):                                                                 # service resistor of a node (names follow parts.py)
    return next(f.GetReference() for f in b.GetFootprints() if f.GetReference().startswith('R') and {a.GetNetname().split('/')[-1] for a in f.Pads()} == {node, 'SRV_' + node})


def sv_pin_without_resistor(b): pad(b, 'J_SV2', '2').SetNet(pad(b, srv_r(b, '5V_SYS'), '1').GetNet())   # 5V_SYS straight to the pin
def sv_resistor_far(b): fp(b, srv_r(b, 'OC_GOOD')).SetPosition(xy(45.0, 90.0))    # OC_GOOD service resistor > 10 mm from every node pad
def narrow_track(b):                                                                # longest signal track thinned to 0.25 mm
    t = max((t for t in b.GetTracks() if not isinstance(t, p.PCB_VIA) and t.GetNetname() != 'GND' and p.ToMM(t.GetWidth()) >= .3), key=lambda t: t.GetLength())
    t.SetWidth(mm(.25))


def pwr_thin(b):                                                                    # a 3V3_IO track at 0.3 mm (class PWR wants 0.4)
    t = max((t for t in b.GetTracks() if not isinstance(t, p.PCB_VIA) and t.GetNetname() == '3V3_IO'), key=lambda t: t.GetLength())
    t.SetWidth(mm(.3))


def bottom_soic(b): flip(fp(b, 'U12'))                                              # U12 (SOIC-14) flipped to the bottom
def force_thermal(b): pad(b, 'RSH1', '1').SetLocalZoneConnection(p.ZONE_CONNECTION_THERMAL)   # shunt force pad on thermal spokes


def force_narrow(b):                                                                # PGND strip between the anchors and the pads cut to ~2 mm
    z = p.ZONE(b); z.SetIsRuleArea(True); ls = p.LSET(); ls.AddLayer(p.F_Cu); ls.AddLayer(p.B_Cu); z.SetLayerSet(ls)
    z.SetDoNotAllowTracks(False); z.SetDoNotAllowVias(False); z.SetDoNotAllowZoneFills(True); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
    o = z.Outline(); o.NewOutline()
    for x, y in [(10.0, 33.0), (15.3, 33.0), (15.3, 35.4), (10.0, 35.4)]:
        o.Append(mm(x), mm(y))
    b.Add(z)


def via_in_shunt_pad(b): via(b, *pxy(b, 'RSH1', '1'), netname(b, 'MOD_MP'))        # stitching via in the MOD_MP force pad of RSH1


def under_shunt(b):                                                                 # a GND track on B.Cu under the shunt
    x, y = fp(b, 'RSH1').GetPosition().x, fp(b, 'RSH1').GetPosition().y; x, y = p.ToMM(x), p.ToMM(y); track(b, p.B_Cu, x - 1.0, y - 2.0, x - 1.0, y + 2.0, 'GND')


def kelvin_via(b):                                                                  # K_MINUS takes a via (and 1.6 mm of B.Cu) on its way to R7
    x0, y0 = pxy(b, 'RSH1', '3'); x1, _ = pxy(b, 'R7', '1'); xm = (x0 + x1) / 2; n = netname(b, 'K_MINUS')
    via(b, xm, y0, n); via(b, xm + 1.6, y0, n); track(b, p.B_Cu, xm, y0, xm + 1.6, y0, n)


def foreign_in_kelvin(b):                                                           # CLK_LOCAL run between the Kelvin lines
    (x0, y0), (x1, y1) = pxy(b, 'RSH1', '3'), pxy(b, 'R6', '1'); ym = (y0 + y1) / 2; track(b, p.F_Cu, x0 + 1.5, ym, x1 - 1.0, ym, netname(b, 'CLK_LOCAL'))


def anchor_track(b):                                                                # GND track 2 mm from a J4 anchor centre
    a = min((q for q in fp(b, 'J4').Pads() if q.GetAttribute() == p.PAD_ATTRIB_NPTH), key=lambda q: q.GetPosition().y)
    x, y = p.ToMM(a.GetPosition().x), p.ToMM(a.GetPosition().y); track(b, p.F_Cu, x + 2.0, y - 1.0, x + 2.0, y + 1.0, 'GND')


def part_on_cable(b): fp(b, 'C17').SetPosition(xy(5.0, 64.0))                      # C17 (top) on the J3 cable (between the wall and the pads)
def tail_turned(b): fp(b, 'J4').SetOrientationDegrees(270)                          # J4 anchors away from x = 0
def column_swap(b):                                                                 # J2 pads swapped: PGND no longer next to the PGND strip
    a1, a2 = pad(b, 'J2', '1'), pad(b, 'J2', '2'); n1, n2 = a1.GetNet(), a2.GetNet(); a1.SetNet(n2); a2.SetNet(n1)


def analog_near_power(b): fp(b, 'U4').SetPosition(xy(44.0, 53.5))                  # U4 (OC reference) 1 mm from the PGND / VMOTOR pours
def c5_far(b): away_net(b, 'C5', 'U2', '2', 5)                                      # MCP1525 load capacitor 5 mm further
def decap_far(b): away_net(b, 'C30', 'U10', '14')                                   # 100 nF 10 mm further from U10.14
def zone_copper(b): track(b, p.B_Cu, 6.0, 13.0, 6.0, 15.0, 'GND')                    # GND track 2 mm from the centre of H1 (D7 zone)


def ref_on_part(b):                                                                 # a visible reference inside U7's courtyard
    f = fp(b, 'R12'); c = fp(b, 'U7'); f.Reference().SetVisible(True); f.Reference().SetPosition(c.GetBoundingBox().GetCenter())


def ref_far(b):                                                                     # R6's reference printed on R7
    f = fp(b, 'R6'); f.Reference().SetVisible(True); f.Reference().SetPosition(fp(b, 'R7').GetPosition())


def strip_part(b): fp(b, 'C28').SetPosition(xy(66.0, 5.0))                          # C28 in the reserved strip of edge A (J_BP2)


def silk_small(b):                                                                  # the J2.1 "B+" mark at 0.8 / 0.12 mm
    q = pad(b, 'J2', '1').GetPosition(); j = (p.ToMM(q.x), p.ToMM(q.y))
    t = next(t for t in b.GetDrawings() if isinstance(t, p.PCB_TEXT) and t.GetText() == 'B+' and math.dist((p.ToMM(t.GetPosition().x), p.ToMM(t.GetPosition().y)), j) < 6)
    t.SetTextSize(p.VECTOR2I(mm(.7), mm(.8))); t.SetTextThickness(mm(.12))


def return_cut(b):                                                                  # no GND fill round the GND pad of C30 (decoupling of U10)
    a = pad(b, 'C30', '2'); x, y = pxy(b, 'C30', '2')
    z = p.ZONE(b); z.SetIsRuleArea(True); ls = p.LSET(); ls.AddLayer(p.F_Cu); ls.AddLayer(p.B_Cu); z.SetLayerSet(ls)
    z.SetDoNotAllowTracks(False); z.SetDoNotAllowVias(False); z.SetDoNotAllowZoneFills(True); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
    o = z.Outline(); o.NewOutline()
    for dx, dy in [(-4, -4), (4, -4), (4, 4), (-4, 4)]:
        o.Append(mm(x + dx), mm(y + dy))
    b.Add(z)
    for t in list(b.GetTracks()):   # and the GND tracks / vias of that pad's neighbourhood
        c = t.GetPosition() if isinstance(t, p.PCB_VIA) else t.GetStart()
        if t.GetNetname() == 'GND' and math.dist((p.ToMM(c.x), p.ToMM(c.y)), (x, y)) < 4:
            b.Remove(t)


def signal_on_in1(b):                                                              # 6.10: a CLK_LOCAL track on the In1 GND plane under U6
    c = fp(b, 'U6').GetBoundingBox().GetCenter(); x, y = p.ToMM(c.x), p.ToMM(c.y); track(b, p.In1_Cu, x - 3, y, x + 3, y, netname(b, 'CLK_LOCAL'))


def null_control(b): pass


CASES = [(null_control, None), (mount_shift, 'M3 holes'), (jbp_shift, 'J_BP (edge A)'), (sv_no_gnd_end, 'Service header'),
         (sv_pin_without_resistor, 'Service header'), (sv_resistor_far, 'Service header'), ('label_missing', 'Service header'),
         ('label_swap', 'Service header'), ('too_tall', 'Every part <='), (narrow_track, 'Every track >='), (pwr_thin, 'Every track >='),
         (bottom_soic, 'S1-2 section 4'), ('dru_present', 'Rules as P02'), ('force_pour_missing', 'Force pours VMOTOR'),
         (force_thermal, 'Force pours VMOTOR'), (force_narrow, 'Force path >= 4 mm'), (via_in_shunt_pad, 'Force pours stitched'),
         (under_shunt, 'Nothing under the shunt'), (kelvin_via, 'Kelvin pair'), (foreign_in_kelvin, 'No track or via of another net'),
         (anchor_track, 'Panel side'), (part_on_cable, 'Panel side'), (tail_turned, 'Panel side'), (column_swap, 'Panel side'),
         (analog_near_power, 'Ground separation'), (c5_far, 'Decoupling at the pins'), (decap_far, 'Decoupling at the pins'), ('gnd_pour_removed', 'GND pours'),
         (ref_on_part, 'Every visible reference outside'), (ref_far, 'Every visible reference nearer'), (strip_part, 'Reserved strip of edge A'),
         ('mark_missing', 'Net marks of the tails'), (zone_copper, 'Standoff zones D7'), ('title_wrong', 'Silkscreen: board name'),
         (silk_small, 'Silkscreen legible'), (return_cut, 'Decoupling return'),
         ('stack_inner_1oz', 'Stack JLC04161H-7628'), ('in1_gnd_removed', 'In1.Cu GND plane'), ('pgnd_in1_to_gnd', 'Ground separation'),
         (signal_on_in1, 'In1.Cu GND plane'), ('in2_zone_missing', 'In2.Cu supply zones')]
assert root.resolve().is_relative_to(P.resolve()) and root.name == 'negative-controls'
shutil.rmtree(root, ignore_errors=True); root.mkdir(parents=True)
labels = json.loads((P / 'routing/silkscreen.json').read_text(encoding='utf-8'))['service_labels']


def drop(copy, pred, n_expected=1):
    t = parse(copy.read_text(encoding='utf-8')); n0 = len(t); t = [g for g in t if not pred(g)]
    assert n0 - len(t) == n_expected, n0 - len(t)
    copy.write_text(dump(t) + '\n', encoding='utf-8')


def zone_of(g, netshort, layer):
    return (isinstance(g, list) and g and g[0] == 'zone' and any(isinstance(x, list) and x[:1] == ['net'] and str(x[1]).split('/')[-1] == netshort for x in g)
            and any(isinstance(x, list) and x and x[0] == 'layer' and x[1] == layer for x in g))


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
    if name == 'label_missing':                                            # silk label of J_SV2 pin 2 deleted at file level
        lab = labels['J_SV2.2']; drop(copy, lambda g: isinstance(g, list) and g and g[0] == 'gr_text' and g[1] == lab)
    if name == 'gnd_pour_removed':                                         # the B.Cu GND pour deleted at file level (b.Remove() breaks SWIG)
        drop(copy, lambda g: zone_of(g, 'GND', 'B.Cu'))
    if name == 'force_pour_missing':                                       # the B.Cu VMOTOR pour deleted at file level
        drop(copy, lambda g: zone_of(g, 'VMOTOR', 'B.Cu'))
    if name == 'label_swap':                                               # labels of J_SV2 pins 8 and 9 (OC_GOOD / DRIVE_OK) swapped
        t = parse(copy.read_text(encoding='utf-8')); l2, l3 = labels['J_SV2.8'], labels['J_SV2.9']; k = 0
        for g in t:
            if isinstance(g, list) and g and g[0] == 'gr_text' and g[1] in (l2, l3):
                g[1] = l3 if g[1] == l2 else l2; k += 1
        assert k == 2, k
        copy.write_text(dump(t) + '\n', encoding='utf-8')
    if name == 'mark_missing':                                             # "VM" mark of J1.1 deleted
        q1 = pad(b, 'J1', '1').GetPosition(); j1 = (p.ToMM(q1.x), p.ToMM(q1.y))
        def at_j3(g):
            at = next((x for x in g if isinstance(x, list) and x and x[0] == 'at'), None)
            return at and math.dist((float(at[1]), float(at[2])), j1) <= 6.0
        drop(copy, lambda g: isinstance(g, list) and g and g[0] == 'gr_text' and g[1] == 'VM' and at_j3(g))
    if name == 'stack_inner_1oz':                                          # 6.10: In1.Cu 35 um instead of 15.2 um in the stack
        txt = copy.read_text(encoding='utf-8'); k = txt.count('(layer "In1.Cu" (type "copper") (thickness 0.0152))')
        assert k == 1, k; copy.write_text(txt.replace('(layer "In1.Cu" (type "copper") (thickness 0.0152))', '(layer "In1.Cu" (type "copper") (thickness 0.035))'), encoding='utf-8')
    if name == 'in1_gnd_removed':                                          # the In1.Cu GND plane deleted at file level
        drop(copy, lambda g: zone_of(g, 'GND', 'In1.Cu'))
    if name == 'in2_zone_missing':                                         # the 3V3_IO supply zone on In2.Cu deleted
        drop(copy, lambda g: zone_of(g, '3V3_IO', 'In2.Cu'))
    if name == 'pgnd_in1_to_gnd':                                          # the PGND area of In1.Cu turned into GND (masses joined)
        t = parse(copy.read_text(encoding='utf-8')); k = 0
        for g in t:
            if zone_of(g, 'PGND', 'In1.Cu'):
                for x in g:
                    if isinstance(x, list) and x[:1] in (['net'], ['net_name']):
                        x[1] = 'GND'; k += x[0] == 'net'
        assert k == 1, k
        copy.write_text(dump(t) + '\n', encoding='utf-8')
    if name == 'title_wrong':                                              # board name without the slots (as R2 up to 30.09)
        t = parse(copy.read_text(encoding='utf-8')); k = 0
        for g in t:
            if isinstance(g, list) and g and g[0] == 'gr_text' and g[1] == TYTUL:
                g[1] = TYTUL.rsplit(' ', 1)[0]; k += 1
        assert k == 1, k
        copy.write_text(dump(t) + '\n', encoding='utf-8')
    for f in (P / 'eda').glob('*.kicad_sch'):
        shutil.copy2(f, d / f.name)
    shutil.copy2(P / f'eda/{NAME}.kicad_pro', d / f'{NAME}.kicad_pro')
    if name == 'dru_present':                                              # a custom rule file appears (P07 has none: S1 rules everywhere)
        (d / f'{NAME}.kicad_dru').write_text('(version 1)\n(rule "waska sciezka"\n  (condition "A.Type == \'Track\'")\n  (constraint track_width (min 0.15mm)))\n', encoding='utf-8')
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
