"""Six readable A3 sheets (R6: + SERWIS). Short titles and individually placed fields."""
from parts import *
import cadlib, collections
names=[('P03','CORE',1),('POWER','Zasilanie i wspolny reset',2),('IO','Bufory wejsciowe',3),('OUT','Bufory wyjsciowe',4),('LINKS','Zlacza krawedzi A (S1)',5),('SERWIS','Listwy serwisowe krawedzi B (S1)',6)]
S={n:Sheet(n,t,i,None if i==1 else uid('P03')) for n,t,i in names}
for r in ['J_BP1','J_BP2','J_BP3','TP6']:PARTS[r]['sheet']='LINKS'
def put(r,x,y,a=0,u=1,txt=None):
    p=dict(PARTS[r])
    if txt is not None:p['text_at']=txt;p['fields_horizontal']=True
    S[p['sheet']].place(p,x,y,a,u)

put('M1',32,37,txt=(-5,-15));put('U1',91,37,txt=(-5,-16));put('SD1',141,34,txt=(-6,-9))
put('C2',111,51);put('R9',71,19);put('R10',78,19);put('R11',132,52)
put('U2',32,74,u=1,txt=(-5,-6));put('U2',77,74,u=2,txt=(-5,-6))
put('U2',104,74,u=3,txt=(-9,-3));put('C1',114,74)
put('R1',13,74);put('R25',13,88)
put('R5',141,73);put('C4',151,85);put('R4',123,90,90,txt=(-3,-4));put('LED1',140,90,180,txt=(-3,-4))
put('R12',54,89,90,txt=(-3,-4));put('R14',88,89,90,txt=(-3,-4))
put('R42',40,108,90,txt=(-3,-4));put('R43',62,106,txt=(2,-1))
S['P03'].text('1  CORE / GPIO zachowane z v6.1; EN wspolne z MCP23017; do P04 przez bufor U6 (R4)',8,6,2)
S['P03'].text('M1: GPIO47/48 nieuzywane. RGB na GPIO38 odlaczyc. 3V3_CORE pochodzi z M1; nigdy nie laczyc z 3V3_IO.',8,58,1.3)
S['P03'].text('U2: CURRENT_CS_N=1 blokuje oba tory. MEAS_BANK=0 po resecie. U1: A2..A0=0, adres 0x20.',8,62,1.3)
S['P03'].text('R6: PFAIL_N z P02 R4 (J_BP2.16) -> R42 1K -> GPIO3 (J1-13). R43 100K do 3V3_CORE po stronie zlacza: bez P02 = H (zasilanie OK).',8,102,1.3)

put('U5',61,26,txt=(-6,-7));put('Q1',100,25,90,txt=(-5,-8))
put('C13',40,33);put('C14',121,32)
for r,x,y in [('TP1',31,17),('TP2',15,40),('TP3',24,40),('TP4',33,40),('TP7',133,17),('TP8',49,64),('TP5',140,63)]:put(r,x,y)
put('U3',28,66,txt=(-5,-11));put('C3',14,80)
put('R13',48,55);put('U4',79,67,txt=(-6,-8));put('R34',112,66,90,txt=(-4,-5))
put('R35',133,79);put('C12',83,82)
put('U6',100,79,txt=(-6,-8));put('R41',118,78,90,txt=(-4,-5));put('C15',92,86)
S['POWER'].text('2  ZASILANIE I RESET / bez udzialu firmware',8,6,2)
S['POWER'].text('U5 + Q1: blokada przeplywu 5V_M1 -> 5V_SYS. Q1: dren=SYS, zrodlo=M1; dioda pasozytnicza SYS -> M1.',8,12,1.3)
S['POWER'].text('USB -> fabryczna D1 Waveshare -> 5V_M1. 5V_M1 -> LDO M1 -> 3V3_CORE. U5 nie ogranicza pradu.',8,45,1.3)
S['POWER'].text('TPS3808G33: prog 3,07 V, CT otwarte = zwloka ok. 20 ms. U4: bufor NIEODWRACAJACY, wyjscie OPEN DRAIN.',8,92,1.3)
S['POWER'].text('SUP_N = M1 EN + U1 RESET; do P04 przez U6 (Schmitt) i R41 jako SUP_N_OUT na J_BP3.12. RESET/auto-reset M1 resetuje tez ekspander.',8,96,1.3)
S['POWER'].text('R34=220R ogranicza rozladowanie fabrycznego C_EN=1uF. Zachowac kondensator i pull-up 10K na Waveshare.',8,100,1.3)
S['POWER'].text('U4 LVC1G37: Schmitt + OPEN DRAIN. U6 LVC1G17: Schmitt + push-pull. P04 U9.5: wymagane zbocze <=10 ns/V, do pomiaru.',8,104,1.3)

pulls={'U11':{1:'R32',2:'R31',3:'R33',4:'R30'},'U12':{1:'R3',2:'R26',3:'R2',4:'R7'},'U13':{1:'R28',2:'R29',3:'R6',4:'R8'},'U14':{1:'R27'}}
for u,x,c in [('U11',24,'C5'),('U12',62,'C6'),('U13',100,'C7'),('U14',138,'C8')]:
    for i in range(1,5):
        y=23+(i-1)*17;put(u,x,y,u=i,txt=(-2,-4))
        if i in pulls[u]:put(pulls[u][i],x-10,y+7,txt=(2,-1))
    put(u,x,92,u=5,txt=(-9,-3));put(c,x+10,92)
S['IO'].text('3  WEJSCIA / rezystory przed U11-U14 ustalaja stan przy wypietym module',8,6,2)
S['IO'].text('CAN_RX=1; pozostale sygnaly=0. Stale 0 na ADC/SPI nie potwierdza obecnosci ani poprawnosci pomiaru. P07 HOLD.',8,12,1.3)

