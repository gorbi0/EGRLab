"""P09 TEMP carrier. Physical bought-module pin order from offer photo 6, not from an assumed Adafruit clone."""
from cadlib import *
import csv,shutil
FP=P/'eda/libraries/P09.pretty';FP.mkdir(parents=True,exist_ok=True);PARTS={}
exec((P/'src/helpers.txt').read_text(encoding='utf-8'))
import make_footprints
G='GND';V='3V3_IO';A5='5V_SYS'
RFP=copyfp('Resistor_THT','R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal')
CS=copyfp('Capacitor_SMD','C_0805_2012Metric');SO14=copyfp('Package_SO','SOIC-14_3.9x8.7mm_P1.27mm');DIP16=copyfp('Package_DIP','DIP-16_W7.62mm')
HDR3=copyfp('Connector_PinHeader_2.54mm','PinHeader_1x03_P2.54mm_Vertical')
shutil.copy2(P/'input/footprints/TestPad_1.kicad_mod',FP/'TestPad_1.kicad_mod');TP='P09:TestPad_1'
def add(r,src,sym,fp,value,mpn,pins,sheet,url='',note='',**extra):
 PARTS[r]=dict(ref=r,source_ref=src,symbol=sym,footprint=fp,display=value,value=value,mpn=mpn,pins={str(k):v for k,v in pins.items()},sheet=sheet,url=url,note=note,qty=1,on_board=True,**extra)
def res(r,val,ohms,a,b,sh='SPI'):
 add(r,'P09_R1',symbol('Device','R'),RFP,val,f'Metal film {val} 1% 0.25W',{1:a,2:b},sh,ohms=ohms,tolerance=.01)
def cap(r,val,farad,a,b,sh='P09'):
 add(r,'P09_R1',symbol('Device','C'),CS,val,'X7R 25V 10% 0805 '+val,{1:a,2:b},sh,farads=farad)
