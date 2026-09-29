"""P11 R1 review document: 4 A4 landscape pages, CAD plots rasterised at 600 dpi in exact physical size.
Generator taken over from P02 R1 / P01 PCB-R2 (the board sits 20 mm from the left and 35 mm from the top edge,
not at the paper corner where printers clip). Print at 100 %. The assembly page also shows the F.Fab
references and the actual footprint outlines.
Run with KiCad Python (pcbnew + PIL). Output: output/pdf/P11-R1-PCB.pdf, output/previews/*.png
"""
from pathlib import Path
import pcbnew as p, math, json, os, subprocess, sys, re
from PIL import Image, ImageDraw, ImageFont
P = Path(__file__).resolve().parents[1]; b = p.LoadBoard(str(P / 'eda/P11.kicad_pcb')); BW, BH = 160, 110
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
    d.text((17 * PX, 202 * PX), 'EGRLab | P11-R1-review | SCH / PCB P11-R1 | 27.09.2026', fill=(87, 103, 114), font=font(8))
    d.text((268 * PX, 202 * PX), f'{n} / 4', fill=(87, 103, 114), font=font(8))
    return d


def scale_bar(d):
    y = OY + BH + 12
    d.line([P2(0, y - OY)[0], y * PX, P2(100, y - OY)[0], y * PX], fill='black', width=5)
    for x in (0, 100):
        d.line([P2(x, 0)[0], (y - 2) * PX, P2(x, 0)[0], (y + 2) * PX], fill='black', width=5)
    d.text((P2(0, 0)[0], (y + 3) * PX), 'Belka kontrolna: dokładnie 100 mm. Obrys PCB: 160 × 110 mm.', fill='black', font=font(9))


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
pcb=json.loads((P/'verification/pcb-checks.json').read_text());ele=json.loads((P/'verification/electrical-checks.json').read_text())
drc=json.loads((P/'verification/drc.json').read_text())
assert all(x['pass'] for x in pcb['checks']) and all(x['pass'] for x in ele['checks'])
assert not any(drc[k] for k in ['violations','unconnected_items','schematic_parity'])
nvia=sum(isinstance(t,p.PCB_VIA) for t in b.GetTracks());pages=[]
img=Image.new('RGB',(W,H),'white');d=page_frame(img,1,'P11 PANEL / R1','Pasywne połączenia panelu EGRLab. Schemat i PCB do recenzji. Sprzęt: NIE ZBADANO.')
stats=[('NETLISTA',f"{sch['pin_checks']} pinów"),('ERC / DRC / BRAKI','0 / 0 / 0'),('KONTROLE NEGATYWNE',f"{len(ele['negative_controls'])} obwodu + {len(pcb['negative_controls'])} PCB")]
for i,(label,val) in enumerate(stats):
 x=17+i*90;d.rounded_rectangle([x*PX,30*PX,(x+83)*PX,52*PX],radius=round(3*PX),fill=(238,244,246))
 d.text(((x+5)*PX,33*PX),label,fill=(87,103,114),font=font(8,True));d.text(((x+5)*PX,41*PX),val,fill=(23,43,58),font=font(14,True))
