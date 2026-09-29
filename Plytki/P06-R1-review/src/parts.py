"""P06-R1: explicit circuit, physical SOIC pinouts and wire endpoints.
Baseline v6.1 preserved at interfaces; see docs/ZMIANY.md for deliberate changes.
"""
from cadlib import *
import csv,shutil
FP=P/'eda/libraries/P06.pretty';FP.mkdir(parents=True,exist_ok=True);PARTS={}
URL={k:v['url'] for k,v in json.loads((P/'reference/datasheets/sources.json').read_text()).items()}
exec((P/'src/helpers.txt').read_text(encoding='utf-8'))
G='GND';V='3V3_P06';A5='5VA_P06'
RFP=copyfp('Resistor_THT','R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal')
R1W=copyfp('Resistor_THT','R_Axial_DIN0411_L9.9mm_D3.6mm_P15.24mm_Horizontal')
R2W=copyfp('Resistor_THT','R_Axial_DIN0617_L17.0mm_D6.0mm_P25.40mm_Horizontal')
C0805=copyfp('Capacitor_SMD','C_0805_2012Metric')
CP=copyfp('Capacitor_THT','CP_Radial_D8.0mm_P3.50mm');CP5=copyfp('Capacitor_THT','CP_Radial_D5.0mm_P2.00mm')
CF=copyfp('Capacitor_THT','C_Rect_L7.2mm_W5.0mm_P5.00mm')
SO8=copyfp('Package_SO','SOIC-8_3.9x4.9mm_P1.27mm');SO14=copyfp('Package_SO','SOIC-14_3.9x8.7mm_P1.27mm')
DIP8=copyfp('Package_DIP','DIP-8_W7.62mm');DIP14=copyfp('Package_DIP','DIP-14_W7.62mm')
TO92=copyfp('Package_TO_SOT_THT','TO-92_Inline_Wide')
DIO=copyfp('Diode_THT','D_DO-41_SOD81_P10.16mm_Horizontal')
def local(name):
 shutil.copy2(P/'input/footprints'/(name+'.kicad_mod'),FP/(name+'.kicad_mod'));return 'P06:'+name
C100=local('C_Vishay_K15_H5_P5');TP=local('TestPad_1')
import make_footprints
def add(ref,src,sym,fp,value,mpn,pins,sheet,url='',note='',on_board=True,**extra):
 PARTS[ref]=dict(ref=ref,source_ref=src,symbol=sym,footprint=fp,display=value,value=value,mpn=mpn,pins={str(k):v for k,v in pins.items()},sheet=sheet,url=url,note=note,qty=1,on_board=on_board,**extra)
SR=symbol('Device','R');SC=symbol('Device','C');SCP=symbol('Device','C_Polarized')
def res(r,src,val,ohms,a,b,sh,tol=.01,power=0.25):
 fp=R2W if power==2 else R1W if power==1 else RFP
 add(r,src,SR,fp,val+(' / 0.1%' if tol==.001 else ''),f'Metal film {val} {tol*100:g}% {power:g}W',{1:a,2:b},sh,ohms=ohms,tolerance=tol,power_w=power,note='Single full-value resistor; TCR <=25ppm/K for 0.1% parts.')
def cap(r,src,val,farad,a,b,sh,smd=False,film=False):
 add(r,src,SC,CF if film else C0805 if smd else C100,val,'MKS2C034701C00KSSD' if film else ('C0G 50V 5% ' if farad<1e-8 else 'X7R 50V 10% ')+val,{1:a,2:b},sh,farads=farad)
ina=custom('INA240A2_D_SOIC',[
 ([(8,'IN+','input'),(1,'IN-','input')],[(5,'OUT','output')]),
 ([(6,'VS','power_in'),(7,'REF1','input'),(3,'REF2','input')],[(2,'GND','power_in'),(4,'NC','no_connect')])])
