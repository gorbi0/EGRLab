"""Independent R2->R3 delta and physical integration contracts, including mutations."""
from pathlib import Path
from cadlib import P,parse,subs,one
import json,csv,copy,hashlib,xml.etree.ElementTree as ET
checks=[]
def check(name,ok):
 checks.append({'id':name,'pass':bool(ok)})
 assert ok,name
def exported(path):
 root=ET.parse(path).getroot()
 nodes={(x.get('ref'),x.get('pin')):n.get('name').split('/')[-1] for n in root.findall('./nets/net') for x in n.findall('node')}
 comps={x.get('ref'):x for x in root.findall('./components/comp')}
 return nodes,comps
old,oc=exported(P/'reference/R2-P01.xml');new,nc=exported(P/'verification/P01.xml')
changed={k:(v,new.get(k)) for k,v in old.items() if new.get(k)!=v}
check('R2 unchanged nodes except Q1 drain',changed=={('Q1','2'):('VPROT','P01_Q1_DRAIN')})
check('only new electrical component LK1',set(nc)-set(oc)=={'LK1'} and not(set(oc)-set(nc)))
check('LK1 only connection between drain and VPROT',new['LK1','1']=='P01_Q1_DRAIN' and new['LK1','2']=='VPROT' and {k for k,v in new.items() if v=='P01_Q1_DRAIN'}=={('LK1','1'),('Q1','2')})
for r in oc:
 check(r+' value unchanged from R2',oc[r].findtext('value')==nc[r].findtext('value'))

fp=parse((P/'eda/libraries/P01.pretty/Link_Kelvin_P10.kicad_mod').read_text())
pads=subs(fp,'pad');small=[p for p in pads if float(one(p,'drill')[1])==1];force=[p for p in pads if float(one(p,'drill')[1])==2.4]
check('LK1 has two power and two Kelvin PTH',len(small)==len(force)==2 and {p[1] for p in small}=={'1','2'} and {p[1] for p in force}=={'1','2'})
hs=parse((P/'eda/libraries/P01.pretty/HS_Fischer_SK129_63.5_STS_D2.8.kicad_mod').read_text())
hp=subs(hs,'pad');xy=[tuple(map(float,one(p,'at')[1:3])) for p in hp]
check('HS pins match Fischer drawing P25.4',sorted(xy)==[(-12.7,0),(12.7,0)] and all(float(one(p,'drill')[1])>=2.8 for p in hp))
bat=parse((P/'eda/libraries/P01.pretty/Pigtail_PWR_2x2.5mm2.kicad_mod').read_text())
bp=[p for p in subs(bat,'pad') if p[1]]
check('J7 thermal settings present on both power pads',len(bp)==2 and all(int(one(p,'zone_connect')[1])==1 and float(one(p,'thermal_bridge_width')[1])==1.2 and float(one(p,'thermal_gap')[1])==.3 for p in bp))
rows=list(csv.DictReader((P/'docs/interfejsy.csv').open(encoding='utf-8-sig'),delimiter=';'))
batrow=next(x for x in rows if x['lacze']=='BAT')
check('BAT cable correctly soldered and sex assigned',batrow['koniec_lutowany']=='P01/J7' and batrow['dlugosc_mm']=='200' and batrow['typ_wtyku']=='H_BAT:1786174 meski; EXT:1757019 zenski')
mechanics=list(csv.reader((P/'docs/BOM-MECHANIKA.csv').open(encoding='utf-8-sig'),delimiter=';'))
check('mechanical BOM matches reversed BAT',any(r[0]=='H_BAT / wtyk Phoenix1786174 (męski)' for r in mechanics) and any(r[0].startswith('EXT/J_BATA Phoenix1757019') for r in mechanics))

contract=json.loads((P/'integration/P02-HOLD/contract.json').read_text())
def valid_topology(d):
 c=d['connections']
 return (c['D_OR']['1']=='VPROT' and c['D_OR']['2']=='VLOG_RES' and c['D_OR']['3']=='HOLD_FUSED'
  and c['R_CHARGE']['1']=='VPROT' and c['R_CHARGE']['2']=='CHARGE_D'
  and c['D_CHARGE']['1']==c['D_CHARGE']['3']=='CHARGE_D' and c['D_CHARGE']['2']=='HOLD_FUSED'
  and c['F_HOLD']['1']=='HOLD_FUSED' and c['F_HOLD']['2']=='HOLD_STORE'
  and all(c[r]['1']=='HOLD_STORE' and c[r]['2']=='GND' for r in ['C_H1','C_H2','C_H3'])
  and d['R_charge_ohm']>=47 and d['converter_inputs']==['P02 F2.IN','P02 F3.IN'])
check('HOLD topology has limited charging and no diode return to VPROT',valid_topology(contract))
for label,ref,pin,net in [('reverse_OR','D_OR','2','VPROT'),('bypass_charge','R_CHARGE','2','HOLD_STORE'),('cap_on_input','C_H1','1','VPROT'),('fuse_bypassed','F_HOLD','2','HOLD_FUSED')]:
 m=copy.deepcopy(contract);m['connections'][ref][pin]=net
 check('HOLD mutation rejected: '+label,not valid_topology(m))
rec=json.loads((P/'verification/recovery.json').read_text());dyn=json.loads((P/'verification/dynamics.json').read_text())
check('recovery from current XML and contract',rec['xml_sha256']==hashlib.sha256((P/'verification/P01.xml').read_bytes()).hexdigest() and rec['contract_sha256']==hashlib.sha256((P/'integration/P02-HOLD/contract.json').read_bytes()).hexdigest())
check('recovery checks completed',len(rec['checks'])==12 and rec['pass'])
check('finite reserve exhaustion was observed',next(r for r in rec['results'] if r['id']=='recovery_exhausted_hold')['bus_below_7V'])
check('C6 WIMA dV/dt below15V/us in screening domain',max(r['C6_peak_dVdt_V_per_us'] for r in dyn['results'])<=15)
check('HOLD energy bound passes',json.loads((P/'verification/hold-budget.json').read_text())['pass'])
erc=json.loads((P/'verification/erc.json').read_text())
check('ERC default ignored categories not expanded',set(x['key'] for x in erc['ignored_checks'])=={'single_global_label','four_way_junction','simulation_model_issue','footprint_filter'})
result={'checks':checks,'pass':True,'scope':'R2 delta, physical access and declared integration topology; no PCB routing/thermal/hardware proof.'}
(P/'verification/r3-checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(len(checks),'R3 checks PASS; 4 HOLD topology mutations rejected.')
