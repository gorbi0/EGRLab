"""Review PDF of the P08 R2 PCB (format S1, class 1/3; P10 R2 make_pdf.py): native KiCad plots at 1:1 (A4 landscape), no redrawn copper (P03 R6 / P09 R2 pattern).
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
jd = next(v for k, v in det.items() if k.startswith('J4 (TSENSOR')); kd = next(v for k, v in det.items() if k.startswith('Sensor path through K1'))
bottom = sorted((r for r, v in json.loads((P / 'src/placement.json').read_text(encoding='utf-8')).items() if len(v) > 3 and v[3] == 'B'),
                key=lambda r: (r[0], int(r[1:])))
nlib = sum(1 for v in drc['violations'] if v['type'] == 'lib_footprint_mismatch')
pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf')); pdfmetrics.registerFont(TTFont('Bold', 'C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Bold', italic='Arial', boldItalic='Bold')   # 30.09: <b> in the notes printed as regular without it
(O / 'pdf').mkdir(parents=True, exist_ok=True)
PDF = O / f"pdf/{REV.replace(' ', '-')}-PCB.pdf"
c = Canvas(str(PDF), pagesize=(297 * mm, 210 * mm)); c.setTitle(f'EGRLab {REV}: PCB SENSOR w formacie S1')
style = ParagraphStyle('body', fontName='Arial', fontSize=9.5, leading=13, textColor=HexColor('#172833'))
NPAGES = 5


def para(t, x, y, w):
    z = Paragraph(t, style); _, h = z.wrap(w * mm, 170 * mm); z.drawOn(c, x * mm, y * mm - h); return y - h / mm - 4


def start(n, title, subtitle):
    c.setFillColor(HexColor('#117e86')); c.rect(0, 204 * mm, 297 * mm, 6 * mm, fill=1, stroke=0)
    c.setFillColor(HexColor('#172833')); c.setFont('Bold', 18); c.drawString(12 * mm, 190 * mm, title)
    c.setFont('Arial', 9); c.drawString(12 * mm, 182 * mm, subtitle)
    c.setStrokeColor(HexColor('#cdd7dc')); c.line(12 * mm, 14 * mm, 285 * mm, 14 * mm)
    c.setFont('Arial', 8); c.drawString(12 * mm, 9 * mm, f'{TYTUL} | 05.10.2026 | PCB do recenzji lokalnej | przymiarka 1:1 i odbiór sprzętu: NIE ZBADANO')
    c.drawRightString(285 * mm, 9 * mm, f'{n} / {NPAGES}')


def board(name, x=20, y=42):
    svg = ET.parse(O / 'svg' / (name + '.svg')).getroot(); w = float(svg.attrib['width'].removesuffix('mm')); h = float(svg.attrib['height'].removesuffix('mm'))
    assert abs(w - 53) < .2 and abs(h - 100) < .2, (name, w, h)
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
start(1, f'{REV} — SENSOR (zasilanie czujnika przez TPS2553 i K1), PCB w formacie S1',
      'Klasa 1/3 (53 × 100 mm), slot S1 poziomu 5 (S1-3, wariant pełny, dystanse 20 mm), przy panelu. Schemat: osobny PDF (P08-R2-schemat.pdf).')
y = 172
ks = kd['track_chain_mm']
fmt = lambda v: str(v).replace('.', ',')
for t in [f'<b>Płytka:</b> 53 × 100 mm (klasa 1/3), narożniki R1, FR4 1,6 mm, 2 × 35 µm; 4 otwory M3 (NPTH 3,2) według format-s1.json, strefy dystansów Ø7 '
          f'bez miedzi i części. {len(onboard)} części; od spodu tylko rezystory serwisowe SMD 1206 ({", ".join(bottom)}); najwyższe: {", ".join(tall)} '
          f'{fmt(hmax)} mm (limit 16,5 mm; K1 G6K 5,2 mm, U2 DIP18 5,33 mm).',
          '<b>Krawędź A:</b> J1 = J_BP (IDC 2×8 kątowe, pinout docs/J_BP.csv: nieparzyste i 12 / 14 GND), środek x = 26,5 mm, pin 1 od mniejszego x. '
          '<b>Krawędź B:</b> J2 goldpin kątowy 1×13 (GND na kołkach 1 i 13, kołki przez 1 kΩ, TPS_EN przez 10 kΩ, docs/SERWIS.csv); pin 1 od większego x (README).',
          f'<b>Tor czujnika:</b> U1 (TPS2553) → K1.3 ({fmt(ks["SENSOR_LIMITED U1.6-K1.3"])} mm), K1.4 → J4.1 5V_SENSOR ({fmt(ks["5V_SENSOR K1.4-J4.1"])} mm, F.Cu), '
          f'K1.5 → J4.2 AGND_SENSOR ({fmt(ks["AGND_SENSOR K1.5-J4.2"])} mm, B.Cu), ścieżki 0,6 mm; styk powrotu K1.6 bez mostków termicznych do GND. '
          f'J4: para 2 × AWG22 lutowana do otworów, kotwa opaski 12 mm w stronę panelu (krawędź otworu {fmt(min(jd["anchor_hole_edge_to_x0_mm"]))} mm od x = 0).',
          f'<b>Kontrole:</b> DRC: {len(drc["unconnected_items"])} niepołączonych, {len(drc["schematic_parity"])} niezgodności ze schematem, '
          f'{len(drc["violations"]) - nlib} innych naruszeń'
          + (f'; {liczba(nlib, "zgłoszenie", "zgłoszenia", "zgłoszeń")} lib_footprint_mismatch u części z przyciętym nadrukiem (przyjęte przez verify_pcb.py)' if nlib else '')
          + f'; PCB {checks["passed"]}/{checks["total"]}; próby ujemne PCB {npass}/{len(neg)} (z próbą zerową).',
          '<b>Otwarte:</b> przymiarka 1:1 (strona 5; kotwa J4 i przebieg pary do portu TEST), recenzja lokalna; '
          f'{liczba(len(hidden), "oznaczenie ukryte", "oznaczenia ukryte", "oznaczeń ukrytych")} z braku miejsca{(" (" + ", ".join(hidden) + "; na rysunku montażowym z warstwy F.Fab)") if hidden else ""}.']:
    y = para(t, 12, y, 150)
c.drawImage(str(O / 'previews/isometric.png'), 168 * mm, 30 * mm, 120 * mm, 140 * mm, preserveAspectRatio=True, anchor='c', mask='auto')
para('Render KiCad bez modeli 3D części (obraz Dockera nie ma biblioteki modeli KiCad).', 170, 30, 115)
c.showPage()
pages = [(2, 'Montaż od góry — 1:1', 'assembly', [
    '<b>J4:</b> para W4 (5V_SENSOR → pole kwadratowe 1, nadruk „1”; AGND_SENSOR → pole 2) lutowana do otworów, opaska na izolacji przez dwa otwory kotwy; '
    'przewody biegną prosto do panelu (x = 0) i dalej do portu TEST (docs/WIAZKI.md). AGND_SENSOR nigdy do GND poza K1.',
    '<b>U1</b> SOT-23-6 i <b>U4 / U5</b> SOIC-14 lutowane wprost od góry; U3 w podstawce DIP14; U2 DIP18 wprost; R15 (MF0207) i R16 (MF0204) na stojąco; '
    'pozostałe R / C SMD 1206 od góry.',
    f'<b>Od spodu:</b> tylko rezystory serwisowe {", ".join(bottom)} (SMD 1206 0,7 mm, ≥ 1 mm od pól THT). Lutować najpierw spód. Wyprowadzenia THT przyciąć do ≤ 1,5 mm (S1 §4).']),
    (3, 'Miedź F.Cu — 1:1', 'copper-front', [
    'Natywny eksport KiCad po wypełnieniu stref. Szare pola to miedź (GND).',
    '<b>Obszary bez miedzi</b> wokół otworów M3 (Ø7) i otworów kotwy J4 (Ø6). Szersze ścieżki: 5V_SYS i tor czujnika (0,6 mm).',
    'Wydruk kontrolny, nie plik produkcyjny.']),
    (4, 'Miedź B.Cu — 1:1, widok od spodu', 'copper-back', [
    'Widok od spodu (lustrzany względem strony 3). B.Cu to głównie masa GND; AGND_SENSOR K1.5 → J4.2 idzie tą warstwą.']),
    (5, 'Przymiarka 1:1 — obrys, obrysy części, otwory', 'fit', [
    'Wydrukować w skali 100 % i położyć na części / w obudowie. Kółka Ø7 wokół otworów M3 to strefy dystansów, kółka Ø6 wokół otworów kotwy J4 '
    'to pola bez miedzi pod opaskę.',
    '<b>Wysokości (limit 16,5 mm, poziom 5):</b> C10 ok. 12,5 mm, IDC ok. 9,2 mm, R15 na stojąco ok. 9 mm, U3 w podstawce ok. 8,5 mm, TO-92 ok. 8 mm, '
    'K1 5,2 mm, U2 5,33 mm, para W4 z opaską ok. 6 mm (szacunki do potwierdzenia).',
    'Kołki listwy J2 wystają ok. 6 mm za krawędź B; J1 wtyk równo z krawędzią A; para W4 wychodzi przy panelu (x = 0).'])]
for n, title, name, notes in pages:
    start(n, title, 'Geometria z natywnego pliku PCB; sprawdź belkę 100 mm przed przymiarką.'); board(name)
    yy = 172
    for t in notes:
        yy = para(t, 135, yy, 150)
    c.showPage()
c.save(); print(PDF)
