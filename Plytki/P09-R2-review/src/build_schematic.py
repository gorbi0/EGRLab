from parts import *
import cadlib,collections,copy
names=[('P09','Moduly termopar i zasilanie'),('SPI','Buforowanie sygnalow do modulow'),('SELECT','Wybor MISO i ochrona wspolnej magistrali'),('CONNECT','Wiazki i punkty pomiarowe')]
S={n:Sheet(n,t,i,None if i==1 else uid('P09')) for i,(n,t) in enumerate(names,1)}
def put(sh,r,x,y,a=0,u=1):
 pp=copy.copy(PARTS[r]);pp['display']=pp['display'].split(' / ')[0]
 if r.startswith(('U','J')):pp['text_at']=(-4,-8)
 if r.startswith('TP'):pp['text_at']=(2,-1)
 S[sh].place(pp,x,y,a,u)
def node(sh,n,refs,bus=None,axis='y'):S[sh].node(n,refs,bus,axis)
srvnet=[n for n,_ in SRV]
for r,x,y in [('JP1',25,29),('J3',63,33),('C6',98,36),('JP2',25,72),('J4',63,76),('C7',98,79)]:put('P09',r,x,y)
S['P09'].text('Zakupione MAX31856 XU z oferty 18805671895. Pinout ze zdjecia; regulator i rozstaw wymagaja pomiaru.',8,12,1.2)
S['P09'].text('JP1/JP2 poczatkowo BEZ ZWOREK. 1-2: VIN=3V3 do kwalifikacji; 2-3: 5V tylko po sprawdzeniu modulu.',8,17,1.2)
S['P09'].text('3Vo obu modulow: osobne punkty pomiarowe, NIE laczyc ze soba ani z 3V3_IO.',8,93,1.2)
S['P09'].text('Termopary K izolowane do zaciskow na modulach. Nie prowadzic sygnalu termopary przez nosnik P09.',8,98,1.2)
for r,x in [('C1',16),('C2',30),('C3',44),('C4',58),('C5',72)]:put('P09',r,x,107)
for i,(n,x) in enumerate([(V,85),(A5,98),(G,111),('TC1_VIN',124),('TC2_VIN',140)],1):S['P09'].place({'ref':f'#FLG{i}','display':'PWR_FLAG','symbol':symbol('power','PWR_FLAG'),'source_ref':'ERC_SOURCE','mpn':'','footprint':'','pins':{'1':n}},x,52)
# Four input buffers and each local resistor network.
for row,(u,ra,rb,rs,net,signal,ip,op) in enumerate([(1,'R3','R7','R14','CLK_BUF','SPI3_SCLK',2,3),(2,'R4','R8','R15','MOSI_BUF','SPI3_MOSI',5,6),(3,'R1','R5','R16','CS1_BUF','TC1_CS',9,8),(4,'R2','R6','R17','CS2_BUF','TC2_CS',12,11)]):
 y=26+row*22
 put('SPI',ra,20,y);put('SPI','U1',53,y,0,u);put('SPI',rb,76,y-5 if row>=2 else y+5);put('SPI',rs,108,y,90)
 node('SPI',net,[('U1',op),(rs,1),(rb,2 if row>=2 else 1)],y)
S['SPI'].text('U1: Nexperia 74LVC125AD z Ioff, zasilanie 3V3_IO. Nie zamieniac na HC125.',8,12,1.2)
S['SPI'].text('Zewnetrzne CS maja pull-up 10k; SCLK/SDI pull-down 100k. P03 U23 ma Ioff przy wylaczonej P03.',8,106,1.2)
S['SPI'].text('SPI TEMP poczatkowo 1 MHz, mode 1; CS setup/hold po 2 takty i przerwa obu CS HIGH przed zmiana kanalu.',8,111,1.2)
put('SPI','U1',138,85,0,5)
# Decoder and MISO drivers.
put('SELECT','U3',37,27,0,1)
for r,x,y in [('R18',72,23),('R19',90,23)]:put('SELECT',r,x,y)
for ch,y in [(1,56),(2,80)]:
 put('SELECT','U2',55,y,0,ch);put('SELECT','R'+str(8+ch),26,y+5);put('SELECT','R'+str(10+ch),88,y,90)
 node('SELECT','TX'+str(ch),[('U2',3 if ch==1 else 6),('R'+str(10+ch),1)],y)
