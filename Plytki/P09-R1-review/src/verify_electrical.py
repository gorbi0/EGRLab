"""Independent requirements against exported native XML; pin-driven logic and fault mutations."""
from pathlib import Path
import xml.etree.ElementTree as ET,json,copy,itertools
P=Path(__file__).resolve().parents[1]
def read():
 root=ET.parse(P/'verification/P09.xml').getroot();c={}
 for x in root.findall('./components/comp'):
  fields={a.get('name'):a.text for a in x.findall('./fields/field')}
  c[x.get('ref')]={'pins':{},'value':x.findtext('value'),'mpn':fields.get('MPN','')}
 for n in root.findall('./nets/net'):
  name=n.get('name').split('/')[-1]
  for x in n.findall('node'):c[x.get('ref')]['pins'][int(x.get('pin'))]='NC' if name.startswith('unconnected-') else name
 return c
def check(c):
 out=[]
 def ok(k,v):out.append({'id':k,'pass':bool(v)})
 def pins(r,x):return c[r]['pins']==x
 for r,file,mate in [('J1','P02-R3-parts.json','J9'),('J2','P03-R2-parts.json','J7')]:
  data=json.loads((P/'reference'/file).read_text());expected={int(k):v for k,v in data[mate]['pins'].items()}
  ok('MATE-'+r,pins(r,expected))
 ok('U1-INPUT-IOFF',pins('U1',{1:'GND',2:'SPI3_SCLK',3:'CLK_BUF',4:'GND',5:'SPI3_MOSI',6:'MOSI_BUF',7:'GND',8:'CS1_BUF',9:'TC1_CS',10:'GND',11:'CS2_BUF',12:'TC2_CS',13:'GND',14:'3V3_IO'}))
 ok('U2-MISO-IOFF',pins('U2',{1:'OE1_N',2:'TC1_MISO',3:'TX1',4:'OE2_N',5:'TC2_MISO',6:'TX2',7:'GND',8:'NC',9:'GND',10:'3V3_IO',11:'NC',12:'GND',13:'3V3_IO',14:'3V3_IO'}))
 ok('U3-HC139',pins('U3',{1:'GND',2:'CS1_BUF',3:'CS2_BUF',4:'NC',5:'OE2_N',6:'OE1_N',7:'NC',8:'GND',9:'NC',10:'NC',11:'NC',12:'NC',13:'GND',14:'GND',15:'3V3_IO',16:'3V3_IO'}))
 ok('MPN',c['U3']['mpn']=='SN74HC139N' and all(c[r]['mpn']=='74LVC125AD,118 Nexperia' for r in ['U1','U2']))
 for ch,j in [(1,'J3'),(2,'J4')]:
  ok('MODULE-PINOUT-'+j,pins(j,{1:f'TC{ch}_VIN',2:f'TC{ch}_3VO',3:'GND',4:'CLK_MODULE',5:f'TC{ch}_MISO',6:'MOSI_MODULE',7:f'TC{ch}_CS_MODULE',8:f'TC{ch}_FLT_N',9:f'TC{ch}_DRDY_N'}))
  ok('VIN-SELECT-'+j,pins('JP'+str(ch),{1:'3V3_IO',2:f'TC{ch}_VIN',3:'5V_SYS'}))
  for suffix,refs in [('3VO',{j,'TP'+str(7+ch)}),('FLT_N',{j,'TP'+str(9+ch)}),('DRDY_N',{j,'TP'+str(11+ch)})]:
   ok('ISOLATED-'+j+suffix,{r for r,v in c.items() if f'TC{ch}_{suffix}' in v['pins'].values()}==refs)
 resistors=[('10K','3V3_IO','TC1_CS'),('10K','3V3_IO','TC2_CS'),('100K','SPI3_SCLK','GND'),('100K','SPI3_MOSI','GND'),('10K','3V3_IO','CS1_BUF'),('10K','3V3_IO','CS2_BUF'),('100K','CLK_BUF','GND'),('100K','MOSI_BUF','GND'),('100K','TC1_MISO','GND'),('100K','TC2_MISO','GND'),('100R','TX1','SPI3_MISO'),('100R','TX2','SPI3_MISO'),('100K','SPI3_MISO','GND'),('47R','CLK_BUF','CLK_MODULE'),('47R','MOSI_BUF','MOSI_MODULE'),('47R','CS1_BUF','TC1_CS_MODULE'),('47R','CS2_BUF','TC2_CS_MODULE'),('10K','3V3_IO','OE1_N'),('10K','3V3_IO','OE2_N')]
 for i,(v,a,b) in enumerate(resistors,1):ok('RES-'+str(i),c['R'+str(i)]['value']==v and pins('R'+str(i),{1:a,2:b}))
 for i,(v,a) in enumerate([('100n','3V3_IO')]*3+[('4u7','3V3_IO'),('4u7','5V_SYS'),('1u','TC1_VIN'),('1u','TC2_VIN')],1):ok('CAP-'+str(i),c['C'+str(i)]['value']==v and pins('C'+str(i),{1:a,2:'GND'}))
 truths=[]
 for a,b in itertools.product([0,1],repeat=2):
  n={'GND':0,'3V3_IO':1,'TC1_CS':a,'TC2_CS':b,'SPI3_SCLK':0,'SPI3_MOSI':0}
  q=c['U1']['pins']
  for oe,ip,op in [(1,2,3),(4,5,6),(10,9,8),(13,12,11)]:
   if n.get(q[oe])==0 and q[ip] in n:n[q[op]]=n[q[ip]]
  q=c['U3']['pins'];sel=n.get(q[2],-10)+2*n.get(q[3],-10)
  for i,pin in enumerate([4,5,6,7]):n[q[pin]]=int(n.get(q[1])!=0 or i!=sel)
  q=c['U2']['pins'];actual=[ch for ch,oe in [(1,1),(2,4)] if n.get(q[oe])==0]
  expected={(0,1):[1],(1,0):[2],(0,0):[],(1,1):[]}[(a,b)]
  truths.append({'CS':[a,b],'enabled_MISO':actual,'expected':expected})
 ok('ACTUAL-NETLIST-TRUTH',all(t['enabled_MISO']==t['expected'] for t in truths))
 return out,truths
