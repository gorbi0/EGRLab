"""P06 R1 review document: 4 A4 landscape pages, CAD plots rasterised at 600 dpi in exact physical size.
Generator taken over from P02 R1 / P01 PCB-R2 (the board sits 20 mm from the left and 35 mm from the top edge,
not at the paper corner where printers clip). Print at 100 %. The assembly page also shows the F.Fab
references and the actual footprint outlines.
Run with KiCad Python (pcbnew + PIL). Output: output/pdf/P06-R1-PCB.pdf, output/previews/*.png
"""
from pathlib import Path
import pcbnew as p, math, json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
P = Path(__file__).resolve().parents[1]; b = p.LoadBoard(str(P / 'eda/P06.kicad_pcb')); BW, BH = 120, 100
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
    d.text((17 * PX, 202 * PX), 'EGRLab | P06-R1-review | SCH / PCB P06-R1 | 27.09.2026', fill=(87, 103, 114), font=font(8))
    d.text((268 * PX, 202 * PX), f'{n} / 4', fill=(87, 103, 114), font=font(8))
    return d


def scale_bar(d):
    y = OY + BH + 12
    d.line([P2(0, y - OY)[0], y * PX, P2(100, y - OY)[0], y * PX], fill='black', width=5)
    for x in (0, 100):
        d.line([P2(x, 0)[0], (y - 2) * PX, P2(x, 0)[0], (y + 2) * PX], fill='black', width=5)
    d.text((P2(0, 0)[0], (y + 3) * PX), 'Belka kontrolna: dokładnie 100 mm. Obrys PCB: 120 × 100 mm.', fill='black', font=font(9))


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
stitch=json.loads((P/'routing/stitching.json').read_text())
solid=sorted({f"{f.GetReference()}.{a.GetNumber()}" for f in b.GetFootprints() for a in f.Pads() if a.GetLocalZoneConnection()==p.ZONE_CONNECTION_FULL})
nvia=sum(isinstance(t,p.PCB_VIA) for t in b.GetTracks())
pages=[]
img=Image.new('RGB',(W,H),'white');d=page_frame(img,1,'P06 I-LOGGER / R1','Pomiar prądu silnika EGR. Pakiet do recenzji. Odbiór sprzętu: NIE ZBADANO.')
stats=[('NETLISTA',f"{sch['pin_checks']} pinów"),('ERC / DRC / BRAKI','0 / 0 / 0'),('KONTROLE NEGATYWNE',f"{len(ele['negative_controls'])} obwodu + {len(pcb['negative_controls'])} PCB")]
for i,(label,value) in enumerate(stats):
 x=17+i*90;d.rounded_rectangle([x*PX,30*PX,(x+83)*PX,52*PX],radius=round(3*PX),fill=(238,244,246))
 d.text(((x+5)*PX,33*PX),label,fill=(87,103,114),font=font(8,True));d.text(((x+5)*PX,41*PX),value,fill=(23,43,58),font=font(14,True))
notes(d,17,60,[
 'ECU_P1 → bocznik PBV 5 mΩ → EGR_P1. Prąd silnika nie płynie przez masę elektroniki. Zasilanie lokalne: 5 V z P02, LDO 3,3 V na P06. Pin 3V3_IO jest tylko punktem kontrolnym.',
 'Pomiar: 4 przewody Kelvina → INA240A2 → dzielnik 5,1 kΩ / 5,1 kΩ i 470 nF PET → MCP6022 → MCP3201. Wynik przez SPI do P03. Filtr nominalnie 133 Hz; zapis prądu 2 ksps.',
 'Nominalnie: 2048 kodów przy 0 A, 204,8 kodu/A. Kalibracja obowiązkowa. Zakres początkowego odbioru ±6 A; matematyczne ±10 A nie oznacza gwarantowanego zakresu analogowego. Tor mocy przewidziany do próby cieplnej 10 A.',
 'SW1 NKK S6A na panelu: MEASURE pozostawia bocznik w torze; BYPASS zwiera go równolegle. Drugi biegun sygnalizuje położenie. Przełączać przy wyłączonym zapłonie. BYPASS nie daje wiarygodnego pomiaru prądu.',
 'LOGGER_CURRENT_OK oznacza poprawne szyny zasilania i pozycję MEASURE. Nie potwierdza ciągłości bocznika, kalibracji ani poprawności napięcia odniesienia.',
 'Wiązki: lutowane PTH po stronie P06; kotwy 12–14,54 mm od lutu. LV06 do P02, ILOG do P03, ISERIES do przyszłej P11, dwie wiązki do SW1.',
 'Zastosowanie diagnostyczne: trend prądu, tarcie, wzrost obciążenia i korelacja z pozycją/temperaturą. P06 nie rejestruje kształtu impulsów PWM; filtr i niesynchroniczny ADC trzeba uwzględnić w analizie.',
 'Następny krok: recenzja schematu i PCB, przymiarka 1:1, potem eksport Gerberów. P07 pozostaje HOLD.'],pt=10,width=263)
