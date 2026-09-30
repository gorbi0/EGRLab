"""Review PDF of P02 R4 (format S1): native KiCad plots at 1:1 (A4 landscape), no redrawn copper.
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
import json, hashlib, xml.etree.ElementTree as ET
P = Path(__file__).resolve().parents[1]; O = P / 'output'
checks = json.loads((P / 'verification/pcb-checks.json').read_text(encoding='utf-8')); assert checks['passed'] == checks['total']
assert checks['board_sha256'] == hashlib.sha256((P / 'eda/P02.kicad_pcb').read_bytes()).hexdigest()
neg = json.loads((P / 'verification/negative-controls.json').read_text(encoding='utf-8'))
el = json.loads((P / 'verification/electrical-checks.json').read_text(encoding='utf-8'))
parts = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
drc = json.loads((P / 'verification/drc.json').read_text(encoding='utf-8')); silk = json.loads((P / 'routing/silkscreen.json').read_text(encoding='utf-8'))
bottom = sorted(r for r, v in json.loads((P / 'src/placement.json').read_text(encoding='utf-8')).items() if len(v) > 3 and v[3] == 'B')   # klasa L (30.09)
pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf')); pdfmetrics.registerFont(TTFont('Bold', 'C:/Windows/Fonts/arialbd.ttf'))
(O / 'pdf').mkdir(parents=True, exist_ok=True)
c = Canvas(str(O / 'pdf/P02-R4-PCB.pdf'), pagesize=(297 * mm, 210 * mm)); c.setTitle('EGRLab P02 R4: PCB w formacie S1 (etap 2)')
style = ParagraphStyle('body', fontName='Arial', fontSize=9.5, leading=13, textColor=HexColor('#172833'))
NPAGES = 5


def para(t, x, y, w):
    z = Paragraph(t, style); _, h = z.wrap(w * mm, 170 * mm); z.drawOn(c, x * mm, y * mm - h); return y - h / mm - 4


def start(n, title, subtitle):
    c.setFillColor(HexColor('#117e86')); c.rect(0, 204 * mm, 297 * mm, 6 * mm, fill=1, stroke=0)
    c.setFillColor(HexColor('#172833')); c.setFont('Bold', 18); c.drawString(12 * mm, 190 * mm, title)
    c.setFont('Arial', 9); c.drawString(12 * mm, 182 * mm, subtitle)
    c.setStrokeColor(HexColor('#cdd7dc')); c.line(12 * mm, 14 * mm, 285 * mm, 14 * mm)
    c.setFont('Arial', 8); c.drawString(12 * mm, 9 * mm, 'P02 R4 S1-L S1–S3 | 29–30.09.2026 | etap 2 do recenzji lokalnej | przymiarka 1:1 i odbiór sprzętu: NIE ZBADANO')
    c.drawRightString(285 * mm, 9 * mm, f'{n} / {NPAGES}')


def board(name, x=12, y=40):
    svg = ET.parse(O / 'svg' / (name + '.svg')).getroot(); w = float(svg.attrib['width'].removesuffix('mm')); h = float(svg.attrib['height'].removesuffix('mm'))
    assert abs(w - 160) < .2 and abs(h - 100) < .2, (name, w, h)
    c.drawImage(str(O / 'previews' / (name + '.png')), x * mm, y * mm, w * mm, h * mm, mask='auto')
    c.setStrokeColor(HexColor('#000000')); c.setLineWidth(1.2); c.line(x * mm, (y - 10) * mm, (x + 100) * mm, (y - 10) * mm)
    for xx in (x, x + 100):
        c.line(xx * mm, (y - 13) * mm, xx * mm, (y - 7) * mm)
    c.setFont('Arial', 8.5); c.drawString(x * mm, (y - 17) * mm, 'Belka 100 mm. Drukować 100 %, bez dopasowania do strony; zmierzyć belkę przed przymiarką.')


npass = sum(x['detected'] for x in neg); nel = sum(k['pass'] for k in el['checks'])
start(1, 'P02 R4 — zasilanie z pakietu 4S, PCB w formacie S1', 'Pilot formatu S1: klasa L (160 × 100 mm), sloty S1–S3 poziomu 1 (dystanse 25 mm). Schemat: osobny PDF (5 arkuszy A3).')
y = 172
for t in [f'<b>Płytka:</b> 160 × 100 mm (klasa L), narożniki R1, FR4 1,6 mm, 2 × 35 µm; 12 otworów M3 (NPTH 3,2) według format-s1.json, strefy dystansów Ø7 bez miedzi i części. '
          f'{sum(1 for p in parts.values() if p["on_board"])} części, od spodu {", ".join(bottom)}; najwyższa część {max(p["height_mm"] for p in parts.values() if p["on_board"])} mm (limit 21,5).',
          '<b>Krawędź A:</b> J_BP (IDC 2×10 kątowe, pinout S1 §8) ze środkiem w x = 133,5. <b>Krawędź B:</b> J_SV1 i J_SV2 (goldpin kątowy 1×13, GND na końcach, każdy kołek przez rezystor 1k / 4,7k / 10k przy węźle).',
          '<b>Ściana wejść (x = 160):</b> J1 BAT (kotwa przewodów), J2 VMOTOR (GMSTBA), J15 VBAT_IN. J14 PWR przy lewej krawędzi (przewód do panelu).',
          '<b>Tor 5 A:</b> strefy miedzi J1 → Q9 → SW_COM → Q1 → VSW → F1 → J2 oraz powrót GND po B.Cu w korytarzu bez ścieżek; ≥ 4 mm miedzi wzdłuż całego toru (IPC-2152, 35 µm, ≤ 20 K). Blaszki TO-220 stoją nad miedzią własnej sieci.',
          f'<b>Kontrole:</b> DRC: {len(drc["unconnected_items"])} niepołączonych, {len(drc["schematic_parity"])} niezgodności ze schematem, '
          f'{len(drc["violations"]) - sum(1 for v in drc['violations'] if v['type'] == 'lib_footprint_mismatch')} innych naruszeń; {sum(1 for v in drc['violations'] if v['type'] == 'lib_footprint_mismatch')} zgłoszeń lib_footprint_mismatch u części z przyciętym nadrukiem (przyjęte przez verify_pcb.py); PCB {checks["passed"]}/{checks["total"]}; próby ujemne PCB {npass}/{len(neg)} (z próbą zerową); ERC 0; kontrole elektryczne {nel}/{len(el["checks"])}.',
          f'<b>Otwarte:</b> przymiarka 1:1 (strona 5), wysokości szacunkowe (bezpieczniki MINI, GMSTBA z wtykiem, MKS2), recenzja lokalna; '
          f'{len(silk["hidden_references"])} oznaczeń ukrytych z braku miejsca ({", ".join(silk["hidden_references"])}); paczka produkcyjna poza zakresem.']:
    y = para(t, 12, y, 120)
c.drawImage(str(O / 'previews/isometric.png'), 138 * mm, 30 * mm, 150 * mm, 125 * mm, preserveAspectRatio=True, anchor='c', mask='auto')
para('Render KiCad z modelami bibliotecznymi (C_H leżący i pigtaile bez modeli 3D).', 142, 30, 140)
c.showPage()
pages = [(2, 'Montaż od góry — 1:1', 'assembly', [
    '<b>C12 (C_H 2200 µF)</b> leży: plus przy D2/D1, puszka przyklejona lub przywiązana do płytki.',
    '<b>TO-220 (Q9, Q1, Q2, D1, D2)</b> stoją; nóżki skrócone do 4 mm, blaszka nad miedzią własnej sieci. Bez radiatorów.',
    '<b>R27, R40</b> (PR02) leżą 1 mm nad płytką. Rezystory THT z zakupów P01 stoją; nowe rezystory i ceramika SMD 1206.',
    '<b>Od spodu (S1-2):</b> U9 74LVC125A (SOIC-14, bez adaptera) oraz C27 i C28 (1206) przy jego pinie 14 — lutować przed częściami THT.',
    '<b>R34</b> to zwora z drutu 0,6 mm (PG_SEND–PG_LINK).', 'Wyprowadzenia THT od spodu przyciąć do ≤ 1,5 mm (S1 §4).']),
    (3, 'Miedź F.Cu — 1:1', 'copper-front', [
    'Natywny eksport KiCad po wypełnieniu stref. Szare pola to miedź.',
    '<b>Strefy mocy:</b> BAT_IN (przy J1), SW_COM (między źródłami Q9/Q1), VSW (lewa strona Q1, w dół do F1), VMOTOR (F1 → J2).',
    '<b>Pasy 5 A</b> i paski pod blaszkami TO-220 są obszarami bez ścieżek i przelotek.', 'Wydruk kontrolny, nie plik produkcyjny.']),
    (4, 'Miedź B.Cu — 1:1, widok od spodu', 'copper-back', [
    'Widok od spodu (lustrzany względem strony 3).', '<b>Powrót 5 A:</b> J2.2 → J1.2 w płaszczyźnie GND, w korytarzu bez ścieżek i przelotek przy ścianie wejść.',
    'Pod źródłami Q9/Q1 i pod VSW kopie stref SW_COM i VSW na B.Cu.']),
    (5, 'Przymiarka 1:1 — obrys, obrysy części, otwory', 'fit', [
    'Wydrukować w skali 100 % i położyć na części / w obudowie. Kółka Ø7 wokół otworów M3 to strefy dystansów.',
    '<b>Wysokości (limit 21,5 mm, poziom 1):</b> TO-220 20,5 (nóżki 4 mm), bezpieczniki MINI ok. 17,5 (szacunek), C12 leżący 16,5, GMSTBA z wtykiem ok. 16 (szacunek), elektrolity 11,5–11,7.',
    'Kołki listew J_SV1/J_SV2 wystają ok. 6 mm za krawędź B; J_BP wtyk równo z krawędzią A.'])]
for n, title, name, notes in pages:
    start(n, title, 'Geometria z natywnego pliku PCB; sprawdź belkę 100 mm przed przymiarką.'); board(name)
    yy = 172
    for t in notes:   # klasa L (30.09): the 160 mm board ends at x = 172; notes to the right of it
        yy = para(t, 178, yy, 107)
    c.showPage()
c.save(); print(O / 'pdf/P02-R4-PCB.pdf')
