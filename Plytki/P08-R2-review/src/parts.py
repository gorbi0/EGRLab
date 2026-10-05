"""P08-R2 SENSOR, format S1 (class 1/3, slot S1, level 5; S1-3). Switched current-limited sensor supply for TEST; the circuit of P08-R1 is unchanged.
R1 -> R2: J1 LV08, J2 SENSOR and J3 SFAULT (soldered harnesses) -> J1 = J_BP (angled shrouded IDC 2x8 at edge A, odd pins GND); TP1..TP13 -> service strip J2
(1x13 at edge B, GND at both ends, series resistors R19..R29 at the nodes); J4 TSENSOR (Mini-Fit 2p) -> wire field with tie anchor at the panel edge x = 0
(wires to the TEST port on the panel). Owned THT parts (Zamowione/zamowione.csv, balance in docs/ZAKUPY.md) stay and stand up; new R and C are SMD 1206."""
from cadlib import *
import csv,shutil
FP=P/'eda/libraries/P08.pretty';FP.mkdir(parents=True,exist_ok=True);PARTS={}
URL={k:v['url'] for k,v in json.loads((P/'reference/datasheets/sources.json').read_text()).items()}
exec((P/'src/helpers.txt').read_text(encoding='utf-8'))
G='GND';V='3V3_IO';A5='5V_SYS'
REG='rejestr';NEW='nowe'
RS=copyfp('Resistor_SMD','R_1206_3216Metric_Pad1.30x1.75mm_HandSolder')        # new resistors
RT7=copyfp('Resistor_THT','R_Axial_DIN0207_L6.3mm_D2.5mm_P5.08mm_Vertical')      # owned MF0207, standing
RT4=copyfp('Resistor_THT','R_Axial_DIN0204_L3.6mm_D1.6mm_P2.54mm_Vertical')      # owned MF0204, standing
CS=copyfp('Capacitor_SMD','C_1206_3216Metric_Pad1.33x1.80mm_HandSolder')       # new ceramics
SO14=copyfp('Package_SO','SOIC-14_3.9x8.7mm_P1.27mm')
DIP14=copyfp('Package_DIP','DIP-14_W7.62mm');DIP18=copyfp('Package_DIP','DIP-18_W7.62mm')
TO92=copyfp('Package_TO_SOT_THT','TO-92_Inline_Wide');SOT6=copyfp('Package_TO_SOT_SMD','SOT-23-6')
DIO=copyfp('Diode_THT','D_DO-35_SOD27_P7.62mm_Horizontal')
IDC16=copyfp('Connector_IDC','IDC-Header_2x08_P2.54mm_Horizontal')
HDR13=copyfp('Connector_PinHeader_2.54mm','PinHeader_1x13_P2.54mm_Horizontal')
import make_footprints
def add(r,src,sym,fp,value,mpn,pins,sheet,url='',note='',zrodlo=NEW,**extra):
 PARTS[r]=dict(ref=r,source_ref=src,symbol=sym,footprint=fp,display=value,value=value,mpn=mpn,pins={str(k):v for k,v in pins.items()},sheet=sheet,url=url,note=note,qty=1,on_board=True,zrodlo=zrodlo,**extra)
SR=symbol('Device','R');SC=symbol('Device','C')
# Owned THT resistors still in stock after P02 R4 / P05 R3 / P06 R2 / P09 R2 / P10 R2 (docs/ZAKUPY.md): MF0207 4k7 (2 left), MF0204 6k8 (1 left).
OWNED_R={'4K7':(RT7,'MF0207FTE-4K7 Yageo 4.7k 1% 0.6W (owned, standing)'),'6K8':(RT4,'MF0204FTE52-6K8 Yageo 6.8k 1% 0.4W (owned, standing)')}
def res(r,src,val,ohms,a,b,sh,note=''):
 if val in OWNED_R:fp,mpn=OWNED_R[val];add(r,src,SR,fp,val,mpn,{1:a,2:b},sh,note=note,zrodlo=REG,ohms=ohms,tolerance=.01)
 else:add(r,src,SR,RS,val,f'SMD 1206 1% 0.25W {val}',{1:a,2:b},sh,note=note,ohms=ohms,tolerance=.01,power_w=.25)
def cap(r,src,val,farad,a,b,sh):
 add(r,src,SC,CS,val,'SMD 1206 X7R 25V 10% '+val,{1:a,2:b},sh,farads=farad)
