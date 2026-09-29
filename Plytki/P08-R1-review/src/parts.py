"""P08-R1: switched sensor supply. Explicit physical pinouts and baseline mapping."""
from cadlib import *
import csv,shutil
FP=P/'eda/libraries/P08.pretty';FP.mkdir(parents=True,exist_ok=True);PARTS={}
URL={k:v['url'] for k,v in json.loads((P/'reference/datasheets/sources.json').read_text()).items()}
exec((P/'src/helpers.txt').read_text(encoding='utf-8'))
G='GND';V='3V3_IO';A5='5V_SYS'
RFP=copyfp('Resistor_THT','R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal')
CS=copyfp('Capacitor_SMD','C_0805_2012Metric');SO14=copyfp('Package_SO','SOIC-14_3.9x8.7mm_P1.27mm')
DIP14=copyfp('Package_DIP','DIP-14_W7.62mm');DIP18=copyfp('Package_DIP','DIP-18_W7.62mm')
TO92=copyfp('Package_TO_SOT_THT','TO-92_Inline_Wide');SOT6=copyfp('Package_TO_SOT_SMD','SOT-23-6')
DIO=copyfp('Diode_THT','D_DO-35_SOD27_P7.62mm_Horizontal')
MINI=copyfp('Connector_Molex','Molex_Mini-Fit_Jr_5566-02A_2x01_P4.20mm_Vertical')
def local(name):
 shutil.copy2(P/'input/footprints'/(name+'.kicad_mod'),FP/(name+'.kicad_mod'));return 'P08:'+name
TP=local('TestPad_1')
import make_footprints
def add(r,src,sym,fp,value,mpn,pins,sheet,url='',note='',**extra):
 PARTS[r]=dict(ref=r,source_ref=src,symbol=sym,footprint=fp,display=value,value=value,mpn=mpn,pins={str(k):v for k,v in pins.items()},sheet=sheet,url=url,note=note,qty=1,on_board=True,**extra)
SR=symbol('Device','R');SC=symbol('Device','C')
def res(r,src,val,ohms,a,b,sh):
 add(r,src,SR,RFP,val,f'Metal film {val} 1% 0.25W',{1:a,2:b},sh,ohms=ohms,tolerance=.01,power_w=.25)
def cap(r,src,val,farad,a,b,sh):
 add(r,src,SC,CS,val,'X7R 25V 10% 0805 '+val,{1:a,2:b},sh,farads=farad)
tps=custom('TPS2553_DBV',[( [(1,'IN','power_in'),(3,'EN','input'),(2,'GND','power_in')],[(6,'OUT','power_out'),(4,'FAULT_N','open_collector'),(5,'ILIM','passive')])])
add('U1','U11',tps,SOT6,'TPS2553DBVR','TPS2553DBVR',{1:A5,2:G,3:'TPS_EN',4:'SENSOR_FAULT_LOCAL_N',5:'ILIM_232K',6:'SENSOR_LIMITED'},'P08',URL['TPS2553.pdf'],'Active-high constant-current version. TPS2552 and TPS2553-1 are not approved substitutes.')
driver=custom('TBD62083_APG',[( [(i,'I'+str(i),'input') for i in range(1,9)]+[(9,'GND','power_in')],[(19-i,'O'+str(i),'open_collector') for i in range(1,9)]+[(10,'COMMON','passive')])])
add('U2','U_RELAY',driver,DIP18,'TBD62083APG','TBD62083APG',{1:'SENSOR_LOCAL',**{i:G for i in range(2,10)},10:A5,**{i:'NC' for i in range(11,18)},18:'SENSOR_COIL_LOW'},'P08',URL['TBD62083.pdf'],'Internal flyback COMMON to 5V_SYS; external D1 at coil. Not a ULN2803 substitution.')
add('U3','U_READY',symbol('74xx','74LS08','SN74HC08N'),DIP14,'SN74HC08N','SN74HC08N',{1:'SUP3_N',2:'SUP5_N',3:'SENSOR_OK_LOCAL',4:'PERMIT_LOCAL',5:'SENSOR_OK_LOCAL',6:'SENSOR_LOCAL',7:G,8:'SENSOR_HEALTH_LOCAL',9:'SENSOR_OK_LOCAL',10:'SENSOR_FAULT_LOCAL_N',11:'NC',12:G,13:G,14:V},'LOGIC',URL['HC08.pdf'])
lvc=symbol('74xx','74LVC125','74LVC125AD')
add('U4','U_SUPBUF',lvc,SO14,'74LVC125AD','74LVC125AD,118 (Nexperia)',{1:G,2:'SUP5_RAW',3:'SUP5_N',4:G,5:'SENSOR_OK_LOCAL',6:'SENSOR_OK_TX',7:G,8:'NC',9:G,10:V,11:'NC',12:G,13:V,14:V},'LOGIC',URL['LVC125.pdf'],'5V tolerant input and Ioff. Spare channel buffers outgoing READY.')
add('U5','U_RX1',lvc,SO14,'74LVC125AD','74LVC125AD,118 (Nexperia)',{1:G,2:'SENSOR_PERMIT',3:'PERMIT_LOCAL',4:G,5:'SENSOR_HEALTH_LOCAL',6:'SENSOR_HEALTH_TX',7:G,8:'NC',9:G,10:V,11:'NC',12:G,13:V,14:V},'LOGIC',URL['LVC125.pdf'],'Ioff required on inter-board signals.')
sup=custom('MCP120_D_TO',[( [(2,'VDD','power_in')],[(1,'RESET_N','open_collector'),(3,'VSS','power_in')])])
for r,src,mpn,rail,out in [('U6','U_SUP3','MCP120-300DI/TO',V,'SUP3_N'),('U7','U_SUP5','MCP120-450DI/TO',A5,'SUP5_RAW'),('U8','ADD_EN_GUARD','MCP120-300DI/TO',V,'TPS_EN')]:
 add(r,src,sup,TO92,mpn,mpn,{1:out,2:rail,3:G},'P08' if r=='U8' else 'LOGIC',URL['MCP120.pdf'],'D bondout: RESET=1, VDD=2, VSS=3. MCP120 only, no internal pull-up.')
