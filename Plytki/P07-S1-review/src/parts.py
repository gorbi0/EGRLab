"""P07-S1 explicit circuit: DRIVE carrier for an off-stack IBT-2 / HW-39 module (2 x BTS7960B, 74HC244 buffer on the module).
Task: Plytki/Format-S1/zadania/ZADANIE-P07-S1.md (5.10.2026). Module facts: Plytki/P07-modul-BTS7960/POMIARY-MODULU.md.
Kept from v6.1 P07 (Rewizje/EGRLab-v6.1-rc1, hardware/netlist.csv): own Kelvin shunt + INA240A2 + MCP3201 (ITEST), window comparator
OC with latch (74HC74 cleared by OC, re-armed only by ARM_CLK while MOTOR_PERMIT is low), KPWR relay with diode + Zener clamp, Ioff
receivers, SAFE_N open collector on OC. New: 3.3 -> 5 V buffer 74AHCT125 with OE blocking (module buffer is always enabled), mapping
VNH5019 INA/INB/PWM -> RPWM/LPWM/R_EN/L_EN, IS diagnostics (divider + clamp + Schmitt) -> ENA_DIAG/ENB_DIAG, second flip-flop
NO_TRIP -> DRIVE_OK, separate PGND for the motor current (no motor current through P12), 10 R in the module logic ground.
Logic on 3V3_IO (same rail as P04), analog on local 3V3A_P07 / 5VA_P07 (as P06 R2), module VCC = 5V_MOD behind a PTC."""
from cadlib import *
import csv,shutil
FP=P/'eda/libraries/P07.pretty';FP.mkdir(parents=True,exist_ok=True);PARTS={}
G='GND';PG='PGND';IO='3V3_IO';A3='3V3A_P07';A5='5VA_P07';M5='5V_MOD';VM='VMOTOR'
NEW='nowe';REG='rejestr'
def copyfp(lib,name):
 src=K/'footprints'/(lib+'.pretty')/(name+'.kicad_mod');assert src.exists(),src
 dest=P/'eda/libraries'/(lib+'.pretty');dest.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest/src.name)
 return lib+':'+name
def custom(name,units):
 # rows: (pin,name,electrical type) left/right. Explicit function symbols (P06 R2 cadlib style), physical pin numbers of the package.
 s=f'(symbol "P07:{name}" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)'
 for u,(left,right) in enumerate(units,1):
  h=max(len(left),len(right))+1;half=12.7
  s+=f'(symbol "{name}_{u}_1" (rectangle (start {-half} {h*1.27}) (end {half} {-h*1.27}) (stroke (width .254) (type default)) (fill (type background))))'
  s+=f'(symbol "{name}_{u}_0"'
  for side,items in [(-1,left),(1,right)]:
   for j,(n,label,typ) in enumerate(items):
    s+=f'(pin {typ} line (at {side*(half+5.08)} {(h-2-j*2)*1.27} {0 if side==-1 else 180}) (length 5.08) (name {q(label)} (effects (font (size 1.0 1.0)))) (number "{n}" (effects (font (size 1 1)))))'
  s+=')'
 return parse(s+')')
# Wire pigtails (P06 R2 tail(): PTH solder joints, two anchor holes 12 mm from the row). 2.0 mm2 motor wires (decision 4.10): 2.4 / 4.5 mm.
def tail(name,n,pitch,drill,pad):
 pts=[(i+1,i*pitch,0,drill,pad) for i in range(n)]+[('',-3.5,-12,3.2,3.2),('',(n-1)*pitch+3.5,-12,3.2,3.2)]
 xmax=(n-1)*pitch
 s=f'(footprint {q(name)} (version 20240108) (generator "pcbnew") (layer "F.Cu") (attr through_hole)'
 for num,x,y,d,w in pts:
  s+=f'(pad "{num}" {"thru_hole" if num else "np_thru_hole"} {"rect" if num==1 else "circle"} (at {x} {y}) (size {w} {w}) (drill {d}) (layers "*.Cu" "*.Mask"))'
 s+=f'(fp_rect (start -5.5 -14) (end {xmax+5.5} {pad/2+.5}) (stroke (width .05) (type default)) (fill none) (layer "F.CrtYd"))'
 s+=f'(fp_text reference "REF**" (at {xmax/2} {pad/2+2}) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15)))))'
 (FP/(name+'.kicad_mod')).write_text(s);return 'P07:'+name
def shunt_fp():
 # As P06 R2 (local review 1.10): Vishay 30108 rev. 11-Dec-2023 sense pad length e = 1.70 mm (KiCad library 1.40).
 name='R_Shunt_Vishay_WSK2512_T1.19mm_SenseE1.70'
 t=(K/'footprints/Resistor_SMD.pretty/R_Shunt_Vishay_WSK2512_6332Metric_T1.19mm.kicad_mod').read_text()
 for a,b in (('(footprint "R_Shunt_Vishay_WSK2512_6332Metric_T1.19mm"',f'(footprint "{name}"'),
             ('(property "Value" "R_Shunt_Vishay_WSK2512_6332Metric_T1.19mm"',f'(property "Value" "{name}"'),
             ('(at -3.43 1.27)\n\t\t(size 1.4 0.76)','(at -3.28 1.27)\n\t\t(size 1.7 0.76)'),
             ('(at 3.43 -1.27)\n\t\t(size 1.4 0.76)','(at 3.28 -1.27)\n\t\t(size 1.7 0.76)'),
             ('(start -2.5 1.7)','(start -2.2 1.7)'),('(end 2.53 -1.7)','(end 2.2 -1.7)')):
  assert t.count(a)==1,a;t=t.replace(a,b)
 t=t.replace('(descr "','(descr "EGRLab P07 S1 (as P06 R2): sense pads e = 1.70 mm per Vishay 30108 rev. 11-Dec-2023 (library: 1.40). ',1)
 (FP/(name+'.kicad_mod')).write_text(t);return 'P07:'+name
