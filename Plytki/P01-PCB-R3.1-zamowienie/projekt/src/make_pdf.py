"""Assembly/inspection PDF using native KiCad exports, with physical scale."""
from pathlib import Path
import json,hashlib,xml.etree.ElementTree as ET,subprocess,sys,shutil,os
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor,black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
P=Path(__file__).resolve().parents[1];O=P/'output'
pdfmetrics.registerFont(TTFont('Arial','C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold','C:/Windows/Fonts/arialbd.ttf'))
checks=json.loads((P/'verification/pcb-checks.json').read_text());assert checks['pass']
assert checks['board_sha256']==hashlib.sha256((P/'eda/P01.kicad_pcb').read_bytes()).hexdigest()
pdf=O/'pdf/P01-PCB-R3.1-dokumentacja.pdf';c=Canvas(str(pdf),pagesize=(297*mm,210*mm))
c.setTitle('EGRLab P01 PCB-R3 (wydanie R3.1) - montaż i przymiarka');c.setAuthor('EGRLab / Codex, poprawki R3.1: Claude')
style=ParagraphStyle('body',fontName='Arial',fontSize=9.3,leading=13,textColor=HexColor('#172833'))
def paragraph(txt,x,y,width=104):
 p=Paragraph(txt,style);_,h=p.wrap(width*mm,160*mm);p.drawOn(c,x*mm,y*mm-h);return y-h/mm-3
def start(num,title,sub):
 c.setFillColor(HexColor('#117e86'));c.rect(0,204*mm,297*mm,6*mm,fill=1,stroke=0)
 c.setFillColor(HexColor('#172833'));c.setFont('Arial-Bold',19);c.drawString(12*mm,188*mm,title)
 c.setFont('Arial',9.2);c.drawString(12*mm,179*mm,sub)
 c.setStrokeColor(HexColor('#cdd7dc'));c.line(12*mm,14*mm,285*mm,14*mm)
 c.setFont('Arial',8);c.drawString(12*mm,9*mm,'EGRLab | PCB-R3, wydanie R3.1 / SCH-R3 / montaż A1 | 25.09.2026 | do przymiarki')
 c.drawRightString(285*mm,9*mm,f'{num} / 6')
def image(name,x,y,w,h):c.drawImage(str(O/'previews'/name),x*mm,y*mm,w*mm,h*mm,preserveAspectRatio=True,anchor='c',mask='auto')
def bar(x,y):
 c.setStrokeColor(black);c.setLineWidth(.5);c.line(x*mm,y*mm,(x+100)*mm,y*mm)
 for xx in (x,x+100):c.line(xx*mm,(y-2)*mm,xx*mm,(y+2)*mm)
 c.setFont('Arial',9);c.drawString(x*mm,(y-7)*mm,'Belka kontrolna 100 mm. Druk 100%, bez dopasowania.')
def board(name):
 svg=ET.parse(O/'svg'/(name+'.svg')).getroot()
 w=float(svg.attrib['width'].removesuffix('mm'));h=float(svg.attrib['height'].removesuffix('mm'))
 assert abs(w-160)<.1 and abs(h-120)<.1,(name,w,h)
 # Preserve native physical dimensions. The plotted Edge.Cuts clipping differs <0.02 mm.
 image(name+'.png',12,44,w,h);bar(12,33)
