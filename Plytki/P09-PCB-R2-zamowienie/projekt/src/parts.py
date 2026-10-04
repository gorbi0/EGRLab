"""P09 TEMP carrier, R2, format S1 (class 1/3, slot S3, level 3). Physical bought-module pin order from offer photo 6, not from an assumed Adafruit clone.
R1 -> R2: J1 LV09 and J2 TEMP (soldered harnesses) -> J_BP (angled shrouded IDC 2x8, odd pins GND); TP1..TP13 -> service strip J2 (1x13, GND at both ends,
1k series resistors R20..R30 at the nodes); owned THT parts (Zamowione/zamowione.csv: MF0207 10k/100k, K104K15X7RF5TH5 100n) stand upright, everything else new is SMD 1206."""
from cadlib import *
import csv,shutil
FP=P/'eda/libraries/P09.pretty';FP.mkdir(parents=True,exist_ok=True);PARTS={}
exec((P/'src/helpers.txt').read_text(encoding='utf-8'))
import make_footprints
G='GND';V='3V3_IO';A5='5V_SYS'
RT=copyfp('Resistor_THT','R_Axial_DIN0207_L6.3mm_D2.5mm_P5.08mm_Vertical')   # owned MF0207, standing
RS=copyfp('Resistor_SMD','R_1206_3216Metric_Pad1.30x1.75mm_HandSolder')      # new
CT=copyfp('Capacitor_THT','C_Disc_D5.0mm_W2.5mm_P5.00mm')                    # owned K104K15X7RF5TH5 100n X7R radial
CS=copyfp('Capacitor_SMD','C_1206_3216Metric_Pad1.33x1.80mm_HandSolder')     # new
SO14=copyfp('Package_SO','SOIC-14_3.9x8.7mm_P1.27mm');DIP16=copyfp('Package_DIP','DIP-16_W7.62mm')
HDR3=copyfp('Connector_PinHeader_2.54mm','PinHeader_1x03_P2.54mm_Vertical')
IDC16=copyfp('Connector_IDC','IDC-Header_2x08_P2.54mm_Horizontal');HDR13=copyfp('Connector_PinHeader_2.54mm','PinHeader_1x13_P2.54mm_Horizontal')
REG='rejestr'   # part of Zamowione/zamowione.csv (owned)
NEW='nowe'      # to be bought (list 2 to be recalculated)
OWN='posiadane' # owned outside the register (the two MAX31856 XU modules from Allegro)
def add(r,src,sym,fp,value,mpn,pins,sheet,url='',note='',zrodlo=NEW,**extra):
 PARTS[r]=dict(ref=r,source_ref=src,symbol=sym,footprint=fp,display=value,value=value,mpn=mpn,pins={str(k):v for k,v in pins.items()},sheet=sheet,url=url,note=note,qty=1,on_board=True,zrodlo=zrodlo,**extra)
OWNED_R={'10K','100K'}
def res(r,val,ohms,a,b,sh='SPI',note=''):
 if val in OWNED_R:add(r,'P09_R1',symbol('Device','R'),RT,val,f'MF0207 Yageo {val} 1% 0.6W (owned, standing)',{1:a,2:b},sh,ohms=ohms,tolerance=.01,note=note,zrodlo=REG)
 else:add(r,'P09_R1' if int(r[1:])<20 else 'P09_R2',symbol('Device','R'),RS,val,f'SMD 1206 1% 0.25W {val}',{1:a,2:b},sh,ohms=ohms,tolerance=.01,note=note)
def cap(r,val,farad,a,b,sh='P09'):
 if val=='100n':add(r,'P09_R1',symbol('Device','C'),CT,val,'K104K15X7RF5TH5 Vishay 100n X7R 50V radial 5mm (owned)',{1:a,2:b},sh,farads=farad,zrodlo=REG)
 else:add(r,'P09_R1',symbol('Device','C'),CS,val,'SMD 1206 X7R 25V 10% '+val,{1:a,2:b},sh,farads=farad)
lvc=symbol('74xx','74LVC125','74LVC125AD');url='https://assets.nexperia.com/documents/data-sheet/74LVC125A.pdf'
add('U1','U_RX1',lvc,SO14,'74LVC125AD','74LVC125AD,118 Nexperia',{1:G,2:'SPI3_SCLK',3:'CLK_BUF',4:G,5:'SPI3_MOSI',6:'MOSI_BUF',7:G,8:'CS1_BUF',9:'TC1_CS',10:G,11:'CS2_BUF',12:'TC2_CS',13:G,14:V},'SPI',url,'Ioff required; all input buffers always enabled.',zrodlo=REG)
add('U2','U_TX',lvc,SO14,'74LVC125AD','74LVC125AD,118 Nexperia',{1:'OE1_N',2:'TC1_MISO',3:'TX1',4:'OE2_N',5:'TC2_MISO',6:'TX2',7:G,8:'NC',9:G,10:V,11:'NC',12:G,13:V,14:V},'SPI',url,'Separate 100R output resistors; inactive channels Hi-Z.',zrodlo=REG)
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
# J_BP (edge A): odd pins GND, even pins signals/supplies; only what P09 uses. 5V_SYS on two pins (S1 spec 5), 3V3_IO on one.
JBP=[(2,'5V_SYS','zasilanie do P09','P02 R4 (przez P12)','5V_SYS: tylko VIN modułów przy JP 2-3 i C5; drugi pin wg S1 §5 (IDC ok. 1 A na styk)'),
     (4,'3V3_IO','zasilanie do P09','P02 R4 (przez P12)','logika U1/U2/U3, pull-upy, VIN modułów przy JP 1-2'),
     (6,'SPI3_SCLK','wejście','P03','SPI3 SCLK, mode 1, 1 MHz; bufor U1'),
     (8,'SPI3_MOSI','wejście','P03','SPI3 MOSI; bufor U1'),
     (10,'SPI3_MISO','wyjście','P03','MISO wspólne; bufor U2 Hi-Z bez wybranego CS, 100R szeregowo'),
     (12,'TC1_CS','wejście','P03','CS termopary 1, aktywny LOW'),
     (14,'TC2_CS','wejście','P03','CS termopary 2, aktywny LOW; przerwa obu CS HIGH >= 1 us między kanałami'),
     (16,'5V_SYS','zasilanie do P09','P02 R4 (przez P12)','drugi pin 5V_SYS (S1 §5)')]
