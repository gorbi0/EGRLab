"""P03 R5 review document: 4 A4 landscape pages, CAD plots rasterised at 600 dpi in exact physical size.
Generator taken over from P00/P02 R1 (P01 PCB-R2 origin): the board sits 20 mm from the left and 35 mm from the top edge,
not at the paper corner where printers clip. Print at 100 %. The assembly page also shows F.Fab (module outlines, antenna
end, USB-C, SD pin names); the copper pages outline the copper-free rule areas in red.
Run with KiCad Python (pcbnew + PIL). Output: output/pdf/P03-R5-PCB.pdf, output/previews/*.png
"""
from pathlib import Path
import pcbnew as p, math, json
from PIL import Image, ImageDraw, ImageFont
P = Path(__file__).resolve().parents[1]; b = p.LoadBoard(str(P / 'eda/P03.kicad_pcb')); BW, BH = 160, 120
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


def keepouts(d, col=(200, 0, 0)):
    """Copper-free rule areas (antenna, SD1 stand-offs, LV03 tie); the M3 hole keepouts are left out (obvious)."""
    for z in b.Zones():
        if z.GetIsRuleArea() and not z.GetZoneName().startswith('M3 '):
            o = z.Outline().Outline(0); pts = [mmv(o.CPoint(i)) for i in range(o.PointCount())]
            thick(d, pts + pts[:1], .2, col)


def plot(kind):
    img = Image.new('RGB', (W, H), 'white'); d = ImageDraw.Draw(img)
    if kind == 'assembly':
        for f in b.GetFootprints():
            for g in f.GraphicalItems():
                if isinstance(g, p.PCB_SHAPE) and g.GetLayer() == p.F_Fab:
                    shape(d, g, (150, 150, 150))
                elif isinstance(g, p.PCB_TEXT) and g.GetLayer() == p.F_Fab and f.GetReference() in ('M1', 'SD1'):
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
                poly_set(d, z.GetFilledPolysList(layer), (205, 205, 205))
        for t in b.GetTracks():
            if isinstance(t, p.PCB_VIA) or t.GetLayer() == layer:
                ps = p.SHAPE_POLY_SET(); t.TransformShapeToPolygon(ps, layer, 0, p.FromMM(.005), p.ERROR_INSIDE); poly_set(d, ps, 'black')
        for f in b.GetFootprints():
            for a in f.Pads():
                if a.IsOnLayer(layer):
                    ps = p.SHAPE_POLY_SET(); a.TransformShapeToPolygon(ps, layer, 0, p.FromMM(.005), p.ERROR_INSIDE); poly_set(d, ps, 'black')
        holes(d); keepouts(d)
    edge(d)
    return img


def page_frame(img, n, title, sub):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, round(6 * PX)], fill=(8, 124, 131))
    d.text((17 * PX, 11 * PX), title, fill=(23, 43, 58), font=font(20, True))
    d.text((17 * PX, 21 * PX), sub, fill=(87, 103, 114), font=font(10))
    d.line([17 * PX, 200 * PX, 280 * PX, 200 * PX], fill=(196, 209, 216), width=3)
    d.text((17 * PX, 202 * PX), 'EGRLab | P03-R5-review | SCH P03-R5 + PCB R5 | 28.09.2026', fill=(87, 103, 114), font=font(8))
    d.text((268 * PX, 202 * PX), f'{n} / 4', fill=(87, 103, 114), font=font(8))
    return d


def scale_bar(d):
    y = OY + BH + 8
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


chk = json.loads((P / 'verification/pcb-checks.json').read_text(encoding='utf-8')); neg = json.loads((P / 'verification/negative-controls.json').read_text(encoding='utf-8'))
drc = json.loads((P / 'verification/drc.json').read_text()); sch = json.loads((P / 'verification/schematic-check.json').read_text())
v61 = json.loads((P / 'verification/v61-compare.json').read_text(encoding='utf-8'))
n_ok = sum(c['pass'] for c in chk['checks']); det = chk['details']
defects = [r for r in neg if r['control'] != 'null_control']; n_neg = sum(r['detected'] for r in defects)
null_ok = all(r['detected'] for r in neg if r['control'] == 'null_control')


def dv(prefix):
    return next(v for k, v in det.items() if k.startswith(prefix))


def pl(v, d=1):
    return f'{v:.{d}f}'.replace('.', ',')


