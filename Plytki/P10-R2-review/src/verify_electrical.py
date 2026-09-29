"""Independent pin requirements against the exported native KiCad XML: CAN receiver topology, S1 connector rules (J_BP, service strip), part sources, and deliberate mutations
(plus a null control that must stay clean)."""
from pathlib import Path
import xml.etree.ElementTree as ET,json,copy,csv
P=Path(__file__).resolve().parents[1]
def read():
 root=ET.parse(P/'verification/P10.xml').getroot();c={}
 for x in root.findall('./components/comp'):
  fields={a.get('name'):a.text for a in x.findall('./fields/field')}
  c[x.get('ref')]={'pins':{},'value':x.findtext('value'),'mpn':fields.get('MPN',''),'fp':x.findtext('footprint') or ''}
 for n in root.findall('./nets/net'):
  name=n.get('name').split('/')[-1]
  for x in n.findall('node'):c[x.get('ref')]['pins'][int(x.get('pin'))]='NC' if name.startswith('unconnected-') else name
 return c
def csv_rows(name):
 with (P/'docs'/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter=';'))
SUPPLIES={'5V_SYS','3V3_IO'}
# service strip contract, independent of parts.py: node net -> required series resistor, ohms (rails and logic 1k; the two vehicle-bus nodes 10k)
SRV_NODES={'5V_SYS':1000,'3V3_IO':1000,'RX_RAW':1000,'CAN_RX':1000,'CAN_TX':1000,'CAN_H':10000,'CAN_L':10000}
def ohms(v):
 v=v.upper().replace(' ','');m=1
 if v.endswith('K'):m=1000;v=v[:-1]
 elif v.endswith('R'):v=v[:-1]
 return float(v)*m