pulls={'U21':{1:'R15',2:'R16',3:'R17',4:'R18'},'U22':{1:'R19',2:'R20'},'U23':{1:'R21',2:'R22',3:'R23',4:'R24'}}
series={('U21',2):'R36',('U21',3):'R39',('U21',4):'R37',('U23',1):'R38',('U23',2):'R40'}
for u,x,c in [('U21',29,'C9'),('U22',79,'C10'),('U23',129,'C11')]:
    for i in range(1,5):
        y=23+(i-1)*17;put(u,x,y,u=i,txt=(-2,-4))
        if i in pulls[u]:put(pulls[u][i],x-14,y+7,txt=(2,-1))
        if (u,i) in series:put(series[u,i],x+16,y+8,90,txt=(-3,-4))
    put(u,x,92,u=5,txt=(-9,-3));put(c,x+10,92)
S['OUT'].text('4  WYJSCIA / CS domyslnie HIGH; RESET, MEAS_EN, CONVST, CLK i DATA domyslnie LOW',8,6,2)
S['OUT'].text('U21-U23 z Ioff. R36-R40: 33R przy wyjsciu bufora; dobierac po pomiarze na koncu lacza (22..47R / 0R).',8,12,1.3)

for r,x,y in [('J_BP1',25,45),('J_BP2',80,45),('J_BP3',135,45)]:put(r,x,y,txt=(-6,-15))
put('TP6',151,18)
S['LINKS'].text('5  ZLACZA KRAWEDZI A / IDC 2x10 katowe, po jednym na slot (S1, S2, S3); tasma ok. 30 mm do P12',8,6,2)
S['LINKS'].text('R6 zastepuje J1 (DAQ B2B), J2-J8 (IDC), J9 (PANELCORE) i J10 (LV03). Sieci bez zmian. Pinout i uzasadnienia: docs/J_BP.csv, README.',8,12,1.3)
S['LINKS'].text('Nieparzyste = GND poza wyjatkami (sygnaly statyczne i zasilanie). ADC_SCLK, SPI3_SCLK i MEAS_EN z GND po obu stronach.',8,15,1.3)
S['LINKS'].text('5V_SYS (J_BP2.17, 19, 20) i 3V3_IO (J_BP3.5) przychodza z P02 R4 przez P12. P12 rozprowadza ADC_SCLK i ADC_DOUTA do P05, P06 i P07.',8,18,1.3)
for k,j in enumerate(['J_SV1','J_SV2','J_SV3']):
    x=20+50*k
    for i in range(2,13):put(SERIES[(j,i)],x,18+3.5*(i-2),90,txt=(-2,-1.2))
    put(j,x+27,36,txt=(-3,-10))
S['SERWIS'].text('6  LISTWY SERWISOWE KRAWEDZI B / goldpin 1x13 katowy, GND na pinach 1 i 13',8,6,2)
S['SERWIS'].text('Kazdy kolek poza GND przez rezystor przy wezle: 1K szyny do 5 V i logika, 10K wezly wysokoimpedancyjne (S1 par. 6). Tresc: docs/SERWIS.csv.',8,10,1.3)
S['SERWIS'].text('SUP_N = EN modulu (J1-3) = RESET MCP23017. Punkty SPI mierzyc na koncu lacza (P05, P09), nie tutaj.',8,62,1.3)

ns=collections.defaultdict(set)
for name,s in S.items():
    for p,pins in s.parts.values():
        for n in pins:ns[p['pins'][n]].add(name)
cadlib.CROSS={n for n,v in ns.items() if len(v)>1 and n!='NC'}|{'GND','5V_SYS','5V_M1','3V3_CORE','3V3_IO'}
pw=S['POWER']
pw.node('SUP_RAW_N',[('U3',1),('U4',2)],axis='y',bus=66)
pw.node('RESET_DRV_N',[('U4',4),('R34',1)],axis='y',bus=66)
pw.node('SUP_N_DRV',[('U6',4),('R41',1)],axis='y',bus=78)  # pin 4 (Y) row; pin 5 (VCC) sits one row lower
P0=S['P03']
for idx,(name,title,num) in enumerate(names[1:]):
    x,y=mm(9+31*idx),mm(95);shid=uid('sheet/'+name)
    P0.items.append(f'(sheet (at {x} {y}) (size 60.96 7.62) (stroke (width 0.15) (type default)) (fill (color 0 0 0 0)) (uuid {shid}) '
      f'(property "Sheetname" {q(name)} (at {x} {y-1.27} 0) (effects (font (size 1 1)) (justify left bottom))) '
      f'(property "Sheetfile" {q(name+".kicad_sch")} (at {x} {y+8.89} 0) (effects (font (size 1 1)) (justify left top))) '
      f'(instances (project "P03" (path {q("/"+uid("P03"))} (page "{num}")))))')
    s=S[name];old=s.path;s.path='/'+uid('P03')+'/'+shid;s.items=[t.replace(q(old),q(s.path)) for t in s.items]
flag=symbol('power','PWR_FLAG')
for idx,(net,x,y) in enumerate([('5V_SYS',38,17),('5V_M1',143,17),('GND',37,40),('3V3_IO',24,49)],1):
    pw.place({'ref':'#FLG'+str(idx),'display':'PWR_FLAG','source_ref':'ERC_SOURCE','mpn':'','footprint':'','symbol':flag,'pins':{'1':net},'qty':0,'url':''},x,y)
for s in S.values():s.finish();s.save()
write_tables()
# Re-exporting the schematic must not erase PCB rules or net classes.
project=P/'eda/P03.kicad_pro'
if not project.exists():
    project.write_text('{}',encoding='utf-8')
print('Placed',len(PARTS),'components on',len(S),'A3 sheets')
