"""Review PDF of the P12 R1 PCB: native KiCad plots at 1:1 (A4 landscape), no redrawn copper (P10 R2 pattern), plus a geometry page
(side view of the ribbon between an angled IDC on a stack board and the straight IDC on P12, row order) drawn from the numbers in
docs/GEOMETRIA.csv. Pages: 1 overview, 2 assembly 1:1 (view from the stack), 3 F.Cu, 4 B.Cu (seen from wall A), 5 geometry.
"""
from pathlib import Path
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
import json, hashlib, sys, xml.etree.ElementTree as ET
P = Path(__file__).resolve().parents[1]; O = P / 'output'
sys.path.insert(0, str(P / 'src'))
from board import NAME, REV, W, H, HOLES_XZ
checks = json.loads((P / 'verification/pcb-checks.json').read_text(encoding='utf-8')); assert checks['passed'] == checks['total']
assert checks['board_sha256'] == hashlib.sha256((P / f'eda/{NAME}.kicad_pcb').read_bytes()).hexdigest()
neg = json.loads((P / 'verification/negative-controls.json').read_text(encoding='utf-8'))
drc = json.loads((P / 'verification/drc.json').read_text(encoding='utf-8'))
el = json.loads((P / 'verification/electrical-checks.json').read_text(encoding='utf-8'))
K = json.loads((P / 'docs/kontrakt-P12.json').read_text(encoding='utf-8'))
geo = next(v for k, v in checks['details'].items() if k.startswith('Connector centres'))
gnd = next(v for k, v in checks['details'].items() if k.startswith('GND pours'))
pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf')); pdfmetrics.registerFont(TTFont('Bold', 'C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Bold', italic='Arial', boldItalic='Bold')
(O / 'pdf').mkdir(parents=True, exist_ok=True)
PDF = O / f"pdf/{REV.replace(' ', '-')}-PCB.pdf"
c = Canvas(str(PDF), pagesize=(297 * mm, 210 * mm)); c.setTitle(f'EGRLab {REV}: plytka polaczen krawedzi A (LOGGER)')
style = ParagraphStyle('body', fontName='Arial', fontSize=9, leading=12, textColor=HexColor('#172833'))
NPAGES = 5


def para(t, x, y, w):
    z = Paragraph(t, style); _, h = z.wrap(w * mm, 190 * mm); z.drawOn(c, x * mm, y * mm - h); return y - h / mm - 3


def start(n, title, subtitle):
    c.setFillColor(HexColor('#117e86')); c.rect(0, 204 * mm, 297 * mm, 6 * mm, fill=1, stroke=0)
    c.setFillColor(HexColor('#172833')); c.setFont('Bold', 17); c.drawString(12 * mm, 191 * mm, title)
    c.setFont('Arial', 9); c.drawString(12 * mm, 184 * mm, subtitle)
    c.setStrokeColor(HexColor('#cdd7dc')); c.line(12 * mm, 14 * mm, 285 * mm, 14 * mm)
    c.setFont('Arial', 8); c.drawString(12 * mm, 9 * mm, f'{REV} S1 LOGGER | 04.10.2026 | PCB do zamowienia | sprzet (przymiarka tasm, odbior): NIE ZBADANO')
    c.drawRightString(285 * mm, 9 * mm, f'{n} / {NPAGES}')


def board(name, x=12, y=60):
    svg = ET.parse(O / 'svg' / (name + '.svg')).getroot(); w = float(svg.attrib['width'].removesuffix('mm')); h = float(svg.attrib['height'].removesuffix('mm'))
    assert abs(w - W) < .3 and abs(h - H) < .3, (name, w, h)
    c.drawImage(str(O / 'previews' / (name + '.png')), x * mm, y * mm, w * mm, h * mm, mask='auto')
    c.setStrokeColor(HexColor('#000000')); c.setLineWidth(1.2); c.line(x * mm, (y - 10) * mm, (x + 100) * mm, (y - 10) * mm)
    for xx in (x, x + 100):
        c.line(xx * mm, (y - 13) * mm, xx * mm, (y - 7) * mm)
    c.setFont('Arial', 8.5); c.drawString(x * mm, (y - 17) * mm, 'Belka 100 mm. Drukowac 100 %, bez dopasowania do strony; zmierzyc belke przed przymiarka.')


