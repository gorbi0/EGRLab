"""Functional checks of the EXPORTED netlist, independent of generator/parts.json.
Facts and pin numbers are reviewed against the manufacturer data sheets listed in docs/ZRODLA.md.
This checks topology and defaults, not transient analogue behaviour or real devices.
"""
from pathlib import Path
import xml.etree.ElementTree as ET,json,sys,copy,re
P=Path(__file__).resolve().parents[1]

SOURCE={
 'ADC_CS_SRC':('U21','2','3V3_CORE'), 'ADC_SCLK_SRC':('U21','5','GND'),
 'ADC_SDI_SRC':('U21','9','GND'), 'ADC_CONVST_SRC':('U21','12','GND'),
 'ADC_RESET_SRC':('U22','2','GND'), 'MEAS_EN_SRC':('U22','5','GND'),
 'SPI3_SCLK_SRC':('U23','2','GND'), 'SPI3_MOSI_SRC':('U23','5','GND'),
 'TC1_CS_SRC':('U23','9','3V3_CORE'), 'TC2_CS_SRC':('U23','12','3V3_CORE'),
 'MEAS_BANK':('U2','2','GND'), 'CURRENT_CS_N':('U2','1','3V3_CORE'), 'SD_CS':('SD1','6','3V3_CORE')}
RECEIVER={
 'INTERLOCK':('U12','5','GND'), 'TEST_KEY':('U14','2','GND'), 'ENA_DIAG':('U13','2','GND'),
 'ENB_DIAG':('U13','5','GND'), 'CAN_RX':('U11','12','3V3_CORE'), 'ADC_BUSY':('U11','5','GND'),
 'ADC_DOUTA':('U11','2','GND'), 'SPI3_MISO':('U11','9','GND'), 'HW_ARMED':('U12','2','GND'),
 'LOGGER_CURRENT_OK':('U12','9','GND'), 'SENSOR_HEALTHY':('U12','12','GND'),
 'LOGGER_CLEAR':('U13','9','GND'), 'TEST_PRESENT':('U13','12','GND')}

def extract(root):
 pins={};comps={c.get('ref'):c for c in root.findall('./components/comp')}
 for n in root.findall('./nets/net'):
  name=n.get('name').split('/')[-1]
  for node in n.findall('node'):pins[node.get('ref'),node.get('pin')]='NC' if name.startswith('unconnected-') else name
 return pins,comps

def checks(root):
 pins,comps=extract(root);out=[]
 def check(name,ok,detail=None):out.append({'check':name,'pass':bool(ok),'detail':detail})
 def pin(r,n):return pins.get((r,str(n)))
 def between(r,a,b):return {pin(r,1),pin(r,2)}=={a,b}
 def value(r,s):return comps.get(r) is not None and comps[r].findtext('value','').startswith(s)
 for n,(u,p,rail) in (SOURCE|RECEIVER).items():
  rs=[r for r in comps if r.startswith('R') and between(r,n,rail) and value(r,'10K')]
  check('default '+n,pin(u,p)==n and len(rs)==1,rs)
 check('common reset MCU MCP P04',all(pin(r,p)=='SUP_N' for r,p in [('M1','J1-3'),('U1','18'),('J4','15'),('TP5','1')]))
 check('supervisor isolated from EN capacitance',pin('U3',1)=='SUP_RAW_N' and pin('U4',2)=='SUP_RAW_N' and between('R13','SUP_RAW_N','3V3_CORE'))
 check('non-inverting open-drain reset buffer',value('U4','SN74LVC1G07DBVR') and all(pin('U4',p)==n for p,n in {'1':'NC','2':'SUP_RAW_N','3':'GND','4':'RESET_DRV_N','5':'3V3_CORE'}.items()))
 check('reset sink current limiter',between('R34','RESET_DRV_N','SUP_N') and value('R34','220R'))
 check('common reset local pullup',between('R35','SUP_N','3V3_CORE') and value('R35','10K'))
 check('TPS3808 DBV supply pins',all(pin('U3',p)==n for p,n in {'1':'SUP_RAW_N','2':'GND','3':'3V3_CORE','4':'NC','5':'3V3_CORE','6':'3V3_CORE'}.items()))
 check('SYS and USB local rail separated',pin('J10',1)=='5V_SYS' and pin('M1','J1-21')=='5V_M1' and pin('TP7',1)=='5V_M1' and not any(r.startswith('R') and between(r,'5V_SYS','5V_M1') for r in comps))
 check('LTC4412 pin map and enable',value('U5','LTC4412IS6') and all(pin('U5',p)==n for p,n in {'1':'5V_SYS','2':'GND','3':'GND','4':'NC','5':'PWR_GATE','6':'5V_M1'}.items()))
 check('PMOS body diode SYS to M1',value('Q1','AO3401A') and pin('Q1',1)=='PWR_GATE' and pin('Q1',2)=='5V_M1' and pin('Q1',3)=='5V_SYS')
 for r,u,p,n in [('R36','U21',6,'ADC_SCLK'),('R37','U21',11,'ADC_CONVST'),('R38','U23',3,'SPI3_SCLK'),('R39','U21',8,'ADC_SDI'),('R40','U23',6,'SPI3_MOSI')]:
  check('source termination '+r,pin(u,p)==n+'_DRV' and between(r,n+'_DRV',n) and value(r,'33R'))
 for r in ['U11','U12','U13','U14','U21','U22','U23']:
  check('buffer powered from CORE '+r,pin(r,14)=='3V3_CORE' and pin(r,7)=='GND')
 # Enforce the R1 contract for ALL existing pins, including unused MCU pins.
 old,_=extract(ET.parse(P/'reference/P03-R1.xml').getroot())
 allowed={('M1','J1-3'):'SUP_N',('M1','J1-21'):'5V_M1',('U3','1'):'SUP_RAW_N',('R13','1'):'SUP_RAW_N',
          ('U21','6'):'ADC_SCLK_DRV',('U21','8'):'ADC_SDI_DRV',('U21','11'):'ADC_CONVST_DRV',
          ('U23','3'):'SPI3_SCLK_DRV',('U23','6'):'SPI3_MOSI_DRV'}
 differences=[(r,p,n,pins.get((r,p))) for (r,p),n in old.items() if pins.get((r,p))!=allowed.get((r,p),n)]
 check('R1 pin contract plus exact R2 delta',not differences,differences)
 return out

