"""Negative controls of the P12 R1 PCB checks: working copies of the finished board with one deliberate defect each, plus a null control
(unchanged copy). verify_pcb.py must fail the named check on every defective copy and pass everything on the null control.
eda/P12.kicad_pcb is never modified; copies and reports stay in verification/negative-controls/ (not production files).
Pattern of P10 R2 negative_controls.py; defects chosen for the P12 checks.
"""
from pathlib import Path
import pcbnew as p, json, subprocess, sys, shutil, os
from sexpr import parse, dump
sys.path.insert(0, str(Path(__file__).resolve().parent))
from board import NAME, REV, kxy
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


def track(b, layer, a, c, netname, w=.3):
    t = p.PCB_TRACK(b); t.SetLayer(layer); t.SetWidth(mm(w)); t.SetStart(a); t.SetEnd(c); t.SetNet(b.FindNet(netname)); b.Add(t)


def conn_shift(b): move(b, 'J3', 1.0, 0)                                       # P03 J_BP2 1 mm off its x
def conn_low(b): move(b, 'J8', 0, 1.0)                                         # P06 J_BP 1 mm lower (z)
def conn_turned(b):                                                            # P05 J_BP2 turned 180 deg about its centre: pin 1 at the larger x, odd row up
    f = fp(b, 'J6'); a1, a20 = pad(b, 'J6', '1').GetPosition(), pad(b, 'J6', '20').GetPosition()
    cx, cy = (a1.x + a20.x) // 2, (a1.y + a20.y) // 2; f.SetOrientationDegrees(270); f.SetPosition(xy(p.ToMM(2 * cx - a1.x), p.ToMM(2 * cy - a1.y)))
def rows_swapped(b):                                                           # P10 J1 mirrored rows: rot 270 + shift (even row below the odd row)
    f = fp(b, 'J9'); a1 = pad(b, 'J9', '1').GetPosition(); f.SetOrientationDegrees(270)
    f.SetPosition(xy(p.ToMM(a1.x) + 4 * 2.54, p.ToMM(a1.y) - 2.54))
def hole_shift(b): move(b, 'H5', .5, 0)                                        # M3 hole 0.5 mm off
def zone_copper(b):                                                            # GND track 2 mm from the centre of H5
    x, y = kxy(53.25, 51.45); track(b, p.B_Cu, xy(x - 1, y + 2), xy(x + 1, y + 2), 'GND')
def v5_narrow(b):                                                              # one 5V_SYS track 0.6 mm
    t = max((t for t in b.GetTracks() if not isinstance(t, p.PCB_VIA) and t.GetNetname() == '5V_SYS'), key=lambda t: t.GetLength()); t.SetWidth(mm(.6))
def v3_narrow(b):                                                              # one 3V3_IO track 0.3 mm
    t = max((t for t in b.GetTracks() if not isinstance(t, p.PCB_VIA) and t.GetNetname() == '3V3_IO'), key=lambda t: t.GetLength()); t.SetWidth(mm(.3))
def pin_in_pin(b):                                                             # P03 J_BP2.17 (5V_SYS) tied pin to pin to P05 J_BP2.17 (GND)
    track(b, p.F_Cu, pad(b, 'J3', '17').GetPosition(), pad(b, 'J6', '17').GetPosition(), '5V_SYS', 1.0)
def pad_net(b): pad(b, 'J2', '13').SetNet(b.FindNet('TEST_KEY'))              # MARK pin given another contract net
def wrong_type(b): fp(b, 'J5').SetFPIDAsString('Connector_IDC:IDC-Header_2x05_P2.54mm_Horizontal')   # angled instead of straight
def small_text(b):                                                             # the title printed 0.8 mm high
    t = next(d for d in b.GetDrawings() if isinstance(d, p.PCB_TEXT) and d.GetText() == f'{REV} S1 LOGGER'); t.SetTextSize(xy(.8, .8))
def label_on_body(b):                                                          # label of J3 moved onto the body of J3
    t = next(d for d in b.GetDrawings() if isinstance(d, p.PCB_TEXT) and d.GetText().startswith('J3  ')); a = pad(b, 'J3', '10').GetPosition(); t.SetPosition(a)
def back_text_on_hole(b):                                                      # bottom note moved onto H5 (as the first 4.10 draft)
    t = next(d for d in b.GetDrawings() if isinstance(d, p.PCB_TEXT) and d.GetLayer() == p.B_SilkS); x, y = kxy(80.0, 51.45); t.SetPosition(xy(x, y))
