from pathlib import Path
import json,csv,copy,html,collections,textwrap
D=Path(__file__).resolve().parents[1]; H=D/'hardware'
base=json.loads((D/'reference/schemat-S1-v4.1/dane/components.json').read_text(encoding='utf-8'))
mapping={r['Oznaczenie']:r['Zespol docelowy'].split()[0] for r in csv.DictReader((D/'reference/mapa-MOD0.1.csv').open(encoding='utf-8-sig'),delimiter=';') if r['Zrodlo']=='v4.1/S1'}
C={}
def put(board,ref,value,pins,kind='ic',note=''):
    key=board+'_'+ref;assert key not in C,key
    C[key]=dict(board=board,ref=ref,value=value,pins={str(k):v for k,v in pins.items()},kind=kind,note=note)
    return key
def passive(b,r,v,a,z,kind='res'):return put(b,r,v,{1:a,2:z},kind)
def resistor(b,r,v,a,z):return passive(b,r,v,a,z)
def capacitor(b,r,v,a,z='GND'):return passive(b,r,v,a,z,'cap')
def change(b,r,p,n): C[b+'_'+r]['pins'][str(p)]=n
removed=[]
for ref,c in base.items():
    if ref=='M5' or ref.startswith('M5_') or ref in ['D1','KCUR','D_KCUR']:
        removed.append(ref);continue
    b=mapping[ref]
    if b=='PANEL':b='P11'
    if not b.startswith(('P','A')): b='EXT'
    if ref=='U18':b='P05'
    pins=copy.deepcopy(c.get('resolved',c['pins']))
    pins={c.get('numbers',{}).get(p,p):n for p,n in pins.items()}
    for p,n in list(pins.items()):
        if n in ['AGND','DGND','PGND','GND_STAR']:n='GND'
        if n=='5V_A':n='5VA_'+b
        if n=='INTERLOCK' and (ref=='JT_LOOP' or ref=='J_TEST' or ref=='R_PD_INTERLOCK'):n='MECH_OK'
        if b=='P03' and n=='3V3_IO':n='3V3_CORE'
        pins[p]=n
    put(b,ref,c['value'],pins,c['kind'],c.get('note',''))
# Replace the evaluation module with the complete, separately tested-on-paper P01 design.
pwr=json.loads((D/'P01-PROTECT/hardware/components.json').read_text(encoding='utf-8'))
for r,c in pwr.items():put('P01',r,c['value'],{p:('SAFE_N' if n=='FAULT_OC' else n) for p,n in c['pins'].items()},c['kind'],c.get('note',''))
change('P03','M1','38','CURRENT_CS_N');change('P03','M1','41','SCOPE_TRIG')
C['P03_M1']['pins']['3V3']='3V3_CORE'
change('P03','U17',25,'LOGGER_CURRENT_OK');change('P03','U17',7,'MARK')
resistor('P03','R_CURRENT_OK','10k','LOGGER_CURRENT_OK','GND')
# STOP's auxiliary NO contact is a local LED/test point only; GPB6 now handles MARK.
if 'P11_SW_STOP' in C:C['P11_SW_STOP']['note']='NO pomocniczy tylko TP STOP_PRESSED; NC zachowuje tor SAFE_N.'
resistor('P05','R_CH6_ZERO','10k','ADC_CH6','GND')
# Local relay drivers; no remote coil-return wires.
def relay_driver(b,loads):
    pins={str(i):'GND' for i in range(1,9)}|{str(i):'NC' for i in range(11,19)}|{'9':'GND','10':'NC'}
    for i,(signal,coil) in enumerate(loads,1):pins[str(i)]=signal;pins[str(19-i)]=coil
    return pins
C['P05_U18']['pins']=relay_driver('P05',[('MEAS_EN','MEAS_COIL_LOW')])
put('P07','U_RELAY','TBD62083APG DIP18',relay_driver('P07',[('LOCAL_PERMIT','PWR_COIL_LOW')]))
put('P08','U_RELAY','TBD62083APG DIP18',relay_driver('P08',[('SENSOR_LOCAL','SENSOR_COIL_LOW')]))
change('P08','U11',3,'SENSOR_LOCAL')
# Decode the one additional chip select with the already existing bank output.
put('P03','U_CS','SN74HC139N DIP16',{1:'CURRENT_CS_N',2:'MEAS_BANK',3:'GND',4:'CS_ILOG_N',5:'CS_ITEST_N',6:'NC',7:'NC',8:'GND',9:'NC',10:'NC',11:'NC',12:'NC',13:'GND',14:'GND',15:'3V3_CORE',16:'3V3_CORE'})
resistor('P03','R_CS_IDLE','10k','CURRENT_CS_N','3V3_CORE')
capacitor('P03','C_CS','100nF','3V3_CORE')

