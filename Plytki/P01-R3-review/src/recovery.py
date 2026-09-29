"""Fault/recovery regression read from actual R3 XML; intentional loss is recorded.
Optional HOLD is an engineering envelope, not a vendor converter model.
"""
from dynamics import P,deck,load
from ngshared import Spice
import numpy as np,json,hashlib,re

XML=P/'verification/P01.xml'
HOLD=json.loads((P/'integration/P02-HOLD/contract.json').read_text())

def pulse(width, repeat=False):
    points=[(0,2.7),(.005,2.7),(.00500001,0),(.005+width,0),(.005+width+1e-8,2.7)]
    if repeat:
        for t in [.025,.045]:points.extend([(t,2.7),(t+1e-8,0),(t+width,0),(t+width+1e-8,2.7)])
    return 'PWL('+ ' '.join(f'{t:.12g} {v}' for t,v in points)+')'

def run(sim, name, vs=14, vt=3, width=50e-6, power=3, hold=False, repeat=False, step=2e-6,cold=False):
    case=dict(input=str(vs),enable='PWL(0 0 1m 0 1.00001m 2.7)' if cold else pulse(width,repeat),end=20 if cold else max(.15,.005+width+.1),step=step,
              vt=vt,bf=30,storage=3e-6,q2c=20e-9,tol=-.05,r_corner='slow',cload=198e-6 if hold else 220e-6)
    d=deck(XML,case)
    # C is total 220 uF directly visible to P01. HOLD branch is separately charged.
    d=re.sub(r'^Bload .*$', 'Bload '+('vlog' if hold else 'vprot')+f' 0 I=(v({"vlog" if hold else "vprot"})>6.5)*{power}/max(v({"vlog" if hold else "vprot"}),6.5)',d,flags=re.M)
    if hold:
        # Worst selected acceptance envelope: C -20%, ESR/diode/wiring loss in each path.
        # D paths modeled explicitly with >=1 V Vf in the operating range.
        # Rcharge and bleeder visible, leakage envelope 9 mA for three capacitors.
        holdlines=f'''
.model DH D(is=1e-16 n=1 rs=.08)
Dfeed vprot vlog DH
Rcharge vprot charge {HOLD['R_charge_ohm']*(1+HOLD['R_charge_tolerance'])}
Dcharge charge hcap DH
Rbleed hcap 0 {HOLD['R_bleed_ohm']}
Bleak hcap 0 I=.009*tanh(v(hcap))
Resr hcap hint .15
Chold hint 0 {HOLD['C_nominal_F']*1.2 if cold else HOLD['C_effective_acceptance_min_F']}
Dhold hcap vlog DH
Cvlog vlog 0 22u
'''
        d=d.replace('.end',holdlines+'\n.end')
    vectors=['time','v(p01_vs)','v(p01_gate)','v(vprot)','v(vlog)' if hold else 'v(vprot)','i(vq1i)']
    if hold:vectors.append('v(hcap)')
    a=sim.run(d,vectors)
    t=a['time'];sg=a['v(p01_vs)']-a['v(p01_gate)'];vp=a['v(vprot)'];bus=a['v(vlog)'] if hold else vp
    off=np.flatnonzero((t>=.005)&(sg<vt));ton=None
    if len(off):
        hit=np.flatnonzero((t>t[off[0]])&(sg>vt+.5));ton=float((t[hit[0]]-t[off[0]])*1000) if len(hit) else None
    after=t>=.005
    out={'id':name,'power_bus_W':power,'VS_V':vs,'Vth_assumption_V':vt,'pulse_us':width*1e6,
         'repeat':repeat,'hold':hold,'Q1_off_ms':ton,'bus_min_V':float(min(bus[after])),
         'bus_below_7V':bool(np.any(bus[after]<7)),
         'final_VPROT_V':float(vp[-1]),'final_VSG_V':float(sg[-1]),'initial_bus_V':float(bus[0]),
         'peak_Q1_channel_A':float(max(a['i(vq1i)'])),
         'initial_hold_V':float(a['v(hcap)'][0]) if hold else None,
         'hold_at_15s_V':float(np.interp(15,t,a['v(hcap)'])) if cold else None,
         'cold_start':cold}
    (P/'simulation/decks'/(name+'.cir')).write_text(d,encoding='ascii')
    idx=np.unique(np.r_[np.arange(0,len(t),max(1,len(t)//2500)),np.argmin(bus),len(t)-1])
    np.savetxt(P/'simulation/results'/(name+'.csv'),np.stack([t,vp,bus,sg,a['i(vq1i)']],1)[idx],delimiter=',',header='t_s,VPROT_V,BUS_V,VSG_V,Q1_channel_A',comments='')
    return out

def main():
    sim=Spice();out=[]
    for vth in [1,2,3]:out.append(run(sim,f'recovery_bare_vt{vth}',vt=vth))
    for width in [10e-6,50e-6,1e-3]:
        out.append(run(sim,f'recovery_hold_{width:g}',width=width,hold=True,vs=11.5,power=6))
    out.append(run(sim,'recovery_burst_bare',repeat=True,vs=11.5,power=6))
    out.append(run(sim,'recovery_burst_hold',repeat=True,hold=True,vs=11.5,power=6))
    # Defined failure outside finite reserve, required negative control.
    out.append(run(sim,'recovery_exhausted_hold',width=.25,hold=True,vs=11.5,power=6))
    out.append(run(sim,'hold_cold_start',hold=True,vs=11.5,power=6,cold=True,step=200e-6))
    checks=[]
    for row in out:
        if row['cold_start']:
            ok=row['initial_hold_V']<.1 and row['hold_at_15s_V']>=9.5 and row['final_VPROT_V']>10 and row['peak_Q1_channel_A']<5
        elif row['id'].startswith('recovery_bare_'):
            # Low Vth can recover before bus collapse. Never claim every part resets.
            ok=row['Q1_off_ms'] is not None and row['Q1_off_ms']>5 and row['final_VPROT_V']>13 and row['final_VSG_V']>=4.5
        elif row['id']=='recovery_exhausted_hold':ok=row['bus_below_7V']
        elif row['hold']:ok=not row['bus_below_7V'] and row['final_VPROT_V']>10
        else:ok=row['bus_below_7V']
        checks.append({'id':row['id'],'pass':bool(ok)})
    checks.append({'id':'unbuffered_power_loss_detected','pass':all(x['bus_below_7V'] for x in out if x['id'] in ['recovery_bare_vt2','recovery_bare_vt3','recovery_burst_bare'])})
    fine=run(sim,'recovery_hold_halfstep',hold=True,vs=11.5,power=6,step=1e-6)
    normal=next(x for x in out if x['id']=='recovery_hold_5e-05')
    checks.append({'id':'recovery_step_convergence','pass':abs(fine['bus_min_V']-normal['bus_min_V'])<.05})
    result={'xml_sha256':hashlib.sha256(XML.read_bytes()).hexdigest(),'contract_sha256':hashlib.sha256((P/'integration/P02-HOLD/contract.json').read_bytes()).hexdigest(),'results':out,'convergence':fine,'checks':checks,'pass':all(x['pass'] for x in checks),
            'scope':'Generic MOS models and constant-power load with assumed cutoff at 6.5V. Recovery uses precharged HOLD; separate cold start uses +20% capacitance and +5% charging resistance. Total direct load capacitance198u+22u=220u for HOLD. No hardware validation.'}
    (P/'verification/recovery.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
    assert result['pass'],checks
if __name__=='__main__':main()
