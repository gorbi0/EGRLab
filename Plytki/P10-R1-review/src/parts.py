"""P10 passive CAN receiver: fixed silent and recessive TXD, protected RX to CORE."""
from cadlib import *
import csv,shutil
FP=P/'eda/libraries/P10.pretty';FP.mkdir(parents=True,exist_ok=True);PARTS={}
exec((P/'src/helpers.txt').read_text(encoding='utf-8'))
import make_footprints
G='GND';V='3V3_IO';V5='5V_SYS'
RFP=copyfp('Resistor_THT','R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal')
CFP=copyfp('Capacitor_SMD','C_0805_2012Metric');SO8=copyfp('Package_SO','SOIC-8_3.9x4.9mm_P1.27mm');SO14=copyfp('Package_SO','SOIC-14_3.9x8.7mm_P1.27mm');SOT=copyfp('Package_TO_SOT_SMD','SOT-23')
shutil.copy2(P/'input/footprints/TestPad_1.kicad_mod',FP/'TestPad_1.kicad_mod')
def add(r,src,sym,fp,value,mpn,pins,sheet,url='',note='',**extra):
 PARTS[r]=dict(ref=r,source_ref=src,symbol=sym,footprint=fp,display=value,value=value,mpn=mpn,pins={str(k):v for k,v in pins.items()},sheet=sheet,url=url,note=note,qty=1,on_board=True,**extra)
tcan=custom('TCAN1051V_SO8',[([(1,'TXD','input'),(8,'S_SILENT','input'),(3,'VCC_5V','power_in'),(5,'VIO','power_in'),(2,'GND','power_in')],[(7,'CANH','bidirectional'),(6,'CANL','bidirectional'),(4,'RXD','output')])])
add('U1','U16',tcan,SO8,'TCAN1051V','TCAN1051VDRQ1',{1:V,2:G,3:V5,4:'RX_RAW',5:V,6:'CAN_L',7:'CAN_H',8:V},'P10','https://www.ti.com/lit/ds/symlink/tcan1051-q1.pdf','S and TXD hardwired to VIO. No MCU transmit connection and no mode jumper. V variant required.')
add('U2','ADDED_RX_IOFF',symbol('74xx','74LVC125','74LVC125AD'),SO14,'74LVC125AD','74LVC125AD,118 Nexperia',{1:G,2:'RX_RAW',3:'RX_BUF',4:V,5:G,6:'NC',7:G,8:'NC',9:G,10:V,11:'NC',12:G,13:V,14:V},'CORE','https://assets.nexperia.com/documents/data-sheet/74LVC125A.pdf','Ioff protects dead P10 from P03 receiver pull-up. HC125 is not a substitute.')
tvs=custom('PESD2CAN_SOT23',[([(1,'CAN_L','passive'),(2,'CAN_H','passive')],[(3,'COMMON_GND','passive')])])
add('D1','D3',tvs,SOT,'PESD2CAN','PESD2CAN,215 Nexperia',{1:'CAN_L',2:'CAN_H',3:G},'P10','https://assets.nexperia.com/documents/data-sheet/PESD2CAN.pdf','Pins1/2 are identical protected lines; pin3 common to GND. Routed at cable entry. Not a TVS for the supply rail.')
for r,val,a,b in [('R1','100R','RX_BUF','CAN_RX'),('R2','10K',V,'RX_RAW')]:add(r,'P10_R1',symbol('Device','R'),RFP,val,f'Metal film {val} 1% 0.25W',{1:a,2:b},'CORE')
for i,(val,net) in enumerate([('100n',V5),('100n',V),('100n',V),('4u7',V5),('4u7',V)],1):add('C'+str(i),'DECOUPLING',symbol('Device','C'),CFP,val,'X7R 25V 10% 0805 '+val,{1:net,2:G},'P10' if i!=3 else 'CORE')
add('J1','J_LV10B',symbol('Connector_Generic','Conn_01x04'),'P10:PTH_LV10','LV10 / PTH','Soldered harness',{1:V5,2:G,3:V,4:G},'P10')
add('J2','J_CANB',symbol('Connector_Generic','Conn_01x06'),'P10:PTH_CAN_CORE','CORE CAN / PTH KEY4','Soldered ribbon 6p',{1:'CAN_TX',2:G,3:'CAN_RX',4:'NC',5:'NC',6:'NC'},'CORE',note='P03-R2/J8. CAN_TX only to TP6; no path to transceiver. Wires4/5/6 insulated at P10.')
add('J3','J_OBD_TAIL',symbol('Connector_Generic','Conn_01x02'),'P10:PTH_OBD','OBD / PTH','Soldered 120ohm twisted pair',{1:'CAN_H',2:'CAN_L'},'P10',note='300mm cable to OBD male typeA pins6/14. All other OBD pins NC, including4/5/16. Device GND from its power input only.')
for i,n in enumerate([V5,V,G,'RX_RAW','CAN_RX','CAN_TX'],1):add('TP'+str(i),'TESTPAD',symbol('Connector','TestPoint'),'P10:TestPad_1',n,'PCB test pad',{1:n},'CORE')
if __name__=='__main__':write_tables();print(len(PARTS),'parts')
