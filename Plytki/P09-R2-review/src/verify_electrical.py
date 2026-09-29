"""Independent requirements against the exported native KiCad XML: pin-driven logic, S1 connector rules (J_BP, service strip), part sources, and deliberate mutations
(plus a null control that must stay clean)."""
from pathlib import Path
import xml.etree.ElementTree as ET,json,copy,itertools,csv
P=Path(__file__).resolve().parents[1]
def read():
 root=ET.parse(P/'verification/P09.xml').getroot();c={}
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
# service strip contract (independent of parts.py): node net -> required series resistor, ohms (all P09 nodes are rails or logic -> 1k; 10k would be for high-impedance nodes)
SRV_NODES={'3V3_IO':1000,'5V_SYS':1000,'TC1_VIN':1000,'TC2_VIN':1000,'TC1_3VO':1000,'TC2_3VO':1000,'CS1_BUF':1000,'CS2_BUF':1000,'OE1_N':1000,'OE2_N':1000,'SPI3_MISO':1000}
def ohms(v):
 v=v.upper().replace(' ','');m=1
 if v.endswith('K'):m=1000;v=v[:-1]
 elif v.endswith('R'):v=v[:-1]
 return float(v)*m
def check(c):
 out=[]
 def ok(k,v):out.append({'id':k,'pass':bool(v)})
 def pins(r,x):return c[r]['pins']==x
 def members(net):return {(r,p) for r,x in c.items() for p,n in x['pins'].items() if n==net}
 # --- J_BP (edge A) ---
 j=c['J1']['pins'];nonG=[n for p,n in j.items() if p%2==0]
 ok('JBP-16-PINS',sorted(j)==list(range(1,17)) and c['J1']['fp'].endswith('IDC-Header_2x08_P2.54mm_Horizontal'))
 ok('JBP-ODD-GND',all(j.get(p)=='GND' for p in range(1,17,2)))
 ok('JBP-EVEN-SIGNALS',all(j.get(p) not in (None,'GND','NC') and not j[p].startswith('SRV_') for p in range(2,17,2)))
 ok('JBP-SPI-NETS',members('SPI3_SCLK')=={('J1',6),('U1',2),('R3',1)} and members('SPI3_MOSI')=={('J1',8),('U1',5),('R4',1)} and members('SPI3_MISO')>= {('J1',10),('R11',2),('R12',2),('R13',1)}
    and members('TC1_CS')=={('J1',12),('U1',9),('R1',2)} and members('TC2_CS')=={('J1',14),('U1',12),('R2',2)})
 d1={int(k):v for k,v in json.loads((P/'reference/P02-R3-parts.json').read_text())['J9']['pins'].items()};d2={int(k):v for k,v in json.loads((P/'reference/P03-R2-parts.json').read_text())['J7']['pins'].items()}
 old={n for n in list(d1.values())+list(d2.values()) if n not in ('GND','NC')}
 ok('JBP-CONTINUITY-R1',{n for n in nonG}==old)   # every signal/supply of the two R1 harnesses is on J_BP, nothing else
 ok('JBP-S1-SUPPLY-PINS',nonG.count('5V_SYS')>=2 and nonG.count('3V3_IO')>=1 and all(nonG.count(n)==1 for n in old-SUPPLIES))
 used=lambda net:any(r not in ('J1','J2') for r,_ in members(net))
 ok('JBP-SUPPLY-USED',all(used(n) for n in SUPPLIES&set(nonG)) and set(nonG)&SUPPLIES==SUPPLIES)
 ok('JBP-CSV',{int(r['pin']):r['siec'] for r in csv_rows('J_BP.csv')}==j)
 # --- service strip (edge B) ---
 s=c['J2']['pins'];n=max(s) if s else 0
 ok('SRV-MAX-13',sorted(s)==list(range(1,n+1)) and n<=13 and c['J2']['fp'].endswith('PinHeader_1x13_P2.54mm_Horizontal'))
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
 ok('SRV-COVERS-ODBIOR',set(seen)>={'3V3_IO','5V_SYS','TC1_VIN','TC2_VIN','TC1_3VO','TC2_3VO','CS1_BUF','CS2_BUF','OE1_N','OE2_N','SPI3_MISO'})
 ok('SRV-CSV',[(int(r['pin']),r['siec']) for r in csv_rows('SERWIS.csv')]==[(p,'GND' if s[p]=='GND' else s[p][4:]) for p in sorted(s)])
 # --- part sources (owned THT stand up, everything new is SMD 1206) ---
 srcok=True
 for r,x in c.items():
  if r.startswith('R') and x['value'] in ('10K','100K'):srcok&=x['fp'].endswith('R_Axial_DIN0207_L6.3mm_D2.5mm_P5.08mm_Vertical')
  elif r.startswith('R'):srcok&=x['fp'].startswith('Resistor_SMD:R_1206')
  if r.startswith('C') and x['value']=='100n':srcok&=x['fp'].endswith('C_Disc_D5.0mm_W2.5mm_P5.00mm')
  elif r.startswith('C'):srcok&=x['fp'].startswith('Capacitor_SMD:C_1206')
 ok('PARTS-SOURCES',srcok)
 # --- silicon and modules (as R1) ---
 ok('U1-INPUT-IOFF',pins('U1',{1:'GND',2:'SPI3_SCLK',3:'CLK_BUF',4:'GND',5:'SPI3_MOSI',6:'MOSI_BUF',7:'GND',8:'CS1_BUF',9:'TC1_CS',10:'GND',11:'CS2_BUF',12:'TC2_CS',13:'GND',14:'3V3_IO'}))
 ok('U2-MISO-IOFF',pins('U2',{1:'OE1_N',2:'TC1_MISO',3:'TX1',4:'OE2_N',5:'TC2_MISO',6:'TX2',7:'GND',8:'NC',9:'GND',10:'3V3_IO',11:'NC',12:'GND',13:'3V3_IO',14:'3V3_IO'}))
 ok('U3-HC139',pins('U3',{1:'GND',2:'CS1_BUF',3:'CS2_BUF',4:'NC',5:'OE2_N',6:'OE1_N',7:'NC',8:'GND',9:'NC',10:'NC',11:'NC',12:'NC',13:'GND',14:'GND',15:'3V3_IO',16:'3V3_IO'}))
 ok('MPN',c['U3']['mpn']=='SN74HC139N' and all(c[r]['mpn']=='74LVC125AD,118 Nexperia' for r in ['U1','U2']))
 for ch,jm in [(1,'J3'),(2,'J4')]:
  ok('MODULE-PINOUT-'+jm,pins(jm,{1:f'TC{ch}_VIN',2:f'TC{ch}_3VO',3:'GND',4:'CLK_MODULE',5:f'TC{ch}_MISO',6:'MOSI_MODULE',7:f'TC{ch}_CS_MODULE',8:'NC',9:'NC'}))
  ok('VIN-SELECT-'+jm,pins('JP'+str(ch),{1:'3V3_IO',2:f'TC{ch}_VIN',3:'5V_SYS'}))
  m3=members(f'TC{ch}_3VO');ok('ISOLATED-'+jm+'-3VO',len(m3)==2 and (jm,2) in m3 and all(r.startswith('R') and p==1 for r,p in m3 if r!=jm))   # 3Vo only to its service resistor, never to a rail or the other module
 resistors=[('10K','3V3_IO','TC1_CS'),('10K','3V3_IO','TC2_CS'),('100K','SPI3_SCLK','GND'),('100K','SPI3_MOSI','GND'),('10K','3V3_IO','CS1_BUF'),('10K','3V3_IO','CS2_BUF'),('100K','CLK_BUF','GND'),('100K','MOSI_BUF','GND'),('100K','TC1_MISO','GND'),('100K','TC2_MISO','GND'),('100R','TX1','SPI3_MISO'),('100R','TX2','SPI3_MISO'),('100K','SPI3_MISO','GND'),('47R','CLK_BUF','CLK_MODULE'),('47R','MOSI_BUF','MOSI_MODULE'),('47R','CS1_BUF','TC1_CS_MODULE'),('47R','CS2_BUF','TC2_CS_MODULE'),('10K','3V3_IO','OE1_N'),('10K','3V3_IO','OE2_N')]
 for i,(v,a,b) in enumerate(resistors,1):ok('RES-'+str(i),c['R'+str(i)]['value']==v and pins('R'+str(i),{1:a,2:b}))
 for i,(v,a) in enumerate([('100n','3V3_IO')]*3+[('4u7','3V3_IO'),('4u7','5V_SYS'),('1u','TC1_VIN'),('1u','TC2_VIN')],1):ok('CAP-'+str(i),c['C'+str(i)]['value']==v and pins('C'+str(i),{1:a,2:'GND'}))
 truths=[]
 for a,b in itertools.product([0,1],repeat=2):
  nn={'GND':0,'3V3_IO':1,'TC1_CS':a,'TC2_CS':b,'SPI3_SCLK':0,'SPI3_MOSI':0}
  q=c['U1']['pins']
  for oe,ip,op in [(1,2,3),(4,5,6),(10,9,8),(13,12,11)]:
   if nn.get(q[oe])==0 and q[ip] in nn:nn[q[op]]=nn[q[ip]]
  q=c['U3']['pins'];sel=nn.get(q[2],-10)+2*nn.get(q[3],-10)
  for i,pin in enumerate([4,5,6,7]):nn[q[pin]]=int(nn.get(q[1])!=0 or i!=sel)
  q=c['U2']['pins'];actual=[ch for ch,oe in [(1,1),(2,4)] if nn.get(q[oe])==0]
  expected={(0,1):[1],(1,0):[2],(0,0):[],(1,1):[]}[(a,b)]
  truths.append({'CS':[a,b],'enabled_MISO':actual,'expected':expected})
 ok('ACTUAL-NETLIST-TRUTH',all(t['enabled_MISO']==t['expected'] for t in truths))
 return out,truths
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
 muts=[('swap-decoder',setp('U3',6,'OE2_N')),('enable-on-both-CS',setp('U3',5,'OE1_N')),('unused-input-float',setp('U2',9,'NC')),('5V-logic',setp('U1',14,'5V_SYS')),
  ('VIN-output-short',setp('J3',2,'3V3_IO')),('module-reversed',setp('J4',1,'TC2_DRDY_N')),('bypass-MISO-R',setp('R11',1,'SPI3_MISO')),('missing-CS-pullup',setp('R1',1,'NC')),
  ('wrong-VIN-select',setp('JP1',3,'GND')),('DRDY-bus-short',setp('J4',9,'SPI3_MISO')),
  ('jbp-odd-pin-signal',setp('J1',3,'SPI3_MOSI')),('jbp-odd-pin-NC',setp('J1',5,'NC')),('jbp-even-pin-GND',setp('J1',6,'GND')),('jbp-second-5V-lost',setp('J1',16,'GND')),
  ('jbp-CS-swapped',swap('J1',12,14)),('jbp-unused-signal',setp('J1',16,'SPI3_MISO')),('jbp-CSV-mismatch',setp('J1',8,'SPI3_SCLK')),
  ('srv-first-not-GND',setp('J2',1,'3V3_IO')),('srv-last-not-GND',setp('J2',13,'CS1_BUF')),('srv-extra-GND-inside',setp('J2',5,'GND')),('srv-14th-pin',setp('J2',14,'GND')),
  ('srv-no-resistor',setp('J2',2,'3V3_IO')),('srv-resistor-shorted',setp('R20',2,'3V3_IO')),('srv-resistor-100R',setf('R25','value','100R')),('srv-resistor-0R',setf('R25','value','0R')),
  ('srv-extra-load-on-pin',setp('U3',4,'SRV_CS1_BUF')),('srv-duplicate-node',setp('R21',1,'3V3_IO')),('srv-node-GND',setp('R23',1,'GND')),
  ('R1-fp-SMD',setf('R1','fp','Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder')),('R11-fp-THT',setf('R11','fp','Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P5.08mm_Vertical')),
  ('C1-fp-SMD',setf('C1','fp','Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder')),('C4-fp-THT',setf('C4','fp','Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm')),
  ('R11-value',setf('R11','value','10K')),('C6-value',setf('C6','value','1n')),('U1-mpn',setf('U1','mpn','74HC125'))]
 for name,fn in muts:
  bad=mutate(c,fn);neg.append({'mutation':name,'expected':'detected','detected':bool(bad),'by':bad})
 zero=mutate(c,lambda cc:None);neg.append({'mutation':'null-control (no change)','expected':'clean','detected':bool(zero),'by':zero})
 (P/'verification/electrical-checks.json').write_text(json.dumps({'checks':base,'negative_controls':neg,'truth_table':truth,'hardware_tested':False},indent=2)+'\n')
 print('Electrical',len(base),'checks;',len(muts),'mutations + null control')
 assert all(t['detected'] for t in neg[:-1]),[t for t in neg[:-1] if not t['detected']]
 assert not neg[-1]['detected'],neg[-1]
