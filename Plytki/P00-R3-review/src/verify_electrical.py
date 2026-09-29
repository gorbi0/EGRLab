"""Check operating constraints against native netlist and BOM, not parts.py (P00 R3: + worst-case load vs budget, heartbeat level).

This is static arithmetic, not a simulation or a substitute for bench acceptance.
"""
from pathlib import Path
import copy, csv, json, re, sys, xml.etree.ElementTree as ET

P=Path(__file__).resolve().parents[1]

def numeric(value):
    token=value.split('/')[0].strip().upper().replace('OHM','').strip()
    m=re.fullmatch(r'(\d+)([RKMG]?)(\d*)',token)
    if not m: raise ValueError(value)
    return float(m[1]+('.'+m[3] if m[3] else ''))*{'':1,'R':1,'K':1e3,'M':1e6,'G':1e9}[m[2]]

def load():
    root=ET.parse(P/'verification/P00.xml').getroot()
    values={c.get('ref'):c.findtext('value') for c in root.findall('./components/comp')}
    mpns={c.get('ref'):next((f.text for f in c.findall('./fields/field') if f.get('name')=='MPN'),'') for c in root.findall('./components/comp')}
    pins={n.get('ref')+'.'+n.get('pin'):net.get('name').lstrip('/') for net in root.findall('./nets/net') for n in net.findall('node')}
    with (P/'docs/BOM.csv').open(encoding='utf-8-sig',newline='') as f: bom=list(csv.DictReader(f,delimiter=';'))
    return values,mpns,pins,json.loads((P/'requirements/electrical.json').read_text()),bom

def evaluate(values,mpns,pins,req,bom):
    checks=[];calc={}
    def check(name,ok): checks.append({'check':name,'pass':bool(ok)})
    dt=max(abs(req['ambient_min_C']-25),abs(req['ambient_max_C']-25))
    rmax=(1+req['resistor_tolerance'])*(1+dt*req['resistor_TCR_per_C'])
    rmin=(1-req['resistor_tolerance'])*(1-dt*req['resistor_TCR_per_C'])
    check('Declared J10 range keeps U2 above 4.75 V after D1 budget',req['input_J10_min_V']-req['D1_design_drop_budget_V']>=4.75 and req['U2_min_VIN_V']==4.75)
    check('Correct regulator variant in exported netlist',mpns.get('U2')=='LM2937ET-3.3/NOPB')
    check('Preload physically connects V33 to GND in exported netlist',pins.get('R5.1')=='P00_V33' and pins.get('R5.2')=='GND')
    rp=numeric(values['R5']); imin=req['V33_min_V']/(rp*rmax); pmax=req['V33_max_V']**2/(rp*rmin)
    calc.update(R5_min_mA=imin*1000,R5_max_mW=pmax*1000,VIN_at_U2_budget_min_V=req['input_J10_min_V']-req['D1_design_drop_budget_V'])
    check('Preload alone meets 5 mA including tolerance and TCR',imin>=0.005 and req['U2_min_IOUT_A']==0.005)
    check('Preload dissipation below one quarter of resistor rating',pmax<=req['R5_rating_W']/4)
    check('C6 is the confirmed Panasonic 22uF 50V D5 P2 part',mpns.get('C6')=='EEUFR1H220' and values.get('C6')=='22u / 50V')
    check('COUT capacitance includes minus 20 percent tolerance',22e-6*(1-req['C6_cap_tolerance'])>=req['COUT_min_F'])
    check('C6 return is connected only to R6, and R6 to GND',sorted(k for k,v in pins.items() if v=='P00_COUT_RET')==['C6.2','R6.1'] and pins.get('R6.2')=='GND' and pins.get('C6.1')=='P00_V33')
    r6=numeric(values['R6']); esrmin=r6*rmin; esrmax=r6*rmax+req['C6_Z_at_20C_100kHz_max_ohm']
    calc.update(C6_branch_min_ohm=esrmin,C6_branch_at_20C_100kHz_max_ohm=esrmax)
    check('Series resistance places C6 branch inside 0.01..3 ohm at reference conditions',0.01<=esrmin and esrmax<=3)
    # BOM column names are checked explicitly; no silent fallback to another table.
    check('BOM matches netlist MPN values and has no invalid C6 code',all(row['mpn']==mpns[row['ref']] for row in bom) and all('EEUFR1C220' not in str(row) for row in bom))
    ra,rb=numeric(values['R1']),numeric(values['R2'])
    calc.update(heartbeat_nominal_Hz=1.44/((ra+2*rb)*100e-9),H_static_into_10k_V=3.3*10000/(1000+10000),H_static_into_5k_V=3.3*5000/6000,
        ground_short_max_mA=req['V33_max_V']/(1000*rmin)*1000)
    pd=(req['input_J10_max_V']-req['V33_min_V'])*req['thermal_design_IOUT_A']+req['input_J10_max_V']*req['thermal_assumed_IG_A']
    calc.update(U2_dissipation_budget_W=pd,U2_junction_estimate_C=req['ambient_max_C']+pd*req['theta_JA_reference_K_per_W'])
    check('Thermal budget estimate below 125C; physical test still required',calc['U2_junction_estimate_C']<125)
    # R3 (review P0-03): the budget must cover the worst load that follows from the netlist values.
    vmax,vfmin=req['V33_max_V'],req['LED_VF_min_V']
    topo={'RL10.1':'P00_V33','R4.1':'P00_V33','RL9.1':'P00_OSC','R3.1':'P00_OSC','R3.2':'P00_HEART','R5.1':'P00_V33',
          **{f'RS{i}.1':f'P00_S{i}' for i in range(1,9)},**{f'RS{i}.2':f'P00_OUT{i}' for i in range(1,9)},**{f'RL{i}.1':f'P00_S{i}' for i in range(1,9)}}
    check('Load topology assumed by the worst-case sum matches the netlist',all(pins.get(k)==v for k,v in topo.items()))
    def led(r):return (vmax-vfmin)/(numeric(values[r])*rmin)
    worst={'R5':vmax/(numeric(values['R5'])*rmin),'LED10':led('RL10'),'LED1..8':sum(led(f'RL{i}') for i in range(1,9)),
           'J1..J8 shorted to GND':sum(vmax/(numeric(values[f'RS{i}'])*rmin) for i in range(1,9)),'U1 IDD':req['TLC555_IDD_max_A'],
           'U1 output H: LED9 + J9 shorted':led('RL9')+vmax/(numeric(values['R3'])*rmin),'R4 (STOP)':vmax/(numeric(values['R4'])*rmin)}
    calc.update(IOUT_worst_mA=sum(worst.values())*1000,IOUT_worst_parts_mA={k:round(v*1000,3) for k,v in worst.items()})
    check('Thermal budget IOUT covers the worst-case load computed from the netlist',req['thermal_design_IOUT_A']>=sum(worst.values()))
    # R3 (review P0-04): heartbeat H at the P04 input (10 k pulldown); TLC555 output modelled as VDD - Ro * I.
    def hb(vdd,ro):
        rl9,r3,rpd=numeric(values['RL9']),numeric(values['R3']),req['P04_input_pulldown_ohm']
        vout=(vdd+ro*vfmin/rl9)/(1+ro/rl9+ro/(r3+rpd));return vout*rpd/(r3+rpd)
    typ=min(hb(req['V33_min_V'],ro) for ro in req['TLC555_Ro_typ_ohm'])
    corner=min(hb(req['V33_min_V'],ro) for ro in req['TLC555_Ro_min_VOH_ohm'])
    calc.update(HB_H_at_P04_typ_min_V=typ,HB_H_at_P04_min_VOH_corner_V=corner,P04_LVC_VIH_V=req['P04_LVC_VIH_V'])
    check('Heartbeat H at the P04 input >= 2.4 V with a typical TLC555 output (min-VOH corner reported; ODBIOR decides)',typ>=req['HB_H_target_V'])
    return {'checks':checks,'passed':sum(c['pass'] for c in checks),'total':len(checks),'calculations':calc,'hardware_verified':False,
            'limits':'C6 ESR bound is at 20C/100kHz. Thermal result is an estimate using the explicitly assumed IG. See bench test sheet.'}