R1206=copyfp('Resistor_SMD','R_1206_3216Metric_Pad1.30x1.75mm_HandSolder');C1206=copyfp('Capacitor_SMD','C_1206_3216Metric_Pad1.33x1.80mm_HandSolder')
R2512=copyfp('Resistor_SMD','R_2512_6332Metric_Pad1.40x3.35mm_HandSolder');PTC=copyfp('Fuse','Fuse_1206_3216Metric_Pad1.42x1.75mm_HandSolder')
SO8=copyfp('Package_SO','SOIC-8_3.9x4.9mm_P1.27mm');SO14=copyfp('Package_SO','SOIC-14_3.9x8.7mm_P1.27mm');DIP8=copyfp('Package_DIP','DIP-8_W7.62mm')
TO92=copyfp('Package_TO_SOT_THT','TO-92_Inline_Wide');SOT23=copyfp('Package_TO_SOT_SMD','SOT-23');SOT236=copyfp('Package_TO_SOT_SMD','SOT-23-6')
SOD123=copyfp('Diode_SMD','D_SOD-123');SMC=copyfp('Diode_SMD','D_SMC');CP8=copyfp('Capacitor_THT','CP_Radial_D8.0mm_P3.50mm')
RELAY=copyfp('Relay_THT','Relay_SPDT_Omron_G2RL-1-E')
IDC8=copyfp('Connector_IDC','IDC-Header_2x04_P2.54mm_Horizontal');IDC16=copyfp('Connector_IDC','IDC-Header_2x08_P2.54mm_Horizontal')
SHUNT_FP=shunt_fp()
def add(ref,src,sym,fp,value,mpn,pins,sheet,url='',note='',zrodlo=NEW,**extra):
 PARTS[ref]=dict(ref=ref,source_ref=src,symbol=sym,footprint=fp,display=value,value=value,mpn=mpn,pins={str(k):v for k,v in pins.items()},sheet=sheet,url=url,note=note,qty=1,on_board=True,zrodlo=zrodlo,**extra)
SR=symbol('Device','R');SC=symbol('Device','C');SCP=symbol('Device','C_Polarized');SD=symbol('Device','D');SZ=symbol('Device','D_Zener')
def code(value):return value.replace('.','K',1)[:-1] if value.endswith('K') and '.' in value else value
def res(r,src,val,ohms,a,b,sh,tol=.01,note=''):
 if tol==.001:add(r,src,SR,R1206,val,'RT1206BRD07'+code(val)+'L',{1:a,2:b},sh,note=note or 'Thin film 1206 0.1 % 25 ppm/K (Yageo RT, MPN to confirm).',ohms=ohms,tolerance=tol,tcr_ppm=25)
 else:add(r,src,SR,R1206,val,'RC1206FR-07'+code(val)+'L',{1:a,2:b},sh,note=note,ohms=ohms,tolerance=tol)
def cap(r,src,val,farad,a,b,sh,mpn=None,note='',volts=50):
 add(r,src,SC,C1206,val,mpn or ('SMD 1206 C0G 50V 5% ' if farad<1.1e-8 else 'SMD 1206 X7R 50V 10% ')+val,{1:a,2:b},sh,farads=farad,volts=volts,note=note)
# ---------------- sheet MOC: VMOTOR in, KPWR, module power, shunt, TEST port -------------------------------------------------------
add('J1','J_VMOTORB',symbol('Connector_Generic','Conn_01x02'),tail('PTH_VMOTOR',2,7.62,2.4,4.5),'VMOTOR / PTH','2 x 2.0 mm2 from P02 R4 J2 (GMSTB plug)',{1:VM,2:PG},'MOC',note='PTH solder joints + tie anchor 12 mm; 2.0 mm2 (decision 4.10). P02 R4 J2.1 VMOTOR (behind F1 5 A), J2.2 GND. See docs/WIAZKA-MODUL.md.')
add('D1','D2',SZ,SMC,'SMCJ18A','SMCJ18A (Littelfuse, 1.5 kW, VRWM 18 V)',{1:VM,2:PG},'MOC',note='TVS at VMOTOR as v6.1 D2: VRWM 18 V >= 16.8 V (4S full), VC ~29 V << 40 V BTS7960 and relay contacts.',vrwm=18.0)
add('C1','C_BULK',SCP,CP8,'220u / 35V','EEU-FR1V221 (Panasonic FR, D8 x 11.5 mm, low ESR; MPN to confirm)',{1:VM,2:PG},'MOC',farads=220e-6,volts=35,note='Local bulk at the input (v6.1: 1000u/50V). Standing, 11.5 mm + 2 mm <= 16.5 mm.')
cap('C2','C_MOTOR_MF','1u',1e-6,VM,PG,'MOC')
cap('C3','C_MOTOR_HF','100n',1e-7,VM,PG,'MOC')
res('R1','R_BLEED','10K',10000,VM,PG,'MOC',note='Bleed of C1 (v6.1 2.2k 0.5W): 28 mW at 16.8 V; tau 2.2 s.')
relay=custom('G2RL_1_E_DC12',[([('A1','COIL+','passive'),('A2','COIL-','passive')],[('11','COM','passive'),('14','NO','passive'),('12','NC','passive')])])
add('K1','KPWR',relay,RELAY,'G2RL-1-E DC12','G2RL-1-E DC12 (Omron, SPDT 16 A, coil 12 V 400 mW, h 15.7 mm; data to confirm)',{'A1':VM,'A2':'KPWR_COIL_LOW','11':VM,'14':'MOD_BP','12':'NC'},'MOC',
    note='KPWR: COM on VMOTOR, NO to module B+. Coil from VMOTOR (12.0-16.8 V = 100-140 % of 12 V); confirm maximum coil voltage >= 17 V at 50 C in the data sheet. Contacts switch without load: EN drops first (ns), relay opens later (ms); closes onto a precharged module capacitor (R4).',coil_ohm=360,coil_v=12)
