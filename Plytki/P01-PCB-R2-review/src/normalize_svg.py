"""Pad the plot viewport by 0.05 mm. Do not scale or change CAD geometry."""
from pathlib import Path
import re,json,hashlib
P=Path(__file__).resolve().parents[1];rows=[]
for name in ['assembly','copper-front','copper-back','silk']:
 f=P/'output/previews'/f'{name}.svg';s=f.read_text();old=re.search(r'width="[0-9.]+mm" height="[0-9.]+mm" viewBox="[^"]+"',s)[0]
 new='width="160.1000mm" height="120.1000mm" viewBox="-0.0500 -0.0500 160.1000 120.1000"'
 s=s.replace(old,new,1);f.write_text(s)
 rows.append({'file':name+'.svg','old_viewport':old,'new_viewport':new,'geometry_changed':False})
(P/'verification/svg-viewport.json').write_text(json.dumps(rows,indent=2)+'\n')