def main():
    data=load(); result=evaluate(*data)
    (P/'verification/electrical-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    scenarios=[]
    for case,target in [('five_volt_claim','Declared J10'),('preload_open','Preload physically'),('preload_100k','Preload alone'),('invalid_C6','C6 is the confirmed'),('C6_return_bypass','C6 return'),('R6_zero','Series resistance'),
                        ('preload_220R','Thermal budget IOUT covers'),('RL9_220R','Heartbeat H at the P04 input'),('RL9_moved_after_R3','Load topology')]:
        v,m,p,r,b=copy.deepcopy(data)
        if case=='five_volt_claim':r['input_J10_min_V']=5
        elif case=='preload_open':p['R5.2']='NC'
        elif case=='preload_100k':v['R5']='100K / 1%'
        elif case=='invalid_C6':m['C6']='EEUFR1C220'
        elif case=='C6_return_bypass':p['C6.2']='GND'
        elif case=='R6_zero':v['R6']='0R / 1%'
        elif case=='preload_220R':v['R5']='220R / 1%'
        elif case=='RL9_220R':v['RL9']='220R / 1%'
        elif case=='RL9_moved_after_R3':p['RL9.1']='P00_HEART'
        bad=evaluate(v,m,p,r,b)
        failed=[c['check'] for c in bad['checks'] if not c['pass']]
        scenarios.append({'case':case,'expected_check':target,'detected':any(c.startswith(target) for c in failed),'failed_checks':failed})
    (P/'verification/electrical-negative-controls.json').write_text(json.dumps(scenarios,indent=2)+'\n')
    print('Electrical',result['passed'],'/',result['total'],'| mutations',sum(c['detected'] for c in scenarios),'/',len(scenarios))
    for c in result['checks']:
        if not c['pass']:print('FAIL',c['check'])
    return 0 if result['passed']==result['total'] and all(c['detected'] for c in scenarios) else 1

if __name__=='__main__':sys.exit(main())
