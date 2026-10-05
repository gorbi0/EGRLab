"""P08-R2: independent requirements against native XML; data-driven gate propagation and mutations (plus a null control that must stay clean).
R1 circuit checks are kept; the R1 harness checks (J1 LV08, J2 SENSOR, J3 SFAULT, TP1..TP13) are replaced by S1 checks: J_BP at edge A, service strip at edge B,
J4 TSENSOR wire field, net-name contracts with P04 R2.2 / P03 R6 / P02 R4 / P12, part sources, and parity of the R1 circuit with the R1 netlist."""
from pathlib import Path
import xml.etree.ElementTree as ET,json,copy,math,itertools,re,csv
P=Path(__file__).resolve().parents[1]
def read(xml=None):
 root=ET.parse(xml or P/'verification/P08.xml').getroot();c={}
 for x in root.findall('./components/comp'):
  fs={a.get('name'):a.text for a in x.findall('./fields/field')}
  c[x.get('ref')]={'pins':{},'value':x.findtext('value'),'mpn':fs.get('MPN',''),'fp':x.findtext('footprint')}
 for n in root.findall('./nets/net'):
  name=n.get('name').split('/')[-1]
  for x in n.findall('node'):c[x.get('ref')]['pins'][int(x.get('pin'))]='NC' if name.startswith('unconnected-') else name
 return c
def val(c,r):
 s=c[r]['value'].split()[0];m=re.fullmatch(r'(\d+(?:\.\d+)?)([mRrKknup]?)(\d*)',s);assert m,(r,s)
 return float(m[1]+('.'+m[3] if m[3] else ''))*{'':1,'R':1,'r':1,'K':1e3,'k':1e3,'m':1e-3,'u':1e-6,'n':1e-9,'p':1e-12}[m[2]]
