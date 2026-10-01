"""P06-R2 explicit circuit (format S1). Circuit as P06-R1; connectors to other boards on edge A (J_BP), service strips on
edge B (J_SV1, J_SV2), Kelvin shunt SMD 2512, BYPASS switch generic (off-board), part types per S1 (owned THT standing, new SMD 1206).
R1 header: explicit circuit, physical SOIC pinouts and wire endpoints; baseline v6.1 preserved at interfaces (R1 docs/ZMIANY.md).
Decisions 1.10.2026 (task Plytki/Format-S1/zadania/ZADANIE-P06-S1.md): class 2/3, slots S1-S2 of level 4; RSH1 2512 Kelvin; BYPASS on the
panel (DPDT ON-ON >= 10 A DC instead of NKK S6A); C3 = 220 uF."""
from cadlib import *
import csv,shutil
FP=P/'eda/libraries/P06.pretty';FP.mkdir(parents=True,exist_ok=True);PARTS={}
URL={k:v['url'] for k,v in json.loads((P/'reference/datasheets/sources.json').read_text()).items()}
G='GND';V='3V3_P06';A5='5VA_P06'
REG='rejestr';NEW='nowe'
def copyfp(lib,name):
 src=K/'footprints'/(lib+'.pretty')/(name+'.kicad_mod');assert src.exists(),src
 dest=P/'eda/libraries'/(lib+'.pretty');dest.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest/src.name)
 return lib+':'+name
def localfp(name):
 shutil.copy2(P/'input/footprints'/(name+'.kicad_mod'),FP/(name+'.kicad_mod'));return 'P06:'+name
def custom(name,units):
 # rows: (pin,name,electrical type) left/right. Explicit function symbols, not fake connectors.
 s=f'(symbol "P06:{name}" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)'
 for u,(left,right) in enumerate(units,1):
  h=max(len(left),len(right))+1;half=12.7
  s+=f'(symbol "{name}_{u}_1" (rectangle (start {-half} {h*1.27}) (end {half} {-h*1.27}) (stroke (width .254) (type default)) (fill (type background))))'
  s+=f'(symbol "{name}_{u}_0"'
  for side,items in [(-1,left),(1,right)]:
   for j,(n,label,typ) in enumerate(items):
    s+=f'(pin {typ} line (at {side*(half+5.08)} {(h-2-j*2)*1.27} {0 if side==-1 else 180}) (length 5.08) (name {q(label)} (effects (font (size 1.0 1.0)))) (number "{n}" (effects (font (size 1 1)))))'
  s+=')'
 return parse(s+')')
# Wire pigtails (unchanged from P06-R1 src/make_footprints.py): PTH solder joints, two anchor holes 12 mm from the first row.
# R2 local layout (1.10): rev=True numbers the pads from the far end (pad 1 at x = (n-1)*pitch). After the 90 deg turn at the x=0 edge
# J3.1 then lies above J3.2, so ECU_P1 and EGR_P1 of J3, J4 and RSH1 each stay one piece of copper on both layers (README, PCB).
def tail(name,n,pitch,drill,pad,rev=False):
 pts=[(i+1,((n-1-i) if rev else i)*pitch,0,drill,pad) for i in range(n)]+[('',-3.5,-12,3.2,3.2),('',(n-1)*pitch+3.5,-12,3.2,3.2)]
 xmax=(n-1)*pitch
 s=f'(footprint {q(name)} (version 20240108) (generator "pcbnew") (layer "F.Cu") (attr through_hole)'
 for num,x,y,d,w in pts:
  s+=f'(pad "{num}" {"thru_hole" if num else "np_thru_hole"} {"rect" if num==1 else "circle"} (at {x} {y}) (size {w} {w}) (drill {d}) (layers "*.Cu" "*.Mask"))'
 s+=f'(fp_rect (start -5.5 -14) (end {xmax+5.5} {pad/2+.5}) (stroke (width .05) (type default)) (fill none) (layer "F.CrtYd"))'
 s+=f'(fp_text reference "REF**" (at {xmax/2} {pad/2+2}) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15)))))'
 (FP/(name+'.kicad_mod')).write_text(s);return 'P06:'+name