add('Q1','ADD_KPWR_DRV',symbol('Transistor_BJT','MMBT3904'),SOT23,'MMBT3904','MMBT3904 (Nexperia/onsemi, SOT-23, 40 V 200 mA)',{1:'KPWR_B',2:PG,3:'KPWR_COIL_LOW'},'MOC',note='Low-side coil switch (v6.1: TBD62083 channel). Emitter on PGND: the coil current does not return through P12.',vceo=40,ic_max=0.2)
res('R2','ADD_KPWR_RB','1K',1000,'LOCAL_PERMIT','KPWR_B','MOC')
res('R3','ADD_KPWR_PD','100K',100000,'KPWR_B',PG,'MOC')
add('D2','D11',SD,SOD123,'1N4148W','1N4148W (SOD-123, 100 V)',{1:'KPWR_CLAMP',2:'KPWR_COIL_LOW'},'MOC',note='Coil clamp diode (anode at coil low end) in series with Zener D3 to VMOTOR: fast release (v6.1 D11/D12).')
add('D3','D12',SZ,SOD123,'BZT52C15','BZT52C15 (Zener 15 V 0.5 W, SOD-123)',{1:'KPWR_CLAMP',2:VM},'MOC',note='Clamp = VMOTOR + 15 V + 0.7 V <= 32.5 V < 40 V VCEO of Q1 (v6.1: 18 V Zener with 60 V transistor array).',vz=15.0)
add('R4','ADD_PRECHARGE',SR,R2512,'1K / 1W','RC2512FK-071KL (Yageo 2512 1 W, MPN to confirm)',{1:VM,2:'MOD_BP'},'MOC',ohms=1000,tolerance=.01,power_w=1.0,
    note='Disputed: precharge of the module 330 uF across the KPWR contacts (no inrush weld). Fault with module shorted: 0.28 W; motor current with KPWR open <= 17 mA.')
res('R5','ADD_MODBP_BLEED','10K',10000,'MOD_BP',PG,'MOC',note='Bleed of the module side; with R4: MOD_BP = 91 % of VMOTOR while KPWR is open (visible on J_SV1.10).')
cap('C4','ADD_MODBP_HF','100n',1e-7,'MOD_BP',PG,'MOC')
add('J2','ADD_MOD_PWR',symbol('Connector_Generic','Conn_01x02'),tail('PTH_MODPWR',2,7.62,2.4,4.5),'MOD B+/B- / PTH','2 x 2.0 mm2 to module B+ / B-',{1:'MOD_BP',2:PG},'MOC',note='To the IBT-2 screw terminals B+ / B-. PTH + anchor.')
add('J3','ADD_MOD_OUT',symbol('Connector_Generic','Conn_01x02'),tail('PTH_MODOUT',2,7.62,2.4,4.5),'MOD M+/M- / PTH','2 x 2.0 mm2 from module M+ / M-',{1:'MOD_MP',2:'T_EGR_P3'},'MOC',note='From the IBT-2 terminals M+ / M-. M- passes through to J4.2.')
add('RSH1','RSH_T',symbol('Device','R_Shunt','R_Shunt_2512_Kelvin'),SHUNT_FP,'5m / 1% / 2512 Kelvin','WSK25125L000FEA (Vishay WSK2512, 5 mOhm 1 %, 1 W at 70 C) - as P06 R2',{1:'MOD_MP',2:'K_PLUS',3:'K_MINUS',4:'T_EGR_P1'},'MOC',
    note='In the motor line M+ -> T_EGR_P1 (task). Pads 1/4 force, 2/3 sense. 6 A: 0.18 W; 10 A: 0.5 W.',ohms=.005,tolerance=.01,power_w=1.0)
