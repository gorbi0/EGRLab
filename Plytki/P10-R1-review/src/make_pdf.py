"""P10 R1 review document: 4 A4 landscape pages, CAD plots rasterised at 600 dpi in exact physical size.
Generator taken over from P02 R1 / P01 PCB-R2 (the board sits 20 mm from the left and 35 mm from the top edge,
not at the paper corner where printers clip). Print at 100 %. The assembly page also shows the F.Fab
references and the actual footprint outlines.
Run with KiCad Python (pcbnew + PIL). Output: output/pdf/P10-R1-PCB.pdf, output/previews/*.png
"""
from pathlib import Path
import pcbnew as p, math, json, os, subprocess, sys, re
from PIL import Image, ImageDraw, ImageFont
P = Path(__file__).resolve().parents[1]; b = p.LoadBoard(str(P / 'eda/P10.kicad_pcb')); BW, BH = 80, 70
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
    d.text((17 * PX, 202 * PX), 'EGRLab | P10-R1-review | SCH / PCB P10-R1 | 27.09.2026', fill=(87, 103, 114), font=font(8))
    d.text((268 * PX, 202 * PX), f'{n} / 4', fill=(87, 103, 114), font=font(8))
    return d


def scale_bar(d):
    y = OY + BH + 12
    d.line([P2(0, y - OY)[0], y * PX, P2(100, y - OY)[0], y * PX], fill='black', width=5)
    for x in (0, 100):
        d.line([P2(x, 0)[0], (y - 2) * PX, P2(x, 0)[0], (y + 2) * PX], fill='black', width=5)
    d.text((P2(0, 0)[0], (y + 3) * PX), 'Belka kontrolna: dokładnie 100 mm. Obrys PCB: 80 × 70 mm.', fill='black', font=font(9))


def notes(d, x, y, lines, pt=9.5, width=92):
    f = font(pt); lh = pt / 72 * 25.4 * 1.45
    for s in lines:
        s = re.sub(r'(?<=[a-ząćęłńóśźż])(?=\d)', ' ', s)
        s = re.sub(r'(?<=\d)(?=(?:mm|rpm|mA|kbit)\b)', ' ', s)
        s = re.sub(r'\b(PCB|OBD|Nexperia|TI|PIN)(?=\d|[A-Z])', r'\1 ', s)
        s = re.sub(r'(?<=[,;:])(?=[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż])', ' ', s)
        s = s.replace('V,2=', 'V, 2=').replace('GND,3=', 'GND, 3=').replace('V,4=', 'V, 4=')
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
img=Image.new('RGB',(W,H),'white');d=page_frame(img,1,'P10 CAN / R1','Pasywny odbiornik CAN dla EGRLab. Pakiet do recenzji. Sprzęt: NIE ZBADANO.')
stats=[('NETLISTA',f"{sch['pin_checks']} pinów"),('ERC / DRC / BRAKI','0 / 0 / 0'),('KONTROLE NEGATYWNE',f"{len(ele['negative_controls'])} obwodu + {len(pcb['negative_controls'])} PCB")]
for i,(label,value) in enumerate(stats):
 x=17+i*90;d.rounded_rectangle([x*PX,30*PX,(x+83)*PX,52*PX],radius=round(3*PX),fill=(238,244,246))
 d.text(((x+5)*PX,33*PX),label,fill=(87,103,114),font=font(8,True));d.text(((x+5)*PX,41*PX),value,fill=(23,43,58),font=font(14,True))
