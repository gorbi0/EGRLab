"""Five-page review document. Raster CAD plots at ~762 dpi, exact SVG millimetres."""
from pathlib import Path
import json,xml.etree.ElementTree as ET
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor,black,white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
P=Path(__file__).resolve().parents[1];O=P/'output/pdf';O.mkdir(exist_ok=True)
pdfmetrics.registerFont(TTFont('Arial','C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold','C:/Windows/Fonts/arialbd.ttf'))
ink=HexColor('#172b3a');teal=HexColor('#087c83');muted=HexColor('#576772');light=HexColor('#eef4f6')
styles={k:ParagraphStyle(k,fontName='Arial',fontSize=size,leading=size*1.38,textColor=ink) for k,size in [('body',10),('small',8.8)]}
styles['body'].spaceAfter=4
W,H=landscape(A4);c=canvas.Canvas(str(O/'P01-PCB-R1-dokumentacja.pdf'),pagesize=(W,H))
c.setTitle('EGRLab P01 - PCB R1 - dokumentacja do przeglądu');c.setAuthor('EGRLab / Codex')
def text(s,x,y,size=10,bold=False,color=ink):
 c.setFillColor(color);c.setFont('Arial-Bold' if bold else 'Arial',size);c.drawString(x*mm,y*mm,s)
def para(s,x,y,w,small=False):
 q=Paragraph(s,styles['small' if small else 'body']);_,h=q.wrap(w*mm,180*mm);q.drawOn(c,x*mm,y*mm-h);return y-h/mm-3
def head(n,title,sub):
 c.setFillColor(teal);c.rect(0,H-7*mm,W,7*mm,fill=1,stroke=0)
 text(title,17,185,21,True);text(sub,17,175,10,color=muted)
 c.setStrokeColor(HexColor('#c4d1d8'));c.line(17*mm,16*mm,280*mm,16*mm)
 text('EGRLab | P01-PCB-R1-review | SCH R3 | 23.09.2026',17,10,8,color=muted)
 text(f'{n} / 5',268,10,8,color=muted)
def finish():c.showPage()
def section(s,x,y):text(s,x,y,11,True,teal);return y-5
def plot(name,x,y,scale=1):
 r=ET.parse(P/'output/previews'/f'{name}.svg').getroot()
 width=float(r.get('width').removesuffix('mm'));height=float(r.get('height').removesuffix('mm'))
 assert abs(width-160.1)<.001 and abs(height-120.1)<.001,(width,height)
 c.drawImage(str(P/'output/previews'/f'{name}-print.png'),x*mm,y*mm,width=width*scale*mm,height=height*scale*mm)
 return width,height
def scale_bar():
 c.setStrokeColor(black);c.setLineWidth(.4);c.line(20*mm,27*mm,120*mm,27*mm)
 for x in [20,120]:c.line(x*mm,25*mm,x*mm,29*mm)
 text('Belka kontrolna: dokładnie 100 mm',20,21,8)
def dimensions():
 c.setStrokeColor(muted);c.setLineWidth(.4)
 c.line(16.05*mm,39*mm,176.05*mm,39*mm)
 for x in [16.05,176.05]:c.line(x*mm,37.8*mm,x*mm,40.2*mm)
 text('160 mm',87,33.5,8)
 c.line(11*mm,43.05*mm,11*mm,163.05*mm)
 for y in [43.05,163.05]:c.line(9.8*mm,y*mm,12.2*mm,y*mm)
 c.saveState();c.translate(7.5*mm,93*mm);c.rotate(90);c.setFont('Arial',8);c.drawString(0,0,'120 mm');c.restoreState()