# Helpers for explicit gates, supervisors, buffers. Every spare input is tied.
def hc08(b,r,gates,supply='3V3_IO'):
    pins={7:'GND',14:supply}
    for p,(a,z,y) in zip([(1,2,3),(4,5,6),(9,10,8),(12,13,11)],gates+[('GND','GND','NC')]*(4-len(gates))):
        pins[p[0]]=a;pins[p[1]]=z;pins[p[2]]=y
    put(b,r,'SN74HC08N DIP14',pins);capacitor(b,'C_'+r,'100nF',supply)
def hc14(b,r,signals,supply='3V3_IO'):
    pins={7:'GND',14:supply}
    for (a,y),(i,o) in zip([(1,2),(3,4),(5,6),(9,8),(11,10),(13,12)],signals+[('GND','NC')]*(6-len(signals))):pins[a]=i;pins[y]=o
    put(b,r,'SN74HC14N DIP14',pins);capacitor(b,'C_'+r,'100nF',supply)
def supervisor(b,r,rail,out,part):
    put(b,r,part+' TO92',{1:out,2:rail,3:'GND'})
    resistor(b,'R_'+r,'10k',out,rail);capacitor(b,'C_'+r,'100nF',rail)
def lvc125(b,r,signals,supply):
    pins={7:'GND',14:supply}
    for (oe,a,y),(en,i,o) in zip([(1,2,3),(4,5,6),(10,9,8),(13,12,11)],signals+[('3V3_IO','GND','NC')]*(4-len(signals))):pins[oe]=en;pins[a]=i;pins[y]=o
    put(b,r,'74LVC125AD Nexperia SO14 + adapter (Ioff)',pins);capacitor(b,'C_'+r,'100nF',supply)

for b,ina,bank,cs in [('P06','U3','L','CS_ILOG_N'),('P07','U2','T','CS_ITEST_N')]:
    # Each current module supplies its own reference and ADC; no analog cable.
    rail='5VA_'+b;v33=b+'_3V3';ref=b+'_REF25';div=b+'_DIV';buf=b+'_BUF';inp=b+'_AIN';localcs=b+'_CS';clk=b+'_CLK';dout=b+'_DOUT'
    resistor(b,'R_AF','1R 0.5W','5V_SYS',rail);capacitor(b,'C_AF','47uF 10V',rail);capacitor(b,'C_AF_HF','100nF',rail)
    put(b,'U_LDO','MCP1702-3302E/TO TO92',{1:'GND',2:rail,3:v33})
    capacitor(b,'C_LDO_IN','1uF X7R',rail);capacitor(b,'C_LDO_OUT','4.7uF X7R',v33)
    put(b,'U_REF','MCP1525-I/TO TO92',{1:'GND',2:ref,3:v33})
    capacitor(b,'C_REF','1uF X7R',ref);capacitor(b,'C_REF_IN','100nF',v33)
    change(b,ina,3,b+'_REF_BUF');change(b,ina,7,b+'_REF_BUF')
    resistor(b,'R_DIV_H','2.00k 0.1% 25ppm','I_'+bank+'_OUT',div)
    resistor(b,'R_DIV_L','2.00k 0.1% 25ppm',div,'GND');capacitor(b,'C_DIV','4.7nF C0G',div)
    put(b,'U_BUF','MCP6022-I/P DIP8',{1:buf,2:buf,3:div,4:'GND',5:ref,6:b+'_REF_BUF',7:b+'_REF_BUF',8:v33})
    capacitor(b,'C_BUF','100nF',v33)
    resistor(b,'R_ADC','47R',buf,inp);capacitor(b,'C_ADC_IN','470pF C0G',inp)
    put(b,'U_ADC','MCP3201-BI/P DIP8',{1:ref,2:inp,3:'GND',4:'GND',5:localcs,6:dout,7:clk,8:v33})
    capacitor(b,'C_ADC','100nF',v33)
    # CS/SCLK receive Ioff protection; MISO can drive the bus only while selected.
    lvc125(b,'U_SPI',[('GND',cs,localcs),('GND','ADC_SCLK',clk),(localcs,dout,'ADC_DOUTA')],v33)
    resistor(b,'R_CS','10k',localcs,v33);resistor(b,'R_MISO','47k',dout,v33)
    supervisor(b,'U_SUP3',v33,b+'_SUP3_N','MCP120-300DI/TO')
    # 5V monitor powered from that rail, open drain to local 3.3V, not 5V.
    put(b,'U_SUP5','MCP120-450DI/TO TO92',{1:b+'_SUP5_N',2:rail,3:'GND'})
    resistor(b,'R_SUP5','10k',b+'_SUP5_N',v33);capacitor(b,'C_SUP5','100nF',rail)
    hc08(b,'U_READY',[(b+'_SUP3_N',b+'_SUP5_N',b+'_RAILS_OK')],v33)
    resistor(b,'R_READY_PD','10k',b+'_RAILS_OK','GND')
    put(b,'J_ANALOG_TP','DEBUG analog only 3-pin',{1:'I_'+bank+'_OUT',2:ref,3:'GND'},'connector','Nie laczyc z DAQ w konfiguracji v5; tylko sonda.')

