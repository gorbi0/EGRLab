from parts import *
import cadlib,collections,copy
names=[('P05','Zasilanie lokalne'),('CON','Interfejsy i wiazki'),('ADC','AD7606B i odsprzeganie'),('DIG','Bufory SPI / IO'),('TAPS','Odczepy EGR i odlaczanie'),('READY','Nadzor zasilania i DAQ_OK'),('AUX','VSENSE, zero i AUX'),('SERV','Zasilanie logiki i punkty pomiarowe')]
S={n:Sheet(n,t,i,None if i==1 else uid('P05')) for i,(n,t) in enumerate(names,1)}
def put(sh,r,x,y,a=0,u=1,off=None):
 v=copy.copy(PARTS[r]);v['text_at']=off or ((-5,-5) if r.startswith('U') else (0,-5) if r.startswith('R') and a==90 else (3,-1))
 if r.startswith('J'):v['text_at']=(3,-len(v['pins'])//2-2)
 if r.startswith('TP'):v['text_at']=(3,-1)
 if r=='SW1':v['text_at']=(-8,-5)
 if r=='U12':v['text_at']=(-12,-5)
 if sh=='SERV' and u==5:v['text_at']=(-8,-5)
 S[sh].place(v,x,y,a,u)
def node(sh,n,p,b=None,axis='y'):S[sh].node(n,p,b,axis)
for r,x,y,a in [('R1',23,22,90),('C1',40,30,0),('C2',57,30,0),('U12',82,22,0),('C3',107,30,0),('R2',128,30,0)]:put('P05',r,x,y,a)
node('P05',A5,[('R1',2),('C1',1),('C2',1),('U12',2)],22)
node('P05',V,[('U12',3),('C3',1),('R2',1)],22)
for i,ref in enumerate(range(14,23)):
 x=18+29*(i%5);y=53+21*(i//5);put('P05',f'C{ref}',x,y)
 S['P05'].text(f'C{ref} przy {PARTS[f"C{ref}"]["source_ref"].replace("C_DEC_","")}',x-4,y+9,1.05)
for i in range(1,17):
 x=15+(i-1)%4*30;y=67+(i-1)//4*13;put('SERV',f'TP{i}',x,y)
for i,n in enumerate([G,S5,A5],1):S['P05'].place({'ref':f'#FLG{i}','display':'PWR_FLAG','symbol':symbol('power','PWR_FLAG'),'source_ref':'ERC_SOURCE','mpn':'','footprint':'','pins':{'1':n}},18+i*26,12)
S['P05'].text('3V3_DAQ pochodzi z 5VA_P05. LV05.3 / 3V3_IO konczy sie na TP5: nie zwierac tych szyn.',8,39,1.3)
S['P05'].text('R1: 1R / 1W. C1: 470u / 16V. C3: efektywnie >=1uF przy 3.3V; R2 rozladowuje szynę lokalna.',8,43,1.2)
for r,x,y in [('J1',30,29),('J2',83,24),('J3',130,24),('J4',30,76),('J5',83,76)]:put('CON',r,x,y)
S['CON'].text('J1: B2B katowe, bez tasmy. Kontakt logiczny 2 usuniety. Patrz MECHANIKA.md: numeracja padów/mating.',8,12,1.25)
S['CON'].text('J2 LV05: 200mm AWG22. J3 DAQOK: 150mm AWG28 / IDC6 KEY4. Kotwy 11.5..15mm od rzedow PTH.',8,47,1.2)
S['CON'].text('J4 TAPS: 50mm AWG24, 5 par. J5 VSENSE: 150mm AWG22, obsadzone tylko piny 1 i 2.',8,102,1.2)
S['CON'].text('Rezystory 300k (motor) / 100k (sensor) pozostaja w adapterach AT/AL1/AL2 przy zrodle sygnalu.',8,107,1.2)
# ADC three units: digital, analog and power. No AD7606-old symbol pin 10 ambiguity.
put('ADC','U1',29,37,u=1,off=(-6,-12));put('ADC','U1',82,24,u=2,off=(-6,-8));put('ADC','U1',82,64,u=3,off=(-6,-9))
for j,ref in enumerate(range(4,14)):
 x=119+23*(j%2);y=18+17*(j//2);put('ADC',f'C{ref}',x,y)
S['ADC'].text('OS[2:0]=111; SER=1; WR10=1. RESET11: pelny reset >=3us. BUSY14 przechodzi przez U11B.',8,100,1.2)
S['ADC'].text('Referencja ADC wewnetrzna. C12/C13: 22uF/25V 1210 X7R, efektywnie >=10uF; 36/39 osobne 1uF.',8,105,1.2)
S['ADC'].text('Nie zwierac pinow 36/39. Wyjscia DOUTB/C/D i FRSTDATA pozostaja NC. Serial DB0..6/12..15 = GND.',8,110,1.15)
sig=['ADC_CS','ADC_SCLK','ADC_SDI','ADC_CONVST','ADC_RESET','MEAS_EN']
mapgate={'ADC_CS':('U9',3,9,8),'ADC_SCLK':('U9',1,2,3),'ADC_SDI':('U9',2,5,6),'ADC_CONVST':('U9',4,12,11),'ADC_RESET':('U10',1,2,3),'MEAS_EN':('U10',2,5,6)}
for i,n in enumerate(sig):
 x=25+52*(i//3);y=23+26*(i%3);r,u,ip,op=mapgate[n];put('DIG',r,x,y,u=u)
 put('DIG',f'R{i+13}',x-12,y+7);put('DIG',f'R{i+19}',x+15,y+7)
 node('DIG',n,[(r,ip),(f'R{i+13}',1)],y)
 node('DIG',n+'_P05',[(r,op),(f'R{i+19}',1)],y)
for r,u,x,y in [('U10',3,129,21),('U10',4,129,43),('U11',1,127,67),('U11',2,127,93)]:put('DIG',r,x,y,u=u)
put('DIG','R26',145,67,90);put('DIG','R27',145,93,90)
node('DIG','DOUT_SER',[('U11',3),('R26',1)],67);node('DIG','BUSY_SER',[('U11',6),('R27',1)],93)
for r,u,x,y in [('U9',5,20,50),('U10',5,45,50),('U11',5,70,50),('U11',3,95,50),('U11',4,120,50)]:put('SERV',r,x,y,u=u)
S['DIG'].text('Ioff chroni wylaczona domene. U11A: OE_N=CS; wspolna linia MISO nie jest stale napedzana.',8,12,1.2)
for i in range(1,4):
 x=28+52*(i-1);put('TAPS',f'K{i}',x,32,off=(-7,-8));put('TAPS',f'D{i}',x+17,20,90)
 # Stagger the long coil label below the adjacent contact labels.
 sh=S['TAPS'];pt=sh.pin(f'K{i}',8);end=(pt[0],pt[1]+10.16)
 sh.wire(pt,end);sh.label('MEAS_COIL_LOW',end,'right');sh.connected.add((f'K{i}','8'))
for i in range(1,6):put('TAPS',f'C{i+26}',22+27*(i-1),66)
put('TAPS','R28',24,83);put('TAPS','R29',49,83);put('TAPS','U4',115,90,off=(-5,-13));put('TAPS','R25',84,96)
S['TAPS'].text('TAP: sygnal juz za rezystorem w adapterze. Nie podlaczac surowego motoru do J4!',8,12,1.25)
S['TAPS'].text('K1/K2/K3 NO: otwarte bez zasilania. Zalaczenie tylko MEAS_EN & DAQ_OK; nie zalezy od ARM.',8,51,1.25)
S['TAPS'].text('CH1/2: dolna galaz 100k. CH3/4/5: bez 100k do masy (pomiar czujnika). Filtry C0G 220p.',8,55,1.15)
S['TAPS'].text('TBD62083: COM=5V_SYS, wejscia 2..8 do GND. Pary 1/18 i cewki 1/8; diody lokalnie.',8,110,1.1)
for r,x,y in [('R3',22,20),('R4',22,36),('R5',50,20),('R6',50,36),('R7',76,20),('R8',76,36),('C25',60,31),('C26',86,31),('U2',117,24),('C23',102,30),('C24',142,30)]:put('READY',r,x,y,off=(-4,-7) if r=='U2' else None)
for top,bot,net,x in [('R3','R4','RAIL_SENSE',22),('R5','R6','RAIL_LOW',50),('R7','R8','RAIL_HIGH',76)]:node('READY',net,[(top,2),(bot,1)],28)
put('READY','U3',28,59,u=1);put('READY','U3',72,59,u=2);put('READY','R9',93,74)
node('READY','DAQ_RAIL_N',[('U3',1),('U3',7),('R9',1)],68)
put('READY','U6',25,89);put('READY','U7',72,89);put('READY','R10',45,91);put('READY','R11',91,89);put('READY','U8',112,89,u=1)
for r,u,x,y in [('U5',1,120,50),('U5',2,120,66),('U5',3,144,82)]:put('READY',r,x,y,u=u,off=(-3,-3))
for r,u,x,y in [('U5',4,145,50),('U5',5,45,28),('U3',3,20,28),('U8',5,70,28),('U8',2,96,28),('U8',3,121,28),('U8',4,146,28)]:put('SERV',r,x,y,u=u,off=(-3,-5))
put('READY','R12',148,58)
S['READY'].text('Okno nominalne 5VA: 4.826..5.165V. Tolerancje i VOS policzone w verification/electrical-checks.json.',8,11,1.2)
S['READY'].text('DAQ_OK: napiecia poprawne; nie jest potwierdzeniem sprawnosci ADC ani kalibracji.',8,74,1.25)
for r,x,y,a in [('R30',28,26,0),('C32',48,26,0),('R31',24,58,90),('R32',50,64,0),('C33',68,64,0),('J6',27,93,0),('SW1',64,84,0),('R33',101,80,90),('R34',101,96,90),('R35',130,88,0),('C34',148,88,0)]:put('AUX',r,x,y,a)
put('AUX','SW1',64,97,u=2)
node('AUX','ADC_CH6',[('R30',1),('C32',1)],18)
node('AUX','ADC_CH7',[('R31',2),('R32',1),('C33',1)],58)
node('AUX','ADC_CH8',[('R33',2),('R34',2),('R35',1),('C34',1)],123,'x')
S['AUX'].text('CH6: terminacja zera; prad z MCP3201 na P06/P07 jest osobnym pomiarem. Nie dodawac shunta do CH6.',8,12,1.2)
S['AUX'].text('VSENSE: 499k/100k, nominalny mnoznik 6.0898; kalibracja offsetu i gain obowiazkowa.',8,43,1.2)
S['AUX'].text('SW1 HI = 2-1 + 5-4; LO = 2-3 + 5-6. Przelaczac bez napiecia. Po zmianie zmienic profil AUX.',8,106,1.2)
ns=collections.defaultdict(set)
for name,sh in S.items():
 for part,pins in sh.parts.values():
  for n in pins:ns[part['pins'][n]].add(name)
cadlib.CROSS={n for n,v in ns.items() if len(v)>1 and n!='NC'}
for sh in S.values():
 for net in cadlib.CROSS:sh.items=[item.replace('(label '+q(net)+' ','(global_label '+q(net)+' (shape passive) ') for item in sh.items]
 sh.text(f'P05-R1 / {sh.num:02d}  {sh.title.upper()}',8,5,2)
for i,(name,title) in enumerate(names[1:],2):
 sh=S[name];x,y=mm(15+(i-2)%3*35),mm(86+(i-2)//3*8);sid=uid('sheet/'+name)
 S['P05'].items.append(f'(sheet (at {x} {y}) (size 55.88 10.16) (stroke (width .15) (type default)) (fill (color 0 0 0 0)) (uuid {sid}) (property "Sheetname" {q(name)} (at {x} {y-1.27} 0) (effects (font (size 1 1)) (justify left bottom))) (property "Sheetfile" {q(name+".kicad_sch")} (at {x} {y+11.43} 0) (effects (font (size 1 1)) (justify left top))) (instances (project "P05" (path {q("/"+uid("P05"))} (page "{i}")))))')
 old=sh.path;sh.path='/'+uid('P05')+'/'+sid;sh.items=[t.replace(q(old),q(sh.path)) for t in sh.items]
for sh in S.values():sh.finish();sh.save()
write_tables()
(P/'verification/sheet-parts.json').write_text(json.dumps({n:list(s.parts) for n,s in S.items()},indent=2))
print(len(PARTS),'parts; eight A3 sheets')