npass = sum(x['detected'] for x in neg); nel = sum(t['ok'] for t in el['negative_controls'])
start(1, f'{REV} — plytka polaczen krawedzi A (wariant LOGGER)', 'Format S1: P12 stoi pionowo przed krawedzia A stosu, strona zlaczy do stosu. Schemat: P12-R1-schemat.pdf.')
y = 174
for t in [f'<b>Plytka:</b> {W:g} × {H:g} mm (x 0…160 jak stos, z 4…96 nad dnem obudowy), FR4 1,6 mm, 2 × 35 µm, narozniki R1; {len(HOLES_XZ)} otworow M3 '
          '(NPTH 3,2, strefy Ø7 bez miedzi): 4 w rogach i 2 miedzy slotami. Elementy: 10 prostych obudowanych gniazd IDC i 4 pola pomiarowe — bez elementow aktywnych.',
          '<b>Zlacza:</b> jedno proste IDC na kazde zlacze krawedzi A plytek LOGGER (P02 J_BP; P03 J_BP1/2/3; P05 J_BP1/2; P09 J1; P06 J_BP; P10 J1) w x zlacza na stosie '
          'i z = spod plytki + 1,6 + 4,45 mm (os katowego IDC); J10 dla tasmy z P11 (panel) nisko przy lewej krawedzi. Pin 1 od mniejszego x, rzad nieparzysty nizej '
          '(strona 5). Polozenia zmierzone na plytce: blad maks. ' + str(max(v['error_mm'] for v in geo.values())).replace('.', ',') + ' mm.',
          f'<b>Sieci:</b> {sum(1 for s, k in K["sieci"].items() if len(k) > 1)} sieci laczonych wylacznie po nazwie (kontrakty z pinoutow plytek); {len(K["niepodlaczone"])} pinow '
          'z sieciami wariantu pelnego (P04 / P07 / P08) bez polaczenia. 5V_SYS sciezkami 1,0 mm, 3V3_IO 0,5 mm, sygnaly 0,3 mm; GND wylewka na obu warstwach '
          f'(F.Cu {str(gnd["cover_percent"]["F.Cu"]).replace(".", ",")} %, B.Cu {str(gnd["cover_percent"]["B.Cu"]).replace(".", ",")} %, {gnd["gnd_vias"]} przelotek GND).',
          f'<b>Kontrole:</b> DRC {len(drc["violations"])} / {len(drc["unconnected_items"])} / {len(drc["schematic_parity"])} (naruszenia / niepolaczone / niezgodnosci ze schematem); '
          f'PCB {checks["passed"]}/{checks["total"]}; proby ujemne PCB {npass}/{len(neg)}; netlista wobec kontraktow {sum(x["pass"] for x in el["checks"])}/{len(el["checks"])}, '
          f'proby ujemne {nel}/{len(el["negative_controls"])} (z zerowymi).',
          '<b>Otwarte:</b> przymiarka tasm (odstep P12 od krawedzi A, gniazda bez odciazki), dlugosc tasmy P11 po layoucie P11 (README).']:
    y = para(t, 12, y, 150)
c.drawImage(str(O / 'previews/isometric.png'), 168 * mm, 30 * mm, 120 * mm, 140 * mm, preserveAspectRatio=True, anchor='c', mask='auto')
para('Render KiCad bez modeli 3D czesci.', 170, 30, 115)
c.showPage()
pages = [(2, 'Montaz — strona zlaczy (widok od stosu, z w gore) — 1:1', 'assembly', [
    '<b>Strona F (gora plytki) jest strona stosu:</b> tu stoja gniazda IDC. Opis przy kazdym zlaczu: oznaczenie, plytka, zlacze, poziom i slot; „1” przy pinie 1.',
    'Klucz (wciecie) obudowy IDC wedlug nadruku footprintu; pin 1 (pole kwadratowe) zawsze od mniejszego x, rzad nieparzysty nizej.',
    'TP1–TP4: pola pomiarowe GND, 5V_SYS, 3V3_IO, GND (stol pomiarowy, przed wlozeniem do obudowy).',
    'Otwory M3: P12 przykrecona dystansami do sciany A (od strony B.Cu); lby srub po stronie zlaczy, poza tasmami.']),
    (3, 'Miedz F.Cu — 1:1', 'copper-front', ['Natywny eksport KiCad po wypelnieniu stref; szare pola to GND. 5V_SYS 1,0 mm, 3V3_IO 0,5 mm.',
                                              'Wydruk kontrolny, nie plik produkcyjny.']),
    (4, 'Miedz B.Cu — 1:1, widok od sciany A', 'copper-back', ['Widok od spodu (lustrzany wzgledem strony 3).'])]
