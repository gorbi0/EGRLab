"""Gate-block screening from actual KiCad XML. Not manufacturer-qualified SPICE.
The comparator/AUX block is a timed ENABLE boundary; delays are explicit.
All R17..R27, C5/C6, Q1..Q5, D4/D9 connections come from the XML.
"""
from pathlib import Path
import xml.etree.ElementTree as ET,json,re,hashlib,argparse
import numpy as np
from ngshared import Spice
P=Path(__file__).resolve().parents[1]
def scalar(s):
 s=s.split('/')[0].strip().replace(' ','').removesuffix('F')
 m=re.fullmatch(r'(\d+(?:\.\d+)?)([RKMunpf]?)(\d*)',s)
 if not m:raise ValueError(s)
 a,u,b=m.groups();return float(a+('.'+b if b else ''))*{'':1,'R':1,'K':1e3,'M':1e6,'u':1e-6,'n':1e-9,'p':1e-12,'f':1e-15}[u]
def load(xml):
 root=ET.parse(xml).getroot();c={x.get('ref'):x for x in root.findall('./components/comp')};nodes={}
 for net in root.findall('./nets/net'):
  n=net.get('name').rsplit('/',1)[-1];n='0' if n=='GND' else n.lower()
  for x in net.findall('node'):nodes[x.get('ref'),x.get('pin')]=n
 def pin(r,p):return nodes[r,str(p)]
 values={r:scalar(c[r].findtext('value')) for r in [*(f'R{i}' for i in range(17,28)),'C5','C6']}
 return c,pin,values

def deck(xml,case,override=None):
 c,pin,v=load(xml);v.update(override or {});tol=case.get('tol',0)
 v['C5']*=1+tol;v['C6']*=1-tol
 if 'c6_factor' in case:v['C6']=load(xml)[2]['C6']*case['c6_factor']
 # Apply an explicit 1% adverse resistor corner to the changed gate branches.
 if case.get('r_corner')=='fast':v['R21']*=.99;v['R22']*=1.01
 if case.get('r_corner')=='slow':
  for r in ['R21','R23','R25','R27']:v[r]*=1.01
  v['R22']*=.99
 # Sensitivity assumptions, not datasheet limits. Intrinsic Cgs excludes Cgd.
 vt=case.get('vt',1);kp=case.get('kp',10);cgd=case.get('cgd',.29e-9);cgs=case.get('cgs',3.21e-9)
 q2c=case.get('q2c',10e-9);bf=case.get('bf',50);tr=case.get('storage',1e-6)
 lines=['P01 R3 gate screening - XML extracted',
 '.options reltol=0.001 abstol=1e-9 vntol=1e-6 method=gear gmin=1e-10',
 f'.model pm VDMOS(pchan vto=-{vt} kp={kp} lambda=0.01 rd=0.004 rs=0.004 cgs=1p cgdmax=1p cgdmin=1p cjo=1p)',
 f'.model npm NPN(is=1e-14 bf={bf} vaf=100 cje=30p cjc=10p tf=2n tr={tr})',
 f'.model ppm PNP(is=1e-14 bf={bf} vaf=100 cje=30p cjc=10p tf=2n tr={tr})',
 '.model body D(is=1n n=1.5 rs=0.01)',
 '.model z15 D(is=1n n=1.5 bv=15 ibv=5m rs=10)',
 f'Vinput input 0 {case["input"]}',f'Rsource input p01_vs {case.get("rs",.05)}',
 'Cin p01_vs 0 10u',f'Venable p01_enable 0 {case["enable"]}',
 f'Cload vprot 0 {case.get("cload",220e-6)}',
 f'Rload vprot 0 {case.get("rload",1e6)}',
 f'Bload vprot 0 I={case.get("iload",0)}*tanh(v(vprot)/0.2)']
 for r,val in v.items():lines.append(f'{r} {pin(r,1)} {pin(r,2)} {val:.12g}')
 for r in ['Q1','Q2','Q3','Q4','Q5']:
  ismos=c[r].find('libsource').get('part')=='Q_PMOS_GDS'
  if ismos:
   g,d,s=[pin(r,i) for i in [1,2,3]]
   # Zero-volt channel monitor excludes external displacement-current branches.
   lines.extend([f'M{r} {r}d {g} {s} pm',f'V{r}i {r}d {d} 0',f'D{r}body {d} {s} body',
                 f'C{r}gs {g} {s} {cgs if r=="Q1" else q2c}',f'C{r}gd {g} {d} {cgd if r=="Q1" else q2c*.3}',f'C{r}ds {d} {s} 600p'])
  else:
   lines.append(f'{r} {pin(r,3)} {pin(r,2)} {pin(r,1)} '+('ppm' if r in ['Q2','Q4'] else 'npm'))
 # Actual drain link topology; channel monitor remains on the transistor side.
 if 'LK1' in c:lines.append(f'RLK1 {pin("LK1",1)} {pin("LK1",2)} {case.get("link_r",.0002)}')
 for r in ['D4','D9']:
  if r in c:lines.append(f'{r} {pin(r,2)} {pin(r,1)} z15')
 if 'precharge' in case:lines.append(f'.ic v(vprot)={case["precharge"]}')
 lines += [f'.tran {case.get("step",.1e-6)} {case["end"]} 0 {case.get("step",.1e-6)}','.end']
 return '\n'.join(lines)