tps=custom('TPS2553_DBV',[( [(1,'IN','power_in'),(3,'EN','input'),(2,'GND','power_in')],[(6,'OUT','power_out'),(4,'FAULT_N','open_collector'),(5,'ILIM','passive')])])
add('U1','U11',tps,SOT6,'TPS2553DBVR','TPS2553DBVR',{1:A5,2:G,3:'TPS_EN',4:'SENSOR_FAULT_LOCAL_N',5:'ILIM_232K',6:'SENSOR_LIMITED'},'P08',URL['TPS2553.pdf'],'Active-high constant-current version. TPS2552 and TPS2553-1 are not approved substitutes. Top side (SMD).')
driver=custom('TBD62083_APG',[( [(i,'I'+str(i),'input') for i in range(1,9)]+[(9,'GND','power_in')],[(19-i,'O'+str(i),'open_collector') for i in range(1,9)]+[(10,'COMMON','passive')])])
add('U2','U_RELAY',driver,DIP18,'TBD62083APG','TBD62083APG',{1:'SENSOR_LOCAL',**{i:G for i in range(2,10)},10:A5,**{i:'NC' for i in range(11,18)},18:'SENSOR_COIL_LOW'},'P08',URL['TBD62083.pdf'],'Internal flyback COMMON to 5V_SYS; external D1 at coil. Not a ULN2803 substitution.')
add('U3','U_READY',symbol('74xx','74LS08','SN74HC08N'),DIP14,'SN74HC08N','SN74HC08N',{1:'SUP3_N',2:'SUP5_N',3:'SENSOR_OK_LOCAL',4:'PERMIT_LOCAL',5:'SENSOR_OK_LOCAL',6:'SENSOR_LOCAL',7:G,8:'SENSOR_HEALTH_LOCAL',9:'SENSOR_OK_LOCAL',10:'SENSOR_FAULT_LOCAL_N',11:'NC',12:G,13:G,14:V},'LOGIC',URL['HC08.pdf'],'Owned (P08 allocation, Mouser 24.09), DIP14 socket Kamami 648.',zrodlo=REG)
lvc=symbol('74xx','74LVC125','74LVC125AD')
add('U4','U_SUPBUF',lvc,SO14,'74LVC125AD','74LVC125AD,118 (Nexperia)',{1:G,2:'SUP5_RAW',3:'SUP5_N',4:G,5:'SENSOR_OK_LOCAL',6:'SENSOR_OK_TX',7:G,8:'NC',9:G,10:V,11:'NC',12:G,13:V,14:V},'LOGIC',URL['LVC125.pdf'],'5V tolerant input and Ioff. Spare channel buffers outgoing READY. Owned; top side (level 5: no SOIC underneath), soldered directly.',zrodlo=REG)
add('U5','U_RX1',lvc,SO14,'74LVC125AD','74LVC125AD,118 (Nexperia)',{1:G,2:'SENSOR_PERMIT',3:'PERMIT_LOCAL',4:G,5:'SENSOR_HEALTH_LOCAL',6:'SENSOR_HEALTH_TX',7:G,8:'NC',9:G,10:V,11:'NC',12:G,13:V,14:V},'LOGIC',URL['LVC125.pdf'],'Ioff required on inter-board signals. Owned; top side, soldered directly.',zrodlo=REG)
sup=custom('MCP120_D_TO',[( [(2,'VDD','power_in')],[(1,'RESET_N','open_collector'),(3,'VSS','power_in')])])
for r,src,mpn,rail,out in [('U6','U_SUP3','MCP120-300DI/TO',V,'SUP3_N'),('U7','U_SUP5','MCP120-450DI/TO',A5,'SUP5_RAW'),('U8','ADD_EN_GUARD','MCP120-300DI/TO',V,'TPS_EN')]:
 add(r,src,sup,TO92,mpn,mpn,{1:out,2:rail,3:G},'P08' if r=='U8' else 'LOGIC',URL['MCP120.pdf'],'D bondout: RESET=1, VDD=2, VSS=3. MCP120 only, no internal pull-up.'+(' Registry has one MCP120-300 for P08 (U6); U8 is a new purchase.' if r=='U8' else ' Owned (P08 allocation).'),zrodlo=NEW if r=='U8' else REG)