head(1,'P01: pierwsza płytka do przeglądu','Zamrożony schemat R3 + wykonany layout dwuwarstwowy')
for x,a,v in [(17,'FORMAT PCB','160 × 120 mm'),(107,'TECHNOLOGIA','2L / FR4 1,6 / Cu70'),(197,'KONTROLA KICAD','DRC 0 / połączenia 0')]:
 c.setFillColor(light);c.roundRect(x*mm,140*mm,83*mm,25*mm,3*mm,fill=1,stroke=0)
 text(a,x+5,157,8,True,muted);text(v,x+5,146,14,True)
y=section('Co zostało wykonane',17,130)
y=para('Rozmieszczenie 89 elementów elektrycznych, dwóch radiatorów i czterech otworów montażowych. Ścieżki, pola GND, odczepy Kelvin, opisy i numeracja złączy są zapisane w natywnej PCB KiCad.',17,y,123)
y=para('17 kontroli PCB: PASS. Trzy celowe usterki w osobnych kopiach zostały wykryte. Schemat i geometria padów R3 zachowane; brak wyłączeń DRC.',17,y,123)
plot('assembly',22,22,.60)
y=section('Zmiana względem założenia R3',158,130)
y=para('Wysokość wzrosła ze 100 do <b>120 mm</b>, aby zmieścić duże THT, radiatory i odciążenie wiązek. Dolny rząd otworów M3: <b>Y=115 mm</b>. Uwzględnij to w obudowie.',158,y,122)
y=section('Co wymaga rzeczywistych części',158,y-4)
y=para('<b>Przymiarka 1:1, termika, SOA i odbiór elektryczny nie zostały wykonane.</b> Czysty DRC potwierdza reguły i połączenia, nie zachowanie układu pod obciążeniem.',158,y,122)
y=para('Wydrukuj stronę 2 w 100%. Po przymiarce i przeglądzie następuje eksport Gerber/Excellon, zamówienie i odbiór samej P01. Pakiet nie zawiera eksportu do zamawiania.',158,y,122)
para('<b>P07 pozostaje HOLD</b> do sprawdzenia modułu BTS7960. P02-HOLD i firmware systemu nie są zmieniane w tym etapie.',158,y-2,122)
finish()

head(2,'Montaż 1:1','Strona elementów. Druk 100%; wyłącz dopasowanie i skalowanie drukarki.')
plot('assembly',16,43);dimensions();scale_bar()
y=section('Przymiarka',188,162)
for s in ['Zmierz belkę 100 mm i obrys 160 × 120 mm przed przykładaniem części.',
 'M3: Ø3,2 mm; środki (5;5), (155;5), (5;115), (155;115). Współrzędne od lewego górnego rogu PCB.',
 'HS1/HS2: SK129-63STS, 42 × 25 mm, wysokość 63,5 mm + prześwit. Sprawdź dojście TO-220 do radiatora z izolacją.',
 'C6: WIMA MKS2 1 µF/100 V, korpus 7,2 × 7,2 mm, raster 5 mm.',
 'Pełne obrysy F.Fab są na tej stronie. Nadruk PCB jest uproszczony; zachowuje oznaczenia elementów.',
 'P01 nie ma jeszcze fizycznego prototypu. Formularz: docs/MECHANIKA.md.']:
 y=para(s,188,y,92,True)
finish()

head(3,'Miedź F.Cu 1:1','Widok od strony elementów. Czarne obszary oznaczają miedź.')
plot('copper-front',16,43);dimensions();scale_bar()
y=section('Tor mocy i pomiary',188,162)
for s in ['Duże odcinki mocy mają 5 mm; dojścia do TO-220 i padów mają miejscami 2 mm. Nie przyjęto ciągłego toru 5 mm na obu stronach.',
 'J7: cztery ramiona termiczne 1,2 mm i szczelina 0,3 mm na każdym padzie, na obu warstwach. Sprawdzono wypełnioną miedź.',
 'LK1: dwa osobne pola mocy i dwa odczepy sense. Nie ma ścieżki omijającej zdejmowaną zworę.',
 'TP1 do SOURCE Q1: 4,805 mm. TP2 do GATE Q1: 4,719 mm. Nie podłączać masy oscyloskopu do SOURCE.',
 'To widok kontrolny layoutu. Nie jest maską do samodzielnego trawienia ani plikiem produkcyjnym.']:
 y=para(s,188,y,92,True)
