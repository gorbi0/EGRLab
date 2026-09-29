"""P08 R1 review document: 4 A4 landscape pages, CAD plots rasterised at 600 dpi in exact physical size.
Generator taken over from P02 R1 / P01 PCB-R2 (the board sits 20 mm from the left and 35 mm from the top edge,
not at the paper corner where printers clip). Print at 100 %. The assembly page also shows the F.Fab
references and the actual footprint outlines.
Run with KiCad Python (pcbnew + PIL). Output: output/pdf/P08-R1-PCB.pdf, output/previews/*.png
"""
from pathlib import Path
import pcbnew as p, math, json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
P = Path(__file__).resolve().parents[1]; b = p.LoadBoard(str(P / 'eda/P08.kicad_pcb')); BW, BH = 100, 80
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
    d.text((17 * PX, 202 * PX), 'EGRLab | P08-R1-review | SCH / PCB P08-R1 | 27.09.2026', fill=(87, 103, 114), font=font(8))
    d.text((268 * PX, 202 * PX), f'{n} / 4', fill=(87, 103, 114), font=font(8))
    return d


def scale_bar(d):
    y = OY + BH + 12
    d.line([P2(0, y - OY)[0], y * PX, P2(100, y - OY)[0], y * PX], fill='black', width=5)
    for x in (0, 100):
        d.line([P2(x, 0)[0], (y - 2) * PX, P2(x, 0)[0], (y + 2) * PX], fill='black', width=5)
    d.text((P2(0, 0)[0], (y + 3) * PX), 'Belka kontrolna: dokładnie 100 mm. Obrys PCB: 100 × 80 mm.', fill='black', font=font(9))


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
img=Image.new('RGB',(W,H),'white');d=page_frame(img,1,'P08 SENSOR / R1','Zasilanie czujnika położenia EGR w TEST. Pakiet do recenzji. Sprzęt: NIE ZBADANO.')
stats=[('NETLISTA',f"{sch['pin_checks']} pinów"),('ERC / DRC / BRAKI','0 / 0 / 0'),('KONTROLE NEGATYWNE',f"{len(ele['negative_controls'])} obwodu + {len(pcb['negative_controls'])} PCB")]
for i,(label,value) in enumerate(stats):
 x=17+i*90;d.rounded_rectangle([x*PX,30*PX,(x+83)*PX,52*PX],radius=round(3*PX),fill=(238,244,246))
 d.text(((x+5)*PX,33*PX),label,fill=(87,103,114),font=font(8,True));d.text(((x+5)*PX,41*PX),value,fill=(23,43,58),font=font(14,True))
notes(d,17,60,[
 '5V_SYS z P02 → TPS2553 → dwubiegunowy przekaźnik → czujnik EGR przez P11. K1 rozłącza zarówno +5 V, jak i powrót. P08 nie ustala kolejności pinów 5/6 i nie zasila czujnika w LOGGER.',
 'R1 = 232 kΩ ±1%: limit około 117 mA typowo, obliczeniowo około 99–139 mA. Pierwsza identyfikacja nieznanego czujnika nadal wymaga zewnętrznego źródła z limitem 20 mA.',
 'U6/U7 monitorują obie szyny. U8 wymusza wyłączenie TPS przy zaniku 3,3 V, także poza zakresem pracy bramek. Przed pierwszym zezwoleniem i po zaniku zasilania odczekać 750 ms ciągłej gotowości.',
 'SENSOR_OK = poprawne szyny; SENSOR_HEALTHY = poprawne szyny i brak FAULT TPS. READY nie zależy od PERMIT. Żaden z tych sygnałów nie potwierdza napięcia na sensorze ani styków K1.',
 'Przeciążenie ogranicza lokalnie TPS; CORE musi zatrzasnąć błąd i cofnąć PERMIT. Nie łączyć FAULT wprost z EN. P08 nie zawiera sprzętowego zatrzasku przeciążenia.',
 'Wiązki J1–J3 lutowane do PTH, kotwy 12–14,54 mm. SENSOR pasuje do P04-R2.1/J4 (6p KEY2), SFAULT do P03-R2/J6 (6p KEY3), LV08 do P02-R3/J8.',
 'PCB 100 × 80 mm, 2 warstwy, FR4 1,6 mm, Cu 35 µm. Większość części THT; U1 SOT-23-6, U4/U5 SO14, lokalne kondensatory 0805. Biblioteka K1 poprawiona według rysunku Omrona.',
 'Kolejny etap: recenzja, przymiarka 1:1, Gerbery zaakceptowanej wersji i odbiór przy stole. Dotychczasowych płytek nie zmieniono. P07 pozostaje HOLD.'],pt=10,width=263)
