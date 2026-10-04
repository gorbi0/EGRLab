"""Negative controls: working copies of the finished P11 R2 board with one deliberate defect each (plus a null control: an unchanged
copy). verify_pcb.py must fail the named check on every defective copy and pass everything on the null control.
eda/P11.kicad_pcb is never modified; copies and their reports stay in verification/negative-controls/ (not production files).
Each copy gets the project, the schematic sheets and absolute library tables, so DRC and parity run as on the release board.
(Pattern and helpers of P10 R2 negative_controls.py; one defect for every P11 check, 4.10.2026.)
"""
from pathlib import Path
import pcbnew as p, json, subprocess, sys, shutil, os, math
from sexpr import parse, dump, Atom
sys.path.insert(0, str(Path(__file__).resolve().parent))
from board import NAME, REV
TYTUL = f'{REV} PANEL'   # as verify_pcb.py
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


def track(b, layer, x0, y0, x1, y1, netname, w=.3):
    t = p.PCB_TRACK(b); t.SetLayer(layer); t.SetWidth(mm(w)); t.SetStart(xy(x0, y0)); t.SetEnd(xy(x1, y1)); t.SetNet(b.FindNet(netname)); b.Add(t)


def anchors(b, r):
    return sorted((a.GetPosition() for a in fp(b, r).Pads() if a.GetAttribute() == p.PAD_ATTRIB_NPTH), key=lambda v: v.y)


def mount_shift(b): move(b, 'H3', .5, 0)                                             # hole 0.5 mm off its corner position
def zone_copper(b): track(b, p.B_Cu, 30.0, 94.0, 30.0, 96.0, 'GND')                  # GND track 2 mm from the centre of H4 (D7 zone)
def jp12_off_edge(b): move(b, 'J_P12', 0, 2.0)                                       # header 2 mm back from the wall-A edge


def jp12_pinout(b):                                                                  # pins 2 / 20 (PANEL_3V3 / 3V3_IO) swapped
    a, c = pad(b, 'J_P12', '2'), pad(b, 'J_P12', '20'); n = a.GetNet(); a.SetNet(c.GetNet()); c.SetNet(n)


def narrow_track(b):                                                                 # longest plain signal track thinned to 0.25 mm
    t = max((t for t in b.GetTracks() if not isinstance(t, p.PCB_VIA) and t.GetNetname().split('/')[-1] not in ('GND', 'PANEL_3V3', '3V3_IO')),
            key=lambda t: t.GetLength())
    t.SetWidth(mm(.25))


def supply_03(b):                                                                    # a PANEL_3V3 track at 0.3 mm (legal for DRC, not for the user rule)
    t = max((t for t in b.GetTracks() if not isinstance(t, p.PCB_VIA) and t.GetNetname() == 'PANEL_3V3'), key=lambda t: t.GetLength())
    t.SetWidth(mm(.3))


def field_turned(b): fp(b, 'J8').SetOrientationDegrees(270)                           # J8 turned: anchors away from the panel edge
def field_drill(b): [a.SetDrillSize(xy(.8, .8)) for a in fp(b, 'J6').Pads() if a.GetNumber()]   # J6 holes 0.8 mm (AWG24 does not fit)


def anchor_track(b):                                                                 # GND track across the keepout of a J11 anchor
    h = anchors(b, 'J11')[0]; x, y = p.ToMM(h.x), p.ToMM(h.y); track(b, p.B_Cu, x - 2, y + 2.4, x + 2, y + 2.4, 'GND')


def strip_blocked(b):                                                                # R1 put under the wires of J6 (between pads and edge)
    f = fp(b, 'R1'); f.SetOrientationDegrees(90); f.SetPosition(xy(9.5, 85.0))


def bottom_part(b):                                                                  # R1 flipped to the bottom
    f = fp(b, 'R1')
    try:
        f.Flip(f.GetPosition(), p.FLIP_DIRECTION_LEFT_RIGHT)
    except (AttributeError, TypeError):
        f.Flip(f.GetPosition(), True)


def ref_on_part(b):                                                                  # J8 reference printed inside the J11 courtyard
    fp(b, 'J8').Reference().SetPosition(xy(10.0, 45.0))