add('J4','J_TMOTORA',symbol('Connector_Generic','Conn_01x02'),tail('PTH_TEST',2,7.62,2.4,4.5),'TEST / PTH','2 x 2.0 mm2 to P11 port TEST (valve pins 1 / 3)',{1:'T_EGR_P1',2:'T_EGR_P3'},'MOC',note='At the x = 0 edge (task). Port TEST on the panel (P11-4: motor current by wires straight to the port).')
# ---------------- sheet ANA: Kelvin, INA240, reference, ITEST divider, OC window ---------------------------------------------------
res('R6','RC1','10R',10,'K_PLUS','INA_PLUS','ANA',tol=.001)
res('R7','RC2','10R',10,'K_MINUS','INA_MINUS','ANA',tol=.001)
ina=custom('INA240A2_D_SOIC',[([(8,'IN+','input'),(1,'IN-','input'),(6,'VS','power_in'),(7,'REF1','input'),(3,'REF2','input')],[(5,'OUT','output'),(2,'GND','power_in'),(4,'NC','no_connect')])])
add('U1','U2',ina,SO8,'INA240A2','INA240A2EDRQ1',{1:'INA_MINUS',2:G,3:'REF_BUF',4:'NC',5:'I_T_OUT',6:A5,7:'REF_BUF',8:'INA_PLUS'},'ANA','https://www.ti.com/lit/ds/symlink/ina240.pdf','Owned (register: P07 U2). 50 V/V, CM -4..80 V, PWM rejection; REF1 = REF2 = 2.5 V -> 2.5 V + 0.25 V/A.',zrodlo=REG,gain=50)
ref=custom('MCP1525_TO92',[([(3,'VIN','power_in'),(1,'GND','power_in')],[(2,'VOUT','power_out')])])
add('U2','U_REF',ref,TO92,'MCP1525-I/TO','MCP1525-I/TO',{1:G,2:'REF25',3:A3},'ANA','https://ww1.microchip.com/downloads/en/DeviceDoc/21653c.pdf','2.5 V +-1 %. TO92: 1 GND, 2 OUT, 3 IN.',vref=2.5,vref_tol=.01)
cap('C5','C_REF','4.7u',4.7e-6,'REF25',G,'ANA',mpn='SMD 1206 X7R 25V 10% 4.7u',volts=25)
add('D4','ADD_REF_DISCHARGE',custom('BAT54_SOT23',[([(1,'A','passive')],[(3,'K','passive'),(2,'NC','no_connect')])]),SOT23,'BAT54','BAT54 (SOT-23, single)',{1:'REF25',3:A3,2:'NC'},'ANA',note='Discharge of C5 into 3V3A on power removal (P06 R2 D2).')
op=custom('MCP6022_SOIC',[([(3,'+INA','input'),(2,'-INA','input'),(5,'+INB','input'),(6,'-INB','input'),(8,'VDD','power_in')],[(1,'OUTA','output'),(7,'OUTB','output'),(4,'VSS','power_in')])])
add('U3','U_BUF',op,SO8,'MCP6022-I/SN','MCP6022-I/SN',{1:'ADC_BUF',2:'ADC_BUF',3:'I_DIV',4:G,5:'REF25',6:'REF_BUF',7:'REF_BUF',8:A3},'ANA','https://ww1.microchip.com/downloads/en/DeviceDoc/20001685E.pdf','A: ADC driver (follower of I_DIV); B: REF_BUF follower for INA240 REF and OC thresholds. 3V3A rail.')
res('R8','R_DIV_H','5.11K',5110,'I_T_OUT','I_DIV','ANA',tol=.001)
res('R9','R_DIV_L','5.11K',5110,'I_DIV',G,'ANA',tol=.001)
cap('C7','C_DIV','100n',1e-7,'I_DIV',G,'ANA',mpn='SMD 1206 C0G 50V 5% 100n (e.g. Murata GRM31C5C1H104JA01; MPN to confirm)',note='Disputed: anti-alias for 2 kS/s: tau = 2.555k x 100n = 0.26 ms (623 Hz). v6.1: 4.7n (4.7 us); P06 R2: 470n (133 Hz).')
res('R10','R_IFILT','1K',1000,'I_T_OUT','I_FILT','ANA')
cap('C8','C_IFILT','1n',1e-9,'I_FILT',G,'ANA')
add('U4','U_OCREF',op,SO8,'MCP6022-I/SN','MCP6022-I/SN',{1:'OC_HIGH',2:'OC_FB',3:'REF_BUF',4:G,5:G,6:'OC_UNUSED',7:'OC_UNUSED',8:A5},'ANA','https://ww1.microchip.com/downloads/en/DeviceDoc/20001685E.pdf','A: OC_HIGH = REF_BUF x (1 + R11/R12); B unused (follower of GND). 5VA rail (output 4.5 V).')
res('R11','R_OC_FB','8.06K',8060,'OC_HIGH','OC_FB','ANA',tol=.001)
res('R12','R_OC_G','10K',10000,'OC_FB',G,'ANA',tol=.001)
res('R13','R_OC_L_TOP','40.2K',40200,'REF_BUF','OC_LOW','ANA',tol=.001)
res('R14','R_OC_L_BOT','10K',10000,'OC_LOW',G,'ANA',tol=.001)
cap('C10','C_OC_LOW','10n',1e-8,'OC_LOW',G,'ANA')
cmp_=custom('TLV1702_SOIC',[([(3,'+IN1','input'),(2,'-IN1','input'),(5,'+IN2','input'),(6,'-IN2','input'),(8,'V+','power_in')],[(1,'OUT1','open_collector'),(7,'OUT2','open_collector'),(4,'V-','power_in')])])
add('U5','U4',cmp_,SO8,'TLV1702AIDR','TLV1702AIDR (TI, SOIC-8, open collector)',{1:'OC_LOCAL_N',2:'OC_LOW',3:'I_FILT',4:G,5:'OC_HIGH',6:'I_FILT',7:'OC_LOCAL_N',8:A5},'ANA','https://www.ti.com/lit/ds/symlink/tlv1702.pdf','Window: OUT1 low if I_FILT < OC_LOW (negative OC), OUT2 low if I_FILT > OC_HIGH (positive OC). v6.1 VSSOP -> SOIC (S1 9).')
res('R15','R_OC_PULL','10K',10000,'OC_LOCAL_N',IO,'ANA')
# ---------------- sheet DIG: MCP3201 and SPI buffer (P06 R2 pattern) --------------------------------------------------------------
adc=custom('MCP3201_B_P',[([(1,'VREF','power_in'),(2,'IN+','input'),(3,'IN-','input'),(4,'VSS','power_in')],[(8,'VDD','power_in'),(7,'CLK','input'),(6,'DOUT','tri_state'),(5,'CS_N','input')])])
add('U6','U_ADC',adc,DIP8,'MCP3201-BI/P','MCP3201-BI/P',{1:'REF25',2:'ADC_AIN',3:G,4:G,5:'CS_LOCAL_N',6:'ADC_DOUT',7:'CLK_LOCAL',8:A3},'DIG','https://ww1.microchip.com/downloads/en/DeviceDoc/21290F.pdf','Owned (register: P07 U_ADC), DIP8 top side.',zrodlo=REG)
res('R16','R_ADC','47R',47,'ADC_BUF','ADC_AIN','DIG')
cap('C11','C_ADC_IN','470p',4.7e-10,'ADC_AIN',G,'DIG')
lvc=custom('74LVC125A_SO14',[([(2,'1A','input'),(1,'1OE_N','input'),(5,'2A','input'),(4,'2OE_N','input'),(9,'3A','input'),(10,'3OE_N','input'),(12,'4A','input'),(13,'4OE_N','input'),(14,'VCC','power_in')],
                             [(3,'1Y','tri_state'),(6,'2Y','tri_state'),(8,'3Y','tri_state'),(11,'4Y','tri_state'),(7,'GND','power_in')])])
add('U7','U_SPI',lvc,SO14,'74LVC125AD','74LVC125AD,118 (Nexperia, Ioff)',{1:G,2:'CS_ITEST_N',3:'CS_LOCAL_N',4:G,5:'ADC_SCLK',6:'CLK_LOCAL',7:G,8:'DOUT_TX',9:'ADC_DOUT',10:'CS_LOCAL_N',11:'SUP5_N',12:'SUP5_RAW',13:G,14:A3},'DIG','https://assets.nexperia.com/documents/data-sheet/74LVC125A.pdf',
    'Owned (register zapas). 1: CS, 2: SCLK, 3: DOUT tri-state (OE = CS_LOCAL_N), 4: SUP5 open drain (5 V pull-up) -> 3.3 V; 3V3A off -> Ioff, R23 holds SUP5_N low.',zrodlo=REG)
