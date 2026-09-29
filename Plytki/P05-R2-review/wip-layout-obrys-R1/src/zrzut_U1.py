"""R2: raster views of the AD7606B area (F.Cu and B.Cu) for the review, from any P05 board file.
usage: python zrzut_U1.py BOARD.kicad_pcb OUT_PREFIX [x0 y0 x1 y1]   (KiCad Python; PIL)"""
import pcbnew as p, sys
from PIL import Image, ImageDraw, ImageFont
b = p.LoadBoard(sys.argv[1]); out = sys.argv[2]
x0, y0, x1, y1 = [float(v) for v in sys.argv[3:7]] if len(sys.argv) > 6 else (96, 29, 128, 57)
S = 40  # px per mm
W, H = int((x1 - x0) * S), int((y1 - y0) * S)
try:
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 14)
except OSError:
    font = ImageFont.load_default()
def P(v): return ((p.ToMM(v.x) - x0) * S, (p.ToMM(v.y) - y0) * S)
def poly(d, ps, fill=None, outline=None, width=1):
    for k in range(ps.OutlineCount()):
        o = ps.Outline(k); pts = [P(o.CPoint(i)) for i in range(o.PointCount())]
        if len(pts) > 2: d.polygon(pts, fill=fill, outline=outline, width=width)
COL = {'5VA_P05': (235, 200, 0), 'REFCAP': (220, 60, 220), 'ADC_REF': (220, 60, 220), 'REGCAP_A': (0, 190, 220), 'REGCAP_D': (0, 190, 220),
       'AD_DOUT_LOCAL': (255, 90, 0), 'GND': (70, 130, 70)}
for layer, name in [(p.F_Cu, 'F.Cu'), (p.B_Cu, 'B.Cu')]:
    img = Image.new('RGB', (W, H), (18, 18, 18)); d = ImageDraw.Draw(img)
    for z in b.Zones():
        if not z.GetIsRuleArea() and z.IsOnLayer(layer):
            poly(d, z.GetFilledPolysList(layer), fill=(40, 60, 40))
    for z in b.Zones():
        if z.GetIsRuleArea() and z.IsOnLayer(layer) and z.GetZoneName().startswith('ANALOG'):
            poly(d, z.Outline(), outline=(200, 200, 60), width=2)
    for t in b.GetTracks():
        n = t.GetNetname().split('/')[-1]; c = COL.get(n, (170, 50, 50))
        if isinstance(t, p.PCB_VIA):
            r = p.ToMM(t.GetWidth(p.F_Cu)) / 2 * S; q = P(t.GetPosition()); d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=(190, 190, 190) if n == 'GND' else c)
        elif t.GetLayer() == layer:
            ps = p.SHAPE_POLY_SET(); t.TransformShapeToPolygon(ps, layer, 0, p.FromMM(.005), p.ERROR_OUTSIDE); poly(d, ps, fill=c)
    for f in b.GetFootprints():
        for a in f.Pads():
            if a.IsOnLayer(layer):
                ps = p.SHAPE_POLY_SET(); a.TransformShapeToPolygon(ps, layer, 0, p.FromMM(.005), p.ERROR_OUTSIDE)
                n = a.GetNetname().split('/')[-1]; poly(d, ps, fill=COL.get(n, (185, 150, 70)) if n in COL and n != 'GND' else (185, 150, 70))
        if layer == p.F_Cu:
            cy = f.GetCourtyard(p.F_CrtYd)
            if cy.OutlineCount(): poly(d, cy, outline=(90, 160, 220))
            q = P(f.GetPosition())
            if x0 < p.ToMM(f.GetPosition().x) < x1 and y0 < p.ToMM(f.GetPosition().y) < y1: d.text((q[0] + 3, q[1] - 22), f.GetReference(), fill=(255, 255, 255), font=font)
    for i in range(int(x0) + 1, int(x1) + 1):
        if i % 5 == 0: d.line([((i - x0) * S, 0), ((i - x0) * S, 8)], fill=(200, 200, 200)); d.text(((i - x0) * S + 2, 8), str(i), fill=(200, 200, 200), font=font)
    for j in range(int(y0) + 1, int(y1) + 1):
        if j % 5 == 0: d.line([(0, (j - y0) * S), (8, (j - y0) * S)], fill=(200, 200, 200)); d.text((10, (j - y0) * S - 7), str(j), fill=(200, 200, 200), font=font)
    d.text((10, H - 22), f'{sys.argv[1].split("/")[-1]}  {name}  (1 mm = {S} px; żółte: 5VA, fiolet: REFCAP/ADC_REF, turkus: REGCAP, pomarańcz: DOUT)', fill=(255, 255, 255), font=font)
    img.save(f'{out}-{name}.png')
print('saved', out)