pages.append(img)
for n,kind,title,sub,lines in [
 (2,'assembly','Montaż 1:1 / strona elementów','Druk 100%, bez dopasowania. Wszystkie elementy na górze. SW1 montowany osobno na panelu.',[
 '120 × 100 mm, 2 warstwy, FR4 1,6 mm, miedź 70 µm. Cztery otwory M3: (5,5), (115,5), (5,95), (115,95) mm.',
 'U1 INA240A2: SOIC8. U5/U6 74LVC125AD: SO14. Bez adapterów. Pozostałe układy DIP/TO92. Kondensatory lokalne 0805.',
 'RSH1 PBV: patrząc na opisaną ściankę, od lewej 1 force ECU, 2 sense+, 3 sense−, 4 force EGR. Przymierzyć rzeczywisty egzemplarz; pod korpusem zostawić odstęp od laminatu.',
 'Sprawdzić pin 1 każdego układu, katody D1/D2 i plus C3/C4/C5. TO92 mają różne kolejności pinów; nie zamieniać układów między pozycjami.',
 'R21 39 Ω / 2 W obciąża styk pomocniczy SW1 (około 0,6 W). Nie zakrywać go taśmą. Rezerwa zasilania P06: 180 mA przy 5 V.',
 'J2: numeracja 1/2 oznacza początek rzędów. Dalej 3/4, 5/6, 7/8 od lewej do prawej; pin 2 pusty. Pełny widok wiązki w WIAZKI.md.',
 'Referencje wewnątrz obrysów rezystorów/DIP czytelne przed montażem. TP3 ma linię wskazującą pad. Rysunek F.Fab pokazuje korpusy.']),
 (3,'front','Miedź F.Cu 1:1','Widok z góry; bez odbicia lustrzanego. Szare pole = masa elektroniki.',[
 'Minimalna ścieżka 0,30 mm, prześwit 0,25 mm; via 0,8 / 0,4 mm. Prąd silnika: zablokowane ścieżki 6 mm, bez przelotek w torze siłowym.',
 'Kelvin zaczyna się na wewnętrznych wyprowadzeniach PBV. Po 10 Ω w każdej gałęzi przy INA240. Brak zaciskanego złącza w torze sense.',
 'Otwory mocy J3/J4: 2,4 mm. PBV: zewnętrzne 2,3 mm, wewnętrzne 2,0 mm. Sprawdzić maksymalną przekątną nóżek i przewody przed zamówieniem.',
 'C5 kompensuje MCP1525, poniżej 5 mm od OUT. Odsprzęganie układów: do 5 mm; C9 na wejściu LDO: 6,94 mm od VIN. Nie przenosić kondensatorów na wiązkę.',
 'Pod opaskami i podkładkami M3 nie ma ścieżek ani wylewek. Duże otwory kotew są nie metalizowane.',
 'Montaż: najpierw SOIC i 0805, potem małe THT, układy, elektrolity, bocznik i wiązki. Zachowano termiki GND; lista zamian na pełną miedź w solid-pads.json jest w R1 pusta.']),
 (4,'back','Miedź B.Cu 1:1 / prześwietlenie','Widok z góry przez laminat. To nie jest lustrzany szablon do trawienia.',[
 f'Łącznie {nvia} przelotek; masa zszyta na obu warstwach. Niezależna analiza geometryczna potwierdza jeden połączony obszar GND. DRC: 0 naruszeń, 0 braków, 0 różnic PCB/schemat.',
 'Tor EGR do obejścia biegnie szeroką ścieżką B.Cu. Nie zmniejszać szerokości przy przebudowie płytki. Obie gałęzie motorowe pozostają odseparowane od GND.',
 'Pierwsze uruchomienie: ograniczony prąd zasilacza 5 V, pomiar 5VA/3V3/REF25, logika READY i SPI bez samochodu, następnie znany prąd w obu kierunkach.',
 'Odbiór obejmuje start/zanik każdej szyny, brak zasilania P06 przy działającym CORE, 4,75 V na wejściu, oba stany SW1 oraz zmiany temperatury.',
 'Filtr 133 Hz wymaga sprawdzenia aliasowania przy rzeczywistym PWM. Przy 2 kHz tłumi około 23,6 dB, przy 20 kHz około 43,6 dB. To pomiar trendu.',
 'Pełny formularz: verification/ODBIOR.md. Wyniki testów plików nie zastępują pomiaru spadku napięcia, temperatury i zakłóceń na zmontowanej płytce.'])]:
 img=plot(kind);d=page_frame(img,n,title,sub);scale_bar(d);end=notes(d,150,35,lines,pt=9,width=130);assert end<197,(n,end);pages.append(img)
out=P/'output/previews';out.mkdir(exist_ok=True,parents=True)
for i,img in enumerate(pages,1):
 img.save(out/f'pcb-page-{i}.png');img.resize((1782,1260)).save(out/f'pcb-preview-{i}.png')
docpy=os.environ.get('EGRLAB_DOC_PYTHON',sys.executable)
subprocess.run([docpy,str(P/'src/wrap_pdf.py'),str(out),str(P/'output/pdf/P06-R1-PCB.pdf')],check=True)
print('Four PCB PDF pages generated.')
