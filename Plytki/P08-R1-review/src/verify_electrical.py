"""Independent requirements against native XML; data-driven gate propagation and mutations."""
from pathlib import Path
import xml.etree.ElementTree as ET,json,copy,math,itertools,re
P=Path(__file__).resolve().parents[1]
def read():
 root=ET.parse(P/'verification/P08.xml').getroot();c={}
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
 for r,name,pins_expected in [('J1','LV08',{1:'5V_SYS',2:'GND',3:'3V3_IO',4:'GND'}),('J2','SENSOR-M2.2',{1:'SENSOR_PERMIT',2:'NC',3:'SENSOR_OK',4:'GND',5:'NC',6:'NC'}),('J3','SFAULT',{1:'SENSOR_HEALTHY',2:'GND',3:'NC',4:'NC',5:'NC',6:'NC'}),('J4','TSENSOR',{1:'5V_SENSOR',2:'AGND_SENSOR'})]:ok('IF-'+name,pins(r,pins_expected))
 for r,board,br in [('J1','P02-R3-review','J8'),('J2','P04-R2.1-review','J4'),('J3','P03-R2-review','J6')]:
  data=json.loads((P/f'reference/{board}-parts.json').read_text());expected={int(k):v for k,v in data[br]['pins'].items()}
  ok('MATE-'+board,c[r]['pins']==expected)
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
 ok('NO-GROUND-BYPASS',ag=={'K1','R18','J4','TP13'},'No GND-referenced output capacitor, LED or bleed around return contact.')
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
if __name__=='__main__':
 c=read();checks,truths=check(c);negative=[]
 muts=[('NC-NO-swap','K1',2,'5V_SENSOR'),('ground-bypass','R18',2,'GND'),('reversed-flyback','D1',1,'SENSOR_COIL_LOW'),('bad-TPS-pin','U1',3,'SENSOR_LOCAL'),('missing-guard','U8',1,'NC'),('wrong-guard-power','U8',2,'5V_SYS'),('5V-to-HC','U3',2,'SUP5_RAW'),('ready-permit-loop','U3',1,'SENSOR_PERMIT'),('fault-retry-loop','U3',5,'SENSOR_FAULT_LOCAL_N'),('health-wrong-gate','U3',10,'PERMIT_LOCAL'),('no-IOff','U5',14,'5V_SYS'),('bad-LV','J1',3,'5V_SYS'),('wrong-SENSOR-key','J2',2,'GND'),('wrong-SFAULT','J3',1,'SENSOR_FAULT_LOCAL_N'),('no-pulldown','R14',2,'NC'),('coil-common','U2',10,'GND')]
 for name,r,pin,net in muts:
  cc=copy.deepcopy(c);cc[r]['pins'][pin]=net;bad=[t['id'] for t in check(cc)[0] if not t['pass']];negative.append({'mutation':name,'detected':bool(bad),'by':bad})
 for name,r,field,new in [('wrong-limit','R1','value','23K2'),('bad-divider','R16','value','68K'),('wrong-variant','U1','mpn','TPS2553-1DBVR'),('wrong-supervisor','U8','mpn','MCP130-300DI/TO')]:
  cc=copy.deepcopy(c);cc[r][field]=new;bad=[t['id'] for t in check(cc)[0] if not t['pass']];negative.append({'mutation':name,'detected':bool(bad),'by':bad})
 r=232;limits={'min_ma':25230/(r*1.01)**1.016,'typ_ma':23950/r**.977,'max_ma':22980/(r*.99)**.94}
 result=dict(checks=checks,negative_controls=negative,truth_table=truths,current_limit=limits,hardware_tested=False)
 (P/'verification/electrical-checks.json').write_text(json.dumps(result,indent=2)+'\n')
 print('Electrical checks',len(checks),'negative controls',len(negative),limits)
 for x in checks:
  if not x['pass']:print('FAIL',x)
 assert all(x['pass'] for x in checks) and all(x['detected'] for x in negative)