dec = dv('100 nF at every IC'); gnd = dv('GND pours'); nvia = sum(isinstance(t, p.PCB_VIA) for t in b.GetTracks())
solid = sorted({f"{f.GetReference()}.{a.GetNumber()}" for f in b.GetFootprints() for a in f.Pads() if a.GetLocalZoneConnection() == p.ZONE_CONNECTION_FULL})
pages = []
img = Image.new('RGB', (W, H), 'white')
d = page_frame(img, 1, 'P03 CORE: schemat i PCB R5 (bufor Schmitta resetu do P04)', 'ESP32-S3 (Waveshare N32R16V), microSD, MCP23017, bufory 74LVC125 i złącza wiązek. R5: U4 LVC1G37; miedź identyczna z R4. Sprzęt: NIE ZBADANO.')
for i, (a, v) in enumerate([('DRC / NIEPOŁĄCZONE / SCHEMAT', f"{len(drc['violations'])} / {len(drc['unconnected_items'])} / {len(drc['schematic_parity'])}"),
                            ('KONTROLE PCB · ERC · v6.1', f"{n_ok}/{len(chk['checks'])} · {sch['erc_violations']} · {v61['v61_pins_checked'] - len(v61['unexpected'])}/{v61['v61_pins_checked']}"),
                            ('PRÓBY UJEMNE', f"{n_neg}/{len(defects)} wykryte" + (' + zerowa' if null_ok else ' / ZEROWA: BŁĄD'))]):
    x = 17 + i * 90; d.rounded_rectangle([x * PX, 30 * PX, (x + 83) * PX, 52 * PX], radius=round(3 * PX), fill=(238, 244, 246))
    d.text(((x + 5) * PX, 33 * PX), a, fill=(87, 103, 114), font=font(8, True)); d.text(((x + 5) * PX, 41 * PX), v, fill=(23, 43, 58), font=font(15, True))
notes(d, 17, 60, [
    'R5: U4 = SN74LVC1G37DBVR (Schmitt + open-drain), bez zmiany padów i miedzi R4. P04-R2.2: R17 = 10 kΩ. U6/R41/C15 z R4 pozostają. Poprawione budżety LOW/upływności; zbocze na końcu taśmy do pomiaru. Geometrię porównuje check_revision.py.',
    'Decyzje użytkownika 25.09: listwy Waveshare co 22,86 mm; P03 i P05 obok siebie, złącze DAQ kątowe przy prawej krawędzi; microSD = Adafruit 4682; format 160 × 120 jak P01/P02; PA0085 w dwóch rzędach po 3 co 15,24 mm; CAN jako IDC 2 × 3 z kluczem na pinie 4.',
    f"Schemat: {v61['v61_pins_checked']} pinów bazowych sprawdzonych; {len(v61['differences'])} jawnych zmian, 0 nieoczekiwanych. R2 dodaje stany domyślne, wspólny reset, blokadę USB i rezystory szeregowe.",
    'M1: USB-C na górnej krawędzi, antena w głąb płytki nad strefą bez miedzi (obie warstwy, +3 mm po bokach, +8 mm za końcem modułu). Karta microSD wysuwa się przy dolnej krawędzi. Złącza wiązek przy krawędziach, rząd sygnałowy do środka płytki; J1 DAQ czołem przy prawej krawędzi między otworami H2 i H5.',
    f"Zachowane moduły i złącza R1; dodatki R2 rozmieszczone z kontrolą obrysów. Prowadzenie Freerouting 2.1 i jawne odcinki krytyczne. 2 × 35 µm, sygnały 0,30/0,25 mm, zasilanie 0,6 mm, 5V_SYS 1,0 mm zablokowane. GND: wylewki F.Cu {pl(gnd['filled_percent']['F.Cu'])} % i B.Cu {pl(gnd['filled_percent']['B.Cu'])} % płytki (największa wyspa {pl(gnd['largest_island_percent']['F.Cu'], 0)} / {pl(gnd['largest_island_percent']['B.Cu'], 0)} % wylewki), zszyte {gnd['stitching_vias']} przelotkami co 8 mm; razem {nvia} przelotek.",
    f"Kondensatory 100 nF ≤ {pl(max(v['straight_mm'] for v in dec.values()))} mm od pinów zasilania (ścieżka ≤ {pl(max(v['routed_mm'] for v in dec.values()))} mm), każdy z przelotką GND obok."], pt=9.5, width=150)
