"""P11-R2 PANEL (format S1, schematic only). Single source of parts and pin nets.
Decisions 4.10.2026 (Plytki/Format-S1/zadania/ZADANIE-P11-S1.md, Plytki/P11-S1-przygotowanie/README.md):
P11-1 slimmed board: contact logic of R1 (key, STOP, ARM, MARK, NC loops L1/L2, TEST_PRESENT, MECH_OK) and one IDC 2x10 to P12;
P11-2 ports L1/L2/TEST = Amphenol AT04-12, off-board, only their signal pins reach P11 (wire field J8); keys as R1: L1 = B, L2 = C,
      TEST = A (user 4.10; adapters AL1/AL2/AT keep their plugs);
P11-3 3V3_IO from P12 through R1 100R, fitted only without P04 (DNP with P04, where PANEL_3V3 comes from P04 R40);
P11-4 no motor current on P11 (motor wires port -> P06 / P07: 2.0 mm2 / AWG14 over the full length, gold contacts AT60-215-1631 pin /
      AT62-209-1631 socket - user 4.10); P11-5 TAPS / ISERIES soldered wires port -> P05 / P06, no J7 / J1 on P11;
P11-7 ordinary push buttons with gold contacts (no MPN here).
Contact logic, functional switch terminals and the 18 used positions of the contact field J11 are taken over 1:1 from P11-R1
(src/parts.py of R1, `contact` and `spec`); verify_electrical.py compares them with reference/P11-R1-parts.json."""
from cadlib import *
import csv,shutil
FP=P/'eda/libraries/P11.pretty';FP.mkdir(parents=True,exist_ok=True);PARTS={}
G='GND';V='PANEL_3V3';N='NC'
def copyfp(lib,name):
 src=K/'footprints'/(lib+'.pretty')/(name+'.kicad_mod');assert src.exists(),src
 dest=P/'eda/libraries'/(lib+'.pretty');dest.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest/src.name)
 return lib+':'+name
def custom(name,units,half=12.7):
 # rows: (pin,name,electrical type) left/right. Explicit function symbols, not fake connectors (as in P11-R1 / P06-R2).
 s=f'(symbol "P11:{name}" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)'
 for u,(left,right) in enumerate(units,1):
  h=max(len(left),len(right))+1
  s+=f'(symbol "{name}_{u}_1" (rectangle (start {-half} {h*1.27}) (end {half} {-h*1.27}) (stroke (width .254) (type default)) (fill (type background))))'
  s+=f'(symbol "{name}_{u}_0"'
  for side,items in [(-1,left),(1,right)]:
   for j,(n,label,typ) in enumerate(items):
    s+=f'(pin {typ} line (at {side*(half+5.08)} {(h-2-j*2)*1.27} {0 if side==-1 else 180}) (length 5.08) (name {q(label)} (effects (font (size 1.0 1.0)))) (number "{n}" (effects (font (size 1 1)))))'
  s+=')'
 return parse(s+')')
