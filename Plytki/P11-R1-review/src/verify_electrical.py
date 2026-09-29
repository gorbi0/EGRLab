"""Independent frozen-neighbour and baseline contracts, actual-net graph interlock, negative controls."""
from pathlib import Path
import xml.etree.ElementTree as ET,json,copy,itertools
P=Path(__file__).resolve().parents[1]
def read(path):
 root=ET.parse(path).getroot();c={x.get('ref'):{'pins':{},'value':x.findtext('value')} for x in root.findall('./components/comp')}
 for n in root.findall('./nets/net'):
  name=n.get('name').split('/')[-1]
  for x in n.findall('node'):c[x.get('ref')]['pins'][x.get('pin')]='NC' if name.startswith('unconnected-') else name
 return c
def pin(*s):return {str(i):n for i,n in enumerate(s,1)}
CONTACT=pin('PANEL_3V3','TEST_KEY','TEST_KEY','ILK_L1_L2','PANEL_3V3','DIAG_L1_L2','ILK_L1_L2','LOOP_OUT','DIAG_L1_L2','LOGGER_CLEAR','PANEL_3V3','STOP_NC_OUT','GND','ARM_CONTACT','GND','MARK','PANEL_3V3','TEST_PRESENT','NC','NC')
SW={'X11':pin('GND','ARM_CONTACT'),'X12':pin('TEST_KEY','ILK_L1_L2','PANEL_3V3','DIAG_L1_L2'),'X13':pin('ILK_L1_L2','LOOP_OUT','DIAG_L1_L2','LOGGER_CLEAR'),'X14':pin('GND','MARK'),'X15':pin('PANEL_3V3','TEST_KEY','NC','NC'),'X16':pin('PANEL_3V3','STOP_NC_OUT','NC','NC'),'X17':pin('PANEL_3V3','TEST_PRESENT')}
def graph(c,key,l1,l2,loop,stop,test,broken=None):
 g={}
 def join(r,a,b,on):
  if not on or broken in [(r,a),(r,b)]:return
  ns=c[r]['pins'];x,y=ns[str(a)],ns[str(b)]
  if x=='NC' or y=='NC':return
  g.setdefault(x,set()).add(y);g.setdefault(y,set()).add(x)
 for r,a,b,on in [('X15',1,2,key),('X12',1,2,not l1),('X12',3,4,not l1),('X13',1,2,not l2),('X13',3,4,not l2),('X8',10,11,loop),('X16',1,2,not stop),('X17',1,2,test)]:join(r,a,b,on)
 seen={c['J5']['pins']['1']};todo=list(seen)
 while todo:
  for nxt in g.get(todo.pop(),[]):
   if nxt not in seen:seen.add(nxt);todo.append(nxt)
 return {'mech':c['J5']['pins']['4'] in seen,'key':c['J5']['pins']['3'] in seen,'clear':c['J4']['pins']['4'] in seen,'stop_feed':c['J5']['pins']['7'] in seen,'present':c['J4']['pins']['5'] in seen}
