"""Review PDF of the P04 R3 PCB (format S1, class L): native KiCad plots at 1:1 (A4 landscape), no redrawn copper (P03 R6 / P05 R3 pattern).
Pages: 1 overview, 2 assembly top, 3 F.Cu, 4 B.Cu (seen from below), 5 fit print 1:1 (outline, courtyards, holes, heights).
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
from heights import HEIGHTS
from board import NAME, REV, CLASS, SLOTS, DATE
TYTUL = f"{REV} S1-{CLASS} {SLOTS[0]}-{SLOTS[-1]}"
checks = json.loads((P / 'verification/pcb-checks.json').read_text(encoding='utf-8')); assert checks['passed'] == checks['total']
assert checks['board_sha256'] == hashlib.sha256((P / f'eda/{NAME}.kicad_pcb').read_bytes()).hexdigest()
neg = json.loads((P / 'verification/negative-controls.json').read_text(encoding='utf-8'))
parts = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
drc = json.loads((P / 'verification/drc.json').read_text(encoding='utf-8')); silk = json.loads((P / 'routing/silkscreen.json').read_text(encoding='utf-8'))
det = checks['details']
supn = next(v for k, v in det.items() if k.startswith('SUP_N_OUT short'))
pw = next(v for k, v in det.items() if k.startswith('Supply nets'))
wd = next(v for k, v in det.items() if k.startswith('Watchdog RC'))
dec = next(v for k, v in det.items() if k.startswith('Decoupling at the IC'))
bottom = sorted(r for r, v in json.loads((P / 'src/placement.json').read_text(encoding='utf-8')).items() if len(v) > 3 and v[3] == 'B')
nlib = sum(1 for v in drc['violations'] if v['type'] == 'lib_footprint_mismatch')
pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf')); pdfmetrics.registerFont(TTFont('Bold', 'C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Bold', italic='Arial', boldItalic='Bold')
(O / 'pdf').mkdir(parents=True, exist_ok=True)
PDF = O / f"pdf/{REV.replace(' ', '-')}-PCB.pdf"
c = Canvas(str(PDF), pagesize=(297 * mm, 210 * mm)); c.setTitle(f'EGRLab {REV}: PCB SAFE w formacie S1')
style = ParagraphStyle('body', fontName='Arial', fontSize=9.5, leading=13, textColor=HexColor('#172833'))
NPAGES = 5
D = '.'.join(reversed(DATE.split('-')))


def pl(v):
    return str(v).replace('.', ',')


def para(t, x, y, w):
    z = Paragraph(t, style); _, h = z.wrap(w * mm, 170 * mm); z.drawOn(c, x * mm, y * mm - h); return y - h / mm - 4


def start(n, title, subtitle):
    c.setFillColor(HexColor('#117e86')); c.rect(0, 204 * mm, 297 * mm, 6 * mm, fill=1, stroke=0)
    c.setFillColor(HexColor('#172833')); c.setFont('Bold', 18); c.drawString(12 * mm, 190 * mm, title)
    c.setFont('Arial', 9); c.drawString(12 * mm, 182 * mm, subtitle)
    c.setStrokeColor(HexColor('#cdd7dc')); c.line(12 * mm, 14 * mm, 285 * mm, 14 * mm)
    c.setFont('Arial', 8); c.drawString(12 * mm, 9 * mm, f'{TYTUL} | {D} | PCB do recenzji lokalnej | przymiarka 1:1 i odbiór sprzętu: NIE ZBADANO')
    c.drawRightString(285 * mm, 9 * mm, f'{n} / {NPAGES}')


def board(name, x=12, y=40):
    svg = ET.parse(O / 'svg' / (name + '.svg')).getroot(); w = float(svg.attrib['width'].removesuffix('mm')); h = float(svg.attrib['height'].removesuffix('mm'))
    assert abs(w - 160) < .2 and abs(h - 100) < .2, (name, w, h)
    c.drawImage(str(O / 'previews' / (name + '.png')), x * mm, y * mm, w * mm, h * mm, mask='auto')
    c.setStrokeColor(HexColor('#000000')); c.setLineWidth(1.2); c.line(x * mm, (y - 10) * mm, (x + 100) * mm, (y - 10) * mm)
    for xx in (x, x + 100):
        c.line(xx * mm, (y - 13) * mm, xx * mm, (y - 7) * mm)
    c.setFont('Arial', 8.5); c.drawString(x * mm, (y - 17) * mm, 'Belka 100 mm. Drukować 100 %, bez dopasowania do strony; zmierzyć belkę przed przymiarką.')


def liczba(n, f1, f2, f5):
    return f'{n} ' + (f1 if n == 1 else f2 if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14 else f5)


npass = sum(x['detected'] for x in neg)
onboard = [r for r in parts if parts[r].get('on_board', True)]
hmax = max((HEIGHTS.get(r, HEIGHTS.get(parts[r]['footprint']))[0], r) for r in onboard)
hidden = silk['hidden_references']
worst = max(dec.items(), key=lambda kv: kv[1]['supply_path_mm'])
start(1, f'{REV} — SAFE, PCB w formacie S1', 'Klasa L (160 × 100 mm), sloty S1–S3 poziomu 6 (dystanse 20 mm). Schemat: osobny PDF (P04-R3-schemat.pdf, 7 arkuszy).')
y = 172
for t in [f'<b>Płytka:</b> 160 × 100 mm (klasa L), narożniki R1, FR4 1,6 mm, 2 × 35 µm; 12 otworów M3 (NPTH 3,2) według format-s1.json, strefy dystansów Ø7 '
          f'bez miedzi i części. {len(onboard)} części, wszystkie od góry{(" (od spodu: " + ", ".join(bottom) + ")") if bottom else ""}; najwyższa {hmax[1]} '
          f'{pl(hmax[0])} mm (limit nad poziomem 6: 16,5 mm). U1–U7 DIP w podstawkach, U8–U10 SOIC-14 lutowane wprost.',
          '<b>Krawędź A:</b> J_BP1 (IDC 2×8), J_BP2 i J_BP3 (IDC 2×10), środki x = 26,5 / 80 / 133,5, pin 1 od mniejszego x, nieparzyste GND; pinout docs/J_BP.csv. '
          '<b>Krawędź B:</b> J_SV1 (1×13), J_SV2 i J_SV3 (1×7), GND na końcach, każdy kołek przez rezystor przy węźle (1 kΩ; SAFE_N i ARM_BUTTON_N 10 kΩ); docs/SERWIS.csv.',
          f'<b>Zasilanie (≥ 0,4 mm):</b> 3V3_IO, P04_3V3, PANEL_3V3, 5V_SYS — najwęższa ścieżka {pl(min(v["min_width_mm"] for v in pw.values()))} mm. Piny zasilania '
          'w parzystym rzędzie J_BP2 / J_BP3 wychodzą po B.Cu w stronę krawędzi A (między pinami GND mieści się tylko 0,3 mm) i obchodzą koniec złącza.',
          f'<b>SUP_N_OUT</b> (reset z P03): J_BP3.12 → U9.5 {pl(supn["copper_mm"])} mm miedzi, {supn["vias"]} przelotka, między pinami GND 11 / 13, masa pod '
          f'{pl(supn["gnd_reference_percent"])} % długości. <b>Watchdog:</b> WD_RC {pl(wd["WD_RC"]["length_mm"])} mm, WD_C {pl(wd["WD_C"]["length_mm"])} mm, F.Cu bez przelotek. '
          f'<b>Odsprzęganie:</b> 100 nF przy każdym układzie, najdalej {worst[0]} {pl(worst[1]["supply_path_mm"])} mm miedzi od pinu VCC.',
          f'<b>Kontrole:</b> DRC: {len(drc["unconnected_items"])} niepołączonych, {len(drc["schematic_parity"])} niezgodności ze schematem, '
          f'{len(drc["violations"]) - nlib} innych naruszeń'
          + (f'; {liczba(nlib, "zgłoszenie", "zgłoszenia", "zgłoszeń")} lib_footprint_mismatch u części z przyciętym nadrukiem (przyjęte po porównaniu pól z biblioteką)' if nlib else '')
          + f'; PCB {checks["passed"]}/{checks["total"]}; próby ujemne PCB {npass}/{len(neg)} (z próbą zerową).',
          '<b>Otwarte:</b> przymiarka 1:1 (strona 5; C1 MKS2 ok. 13 mm pod pokrywą), recenzja lokalna; '
          f'{liczba(len(hidden), "oznaczenie ukryte", "oznaczenia ukryte", "oznaczeń ukrytych")} z braku miejsca'
          f'{(" (" + ", ".join(hidden) + "; na rysunku montażowym z warstwy F.Fab)") if hidden else ""}.']:
    y = para(t, 12, y, 120)
c.drawImage(str(O / 'previews/isometric.png'), 138 * mm, 30 * mm, 150 * mm, 125 * mm, preserveAspectRatio=True, anchor='c', mask='auto')
para('Render KiCad bez modeli 3D części (obraz Dockera nie ma biblioteki modeli KiCad).', 142, 30, 140)
c.showPage()
pages = [(2, 'Montaż od góry — 1:1', 'assembly', [
    '<b>U1–U7</b> (DIP-14 / DIP-16) w podstawkach, <b>U8–U10</b> SOIC-14 lutowane wprost (decyzja 5.10), C15–C17 na płytce. Rezystory i 100 nF: SMD 1206, wszystko od góry.',
    '<b>C1</b> (MKS2 1 µF / 100 V) przy U1.15 / U1.14 z R1 220 kΩ nad nim; <b>C18</b> (1 nF) i R5 przy U2.11; Q1–Q3 (kolektory na SAFE_N) obok U2.',
    '<b>Listwy serwisowe:</b> pełne nazwy węzłów (do 7 znaków) pionowo nad kołkami, GND przy pierwszym i ostatnim kołku.',
    'Wyprowadzenia THT od spodu przyciąć do ≤ 1,5 mm (S1 §4).']),
    (3, 'Miedź F.Cu — 1:1', 'copper-front', [
    'Natywny eksport KiCad po wypełnieniu stref. Szare pola to miedź (GND).',
    'Pod każdym J_BP grzebień GND (piny nieparzyste) na F.Cu; bez miedzi wokół otworów M3 (Ø7).', 'Wydruk kontrolny, nie plik produkcyjny.']),
    (4, 'Miedź B.Cu — 1:1, widok od spodu', 'copper-back', [
    'Widok od spodu (lustrzany względem strony 3).',
    '<b>Wyjścia zasilania</b> 0,4 mm z J_BP2.10 / .14 i J_BP3.8 / .10 pod korpusem złącza (pas przy krawędzi A) do końca złącza; SUP_N_OUT z J_BP3.12 między pinami GND do przelotki przy U9.']),
    (5, 'Przymiarka 1:1 — obrys, obrysy części, otwory', 'fit', [
    'Wydrukować w skali 100 % i położyć na części / w obudowie. Kółka Ø7 wokół otworów M3 to strefy dystansów.',
    f'<b>Wysokości (limit 16,5 mm nad poziomem 6):</b> C1 ok. {pl(HEIGHTS[parts["C1"]["footprint"]][0])} mm, C3 ok. {pl(HEIGHTS[parts["C3"]["footprint"]][0])} mm, '
    f'C2 ok. {pl(HEIGHTS[parts["C2"]["footprint"]][0])} mm, IDC ok. 9,2 mm, DIP w podstawkach ok. 8,5 mm (szacunek).',
    'Kołki listew J_SV wystają ok. 6 mm za krawędź B (rysunek obejmuje tylko płytkę 160 × 100 mm); J_BP wtyk równo z krawędzią A.'])]
for n, title, name, notes in pages:
    start(n, title, 'Geometria z natywnego pliku PCB; sprawdź belkę 100 mm przed przymiarką.'); board(name)
    yy = 172
    for t in notes:
        yy = para(t, 178, yy, 107)
    c.showPage()
c.save(); print(PDF)
