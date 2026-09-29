"""Static netlist/DC audit. No transistor SPICE model and no hardware validation."""
from pathlib import Path
import csv,json,random,copy,math
ROOT=Path(__file__).resolve().parents[1]
C=json.loads((ROOT/'hardware/components.json').read_text(encoding='utf-8'))
rows=list(csv.DictReader((ROOT/'hardware/netlist.csv').open(encoding='utf-8-sig'),delimiter=';'))
P={(r['Element'],r['Pin']):r['Siec'] for r in rows}
checks=[]
def check(name,condition):
    checks.append({'check':name,'pass':bool(condition)})
    if not condition:raise AssertionError(name)
def n(ref,p):return P[ref,str(p)]
check('Every JSON terminal represented exactly once in CSV',len(P)==len(rows)==sum(len(c['pins']) for c in C.values()) and all(P[k,p]==v for k,c in C.items() for p,v in c['pins'].items()))
check('Main MOSFET orientation G,D,S', [n('Q1',p) for p in [1,2,3]]==['GATE','VPROT','VS'])
check('Schottky common cathode; both anodes upstream', [n('D2',p) for p in [1,2,3]]==['BAT_FUSED','VS','BAT_FUSED'])
check('Correct logic-level MOSFET, not an unqualified substitute',C['Q1']['value']=='SUP53P06-20-E3')
check('OVP polarity physically connected', [n('U2',p) for p in [2,3]]==['OV_SENSE','OV_REF'])
check('UVLO polarity physically connected',[n('U2',p) for p in [5,6]]==['UV_SENSE','REF'])
check('Both open collectors, supervisor and inhibit share OK',n('U2',1)==n('U2',7)==n('U4',1)==n('J3',1)=='OK')
check('Auxiliary regulator upstream of main MOSFET',n('R1',1)=='VS' and n('R1',2)==n('U1',3)=='AUX_IN')
check('LM2936 TO92 OUT-GND-IN pinout',[n('U1',p) for p in [1,2,3]]==['AUX5','GND','AUX_IN'])
check('TL431 cathode and REF tied, anode grounded',[n('U3',p) for p in [1,2,3]]==['REF','GND','REF'])
check('TVS and VGS clamp orientations',n('D3','K')=='VPROT' and n('D3','A')=='GND' and n('D4','K')=='VS' and n('D4','A')=='GATE')
check('Sense path blocks reversed battery',n('D6','A')=='BAT_FUSED' and n('D6','K')=='SENSE_RAW')
check('Trim wiper strapped to end',[n('RV1',p) for p in [1,2,3]]==['OV_TRIM_TOP','OV_TRIM_TOP','OV_SENSE'])
check('Default OFF pullup has no dependency on AUX5',[n('Q2',p) for p in [1,2,3]]==['VS','OFF_BASE','OFF_COL'] and n('R23',1)=='OFF_BASE' and n('R23',2)=='GND' and n('R27',1)=='OFF_COL' and n('R27',2)=='GATE')
check('Only Q3 provides intentional gate pull-down',[n('Q3',p) for p in [1,2,3]]==['GND','ON_BASE','ON_COL'] and n('R21',1)=='GATE' and n('R21',2)=='ON_COL')
check('C9 regulator ESR is present',n('R2',1)=='AUX5' and n('R2',2)==n('C9',1) and C['R2']['rating']==1)
check('No capacitor directly on TL431 cathode',not any(c['kind']=='C' and 'REF' in c['pins'].values() for c in C.values()))
check('Fault signal is an open collector',[n('Q7',p) for p in [1,2,3]]==['GND','FAULT_BASE','FAULT_OC'] and not any(c['kind']=='R' and 'FAULT_OC' in c['pins'].values() for c in C.values()))
check('Fault pullup powered from receiving board, not AUX',[n('R30',p) for p in [1,2]]==['BOARD_3V3','FAULT_BASE'])
check('Loss of ENABLE releases fault transistor drive',[n('Q8',p) for p in [1,2,3]]==['GND','FAULT_RELEASE_BASE','FAULT_BASE'] and n('R32',1)=='ENABLE')

def solve(a,b):
    a=[x[:]+[y] for x,y in zip(a,b)];s=len(b)
    for j in range(s):
        k=max(range(j,s),key=lambda k:abs(a[k][j]));a[k],a[j]=a[j],a[k]
        z=a[j][j];assert abs(z)>1e-20
        a[j]=[v/z for v in a[j]]
        for k in range(s):
            if k!=j:
                z=a[k][j];a[k]=[v-z*w for v,w in zip(a[k],a[j])]
    return [r[-1] for r in a]

RR=[f'R{i}' for i in [5,6,7,8,9,10,11,13]]
def nodes(vin,high,trim=2000,vref=2.495,vdd=5.0,vf=.6,vol=.2,load=80e-6,ib=25e-9,scale=None):
    fixed={'GND':0,'AUX5':vdd,'REF':vref,'SENSE_RAW':vin-vf}
    if not high:fixed['OK']=vol
    resistors=[(n(ref,1),n(ref,2),C[ref]['rating']*(scale or {}).get(ref,1)) for ref in RR]
    resistors.append((n('RV1',1),n('RV1',3),max(trim,1e-6)))
    unknown=sorted({x for a,b,r in resistors for x in [a,b]}-fixed.keys());idx={v:i for i,v in enumerate(unknown)}
    a=[[0.0]*len(idx) for _ in idx];b=[0.0]*len(idx)
    for p,q,r in resistors:
        for u,v in [(p,q),(q,p)]:
            if u not in idx:continue
            i=idx[u];a[i][i]+=1/r
            if v in idx:a[i][idx[v]]-=1/r
            else:b[i]+=fixed[v]/r
    for u in ['OV_SENSE','OV_REF','UV_SENSE']:
        if u in idx:b[idx[u]]+=ib # PNP input sources current out of pin
    if high:b[idx['OK']]-=load
    return fixed|dict(zip(unknown,solve(a,b)))