for n, title, name, notes in pages:
    start(n, title, 'Geometria z natywnego pliku PCB; sprawdz belke 100 mm przed przymiarka.'); board(name)
    yy = 176
    for t in notes:
        yy = para(t, 180, yy, 105)
    c.showPage()
# ---- page 5: geometry ----
start(5, 'Geometria: polozenia zlaczy i kolejnosc rzedow (tasma bez skretu)', 'Widok z boku (przekroj y–z) i tabela z docs/GEOMETRIA.csv; skala 1:1.')
S = 1.0; ox, oz = 30, 40   # origin of the side view on the page: y = 0 (edge A) at x = ox + 40 mm; z = 0 at oz


def Y(y):
    return (ox + 40 + y * S) * mm


def Z(z):
    return (oz + z * S) * mm


c.setLineWidth(.6); c.setStrokeColor(HexColor('#172833'))
for z0 in (8.0, 34.6, 56.2, 77.8):
    c.rect(Y(0), Z(z0), 60 * mm, 1.6 * mm)                                     # stack board (edge A at y = 0)
    c.setFillColor(HexColor('#117e86')); c.rect(Y(0), Z(z0 + 1.6), 8.9 * mm, 8.9 * mm, fill=1, stroke=0); c.setFillColor(HexColor('#172833'))
    zp = z0 + 1.6 + 4.45
    for dz in (1.27, -1.27):
        c.circle(Y(1.5), Z(zp + dz), .6 * mm, fill=1 if dz > 0 else 0)   # filled = odd row
    c.setFont('Arial', 6); c.drawString(Y(10), Z(zp + 1), 'katowe IDC: rzad nieparzysty GORA, parzysty DOL (blizej krawedzi)')
    c.setDash(2, 2); c.line(Y(-18), Z(zp), Y(0), Z(zp)); c.setDash()
    c.rect(Y(-16.4), Z(zp - 4.45), 9 * mm, 8.9 * mm)                           # straight IDC on P12
    c.circle(Y(-10), Z(zp - 1.27), .6 * mm, fill=1); c.circle(Y(-10), Z(zp + 1.27), .6 * mm, fill=0)
    c.drawString(Y(-40), Z(zp - 2), 'P12: nieparz. DOL'); c.drawString(Y(-40), Z(zp + 1), f'z osi {str(round(zp, 2)).replace(".", ",")}')
c.rect(Y(-18), Z(4), 1.6 * mm, 92 * mm)                                        # P12
c.setFont('Bold', 7); c.drawString(Y(-20), Z(98), 'P12 (y = -18)'); c.drawString(Y(0), Z(98), 'krawedz A (y = 0)  ->  stos')
c.setFont('Arial', 6); c.drawString(Y(-40), Z(-4), 'kolko pelne = rzad nieparzysty (pin 1, 3, ...), puste = parzysty')
c.drawString(Y(-40), Z(1), 'dno obudowy z = 0; plytki stosu: z = 8,0 / 34,6 / 56,2 / 77,8; os katowego IDC 1,6 + 4,45 mm nad spodem plytki')
yy = 176
rows = '<br/>'.join(f"{r}: {z['plytka']} {z['zlacze']} ({z['typ']}) — x {str(z['x_mm']).replace('.', ',')}, z {str(z['z_osi_mm']).replace('.', ',')}"
                    for r, z in [(z['ref'], z) for z in K['zlacza']])
for t in ['<b>Kolejnosc rzedow.</b> Na plytkach stosu katowe IDC ma rzad parzysty blizej krawedzi A, czyli nizej w otworze wtyku (piny rzedu dalszego musza isc gora), '
          'a pin 1 od mniejszego x. Tasma plaska bez skretu zachowuje x zyl. Gniazdo na P12 patrzy w przeciwna strone (−y), wiec przy tym samym ukladzie styków gniazda '
          'jego rzad nieparzysty wypada NIZEJ. Dlatego na P12: pin 1 od mniejszego x, pin 2 nad pinem 1. Kontrola: verify_pcb.py „Orientation”, proby ujemne conn_turned / rows_swapped.',
          '<b>Tasma:</b> gniazda IDC bez odciazki, tasma wychodzi z gniazd w gore lub w dol i zawija sie miedzy krawedzia A a P12 (gniazda „plecami do siebie”). '
          'Polozenie P12 w osi y (ok. 18–20 mm od krawedzi A) ustalaja dystanse do sciany A — do przymiarki.',
          f'<b>Polozenia (x stosu, z osi):</b><br/>{rows}']:
    yy = para(t, 160, yy, 125)
c.showPage(); c.save(); print(PDF)
