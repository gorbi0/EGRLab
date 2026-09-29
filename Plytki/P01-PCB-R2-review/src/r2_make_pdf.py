"""R2 review document: 4 A4 landscape pages, CAD plots rasterised at 600 dpi in exact physical size.
KiCad's own PDF plot places this board at the paper corner (board origin 0,0), where printers clip;
here the board sits 20 mm from the left and 35 mm from the top edge. Print at 100 %, no fitting.
Run with KiCad Python (pcbnew + PIL). Output: output/pdf/P01-PCB-R2-dokumentacja.pdf, output/previews/*.png
"""
from pathlib import Path
import pcbnew as p, math, json
from PIL import Image, ImageDraw, ImageFont
P = Path(__file__).resolve().parents[1]; b = p.LoadBoard(str(P / 'eda/P01.kicad_pcb'))
DPI = 600; PX = DPI / 25.4; W, H = round(297 * PX), round(210 * PX); OX, OY = 20.0, 35.0
FONT = 'C:/Windows/Fonts/arial.ttf'; FONTB = 'C:/Windows/Fonts/arialbd.ttf'


def font(pt, bold=False):
    return ImageFont.truetype(FONTB if bold else FONT, round(pt / 72 * DPI))


def P2(x, y):  # board mm -> page px
    return ((OX + x) * PX, (OY + y) * PX)


def mmv(v):
    return (p.ToMM(v.x), p.ToMM(v.y))


def poly_set(d, ps, fill, bg='white'):
    for k in range(ps.OutlineCount()):
        o = ps.Outline(k); pts = [P2(*mmv(o.CPoint(i))) for i in range(o.PointCount())]
        if len(pts) > 2:
            d.polygon(pts, fill=fill)
        for h in range(ps.HoleCount(k)):
            hh = ps.Hole(k, h); hp = [P2(*mmv(hh.CPoint(i))) for i in range(hh.PointCount())]
            if len(hp) > 2:
                d.polygon(hp, fill=bg)


def thick(d, pts, w, col):
    wpx = max(1, round(w * PX))
    for a, c in zip(pts, pts[1:]):
        d.line([P2(*a), P2(*c)], fill=col, width=wpx)
    r = w / 2
    for q in pts:
        x, y = P2(*q); d.ellipse([x - r * PX, y - r * PX, x + r * PX, y + r * PX], fill=col)


def shape(d, g, col):
    w = max(p.ToMM(g.GetWidth()), .1); s = g.GetShape()
    if s == p.SHAPE_T_SEGMENT:
        thick(d, [mmv(g.GetStart()), mmv(g.GetEnd())], w, col)
    elif s == p.SHAPE_T_RECT:
        a, c = mmv(g.GetStart()), mmv(g.GetEnd())
        thick(d, [a, (c[0], a[1]), c, (a[0], c[1]), a], w, col)
    elif s == p.SHAPE_T_CIRCLE:
        c = mmv(g.GetCenter()); r = p.ToMM(g.GetRadius())
        thick(d, [(c[0] + r * math.cos(k * math.tau / 72), c[1] + r * math.sin(k * math.tau / 72)) for k in range(73)], w, col)
    elif s == p.SHAPE_T_ARC:
        c = mmv(g.GetCenter()); a = mmv(g.GetStart()); r = p.ToMM(g.GetRadius())
        a0 = math.atan2(a[1] - c[1], a[0] - c[0]); sweep = math.radians(g.GetArcAngle().AsDegrees()); n = max(8, int(abs(sweep) * r * 4))
        thick(d, [(c[0] + r * math.cos(a0 + sweep * k / n), c[1] + r * math.sin(a0 + sweep * k / n)) for k in range(n + 1)], w, col)
    elif s == p.SHAPE_T_POLY:
        ps = g.GetPolyShape()
        for k in range(ps.OutlineCount()):
            o = ps.Outline(k); pts = [mmv(o.CPoint(i)) for i in range(o.PointCount())]
            thick(d, pts + pts[:1], w, col)
    else:
        thick(d, [mmv(g.GetStart()), mmv(g.GetEnd())], w, col)


def text(d, t, col, layer):
    if not t.IsVisible() or t.GetLayer() != layer:
        return
    ps = p.SHAPE_POLY_SET(); t.TransformTextToPolySet(ps, 0, p.FromMM(.005), p.ERROR_INSIDE); poly_set(d, ps, col)


def edge(d):
    for g in b.GetDrawings():
        if g.GetLayer() == p.Edge_Cuts:
            shape(d, g, 'black')


