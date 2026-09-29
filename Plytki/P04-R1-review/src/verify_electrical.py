"""Independent, pin-level checks of KiCad's exported XML, not of parts.py.

Truth tables are bit-parallel: one bit per combination of 17 independent inputs.
This is a digital steady-state model. It does not prove analog timing, EMI,
metastability, contact debounce or component failure coverage; those need bench tests.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import json,copy
P=Path(__file__).resolve().parents[1]

def load():
    r=ET.parse(P/'verification/P04.xml').getroot(); pins={}
    for n in r.findall('./nets/net'):
        for q in n.findall('node'):pins[q.get('ref'),int(q.get('pin'))]=n.get('name').split('/')[-1]
    comps={c.get('ref'):{'value':c.findtext('value'),'fields':{x.get('name'):x.text for x in c.findall('./fields/field')}} for c in r.findall('./components/comp')}
    return pins,comps

PORTS={'PWM':('J2',1),'HEARTBEAT':('J2',3),'MCU_ARM':('J2',5),'SENSOR_ENABLE':('J2',11),'CORE_LINK':('J2',13),'SUP_N':('J2',15),
       'DRIVE_OK':('J3',7),'SENSOR_OK':('J4',3),'DAQ_OK':('J5',1),'PSU_OK':('J6',1),'PG_LINK':('J7',5),'TEST_KEY':('J8',3),'MECH_OK':('J8',4)}
READY=['PSU_OK','DAQ_OK','DRIVE_OK','SENSOR_OK','CORE_LINK','PG_LINK']
INPUTS=READY+['TEST_KEY','MECH_OK','SUP_N','LOCAL_SUP','WD_ALIVE','STOP_CLOSED','EXT_FAULT','MCU_ARM','SENSOR_ENABLE','PWM','ARM_STORED']

def simulate(pin,iv,mask,button=False):
    """Wire actual package pins through real gate pin maps. Supplies are ideal 3.3 V."""
    d={'GND':0,'3V3_IO':mask}
    for name,port in PORTS.items():d[pin[port]]=iv.get(name,0)
    d[pin['U1',13]]=iv['WD_ALIVE'];d[pin['U11',1]]=iv['LOCAL_SUP']
    d[pin['J8',7]]=iv['STOP_CLOSED'];d['ARM_BUTTON_N']=0 if button else mask
    # Q bases: find the resistor connected to each base (actual netlist).
    base=[]
    for q in ['Q1','Q2','Q3']:
        bn=pin[q,2]
        rs=[r for r in {r for r,n in pin if r.startswith('R')} if bn in [pin[r,1],pin[r,2]] and 'GND' not in [pin[r,1],pin[r,2]]]
        if len(rs)!=1:raise ValueError('Missing/ambiguous base driver '+q)
        r=rs[0];base.append(next(pin[r,k] for k in [1,2] if pin[r,k]!=bn))
    get=lambda r,n:d.get(pin[r,n],0)
    for _ in range(30):
        old=d.copy()
        for r in ['U8','U9','U10']:
            for en,a,y in [(1,2,3),(4,5,6),(10,9,8),(13,12,11)]:d[pin[r,y]]=get(r,a)&(mask^get(r,en))
        for r in ['U4','U5','U6','U7']:
            for a,b,y in [(1,2,3),(4,5,6),(9,10,8),(12,13,11)]:d[pin[r,y]]=get(r,a)&get(r,b)
        for a,y in [(1,2),(3,4),(5,6),(9,8),(11,10),(13,12)]:d[pin['U2',y]]=mask^get('U2',a)
        sink=iv['EXT_FAULT']
        for n in base:sink|=d.get(n,0)
        d['SAFE_N']=d.get(pin['R4',1],0)&(mask^sink)
        # Active-low asynchronous clear dominates the stored state.
        d[pin['U3',5]]=iv['ARM_STORED']&get('U3',1)
        if d==old:return d
    raise ValueError('Logic did not settle')

def checks(pin,comps,exhaustive=True):
    out=[]
    def ck(name,ok,detail=None):out.append({'name':name,'pass':bool(ok),'detail':detail})
    def eq(ref,pairs):return all(pin.get((ref,k))==v for k,v in pairs.items())
    ck('Watchdog pinout and independent clear',eq('U1',{1:'GND',2:'HEARTBEAT_P04',3:'SUP_OK',13:'WD_Q',14:'WD_C',15:'WD_RC',16:'3V3_IO',8:'GND',9:'GND',10:'GND',11:'GND'}))
    ck('Watchdog capacitor is between 15 and 14, never ground',eq('C1',{1:pin['U1',15],2:pin['U1',14]}) and eq('R1',{1:'3V3_IO',2:pin['U1',15]}) and 'GND' not in [pin['C1',1],pin['C1',2]])
    ck('Local supervisor D bondout',eq('U11',{1:'LOCAL_SUP_N',2:'3V3_IO',3:'GND'}) and comps['U11']['value']=='MCP100-315DI/TO')
    ck('Both supervisors qualify watchdog',set([pin['U5',9],pin['U5',10]])=={'SUP_N_P04','LOCAL_SUP_N'} and pin['U5',8]=='SUP_OK')
    ck('Latch and Schmitt conditioning',eq('U3',{1:'SAFE_OK',2:'3V3_IO',3:'ARM_CLK',4:'3V3_IO',5:'HW_ARMED',7:'GND',14:'3V3_IO',13:'GND',12:'GND',11:'GND',10:'3V3_IO'}) and eq('U2',{11:'SAFE_N',10:'SAFE_OK_N',13:'SAFE_OK_N',12:'SAFE_OK',3:'ARM_BUTTON_N',4:'ARM_CLK'}))
    ck('ARM contact topology',eq('R2',{1:'3V3_IO',2:'ARM_BUTTON_N'}) and eq('R3',{1:'ARM_BUTTON_N',2:pin['J8',9]}) and eq('C2',{1:'ARM_BUTTON_N',2:'GND'}) and pin['J8',10]=='GND')
    allowed={('R4',2),('R5',1),('U2',11),('J3',9),('J7',2),('TP6',1)}|{('Q'+str(i),3) for i in range(1,4)}
    ck('SAFE_N has only one passive pull-up and open collectors',{k for k,v in pin.items() if v=='SAFE_N'}==allowed and eq('R4',{1:pin['J8',7],2:'SAFE_N'}) and eq('R5',{1:'SAFE_N',2:'GND'}) and all(eq('Q'+str(i),{1:'GND',3:'SAFE_N'}) for i in range(1,4)))
    ck('All command/READY ports mapped',all(pin.get(port)==n for n,port in PORTS.items()))
    sig=['PWM','HEARTBEAT','MCU_ARM','SENSOR_ENABLE','CORE_LINK','SUP_N','PSU_OK','DAQ_OK','DRIVE_OK','SENSOR_OK','PG_LINK']
    ck('Input and post-adapter pull-downs',all(eq('R'+str(12+i),{1:n,2:'GND'}) and eq('R'+str(25+i),{1:n+'_P04',2:'GND'}) for i,n in enumerate(sig)))
    ck('Exact Ioff buffer and unused channel safe',all('74LVC125AD' in comps['U'+str(i)]['fields'].get('MPN','') and 'Nexperia' in comps['U'+str(i)]['fields'].get('MPN','') for i in range(8,11)) and eq('U10',{13:'3V3_IO',12:'GND'}))
    ck('One carrier decoupler per IC and 3 adapter capacitors',all(eq('C'+str(i),{1:'3V3_IO',2:'GND'}) for i in range(4,18)))
    ck('SENSOR 6-way contract and key positions',all(pin[r,n].startswith('unconnected-') for r,n in [('J2',4),('J3',2),('J4',2),('J4',5),('J4',6),('J5',4),('J6',5)]) and eq('J4',{1:'SENSOR_PERMIT',3:'SENSOR_OK',4:'GND'}))
    if exhaustive:
        rows=1<<len(INPUTS);mask=(1<<rows)-1;iv={}
        for i,n in enumerate(INPUTS):
            bb=bytes([[0xAA,0xCC,0xF0][i]])*(rows//8) if i<3 else (bytes(1<<(i-3))+bytes([255])*(1<<(i-3)))*(rows//(1<<(i+1)))
            iv[n]=int.from_bytes(bb,'little')
        d=simulate(pin,iv,mask)
        ilk=mask
        for n in READY+['TEST_KEY','MECH_OK']:ilk&=iv[n]
        safe=ilk&iv['SUP_N']&iv['LOCAL_SUP']&iv['WD_ALIVE']&iv['STOP_CLOSED']&(mask^iv['EXT_FAULT'])
        expected={'INTERLOCK':ilk,'SAFE_N':safe,'HW_ARMED':safe&iv['ARM_STORED'],'MOTOR_PERMIT':safe&iv['ARM_STORED']&iv['MCU_ARM'],
                  'PWM_OUT':safe&iv['ARM_STORED']&iv['MCU_ARM']&iv['PWM'],'SENSOR_PERMIT':safe&iv['SENSOR_ENABLE']}
        for n,v in expected.items():
            diff=d.get(n,0)^v
            first=(diff&-diff).bit_length()-1 if diff else None
            ck('Truth table '+n,not diff,{'rows':rows,'expected_high_rows':v.bit_count(),'actual_high_rows':d.get(n,0).bit_count(),'first_failing_row':first,'inputs':{k:bool((first>>i)&1) for i,k in enumerate(INPUTS)} if diff else None})
    # Event sequence driven through actual gates and clear/clock pin connections.
    iv={n:1 for n in INPUTS};iv.update(EXT_FAULT=0,ARM_STORED=0);last_clk=0;armed=0;events=[]
    seq=[('boot',False,None,None,0),('press ARM',True,None,None,1),('release ARM',False,None,None,1)]
    for fault in ['WD_ALIVE','SUP_N','LOCAL_SUP','STOP_CLOSED']+READY+['TEST_KEY','MECH_OK']:
        seq += [(fault+' fault',True,fault,0,0),(fault+' restored, ARM held',True,fault,1,0),(fault+' release',False,None,None,0),(fault+' fresh ARM',True,None,None,1),(fault+' release after arm',False,None,None,1)]
    seq += [('external OC',True,'EXT_FAULT',1,0),('OC released, ARM held',True,'EXT_FAULT',0,0),('release',False,None,None,0),('fresh press',True,None,None,1)]
    for name,button,k,v,want in seq:
        if k:iv[k]=v
        iv['ARM_STORED']=armed;d=simulate(pin,iv,1,button)
        clk=d.get(pin['U3',3],0);clr=d.get(pin['U3',1],0)
        if not clr:armed=0
        elif clk and not last_clk:armed=d.get(pin['U3',2],0)
        last_clk=clk;events.append({'event':name,'armed':armed,'expected':want,'pass':armed==want})
    ck('Fault recovery never automatically rearms',all(x['pass'] for x in events),events)
    return out

def main():
    pin,comps=load();out=checks(pin,comps);negative=[]
    mutations=[('watchdog CLR on SAFE_N',('U1',3),'SAFE_N','Watchdog pinout and independent clear'),
      ('watchdog Cext to ground',('C1',2),'GND','Watchdog capacitor is between 15 and 14, never ground'),
      ('bypassed local supervisor',('U5',10),'3V3_IO','Both supervisors qualify watchdog'),
      ('MCP100 pins reversed',('U11',3),'3V3_IO','Local supervisor D bondout'),
      ('missing TEST_KEY gate',('U7',10),'3V3_IO','Truth table INTERLOCK'),
      ('bypassed MCU arm',('U4',2),'3V3_IO','Truth table MOTOR_PERMIT'),
      ('sensor incorrectly requires manual ARM',('U5',5),'HW_ARMED','Truth table SENSOR_PERMIT'),
      ('no SAFE conditioning',('U3',1),'SAFE_N','Latch and Schmitt conditioning'),
      ('push-pull output on shared SAFE',('U2',12),'SAFE_N','SAFE_N has only one passive pull-up and open collectors'),
      ('missing receiver default',('R25',2),'3V3_IO','Input and post-adapter pull-downs')]
    for name,k,v,target in mutations:
        m=pin.copy();m[k]=v
        # Run the relevant independent check; no exception counts as detection.
        tests=checks(m,comps,exhaustive=target.startswith('Truth table'))
        detected=not next(x['pass'] for x in tests if x['name']==target)
        negative.append({'mutation':name,'target_check':target,'detected':detected})
    result={'source':'verification/P04.xml','checks':out,'truth_table_rows':1<<len(INPUTS),'negative_controls':negative,
            'limitations':'Ideal steady-state logic and ideal sequential edges; analog timing, debounce, simultaneous edges and physical fault testing remain NOT TESTED.'}
    (P/'verification/electrical-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    bad=[x['name'] for x in out if not x['pass']];miss=[x['mutation'] for x in negative if not x['detected']]
    print('Electrical',len(out)-len(bad),'/',len(out),'Mutation detections',len(negative)-len(miss),'/',len(negative));assert not bad and not miss,(bad,miss)
if __name__=='__main__':main()