add('U1','U37',ina,SO8,'INA240A2','INA240A2EDRQ1',{1:'INA_MINUS',2:G,3:'REF_BUF',4:'NC',5:'I_L_OUT',6:A5,7:'REF_BUF',8:'INA_PLUS'},'ANA',URL['INA240.pdf'],'SOIC D pinout. Direct hand soldering, 1.27 mm pitch; no socket in Kelvin path.')
add('U2','U39',symbol('Amplifier_Operational','MCP6022'),DIP8,'MCP6022-I/P','MCP6022-I/P',{1:'ADC_BUF',2:'ADC_BUF',3:'I_DIV',4:G,5:'REF25',6:'REF_BUF',7:'REF_BUF',8:V},'ANA',URL['MCP6022.pdf'])
adc=custom('MCP3201_B_P',[( [(1,'VREF','power_in'),(2,'IN+','input'),(3,'IN-','input'),(4,'VSS','power_in')],[(8,'VDD','power_in'),(7,'CLK','input'),(6,'DOUT','tri_state'),(5,'CS_N','input')])])
add('U3','U38',adc,DIP8,'MCP3201-BI/P','MCP3201-BI/P',{1:'REF25',2:'ADC_AIN',3:G,4:G,5:'CS_LOCAL_N',6:'ADC_DOUT',7:'CLK_LOCAL',8:V},'ADC',URL['MCP3201.pdf'])
ldo=custom('MCP1702_TO92',[( [(2,'VIN','power_in'),(1,'GND','power_in')],[(3,'VOUT','power_out')])])
add('U4','U40',ldo,TO92,'MCP1702-3302E/TO','MCP1702-3302E/TO',{1:G,2:A5,3:V},'P06',URL['MCP1702.pdf'])
lvc=symbol('74xx','74LVC125','74LVC125AD')
add('U5','U43',lvc,SO14,'74LVC125AD','74LVC125AD,118 (Nexperia)',{1:G,2:'CS_ILOG_N',3:'CS_LOCAL_N',4:G,5:'ADC_SCLK',6:'CLK_LOCAL',7:G,8:'DOUT_TX',9:'ADC_DOUT',10:'CS_LOCAL_N',11:'NC',12:G,13:V,14:V},'DIG',URL['LVC125.pdf'],'Ioff required. Unused OE tied to LOCAL rail, not LV06.3.')
add('U6','U46',lvc,SO14,'74LVC125AD','74LVC125AD,118 (Nexperia)',{1:G,2:'SUP5_RAW',3:'SUP5_N',4:G,5:'SW_SENSE',6:'SHUNT_ENABLED',7:G,8:'LOGGER_OK_TX',9:'LOGGER_OK_LOCAL',10:G,11:'NC',12:G,13:V,14:V},'READY',URL['LVC125.pdf'],'5V-tolerant input for 5V supervisor and switch; Ioff on READY output.')
add('U7','U41',symbol('74xx','74LS08','SN74HC08N'),DIP14,'SN74HC08N','SN74HC08N',{1:'SUP3_N',2:'SUP5_N',3:'RAILS_OK',4:'RAILS_OK',5:'SHUNT_ENABLED',6:'LOGGER_OK_LOCAL',7:G,8:'NC',9:G,10:G,11:'NC',12:G,13:G,14:V},'READY',URL['HC08.pdf'])
sup=custom('MCP120_D_TO',[( [(2,'VDD','power_in')],[(1,'RESET_N','open_collector'),(3,'VSS','power_in')])])
for r,src,mpn,rail,out in [('U8','U44','MCP120-300DI/TO',V,'SUP3_N'),('U9','U45','MCP120-450DI/TO',A5,'SUP5_RAW')]:
 add(r,src,sup,TO92,mpn,mpn,{1:out,2:rail,3:G},'READY',URL['MCP120.pdf'],'D bondout: reset=1, VDD=2, GND=3. Open drain.')
