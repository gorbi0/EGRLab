from parts import *
import cadlib,collections,copy
names=[('P11','Moc i adapter TEST / pigtails do gniazd panelowych'),('TAPS','TAPS / adapter L2 / granice zakresu P11'),('CONTROL','Wiazki SAFE CORE i kontaktow panelu'),('CONTACTS','Kontakty zewnetrzne / funkcje i stany spoczynkowe')]
S={n:Sheet(n,t,i,None if i==1 else uid('P11')) for i,(n,t) in enumerate(names,1)}
def put(sh,r,x,y):
 pp=copy.copy(PARTS[r]);pp['text_at']=(2,-max(4,len(pp['pins'])//2+2));S[sh].place(pp,x,y)
for r,x,y in [('J2',28,35),('X2',72,35),('J1',119,29),('J8',28,74),('X8',72,74),('J9',119,69),('J10',119,91)]:put('P11',r,x,y)
S['P11'].text('L1: ECU_P1 -> P06 bocznik/bypass -> EGR_P1. Powrot silnika P3 jest w adapterze AL1, poza P11.',8,12,1.2)
S['P11'].text('J9 / P07 HOLD. Tylko dwa przewody silnika; brak polaczenia z torem mocy LOGGER.',8,102,1.2)
for r,x,y in [('J3',30,38),('X3',76,38),('J7',126,38)]:put('TAPS',r,x,y)
S['TAPS'].text('J7: kabel P05 50 mm maks. GOLD. Masa sensora AGND_SENSOR NIE jest masa GND na P11.',8,12,1.2)
S['TAPS'].text('TAP_P1/P3/P4/P5/P6 sa wspolne dla TEST, L1 i L2. P11 NIE wybiera adaptera.',8,64,1.4)
S['TAPS'].text('Dopuszczony jeden adapter naraz. Wymagana przeslona mechaniczna portow lub odbior procedury operatora.',8,72,1.2)
S['TAPS'].text('Rezystory zabezpieczajace odczepy pozostaja przy zaworze w adapterze AT/AL1/AL2, przed dlugim przewodem.',8,80,1.2)
S['TAPS'].text('Gniazda X2/X3/X8 i wszystkie X11...X17 sa poza PCB. Numery DT oznaczaja komory obudowy.',8,88,1.2)
S['TAPS'].text('Nie zakladac kolejnosci przestrzennej pinow DT ani Mini-Fit z widoku od lutowania; sprawdzic kazda zyle.',8,96,1.2)
for r,x,y in [('J4',33,35),('J5',85,35),('J11',134,48),('J6',33,74),('X6',76,74)]:put('CONTROL',r,x,y)
S['CONTROL'].text('PANEL_3V3 tylko z P04-R2.1/J8.1 przez R40=100R. Nie zasilac LED ani podciagac z 3V3_CORE.',8,12,1.2)
S['CONTROL'].text('J4 -> P03-R2/J9, J5 -> P04-R2.1/J8. Pull-up/pull-down oraz filtry znajduja sie na tych plytkach.',8,91,1.2)
S['CONTROL'].text('SCOPE: wyjscie GPIO przez 330R w CORE. Odbiornik >=1Mohm; bez terminacji 50R. Ekran BNC=GND.',8,99,1.2)
for r,x,y in [('X15',34,30),('X12',86,30),('X13',136,30),('X16',34,65),('X11',82,61),('X14',131,61),('X17',82,86)]:put('CONTACTS',r,x,y)
S['CONTACTS'].text('Numery pinow blokow X11...X17 sa FUNKCYJNE, nie katalogowe. Styki Au low-level, bez podswietlenia.',8,12,1.2)
S['CONTACTS'].text('L1/L2: obie pary NC zamkniete przy pustym porcie; rozwarcie przed pierwszym stykiem elektrycznym wtyku.',8,47,1.2)
S['CONTACTS'].text('TEST NO zamyka dopiero po pelnym osadzeniu. STOP: NC rozwarty w stanie STOP; NO oba konce NC.',8,98,1.2)
S['CONTACTS'].text('MECH_OK wraca przez mostek 10-11 dopiero na odleglym koncu adaptera AT. Brak tego mostka na P11.',8,106,1.2)
ns=collections.defaultdict(set)
for sh in S.values():
 for pp,coords in sh.parts.values():
  for n in coords:ns[pp['pins'][n]].add(sh.name)
cadlib.CROSS={n for n,v in ns.items() if len(v)>1 and n!='NC'}
for i,(n,t) in enumerate(names[1:],2):
 sid=uid('sheet/'+n);sh=S[n];x,y=mm(10+(i-2)*35),mm(110)
 S['P11'].items.append(f'(sheet (at {x} {y}) (size 75 5.08) (stroke (width .15) (type default)) (fill (color 0 0 0 0)) (uuid {sid}) (property "Sheetname" "{n}" (at {x} {y-1.27} 0) (effects (font (size 1 1)) (justify left bottom))) (property "Sheetfile" "{n}.kicad_sch" (at {x} {y+5.08} 0) (effects (font (size 1 1)) hide)) (instances (project "P11" (path {q("/"+uid("P11"))} (page "{i}")))))')
 old=sh.path;sh.path='/'+uid('P11')+'/'+sid;sh.items=[t.replace(q(old),q(sh.path)) for t in sh.items]
for sh in S.values():sh.text(f'P11-R1 / {sh.num:02d}   {sh.title.upper()}',8,7,1.8);sh.finish();sh.save()
write_tables();(P/'verification/sheet-parts.json').write_text(json.dumps({n:list(s.parts) for n,s in S.items()},indent=2));print(len(PARTS),'parts; four sheets')