res('R17','R_EXT_CS_ITEST_N','100K',100000,A3,'CS_ITEST_N','DIG')
res('R18','R_CS','10K',10000,A3,'CS_LOCAL_N','DIG')
res('R19','ADD_CLK_PD','10K',10000,'CLK_LOCAL',G,'DIG')
res('R20','ADD_CLK_EXT_PD','100K',100000,'ADC_SCLK',G,'DIG')
res('R21','R_MISO','47K',47000,A3,'ADC_DOUT','DIG')
res('R22','ADD_DOUT_SER','47R',47,'DOUT_TX','ADC_DOUTA','DIG')
res('R23','ADD_SUP5_PD','10K',10000,'SUP5_N',G,'DIG')
# ---------------- sheet LOGIKA: supervisors, receivers, gates, latch, SAFE_N --------------------------------------------------------
sup=custom('MCP120_D_TO',[([(2,'VDD','power_in')],[(1,'RESET_N','open_collector'),(3,'VSS','power_in')])])
add('U8','U_SUP3',sup,TO92,'MCP120-300DI/TO','MCP120-300DI/TO',{1:'SUP3_N',2:A3,3:G},'LOGIKA','https://ww1.microchip.com/downloads/en/DeviceDoc/11184d.pdf','D bondout: RESET = 1, VDD = 2, GND = 3. Open drain. Watches 3V3A (REF, OC thresholds).',vth=(2.85,3.0))
res('R24','R_U_SUP3','10K',10000,A3,'SUP3_N','LOGIKA')
add('U9','U_SUP5',sup,TO92,'MCP120-450DI/TO','MCP120-450DI/TO',{1:'SUP5_RAW',2:A5,3:G},'LOGIKA','https://ww1.microchip.com/downloads/en/DeviceDoc/11184d.pdf','Watches 5VA (INA240, OC comparator).',vth=(4.25,4.5))
res('R25','R_SUP5','10K',10000,A5,'SUP5_RAW','LOGIKA')
add('U10','U_RX1',lvc,SO14,'74LVC125AD','74LVC125AD,118 (Nexperia, Ioff)',{1:G,2:'MOTOR_INA',3:'INA_P07',4:G,5:'MOTOR_INB',6:'INB_P07',7:G,8:'PERMIT_P07',9:'MOTOR_PERMIT',10:G,11:'PWM_P07',12:'PWM_OUT',13:G,14:IO},'LOGIKA','https://assets.nexperia.com/documents/data-sheet/74LVC125A.pdf',
    'Owned (register zapas). Ioff receivers: MOTOR_INA/INB come from the P03 domain (P03 may run from USB alone).',zrodlo=REG)
for i,n in enumerate(['MOTOR_INA','MOTOR_INB','MOTOR_PERMIT','PWM_OUT','ARM_CLK'],26):res(f'R{i}','R_PD_'+n,'100K',100000,n,G,'LOGIKA',note='Input pull-down at J_BP: open tape = L.')
inv=custom('74LVC14A_SO14',[([(1,'1A','input'),(3,'2A','input'),(5,'3A','input'),(9,'4A','input'),(11,'5A','input'),(13,'6A','input'),(14,'VCC','power_in')],
                            [(2,'1Y','output'),(4,'2Y','output'),(6,'3Y','output'),(8,'4Y','output'),(10,'5Y','output'),(12,'6Y','output'),(7,'GND','power_in')])])
add('U11','U_INV',inv,SO14,'74LVC14AD','74LVC14AD,118 (Nexperia, Schmitt, Ioff)',{1:'OC_LOCAL_N',2:'OC_FAULT',3:'PERMIT_P07',4:'PERMIT_N',5:'SAFE_SENSE',6:'SAFE_BAD',7:G,8:'SAFE_OK',9:'SAFE_BAD',10:'DRV_OFF',11:'DRIVE_EN',12:'NC',13:G,14:IO},'LOGIKA','https://assets.nexperia.com/documents/data-sheet/74LVC14A.pdf',
    'Schmitt inputs for SAFE_N (RC edge ~10 us on P04) and OC_LOCAL_N (pull-up edge). v6.1 SN74HC14N -> LVC14A (Ioff, 5 V tolerant).')
and_=custom('74HC08_SO14',[([(1,'1A','input'),(2,'1B','input'),(4,'2A','input'),(5,'2B','input'),(9,'3A','input'),(10,'3B','input'),(12,'4A','input'),(13,'4B','input'),(14,'VCC','power_in')],
                           [(3,'1Y','output'),(6,'2Y','output'),(8,'3Y','output'),(11,'4Y','output'),(7,'GND','power_in')])])
HC08='SN74HC08DR (TI, SOIC-14)'
add('U12','U_GATE',and_,SO14,'SN74HC08D',HC08,{1:'SUP3_N',2:'SUP5_N',3:'RAILS_OK',4:'RAILS_OK',5:'OC_LOCAL_N',6:'LOCAL_CLEAR_N',7:G,8:'PERMIT_ARMED',9:'PERMIT_P07',10:'OC_GOOD',11:'LOCAL_PERMIT',12:'PERMIT_ARMED',13:'RAILS_OK',14:IO},'LOGIKA','https://www.ti.com/lit/ds/symlink/sn74hc08.pdf','RAILS_OK, LOCAL_CLEAR_N, PERMIT_ARMED, LOCAL_PERMIT (v6.1 U_GATE / U_READY).')
add('U13','U_PWM',and_,SO14,'SN74HC08D',HC08,{1:'LOCAL_PERMIT',2:'SAFE_OK',3:'DRIVE_EN',4:'RAILS_OK',5:'NO_TRIP',6:'DRIVE_OK_L',7:G,8:'PWM_EN',9:'PWM_P07',10:'DRIVE_EN',11:'RPWM_L',12:'PWM_EN',13:'INA_P07',14:IO},'LOGIKA','https://www.ti.com/lit/ds/symlink/sn74hc08.pdf','DRIVE_EN, DRIVE_OK, PWM_EN, RPWM = PWM_EN & INA.')
add('U14','ADD_U_DIR',and_,SO14,'SN74HC08D',HC08,{1:'PWM_EN',2:'INB_P07',3:'LPWM_L',4:G,5:G,6:'NC',7:G,8:'NC',9:G,10:G,11:'NC',12:G,13:G,14:IO},'LOGIKA','https://www.ti.com/lit/ds/symlink/sn74hc08.pdf','LPWM = PWM_EN & INB; gates 2-4 unused, inputs on GND.')
ff=custom('74HC74_SO14',[([(2,'1D','input'),(3,'1CLK','input'),(4,'1PRE_N','input'),(1,'1CLR_N','input'),(12,'2D','input'),(11,'2CLK','input'),(10,'2PRE_N','input'),(13,'2CLR_N','input'),(14,'VCC','power_in')],
                         [(5,'1Q','output'),(6,'1Q_N','output'),(9,'2Q','output'),(8,'2Q_N','output'),(7,'GND','power_in')])])
