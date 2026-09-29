"""Working preview (not a release artifact): per-layer copper incl. filled zones, pads, courtyards, refs,
rule areas (dashed) and, with 'rats', the unrouted connections (minimum spanning tree per net, GND left out).
usage: preview.py OUT.png [F|B|both] [rats]"""
import pcbnew as p, sys, math, collections
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
P = Path(__file__).resolve().parents[2]
b = p.LoadBoard(str(P / 'eda/P03.kicad_pcb')); S = 8; BW, BH = 160, 120
side = sys.argv[2] if len(sys.argv) > 2 else 'both'
layers = {'F': [p.F_Cu], 'B': [p.B_Cu], 'both': [p.B_Cu, p.F_Cu]}[side]
im = Image.new('RGB', (BW * S + 1, BH * S + 1), 'white'); d = ImageDraw.Draw(im)
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
                d.polygon(pts, fill=ZC[layer])
            for h in range(polys.HoleCount(i)):
                hl = polys.Hole(i, h)
                hp = [(m(hl.CPoint(k).x), m(hl.CPoint(k).y)) for k in range(hl.PointCount())]
                if len(hp) > 2:
                    d.polygon(hp, fill='white')
d.rectangle([0, 0, BW * S, BH * S], outline='black')
for z in b.Zones():
    if z.GetIsRuleArea():
        o = z.Outline().Outline(0); pts = [(m(o.CPoint(k).x), m(o.CPoint(k).y)) for k in range(o.PointCount())]
        for a, c in zip(pts, pts[1:] + pts[:1]):
            d.line([a, c], fill='#0a0', width=1)
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
if 'rats' in sys.argv:
    nets = collections.defaultdict(list)
    for f in b.GetFootprints():
        for a in f.Pads():
            if a.GetNetCode() > 0 and not a.GetNetname().endswith('GND'):
                nets[a.GetNetname()].append((p.ToMM(a.GetPosition().x), p.ToMM(a.GetPosition().y)))
    total = 0
    for n, pts in nets.items():
        if len(pts) < 2:
            continue
        done = {0}; dist = {i: math.dist(pts[0], pts[i]) for i in range(1, len(pts))}; par = {i: 0 for i in range(1, len(pts))}
        while dist:
            j = min(dist, key=dist.get); done.add(j); total += dist[j]
            d.line([pts[par[j]][0] * S, pts[par[j]][1] * S, pts[j][0] * S, pts[j][1] * S], fill='#a0a', width=1)
            del dist[j]
            for k in dist:
                e = math.dist(pts[j], pts[k])
                if e < dist[k]:
                    dist[k] = e; par[k] = j
    print('ratsnest length (non-GND, MST) %.0f mm' % total)
im.save(sys.argv[1] if len(sys.argv) > 1 else str(P / 'verification/preview.png')); print('preview saved', side)
