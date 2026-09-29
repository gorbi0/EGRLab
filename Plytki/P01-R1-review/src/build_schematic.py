from parts import *
import cadlib,collections
S={n:Sheet(n,t,i+1,uid('P01') if i else None) for i,(n,t) in enumerate([('P01','Tor mocy i sterowanie bramka'),('AUX','Zasilanie pomocnicze i okno napiecia'),('SAFE','Zezwolenie i interfejs SAFE')])}
def put(s,r,x,y,a=0,u=1,m=None):
 if r in ['R24','R25']:a=180
 if r.startswith('R') and a==270:a=90
 if r in ['J7','J1']:x=17
 if r in ['J6','J2']:x=148;y=19 if r=='J6' else 46
 if r=='TP9':x,y=140,89
 S[s].place(PARTS[r],x,y,a,u,m)
def node(s,net,refs,b=None,axis='y'):S[s].node(net,refs,b,axis)
# Positions are intentional functional groups, in 2.54 mm units.
for r,x,y,a in [('J7',12,22,0),('J1',12,36,0),('D1',24,32,90),('D2',46,22,0),('Q1',83,22,270),('C1',65,32,0),('C2',76,32,0),('D3',95,32,270),('C3',107,32,0),('C4',118,32,0),('R28',129,32,0),('R29',141,28,0),('LED1',141,37,90),('J6',154,24,0),('J2',154,38,0),('R17',99,92,270),('R18',104,99,0),('R19',22,92,270),('R20',28,99,0),('Q3',115,92,0),('Q5',35,92,0),('R21',116,79,0),('R22',130,67,180),('R23',55,79,0),('R24',78,65,0),('R25',25,65,0),('R26',36,79,0),('R27',68,77,0),('D4',142,67,270),('C6',153,67,180),('C5',141,86,0),('TP1',54,46,0),('TP2',93,106,0)]:put('P01',r,x,y,a)
put('P01','Q2',67,65,m='x');put('P01','Q4',38,65,m='x')
for r,x,y,a in [('R1',23,24,270),('D5',38,32,270),('C7',49,32,0),('C8',60,32,0),('U1',75,24,0),('R2',94,29,0),('C9',94,39,0),('C10',110,32,0),('C11',124,32,0),('R3',22,63,0),('U3',22,79,90),('R4',38,79,0),('D6',23,99,180),('R12',42,104,0),('R5',72,59,0),('RV1',72,69,0),('R6',72,82,0),('R7',88,68,270),('R8',98,59,0),('C12',89,83,0),('R9',75,99,270),('R10',90,105,0),('R11',98,93,0),('C13',105,105,0),('U4',144,71,0),('R13',153,57,0),('TP3',15,46,0),('TP4',55,46,0),('TP5',15,89,0),('TP8',116,83,0),('TP9',136,106,0)]:put('AUX',r,x,y,a)
put('AUX','U2',108,75,u=1);put('AUX','U2',115,96,u=2);put('AUX','U2',140,32,u=3)
for r,x,y,a in [('R14',21,28,270),('D7',37,28,180),('D8',53,28,180),('R15',65,39,0),('Q6',78,28,0),('R16',95,39,0),('R30',62,62,0),('R31',51,87,0),('R32',22,78,270),('R33',29,87,0),('Q7',69,78,0),('Q8',38,78,0),('J3',21,103,0),('J4',116,83,0),('J5',116,61,0),('J8',147,93,0),('R34',119,94,270),('TP6',117,28,0),('TP7',144,28,0),('TP10',73,103,0)]:put('SAFE',r,x,y,a)
# Global labels only where a net really crosses sheets.
ns=collections.defaultdict(set)
for name,s in S.items():
 for p,pins in s.parts.values():
  for n in pins:ns[p['pins'][n]].add(name)
