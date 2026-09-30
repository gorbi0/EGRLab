from parts import *
import cadlib,collections,copy
names=[('P10','CAN pasywny / zasilanie / OBD'),('CORE','Bufor RX / wiazka CORE / punkty pomiarowe')]
S={n:Sheet(n,t,i,None if i==1 else uid('P10')) for i,(n,t) in enumerate(names,1)}
def put(sh,r,x,y,a=0,u=1):
 pp=copy.copy(PARTS[r]);pp['display']=pp['display'].split(' / ')[0]
 if r.startswith(('U','J','D')):pp['text_at']=(-4,-8)
 if r=='U2' and u==5:pp['text_at']=(-12,-8)
 if r.startswith('TP'):pp['text_at']=(2,-1)
 S[sh].place(pp,x,y,a,u)
put('P10','U1',75,33);put('P10','D1',108,58);put('P10','J3',139,36)
for r,x in [('C1',25),('C2',43),('C4',61),('C5',79)]:put('P10',r,x,76)
for i,(n,x) in enumerate([(V5,30),(V,58),(G,86)],1):S['P10'].place({'ref':f'#FLG{i}','display':'PWR_FLAG','symbol':symbol('power','PWR_FLAG'),'source_ref':'ERC_SOURCE','mpn':'','footprint':'','pins':{'1':n}},x,94)
S['P10'].text('S oraz TXD sa na stale polaczone z VIO=3V3_IO. Brak zwory TX / brak terminacji CAN na P10. Zasilanie i CAN_RX/CAN_TX: J_BP na arkuszu CORE.',8,12,1.3)
S['P10'].text('J3.1 -> OBD 6 CANH; J3.2 -> OBD 14 CANL. Skrecona para 120 ohm, 300 mm. Pozostale styki OBD: NC.',8,53,1.3)
S['P10'].text('Masa P10 przez P02 i glowne zasilanie urzadzenia. Nie dodawac polaczen OBD 4/5/16. Brak izolacji galwanicznej.',8,60,1.3)
S['P10'].text('D1 piny 1/2 rownowazne: w tej PCB 1=CANL, 2=CANH, 3=GND. Obudowa SOT23, nie SOT323.',8,106,1.2)
put('CORE','U2',43,31,0,1);put('CORE','R2',20,30);put('CORE','R1',67,31,90);put('CORE','J1',96,32)
S['CORE'].node('RX_BUF',[('U2',3),('R1',1)],31)
put('CORE','U2',133,30,0,2);put('CORE','U2',133,49,0,3);put('CORE','U2',133,68,0,4);put('CORE','U2',103,88,0,5);put('CORE','C3',80,88)
put('CORE','J2',100,66)
for i,k in enumerate(range(2,9)):put('CORE','R'+str(k+1),20+(i%4)*20,64+(i//4)*16)
S['CORE'].text('CAN_TX z CORE (J_BP pin 6) prowadzi tylko do kolka serwisowego. Nawet bledny program nie steruje TXD ani S transceivera.',8,12,1.3)
S['CORE'].text('U2 Nexperia 74LVC125AD z Ioff; wyjscie oddziela RXD od pull-up R30 w P03 przy wylaczonej P10.',8,48,1.2)
S['CORE'].text('J_BP -> plytka polaczen P12 (krawedz A, slot S3 poziomu 4): piny nieparzyste GND; 2 i 10 5V_SYS, 4 3V3_IO, 6 CAN_TX, 8 CAN_RX. Zastepuje LV10 i CORE CAN z R1.',8,101,1.2)
S['CORE'].text('SERWIS (krawedz B): GND na obu koncach; kolki przez R3..R9 (1k, a CAN_H/CAN_L 10k) przy wezlach: pin 1 rezystora = siec macierzysta, pin 2 = SRV_<siec>.',8,107,1.2)
S['CORE'].text('Firmware nadal LISTEN_ONLY, 500 kbit/s do kwalifikacji. RPM wymaga potwierdzonego zrodla ramek; P10 nie pyta o PID.',8,95,1.2)
ns=collections.defaultdict(set)
for sh in S.values():
 for pp,coords in sh.parts.values():
  for n in coords:ns[pp['pins'][n]].add(sh.name)
cadlib.CROSS={n for n,v in ns.items() if len(v)>1 and n!='NC'}
for sh in S.values():
 for net in cadlib.CROSS:sh.items=[t.replace('(label '+q(net)+' ','(global_label '+q(net)+' (shape passive) ') for t in sh.items]
 sh.text(f'P10-R2 / {sh.num:02d}   {sh.title.upper()}',8,7,2)
sid=uid('sheet/CORE');sh=S['CORE'];x,y=mm(126),mm(88)
S['P10'].items.append(f'(sheet (at {x} {y}) (size 55.88 10.16) (stroke (width .15) (type default)) (fill (color 0 0 0 0)) (uuid {sid}) (property "Sheetname" "CORE" (at {x} {y-1.27} 0) (effects (font (size 1 1)) (justify left bottom))) (property "Sheetfile" "CORE.kicad_sch" (at {x} {y+10.16} 0) (effects (font (size 1 1)) hide)) (instances (project "P10" (path {q("/"+uid("P10"))} (page "2")))))')
old=sh.path;sh.path='/'+uid('P10')+'/'+sid;sh.items=[t.replace(q(old),q(sh.path)) for t in sh.items]
for sh in S.values():sh.finish();sh.save()
write_tables();(P/'verification/sheet-parts.json').write_text(json.dumps({n:list(s.parts) for n,s in S.items()},indent=2));print(len(PARTS),'parts; two sheets')
