"""Read actual exported netlist, symbols and footprint files. Mutation checks use copies."""
from cadlib import P,parse,subs,one,pin_defs
import json,csv,xml.etree.ElementTree as ET,tempfile,subprocess,sys,copy,shutil
parts=json.loads((P/'docs/parts.json').read_text(encoding='utf-8'))
checks=[];audit=[]
def check(name,result):
 checks.append({'check':name,'pass':bool(result)})
 if not result:raise AssertionError(name)
for r,p in parts.items():
 lib,name=p['footprint'].split(':')
 fp=parse((P/'eda/libraries'/(lib+'.pretty')/(name+'.kicad_mod')).read_text(encoding='utf-8'))
 pads=subs(fp,'pad');electrical=[pad for pad in pads if pad[1]]
 check(r+' footprint pad numbers match schematic terminals',{str(pad[1]) for pad in electrical}==set(p['pins']))
 check(r+' all electrical pads plated through-hole',all(pad[2]=='thru_hole' for pad in electrical))
 holes=[float(one(pad,'drill')[1]) for pad in electrical]
 if r in ['Q1','Q2','D2']:
  check(r+' TO220 holes cover max rectangular lead with clearance',all(d>=1.4 for d in holes))
 audit.append({'ref':r,'mpn':p['mpn'],'footprint':p['footprint'],'pads':','.join(pad[1] for pad in electrical),'drill_mm':','.join(map(str,holes)),'source':p['url'],'status':'PAD_NUMBERS_CHECKED; package fit reviewed separately'})
 if r in ['J5','J7']:
  anchors=[pad for pad in pads if pad[2]=='np_thru_hole']
  check(r+' two anchors 12.5 mm from solder row',len(anchors)==2 and all(abs(float(one(a,'at')[2]))==12.5 for a in anchors))
  tie_width=2.5 if r=='J5' else 3.6
  check(r+' anchor hole accepts selected tie',all(float(one(a,'drill')[1])>tie_width for a in anchors))
with (P/'verification/footprint-pads.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,audit[0].keys(),delimiter=';');w.writeheader();w.writerows(audit)

lib=parse((P/'eda/libraries/P01.kicad_sym').read_text(encoding='utf-8'))
symbols={s[1]:s for s in subs(lib,'symbol')}
# These maps are independent manufacturer pin functions, not copied from our netlist.
for sym,want in {'TL431LP':{'1':'K','2':'A','3':'REF'},'Q_NPN_EBC':{'1':'E','2':'B','3':'C'},'Q_PNP_EBC':{'1':'E','2':'B','3':'C'},'Q_PMOS_GDS':{'1':'G','2':'D','3':'S'}}.items():
 got={n:str(one(pin,'name')[1]) for n,pin in pin_defs(symbols[sym]).items()}
 check(sym+' symbol pin functions',got==want)
for r in ['C8','C10','C11','C12','C13']:
 check(r+' specified H5 ceramic is 5 mm pitch',parts[r]['mpn'].endswith('3H5') and parts[r]['footprint']=='P01:C_Vishay_K15_H5_P5')
erc=json.loads((P/'verification/erc.json').read_text(encoding='utf-8'))
check('KiCad ERC reports zero violations at default severities',all(not s.get('violations') for s in erc['sheets']))

root=ET.parse(P/'verification/P01.xml').getroot()
def findnode(tree,r,p):
 return next((net,node) for net in tree.findall('./nets/net') for node in net.findall('node') if node.get('ref')==r and node.get('pin')==p)
def swap(tree,r,a,b):
 na,pa=findnode(tree,r,a);nb,pb=findnode(tree,r,b)
 na.remove(pa);nb.remove(pb);na.append(pb);nb.append(pa)
with tempfile.TemporaryDirectory(prefix='p01-check-') as td:
 td=__import__('pathlib').Path(td)
 for test in ['Q1_DS_swapped','Q2_GS_swapped','U2_OV_inputs_swapped','SAFE_N_disconnected','J6_footprint_removed','C5_value_changed','R21_value_changed','Q2_MPN_changed','D9_polarity_reversed']:
  t=copy.deepcopy(root)
  if test=='Q1_DS_swapped':swap(t,'Q1','2','3')
  if test=='Q2_GS_swapped':swap(t,'Q2','1','3')
  if test=='D9_polarity_reversed':swap(t,'D9','1','2')
  if test=='C5_value_changed':t.find("./components/comp[@ref='C5']/value").text='220nF / 100V'
  if test=='R21_value_changed':t.find("./components/comp[@ref='R21']/value").text='4K7 / 0.5W'
  if test=='Q2_MPN_changed':t.find("./components/comp[@ref='Q2']/property[@name='MPN']").set('value','2N5401YBU')
  if test=='U2_OV_inputs_swapped':swap(t,'U2','2','3')
  if test=='SAFE_N_disconnected':
   net,node=findnode(t,'J5','2');net.remove(node)
  if test=='J6_footprint_removed':t.find("./components/comp[@ref='J6']/footprint").text=''
  xml=td/(test+'.xml');out=td/(test+'.json');ET.ElementTree(t).write(xml,encoding='utf-8')
  proc=subprocess.run([sys.executable,str(P/'src/verify.py'),'--xml',str(xml),'--out',str(out)],capture_output=True)
  check('Mutation detected: '+test,proc.returncode==1 and bool(json.loads(out.read_text(encoding='utf-8'))['errors']))
 # Re-run unchanged DC model on a disposable copy; immutable baseline is never written.
 model=td/'static-model';shutil.copytree(P/'baseline/P01-PROTECT',model);(model/'verification').mkdir(exist_ok=True)
 proc=subprocess.run([sys.executable,str(model/'src/verify.py')],capture_output=True)
 check('Baseline DC model executes successfully',proc.returncode==0)
 shutil.copy2(model/'verification/report.json',P/'verification/legacy-static-model.json')

(P/'verification/package-checks.json').write_text(json.dumps({'checks':checks,'pass':all(c['pass'] for c in checks),'scope':'Connectivity, pin functions and footprint pad mapping; no hardware or transistor dynamics validation.'},indent=2),encoding='utf-8')
print(f'{len(checks)} package checks PASS; 9 injected regressions detected; legacy DC model replayed (old gate values are not R2 validation)')
