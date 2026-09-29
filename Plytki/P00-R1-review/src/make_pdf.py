"""P00 R1 review document: 4 A4 landscape pages, CAD plots rasterised at 600 dpi in exact physical size.
Generator taken over from P02 R1 / P01 PCB-R2 (the board sits 20 mm from the left and 35 mm from the top edge,
not at the paper corner where printers clip). Print at 100 %. The assembly page also shows the F.Fab
references, because the channel columns carry only channel numbers on the silkscreen.
Run with KiCad Python (pcbnew + PIL). Output: output/pdf/P00-R1-PCB.pdf, output/previews/*.png
"""
from pathlib import Path
import pcbnew as p, math, json
from PIL import Image, ImageDraw, ImageFont
P = Path(__file__).resolve().parents[1]; b = p.LoadBoard(str(P / 'eda/P00.kicad_pcb')); BW, BH = 115, 70
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
        c = g.GetCorners(); pts = [mmv(v) for v in c]
        thick(d, pts + pts[:1], w, col)
    elif s == p.SHAPE_T_CIRCLE:
        c = mmv(g.GetCenter()); r = p.ToMM(g.GetRadius())
        thick(d, [(c[0] + r * math.cos(k * math.tau / 144), c[1] + r * math.sin(k * math.tau / 144)) for k in range(145)], w, col)
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


def corridor(d, col=(200, 0, 0)):
    for z in b.Zones():
        if z.GetIsRuleArea() and z.GetZoneName().startswith('B.Cu GND return'):
            o = z.Outline().Outline(0); pts = [mmv(o.CPoint(i)) for i in range(o.PointCount())]
            thick(d, pts + pts[:1], .2, col)


def plot(kind):
    img = Image.new('RGB', (W, H), 'white'); d = ImageDraw.Draw(img)
    if kind == 'assembly':
        for f in b.GetFootprints():
            for g in f.GraphicalItems():
                if isinstance(g, p.PCB_SHAPE) and g.GetLayer() == p.F_Fab:
                    shape(d, g, (150, 150, 150))
                elif isinstance(g, p.PCB_TEXT) and g.GetLayer() == p.F_Fab and not f.Reference().IsVisible() and not f.GetReference().startswith(('TP', 'H')):
                    text(d, g, (120, 120, 120), p.F_Fab)
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
                poly_set(d, z.GetFilledPolysList(layer), (205, 205, 205) if z.GetNetname() == 'GND' else (150, 150, 150))
        for t in b.GetTracks():
            if isinstance(t, p.PCB_VIA) or t.GetLayer() == layer:
                ps = p.SHAPE_POLY_SET(); t.TransformShapeToPolygon(ps, layer, 0, p.FromMM(.005), p.ERROR_INSIDE); poly_set(d, ps, 'black')
        for f in b.GetFootprints():
            for a in f.Pads():
                if a.IsOnLayer(layer):
                    ps = p.SHAPE_POLY_SET(); a.TransformShapeToPolygon(ps, layer, 0, p.FromMM(.005), p.ERROR_INSIDE); poly_set(d, ps, 'black')
        holes(d)
    edge(d)
    return img


def page_frame(img, n, title, sub):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, round(6 * PX)], fill=(8, 124, 131))
    d.text((17 * PX, 11 * PX), title, fill=(23, 43, 58), font=font(20, True))
    d.text((17 * PX, 21 * PX), sub, fill=(87, 103, 114), font=font(10))
    d.line([17 * PX, 200 * PX, 280 * PX, 200 * PX], fill=(196, 209, 216), width=3)
    d.text((17 * PX, 202 * PX), 'EGRLab | P00-R1-review | SCH P00-R1 + PCB R1 | 25.09.2026', fill=(87, 103, 114), font=font(8))
    d.text((268 * PX, 202 * PX), f'{n} / 4', fill=(87, 103, 114), font=font(8))
    return d