def check(c):
 out=[]
 def ok(k,v):out.append({'id':k,'pass':bool(v)})
 def pins(r,v):return c[r]['pins']==v
 def members(net):return {(r,p) for r,x in c.items() for p,n in x['pins'].items() if n==net}
 # --- J_BP (edge A) ---
 j=c['J1']['pins'];nonG=[n for p,n in j.items() if p%2==0]
 ok('JBP-10-PINS',sorted(j)==list(range(1,11)) and c['J1']['fp'].endswith('IDC-Header_2x05_P2.54mm_Horizontal'))
 ok('JBP-ODD-GND',all(j.get(p)=='GND' for p in range(1,11,2)))
 ok('JBP-EVEN-SIGNALS',all(j.get(p) not in (None,'GND','NC') and not j[p].startswith('SRV_') for p in range(2,11,2)))
 d1={int(k):v for k,v in json.loads((P/'reference/P02-R3-parts.json').read_text())['J10']['pins'].items()};d2={int(k):v for k,v in json.loads((P/'reference/P03-R2-parts.json').read_text())['J8']['pins'].items()}
 old={n for n in list(d1.values())+list(d2.values()) if n not in ('GND','NC')}
 ok('JBP-CONTINUITY-R1',set(nonG)==old)   # every signal/supply of the two R1 harnesses is on J_BP, nothing else
 ok('JBP-S1-SUPPLY-PINS',nonG.count('5V_SYS')>=2 and nonG.count('3V3_IO')>=1 and all(nonG.count(n)==1 for n in old-SUPPLIES))
 ok('JBP-SUPPLY-USED',SUPPLIES<=set(nonG) and all(any(r not in ('J1','J2') and not r.startswith('R') for r,_ in members(n)) for n in SUPPLIES))
 ok('JBP-CSV',{int(r['pin']):r['siec'] for r in csv_rows('J_BP.csv')}==j)
 # --- service strip (edge B) ---
 s=c['J2']['pins'];n=max(s) if s else 0
 ok('SRV-MAX-13',sorted(s)==list(range(1,n+1)) and n<=13 and c['J2']['fp'].endswith('PinHeader_1x09_P2.54mm_Horizontal'))
 ok('SRV-ENDS-GND',s.get(1)=='GND' and s.get(n)=='GND')
 ok('SRV-GND-ONLY-ENDS',[p for p,v in s.items() if v=='GND']==[1,n])
 seen=[];good=True
 for p in range(2,n):
  net=s[p];m=members(net);rr=[r for r,q in m if r.startswith('R')]
  if not net.startswith('SRV_') or len(m)!=2 or len(rr)!=1 or ('J2',p) not in m or (rr[0],2) not in m:good=False;continue
  r=rr[0];node=c[r]['pins'].get(1)
  if node!=net[4:] or node in ('GND','NC') or node.startswith('SRV_'):good=False;continue
  seen.append(node)
  if node not in SRV_NODES or abs(ohms(c[r]['value'])-SRV_NODES[node])>1e-6:good=False
 ok('SRV-SERIES-R-AT-NODE',good and len(seen)==n-2 and len(set(seen))==n-2)
 ok('SRV-COVERS-ODBIOR',set(seen)>=set(SRV_NODES))
 ok('SRV-CSV',[(int(r['pin']),r['siec']) for r in csv_rows('SERWIS.csv')]==[(p,'GND' if s[p]=='GND' else s[p][4:]) for p in sorted(s)])
 # --- part sources (owned THT stand up, everything new is SMD 1206) ---
 srcok=True
 for r,x in c.items():
  if r.startswith('R') and x['value']=='10K':srcok&=x['fp'].endswith('R_Axial_DIN0207_L6.3mm_D2.5mm_P5.08mm_Vertical')
  elif r.startswith('R'):srcok&=x['fp'].startswith('Resistor_SMD:R_1206')
  if r.startswith('C') and x['value']=='100n':srcok&=x['fp'].endswith('C_Disc_D5.0mm_W2.5mm_P5.00mm')
  elif r.startswith('C'):srcok&=x['fp'].startswith('Capacitor_SMD:C_1206')
 ok('PARTS-SOURCES',srcok)
 # --- CAN receiver (as R1) ---
 ok('TCAN-PINOUT',pins('U1',{1:'3V3_IO',2:'GND',3:'5V_SYS',4:'RX_RAW',5:'3V3_IO',6:'CAN_L',7:'CAN_H',8:'3V3_IO'}))
 ok('TCAN-V-SUFFIX',c['U1']['mpn']=='TCAN1051VDRQ1')
 ok('RX-IOFF-BUFFER',pins('U2',{1:'GND',2:'RX_RAW',3:'RX_BUF',4:'3V3_IO',5:'GND',6:'NC',7:'GND',8:'NC',9:'GND',10:'3V3_IO',11:'NC',12:'GND',13:'3V3_IO',14:'3V3_IO'}))
 ok('RX-IOFF-MPN',c['U2']['mpn']=='74LVC125AD,118 Nexperia')
 ok('TVS-PINOUT',pins('D1',{1:'CAN_L',2:'CAN_H',3:'GND'}) and c['D1']['mpn']=='PESD2CAN,215 Nexperia')
 ok('OBD-TWO-WIRES',pins('J3',{1:'CAN_H',2:'CAN_L'}))
 srv=lambda net:{(r,p) for r,p in members(net) if r.startswith('R') and r not in ('R1','R2')}   # the service resistor pin on a node
 def only(net,base):return {m for m in members(net) if m not in srv(net)}==base and len(srv(net))==1
 ok('TX-ONLY-JBP-AND-SERVICE-PIN',only('CAN_TX',{('J1',6)}))   # CAN_TX has no path to the transceiver: only J_BP pin 6 and its service resistor
 ok('RX-NO-BUFFER-BYPASS',only('RX_RAW',{('U1',4),('U2',2),('R2',2)}) and only('CAN_RX',{('R1',2),('J1',8)}))
 ok('NO-TERM-NO-EXTRA-CAN-LOAD',only('CAN_H',{('U1',7),('D1',2),('J3',1)}) and only('CAN_L',{('U1',6),('D1',1),('J3',2)}))
 for r,v,a,b in [('R1','100R','RX_BUF','CAN_RX'),('R2','10K','3V3_IO','RX_RAW')]:ok('RES-'+r,c[r]['value']==v and pins(r,{1:a,2:b}))
 for i,(v,nn) in enumerate([('100n','5V_SYS'),('100n','3V3_IO'),('100n','3V3_IO'),('4u7','5V_SYS'),('4u7','3V3_IO')],1):ok('CAP-'+str(i),c['C'+str(i)]['value']==v and pins('C'+str(i),{1:nn,2:'GND'}))
 # Functional checks consume ACTUAL exported nets (steady-state digital transfer only).
 truth=[]
 for tx in [0,1]:
  for rx in [0,1]:
   nn={'GND':0,'3V3_IO':1,'CAN_TX':tx,'RX_RAW':rx};q=c['U2']['pins']
   if nn.get(q[1])==0:nn[q[3]]=nn.get(q[2])
   r=c['R1']['pins'];nn[r[2]]=nn.get(r[1]);t=c['U1']['pins']
   truth.append({'core_tx':tx,'bus_rx':rx,'core_rx':nn.get(c['J1']['pins'][8]),'silent':nn.get(t[8]),'txd':nn.get(t[1])})
 ok('ACTUAL-NETS-SILENT',all(t['silent']==1 and t['txd']==1 for t in truth))
 ok('ACTUAL-NETS-RX',all(t['core_rx']==t['bus_rx'] for t in truth))
 return out,truth