start(1,'P01 PROTECT / PCB-R3, wydanie R3.1','Dwie warstwy, 160 x 120 mm, FR4 1,6 mm, miedź 70 um na stronę.')
y=165
for txt in [
 '<b>Zmiana lokalna na bazie R2.</b> Zachowane bloki funkcjonalne i interfejsy. D4 przy Q1, C6 odsunięty dla dostępu montażowego, sondowanie od spodu.',
 '<b>R3.1:</b> płytka bez zmian. Poprawione: kolejność montażu (C6 po dokręceniu Q1), BOM A1 (U4, uwagi o wyprowadzeniach i polaryzacji z BOM R3) i kontrole.',
 '<b>Wynik cyfrowy:</b> świeży DRC 0/0/0; '+str(len(checks['checks']))+' kontroli PASS. Pięć celowych usterek wykrytych w kopiach.',
 '<b>D4 do Q1:</b> K-S 5,25 mm, A-G 6,78 mm. TP1/TP2: po 4,62 mm ścieżki. C6: 9,8 mm od G/S.',
 '<b>Montaż A1:</b> użyj BOM-MONTAZOWY-A1.csv. R8 = 221 kΩ; R1/R23/R27 = 5%. Schemat nominalny R3 pozostaje materiałem odniesienia.',
 '<b>Przymiarka i sprzęt:</b> NIE ZBADANO. Render pokazuje lokalne modele gabarytowe, nie pomiar dopasowania rzeczywistych części.'
]:y=paragraph(txt,12,y,111)
image('isometric.png',130,34,155,137)
c.setFont('Arial',8);c.drawString(132*mm,27*mm,'Modele gabarytowe: 77 footprintów; pozostałe to pola i zworki.')
c.showPage()
start(2,'Montaż - widok z góry 1:1','Geometria z natywnego eksportu KiCad. Obrys płytki: 160 x 120 mm.')
board('assembly');y=163
for txt in [
 '<b>Q1, Q2 i D2:</b> gruba linia nadruku oznacza stronę metalowego tyłu. Q2 ma dodatkowy napis TAB.',
 '<b>D4:</b> pasek katody po prawej, do SOURCE Q1. D4 przed Q1/HS2; <b>C6 dopiero po dokręceniu Q1</b> - zasłania łeb śruby od przodu.',
 '<b>Radiatory:</b> izolować taby i śruby. Miedź F.Cu wykluczona spod profili.',
 '<b>J5:</b> przewody ku dolnej krawędzi, kotwa 12,5 mm od lutów. Nie zmieniać numeracji komór wtyku.',
 '<b>TP1/TP2:</b> podstawowy dostęp od spodu; oznaczenia na stronie 3. Nie potrzebują pętelek ani dodatkowych złączy.'
]:y=paragraph(txt,185,y,100)
c.showPage()
start(3,'Spód - dostęp pomiarowy 1:1','Widok bezpośrednio od spodu (odbicie względem widoku z góry). Tekst czytelny po odwróceniu PCB.')
board('bottom');y=163
for txt in [
 '<b>TP1 S = SOURCE, TP2 G = GATE.</b> VGS mierzyć różnicowo między G i S. SOURCE nie jest GND oscyloskopu.',
 'Sondować pola od spodu na stanowisku pozwalającym bezpiecznie odsłonić spód PCB. Użyć krótkich końcówek zgodnie z METROLOGIA R3.',
 'Dodatkowe oznaczenia rezystorów pozostają widoczne po montażu elementów od góry.',
 'Wiązki i kołki radiatorów przechodzą przez PCB. Sprawdzić długość końcówek, luty i prześwit nad podstawą obudowy.',
 '<b>Przed uruchomieniem:</b> sprawdzić izolację radiatorów, połączenia LK1 i polaryzację. Najpierw zasilacz laboratoryjny i sama P01.'
]:y=paragraph(txt,185,y,100)
c.showPage()
start(4,'Miedź F.Cu 1:1','Natywny eksport gotowej PCB. Widok od góry, po wypełnieniu stref.')
board('copper-front');y=163
for txt in [
 'Obszary pod profilem HS1/HS2 pozostają bez miedzi F.Cu. Wnęki mieszczą elementy TO-220 i obwody lokalne.',
 'D4 jest podłączona lokalnie do G/S Q1. Dawne odgałęzienia do poprzedniego położenia D4 usunięto lub zakończono na właściwych odczepach.',
 'C5 ma osobną ścieżkę GATE. Nie korzysta z małych pól Kelvin LK1 jako toru roboczego.',
 'BAT_FUSED: lokalny odcinek 3 mm z R2 pozostaje jawnym odstępstwem od wcześniejszej wytycznej 5 mm. Sprawdzić nagrzewanie całej gałęzi podczas odbioru.',
 'To rysunek kontrolny. Pliki produkcyjne wymagają domkniętej przymiarki i eksportu z tego samego sprawdzonego źródła.'
]:y=paragraph(txt,185,y,100)
c.showPage()
start(5,'Miedź B.Cu 1:1','Widok bezpośrednio od spodu. Ta sama orientacja co strona 3.')
board('copper-back');y=163
for txt in [
 'Szyna VS lokalnie omija przesunięty pad GATE kondensatora C6. Nie ma zwarcia z C6 po ponownym wypełnieniu miedzi.',
 'Zachowane powroty mocy GND, trzy przelotki szyny VS i termiki połączenia J7.',
 'Miedź B.Cu może przebiegać pod radiatorami: od metalu profilu oddziela ją laminat. Kołki radiatorów pozostają bez sieci.',
 'Odbiór obejmuje rzeczywiste luty przewlekane, spadki napięć i temperaturę przy obciążeniu. DRC nie potwierdza obciążalności cieplnej.',
 'Szerokie połączenia nie zastępują bezpiecznika ani sprawdzenia czasu odcięcia Q1.'
]:y=paragraph(txt,185,y,100)
c.showPage()
start(6,'Wnęka HS2 i przymiarka','Powiększenie natywnej geometrii; ta strona nie jest szablonem w skali 1:1.')
image('gate-detail.png',12,65,100,100)
y=165
for txt in [
 '<b>Ułożenie:</b> Q1, niżej D4, następnie C6. Wnęka radiatora nominalnie 17 mm. C6 ma korpus 7,2 x 7,2 x 13 mm.',
 '<b>Prześwity nominalne:</b> D4-C6 1,075 mm; czoło Q1-C6 4,85 mm. Rzeczywiste tolerancje i sposób uformowania nóżek sprawdzić częściami.',
 '<b>Śruba i izolacja:</b> złożyć Q1/D2 z radiatorem i dokręcić przed lutowaniem nóżek. C6 ma 13 mm, oś śruby 13,5 mm: po wlutowaniu C6 śruba tylko od tyłu kanału, nakrętka od strony Q1 kluczem 5,5 mm.',
 '<b>Kolejność:</b> drobne THT i D4, Q1/D2 z radiatorami (śruby dokręcone), lutowanie nóżek, C6 od góry kanału, pozostałe duże części, wiązki i LK1.',
 '<b>Do wpisania przy stole:</b> dopasowanie otworów; izolacja tabów/śrub; dostęp do sond i śruby; wiązki; obudowa; możliwość wyjęcia modułu.'
]:y=paragraph(txt,125,y,160)
c.setFont('Arial',9);c.drawString(12*mm,48*mm,'Przymiarka:  NIE ZBADANO    Data: __________________    Wykonawca: __________________')
c.drawString(12*mm,36*mm,'Wynik / korekty: __________________________________________________________________________________________')
c.drawString(12*mm,24*mm,'Uruchomienie i kryteria pomiarów: reference/R3-docs/ODBIOR.md oraz METROLOGIA.md.')
c.save()
renderer=os.environ.get('EGRLAB_PDFTOPPM') or shutil.which('pdftoppm')
if not renderer:
 candidate=Path(sys.executable).parent.parent/'native/poppler/Library/bin/pdftoppm.exe'
 if candidate.exists():renderer=str(candidate)
if not renderer:raise RuntimeError('pdftoppm required for bound PDF previews; set EGRLAB_PDFTOPPM')
subprocess.run([renderer,'-r','110','-png',str(pdf),str(O/'previews/pdf')],check=True)
print(pdf)
