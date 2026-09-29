"""Independent physical faults, always in disposable copies with fresh DRC.
The original board, schematic and rules are never mutated.
"""
from pathlib import Path
import json,subprocess,sys,shutil,hashlib
from sexpr import parse,dump,one,sub,Atom
from provenance import current_receipt
P=Path(__file__).resolve().parents[1];out=P/'verification/negative-controls';out.mkdir(exist_ok=True)
original=P/'eda/P01.kicad_pcb';original_sha=hashlib.sha256(original.read_bytes()).hexdigest()
results=[]
for case in ('probe_open','power_short_stale_report','missing_heatsink_keepout','missing_tab_marker','d4_moved'):
 folder=out/case;folder.mkdir(exist_ok=True);target=folder/'P01.kicad_pcb'
 root=parse(original.read_text())
 if case=='probe_open':
  candidates=[v for v in sub(root,'segment') if tuple(float(n) for n in one(v,'end')[1:])==(101.4,24.5) or tuple(float(n) for n in one(v,'start')[1:])==(101.4,24.5)]
  assert len(candidates)==1;root.remove(candidates[0])
 elif case=='power_short_stale_report':
  v=max((v for v in sub(root,'segment') if str(one(v,'net')[1]).endswith('SAFE_N')),key=lambda v:sum((float(a)-float(c))**2 for a,c in zip(one(v,'start')[1:],one(v,'end')[1:])))
  one(v,'width')[1]=Atom('12')
 elif case=='missing_heatsink_keepout':
  z=next(z for z in sub(root,'zone') if sub(z,'name') and one(z,'name')[1]=='HS2 F.Cu keepout');root.remove(z)
 elif case=='missing_tab_marker':
  fp=next(fp for fp in sub(root,'footprint') if any(v[1]=='Reference' and v[2]=='Q2' for v in sub(fp,'property')))
  lines=[v for v in sub(fp,'fp_line') if one(v,'layer')[1]=='F.SilkS' and float(one(one(v,'stroke'),'width')[1])>=.35]
  assert lines
  for line in lines:fp.remove(line)
 else:
  fp=next(fp for fp in sub(root,'footprint') if any(v[1]=='Reference' and v[2]=='D4' for v in sub(fp,'property')))
  one(fp,'at')[2]=Atom('40')
 target.write_text(dump(root)+'\n')
 for src in (P/'eda').glob('*.kicad_sch'):shutil.copy2(src,folder/src.name)
 shutil.copy2(P/'eda/P01.kicad_pro',folder/'P01.kicad_pro')
 shutil.copy2(P/'eda/fp-lib-table',folder/'fp-lib-table')
 # Library paths remain the release libraries, not copies with silently changed pads.
 (folder/'fp-lib-table').write_text((folder/'fp-lib-table').read_text().replace('${KIPRJMOD}/libraries',(P/'eda/libraries').as_posix()))
 cached=json.loads((P/'verification/drc.provenance.json').read_text())
 stale_rejected=not current_receipt(cached,target)
 run=subprocess.run([sys.executable,str(P/'src/verify_pcb.py'),str(target)],capture_output=True,text=True)
 (folder/'run.log').write_text(run.stdout+'\n'+run.stderr)
 report=json.loads(target.with_suffix('.checks.json').read_text())
 failed=[c['check'] for c in report['checks'] if not c['pass']]
 drc=json.loads(target.with_suffix('.drc.json').read_text())
 if case=='probe_open':specific=bool(drc['unconnected_items']) and 'Actual Q1 source/gate probe tracks <= 5 mm' in failed
 elif case=='power_short_stale_report':specific=stale_rejected and any(v['type']=='shorting_items' for v in drc['violations'])
 elif case=='missing_heatsink_keepout':specific=any('F.Cu rule areas cover' in v for v in failed)
 elif case=='missing_tab_marker':specific=any('tab side marked' in v for v in failed)
 else:specific='R3 D4 clamp paths to Q1 source/gate <=8 mm' in failed
 results.append({'case':case,'detected':run.returncode==1 and not report['pass'] and specific,'stale_receipt_rejected':stale_rejected,'failed_checks':failed,
 'fresh_drc_counts':{k:len(drc[k]) for k in ('violations','unconnected_items','schematic_parity')}})
assert hashlib.sha256(original.read_bytes()).hexdigest()==original_sha
(P/'verification/negative-controls.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2));assert all(r['detected'] for r in results)
