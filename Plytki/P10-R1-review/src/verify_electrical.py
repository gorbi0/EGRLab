"""Independent pin requirements against native KiCad XML, plus deliberate circuit mutations."""
from pathlib import Path
import xml.etree.ElementTree as ET,json,copy
P=Path(__file__).resolve().parents[1]

def read():
 root=ET.parse(P/'verification/P10.xml').getroot();c={}
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
 def pins(r,v):return c[r]['pins']==v
 for r,file,mate in [('J1','P02-R3-parts.json','J10'),('J2','P03-R2-parts.json','J8')]:
  data=json.loads((P/'reference'/file).read_text());expected={int(k):v for k,v in data[mate]['pins'].items()}
  ok('MATE-'+r,pins(r,expected))
 ok('TCAN-PINOUT',pins('U1',{1:'3V3_IO',2:'GND',3:'5V_SYS',4:'RX_RAW',5:'3V3_IO',6:'CAN_L',7:'CAN_H',8:'3V3_IO'}))
 ok('TCAN-V-SUFFIX',c['U1']['mpn']=='TCAN1051VDRQ1')
 ok('RX-IOFF-BUFFER',pins('U2',{1:'GND',2:'RX_RAW',3:'RX_BUF',4:'3V3_IO',5:'GND',6:'NC',7:'GND',8:'NC',9:'GND',10:'3V3_IO',11:'NC',12:'GND',13:'3V3_IO',14:'3V3_IO'}))
 ok('RX-IOFF-MPN',c['U2']['mpn']=='74LVC125AD,118 Nexperia')
 ok('TVS-PINOUT',pins('D1',{1:'CAN_L',2:'CAN_H',3:'GND'}) and c['D1']['mpn']=='PESD2CAN,215 Nexperia')
 ok('OBD-TWO-WIRES',pins('J3',{1:'CAN_H',2:'CAN_L'}))
 def members(net):return {(r,p) for r,x in c.items() for p,n in x['pins'].items() if n==net}
 ok('TX-ONLY-TESTPAD',members('CAN_TX')=={('J2',1),('TP6',1)})
 ok('RX-NO-BUFFER-BYPASS',members('RX_RAW')=={('U1',4),('U2',2),('R2',2),('TP4',1)} and members('CAN_RX')=={('R1',2),('J2',3),('TP5',1)})
 ok('NO-TERM-NO-EXTRA-CAN-LOAD',members('CAN_H')=={('U1',7),('D1',2),('J3',1)} and members('CAN_L')=={('U1',6),('D1',1),('J3',2)})
 for r,v,a,b in [('R1','100R','RX_BUF','CAN_RX'),('R2','10K','3V3_IO','RX_RAW')]:ok('RES-'+r,c[r]['value']==v and pins(r,{1:a,2:b}))
 for i,(v,n) in enumerate([('100n','5V_SYS'),('100n','3V3_IO'),('100n','3V3_IO'),('4u7','5V_SYS'),('4u7','3V3_IO')],1):ok('CAP-'+str(i),c['C'+str(i)]['value']==v and pins('C'+str(i),{1:n,2:'GND'}))
 for i,n in enumerate(['5V_SYS','3V3_IO','GND','RX_RAW','CAN_RX','CAN_TX'],1):ok('TP-'+str(i),pins('TP'+str(i),{1:n}))
 # Functional checks consume ACTUAL exported nets. They are not a hardware timing/UVLO simulation.
 truth=[]
 for tx in [0,1]:
  for rx in [0,1]:
   n={'GND':0,'3V3_IO':1,'CAN_TX':tx,'RX_RAW':rx};q=c['U2']['pins']
   if n.get(q[1])==0:n[q[3]]=n.get(q[2])
   r=c['R1']['pins'];n[r[2]]=n.get(r[1]);t=c['U1']['pins']
   truth.append({'core_tx':tx,'bus_rx':rx,'core_rx':n.get(c['J2']['pins'][3]),'silent':n.get(t[8]),'txd':n.get(t[1])})
 ok('ACTUAL-NETS-SILENT',all(t['silent']==1 and t['txd']==1 for t in truth))
 ok('ACTUAL-NETS-RX',all(t['core_rx']==t['bus_rx'] for t in truth))
 return out,truth

if __name__=='__main__':
 c=read();base,truth=check(c);neg=[]
 def trial(name,fn):
  cc=copy.deepcopy(c);fn(cc);bad=[t['id'] for t in check(cc)[0] if not t['pass']];neg.append({'mutation':name,'detected':bool(bad),'by':bad})
 for name,r,pin,v in [('silent-low','U1',8,'GND'),('MCU-to-TXD','U1',1,'CAN_TX'),('swap-CAN','U1',7,'CAN_L'),('TVS-common-wrong','D1',3,'3V3_IO'),('RX-buffer-bypass','U1',4,'CAN_RX'),('RX-OE-wrong','U2',1,'3V3_IO'),('unused-input-float','U2',9,'NC'),('wrong-KEY4','J2',4,'GND'),('wrong-LV','J1',3,'5V_SYS'),('missing-RX-pullup','R2',1,'NC'),('RX-R-bypass','R1',1,'CAN_RX')]:
  trial(name,lambda cc,r=r,pin=pin,v=v:cc[r]['pins'].__setitem__(pin,v))
 for r,field,v in [('U1','mpn','TCAN1051DRQ1'),('U2','mpn','74HC125'),('C2','value','1p'),('R1','value','10K')]:trial(r+'-'+field,lambda cc,r=r,field=field,v=v:cc[r].__setitem__(field,v))
 trial('extra-120R',lambda cc:cc.update(RX={'pins':{1:'CAN_H',2:'CAN_L'},'value':'120R','mpn':'120R'}))
 (P/'verification/electrical-checks.json').write_text(json.dumps({'checks':base,'negative_controls':neg,'truth_table':truth,'scope':'Static pin topology and steady-state digital transfer only; no simulated transient protection or power sequencing.','hardware_tested':False},indent=2)+'\n')
 print('Electrical',len(base),'checks;',len(neg),'mutations')
 assert all(x['pass'] for x in base),[x for x in base if not x['pass']]
 assert all(x['detected'] for x in neg),neg
