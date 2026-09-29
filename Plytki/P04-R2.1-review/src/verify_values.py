"""R2.1 independent numeric/MPN and mating-netlist audit; no parts.py import.

Timing calculations are sizing estimates, not device guarantees at 3.3 V.
Inputs are the exported KiCad XML, BOM and XML snapshots of adjacent boards.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import json, csv, copy, itertools, hashlib
P = Path(__file__).resolve().parents[1]

def load(path):
    root = ET.parse(path).getroot()
    cs = {c.get('ref'): {'value': c.findtext('value'), 'mpn': next((f.text for f in c.findall('./fields/field') if f.get('name') == 'MPN'), '')} for c in root.findall('./components/comp')}
    ps = {(q.get('ref'), int(q.get('pin'))): n.get('name').split('/')[-1] for n in root.findall('./nets/net') for q in n.findall('node') if q.get('pin').isdigit()}
    return cs, ps

def checks(cs):
    out = []
    def ck(name, ok, detail=None): out.append({'name':name,'pass':bool(ok),'detail':detail})
    def match(spec): return all(cs.get(r,{}).get('value')==v and cs[r]['mpn']==m for r,(v,m) in spec.items())
    def res(spec): return {r:(v,'MFR-25FRF52-'+v) for r,v in spec.items()}
    ck('Watchdog RC and film dielectric', match(dict(res({'R1':'220K'}), C1=('1u','MKS2C041001F00KSSD'))))
    ck('ARM RC and film dielectric', match(dict(res({'R2':'10K','R3':'1K'}), C2=('1u','MKS2C041001F00KSSD'))))
    ck('SAFE divider and C0G filter', match(dict(res({'R4':'10K','R5':'100K'}), C18=('1n','K102J15C0GF53H5'))))
    ck('Sink base resistors', match(res({**{f'R{i}':'10K' for i in (6,7,8)},**{f'R{i}':'100K' for i in (9,10,11)}})))
    spec={f'R{i}':'10K' for i in range(12,37)}
    spec.update(R17='100K',R26='47K',R27='47K',R28='100K',R30='100K')
    ck('Every receiver bias including SUP_N', match(res(spec)))
    ck('Panel/PG limiting resistors and LED', match(res({**{f'R{i}':'1K' for i in (37,38,39,41,42)},'R40':'100R'})))
    ck('Decoupling values and MPN', match({'C3':('10u','EEUFR1H100'),**{f'C{i}':('100n','K104K15X7RF53H5') for i in range(4,18)}}))
    ck('Exact supervisor variant', match({'U11':('MCP100-300DI/TO','MCP100-300DI/TO')}))
    return out

def main():
    cs,ps=load(P/'verification/P04.xml')
    out=checks(cs); negative=[]
    mutations=[('R1','22K'),('C1','100n'),('R2','100K'),('R3','100R'),('C2','100n'),('R4','100K'),('R5','10K'),('C18','100n'),('R6','100K'),('R9','1K'),('R17','10K'),('R25','100K'),('R26','470K'),('R28','10K'),('R30','10K'),('R38','0R'),('R39','0R'),('R40','1K'),('R41','10K'),('R42','10K'),('C4','1n'),('C15','1n'),('U11','MCP100-315DI/TO')]
    for r,v in mutations:
        m=copy.deepcopy(cs);m[r]['value']=v
        failed=[c['name'] for c in checks(m) if not c['pass']]
        negative.append({'mutation':f'{r} value -> {v}','detected':bool(failed),'failed_checks':failed})
    m=copy.deepcopy(cs);m['C1']['mpn']='unqualified-X7R'
    negative.append({'mutation':'C1 dielectric/MPN changed with same 1u value','detected':not checks(m)[0]['pass']})
    with (P/'docs/BOM.csv').open(encoding='utf-8-sig') as f:
        bom={r['ref']:r for r in csv.DictReader(f,delimiter=';')}
    wrong=[r for r,c in cs.items() if r not in bom or bom[r]['display'].split(' / ')[0]!=c['value'] or bom[r]['mpn']!=c['mpn']]
    out.append({'name':'Exported values and MPN agree with the BOM','pass':not wrong,'detail':wrong})
    # Compare actual counterpart exports; NC is electrically compatible with unused extra outputs.
    comparisons=[]
    maps=[('P03.xml','J4','J2',16),('P02.xml','J12','J6',6),('P05.xml','J3','J5',6),('P01.xml','J5','J7',6)]
    for fn,jother,jhere,count in maps:
        _,other=load(P/'audit'/fn)
        for pin in range(1,count+1):
            a,b=other[jother,pin],ps[jhere,pin]
            nc=lambda n:n.startswith('unconnected-')
            ok=a==b or (nc(a) and nc(b)) or (fn=='P02.xml' and pin==3 and a=='HOLD_READY' and nc(b)) or (fn=='P01.xml' and pin==1 and a=='3V3_IO' and b=='PG_3V3')
            comparisons.append({'source':fn,'pin':pin,'source_net':a,'P04_connector':jhere,'P04_net':b,'pass':ok})
    out.append({'name':'Counterpart pin maps P01/P02/P03/P05','pass':all(r['pass'] for r in comparisons),'detail':comparisons})
    # R40 feeds three parallel branches. Enumerate independent +/-1% resistor corners.
    levels=[]
    for vdd in (3.18,3.465):
        for signs in itertools.product((.99,1.01),repeat=7):
            rs=[r*s for r,s in zip((100,1000,10000,1000,10000,10000,100000),signs)]
            r40,r41,r23,r42,r24,r4,r5=rs
            panel=vdd/(1+r40*(1/(r41+r23)+1/(r42+r24)+1/(r4+r5)))
            levels.append({'panel':panel,'key':panel*r23/(r41+r23),'mech':panel*r24/(r42+r24),'safe':panel*r5/(r4+r5)})
    bounds={k:{'min':min(d[k] for d in levels),'max':max(d[k] for d in levels)} for k in levels[0]}
    pshort=3.465**2/99
    out.append({'name':'Resistor-corner sizing of panel and SAFE (unloaded by other modules)','pass':bounds['safe']['min']>2.7 and min(bounds[k]['min'] for k in ('key','mech'))>2.7 and pshort<.125,'detail':{'voltage_V':bounds,'R40_short_W':pshort,'limitation':'3.18..3.465 V, 1% resistors; no cable resistance/leakage, no HC14 threshold guarantee. Verify E05/I01 on hardware.'}})
    result={'checks':out,'negative_controls':negative,'timing_estimates':{'watchdog_5V_formula_ms':[.45*220000*.99*1e-6*.9*1000,.45*220000*1.01*1e-6*1.1*1000],'watchdog_3V3':'NOT QUALIFIED: accept by E11 50..150 ms','MCP100_release_margin':'At 3.16 V ripple trough and 50 mV TYP hysteresis: 110 mV estimate; no guaranteed max hysteresis in DS11187F.'},'inputs':{s:hashlib.sha256((P/s).read_bytes()).hexdigest() for s in ['verification/P04.xml','docs/BOM.csv']+[f'audit/{m[0]}' for m in maps]}}
    (P/'verification/value-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    bad=[c['name'] for c in out if not c['pass']];miss=[c['mutation'] for c in negative if not c['detected']]
    print('Values/interfaces',len(out)-len(bad),'/',len(out),'negative controls',len(negative)-len(miss),'/',len(negative));assert not bad and not miss,(bad,miss)
if __name__=='__main__':main()