def offboard():
 s='(footprint "OFFBOARD" (version 20240108) (generator "pcbnew") (layer "F.Cu") (attr through_hole)(fp_rect (start -1 -1) (end 1 1) (stroke (width .05) (type default)) (fill none) (layer "F.CrtYd"))(fp_text reference "REF**" (at 0 2.5) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15)))))'
 (FP/'OFFBOARD.kicad_mod').write_text(s);return 'P06:OFFBOARD'
# S1 1/4/9: owned THT parts from Zamowione/zamowione.csv where a surplus remains after P02 R4, P05 R3, P09 R2 and P10 R2 (docs/ZAKUPY.md):
# resistors stand upright; everything new is SMD 1206. Exceptions (README): RSH1 2512 Kelvin, R6 1 W and R21 2 W lying (power),
# C3 radial electrolytic, diodes and ICs with the R1 packages.
RV=copyfp('Resistor_THT','R_Axial_DIN0207_L6.3mm_D2.5mm_P5.08mm_Vertical')
R1206=copyfp('Resistor_SMD','R_1206_3216Metric_Pad1.30x1.75mm_HandSolder');C1206=copyfp('Capacitor_SMD','C_1206_3216Metric_Pad1.33x1.80mm_HandSolder')
RPOWER=copyfp('Resistor_THT','R_Axial_DIN0411_L9.9mm_D3.6mm_P15.24mm_Horizontal');RPR02=localfp('R_PR02_P17.78')
CP63=copyfp('Capacitor_THT','CP_Radial_D6.3mm_P2.50mm')
SO8=copyfp('Package_SO','SOIC-8_3.9x4.9mm_P1.27mm');SO14=copyfp('Package_SO','SOIC-14_3.9x8.7mm_P1.27mm')
DIP8=copyfp('Package_DIP','DIP-8_W7.62mm');DIP14=copyfp('Package_DIP','DIP-14_W7.62mm')
TO92=copyfp('Package_TO_SOT_THT','TO-92_Inline_Wide')
DIO=copyfp('Diode_THT','D_DO-41_SOD81_P10.16mm_Horizontal');DIO35=copyfp('Diode_THT','D_DO-35_SOD27_P7.62mm_Horizontal')
def shunt_fp():
 # R2 local review (1.10): Vishay data sheet 30108 (rev. 11-Dec-2023), solder pads for 0.005..0.2 Ohm: a 2.29, b 3.30, c 0.76, d 0.51,
 # e 1.70, l 3.68 mm. The KiCad library footprint matches except the sense pad length e (1.40): sense pads 1.70 mm from the outer edge.
 name='R_Shunt_Vishay_WSK2512_T1.19mm_SenseE1.70'
 t=(K/'footprints/Resistor_SMD.pretty/R_Shunt_Vishay_WSK2512_6332Metric_T1.19mm.kicad_mod').read_text()
 for a,b in (('(footprint "R_Shunt_Vishay_WSK2512_6332Metric_T1.19mm"',f'(footprint "{name}"'),
             ('(property "Value" "R_Shunt_Vishay_WSK2512_6332Metric_T1.19mm"',f'(property "Value" "{name}"'),
             ('(at -3.43 1.27)\n\t\t(size 1.4 0.76)','(at -3.28 1.27)\n\t\t(size 1.7 0.76)'),
             ('(at 3.43 -1.27)\n\t\t(size 1.4 0.76)','(at 3.28 -1.27)\n\t\t(size 1.7 0.76)')):
  assert t.count(a)==1,a;t=t.replace(a,b)
 t=t.replace('(descr "','(descr "EGRLab P06 R2: sense pads e = 1.70 mm per Vishay 30108 rev. 11-Dec-2023 (library: 1.40). ',1)
 (FP/(name+'.kicad_mod')).write_text(t);return 'P06:'+name