def ref_far(b):                                                                      # R1 reference 9 mm away from R1
    fp(b, 'R1').Reference().SetPosition(xy(14.0, 21.0))


def drc_short(b):                                                                    # LOOP_OUT track from J8.1 onto J8.2 (MECH_OK): short
    a, c = pad(b, 'J8', '1'), pad(b, 'J8', '2'); t = p.PCB_TRACK(b); t.SetLayer(p.F_Cu); t.SetWidth(mm(.3)); t.SetStart(a.GetPosition())
    t.SetEnd(c.GetPosition()); t.SetNet(a.GetNet()); b.Add(t)


def ref_renamed(b): fp(b, 'R1').SetReference('R2')                                   # part not in the schematic (R2) instead of R1
def value_changed(b): fp(b, 'R1').SetValue('1K')                                     # value differs from the netlist


def small_ring(b):                                                                   # one stitching via 0.8 / 0.4 (ring 0.2 mm)
    v = next(t for t in b.GetTracks() if isinstance(t, p.PCB_VIA) and t.GetNetname() == 'GND'); v.SetWidth(mm(.8))


def null_control(b): pass


def drop_text(t, text):
    n0 = len(t); t2 = [g for g in t if not (isinstance(g, list) and g and g[0] == 'gr_text' and g[1] == text)]
    assert len(t2) == n0 - 1, (text, n0 - len(t2)); return t2


def swap_text(t, a, c):
    k = 0
    for g in t:
        if isinstance(g, list) and g and g[0] == 'gr_text' and g[1] in (a, c):
            g[1] = c if g[1] == a else a; k += 1
    assert k == 2, (a, c, k); return t


def text_size(t, text, h):
    k = 0
    for g in t:
        if isinstance(g, list) and g and g[0] == 'gr_text' and g[1] == text:
            for e in g:
                if isinstance(e, list) and e and e[0] == 'effects':
                    for fnt in e:
                        if isinstance(fnt, list) and fnt and fnt[0] == 'font':
                            for sz in fnt:
                                if isinstance(sz, list) and sz and sz[0] == 'size':
                                    sz[1], sz[2] = Atom(str(h)), Atom(str(h)); k += 1
    assert k == 1, (text, k); return t


def drop_arc(t):
    n0 = len(t); i = next(k for k, g in enumerate(t) if isinstance(g, list) and g and g[0] == 'gr_arc'
                          and any(isinstance(x, list) and x[:2] == ['layer', 'Edge.Cuts'] for x in g))
    del t[i]; assert len(t) == n0 - 1; return t


def gnd_pour_removed(t):
    n0 = len(t)
    t2 = [g for g in t if not (isinstance(g, list) and g and g[0] == 'zone' and any(isinstance(x, list) and x[:2] == ['net', 'GND'] for x in g)
                                and any(isinstance(x, list) and x and x[0] == 'layer' and x[1] == 'B.Cu' for x in g))]
    assert len(t2) == n0 - 1, n0 - len(t2); return t2


FILE = {   # defects made at file level (text edits; 1.10 P09: b.Remove() broke SWIG)
    'outline_arc_missing': drop_arc,
    'pin1_mark_missing': lambda t: drop_text(t, '1'),
    'label_missing': lambda t: drop_text(t, 'X16.1-2 STOP'),
    'label_swap': lambda t: swap_text(t, 'X11.1-2 ARM', 'X14.1-2 MARK'),
    'label_swap_test': lambda t: swap_text(t, 'TEST kom.10', 'TEST kom.11'),
    'variant_missing': lambda t: drop_text(t, 'Z P04: DNP'),
    'small_text': lambda t: text_size(t, 'EGRLab 10.2026', .8),
    'gnd_pour_removed': gnd_pour_removed,
    'title_wrong': lambda t: swap_text(t, TYTUL, 'STRONA PANELU'),
    'copper_18um': lambda t: cu18(t),
}


