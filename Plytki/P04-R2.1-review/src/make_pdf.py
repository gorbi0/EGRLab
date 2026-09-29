"""P04 R2 review document: 4 A4 landscape pages, CAD plots rasterised at 600 dpi in exact physical size.
Generator taken over from P02 R1 / P01 PCB-R2 (the board sits 20 mm from the left and 35 mm from the top edge,
not at the paper corner where printers clip). Print at 100 %. The assembly page also shows the F.Fab
references and the actual footprint outlines.
Run with KiCad Python (pcbnew + PIL). Output: output/pdf/P04-R2-PCB.pdf, output/previews/*.png
"""
from pathlib import Path
import pcbnew as p, math, json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
P = Path(__file__).resolve().parents[1]; b = p.LoadBoard(str(P / 'eda/P04.kicad_pcb')); BW, BH = 160, 120
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
    d.text((17 * PX, 202 * PX), 'EGRLab | P04-R2-review | SCH P04-R2 + PCB R2 | 26.09.2026', fill=(87, 103, 114), font=font(8))
    d.text((268 * PX, 202 * PX), f'{n} / 4', fill=(87, 103, 114), font=font(8))
    return d


def scale_bar(d):
    y = OY + BH + 12
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

sch=json.loads((P/'verification/schematic-check.json').read_text())
pcb=json.loads((P/'verification/pcb-checks.json').read_text())
ele=json.loads((P/'verification/electrical-checks.json').read_text())
assert all(x['pass'] for x in pcb['checks']) and all(x['pass'] for x in ele['checks'])
stitch=json.loads((P/'routing/stitching.json').read_text())
solid=sorted({f"{f.GetReference()}.{a.GetNumber()}" for f in b.GetFootprints() for a in f.Pads() if a.GetLocalZoneConnection()==p.ZONE_CONNECTION_FULL},key=lambda s:(s[0],int(''.join(c for c in s.split('.')[0] if c.isdigit()) or 0),s))
nvia=sum(isinstance(t,p.PCB_VIA) for t in b.GetTracks())
pages=[]
img=Image.new('RGB',(W,H),'white');d=page_frame(img,1,'P04 SAFE: schemat i PCB R2 do recenzji','R2 (Claude) po recenzji R1 Astry, uwagi R4-01…R4-07. P07 nadal HOLD. Sprzęt: NIE ZBADANO.')
stats=[('ERC / NETLISTA',f"{sch['erc_violations']} / {sch['pin_checks']} pinów"),('DRC / BRAKI / PARITY','0 / 0 / 0'),('MUTACJE WYKRYTE',f"{len(ele['negative_controls'])} logicznych + {len(pcb['negative_controls'])} PCB")]
for i,(label,value) in enumerate(stats):
 x=17+i*90;d.rounded_rectangle([x*PX,30*PX,(x+83)*PX,52*PX],radius=round(3*PX),fill=(238,244,246))
 d.text(((x+5)*PX,33*PX),label,fill=(87,103,114),font=font(8,True));d.text(((x+5)*PX,41*PX),value,fill=(23,43,58),font=font(14,True))
notes(d,17,61,[
 'Zasilanie: 3V3_IO z P02. P04 nie przełącza prądu silnika. SAFE_N ma pojedynczy pull-up przez STOP oraz otwarte kolektory; dwie bramki Schmitta odtwarzają sygnał kasujący zatrzask.',
 'Zmiany R2: U11 MCP100-300DI/TO, próg 2,85–3,00 V (R4-01). SAFE_WD = SAFE_OK & WD_Q z wolnej bramki U7D kasuje zatrzask i obie zgody także przy rozwartym Q1 (R4-02). 3V3 wychodzi na złącza tylko przez R38/R39 1 kΩ (PG) i R40 100 Ω (panel) (R4-03). C18 1 nF C0G i R5 przy U2.11 (R4-04). KEY n przy złączach IDC (R4-05). Wylewki GND zszyte przelotkami (R4-06). R41/R42 1 kΩ w liniach TEST_KEY i MECH_OK przy J8 (R4-07).',
 'Bez zmian względem R1: tranzystory 2N3904BU, filtr ARM 1 kΩ / 1 µF, R1=220 kΩ, C1=1 µF PET między pinami 15 i 14 HC123 (nie do masy).',
 'SENSOR M2.2 ma teraz IDC 6p: 1 permit, 2 klucz, 3 ready, 4 GND, 5/6 NC. Przyszła P08 musi mieć zgodną wiązkę. Numeracja funkcji SAFE do CORE pozostaje bez zmian.',
 f"Kontrole: {len(pcb['checks'])} PCB, {len(ele['checks'])} elektrycznych. Tablice prawdy: {format(ele['truth_table_rows'],',').replace(',',' ')} kombinacji, odczyt bramek z eksportowanej netlisty. Model logiczny nie sprawdza czasu analogowego ani drgań przycisku.",
 'Po zmianie trybu zatrzymującej heartbeat trzeba ponownie nacisnąć ARM. Sam czujnik może otrzymać zgodę bez ręcznego uzbrojenia silnika.',
 'Przed zamówieniem: recenzja + przymiarka złączy i adapterów. Nie wydano Gerberów do produkcji. Dokumenty: MECHANIKA, PROJEKT, ODBIOR oraz DLA-RECENZENTA w docs/.'],pt=9.5,width=150)