SHUNT_FP=shunt_fp()
def add(ref,src,sym,fp,value,mpn,pins,sheet,url='',note='',on_board=True,zrodlo=NEW,**extra):
 PARTS[ref]=dict(ref=ref,source_ref=src,symbol=sym,footprint=fp,display=value,value=value,mpn=mpn,pins={str(k):v for k,v in pins.items()},sheet=sheet,url=url,note=note,qty=1,on_board=on_board,zrodlo=zrodlo,**extra)
SR=symbol('Device','R');SC=symbol('Device','C');SCP=symbol('Device','C_Polarized')
# Owned MF0207 left after P02 R4 / P05 R3 / P09 R2 / P10 R2 (docs/ZAKUPY.md): 47K x1 (R11). 10K and 100K: none left.
OWNED_R={'47K':'MF0207FTE-47K'}
def code(value):return value.replace('.','K',1)[:-1] if value.endswith('K') and '.' in value else value
def res(r,src,val,ohms,a,b,sh,tol=.01):
 if tol==.001:
  add(r,src,SR,R1206,val,'RT1206BRD07'+code(val)+'L',{1:a,2:b},sh,note='Thin film 1206, 0.1 %, 25 ppm/K (Yageo RT, MPN proposal to confirm in TME/data sheet). One full-value resistor.',ohms=ohms,tolerance=tol,tcr_ppm=25)
 elif val in OWNED_R:add(r,src,SR,RV,val,OWNED_R[val]+' (Yageo MF0207 1% 0.6W, owned, standing)',{1:a,2:b},sh,zrodlo=REG,ohms=ohms,tolerance=tol)
 else:add(r,src,SR,R1206,val,'RC1206FR-07'+code(val)+'L',{1:a,2:b},sh,ohms=ohms,tolerance=tol)
def cap(r,src,val,farad,a,b,sh,mpn=None,note=''):
 add(r,src,SC,C1206,val,mpn or ('SMD 1206 C0G 50V 5% ' if farad<1e-8 else 'SMD 1206 X7R 50V 10% ')+val,{1:a,2:b},sh,farads=farad,note=note)
ina=custom('INA240A2_D_SOIC',[
 ([(8,'IN+','input'),(1,'IN-','input')],[(5,'OUT','output')]),
 ([(6,'VS','power_in'),(7,'REF1','input'),(3,'REF2','input')],[(2,'GND','power_in'),(4,'NC','no_connect')])])
