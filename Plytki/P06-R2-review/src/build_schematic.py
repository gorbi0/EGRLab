from parts import *
import cadlib,collections,copy
names=[('P06','Zasilanie lokalne'),('FORCE','Bocznik i mechaniczny BYPASS'),('ANA','Pomiar pradu i odniesienie'),('DIG','ADC i interfejs SPI'),('READY','Sygnal gotowosci'),('CONNECT','Zlacze J_BP do P12 (krawedz A)'),('SERWIS','Listwy serwisowe J_SV1/J_SV2 (krawedz B)')]
S={n:Sheet(n,t,i,None if i==1 else uid('P06')) for i,(n,t) in enumerate(names,1)}
def put(sh,r,x,y,a=0,u=1,off=None):
 pp=copy.copy(PARTS[r]);pp['display']=pp['display'].split(' / ')[0]
 if r.startswith('U'):pp['text_at']=(-5,-7)
 if r.startswith('J'):pp['text_at']=(2,-(len(pp['pins'])//2)-3)
 if r.startswith('TP'):pp['text_at']=(2,-1)
 if off:pp['text_at']=off
 S[sh].place(pp,x,y,a,u)
def node(sh,n,refs,bus=None,axis='y'):S[sh].node(n,refs,bus,axis)
# Power tree and discharge path: LV06.3 is deliberately not a power source.
for r,x,y,a in [('R6',28,20,90),('C3',45,27,0),('U4',72,23,0),('D1',73,11,90),('C4',98,27,0),('R24',113,27,0),('C9',56,27,0)]:put('P06',r,x,y,a)
node('P06',A5,[('R6',2),('C3',1),('U4',2),('C9',1)],20)
node('P06',V,[('U4',3),('C4',1),('R24',1)],23)
for i,(ref,unit,capref,x,y,vpin,gpin) in enumerate([('U2',3,'C7',20,53,8,4),('U5',5,'C10',62,53,14,7),('U6',5,'C11',105,53,14,7),('U7',5,'C12',20,78,14,7)]):
 put('P06',ref,x,y,u=unit,off=(3,-2));put('P06',capref,x+16,y)
 node('P06',V,[(ref,vpin),(capref,1)],y-8)
 node('P06',G,[(ref,gpin),(capref,2)],y+8)
for r,x,y in [('C8',62,78),('C13',81,78),('C14',100,78),('C15',119,78)]:put('P06',r,x,y)
for i,(n,x) in enumerate([('5V_SYS',15),(G,38),(A5,62),('3V3_IO',89)],1):
 S['P06'].place({'ref':f'#FLG{i}','display':'PWR_FLAG','symbol':symbol('power','PWR_FLAG'),'source_ref':'ERC_SOURCE','mpn':'','footprint':'','pins':{'1':n}},x,99)
S['P06'].text('J_BP: 5V_SYS (piny 10/12) zasila plytke. 3V3_IO (J_BP.14) idzie tylko na kolek J_SV2. Logika pracuje z lokalnego 3V3_P06.',8,37,1.25)
S['P06'].text('D1: anoda 3V3_P06, katoda 5VA_P06. Budzet MEASURE: 180 mA, wiekszosc poboru przez R21 obciazajacy styk. R6 1R/1W lezacy; C3 220u (1.10): impuls ladowania ok. 3 mJ.',8,104,1.2)
# Force circuit (always present) and independent auxiliary pole.
put('FORCE','J3',20,32);put('FORCE','RSH1',75,31,90,off=(-6,-8));put('FORCE','J4',131,30)
put('FORCE','SW1',76,69,u=1,off=(-3,-6));put('FORCE','SW1',76,85,u=2,off=(-3,-6));put('FORCE','J5',24,76);put('FORCE','R21',126,76)
node('FORCE','ECU_P1',[('J3',1),('RSH1',1),('J4',1)],24)
node('FORCE','EGR_P1',[('J3',2),('RSH1',4),('J4',2)],40)
node('FORCE','K_PLUS',[('RSH1',2)],26)
node('FORCE','K_MINUS',[('RSH1',3)],28)
S['FORCE'].text('RSH1 5 mOhm 2512 Kelvin (pady 1/4 pradowe, 2/3 pomiarowe) stale w torze ECU_P1 -> EGR_P1. Brak przelacznika szeregowego i polaczenia mocy z GND.',8,11,1.3)
S['FORCE'].text('BYPASS: SW1 2-3 + 5-6. MEASURE: SW1 2-1 (NC) + 5-4. COM to zaciski 2 i 5, nie 1 i 4.',8,49,1.3)
S['FORCE'].text('SW1 na panelu (DPDT ON-ON >=10 A DC, oczka). J4.1 -> SW1.2; J4.2 -> SW1.3. J5.1 -> SW1.4; J5.2 -> SW1.5; J5.3 -> SW1.6. J3/J4/J5 przy brzegu x=0.',8,97,1.25)
S['FORCE'].text('R21: 39R PR02 2W lezacy, prad styku ok. 0.13 A (0.71 W przy 5.25 V). Goracy element oddalony od bocznika. Nie przelaczac przy wlaczonym zaplonie.',8,104,1.2)
# INA pins and conventional op-amp feedback drawn explicitly.
put('ANA','U1',47,27,u=1);put('ANA','R1',18,26,90);put('ANA','R2',18,31,90)
put('ANA','R3',72,26,90);put('ANA','R4',91,34);put('ANA','C1',104,34);put('ANA','U2',132,29,u=1,off=(-3,-7))
node('ANA','INA_PLUS',[('R1',2),('U1',8)],26)
node('ANA','INA_MINUS',[('R2',2),('U1',1)],31)
node('ANA','I_L_OUT',[('U1',5),('R3',1)],26)
node('ANA','I_DIV',[('R3',2),('R4',1),('C1',1),('U2',3)],29)
node('ANA','ADC_BUF',[('U2',1),('U2',2)],145,'x')
put('ANA','D2',45,93,90);put('ANA','U10',30,71);put('ANA','C5',51,79);put('ANA','U2',79,74,u=2,off=(-3,-8))
put('ANA','U1',121,74,u=2);put('ANA','C6',145,75)
node('ANA','REF25',[('U10',2),('C5',1),('U2',5)],71)
node('ANA','REF_BUF',[('U2',6),('U2',7),('U1',7),('U1',3)],91,'x')
S['ANA'].text('5 mOhm x 50 V/V x 1/2 = 0.125 V/A. ADC: 1.25 V przy 0 A, idealnie 204.8 kodu/A; kalibracja offsetu i nachylenia obowiazkowa.',8,11,1.2)
S['ANA'].text('R3/R4 5.11k 0.1% (R3 || R4 = 2.555k); C1 = 470n X7R: fc = 133 Hz, tau = 1.20 ms. Pomiar trendu pradu; nie przebieg pojedynczych impulsow PWM.',8,48,1.25)
S['ANA'].text('U1 SOIC D: 8 IN+, 1 IN-, 5 OUT, 6 VS, 2 GND, 7 REF1, 3 REF2, 4 NC. Oba REF sterowane wspolnym buforem.',8,101,1.2)
S['ANA'].text('U10 TO92: 1 GND, 2 VOUT, 3 VIN. C5 4.7uF X7R 1206 przy U10; R1/R2 10R 0.1% identyczne, sciezki Kelvin lokalne.',8,107,1.2)
# MCP3201 conversion framing and Ioff buffer.
put('DIG','C16',19,45);put('DIG','U3',41,30);put('DIG','R5',16,25,90);put('DIG','C2',25,39)
node('DIG','ADC_AIN',[('R5',2),('U3',2),('C2',1)],26)
for r,x,y,u in [('U5',99,25,1),('U5',99,49,2),('U5',99,74,3),('U5',142,89,4)]:put('DIG',r,x,y,u=u)
for r,x,y in [('R7',122,19),('R8',76,19),('R9',122,45),('R10',76,45),('R11',76,69)]:put('DIG',r,x,y)
put('DIG','R12',130,74,90)
node('DIG','DOUT_TX',[('U5',8),('R12',1)],74)
S['DIG'].text('SPI mode 0, 500 kHz, 16 zegarow. raw = (word >> 1) & 0x0FFF. DOUT odlaczony od wspolnej magistrali gdy CS_LOCAL_N=1.',8,11,1.25)
S['DIG'].text('2 kS/s z firmware v6.1. Probka niesymultaniczna wzgledem AD7606B; zachowac timestamp/skew. Nie wyprowadzac I2C do analogu.',8,103,1.2)
S['DIG'].text('U5/U6 tylko Nexperia 74LVC125AD z Ioff. HC125 nie jest zamiennikiem. SOIC/SO14 raster 1.27 mm.',8,108,1.2)
# Readiness independently observes both supplies and mechanical mode.
put('READY','U8',29,23);put('READY','R14',12,18);put('READY','U9',29,51);put('READY','R13',12,46)
put('READY','U6',73,48,u=1);put('READY','R15',88,55)
put('READY','U7',118,28,u=1);put('READY','R17',142,33)
put('READY','R22',22,78,90);put('READY','R23',40,87);put('READY','U6',73,78,u=2);put('READY','R16',88,87)
node('READY','SW_SENSE',[('R22',2),('R23',1),('U6',5)],78)
put('READY','U7',118,71,u=2);put('READY','R18',142,76)
put('READY','U6',52,99,u=3);put('READY','R19',80,99,90);put('READY','R20',95,99)
put('READY','U6',117,89,u=4);put('READY','U7',142,48,u=3);put('READY','U7',142,87,u=4)
S['READY'].text('LOGGER_CURRENT_OK = SUP3_N & SUP5_N & SHUNT_ENABLED; BYPASS daje LOW. READY nie jest dowodem kalibracji ani sprawnosci bocznika.',8,10,1.2)
S['READY'].text('MCP120: -300 reset 2.85..3.00 V, -450 reset 4.25..4.50 V. Histereza 50 mV TYP; odbior przy minimalnym zasilaniu.',8,111,1.1)
# Edge A connector (S1 5) and service strips (S1 6).
put('CONNECT','J_BP',30,40)
S['CONNECT'].text('J_BP: katowe obudowane IDC 2x8 na krawedzi A, slot S2 (srodek x=80.0 mm), pin 1 od strony mniejszego x. Tasma ok. 30 mm do P12.',8,12,1.25)
S['CONNECT'].text('ADC_SCLK/ADC_DOUTA na pinach 2/4 jak J_BP2 plytek P03 R6 i P05 R3. Nieparzyste GND, 16 GND (rezerwa). Zastepuje J1 LV06 i J2 ILOG z R1.',8,15.5,1.2)
S['CONNECT'].text('3V3_IO (pin 14) nie ma odbiorcy na P06 (jak LV06.3 -> TP4 w R1): tylko kolek J_SV2.6 przez 1k.',8,75,1.2)
for row,(jref,y0) in enumerate([('J_SV1',24),('J_SV2',62)]):
 put('SERWIS',jref,18,y0+8)
 rr=[v for v in SERVICE.values() if v[0]==jref]
 for k,(j,pin,r,ohm,why) in enumerate(rr):put('SERWIS',r,48+k*9.5,y0+4+(k%2)*10)
S['SERWIS'].text('J_SV1 (slot S1, x=10..43): wezly analogowe przez 10k, GND na 1, 4, 7. J_SV2 (slot S2, x=63.5..96.5): szyny i logika, GND na 1, 5, 13.',8,12,1.25)
S['SERWIS'].text('Rezystor przy wezle: 1k szyny/logika, 10k wezly analogowe i SUP3_N/SUP5_N. Szyna tylko obok GND, innej szyny albo linii 10k. Numeracja zawsze od pinu 1.',8,15.5,1.15)
# Promote shared names to actual cross-sheet connections.
ns=collections.defaultdict(set)
for name,sh in S.items():
 for part,pins in sh.parts.values():
  for n in pins:ns[part['pins'][n]].add(name)
cadlib.CROSS={n for n,v in ns.items() if len(v)>1 and n!='NC'}
for sh in S.values():
 for net in cadlib.CROSS:sh.items=[t.replace('(label '+q(net)+' ','(global_label '+q(net)+' (shape passive) ') for t in sh.items]
 sh.text(f'{cadlib.REV} / {sh.num:02d}   {sh.title.upper()}',8,5,2)
for i,(name,title) in enumerate(names[1:],2):
 sh=S[name];x,y=mm(132),mm(43+(i-2)*10);sid=uid('sheet/'+name)
 S['P06'].items.append(f'(sheet (at {x} {y}) (size 55.88 10.16) (stroke (width .15) (type default)) (fill (color 0 0 0 0)) (uuid {sid}) (property "Sheetname" {q(name)} (at {x} {y-1.27} 0) (effects (font (size 1 1)) (justify left bottom))) (property "Sheetfile" {q(name+".kicad_sch")} (at {x} {y+10.16} 0) (effects (font (size 1 1)) (justify left top))) (instances (project "P06" (path {q("/"+uid("P06"))} (page "{i}")))))')
 old=sh.path;sh.path='/'+uid('P06')+'/'+sid;sh.items=[t.replace(q(old),q(sh.path)) for t in sh.items]
for sh in S.values():sh.finish();sh.save()
write_tables()
(P/'verification/sheet-parts.json').write_text(json.dumps({n:list(s.parts) for n,s in S.items()},indent=2))
print(len(PARTS),'parts; seven sheets')