add('U15','U_OC_LATCH',ff,SO14,'SN74HC74D','SN74HC74DR (TI, SOIC-14)',{1:'LOCAL_CLEAR_N',2:'PERMIT_N',3:'ARM_CLK',4:IO,5:'OC_GOOD',6:'NC',7:G,8:'NC',9:'NO_TRIP',10:'RAILS_OK',11:'ARM_CLK',12:IO,13:'OC_LOCAL_N',14:IO},'LOGIKA','https://www.ti.com/lit/ds/symlink/sn74hc74.pdf',
    'FF1 (v6.1): OC_GOOD cleared by OC or rails, set only by ARM_CLK while MOTOR_PERMIT = L. FF2 (new): NO_TRIP preset while rails are not OK (power-up = no trip), cleared by OC, set again by ARM_CLK -> DRIVE_OK.')
res('R31','ADD_SAFE_SER','1K',1000,'SAFE_N','SAFE_SENSE','LOGIKA',note='Series into the Schmitt input; no pull on SAFE_N (P04 R4 is the only pull-up).')
add('Q2','Q_OC',symbol('Transistor_BJT','MMBT3904'),SOT23,'MMBT3904','MMBT3904 (SOT-23)',{1:'OC_B',2:G,3:'SAFE_N'},'LOGIKA',note='Open collector on the common SAFE_N node during OC (v6.1 Q_OC 2N5551).')
res('R33','R_QOC_B','10K',10000,'OC_FAULT','OC_B','LOGIKA')
res('R34','R_QOC_PD','100K',100000,'OC_B',G,'LOGIKA')
res('R32','ADD_DRIVE_OK_SER','100R',100,'DRIVE_OK_L','DRIVE_OK','LOGIKA',note='P04 R3: DRIVE_OK -> U10A (LVC125), 10k R20 to GND.')
# ---------------- sheet MODUL: 3.3 -> 5 V buffer, harness, IS diagnostics ------------------------------------------------------------
add('F1','ADD_MOD_VCC_PTC',symbol('Device','Polyfuse'),PTC,'PTC 0.12A','MF-NSMF012-2 (Bourns 1206, Ihold 0.12 A, Itrip 0.29 A; MPN to confirm)',{1:'5V_SYS',2:M5},'MODUL',note='Module VCC (74HC244 on the module) and U16: a shorted harness does not pull 5V_SYS down.',ihold=.12)
ahct=custom('74AHCT125_SO14',[([(2,'1A','input'),(1,'1OE_N','input'),(5,'2A','input'),(4,'2OE_N','input'),(9,'3A','input'),(10,'3OE_N','input'),(12,'4A','input'),(13,'4OE_N','input'),(14,'VCC','power_in')],
                              [(3,'1Y','tri_state'),(6,'2Y','tri_state'),(8,'3Y','tri_state'),(11,'4Y','tri_state'),(7,'GND','power_in')])])
add('U16','ADD_LEVEL',ahct,SO14,'74AHCT125D','74AHCT125D,118 (Nexperia, SOIC-14; TTL inputs, VCC 5 V)',{1:'DRV_OFF',2:'RPWM_L',3:'RPWM_D',4:'DRV_OFF',5:'LPWM_L',6:'LPWM_D',7:G,8:'REN_D',9:'DRIVE_EN',10:'DRV_OFF',11:'LEN_D',12:'DRIVE_EN',13:'DRV_OFF',14:M5},'MODUL','https://assets.nexperia.com/documents/data-sheet/74AHCT125.pdf',
    '3.3 -> 5 V: module 74HC244 at 5 V needs VIH >= 3.5 V. OE_N = DRV_OFF: outputs Z unless DRIVE_EN (second block after the AND gates; module 30k pull-downs give L).')
res('R35','ADD_OE_PU','100K',100000,M5,'DRV_OFF','MODUL',note='3V3_IO domain dead -> U11 Ioff -> DRV_OFF high -> U16 outputs Z.')
for i,n in enumerate(['RPWM_L','LPWM_L','DRIVE_EN'],36):res(f'R{i}','ADD_PD_'+n,'100K',100000,n,G,'MODUL')
for i,(a,b) in enumerate([('RPWM_D','RPWM'),('LPWM_D','LPWM'),('REN_D','R_EN'),('LEN_D','L_EN')],39):res(f'R{i}','ADD_SER_'+b,'100R',100,a,b,'MODUL',note='Series at the source: ringing on the 8-wire harness, ESD.')
add('J5','ADD_J_MOD',symbol('Connector_Generic','Conn_02x04_Odd_Even'),IDC8,'J_MOD / IDC 2x4','IDC header 2x4 2.54 mm angled shrouded, Au',{1:'RPWM',2:'LPWM',3:'R_EN',4:'L_EN',5:'R_IS',6:'L_IS',7:M5,8:'MOD_GND'},'MODUL',
    note='8-wire control harness to the IBT-2 2x4 header (ribbon 1:1). Pin order of the module header to confirm (POMIARY B4) - docs/WIAZKA-MODUL.md.')
