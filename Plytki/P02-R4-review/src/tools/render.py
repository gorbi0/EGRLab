"""Debug render (not a release output): filled zones, tracks (F red, B blue), vias, pads; routing/render.png. Optional arg: DRC json to mark unconnected pairs."""
from pathlib import Path
import pcbnew as p, sys, json
from PIL import Image, ImageDraw
P = Path(__file__).resolve().parents[2]
b = p.LoadBoard(str(P / 'eda/P02.kicad_pcb')); S = 12
img = Image.new('RGB', (int(106.5 * S) + 1, int(100 * S) + 1), 'white'); d = ImageDraw.Draw(img, 'RGBA')
def poly(ps, fill):
    for k in range(ps.OutlineCount()):
        o = ps.Outline(k); d.polygon([(p.ToMM(o.CPoint(i).x) * S, p.ToMM(o.CPoint(i).y) * S) for i in range(o.PointCount())], fill=fill)
for z in b.Zones():
    if z.GetIsRuleArea():
        o = z.Outline().Outline(0); d.polygon([(p.ToMM(o.CPoint(i).x) * S, p.ToMM(o.CPoint(i).y) * S) for i in range(o.PointCount())], outline=(0, 150, 0, 255)); continue
    for L, col in ((p.B_Cu, (80, 80, 255, 50)), (p.F_Cu, (255, 120, 0, 60) if z.GetNetname() != 'GND' else (255, 80, 80, 35))):
        if z.IsOnLayer(L): poly(z.GetFilledPolysList(L), col)
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        c = t.GetPosition(); r = p.ToMM(t.GetWidth(p.F_Cu)) / 2 * S; d.ellipse([p.ToMM(c.x) * S - r, p.ToMM(c.y) * S - r, p.ToMM(c.x) * S + r, p.ToMM(c.y) * S + r], fill=(0, 0, 0, 255))
    else:
        col = (220, 0, 0, 255) if t.GetLayer() == p.F_Cu else (0, 0, 220, 200)
        d.line([(p.ToMM(t.GetStart().x) * S, p.ToMM(t.GetStart().y) * S), (p.ToMM(t.GetEnd().x) * S, p.ToMM(t.GetEnd().y) * S)], fill=col, width=max(1, int(p.ToMM(t.GetWidth()) * S)))
for f in b.GetFootprints():
    for a in f.Pads():
        bb = a.GetBoundingBox(); d.rectangle([p.ToMM(bb.GetLeft()) * S, p.ToMM(bb.GetTop()) * S, p.ToMM(bb.GetRight()) * S, p.ToMM(bb.GetBottom()) * S], outline=(0, 0, 0, 255))
if len(sys.argv) > 1:
    for u in json.loads(Path(sys.argv[1]).read_text())['unconnected_items']:
        pts = [(i['pos']['x'] * S, i['pos']['y'] * S) for i in u['items']]; d.line(pts, fill=(255, 0, 255, 255), width=3)
img.save(P / 'routing/render.png'); print('routing/render.png')
