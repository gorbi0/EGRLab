"""Cross-check human-facing CSV tables against the exported CAD and parts list.
Run with standard Python, from any directory. The generator is not imported.
"""
from pathlib import Path
import csv, json, xml.etree.ElementTree as ET
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
csvpins={(r['ref'],r['pin']):r['net'] for r in tables['netlist-pinowa.csv']}
assert csvpins==pins, 'CSV pinmap differs from CAD'
for r in tables['interfejsy.csv']:
    assert pins[(r['zlacze'],r['pin'])]==r['sygnal'],r
    assert r['koniec_lutowany'],r
parts=json.loads((P/'docs/parts.json').read_text(encoding='utf-8'))
assert len(tables['BOM.csv'])==len(parts)==88
for r in tables['BOM.csv']:
    assert r['mpn']==parts[r['ref']]['mpn'] and r['footprint']==parts[r['ref']]['footprint'],r
purchase_refs=[]
for r in tables['zakupy.csv']:
    refs=[x.strip() for x in r['oznaczenia'].split(',')]
    assert len(refs)==int(r['ilosc_szt']),r
    assert all(parts[ref]['mpn']==r['nazwa'] for ref in refs),r
    purchase_refs+=refs
assert len(set(purchase_refs))==len(purchase_refs)
assert set(purchase_refs)=={r for r in parts if not r.startswith('TP')}
report={'pass':True,'csv_rows':{n:len(r) for n,r in tables.items()},'cad_pins_checked':len(pins),'purchase_parts_checked':len(purchase_refs)}
(P/'verification/table-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(report)