def check(c):
 out=[]
 def ok(k,v):out.append({'id':k,'pass':bool(v)})
 for r,file,mate in [('J4','P03-R2-parts.json','J9'),('J5','P04-R2.1-parts.json','J8'),('J7','P05-R1-parts.json','J4'),('J1','P06-R1-parts.json','J3'),('J10','P08-R1-parts.json','J4')]:
  expected=json.loads((P/'reference'/file).read_text())[mate]['pins'];ok('MATE-'+r,c[r]['pins']==expected)
 base=read(P/'reference/P11-baseline.xml')
 for r in ['J2','J3','J8','J9']:
  ok('BASELINE-'+r,c[r]['pins']==base[r]['pins'])
 for x,j in [('X2','J2'),('X3','J3'),('X8','J8')]:ok('TAIL-TO-PORT-'+x,c[x]['pins']==c[j]['pins'])
 ok('CONTACT-TAIL',c['J11']['pins']==CONTACT)
 for r,ps in SW.items():ok('CONTACT-'+r,c[r]['pins']==ps)
 for r in ['J6','X6']:ok('SCOPE-'+r,c[r]['pins']==pin('N_J_SCOPE_HOT','GND'))
 def members(n):return {(r,p) for r,v in c.items() for p,net in v['pins'].items() if net==n}
 for net,expected in [('AGND_SENSOR',{('J10','2'),('J8','4'),('X8','4')}),('5V_SENSOR',{('J10','1'),('J8','3'),('X8','3')}),('ECU_P1',{('J1','1'),('J2','1'),('X2','1')}),('EGR_P1',{('J1','2'),('J2','2'),('X2','2')}),('T_EGR_P1',{('J9','1'),('J8','1'),('X8','1')}),('T_EGR_P3',{('J9','2'),('J8','2'),('X8','2')})]:ok('ISOLATED-'+net,members(net)==expected)
 ok('NO-ACTIVE-OR-LOAD-PARTS',set(c)=={'J'+str(i) for i in range(1,12)}|{'X2','X3','X6','X8'}|set(SW))
 truth=[]
 for key,l1,l2,loop,stop,test in itertools.product([False,True],repeat=6):
  actual=graph(c,key,l1,l2,loop,stop,test);expected=dict(mech=key and not l1 and not l2 and loop,key=key,clear=not l1 and not l2,stop_feed=not stop,present=test)
  truth.append(dict(key=key,l1=l1,l2=l2,loop=loop,stop=stop,test=test,actual=actual,expected=expected))
 ok('ACTUAL-NETS-64-STATES',all(x['actual']==x['expected'] for x in truth))
 for r,p in [('X15',1),('X12',1),('X12',2),('X13',1),('X13',2),('X8',10),('X8',11)]:ok(f'OPEN-WIRE-KILLS-{r}.{p}',not graph(c,1,0,0,1,0,1,(r,p))['mech'])
 ok('STOP-OPEN-WIRE',not graph(c,1,0,0,1,0,1,('X16',1))['stop_feed'])
 return out,truth
if __name__=='__main__':
 c=read(P/'verification/P11.xml');base,truth=check(c);neg=[]
 def trial(name,fn):
  cc=copy.deepcopy(c);fn(cc);bad=[x['id'] for x in check(cc)[0] if not x['pass']];neg.append({'mutation':name,'detected':bool(bad),'by':bad})
 for r,p,n in [('J5','1','3V3_IO'),('J5','7','PANEL_3V3'),('J5','4','LOOP_OUT'),('X12','2','TEST_KEY'),('X13','2','ILK_L1_L2'),('X13','4','PANEL_3V3'),('X15','2','PANEL_3V3'),('J10','2','GND'),('J9','1','ECU_P1'),('X8','1','EGR_P1'),('J7','7','GND'),('J11','12','GND'),('X16','3','PANEL_3V3'),('J4','6','GND'),('X6','2','AGND_SENSOR'),('X3','2','TAP_P1')]:trial(f'{r}.{p}->{n}',lambda x,r=r,p=p,n=n:x[r]['pins'].__setitem__(p,n))
 trial('extra-LED-load',lambda x:x.update(LED99={'pins':pin('PANEL_3V3','GND'),'value':'LED'}))
 (P/'verification/electrical-checks.json').write_text(json.dumps({'checks':base,'negative_controls':neg,'truth_table':truth,'hardware_tested':False,'scope':'Static net graph, no mechanical travel/timing/failure-rate qualification. NC switches assumed healthy. Shared TAPs do not select source.'},indent=2)+'\n')
 print('Electrical',len(base),'checks;',len(neg),'mutations');assert all(x['pass'] for x in base),[x for x in base if not x['pass']];assert all(x['detected'] for x in neg)
