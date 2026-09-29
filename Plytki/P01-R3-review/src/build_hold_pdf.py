"""Single-page vector wiring sheet for the bounded P02-HOLD subcircuit."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4,landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
P=Path(__file__).resolve().parents[1]
for name,file in [('Arial','arial.ttf'),('Arial-Bold','arialbd.ttf')]:pdfmetrics.registerFont(TTFont(name,str(Path('C:/Windows/Fonts')/file)))
f=P/'output/pdf/P02-HOLD-C1-polaczenia.pdf'
c=canvas.Canvas(str(f),pagesize=landscape(A4));W,H=landscape(A4)
c.setTitle('EGRLab P02-HOLD C1 - polaczenia i granice')
def text(x,y,s,size=10,bold=False):
 c.setFont('Arial-Bold' if bold else 'Arial',size);c.drawString(x,y,s)
def line(x1,y1,x2,y2):c.line(x1,y1,x2,y2)
def box(x,y,w,h,label):
 c.setFillColorRGB(.96,.98,.99);c.rect(x,y,w,h,fill=1);c.setFillColorRGB(.1,.15,.2);text(x+6,y+h/2-3,label,9)
def diode(x,y,label):
 line(x-15,y,x-5,y);line(x+5,y,x+15,y)
 path=c.beginPath();path.moveTo(x-5,y-6);path.lineTo(x+5,y);path.lineTo(x-5,y+6);path.close();c.drawPath(path)
 line(x+5,y-7,x+5,y+7);text(x-35,y+14,label,9)
def dot(x,y):c.circle(x,y,2,fill=1,stroke=0)
c.setStrokeColorRGB(.1,.2,.28);c.setFillColorRGB(.1,.15,.2);c.setLineWidth(1.2)
text(35,H-40,'EGRLab / P02-HOLD C1',22,True)
text(35,H-62,'Obwód do włączenia w P02. Nie jest kompletnym projektem PCB P02.',11)
text(35,H-80,'Decyzja: podtrzymywać pomiary i zapis; silnik zasilać z niepodtrzymanego VPROT.',10)
y=410
text(35,y+17,'VPROT z P01',11,True);line(35,y,210,y)
diode(225,y,'D_OR.1 = A1');line(240,y,430,y);dot(370,y)
text(400,y-17,'D_OR.2 = K / tab',9);text(466,y+14,'VLOG_RES',11,True)
line(430,y,610,y);line(570,y,570,y-42);line(570,y-42,610,y-42)
box(610,y-12,170,24,'F2 1A → TSR2-2450 → 5V')
box(610,y-54,170,24,'F3 1A → TSR2-2433 → 3V3')
line(85,y,85,y+42);line(85,y+42,585,y+42);text(170,y+48,'VPROT → F4 / KPWR / silnik (bez podtrzymania)',10)
dot(85,y)
line(85,y,85,305);box(110,294,120,22,'R_CHARGE 47R / 25W');line(85,305,110,305)
line(230,305,260,305);diode(275,305,'D_CHARGE A1+A2 → K');line(290,305,370,305)
line(370,305,370,360);line(370,360,400,360)
diode(415,360,'D_OR.3 = A2');line(430,360,470,360);line(470,360,470,410);dot(470,410)
text(270,280,'HOLD_FUSED',9,True);line(350,305,350,247);dot(350,305)
box(310,227,80,20,'F_HOLD T2A');line(350,227,350,205);text(360,207,'HOLD_STORE / TP',9,True)
line(200,205,510,205);dot(350,205)
for x,label in [(215,'C_H1'),(290,'C_H2'),(365,'C_H3')]:
 line(x,205,x,185);line(x-8,185,x+8,185);line(x-8,180,x+8,180);line(x,180,x,162)
 text(x-15,148,label,8);text(x-19,192,'+',8)
line(510,205,510,193);box(482,170,56,23,'4k7/0,5W');line(510,170,510,162)
line(200,162,540,162);text(546,159,'GND',9);text(205,129,'3 × 22000µF / 35V; wspólna masa',9,True)
line(560,410,560,330);line(552,330,568,330);line(552,325,568,325);line(560,325,560,310)
line(550,310,570,310);text(550,296,'GND',8);text(577,327,'C_BUS 22µF/50V',8)
text(35,99,'Budżet: ≤6W na wejściu przetwornic; rezerwa ≥9,5V; Ceff ≥52,8mF; spadek całej gałęzi ≤1,2V.',10)
text(35,82,'Wymóg: VLOG_RES ≥7V przez 50ms. Zapas obliczeniowy ≈85ms, do odbioru w 0/25/50°C.',10)
text(35,64,'D_OR i D_CHARGE: STPS20100CT, 1=A1 / 2=K / 3=A2. Nie zamieniać połączeń anod D_OR.',10)
text(35,45,'Pełny BOM, połączenia, ładowanie, bezpieczniki i procedura: integration/P02-HOLD/PROJEKT.md.',9)
text(35,27,'23.09.2026 • model i obliczenia, bez pomiarów sprzętu • P07 nadal HOLD',8)
c.showPage();c.save();print(f)