res('R43','ADD_MOD_GND','10R',10,G,'MOD_GND','MODUL',note='Module logic ground: if the module ties GND to B- internally, the loop current through the harness is limited (dV on the VMOTOR return / 10 ohm); acts as a fuse if B- opens.')
for i,(isn,div,rr) in enumerate([('R_IS','ISR_DIV',44),('L_IS','ISL_DIV',46)]):
 res(f'R{rr}','ADD_'+isn+'_TOP','100K',100000,isn,div,'MODUL',note='IS divider: loads the module 10k by 4.8 %.')
 res(f'R{rr+1}','ADD_'+isn+'_BOT','100K',100000,div,G,'MODUL')
 cap(f'C{14+i}','ADD_'+isn+'_C','10n',1e-8,div,G,'MODUL',note='tau = 50k x 10n = 0.5 ms: averages PWM.')
 add(f'D{5+i}','ADD_'+isn+'_CLAMP',custom('BAT54S_SOT23',[([(1,'A1','passive')],[(3,'K1A2','passive'),(2,'K2','passive')])]),SOT23,'BAT54S','BAT54S (SOT-23, series pair)',{1:G,3:div,2:IO},'MODUL',note='Clamp of the divided IS to GND-0.3 / 3V3_IO+0.3 V (IS up to VS = 16.8 V).')
sch=custom('74LVC2G17_SOT23_6',[([(1,'1A','input'),(3,'2A','input'),(5,'VCC','power_in')],[(6,'1Y','output'),(4,'2Y','output'),(2,'GND','power_in')])])
add('U17','ADD_IS_SCHMITT',sch,SOT236,'74LVC2G17','74LVC2G17GV,125 (Nexperia SC-74 / SOT-23-6; DBV pinout to confirm)',{1:'ISR_DIV',2:G,3:'ISL_DIV',4:'ENB_L',5:IO,6:'ENA_L'},'MODUL','https://assets.nexperia.com/documents/data-sheet/74LVC2G17.pdf','Schmitt buffers of the divided IS -> ENA_DIAG / ENB_DIAG (H = half-bridge current >~2-3 A or IS fault level).')
res('R48','ADD_ENA_SER','100R',100,'ENA_L','ENA_DIAG','MODUL')
res('R49','ADD_ENB_SER','100R',100,'ENB_L','ENB_DIAG','MODUL')
# ---------------- root sheet P07: local supplies ---------------------------------------------------------------------------------
res('R50','R_AF','10R',10,'5V_SYS',A5,'P07',note='5VA filter (v6.1 R_AF 1R 0.5W; load here ~6 mA -> 60 mV).')
cap('C16','C_AF','10u',1e-5,A5,G,'P07',mpn='SMD 1206 X7R 16V 10% 10u',volts=16)
ldo=custom('MCP1702_TO92',[([(2,'VIN','power_in'),(1,'GND','power_in')],[(3,'VOUT','power_out')])])
add('U18','U_LDO',ldo,TO92,'MCP1702-3302E/TO','MCP1702-3302E/TO',{1:G,2:A5,3:A3},'P07','https://ww1.microchip.com/downloads/en/DeviceDoc/22008E.pdf','3V3A_P07: REF, MCP6022 (U3), MCP3201, SPI buffer, SUP3.')
cap('C18','C_LDO_IN','1u',1e-6,A5,G,'P07')
cap('C19','C_LDO_OUT','4.7u',4.7e-6,A3,G,'P07',mpn='SMD 1206 X7R 25V 10% 4.7u',volts=25)
add('D7','ADD_LDO_DISCHARGE',SD,SOD123,'B5819W','B5819W (Schottky 1 A 40 V, SOD-123)',{1:A5,2:A3},'P07',note='Anode 3V3A, cathode 5VA: output capacitor discharge on supply removal (P06 R2 D1).')
cap('C12','ADD_5VMOD_BULK','10u',1e-5,M5,G,'P07',mpn='SMD 1206 X7R 16V 10% 10u',volts=16)
cap('C21','ADD_3V3IO_BULK','10u',1e-5,IO,G,'P07',mpn='SMD 1206 X7R 16V 10% 10u',volts=16)
DEC=[('U1',A5),('U3',A3),('U4',A5),('U5',A5),('U6',A3),('U7',A3),('U8',A3),('U9',A5),('U10',IO),('U11',IO),('U12',IO),('U13',IO),('U14',IO),('U15',IO),('U16',M5),('U17',IO),('U2',A3)]
for i,(u,rail) in enumerate(DEC,22):cap(f'C{i}','DEC_'+u,'100n',1e-7,rail,G,'P07',note='Decoupling at '+u+'.')
cap('C6','C_REF_HF','100n',1e-7,'REF25',G,'ANA',note='At VREF of U6 (MCP3201).')
cap('C13','ADD_5VMOD_HF','100n',1e-7,M5,G,'P07',note='At J5.7 (module VCC).')
cap('C17','ADD_5VA_HF','100n',1e-7,A5,G,'P07')
cap('C20','ADD_3V3IO_HF','100n',1e-7,IO,G,'P07')
# ---------------- sheet ZLACZA: edge A ---------------------------------------------------------------------------------------------
# J_BP1 (slot S2, board x = 26.5 / stack x = 80.0): ITEST SPI on 2/4 as J_BP2 of P03 R6 / P05 R3 / P06 R2 J_BP; DIR and diagnostics to P03.
# J_BP2 (slot S3, board x = 80.0 / stack x = 133.5): DRIVE to P04 R3 on the same pins as P04 R3 J_BP2 (2/4/6/8/16), power 10/12/14.
JBP1={2:'ADC_SCLK',4:'ADC_DOUTA',6:'CS_ITEST_N',8:'MOTOR_INA',10:'MOTOR_INB',12:'ENA_DIAG',14:'ENB_DIAG',16:G}
JBP2={2:'MOTOR_PERMIT',4:'PWM_OUT',6:'ARM_CLK',8:'DRIVE_OK',10:'5V_SYS',12:'5V_SYS',14:IO,16:'SAFE_N'}
for j in (JBP1,JBP2):j.update({i:G for i in range(1,16,2)})
add('J_BP1','J_ITESTB+J_DIRB',symbol('Connector_Generic','Conn_02x08_Odd_Even'),IDC16,'J_BP1 / IDC 2x8','IDC header 2x8 2.54mm angled shrouded, Au',JBP1,'ZLACZA',note='Edge A, slot S2 (board x = 26.5 mm, stack x = 80.0 mm), pin 1 towards smaller x. Odd pins GND, 16 GND reserve. Partner: P03 R6 (J_BP1 / J_BP2) through P12.')
add('J_BP2','J_DRIVEB+J_LV07B',symbol('Connector_Generic','Conn_02x08_Odd_Even'),IDC16,'J_BP2 / IDC 2x8','IDC header 2x8 2.54mm angled shrouded, Au',JBP2,'ZLACZA',note='Edge A, slot S3 (board x = 80.0 mm, stack x = 133.5 mm). 2/4/6/8/16 = P04 R3 J_BP2 pins; 5V_SYS x2, 3V3_IO x1 (S1 5).')
# ---------------- sheet SERWIS: edge B ---------------------------------------------------------------------------------------------
SV1=[(None,),('I_T_OUT',10000,'wyjscie INA240: 2,500 V przy 0 A, 0,25 V/A'),('ADC_AIN',10000,'wejscie MCP3201: 1,250 V przy 0 A, 0,125 V/A'),('REF_BUF',10000,'bufor U3B: REF INA240 i progi OC'),
 ('REF25',10000,'MCP1525: 2,475-2,525 V'),('OC_HIGH',10000,'prog OC dodatni: ok. 4,51 V (+8 A)'),('OC_LOW',10000,'prog OC ujemny: ok. 0,50 V (-8 A)'),(None,),
 (VM,4700,'VMOTOR z P02 (12,0-16,8 V)'),('MOD_BP',4700,'B+ modulu: = VMOTOR przy zamknietym KPWR, ok. 91 % przy otwartym (R4/R5)'),('KPWR_COIL_LOW',4700,'dol cewki KPWR: ok. 0,1 V = zalaczony, = VMOTOR = wylaczony'),('T_EGR_P1',4700,'zacisk zaworu pin 1 (za bocznikiem)'),(None,)]
