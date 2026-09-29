"""Cross-check human-facing CSV tables against the exported CAD and parts list (R6: + J_BP.csv, SERWIS.csv for P12).
Run with standard Python, from any directory. The generator is not imported.
"""
from pathlib import Path
import csv, json, re, xml.etree.ElementTree as ET
P=Path(__file__).resolve().parents[1]
def rows(name):
    with (P/'docs'/name).open(encoding='utf-8-sig',newline='') as f:
        r=list(csv.reader(f,delimiter=';'))
    assert all(len(x)==len(r[0]) for x in r), name+' column count'
    return [dict(zip(r[0],x)) for x in r[1:]]
tables={f.name:rows(f.name) for f in (P/'docs').glob('*.csv')}
x=ET.parse(P/'verification/P03.xml').getroot()
pins={(n.get('ref'),n.get('pin')):('NC' if net.get('name').split('/')[-1].startswith('unconnected-') else net.get('name').split('/')[-1])
      for net in x.findall('./nets/net') for n in net.findall('node')}
vals={c.get('ref'):c.findtext('value','') for c in x.findall('./components/comp')}
csvpins={(r['ref'],r['pin']):r['net'] for r in tables['netlist-pinowa.csv']}
assert csvpins==pins, 'CSV pinmap differs from CAD'
jbp=tables['J_BP.csv'];assert list(jbp[0])==['zlacze','pin','siec','kierunek','plytka_docelowa','uwagi']
assert len(jbp)==60 and {(r['zlacze'],r['pin']) for r in jbp}=={(k,p) for k,p in pins if k.startswith('J_BP')}
for r in jbp:
    assert pins[(r['zlacze'],r['pin'])]==r['siec'],r
    assert r['kierunek'] in ('in','out','pwr','gnd') and (r['kierunek']=='gnd')==(r['siec']=='GND'),r
    assert r['plytka_docelowa'],r
sv=tables['SERWIS.csv'];assert list(sv[0])==['zlacze','pin','siec','rezystor','cel_pomiaru']
assert {(r['zlacze'],r['pin']) for r in sv}=={(k,p) for k,p in pins if k.startswith('J_SV')}
for r in sv:
    hp=pins[(r['zlacze'],r['pin'])]
    if r['siec']=='GND':assert hp=='GND' and r['rezystor']=='-',r;continue
    ref,val=r['rezystor'].split(' ',1)
    assert {pins[(ref,'1')],pins[(ref,'2')]}=={r['siec'],hp} and vals[ref]==val,r
parts=json.loads((P/'docs/parts.json').read_text(encoding='utf-8'))
assert len(tables['BOM.csv'])==len(parts)==len(vals)
for r in tables['BOM.csv']:
    assert r['mpn']==parts[r['ref']]['mpn'] and r['footprint']==parts[r['ref']]['footprint'],r
# R6 mounting rule (task §4): owned values THT (resistors vertical), other passives SMD 1206
for ref,p in parts.items():
    if re.fullmatch(r'R\d+',ref):
        v=p['value'].split('/')[0].strip()
        assert ('Vertical' in p['footprint'])==(v in ('10K','4K7')) and ('1206' in p['footprint'])==(v not in ('10K','4K7')),(ref,v,p['footprint'])
purchase_refs=[]
for r in tables['zakupy.csv']:
    refs=[x.strip() for x in r['oznaczenia'].split(',')]
    assert len(refs)==int(r['ilosc_szt']),r
    assert all(parts[ref]['mpn']==r['nazwa'] for ref in refs),r
    purchase_refs+=refs
assert len(set(purchase_refs))==len(purchase_refs)
assert set(purchase_refs)=={r for r in parts if not r.startswith('TP')}
report={'pass':True,'csv_rows':{n:len(r) for n,r in sorted(tables.items())},'cad_pins_checked':len(pins),'purchase_parts_checked':len(purchase_refs)}
(P/'verification/table-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(report)