add('U1','U37',ina,SO8,'INA240A2','INA240A2EDRQ1',{1:'INA_MINUS',2:G,3:'REF_BUF',4:'NC',5:'I_L_OUT',6:A5,7:'REF_BUF',8:'INA_PLUS'},'ANA',URL['INA240.pdf'],'SOIC D pinout. Direct hand soldering, 1.27 mm pitch, top side only (level 4); no socket in Kelvin path.',zrodlo=REG)
add('U2','U39',symbol('Amplifier_Operational','MCP6022'),DIP8,'MCP6022-I/P','MCP6022-I/P',{1:'ADC_BUF',2:'ADC_BUF',3:'I_DIV',4:G,5:'REF25',6:'REF_BUF',7:'REF_BUF',8:V},'ANA',URL['MCP6022.pdf'],'Owned DIP8 socket (Kamami 1207058) optional.',zrodlo=REG)
adc=custom('MCP3201_B_P',[( [(1,'VREF','power_in'),(2,'IN+','input'),(3,'IN-','input'),(4,'VSS','power_in')],[(8,'VDD','power_in'),(7,'CLK','input'),(6,'DOUT','tri_state'),(5,'CS_N','input')])])
add('U3','U38',adc,DIP8,'MCP3201-BI/P','MCP3201-BI/P',{1:'REF25',2:'ADC_AIN',3:G,4:G,5:'CS_LOCAL_N',6:'ADC_DOUT',7:'CLK_LOCAL',8:V},'DIG',URL['MCP3201.pdf'],zrodlo=REG)
ldo=custom('MCP1702_TO92',[( [(2,'VIN','power_in'),(1,'GND','power_in')],[(3,'VOUT','power_out')])])
add('U4','U40',ldo,TO92,'MCP1702-3302E/TO','MCP1702-3302E/TO',{1:G,2:A5,3:V},'P06',URL['MCP1702.pdf'],zrodlo=REG)
lvc=symbol('74xx','74LVC125','74LVC125AD')
add('U5','U43',lvc,SO14,'74LVC125AD','74LVC125AD,118 (Nexperia)',{1:G,2:'CS_ILOG_N',3:'CS_LOCAL_N',4:G,5:'ADC_SCLK',6:'CLK_LOCAL',7:G,8:'DOUT_TX',9:'ADC_DOUT',10:'CS_LOCAL_N',11:'NC',12:G,13:V,14:V},'DIG',URL['LVC125.pdf'],'Ioff required. Unused OE tied to LOCAL rail. SOIC top side only (level 4).',zrodlo=REG)
add('U6','U46',lvc,SO14,'74LVC125AD','74LVC125AD,118 (Nexperia)',{1:G,2:'SUP5_RAW',3:'SUP5_N',4:G,5:'SW_SENSE',6:'SHUNT_ENABLED',7:G,8:'LOGGER_OK_TX',9:'LOGGER_OK_LOCAL',10:G,11:'NC',12:G,13:V,14:V},'READY',URL['LVC125.pdf'],'5V-tolerant input for 5V supervisor and switch; Ioff on READY output. SOIC top side only.',zrodlo=REG)
add('U7','U41',symbol('74xx','74LS08','SN74HC08N'),DIP14,'SN74HC08N','SN74HC08N',{1:'SUP3_N',2:'SUP5_N',3:'RAILS_OK',4:'RAILS_OK',5:'SHUNT_ENABLED',6:'LOGGER_OK_LOCAL',7:G,8:'NC',9:G,10:G,11:'NC',12:G,13:G,14:V},'READY',URL['HC08.pdf'],'Owned DIP14 socket (Kamami 648) optional.',zrodlo=REG)
sup=custom('MCP120_D_TO',[( [(2,'VDD','power_in')],[(1,'RESET_N','open_collector'),(3,'VSS','power_in')])])
for r,src,mpn,rail,out in [('U8','U44','MCP120-300DI/TO',V,'SUP3_N'),('U9','U45','MCP120-450DI/TO',A5,'SUP5_RAW')]:
 add(r,src,sup,TO92,mpn,mpn,{1:out,2:rail,3:G},'READY',URL['MCP120.pdf'],'D bondout: reset=1, VDD=2, GND=3. Open drain.',zrodlo=REG)
