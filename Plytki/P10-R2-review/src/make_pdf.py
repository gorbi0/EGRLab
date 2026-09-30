"""Review PDF of the P10 R2 PCB (format S1, class 1/3): native KiCad plots at 1:1 (A4 landscape), no redrawn copper (P03 R6 / P09 R2 pattern).
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
from board import NAME, REV
checks = json.loads((P / 'verification/pcb-checks.json').read_text(encoding='utf-8')); assert checks['passed'] == checks['total']
assert checks['board_sha256'] == hashlib.sha256((P / f'eda/{NAME}.kicad_pcb').read_bytes()).hexdigest()
neg = json.loads((P / 'verification/negative-controls.json').read_text(encoding='utf-8'))
parts = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
drc = json.loads((P / 'verification/drc.json').read_text(encoding='utf-8')); silk = json.loads((P / 'routing/silkscreen.json').read_text(encoding='utf-8'))
det = checks['details']
jd = next(v for k, v in det.items() if k.startswith('J3 (OBD tail'))
bottom = sorted((r for r, v in json.loads((P / 'src/placement.json').read_text(encoding='utf-8')).items() if len(v) > 3 and v[3] == 'B'),
                key=lambda r: (r[0], int(r[1:])))
nlib = sum(1 for v in drc['violations'] if v['type'] == 'lib_footprint_mismatch')
pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf')); pdfmetrics.registerFont(TTFont('Bold', 'C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Bold', italic='Arial', boldItalic='Bold')   # 30.09: <b> in the notes printed as regular without it
(O / 'pdf').mkdir(parents=True, exist_ok=True)
PDF = O / f"pdf/{REV.replace(' ', '-')}-PCB.pdf"
c = Canvas(str(PDF), pagesize=(297 * mm, 210 * mm)); c.setTitle(f'EGRLab {REV}: PCB CAN w formacie S1')
style = ParagraphStyle('body', fontName='Arial', fontSize=9.5, leading=13, textColor=HexColor('#172833'))
NPAGES = 5


def para(t, x, y, w):
    z = Paragraph(t, style); _, h = z.wrap(w * mm, 170 * mm); z.drawOn(c, x * mm, y * mm - h); return y - h / mm - 4


def start(n, title, subtitle):
    c.setFillColor(HexColor('#117e86')); c.rect(0, 204 * mm, 297 * mm, 6 * mm, fill=1, stroke=0)
    c.setFillColor(HexColor('#172833')); c.setFont('Bold', 18); c.drawString(12 * mm, 190 * mm, title)
    c.setFont('Arial', 9); c.drawString(12 * mm, 182 * mm, subtitle)
    c.setStrokeColor(HexColor('#cdd7dc')); c.line(12 * mm, 14 * mm, 285 * mm, 14 * mm)
    c.setFont('Arial', 8); c.drawString(12 * mm, 9 * mm, f'{REV} S1-1/3 | 30.09.2026 | PCB do recenzji lokalnej | przymiarka 1:1 i odbiór sprzętu: NIE ZBADANO')
    c.drawRightString(285 * mm, 9 * mm, f'{n} / {NPAGES}')


def board(name, x=20, y=42):
    svg = ET.parse(O / 'svg' / (name + '.svg')).getroot(); w = float(svg.attrib['width'].removesuffix('mm')); h = float(svg.attrib['height'].removesuffix('mm'))
    assert abs(w - 53) < .2 and abs(h - 100) < .2, (name, w, h)
    c.drawImage(str(O / 'previews' / (name + '.png')), x * mm, y * mm, w * mm, h * mm, mask='auto')
    c.setStrokeColor(HexColor('#000000')); c.setLineWidth(1.2); c.line(x * mm, (y - 10) * mm, (x + 100) * mm, (y - 10) * mm)
    for xx in (x, x + 100):
        c.line(xx * mm, (y - 13) * mm, xx * mm, (y - 7) * mm)
    c.setFont('Arial', 8.5); c.drawString(x * mm, (y - 17) * mm, 'Belka 100 mm. Drukować 100 %, bez dopasowania do strony; zmierzyć belkę przed przymiarką.')


def h_of(r):
    return HEIGHTS.get(r, HEIGHTS.get(parts[r]['footprint']))[0]


npass = sum(x['detected'] for x in neg)
onboard = [r for r in parts if parts[r].get('on_board', True)]
hmax = max(h_of(r) for r in onboard); tall = sorted(r for r in onboard if h_of(r) == hmax)
hidden = silk['hidden_references']
start(1, f'{REV} — CAN (odbiornik pasywny), PCB w formacie S1',
      'Klasa 1/3 (53 × 100 mm), slot S3 poziomu 4 (S1-3, dystanse 20 mm), przy ścianie wejść. Schemat: osobny PDF (P10-R2-schemat.pdf).')
y = 172
for t in [f'<b>Płytka:</b> 53 × 100 mm (klasa 1/3), narożniki R1, FR4 1,6 mm, 2 × 35 µm; 4 otwory M3 (NPTH 3,2) według format-s1.json, strefy dystansów Ø7 '
          f'bez miedzi i części. {len(onboard)} części, wszystkie od góry (poziom 4: od spodu bez SOIC); najwyższe: {", ".join(tall)} '
          f'{str(hmax).replace(".", ",")} mm (limit 16,5 mm).',
          '<b>Krawędź A:</b> J1 = J_BP (IDC 2×5 kątowe, pinout docs/J_BP.csv), środek x = 26,5 mm, pin 1 od mniejszego x. <b>Krawędź B:</b> J2 goldpin '
          'kątowy 1×9 (GND na kołkach 1 i 9; kołki 2–6 przez 1 kΩ, CAN_H / CAN_L przez 10 kΩ, docs/SERWIS.csv); pin 1 od większego x — kątowa listwa '
          'od góry z kołkami za krawędzią B nie pozwala inaczej (README).',
          f'<b>Wejście OBD:</b> J3 (koniec wiązki W3, lutowany do otworów) przy ścianie wejść; kotwa opaski (2 × Ø3,2) 12 mm od rzędu lutów, w stronę ściany; '
          f'pas pod przewodem od kotwy do krawędzi wolny. D1 (PESD2CAN) przy wejściu kabla ({str(max(jd["D1_pad_to_J3_pad_mm"].values())).replace(".", ",")} mm od pól J3), '
          'dalej U1 (TCAN1051V, S i TXD na stałe do VIO) i bufor U2 z Ioff.',
          f'<b>Kontrole:</b> DRC: {len(drc["unconnected_items"])} niepołączonych, {len(drc["schematic_parity"])} niezgodności ze schematem, '
          f'{len(drc["violations"]) - nlib} innych naruszeń'
          + (f'; {nlib} zgłoszeń lib_footprint_mismatch u części z przyciętym nadrukiem (przyjęte przez verify_pcb.py)' if nlib else '')
          + f'; PCB {checks["passed"]}/{checks["total"]}; próby ujemne PCB {npass}/{len(neg)} (z próbą zerową).',
          '<b>Otwarte:</b> przymiarka 1:1 (strona 5; kotwa J3 i przebieg przewodu), recenzja lokalna; '
          f'{len(hidden)} oznaczeń ukrytych z braku miejsca{(" (" + ", ".join(hidden) + ")") if hidden else ""}; paczka produkcyjna poza zakresem.']:
    y = para(t, 12, y, 150)
c.drawImage(str(O / 'previews/isometric.png'), 168 * mm, 30 * mm, 120 * mm, 140 * mm, preserveAspectRatio=True, anchor='c', mask='auto')
para('Render KiCad z modelami bibliotecznymi (koniec wiązki J3 bez modelu 3D).', 170, 30, 115)
c.showPage()
pages = [(2, 'Montaż od góry — 1:1', 'assembly', [
    '<b>J3:</b> skrętka W3 (CAN_H → pole kwadratowe 1, CAN_L → pole 2) lutowana do otworów, opaska na izolacji przez dwa otwory kotwy; przewód biegnie prosto '
    'do ściany wejść, bez przecinania izolacji krawędzią płytki (docs/WIAZKI.md).',
    '<b>U1 / U2</b> SOIC lutowane wprost, <b>D1</b> SOT-23. Rezystory R2, R8, R9 (MF0207) i kondensatory 100 n na stojąco; pozostałe R/C SMD 1206.',
    '<b>Od spodu:</b> brak części (poziom 4). Wyprowadzenia THT od spodu przyciąć do ≤ 1,5 mm (S1 §4).']),
    (3, 'Miedź F.Cu — 1:1', 'copper-front', [
    'Natywny eksport KiCad po wypełnieniu stref. Szare pola to miedź (GND).',
    '<b>Obszary bez miedzi</b> wokół otworów M3 (Ø7) i otworów kotwy J3 (Ø6, na obu warstwach).', 'Wydruk kontrolny, nie plik produkcyjny.']),
    (4, 'Miedź B.Cu — 1:1, widok od spodu', 'copper-back', [
    'Widok od spodu (lustrzany względem strony 3). B.Cu to głównie masa GND.']),
    (5, 'Przymiarka 1:1 — obrys, obrysy części, otwory', 'fit', [
    'Wydrukować w skali 100 % i położyć na części / w obudowie. Kółka Ø7 wokół otworów M3 to strefy dystansów, kółka Ø6 wokół otworów kotwy J3 '
    'to pola bez miedzi pod opaskę.',
    '<b>Wysokości (limit 16,5 mm, poziom 4):</b> IDC ok. 9,2 mm, rezystory na stojąco ok. 9 mm, kondensatory 100 n ok. 7 mm, przewód W3 z opaską ok. 6 mm (szacunek).',
    'Kołki listwy J2 wystają ok. 6 mm za krawędź B; J1 wtyk równo z krawędzią A; przewód W3 wychodzi przy ścianie wejść.'])]
for n, title, name, notes in pages:
    start(n, title, 'Geometria z natywnego pliku PCB; sprawdź belkę 100 mm przed przymiarką.'); board(name)
    yy = 172
    for t in notes:
        yy = para(t, 135, yy, 150)
    c.showPage()
c.save(); print(PDF)
