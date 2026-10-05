"""P07-S1 schematic generator: eight A3 sheets. Parts come from parts.py (single source); every pin gets a short wire stub with a net
label (cadlib.Sheet.finish), names shared by sheets become global labels. Placement is a deterministic row packing with the label text
widths included, so no stub can end on another pin (verify_schematic.py checks the exported netlist pin by pin anyway)."""
from parts import *
import cadlib,collections,copy,math
names=[('P07','Zasilanie lokalne i arkusze'),('MOC','VMOTOR, KPWR, modul B+/B-, bocznik, port TEST'),('ANA','INA240, odniesienie, ITEST, okno OC'),('DIG','MCP3201 ITEST i bufor SPI'),
       ('LOGIKA','Nadzorcy, odbiorniki, bramki, zatrzask OC, SAFE_N'),('MODUL','Bufor 3,3 -> 5 V, wiazka modulu, diagnostyka IS'),('ZLACZA','J_BP1 / J_BP2 do P12 (krawedz A)'),('SERWIS','Listwy serwisowe J_SV1 / J_SV2 (krawedz B)')]
S={n:Sheet(n,t,i,None if i==1 else uid('P07')) for i,(n,t) in enumerate(names,1)}
CH=1.0;STUB=5.08;W=405.0;Y0=40.0;YMAX=268.0
def geometry(part,unit,a):
 sym=part['symbol'];pins=pin_defs(sym,unit);pts=[]
 for n,p in pins.items():
  px,py,pa=map(float,one(p,'at')[1:]);t=math.radians(a)
  dx=px*math.cos(t)-py*math.sin(t);dy=px*math.sin(t)+py*math.cos(t);ang=(pa+a)%360;rad=math.radians(ang)
  x,y=dx,-dy;ex,ey=x-STUB*math.cos(rad),y+STUB*math.sin(rad);net=part['pins'][n]
  L=0 if net=='NC' else len(net)*CH+4
  pts+=[(x,y),(ex,ey-1.5),(ex,ey+1.5),((ex-L) if ang==0 else (ex+L),ey)]
 pts+=[(-6,-6),(6,6)]                                        # symbol body (connectors, transistors, diodes)
 xs=[p[0] for p in pts];ys=[p[1] for p in pts]
 return min(xs)-2,max(xs)+2,min(ys)-4,max(ys)+3
