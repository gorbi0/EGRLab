"""Checks actual KiCad XML export against immutable v6.1 reference, not builder intent."""
from pathlib import Path
import xml.etree.ElementTree as ET,json,collections,hashlib,sys,argparse
P=Path(__file__).resolve().parents[1]
args=argparse.ArgumentParser()
args.add_argument('--xml',type=Path,default=P/'verification/P01.xml')
args.add_argument('--out',type=Path,default=P/'verification/connectivity.json')
args=args.parse_args()
base=json.loads((P/'baseline/components.json').read_text(encoding='utf-8'))
delta=json.loads((P/'design/changes.json').read_text(encoding='utf-8'))
parts=json.loads((P/'docs/parts.json').read_text(encoding='utf-8'))
root=ET.parse(args.xml).getroot()
actual={};groups={};errors=[]
for net in root.findall('./nets/net'):
 name=net.get('name');nodes={(x.get('ref'),x.get('pin')) for x in net.findall('node')};groups[name]=nodes
 for n in nodes:actual[n]=name
def canonical(n):return n.rsplit('/',1)[-1]
expected={}
for r,p in parts.items():
 if p['source_ref']=='ADDED_TESTPAD':pins=p['pins']
 elif p['source_ref'] in ['ADDED_R2','ADDED_R3']:
  pins={('1' if n=='K' else '2' if n=='A' else n):v for n,v in delta[r]['pins'].items()}
 else:
  c=dict(base['P01_'+p['source_ref']]);c.update(delta.get(r,{}))
  pins={('1' if n=='K' else '2' if n=='A' else n):v for n,v in c['pins'].items()}
  if pins!=p['pins']:errors.append({'type':'model_modified','ref':r})
 for pin,net in pins.items():
  expected[r,pin]=net
  got=actual.get((r,pin))
  if net=='NC':
   if got and groups[got]!={(r,pin)}:errors.append({'type':'NC_connected','ref':r,'pin':pin,'actual':got})
  elif got is None or canonical(got)!=net:errors.append({'type':'net','ref':r,'pin':pin,'expected':net,'actual':got})
for name,nodes in groups.items():
 names={expected[n] for n in nodes if n in expected and expected[n]!='NC'}
 if len(names)>1:errors.append({'type':'short','net':name,'expected_nets':sorted(names)})
components={x.get('ref'):x for x in root.findall('./components/comp')}
if set(components)!=set(parts):errors.append({'type':'component_set','missing':sorted(set(parts)-set(components)),'extra':sorted(set(components)-set(parts))})
for r,p in parts.items():
 if r in components and components[r].findtext('footprint')!=p['footprint']:errors.append({'type':'footprint_export','ref':r})
 if r in components and components[r].findtext('value')!=p['display']:errors.append({'type':'value_export','ref':r})
 if r in components:
  mpn=components[r].find("./property[@name='MPN']")
  if mpn is None or mpn.get('value')!=p['mpn']:errors.append({'type':'MPN_export','ref':r})
for rel,sha in json.loads((P/'baseline/sha256.json').read_text()).items():
 if hashlib.sha256((P/'baseline'/rel).read_bytes()).hexdigest()!=sha:errors.append({'type':'baseline_changed','file':rel})
report={'baseline':'EGRLab-v6.1-rc1 P01 plus explicit design/changes.json R3 delta','components':len(components),'terminals':len(expected),'nets':len(groups),'errors':errors}
args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
sys.exit(bool(errors))
