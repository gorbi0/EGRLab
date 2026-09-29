"""P02-R3 (R2 layout of four readable A3 sheets; R3: D1 fields off the VLOG_RES label, global labels off the bus wires)."""
from parts import *
import cadlib, collections, copy
S={n:Sheet(n,t,i,None if i==1 else uid('P02')) for i,(n,t) in enumerate([
 ('P02','Wejscie i rezerwa HOLD'),('LV','Przetwornice i rozdzial LV'),
 ('MON','Nadzor szyn i logika gotowosci'),('HOLD','Komparatory: filtr przed sprzezeniem')],1)}
def put(sh,r,x,y,a=0,u=1):
 p=copy.copy(PARTS[r]);p['sch_value']=p['display'].split(' / ')[0]
 if r.startswith('J'):p['sch_value']={'J1':'SUPPLY','J2':'VMOTOR','J11':'VSENSE','J12':'PSUOK','J13':'R_CHARGE'}.get(r,p['sch_value'])
 if r.startswith('U'):p['fields']=(-5,-14) if u!=5 else (4,-7)
 if r.startswith('J'):p['fields']=(-5,-12)
 if r.startswith('TP'):p['fields']=(3,-4);p['sch_value']=''
 if r.startswith('D'):p['fields']=(6,-12)
 if r=='D1':p['fields']=(-19,-3)  # R3: left of the symbol, clear of VLOG_RES
 if a%180 and r.startswith(('R','F')):p['fields']=(-5,-8)
 if r in ('U3','U4'):p['fields']=(10,-10)
 if r=='U8':p['fields']=(-22,-8)
 if (r=='U7' and u==3) or (r in ('U5','U6') and u==5):p['fields']=(10,-10)
 if r=='J11':p['fields']=(-5,-24)
 if r=='LED1':p['fields']=(6,-8);p['sch_value']='GREEN 3mm'
 S[sh].place(p,x,y,a,u)
def rows(sh,items):
 for item in items:put(sh,*item)
rows('P02',[
 ('J1',16,24),('TP1',29,16),('J13',48,24),('R17',68,24,90),('D2',89,24,90),('F1',110,24,90),
 ('R20',137,24,90),('TP3',155,24),('C1',115,45),('C2',128,45),('C3',141,45),('R1',154,45),
 ('J2',16,60),('F4',45,60,90),('J11',65,61),('D1',91,66,90),('C4',110,70),('TP2',127,62),('TP6',145,70)])
rows('LV',[
 ('F2',19,26,90),('C5',37,30),('U1',55,26),('C6',69,30),('TP4',79,23),
 ('F3',98,26,90),('C7',114,30),('U2',132,26),('C8',146,30),('TP5',156,23)])
