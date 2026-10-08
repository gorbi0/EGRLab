"""Review PDF of the M1-R1 PCB (150 x 80 mm, 4 layers): native KiCad plots at 1:1 (A4 landscape), no redrawn copper (P07 S1 make_pdf.py pattern).
Pages: 1 overview, 2 assembly top, 3 F.Cu, 4 In1.Cu, 5 In2.Cu, 6 B.Cu (seen from below), 7 fit print 1:1.
Fonts: reportlab with the Arial files named here; in the cloud image egrlab_winpaths maps them to Liberation Sans.
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
from heights import HEIGHTS
from board import NAME, REV, W as BW, H as BH
TYTUL = f'EGRLab {REV}'
checks = json.loads((P / 'verification/pcb-checks.json').read_text(encoding='utf-8')); assert checks['passed'] == checks['total']
neg = json.loads((P / 'verification/negative-controls.json').read_text(encoding='utf-8'))
parts = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
drc = json.loads((P / 'verification/drc.json').read_text(encoding='utf-8')); silk = json.loads((P / 'routing/silkscreen.json').read_text(encoding='utf-8'))
snap = json.loads((P / 'verification/pcb-snapshot.json').read_text())
bottom = sorted((r for r, v in json.loads((P / 'src/placement.json').read_text(encoding='utf-8')).items() if len(v) > 3 and v[3] == 'B'),
                key=lambda r: (r[0], int(''.join(ch for ch in r if ch.isdigit()))))
nlib = sum(1 for v in drc['violations'] if v['type'] == 'lib_footprint_mismatch')
pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf')); pdfmetrics.registerFont(TTFont('Bold', 'C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Bold', italic='Arial', boldItalic='Bold')   # 30.09: <b> in the notes printed as regular without it
(O / 'pdf').mkdir(parents=True, exist_ok=True)
PDF = O / f"pdf/{REV.replace(' ', '-')}-PCB.pdf"
c = Canvas(str(PDF), pagesize=(297 * mm, 210 * mm)); c.setTitle(f'EGRLab {REV}: PCB (LOGGER + TESTER, jedna plytka)')
style = ParagraphStyle('body', fontName='Arial', fontSize=9.5, leading=13, textColor=HexColor('#172833'))
NPAGES = 7


def para(t, x, y, w):
    z = Paragraph(t, style); _, h = z.wrap(w * mm, 170 * mm); z.drawOn(c, x * mm, y * mm - h); return y - h / mm - 4


def start(n, title, subtitle):
    c.setFillColor(HexColor('#117e86')); c.rect(0, 204 * mm, 297 * mm, 6 * mm, fill=1, stroke=0)
    c.setFillColor(HexColor('#172833')); c.setFont('Bold', 18); c.drawString(12 * mm, 190 * mm, title)
    c.setFont('Arial', 9); c.drawString(12 * mm, 182 * mm, subtitle)
    c.setStrokeColor(HexColor('#cdd7dc')); c.line(12 * mm, 14 * mm, 285 * mm, 14 * mm)
    c.setFont('Arial', 8); c.drawString(12 * mm, 9 * mm, f'{TYTUL} | 08.10.2026 | PCB (layout lokalny) | przymiarka 1:1 i odbiór sprzętu: NIE ZBADANO')
    c.drawRightString(285 * mm, 9 * mm, f'{n} / {NPAGES}')


def board(name, x=12, y=92):
    svg = ET.parse(O / 'svg' / (name + '.svg')).getroot(); w = float(svg.attrib['width'].removesuffix('mm')); h = float(svg.attrib['height'].removesuffix('mm'))
    assert abs(w - BW) < .2 and abs(h - BH) < .2, (name, w, h)
    c.drawImage(str(O / 'previews' / (name + '.png')), x * mm, y * mm, w * mm, h * mm, mask='auto')
    c.setStrokeColor(HexColor('#000000')); c.setLineWidth(1.2); c.line(x * mm, (y - 10) * mm, (x + 100) * mm, (y - 10) * mm)
    for xx in (x, x + 100):
        c.line(xx * mm, (y - 13) * mm, xx * mm, (y - 7) * mm)
    c.setFont('Arial', 8.5); c.drawString(x * mm, (y - 17) * mm, 'Belka 100 mm. Drukować 100 %, bez dopasowania do strony; zmierzyć belkę przed przymiarką.')


def liczba(n, f1, f2, f5):   # 1 zgłoszenie, 2 zgłoszenia, 5 zgłoszeń
    return f'{n} ' + (f1 if n == 1 else f2 if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14 else f5)


def h_of(r):
    return HEIGHTS.get(r, HEIGHTS.get(parts[r]['footprint']))[0]


npass = sum(x['detected'] for x in neg)
onboard = [r for r in parts if parts[r].get('on_board', True)]
fitted = [r for r in onboard if not parts[r].get('dnp')]
hmax = max(h_of(r) for r in onboard); tall = sorted(r for r in onboard if h_of(r) == hmax)
hidden = silk['hidden_references']
fx = lambda v: str(v).replace('.', ',')
start(1, f'{REV} — jedna płytka LOGGER + TESTER (wariant M1)', f'{fx(BW)} × {fx(BH)} mm, 4 warstwy. Schemat: osobny PDF (M1-R1-schemat.pdf, 7 arkuszy A3). Obudowa dopasowana do płytki.')
y = 172
for t in [f'<b>Płytka:</b> {fx(BW)} × {fx(BH)} mm, narożniki R1, 4 warstwy JLC04161H-7628 1,6 mm (zewnętrzne 35 µm, wewnętrzne 15 µm; In1 ciągła masa, In2 sygnały); '
          f'4 otwory M3 (NPTH 3,2) w narożach, strefy Ø7 bez miedzi. {len(fitted)} części montowanych (+ {len(onboard) - len(fitted)} DNP), od spodu {len(bottom)} kondensatory 1206 pod AD7606B (jak P05 R3); '
          f'najwyższa {", ".join(tall)} {fx(hmax)} mm (szacunek).',
          '<b>Górna krawędź:</b> pola przewodów do listwy X1 w kolejności zacisków (docs/X1.csv): BAT+ / GND, VMOTOR, P1_ECU / P1_EGR (2,0 mm²), P3 … CAN_GND (cienkie); '
          'kotwy opasek 12 mm nad polami. <b>Prawa:</b> ESP32-S3 DEV-KIT na kołkach, antena w rogu (strefa bez miedzi na wszystkich warstwach), USB-C przy dolnej krawędzi. '
          '<b>Dolna:</b> pola IBT-2 (J4), moduły MAX31856 (zaciski termopar przy krawędzi, osobna mufa), moduł microSD (gniazdo przy krawędzi).',
          '<b>Tor 7,5 A:</b> BAT_P (J1.1 → F1), VBUS (F1 → J2 VMOTOR), P1_ECU / P1_EGR (J5 ↔ bocznik) jako wylewki na F.Cu i B.Cu, zszyte przelotkami; minus silnika poza płytką (X1.4 ↔ X1.2). '
          '<b>Kelvin:</b> K_PLUS z pola 2 w dół po F.Cu do R22, K_MINUS z pola 3 przelotką na In2.Cu (pod masą In1) do R23; tylko miedź zablokowana, pod bocznikiem od spodu nic. '
          '<b>AD7606B:</b> miedź wokół układu przeniesiona z P05 R3 (to samo ułożenie, przesunięcie +37 / −15 mm): odsprzęganie, wyprowadzenia, masa wewnątrz pierścienia pól.',
          f'<b>Kontrole:</b> DRC: {len(drc["unconnected_items"])} niepołączonych, {len(drc["schematic_parity"])} niezgodności ze schematem, '
          f'{len(drc["violations"]) - nlib} innych naruszeń'
          + (f'; {liczba(nlib, "zgłoszenie", "zgłoszenia", "zgłoszeń")} lib_footprint_mismatch u części z przyciętym nadrukiem' if nlib else '')
          + f'; PCB {checks["passed"]}/{checks["total"]}; próby ujemne PCB {npass}/{len(neg)} (z próbą zerową).',
          '<b>Otwarte:</b> przymiarka 1:1 (strona 7: moduły, oprawka F1, pola przewodów), wysokości modułów (szacunek); '
          f'{liczba(len(hidden), "oznaczenie ukryte", "oznaczenia ukryte", "oznaczeń ukrytych")} z braku miejsca.']:
    y = para(t, 12, y, 120)
c.drawImage(str(O / 'previews/isometric.png'), 138 * mm, 30 * mm, 150 * mm, 125 * mm, preserveAspectRatio=True, anchor='c', mask='auto')
para('Render KiCad bez modeli 3D części (obraz Dockera nie ma biblioteki modeli KiCad).', 140, 30, 140)
c.showPage()
pages = [(2, 'Montaż od góry — 1:1', 'assembly', [
    '<b>Kolejność:</b> spód (C8, C9, C10, C13 pod AD7606B), potem SMD od góry (AD7606B najpierw), THT (TSR, oprawka F1), na końcu moduły ESP32 / SD / MAX31856 (lutowane wprost, D-M1-11 / 12). '
    '<b>RSH1</b>: pola pomiarowe 2 / 3 na przekątnej; bez nadmiaru cyny na polach prądowych. R25 / R27 (0R, opcja 5 V modułów termopar) nie montować.',
    '<b>Przewody:</b> 2,0 mm² do J1 / J2 / J5, cienkie do J6 / J4, opaska przez dwa otwory kotwy nad każdym rzędem; opisy przy polach (B+, B-, VM, ECU, EGR, P3 … G, RP … G).']),
    (3, 'Miedź F.Cu — 1:1', 'copper-front', [
    'Natywny eksport KiCad po wypełnieniu stref (szare = miedź). Wylewki toru 7,5 A w lewym górnym rogu i pod polami P1; reszta warstwy to masa GND. Wydruk kontrolny, nie plik produkcyjny.']),
    (4, 'Miedź In1.Cu — 1:1 (masa)', 'copper-in1', [
    'Warstwa wewnętrzna 1 (0,5 oz): ciągła masa GND pod całą płytką (otwory przelotek i pól THT jako wycięcia); bez miedzi w strefie anteny.']),
    (5, 'Miedź In2.Cu — 1:1 (sygnały)', 'copper-in2', [
    'Warstwa wewnętrzna 2 (0,5 oz): ścieżki sygnałowe routera i K_MINUS (zablokowany, pod torem P1_EGR). Zasilania 5V / 3V3 jako ścieżki klasy PWR (0,5 mm).']),
    (6, 'Miedź B.Cu — 1:1, widok od spodu', 'copper-back', [
    'Widok od spodu (lustrzany względem strony 3). Druga warstwa wylewek toru 7,5 A, kondensatory pod AD7606B, reszta masa GND; pod bocznikiem pusto.']),
    (7, 'Przymiarka 1:1 — obrys, obrysy części, otwory', 'fit', [
    'Wydrukować w skali 100 % (sprawdzić belkę 100 mm). Kółka Ø7 wokół otworów M3 to strefy dystansów.',
    f'<b>Wysokości (szacunek, do projektu obudowy):</b> moduły MAX31856 {fx(h_of("TC1"))} mm, oprawka F1 z wkładką {fx(h_of("F1"))} mm, ESP32 {fx(h_of("M1"))} mm, TSR {fx(h_of("U1"))} mm.'])]
for n, title, name, notes in pages:
    start(n, title, 'Geometria z natywnego pliku PCB; sprawdź belkę 100 mm przed przymiarką.'); board(name)
    yy = 70
    for t in notes:
        yy = para(t, 12, yy, 270)
    c.showPage()
c.save(); print(PDF)