def check(c):
 out=[]
 def ok(k,v,n=''):out.append({'id':k,'pass':bool(v),'note':n})
 def pins(r,x):return c[r]['pins']==x
 def pair(r,a,b):return set(c[r]['pins'].values())=={a,b}
 # ---------------- S1 connectors (independent of parts.py) ----------------
 def members(net):return {(r,p) for r,x in c.items() for p,n in x['pins'].items() if n==net}
 j=c.get('J1',{'pins':{},'fp':''});jp=j['pins'];even={p:n for p,n in jp.items() if p%2==0}
 sig={n for n in even.values() if n not in ('GND','NC')}
 ok('JBP-2x8',sorted(jp)==list(range(1,17)) and j['fp'].endswith('IDC-Header_2x08_P2.54mm_Horizontal'))
 ok('JBP-ODD-GND',all(jp.get(p)=='GND' for p in range(1,17,2)))
 ok('JBP-EVEN-NO-GND',all(n!='GND' and not n.startswith('SRV_') for n in even.values()))
 old=set()
 for board,br in [('P02-R3-review','J8'),('P04-R2.1-review','J4'),('P03-R2-review','J6')]:
  old|={n for n in json.loads((P/f'reference/{board}-parts.json').read_text())[br]['pins'].values() if n not in ('GND','NC')}
 ok('JBP-CONTINUITY-R1',sig==old,'Every signal/supply of the three R1 harnesses (mating pinouts of P02-R3/J8, P04-R2.1/J4, P03-R2/J6) is on J_BP, nothing else.')
 vals=list(even.values())
 ok('JBP-S1-SUPPLY-PINS',vals.count('5V_SYS')>=2 and vals.count('3V3_IO')>=1 and all(vals.count(n)==1 for n in sig-{'5V_SYS','3V3_IO'}))
 ok('JBP-NC-ONLY-SPARE',[p for p,n in sorted(even.items()) if n=='NC']==[12,14] and all(len(members(n))>1 for n in sig))
 rows=list(csv.DictReader((P/'docs/J_BP.csv').open(encoding='utf-8-sig',newline=''),delimiter=';'))
 ok('JBP-CSV',{int(r['pin']):r['siec'] for r in rows}==jp)
 kier={r['siec']:r['kierunek'] for r in rows}
 # direction: who drives each J_BP signal on P08 (actual pins), and what the CSV promises P12
 drv=lambda net,ref,pin:(ref,pin) in members(net)
 ok('JBP-DIRECTIONS',kier.get('SENSOR_PERMIT')=='wejście' and drv('SENSOR_PERMIT','U5',2) and kier.get('SENSOR_OK')=='wyjście' and drv('SENSOR_OK','R11',2)
    and kier.get('SENSOR_HEALTHY')=='wyjście' and drv('SENSOR_HEALTHY','R13',2))
 # contracts: exact net names as in the neighbours (P12 joins by name)
 p04=json.loads((P/'reference/P04-R2.2-review-parts.json').read_text())['J4']['pins']
 ok('CONTRACT-P04-R2.2-SENSOR',{n for n in p04.values() if n not in ('GND','NC')}=={'SENSOR_PERMIT','SENSOR_OK'}<=sig)
 p03=json.loads((P/'reference/P03-R6-review-parts.json').read_text())['J_BP1']['pins']
 k=json.loads((P/'reference/P12-kontrakty.json').read_text())['sieci'].get('SENSOR_HEALTHY',{})
 ok('CONTRACT-P03-R6-SFAULT',p03.get('12')=='SENSOR_HEALTHY' and 'SENSOR_HEALTHY' in sig and any(e.endswith(' IN') for e in k.get('konce',[])) and 'P08' in k.get('czeka_na',[]))
 p02={n for n in json.loads((P/'reference/P02-R4-review-parts.json').read_text())['J_BP']['pins'].values()}
 ok('CONTRACT-P02-R4-SUPPLIES',{'5V_SYS','3V3_IO'}<=p02 and {'5V_SYS','3V3_IO'}<=sig)
 # J4 TSENSOR: wire field, numbering kept from R1 (W4 contract to P11)
 ok('IF-TSENSOR',pins('J4',{1:'5V_SENSOR',2:'AGND_SENSOR'}) and c['J4']['fp']=='P08:PTH_TSENSOR_2')
 # service strip (edge B): node net -> series resistor ohms, independent of parts.py
 SRV_NODES={'5V_SYS':1e3,'3V3_IO':1e3,'SUP3_N':1e3,'SUP5_N':1e3,'SENSOR_OK':1e3,'SENSOR_HEALTHY':1e3,'PERMIT_LOCAL':1e3,'SENSOR_LOCAL':1e3,'TPS_EN':1e4,'SENSOR_LIMITED':1e3,'SENSOR_FAULT_LOCAL_N':1e3}
 sv=c.get('J2',{'pins':{},'fp':''});s=sv['pins'];n=max(s) if s else 0
 ok('SRV-MAX-13',sorted(s)==list(range(1,n+1)) and n<=13 and sv['fp'].endswith('PinHeader_1x13_P2.54mm_Horizontal'))
 ok('SRV-ENDS-GND',s.get(1)=='GND' and s.get(n)=='GND' and [p for p,v in s.items() if v=='GND']==[1,n])
 seen=[];good=True
 for p in range(2,n):
  net=s[p];m=members(net);rr=[r for r,q in m if r.startswith('R')]
  if not net.startswith('SRV_') or len(m)!=2 or len(rr)!=1 or ('J2',p) not in m or (rr[0],2) not in m:good=False;continue
  r=rr[0];node=c[r]['pins'].get(1)
  if node!=net[4:] or node in ('GND','NC') or node.startswith('SRV_'):good=False;continue
  seen.append(node)
  if node not in SRV_NODES or abs(val(c,r)-SRV_NODES[node])>1e-6:good=False
 ok('SRV-SERIES-R-AT-NODE',good and len(seen)==n-2 and len(set(seen))==n-2)
 ok('SRV-COVERS-ODBIOR',set(seen)==set(SRV_NODES))
 ok('SRV-NOT-ON-SENSOR-OUTPUT',not ({'5V_SENSOR','AGND_SENSOR'}&set(seen)) and {r for r,_ in members('5V_SENSOR')}=={'K1','R18','J4'},'Sensor output measured at the TEST port, never through the strip next to GND.')
 rows=list(csv.DictReader((P/'docs/SERWIS.csv').open(encoding='utf-8-sig',newline=''),delimiter=';'))
 ok('SRV-CSV',[(int(r['pin']),r['siec']) for r in rows]==[(p,'GND' if s[p]=='GND' else s[p][4:]) for p in sorted(s)])
 # part sources (S1 sec. 9): owned THT standing (MF0207 4k7, MF0204 6k8), every other R and C new SMD 1206 except the electrolytic C10
 srcok=True
 for r,x in c.items():
  if r.startswith('R') and x['value']=='4K7':srcok&=x['fp'].endswith('R_Axial_DIN0207_L6.3mm_D2.5mm_P5.08mm_Vertical')
  elif r.startswith('R') and x['value']=='6K8':srcok&=x['fp'].endswith('R_Axial_DIN0204_L3.6mm_D1.6mm_P2.54mm_Vertical')
  elif r.startswith('R'):srcok&=x['fp'].startswith('Resistor_SMD:R_1206')
  if r=='C10':srcok&=x['fp'].startswith('Capacitor_THT:CP_Radial')
  elif r.startswith('C'):srcok&=x['fp'].startswith('Capacitor_SMD:C_1206')
 ok('PARTS-SOURCES',srcok)
 ok('NO-TESTPADS-NO-HARNESS-TAILS',not any(r.startswith('TP') for r in c) and 'J3' not in c)
 # parity with R1: every R1 circuit part (no connectors, no test pads) has the same nets pin by pin and the same value
 r1=R1 if R1 is not None else {}
 diff=[(r,p,n,c.get(r,{'pins':{}})['pins'].get(p)) for r,x in r1.items() if not r.startswith(('J','TP','#')) for p,n in x['pins'].items() if c.get(r,{'pins':{}})['pins'].get(p)!=n]
 diff+=[(r,'value',x['value'],c[r]['value']) for r,x in r1.items() if r in c and not r.startswith(('J','TP')) and x['value']!=c[r]['value']]
 added={r for r in c if r not in r1 and not r.startswith('#')}
 ok('R1-CIRCUIT-PARITY',bool(r1) and not diff and added=={'R'+str(i) for i in range(19,30)},f'{len(diff)} differences; added parts: {sorted(added)}')
 ok('TPS-DBV-PINS',pins('U1',{1:'5V_SYS',2:'GND',3:'TPS_EN',4:'SENSOR_FAULT_LOCAL_N',5:'ILIM_232K',6:'SENSOR_LIMITED'}) and c['U1']['mpn']=='TPS2553DBVR')
 ok('CURRENT-LIMIT-RESISTOR',pair('R1','ILIM_232K','GND') and val(c,'R1')==232000 and '1%' in c['R1']['mpn'])
 ok('RELAY-CONTACTS',pins('K1',{1:'5V_SYS',8:'SENSOR_COIL_LOW',2:'NC',3:'SENSOR_LIMITED',4:'5V_SENSOR',5:'AGND_SENSOR',6:'GND',7:'NC'}) and c['K1']['mpn']=='G6K-2P-Y DC5')
 ok('DRIVER',pins('U2',{1:'SENSOR_LOCAL',**{i:'GND' for i in range(2,10)},10:'5V_SYS',**{i:'NC' for i in range(11,18)},18:'SENSOR_COIL_LOW'}) and c['U2']['mpn']=='TBD62083APG')
 ok('FLYBACK',pins('D1',{1:'5V_SYS',2:'SENSOR_COIL_LOW'}))
 for r,mpn,rail,net in [('U6','MCP120-300DI/TO','3V3_IO','SUP3_N'),('U7','MCP120-450DI/TO','5V_SYS','SUP5_RAW'),('U8','MCP120-300DI/TO','3V3_IO','TPS_EN')]:ok('SUP-'+r,pins(r,{1:net,2:rail,3:'GND'}) and c[r]['mpn']==mpn)
 ok('SUP-PULLUPS',pair('R3','SUP3_N','3V3_IO') and pair('R4','SUP5_RAW','5V_SYS') and val(c,'R3')==val(c,'R4')==10000)
 ok('FAULT-PULLUP-3V3',pair('R2','SENSOR_FAULT_LOCAL_N','3V3_IO') and val(c,'R2')==10000)
 ok('NO-FAULT-EN-FEEDBACK',c['U3']['pins'].get(4)=='PERMIT_LOCAL' and c['U3']['pins'].get(5)=='SENSOR_OK_LOCAL')
 ok('GUARD-DIVIDER',pair('R15','SENSOR_LOCAL','TPS_EN') and pair('R16','TPS_EN','GND') and val(c,'R15')==4700 and val(c,'R16')==6800)
 rhi=val(c,'R15');rlo=val(c,'R16')
 # Below VDD=1V even an output at VDD must not enable TPS; leakage bounds 0.5uA TPS + 1uA supervisor, plus 5uA conservative output injection.
 vmax=1*rlo*1.01/(rhi*.99+rlo*1.01)+6.5e-6/(1/(rhi*.99)+1/(rlo*1.01))
 vmin=2.7*rlo*.99/(rhi*1.01+rlo*.99)-1.5e-6/(1/(rhi*1.01)+1/(rlo*.99))
 ok('GUARD-MARGINS',vmax<.66 and vmin>1.1,f'Calculated EN below1V: {vmax:.3f}V; valid-state at 2.7V drive: {vmin:.3f}V. Brownout waveform still requires bench test.')
 ok('HC08-PINS',pins('U3',{1:'SUP3_N',2:'SUP5_N',3:'SENSOR_OK_LOCAL',4:'PERMIT_LOCAL',5:'SENSOR_OK_LOCAL',6:'SENSOR_LOCAL',7:'GND',8:'SENSOR_HEALTH_LOCAL',9:'SENSOR_OK_LOCAL',10:'SENSOR_FAULT_LOCAL_N',11:'NC',12:'GND',13:'GND',14:'3V3_IO'}) and c['U3']['mpn']=='SN74HC08N')
 exp4={1:'GND',2:'SUP5_RAW',3:'SUP5_N',4:'GND',5:'SENSOR_OK_LOCAL',6:'SENSOR_OK_TX',7:'GND',8:'NC',9:'GND',10:'3V3_IO',11:'NC',12:'GND',13:'3V3_IO',14:'3V3_IO'}
 exp5={1:'GND',2:'SENSOR_PERMIT',3:'PERMIT_LOCAL',4:'GND',5:'SENSOR_HEALTH_LOCAL',6:'SENSOR_HEALTH_TX',7:'GND',8:'NC',9:'GND',10:'3V3_IO',11:'NC',12:'GND',13:'3V3_IO',14:'3V3_IO'}
 ok('IOFF-TRANSLATION',pins('U4',exp4) and pins('U5',exp5) and all(c[r]['mpn']=='74LVC125AD,118 (Nexperia)' for r in ['U4','U5']))
 for r,n in [('R5','SUP5_N'),('R6','PERMIT_LOCAL'),('R7','SENSOR_PERMIT'),('R8','SENSOR_OK_LOCAL'),('R9','SENSOR_LOCAL'),('R10','SENSOR_HEALTH_LOCAL'),('R12','SENSOR_OK'),('R14','SENSOR_HEALTHY')]:ok('DEFAULT-'+r,pair(r,n,'GND') and val(c,r)==10000)
 ok('OUTPUT-SERIES',pair('R11','SENSOR_OK_TX','SENSOR_OK') and pair('R13','SENSOR_HEALTH_TX','SENSOR_HEALTHY') and val(c,'R11')==val(c,'R13')==100)
 ok('DISCHARGE',pair('R17','SENSOR_LIMITED','GND') and pair('R18','5V_SENSOR','AGND_SENSOR') and val(c,'R17')==val(c,'R18')==10000)
 ag={r for r,a in c.items() if 'AGND_SENSOR' in a['pins'].values()}
 ok('NO-GROUND-BYPASS',ag=={'K1','R18','J4'},'No GND-referenced output capacitor, LED or bleed around return contact.')
 ok('INPUT-OUTPUT-CAPS',pair('C1','5V_SYS','GND') and pair('C2','SENSOR_LIMITED','GND') and val(c,'C1')==val(c,'C2')==1e-6)
 truths=[]
 for s3,s5,permit,fault in itertools.product([0,1],repeat=4):
  n={'GND':0,'3V3_IO':1,'SUP3_N':s3,'SUP5_RAW':s5,'SENSOR_PERMIT':permit,'SENSOR_FAULT_LOCAL_N':fault}
  for _ in range(8):
   for ref in ['U4','U5']:
    p=c[ref]['pins']
    for oe,a,y in [(1,2,3),(4,5,6),(10,9,8),(13,12,11)]:
     if n.get(p[oe])==0 and p[a] in n:n[p[y]]=n[p[a]]
   p=c['U3']['pins']
   for a,b,y in [(1,2,3),(4,5,6),(9,10,8),(12,13,11)]:
    if p[a] in n and p[b] in n:n[p[y]]=n[p[a]]&n[p[b]]
   for r in ['R11','R13']:
    p=c[r]['pins']
    if p[1] in n:n[p[2]]=n[p[1]]
  truths.append(dict(inputs=[s3,s5,permit,fault],actual=[n.get(x) for x in ['SENSOR_OK','SENSOR_LOCAL','SENSOR_HEALTHY']],expected=[s3&s5,s3&s5&permit,s3&s5&fault]))
 ok('ACTUAL-NETLIST-TRUTH',all(t['actual']==t['expected'] for t in truths),'16 cases, propagated through actual HC08/LVC pins and series resistors. No formula-against-itself test.')
 return out,truths