relay=custom('G6K_2P_Y',[( [(1,'COIL+','passive'),(8,'COIL-','passive')],[]), ([(3,'COM_A','passive'),(6,'COM_B','passive')],[(2,'NC_A','passive'),(4,'NO_A','passive'),(7,'NC_B','passive'),(5,'NO_B','passive')])])
add('K1','KSENSOR',relay,'P08:G6K_2P_Y_verified','G6K-2P-Y DC5','G6K-2P-Y DC5',{1:A5,8:'SENSOR_COIL_LOW',3:'SENSOR_LIMITED',2:'NC',4:'5V_SENSOR',6:G,7:'NC',5:'AGND_SENSOR'},'P08',URL['G6K.pdf'],'THT monostable; coil polarized. Library pad 2/7 corrected from 3.0 to 3.2 mm per Omron p6.')
add('D1','D8',symbol('Device','D'),DIO,'1N4148','1N4148',{1:A5,2:'SENSOR_COIL_LOW'},'P08',URL['1N4148.pdf'],'Cathode to coil positive. Release time with diode must be measured. Owned (Kamami 1187768).',zrodlo=REG)
rows=[
 ('R1','R_ILIM','232K',232000,'ILIM_232K',G,'P08'),
 ('R2','R_FAULT_PU','10K',10000,V,'SENSOR_FAULT_LOCAL_N','LOGIC'),
 ('R3','R_SUP3','10K',10000,V,'SUP3_N','LOGIC'),
 ('R4','R_SUP5','10K',10000,A5,'SUP5_RAW','LOGIC'),
 ('R5','ADD_SUP5_PD','10K',10000,'SUP5_N',G,'LOGIC'),
 ('R6','R_PERMIT_PD+R_DEFAULT_SENSOR_PERMIT','10K',10000,'PERMIT_LOCAL',G,'LOGIC'),
 ('R7','R_EXT_SENSOR','10K',10000,'SENSOR_PERMIT',G,'LOGIC'),
 ('R8','R_READY_PD','10K',10000,'SENSOR_OK_LOCAL',G,'LOGIC'),
 ('R9','ADD_EN_PD','10K',10000,'SENSOR_LOCAL',G,'LOGIC'),
 ('R10','ADD_HEALTH_PD','10K',10000,'SENSOR_HEALTH_LOCAL',G,'LOGIC'),
 ('R11','ADD_READY_SER','100R',100,'SENSOR_OK_TX','SENSOR_OK','LOGIC'),
 ('R12','ADD_READY_EXT_PD','10K',10000,'SENSOR_OK',G,'LOGIC'),
 ('R13','ADD_HEALTH_SER','100R',100,'SENSOR_HEALTH_TX','SENSOR_HEALTHY','LOGIC'),
 ('R14','ADD_HEALTH_EXT_PD','10K',10000,'SENSOR_HEALTHY',G,'LOGIC'),
 ('R15','ADD_GUARD_SER','4K7',4700,'SENSOR_LOCAL','TPS_EN','P08'),
 ('R16','ADD_GUARD_PD','6K8',6800,'TPS_EN',G,'P08'),
 ('R17','ADD_LOCAL_DISCHARGE','10K',10000,'SENSOR_LIMITED',G,'P08'),
 ('R18','ADD_OUTPUT_DISCHARGE','10K',10000,'5V_SENSOR','AGND_SENSOR','P08')]
for args in rows:res(*args)
cap('C1','C_SIN','1u',1e-6,A5,G,'P08');cap('C2','C_SOUT','1u',1e-6,'SENSOR_LIMITED',G,'P08')
for i,(u,rail,sh) in enumerate([('U3',V,'P08'),('U4',V,'P08'),('U5',V,'P08'),('U6',V,'P08'),('U7',A5,'P08'),('U8',V,'P08')],3):cap('C'+str(i),'DEC_'+u,'100n',1e-7,rail,G,sh)
cap('C9','ADD_COIL_DECOUPLING','1u',1e-6,A5,G,'P08')
cp=copyfp('Capacitor_THT','CP_Radial_D5.0mm_P2.00mm')
add('C10','ADD_LV_BULK',symbol('Device','C_Polarized'),cp,'22u / 25V','EEUFR1E220',{1:A5,2:G},'P08',farads=22e-6,note='D5 pitch 2 mm, ca. 11 mm high (level limit 16.5 mm). The two owned EEUFR1H220 are used by P02 R4; new purchase.')
# J_BP (edge A, slot S1, centre x = 26.5 mm): odd pins GND, even pins signals/supplies. 3 signals + 5V_SYS x2 (S1 sec. 5) + 3V3_IO = 6 even pins -> 2x8 (2x5 has 5).
# Net names exactly as P08-R1 / P04-R2.2 interfejsy (SENSOR) and P03 R6 J_BP1.12 (SFAULT); P12 joins by name.
JBP=[(2,'5V_SYS','zasilanie do P08','P02 R4 (przez P12)','U1 (TPS2553) i K1/U2 (cewka), U7, R4; S1 §5: co najmniej 2 piny; budżet 200 mA'),
     (4,'3V3_IO','zasilanie do P08','P02 R4 (przez P12)','logika U3–U5, nadzorcy U6/U8, podciąganie R2/R3; budżet 15 mA'),
     (6,'SENSOR_PERMIT','wejście','P04 (przez P12)','zezwolenie z P04 (R1: P04/J4.1); bufor U5 z Ioff, R7 10 kΩ do GND'),
     (8,'SENSOR_OK','wyjście','P04 (przez P12)','obie szyny poprawne (R1: P04/J4.3); U4 + R11 100 Ω, R12 10 kΩ do GND'),
     (10,'SENSOR_HEALTHY','wyjście','P03 (przez P12)','szyny poprawne i brak FAULT TPS (R1: P03/J6.1; P03 R6 J_BP1.12 wejście); U5 + R13 100 Ω, R14 10 kΩ do GND'),
     (12,'NC','—','—','wolny (2×8 ma 8 pinów parzystych, P08 używa 6)'),
     (14,'NC','—','—','wolny'),
     (16,'5V_SYS','zasilanie do P08','P02 R4 (przez P12)','drugi pin 5V_SYS (S1 §5)')]