def run_case(sim,xml,case,override=None,save=True):
 d=deck(xml,case,override)
 if save:(P/'simulation/decks'/f'{case["id"]}.cir').write_text(d,encoding='ascii')
 vectors=['time','v(p01_vs)','v(p01_gate)','v(vprot)','i(vq1i)','v(p01_off_base)','v(p01_enable)']
 has_link='LK1' in load(xml)[0]
 if has_link:vectors.append('v(p01_q1_drain)')
 a=sim.run(d,vectors);t=a['time'];vs=a['v(p01_vs)'];vg=a['v(p01_gate)'];vo=a['v(vprot)'];i=a['i(vq1i)'];vsg=vs-vg
 mask=(t>=case.get('measure_start',0));ix=np.flatnonzero(mask)
 t0=case.get('off_at');delay=None
 if t0 is not None:
  hit=np.flatnonzero((t>=t0)&(vsg<.5));delay=float((t[hit[0]]-t0)*1e6) if len(hit) else None
 onset=np.flatnonzero((vo>=.95*vs)&(vs>5)&(t>=.001))
 out={'id':case['id'],'samples':len(t),'peak_VSG_V':float(max(vsg[mask])),'peak_channel_A':float(max(i[mask])),
      'peak_VPROT_V':float(max(vo[mask])),'final_VSG_V':float(vsg[-1]),'final_VPROT_V':float(vo[-1]),
      'positive_channel_charge_uC':float(np.trapezoid(np.maximum(i[mask],0),t[mask])*1e6),
      'channel_energy_mJ':float(np.trapezoid(np.maximum(i[mask]*(vs[mask]-(a['v(p01_q1_drain)'] if has_link else vo)[mask]),0),t[mask])*1e3),
      'C6_peak_dVdt_V_per_us':float(np.max(np.abs(np.diff(vsg)/np.diff(t)))/1e6),
      'off_to_0p5_us':delay,'start_to_95pct_ms':float((t[onset[0]]-.001)*1e3) if len(onset) else None,'case':case}
 if save:
  # Retain endpoints and peaks as well as downsampled trace; all metrics use full trace.
  select=np.unique(np.r_[np.arange(0,len(t),max(1,len(t)//2500)),len(t)-1,np.argmax(vsg),np.argmax(i),np.argmax(vo)])
  np.savetxt(P/'simulation/results'/f'{case["id"]}.csv',np.stack([t,vs,vg,vo,i,a['v(p01_off_base)'],a['v(p01_enable)']],1)[select],delimiter=',',header='t_s,VS_V,GATE_V,VPROT_V,Q1_channel_A,Q2_gate_V,ENABLE_V',comments='')
 return out

def main():
 xml=P/'verification/P01.xml';sim=Spice();cases=[]
 for peak in [14,24,48]:
  for rise in [1e-6,1e-3]:
   for corner in [False,True]:
    cases.append(dict(id=f'hot_{peak}_{rise:g}_{int(corner)}',input=f'PWL(0 0 10u 0 {10e-6+rise} {peak})',enable='0',end=rise+200e-6,step=min(rise/20,2e-6),tol=.05 if corner else 0,cgd=2e-9 if corner else .29e-9,vt=.8 if corner else 1,cgs=2e-9 if corner else 3.21e-9,q2c=20e-9 if corner else 10e-9))
 for voltage in [9,14,17]:
  for load in [0,1.5]:
    cases.append(dict(id=f'start_{voltage}_{load}',input=str(voltage),enable='PWL(0 0 1m 0 1.000001m 2.7)',end=.5,step=10e-6,iload=load,vt=1,cgd=2e-9,tol=-.05,r_corner='fast'))
 cases.append(dict(id='start_slow_corner',input='9',enable='PWL(0 0 1m 0 1.000001m 2.5)',end=.5,step=10e-6,iload=1.5,vt=3,kp=4,bf=30,cgd=2e-9,tol=-.05,r_corner='slow'))
 cases.append(dict(id='start_fast_corner',input='17',enable='PWL(0 0 1m 0 1.000001m 2.9)',end=.5,step=5e-6,iload=1.5,vt=.8,kp=20,bf=100,cgd=.1e-9,cgs=2e-9,tol=-.05,c6_factor=.95,r_corner='fast'))
 for corner in [False,True]:
  cases.append(dict(id=f'off_{int(corner)}',input='17',enable='PWL(0 2.7 50u 2.7 50.001u 0)',end=.0003,step=.1e-6,off_at=50e-6,measure_start=50e-6,iload=1.5,q2c=20e-9 if corner else 10e-9,vt=3 if corner else 1,bf=30 if corner else 50,storage=3e-6 if corner else 1e-6,tol=-.05 if corner else 0,r_corner='slow' if corner else None))
 cases.append(dict(id='off_step_18_48',input='PWL(0 18 10u 18 11u 48)',enable='0',end=.0002,step=.05e-6,cgd=2e-9,cgs=2e-9,tol=.05,vt=.8))
 cases.append(dict(id='off_precharged_18_48',input='PWL(0 18 10u 18 11u 48)',enable='0',precharge=17,end=.0002,step=.05e-6,cgd=2e-9,cgs=2e-9,tol=.05,vt=.8))
 cases.append(dict(id='hot_bounce_24',input='PWL(0 0 10u 0 11u 24 30u 24 31u 0 40u 0 41u 24 60u 24 61u 0 80u 0 81u 24)',enable='0',end=.0002,step=.05e-6,cgd=2e-9,cgs=2e-9,tol=.05,vt=.8))
 cases.append(dict(id='ovp_17_24_delay20us',input='PWL(0 17 50u 17 51u 24)',enable='PWL(0 2.7 70.3u 2.7 70.301u 0)',end=.0003,step=.05e-6,off_at=50.2143e-6,measure_start=50e-6,iload=1.5,vt=3,q2c=20e-9,bf=30,storage=3e-6,tol=-.05,r_corner='slow'))
 out=[run_case(sim,xml,c) for c in cases]
 # Known-bad R1 circuit: identical stimulus, separate frozen exported XML.
 legacy=run_case(sim,P/'reference/R1-P01.xml',dict(id='regression_R1_hot24',input='PWL(0 0 10u 0 11u 24)',enable='0',end=.0002,step=.05e-6,vt=1))
 checks=[]
 for row in out:
  name=row['id']
  if name.startswith(('hot','off_step','off_precharged')):
   checks.append({'id':name,'pass':row['peak_VSG_V']<=.8 and row['positive_channel_charge_uC']<=10,'criterion':'VSG<=0.8 V; forward channel charge<=10 uC'})
  if name.startswith('start'):
   checks.append({'id':name,'pass':row['peak_channel_A']<=5 and row['final_VSG_V']>=4.5 and row['start_to_95pct_ms'] is not None and row['start_to_95pct_ms']<300,'criterion':'peak<=5 A; final VSG>=4.5 V; VPROT95% within300ms after ENABLE'})
  if name in ['off_0','off_1']:
   checks.append({'id':name,'pass':row['off_to_0p5_us'] is not None and row['off_to_0p5_us']<=80,'criterion':'gate block <=80us (20us reserved upstream)'})
  if name.startswith('ovp'):
   checks.append({'id':name,'pass':row['off_to_0p5_us'] is not None and row['off_to_0p5_us']<=100,'criterion':'from source18.5V including imposed20us delay <=100us'})
 checks.append({'id':'known_R1_fault_detected','pass':legacy['peak_VSG_V']>1 and legacy['positive_channel_charge_uC']>10,'criterion':'old R1 fails hotplug screening'})
 convergence=[]
 for name in ['hot_48_1e-06_1','off_1','start_fast_corner']:
  old=next(x for x in out if x['id']==name);case=dict(old['case']);case['id']+='_halfstep';case['step']/=2
  new=run_case(sim,xml,case,save=False)
  keys=['peak_VSG_V','peak_channel_A']+(['off_to_0p5_us'] if name=='off_1' else [])
  diffs={k:abs(new[k]-old[k])/max(abs(old[k]),1e-3) for k in keys}
  convergence.append({'id':name,'relative_differences':diffs})
  checks.append({'id':name+'_time_step_convergence','pass':max(diffs.values())<.03,'criterion':'halved time step changes selected metrics <3%'})
 print(json.dumps([{k:v for k,v in row.items() if k not in ['case','samples']} for row in out],indent=2))
 (P/'verification/dynamics.json').write_text(json.dumps({'scope':'Gate-block SPICE sensitivity screening; generic transistor models; not hardware proof','xml_sha256':hashlib.sha256(xml.read_bytes()).hexdigest(),'results':out,'R1_regression':legacy,'convergence':convergence,'checks':checks,'pass':all(x['pass'] for x in checks)},indent=2),encoding='utf-8')
 assert all(x['pass'] for x in checks),[x for x in checks if not x['pass']]
if __name__=='__main__':main()