end=notes(d,17,60,[
 'P11 łączy trzy porty EGR z TAPS, bocznikiem LOGGER, przyszłym mostkiem TEST i zasilaniem sensora P08. Rozprowadza kluczyk, STOP, ARM, MARK i detektory. Gniazda DT, kontakty i BNC są montowane poza PCB.',
 '160×110 mm, dwie warstwy Cu70 µm, FR4 1,6 mm. Na PCB dwa złącza THT oraz dziewięć lutowanych wiązek z kotwami. Ścieżki mocy3 mm, bez przelotek: LOGGER13,8 mm na żyłę, TEST10,8 mm. Wymagany odbiór cieplny z obciążeniem zastępczym.',
 'J1 Phoenix1755752 MSTB4p pionowy; J7 Molex39-29-9129 Mini-Fit12p Au z kołkami. Wiązki TAPS50 mm i ISERIES150 mm należą do BOM P05 i P06. J9 TMOTOR pozostaje HOLD do zatwierdzenia P07/BTS7960.',
 'PANEL_3V3 z P04-R2.1 ma szeregowy100 Ω. Bez LED i dodatkowych obciążeń na P11. Pełne obciążenie P03/P04 zmniejsza SAFE_N: model przy3,18 V daje2,748 V, a dodatkowe5 µA sink daje2,702 V. Sumę upływności i stan gorący trzeba zmierzyć.',
 'STOP przewodzi około27 µA w stanie zezwolenia. Referencyjne styki EAO low-level mają odpowiednią rolę; zwykłe styki srebrne lub samo oznaczenie Au nie potwierdzają pracy przy tak małym obciążeniu. Numery zacisków X na schemacie są funkcjonalne.',
 'DT nie ma wbudowanego detektora. Własny popychacz musi otworzyć oba NC LOGGER przed pierwszym kontaktem elektrycznym DT. TEST_NO zamyka po osadzeniu. Sekwencję sprawdzić oscyloskopem z P04. Brak zwory LOOP_OUT-MECH_OK na P11.',
 'TAPy są wspólne dla trzech portów: wolno podłączyć jeden adapter naraz. Zalecana przesłona odsłaniająca jeden port. Rezystory odczepów pozostają przy EGR w adapterze. AGND_SENSOR nie łączy się z GND panelu.',
 'Źródła, BOM, każda żyła, obliczenia i formularz odbioru w pakiecie. Kontrole netlisty i PCB nie zastępują przymiarki ani badania mechaniki. Nie zmieniono wcześniejszych płytek ani firmware. Gerbery po recenzji i przymiarce.'
],pt=10,width=263);assert end<197,end;pages.append(img)
data=[
 (2,'assembly','Montaż 1:1 / strona elementów','Druk 100%, bez dopasowania. Wiązki wychodzą przez kotwy; nie obciążać lutów.',[
 'M3:(5,5),(155,5),(5,105),(155,105) mm. Dystanse≥10 mm; podkładki OD≤8 mm.',
 'DTtail J2/J3/J8: górny rząd7–12, dolny1–6. Pole1 kwadratowe. To nie jest układ pinów IDC.',
 'J4:1–4 /5–8; J5:1–5 /6–10; J11:1–10 /11–20. J1 i J9 od lewej. Czytać numery każdej końcówki z lista-przewodow.csv.',
 'J1 MSTB4p12A; J7 Mini-Fit12p Au z kołkami. Przymierzyć realny wtyk i miejsce na zatrzask przed zamówieniem PCB.',
 'Kotwy10,5–14,7 mm od rzędów. J9 kotwa12 mm po drugiej stronie. Opaska2,5 mm i łuk na izolacji. Nie lutować do pól SMD.',
 'STOP, kluczyk, przyciski i porty DT poza PCB. Dobór panelu i popychaczy wymaga realnych części; footprinty PCB pozostają stałe.'
 ]),
 (3,'front','Miedź F.Cu 1:1','Widok z góry. Szare pola GND; cztery szerokie tory mocy na tej warstwie.',[
 'Ścieżki sygnałowe≥0,30 mm; odstęp≥0,25 mm. Cztery tory silnika3 mm/70 µm, bez przelotek i przewężeń ścieżek.',
 'LOGGER: J2.1/2 do J1.1/2. TEST: J8.1/2 do J9.1/2. Brak wspólnego węzła mocy ECU i TEST.',
 'AGND_SENSOR J10.2-J8.4 to osobny powrót przełączany na P08. Wylewka GND nie może go zwierać.',
 'Tory3 mm mają około0,9–1,15 mΩ na żyłę w20°C. Liczby nie obejmują PTH, lutów ani kontaktów.',
 'Próba2/5/10 A na obciążeniu zastępczym, nie na EGR. CelΔT≤25 K i temperatura≤70°C. Ustalić limit całej wiązki.',
 'Nie wykonywać wtyku TMOTOR przed P07. P11 można testować bez mostka; nie zastępuje jego zabezpieczeń.'
 ]),
 (4,'back','Miedź B.Cu 1:1 / prześwietlenie','Widok z góry przez laminat, bez odbicia lustrzanego.',[
 f'{nvia} przelotek. GND połączone między warstwami; keepouty pod opaskami i mocowaniem. Sygnały prowadzone w obu warstwach.',
 'Pętla: KEY -> L1 NC_A -> L2 NC_A -> AT pin10 -> mostek przy EGR -> AT pin11 -> MECH_OK.',
 'Osobny tor NC_B daje LOGGER_CLEAR. Brak programowego obejścia pętli; testy obejmują64 kombinacje stanów i przerwy żył.',
 'Zamiana adaptera przy STOP, kluczyku poza TEST i zatrzymanym silniku. Po rozbrojeniu ponownie ARM.',
 'SCOPE do oscyloskopu1 MΩ. Ekran=GND, gniazdo izolowane od blachy. Brak terminacji50 Ω.',
 'Przed integracją: stan gorący, SAFE_N, pełny skok popychaczy, obciążenia i przesłuchy TAP. Formularz ODBIOR pozostaje niewypełniony.'
 ])]
for n,kind,title,sub,lines in data:
 img=plot(kind);d=page_frame(img,n,title,sub);scale_bar(d);end=notes(d,190,35,lines,pt=9,width=90);assert end<197,(n,end);pages.append(img)
out=P/'output/previews';out.mkdir(exist_ok=True,parents=True)
for i,img in enumerate(pages,1):img.save(out/f'pcb-page-{i}.png');img.resize((1782,1260)).save(out/f'pcb-preview-{i}.png')
docpy=os.environ.get('EGRLAB_DOC_PYTHON',sys.executable)
subprocess.run([docpy,str(P/'src/wrap_pdf.py'),str(out),str(P/'output/pdf/P11-R1-PCB.pdf')],check=True)
print('Four P11 PCB PDF pages generated.')