def mutate(c,fn):
 cc=copy.deepcopy(c);fn(cc);return [t['id'] for t in check(cc)[0] if not t['pass']]
if __name__=='__main__':
 c=read();base,truth=check(c);neg=[]
 assert all(t['pass'] for t in base),[t for t in base if not t['pass']]
 def setp(r,pin,v):return lambda cc:cc[r]['pins'].__setitem__(pin,v)
 def setf(r,f,v):return lambda cc:cc[r].__setitem__(f,v)
 def swap(r,a,b):
  def f(cc):p=cc[r]['pins'];p[a],p[b]=p[b],p[a]
  return f
 muts=[('silent-low',setp('U1',8,'GND')),('MCU-to-TXD',setp('U1',1,'CAN_TX')),('swap-CAN',setp('U1',7,'CAN_L')),('TVS-common-wrong',setp('D1',3,'3V3_IO')),('RX-buffer-bypass',setp('U1',4,'CAN_RX')),
  ('RX-OE-wrong',setp('U2',1,'3V3_IO')),('unused-input-float',setp('U2',9,'NC')),('missing-RX-pullup',setp('R2',1,'NC')),('RX-R-bypass',setp('R1',1,'CAN_RX')),
  ('extra-120R',lambda cc:cc.update(RX={'pins':{1:'CAN_H',2:'CAN_L'},'value':'120R','mpn':'120R','fp':''})),
  ('jbp-odd-pin-signal',setp('J1',3,'CAN_RX')),('jbp-odd-pin-NC',setp('J1',5,'NC')),('jbp-even-pin-GND',setp('J1',6,'GND')),('jbp-second-5V-lost',setp('J1',10,'GND')),
  ('jbp-TX-RX-swapped',swap('J1',6,8)),('jbp-unused-signal',setp('J1',10,'CAN_H')),('jbp-CSV-mismatch',setp('J1',4,'5V_SYS')),
  ('srv-first-not-GND',setp('J2',1,'3V3_IO')),('srv-last-not-GND',setp('J2',9,'CAN_H')),('srv-extra-GND-inside',setp('J2',5,'GND')),('srv-10th-pin',setp('J2',10,'GND')),
  ('srv-no-resistor',setp('J2',2,'5V_SYS')),('srv-resistor-shorted',setp('R3',2,'5V_SYS')),('srv-CAN-resistor-1k',setf('R8','value','1K')),('srv-resistor-0R',setf('R5','value','0R')),
  ('srv-CAN_TX-to-transceiver',setp('U1',1,'SRV_CAN_TX')),('srv-duplicate-node',setp('R4',1,'5V_SYS')),('srv-node-GND',setp('R6',1,'GND')),
  ('R1-fp-THT',setf('R1','fp','Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P5.08mm_Vertical')),('R2-fp-SMD',setf('R2','fp','Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder')),
  ('C1-fp-SMD',setf('C1','fp','Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder')),('C4-fp-THT',setf('C4','fp','Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm')),
  ('U1-mpn',setf('U1','mpn','TCAN1051DRQ1')),('U2-mpn',setf('U2','mpn','74HC125')),('C2-value',setf('C2','value','1p')),('R1-value',setf('R1','value','10K'))]
 for name,fn in muts:
  bad=mutate(c,fn);neg.append({'mutation':name,'expected':'detected','detected':bool(bad),'by':bad})
 zero=mutate(c,lambda cc:None);neg.append({'mutation':'null-control (no change)','expected':'clean','detected':bool(zero),'by':zero})
 (P/'verification/electrical-checks.json').write_text(json.dumps({'checks':base,'negative_controls':neg,'truth_table':truth,'scope':'Static pin topology and steady-state digital transfer only; no simulated transient protection or power sequencing.','hardware_tested':False},indent=2)+'\n')
 print('Electrical',len(base),'checks;',len(muts),'mutations + null control')
 assert all(t['detected'] for t in neg[:-1]),[t for t in neg[:-1] if not t['detected']]
 assert not neg[-1]['detected'],neg[-1]