put('P06','SW_BYPASS','DPDT ON-ON >=10A mechanicznie sprzezone',{1:'ECU_P1',2:'EGR_P1',3:'NC',4:'P06_3V3',5:'NC',6:'SHUNT_ENABLED'},'switch','Pozycja BYPASS zwiera 1-2 i 4-5; MEASURE zwiera 1-3 i 4-6. Bocznik zawsze pozostaje w obwodzie.')
resistor('P06','R_ENABLE_PD','10k','SHUNT_ENABLED','GND')
# second gate in U_READY
for p,n in {4:'P06_RAILS_OK',5:'SHUNT_ENABLED',6:'LOGGER_CURRENT_OK'}.items():change('P06','U_READY',p,n)
# Remove the old independent bypass cap: only coupled switch reports correct state.
for key in list(C):
    if C[key]['board']=='P06' and C[key]['ref'] in ['J_BYPASS','JP_BYPASS']:del C[key]

# Precise OC window is referenced to the local 2.5 V; independent of serial ADC.
for p in [1,7]:change('P07','U4',p,'OC_LOCAL_N')
resistor('P07','R_OC_PULL','10k','OC_LOCAL_N','P07_3V3')
for key in list(C):
    if C[key]['board']=='P07' and C[key]['ref'] in ['R_OC_LT','R_OC_LB','R_OC_HT','R_OC_HB']:del C[key]
resistor('P07','R_OC_L_TOP','10.0k 0.1%','P07_REF_BUF','OC_LOW');resistor('P07','R_OC_L_BOT','15.0k 0.1%','OC_LOW','GND')
put('P07','U_OCREF','MCP6022-I/P DIP8',{1:'OC_HIGH',2:'OC_FB',3:'P07_REF_BUF',4:'GND',5:'GND',6:'OC_UNUSED',7:'OC_UNUSED',8:'5VA_P07'})
resistor('P07','R_OC_FB','10.0k 0.1%','OC_HIGH','OC_FB');resistor('P07','R_OC_G','24.9k 0.1%','OC_FB','GND');capacitor('P07','C_OCREF','100nF','5VA_P07')
# +/-4 A comparator trips latch locally, and separately clears the central ARM latch.
hc14('P07','U_INV',[('OC_LOCAL_N','OC_FAULT'),('MOTOR_PERMIT','PERMIT_N')],'P07_3V3')
put('P07','Q_OC','2N5551 onsemi TO92',{1:'GND',2:'OC_BASE',3:'SAFE_N'},'bjt','pin1 E pin2 B pin3 C; pull-up tylko na SAFE')
resistor('P07','R_QOC_B','10k','OC_FAULT','OC_BASE');resistor('P07','R_QOC_PD','100k','OC_BASE','GND')
hc08('P07','U_GATE', [('P07_RAILS_OK','OC_LOCAL_N','LOCAL_CLEAR_N'),('ARM_CLK','PERMIT_N','LOCAL_ARM_CLK'),('MOTOR_PERMIT','OC_GOOD','PERMIT_ARMED'),('PERMIT_ARMED','P07_RAILS_OK','LOCAL_PERMIT')],'P07_3V3')
put('P07','U_OC_LATCH','SN74HC74N DIP14',{1:'LOCAL_CLEAR_N',2:'PERMIT_N',3:'ARM_CLK',4:'P07_3V3',5:'OC_GOOD',6:'NC',7:'GND',8:'NC',9:'NC',10:'P07_3V3',11:'GND',12:'GND',13:'GND',14:'P07_3V3'})
capacitor('P07','C_OC_LATCH','100nF','P07_3V3')
hc08('P07','U_PWM',[('PWM_OUT','LOCAL_PERMIT','PWM_LOCAL'),('P07_RAILS_OK','P07_RAILS_OK','DRIVE_OK')],'P07_3V3')
change('P07','M2','VDD','LOCAL_PERMIT')
change('P07','R_PWM',1,'PWM_LOCAL')
for n in ['MOTOR_PERMIT','ARM_CLK','PWM_OUT','MOTOR_INA','MOTOR_INB','LOCAL_PERMIT']:
    resistor('P07','R_PD_'+n,'10k',n,'GND')

# DAQ rail monitor from S1 gets a local positive READY; open drain faults still propagate.
for p in [1,7]:change('P05','U6',p,'DAQ_RAIL_N')
resistor('P05','R_RAIL_PULL','10k','DAQ_RAIL_N','3V3_IO')
supervisor('P05','U_SUP3','3V3_IO','P05_SUP3_N','MCP120-300DI/TO')
put('P05','U_SUP5','MCP120-450DI/TO TO92',{1:'DAQ_RAIL_N',2:'5V_SYS',3:'GND'})
hc08('P05','U_READY',[('DAQ_RAIL_N','P05_SUP3_N','DAQ_OK')])
resistor('P05','R_READY_PD','10k','DAQ_OK','GND')
# PSU and SENSOR positive READY do not depend on their permits.
for b,out in [('P02','PSU_OK'),('P08','SENSOR_OK')]:
    supervisor(b,'U_SUP3','3V3_IO',b+'_SUP3_N','MCP120-300DI/TO')
    put(b,'U_SUP5','MCP120-450DI/TO TO92',{1:b+'_SUP5_N',2:'5V_SYS',3:'GND'})
    resistor(b,'R_SUP5','10k',b+'_SUP5_N','3V3_IO');capacitor(b,'C_SUP5','100nF','5V_SYS')
    hc08(b,'U_READY',[(b+'_SUP3_N',b+'_SUP5_N',out)]+([('SENSOR_PERMIT',out,'SENSOR_LOCAL')] if b=='P08' else []))
    resistor(b,'R_READY_PD','10k',out,'GND')
