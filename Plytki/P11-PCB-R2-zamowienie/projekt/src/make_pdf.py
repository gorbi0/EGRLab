"""Review PDF of the P11 R2 PCB (panel wiring board): native KiCad plots at 1:1 (A4 landscape), no redrawn copper (P10 R2 pattern).
Pages: 1 overview, 2 assembly top, 3 F.Cu, 4 B.Cu (seen from below), 5 fit print 1:1 (outline, courtyards, holes).
Fonts: reportlab with the Arial files named here; in the Docker image egrlab_winpaths maps them to Liberation Sans.
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
from board import NAME, REV, W, H
TYTUL = f'{REV} PANEL'
checks = json.loads((P / 'verification/pcb-checks.json').read_text(encoding='utf-8')); assert checks['passed'] == checks['total']
assert checks['board_sha256'] == hashlib.sha256((P / f'eda/{NAME}.kicad_pcb').read_bytes()).hexdigest()
neg = json.loads((P / 'verification/negative-controls.json').read_text(encoding='utf-8'))
parts = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
drc = json.loads((P / 'verification/drc.json').read_text(encoding='utf-8')); silk = json.loads((P / 'routing/silkscreen.json').read_text(encoding='utf-8'))
det = checks['details']
nlib = sum(1 for v in drc['violations'] if v['type'] == 'lib_footprint_mismatch')
gnd = next(v for k, v in det.items() if k.startswith('GND pours'))
pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf')); pdfmetrics.registerFont(TTFont('Bold', 'C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Bold', italic='Arial', boldItalic='Bold')   # 30.09: <b> in the notes printed as regular without it
(O / 'pdf').mkdir(parents=True, exist_ok=True)
PDF = O / f"pdf/{REV.replace(' ', '-')}-PCB.pdf"
c = Canvas(str(PDF), pagesize=(297 * mm, 210 * mm)); c.setTitle(f'EGRLab {REV}: PCB płytki okablowania panelu')
style = ParagraphStyle('body', fontName='Arial', fontSize=9.5, leading=13, textColor=HexColor('#172833'))
NPAGES = 5


def para(t, x, y, w):
    z = Paragraph(t, style); _, h = z.wrap(w * mm, 170 * mm); z.drawOn(c, x * mm, y * mm - h); return y - h / mm - 4


def start(n, title, subtitle):
    c.setFillColor(HexColor('#117e86')); c.rect(0, 204 * mm, 297 * mm, 6 * mm, fill=1, stroke=0)
    c.setFillColor(HexColor('#172833')); c.setFont('Bold', 18); c.drawString(12 * mm, 190 * mm, title)
    c.setFont('Arial', 9); c.drawString(12 * mm, 182 * mm, subtitle)
    c.setStrokeColor(HexColor('#cdd7dc')); c.line(12 * mm, 14 * mm, 285 * mm, 14 * mm)
    c.setFont('Arial', 8); c.drawString(12 * mm, 9 * mm, f'{TYTUL} | 04.10.2026 | PCB do zamówienia | przymiarka 1:1 i odbiór sprzętu: NIE ZBADANO')
    c.drawRightString(285 * mm, 9 * mm, f'{n} / {NPAGES}')


def board(name, x=40, y=40):
    svg = ET.parse(O / 'svg' / (name + '.svg')).getroot(); w = float(svg.attrib['width'].removesuffix('mm')); h = float(svg.attrib['height'].removesuffix('mm'))
    assert abs(w - W) < .2 and abs(h - H) < .2, (name, w, h)
    c.drawImage(str(O / 'previews' / (name + '.png')), x * mm, y * mm, w * mm, h * mm, mask='auto')
    c.setStrokeColor(HexColor('#000000')); c.setLineWidth(1.2); c.line(x * mm, (y - 10) * mm, (x + 100) * mm, (y - 10) * mm)
    for xx in (x, x + 100):
        c.line(xx * mm, (y - 13) * mm, xx * mm, (y - 7) * mm)
    c.setFont('Arial', 8.5); c.drawString(x * mm, (y - 17) * mm, 'Belka 100 mm. Drukować 100 %, bez dopasowania do strony; zmierzyć belkę przed przymiarką.')


def liczba(n, f1, f2, f5):   # 1 zgłoszenie, 2 zgłoszenia, 5 zgłoszeń
    return f'{n} ' + (f1 if n == 1 else f2 if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14 else f5)


npass = sum(x['detected'] for x in neg)
onboard = [r for r in parts if parts[r].get('on_board', True)]
hidden = silk['hidden_references']
start(1, f'{REV} — PANEL: płytka okablowania styków panelu',
      f'{W:g} × {H:g} mm, leży poziomo na dnie strefy panelu (50 mm przed stosem S1), długim bokiem wzdłuż ściany panelu. Schemat: osobny PDF (P11-R2-schemat.pdf).')
y = 172
for t in [f'<b>Płytka:</b> {W:g} × {H:g} mm (limit użytkownika 45 × 130 mm), narożniki R1, FR4 1,6 mm, 2 × 35 µm; 4 otwory M3 (NPTH 3,2) w narożnikach, strefy Ø7 '
          'bez miedzi i części; górna para za J_P12 (y = 19 mm), bo korpus IDC 2×10 zajmuje całą krótką krawędź. '
          f'{len(onboard)} części na płytce, wszystkie od góry.',
          '<b>J_P12</b> (IDC 2×10 kątowe obudowane, pinout docs/J_P12.csv) na krótkiej krawędzi y = 0 od strony ściany A: wtyk równo z krawędzią, '
          'pin 1 od strony panelu (mniejsze x), nadruk „1”. Taśma 1,27 mm do P12.',
          '<b>Pola przewodów</b> przy długim boku od strony panelu (x = 0): J11 (18 pól, 9 kolumn = 9 styków X11–X17, po dwa przewody na styk), '
          'J8 (port TEST, komory 10 / 11), J6 (RG174 do BNC SCOPE). Otwory 1,1 mm, pola 2,3 mm, raster 3,5 mm; przy każdym polu kotwa opaski '
          '(2 × Ø3,2 NPTH) między polami a krawędzią panelu, wokół kotew 3 mm bez miedzi. Przy każdej kolumnie nadruk z nazwą styku.',
          '<b>R1</b> 100 Ω 1206: nadruk „LOGGER: LUTOWAC / Z P04: DNP” (z P04 R40 jest jedynym źródłem PANEL_3V3).',
          f'<b>Ścieżki:</b> sygnały 0,3 mm, PANEL_3V3 i 3V3_IO 0,4 mm; wylewki GND na obu warstwach (F.Cu {str(gnd["cover_percent"]["F.Cu"]).replace(".", ",")} %, '
          f'B.Cu {str(gnd["cover_percent"]["B.Cu"]).replace(".", ",")} %), {gnd["gnd_vias"]} przelotek zszywających GND.',
          f'<b>Kontrole:</b> DRC: {len(drc["unconnected_items"])} niepołączonych, {len(drc["schematic_parity"])} niezgodności ze schematem, '
          f'{len(drc["violations"]) - nlib} innych naruszeń'
          + (f'; {liczba(nlib, "zgłoszenie", "zgłoszenia", "zgłoszeń")} lib_footprint_mismatch u części z przyciętym nadrukiem (przyjęte przez verify_pcb.py)' if nlib else '')
          + f'; PCB {checks["passed"]}/{checks["total"]}; próby ujemne PCB {npass}/{len(neg)} (z próbą zerową).',
          '<b>Otwarte:</b> przymiarka 1:1 (strona 5) w strefie panelu; długości przewodów do styków z makiety panelu; '
          f'{liczba(len(hidden), "oznaczenie ukryte", "oznaczenia ukryte", "oznaczeń ukrytych")}{(" (" + ", ".join(hidden) + ")") if hidden else ""}.']:
    y = para(t, 12, y, 150)
c.drawImage(str(O / 'previews/isometric.png'), 168 * mm, 30 * mm, 120 * mm, 140 * mm, preserveAspectRatio=True, anchor='c', mask='auto')
para('Render KiCad bez modeli 3D części (obraz Dockera nie ma biblioteki modeli KiCad).', 170, 30, 115)
c.showPage()
pages = [(2, 'Montaż od góry — 1:1', 'assembly', [
    '<b>J11:</b> kolumna = jeden styk panelu (nadruk Xnn.a-b), dwa przewody AWG24 do jego zacisków; pole 1 kwadratowe. Zaciski styków są '
    'funkcyjne: rzeczywiste zaciski kupionej części ustalić przejściem (docs/WIAZKI.md). Najpierw lutować rząd bliżej kotwy, potem drugi.',
    '<b>J8:</b> przewody do portu TEST, komora 10 (LOOP_OUT) i 11 (MECH_OK). <b>J6:</b> RG174, żyła do pola 1 (kwadratowe), ekran do pola 2 (GND).',
    '<b>Opaski:</b> na izolacji przez dwa otwory kotwy każdego pola; przewody biegną prosto w stronę panelu (x = 0), pas pod nimi bez części.',
    '<b>R1:</b> lutować tylko w wariancie LOGGER (bez P04). <b>J_P12:</b> gniazdo kątowe, wtyk w stronę ściany A.']),
    (3, 'Miedź F.Cu — 1:1', 'copper-front', [
    'Natywny eksport KiCad po wypełnieniu stref. Szare pola to miedź (GND).',
    '<b>Obszary bez miedzi</b> wokół otworów M3 (Ø7) i otworów kotew (Ø6), na obu warstwach. PANEL_3V3 i 3V3_IO 0,4 mm, pozostałe 0,3 mm.',
    'Wydruk kontrolny, nie plik produkcyjny.']),
    (4, 'Miedź B.Cu — 1:1, widok od spodu', 'copper-back', [
    'Widok od spodu (lustrzany względem strony 3). B.Cu to głównie masa GND.']),
    (5, 'Przymiarka 1:1 — obrys, obrysy części, otwory', 'fit', [
    'Wydrukować w skali 100 % i położyć w strefie panelu. Kółka Ø7 wokół otworów M3 to strefy dystansów, kółka Ø6 wokół otworów kotew '
    'to pola bez miedzi pod opaskę.',
    '<b>Wysokości:</b> IDC kątowe ok. 9,2 mm nad płytką; przewody z opaskami ok. 4–6 mm (szacunek).',
    'Krótka krawędź y = 0 (J_P12) od strony ściany A; długi bok x = 0 od strony panelu.'])]
for n, title, name, notes in pages:
    start(n, title, 'Geometria z natywnego pliku PCB; sprawdź belkę 100 mm przed przymiarką.'); board(name)
    yy = 172
    for t in notes:
        yy = para(t, 135, yy, 150)
    c.showPage()
c.save(); print(PDF)
