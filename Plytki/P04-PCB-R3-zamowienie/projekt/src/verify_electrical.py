"""Independent, pin-level checks of KiCad's exported XML, not of parts.py.
P04-R3: R2.2 checks with the connector pins moved to J_BP1..J_BP3 (edge A) and the service-strip resistors (SRV_*) ignored
where a check counts the members of a net; the logic model and the truth tables are unchanged.

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

PORTS={'PWM':('J_BP3',14),'HEARTBEAT':('J_BP3',16),'MCU_ARM':('J_BP3',18),'SENSOR_ENABLE':('J_BP3',2),'CORE_LINK':('J_BP3',4),'SUP_N':('J_BP3',12),
       'DRIVE_OK':('J_BP2',8),'SENSOR_OK':('J_BP1',12),'DAQ_OK':('J_BP1',16),'PSU_OK':('J_BP2',12),'PG_LINK':('J_BP2',18),'TEST_KEY':('J_BP1',14),'MECH_OK':('J_BP1',4)}
STOP=('J_BP1',6);ARM=('J_BP1',8);PANEL=('J_BP1',2);PG3=('J_BP2',14);PGS=('J_BP2',20);SAFE=('J_BP2',16)
def service(pin):
    """Service-strip series resistors: one pin on a SRV_* net (to the edge-B strip)."""
    return {r for (r,k),n in pin.items() if r.startswith('R') and n.startswith('SRV_')}
READY=['PSU_OK','DAQ_OK','DRIVE_OK','SENSOR_OK','CORE_LINK','PG_LINK']
INPUTS=READY+['TEST_KEY','MECH_OK','SUP_N','LOCAL_SUP','WD_ALIVE','STOP_CLOSED','EXT_FAULT','MCU_ARM','SENSOR_ENABLE','PWM','ARM_STORED']

def simulate(pin,iv,mask,button=False):
    """Wire actual package pins through real gate pin maps. Supplies are ideal 3.3 V."""
    d={'GND':0,'3V3_IO':mask}
    for name,port in PORTS.items():d[pin[port]]=iv.get(name,0)
    d[pin['U1',13]]=iv['WD_ALIVE'];d[pin['U11',1]]=iv['LOCAL_SUP']
    d[pin[STOP]]=iv['STOP_CLOSED'];d['ARM_BUTTON_N']=0 if button else mask
    # Q bases: find the resistor connected to each base (actual netlist).
    base=[]
    for q in ['Q1','Q2','Q3']:
        if pin.get((q,3))!='SAFE_N':continue  # open collector (single-fault model): no sink
        bn=pin[q,2]
        rs=[r for r in {r for r,n in pin if r.startswith('R')}-service(pin) if bn in [pin[r,1],pin[r,2]] and 'GND' not in [pin[r,1],pin[r,2]]]
        if len(rs)!=1:raise ValueError('Missing/ambiguous base driver '+q)
        r=rs[0];base.append(next(pin[r,k] for k in [1,2] if pin[r,k]!=bn))
    get=lambda r,n:d.get(pin[r,n],0)
    for r in ['R41','R42']:  # R2: series resistors between panel lines and gate inputs, modelled as wires
        if (r,1) in pin and (r,2) in pin:d[pin[r,2]]=d.get(pin[r,1],0)
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
    srv=service(pin)
    def members(net):return {k for k,v in pin.items() if v==net and k[0] not in srv}
    ck('Watchdog pinout and independent clear',eq('U1',{1:'GND',2:'HEARTBEAT_P04',3:'SUP_OK',13:'WD_Q',14:'WD_C',15:'WD_RC',16:'3V3_IO',8:'GND',9:'GND',10:'GND',11:'GND'}))
    ck('Watchdog capacitor is between 15 and 14, never ground',eq('C1',{1:pin['U1',15],2:pin['U1',14]}) and eq('R1',{1:'3V3_IO',2:pin['U1',15]}) and 'GND' not in [pin['C1',1],pin['C1',2]])
    ck('Local supervisor D bondout',eq('U11',{1:'LOCAL_SUP_N',2:'3V3_IO',3:'GND'}) and comps['U11']['value']=='MCP100-300DI/TO')
    ck('Both supervisors qualify watchdog',set([pin['U5',9],pin['U5',10]])=={'SUP_N_P04','LOCAL_SUP_N'} and pin['U5',8]=='SUP_OK')
    ck('Latch and Schmitt conditioning',eq('U7',{12:'SAFE_OK',13:'WD_Q',11:'SAFE_WD'}) and eq('U5',{5:'SAFE_WD',13:'SAFE_WD'}) and eq('U3',{1:'SAFE_WD',2:'3V3_IO',3:'ARM_CLK',4:'3V3_IO',5:'HW_ARMED',7:'GND',14:'3V3_IO',13:'GND',12:'GND',11:'GND',10:'3V3_IO'}) and eq('U2',{11:'SAFE_N',10:'SAFE_OK_N',13:'SAFE_OK_N',12:'SAFE_OK',3:'ARM_BUTTON_N',4:'ARM_CLK'}))
    ck('ARM contact topology',eq('R2',{1:'3V3_IO',2:'ARM_BUTTON_N'}) and eq('R3',{1:'ARM_BUTTON_N',2:pin[ARM]}) and pin[ARM]=='ARM_CONTACT' and eq('C2',{1:'ARM_BUTTON_N',2:'GND'}))
    allowed={('R4',2),('R5',1),('U2',11),SAFE,('C18',1)}|{('Q'+str(i),3) for i in range(1,4)}
    ck('SAFE_N has only one passive pull-up and open collectors',members('SAFE_N')==allowed and eq('R4',{1:pin[STOP],2:'SAFE_N'}) and eq('R5',{1:'SAFE_N',2:'GND'}) and eq('C18',{1:'SAFE_N',2:'GND'}) and all(eq('Q'+str(i),{1:'GND',3:'SAFE_N'}) for i in range(1,4)))
    # R2 (R4-07): panel contacts reach the HC08 inputs only through R41/R42; pulldowns sit on the gate side
    ck('Panel contacts reach the gates only through R41/R42 1 k; pulldowns on the gate side',
       eq('R41',{1:'TEST_KEY',2:'TEST_KEY_P04'}) and eq('R42',{1:'MECH_OK',2:'MECH_OK_P04'}) and eq('R23',{1:'TEST_KEY_P04',2:'GND'}) and eq('R24',{1:'MECH_OK_P04',2:'GND'})
       and members('TEST_KEY')=={PORTS['TEST_KEY'],('R41',1)} and members('MECH_OK')=={PORTS['MECH_OK'],('R42',1)}
       and comps['R41']['value'].startswith('1K') and comps['R42']['value'].startswith('1K'))
    # R2 (R4-03): 3V3_IO reaches off-board contacts only through current-limiting resistors; J1.3 is the supply input
    ck('3V3 leaves the board only through current-limiting resistors (R38/R39 1 k, R40 100 R)',
       {k for k,v in pin.items() if v=='3V3_IO' and k[0].startswith('J')}=={('J_BP2',10),('J_BP3',10)} and eq('R38',{1:'3V3_IO',2:'PG_SEND'}) and eq('R39',{1:'3V3_IO',2:pin[PG3]})
       and eq('R40',{1:'3V3_IO',2:pin[PANEL]}) and pin[PGS]=='PG_SEND' and members(pin[PG3])=={PG3,('R39',2)}
       and members(pin[PANEL])=={PANEL,('R40',2)} and members('PG_SEND')=={PGS,('R38',2)} and comps['R38']['value'].startswith('1K') and comps['R39']['value'].startswith('1K') and comps['R40']['value'].startswith('100R'))
    # R2 (R4-02): with Q1 open (collector lifted) a dead heartbeat must still clear the latch and both permits
    good={n:1 for n in INPUTS};good.update(EXT_FAULT=0,ARM_STORED=1)
    q1open=dict(pin);q1open['Q1',3]='NC_Q1_OPEN'
    dead=simulate(q1open,dict(good,WD_ALIVE=0),1);alive=simulate(q1open,good,1)
    res={'dead_heartbeat':{n:dead.get(n,0) for n in ['SAFE_N','HW_ARMED','MOTOR_PERMIT','PWM_OUT','SENSOR_PERMIT']},'alive':{n:alive.get(n,0) for n in ['SAFE_N','MOTOR_PERMIT','SENSOR_PERMIT']}}
    ck('Watchdog clears the latch and both permits without Q1 (single-fault)',res['dead_heartbeat']=={'SAFE_N':1,'HW_ARMED':0,'MOTOR_PERMIT':0,'PWM_OUT':0,'SENSOR_PERMIT':0}
       and res['alive']=={'SAFE_N':1,'MOTOR_PERMIT':1,'SENSOR_PERMIT':1},res)
    ck('All command/READY ports mapped',all(pin.get(port)==('SUP_N_OUT' if n=='SUP_N' else n) for n,port in PORTS.items()))
    sig=['PWM','HEARTBEAT','MCU_ARM','SENSOR_ENABLE','CORE_LINK','SUP_N','PSU_OK','DAQ_OK','DRIVE_OK','SENSOR_OK','PG_LINK']
    ext=lambda n:'SUP_N_OUT' if n=='SUP_N' else n   # R3: P12 name of the reset line; internal SUP_N_P04 unchanged
    ck('Input and post-buffer pull-downs',all(eq('R'+str(12+i),{1:ext(n),2:'GND'}) and eq('R'+str(25+i),{1:n+'_P04',2:'GND'}) for i,n in enumerate(sig)))
    ck('Exact Ioff buffer and unused channel safe',all('74LVC125AD' in comps['U'+str(i)]['fields'].get('MPN','') and 'Nexperia' in comps['U'+str(i)]['fields'].get('MPN','') for i in range(8,11)) and eq('U10',{13:'3V3_IO',12:'GND'}))
    ck('One decoupler per IC plus second 100n at U8-U10 (R2.2 adapter capacitors)',all(eq('C'+str(i),{1:'3V3_IO',2:'GND'}) for i in range(4,18)))
    ck('DRIVE and SENSOR nets leave on J_BP with the R2.2 names',eq('J_BP2',{2:'MOTOR_PERMIT',4:'PWM_OUT',6:'ARM_CLK',8:'DRIVE_OK',16:'SAFE_N'}) and eq('J_BP1',{10:'SENSOR_PERMIT',12:'SENSOR_OK'}))
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
      ('missing receiver default',('R25',2),'3V3_IO','Input and post-buffer pull-downs'),
      ('SENSOR_OK moved off its R2.2 name',('J_BP1',12),'SENSOR_READY','DRIVE and SENSOR nets leave on J_BP with the R2.2 names'),
      ('LED load on SAFE_N',('R37',2),'SAFE_N','SAFE_N has only one passive pull-up and open collectors'),
      ('R1 latch clear (watchdog only via Q1)',('U3',1),'SAFE_OK','Watchdog clears the latch and both permits without Q1 (single-fault)'),
      ('motor permit on SAFE_OK only (masked by the latch clear in steady state; structural check)',('U5',13),'SAFE_OK','Latch and Schmitt conditioning'),
      ('panel line straight to a gate',('U7',10),'TEST_KEY','Panel contacts reach the gates only through R41/R42 1 k; pulldowns on the gate side'),
      ('3V3 straight to the panel',('J_BP1',2),'3V3_IO','3V3 leaves the board only through current-limiting resistors (R38/R39 1 k, R40 100 R)')]
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
