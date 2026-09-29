"""Review PDF from native KiCad plots; 1:1 board geometry, no reconstructed copper."""
from pathlib import Path
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
import json,hashlib,xml.etree.ElementTree as ET
P=Path(__file__).resolve().parents[1];O=P/'output'
checks=json.loads((P/'verification/pcb-checks.json').read_text());assert checks['passed']==checks['total']
assert checks['board_sha256']==hashlib.sha256((P/'eda/P02.kicad_pcb').read_bytes()).hexdigest()
pdfmetrics.registerFont(TTFont('Arial','C:/Windows/Fonts/arial.ttf'));pdfmetrics.registerFont(TTFont('Bold','C:/Windows/Fonts/arialbd.ttf'))
c=Canvas(str(O/'pdf/P02-R3-PCB.pdf'),pagesize=(297*mm,210*mm));c.setTitle('EGRLab P02-R3: PCB, rewizja zamykajaca')
style=ParagraphStyle('body',fontName='Arial',fontSize=10,leading=14,textColor=HexColor('#172833'))
def para(t,x,y,w):
 z=Paragraph(t,style);_,h=z.wrap(w*mm,160*mm);z.drawOn(c,x*mm,y*mm-h);return y-h/mm-5
def start(n,title,sub):
 c.setFillColor(HexColor('#117e86'));c.rect(0,204*mm,297*mm,6*mm,fill=1,stroke=0)
 c.setFillColor(HexColor('#172833'));c.setFont('Bold',19);c.drawString(12*mm,188*mm,title)
 c.setFont('Arial',9);c.drawString(12*mm,178*mm,sub)
 c.setStrokeColor(HexColor('#cdd7dc'));c.line(12*mm,14*mm,285*mm,14*mm)
 c.setFont('Arial',8);c.drawString(12*mm,9*mm,'P02-R3 | 26.09.2026 | PROJEKT ZAMKNIĘTY | przymiarka i pomiary sprzętu: NIE ZBADANO')
 c.drawRightString(285*mm,9*mm,f'{n} / 5')
def image(name,x,y,w,h):c.drawImage(str(O/'previews'/name),x*mm,y*mm,w*mm,h*mm,preserveAspectRatio=True,anchor='c',mask='auto')
def board(name):
 svg=ET.parse(O/'svg'/(name+'.svg')).getroot();w=float(svg.attrib['width'].removesuffix('mm'));h=float(svg.attrib['height'].removesuffix('mm'))
 assert abs(w-160)<.1 and abs(h-120)<.1,(w,h)
 image(name+'.png',12,44,w,h)
 c.setStrokeColor(HexColor('#000000'));c.setLineWidth(1.2);c.line(12*mm,32*mm,112*mm,32*mm)  # R3: black bar (R2: light grey, hard to print)
 for x in [12,112]:c.line(x*mm,29*mm,x*mm,35*mm)
 c.setFont('Arial',9);c.drawString(12*mm,24*mm,'Belka 100 mm. Druk 100%, bez dopasowania.')
start(1,'P02 PSU + HOLD / rewizja R3 (zamykająca)','R3 = R2 Astry + recenzja Claude P2-01…P2-08; miedź i rozmieszczenie jak w R2. Schemat: osobny PDF, cztery arkusze A3.')
y=163
for t in ['<b>Poprawione:</b> progi z tolerancjami, filtry przed sprzężeniem, zabezpieczony TP3 i czytelność schematu.',
 '<b>PCB:</b> 160×120 mm, FR4 1,6 mm, dwie warstwy miedzi 70 µm. 72 części na PCB i cztery otwory M3.',
 '<b>Kontrole:</b> ERC 0; DRC 0/0/0; 208 pinów zgodnych ze schematem. Testy dodatkowe opisano w verification/QA.md.',
 '<b>HOLD_READY:</b> lokalny wskaźnik napięciowy. 15 s kwalifikuje operator. Brak połączenia z CORE/P04.',
 '<b>Bezpieczniki R3:</b> Schurter SPT 5×20, 300 VDC: F1 T2A, F2/F3 T1A (zwłoczne, jak zaleca TRACO), F4 T0,5A. LED1 przez 470 Ω.',
 '<b>Otwarte:</b> przymiarka części, odbiór pod obciążeniem i pomiary według verification/ODBIOR.md. Gerbery po przymiarce.']:
 y=para(t,12,y,111)
