"""P09 R1 review document: 4 A4 landscape pages, CAD plots rasterised at 600 dpi in exact physical size.
Generator taken over from P02 R1 / P01 PCB-R2 (the board sits 20 mm from the left and 35 mm from the top edge,
not at the paper corner where printers clip). Print at 100 %. The assembly page also shows the F.Fab
references and the actual footprint outlines.
Run with KiCad Python (pcbnew + PIL). Output: output/pdf/P09-R1-PCB.pdf, output/previews/*.png
"""
from pathlib import Path
import pcbnew as p, math, json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
P = Path(__file__).resolve().parents[1]; b = p.LoadBoard(str(P / 'eda/P09.kicad_pcb')); BW, BH = 100, 100
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
    d.text((17 * PX, 202 * PX), 'EGRLab | P09-R1-review | SCH / PCB P09-R1 | 27.09.2026', fill=(87, 103, 114), font=font(8))
    d.text((268 * PX, 202 * PX), f'{n} / 4', fill=(87, 103, 114), font=font(8))
    return d


def scale_bar(d):
    y = OY + BH + 12
    d.line([P2(0, y - OY)[0], y * PX, P2(100, y - OY)[0], y * PX], fill='black', width=5)
    for x in (0, 100):
        d.line([P2(x, 0)[0], (y - 2) * PX, P2(x, 0)[0], (y + 2) * PX], fill='black', width=5)
    d.text((P2(0, 0)[0], (y + 3) * PX), 'Belka kontrolna: dokładnie 100 mm. Obrys PCB: 100 × 100 mm.', fill='black', font=font(9))


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


sch=json.loads((P/'verification/schematic-check.json').read_text())
pcb=json.loads((P/'verification/pcb-checks.json').read_text())
ele=json.loads((P/'verification/electrical-checks.json').read_text())
drc=json.loads((P/'verification/drc.json').read_text())
assert all(x['pass'] for x in pcb['checks']) and all(x['pass'] for x in ele['checks'])
assert not any(drc[k] for k in ['violations','unconnected_items','schematic_parity'])
nvia=sum(isinstance(t,p.PCB_VIA) for t in b.GetTracks())
pages=[]
img=Image.new('RGB',(W,H),'white');d=page_frame(img,1,'P09 TEMP / R1','Nośnik dwóch kupionych MAX31856 XU. Pakiet do recenzji. Sprzęt: NIE ZBADANO.')
stats=[('NETLISTA',f"{sch['pin_checks']} pinów"),('ERC / DRC / BRAKI','0 / 0 / 0'),('KONTROLE NEGATYWNE',f"{len(ele['negative_controls'])} obwodu + {len(pcb['negative_controls'])} PCB")]
for i,(label,value) in enumerate(stats):
 x=17+i*90;d.rounded_rectangle([x*PX,30*PX,(x+83)*PX,52*PX],radius=round(3*PX),fill=(238,244,246))
 d.text(((x+5)*PX,33*PX),label,fill=(87,103,114),font=font(8,True));d.text(((x+5)*PX,41*PX),value,fill=(23,43,58),font=font(14,True))
notes(d,17,60,[
 'P09 zbiera temperatury dwóch termopar K. Sygnały termopar trafiają bezpośrednio do zacisków kupionych modułów. Nośnik przenosi zasilanie i cyfrowe SPI; pozostaje poza ogrzewaną strefą EGR.',
 'Moduły: oferta Allegro 18805671895. Zdjęcia pokazują VIN / 3Vo / GND / SCK / SDO / SDI / CS / FLT / DRDY oraz napis VIN/Logic: 3.3–5V. Brak schematu regulatora i wymiarowanego rysunku; konieczna kwalifikacja egzemplarzy.',
 'JP1/JP2 początkowo bez zwór. 1–2 wybiera VIN=3,3 V; 2–3 wybiera 5 V wyłącznie po pomiarach. Wyjść 3Vo nie łączyć ze sobą ani z szyną 3V3_IO. Dwa selektory mogą mieć różne ustawienia po kwalifikacji.',
 'U1/U2 mają Ioff. U3 HC139 dopuszcza MISO tylko kanału wybranego pojedynczym CS. Gdy oba CS są HIGH albo oba LOW, oba bufory wyjściowe pozostają Hi-Z w stanie ustalonym. Wymagana przerwa obu CS HIGH co najmniej 1 µs.',
 'W1 LV09: 200 mm AWG22 do P02-R3/J9. W2 TEMP: 100 mm taśma 10-żyłowa do P03-R2/J7, KEY4. Na nośniku luty PTH i kotwy; przy CORE i zasilaczu wtyki. Moduły pozostają w rozłącznych gniazdach.',
 'Firmware: poprawka błędnej mapy rejestrów — temperatura 0x0C–0x0E, status 0x0F. Dołączono diff, pełną kopię bazowego board.c i test 27 przypadków z trzema wykrywanymi regresjami. Pełna kompilacja ESP-IDF pozostaje do integracji.',
 'PCB 100 × 100 mm, dwie warstwy. U1/U2 SO14, C1–C7 0805, U3 DIP16, rezystory DIN0207. Otwory podparcia modułów Ø6 mm służą regulacji nylonowych M2.5; rozstaw listwy i mechanikę sprawdzić przed produkcją.',
 'Kolejny krok: recenzja, przymiarka 1:1 i odbiór modułów. Gerbery powstają po potwierdzeniu mechaniki. P07 nadal HOLD. Formularz verification/ODBIOR.md celowo pozostaje niewypełniony.'],pt=10,width=263)
