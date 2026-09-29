"""R2 legends on F.SilkS, placed without collisions (run after finish_silkscreen.py).
- J7 B+/GND and J6 OUT+/GND/NC as in R1,
- J5 pin numbers 1..6 for the new (rot 180) orientation, wires leave towards the bottom edge,
- PCB1-06: net names at the test pads J1, J2 and J4 (ODBIOR refers to J1.1 and J4.2); J8 is dense: S = PG_SEND, L = PG_LINK,
- PCB1-02: 'TAB' at Q2 in addition to the thick tab-side line of the TO-220 outline.
Each label is moved at most 4 mm from its preferred point; otherwise the script fails.
"""
from pathlib import Path
import pcbnew as p, math, json
from sexpr import parse, dump
P = Path(__file__).resolve().parents[1]; fn = P / 'eda/P01.kicad_pcb'
LEGENDS = {'B+', 'GND', 'OUT+', 'NC', 'BAT', '3V3', 'SAFE_N', 'S', 'L', 'TAB', '1', '2', '3', '4', '5', '6'}
# Idempotent: drop board-level legends of a previous run at file level (pcbnew Remove() on drawings crashes).
tree = parse(fn.read_text(encoding='utf-8'))
tree = [g for g in tree if not (isinstance(g, list) and g and g[0] == 'gr_text' and g[1] in LEGENDS and ['layer', 'F.SilkS'] in [x[:2] for x in g if isinstance(x, list)])]
fn.write_text(dump(tree) + chr(10), encoding='utf-8')
b = p.LoadBoard(str(fn))
mm = p.FromMM


def xy(x, y):
    return p.VECTOR2I(mm(x), mm(y))


def box(item, extra=0.0):
    q = item.GetBoundingBox()
    return (p.ToMM(q.GetLeft()) - extra, p.ToMM(q.GetTop()) - extra, p.ToMM(q.GetRight()) + extra, p.ToMM(q.GetBottom()) + extra)


def hit(a, c):
    return a[0] < c[2] and a[2] > c[0] and a[1] < c[3] and a[3] > c[1]


obst = []
for f in b.GetFootprints():
    for pad in f.Pads():
        obst.append(box(pad, .35))
    for g in f.GraphicalItems():
        if g.GetLayer() == p.F_SilkS:
            obst.append(box(g, .2))
    if f.Reference().IsVisible():
        obst.append(box(f.Reference(), .2))
for g in b.GetDrawings():
    if g.GetLayer() == p.F_SilkS:
        obst.append(box(g, .2))
for hx in (55, 108):  # keep legends off the heatsink footprint (invisible after assembly)
    obst.append((hx - 21.3, 5.2, hx + 21.3, 30.8))
labels = [('B+', 15, 29.6), ('GND', 27.5, 25),
          ('OUT+', 141, 32), ('GND', 141, 26.92), ('NC', 141, 21.84),
          ('BAT', 15.9, 46.0), ('GND', 15.9, 51.08),
          ('OUT+', 151.3, 60.2), ('GND', 146.22, 55.2),
          ('3V3', 147.8, 87.5), ('SAFE_N', 149.3, 92.58), ('GND', 147.8, 97.66),
          ('S', 139.4, 95.4), ('L', 134.32, 95.4),
          ('TAB', 87.0, 39.2)]
labels += [(str(k), 144.5 - 2.54 * (k - 1), 103.3) for k in range(1, 7)]
report = []
for text, x0, y0 in labels:
    t = p.PCB_TEXT(b); t.SetText(text); t.SetTextSize(xy(1, 1)); t.SetTextThickness(mm(.15)); t.SetLayer(p.F_SilkS)
    cands = sorted({(round(x0 + dx * .25, 2), round(y0 + dy * .25, 2)) for dx in range(-16, 17) for dy in range(-16, 17)},
                   key=lambda q: math.dist(q, (x0, y0)))
    for q in cands:
        t.SetPosition(xy(*q)); bb = box(t, .18)
        if bb[0] < 1 or bb[1] < 1 or bb[2] > 159 or bb[3] > 119 or any(hit(bb, o) for o in obst):
            continue
        b.Add(t); obst.append(bb); report.append({'text': text, 'preferred': [x0, y0], 'placed': list(q), 'shift_mm': round(math.dist(q, (x0, y0)), 2)})
        break
    else:
        raise SystemExit(f'No clear position within 4 mm for legend {text} at ({x0},{y0})')
p.SaveBoard(str(fn), b, True)
(P / 'verification/legends-placement.json').write_text(json.dumps(report, indent=2) + '\n')
print('Placed', len(report), 'legends; max shift', max(r['shift_mm'] for r in report), 'mm')