end=notes(d,17,60,[
 'TCAN1051VDRQ1 ma osobne zasilanie logiki VIO=3,3 V i toru magistrali VCC=5 V. Wariant V jest obowiązkowy. S oraz TXD są połączone na stałe z VIO: nadajnik wyłączony, odbiornik pracuje. Nie ma zwory aktywnego nadawania.',
 'Wyjście RXD prowadzi przez bufor Nexperia74LVC125AD z Ioff i rezystor100 Ω do CORE. Bufor oddziela wyłączoną P10 od podciągania R30 na P03 zasilanej z USB. Test obu kolejności zasilania pozostaje obowiązkowy.',
 'PESD2CAN przy wejściu skrętki: pin1=CAN_L, pin2=CAN_H, pin3=GND. Krótkie ścieżki H/L i lokalna przelotka masy są zablokowane przed trasowaniem. Brak dodatkowej terminacji120 Ω.',
 'W1 LV10:200 mm 4×AWG22 do P02-R3/J10. W2:150 mm taśma6p do P03-R2/J8, IDC2×3 KEY4. W3:300 mm skrętka120 Ω do OBD6/14. Wszystkie wiązki przy P10 lutowane w PTH i odciążone opaską.',
 'OBD4/5/16 i pozostałe piny NC. Masa P10 pochodzi z głównego zasilania urządzenia; wymagane wspólne odniesienie z samochodem. P10 nie ma izolacji galwanicznej. Najpierw podłączyć masę zasilania, potem CAN.',
 'P10 zapisuje obserwowane ramki, nie wysyła zapytań OBD i nie potwierdza ACK. RPM pojawi się tylko z potwierdzonego źródła. TCAN obsługuje szybkie zbocza CAN FD, ale kontroler ESP32-S3 odbiera Classical CAN.',
 'Firmware bazowy:GPIO17/18, listen-only,500 kbit/s do kwalifikacji, RX kolejka128. Potrzebne testy strat i opóźnień przy DAQ/SD/TEMP; obecny czas ramki oznacza obsługę w zadaniu. Wspólnego firmware nie zmieniono.',
 'Dwie warstwy,80×70 mm,FR4 1,6 mm,Cu35 µm. SOIC8,SO14,SOT23,0805 oraz THT DIN0207. Dokumenty źródłowe, BOM i formularz odbioru są w pakiecie. Gerbery po recenzji i przymiarce. P07 nadal HOLD.'
],pt=10,width=263);assert end<197,end
pages.append(img)
for n,kind,title,sub,lines in [
 (2,'assembly','Montaż 1:1 / strona elementów','Druk 100%, bez dopasowania do strony. Wszystkie części na górze.',[
 'PCB80×70 mm. Otwory M3:(5,5),(75,5),(5,65),(75,65) mm. Dystanse≥10 mm, podkładki OD≤8 mm. Brak elementów pod spodem.',
 'U1 SOIC8 obrócony270°: pin1 u góry po prawej. U2 SO14: pin1 lewy górny. D1 SOT23: pin3 GND u góry, dwa dolne piny są liniami CAN. Sprawdzić obrys F.Fab i oznaczenie układu.',
 'J1 od lewej1=5 V,2=GND,3=3,3 V,4=GND. J2 górny rząd1/3/5, dolny2/4/6. Pin4 KEY, piny5/6 NC. CAN_TX na pin1 idzie tylko do TP6.',
 'J3 po prawej kwadratowy pin1=CAN_H do OBD6, po lewej pin2=CAN_L do OBD14. Nie mylić numerów oglądając złącze od strony lutowania. Ciągłość sprawdzić miernikiem.',
 'Najpierw U1/U2/D1 i0805, potem R1/R2, na końcu wiązki. Luty w otworach metalizowanych, łuk odciążający i opaski2,5 mm. Kotwy12 mm, drugi rząd J2:14,54 mm.',
 'Źródła:TI TCAN1051-Q1; Nexperia PESD2CAN i74LVC125A. Pełne adresy i miejsca weryfikacji w docs/ZRODLA.md. Wymiary montażowe nie zależą od gotowych modułów.'
 ]),
 (3,'front','Miedź F.Cu 1:1','Widok od strony elementów; szare pola = GND.',[
 'Ścieżki≥0,30 mm, odstęp≥0,25 mm. P10 jest płytką małego poboru; rezerwa10 mA na5 V i10 mA na3,3 V. Nie podawać12 V na J1.',
 'H/L prowadzone wyłącznie na górze, przez zabezpieczenie D1 bez dodatkowych odgałęzień. Ścieżki H i L każda krótsza niż15 mm. Brak terminatora, dławika i kondensatorów między H/L.',
 'D1 ma lokalną przelotkę GND w odległości<1,5 mm od pinu3. Ochrona TVS dotyczy impulsów; nie zastępuje ochrony zasilania P01 ani badań całego urządzenia.',
 'C1 odsprzęga U1.3 VCC, C2 U1.5 VIO, C3 U2.14 VCC. C4/C5 po4,7 µF przy doprowadzeniu szyn. Połączenia odsprzęgania zablokowane przed trasowaniem.',
 'W3 to krótki odczep magistrali300 mm, skrętka120 Ω2×AWG24, rozplot≤10 mm. Trzymać z dala od PWM i silnika. Ekran, jeśli obecny, izolowany na obu końcach.',
 'P10 nie jest bramką OBD i nie obsługuje innych protokołów samochodu. Do obserwacji wymagane zasilanie obu szyn; sama obecność3,3 V nie potwierdza działania CAN.'
 ]),
 (4,'back','Miedź B.Cu 1:1 / prześwietlenie','Widok z góry przez laminat. Bez odbicia lustrzanego.',[
 f'Łącznie{nvia} przelotek. Wylewki GND tworzą jeden obszar elektryczny między warstwami według niezależnej analizy geometrii. DRC:zero naruszeń i niedokończonych połączeń.',
 'Stanowisko: dwa aktywne węzły CAN, prawidłowe dwa terminatory120 Ω na końcach magistrali. P10 jest trzecim pasywnym węzłem. P10 nie zapewnia ACK generatorowi.',
 'Sprawdzić odbiór znanej sekwencji, brak nadawania przy wymuszaniu CAN_TX, zachowanie przy zaniku5 V, zaniku3,3 V i wyłączeniu P10 przy CORE z USB.',
 'Ioff dotyczy stanu wyłączonego bufora. Przejścia zasilania i brownout wymagają oscyloskopu: monitorować szyny, RX i magistralę, bez pomijania błędnych ramek.',
 'Kwalifikacja logowania: porównać liczbę ramek i znaczniki z interfejsem odniesienia przy pracy SD, DAQ i temperatur. Zapisywać utracone ramki i źródło RPM. Formularz ODBIOR.md pozostaje niewypełniony.',
 'Pakiet jest projektem do niezależnej recenzji. Brak pomiarów EMC, zasilania i CAN na samochodzie. Nie utożsamiać czystego ERC/DRC z potwierdzeniem poprawności fizycznego prototypu.'
 ])]:
 img=plot(kind);d=page_frame(img,n,title,sub);scale_bar(d);end=notes(d,135,35,lines,pt=9,width=145);assert end<197,(n,end);pages.append(img)
out=P/'output/previews';out.mkdir(exist_ok=True,parents=True)
for i,img in enumerate(pages,1):
 img.save(out/f'pcb-page-{i}.png');img.resize((1782,1260)).save(out/f'pcb-preview-{i}.png')
docpy=os.environ.get('EGRLAB_DOC_PYTHON',sys.executable)
subprocess.run([docpy,str(P/'src/wrap_pdf.py'),str(out),str(P/'output/pdf/P10-R1-PCB.pdf')],check=True)
print('Four PCB PDF pages generated.')