R1=read(P/'reference/P08-R1.xml')
if __name__=='__main__':
 c=read();checks,truths=check(c);negative=[]
 for x in checks:
  if not x['pass']:print('FAIL',x)
 muts=[('NC-NO-swap','K1',2,'5V_SENSOR'),('ground-bypass','R18',2,'GND'),('reversed-flyback','D1',1,'SENSOR_COIL_LOW'),('bad-TPS-pin','U1',3,'SENSOR_LOCAL'),('missing-guard','U8',1,'NC'),('wrong-guard-power','U8',2,'5V_SYS'),('5V-to-HC','U3',2,'SUP5_RAW'),('ready-permit-loop','U3',1,'SENSOR_PERMIT'),('fault-retry-loop','U3',5,'SENSOR_FAULT_LOCAL_N'),('health-wrong-gate','U3',10,'PERMIT_LOCAL'),('no-IOff','U5',14,'5V_SYS'),('no-pulldown','R14',2,'NC'),('coil-common','U2',10,'GND'),
  # S1 connectors
  ('jbp-odd-pin-signal','J1',3,'SENSOR_OK'),('jbp-odd-pin-NC','J1',5,'NC'),('jbp-even-pin-GND','J1',8,'GND'),('jbp-second-5V-lost','J1',16,'NC'),('jbp-PERMIT-missing','J1',6,'NC'),
  ('jbp-HEALTHY-renamed','J1',10,'SENSOR_HEALTH_TX'),('jbp-spare-used','J1',12,'SENSOR_LOCAL'),('jbp-extra-3V3','J1',14,'3V3_IO'),('jbp-OK-driven-raw','R11',2,'SENSOR_OK_TX'),
  ('tsensor-return-to-GND','J4',2,'GND'),('tsensor-swapped','J4',1,'AGND_SENSOR'),
  ('srv-first-not-GND','J2',1,'3V3_IO'),('srv-last-not-GND','J2',13,'SRV_TPS_EN'),('srv-extra-GND-inside','J2',7,'GND'),('srv-14th-pin','J2',14,'GND'),('srv-no-resistor','J2',2,'5V_SYS'),
  ('srv-resistor-shorted','R19',2,'5V_SYS'),('srv-duplicate-node','R20',1,'5V_SYS'),('srv-node-GND','R21',1,'GND'),('srv-on-AGND_SENSOR','R29',1,'AGND_SENSOR'),('srv-on-5V_SENSOR','R28',1,'5V_SENSOR')]
 for name,r,pin,net in muts:
  cc=copy.deepcopy(c);cc[r]['pins'][pin]=net;bad=[t['id'] for t in check(cc)[0] if not t['pass']];negative.append({'mutation':name,'expected':'detected','detected':bool(bad),'by':bad})
 for name,r,field,new in [('wrong-limit','R1','value','23K2'),('bad-divider','R16','value','68K'),('wrong-variant','U1','mpn','TPS2553-1DBVR'),('wrong-supervisor','U8','mpn','MCP130-300DI/TO'),
   ('srv-TPS_EN-1k','R27','value','1K'),('srv-rail-0R','R19','value','0R'),('jbp-wrong-header','J1','fp','Connector_IDC:IDC-Header_2x05_P2.54mm_Horizontal'),
   ('R2-fp-THT','R2','fp','Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P5.08mm_Vertical'),('R15-fp-SMD','R15','fp','Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder'),('C3-fp-0805','C3','fp','Capacitor_SMD:C_0805_2012Metric'),
   ('R1-circuit-value-changed','R17','value','4K7')]:
  cc=copy.deepcopy(c);cc[r][field]=new;bad=[t['id'] for t in check(cc)[0] if not t['pass']];negative.append({'mutation':name,'expected':'detected','detected':bool(bad),'by':bad})
 for name,fn in [('testpad-reintroduced',lambda cc:cc.update(TP1={'pins':{1:'5V_SYS'},'value':'5V_SYS','mpn':'','fp':''})),('extra-part-on-AGND',lambda cc:cc.update(C99={'pins':{1:'AGND_SENSOR',2:'GND'},'value':'100n','mpn':'','fp':'Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder'}))]:
  cc=copy.deepcopy(c);fn(cc);bad=[t['id'] for t in check(cc)[0] if not t['pass']];negative.append({'mutation':name,'expected':'detected','detected':bool(bad),'by':bad})
 bad=[t['id'] for t in check(copy.deepcopy(c))[0] if not t['pass']];negative.append({'mutation':'null-control (no change)','expected':'clean','detected':bool(bad),'by':bad})
 r=232;limits={'min_ma':25230/(r*1.01)**1.016,'typ_ma':23950/r**.977,'max_ma':22980/(r*.99)**.94}
 result=dict(checks=checks,negative_controls=negative,truth_table=truths,current_limit=limits,hardware_tested=False)
 (P/'verification/electrical-checks.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 print('Electrical checks',len(checks),'negative controls',len(negative),limits)
 for t in negative[:-1]:
  if not t['detected']:print('UNDETECTED',t)
 assert all(x['pass'] for x in checks) and all(x['detected'] for x in negative[:-1]) and not negative[-1]['detected'],negative[-1]
