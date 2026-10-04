"""P11-R2 schematic: three A3 sheets (root P12 interface + PANEL_3V3 source, CONTACTS, PORTY). Connectivity only through
pin stubs and labels written by cadlib.Sheet.finish(); names used on two sheets become global labels."""
from parts import *
import cadlib,collections,copy
names=[('P11','Zlacze J_P12 do P12, zrodlo PANEL_3V3, SCOPE'),('CONTACTS','Styki panelu - logika R1'),('PORTY','Porty L1 / L2 / TEST (poza P11)')]
S={n:Sheet(n,t,i,None if i==1 else uid('P11')) for i,(n,t) in enumerate(names,1)}
def put(sh,r,x,y,a=0,off=None):
 pp=copy.copy(PARTS[r]);pp['display']=pp['display'].split(' / ')[0]
 pp['text_at']=off or (2,-max(4,len(pp['pins'])//2+2))
 S[sh].place(pp,x,y,a)
# --- root: P12 ribbon, R1, SCOPE
put('P11','J_P12',40,52,off=(-4,-15));put('P11','R1',96,30,90,off=(-2,-3));put('P11','J6',96,62);put('P11','X6',126,62)
t=S['P11'].text
t('J_P12: IDC 2x10 do P12 (S1 8, PANELCORE + PANELSAFE). Piny 10/13/14/15/16 jak P03 R6 J_BP1 (N_J_SCOPE_HOT, MARK, TEST_KEY, LOGGER_CLEAR, TEST_PRESENT).',8,12,1.3)
t('Nieparzyste GND poza 13 MARK i 15 LOGGER_CLEAR (wyjatek jak w P03 R6). 12 i 18 GND (rezerwa). 3V3_IO na 20 - z dala od PANEL_3V3 (pin 2).',8,15.5,1.3)
t('PANELSAFE do P04 (wariant pelny): PANEL_3V3 2, MECH_OK 4, STOP_NC_OUT 6, ARM_CONTACT 8, TEST_KEY 14 (wspolny z P03). W LOGGER piny 4/6/8 bez odbiornika.',8,19,1.3)
t('R1 100R (decyzja P11-3): LOGGER bez P04 = OBSADZONY. Wariant z P04 = DNP (nie montowac): PANEL_3V3 zasila wtedy tylko P04 R40 100R z 3V3_IO.',70,40,1.3)
t('Obsadzony R1 przy P04 = dwa zrodla (2 x 100R rownolegle): znika ograniczenie pradu R40. Brak R1 bez P04 = TEST_KEY, LOGGER_CLEAR, TEST_PRESENT zawsze L.',70,43.5,1.3)
t('Zwarcie PANEL_3V3-GND przy R1: 33 mA, 0.11 W w 1206 (0.25 W). Odbiorniki 3 x 10k do GND na P03 R6 (R27, R6, R8); MARK: 10k do 3V3_CORE na P03 R6.',70,47,1.3)
t('SCOPE: N_J_SCOPE_HOT z P03 R6 przez R12 330R. BNC izolowany, odbiornik >= 1 Mohm, bez terminacji 50R. Ekran = GND.',70,75,1.3)
t('Na P11 nie ma: pradu silnika, TAPS, ISERIES, 5V_SENSOR, J1, J7, J9, J10 ani wiazek W3-W7 z R1 (P11-1, P11-4, P11-5).',8,100,1.3)
# --- CONTACTS: R1 logic, functional terminals
for r,x,y in [('X15',30,32),('X12',80,32),('X13',130,32),('X16',30,62),('X11',80,58),('X14',130,58),('X17',80,80)]:put('CONTACTS',r,x,y)
put('CONTACTS','X8',36,92,off=(-6,-9));put('CONTACTS','J8',80,96);put('CONTACTS','J11',150,84,off=(2,-13))
t=S['CONTACTS'].text
t('Numery pinow X11...X17 sa FUNKCYJNE, nie katalogowe. P11-7: zwykle przyciski i przelaczniki ze stykami ZLOCONYMI (ok. 0.3 mA / 3.3 V), bez podswietlenia.',8,12,1.3)
t('Lancuch MECH: PANEL_3V3 - kluczyk X15 - TEST_KEY - X12 NC_A - ILK_L1_L2 - X13 NC_A - LOOP_OUT - port TEST 10 - mostek w adapterze AT - port TEST 11 - MECH_OK.',8,15.5,1.3)
t('Lancuch DIAG: PANEL_3V3 - X12 NC_B - DIAG_L1_L2 - X13 NC_B - LOGGER_CLEAR. STOP: PANEL_3V3 - X16 NC - STOP_NC_OUT. TEST_PRESENT: PANEL_3V3 - X17 NO.',8,19,1.3)
t('L1/L2: obie pary NC zamkniete przy pustym porcie; rozwarcie przed pierwszym stykiem elektrycznym wtyku. TEST NO zamyka dopiero po pelnym osadzeniu.',8,44,1.3)
t('ARM i MARK zwieraja do GND; podciaganie na P04 (ARM) i P03 R6 (MARK). W LOGGER ARM_CONTACT bez odbiornika.',8,47.5,1.3)
t('J8: tylko komory 10/11 portu TEST. Pozostale komory portow ida przewodami wprost do P05 / P06 / P07 / P08 (arkusz PORTY, docs/PORTY.csv).',8,108,1.3)
# --- PORTY: off-board, documentation only (all cavities NC on P11 except TEST 10/11 on sheet CONTACTS)
put('PORTY','X2',36,40,off=(-6,-10));put('PORTY','X3',120,40,off=(-6,-10))
t=S['PORTY'].text
t('Porty na panelu: Amphenol AT04-12, klucz A = L1, B = L2, C = TEST (decyzja P11-2). Komory jak w R1 (adaptery AL1 / AL2 / AT bez zmian).',8,12,1.3)
t('Zadna komora L1 / L2 nie laczy sie z P11: przewody z portu wprost do P05 J4 (TAPS, GND) i P06 J3 (ECU_P1, EGR_P1) - P11-4, P11-5.',8,15.5,1.3)
t('TEST: komory 1/2 -> P07 (T_EGR), 3/4 -> P08, 5-9 -> P05 J4; 10/11 -> P11 J8 (arkusz CONTACTS). TAPy trzech portow lacza sie przy portach (docs/WIAZKI.md).',8,19,1.3)
t('Dopuszczony jeden adapter naraz. P11 nie wybiera zrodla TAP; wspolne TAPy wymagaja procedury lub przeslony mechanicznej portow (jak R1).',8,70,1.3)
t('Prad silnika (do 6 A, 10 A w probie biernej): przewody >= 1.0 mm2 z portu wprost do P06 / P07, styki AT 13 A. Pomiar cieplny calej petli w odbiorze.',8,73.5,1.3)
ns=collections.defaultdict(set)
for name,sh in S.items():
 for part,pp in sh.parts.values():
  for n in pp:ns[part['pins'][n]].add(name)
cadlib.CROSS={n for n,v in ns.items() if len(v)>1 and n!='NC'}
for sh in S.values():sh.text(f'{cadlib.REV} / {sh.num:02d}   {sh.title.upper()}',8,5,2)
for i,(name,title) in enumerate(names[1:],2):
 sh=S[name];x,y=mm(132),mm(84+(i-2)*10);sid=uid('sheet/'+name)
 S['P11'].items.append(f'(sheet (at {x} {y}) (size 55.88 10.16) (stroke (width .15) (type default)) (fill (color 0 0 0 0)) (uuid {sid}) (property "Sheetname" {q(name)} (at {x} {y-1.27} 0) (effects (font (size 1 1)) (justify left bottom))) (property "Sheetfile" {q(name+".kicad_sch")} (at {x} {y+10.16} 0) (effects (font (size 1 1)) (justify left top))) (instances (project "P11" (path {q("/"+uid("P11"))} (page "{i}")))))')
 old=sh.path;sh.path='/'+uid('P11')+'/'+sid;sh.items=[t.replace(q(old),q(sh.path)) for t in sh.items]
for sh in S.values():sh.finish();sh.save()
write_tables()
(P/'verification/sheet-parts.json').write_text(json.dumps({n:list(s.parts) for n,s in S.items()},indent=2))
print(len(PARTS),'parts; three sheets')