def cu18(t):                                                                        # F.Cu 18 um in the stackup instead of 35 um
    k = 0
    for g in t:
        if isinstance(g, list) and g and g[0] == 'setup':
            for st in g:
                if isinstance(st, list) and st and st[0] == 'stackup':
                    for L in st:
                        if isinstance(L, list) and L[:2] == ['layer', 'F.Cu']:
                            for e in L:
                                if isinstance(e, list) and e and e[0] == 'thickness':
                                    e[1] = Atom('0.018'); k += 1
    assert k == 1, k; return t


PRO = {'rules_relaxed': lambda d: d['board']['design_settings']['rules'].update(min_text_height=.8)}   # DRC legend minimum lowered
CASES = [(null_control, None), (drc_short, 'Fresh native DRC'), (ref_renamed, 'Parts'), (value_changed, 'Netlist'), ('copper_18um', 'Board stack'),
         (small_ring, 'Every PTH pad and via'), ('rules_relaxed', 'Rules'), ('outline_arc_missing', 'Outline'), (mount_shift, 'M3 holes'), (zone_copper, 'Standoff zones D7'),
         (jp12_off_edge, 'J_P12'), (jp12_pinout, 'J_P12'), ('pin1_mark_missing', 'J_P12'), (narrow_track, 'Track widths'),
         (supply_03, 'Track widths'), (field_turned, 'Wire fields'), (field_drill, 'Wire fields'), (anchor_track, 'Wire fields'),
         (strip_blocked, 'Wire fields'), ('label_missing', 'Field labels'), ('label_swap', 'Field labels'), ('label_swap_test', 'Field labels'),
         ('variant_missing', 'R1 variant note'), ('small_text', 'Legend size'), ('gnd_pour_removed', 'GND pours'), (bottom_part, 'All parts on the top side'),
         (ref_on_part, 'Every visible reference outside'), (ref_far, 'Every visible reference nearer'), ('title_wrong', 'Silkscreen: board name')]
assert root.resolve().is_relative_to(P.resolve()) and root.name == 'negative-controls'
shutil.rmtree(root, ignore_errors=True); root.mkdir(parents=True)
results = []
for fn, expected in CASES:
    name = fn if isinstance(fn, str) else fn.__name__; d = root / name; d.mkdir()
    b = p.LoadBoard(str(src))
    if callable(fn):
        fn(b)
    b.BuildConnectivity(); p.ZONE_FILLER(b).Fill(b.Zones())
    copy = d / f'{NAME}.kicad_pcb'; p.SaveBoard(str(copy), b)
    if name in FILE:
        t = FILE[name](parse(copy.read_text(encoding='utf-8'))); copy.write_text(dump(t) + '\n', encoding='utf-8')
    for f in (P / 'eda').glob('*.kicad_sch'):
        shutil.copy2(f, d / f.name)
    shutil.copy2(P / f'eda/{NAME}.kicad_pro', d / f'{NAME}.kicad_pro')
    if name in PRO:
        pj = json.loads((d / f'{NAME}.kicad_pro').read_text()); PRO[name](pj); (d / f'{NAME}.kicad_pro').write_text(json.dumps(pj, indent=2) + '\n')
    for tbl in ('fp-lib-table', 'sym-lib-table'):
        (d / tbl).write_text((P / 'eda' / tbl).read_text().replace('${KIPRJMOD}', (P / 'eda').as_posix()))
    subprocess.run([sys.executable, str(P / 'src/verify_pcb.py'), str(copy), str(d)], capture_output=True, text=True)
    rep = json.loads((d / 'pcb-checks.json').read_text(encoding='utf-8'))
    failed = [c['check'] for c in rep['checks'] if not c['pass']]
    hit = (not failed) if expected is None else any(c.startswith(expected) for c in failed)
    results.append({'control': name, 'expected_failing_check': expected or 'none (all PASS)', 'detected': hit, 'failed_checks': failed})
    print('OK ' if hit else 'BAD', name, '->', len(failed), 'failing checks', flush=True)
(P / 'verification/negative-controls.json').write_text(json.dumps(results, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(sum(r['detected'] for r in results), '/', len(results), 'negative controls (with the null control)')
sys.exit(0 if all(r['detected'] for r in results) else 1)