if __name__=='__main__':
 c=read();base,truth=check(c);neg=[]
 for name,r,pin,new in [('swap-decoder','U3',6,'OE2_N'),('enable-on-both-CS','U3',5,'OE1_N'),('unused-input-float','U2',9,'NC'),('5V-logic','U1',14,'5V_SYS'),('VIN-output-short','J3',2,'3V3_IO'),('module-reversed','J4',1,'TC2_DRDY_N'),('wrong-key','J2',4,'GND'),('wrong-LV','J1',3,'5V_SYS'),('bypass-MISO-R','R11',1,'SPI3_MISO'),('missing-CS-pullup','R1',1,'NC'),('wrong-VIN-select','JP1',3,'GND'),('DRDY-bus-short','J4',9,'SPI3_MISO')]:
  cc=copy.deepcopy(c);cc[r]['pins'][pin]=new;bad=[t['id'] for t in check(cc)[0] if not t['pass']];neg.append({'mutation':name,'detected':bool(bad),'by':bad})
 for r,field,value in [('R11','value','10K'),('C6','value','1n'),('U1','mpn','74HC125')]:
  cc=copy.deepcopy(c);cc[r][field]=value;bad=[t['id'] for t in check(cc)[0] if not t['pass']];neg.append({'mutation':r+'-'+field,'detected':bool(bad),'by':bad})
 (P/'verification/electrical-checks.json').write_text(json.dumps({'checks':base,'negative_controls':neg,'truth_table':truth,'hardware_tested':False},indent=2)+'\n')
 print('Electrical',len(base),'checks;',len(neg),'mutations')
 assert all(t['pass'] for t in base),[t for t in base if not t['pass']]
 assert all(t['detected'] for t in neg),neg