relay=custom('G6K_2P_Y',[( [(1,'COIL+','passive'),(8,'COIL-','passive')],[]), ([(3,'COM_A','passive'),(6,'COM_B','passive')],[(2,'NC_A','passive'),(4,'NO_A','passive'),(7,'NC_B','passive'),(5,'NO_B','passive')])])
add('K1','KSENSOR',relay,'P08:G6K_2P_Y_verified','G6K-2P-Y DC5','G6K-2P-Y DC5',{1:A5,8:'SENSOR_COIL_LOW',3:'SENSOR_LIMITED',2:'NC',4:'5V_SENSOR',6:G,7:'NC',5:'AGND_SENSOR'},'P08',URL['G6K.pdf'],'THT monostable; coil polarized. Library pad 2/7 corrected from 3.0 to 3.2 mm per Omron p6.')
add('D1','D8',symbol('Device','D'),DIO,'1N4148','1N4148',{1:A5,2:'SENSOR_COIL_LOW'},'P08',URL['1N4148.pdf'],'Cathode to coil positive. Release time with diode must be measured.')
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
add('C10','ADD_LV_BULK',symbol('Device','C_Polarized'),cp,'22u / 25V','EEUFR1E220',{1:A5,2:G},'P08',farads=22e-6,note='D5 pitch2 mm; verify actual height.')
for r,src,n,c,fp,pins in [
 ('J1','J_LV08B','LV08',4,'PTH_LV08',{1:A5,2:G,3:V,4:G}),
 ('J2','J_SENSORB','SENSOR M2.2',6,'PTH_IDC6',{1:'SENSOR_PERMIT',2:'NC',3:'SENSOR_OK',4:G,5:'NC',6:'NC'}),
 ('J3','J_SFAULTB','SFAULT',6,'PTH_IDC6',{1:'SENSOR_HEALTHY',2:G,3:'NC',4:'NC',5:'NC',6:'NC'})]:
 add(r,src,symbol('Connector_Generic',f'Conn_01x{c:02d}'),'P08:'+fp,n+' / PTH','Soldered harness',pins,'CONNECT',note='One soldered end, tie anchor 12 mm; see WIAZKI.md.')
add('J4','J_TSENSORA',symbol('Connector_Generic','Conn_01x02'),MINI,'TSENSOR / Mini-Fit 2p','Molex 39-29-6028',{1:'5V_SENSOR',2:'AGND_SENSOR'},'CONNECT','https://www.molex.com/en-us/products/part-detail/39296028','Vertical Au, no snap pegs; mating harness soldered at P11. Physical fit M01 before fabrication.')
for i,n in enumerate([A5,V,G,'SUP3_N','SUP5_N','SENSOR_LOCAL','TPS_EN','SENSOR_LIMITED','SENSOR_FAULT_LOCAL_N','SENSOR_OK','SENSOR_HEALTHY','5V_SENSOR','AGND_SENSOR'],1):
 add('TP'+str(i),'ADD_TESTPAD',symbol('Connector','TestPoint'),TP,n,'PCB test pad',{1:n},'CONNECT')
if __name__=='__main__':write_tables();print(len(PARTS),'parts')
