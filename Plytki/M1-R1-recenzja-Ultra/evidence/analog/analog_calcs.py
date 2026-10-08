from pathlib import Path
import json,math
p=Path(__file__).parent
g=json.loads((p/'geometry.json').read_text())
for n in ['K_PLUS','K_MINUS','INA_PLUS','INA_MINUS','ADC_CH1','ADC_CH2']:
 ts=[t for t in g['tracks'] if t['net'].split('/')[-1]==n]
 print(n, 'total_trace_mm',sum(t['len'] for t in ts),'layers',sorted(set(t['layer'] for t in ts)))
points=[g['pads']['RSH1.2']['xy'],[42.72,32.5],g['pads']['R22.1']['xy'],g['pads']['R22.2']['xy'],[50.095,32.5],g['pads']['U4.8']['xy'],g['pads']['U4.1']['xy'],[50.095,40.5],g['pads']['R23.2']['xy'],g['pads']['R23.1']['xy'],[42.62,40.5],[42.62,36.66],[49.28,30],[49.28,21.4],g['pads']['RSH1.3']['xy']]
area=abs(sum(x*v-y*u for (x,y),(u,v) in zip(points,points[1:]+points[:1])))/2
r={'planar_loop_area_mm2_including_straight_chord_inside_IC_and_shunt':area,'points':points}
cross=[46.78,32.5]
lobes=[points[:3]+[cross]+points[12:],[cross]+points[3:12]]
areaof=lambda a:abs(sum(x*v-y*u for (x,y),(u,v) in zip(a,a[1:]+a[:1])))/2
r['projected_lobe_areas_approx_mm2']=[areaof(a) for a in lobes]
print(r);(p/'kelvin-geometry.json').write_text(json.dumps(r,indent=2))
for title,rth,c in [('MOTOR',1/(1/300000+1/100000+1/5e6),220e-12),('SENSOR',1/(1/100000+1/5e6),220e-12),('VSENSE',1/(1/499000+1/100000+1/5e6),220e-12),('CURRENT',1/(1/1000+1/5e6),1e-9)]:
 print(title,'Rth',rth,'tau_us',rth*c*1e6,'fc_Hz',1/(2*math.pi*rth*c))

