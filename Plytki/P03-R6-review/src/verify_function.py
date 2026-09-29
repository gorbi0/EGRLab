"""Functional checks of the EXPORTED netlist, independent of generator/parts.json (R3: + supply rails on connectors, frozen neighbour pin maps;
R4: reset to P04 through the Schmitt buffer U6 and R41).
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
 def nodes(n):return sorted(k for k,v in pins.items() if v==n)
 check('common reset MCU MCP',all(pin(r,p)=='SUP_N' for r,p in [('M1','J1-3'),('U1','18'),('TP5','1')]))
 # R4: P04 takes the common reset through a Schmitt buffer: its 74LVC125A needs <= 10 ns/V, SUP_N rises in milliseconds.
 check('reset to P04 through Schmitt buffer U6 and R41',value('U6','SN74LVC1G17DBVR') and all(pin('U6',p)==n for p,n in {'1':'NC','2':'SUP_N','3':'GND','4':'SUP_N_DRV','5':'3V3_CORE'}.items())
       and value('R41','220R') and nodes('SUP_N_DRV')==[('R41','1'),('U6','4')] and nodes('SUP_N_OUT')==[('J4','15'),('R41','2')])
 check('U6 decoupling C15 100nF',between('C15','3V3_CORE','GND') and value('C15','100nF'))
 check('supervisor isolated from EN capacitance',pin('U3',1)=='SUP_RAW_N' and pin('U4',2)=='SUP_RAW_N' and between('R13','SUP_RAW_N','3V3_CORE'))
 check('Schmitt-input non-inverting open-drain reset buffer',value('U4','SN74LVC1G37DBVR') and all(pin('U4',p)==n for p,n in {'1':'NC','2':'SUP_RAW_N','3':'GND','4':'RESET_DRV_N','5':'3V3_CORE'}.items()))
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
          ('U23','3'):'SPI3_SCLK_DRV',('U23','6'):'SPI3_MOSI_DRV',('J4','15'):'SUP_N_OUT'}
 differences=[(r,p,n,pins.get((r,p))) for (r,p),n in old.items() if pins.get((r,p))!=allowed.get((r,p),n)]
 check('R1 pin contract plus exact R2/R4 delta',not differences,differences)
 # R3 (review P3-02): no connector pin may carry a supply rail directly or through < 100 ohm (J10 = LV03 supply input).
 def ohms(v):
  m=re.fullmatch(r'(\d+)([RKM]?)(\d*)',v.split('/')[0].strip().upper())
  return float(m[1]+('.'+m[3] if m[3] else ''))*{'':1,'R':1,'K':1e3,'M':1e6}[m[2]] if m else None
 rails={'3V3_CORE','3V3_IO','5V_SYS','5V_M1'};hot=[]
 for (r,p),n in pins.items():
  if not re.fullmatch(r'J\d+',r) or r=='J10' or n in ('GND','NC'):continue
  if n in rails:hot.append((r,p,n,'direct'))
  for rr in comps:
   if rr.startswith('R') and n in (pin(rr,1),pin(rr,2)):
    far=pin(rr,2) if pin(rr,1)==n else pin(rr,1)
    if far in rails and (ohms(comps[rr].findtext('value','')) or 0)<100:hot.append((r,p,n,rr+' '+comps[rr].findtext('value','')))
 check('no supply rail on a connector pin directly or through < 100 ohm (LV03 J10 excepted)',not hot,hot)
 check('CORE_LINK from 3V3_CORE through 1K (R14)',between('R14','3V3_CORE','CORE_LINK') and value('R14','1K') and pin('J4',13)=='CORE_LINK')
 # R3: mating connectors equal the frozen pin maps of the neighbour releases (P02-R3 J3, P04-R2.1 J2, P05-R1 J1).
 # R4: P04 J2.15 (SUP_N in the frozen P04 map) is driven from the buffered copy SUP_N_OUT; the frozen file is unchanged.
 ALIAS={('J4','15'):{'SUP_N':'SUP_N_OUT'}}
 iface=json.loads((P/'reference/interfaces-R3.json').read_text(encoding='utf-8'));bad=[]
 for link in iface['links']:
  for p_,n in link['pins'].items():
   got=pin(link['mine'],p_);want=ALIAS.get((link['mine'],p_),{}).get(n,n)
   if not (got==want or (n=='NC' and got=='NC')):bad.append((link['name'],link['mine']+'.'+p_,got,want))
 check('mating connectors equal the frozen neighbour pin maps (LV03, H_SAFE, DAQ B2B)',not bad,bad)
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
 for desc,r,p,n,expected in [('MCU EN disconnected','M1','J1-3','NC','common reset MCU MCP'),
                           ('USB rail directly connected','M1','J1-21','5V_SYS','SYS and USB local rail separated'),
                           ('PMOS reversed','Q1','2','5V_SYS','PMOS body diode SYS to M1'),
                           ('RAW bypasses output buffer','U3','1','SUP_N','supervisor isolated from EN capacitance'),
                           ('VDD and CT mistaken','U3','6','NC','TPS3808 DBV supply pins')]:
  m=copy.deepcopy(root);move_pin(m,r,p,n);mutants.append((desc,expected,m))
 m=copy.deepcopy(root);m.find("./components/comp[@ref='R34']/value").text='0R';mutants.append(('reset limiter shorted','reset sink current limiter',m))
 m=copy.deepcopy(root);m.find("./components/comp[@ref='U4']/value").text='SN74LVC1G17';mutants.append(('push pull instead of OD','Schmitt-input non-inverting open-drain reset buffer',m))
 m=copy.deepcopy(root);m.find("./components/comp[@ref='R14']/value").text='0R';mutants.append(('R14 back to 0R (R2)','no supply rail on a connector pin directly or through < 100 ohm (LV03 J10 excepted)',m))
 m=copy.deepcopy(root);move_pin(m,'J4','13','3V3_CORE');mutants.append(('J4.13 tied to 3V3_CORE','no supply rail on a connector pin directly or through < 100 ohm (LV03 J10 excepted)',m))
 m=copy.deepcopy(root);move_pin(m,'J4','15','CORE_LINK');mutants.append(('SUP_N pin moved onto CORE_LINK','mating connectors equal the frozen neighbour pin maps (LV03, H_SAFE, DAQ B2B)',m))
 m=copy.deepcopy(root);move_pin(m,'J1','1','ADC_SDI');mutants.append(('B2B pin 1 carries ADC_SDI','mating connectors equal the frozen neighbour pin maps (LV03, H_SAFE, DAQ B2B)',m))
 m=copy.deepcopy(root);m.find("./components/comp[@ref='U4']/value").text='SN74LVC1G07DBVR';mutants.append(('U4 regressed to non-Schmitt LVC1G07','Schmitt-input non-inverting open-drain reset buffer',m))
 # R4 buffer U6/R41/C15
 m=copy.deepcopy(root);move_pin(m,'J4','15','SUP_N');mutants.append(('J4.15 back on SUP_N (buffer bypassed, R3)','reset to P04 through Schmitt buffer U6 and R41',m))
 m=copy.deepcopy(root);move_pin(m,'J4','15','SUP_N');mutants.append(('J4.15 back on SUP_N vs frozen P04 map','mating connectors equal the frozen neighbour pin maps (LV03, H_SAFE, DAQ B2B)',m))
 m=copy.deepcopy(root);m.find("./components/comp[@ref='U6']/value").text='SN74LVC1G14DBVR';mutants.append(('inverting Schmitt LVC1G14 instead of LVC1G17','reset to P04 through Schmitt buffer U6 and R41',m))
 m=copy.deepcopy(root);m.find("./components/comp[@ref='R41']/value").text='0R';mutants.append(('R41 shorted','reset to P04 through Schmitt buffer U6 and R41',m))
 m=copy.deepcopy(root);move_pin(m,'U6','2','SUP_RAW_N');mutants.append(('U6 fed from SUP_RAW_N','reset to P04 through Schmitt buffer U6 and R41',m))
 m=copy.deepcopy(root);move_pin(m,'C15','1','NC');mutants.append(('C15 not on 3V3_CORE','U6 decoupling C15 100nF',m))
 rep=[]
 for name,expected,m in mutants:
  failed=[c['check'] for c in checks(m) if not c['pass']];rep.append({'mutation':name,'expected':expected,'detected':expected in failed})
 (P/'verification/function-mutations.json').write_text(json.dumps(rep,indent=2)+'\n')
 print(f'{len(out)} functional checks; {sum(x["detected"] for x in rep)}/{len(rep)} mutations detected')
 assert all(x['detected'] for x in rep),'missed mutation'
if __name__=='__main__':run()