def scale_bar(d):
    y = OY + BH + 12
    d.line([P2(0, y - OY)[0], y * PX, P2(100, y - OY)[0], y * PX], fill='black', width=5)
    for x in (0, 100):
        d.line([P2(x, 0)[0], (y - 2) * PX, P2(x, 0)[0], (y + 2) * PX], fill='black', width=5)
    d.text((P2(0, 0)[0], (y + 3) * PX), 'Belka kontrolna: dokładnie 100 mm. Obrys PCB: 115 × 70 mm.', fill='black', font=font(9))


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


chk = json.loads((P / 'verification/pcb-checks.json').read_text(encoding='utf-8')); neg = json.loads((P / 'verification/negative-controls.json').read_text(encoding='utf-8'))
drc = json.loads((P / 'verification/drc.json').read_text()); sch = json.loads((P / 'verification/schematic-check.json').read_text())
n_ok = sum(c['pass'] for c in chk['checks']); n_neg = sum(r['detected'] for r in neg); det = chk['details']


def dv(prefix):
    return next(v for k, v in det.items() if k.startswith(prefix))


def pl(v, d=1):
    return f'{v:.{d}f}'.replace('.', ',')


dec = dv('Capacitors at their pins'); gnd = dv('GND pours')
pages = []
img = Image.new('RGB', (W, H), 'white')
d = page_frame(img, 1, 'P00 FIXTURE: schemat i PCB R1 do recenzji', 'Przyrząd stanowiskowy do odbioru płytek (nie wchodzi do auta). Recenzja: Astra. Sprzęt: NIE ZBADANO.')
for i, (a, v) in enumerate([('DRC / NIEPOŁĄCZONE / SCHEMAT', f"{len(drc['violations'])} / {len(drc['unconnected_items'])} / {len(drc['schematic_parity'])}"),
                            ('KONTROLE PCB · ERC', f"{n_ok}/{len(chk['checks'])} PASS · {sch['erc_violations']}"), ('PRÓBY UJEMNE', f'{n_neg}/{len(neg)} wykryte')]):
    x = 17 + i * 90; d.rounded_rectangle([x * PX, 30 * PX, (x + 83) * PX, 52 * PX], radius=round(3 * PX), fill=(238, 244, 246))
    d.text(((x + 5) * PX, 33 * PX), a, fill=(87, 103, 114), font=font(8, True)); d.text(((x + 5) * PX, 41 * PX), v, fill=(23, 43, 58), font=font(15, True))
notes(d, 17, 60, [
    'Decyzje użytkownika 25.09: P00 jako następna płytka; wyjścia na listwach 2,54 mm (przewody Dupont); zasilanie 5–15 V z własnym LM2937 3,3 V; dioda LED stanu przy każdym kanale.',
    'Funkcja jak w v6.1: osiem źródeł 3V3/GND przez 1 kΩ (najwyżej 3,3 mA w zwarcie) i heartbeat TLC555 ok. 102 Hz przez 1 kΩ. Dodane: D1 przeciw odwrotnej polaryzacji, LED zasilania, SW9 RUN/STOP heartbeatu (STOP trzyma wyjście w L — zablokowany heartbeat do próby watchdoga).',
    'Pułapka części: przełącznik Würth WS-SLTV ma wspólny styk na ŚRODKOWYM pinie 1, a łączy go ze stykiem po przeciwnej stronie suwaka. Symbol przenumerowany; kontrola: we wszystkich 9 przełącznikach pin 3 (GND) nad pinem 2 (3V3), więc suwak w górę = H, jak na nadruku.',
    f"Layout: 115 × 70 mm, 2 × 35 µm, M3 w narożnikach. Kolumny kanałów co 11 mm prowadzone ręcznie i zablokowane, 3V3 szyną B.Cu pod przełącznikami, blok 555 — Freerouting. Masa: wylewki (B.Cu {pl(gnd['filled_percent']['B.Cu'])} %, F.Cu {pl(gnd['filled_percent']['F.Cu'])} %).",
    f"Kondensatory przy pinach: LM2937 ≤ {pl(max(dec['C5.1-U2.1'], dec['C6.1-U2.3'], dec['C7.1-U2.3']))} mm, TLC555 ≤ {pl(max(dec['C3.1-U1.8'], dec['C2.1-U1.5']))} mm."], pt=9.5, width=150)