def holes(d):
    for f in b.GetFootprints():
        for a in f.Pads():
            c = P2(*mmv(a.GetPosition())); r = p.ToMM(a.GetDrillSize().x) / 2 * PX
            if r > 0:
                d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill='white', outline='black', width=2)
    for t in b.GetTracks():
        if isinstance(t, p.PCB_VIA):
            c = P2(*mmv(t.GetPosition())); r = p.ToMM(t.GetDrill()) / 2 * PX; d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill='white')


def keepouts(d, col=(200, 0, 0)):
    for z in b.Zones():
        if z.GetIsRuleArea() and z.GetZoneName().endswith('F.Cu keepout'):
            o = z.Outline().Outline(0); pts = [mmv(o.CPoint(i)) for i in range(o.PointCount())]
            thick(d, pts + pts[:1], .15, col)


def plot(kind):
    img = Image.new('RGB', (W, H), 'white'); d = ImageDraw.Draw(img)
    if kind == 'assembly':
        for f in b.GetFootprints():
            for g in f.GraphicalItems():
                if isinstance(g, p.PCB_SHAPE) and g.GetLayer() == p.F_Fab:
                    shape(d, g, (150, 150, 150))
        for f in b.GetFootprints():
            for a in f.Pads():
                ps = p.SHAPE_POLY_SET(); a.TransformShapeToPolygon(ps, p.F_Cu if a.IsOnLayer(p.F_Cu) else p.B_Cu, 0, p.FromMM(.005), p.ERROR_INSIDE)
                for k in range(ps.OutlineCount()):
                    o = ps.Outline(k); pts = [mmv(o.CPoint(i)) for i in range(o.PointCount())]
                    thick(d, pts + pts[:1], .12, (60, 60, 60))
            for g in f.GraphicalItems():
                if isinstance(g, p.PCB_SHAPE) and g.GetLayer() == p.F_SilkS:
                    shape(d, g, 'black')
                elif isinstance(g, p.PCB_TEXT):
                    text(d, g, 'black', p.F_SilkS)
            text(d, f.Reference(), 'black', p.F_SilkS)
        for g in b.GetDrawings():
            if isinstance(g, p.PCB_TEXT):
                text(d, g, 'black', p.F_SilkS)
            elif isinstance(g, p.PCB_SHAPE) and g.GetLayer() == p.F_SilkS:
                shape(d, g, 'black')
        holes(d)
    else:
        layer = p.F_Cu if kind == 'front' else p.B_Cu
        for z in b.Zones():
            if not z.GetIsRuleArea() and z.IsOnLayer(layer):
                poly_set(d, z.GetFilledPolysList(layer), (205, 205, 205))
        for t in b.GetTracks():
            if isinstance(t, p.PCB_VIA) or t.GetLayer() == layer:
                ps = p.SHAPE_POLY_SET(); t.TransformShapeToPolygon(ps, layer, 0, p.FromMM(.005), p.ERROR_INSIDE); poly_set(d, ps, 'black')
        for f in b.GetFootprints():
            for a in f.Pads():
                if a.IsOnLayer(layer):
                    ps = p.SHAPE_POLY_SET(); a.TransformShapeToPolygon(ps, layer, 0, p.FromMM(.005), p.ERROR_INSIDE); poly_set(d, ps, 'black')
        holes(d)
        if kind == 'front':
            keepouts(d)
    edge(d)
    return img


def page_frame(img, n, title, sub):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, round(6 * PX)], fill=(8, 124, 131))
    d.text((17 * PX, 11 * PX), title, fill=(23, 43, 58), font=font(20, True))
    d.text((17 * PX, 21 * PX), sub, fill=(87, 103, 114), font=font(10))
    d.line([17 * PX, 200 * PX, 280 * PX, 200 * PX], fill=(196, 209, 216), width=3)
    d.text((17 * PX, 202 * PX), 'EGRLab | P01-PCB-R2-review | SCH R3 | 24.09.2026', fill=(87, 103, 114), font=font(8))
    d.text((268 * PX, 202 * PX), f'{n} / 4', fill=(87, 103, 114), font=font(8))
    return d


def scale_bar(d):
    y = OY + 120 + 12
    d.line([P2(0, y - OY)[0], y * PX, P2(100, y - OY)[0], y * PX], fill='black', width=5)
    for x in (0, 100):
        d.line([P2(x, 0)[0], (y - 2) * PX, P2(x, 0)[0], (y + 2) * PX], fill='black', width=5)
    d.text((P2(0, 0)[0], (y + 3) * PX), 'Belka kontrolna: dokładnie 100 mm. Obrys PCB: 160 × 120 mm.', fill='black', font=font(9))


