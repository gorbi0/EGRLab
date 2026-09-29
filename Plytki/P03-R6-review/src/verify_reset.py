"""Reset interface budget from exported own netlist and frozen peer part map (R6: SUP_N_OUT on J_BP3.12 + P12 path estimate).
Datasheet limits are independent requirements, not copied generator values.
"""
from pathlib import Path
import json, re, copy, xml.etree.ElementTree as ET
P=Path(__file__).resolve().parents[1];ID='P03' if P.name.startswith('P03') else 'P04'
def netparts(root):
    parts={c.get('ref'):{'value':c.findtext('value'),'pins':{}} for c in root.findall('./components/comp')}
    for net in root.findall('./nets/net'):
        for n in net.findall('node'):parts[n.get('ref')]['pins'][n.get('pin')]=net.get('name').split('/')[-1]
    return parts
def ohm(parts,ref):
    v=parts[ref]['value'].split()[0].upper();m=re.fullmatch(r'(\d+(?:\.\d+)?)([RK]?)',v)
    assert m,(ref,v)
    return float(m[1])*(1000 if m[2]=='K' else 1)
def evaluate(a,b):
    r13,r34,r35,r41=(ohm(a,r) for r in ['R13','R34','R35','R41']);r17=ohm(b,'R17')
    # 1% board resistors; Waveshare EN pull-up assumed 10k +/-5%, verify actual module.
    rp_min=1/(1/(r35*.99)+1/9500)
    low=(.4*rp_min+3.0*r34*1.01)/(rp_min+r34*1.01)
    leakage_low=30e-6*r17*1.01  # |Ioff| U6=10u + |II| U9=20u; conservative sum to 125C
    high=2.4*(r17*.99)/(r17*.99+r41*1.01)-20e-6*(r17*.99*r41*1.01)/(r17*.99+r41*1.01)
    rows=[]
    def ck(name,ok,detail):rows.append({'check':name,'pass':bool(ok),'detail':detail})
    ck('U4 Schmitt input and open drain, exact pinout',a['U4']['value']=='SN74LVC1G37DBVR' and all(a['U4']['pins'].get(k)==v for k,v in {'2':'SUP_RAW_N','3':'GND','4':'RESET_DRV_N','5':'3V3_CORE'}.items()),a['U4'])
    ck('TPS3808 pull-up nominal >=10k and connected correctly',r13>=10000 and set(a['R13']['pins'].values())=={'SUP_RAW_N','3V3_CORE'},r13)
    ck('R34 discharge peak <=16mA',3.465/(r34*.99)<=.016,3.465/(r34*.99))
    ck('SUP_N low at 3.0V below MCP VIL=0.6V',low<.6,{'worst_estimate_V':low,'U4_VOL_V':.4,'EN_pullup_assumption_ohm':[9500,10500]})
    ck('P04 R17 default low from worst-case leakage below 0.8V',leakage_low<.8 and set(b['R17']['pins'].values())=={'SUP_N','GND'},{'voltage_V':leakage_low,'sum_uA':30,'direction':'conservative absolute sum, not measured current'})
    ck('P04 active input high above 2.0V',high>2 and 2.4/(r17*.99+r41*.99)<.016,{'lower_bound_V':high,'U6_VOH_min_V':2.4,'U9_input_uA':20})
    ck('U6 output and P04 receiver retain reviewed topology',a['U6']['value']=='SN74LVC1G17DBVR' and a['U6']['pins'].get('4')=='SUP_N_DRV' and set(a['R41']['pins'].values())=={'SUP_N_DRV','SUP_N_OUT'} and a['J_BP3']['pins'].get('12')=='SUP_N_OUT' and b['J2']['pins'].get('15')=='SUP_N' and b['U9']['pins'].get('5')=='SUP_N',{'P03_J_BP3_12':'SUP_N_OUT','P04_J2_15 (P04-R2.2, frozen; S1 revision of P04 pending)':'SUP_N'})
    return rows
root=ET.parse(P/'verification'/(ID+'.xml')).getroot()
own=netparts(root);peer=json.loads((P/'reference/reset-peer-parts.json').read_text(encoding='utf-8'))
a,b=(own,peer) if ID=='P03' else (peer,own)
rows=evaluate(a,b)
mutations=[]
for ref,value,expected in [('U4','SN74LVC1G07DBVR','U4 Schmitt'),('R13','1K / 1%','TPS3808'),('R34','0R / 1%','R34'),('R17','100K / 1%','P04 R17')]:
    ma,mb=copy.deepcopy(a),copy.deepcopy(b)
    if ref=='R34':value='10R / 1%' # finite but unsafe limiter, exercises current calculation
    (mb if ref=='R17' else ma)[ref]['value']=value
    failed=[r['check'] for r in evaluate(ma,mb) if not r['pass']]
    mutations.append({'mutation':ref+'='+value,'detected':any(s.startswith(expected) for s in failed),'failures':failed})
# R6: edge-rate ESTIMATE on the new path (task §4). Same ideal-RC model as R4 (docs/ZASILANIE-RESET.md): slowest point of the
# 0.8-2.0 V window is 0.8 V from the final value on both edges, so ns/V = R41 * C / 0.8 V. Not a guarantee; ODBIOR measures it.
PATH={'ribbon P03-P12 30 mm':30*0.1,'ribbon P12-P04 30 mm':30*0.1,'P12 trace (assumed <= 120 mm, 0.1 pF/mm over GND)':120*0.1,
      '4 IDC contacts x 1 pF':4.0,'P04 74LVC125A input':5.0,'local traces P03+P04':3.0}
c_pf=sum(PATH.values());r41=ohm(a,'R41');nsv=r41*c_pf*1e-12/0.8*1e9;c_max=10e-9*0.8/r41*1e12
R5_REF={'ribbon H_SAFE 150 mm incl. input and traces (R4 estimate)':20.0}
slew={'model':'ideal RC, ns/V = R41*C/0.8 V','R41_ohm':r41,'C_components_pF':PATH,'C_total_pF':round(c_pf,1),'estimate_ns_per_V':round(nsv,2),
      'limit_ns_per_V':10,'C_for_limit_pF':round(c_max,1),'R5_reference':{'C_pF':20.0,'ns_per_V':round(r41*20e-12/0.8*1e9,2)},
      'P12_requirement':'SUP_N_OUT trace on P12 <= 120 mm over continuous GND, no stubs; total load <= 30 pF',
      'status':'ESTIMATE - measure both edges at P04 U9.5 (ODBIOR)'}
rows.append({'check':'R6 path estimate within the 10 ns/V limit (estimate, not a guarantee)','pass':nsv<10,'detail':slew})
out={'checks':rows,'negative_controls':mutations,'hardware_tested':False,'slew_estimate_R6':slew,
     'scope':'DC limits, exact parts and pin maps; output slew, power ramps and B2B fit require bench/physical checks.'}
(P/'verification/reset-budget.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
for r in rows:print('PASS' if r['pass'] else 'FAIL',r['check'],r['detail'] if not r['pass'] else '')
assert all(r['pass'] for r in rows) and all(m['detected'] for m in mutations)
print('Reset budget:',len(rows),'checks;',len(mutations),'mutations detected')