jbp_pins={i:G for i in range(1,17,2)};jbp_pins.update({p:n for p,n,*_ in JBP})
add('J1','J_BP',symbol('Connector_Generic','Conn_02x08_Odd_Even'),IDC16,'J_BP / IDC 2x8','IDC header 2x8 2.54mm angled shrouded, Au (type as P09 R2 J1 in the purchase list)',jbp_pins,'CONNECT',note='Edge A, slot S1, centre x=26.5 mm. Odd pins GND, even pins signals/supplies, 12/14 free. Pin 1 towards smaller x. Replaces LV08 (P02-R3/J8), SENSOR (P04-R2.1/J4) and SFAULT (P03-R2/J6).')
# J4 TSENSOR: wire field to the TEST port on the panel (not P12; the switched sensor supply and its isolated return leave the board as a pair).
add('J4','J_TSENSORA',symbol('Connector_Generic','Conn_01x02'),'P08:PTH_TSENSOR_2','TSENSOR / PTH','2 x AWG22 soldered, tie anchor 12 mm',{1:'5V_SENSOR',2:'AGND_SENSOR'},'CONNECT',note='Wire field at the panel edge x=0 (as J4/J6 of P05 R3): pair to the TEST port on the panel; numbering kept from R1 (contract W4 to P11). AGND_SENSOR never to GND outside K1.')
# Service strip (edge B, x = 10..43 mm of the slot): ODBIOR R1 points. 1 k for rails and logic, 10 k for the high-impedance divider node TPS_EN (S1 sec. 6).
# 5V_SENSOR / AGND_SENSOR are measured differentially at the TEST port (J4 pair) instead: a probe slipped to the neighbouring GND pin must not bypass the K1 return contact.
SRV=[('5V_SYS',1000,'E02/E15: szyna 5 V, pobór, granice 4,75/5,25 V'),
     ('3V3_IO',1000,'E02/E11/E12: szyna 3,3 V, rampy i zaniki'),
     ('SUP3_N',1000,'E11/E12: wyjście U6 (nadzorca 3,3 V), opóźnienie 150–700 ms'),
     ('SUP5_N',1000,'E11: nadzorca 5 V za buforem U4'),
     ('SENSOR_OK',1000,'E03/E13: SENSOR_OK do P04 (za R11), stan przy martwej P08'),
     ('SENSOR_HEALTHY',1000,'E03/E07/E13: SENSOR_HEALTHY do P03 (za R13)'),
     ('PERMIT_LOCAL',1000,'E10: PERMIT za buforem U5 (LOW przy odłączonym P04)'),
     ('SENSOR_LOCAL',1000,'E04/E09/E10: zezwolenie lokalne (U3), sterowanie U2 i dzielnika EN'),
     ('TPS_EN',10000,'E02/E04/E12: EN TPS2553 (dzielnik R15/R16 i U8); ≤ 0,66 V wyłączony, ok. 1,95 V włączony'),
     ('SENSOR_LIMITED',1000,'E04–E07/E09: wyjście U1 przed K1 (limit prądu, rozładowanie R17)'),
     ('SENSOR_FAULT_LOCAL_N',1000,'E07: FAULT_N TPS2553 (deglitch 5–10 ms)')]
srv_pins={1:G,len(SRV)+2:G};srv_r={}
for k,(net,ohm,_) in enumerate(SRV,2):
 r='R'+str(k+17);srv_r[net]=r;srv_pins[k]='SRV_'+net
 res(r,'P08_R2','1K' if ohm==1000 else '10K',ohm,net,'SRV_'+net,'CONNECT','Serwis: kołek przez rezystor przy węźle, zsunięta sonda nic nie uszkodzi')
add('J2','J_SRV',symbol('Connector_Generic','Conn_01x13'),HDR13,'SERWIS / goldpin 1x13','Goldpin 1x13 2.54mm angled (buy angled strip, owned 1x40 is straight)',srv_pins,'CONNECT',note='Edge B, x=10..43 mm of the slot (13 pins = slot maximum); pin 1 towards larger x (angled strip on the top side: the footprint fixes the order, as P09/P10 R2); pins stick ~6 mm beyond the edge. GND at both ends.')
if __name__=='__main__':write_tables();print(len(PARTS),'parts')
