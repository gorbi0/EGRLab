"""P05 R1 review document: 4 A4 landscape pages, CAD plots rasterised at 600 dpi in exact physical size.
Generator taken over from P02 R1 / P01 PCB-R2 (the board sits 20 mm from the left and 35 mm from the top edge,
not at the paper corner where printers clip). Print at 100 %. The assembly page also shows the F.Fab
references and the actual footprint outlines.
Run with KiCad Python (pcbnew + PIL). Output: output/pdf/P05-R2-PCB.pdf, output/previews/*.png
"""
from pathlib import Path
import pcbnew as p, math, json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
P = Path(__file__).resolve().parents[1]; b = p.LoadBoard(str(P / 'eda/P05.kicad_pcb')); BW, BH = 160, 120
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
            if f.Reference().GetLayer()==p.B_SilkS and f.Reference().IsVisible():
                t=p.PCB_TEXT(f.Reference());t.SetLayer(p.F_SilkS);t.SetMirrored(False)
                text(d,t,(40,40,160),p.F_SilkS)
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
    d.text((17 * PX, 202 * PX), 'EGRLab | P05-R2-review | SCH P05-R2 + PCB R2 | 29.09.2026', fill=(87, 103, 114), font=font(8))
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
pages=[]
img=Image.new('RGB',(W,H),'white');d=page_frame(img,1,'P05 DAQ — schemat i PCB R2','AD7606B / 8 kanałów / przekaźniki odczepów / AUX. Projekt do recenzji. Sprzęt: NIE ZBADANO.')
stats=[('ERC / NETLISTA',f"{sch['erc_violations']} / {sch['pin_checks']} pinów"),('DRC / BRAKI / PARITY','0 / 0 / 0'),('MUTACJE WYKRYTE',f"{len(ele['negative_controls'])} elektrycznych + {len(pcb['negative_controls'])} PCB")]
for i,(label,value) in enumerate(stats):
 x=17+i*90;d.rounded_rectangle([x*PX,30*PX,(x+83)*PX,52*PX],radius=round(3*PX),fill=(238,244,246))
 d.text(((x+5)*PX,33*PX),label,fill=(87,103,114),font=font(8,True));d.text(((x+5)*PX,41*PX),value,fill=(23,43,58),font=font(14,True))
notes(d,17,61,[
 'P05 mierzy napięcia. Prąd silnika pozostaje osobnym pomiarem MCP3201 na P06/P07. CH6 ADC jest terminacją zera.',
 '5V_SYS → filtr 1 Ω / 470 µF → AVCC. Lokalny MCP1700 tworzy 3V3_DAQ dla VDRIVE i logiki. LV05.3 / 3V3_IO kończy się na TP5.',
 'Bufory Ioff na wejściach i DOUT/BUSY; MISO włączane tylko przez aktywny CS. Sprzętowe MEAS_EN & DAQ_OK steruje cewkami.',
 'Okno nominalne AVCC: 4,826–5,165 V. DAQ_OK potwierdza napięcia, nie inicjalizację ani kalibrację ADC.',
 'Nowy warunek integracji: po pierwszym pełnym resecie ADC odczekać 2100 ms. Po zaniku P05 wymagana ponowna inicjalizacja i ręczny restart sesji do wdrożenia obsługi brownoutu.',
 'Przed produkcją: niezależna recenzja, fizyczna przymiarka B2B/SW1 i kwalifikacja C12/C13 pod napięciem. Gerbery nie zostały wydane. P07 nadal HOLD.'],pt=9.5,width=150)