raw=Image.open(P/'output/previews/render-top.png');render=Image.new('RGB',raw.size,'white');render.paste(raw.convert('RGB'),mask=raw.getchannel('A') if 'A' in raw.getbands() else None)
bb=render.convert('L').point(lambda v:255 if v<250 else 0).getbbox();render=render.crop(bb)
rw=100;rh=rw*render.height/render.width;render=render.resize((round(rw*PX),round(rh*PX)));img.paste(render,(round(180*PX),round(61*PX)))
notes(d,180,65+rh,['Render poglądowy. Brak części korpusów 3D; adaptery i wiązki trzeba przymierzyć. Kolor LED w bibliotece nie określa zamawianej części.','Schemat ma 6 arkuszy A3 w osobnym PDF. Pełny, edytowalny projekt: eda/P04.kicad_pro.'],pt=9,width=99)
pages.append(img)
for n,kind,title,sub,lines in [
 (2,'assembly','Montaż 1:1 — strona elementów','Druk 100%, bez dopasowania. Kontrola rzeczywistych części przed zamówieniem PCB.',[
 'PCB 160 × 120 mm. Wszystkie układy i złącza na górze. Referencje R/U w obrysie korpusu są czytelne przed montażem.',
 'U1: CD74HC123E, DIP16. U2/U3: HC14/HC74. U4–U7: HC08. Podstawki według wycięcia i pinu 1.',
 'U8–U10: SO14 na adapterach 18 × 18 mm, rzędy 15,24 mm. C15–C17 lutować przy układach na adapterach; na płycie bazowej nie ma ich footprintów.',
 'U11 MCP100-300DI/TO: 1 RESET, 2 VDD, 3 GND. Q1–Q3 2N3904BU: 1 E, 2 B, 3 C.',
 'Nowe w R2: R39–R42 przy J7/J8, C18 przy U2, TP14 (SAFE_WD), TP15 (Q1_B). Przeniesione: R4 (nad J8.5), R5 (pod U2), TP8.',
 'J1: LV04 AWG22, 200 mm; J2: SAFE16 AWG28, 150 mm. Luty PTH, opaska na izolacji w kotwie 12–14,54 mm od lutów.',
 'IDC: J3 DRIVE K2, J4 SENSOR K2, J5 DAQOK K4, J6 PSUOK K5; napis KEY n stoi przy złączu w linii z tym pinem. Usunąć ten styk męski; zaślepić pozycję żeńską.']),
 (3,'front','Miedź F.Cu 1:1','Widok z góry; bez odbicia lustrzanego. Wylewka szara = GND.',[
 'Dwie warstwy 35 µm, laminat 1,6 mm. Minimalna ścieżka 0,30 mm; prześwit 0,25 mm. Via 0,8 / 0,4 mm.',
 'R1/C1 bezpośrednio obok U1. Ścieżki WD_RC i WD_C zablokowane, F.Cu, bez przelotek.',
 'C4–C14: odległość pad VDD – pad kondensatora do 8 mm. C15–C17 dodatkowo na adapterach.',
 f"J1/J2 i złącza zachowują termiki GND; pod rzędem GND J2 pas bez ścieżek i przelotek (wylewka dochodzi do każdego padu). Pełne połączenie z masą po kontroli wylewek ({len(solid)}): {', '.join(solid)}; dłużej grzać przy lutowaniu.",
 'Pod opaskami i podkładkami M3 brak ścieżek, przelotek i wylewek na obu stronach.']),
 (4,'back','Miedź B.Cu 1:1 — prześwietlenie','Widok z góry przez laminat; NIE jest to lustrzany szablon trawienia.',[
 f"B.Cu i F.Cu wypełnione GND; wyspy odłączone usuwane. Zszycie: {stitch['vias']} przelotek GND 0,8 / 0,4 mm w siatce 10 mm poza obrysami części oraz {stitch['rescue_vias']} w kawałkach wylewki zamkniętych ścieżkami (bez nich KiCad by je usunął); razem {nvia} przelotek. Ścieżki uzupełniające: routing/completion-routes.json.",
 'Native DRC sprawdza wszystkie warstwy i zgodność ze schematem. Wynik wiąże się z hashami źródeł w verification/drc.provenance.json.',
 'Odbiór: najpierw 3V3, potem bufory, READY, STOP, ARM i watchdog z P00. Bez samochodu i bez silnika.',
 'Watchdog 50–150 ms przy 3,3 V jest kryterium pomiaru. Wzór 0,45RC dotyczy 5 V. Sprawdzić także pojedynczy impuls po zwolnieniu CLR przy HB stale H.',
 'Próba pojedynczego uszkodzenia (R4-02): TP15 zwarty do GND, zatrzymać heartbeat → HW_ARMED, MOTOR_PERMIT i SENSOR_PERMIT = L, choć SAFE_N zostaje H.',
 'P07 nadal HOLD do pomiarów rzeczywistego BTS7960; ta płytka nie zatwierdza zamiany mostka.'])]:
 img=plot(kind);d=page_frame(img,n,title,sub);scale_bar(d);notes(d,187,35,lines,pt=9,width=94);pages.append(img)
out=P/'output/previews';out.mkdir(exist_ok=True,parents=True)
for i,img in enumerate(pages,1):
 img.save(out/f'pcb-page-{i}.png');img.resize((1782,1260)).save(out/f'pcb-preview-{i}.png')
docpy=os.environ.get('EGRLAB_DOC_PYTHON',sys.executable)
subprocess.run([docpy,str(P/'src/wrap_pdf.py'),str(out),str(P/'output/pdf/P04-R2-PCB.pdf')],check=True)
print('Four PCB PDF pages generated.')


