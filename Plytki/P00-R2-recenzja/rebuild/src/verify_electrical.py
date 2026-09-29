"""Check operating constraints against native netlist and BOM, not parts.py.

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
    return {'checks':checks,'passed':sum(c['pass'] for c in checks),'total':len(checks),'calculations':calc,'hardware_verified':False,
            'limits':'C6 ESR bound is at 20C/100kHz. Thermal result is an estimate using the explicitly assumed IG. See bench test sheet.'}

def main():
    data=load(); result=evaluate(*data)
    (P/'verification/electrical-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    scenarios=[]
    for case,target in [('five_volt_claim','Declared J10'),('preload_open','Preload physically'),('preload_100k','Preload alone'),('invalid_C6','C6 is the confirmed'),('C6_return_bypass','C6 return'),('R6_zero','Series resistance')]:
        v,m,p,r,b=copy.deepcopy(data)
        if case=='five_volt_claim':r['input_J10_min_V']=5
        elif case=='preload_open':p['R5.2']='NC'
        elif case=='preload_100k':v['R5']='100K / 1%'
        elif case=='invalid_C6':m['C6']='EEUFR1C220'
        elif case=='C6_return_bypass':p['C6.2']='GND'
        elif case=='R6_zero':v['R6']='0R / 1%'
        bad=evaluate(v,m,p,r,b)
        failed=[c['check'] for c in bad['checks'] if not c['pass']]
        scenarios.append({'case':case,'expected_check':target,'detected':any(c.startswith(target) for c in failed),'failed_checks':failed})
    (P/'verification/electrical-negative-controls.json').write_text(json.dumps(scenarios,indent=2)+'\n')
    print('Electrical',result['passed'],'/',result['total'],'| mutations',sum(c['detected'] for c in scenarios),'/',len(scenarios))
    for c in result['checks']:
        if not c['pass']:print('FAIL',c['check'])
    return 0 if result['passed']==result['total'] and all(c['detected'] for c in scenarios) else 1

if __name__=='__main__':sys.exit(main())