resistor('P08','R_PERMIT_PD','10k','SENSOR_PERMIT','GND')
# A supervisor cannot actively sink at VDD=0. Pull its RESET to the monitored
# rail, then translate the 5V logic through a tolerant Ioff buffer. This also
# defines the zero-volt state when the independent 3.3V rail is still alive.
for b in ['P02','P06','P07','P08']:
    raw=b+'_SUP5_RAW';rail='5VA_'+b if b in ['P06','P07'] else '5V_SYS'
    v33=b+'_3V3' if b in ['P06','P07'] else '3V3_IO'
    change(b,'U_SUP5',1,raw);change(b,'R_SUP5',1,raw);change(b,'R_SUP5',2,rail)
    lvc125(b,'U_SUPBUF',[('GND',raw,b+'_SUP5_N')],v33)
change('P05','U_SUP5',1,'P05_SUP5_RAW')
resistor('P05','R_SUP5_RAW','10k','P05_SUP5_RAW','5V_SYS')
lvc125('P05','U_SUPBUF',[('GND','P05_SUP5_RAW','P05_SUP5_N')],'3V3_IO')
for pin,net in {3:'DAQ_TWO_OK',4:'DAQ_TWO_OK',5:'P05_SUP5_N',6:'DAQ_OK'}.items():change('P05','U_READY',pin,net)

# Final interlock is an electrical gate tree, tested from this netlist.
hc08('P04','U_LINK', [('PSU_OK','DAQ_OK','OK_A'),('DRIVE_OK','SENSOR_OK','OK_B'),('CORE_LINK','PG_LINK','OK_C'),('OK_A','OK_B','OK_AB')])
hc08('P04','U_LINK2',[('OK_AB','OK_C','MODULES_OK'),('MODULES_OK','MECH_OK','INTERLOCK')])
for n in ['PSU_OK','DAQ_OK','DRIVE_OK','SENSOR_OK','CORE_LINK','PG_LINK','MECH_OK','INTERLOCK']:
    resistor('P04','R_LINK_'+n,'10k',n,'GND')
put('P01','J_PRES','Obecnosc P01 - petla 2-pin',{1:'PG_SEND',2:'PG_LINK'},'connector','Zewrzec styki na PCB P01; niezaleznie od J4 FAULT.')
passive('P01','W_PRES','0R','PG_SEND','PG_LINK','wire')
passive('P04','W_SEND','0R','3V3_IO','PG_SEND','wire')
passive('P03','W_LINK','0R','3V3_CORE','CORE_LINK','wire')

