from parts import *
import cadlib,collections,copy
names=[('P08','Zasilanie czujnika i przekaznik'),('LOGIC','Gotowosc i warunki zezwolenia'),('IO','Bufory sygnalow miedzy plytkami'),('CONNECT','Wiazki i punkty pomiarowe')]
class CompactSheet(Sheet):
 def text(self,t,x,y,size=1.27):super().text(t,x,y*.88,size)
S={n:CompactSheet(n,t,i,None if i==1 else uid('P08')) for i,(n,t) in enumerate(names,1)}
def put(sh,r,x,y,a=0,u=1,off=None):
 pp=copy.copy(PARTS[r]);pp['display']=pp['display'].split(' / ')[0]
 if r.startswith(('U','K')):pp['text_at']=(-5,-7)
 if r.startswith('J'):pp['text_at']=(2,-(len(pp['pins'])//2)-3)
 if r.startswith('TP'):pp['text_at']=(2,-1)
 if off:pp['text_at']=off
 S[sh].place(pp,x,round(y*.88*2)/2,a,u)
def node(sh,n,refs,bus=None,axis='y'):S[sh].node(n,refs,round(bus*.88*2)/2 if bus is not None and axis=='y' else bus,axis)
for r,x,y,a,u in [('U1',40,25,0,1),('C1',17,27,0,1),('C2',67,27,0,1),('R1',60,43,0,1),('R17',81,27,0,1),('K1',109,28,0,2),('R18',145,28,0,1)]:put('P08',r,x,y,a,u)
node('P08',A5,[('C1',1),('U1',1)],19)
node('P08','SENSOR_LIMITED',[('U1',6),('C2',1),('R17',1),('K1',3)],20)
node('P08','ILIM_232K',[('U1',5),('R1',1)],36)
node('P08','5V_SENSOR',[('K1',4),('R18',1)],20)
node('P08','AGND_SENSOR',[('K1',5),('R18',2)],40)
for r,x,y,a,u in [('R15',23,62,90,1),('R16',44,71,0,1),('U8',68,64,0,1),('U2',114,66,0,1),('K1',145,57,0,1),('D1',143,78,90,1)]:put('P08',r,x,y,a,u)
node('P08','TPS_EN',[('R15',2),('R16',1),('U8',1)],62)
node('P08','SENSOR_COIL_LOW',[('U2',18),('K1',8),('D1',2)],135,'x')
S['P08'].text('R1 232k 1%: okolo 117 mA typ.; z rownan TI okolo 99..139 mA z tolerancja rezystora. Nie jest to limit 20 mA.',8,11,1.2)
S['P08'].text('K1: COM 3/6, NO 4/5. Rozlacza +5V i powrot; AGND_SENSOR nie laczyc z GND poza K1.',8,46,1.2)
S['P08'].text('U8 wymusza TPS_EN=0 przy brownout 3V3. R15/R16 zmniejszaja EN ponizej 0.66 V gdy 3V3 <1 V.',8,86,1.2)
S['P08'].text('U8 zwalnia do 700 ms; przed pierwszym wlaczeniem odczekac 750 ms od SENSOR_OK=1. K1 moze zalaczyc wczesniej niz U1.',8,91,1.15)
for r,x,y in [('C3',15,105),('C4',30,105),('C5',45,105),('C6',60,105),('C7',75,105),('C8',90,105),('C9',105,105),('C10',120,105)]:put('P08',r,x,y)
for i,(n,x) in enumerate([(A5,12),(V,28),(G,44)],1):
 S['P08'].place({'ref':f'#FLG{i}','display':'PWR_FLAG','symbol':symbol('power','PWR_FLAG'),'source_ref':'ERC_SOURCE','mpn':'','footprint':'','pins':{'1':n}},x,round(116*.88*2)/2)
# Supervisors, translation and AND functions.
for r,x,y,a,u in [('U6',31,24,0,1),('R3',13,18,0,1),('U7',31,49,0,1),('R4',13,43,0,1),('U4',73,49,0,1),('R5',93,56,0,1),('U3',122,30,0,1),('R8',145,38,0,1),('U3',46,81,0,2),('R9',70,87,0,1),('U3',115,80,0,3),('R2',85,69,0,1),('R10',144,87,0,1),('U3',21,106,0,4),('U3',62,109,0,5)]:put('LOGIC',r,x,y,a,u)
S['LOGIC'].text('SENSOR_OK_LOCAL = SUP3_N & SUP5_N; niezalezny od PERMIT i od napiecia za przekaznikiem.',8,11,1.2)
S['LOGIC'].text('SENSOR_LOCAL = PERMIT_LOCAL & SENSOR_OK_LOCAL. HEALTH_LOCAL = SENSOR_OK_LOCAL & FAULT_N.',8,61,1.2)
S['LOGIC'].text('Brak sprzetowego latch FAULT. U1 ogranicza prad; CORE musi zatrzasnac blad i cofnac PERMIT.',8,117,1.2)
# Outgoing buffers with series R and defaults, input Ioff buffer.
for r,x,y,a,u in [('U5',47,27,0,1),('R7',22,29,0,1),('R6',72,29,0,1),('U4',47,56,0,2),('R11',77,56,90,1),('R12',98,62,0,1),('U5',47,86,0,2),('R13',77,86,90,1),('R14',98,92,0,1),('U4',128,26,0,3),('U4',149,26,0,4),('U4',135,52,0,5),('U5',128,78,0,3),('U5',149,78,0,4),('U5',135,105,0,5)]:put('IO',r,x,y,a,u)
node('IO','SENSOR_OK_TX',[('U4',6),('R11',1)],56)
node('IO','SENSOR_OK',[('R11',2),('R12',1)],56)
node('IO','SENSOR_HEALTH_TX',[('U5',6),('R13',1)],86)
node('IO','SENSOR_HEALTHY',[('R13',2),('R14',1)],86)
S['IO'].text('U4/U5: Nexperia 74LVC125AD z Ioff, bez zamiany na HC125. Zasilanie obu 3V3_IO.',8,11,1.2)
S['IO'].text('Wyjscia SENSOR_OK i SENSOR_HEALTHY: 100R szeregowo, 10k do GND. Brak zasilania -> LOW u odbiorcy.',8,114,1.2)
S['IO'].text('HEALTHY=1 nie dowodzi zamkniecia K1, poprawnego mapowania pinow EGR ani obecnosci 5 V na czujniku.',8,119,1.2)
for r,x,y in [('J1',23,30),('J2',63,30),('J3',106,30),('J4',145,30)]:put('CONNECT',r,x,y)
S['CONNECT'].text('J1 -> P02/J8 (LV08). J2 -> P04-R2.1/J4 (SENSOR 6p, KEY2). J3 -> P03-R2/J6 (SFAULT 6p, KEY3).',8,11,1.2)
S['CONNECT'].text('J1/J2/J3: lutowane PTH, kotwa 12 mm. J4: gniazdo meskie na PCB; wiazka lutowana po stronie przyszlej P11.',8,51,1.2)
for i in range(1,14):put('CONNECT','TP'+str(i),18+(i-1)%5*30,68+(i-1)//5*16)
S['CONNECT'].text('TEST: mapowanie 5V/GND czujnika zatwierdzone poza P08. LOGGER: SENSOR_PERMIT=0; zasilanie czujnika pochodzi z ECU.',8,112,1.2)
ns=collections.defaultdict(set)
for sh in S.values():
 for pp,coords in sh.parts.values():
  for n in coords:ns[pp['pins'][n]].add(sh.name)
cadlib.CROSS={n for n,v in ns.items() if len(v)>1 and n!='NC'}
for sh in S.values():
 for net in cadlib.CROSS:sh.items=[t.replace('(label '+q(net)+' ','(global_label '+q(net)+' (shape passive) ') for t in sh.items]
 sh.text(f'P08-R1 / {sh.num:02d}   {sh.title.upper()}',8,7.5,2)
for i,(name,title) in enumerate(names[1:],2):
 sh=S[name];x,y=mm(131),mm((93+(i-2)*7)*.88);sid=uid('sheet/'+name)
 S['P08'].items.append(f'(sheet (at {x} {y}) (size 55.88 7.62) (stroke (width .15) (type default)) (fill (color 0 0 0 0)) (uuid {sid}) (property "Sheetname" {q(name)} (at {x} {y-1.27} 0) (effects (font (size 1 1)) (justify left bottom))) (property "Sheetfile" {q(name+".kicad_sch")} (at {x} {y+7.62} 0) (effects (font (size 1 1)) hide)) (instances (project "P08" (path {q("/"+uid("P08"))} (page "{i}")))))')
 old=sh.path;sh.path='/'+uid('P08')+'/'+sid;sh.items=[t.replace(q(old),q(sh.path)) for t in sh.items]
for sh in S.values():sh.finish();sh.save()
write_tables()
(P/'verification/sheet-parts.json').write_text(json.dumps({n:list(s.parts) for n,s in S.items()},indent=2))
print(len(PARTS),'parts; four sheets')
