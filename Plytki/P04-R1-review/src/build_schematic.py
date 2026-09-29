from parts import *
import cadlib,collections,copy
names=[('P04','Zasilanie i odsprzeganie'),('CON','Zlacza i interfejsy'),('RX','Bufory i stany domyslne'),('ILK','Gotowosc i interlock'),('WD','Watchdog, STOP i fizyczny ARM'),('OUT','Zezwolenia MOTOR / SENSOR')]
S={n:Sheet(n,t,i,None if i==1 else uid('P04')) for i,(n,t) in enumerate(names,1)}
def put(sh,r,x,y,a=0,u=1,off=None):
 pp=copy.copy(PARTS[r]);pp['display']=pp['display'].split(' / ')[0]
 if r.startswith('J'):pp['text_at']=(2,-(len(pp['pins'])//2)-3)
 if r.startswith('TP'):pp['text_at']=(3,-1)
 if r.startswith('U'):pp['text_at']=(-3,-5)
 if r.startswith('Q'):pp['text_at']=(4,-2)
 if off:pp['text_at']=off
 S[sh].place(pp,x,y,a,u)
def node(sh,net,refs,bus=None,axis='y'):S[sh].node(net,refs,bus,axis)
# Main supply: local supervisor, bulk, one capacitor for every IC and extra adapter capacitors.
put('P04','U11',70,22,off=(5,-3));put('P04','C14',87,22);put('P04','C3',24,22)
put('P04','R37',127,22,90);put('P04','LED1',145,22,90)
node('P04','LED_PWR',[('R37',2),('LED1',2)],22)
for r,x,y in [('TP1',15,16),('TP2',15,29),('TP3',97,22),('TP13',52,29)]:put('P04',r,x,y)
power_units={1:3,2:7,3:3,4:5,5:5,6:5,7:5,8:5,9:5,10:5}
for i,unit in power_units.items():
 x=16+36*((i-1)%4);y=45+22*((i-1)//4)
 put('P04',f'U{i}',x,y,u=unit,off=(3,-1));put('P04',f'C{i+3}',x+14,y)
 vp=16 if i==1 else 14;gp=8 if i==1 else 7
 node('P04',V,[(f'U{i}',vp),(f'C{i+3}',1)],y-7)
 node('P04',G,[(f'U{i}',gp),(f'C{i+3}',2)],y+7)
 if i>=8:
  put('P04',f'C{i+7}',x+25,y)
  S['P04'].text(f'C{i+7}: na adapterze U{i}',140 if i==8 else x+9,60 if i==8 else y+9,1.0)
for i,(net,x,y) in enumerate([(V,15,10),(G,39,10)],1):
 S['P04'].place({'ref':f'#FLG{i}','display':'PWR_FLAG','symbol':symbol('power','PWR_FLAG'),'source_ref':'ERC_SOURCE','mpn':'','footprint':'','pins':{'1':net}},x,y)
S['P04'].text('Zasilanie 3V3_IO z P02. 5V_SYS z LV04 jest dostepne na J1.1 i TP13; nie zasila logiki.',8,34,1.3)
S['P04'].text('U11: MCP100 w bondout D, 1 RESET / 2 VDD / 3 GND. Lokalny reset nie jest podlaczony push-pull do SAFE_N.',8,103,1.15)
# Connectors: numbered electrical mapping, physical geometry is in PCB/mechanics documentation.
for r,x,y in [('J1',25,27),('J2',80,23),('J3',135,23),('J4',25,61),('J5',80,61),('J6',135,61),('J7',25,88),('J8',90,88),('R38',134,91)]:put('CON',r,x,y)
S['CON'].text('J1 LV04: przewody AWG22 200 mm. J2 SAFE: tasma 16 zyl AWG28 150 mm. PTH + kotwa 12 mm.',8,12,1.3)
S['CON'].text('Klucze: SAFE 4 / DRIVE 2 / SENSOR 2 / DAQOK 4 / PSUOK 5. Pad klucza NC; usuniety styk w gniezdzie.',8,48,1.2)
S['CON'].text('SENSOR M2.2: IDC 6p; 1 permit, 2 KEY, 3 ready, 4 GND, 5/6 NC. Wymagana zgodna wiazka P08.',8,74,1.2)
S['CON'].text('PANELSAFE: STOP NC miedzy 1 i 7. ARM NO miedzy 9 i 10. Nie laczyc szyny P00 3V3 z P04 3V3_IO.',8,105,1.2)
# Receiver matrix: preserve independent input and post-adapter pulldowns.
for idx,signal in enumerate(signals):
 col,row=divmod(idx,4);x=25+52*col;y=23+22*row;u=8+col;unit=row+1
 put('RX',f'U{u}',x,y,u=unit)
 put('RX',f'R{12+idx}',x-11,y+6);put('RX',f'R{25+idx}',x+11,y+6)
 a,yp=[(2,3),(5,6),(9,8),(12,11)][row]
 node('RX',signal,[(f'U{u}',a),(f'R{12+idx}',1)],y)
 node('RX',signal+'_P04',[(f'U{u}',yp),(f'R{25+idx}',1)],y)
put('RX','U10',129,89,u=4)
S['RX'].text('74LVC125AD Nexperia: Ioff; pin wejscia nie zasila nieaktywnej domeny. Nie zastapic ukladem HC125.',8,107,1.2)
# Module combination, explicit key qualification uses one former spare gate.
for r,x,y,u in [('U6',22,25,1),('U6',72,25,2),('U6',122,25,3),('U6',47,50,4),('U7',90,50,1),('U7',135,50,3),('U7',110,76,2),('U7',22,91,4)]:put('ILK',r,x,y,u=u)
for r,x,y in [('R23',28,66),('R24',48,66),('R36',145,89),('TP10',135,76)]:put('ILK',r,x,y)
S['ILK'].text('MODULES_OK = PSU_OK & DAQ_OK & DRIVE_OK & SENSOR_OK & CORE_LINK & PG_LINK (po buforach).',8,12,1.3)
S['ILK'].text('INTERLOCK = MODULES_OK & MECH_OK & TEST_KEY. P11 MECH_OK zawiera klucz, oba styki LOGGER i petle TEST.',8,104,1.2)
S['ILK'].text('READY nie zalezy od przekaźnika, ktory ma uzbroic. Powrot READY nie wywoluje nowego zbocza ARM.',8,108,1.2)
# Watchdog and wired collector reset: main analog paths are drawn as wires.
for r,x,y,a,u in [('U1',45,25,0,1),('R1',15,16,0,1),('C1',28,22,0,1),('U5',82,25,0,3),('U1',140,25,0,2)]:put('WD',r,x,y,a,u)
node('WD','WD_RC',[('R1',2),('C1',1),('U1',15)],19)
node('WD','WD_C',[('C1',2),('U1',14)],24)
for qr,x,unit in [('Q1',37,1),('Q2',87,3),('Q3',137,4)]:
 i=int(qr[-1]);put('WD','U2',x-25,58,u=unit);put('WD',f'R{i+5}',x-12,58,90);put('WD',qr,x,58);put('WD',f'R{i+8}',x-6,67)
 yp={1:2,3:6,4:8}[unit]
 node('WD',PARTS[f'R{i+5}']['pins']['1'],[('U2',yp),(f'R{i+5}',1)],58)
 node('WD',f'Q{i}_B',[(f'R{i+5}',2),(qr,2),(f'R{i+8}',1)],58)
put('WD','R4',153,40);put('WD','R5',153,59)
node('WD','SAFE_N',[('Q1',3),('Q2',3),('Q3',3),('R4',2),('R5',1)],49)
for r,x,y,a in [('R2',43,76,0),('R3',27,87,270),('C2',43,97,0)]:put('WD',r,x,y,a)
put('WD','U2',62,87,u=2);put('WD','U3',105,87,u=1)
node('WD','ARM_BUTTON_N',[('R2',2),('R3',1),('C2',1),('U2',3)],43,'x')
node('WD','ARM_CLK',[('U2',4),('U3',3)],87)
put('WD','U2',70,103,u=5);put('WD','U2',93,103,u=6)
node('WD','SAFE_OK_N',[('U2',10),('U2',13)],103)
put('WD','U3',143,87,u=2)
for r,x,y in [('TP4',96,25),('TP5',62,21),('TP6',145,49),('TP7',110,103),('TP8',84,87),('TP9',119,86)]:put('WD',r,x,y)
S['WD'].text('U1 CLR = SUP_OK, niezaleznie od SAFE_N. C1 pomiedzy pinami 15 i 14; pin 14 NIE jest masa.',8,11,1.3)
S['WD'].text('SAFE_N: tylko rezystory i kolektory. RESET latch: SAFE_OK po dwoch bramkach Schmitta.',8,38,1.2)
S['WD'].text('WD: cel 50-150 ms przy 3V3, do pomiaru. ARM: zwolnic i nacisnac ponownie po bledzie.',8,109,1.15)
# Permits remain separate: sensor can run with HW_ARMED=0; both depend on SAFE_OK.
for r,x,y,u in [('U4',25,26,1),('U4',72,26,2),('U5',120,26,4),('U4',120,52,3),('U4',25,79,4),('U5',72,79,1),('U5',120,79,2)]:put('OUT',r,x,y,u=u)
put('OUT','TP11',143,26);put('OUT','TP12',143,79)
S['OUT'].text('MOTOR_PERMIT = HW_ARMED & MCU_ARM & INTERLOCK & SAFE_OK. PWM_OUT = PWM & MOTOR_PERMIT.',8,12,1.3)
S['OUT'].text('SENSOR_PERMIT = SENSOR_ENABLE & TEST_KEY & INTERLOCK & SAFE_OK. Fizyczny ARM nie jest potrzebny do samego czujnika.',8,99,1.2)
S['OUT'].text('P07 pozostaje HOLD do kontroli rzeczywistego BTS7960. P04 nie ustala pradu ani kierunku mostka.',8,105,1.2)
# All global nets are determined from the sheets actually containing the pins.
ns=collections.defaultdict(set)
for name,sh in S.items():
 for part,pins in sh.parts.values():
  for n in pins:ns[part['pins'][n]].add(name)
cadlib.CROSS={n for n,v in ns.items() if len(v)>1 and n!='NC'}
# Existing node labels were created before CROSS was known; promote cross-sheet names consistently.
for sh in S.values():
 for net in cadlib.CROSS:
  sh.items=[item.replace('(label '+q(net)+' ','(global_label '+q(net)+' (shape passive) ') for item in sh.items]
 sh.text(f'P04-R1 / {sh.num:02d}   {sh.title.upper()}',8,5,2)
for i,(name,title) in enumerate(names[1:],2):
 sh=S[name];x,y=mm(91+(i-2)%2*33),mm(75+(i-2)//2*8);sid=uid('sheet/'+name)
 S['P04'].items.append(f'(sheet (at {x} {y}) (size 76.2 12.7) (stroke (width .15) (type default)) (fill (color 0 0 0 0)) (uuid {sid}) (property "Sheetname" {q(name)} (at {x} {y-1.27} 0) (effects (font (size 1.1 1.1)) (justify left bottom))) (property "Sheetfile" {q(name+".kicad_sch")} (at {x} {y+13.97} 0) (effects (font (size 1.1 1.1)) (justify left top))) (instances (project "P04" (path {q("/"+uid("P04"))} (page "{i}")))))')
 old=sh.path;sh.path='/'+uid('P04')+'/'+sid;sh.items=[t.replace(q(old),q(sh.path)) for t in sh.items]
for sh in S.values():sh.finish();sh.save()
write_tables()
(P/'verification/sheet-parts.json').write_text(json.dumps({n:list(s.parts) for n,s in S.items()},indent=2))
print(len(PARTS),'parts; six A3 sheets')