ref=custom('MCP1525_TO92',[( [(3,'VIN','power_in'),(1,'GND','power_in')],[(2,'VOUT','power_out')])])
add('U10','U42',ref,TO92,'MCP1525-I/TO','MCP1525-I/TO',{1:G,2:'REF25',3:V},'ANA',URL['MCP1525.pdf'],'TO92: 1 GND, 2 OUT, 3 IN; not the SOT23 pin order.',zrodlo=REG)
# R2: Kelvin shunt SMD 2512 (decision 28.09/1.10) instead of PBV. Footprint pads (WSK2512, T 1.19 mm for 5..200 mOhm, shunt_fp()):
# 1 force left, 2 sense left, 3 sense right, 4 force right -> nets as R1 by function: force ECU_P1 / EGR_P1, sense K_PLUS next to ECU_P1.
sh=symbol('Device','R_Shunt','R_Shunt_2512_Kelvin')
add('RSH1','X24',sh,SHUNT_FP,'5m / 1% / 2512 Kelvin','WSK25125L000FEA (Vishay WSK2512, 5 mOhm 1%, 1 W at 70 C, TCR +-35 ppm/K, 4-terminal; alt. Bourns CSS2H-2512K-5L00F - footprint differs)',{1:'ECU_P1',2:'K_PLUS',3:'K_MINUS',4:'EGR_P1'},'FORCE','https://www.vishay.com/docs/30108/wsk2512.pdf','Pads 1/4 force (current), 2/3 sense (Kelvin). Data sheet 30108 rev. 11-Dec-2023 (checked locally 1.10): 1.0 W at 70 C, TCR +-35 ppm/K for 5..200 mOhm, part code 5L000 for 5 mOhm (L = mOhm below 0.01 Ohm); sense pads e = 1.70 mm (KiCad library 1.40). 6 A: 0.18 W; 10 A passive qualification: 0.5 W.',ohms=.005,tolerance=.01)
# R2: BYPASS switch off-board on the panel, generic DPDT ON-ON >= 10 A DC (decision 1.10) instead of NKK S6A. Terminal numbering of
# the KiCad SW_DPDT_x2 symbol: commons 2 and 5 (as S6A): BYPASS 2-3 + 5-6, MEASURE 2-1 + 5-4. Real lug numbers to check with an ohmmeter.
sw=symbol('Switch','SW_DPDT_x2','SW_DPDT_ONON_PANEL')
add('SW1','X36',sw,offboard(),'DPDT ON-ON / BYPASS-MEASURE','DPDT ON-ON panel toggle >=10A 12-30VDC, solder lugs (MPN to confirm)',{1:'NC',2:'ECU_P1',3:'EGR_P1',4:A5,5:'SW_RAW',6:G},'FORCE','','Panel mount. BYPASS 2-3,5-6; MEASURE 2-1,5-4. No motor current in pole B. Switch only with ignition off.',False)
# Current path and analog scaling. R2: R3/R4 5.11K 0.1 % (list 2 replacement 1:1 for 5K1), 1206 25 ppm/K.
for a in [('R1','R22','10R',10,'K_PLUS','INA_PLUS'),('R2','R23','10R',10,'K_MINUS','INA_MINUS'),('R3','R28','5.11K',5110,'I_L_OUT','I_DIV'),('R4','R29','5.11K',5110,'I_DIV',G)]:res(*a,'ANA',tol=.001)
res('R5','R25','47R',47,'ADC_BUF','ADC_AIN','DIG')
add('R6','R26',SR,RPOWER,'1R','KNP01U-1R (1R 1W wirewound, body 3x9mm)',{1:'5V_SYS',2:A5},'P06',note='Power exception, lying (as P05 R3 R1). Charge pulse of C3 220uF: ~3.0mJ at 5.25V, tau ~0.22ms (R1: 6.5mJ with 470uF); pulse rating to confirm with the data sheet.',ohms=1,tolerance=.01)
res('R7','R27','10K',10000,V,'CS_LOCAL_N','DIG')
res('R8','R31','100K',100000,V,'CS_ILOG_N','DIG')
res('R9','ADD_CLK_PD','10K',10000,'CLK_LOCAL',G,'DIG')
res('R10','ADD_CLK_EXT_PD','100K',100000,'ADC_SCLK',G,'DIG')
res('R11','R32','47K',47000,V,'ADC_DOUT','DIG')
res('R12','ADD_DOUT_SER','47R',47,'DOUT_TX','ADC_DOUTA','DIG')
res('R13','R34','10K',10000,A5,'SUP5_RAW','READY')
res('R14','R35','10K',10000,V,'SUP3_N','READY')
res('R15','ADD_SUP5_PD','10K',10000,'SUP5_N',G,'READY')
res('R16','R30','10K',10000,'SHUNT_ENABLED',G,'READY')
res('R17','R33','10K',10000,'RAILS_OK',G,'READY')
res('R18','ADD_READY_PD','10K',10000,'LOGGER_OK_LOCAL',G,'READY')
res('R19','ADD_READY_SER','100R',100,'LOGGER_OK_TX','LOGGER_CURRENT_OK','READY')
res('R20','ADD_READY_EXT_PD','10K',10000,'LOGGER_CURRENT_OK',G,'READY')
# R21: contact wetting ~0.13 A, 0.64 W at 5.0 V / 0.71 W at 5.25 V. Exception: THT PR02 2 W lying, 3-5 mm above the laminate
# (2512 1 W would run at ~70 % of rating with the hot spot on the laminate next to the analog path) - README.
add('R21','ADD_CONTACT_WETTING',SR,RPR02,'39R','PR02000203909JA100 (Vishay PR02 39R 5% 2W, lying; code by analogy with the owned PR02000201009JA100, to confirm)',{1:'SW_RAW',2:G},'FORCE','https://www.vishay.com/docs/28729/pr010203.pdf','Power exception: 0.71W max at 5.25V = 36% of 2W; lying 3-5 mm above PCB, away from RSH1/U10.',ohms=39,tolerance=.05,power_w=2)
res('R22','ADD_CONTACT_SER','1K',1000,'SW_RAW','SW_SENSE','READY')
res('R23','ADD_CONTACT_PD','100K',100000,'SW_SENSE',G,'READY')
res('R24','ADD_LOCAL_BLEED','1K',1000,V,G,'P06')
# R2: C1 X7R 1206 (was PET film; tau tolerance budget in verify_electrical.py), C4/C5 4.7u X7R 1206 (MCP1525: CL 1..10 uF,
# MCP1702: ceramic X7R output allowed - reference/datasheets/*.txt), C3 220u (decision 1.10).
cap('C1','C_DIV_L','470n',470e-9,'I_DIV',G,'ANA',note='X7R 1206 50V 10%: trend filter, not precision; tau budget includes X7R tolerance and temperature.')
cap('C2','C_AIN','470p',470e-12,'ADC_AIN',G,'ADC')
add('C3','C28',SCP,CP63,'220u / 16V','EEUFR1C221',{1:A5,2:G},'P06',farads=220e-6,note='Panasonic FR, D6.3 x 11.2mm, pitch 2.5mm; 20%. 1.10 user decision: 220uF (was 470uF) - with P05 C1 220uF the 5V_SYS load stays under the 600uF of the TSR 2-2450 (about 486uF in all). MPN/size to confirm.')
cap('C4','C_LDO_OUT','4.7u',4.7e-6,V,G,'P06',mpn='SMD 1206 X7R 25V 10% 4.7u')
cap('C5','C_REF','4.7u',4.7e-6,'REF25',G,'ANA',mpn='SMD 1206 X7R 25V 10% 4.7u',note='MCP1525 load capacitor 1..10 uF effective, within 5 mm of U10.')
cap('C16','ADD_ADC_REF_HF','100n',1e-7,'REF25',G,'ADC')
add('D2','ADD_REF_DISCHARGE',symbol('Device','D_Schottky'),DIO35,'BAT85','BAT85,133 (Nexperia)',{1:V,2:'REF25'},'ANA','https://assets.nexperia.com/documents/data-sheet/BAT85.pdf','Discharge of reference capacitor into local rail during power removal.')
for i,(r,rail) in enumerate([('U1',A5),('U2',V),('U3',V),('U4',A5),('U5',V),('U6',V),('U7',V),('U8',V),('U9',A5),('U10',V)],6):
 cap('C'+str(i),'DEC_'+r,'100n',1e-7,rail,G,'P06')