ref=custom('MCP1525_TO92',[( [(3,'VIN','power_in'),(1,'GND','power_in')],[(2,'VOUT','power_out')])])
add('U10','U42',ref,TO92,'MCP1525-I/TO','MCP1525-I/TO',{1:G,2:'REF25',3:V},'ANA',URL['MCP1525.pdf'],'TO92: 1 GND, 2 OUT, 3 IN; not the SOT23 pin order.')
sh=symbol('Device','R_Shunt','PBV_4terminal')
add('RSH1','X24',sh,'P06:PBV_2317_F1','5m / 0.5% / 3W','PBV-R005-F1-0.5',{1:'ECU_P1',2:'K_PLUS',3:'K_MINUS',4:'EGR_P1'},'FORCE',URL['PBV.pdf'],'Numbering assigned left to right viewing marked face. Force outer pins, Kelvin inner. 3 W without heatsink; do not claim 10 W without heatsink.',ohms=.005,tolerance=.005,power_w=3)
sw=symbol('Switch','SW_DPDT_x2','NKK_S6A_DPDT')
add('SW1','X36',sw,'P06:OFFBOARD','S6A / BYPASS-MEASURE','S6A (NKK)',{1:'NC',2:'ECU_P1',3:'EGR_P1',4:A5,5:'SW_RAW',6:G},'FORCE','https://www.nkkswitches.com.hk/documents/products/series_pdf/toggle_S.pdf','Panel mount. BYPASS 2-3,5-6; MEASURE 2-1,5-4. No motor current in pole B. Switch only with ignition off.',False)
# Current path and analog scaling.
for a in [('R1','R22','10R',10,'K_PLUS','INA_PLUS'),('R2','R23','10R',10,'K_MINUS','INA_MINUS'),('R3','R28','5K1',5100,'I_L_OUT','I_DIV'),('R4','R29','5K1',5100,'I_DIV',G)]:res(*a,'ANA',tol=.001)
res('R5','R25','47R',47,'ADC_BUF','ADC_AIN','ADC')
res('R6','R26','1R',1,'5V_SYS',A5,'P06',power=1)
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
res('R21','ADD_CONTACT_WETTING','39R',39,'SW_RAW',G,'FORCE',power=2)
res('R22','ADD_CONTACT_SER','1K',1000,'SW_RAW','SW_SENSE','READY')
res('R23','ADD_CONTACT_PD','100K',100000,'SW_SENSE',G,'READY')
res('R24','ADD_LOCAL_BLEED','1K',1000,V,G,'P06')
cap('C1','C_DIV_L','470n / PET',470e-9,'I_DIV',G,'ANA',film=True)
cap('C2','C_AIN','470p / C0G',470e-12,'ADC_AIN',G,'ADC')
add('C3','C28',SCP,CP,'470u / 16V','EEUFR1C471',{1:A5,2:G},'P06',farads=470e-6,note='D8 pitch3.5. Verify supplier body height <=12 mm.')
add('C4','C_LDO_OUT',SCP,CP5,'4.7u / 50V','EEUFR1H4R7',{1:V,2:G},'P06',farads=4.7e-6)
add('C5','C_REF',SCP,CP5,'4.7u / 50V','EEUFR1H4R7',{1:'REF25',2:G},'ANA',farads=4.7e-6)
cap('C16','ADD_ADC_REF_HF','100n',1e-7,'REF25',G,'ADC',smd=True)
add('D2','ADD_REF_DISCHARGE',symbol('Device','D_Schottky'),copyfp('Diode_THT','D_DO-35_SOD27_P7.62mm_Horizontal'),'BAT85','BAT85,133 (Nexperia)',{1:V,2:'REF25'},'ANA','https://assets.nexperia.com/documents/data-sheet/BAT85.pdf','Discharge of reference capacitor into local rail during power removal.')
for i,(r,rail) in enumerate([('U1',A5),('U2',V),('U3',V),('U4',A5),('U5',V),('U6',V),('U7',V),('U8',V),('U9',A5),('U10',V)],6):
 cap('C'+str(i),'DEC_'+r,'100n',1e-7,rail,G,'P06',smd=True)
add('D1','ADD_LDO_DISCHARGE',symbol('Device','D_Schottky'),DIO,'1N5819','1N5819',{1:A5,2:V},'P06','https://www.vishay.com/docs/88525/1n5817.pdf','Anode on local 3.3 V, cathode on 5VA; output-cap discharge path on supply removal.')
conns=[('J1','J_LV06B','LV06',4,'PTH_LV06',{1:'5V_SYS',2:G,3:'3V3_IO',4:G}),
 ('J2','J_ILOGB','ILOG',8,'PTH_ILOG',{1:'ADC_SCLK',2:'NC',3:'ADC_DOUTA',4:G,5:'CS_ILOG_N',6:G,7:'LOGGER_CURRENT_OK',8:G}),
 ('J3','J_ISERIESB','ISERIES',4,'PTH_ISERIES',{1:'ECU_P1',2:'EGR_P1',3:'NC',4:'NC'}),
 ('J4','ADD_BYPASS_FORCE','SW1 A',2,'PTH_BYPASS',{1:'ECU_P1',2:'EGR_P1'}),
 ('J5','ADD_BYPASS_STATUS','SW1 B',3,'PTH_SWSTATUS',{1:A5,2:'SW_RAW',3:G})]
for r,s,n,c,fp,pins in conns:add(r,s,symbol('Connector_Generic',f'Conn_01x{c:02d}'),'P06:'+fp,n+' / PTH','Soldered harness',pins,'CONNECT',note='PTH solder joint; tie anchor 12 mm. See docs/WIAZKI.md.')
for i,n in enumerate(['5V_SYS',A5,V,'3V3_IO',G,'REF25','REF_BUF','I_L_OUT','ADC_AIN','SUP3_N','SUP5_N','SHUNT_ENABLED','LOGGER_CURRENT_OK','CS_LOCAL_N','CLK_LOCAL'],1):
 add('TP'+str(i),'ADD_TESTPAD',symbol('Connector','TestPoint'),TP,n,'PCB test pad',{1:n},'CONNECT',note='No purchased component. Use a ground spring for analog probes.')
if __name__=='__main__':write_tables();print(len(PARTS),'parts')

