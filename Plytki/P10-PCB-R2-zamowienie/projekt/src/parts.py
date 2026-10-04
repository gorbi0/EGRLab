"""P10 passive CAN receiver, R2, format S1 (class 1/3, slot S3, level 4; S1-3). Fixed silent and recessive TXD, protected RX to CORE.
R1 -> R2: J1 LV10 and J2 CAN_CORE (soldered harnesses) -> J_BP (angled shrouded IDC 2x5, odd pins GND); TP1..TP6 -> service strip J2 (1x9, GND at both ends,
series resistors R3..R9 at the nodes); J3 OBD tail stays; owned THT parts (Zamowione/zamowione.csv: MF0207 10k, K104K15X7RF5TH5 100n) stand upright, everything else new is SMD 1206."""
from cadlib import *
import csv,shutil
FP=P/'eda/libraries/P10.pretty';FP.mkdir(parents=True,exist_ok=True);PARTS={}
exec((P/'src/helpers.txt').read_text(encoding='utf-8'))
import make_footprints
G='GND';V='3V3_IO';V5='5V_SYS'
RT=copyfp('Resistor_THT','R_Axial_DIN0207_L6.3mm_D2.5mm_P5.08mm_Vertical')   # owned MF0207, standing
RS=copyfp('Resistor_SMD','R_1206_3216Metric_Pad1.30x1.75mm_HandSolder')      # new
CT=copyfp('Capacitor_THT','C_Disc_D5.0mm_W2.5mm_P5.00mm')                    # owned K104K15X7RF5TH5 100n X7R radial
CS=copyfp('Capacitor_SMD','C_1206_3216Metric_Pad1.33x1.80mm_HandSolder')     # new
SO8=copyfp('Package_SO','SOIC-8_3.9x4.9mm_P1.27mm');SO14=copyfp('Package_SO','SOIC-14_3.9x8.7mm_P1.27mm');SOT=copyfp('Package_TO_SOT_SMD','SOT-23')
IDC10=copyfp('Connector_IDC','IDC-Header_2x05_P2.54mm_Horizontal');HDR9=copyfp('Connector_PinHeader_2.54mm','PinHeader_1x09_P2.54mm_Horizontal')
REG='rejestr';NEW='nowe'
def add(r,src,sym,fp,value,mpn,pins,sheet,url='',note='',zrodlo=NEW,**extra):
 PARTS[r]=dict(ref=r,source_ref=src,symbol=sym,footprint=fp,display=value,value=value,mpn=mpn,pins={str(k):v for k,v in pins.items()},sheet=sheet,url=url,note=note,qty=1,on_board=True,zrodlo=zrodlo,**extra)
OWNED_R={'10K'}
def res(r,val,a,b,sh,src='P10_R1',note=''):
 if val in OWNED_R:add(r,src,symbol('Device','R'),RT,val,f'MF0207 Yageo {val} 1% 0.6W (owned, standing)',{1:a,2:b},sh,note=note,zrodlo=REG)
 else:add(r,src,symbol('Device','R'),RS,val,f'SMD 1206 1% 0.25W {val}',{1:a,2:b},sh,note=note)
def cap(r,val,net,sh,src='DECOUPLING'):
 if val=='100n':add(r,src,symbol('Device','C'),CT,val,'K104K15X7RF5TH5 Vishay 100n X7R 50V radial 5mm (owned)',{1:net,2:G},sh,zrodlo=REG)
 else:add(r,src,symbol('Device','C'),CS,val,'SMD 1206 X7R 25V 10% '+val,{1:net,2:G},sh)