add('D1','ADD_LDO_DISCHARGE',symbol('Device','D_Schottky'),DIO,'1N5819','1N5819',{1:A5,2:V},'P06','https://www.vishay.com/docs/88525/1n5817.pdf','Anode on local 3.3 V, cathode on 5VA; output-cap discharge path on supply removal.')
# Wires that stay (S1 5): ISERIES and both BYPASS harnesses, PTH at the x=0 board edge (R1 pigtails: 2.4 mm holes, tie anchor 12 mm).
# R2 local layout (1.10): J3 with 2 pads (R1 pads 3/4 were empty) and J4 at 7.62 mm instead of 17.78 - with the R1 sizes J3, J4 and J5
# need 81 mm of the x=0 edge, the M3 zones leave 65 mm. J3 numbered from the far end (tail rev).
conns=[('J3','J_ISERIESB','ISERIES',tail('PTH_ISERIES',2,7.62,2.4,4.5,rev=True),{1:'ECU_P1',2:'EGR_P1'}),
 ('J4','ADD_BYPASS_FORCE','SW1 A',tail('PTH_BYPASS',2,7.62,2.4,4.5),{1:'ECU_P1',2:'EGR_P1'}),
 ('J5','ADD_BYPASS_STATUS','SW1 B',tail('PTH_SWSTATUS',3,3.5,1.1,2.2),{1:A5,2:'SW_RAW',3:G})]