raw = Image.open(P / 'output/previews/render-top.png'); render = Image.new('RGB', raw.size, 'white')
render.paste(raw.convert('RGB'), mask=raw.getchannel('A') if 'A' in raw.getbands() else None)  # kicad-cli render: transparent background
render = render.crop(render.convert('L').point(lambda v: 255 if v < 250 else 0).getbbox())
rw = 105; rh = rw * render.height / render.width; render = render.resize((round(rw * PX), round(rh * PX)))
img.paste(render, (round(178 * PX), round(60 * PX)))
notes(d, 178, 60 + rh + 4, ['Render 3D (modele z biblioteki KiCad; moduły Waveshare i Adafruit, adaptery i złącza IDC bez modeli). Przymiarka 1:1 i odbiór: NIE ZBADANO.'], pt=9, width=100)
pages.append(img)
for n, kind, title, sub, lines in [
    (2, 'assembly', 'Montaż 1:1', 'Strona elementów. Druk 100 %, bez dopasowania do strony. Szare: warstwa Fab (obrysy modułów, nie drukowana).',
     ['Zmierz belkę 100 mm i obrys; przyłóż moduł Waveshare do listew M1 (22,86 mm) i Adafruit 4682 do SD1 przed zamówieniem PCB.',
      'M1: gniazda 2 × 1×22; USB-C do górnej krawędzi. Przed włożeniem odlutuj diodę RGB na GPIO38 (v6.1). 3V3 modułu = 3V3_CORE.',
      'SD1: gniazdo 1×9 + 2 dystanse M2.5; karta do dolnej krawędzi. U4/U5/U6/Q1: SOT23 bezpośrednio na PCB; C12–C15 i R41: 1206.',
      'U11–U14, U21–U23: 74LVC125AD (Nexperia) na adapterach Kamami SO14 (18 × 18 mm, piny z goldpinów; nie do podstawki DIP14). U1 w dwóch podstawkach DIP14 w linii, U2 w DIP16.',
      'U3 TPS3808 na Chip Quik PA0085: numerację 1–6 potwierdź na nadruku adaptera (1 = SUP_RAW_N, 2 = GND, 3/5/6 = 3V3, 4 = CT wolny).',
      'Złącza IDC: usuń pin KEY n i zaślep otwór we wtyku (v6.1). J10 LV03: żyły lutowane, opaska w otworach TIE 12,5 mm od lutów.',
      f"Pady GND z pełnym połączeniem do wylewki ({len(solid)}): dłużej grzać przy lutowaniu."]),
    (3, 'front', 'Miedź F.Cu 1:1', 'Widok od strony elementów. Czerwone obrysy: strefy bez miedzi (antena M1, dystanse SD1, opaska LV03).',
     ['Tor 1 mm: J10.1 → Q1 dren; Q1 źródło → M1.J1-21. U5/Q1 blokują powrót z USB do 5V_SYS. Odgałęzienia 0,6 mm.',
      'Każdy kondensator 100 nF: krótki odcinek 0,6 mm do pinu zasilania układu i przelotka GND tuż obok.',
      f"Przelotki GND 0,8/0,4 mm: siatka 8 mm poza obrysami części i dwie lokalne przy C13/U5; razem {gnd['stitching_vias']}.",
      'Pod anteną M1: brak miedzi na obu warstwach. Pod modułem Waveshare między listwami biegną ścieżki (moduł stoi na gniazdach).',
      'R4 nad J4: SUP_N (B.Cu) → przelotka → U6.2; U6.4 → R41 → przelotka → J4.15 po B.Cu. HW_ARMED_CORE przechodzi pod U6 po B.Cu między dwiema przelotkami. Zasilanie U6/C15 z U12.14 wzdłuż górnej krawędzi adaptera U12.',
      'To widok kontrolny, nie maska do trawienia.']),
    (4, 'back', 'Miedź B.Cu 1:1', 'Widok przez PCB od strony elementów, bez odbicia lustrzanego.',
     [f"Wylewka GND na {pl(gnd['filled_percent']['B.Cu'])} % płytki; największa wyspa to {pl(gnd['largest_island_percent']['B.Cu'], 0)} % wylewki, zszyta z F.Cu {gnd['stitching_vias']} przelotkami.",
      'Długie ścieżki magistrali ADC (M1 → bufory U21/U11 → J1 DAQ) biegną wzdłuż górnej części płytki; v6.1 wymaga odbioru zboczy SCLK/CS/CONVST na P05.',
      'Zmiany warstwy także przez pady THT.'])]:
    img = plot(kind); d = page_frame(img, n, title, sub); scale_bar(d); notes(d, 188, 38, lines, pt=9.5, width=90); pages.append(img)
out = P / 'output/pdf/P03-R5-PCB.pdf'; out.parent.mkdir(parents=True, exist_ok=True)
pages[0].save(out, 'PDF', resolution=DPI, save_all=True, append_images=pages[1:])
for n, name in [(1, 'assembly'), (2, 'copper-front'), (3, 'copper-back')]:
    crop = pages[n].crop((round(OX * PX) - 20, round(OY * PX) - 20, round((OX + BW) * PX) + 20, round((OY + BH) * PX) + 20))
    crop.resize((crop.width // 4, crop.height // 4), Image.LANCZOS).save(P / f'output/previews/{name}.png')
for n, pg in enumerate(pages, 1):
    pg.resize((pg.width // 5, pg.height // 5), Image.LANCZOS).save(P / f'output/previews/pdf-{n}.png')
print(out, 'pages', len(pages))