image('isometric.png',130,31,155,137);para('Modele gabarytowe. Wtyki pokazano jako obwiednie; bez obejm banku i obudowy.',134,34,145)
c.showPage()
pages=[(2,'Montaż z góry — 1:1','assembly',[
 '<b>R18/R19:</b> przy U7; oddzielają C14/C15 od dodatniego sprzężenia. Nie zwierać ich zworami.',
 '<b>R20 i TP3:</b> górny lewy obszar banku. TP3 ma opis BANK/1k. Zmierz rezystancję 1 kΩ do HOLD_STORE przed uruchomieniem.',
 '<b>U5:</b> 18×18 mm adapter, rzędy 15,24 mm. C16 lutowany na adapterze. C11 pozostaje na płycie.',
 '<b>Bank:</b> plus na dolnym padzie, minus ku górnej krawędzi. Podparcie puszek do obudowy i osłona lutów od spodu.',
 '<b>R17:</b> poza PCB. J13 to lutowane przewody do rezystora 47 Ω/25 W na oddzielnej blasze.']),
 (3,'Spód płytki — 1:1','bottom',[
 'Widok bezpośrednio od spodu, odbity względem góry. Nie używać jako rysunku miedzi od góry.',
 '<b>Osłona banku:</b> przykryć surowe luty C1–C3 i ich szynę izolującą osłoną. TP3 jest chroniony, te luty pozostają bezpośrednio połączone z bankiem.',
 'Sprawdzić długość końcówek nad podstawą obudowy. Dystanse M3 muszą przenosić masę modułu; nie obciążać lutów puszek.',
 'Kotwy J1/J12/J13 są 12,5 mm od lutów. Przewody mają być odciążone przed poruszeniem wtykiem.',
 'Po odłączeniu zasilania zmierzyć TP3. Bleeder może potrzebować około 22 min do 1 V.']),
 (4,'Miedź F.Cu — 1:1','copper-front',[
 'Natywny eksport KiCad, po wypełnieniu stref. Jasnoszare pola to miedź, czarne linie to ścieżki.',
 '<b>VPROT:</b> strefa przy J1/J2. Tor VMOTOR pozostaje bez podtrzymania bankiem.',
 '<b>Bank:</b> gruba szyna i krótkie odgałęzienia. R6 ogranicza prąd długiego toru pomiarowego; R20 chroni TP3.',
 '<b>Filtry:</b> kondensatory na węzłach DIV; osobne węzły CMP po R18/R19. Sprzężenie R8/R11 trafia do CMP.',
 'Wydruk kontrolny, nie plik produkcyjny. Pliki Gerber nie są częścią tego wydania.']),
 (5,'Miedź B.Cu — 1:1','copper-back',[
 'Widok od spodu, orientacja taka sama jak na stronie 3.',
 '<b>Powrót 5 A:</b> korytarz masy między J2.2 a J1.2 chroniony przed ścieżkami i przelotkami.',
 'Spójność płaszczyzny masy sprawdza skrypt. DRC nie zastępuje pomiaru temperatury i spadku napięcia.',
 '<b>U5.9/U5.12:</b> pełne połączenie z masą zamiast niekompletnych termików; dobrać temperaturę lutowania do pola miedzi.',
 'Odbiór i przebiegi: verification/ODBIOR.md. Zmiany R3: docs/ZMIANY-R3.md; historia R2: docs/ODPOWIEDZ-NA-RECENZJE.md.'])]
for n,title,name,notes in pages:
 start(n,title,'Geometria z natywnego pliku PCB; sprawdź belkę kontrolną przed przymiarką.');board(name);y=164
 for t in notes:y=para(t,184,y,101)
 c.showPage()
c.save();print(O/'pdf/P02-R3-PCB.pdf')