def notes(d, x, y, lines, pt=9.5, width=92):
    f = font(pt); lh = pt / 72 * 25.4 * 1.45
    for s in lines:
        words = s.split(); line = ''
        for w in words:
            cand = (line + ' ' + w).strip()
            if d.textlength(cand, font=f) / PX > width:
                d.text((x * PX, y * PX), line, fill=(23, 43, 58), font=f); y += lh; line = w
            else:
                line = cand
        d.text((x * PX, y * PX), line, fill=(23, 43, 58), font=f); y += lh * 1.35
    return y


chk = json.loads((P / 'verification/pcb-checks.json').read_text()); neg = json.loads((P / 'verification/negative-controls.json').read_text())
drc = json.loads((P / 'verification/drc.json').read_text())
n_ok = sum(c['pass'] for c in chk['checks']); n_neg = sum(r['detected'] for r in neg)
det = chk['details']; L = next(v for k, v in det.items() if k.startswith('R2/PCB1-03: OV_REF'))
NB = next(v for k, v in det.items() if k.startswith('R2/PCB1-03,05,06')); TP = det['Actual Q1 source/gate probe tracks <= 5 mm']
ln = L['routed_mm']; gmin = min(L['min_edge_gap_to_power_mm'].values())
def pl(v, d=1):
    return f'{v:.{d}f}'.replace('.', ',')
pages = []
# Page 1: summary
img = Image.new('RGB', (W, H), 'white'); d = page_frame(img, 1, 'P01 PROTECT: PCB R2 do recenzji', 'Poprawki z recenzji PCB R1 (PCB1-01…06). Schemat R3 bez zmian.')
for i, (a, v) in enumerate([('DRC / NIEPOŁĄCZONE / SCHEMAT', f"{len(drc['violations'])} / {len(drc['unconnected_items'])} / {len(drc['schematic_parity'])}"),
                            ('KONTROLE PCB', f'{n_ok}/{len(chk["checks"])} PASS'), ('PRÓBY UJEMNE', f'{n_neg}/{len(neg)} wykryte')]):
    x = 17 + i * 90; d.rounded_rectangle([x * PX, 30 * PX, (x + 83) * PX, 52 * PX], radius=round(3 * PX), fill=(238, 244, 246))
    d.text(((x + 5) * PX, 33 * PX), a, fill=(87, 103, 114), font=font(8, True)); d.text(((x + 5) * PX, 41 * PX), v, fill=(23, 43, 58), font=font(15, True))
y = notes(d, 17, 60, [
    'PCB1-01 (blokujące): pod profilami HS1/HS2 nie ma miedzi F.Cu — obszary reguł na F.Cu (obrys profilu +0,5 mm, wnęka TO-220 otwarta). BAT_FUSED wchodzi do wnęki HS1 od dołu, DRAIN i GATE wychodzą z wnęki HS2 pionowo; pod profilami zostaje tylko B.Cu (powrót GND), za laminatem.',
    'PCB1-02 (blokujące): TO-220 (Q1, Q2, D2) mają na nadruku obrys z grubą linią po stronie taba; przy Q2 dodatkowo napis TAB.',
    f"PCB1-03: rozmieszczenie w blokach funkcjonalnych. Długość ścieżek R1 → R2: OV_REF 107 → {pl(ln['P01_OV_REF'])} mm, OV_SENSE 51 → {pl(ln['P01_OV_SENSE'])} mm, UV_SENSE 79 → {pl(ln['P01_UV_SENSE'])} mm, REF 97 → {pl(ln['P01_REF'])} mm; sieci wrażliwe ≥ {pl(gmin)} mm od miedzi mocy (R1: OV_REF przecinało BAT_FUSED). C10 przy U2, C11 przy U4 (uwagi BOM R3).",
    'PCB1-04: J5 obrócone — przewody wychodzą w dół, do najbliższej krawędzi; pod nimi nie ma elementów.',
    f"PCB1-05: C6 we wnęce HS2 bezpośrednio pod G i S Q1 ({pl(NB['C6.1-Q1.1'])} mm od każdego pinu; R1: 18,5 mm). TP1/TP2 we wnęce, {pl(TP['TP1'], 2)}/{pl(TP['TP2'], 2)} mm ścieżki do Q1.",
    f"PCB1-06: nazwy sieci przy J1, J2, J4, J8; D9 {pl(NB['D9.2-Q2.1'])}/{pl(NB['D9.1-Q2.3'])} mm od G/S Q2 (R1: 32/20 mm). Oznaczenia rezystorów wewnątrz obrysów korpusu.",
    'Bez zmian: wymiar 160 × 120 mm, otwory M3, położenie HS1/HS2, D2, Q1, J7, J6, LK1, D1, D3, C3, C4; wartości, footprinty i pady R3.'], pt=10, width=150)