raw = Image.open(P / 'output/previews/render-top.png'); render = Image.new('RGB', raw.size, 'white')
render.paste(raw.convert('RGB'), mask=raw.getchannel('A') if 'A' in raw.getbands() else None)  # kicad-cli render: transparent background
render = render.crop(render.convert('L').point(lambda v: 255 if v < 250 else 0).getbbox())
rw = 105; rh = rw * render.height / render.width; render = render.resize((round(rw * PX), round(rh * PX)))
img.paste(render, (round(178 * PX), round(60 * PX)))
notes(d, 178, 60 + rh + 4, ['Render 3D (modele z biblioteki KiCad; przełączniki Würth bez modelu). Przymiarka i odbiór (ODBIOR P00: 102 Hz, 3,3 V, 8 kanałów): NIE ZBADANO.'], pt=9, width=100)
pages.append(img)
for n, kind, title, sub, lines in [
    (2, 'assembly', 'Montaż 1:1', 'Strona elementów. Druk 100 %, bez dopasowania do strony. Szare oznaczenia: warstwa Fab (nie drukowana).',
     ['Zmierz belkę 100 mm i obrys przed przykładaniem części.',
      'Kolumna kanału n: LEDn (u góry), RLn (lewy), SWn (środek), RSn (prawy), Jn (dół). RLn i RSn to oba 1 kΩ.',
      'SW1–SW9 Würth 450301014042: przed montażem sprawdź omomierzem jeden egzemplarz — suwak w górę ma łączyć środkowy pin z DOLNYM.',
      'LED: płaska strona = katoda. Kanały zielone, HB żółta, zasilanie czerwona.',
      'U1 TLC555CP w podstawce DIP8 (wycięcie = pin 1); wkładać po sprawdzeniu 3,3 V. U2 LM2937ET-3.3: gruba linia = strona taba.',
      'D1 1N5819: pasek = katoda (od strony U2). C4, C6: plus na nadruku.',
      'J10: przewody wchodzą od lewej krawędzi; 1 = +VIN (dół), 2 = GND (góra).']),
    (3, 'front', 'Miedź F.Cu 1:1', 'Widok od strony elementów.',
     ['Zasilanie 1 mm: J10 → D1 → C4/C5 → U2 → C6/C7 → LED zasilania, zablokowane przed autorouterem.',
      'W każdej kolumnie: COM przełącznika → ścieżka pod korpusami RLn i RSn; RLn → anoda LED; RSn → pin sygnałowy Jn.',
      '3V3 do przełączników: zjazd między kanałami 4 i 5 do jednej przelotki, dalej szyna B.Cu.',
      'To widok kontrolny, nie maska do trawienia.']),
    (4, 'back', 'Miedź B.Cu 1:1', 'Widok przez PCB od strony elementów, bez odbicia lustrzanego.',
     ['Szyna 3V3 0,8 mm pod rzędem przełączników (pin 2 SW1–SW9).',
      'Pozostałe ścieżki B.Cu: RESET i zasilanie bloku 555 (Freerouting). Reszta to wylewka GND.'])]:
    img = plot(kind); d = page_frame(img, n, title, sub); scale_bar(d); notes(d, 150, 38, lines, pt=9.5, width=128); pages.append(img)
out = P / 'output/pdf/P00-R1-PCB.pdf'; out.parent.mkdir(parents=True, exist_ok=True)
pages[0].save(out, 'PDF', resolution=DPI, save_all=True, append_images=pages[1:])
for n, name in [(1, 'assembly'), (2, 'copper-front'), (3, 'copper-back')]:
    crop = pages[n].crop((round(OX * PX) - 20, round(OY * PX) - 20, round((OX + BW) * PX) + 20, round((OY + BH) * PX) + 20))
    crop.resize((crop.width // 4, crop.height // 4), Image.LANCZOS).save(P / f'output/previews/{name}.png')
for n, pg in enumerate(pages, 1):
    pg.resize((pg.width // 5, pg.height // 5), Image.LANCZOS).save(P / f'output/previews/pdf-{n}.png')
print(out, 'pages', len(pages))