# Source-series damping footprints on CLK/CS; active receivers have Ioff buffers.
# CORE -> DAQ: eight unidirectional signals, DAQ -> CORE: two.
# All MCU-facing inputs end in buffers powered by CORE's own regulator.
def buffer_group(b,r,items,supply):
    for j in range(0,len(items),4):lvc125(b,r+str(j//4+1),items[j:j+4],supply)
inbound=['ADC_DOUTA','ADC_BUSY','SPI3_MISO','CAN_RX','HW_ARMED','INTERLOCK','LOGGER_CURRENT_OK','SENSOR_FAULT_N','ENA_DIAG','ENB_DIAG','LOGGER_CLEAR','TEST_PRESENT','TEST_KEY']
for n in inbound:
    for ref in ['M1','U17']:
        for p,val in C['P03_'+ref]['pins'].items():
            if val==n:C['P03_'+ref]['pins'][p]=n+'_CORE'
buffer_group('P03','U_IN', [('GND',n,n+'_CORE') for n in inbound],'3V3_CORE')
# Positive ready GPIO A4 pulldown must be on buffer input too. A buffer output is push-pull.
change('P03','R_CURRENT_OK',1,'LOGGER_CURRENT_OK')
outs=['ADC_SCLK','ADC_SDI','ADC_CS','ADC_CONVST','ADC_RESET','MEAS_EN']
for n in outs:
    for key,c in C.items():
        if c['board']=='P05':
            for p,val in list(c['pins'].items()):
                if val==n:c['pins'][p]=n+'_P05'
buffer_group('P05','U_RX',[('GND',n,n+'_P05') for n in outs],'3V3_IO')
for n in ['ADC_CS_P05']:
    resistor('P05','R_'+n,'10k',n,'3V3_IO')
# Resistor fallback for mode signals at their receiver, no remote pull-up used for permits.
for b,n in [('P05','MEAS_EN_P05'),('P05','ADC_CONVST_P05'),('P05','ADC_RESET_P05')]:resistor(b,'R_LOCAL_'+n,'10k',n,'GND')
# CAN/TEMP receiver-side input protection; MISO enable retains tri-state behaviour.
tempnets=['SPI3_SCLK','SPI3_MOSI','TC1_CS','TC2_CS']
for n in tempnets:
    for key,c in C.items():
        if c['board']=='P09':
            for p,val in list(c['pins'].items()):
                if val==n:c['pins'][p]=n+'_P09'
buffer_group('P09','U_RX',[('GND',n,n+'_P09') for n in tempnets],'3V3_IO')
for j in [1,2]:
    c=C['P09_TC'+str(j)]
    for p,n in list(c['pins'].items()):
        if n=='SPI3_MISO':c['pins'][p]='TC'+str(j)+'_MISO'
lvc125('P09','U_TX',[('TC1_CS_P09','TC1_MISO','SPI3_MISO'),('TC2_CS_P09','TC2_MISO','SPI3_MISO')],'3V3_IO')
for key,c in C.items():
    if c['board']=='P05' and c['ref']=='U1':
        for p,n in list(c['pins'].items()):
            if n=='ADC_DOUTA':c['pins'][p]='AD_DOUT_LOCAL'
lvc125('P05','U_TX',[('ADC_CS_P05','AD_DOUT_LOCAL','ADC_DOUTA')],'3V3_IO')
# Protect logic inputs when a module is absent/unpowered; all inputs below are unidirectional.
for b,names,supply in [
    ('P04',['PWM','HEARTBEAT','MCU_ARM','SENSOR_ENABLE','CORE_LINK','SUP_N','PSU_OK','DAQ_OK','DRIVE_OK','SENSOR_OK','PG_LINK'],'3V3_IO'),
    ('P07',['MOTOR_PERMIT','ARM_CLK','PWM_OUT','MOTOR_INA','MOTOR_INB'],'P07_3V3'),
    ('P08',['SENSOR_PERMIT'],'3V3_IO'),('P10',['CAN_TX'],'3V3_IO')]:
    for n in names:
        for c in C.values():
            if c['board']==b:
                for p,val in list(c['pins'].items()):
                    if val==n:c['pins'][p]=n+'_'+b
    buffer_group(b,'U_RX',[('GND',n,n+'_'+b) for n in names],supply)
# CPU reset pull-up must belong to its own voltage domain.
C['P03_R_SUP_PU']=C.pop('P04_R_SUP_PU');C['P03_R_SUP_PU']['board']='P03'
C['P03_R_SUP_PU']['pins']={'1':'SUP_N','2':'3V3_CORE'}
C['P03_U5']=C.pop('P04_U5');C['P03_U5']['board']='P03'
C['P03_U5']['pins']={'1':'SUP_N','2':'GND','3':'3V3_CORE','4':'NC','5':'3V3_CORE','6':'3V3_CORE'}
C['P03_C_DEC_U5_6']=C.pop('P04_C_DEC_U5_6');C['P03_C_DEC_U5_6']['board']='P03'
C['P03_C_DEC_U5_6']['pins']={'1':'3V3_CORE','2':'GND'}
# Explicit low states on disconnected external positive-ready inputs, before buffers.
for n in ['PSU_OK','DAQ_OK','DRIVE_OK','SENSOR_OK','CORE_LINK','PG_LINK','PWM','HEARTBEAT','MCU_ARM','SENSOR_ENABLE']:
    resistor('P04','R_EXT_'+n,'10k',n,'GND')
resistor('P04','R_EXT_SUP_N','100k','SUP_N','GND')
for n in ['MOTOR_PERMIT','ARM_CLK','PWM_OUT','MOTOR_INA','MOTOR_INB']:
    resistor('P07','R_EXT_'+n,'10k',n,'GND')
resistor('P08','R_EXT_SENSOR','10k','SENSOR_PERMIT','GND')
resistor('P08','R_FAULT_PU','10k','SENSOR_FAULT_N','3V3_IO')
for b,n,rail in [('P05','ADC_CS','3V3_IO'),('P06','CS_ILOG_N','P06_3V3'),('P07','CS_ITEST_N','P07_3V3'),('P09','TC1_CS','3V3_IO'),('P09','TC2_CS','3V3_IO')]:
    resistor(b,'R_EXT_'+n,'10k',n,rail)
for n in ['ADC_SCLK','ADC_SDI','ADC_CONVST','ADC_RESET','MEAS_EN']:
    resistor('P05','R_EXT_'+n,'10k',n,'GND')
# All externally pulled chip selects terminate in Ioff outputs, including when CORE is off.
coreouts=['ADC_CS','ADC_SCLK','ADC_SDI','ADC_CONVST','ADC_RESET','MEAS_EN','CS_ILOG_N','CS_ITEST_N','SPI3_SCLK','SPI3_MOSI','TC1_CS','TC2_CS']
for n in coreouts:
    for ref in ['M1','U17','U_CS']:
        for p,val in list(C['P03_'+ref]['pins'].items()):
            if val==n:C['P03_'+ref]['pins'][p]=n+'_SRC'
buffer_group('P03','U_OUT',[('GND',n+'_SRC',n) for n in coreouts],'3V3_CORE')

# Connector schedule is authoritative for the new PCB revision, old exterior adapters remain physical reference.
W=[];K=[]
def cable(name,a,b,nets,kind='IDC',maxcm=10):
    # pin-numbering is straight-through, viewed into PCB header, triangle=1.
    key={'DAQ':2,'SAFE':4,'ILOG':2,'DIR':4,'ITEST':2,'DRIVE':2,'TEMP':4,'SENSOR':2,'CAN':4,'SFAULT':3,'DAQOK':4,'PSUOK':5}.get(name)
    if name in ['SFAULT','DAQOK','PSUOK']:nets=nets+['NC']*4
    if name in ['SUPPLY','VMOTOR']:nets=nets+['NC']
    if name=='ISERIES':nets=nets+['NC']*2
    if name=='TMOTOR':nets=nets+['NC']*3
    if key:assert nets[key-1] in ['GND','NC']
    label=kind+' '+str(len(nets))+'p'+(f' KEY{key}' if key else '')
    for end,board in [('A',a),('B',b)]:put(board,'J_'+name+end,label,{i+1:n for i,n in enumerate(nets) if i+1!=key},'connector',name)
    for i,n in enumerate(nets,1):
        if i!=key:W.append(dict(cable=name,from_board=a,from_ref='J_'+name+'A',from_pin=i,to_board=b,to_ref='J_'+name+'B',to_pin=i,net=n,connector=kind,max_cm=maxcm))
    K.append(dict(cable=name,ends=a+'/'+b,family=kind,positions=len(nets),key_pin=key or '',blocking=(f'Usuniety pin {key} obu gniazd; zaslepka pozycji {key} obu wtykow IDC' if key else 'Polaryzacja korpusu / liczba pozycji'),compatible_group=('LV' if name.startswith('LV') else ('VPROT' if name in ['SUPPLY','VMOTOR'] else name))))
def digital(signals):return [x for n in signals for x in (n,'GND')]
cable('DAQ','P03','P05',digital(['ADC_SCLK','ADC_SDI','ADC_DOUTA','ADC_CS','ADC_CONVST','ADC_BUSY','ADC_RESET','MEAS_EN']),maxcm=10)
cable('ILOG','P03','P06',digital(['ADC_SCLK','ADC_DOUTA','CS_ILOG_N','LOGGER_CURRENT_OK']),maxcm=10)
cable('ITEST','P03','P07',digital(['ADC_SCLK','ADC_DOUTA','CS_ITEST_N']),maxcm=10)
cable('SAFE','P03','P04',digital(['PWM','HEARTBEAT','MCU_ARM','HW_ARMED','INTERLOCK','SENSOR_ENABLE','CORE_LINK','SUP_N']),maxcm=15)
cable('DRIVE','P04','P07',digital(['MOTOR_PERMIT','PWM_OUT','ARM_CLK','DRIVE_OK','SAFE_N']),maxcm=15)
cable('DIR','P03','P07',digital(['MOTOR_INA','MOTOR_INB','ENA_DIAG','ENB_DIAG']),maxcm=15)
cable('SENSOR','P04','P08',digital(['SENSOR_PERMIT','SENSOR_OK']),maxcm=15)
cable('SFAULT','P03','P08',digital(['SENSOR_FAULT_N']),maxcm=15)
cable('DAQOK','P04','P05',digital(['DAQ_OK']),maxcm=15)
cable('PSUOK','P04','P02',digital(['PSU_OK']),maxcm=15)
cable('PG','P04','P01',['3V3_IO','SAFE_N','GND','PG_SEND','PG_LINK','GND'],'MicroFit-6',20)
cable('TEMP','P03','P09',digital(['SPI3_SCLK','SPI3_MOSI','SPI3_MISO','TC1_CS','TC2_CS']),maxcm=10)
cable('CAN','P03','P10',digital(['CAN_TX','CAN_RX']),maxcm=15)
# Panel / interlock harness explicitly lists all monitor and actual safety contacts.
cable('PANELSAFE','P04','P11',['3V3_IO','GND','TEST_KEY','MECH_OK','LOGGER_CLEAR','TEST_PRESENT','STOP_NC_OUT','NC','ARM_CONTACT','GND'],'MicroFit-10',30)
cable('PANELCORE','P03','P11',['GND','MARK','TEST_KEY','LOGGER_CLEAR','TEST_PRESENT','STATUS_LED','N_J_SCOPE_HOT','GND'],'MicroFit-8',30)
cable('SUPPLY','P01','P02',['VPROT','GND'],'MSTB 5.08 >=12A',20)
cable('VMOTOR','P02','P07',['VPROT','GND'],'MSTB 5.08 >=12A',20)
for b in ['P03','P04','P05','P06','P07','P08','P09','P10']:
    cable('LV'+b[1:],'P02',b,['5V_SYS','GND','3V3_IO','GND'],'MicroFit-4',20)
cable('TAPS','P11','P05',['TAP_P1','TAP_P3','TAP_P4','TAP_P5','TAP_P6','GND'],'MSTB 3.81 ANALOG',5)
cable('ISERIES','P11','P06',['ECU_P1','EGR_P1'],'MSTB 5.08 >=12A yellow',15)
cable('TMOTOR','P07','P11',['T_EGR_P1','T_EGR_P3'],'MSTB 5.08 >=12A red',15)
cable('TSENSOR','P08','P11',['5V_SENSOR','AGND_SENSOR'],'MicroFit-2 blue',15)
# Outside adapters enter exclusively through their keyed panel connector.
for name,a,panel,key in [('EXT_T','AT','J_TEST','A'),('EXT_L1','AL1','J_L1','B'),('EXT_L2','AL2','J_L2','C')]:
    pins=copy.deepcopy(C['P11_'+panel]['pins'])
    C['P11_'+panel]['value']='DEUTSCH DT04-12P'+key+' + uchwyt panelowy, styki size16'
    put(a,'PLUG','DEUTSCH DT06-12S'+key+' plug, contacts size16',pins,'connector','Jedyny port zewnetrzny adaptera; klucz '+key)
    for pin,net in pins.items():W.append(dict(cable=name,from_board='P11',from_ref=panel,from_pin=pin,to_board=a,to_ref='PLUG',to_pin=pin,net=net,connector='DEUTSCH DT12 key '+key,max_cm=100))
    K.append(dict(cable=name,ends='P11/'+a,family='DEUTSCH DT12',positions=12,key_pin=key,blocking='Fabryczny klucz '+key,compatible_group=name))
cable('BAT','EXT','P01',['BAT_FUSED','GND'],'MSTB 5.08 >=12A black',20)
# Remove abandoned current-bank coil pieces and the former STOP sense resistor.
for k in list(C):
    c=C[k]
    if (c['board']=='P05' and c['kind'] not in ['ic','connector'] and any(n in ['KCUR_COIL_LOW','MEAS_BANK'] for n in c['pins'].values())) or k=='P03_R_PD_STOP_PRESSED':del C[k]
# P01 is a hierarchical subassembly: local names cannot alias another board's LED/gate.
for c in C.values():
    if c['board']=='P01':
        c['pins']={p:(n if n in ['GND','VPROT','BAT_FUSED','3V3_IO','SAFE_N','PG_SEND','PG_LINK','NC'] else 'P01_'+n) for p,n in c['pins'].items()}

# Four mounting holes have a common coordinate convention; large boards use a larger envelope.
for ref in ['SW_LOG1','SW_LOG2']:
    C['P11_'+ref]['value']='Zespol detekcji wtyku: 2 styki NC, osobna mechanika'
    C['P11_'+ref]['note']='DT nie ma wbudowanych stykow detekcji. Dwa styki NC rozwierane wsunieciem wtyku; uchwyt sprawdzic przed integracja.'
C['P11_SW_TEST']['value']='Mikrowylacznik NO detekcji wtyku TEST + uchwyt'
C['P11_SW_TEST']['note']='Osobny element mechaniczny; nie jest czescia zlacza DT.'
put('P00','J_PWR','Zasilanie tylko 3.3V stanowiskowe',{1:'P00_V33',2:'P00_GND'},'connector','P00 odpinany przed integracja; GND polaczyc z badana PCB.')
put('P00','U1','TLC555CP DIP8',{1:'P00_GND',2:'P00_RC',3:'P00_OSC',4:'P00_V33',5:'P00_CTRL',6:'P00_RC',7:'P00_DIS',8:'P00_V33'})
resistor('P00','R1','4.7k','P00_V33','P00_DIS');resistor('P00','R2','68k','P00_DIS','P00_RC')
capacitor('P00','C1','100nF','P00_RC','P00_GND');capacitor('P00','C2','10nF','P00_CTRL','P00_GND');capacitor('P00','C3','100nF','P00_V33','P00_GND')
resistor('P00','R3','1k','P00_OSC','P00_HEART')
put('P00','J_HEART','Generator heartbeat test only',{1:'P00_HEART',2:'P00_GND'},'connector')
for i in range(1,9):
    put('P00','SW'+str(i),'SPDT ON-ON simulation only',{1:'P00_GND',2:'P00_S'+str(i),3:'P00_V33'},'switch')
    resistor('P00','RS'+str(i),'1k','P00_S'+str(i),'P00_OUT'+str(i))
    put('P00','J'+str(i),'Gniazdo probne 2-pin',{1:'P00_OUT'+str(i),2:'P00_GND'},'connector')
mods=[]
for b,name,x,y in [('P01','PROTECT',100,160),('P02','PSU',80,70),('P03','CORE',110,90),('P04','SAFE',100,80),('P05','DAQ',110,100),('P06','I-LOGGER',80,65),('P07','DRIVE',120,100),('P08','SENSOR',65,55),('P09','TEMP',75,55),('P10','CAN',60,50),('P11','PANEL',100,60)]:
    mods.append(dict(id=b,function=name,interface='M1',hw_rev='5.0',envelope_mm=[x,y],mounting_holes_mm=[[5,5],[x-5,5],[5,y-5],[x-5,y-5]],status='placement_and_routing_not_done'))
(H/'modules.json').write_text(json.dumps(mods,indent=2),encoding='utf-8')
(H/'components.json').write_text(json.dumps(C,indent=2,ensure_ascii=False),encoding='utf-8')
def writecsv(path,rows,fields):
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fields,delimiter=';');w.writeheader();w.writerows(rows)
pins=[dict(module=c['board'],ref=c['ref'],part=c['value'],pin=p,net=n) for c in C.values() for p,n in c['pins'].items()]
writecsv(H/'netlist.csv',pins,['module','ref','part','pin','net'])
writecsv(H/'wiring.csv',W,list(W[0]))
writecsv(H/'connectors.csv',K,list(K[0]))
bom=[dict(module=c['board'],ref=c['ref'],name=c['value'],quantity=1,note=c['note']) for c in C.values()]
writecsv(H/'BOM.csv',bom,list(bom[0]))
groups=collections.Counter(c['value'] for c in C.values())
writecsv(H/'zakupy.csv',[dict(nazwa=k,ilosc=v) for k,v in sorted(groups.items())],['nazwa','ilosc'])
(H/'removed-from-v4.1.json').write_text(json.dumps(removed,indent=2),encoding='utf-8')
# Auditable gate list for exhaustive tests, sourced from actual gate IC pin nets.
gates=[]
for key,c in C.items():
    if c['board']=='P04' and c['ref'].startswith('U_LINK'):
        for a,z,y in [(1,2,3),(4,5,6),(9,10,8),(12,13,11)]:
            n=c['pins'];
            if n[str(y)]!='NC':gates.append(dict(ref=key,a=n[str(a)],b=n[str(z)],out=n[str(y)]))
(H/'interlock-gates.json').write_text(json.dumps(gates,indent=2),encoding='utf-8')
# A navigable full connection atlas: pin-level SVG, consistent with CSV, not routed PCB CAD.
out=D/'schematy';out.mkdir(exist_ok=True)
index=['<!doctype html><meta charset="utf-8"><title>EGRLab v5 — atlas połączeń</title><style>body{font:16px system-ui;max-width:1100px;margin:30px auto}img{width:100%}a{color:#056}h2{margin-top:40px}</style><h1>EGRLab v5 — atlas połączeń</h1><p>Arkusze pinowe: każda linia kończy się nazwą sieci. Jednakowe nazwy oznaczają połączenie elektryczne; fizyczne przejścia między PCB określa hardware/wiring.csv. To dokumentacja obwodu, bez layoutu PCB.</p>']
pages=[]
for b in sorted(set(c['board'] for c in C.values())):
    items=sorted((c for c in C.values() if c['board']==b),key=lambda c:c['ref'])
    # One component per row permits labels to remain unambiguous even on AD7606B.
    for page in range(0,len(items),8):
        chunk=items[page:page+8]
        labels=lambda c:textwrap.wrap(c['ref']+': '+c['value'],width=46)
        height=70+sum(max(72,26+max(len(c['pins']),len(labels(c)))*17) for c in chunk)
        svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="{height}" viewBox="0 0 1100 {height}"><rect width="100%" height="100%" fill="white"/><g font-family="monospace" font-size="13"><text x="25" y="28" font-size="21">EGRLab v5 / {b} / arkusz {page//8+1}</text>']
        y=55
        for c in chunk:
            ht=max(62,18+max(len(c['pins']),len(labels(c)))*17)
            svg.append(f'<rect x="20" y="{y}" width="390" height="{ht}" fill="#eef4f7" stroke="#456"/>')
            for i,label in enumerate(labels(c)):svg.append(f'<text x="32" y="{y+19+i*17}">{html.escape(label)}</text>')
            for j,(pin,net) in enumerate(c['pins'].items()):
                yy=y+14+j*17
                svg.append(f'<text x="425" y="{yy+5}">{html.escape(pin)}</text><path d="M 490 {yy} H 530" stroke="#176"/><text x="540" y="{yy+5}">{html.escape(net)}</text>')
            y+=ht+10
        svg.append('</g></svg>');name=f'{b}-{page//8+1:02d}.svg';(out/name).write_text(''.join(svg),encoding='utf-8');pages.append(name)
        index.append(f'<h2>{b} — {page//8+1}</h2><img src="{name}" alt="{b} połączenia" loading="lazy">')
(out/'index.html').write_text('\n'.join(index),encoding='utf-8')
for old in out.glob('*.svg'):
    if old.name not in pages:old.unlink() # only obsolete generated SVG in this new revision
print(f'{len(C)} components, {len(pins)} pin assignments, {len(W)} cable wires, {len(pages)} SVG sheets')