finish()

head(4,'Miedź B.Cu 1:1','Widok przez PCB od strony elementów - bez odbicia lustrzanego.')
plot('copper-back',16,43);dimensions();scale_bar()
y=section('Powrót prądu',188,162)
for s in ['GND ma pola na obu warstwach. Szeroki powrót mocy biegnie górą i prawym bokiem PCB, powyżej części odniesienia.',
 'VS ma równoległy fragment F.Cu/B.Cu i trzy przelotki Ø1,2/0,6 mm. PTH D2 oraz Q1 są częścią toru mocy.',
 'Pady radiatorów pozostają poza sieciami elektrycznymi. Nie służą jako punkty GND; wymagają kontroli izolacji po montażu.',
 'Przykład rachunku Cu70: 20 mm × 2 mm to ok. 2,5 mΩ i 62,5 mW przy 5 A. Nie obejmuje PTH, termików, lutów i elementów.',
 'Kwalifikacja 5 A wymaga pomiaru nagrzewania przy stopniowym obciążeniu, także w docelowej obudowie. Procedura pozostaje w ODBIOR R3.']:
 y=para(s,188,y,92,True)
finish()

head(5,'Kontrola przed zamówieniem','Wyniki przymiarki: NIE ZBADANO. Wypełnij po przyłożeniu rzeczywistych części.')
y=section('Lista przy stole',17,162)
for s in ['Skala wydruku i obrys 160 × 120 mm pasują do obudowy.',
 'Radiatory pasują do otworów P25,4; TO-220 dochodzi do radiatora bez naprężenia wyprowadzeń.',
 'Podkładki izolacyjne, tulejki M3, śruby i narzędzie mają miejsce. Wysokość pod pokrywą wystarcza.',
 'Wtyk J6 i wkrętak są dostępne od prawej strony. C6 i większe rezystory pasują do rastrów.',
 'Wiązki przechodzą przez PTH; kotwy leżą 12,5 mm od lutów. Opaski zaciskają izolację.',
 'LK1 można odlutować; osobne pola sense i TP1/TP2 pozostają dostępne po montażu radiatorów.']:
 c.setStrokeColor(muted);c.rect(18*mm,(y-4)*mm,2.5*mm,2.5*mm,fill=0,stroke=1)
 y=para(s,24,y,116,True)-2
text('Data: __________________  Wykonawca: __________________',17,y-3,9)
para('Uwagi: __________________________________________________<br/>________________________________________________________',17,y-13,123,True)
y=section('Orientacja i kolejność',158,162)
for s in ['<b>J7</b>: pad 1 po lewej = BAT_FUSED; pad 2 po prawej = GND. Wiązka wychodzi w górę do opaski.',
 '<b>J6 od dołu</b>: 1 VPROT / 2 GND / 3 NC. Nie mostkować pinu 3.',
 '<b>J5 od dołu</b>: 1 3V3_IO / 2 SAFE_N / 3 GND / 4 PG_SEND / 5 PG_LINK / 6 GND. Wiązka wychodzi w lewo.',
 'Po zaakceptowanej przymiarce: eksport produkcyjny, PCB, montaż. Następnie sama P01 z ograniczonym prądem, bez auta, EGR i dalszych modułów.',
 'Pełne procedury: reference/R3-docs/ODBIOR.md i METROLOGIA.md. Nie zamykać odbioru samym sprawdzeniem napięcia stałego.',
 'Źródło edycji: eda/P01.kicad_pcb. Raporty: verification/QA.md, drc.json i pcb-checks.json. P07 nadal HOLD.']:
 y=para(s,158,y,122,True)
finish();c.save()
print(O/'P01-PCB-R1-dokumentacja.pdf')