lvc=symbol('74xx','74LVC125','74LVC125AD');url='https://assets.nexperia.com/documents/data-sheet/74LVC125A.pdf'
add('U1','U_RX1',lvc,SO14,'74LVC125AD','74LVC125AD,118 Nexperia',{1:G,2:'SPI3_SCLK',3:'CLK_BUF',4:G,5:'SPI3_MOSI',6:'MOSI_BUF',7:G,8:'CS1_BUF',9:'TC1_CS',10:G,11:'CS2_BUF',12:'TC2_CS',13:G,14:V},'SPI',url,'Ioff required; all input buffers always enabled.')
add('U2','U_TX',lvc,SO14,'74LVC125AD','74LVC125AD,118 Nexperia',{1:'OE1_N',2:'TC1_MISO',3:'TX1',4:'OE2_N',5:'TC2_MISO',6:'TX2',7:G,8:'NC',9:G,10:V,11:'NC',12:G,13:V,14:V},'SPI',url,'Separate 100R output resistors; inactive channels Hi-Z.')
dec=custom('HC139_DIP',[( [(1,'G_N','input'),(2,'A','input'),(3,'B','input')],[(4,'Y0_N','output'),(5,'Y1_N','output'),(6,'Y2_N','output'),(7,'Y3_N','output')]), ([(15,'G_N','input'),(14,'A','input'),(13,'B','input')],[(12,'Y0_N','output'),(11,'Y1_N','output'),(10,'Y2_N','output'),(9,'Y3_N','output')]), ([(16,'VCC','power_in')],[(8,'GND','power_in')])])
add('U3','ADDED_CS_DECODER',dec,DIP16,'SN74HC139N','SN74HC139N',{1:G,2:'CS1_BUF',3:'CS2_BUF',4:'NC',5:'OE2_N',6:'OE1_N',7:'NC',8:G,9:'NC',10:'NC',11:'NC',12:'NC',13:G,14:G,15:V,16:V},'SPI','https://www.ti.com/lit/ds/symlink/sn74hc139.pdf','Only exactly one active CS enables a MISO buffer. Static truth table, not a substitute for CS dead time.')
for i,n in [(1,'TC1_CS'),(2,'TC2_CS')]:res('R'+str(i),'10K',10000,V,n)
for i,n in [(3,'SPI3_SCLK'),(4,'SPI3_MOSI')]:res('R'+str(i),'100K',100000,n,G)
for i,n in [(5,'CS1_BUF'),(6,'CS2_BUF')]:res('R'+str(i),'10K',10000,V,n)
for i,n in [(7,'CLK_BUF'),(8,'MOSI_BUF'),(9,'TC1_MISO'),(10,'TC2_MISO')]:res('R'+str(i),'100K',100000,n,G)
res('R11','100R',100,'TX1','SPI3_MISO');res('R12','100R',100,'TX2','SPI3_MISO');res('R13','100K',100000,'SPI3_MISO',G)
for i,a,b in [(14,'CLK_BUF','CLK_MODULE'),(15,'MOSI_BUF','MOSI_MODULE'),(16,'CS1_BUF','TC1_CS_MODULE'),(17,'CS2_BUF','TC2_CS_MODULE')]:res('R'+str(i),'47R',47,a,b)
for i,n in [(18,'OE1_N'),(19,'OE2_N')]:res('R'+str(i),'10K',10000,V,n)
for i in range(1,4):cap('C'+str(i),'100n',1e-7,V,G)
cap('C4','4u7',4.7e-6,V,G);cap('C5','4u7',4.7e-6,A5,G)
cap('C6','1u',1e-6,'TC1_VIN',G);cap('C7','1u',1e-6,'TC2_VIN',G)
add('J1','J_LV09B',symbol('Connector_Generic','Conn_01x04'),'P09:PTH_LV09','LV09 / PTH','Soldered harness',{1:A5,2:G,3:V,4:G},'P09')
add('J2','J_TEMPB',symbol('Connector_Generic','Conn_01x10'),'P09:PTH_TEMP','TEMP / PTH KEY4','Soldered harness',{1:'SPI3_SCLK',2:G,3:'SPI3_MOSI',4:'NC',5:'SPI3_MISO',6:G,7:'TC1_CS',8:G,9:'TC2_CS',10:G},'P09')
mod=custom('MAX31856_MODULE_SOCKET',[( [(1,'VIN','power_in'),(3,'GND','power_in'),(4,'SCK','input'),(6,'SDI','input'),(7,'CS_N','input')],[(2,'3Vo','passive'),(5,'SDO','tri_state'),(8,'FLT_N','output'),(9,'DRDY_N','output')])])
for ch,j in [(1,'J3'),(2,'J4')]:
 add(j,'TC'+str(ch),mod,'P09:MAX31856_XU_socket','TC'+str(ch)+' / MAX31856 XU','Socket 1x9 2.54mm Au + owned MAX31856 module',{1:f'TC{ch}_VIN',2:f'TC{ch}_3VO',3:G,4:'CLK_MODULE',5:f'TC{ch}_MISO',6:'MOSI_MODULE',7:f'TC{ch}_CS_MODULE',8:f'TC{ch}_FLT_N',9:f'TC{ch}_DRDY_N'},'P09','https://allegro.pl/oferta/max31856-modul-termopary-dla-typow-k-j-n-r-s-t-e-b-19-bitowy-modul-xu-18805671895','Pinout photo6: VIN/3Vo/GND/SCK/SDO/SDI/CS/FLT/DRDY. Pitch/body/hole fit must be measured; carrier mounting holes are oversize 6mm for nylon M2.5 with 8mm washers. No Adafruit electrical equivalence assumed.')
 add('JP'+str(ch),'ADDED_VIN_SELECT',symbol('Connector_Generic','Conn_01x03'),HDR3,'VIN SELECT / OPEN','Header 1x3 + one shunt (not fitted initially)',{1:V,2:f'TC{ch}_VIN',3:A5},'P09',note='One shunt: 1-2=3.3V initial qualification; 2-3=5V ONLY after regulator and level-shifter qualification. Never two shunts. Power off before change.')
for i,n in enumerate([V,A5,G,'CS1_BUF','CS2_BUF','OE1_N','OE2_N','TC1_3VO','TC2_3VO','TC1_FLT_N','TC2_FLT_N','TC1_DRDY_N','TC2_DRDY_N'],1):add('TP'+str(i),'TESTPAD',symbol('Connector','TestPoint'),TP,n,'PCB test pad',{1:n},'CONNECT')
if __name__=='__main__':write_tables();print(len(PARTS),'parts')