put('SELECT','R13',114,68)
put('SELECT','U3',136,28,0,2);put('SELECT','U3',134,54,0,3)
put('SELECT','U2',135,72,0,3);put('SELECT','U2',135,90,0,4);put('SELECT','U2',106,94,0,5)
S['SELECT'].text('CS1 CS2: 0 1 -> TC1; 1 0 -> TC2; 0 0 oraz 1 1 -> oba wyjscia Hi-Z.',8,12,1.2)
S['SELECT'].text('U3: A=CS1, B=CS2; Y2 steruje OE1, Y1 steruje OE2. Oba CS=LOW nie zwieraja wyjsc SDO.',8,40,1.2)
S['SELECT'].text('Tablica dotyczy stanow ustalonych. Przed drugim CS zapewnic oba HIGH >=1 us; 100R ograniczaja prad przejsciowy.',8,110,1.15)
# Connections (J_BP, edge A) and service strip (edge B); the series resistors sit in a grid and connect by labels.
put('CONNECT','J1',30,32)
S['CONNECT'].text('J_BP -> plytka polaczen P12 (tasma IDC), krawedz A, srodek slotu S3. Piny nieparzyste GND; parzyste: 5V_SYS x2, 3V3_IO, SPI3 SCLK/MOSI/MISO, TC1_CS, TC2_CS.',8,12,1.2)
S['CONNECT'].text('Zastepuje wiazki LV09 (P02-R3/J9) i TEMP (P03-R2/J7) z R1. Zasilanie tylko takie, jakiego P09 uzywa.',8,17,1.2)
S['CONNECT'].text('SERWIS (krawedz B): GND na obu koncach, kazdy kolek przez 1k (R20..R30) postawione przy wezle; katowy goldpin, kolki ok. 6 mm za krawedz plytki.',8,52,1.2)
S['CONNECT'].text('Rezystor: pin 1 = siec macierzysta (wezel), pin 2 = SRV_<siec> -> kolek. 3Vo modulow: tylko przez swoj rezystor do kolka.',8,57,1.2)
put('CONNECT','J2',138,72)
for i,k in enumerate(range(2,13)):
 put('CONNECT','R'+str(19+k-1),30+(i%6)*18,72+(i//6)*22)
S['CONNECT'].text('FLT i DRDY modulow sa nieprzylaczone (NC). Punkty spoza listwy (SCLK/MOSI/CS wejsciowe, FLT, DRDY) wymagaja rozebrania stosu albo pomiaru na P03.',8,108,1.2)
ns=collections.defaultdict(set)
for sh in S.values():
 for pp,coords in sh.parts.values():
  for n in coords:ns[pp['pins'][n]].add(sh.name)
cadlib.CROSS={n for n,v in ns.items() if len(v)>1 and n!='NC'}
for sh in S.values():
 for net in cadlib.CROSS:sh.items=[t.replace('(label '+q(net)+' ','(global_label '+q(net)+' (shape passive) ') for t in sh.items]
 sh.text(f'P09-R2 / {sh.num:02d}   {sh.title.upper()}',8,7,2)
for i,(name,title) in enumerate(names[1:],2):
 sh=S[name];x,y=mm(130),mm(65+(i-2)*8);sid=uid('sheet/'+name)
 S['P09'].items.append(f'(sheet (at {x} {y}) (size 55.88 10.16) (stroke (width .15) (type default)) (fill (color 0 0 0 0)) (uuid {sid}) (property "Sheetname" {q(name)} (at {x} {y-1.27} 0) (effects (font (size 1 1)) (justify left bottom))) (property "Sheetfile" {q(name+".kicad_sch")} (at {x} {y+10.16} 0) (effects (font (size 1 1)) hide)) (instances (project "P09" (path {q("/"+uid("P09"))} (page "{i}")))))')
 old=sh.path;sh.path='/'+uid('P09')+'/'+sid;sh.items=[t.replace(q(old),q(sh.path)) for t in sh.items]
for sh in S.values():sh.finish();sh.save()
write_tables();(P/'verification/sheet-parts.json').write_text(json.dumps({n:list(s.parts) for n,s in S.items()},indent=2));print(len(PARTS),'parts; four sheets')