SV2=[(None,),('5V_SYS',1000,'5V_SYS z J_BP2'),(A5,1000,'5VA_P07 za R50'),(A3,1000,'3V3A_P07 z U18'),(IO,1000,'3V3_IO z J_BP2 (logika)'),(M5,1000,'5V_MOD za F1 (VCC modulu)'),(None,),
 ('RAILS_OK',1000,'SUP3_N & SUP5_N'),('OC_LOCAL_N',1000,'wyjscie OC (L = przetezenie); zwarcie kolka do GND = wymuszone OC'),('OC_GOOD',1000,'zatrzask OC (H = uzbrojony)'),('NO_TRIP',1000,'pamiec zadzialania OC (L = bylo OC od ostatniego ARM)'),('DRIVE_EN',1000,'zezwolenie mostka (R_EN / L_EN)'),(None,)]
SERVICE={};nr=52
for jref,rows,src in [('J_SV1',SV1,'SERVICE_S2'),('J_SV2',SV2,'SERVICE_S3')]:
 n=len(rows);pp={}
 for k,row in enumerate(rows,1):
  if row[0] is None:pp[k]=G;continue
  net,ohm,why=row;r='R'+str(nr);nr+=1;pp[k]='SRV_'+net;SERVICE[net]=(jref,k,r,ohm,why)
  res(r,'ADDED_'+src,{1000:'1K',4700:'4K7',10000:'10K'}[ohm],ohm,net,'SRV_'+net,'SERWIS',note='Service pin series resistor at the node (S1 6). SMD, may sit on the bottom side.')
 add(jref,src,symbol('Connector_Generic',f'Conn_01x{n:02d}'),copyfp('Connector_PinHeader_2.54mm',f'PinHeader_1x{n:02d}_P2.54mm_Horizontal'),f'{jref} SERWIS 1x{n}',f'Pin header 1x{n}, 2.54 mm, right angle, Au',pp,'SERWIS',
     note='Edge B, '+('slot S2 (board x = 10..43 mm)' if jref=='J_SV1' else 'slot S3 (board x = 63.5..96.5 mm)')+'; pins ~6 mm beyond the edge. Angled strip seen from the top: pin 1 at the LARGER x (P09 R2 note).')
def write_tables():
 clean={r:{k:v for k,v in p.items() if k!='symbol'} for r,p in PARTS.items()}
 (P/'docs/parts.json').write_text(json.dumps(clean,indent=2,ensure_ascii=False),encoding='utf-8')
 with (P/'docs/BOM.csv').open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,['ref','source_ref','display','mpn','qty','footprint','zrodlo','url','note'],delimiter=';',extrasaction='ignore');w.writeheader();w.writerows(sorted(PARTS.values(),key=lambda p:(re.sub(r'\d','',p['ref']),int(re.sub(r'\D','',p['ref']) or 0))))
 libs={p['symbol'][1]:p['symbol'] for p in PARTS.values()};libs[PRJ+':PWR_FLAG']=symbol('power','PWR_FLAG')
 (P/'eda/libraries/P07.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor")'+''.join(dump([s[0],s[1].split(':')[1]]+s[2:]) for s in libs.values())+')',encoding='utf-8')
 (P/'eda/sym-lib-table').write_text('(sym_lib_table (lib (name "P07") (type "KiCad") (uri "${KIPRJMOD}/libraries/P07.kicad_sym") (options "") (descr "P07 symbols")))')
 flibs=sorted({p['footprint'].split(':')[0] for p in PARTS.values()})
 (P/'eda/fp-lib-table').write_text('(fp_lib_table '+''.join(f'(lib (name {q(l)}) (type "KiCad") (uri "${{KIPRJMOD}}/libraries/{l}.pretty") (options "") (descr "P07 local library"))' for l in flibs)+')')
if __name__=='__main__':write_tables();print(len(PARTS),'parts')