# Wire fields (PTH solder pads, as P11-R1 make_footprints.py): 3.5 mm pitch, drill 1.1 / pad 2.3 (AWG22-24 and RG174 core),
# two NPTH 3.2 holes for a cable tie 10.5 mm behind the first row. PCB 4.10 (layout): pads numbered column by column, `rows` pads
# per column (as P05 J4): J11 has one switch contact per column (pads 2k-1 / 2k = the two wires of one contact, R1 pairs), so
# each column gets one silk label; J8 / J6 one pad per column.
def field(name,n,rows):
 pts=[(i+1,(i//rows)*3.5,(i%rows)*3.5) for i in range(n)];xmax=((n-1)//rows)*3.5;ymax=(min(n,rows)-1)*3.5
 s=f'(footprint {q(name)} (version 20240108) (generator "pcbnew") (layer "F.Cu") (attr through_hole)'
 for num,x,y in pts:s+=f'(pad "{num}" thru_hole {"rect" if num==1 else "circle"} (at {x} {y}) (size 2.3 2.3) (drill 1.1) (layers "*.Cu" "*.Mask"))'
 for x in (-3.5,xmax+3.5):s+=f'(pad "" np_thru_hole circle (at {x} -10.5) (size 3.2 3.2) (drill 3.2) (layers "*.Cu" "*.Mask"))'
 s+=f'(fp_rect (start -5.5 -12.5) (end {xmax+5.5} {ymax+2.4}) (stroke (width .05) (type default)) (fill none) (layer "F.CrtYd"))'
 s+=f'(fp_text reference "REF**" (at {xmax/2} -5) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15)))))'
 (FP/(name+'.kicad_mod')).write_text(s);return 'P11:'+name
def offboard():
 s='(footprint "OFFBOARD" (version 20240108) (generator "pcbnew") (layer "F.Cu") (attr through_hole)(fp_rect (start -1 -1) (end 1 1) (stroke (width .05) (type default)) (fill none) (layer "F.CrtYd"))(fp_text reference "REF**" (at 0 2.5) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15)))))'
 (FP/'OFFBOARD.kicad_mod').write_text(s);return 'P11:OFFBOARD'
OFF=offboard();F18=field('FIELD_CONTACT18',18,2);F2=field('FIELD_PAIR2',2,1)
IDC=copyfp('Connector_IDC','IDC-Header_2x10_P2.54mm_Horizontal')
R1206=copyfp('Resistor_SMD','R_1206_3216Metric_Pad1.30x1.75mm_HandSolder')
def add(ref,src,sym,fp,value,mpn,pins,sheet,url='',note='',on_board=True,**extra):
 PARTS[ref]=dict(ref=ref,source_ref=src,symbol=sym,footprint=fp,display=value,value=value,mpn=mpn,pins={str(k):v for k,v in pins.items()},sheet=sheet,url=url,note=note,qty=1,on_board=on_board,**extra)
def pins(*ns):return dict(enumerate(ns,1))
# --- J_P12: IDC 2x10 to P12 (S1 8: PANELCORE + PANELSAFE). Positions 10/13/14/15/16 = P03 R6 J_BP1 (straight P12 routing);
# odd pins GND except 13 MARK and 15 LOGGER_CLEAR (same exception as P03 R6 J_BP1); 3V3_IO on 20, away from PANEL_3V3 (pin 2),
# so a neighbour short in the ribbon cannot bypass R1 or put 3V3_IO in parallel with P04 R40. 12 and 18: GND (confirmed 4.10).
# Right-angle box header on the P11 edge facing wall A: P11 lies flat on the bottom of the panel zone (max approx. 45 x 130 mm,
# Plytki/P11-S1-przygotowanie/README.md P11-6), the ribbon leaves horizontally towards wall A.
JP12=pins(G,V,G,'MECH_OK',G,'STOP_NC_OUT',G,'ARM_CONTACT',G,'N_J_SCOPE_HOT',G,G,'MARK','TEST_KEY','LOGGER_CLEAR','TEST_PRESENT',G,G,G,'3V3_IO')
add('J_P12','J4+J5',symbol('Connector_Generic','Conn_02x10_Odd_Even'),IDC,'IDC 2x10 katowe do P12','Box header IDC 2x10 2.54 mm, right-angle, gold (MPN in purchase task)',JP12,'P12',
    note='Ribbon to P12 (S1 8). RIGHT-ANGLE box header on the P11 edge facing wall A (P11 lies flat on the bottom of the panel zone, max approx. 45 x 130 mm; user 4.10). Pins 12/18 GND. Replaces R1 J4 PANELCORE and J5 PANELSAFE.')
# --- R1: PANEL_3V3 source in LOGGER (P11-3). DNP when P04 is fitted (P04 R40 100R from 3V3_IO feeds PANEL_3V3 then).
add('R1','ADDED_P11_3',symbol('Device','R'),R1206,'100R','RC1206FR-07100RL',pins('3V3_IO',V),'P12',
    note='LOGGER (no P04): FITTED. Full variant (P04 fitted): DNP - P04 R40 is the only PANEL_3V3 source. 1206 0.25 W; short PANEL_3V3-GND: 34 mA / 0.12 W.',
    variant={'LOGGER':'fitted','FULL':'DNP'},variant_label='LOGGER: obsadzony / z P04: DNP',ohms=100.0,tolerance=.01,power_W=.25)
# --- Contact field J11 (R1 mapping, positions 19/20 of R1 were NC and are dropped).
CONTACT=pins(V,'TEST_KEY','TEST_KEY','ILK_L1_L2',V,'DIAG_L1_L2','ILK_L1_L2','LOOP_OUT','DIAG_L1_L2','LOGGER_CLEAR',V,'STOP_NC_OUT',G,'ARM_CONTACT',G,'MARK',V,'TEST_PRESENT')
add('J11','J11',symbol('Connector_Generic','Conn_01x18'),F18,'CONTACTS / panel','Soldered AWG24 wires (PTFE or PVC 0.25 mm2)',CONTACT,'CONTACTS',
    note='Functional wire list in docs/WIAZKI.md. Same contact assignment as R1 J11.1..18.')
# --- TEST port signal pins (P11-2): port cavity 10 LOOP_OUT, 11 MECH_OK. MECH_OK returns via the bridge 10-11 at the far end of adapter AT.
add('J8','J8 (pins 10/11)',symbol('Connector_Generic','Conn_01x02'),F2,'TEST signal / port 10-11','Soldered AWG24 wires to TEST port cavities 10/11',pins('LOOP_OUT','MECH_OK'),'CONTACTS',
    note='1 -> TEST port cavity 10 (LOOP_OUT), 2 -> cavity 11 (MECH_OK). Other TEST cavities do not reach P11 (P11-4/P11-5).')
# --- SCOPE trigger to insulated BNC (R1 J6/X6 unchanged).
add('J6','J6_TAIL',symbol('Connector_Generic','Conn_01x02'),F2,'SCOPE tail','RG174 ~100 mm',pins('N_J_SCOPE_HOT',G),'P12')
add('X6','J6',symbol('Connector_Generic','Conn_01x02'),OFF,'SCOPE BNC','Insulated panel BNC, solder cup',pins('N_J_SCOPE_HOT',G),'P12',on_board=False,
    note='1=center; 2=shell. High impedance 1 Mohm only, no 50R termination. Insulated from a metal panel.')
# --- Ports (off-board, panel). Cavity mapping as R1 (adapters AL1/AL2/AT unchanged); function names show where the wire goes.
PORT_L1=[('1','ECU_P1 -> P06 J3'),('2','EGR_P1 -> P06 J3'),('3','TAP_P1 -> P05 J4'),('4','TAP_P3 -> P05 J4'),('5','TAP_P4 -> P05 J4'),('6','TAP_P5 -> P05 J4'),('7','TAP_P6 -> P05 J4'),('8','-'),('9','-'),('10','-'),('11','-'),('12','GND -> P05 J4')]
PORT_L2=[('1','TAP_P1 -> P05 J4'),('2','TAP_P3 -> P05 J4'),('3','TAP_P4 -> P05 J4'),('4','TAP_P5 -> P05 J4'),('5','TAP_P6 -> P05 J4')]+[(str(i),'-') for i in range(6,12)]+[('12','GND -> P05 J4')]
PORT_T=[('1','T_EGR_P1 -> P07'),('2','T_EGR_P3 -> P07'),('3','5V_SENSOR -> P08'),('4','AGND_SENSOR -> P08'),('5','TAP_P1 -> P05 J4'),('6','TAP_P3 -> P05 J4'),('7','TAP_P4 -> P05 J4'),('8','TAP_P5 -> P05 J4'),('9','TAP_P6 -> P05 J4'),('10','LOOP_OUT -> P11 J8.1'),('11','MECH_OK -> P11 J8.2'),('12','-')]
PORTS={'X2':('L1','B',PORT_L1),'X3':('L2','C',PORT_L2),'X8':('TEST','A',PORT_T)}   # keys as R1 (user 4.10)
MOTOR={'X2':'1/2','X8':'1/2'}   # motor current cavities: ECU_P1/EGR_P1 -> P06 J3, T_EGR_P1/T_EGR_P3 -> P07
for r,(name,key,pp) in PORTS.items():
 sy=custom('PORT_'+name,[([(n,l,'passive') for n,l in pp[:6]],[(n,l,'passive') for n,l in pp[6:]])],half=27.94)
 net={n:N for n,_ in pp}
 if r=='X8':net.update({'10':'LOOP_OUT','11':'MECH_OK'})
 add(r,r.replace('X','J')+' (R1)',sy,OFF,f'{name} port AT04-12 key {key}',f'Amphenol AT04-12P{key} receptacle'+(f'; cavities {MOTOR[r]} (motor current): gold pins AT60-215-1631 for 2.0 mm2 / AWG14, mating gold sockets AT62-209-1631' if r in MOTOR else '')+'; other contacts per data sheet (purchase task)',net,'CONTACTS',on_board=False,
     note=f'Panel port {name}, key {key} (as R1, user 4.10). '+(f'Motor current cavities {MOTOR[r]}: 2.0 mm2 (AWG14) wire over the full length to P06 / P07, not via P11. ' if r in MOTOR else '')+'Only cavities 10/11 of TEST reach P11; all other cavities are wired port -> board directly (docs/PORTY.csv). Cavity numbers, not pin positions.',port=name,key=key)
# --- Panel contacts: functional terminals as R1 (X11..X17). P11-7: ordinary buttons/switches with GOLD contacts, low-level duty.
GOLD='Gold-plated contacts for low-level duty (closed contact approx. 0.31-0.32 mA in LOGGER, 0.03-0.87 mA in the full variant, at 3.3 V; verification/QA.md, verify_electrical.py); MPN chosen in a separate purchase task.'
spec=[('X11','ARM momentary NO','ARM: push button, momentary, NO',pins(G,'ARM_CONTACT'),['COM','NO']),
      ('X12','L1 detector 2NC','L1 port detector: 2 x NC, opens before the first plug contact',pins('TEST_KEY','ILK_L1_L2',V,'DIAG_L1_L2'),['COM_A','NC_A','COM_B','NC_B']),
      ('X13','L2 detector 2NC','L2 port detector: 2 x NC, opens before the first plug contact',pins('ILK_L1_L2','LOOP_OUT','DIAG_L1_L2','LOGGER_CLEAR'),['COM_A','NC_A','COM_B','NC_B']),
      ('X14','MARK momentary NO','MARK: push button, momentary, NO',pins(G,'MARK'),['COM','NO']),
      ('X15','KEY TEST NO','Key switch: NO in position TEST, key removable in OFF',pins(V,'TEST_KEY',N,N),['COM_NO','TEST_NO','NC_UNUSED_A','NC_UNUSED_B']),
      ('X16','STOP latched NC+NO','STOP: latching mushroom, NC opens in STOP (NO unused)',pins(V,'STOP_NC_OUT',N,N),['COM_NC','NC','NO_UNUSED_A','NO_UNUSED_B']),
      ('X17','TEST detector NO','TEST port detector: NO, closes only with the plug fully seated',pins(V,'TEST_PRESENT'),['COM','NO'])]
for r,val,mpn,pn,labels in spec:
 sy=custom(r+'_CONTACT',[([(i+1,l,'passive') for i,l in enumerate(labels)],[])])
 add(r,r,sy,OFF,val,mpn+' - gold contacts',pn,'CONTACTS',on_board=False,
     note='Functional terminal numbers; identify physical terminals on the purchased part by continuity test. '+GOLD+' No illumination supply.',gold=True)
def write_tables():
 clean={r:{k:v for k,v in p.items() if k!='symbol'} for r,p in PARTS.items()}
 (P/'docs/parts.json').write_text(json.dumps(clean,indent=2,ensure_ascii=False),encoding='utf-8')
 libs={p['symbol'][1]:p['symbol'] for p in PARTS.values()}
 (P/'eda/libraries/P11.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor")'+''.join(dump([s[0],s[1].split(':')[1]]+s[2:]) for s in libs.values())+')',encoding='utf-8')
 (P/'eda/sym-lib-table').write_text('(sym_lib_table (lib (name "P11") (type "KiCad") (uri "${KIPRJMOD}/libraries/P11.kicad_sym") (options "") (descr "P11 symbols")))')
 flibs=sorted({p['footprint'].split(':')[0] for p in PARTS.values()})
 (P/'eda/fp-lib-table').write_text('(fp_lib_table '+''.join(f'(lib (name {q(l)}) (type "KiCad") (uri "${{KIPRJMOD}}/libraries/{l}.pretty") (options "") (descr "P11 local library"))' for l in flibs)+')')
if __name__=='__main__':write_tables()
