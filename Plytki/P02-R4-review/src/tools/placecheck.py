"""Placement aid (not a release check): courtyard overlaps, courtyards in the D7 standoff zones or outside the board, and a PNG
(courtyards, pads coloured by net class, references) in routing/placement.png. Run after build_board.py."""
from pathlib import Path
import pcbnew as p, sys, itertools, math
from PIL import Image, ImageDraw, ImageFont
P = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(P / 'src'))
from build_board import holes, W, Hh
b = p.LoadBoard(str(P / 'eda/P02.kicad_pcb'))
S = 10; img = Image.new('RGB', (int(W * S) + 1, int((Hh + 8) * S) + 1), 'white'); d = ImageDraw.Draw(img)
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 11)
except OSError:
    font = ImageFont.load_default()
d.rectangle([0, 0, W * S, Hh * S], outline='black')
for x, y in holes():
    d.ellipse([(x - 3.5) * S, (y - 3.5) * S, (x + 3.5) * S, (y + 3.5) * S], outline='red')
polys = {}; side = {}
OUT_OK = {'J_SV1', 'J_SV2', 'J2', 'J_BP'}
for f in b.GetFootprints():
    r = f.GetReference()
    if r.startswith('H'): continue
    f.BuildCourtyardCaches(); cy = f.GetCourtyard(p.B_CrtYd if f.IsFlipped() else p.F_CrtYd); polys[r] = cy; side[r] = f.IsFlipped()
    o = cy.Outline(0); pts = [(p.ToMM(o.CPoint(i).x) * S, p.ToMM(o.CPoint(i).y) * S) for i in range(o.PointCount())]
    d.polygon(pts, outline='blue')
    for a in f.Pads():
        bb = a.GetBoundingBox(); n = a.GetNetname()
        col = 'green' if n == 'GND' else 'orange' if any(k in n for k in ('BAT_IN', 'SW_COM', 'VSW', 'VMOTOR', 'HOLD_C', 'VLOG', 'CH_A')) else 'gray'
        d.rectangle([p.ToMM(bb.GetLeft()) * S, p.ToMM(bb.GetTop()) * S, p.ToMM(bb.GetRight()) * S, p.ToMM(bb.GetBottom()) * S], fill=col)
    c = cy.BBox().GetCenter(); d.text((p.ToMM(c.x) * S - 8, p.ToMM(c.y) * S - 6), r, fill='black', font=font)
bad = []
for (a, pa), (c, pc) in itertools.combinations(polys.items(), 2):
    if side[a] != side[c]: continue
    x = p.SHAPE_POLY_SET(pa); x.BooleanIntersection(pc)
    if x.Area() / 1e12 > 0.01: bad.append(f'overlap {a}-{c} {x.Area() / 1e12:.1f}')
for r, cy in polys.items():
    for hx, hy in holes():
        circ = p.SHAPE_POLY_SET(); circ.NewOutline()
        for k in range(32): circ.Append(p.FromMM(hx + 3.5 * math.cos(k * math.tau / 32)), p.FromMM(hy + 3.5 * math.sin(k * math.tau / 32)))
        x = p.SHAPE_POLY_SET(cy); x.BooleanIntersection(circ)
        if x.Area() > 0: bad.append(f'standoff {r} H({hx},{hy})')
    bb = cy.BBox()
    if r not in OUT_OK and (p.ToMM(bb.GetLeft()) < -0.01 or p.ToMM(bb.GetTop()) < -0.01 or p.ToMM(bb.GetRight()) > W + .01 or p.ToMM(bb.GetBottom()) > Hh + .01):
        bad.append(f'outside {r}')
img.save(P / 'routing/placement.png'); print('\n'.join(bad) or 'placement clean'); print(len(bad), 'issues')
