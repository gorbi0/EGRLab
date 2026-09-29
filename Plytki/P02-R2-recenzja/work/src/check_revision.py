"""Constrain R2 delta against frozen R1 evidence. Independent of parts generator."""
from pathlib import Path
import json,pcbnew as p
P=Path(__file__).resolve().parents[1]
old=json.loads((P/'reference/R1-parts.json').read_text(encoding='utf-8'));new=json.loads((P/'docs/parts.json').read_text(encoding='utf-8'))
pinchanges={}
for r in old:
 for n,net in old[r]['pins'].items():
  if new[r]['pins'].get(n)!=net:pinchanges[f'{r}.{n}']=[net,new[r]['pins'].get(n)]
expected={'R8.2':['P02_BANK_DIV','P02_BANK_CMP'],'R11.2':['P02_VPROT_DIV','P02_VPROT_CMP'],
 'U7.3':['P02_BANK_DIV','P02_BANK_CMP'],'U7.5':['P02_VPROT_DIV','P02_VPROT_CMP'],'TP3.1':['HOLD_STORE','HOLD_TP']}
changedvalues=sorted(r for r in old if old[r]['display']!=new[r]['display'])
allowedvalues={'R5','R6','R7','R8','R9','R10','R11','C14','C15','TP3'}
b0=p.LoadBoard(str(P/'reference/R1.kicad_pcb'));b1=p.LoadBoard(str(P/'eda/P02.kicad_pcb'))
def positions(b):return {f.GetReference():[f.GetPosition().x,f.GetPosition().y,f.GetOrientationDegrees()] for f in b.GetFootprints()}
p0=positions(b0);p1=positions(b1);moved={r:[p0[r],p1.get(r)] for r in p0 if p0[r]!=p1.get(r)}
checks=[('Only four added parts',set(new)-set(old)=={'R18','R19','R20','C16'} and set(old)<=set(new)),
 ('Only explicitly approved pin changes',pinchanges==expected),('Only approved value changes',set(changedvalues)<=allowedvalues),
 ('Only R8/R11/TP3 moved from R1',set(moved)=={'R8','R11','TP3'})]
rep={'checks':[{'check':n,'pass':bool(ok)} for n,ok in checks],'pin_changes':pinchanges,'value_changes':changedvalues,'moved':moved,'passed':all(ok for _,ok in checks)}
(P/'verification/revision-checks.json').write_text(json.dumps(rep,indent=2)+'\n')
print(json.dumps(rep['checks'],indent=2));assert rep['passed']