pages.append(img)
for n,kind,title,sub,lines in [
 (2,'assembly','Montaż 1:1 / strona elementów','Druk 100%, bez dopasowania. Wszystkie elementy na stronie górnej.',[
 '100 × 80 mm, cztery otwory M3: (5,5), (95,5), (5,75), (95,75) mm. Podkładki do 8 mm; dystanse co najmniej 10 mm.',
 'U1: TPS2553DBVR SOT-23-6. U4/U5: Nexperia 74LVC125AD SO14, Ioff wymagane. U2 DIP18, U3 DIP14, U6–U8 TO92 z bondout D.',
 'K1 G6K-2P-Y DC5: przewlekany, monostabilny. Pin 1 = plus cewki, 8 = minus. Otwory wzdłuż rzędu: 0 / 3,2 / 5,4 / 7,6 mm; drugi rząd 5,08 mm.',
 'J4 TSENSOR: pin 1 zasilanie, pin 2 powrót. Odległość otworów PCB 5,5 mm, mimo 4,2 mm rastra części współpracującej. Przymierzyć realny Molex 39-29-6028.',
 'J1: pola 1–4 od lewej. J2/J3: górny rząd 1/3/5, dolny 2/4/6. Żyły NC izolowane. Pełna numeracja w WIAZKI.md; sprawdzić omomierzem przed podłączeniem.',
 'D1 katodą do 5V_SYS. C10 ma polaryzację. Rezystory DIN0207 pojedyncze, 1%, 0,25 W. TPS2553-1 i G6KU nie są zamiennikami.',
 'Montaż: SOT/SO14 i 0805, następnie niskie THT, DIP, K1, J4, C10, na końcu wiązki i opaski. Referencje rezystorów/DIP są wewnątrz korpusów.']),
 (3,'front','Miedź F.Cu 1:1','Widok od strony elementów, bez odbicia lustrzanego. Szare pola = GND.',[
 'Minimalna ścieżka 0,30 mm, prześwit 0,25 mm. Prąd toru sensora poniżej 0,14 A według obliczenia limitu; rezerwa zasilania płytki 200 mA / 5 V i 15 mA / 3,3 V.',
 'Krótka ścieżka ILIM do R1 jest zablokowana. Kondensatory wejścia i wyjścia TPS blisko nóżek. Lokalne odsprzęganie THT supervisorów mieści się w 6 mm, pozostałej logiki w 5 mm.',
 'AGND_SENSOR jest oddzielną siecią. Nie ma połączenia z wylewką GND. R18 łączy tylko dwie żyły wyjścia; nie może obchodzić styku powrotu K1.',
 'Kotwy taśm mają otwory NPTH 3,2 mm i obszary bez miedzi. Pola wiązek są metalizowane; przewodów nie lutować do padów powierzchniowych.',
 'Montaż termiczny prototypu: nie ogrzewać tej PCB razem z EGR. K1 ma zakres do +70°C; odbiór płytki przewidziano 0–50°C.',
 'U1 może silnie się grzać podczas długiego zwarcia. Odbiór ograniczenia prądu zaczyna się od krótkich impulsów na sztucznym obciążeniu, bez zaworu.']),
 (4,'back','Miedź B.Cu 1:1 / prześwietlenie','Widok z góry przez laminat. Nie jest lustrzanym szablonem do trawienia.',[
 f'Łącznie {nvia} przelotek. Wylewki GND obu warstw są połączone; niezależna analiza geometryczna potwierdza jeden obszar elektryczny. DRC: brak naruszeń, brak niedokończonych połączeń.',
 'Pierwsze uruchomienie: same szyny, PERMIT=0, pomiar TPS_EN i gotowości. Następnie znane obciążenie 1 kΩ / 250 Ω / 100 Ω, pomiar spadków i ograniczenia prądu.',
 'Sprawdzić osobno zanik 5 V, zanik 3,3 V, obie kolejności startu, wymuszony PERMIT przy martwej P08 i przerwanie W2/W3.',
 'Zmierzona szybkość wyłączenia całego TEST zależy też od firmware. K1 z diodą D1 zwalnia wolniej niż goła cewka. Nie przypisywać gotowej płytce katalogowych 3 ms bez pomiaru.',
 'Dodatkowy U8 wymaga 750 ms stabilnej gotowości przed pierwszym włączeniem po starcie. Integrację wspólnego firmware opisano w ZMIANY.md; wcześniejszych plików P03 nie zmieniano.',
 'Formularz verification/ODBIOR.md pozostaje niewypełniony. Recenzja CAD i testy plików nie zastępują przymiarki części i pomiarów gotowego egzemplarza.'])]:
 img=plot(kind);d=page_frame(img,n,title,sub);scale_bar(d);end=notes(d,135,35,lines,pt=9,width=145);assert end<197,(n,end);pages.append(img)
out=P/'output/previews';out.mkdir(exist_ok=True,parents=True)
for i,img in enumerate(pages,1):
 img.save(out/f'pcb-page-{i}.png');img.resize((1782,1260)).save(out/f'pcb-preview-{i}.png')
docpy=os.environ.get('EGRLAB_DOC_PYTHON',sys.executable)
subprocess.run([docpy,str(P/'src/wrap_pdf.py'),str(out),str(P/'output/pdf/P08-R1-PCB.pdf')],check=True)
print('Four PCB PDF pages generated.')