raw=Image.open(P/'output/previews/render-top.png');render=Image.new('RGB',raw.size,'white');render.paste(raw.convert('RGB'),mask=raw.getchannel('A') if 'A' in raw.getbands() else None)
bb=render.convert('L').point(lambda v:255 if v<250 else 0).getbbox();render=render.crop(bb)
rw=100;rh=rw*render.height/render.width;render=render.resize((round(rw*PX),round(rh*PX)));img.paste(render,(round(180*PX),round(61*PX)))
notes(d,180,65+rh,['Render poglądowy; własne footprinty mogą nie mieć korpusów 3D. Miarodajny jest projekt i rysunek 1:1.','Osiem arkuszy A3 schematu w osobnym PDF. KiCad: eda/P05.kicad_pro. Formularz prób: docs/ODBIOR.md.'],pt=9,width=99)
pages.append(img)
for n,kind,title,sub,lines in [
 (2,'assembly','Montaż 1:1 — strona elementów','Druk 100%, bez dopasowania. Przyłożyć rzeczywiste części przed zamówieniem PCB.',[
 'PCB 160 × 120 mm, 4 otwory M3. U1 LQFP64 i U3 VSSOP8 lutowane bezpośrednio; bufory SO14 również bez adapterów. Niebieskie C27–C34: napisy na odwrocie PCB, tu pokazane w widoku montażowym.',
 'C1: EEUFR1C471, Ø8 × 11,5 mm, raster 3,5 mm. U12: 1 GND, 2 VIN, 3 VOUT. U6/U7: 1 RESET, 2 VDD, 3 GND.',
 'K1–K3: G6K-2P-Y DC5, THT. SW1: 7201SYCBE, terminale C do PCB. HI 2–1/5–4; LO 2–3/5–6.',
 'J1 B2B: obok P03, bez kabla. Logiczny pin 1 w kolumnie dalej od krawędzi. Przymiarka i test wszystkich kontaktów według MECHANIKA.md są obowiązkowe przed wydaniem PCB.',
 'J2 LV05 200 mm, J3 DAQOK 150 mm, J4 TAPS 50 mm, J5 VSENSE 150 mm, J6 AUX 50 mm. Końce PTH lutowane, kotwy 11,5–15 mm od rzędów.']),
 (3,'front','Miedź F.Cu 1:1','Widok z góry, bez odbicia. Szare pola = GND.',[
 'Dwie warstwy 35 µm; FR4 1,6 mm. Prześwit min. 0,15 mm, domyślna ścieżka 0,20 mm. Via 0,60 / 0,30 mm.',
 'Wejścia, REGCAP i referencja mają zaplanowane ścieżki po stronie elementów. ADC ma dedykowane powroty do GND.',
 'C12/C13: efektywnie co najmniej 10 µF przy napięciu pracy. Wybrane 22 µF / 25 V / 1210 wymagają kwalifikacji DC-bias.',
 'SMD GND ma połączenia pełne tam, gdzie termiki nie mieszczą się przy rastrze wyprowadzeń. Złącza i wiązki mają termiki.',
 'TAPS wymaga 300k/100k przy źródłach w adapterach; nie podłączać surowego motoru bez tych rezystorów.']),
 (4,'back','Miedź B.Cu 1:1 — prześwietlenie','Widok z góry przez laminat; nie jest lustrzanym szablonem trawienia.',[
 'Pod rdzeniem ADC, końcowym rozprowadzeniem wejść i referencją zakaz ścieżek B.Cu. Odcinki przekaźnik–filtr mogą korzystać z B.Cu powyżej y=35,5 mm. Pola GND łączą przelotki.',
 'Pod kotwami i podkładkami M3 obie strony bez miedzi. Nie dociskać przewodów do odkrytej ścieżki.',
 'Kontrola natywna KiCad obejmuje DRC, brak niepołączonych sieci i zgodność PCB ze schematem. Hash źródeł jest w drc.provenance.json.',
 'Uruchamianie: najpierw napięcia i READY, potem SPI, przekaźniki, wzorce napięcia, kalibracja i test temperatury. Bez ECU oraz silnika.',
 '1 MHz SPI i do 2 kSPS na początek. 10 kSPS wymaga szybszego SPI i pomiaru przepustowości całego firmware. DRC nie sprawdza szumu ani aliasingu.'])]:
 img=plot(kind);d=page_frame(img,n,title,sub);scale_bar(d);notes(d,187,35,lines,pt=9,width=94);pages.append(img)
out=P/'output/previews';out.mkdir(exist_ok=True,parents=True)
for i,img in enumerate(pages,1):
 img.save(out/f'pcb-page-{i}.png');img.resize((1782,1260)).save(out/f'pcb-preview-{i}.png')
docpy=os.environ.get('EGRLAB_DOC_PYTHON',sys.executable)
subprocess.run([docpy,str(P/'src/wrap_pdf.py'),str(out),str(P/'output/pdf/P05-R2-PCB.pdf')],check=True)
print('Four PCB PDF pages generated.')