tcan=custom('TCAN1051V_SO8',[([(1,'TXD','input'),(8,'S_SILENT','input'),(3,'VCC_5V','power_in'),(5,'VIO','power_in'),(2,'GND','power_in')],[(7,'CANH','bidirectional'),(6,'CANL','bidirectional'),(4,'RXD','output')])])
add('U1','U16',tcan,SO8,'TCAN1051V','TCAN1051VDRQ1',{1:V,2:G,3:V5,4:'RX_RAW',5:V,6:'CAN_L',7:'CAN_H',8:V},'P10','https://www.ti.com/lit/ds/symlink/tcan1051-q1.pdf','S and TXD hardwired to VIO. No MCU transmit connection and no mode jumper. V variant required.')
add('U2','ADDED_RX_IOFF',symbol('74xx','74LVC125','74LVC125AD'),SO14,'74LVC125AD','74LVC125AD,118 Nexperia',{1:G,2:'RX_RAW',3:'RX_BUF',4:V,5:G,6:'NC',7:G,8:'NC',9:G,10:V,11:'NC',12:G,13:V,14:V},'CORE','https://assets.nexperia.com/documents/data-sheet/74LVC125A.pdf','Ioff protects dead P10 from P03 receiver pull-up. HC125 is not a substitute.',zrodlo=REG)
tvs=custom('PESD2CAN_SOT23',[([(1,'CAN_L','passive'),(2,'CAN_H','passive')],[(3,'COMMON_GND','passive')])])
add('D1','D3',tvs,SOT,'PESD2CAN','PESD2CAN,215 Nexperia',{1:'CAN_L',2:'CAN_H',3:G},'P10','https://assets.nexperia.com/documents/data-sheet/PESD2CAN.pdf','Pins1/2 are identical protected lines; pin3 common to GND. Routed at cable entry. Not a TVS for the supply rail.')
res('R1','100R','RX_BUF','CAN_RX','CORE');res('R2','10K',V,'RX_RAW','CORE')
for i,(val,net) in enumerate([('100n',V5),('100n',V),('100n',V),('4u7',V5),('4u7',V)],1):cap('C'+str(i),val,net,'P10' if i!=3 else 'CORE')
# J_BP (edge A): odd pins GND, even pins signals/supplies; only what P10 uses. 5V_SYS on two pins (S1 spec 5), 3V3_IO on one.
JBP=[(2,'5V_SYS','zasilanie do P10','P02 R4 (przez P12)','5V_SYS: VCC transceivera U1 (TCAN1051V), C1/C4; S1 §5: co najmniej 2 piny'),
     (4,'3V3_IO','zasilanie do P10','P02 R4 (przez P12)','VIO transceivera, S i TXD na stałe, U2 z Ioff, pull-up R2'),
     (6,'CAN_TX','wejście (niepodłączone do transceivera)','P03','GPIO17 CORE; na P10 tylko do kołka serwisowego, żadnej ścieżki do TXD ani S'),
     (8,'CAN_RX','wyjście','P03','GPIO18 CORE; RXD transceivera przez bufor U2 (Ioff) i R1 100 Ω'),
     (10,'5V_SYS','zasilanie do P10','P02 R4 (przez P12)','drugi pin 5V_SYS (S1 §5)')]
jbp_pins={i:G for i in range(1,11,2)};jbp_pins.update({p:n for p,n,*_ in JBP})
add('J1','J_BP',symbol('Connector_Generic','Conn_02x05_Odd_Even'),IDC10,'J_BP / IDC 2x5','IDC header 2x5 2.54mm angled shrouded, Au (type to be chosen in the purchase list)',jbp_pins,'CORE',note='Edge A, centre x=26.5 mm of the slot (S3). Odd pins GND, even pins signals/supplies. Pin 1 towards smaller x. Replaces LV10 (P02-R3/J10) and CORE CAN (P03-R2/J8).')
add('J3','J_OBD_TAIL',symbol('Connector_Generic','Conn_01x02'),'P10:PTH_OBD','OBD / PTH','Soldered 120ohm twisted pair',{1:'CAN_H',2:'CAN_L'},'P10',note='300mm cable to OBD male typeA pins6/14. All other OBD pins NC, including4/5/16. Device GND from its power input only.')
# Service strip (edge B). 1k for rails and logic; 10k for the two CAN bus nodes (external vehicle network: a slipped probe must not load or stress the bus).
SRV=[('5V_SYS',1000,'VCC transceivera: obecność 5 V, pobór, spadek'),
     ('3V3_IO',1000,'VIO, S i TXD na stałe, U2: obecność 3,3 V'),
     ('RX_RAW',1000,'RXD transceivera przed buforem U2: przebieg RX, stan recesywny'),
     ('CAN_RX',1000,'RX do P03 za U2 i R1: zgodność z RX_RAW, zachowanie przy martwej P10'),
     ('CAN_TX',1000,'CAN_TX z P03: tylko kołek, brak wpływu na H/L (próba „brak TX”)'),
     ('CAN_H',10000,'CANH: brak dominacji od P10, poziomy recesywne (obserwacja; przebiegi lepiej na J3)'),
     ('CAN_L',10000,'CANL: jw.')]
srv_pins={1:G,len(SRV)+2:G};srv_r={}
for k,(net,ohm,_) in enumerate(SRV,2):
 r='R'+str(k+1);srv_r[net]=r;srv_pins[k]='SRV_'+net
 res(r,'1K' if ohm==1000 else '10K',net,'SRV_'+net,'CORE','P10_R2','Serwis: kołek przez rezystor przy węźle, zsunięta sonda nic nie uszkodzi')
add('J2','J_SRV',symbol('Connector_Generic','Conn_01x09'),HDR9,'SERWIS / goldpin 1x9','Goldpin 1x9 2.54mm angled (buy angled strip, owned 1x40 is straight)',srv_pins,'CORE',note='Edge B, x=10..43 mm of the slot; pin 1 towards larger x (angled strip on the top side, pins out of edge B: the footprint fixes the order); pins stick ~6 mm beyond the edge. GND at both ends.')
if __name__=='__main__':write_tables();print(len(PARTS),'parts')