for i in range(8):put('LV',f'J{i+3}',25+37*(i%4),62+25*(i//4))
rows('MON',[
 ('U4',20,25),('R3',36,22),('C10',46,26),('U5',72,25,0,1),('U3',112,25),('R2',131,22),('C9',142,26),
 ('U6',25,52,0,1),('R4',45,56),('TP7',57,49),('U6',74,52,0,2),('U6',99,52,0,3),
 ('R14',119,51,90),('TP8',132,45),('R15',112,65),('R16',132,65),('LED1',144,65,90),('J12',151,88),
 ('U5',18,85,0,5),('C11',28,86),('C16',39,86),('U6',55,85,0,5),('C12',67,86),
 ('U6',86,87,0,4),('U5',105,87,0,2),('U5',105,102,0,3),('U5',128,87,0,4)])
rows('HOLD',[
 ('R6',21,24),('R7',21,44),('C14',34,44),('R18',46,35,90),('U7',68,36,0,1),('R8',61,18,270),('R12',88,24),
 ('R9',21,66),('R10',21,86),('C15',34,86),('R19',46,77,90),('U7',68,78,0,2),('R11',61,60,270),('R13',88,66),
 ('R5',116,26),('U8',116,44),('TP9',129,34),('U7',139,67,0,3),('C13',151,70),('TP10',141,91)])
ns=collections.defaultdict(set)
for name,sh in S.items():
 for part,pins in sh.parts.values():
  for n in pins:ns[part['pins'][n]].add(name)
cadlib.CROSS={n for n,v in ns.items() if len(v)>1 and n!='NC'}
def connect(sh,net,refs,bus=None,axis='y'):S[sh].node(net,refs,bus,axis)
connect('P02','HOLD_STORE',[('F1',2),('R20',1),('C1',1),('C2',1),('C3',1),('R1',1)],35)
connect('P02','HOLD_TP',[('R20',2),('TP3',1)],24)
connect('P02','GND',[('C1',2),('C2',2),('C3',2),('R1',2)],54)
connect('P02','HOLD_FUSED',[('D2',2),('F1',1)],24)
connect('P02','VLOG_RES',[('D1',2),('C4',1),('TP2',1)],62)
for off,rt,rb,cc,rs,rf,rp,inp,out in [(0,'R6','R7','C14','R18','R8','R12',3,1),(42,'R9','R10','C15','R19','R11','R13',5,7)]:
 div=PARTS[rt]['pins']['2'];cmp=PARTS[rs]['pins']['2'];ok=PARTS[rp]['pins']['1']
 connect('HOLD',div,[(rt,2),(rb,1),(cc,1),(rs,1)],35+off)
 connect('HOLD',cmp,[(rs,2),(rf,2),('U7',inp)],55,'x')
 connect('HOLD',ok,[(rf,1),('U7',out),(rp,1)],94,'x')
 connect('HOLD','GND',[(rb,2),(cc,2)],51+off)
connect('HOLD','P02_REF25',[('R5',2),('U8',1),('U8',3),('TP9',1)],34)
flag=symbol('power','PWR_FLAG')
for i,(sh,net,x,y) in enumerate([('P02','VPROT',16,39),('P02','GND',30,39),('LV','P02_VIN_DC5',25,43),('LV','P02_VIN_DC33',108,43)],1):
 part={'ref':f'#FLG{i}','display':'PWR_FLAG','source_ref':'ERC_SOURCE','mpn':'','footprint':'','symbol':flag,'pins':{'1':net},'qty':0,'url':''};S[sh].place(part,x,y)
for name,sh in S.items():sh.text(f'P02-R3 / {sh.num:02d}   {sh.title.upper()}',8,6,2)
S['P02'].text('R17 poza PCB: HSA2547RJ na osobnej blasze. J13 jest zakonczeniem jego przewodow.',8,78,1.3)
S['P02'].text('TP3 przez R20=1k/2W. DMM >=10 Mohm. Bank 3x22mF: do 41J przy 32V, rozladowanie przez R1 do 22 min.',8,81,1.3)
S['P02'].text('F1 T2A, F4 T0,5A: Schurter SPT 5x20, 300 VDC. VSENSE niesie ok. 25 uA; F4 chroni tylko przewod.',8,84,1.3)
S['LV'].text('BUDZET LACZNY <=6W na VLOG_RES (wliczaj straty przetwornic). Nie 2A na kazde zlacze.',8,46,1.5)
S['LV'].text('F2/F3: Schurter 0001.2504 T1A, 300 VDC - zwloczne, jak zaleca TRACO dla TSR2.',8,54,1.3)
S['LV'].text('LV03..LV10: 1=5V_SYS, 2=GND, 3=3V3_IO, 4=GND. Nie laczyc 3V3_IO z 3V3_CORE.',8,50,1.3)
S['LV'].text('Dodatkowa pojemnosc obciazenia: suma <=600uF na 5V i <=900uF na 3V3 (wlicz C6/C8).',8,97,1.3)
S['MON'].text('U5A: wejscie toleruje 5V; zasilanie 3V3. C16 na adapterze przy samym IC (nie na plycie P02).',8,36,1.3)
S['MON'].text('HOLD_READY = BANK_OK & VPROT_OK & PSU_OK. Sygnal lokalny; J12.3 na P04 nadal NC.',8,71,1.3)
S['MON'].text('15 s kwalifikacji wykonuje operator. CORE nie realizuje tej funkcji w tej rewizji.',8,74,1.3)
S['HOLD'].text('FILTR: C14/C15 PRZED R18/R19. Sprzezenie R8/R11 za nimi, przy wejsciu komparatora.',8,97,1.3)
S['HOLD'].text('Progi z tolerancjami: docs/HOLD-ANALIZA.md. Przerwany F1: LED gasnie po ok. 1-2 min (R1 rozladowuje bank). Ceff nie jest sprawdzane.',8,104,1.3)
S['HOLD'].text('U8 TI LP: 1=K, 2=A, 3=REF.',105,50,1.2)
S['HOLD'].text('R6/R7/R9/R10: 0.1%, 25ppm/K.',105,53,1.2)
S['HOLD'].text('R5: 330R, IKA ok. 7.6mA.',105,56,1.2)
for i,name in enumerate(['LV','MON','HOLD'],2):
 sh=S[name];x,y=mm(10+(i-2)*50),mm(88);sid=uid('sheet/'+name)
 S['P02'].items.append(f'(sheet (at {x} {y}) (size 101.6 20.32) (stroke (width .15) (type default)) (fill (color 0 0 0 0)) (uuid {sid}) (property "Sheetname" "{name}" (at {x} {y-1.27} 0) (effects (font (size 1.3 1.3)) (justify left bottom))) (property "Sheetfile" "{name}.kicad_sch" (at {x} {y+21.59} 0) (effects (font (size 1.3 1.3)) (justify left top))) (instances (project "P02" (path {q("/"+uid("P02"))} (page "{i}")))))')
 old=sh.path;sh.path='/'+uid('P02')+'/'+sid;sh.items=[t.replace(q(old),q(sh.path)) for t in sh.items]
for sh in S.values():sh.finish();sh.save()
write_tables()
(P/'verification/sheet-parts.json').write_text(json.dumps({n:list(s.parts) for n,s in S.items()},indent=2))
print(f'{len(PARTS)} parts; four A3 sheets written')