jbp_pins={i:G for i in range(1,17,2)};jbp_pins.update({p:n for p,n,*_ in JBP})
add('J1','J_BP',symbol('Connector_Generic','Conn_02x08_Odd_Even'),IDC16,'J_BP / IDC 2x8','IDC header 2x8 2.54mm angled shrouded, Au (type to be chosen in the purchase list)',jbp_pins,'CONNECT',note='Edge A, centre x=26.5 mm of the slot (S3). Odd pins GND, even pins signals/supplies. Pin 1 towards smaller x. Replaces LV09 (P02-R3/J9) and TEMP (P03-R2/J7).')
mod=custom('MAX31856_MODULE',[( [(1,'VIN','power_in'),(3,'GND','power_in'),(4,'SCK','input'),(6,'SDI','input'),(7,'CS_N','input')],[(2,'3Vo','passive'),(5,'SDO','tri_state'),(8,'FLT_N','output'),(9,'DRDY_N','output')])])
for ch,j in [(1,'J3'),(2,'J4')]:
 add(j,'TC'+str(ch),mod,'P09:MAX31856_XU','TC'+str(ch)+' / MAX31856 XU','Owned MAX31856 XU module, soldered directly by its 1x9 header (no socket)',{1:f'TC{ch}_VIN',2:f'TC{ch}_3VO',3:G,4:'CLK_MODULE',5:f'TC{ch}_MISO',6:'MOSI_MODULE',7:f'TC{ch}_CS_MODULE',8:'NC',9:'NC'},'P09','https://allegro.pl/oferta/max31856-modul-termopary-dla-typow-k-j-n-r-s-t-e-b-19-bitowy-modul-xu-18805671895','Pinout photo6: VIN/3Vo/GND/SCK/SDO/SDI/CS/FLT/DRDY. Pitch/body/hole fit must be measured. 1.10.2026 (user decision): soldered directly by the factory male header (plastic spacer under the module), no socket and no support posts; header pins cut to <= 1.5 mm under P09 (S1 section 4). FLT_N (8) and DRDY_N (9) are unconnected in R2 (R1 test pads TP10..TP13 dropped; the contract has no spare wire). No Adafruit electrical equivalence assumed.',zrodlo=OWN)
 add('JP'+str(ch),'ADDED_VIN_SELECT',symbol('Connector_Generic','Conn_01x03'),HDR3,'VIN SELECT / OPEN','Header 1x3 + one shunt (not fitted initially)',{1:V,2:f'TC{ch}_VIN',3:A5},'P09',note='One shunt: 1-2=3.3V initial qualification; 2-3=5V ONLY after regulator and level-shifter qualification. Never two shunts. Power off before change.')
# Service strip (edge B): GND at both ends, every other pin through a 1k series resistor placed at the node (all P09 nodes are rails or logic).
SRV=[('3V3_IO','szyna logiki i VIN przy JP 1-2: pobór, brak zwarć, minimum przy zimnym i ciepłym modułem'),
     ('5V_SYS','szyna 5 V (VIN przy JP 2-3), obecność i spadek pod obciążeniem'),
     ('TC1_VIN','VIN modułu TC1: wybór JP1 (3,3 V albo 5 V), kwalifikacja modułu'),
     ('TC2_VIN','VIN modułu TC2: wybór JP2'),
     ('TC1_3VO','3Vo modułu TC1: VDD MAX31856 3,0-3,6 V (tylko pomiar, nie zasilać)'),
     ('TC2_3VO','3Vo modułu TC2: VDD MAX31856 3,0-3,6 V (tylko pomiar)'),
     ('CS1_BUF','CS1 za buforem U1: setup/hold, przerwa obu CS HIGH >= 1 us'),
     ('CS2_BUF','CS2 za buforem U1'),
     ('OE1_N','wybór MISO TC1 (Y2 U3, aktywny LOW): tablica prawdy CS'),
     ('OE2_N','wybór MISO TC2 (Y1 U3, aktywny LOW)'),
     ('SPI3_MISO','wspólne MISO: TC1, TC2, oba CS HIGH i LOW; Hi-Z przy nieaktywnych buforach')]
srv_pins={1:G,13:G};srv_r={}
for k,(net,_) in enumerate(SRV,2):
 r='R'+str(19+k-1);srv_r[net]=r;srv_pins[k]='SRV_'+net
 res(r,'1K',1000,net,'SRV_'+net,'CONNECT','Serwis: kołek przez 1k przy węźle, zsunięta sonda nic nie uszkodzi')
add('J2','J_SRV',symbol('Connector_Generic','Conn_01x13'),HDR13,'SERWIS / goldpin 1x13','Goldpin 1x13 2.54mm angled (buy angled strip, owned 1x40 is straight)',srv_pins,'CONNECT',note='Edge B, x=10..43 mm of the slot; pin 1 towards larger x (angled strip on the top side, pins out of edge B: the footprint fixes the order); pins stick ~6 mm beyond the edge. GND at both ends.')
if __name__=='__main__':write_tables();print(len(PARTS),'parts')