def null_control(b): pass


CASES = [(null_control, None), (conn_shift, 'Connector centres'), (conn_low, 'Connector centres'), (conn_turned, 'Orientation'), (rows_swapped, 'Orientation'),
         (hole_shift, 'M3:'), (zone_copper, 'Standoff zones D7'), (v5_narrow, 'Track widths'), (v3_narrow, 'Track widths'),
         (pin_in_pin, '5V_SYS, 3V3_IO and GND separate'), (pad_net, 'Every connector: straight IDC'), (wrong_type, 'Every connector: straight IDC'),
         ('gnd_pour_removed', 'GND pours'), ('label_missing', 'Every connector: one label'), ('label_swap', 'Every connector: one label'),
         ('pin1_missing', 'Every connector: one label'), (small_text, 'Every silkscreen text'), (label_on_body, 'No silkscreen text'), (back_text_on_hole, 'No silkscreen text'),
         ('title_wrong', 'Silkscreen: board name')]
assert root.resolve().is_relative_to(P.resolve()) and root.name == 'negative-controls'
shutil.rmtree(root, ignore_errors=True); root.mkdir(parents=True)
silk = json.loads((P / 'routing/silkscreen.json').read_text(encoding='utf-8'))
results = []


def file_edit(copy, f):
    t = parse(copy.read_text(encoding='utf-8')); n0 = len(t); t = f(t); copy.write_text(dump(t) + '\n', encoding='utf-8'); return n0 - len(t)


for fn, expected in CASES:
    name = fn if isinstance(fn, str) else fn.__name__; d = root / name; d.mkdir()
    b = p.LoadBoard(str(src))
    if callable(fn):
        fn(b)
    b.BuildConnectivity(); p.ZONE_FILLER(b).Fill(b.Zones())
    copy = d / f'{NAME}.kicad_pcb'; p.SaveBoard(str(copy), b)
    if name == 'gnd_pour_removed':   # B.Cu GND pour deleted at file level (pcbnew Remove() breaks SWIG)
        k = file_edit(copy, lambda t: [g for g in t if not (isinstance(g, list) and g and g[0] == 'zone' and any(isinstance(x, list) and x[:2] == ['net', 'GND'] for x in g)
                                                           and any(isinstance(x, list) and x and x[0] == 'layer' and x[1] == 'B.Cu' for x in g))]); assert k == 1, k
    if name == 'label_missing':      # label of J6 (P05 J_BP2) deleted
        lab = silk['labels']['J6']['text']; k = file_edit(copy, lambda t: [g for g in t if not (isinstance(g, list) and g and g[0] == 'gr_text' and g[1] == lab)]); assert k == 1, k
    if name == 'pin1_missing':       # pin-1 mark of J7 (P09 J1) deleted
        x, y = silk['pin1']['J7']
        def drop(t):
            out = []
            for g in t:
                if isinstance(g, list) and g and g[0] == 'gr_text' and g[1] == '1':
                    at = next(x_ for x_ in g if isinstance(x_, list) and x_ and x_[0] == 'at')
                    if abs(float(at[1]) - x) < .01 and abs(float(at[2]) - y) < .01:
                        continue
                out.append(g)
            return out
        k = file_edit(copy, drop); assert k == 1, k
    if name in ('label_swap', 'title_wrong'):
        t = parse(copy.read_text(encoding='utf-8')); k = 0
        l3, l6 = silk['labels']['J3']['text'], silk['labels']['J6']['text']
        for g in t:
            if isinstance(g, list) and g and g[0] == 'gr_text':
                if name == 'label_swap' and g[1] in (l3, l6):
                    g[1] = l6 if g[1] == l3 else l3; k += 1
                if name == 'title_wrong' and g[1] == f'{REV} S1 LOGGER':
                    g[1] = 'P12 S1 LOGGER'; k += 1
        assert k == (2 if name == 'label_swap' else 1), k
        copy.write_text(dump(t) + '\n', encoding='utf-8')
    for f in (P / 'eda').glob('*.kicad_sch'):
        shutil.copy2(f, d / f.name)
    shutil.copy2(P / f'eda/{NAME}.kicad_pro', d / f'{NAME}.kicad_pro')
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
