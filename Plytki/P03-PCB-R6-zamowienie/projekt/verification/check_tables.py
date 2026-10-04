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
# 1.10 (review): default states - the stated input pin carries the signal and a 10K resistor ties it to the stated rail
st=tables['STANY-DOMYSLNE.csv'];assert list(st[0])==['sygnal','wejscie','rezystor_do','poziom','rezystancja','grupa','znaczenie']
for r in st:
    u,n=r['wejscie'].split('.')
    assert pins[(u,n)]==r['sygnal'],r
    assert any(k.startswith('R') and vals[k].startswith('10K') and {pins.get((k,'1')),pins.get((k,'2'))}=={r['sygnal'],r['rezystor_do']} for k in vals),r
    assert r['poziom']==('0' if r['rezystor_do']=='GND' else '1') and r['rezystancja']=='10k',r
# 1.10: the service-wall sticker names the node of every pin as SERWIS.csv
stk={}
for line in (P/'docs/NAKLEJKA-SERWIS.md').read_text(encoding='utf-8').splitlines():
    c=[x.strip() for x in line.strip('|').split('|')]
    if len(c)==4 and c[0].isdigit():
        for j,cellv in zip(('J_SV1','J_SV2','J_SV3'),c[1:]):stk[(j,c[0])]=cellv.split('= ')[-1]
assert stk=={(r['zlacze'],r['pin']):r['siec'] for r in sv},'sticker differs from SERWIS.csv'
parts=json.loads((P/'docs/parts.json').read_text(encoding='utf-8'))
assert len(tables['BOM.csv'])==len(parts)==len(vals)
for r in tables['BOM.csv']:
    assert r['mpn']==parts[r['ref']]['mpn'] and r['footprint']==parts[r['ref']]['footprint'],r
# R6 mounting rule (task §4; 30.09: owned MF0207/K15 stock is used up by P09 R2 and P10 R2, so every P03 resistor and
# capacitor is a purchase and new purchases are SMD 1206; one 100 nF code on the whole board)
for ref,p in parts.items():
    if re.fullmatch(r'[RC]\d+',ref):
        assert '1206' in p['footprint'] and 'Vertical' not in p['footprint'] and 'K15' not in p['footprint'],(ref,p['footprint'])
    if re.fullmatch(r'C\d+',ref) and p['value'].startswith('100n'):
        assert p['mpn']=='GRM31CR71H104KA01L',(ref,p['mpn'])
purchase_refs=[]
for r in tables['zakupy.csv']:
    refs=[x.strip() for x in r['oznaczenia'].split(',')]
    assert len(refs)==int(r['ilosc_szt']),r
    assert all(parts[ref]['mpn']==r['nazwa'] for ref in refs),r
    purchase_refs+=refs
assert len(set(purchase_refs))==len(purchase_refs)
assert set(purchase_refs)=={r for r in parts if not r.startswith('TP')}
report={'pass':True,'csv_rows':{n:len(r) for n,r in sorted(tables.items())},'sticker_pins':len(stk),'cad_pins_checked':len(pins),'purchase_parts_checked':len(purchase_refs)}
(P/'verification/table-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(report)