for r,s,n,fp,pins in conns:add(r,s,symbol('Connector_Generic',f'Conn_01x{len(pins):02d}'),fp,n+' / PTH','Soldered harness',pins,'FORCE',note='PTH solder joint at the x=0 edge; tie anchor 12 mm. See docs/WIAZKI.md.')
# R2 (S1 5): J1 LV06 and J2 ILOG replaced by one angled shrouded IDC 2x8 on edge A, slot S2 (centre x = 80.0 mm). Nets and functions as R1.
# ADC_SCLK / ADC_DOUTA on pins 2 / 4 as J_BP2 of P03 R6 and P05 R3 (common bus straight up on P12).
JBP={2:'ADC_SCLK',4:'ADC_DOUTA',6:'CS_ILOG_N',8:'LOGGER_CURRENT_OK',10:'5V_SYS',12:'5V_SYS',14:'3V3_IO',16:G}
JBP.update({i:G for i in range(1,16,2)})
add('J_BP','J_LV06B+J_ILOGB',symbol('Connector_Generic','Conn_02x08_Odd_Even'),copyfp('Connector_IDC','IDC-Header_2x08_P2.54mm_Horizontal'),'J_BP / IDC 2x8','IDC header 2x8 2.54mm angled shrouded, Au',JBP,'CONNECT',note='Edge A, slot S2 (centre x=80.0 mm), pin 1 towards smaller x. Odd pins GND; 5V_SYS x2 (S1 5); 3V3_IO only to the service strip (no consumer on P06, as R1 LV06.3 -> TP4); 16 GND reserve.')
# Service strips on edge B (S1 6): angled goldpin, GND first and last, every other pin through a series resistor placed at the node.
# 1K rails/logic, 10K high-impedance and analog nodes (task 6: REF25, REF_BUF, ADC_AIN, SUP3_N, SUP5_N; I_L_OUT too - analog node).
# Neighbour rule (P03 R6, decision 1.10): rail only next to GND, another rail or a 10K line; analog nodes not next to rails.
SV1=[(None,),('I_L_OUT',10000,'wyjscie INA240: 2,500 V przy 0 A, 0,25 V/A (E04, E11-E13)'),('ADC_AIN',10000,'wejscie MCP3201 za R5/C2: 1,250 V przy 0 A (E11)'),(None,),
 ('REF_BUF',10000,'bufor U2B na REF INA240: = REF25 +/- offset U2 (E04)'),('REF25',10000,'MCP1525 (U10), VREF ADC: 2,475-2,525 V (E04)'),(None,)]