cadlib.CROSS={n for n,v in ns.items() if len(v)>1 and n!='NC'}
# Actual wires within functional blocks; labels at boundaries carry rail names.
node('P01','BAT_FUSED',[('D2',1),('D2',3)],18)
node('P01','P01_VS',[('D2',2),('C1',1),('C2',1),('Q1',3)],26)
node('P01','VPROT',[('Q1',2),('D3',1),('C3',1),('C4',1),('R28',1)],26)
node('P01','GND',[('D3',2),('C3',2),('C4',2),('R28',2)],43)
node('P01','GND',[('C1',2),('C2',2)],43)
node('P01','P01_LED_A',[('R29',2),('LED1',2)])
node('P01','P01_VS',[('Q4',1),('Q2',1),('R25',2),('R24',2)],58)
# R24/R25 have been rotated so their VS terminal is at the top.
node('P01','P01_OFF_BASE',[('Q4',3),('Q2',2),('R23',1),('R24',1)],72)
node('P01','P01_RELEASE_PBASE',[('Q4',2),('R25',1),('R26',1)],71)
node('P01','P01_RELEASE_COL',[('R26',2),('Q5',3)])
node('P01','P01_OFF_COL',[('Q2',3),('R27',1)])
node('P01','P01_ON_COL',[('R21',2),('Q3',3)])
node('P01','P01_RELEASE_BASE',[('R19',2),('R20',1),('Q5',2)],92)
node('P01','P01_ON_BASE',[('R17',2),('R18',1),('Q3',2)],92)
node('P01','GND',[('R20',2),('Q5',1)],103)
node('P01','GND',[('R18',2),('Q3',1)],103)
node('P01','P01_VS',[('R22',2),('D4',1),('C6',2)],59)
node('P01','P01_GATE',[('R21',1),('R22',1),('D4',2),('C6',1),('C5',1)],75)

node('AUX','P01_AUX_IN',[('R1',2),('D5',1),('C7',1),('C8',1),('U1',3)],24)
node('AUX','GND',[('D5',2),('C7',2),('C8',2),('U1',2)],44)
node('AUX','P01_AUX5',[('U1',1),('R2',1),('C10',1),('C11',1),('U2',8)],24)
node('AUX','P01_C_AUX_TOP',[('R2',2),('C9',1)])
node('AUX','GND',[('C9',2),('C10',2),('C11',2),('U2',4)],45)
node('AUX','P01_REF',[('R3',2),('U3',1),('U3',3),('R4',1)],72)
node('AUX','GND',[('U3',2),('R4',2)],85)
node('AUX','P01_SENSE_RAW',[('D6',1),('R12',1)],99)
node('AUX','P01_OV_TRIM_TOP',[('R5',2),('RV1',1),('RV1',2)],64)
node('AUX','P01_OV_SENSE',[('RV1',3),('R6',1),('C12',1),('U2',2)],76)
node('AUX','P01_OV_REF',[('R7',2),('R8',2),('U2',3)],68)
node('AUX','GND',[('R6',2),('C12',2)],88)
node('AUX','P01_UV_SENSE',[('R9',2),('R10',1),('R11',2),('C13',1),('U2',5)],95)
node('AUX','GND',[('R10',2),('C13',2)],111)
node('AUX','P01_OK',[('R13',2),('U4',1)],70)

node('SAFE','P01_BUF_D1',[('R14',2),('D7',2)])
node('SAFE','P01_BUF_D2',[('D7',1),('D8',2)])
node('SAFE','P01_BUF_BASE',[('D8',1),('R15',1),('Q6',2)],28)
node('SAFE','P01_ENABLE',[('Q6',1),('R16',1)],34)
node('SAFE','GND',[('R15',2),('R16',2)],45)
node('SAFE','P01_FAULT_RELEASE_BASE',[('R32',2),('R33',1),('Q8',2)],78)
node('SAFE','P01_FAULT_BASE',[('R30',2),('R31',1),('Q8',3),('Q7',2)],70)
node('SAFE','GND',[('R33',2),('R31',2),('Q8',1),('Q7',1)],95)