def text_at(part,unit):
 if part['ref'].startswith('U') or part['ref']=='K1':
  ys=[float(one(p,'at')[2]) for p in pin_defs(part['symbol'],unit).values()];return (-5,-(max(ys)/2.54+3))
 if part['ref'].startswith('J'):return (2,-(len(part['pins'])//2)-3)
 return None
def layout(sh,items,width=W,y0=Y0):
 x=8.0;y=y0;rowh=0
 for it in items:
  ref=it[0];unit=it[1] if len(it)>1 else 1;a=it[2] if len(it)>2 else 0
  if ref not in PARTS:raise KeyError(ref)
  p=copy.copy(PARTS[ref]);p['display']=p['display'].split(' / ')[0]
  if ref.startswith(('R','C','F')) and len(p['pins'])==2 and a==0:a=90      # Device R/C/Polyfuse are vertical at 0 deg; D is horizontal
  ta=text_at(p,unit)
  if ta:p['text_at']=ta
  x0,x1,y0_,y1=geometry(p,unit,a)
  if x+(x1-x0)>width:x=8.0;y+=rowh+3;rowh=0
  cx=x-x0;cy=y-y0_
  if y+(y1-y0_)>YMAX:raise SystemExit(f'sheet {sh} overflows at {ref}')
  # snap the symbol origin to the 1.27 mm grid (pins stay on grid)
  gx=round(cx/1.27)*1.27;gy=round(cy/1.27)*1.27
  S[sh].place(p,gx/2.54,gy/2.54,a,unit)
  x+=x1-x0+4;rowh=max(rowh,y1-y0_)
 return y+rowh
SHEETS={
 'P07':[('R50',),('C16',),('C17',),('C18',),('U18',),('C19',),('D7',),('C21',),('C20',),('C12',),('C13',)]+[(f'C{i}',) for i in range(22,39)],
 'MOC':[('J1',),('D1',),('C1',),('C2',),('C3',),('R1',),('K1',),('Q1',),('R2',),('R3',),('C9',),('D2',),('D3',),('R4',),('R5',),('C4',),('J2',),('J3',),('RSH1',),('J4',)],
 'ANA':[('R6',),('R7',),('U1',),('U2',),('C5',),('C6',),('D4',),('U3',),('R8',),('R9',),('C7',),('R10',),('C8',),('U4',),('R11',),('R12',),('R13',),('R14',),('C10',),('U5',),('R15',)],
 'DIG':[('U6',),('R16',),('C11',),('U7',),('R17',),('R18',),('R19',),('R20',),('R21',),('R22',),('R23',)],
 'LOGIKA':[('U8',),('R24',),('U9',),('R25',),('U10',)]+[(f'R{i}',) for i in range(26,31)]+[('U11',),('R31',),('R51',),('U12',),('U13',),('U14',),('U15',),('Q2',),('R33',),('R34',),('R32',)],
 'MODUL':[('F1',),('U16',),('R35',),('R36',),('R37',),('R38',),('R39',),('R40',),('R41',),('R42',),('J5',),('R43',),('R44',),('R45',),('C14',),('D5',),('R46',),('R47',),('C15',),('D6',),('U17',),('R48',),('R49',)],
 'ZLACZA':[('J_BP1',),('J_BP2',)],
 'SERWIS':[('J_SV1',)]+[(SERVICE[n][2],) for n in SERVICE if SERVICE[n][0]=='J_SV1']+[('J_SV2',)]+[(SERVICE[n][2],) for n in SERVICE if SERVICE[n][0]=='J_SV2']}
NOTES={
 'P07':['J_BP2: 5V_SYS (piny 10/12) i 3V3_IO (pin 14) z P02 R4 przez P12. Logika (U10-U15, U17) na 3V3_IO - ta sama szyna co P04 R3. Analog na lokalnych 5VA_P07 (R50 10R) i 3V3A_P07 (U18).',
        '5V_MOD = 5V_SYS za PTC F1: VCC modulu IBT-2 (74HC244) i bufora U16. GND (logika, analog) i PGND (prad silnika) NIE sa polaczone na P07: wspolny punkt mas = P02 R4 J2 (VMOTOR).'],
 'MOC':['VMOTOR (P02 R4 J2, za F1 MINI 7,5 A) -> J1 -> KPWR K1 (NO) -> MOD_BP -> J2 -> modul B+. R4 1k laduje 330 uF modulu przy otwartym KPWR; KPWR: cewka 5 V z 5V_SYS (decyzja 5.10), Q1 AO3400A (zrodlo na GND) z LOCAL_PERMIT; clamp D2 + D3 15 V do 5V_SYS.',
        'Modul M+ -> J3.1 -> RSH1 5 mOhm (Kelvin K_PLUS/K_MINUS) -> T_EGR_P1 -> J4.1 -> port TEST (P11). M- -> J3.2 = T_EGR_P3 -> J4.2. Prad dodatni: kierunek A (RPWM, M+ wyzej).',
        'PGND: powrot przez J1.2 do P02, B- modulu przez J2.2, TVS D1, C1-C4, R1/R5 (obwod cewki KPWR w domenie GND). Tor 10 A: pola >= 4 mm na obu warstwach (S1 3, jak P06 R2).'],
 'ANA':['I_T_OUT = REF_BUF + 50 x 5 mOhm x I = 2,5 V + 0,25 V/A. ITEST: R8/R9 1:2 + C7 100n (tau 0,26 ms) -> U3A -> MCP3201: 1,25 V + 0,125 V/A, +-10 A w 0..2,5 V.',
        'Okno OC: I_FILT (R10 1k / C8 1n) vs OC_HIGH = REF_BUF x 1,806 (4,515 V, +8,06 A) i OC_LOW = REF_BUF x 0,1992 (0,498 V, -8,01 A). U5 open collector -> OC_LOCAL_N (R15 10k do 3V3_IO).'],
 'DIG':['SPI mode 0, 16 zegarow, raw = (word >> 1) & 0x0FFF (jak P06 R2). DOUT_TX trojstanowy (OE = CS_LOCAL_N) + R22 47R na wspolnej ADC_DOUTA. U7 gate 4: SUP5_RAW (5 V) -> SUP5_N (3,3 V).'],
 'LOGIKA':['RAILS_OK = SUP3_N & SUP5_N. LOCAL_CLEAR_N = RAILS_OK & OC_LOCAL_N. OC_GOOD: kasowany przez OC/zasilanie, ustawiany TYLKO zboczem ARM_CLK przy MOTOR_PERMIT = L (D = PERMIT_N).',
           'LOCAL_PERMIT = MOTOR_PERMIT & OC_GOOD & RAILS_OK (-> KPWR). DRIVE_EN = LOCAL_PERMIT & SAFE_OK. RPWM = PWM_OUT & DRIVE_EN & MOTOR_INA; LPWM = PWM_OUT & DRIVE_EN & MOTOR_INB.',
           'NO_TRIP (FF2): PRE = RAILS_OK (start = brak zadzialania), CLR = OC_LOCAL_N, D = 1 przy ARM_CLK. DRIVE_OK = RAILS_OK & NO_TRIP. Q2 sciaga SAFE_N podczas OC.'],
 'MODUL':['U16 74AHCT125 (5V_MOD): 3,3 -> 5 V dla 74HC244 modulu (VIH 3,5 V przy 5 V). OE_N = DRV_OFF: wyjscia Z bez DRIVE_EN; modul ma 30k do GND na wejsciach -> L. R_EN = L_EN = DRIVE_EN.',
          'IS: modul 10k do GND (ok. 1,2 V/A). R44/R45 1:2 + C 10n, clamp BAT54S do 3V3_IO, U17 Schmitt -> ENA_DIAG / ENB_DIAG (H = prad galezi powyzej progu albo blad IS; decyzja 5.10). Tylko diagnostyka.',
          'MOD_GND przez R43 10R: dziala przy GND modulu polaczonym z B- i przy rozdzielonym (pomiar 5.10: 508 mV w trybie diody).'],
 'ZLACZA':['J_BP1 (S2, x plytki 26,5 / stosu 80,0): ADC_SCLK 2 / ADC_DOUTA 4 jak J_BP2 P03 R6, P05 R3 i J_BP P06 R2; CS_ITEST_N, MOTOR_INA/INB, ENA/ENB_DIAG do P03 R6.',
           'J_BP2 (S3, x plytki 80,0 / stosu 133,5): MOTOR_PERMIT 2, PWM_OUT 4, ARM_CLK 6, DRIVE_OK 8, SAFE_N 16 na tych samych pinach co J_BP2 P04 R3; 5V_SYS 10/12, 3V3_IO 14. Nieparzyste GND.'],
 'SERWIS':['J_SV1 (S2, x 10..43): wezly analogowe 10k (piny 2-7), szyny pakietu 4,7k (9-12), GND 1/8/13. J_SV2 (S3, x 63,5..96,5): szyny 1k (2-6), logika 1k (8-12), GND 1/7/13.',
           'Rezystor przy wezle (S1 6). Szyna tylko obok GND, innej szyny albo linii logicznej; wezly analogowe tylko obok siebie i GND.']}
for sh,items in SHEETS.items():
 for k,t in enumerate(NOTES[sh]):S[sh].text(t,8,7.6+k*2.2,1.25)
 layout(sh,items,W if sh!='P07' else 300.0,Y0+(5.6 if len(NOTES[sh])>2 else 0))
for i,n in enumerate(['5V_SYS',G,PG,IO,A5,M5,VM],1):
 S['P07'].place({'ref':f'#FLG{i}','display':'PWR_FLAG','symbol':symbol('power','PWR_FLAG'),'source_ref':'ERC_SOURCE','mpn':'','footprint':'','pins':{'1':n}},4+i*7,92)
ns=collections.defaultdict(set)
for name,sh in S.items():
 for part,pins in sh.parts.values():
  for n in pins:ns[part['pins'][n]].add(name)
cadlib.CROSS={n for n,v in ns.items() if len(v)>1 and n!='NC'}
for sh in S.values():sh.text(f'{cadlib.REV} / {sh.num:02d}   {sh.title.upper()}',8,5,2)
for i,(name,title) in enumerate(names[1:],2):
 sh=S[name];x,y=mm(124),mm(20+(i-2)*9);sid=uid('sheet/'+name)
 S['P07'].items.append(f'(sheet (at {x} {y}) (size 55.88 10.16) (stroke (width .15) (type default)) (fill (color 0 0 0 0)) (uuid {sid}) (property "Sheetname" {q(name)} (at {x} {y-1.27} 0) (effects (font (size 1 1)) (justify left bottom))) (property "Sheetfile" {q(name+".kicad_sch")} (at {x} {y+10.16} 0) (effects (font (size 1 1)) (justify left top))) (instances (project "P07" (path {q("/"+uid("P07"))} (page "{i}")))))')
 old=sh.path;sh.path='/'+uid('P07')+'/'+sid;sh.items=[t.replace(q(old),q(sh.path)) for t in sh.items]
for sh in S.values():sh.finish();sh.save()
write_tables()
pro={'meta':{'filename':'P07.kicad_pro','version':3},'sheets':[[uid(n) if n=='P07' else uid('sheet/'+n),n] for n,_ in names],'boards':[],'libraries':{'pinned_footprint_libs':[],'pinned_symbol_libs':[]},
     'schematic':{'legacy_lib_dir':'','legacy_lib_list':[]},'text_variables':{}}
(P/'eda/P07.kicad_pro').write_text(json.dumps(pro,indent=2)+'\n')
(P/'verification/sheet-parts.json').write_text(json.dumps({n:list(s.parts) for n,s in S.items()},indent=2))
print(len(PARTS),'parts;',len(S),'sheets')