pages.append(img)
for n,kind,title,sub,lines in [
 (2,'assembly','Montaż 1:1 / strona elementów','Druk 100%, bez dopasowania do strony. Wszystkie części na górze.',[
 'PCB 100 × 100 mm. Cztery otwory M3: (5,5), (95,5), (5,95), (95,95) mm. Podkładki OD do 8 mm, dystanse ≥10 mm.',
 'Moduły wkładamy listwą u góry i terminalem termopary w kierunku dolnej krawędzi. Pin 1 VIN jest po prawej w rzędzie J3/J4, oznaczony kwadratowym polem i VIN 1. Pin 2 = 3Vo, pin 3 = GND.',
 'Gniazda 1×9 / 2,54 mm Au. Nominalne podpory 20,32 mm pomiędzy osiami, 16 mm od listwy. To założenie do przymiarki, nie zweryfikowany rysunek producenta modułu.',
 'Podpory: nylon M2.5, otwory Ø6 mm, podkładki OD8 mm. Regulacja osi maksymalnie ±1,75 mm, ograniczona także podkładką i obrysem. Wysokość dobrać do gniazda, bez wyginania modułu.',
 'JP1/JP2: pin 1 = 3V3_IO, pin 2 = VIN modułu, pin 3 = 5V_SYS. Początkowo OPEN. Jedna zwora na selektor, zmiana tylko bez zasilania.',
 'Najpierw SO14 i 0805, potem rezystory i DIP16, następnie listwy, na końcu wiązki i opaski. Moduły wkładać po sprawdzeniu szyn i ustawieniu wykwalifikowanego VIN.']),
 (3,'front','Miedź F.Cu 1:1','Widok od strony elementów; szare pola = GND.',[
 'Ścieżki co najmniej 0,30 mm, odstęp 0,25 mm, Cu35 µm. Rezerwa poboru nośnika z modułami: 200 mA łącznie na wybranych szynach. Potwierdzić pomiarem i bilansem P02.',
 'C1/C2/C3 blisko zasilania U1/U2/U3. C6/C7 przy VIN modułów. Ścieżki lokalnego odsprzęgania zablokowane przed trasowaniem reszty PCB.',
 'J1: 1–4 od lewej. J2: górny rząd 1/3/5/7/9, dolny 2/4/6/8/10. Piny 1/2 opisane, pełny kontrakt w WIAZKI.md. Żyłę KEY4 zakończyć izolacją, pole4 NC.',
 'Wiązki lutować do PTH. Kotwy opasek 12 mm przed pierwszym rzędem, 14,54 mm przed drugim. Opaska nie może przecinać izolacji; mały łuk przewodów odciąża lut.',
 'U3: Y2→OE1, Y1→OE2. R11/R12 po 100 Ω na osobnych wyjściach. Dekoder nie gwarantuje braku hazardów przy jednoczesnych zboczach; przerwa CS w firmware jest wymagana.',
 'Termopary z izolowaną spoiną pomiarową. Brak izolacji galwanicznej P09. Nie nagrzewać zacisków i elektroniki podczas testu EGR; błędy zimnego końca mogą maskować wynik.']),
 (4,'back','Miedź B.Cu 1:1 / prześwietlenie','Widok z góry przez laminat. Bez odbicia lustrzanego.',[
 f'Łącznie {nvia} przelotek. Wylewki GND tworzą jeden obszar elektryczny między warstwami według niezależnej analizy geometrii. DRC: zero naruszeń i niedokończonych połączeń.',
 'Uruchomienie: nośnik bez modułów, potem pojedynczy moduł kwalifikowany osobno, następnie oba kanały oraz wspólna magistrala z kartą SD. Wyniki wpisać w ODBIOR.md.',
 'SPI mode1, start 1 MHz, CS setup/hold po 2 takty. CR0=0x91, CR1=0x03, początkowo 300 ms oczekiwania. Odczyt co 200 ms wystarcza do temperatury obudowy.',
 'Sprawdzić rozwarcie sondy, brak modułu, zaniki każdej szyny i obie kolejności włączania P03/P09. Ioff chroni stan wyłączony; zachowanie przy brownoucie wymaga oscyloskopu.',
 'FLT/DRDY: TP10/TP12 kanału1, TP11/TP13 kanału2. Wyjścia 3Vo: TP8/TP9. Nie ma dodatkowych żył FLT/DRDY w TEMP; znacznik czasu dotyczy odczytu.',
 'Rozdzielczość 1/128°C nie określa dokładności termopary i jej mocowania. Porównać z termometrem odniesienia. Stała poprawna ramka SPI nie potwierdza świeżej konwersji.'])]:
 img=plot(kind);d=page_frame(img,n,title,sub);scale_bar(d);end=notes(d,135,35,lines,pt=9,width=145);assert end<197,(n,end);pages.append(img)
out=P/'output/previews';out.mkdir(exist_ok=True,parents=True)
for i,img in enumerate(pages,1):
 img.save(out/f'pcb-page-{i}.png');img.resize((1782,1260)).save(out/f'pcb-preview-{i}.png')
docpy=os.environ.get('EGRLAB_DOC_PYTHON',sys.executable)
subprocess.run([docpy,str(P/'src/wrap_pdf.py'),str(out),str(P/'output/pdf/P09-R1-PCB.pdf')],check=True)
print('Four PCB PDF pages generated.')
