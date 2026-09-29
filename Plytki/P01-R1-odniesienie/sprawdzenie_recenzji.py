"""Review sensitivity only; no hardware qualification or revised design.

Uses the reviewed Opus script without executing its main block or writing into its folder.
"""
from pathlib import Path
import runpy,json,hashlib
P=Path(__file__).resolve().parent
source=Path(r'C:\Users\tgorbacz\Documents\GORBI\Priv\Kia\Sportage\EGRLab\P01-R1-recenzja\model\model_bramki_Q1.py')
m=runpy.run_path(str(source),run_name='review_model')
p=(22e-9,680e-9,47000.0,33.0)
rows=[]
# Correct definition: Ciss=Cgs+Cgd. Intrinsic capacitances here are typical, not bounds.
ciss,crss=3.5e-9,.29e-9
for dv in [24,30,48]:
 for tol in [0,.05,.10]:
  c5=p[0]*(1+tol);c6=p[1]*(1-tol)
  rows.append({'step_V':dv,'assumed_cap_tolerance':tol,'C5_nF':c5*1e9,'C6_nF':c6*1e9,
               'initial_VSG_capacitive_V':dv*(c5+crss)/(c5+c6+ciss)})
# Keep the author's model otherwise unchanged to show its comparison results directly.
sensitivity=[]
for beta in [60,30,20,10]:
 m['_i_gate'].__globals__['BETA_Q2']=beta
 w=m['wylaczenie'](p)
 sensitivity.append({'assumed_beta':beta,'t_to_0p5_us':None if w['t05'] is None else w['t05']*1e6})
m['_i_gate'].__globals__['BETA_Q2']=60
steps=[]
for v0,v1,vp0 in [(0,24,0),(0,48,0),(18,48,17)]:
 w=m['sim_idealne'](p,1e-6,V0=v0,V1=v1,VP0=vp0,vt=1.0,Tend=200e-6)
 steps.append({'V0':v0,'V1':v1,'VP0':vp0,'tr_us':1,'assumed_vt_V':1,**w})
out={'scope':'Review calculations; assumed tolerances and beta are sensitivity parameters, not manufacturer guaranteed corners.',
 'model_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'capacitive_bound_estimates':rows,
 'turnoff_sensitivity_original_model':sensitivity,'extended_steps_original_model':steps}
(P/'dodatkowe-obliczenia.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