render = Image.open(P / 'output/previews/render-top.png').convert('RGB'); render = render.crop(render.convert('L').point(lambda v: 255 if v > 12 else 0).getbbox()); rw = 105; rh = rw * render.height / render.width; render = render.resize((round(rw * PX), round(rh * PX)))
img.paste(render, (round(178 * PX), round(60 * PX)))
notes(d, 178, 60 + rh + 4, ['Render 3D (poglądowy, bez modeli części). Przymiarka, termika, SOA i odbiór elektryczny: NIE ZBADANO. Gerbery dopiero po przymiarce 1:1 i przeglądzie.'], pt=9, width=100)
pages.append(img)
for n, kind, title, sub, lines in [
    (2, 'assembly', 'Montaż 1:1', 'Strona elementów. Druk 100 %, bez dopasowania do strony.',
     ['Zmierz belkę 100 mm i obrys przed przykładaniem części.', 'HS1/HS2: SK129-63STS; TO-220 D2/Q1 we wnękach, gruba linia nadruku = strona taba.',
      'C6 (WIMA 1 µF) stoi we wnęce HS2 pod Q1 — wlutuj przed Q1/HS2; sprawdź prześwit do korpusu TO-220 i dostęp sondy do TP1/TP2.',
      'J5: przewody w dół do kotew 12,5 mm od lutów; J7 bez zmian.', 'R1 i R23 (PR02) montować ok. 3 mm nad laminatem (wymóg R3).',
      'Oznaczenia rezystorów są wewnątrz obrysów korpusów.']),
    (3, 'front', 'Miedź F.Cu 1:1', 'Widok od strony elementów. Czerwony obrys: obszar reguł bez miedzi F.Cu pod profilami.',
     ['Pod profilami radiatorów brak miedzi F.Cu (ścieżek, przelotek, wylewki). Wnęki TO-220 otwarte.', 'BAT_FUSED: ścieżka 3 mm pod dolną krawędzią strefy HS1, wejście do wnęki od dołu.',
      'DRAIN 2 mm pionowo we wnęce HS2, dalej 4 mm do LK1. GATE 0,8 mm: Q1 → C6 → D4/R27.', f"TP1/TP2 we wnęce: {pl(TP['TP1'], 2)} / {pl(TP['TP2'], 2)} mm ścieżki do Q1.",
      'To widok kontrolny, nie maska do trawienia.']),
    (4, 'back', 'Miedź B.Cu 1:1', 'Widok przez PCB od strony elementów — bez odbicia lustrzanego.',
     ['Szyna VS 5 mm na B.Cu (i F.Cu do x=94), trzy przelotki Ø1,2/0,6.', 'Powrót GND 5 mm górą i prawym bokiem — pod profilami tylko B.Cu.',
      'Pady kołków radiatorów pozostają bez sieci.', 'Kwalifikacja 5 A wymaga pomiaru nagrzewania (ODBIOR R3).'])]:
    img = plot(kind); d = page_frame(img, n, title, sub); scale_bar(d); notes(d, 188, 38, lines, pt=9.5, width=90); pages.append(img)
out = P / 'output/pdf/P01-PCB-R2-dokumentacja.pdf'
pages[0].save(out, 'PDF', resolution=DPI, save_all=True, append_images=pages[1:])
for n, name in [(1, 'assembly'), (2, 'copper-front'), (3, 'copper-back')]:
    crop = pages[n].crop((round(OX * PX) - 20, round(OY * PX) - 20, round((OX + 160) * PX) + 20, round((OY + 120) * PX) + 20))
    crop.resize((crop.width // 4, crop.height // 4), Image.LANCZOS).save(P / f'output/previews/{name}.png')
for n, pg in enumerate(pages, 1):
    pg.resize((pg.width // 5, pg.height // 5), Image.LANCZOS).save(P / f'output/previews/pdf-{n}.png')
print(out, 'pages', len(pages))