S['P01'].text('P01 / 01   TOR MOCY',8,6,2)
S['P01'].text('Wejscie za zewnetrznym bezpiecznikiem 5 A. Prad calosci <=5 A po odbiorze termicznym.',8,10)
S['P01'].text('D2: obie anody do BAT. Tab D2 = VS. Tab Q1 = VPROT. Osobne radiatory lub pelna izolacja.',8,48)
S['P01'].text('Sterowanie domyslnie OFF: Q2 podciaga GATE do SOURCE bez AUX5. Q4 blokuje Q2 przy ENABLE.',8,53,1.25)
S['P01'].text('R23: 2 W, odsunac od wzorca. R27: 2 W, krotki tor bramki. C5/C6/D4 blisko Q1.',8,108)
S['P01'].text('Budzet C na VPROT <=220uF przy otwartym KPWR. Pojemnosc silnika znajduje sie za KPWR.',8,110)
S['AUX'].text('P01 / 02   AUX5, WZORZEC, OVP / UVLO',8,6,2)
S['AUX'].text('U1: OUT=1, GND=2, IN=3. R2=1R pozostaje w szeregu z C9 (wymaganie ESR LM2936).',8,10)
S['AUX'].text('U3 TI LP: K=1, A=2, REF=3. Piny 1+3 zwarte. Bez kondensatora na REF.',8,52,1.15)
S['AUX'].text('OVP ok.18V / powrot ok.16.7V; UVLO ok.9.85 / 9.37V. Kalibracja RV1 na stole.',56,90,1.15)
S['AUX'].text('U2A/U2B i U4 maja wyjscia otwarte. R13 jest jedynym pull-up sieci OK.',107,48,1.05)
S['SAFE'].text('P01 / 03   ENABLE, SAFE_N, WIAZKA PG',8,6,2)
S['SAFE'].text('D7+D8 odcinaja niski poziom OK od bazy Q6. ENABLE jest lokalnym sygnalem analogowym.',8,11)
S['SAFE'].text('Q7: otwarty kolektor. Polaryzacja R30 z 3V3_IO odbiornika, niezaleznie od AUX5.',8,51,1.15)
S['SAFE'].text('J5 = dawne J_PGB. H_PG: 200mm, AWG22,\n6 zyl, wtyk Mini-Fit Jr 6p na P04;\nP01: lut do PTH + opaska 12.5mm od lutu.\n1=3V3_IO  2=SAFE_N  3=GND\n4=PG_SEND  5=PG_LINK  6=GND',125,55,1.05)
S['SAFE'].text('J3: tylko suchy styk / zworka serwisowa.\nZwarcie wylacza; normalnie ROZWARTE.',8,108)
S['SAFE'].text('R34 = dawne W_PRES. Mostek obecnosci modulu.\nJ1/J2/J4/J8 i TP: same pola PCB, bez zakupu gniazd.\nSAFE_N ma pull-up na P04, nie na P01.',98,95,1.05)

# Root links for the other two sheets; all cross-sheet connections use named global nets.
for i,n in enumerate(['AUX','SAFE']):
 x=mm(9+i*40);y=mm(115) # moved to a reserved root corner by final visual QA
 x=mm(85+i*37);y=mm(8)
 shid=uid('sheet/'+n)
 S['P01'].items.append(f'(sheet (at {x} {y}) (size 76.2 12.7) (fields_autoplaced yes) (stroke (width 0.15) (type default)) (fill (color 0 0 0 0)) (uuid {shid}) (property "Sheetname" {q(n)} (at {x} {y-1.27} 0) (effects (font (size 1 1)) (justify left bottom))) (property "Sheetfile" {q(n+".kicad_sch")} (at {x} {y+13.97} 0) (effects (font (size 1 1)) (justify left top))) (instances (project "P01" (path {q("/"+uid("P01"))} (page {q(i+2)})))))')
 # Child instance path uses the hierarchical sheet UUID, not its document UUID.
 old=S[n].path;new='/'+uid('P01')+'/'+shid
 S[n].items=[t.replace(q(old),q(new)) for t in S[n].items];S[n].path=new
# Explicit power source flags: source is the input harness return and upstream AUX filter.
flag=symbol('power','PWR_FLAG')
for idx,(sheet,net,x,y) in enumerate([('P01','GND',36,44),('AUX','P01_AUX_IN',32,21)],1):
 p={'ref':'#FLG'+str(idx),'display':'PWR_FLAG','source_ref':'ERC_SOURCE','mpn':'','footprint':'','symbol':flag,'pins':{'1':net},'qty':0,'url':''}
 S[sheet].place(p,x,y)
for s in S.values():s.finish();s.save()
write_tables()
(P/'eda/P01.kicad_pro').write_text('{}',encoding='utf-8')
(P/'verification/sheet-parts.json').write_text(json.dumps({n:[k for k in s.parts] for n,s in S.items()},indent=2),encoding='utf-8')
print('Placed',len(PARTS),'components,',sum(len(s.parts) for s in S.values()),'symbol units; 3 A3 sheets')