SV2=[(None,),('5V_SYS',1000,'5V_SYS na P06 z J_BP (E04, E05)'),(A5,1000,'5VA_P06 za R6 1R (spadek ok. 0,18 V przy 180 mA)'),(V,1000,'3V3_P06 z U4 (E04; E08: < 0,1 V przy wylaczonym P06)'),(None,),
 ('3V3_IO',1000,'3V3_IO z P02 przez J_BP.14 (bez odbiorcy na P06)'),('SUP3_N',10000,'nadzorca 3V3_P06 U8 (OD, 10k R14) (E06, E07)'),('SUP5_N',10000,'nadzorca 5VA U9 za buforem U6A (E06, E07)'),
 ('SHUNT_ENABLED',1000,'styk MEASURE za U6B: H w MEASURE, L w BYPASS (E07)'),('LOGGER_CURRENT_OK',1000,'READY do P03 za R19 (E07, E14)'),('CS_LOCAL_N',1000,'CS MCP3201 za U5A (E08, E10)'),
 ('CLK_LOCAL',1000,'zegar MCP3201 za U5B (E10)'),(None,)]
SERVICE={};nr=25
for jref,rows,src in [('J_SV1',SV1,'SERVICE_S1'),('J_SV2',SV2,'SERVICE_S2')]:
 n=len(rows);pp={}
 for k,row in enumerate(rows,1):
  if row[0] is None:pp[k]=G;continue
  net,ohm,why=row;r='R'+str(nr);nr+=1;pp[k]='SRV_'+net;SERVICE[net]=(jref,k,r,ohm,why)
  res(r,'ADDED_'+src,{1000:'1K',10000:'10K'}[ohm],ohm,net,'SRV_'+net,'SERWIS')
  PARTS[r]['note']='Service pin series resistor at the node (S1 6): slipped probe cannot damage anything. SMD, may sit on the bottom side.'
 add(jref,src,symbol('Connector_Generic',f'Conn_01x{n:02d}'),copyfp('Connector_PinHeader_2.54mm',f'PinHeader_1x{n:02d}_P2.54mm_Horizontal'),f'{jref} SERWIS 1x{n}',f'Pin header 1x{n}, 2.54 mm, right angle, Au',pp,'SERWIS',note='Edge B, x='+('10..43 mm (slot S1)' if jref=='J_SV1' else '63.5..96.5 mm (slot S2)')+'; pins ~6 mm beyond the edge. Numbering always from pin 1 (angled strip seen from the top has pin 1 at LARGER x).')
def write_tables():
 clean={r:{k:v for k,v in p.items() if k!='symbol'} for r,p in PARTS.items()}
 (P/'docs/parts.json').write_text(json.dumps(clean,indent=2,ensure_ascii=False),encoding='utf-8')
 with (P/'docs/BOM.csv').open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,['ref','source_ref','display','mpn','qty','footprint','on_board','zrodlo','url','note'],delimiter=';',extrasaction='ignore');w.writeheader();w.writerows(PARTS.values())
 libs={p['symbol'][1]:p['symbol'] for p in PARTS.values()};libs[PRJ+':PWR_FLAG']=symbol('power','PWR_FLAG')
 (P/'eda/libraries/P06.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor")'+''.join(dump([s[0],s[1].split(':')[1]]+s[2:]) for s in libs.values())+')',encoding='utf-8')
 (P/'eda/sym-lib-table').write_text('(sym_lib_table (lib (name "P06") (type "KiCad") (uri "${KIPRJMOD}/libraries/P06.kicad_sym") (options "") (descr "P06 symbols")))')
 flibs=sorted({p['footprint'].split(':')[0] for p in PARTS.values()})
 (P/'eda/fp-lib-table').write_text('(fp_lib_table '+''.join(f'(lib (name {q(l)}) (type "KiCad") (uri "${{KIPRJMOD}}/libraries/{l}.pretty") (options "") (descr "P06 local library"))' for l in flibs)+')')
if __name__=='__main__':write_tables();print(len(PARTS),'parts')
