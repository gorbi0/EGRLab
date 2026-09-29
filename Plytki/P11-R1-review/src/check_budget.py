"""Resistive PANEL_3V3 corner model sourced from frozen P03/P04 parts; separate leakage sensitivity."""
from pathlib import Path
import json,itertools
P=Path(__file__).resolve().parents[1];safe=json.loads((P/'reference/P04-R2.1-parts.json').read_text());core=json.loads((P/'reference/P03-R2-parts.json').read_text())
def value(d,r):
 s=d[r]['value'].split(' / ')[0].upper();return float(s.replace('K','').replace('R',''))*(1000 if 'K' in s else 1)
assert safe['R40']['pins']=={'1':'3V3_IO','2':'PANEL_3V3'}
assert value(safe,'R40')==100 and value(safe,'R4')==10000 and value(safe,'R5')==100000
for r,n in [('R27','TEST_KEY'),('R6','LOGGER_CLEAR'),('R8','TEST_PRESENT')]:assert core[r]['pins']=={'1':n,'2':'GND'} and value(core,r)==10000
# P04 TEST_KEY/MECH inputs: 1k series + 10k pulldown each. Verify nodes, not only values.
branches=[]
for ser,net in [('R41','TEST_KEY'),('R42','MECH_OK')]:
 a=safe[ser];assert a['pins']['1']==net and value(safe,ser)==1000
 pd=[r for r,d in safe.items() if r.startswith('R') and set(d['pins'].values())=={a['pins']['2'],'GND'}];assert len(pd)==1 and value(safe,pd[0])==10000
 branches.append({'series':ser,'pd':pd[0],'ohm':value(safe,ser)+value(safe,pd[0])})
rows=[]
for v in [3.18,3.30,3.42]:
 for leakage in [0,1e-6,5e-6]:
  # Conservative low voltages: all external pulldowns -1%, R40/R4 +1%, R5 -1%.
  r40=value(safe,'R40')*1.01;r4=value(safe,'R4')*1.01;r5=value(safe,'R5')*.99
  g=sum(1/(b['ohm']*.99) for b in branches)+sum(1/(value(core,r)*.99) for r in ['R27','R6','R8'])
  # Leakage applied at SAFE_N, includes its extra current through STOP and R40.
  vp=(v-r40*leakage*r5/(r4+r5))/(1+r40*(g+1/(r4+r5)))
  vs=(vp-leakage*r4)*r5/(r4+r5)
  rows.append({'input_V':v,'SAFE_sink_uA':leakage*1e6,'panel_V':vp,'safe_V':vs,'input_mA':(v-vp)/r40*1000,'safe_margin_over_2V7':vs-2.7})
doc={'rows':rows,'input_min_V_assumption':3.18,'source':'P02 acceptance envelope; verify loaded rail at P04. P03 three pulldowns and P04 two input branches included. All closed at once conservative.','branches':branches,'qualification':'Leakage sensitivity is not a measured or guaranteed total leakage budget. P07 remains HOLD. Bench SAFE_N >=2.7V loaded, KEY/MECH after series >=2.4V. No LEDs/pull-downs added on P11.','hardware_tested':False}
(P/'verification/panel-budget.json').write_text(json.dumps(doc,indent=2)+'\n');print(json.dumps(rows[:3]));assert rows[0]['safe_V']>=2.7
