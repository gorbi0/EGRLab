"""Review PDF of the P05 R3 PCB (format S1, class 2/3): native KiCad plots at 1:1 (A4 landscape), no redrawn copper (P03 R6 / P09 R2 / P10 R2 pattern).
Pages: 1 overview, 2 assembly top, 3 F.Cu, 4 B.Cu (seen from below), 5 fit print 1:1 (outline, courtyards, holes, heights).
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
from board import NAME, REV, CLASS, SLOTS
TYTUL = f"{REV} S1-{CLASS} {SLOTS[0] if len(SLOTS) == 1 else SLOTS[0] + '-' + SLOTS[-1]}"
checks = json.loads((P / 'verification/pcb-checks.json').read_text(encoding='utf-8')); assert checks['passed'] == checks['total']
assert checks['board_sha256'] == hashlib.sha256((P / f'eda/{NAME}.kicad_pcb').read_bytes()).hexdigest()
neg = json.loads((P / 'verification/negative-controls.json').read_text(encoding='utf-8'))
parts = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
drc = json.loads((P / 'verification/drc.json').read_text(encoding='utf-8')); silk = json.loads((P / 'routing/silkscreen.json').read_text(encoding='utf-8'))
det = checks['details']
dec = next(v for k, v in det.items() if k.startswith('U1 decoupling'))
bottom = sorted((r for r, v in json.loads((P / 'src/placement.json').read_text(encoding='utf-8')).items() if len(v) > 3 and v[3] == 'B'),
                key=lambda r: (r[0], int(''.join(ch for ch in r if ch.isdigit()))))
nlib = sum(1 for v in drc['violations'] if v['type'] == 'lib_footprint_mismatch')
pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf')); pdfmetrics.registerFont(TTFont('Bold', 'C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Bold', italic='Arial', boldItalic='Bold')   # 30.09: <b> in the notes printed as regular without it
(O / 'pdf').mkdir(parents=True, exist_ok=True)
PDF = O / f"pdf/{REV.replace(' ', '-')}-PCB.pdf"
c = Canvas(str(PDF), pagesize=(297 * mm, 210 * mm)); c.setTitle(f'EGRLab {REV}: PCB DAQ w formacie S1')
style = ParagraphStyle('body', fontName='Arial', fontSize=9.5, leading=13, textColor=HexColor('#172833'))
NPAGES = 5


def para(t, x, y, w):
    z = Paragraph(t, style); _, h = z.wrap(w * mm, 170 * mm); z.drawOn(c, x * mm, y * mm - h); return y - h / mm - 4


def start(n, title, subtitle):
    c.setFillColor(HexColor('#117e86')); c.rect(0, 204 * mm, 297 * mm, 6 * mm, fill=1, stroke=0)
    c.setFillColor(HexColor('#172833')); c.setFont('Bold', 18); c.drawString(12 * mm, 190 * mm, title)
    c.setFont('Arial', 9); c.drawString(12 * mm, 182 * mm, subtitle)
    c.setStrokeColor(HexColor('#cdd7dc')); c.line(12 * mm, 14 * mm, 285 * mm, 14 * mm)
    c.setFont('Arial', 8); c.drawString(12 * mm, 9 * mm, f'{TYTUL} | 01.10.2026 | PCB do recenzji lokalnej | przymiarka 1:1 i odbiór sprzętu: NIE ZBADANO')
    c.drawRightString(285 * mm, 9 * mm, f'{n} / {NPAGES}')


def board(name, x=12, y=42):
    svg = ET.parse(O / 'svg' / (name + '.svg')).getroot(); w = float(svg.attrib['width'].removesuffix('mm')); h = float(svg.attrib['height'].removesuffix('mm'))
    assert abs(w - 106.5) < .2 and abs(h - 100) < .2, (name, w, h)
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
hmax = max(h_of(r) for r in onboard); tall = sorted(r for r in onboard if h_of(r) == hmax)
hidden = silk['hidden_references']
start(1, f'{REV} — DAQ (AD7606B), PCB w formacie S1',
      'Klasa 2/3 (106,5 × 100 mm), sloty S1–S2 poziomu 3 (dystanse 20 mm). Schemat: osobny PDF (P05-R3-schemat.pdf, 9 arkuszy A3).')
worst = max(dec, key=lambda x: x['path_mm'] / x['limit_mm'])
y = 172
for t in [f'<b>Płytka:</b> 106,5 × 100 mm (klasa 2/3), narożniki R1, FR4 1,6 mm, 2 × 35 µm; 8 otworów M3 (NPTH 3,2) według format-s1.json, strefy dystansów Ø7 '
          f'bez miedzi i części. {len(onboard)} części; od spodu {len(bottom)} SMD ≤ 1,5 mm ({", ".join(bottom)}); najwyższa {", ".join(tall)} '
          f'{str(hmax).replace(".", ",")} mm (limit 16,5 mm).',
          '<b>Krawędź A:</b> J_BP1 (IDC 2×5, slot S1, x = 26,5) i J_BP2 (IDC 2×10, slot S2, x = 80,0), pinout docs/J_BP.csv, pin 1 od mniejszego x. '
          '<b>Krawędź B:</b> J_SV1 / J_SV2 (goldpin kątowy 1×13, GND na końcach, każdy kołek przez rezystor przy węźle: 1 kΩ, 10 kΩ węzły '
          'wysokoimpedancyjne, 4,7 kΩ VBAT_SENSE; docs/SERWIS.csv). <b>Strona panelu (x = 0):</b> TAPS J4 i AUX J6 (przewody lutowane, kotwy opasek), '
          'SW1 E-Switch 100 M6 (tuleja i dźwignia przez panel).',
          f'<b>U1 (AD7606B, LQFP-64):</b> odsprzęganie na miedzi od pinu do pola kondensatora — najbliżej limitu {worst["capacitor"]} przy '
          f'{worst["pin"]}: {str(worst["path_mm"]).replace(".", ",")} mm (limit {str(worst["limit_mm"]).replace(".", ",")}); 1 µF i 22 µF od góry, '
          '100 nF od spodu pod korpusem (przelotki wewnątrz pierścienia pól); REFCAP / REGCAP bez przelotek; piny GND do wylewki wewnątrz pierścienia '
          'z 4 przelotkami. Reguła drobnego rastra (odstęp 0,15 / tor 0,2 mm) tylko w obrysach U1 i U3, reszta płytki jak P02-R3 (0,25 / 0,3).',
          f'<b>Kontrole:</b> DRC: {len(drc["unconnected_items"])} niepołączonych, {len(drc["schematic_parity"])} niezgodności ze schematem, '
          f'{len(drc["violations"]) - nlib} innych naruszeń'
          + (f'; {liczba(nlib, "zgłoszenie", "zgłoszenia", "zgłoszeń")} lib_footprint_mismatch u części z przyciętym nadrukiem (przyjęte przez verify_pcb.py)' if nlib else '')
          + f'; PCB {checks["passed"]}/{checks["total"]}; próby ujemne PCB {npass}/{len(neg)} (z próbą zerową).',
          '<b>Otwarte:</b> przymiarka 1:1 (strona 5: SW1 w panelu, przewody TAPS / AUX), kod SW1 i C1 przy zakupie, grubość 100 nF od spodu (BOM), '
          f'recenzja lokalna; {liczba(len(hidden), "oznaczenie ukryte", "oznaczenia ukryte", "oznaczeń ukrytych")} z braku miejsca'
          f'{(" (" + ", ".join(hidden) + "; na rysunku montażowym z warstwy F.Fab)") if hidden else ""}; paczka produkcyjna poza zakresem.']:
    y = para(t, 12, y, 120)
c.drawImage(str(O / 'previews/isometric.png'), 138 * mm, 30 * mm, 150 * mm, 125 * mm, preserveAspectRatio=True, anchor='c', mask='auto')
para('Render KiCad bez modeli 3D części (obraz Dockera nie ma biblioteki modeli KiCad).', 140, 30, 140)
c.showPage()
pages = [(2, 'Montaż od góry — 1:1', 'assembly', [
    '<b>Kolejność lutowania:</b> najpierw spód (100 nF pod U1: C5, C7, C8, C11 — grubość ≤ 1,5 mm; rezystory listew), potem góra (S1-2).',
    '<b>U1</b> LQFP-64 (raster 0,5 mm) i <b>U3</b> VSSOP-8 (0,65 mm) lutowane wprost; SOIC-14 / SOIC-8 wprost; DIP-14 / DIP-18 i TO-92 THT.',
    '<b>TAPS J4 / AUX J6:</b> przewody lutowane do otworów, opaska na izolacji przez dwa otwory kotwy przy krawędzi x = 0; nadruk „1” przy polu 1.',
    '<b>SW1:</b> E-Switch 100 M6 kątowy, tuleja i dźwignia za krawędzią x = 0 przez otwór w panelu (makieta).']),
    (3, 'Miedź F.Cu — 1:1', 'copper-front', [
    'Natywny eksport KiCad po wypełnieniu stref. Szare pola to miedź (GND).',
    '<b>U1:</b> wachlarz wejść 49–63 do kolumny filtrów C27–C34, REFCAP pod C12 wzdłuż końców pól do C13, odgałęzienia TP2–TP5. '
    '<b>Bez miedzi</b> wokół otworów M3 (Ø7).',
    'Wydruk kontrolny, nie plik produkcyjny.']),
    (4, 'Miedź B.Cu — 1:1, widok od spodu', 'copper-back', [
    'Widok od spodu (lustrzany względem strony 3). B.Cu to głównie masa GND; pod U1 kondensatory 100 nF, pasek 5VA i połączenie 3V3 (VDRIVE / REFSEL).']),
    (5, 'Przymiarka 1:1 — obrys, obrysy części, otwory', 'fit', [
    'Wydrukować w skali 100 % i położyć na części / w obudowie. Kółka Ø7 wokół otworów M3 to strefy dystansów.',
    f'<b>Wysokości (limit 16,5 mm, poziom 3):</b> C1 ok. {str(h_of("C1")).replace(".", ",")} mm, SW1 {str(h_of("SW1")).replace(".", ",")} mm, '
    'IDC ok. 9,2 mm, MF0207 na stojąco ok. 9 mm (szacunek), TO-92 ok. 7 mm (szacunek).',
    'Kołki listew J_SV wystają ok. 6 mm za krawędź B; J_BP wtyk równo z krawędzią A; tuleja SW1 wychodzi za krawędź x = 0.'])]
for n, title, name, notes in pages:
    start(n, title, 'Geometria z natywnego pliku PCB; sprawdź belkę 100 mm przed przymiarką.'); board(name)
    yy = 172
    for t in notes:
        yy = para(t, 128, yy, 157)
    c.showPage()
c.save(); print(PDF)
