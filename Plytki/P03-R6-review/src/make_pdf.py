"""Review PDF of the P03 R6 PCB (format S1): native KiCad plots at 1:1 (A4 landscape), no redrawn copper (P02 R4 pattern).
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
checks = json.loads((P / 'verification/pcb-checks.json').read_text(encoding='utf-8')); assert checks['passed'] == checks['total']
assert checks['board_sha256'] == hashlib.sha256((P / 'eda/P03.kicad_pcb').read_bytes()).hexdigest()
neg = json.loads((P / 'verification/negative-controls.json').read_text(encoding='utf-8'))
parts = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
drc = json.loads((P / 'verification/drc.json').read_text(encoding='utf-8')); silk = json.loads((P / 'routing/silkscreen.json').read_text(encoding='utf-8'))
det = checks['details']
p5 = next(v for k, v in det.items() if k.startswith('5 V path'))
m1 = next(v for k, v in det.items() if k.startswith('M1 Waveshare')); sd = next(v for k, v in det.items() if k.startswith('SD1 Adafruit'))
bottom = sorted(r for r, v in json.loads((P / 'src/placement.json').read_text(encoding='utf-8')).items() if len(v) > 3 and v[3] == 'B')
nlib = sum(1 for v in drc['violations'] if v['type'] == 'lib_footprint_mismatch')
pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf')); pdfmetrics.registerFont(TTFont('Bold', 'C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Bold', italic='Arial', boldItalic='Bold')   # 30.09: <b> in the notes printed as regular without it
(O / 'pdf').mkdir(parents=True, exist_ok=True)
c = Canvas(str(O / 'pdf/P03-R6-PCB.pdf'), pagesize=(297 * mm, 210 * mm)); c.setTitle('EGRLab P03 R6: PCB CORE w formacie S1')
style = ParagraphStyle('body', fontName='Arial', fontSize=9.5, leading=13, textColor=HexColor('#172833'))
NPAGES = 5


def pl(v):
    return str(v).replace('.', ',')   # Polish decimal comma (30.09: numbers printed as 6.15 mm)


def para(t, x, y, w):
    z = Paragraph(t, style); _, h = z.wrap(w * mm, 170 * mm); z.drawOn(c, x * mm, y * mm - h); return y - h / mm - 4


def start(n, title, subtitle):
    c.setFillColor(HexColor('#117e86')); c.rect(0, 204 * mm, 297 * mm, 6 * mm, fill=1, stroke=0)
    c.setFillColor(HexColor('#172833')); c.setFont('Bold', 18); c.drawString(12 * mm, 190 * mm, title)
    c.setFont('Arial', 9); c.drawString(12 * mm, 182 * mm, subtitle)
    c.setStrokeColor(HexColor('#cdd7dc')); c.line(12 * mm, 14 * mm, 285 * mm, 14 * mm)
    c.setFont('Arial', 8); c.drawString(12 * mm, 9 * mm, 'P03 R6 S1-L | 30.09.2026 | PCB do recenzji lokalnej | przymiarka 1:1 i odbiór sprzętu: NIE ZBADANO')
    c.drawRightString(285 * mm, 9 * mm, f'{n} / {NPAGES}')


def board(name, x=12, y=40):
    svg = ET.parse(O / 'svg' / (name + '.svg')).getroot(); w = float(svg.attrib['width'].removesuffix('mm')); h = float(svg.attrib['height'].removesuffix('mm'))
    assert abs(w - 160) < .2 and abs(h - 100) < .2, (name, w, h)
    c.drawImage(str(O / 'previews' / (name + '.png')), x * mm, y * mm, w * mm, h * mm, mask='auto')
    c.setStrokeColor(HexColor('#000000')); c.setLineWidth(1.2); c.line(x * mm, (y - 10) * mm, (x + 100) * mm, (y - 10) * mm)
    for xx in (x, x + 100):
        c.line(xx * mm, (y - 13) * mm, xx * mm, (y - 7) * mm)
    c.setFont('Arial', 8.5); c.drawString(x * mm, (y - 17) * mm, 'Belka 100 mm. Drukować 100 %, bez dopasowania do strony; zmierzyć belkę przed przymiarką.')


npass = sum(x['detected'] for x in neg)
hmax = max((HEIGHTS.get(r, HEIGHTS.get(parts[r]['footprint']))[0], r) for r in parts if parts[r].get('on_board', True))
start(1, 'P03 R6 — CORE (ESP32-S3), PCB w formacie S1', 'Klasa L (160 × 100 mm), sloty S1–S3 poziomu 2 (dystanse 20 mm). Schemat: osobny PDF (6 arkuszy A3).')
y = 172
for t in [f'<b>Płytka:</b> 160 × 100 mm (klasa L), narożniki R1, FR4 1,6 mm, 2 × 35 µm; 12 otworów M3 (NPTH 3,2) według format-s1.json, strefy dystansów Ø7 bez miedzi i części. '
          f'{sum(1 for q in parts.values() if q["on_board"])} części, od spodu {", ".join(bottom) or "żadnych"}; najwyższa część {hmax[1]} {pl(hmax[0])} mm (limit 16,5).',
          '<b>Krawędź A:</b> J_BP1 / J_BP2 / J_BP3 (IDC 2×10 kątowe, pinout docs/J_BP.csv) ze środkami w x = 26,5 / 80 / 133,5. <b>Krawędź B:</b> J_SV1–J_SV3 '
          '(goldpin kątowy 1×13, GND na końcach, każdy kołek przez rezystor 1k / 10k przy węźle; przydział według położenia węzłów, docs/SERWIS.csv).',
          f'<b>Moduły:</b> M1 (Waveshare ESP32-S3) w S2, USB-C w stronę krawędzi B, {pl(m1["usb_to_edge_B_mm"])} mm od niej; antena w stronę krawędzi A, pod nią obszar bez miedzi. '
          f'SD1 (Adafruit 4682) w S3, karta w stronę krawędzi B, {pl(sd["card_tip_to_edge_B_mm"])} mm od niej. Oba moduły kończą się przed obrysem listew serwisowych (sporne, README).',
          f'<b>5 V:</b> J_BP2.17/19/20 → Q1 (blokada USB) → ścieżka 1,5 mm po B.Cu wzdłuż prawego boku M1 → M1 J1-21; miedź toru {pl(p5["total_mOhm"])} mΩ (budżet 50 mΩ).',
          f'<b>Kontrole:</b> DRC: {len(drc["unconnected_items"])} niepołączonych, {len(drc["schematic_parity"])} niezgodności ze schematem, '
          f'{len(drc["violations"]) - nlib} innych naruszeń; {nlib} zgłoszeń lib_footprint_mismatch u części z przyciętym nadrukiem (przyjęte przez verify_pcb.py); '
          f'PCB {checks["passed"]}/{checks["total"]}; próby ujemne PCB {npass}/{len(neg)} (z próbą zerową).',
          f'<b>Otwarte:</b> przymiarka 1:1 (strona 5), wysokość M1 na listwach (szacunek), recenzja lokalna; '
          f'{len(silk["hidden_references"])} oznaczeń ukrytych z braku miejsca{(" (" + ", ".join(silk["hidden_references"]) + ")") if silk["hidden_references"] else ""}; paczka produkcyjna poza zakresem.']:
    y = para(t, 12, y, 120)
c.drawImage(str(O / 'previews/isometric.png'), 138 * mm, 30 * mm, 150 * mm, 125 * mm, preserveAspectRatio=True, anchor='c', mask='auto')
para('Render KiCad z modelami bibliotecznymi (moduły bez modeli 3D).', 142, 30, 140)
c.showPage()
pages = [(2, 'Montaż od góry — 1:1', 'assembly', [
    '<b>M1</b> na dwóch listwach żeńskich 1×22 (rzędy 22,86 mm), USB-C w stronę krawędzi B. <b>SD1</b> na listwie żeńskiej 1×9 i dwóch dystansach M2,5.',
    '<b>U1 (DIP28) i U2 (DIP16)</b> w podstawkach. SOIC-14 i SOT-23 lutowane wprost. Wszystkie rezystory i kondensatory SMD 1206.',
    '<b>Listwy serwisowe:</b> przy J_SV1 pełne nazwy; przy J_SV2 i J_SV3 skróty trzyliterowe (nad nimi stoją moduły), legenda skrótów na płytce.',
    'Wyprowadzenia THT od spodu przyciąć do ≤ 1,5 mm (S1 §4).']),
    (3, 'Miedź F.Cu — 1:1', 'copper-front', [
    'Natywny eksport KiCad po wypełnieniu stref. Szare pola to miedź (GND).',
    '<b>Obszar bez miedzi</b> pod anteną M1 (obie warstwy) i wokół dystansów M3 i M2,5.', 'Wydruk kontrolny, nie plik produkcyjny.']),
    (4, 'Miedź B.Cu — 1:1, widok od spodu', 'copper-back', [
    'Widok od spodu (lustrzany względem strony 3).', '<b>Tor 5V_M1:</b> ścieżka 1,5 mm wzdłuż prawego boku M1 i pod końcem USB do J1-21.']),
    (5, 'Przymiarka 1:1 — obrys, obrysy części, otwory', 'fit', [
    'Wydrukować w skali 100 % i położyć na części / w obudowie. Kółka Ø7 wokół otworów M3 to strefy dystansów, kółka Ø6 przy SD1 — '
    'pola dystansów M2,5 modułu karty.',
    f'<b>Wysokości (limit 16,5 mm, poziom 2):</b> M1 na listwach ok. {pl(HEIGHTS["M1"][0])} mm (szacunek), SD1 ok. {pl(HEIGHTS["SD1"][0])} mm, IDC ok. 9,2 mm, DIP w podstawkach ok. 8 mm.',
    'Kołki listew J_SV wystają ok. 6 mm za krawędź B; J_BP wtyk równo z krawędzią A.'])]
for n, title, name, notes in pages:
    start(n, title, 'Geometria z natywnego pliku PCB; sprawdź belkę 100 mm przed przymiarką.'); board(name)
    yy = 172
    for t in notes:
        yy = para(t, 178, yy, 107)
    c.showPage()
c.save(); print(O / 'pdf/P03-R6-PCB.pdf')