def move_pin(root,r,p,target):
 node=None
 for n in root.findall('./nets/net'):
  for q in list(n):
   if q.tag=='node' and q.get('ref')==r and q.get('pin')==str(p):node=q;n.remove(q)
 assert node is not None
 dest=next((n for n in root.findall('./nets/net') if n.get('name').split('/')[-1]==target),None)
 if dest is None:dest=ET.SubElement(root.find('nets'),'net',{'code':'999','name':target})
 dest.append(node)

def run():
 root=ET.parse(P/'verification/P03.xml').getroot();out=checks(root)
 (P/'verification/function-checks.json').write_text(json.dumps(out,indent=2)+'\n')
 for a in out:print('PASS' if a['pass'] else 'FAIL',a['check'])
 assert all(a['pass'] for a in out),'functional check failed'
 mutants=[]
 # Every required resistor removal must specifically fail its source/receiver default check.
 for n,(u,p,rail) in (SOURCE|RECEIVER).items():
  m=copy.deepcopy(root);pins,comps=extract(m)
  r=next(r for r,c in comps.items() if r.startswith('R') and {pins.get((r,'1')),pins.get((r,'2'))}=={n,rail} and c.findtext('value','').startswith('10K'))
  for net in m.findall('./nets/net'):
   for x in list(net):
    if x.tag=='node' and x.get('ref')==r:net.remove(x)
  mutants.append((f'remove {r}',f'default {n}',m))
 for desc,r,p,n,expected in [('MCU EN disconnected','M1','J1-3','NC','common reset MCU MCP P04'),
                           ('USB rail directly connected','M1','J1-21','5V_SYS','SYS and USB local rail separated'),
                           ('PMOS reversed','Q1','2','5V_SYS','PMOS body diode SYS to M1'),
                           ('RAW bypasses output buffer','U3','1','SUP_N','supervisor isolated from EN capacitance'),
                           ('VDD and CT mistaken','U3','6','NC','TPS3808 DBV supply pins')]:
  m=copy.deepcopy(root);move_pin(m,r,p,n);mutants.append((desc,expected,m))
 m=copy.deepcopy(root);m.find("./components/comp[@ref='R34']/value").text='0R';mutants.append(('reset limiter shorted','reset sink current limiter',m))
 m=copy.deepcopy(root);m.find("./components/comp[@ref='U4']/value").text='SN74LVC1G17';mutants.append(('push pull instead of OD','non-inverting open-drain reset buffer',m))
 rep=[]
 for name,expected,m in mutants:
  failed=[c['check'] for c in checks(m) if not c['pass']];rep.append({'mutation':name,'expected':expected,'detected':expected in failed})
 (P/'verification/function-mutations.json').write_text(json.dumps(rep,indent=2)+'\n')
 print(f'{len(out)} functional checks; {sum(x["detected"] for x in rep)}/{len(rep)} mutations detected')
 assert all(x['detected'] for x in rep),'missed mutation'
if __name__=='__main__':run()