def error(vin,high,channel,vos=0,**kwargs):
    v=nodes(vin,high,**kwargs)
    pp,pm=(3,2) if channel=='ov' else (5,6)
    return v[n('U2',pp)]-v[n('U2',pm)]+vos
def threshold(high,channel,**kw):
    # Resistor network is affine in VIN; solve the comparator zero exactly.
    f0=error(0,high,channel,**kw);f40=error(40,high,channel,**kw)
    return -40*f0/(f40-f0)
lo,hi=0,5000
for _ in range(35):
    mid=(lo+hi)/2
    if threshold(True,'ov',trim=mid)<18:lo=mid
    else:hi=mid
TRIM=(lo+hi)/2
nom={k:threshold(h,c,trim=TRIM) for k,h,c in [('ov_off',True,'ov'),('ov_return',False,'ov'),('uv_start',False,'uv'),('uv_off',True,'uv')]}
check('OVP calibratable with supplied trim',0<TRIM<5000 and abs(nom['ov_off']-18)<1e-7)
check('Nominal hysteresis windows make physical sense',16<nom['ov_return']<17 and 9<nom['uv_off']<9.8 and 9.7<nom['uv_start']<10.3)
for vin,expected in [(8,False),(12,True),(14.4,True),(19,False),(24,False)]:
    for start in [False,True]:
        state=start
        for _ in range(4):state=error(vin,state,'ov',trim=TRIM)>0 and error(vin,state,'uv',trim=TRIM)>0
        check(f'Physical comparator network at {vin} V, previous state {start}',state==expected)

# Negative control: the check must notice a swapped OVP input in the netlist.
saved=P['U2','2'],P['U2','3'];P['U2','2'],P['U2','3']=saved[::-1]
check('Mutation control detects inverted OVP',error(24,True,'ov',trim=TRIM)>0)
P['U2','2'],P['U2','3']=saved

# Sensitivity envelope, NOT a certified worst-case guarantee. Diode VF and buffer
# load are assumed bounded application values, not guaranteed datasheet minima.
rng=random.Random(20260922);samples=[]
for _ in range(5000):
    kw=dict(trim=TRIM*rng.uniform(.995,1.005),vref=rng.uniform(2.4655,2.5245),vdd=rng.uniform(4.85,5.15),vf=rng.uniform(.4,.85),vol=rng.uniform(.1,.7),load=rng.uniform(20e-6,150e-6),ib=rng.uniform(0,500e-9),scale={r:rng.uniform(.99,1.01) if r=='R13' else rng.uniform(.999,1.001) for r in RR})
    ovos=rng.uniform(-.015,.015);uvos=rng.uniform(-.015,.015)
    samples.append([threshold(True,'ov',vos=ovos,**kw),threshold(False,'ov',vos=ovos,**kw),threshold(False,'uv',vos=uvos,**kw),threshold(True,'uv',vos=uvos,**kw)])
envelope={k:[min(x[i] for x in samples),max(x[i] for x in samples)] for i,k in enumerate(nom)}
check('Sampled hysteresis never collapses',all(s[0]>s[1] and s[2]>s[3] for s in samples))
check('Reference bias margin', (4.85-2.5245)/(820*1.01)-2.5245/10000-.03e-3>1e-3)
check('Supervisor and comparator sink budget',5.15/(2200*.99)+.1e-3<4e-3)
gate_min=(8.9-.95-.3)*100000/(100000+4700)
check('MOSFET drive margin at conservative low input',gate_min>4.5)
check('TVS residual voltage leaves MOSFET margin',48<60)
check('Secondary TVS clamp below regulator input rating at 25 C',29.2<36 and 25.2<40)
loss=[]
for current in [1,3.5,5]:
    pd=2*(.55*(current/2)+.015*(current/2)**2)
    pq=current**2*.025*2
    loss.append({'A':current,'diode_estimate_W':pd,'mosfet_hot_budget_W':pq,'sum_W':pd+pq,'drop_V':(pd+pq)/current})
result=dict(status='STATIC_CHECKS_PASS_HARDWARE_UNTESTED',checks=checks,component_count=len(C),terminal_count=len(P),nominal_thresholds_V=nom,trim_ohm=TRIM,sensitivity_envelope_5000_samples_V=envelope,sensitivity_note='Not guaranteed limits; assumes VF=0.4..0.85 V and buffer load 20..150 uA; calibrated trim held fixed; no transistor dynamic model.',loss_budget=loss,hardware_measurements=None,spice_simulation=False,iso_qualification=False)
(ROOT/'verification/report.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({'checks':len(checks),'thresholds':nom,'trim':TRIM,'envelope':envelope,'loss':loss},indent=2))
