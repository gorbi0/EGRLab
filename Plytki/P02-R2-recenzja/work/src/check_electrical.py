"""Electrical review checks: real exported netlist, parts tolerances, full corner enumeration.
No transistor-level simulation or bench certification is claimed.
Run with Python 3, optionally --negative for deliberate topology/value mutations.
"""
from pathlib import Path
import xml.etree.ElementTree as ET, json, itertools, math, copy, sys, hashlib
P=Path(__file__).resolve().parents[1]
parts=json.loads((P/'docs/parts.json').read_text(encoding='utf-8'))
xml=ET.parse(P/'verification/P02.xml').getroot()
values={c.get('ref'):c.findtext('value') for c in xml.findall('./components/comp')}
pins={(x.get('ref'),x.get('pin')):n.get('name').split('/')[-1] for n in xml.findall('./nets/net') for x in n.findall('node')}
def value(r, vv=values):
 s=vv[r].split(' / ')[0].upper().removesuffix('F')
 for k,m in [('K',1e3),('M',1e6),('R',1),('U',1e-6),('N',1e-9)]:
  if k in s:
   a,b=s.split(k);return float(a+('.'+b if b else ''))*m
 return float(s)
def limits(r,vv):
 t=parts[r]['tolerance']+parts[r]['tcr_ppm']*1e-6*25
 return [value(r,vv)*(1-t),value(r,vv)*(1+t)]
def corner(vv,refs):
 rt,rb,rs,rf,rp=refs;up=[];down=[];hys=[];jump=[]
 # Vref initial 2.483..2.507, full industrial drift +/-34mV,
 # current correction +/-4mV (0.5ohm*8mA), LM2903 full-temp Vos +/-15mV.
 for a,b,c,d,e,v,ib,rail,vol,leak in itertools.product(*[limits(r,vv) for r in refs],
   [2.483-.034-.004-.015,2.507+.034+.004+.015],[-.5e-6,0],[3.135,3.465],[0,.7],[0,1e-6]):
  A=1+a/b;S=A*c+a
  hi=(rail/e+v/d-leak)/(1/e+1/d)
  u=v*A+(v-vol)*S/d+ib*S;l=v*A+(v-hi)*S/d+ib*S
  up.append(u);down.append(l);hys.append(u-l);jump.append((hi-vol)*c/(c+d))
 a,b,c,d,e=[value(r,vv) for r in refs];v=2.495;hi=(3.3/e+v/d)/(1/e+1/d)
 A=1+a/b;S=A*c+a
 return {'rise_V':[min(up),max(up)],'fall_V':[min(down),max(down)],'hysteresis_V':[min(hys),max(hys)],
 'instant_feedback_min_V':min(jump),'nominal_rise_V':v*A+(v-.15)*S/d,'nominal_fall_V':v*A+(v-hi)*S/d,
 'filter_tau_max_us':1/(1/a+1/b+1/(c+d))*13e-9*1e6,'corners':len(up)}
def evaluate(vv, pp):
 checks=[]
 def ck(n,v):checks.append({'check':n,'pass':bool(v)})
 mismatch=[]
 for r,p in parts.items():
  for n,net in p['pins'].items():
   got=pp.get((r,n),'')
   if net!='NC' and got!=net:mismatch.append((r,n,net,got))
 ck('Every exported functional pin agrees with explicit parts contract',not mismatch)
 # Independent assertions, not generated from parts.py.
 ck('Feedback isolated from C14/C15 by R18/R19', all(pp[(r,n)]==net for r,n,net in [
 ('C14','1','P02_BANK_DIV'),('R18','1','P02_BANK_DIV'),('R18','2','P02_BANK_CMP'),('R8','2','P02_BANK_CMP'),('U7','3','P02_BANK_CMP'),
 ('C15','1','P02_VPROT_DIV'),('R19','1','P02_VPROT_DIV'),('R19','2','P02_VPROT_CMP'),('R11','2','P02_VPROT_CMP'),('U7','5','P02_VPROT_CMP')]) and value('C14',vv)==value('C15',vv)==10e-9)
 ck('Protected TP3 has 1k/2W series element; raw rail not on any TP',pp[('TP3','1')]=='HOLD_TP' and pp[('R20','1')]=='HOLD_STORE' and pp[('R20','2')]=='HOLD_TP' and value('R20',vv)==1000 and all(net!='HOLD_STORE' for (r,n),net in pp.items() if r.startswith('TP')))
 bank=corner(vv,['R6','R7','R18','R8','R12']);prot=corner(vv,['R9','R10','R19','R11','R13'])
 ck('Bank falling >=9.60V, rising <=10.50V across declared corners',bank['fall_V'][0]>=9.60 and bank['rise_V'][1]<=10.50)
 ck('VPROT falling >=11.57V, rising <=12.65V across declared corners',prot['fall_V'][0]>=11.57 and prot['rise_V'][1]<=12.65)
 ck('Feedback step >=20mV; RC time constant <=110us',all(x['instant_feedback_min_V']>=.02 and x['filter_tau_max_us']<=110 for x in [bank,prot]))
 # Declared loss limit, not an unverified data-sheet guarantee of the assembly.
 C=.066*.8; power=6+.15;loss=1.2;floor=7
 hold=C*((9.5-loss)**2-floor**2)/(2*power)
 ck('Conservative energy model at bank9.5V gives >=50ms',hold>=.050)
 rmin=1000*(1-.05-250e-6*25)
 ck('TP3 sustained short at32V <=35mA and <=1.1W',32/rmin<=.035 and 32**2/rmin<=1.1)
 return {'checks':checks,'bank':bank,'vprot':prot,'pin_mismatches':mismatch,
 'hold_model_seconds_at9V5':hold,'bank_energy_max_J':.5*.066*1.2*32**2,
 'bleed_to1V_seconds':4700*1.01*.066*1.2*math.log(32),'tp3_short_mA':32/rmin*1000,
 'tp3_short_W':32**2/rmin,'limits':'0..50C; 3V3_IO +/-5%; regulator/diode/ESR path loss <=1.2V by bench; NOT_TESTED hardware'}
rep=evaluate(values,pins)
rep['inputs_sha256']={f:hashlib.sha256((P/f).read_bytes()).hexdigest() for f in ['verification/P02.xml','docs/parts.json','src/check_electrical.py']}
rep['passed']=all(c['pass'] for c in rep['checks'])
(P/'verification/electrical-checks.json').write_text(json.dumps(rep,indent=2)+'\n')
for c in rep['checks']:print('PASS' if c['pass'] else 'FAIL',c['check'])
if '--negative' in sys.argv:
 tests=[]
 for name,rv,pv,target in [('bank_old_ratio',{'R6':'26K7'},{},'Bank falling'),('vprot_old_ratio',{'R9':'34K8'},{},'VPROT falling'),('cap_on_feedback',{}, {('C14','1'):'P02_BANK_CMP'},'Feedback isolated'),('raw_tp3',{}, {('TP3','1'):'HOLD_STORE'},'Protected TP3'),('unqualified_100n',{'C15':'100N'},{},'Feedback isolated')]:
  r=evaluate({**values,**rv},{**pins,**pv});hit=any(not c['pass'] and c['check'].startswith(target) for c in r['checks']);tests.append({'mutation':name,'expected':target,'detected':hit})
 (P/'verification/electrical-negative-controls.json').write_text(json.dumps(tests,indent=2)+'\n')
 print('Electrical negative controls:',sum(t['detected'] for t in tests),'/',len(tests));assert all(t['detected'] for t in tests)
sys.exit(0 if rep['passed'] else 1)

