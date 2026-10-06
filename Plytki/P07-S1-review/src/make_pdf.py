"""Review PDF of the P07 S1 PCB (format S1, class 2/3): native KiCad plots at 1:1 (A4 landscape), no redrawn copper (P03 R6 / P09 R2 / P10 R2 pattern).
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
kel = next(v for k, v in det.items() if k.startswith('Kelvin pair'))
dcp = next(v for k, v in det.items() if k.startswith('Decoupling at the pins'))
force = next(v for k, v in det.items() if k.startswith('Force pours VMOTOR'))
bottom = sorted((r for r, v in json.loads((P / 'src/placement.json').read_text(encoding='utf-8')).items() if len(v) > 3 and v[3] == 'B'),
                key=lambda r: (r[0], int(''.join(ch for ch in r if ch.isdigit()))))
nlib = sum(1 for v in drc['violations'] if v['type'] == 'lib_footprint_mismatch')
pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf')); pdfmetrics.registerFont(TTFont('Bold', 'C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Bold', italic='Arial', boldItalic='Bold')   # 30.09: <b> in the notes printed as regular without it
(O / 'pdf').mkdir(parents=True, exist_ok=True)
PDF = O / f"pdf/{REV.replace(' ', '-')}-PCB.pdf"
c = Canvas(str(PDF), pagesize=(297 * mm, 210 * mm)); c.setTitle(f'EGRLab {REV}: PCB DRIVE w formacie S1')
style = ParagraphStyle('body', fontName='Arial', fontSize=9.5, leading=13, textColor=HexColor('#172833'))
NPAGES = 7


def para(t, x, y, w):
    z = Paragraph(t, style); _, h = z.wrap(w * mm, 170 * mm); z.drawOn(c, x * mm, y * mm - h); return y - h / mm - 4


def start(n, title, subtitle):
    c.setFillColor(HexColor('#117e86')); c.rect(0, 204 * mm, 297 * mm, 6 * mm, fill=1, stroke=0)
    c.setFillColor(HexColor('#172833')); c.setFont('Bold', 18); c.drawString(12 * mm, 190 * mm, title)
    c.setFont('Arial', 9); c.drawString(12 * mm, 182 * mm, subtitle)
    c.setStrokeColor(HexColor('#cdd7dc')); c.line(12 * mm, 14 * mm, 285 * mm, 14 * mm)
    c.setFont('Arial', 8); c.drawString(12 * mm, 9 * mm, f'{TYTUL} | 05.10.2026 | PCB (layout lokalny) | przymiarka 1:1 i odbiór sprzętu: NIE ZBADANO')
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
start(1, f'{REV} — DRIVE pod moduł IBT-2 (KPWR, bocznik 5 mΩ, INA240), PCB w formacie S1',
      'Klasa 2/3 (106,5 × 100 mm), sloty S2–S3 poziomu 5 (dystanse 20 mm). Schemat: osobny PDF (P07-S1-schemat.pdf, 8 arkuszy A3).')
y = 172
fx = lambda v: str(v).replace('.', ',')
for t in [f'<b>Płytka:</b> 106,5 × 100 mm (klasa 2/3), narożniki R1, 4 warstwy JLC04161H-7628 1,6 mm (zewnętrzne 35 µm, wewnętrzne 15 µm; In1 masa, In2 sygnały + zasilania); 8 otworów M3 (NPTH 3,2) według format-s1.json, strefy dystansów Ø7 '
          f'bez miedzi i części. {len(onboard)} części; od spodu {len(bottom)} SMD ≤ 1,5 mm; najwyższa {", ".join(tall)} {fx(hmax)} mm (limit 16,5 mm).',
          '<b>Krawędź A:</b> J_BP1 (S2, x = 26,5) i J_BP2 (S3, x = 80,0), IDC 2×8, pinout docs/J_BP.csv, pin 1 od mniejszego x. '
          '<b>Krawędź B:</b> jedna listwa J_SV2 (slot S3, 12 kołków: szyny, KPWR, SAFE_OK, łańcuch OC, DRIVE_OK, ITEST — uproszczenie 6.10), GND na końcach, rezystory przy węzłach (docs/SERWIS.csv). '
          '<b>Strona panelu (x = 0):</b> J1 VMOTOR, J2 B+/B−, J3 M+/M−, J4 TEST (2 × 2,0 mm² każde), przewody lutowane, kotwy opasek 12 mm za polami. '
          '<b>J5</b> (obudowane IDC 2×4 kątowe) przy krawędzi x = 106,5 — taśma 8 żył do modułu.',
          '<b>Tor 10 A:</b> VMOTOR, MOD_BP, MOD_MP, T_EGR_P1 / P3 i PGND jako wylewki na obu warstwach (≥ 4 mm, zszyte przelotkami); styki K1 (COM / NO) '
          'na wysokości J1.1 / J2.1, PGND łączy J2.2 i J1.2 pasem między kotwami a polami. GND i PGND rozdzielone (wspólny punkt na P02 R4); cewka K1 5 V z 5V_SYS w domenie GND. '
          f'<b>Kelvin:</b> z pól pomiarowych RSH1 przez R6 / R7 do U1 (INA240), tylko F.Cu, bez przelotek (drogi: K_PLUS {fx(kel["K_PLUS"]["path_mm"])} mm, '
          f'K_MINUS {fx(kel["K_MINUS"]["path_mm"])} mm). Pod bocznikiem od spodu nic (strefa zakazana).',
          f'<b>U2</b> (MCP1525): C5 {fx(dcp["C5-U2.2"][0])} mm od wyjścia (karta: ≤ 5 mm); 100 nF przy każdym układzie (≤ 6 mm).',
          f'<b>Kontrole:</b> DRC: {len(drc["unconnected_items"])} niepołączonych, {len(drc["schematic_parity"])} niezgodności ze schematem, '
          f'{len(drc["violations"]) - nlib} innych naruszeń'
          + (f'; {liczba(nlib, "zgłoszenie", "zgłoszenia", "zgłoszeń")} lib_footprint_mismatch u części z przyciętym nadrukiem (przyjęte przez verify_pcb.py)' if nlib else '')
          + f'; PCB {checks["passed"]}/{checks["total"]}; próby ujemne PCB {npass}/{len(neg)} (z próbą zerową).',
          '<b>Otwarte:</b> przymiarka 1:1 (strona 5: końcówki przewodów przy x = 0, K1 15,7 mm, C1 stojący), grubość kondensatorów od spodu (BOM ≤ 1,5 mm); '
          f'{liczba(len(hidden), "oznaczenie ukryte", "oznaczenia ukryte", "oznaczeń ukrytych")} z braku miejsca'
          f'{(" (na rysunku montażowym z warstwy F.Fab)") if hidden else ""}; pomiary modułu D1 / E2 / E3 przy odbiorze.']:
    y = para(t, 12, y, 120)
c.drawImage(str(O / 'previews/isometric.png'), 138 * mm, 30 * mm, 150 * mm, 125 * mm, preserveAspectRatio=True, anchor='c', mask='auto')
para('Render KiCad bez modeli 3D części (obraz Dockera nie ma biblioteki modeli KiCad).', 140, 30, 140)
c.showPage()
pages = [(2, 'Montaż od góry — 1:1', 'assembly', [
    '<b>Kolejność lutowania:</b> najpierw spód (rezystory listew i części przy węzłach, R4 2512 pod K1 — grubość kondensatorów ≤ 1,5 mm), potem góra (S1-2).',
    '<b>RSH1</b> (WSK2512, 4 pola): pola pomiarowe 2 / 3 na przekątnej; lutować bez nadmiaru cyny na polach prądowych. SOIC wprost; U6 (MCP3201) w podstawce '
    '(opcjonalnie), TO-92, K1 i C1 od góry.',
    '<b>J1–J4:</b> przewody 2,0 mm² lutowane do otworów (opisy VM / PG, B+ / B−, M+ / M−, P1 / P3 obok pól), opaska na izolacji przez dwa otwory kotwy. '
    '<b>J5:</b> wycięcie klucza obudowy ustala orientację gniazda taśmy (pin 1 = RPWM).']),
    (3, 'Miedź F.Cu — 1:1', 'copper-front', [
    'Natywny eksport KiCad po wypełnieniu stref. Szare pola to miedź: GND oraz wylewki toru 10 A i PGND przy x = 0.',
    '<b>Bocznik:</b> MOD_MP dochodzi do górnego pola prądowego z prawej, T_EGR_P1 do dolnego od lewej i od dołu; K_PLUS z lewego górnego pola pomiarowego w dół i pod '
    'korpusem w prawo, K_MINUS z prawego dolnego pola w prawo. <b>Bez miedzi</b> wokół otworów M3 (Ø7) i kotw opasek (3 mm).',
    'Wydruk kontrolny, nie plik produkcyjny.']),
    (4, 'Miedź B.Cu — 1:1, widok od spodu', 'copper-back', [
    'Widok od spodu (lustrzany względem strony 3). B.Cu to głównie masa GND; przy x = 0 druga warstwa wylewek toru 10 A i PGND, pod bocznikiem pusto.']),
    (5, 'Miedź In1.Cu — 1:1 (płaszczyzna masy)', 'copper-in1', [
    'Warstwa wewnętrzna 1 (0,5 oz): ciągła masa GND pod logiką, łańcuchem analogowym i parą Kelvina; pod blokiem mocy osobny obszar PGND (masy łączą się tylko na P02 R4).']),
    (6, 'Miedź In2.Cu — 1:1 (sygnały i zasilania)', 'copper-in2', [
    'Warstwa wewnętrzna 2 (0,5 oz): część ścieżek sygnałowych i strefy zasilań 3V3A_P07 (ADC), 5VA_P07 (INA240 / okno OC) i 3V3_IO (logika); pod blokiem mocy nic. Tor 10 A tylko na warstwach zewnętrznych.']),
    (7, 'Przymiarka 1:1 — obrys, obrysy części, otwory', 'fit', [
    'Wydrukować w skali 100 % i położyć na części / w obudowie. Kółka Ø7 wokół otworów M3 to strefy dystansów.',
    f'<b>Wysokości (limit 16,5 mm, poziom 5):</b> K1 {fx(h_of("K1"))} mm, C1 ok. {fx(h_of("C1"))} mm, IDC ok. 9,2 mm, '
    'DIP w podstawce ok. 8 mm, TO-92 ok. 7 mm (szacunek).',
    'Kołki listew J_SV wystają ok. 6 mm za krawędź B; J_BP wtyk równo z krawędzią A; przewody J1–J4 wychodzą za krawędź x = 0, taśma J5 za krawędź x = 106,5.'])]
for n, title, name, notes in pages:
    start(n, title, 'Geometria z natywnego pliku PCB; sprawdź belkę 100 mm przed przymiarką.'); board(name)
    yy = 172
    for t in notes:
        yy = para(t, 128, yy, 157)
    c.showPage()
c.save(); print(PDF)
