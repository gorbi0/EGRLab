"""Working preview (not a release artifact): per-layer copper incl. filled zones, pads, courtyards, refs.
usage: preview.py OUT.png [F|B|both]"""
import pcbnew as p, sys
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
P = Path(__file__).resolve().parents[2]
b = p.LoadBoard(str(P / 'eda/P00.kicad_pcb')); S = 8
side = sys.argv[2] if len(sys.argv) > 2 else 'both'
layers = {'F': [p.F_Cu], 'B': [p.B_Cu], 'both': [p.B_Cu, p.F_Cu]}[side]
im = Image.new('RGB', (115 * S + 1, 70 * S + 1), 'white'); d = ImageDraw.Draw(im)
font = ImageFont.load_default()


def m(v):
    return p.ToMM(v) * S


ZC = {p.F_Cu: '#f4c7c3', p.B_Cu: '#c3d4f4'}; TC = {p.F_Cu: '#c33', p.B_Cu: '#36c'}
for layer in layers:
    for z in b.Zones():
        if z.GetIsRuleArea() or not z.IsOnLayer(layer):
            continue
        polys = z.GetFilledPolysList(layer)
        for i in range(polys.OutlineCount()):
            ol = polys.Outline(i)
            pts = [(m(ol.CPoint(k).x), m(ol.CPoint(k).y)) for k in range(ol.PointCount())]
            if len(pts) > 2:
                d.polygon(pts, fill='#f0e68c' if z.GetNetname() == 'VPROT' else ZC[layer])
            for h in range(polys.HoleCount(i)):
                hl = polys.Hole(i, h)
                hp = [(m(hl.CPoint(k).x), m(hl.CPoint(k).y)) for k in range(hl.PointCount())]
                if len(hp) > 2:
                    d.polygon(hp, fill='white')
d.rectangle([0, 0, 115 * S, 70 * S], outline='black')
for layer in layers:
    for t in b.GetTracks():
        if isinstance(t, p.PCB_VIA):
            r = m(t.GetWidth(p.F_Cu)) / 2; c = t.GetPosition(); d.ellipse([m(c.x) - r, m(c.y) - r, m(c.x) + r, m(c.y) + r], fill='#3a3')
        elif t.GetLayer() == layer:
            d.line([m(t.GetStart().x), m(t.GetStart().y), m(t.GetEnd().x), m(t.GetEnd().y)], fill=TC[layer], width=max(1, int(m(t.GetWidth()))))
for f in b.GetFootprints():
    for g in f.GraphicalItems():
        if g.GetLayer() == p.F_CrtYd and isinstance(g, p.PCB_SHAPE):
            if g.GetShape() == p.SHAPE_T_CIRCLE:
                c = g.GetCenter(); r = m(g.GetRadius()); d.ellipse([m(c.x) - r, m(c.y) - r, m(c.x) + r, m(c.y) + r], outline='#999')
            elif g.GetShape() == p.SHAPE_T_RECT:
                d.polygon([(m(v.x), m(v.y)) for v in g.GetCorners()], outline='#999')
            else:
                d.line([(m(g.GetStart().x), m(g.GetStart().y)), (m(g.GetEnd().x), m(g.GetEnd().y))], fill='#999')
    for a in f.Pads():
        c = a.GetPosition(); sx, sy = m(a.GetSize(p.F_Cu).x) / 2, m(a.GetSize(p.F_Cu).y) / 2
        if a.GetOrientationDegrees() % 180:
            sx, sy = sy, sx
        col = '#e90' if a.GetAttribute() != p.PAD_ATTRIB_NPTH else '#000'
        d.ellipse([m(c.x) - sx, m(c.y) - sy, m(c.x) + sx, m(c.y) + sy], outline=col, width=2)
    bb = f.GetBoundingBox(False)
    d.text((m(bb.GetCenter().x) - 8, m(bb.GetCenter().y) - 5), f.GetReference(), fill='blue', font=font)
im.save(sys.argv[1] if len(sys.argv) > 1 else str(P / 'verification/preview.png')); print('preview saved', side)
