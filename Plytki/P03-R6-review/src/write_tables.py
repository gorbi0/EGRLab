"""R6: human-facing tables from the generator sources and the exported netlist. Checked independently by verification/check_tables.py.
docs/J_BP.csv (for P12): zlacze;pin;siec;kierunek;plytka_docelowa;uwagi
docs/SERWIS.csv: zlacze;pin;siec;rezystor;cel_pomiaru   (siec = node measured; rezystor = reference and value)
docs/netlist-pinowa.csv: ref;pin;net from verification/P03.xml
"""
from pathlib import Path
import csv, json, sys, xml.etree.ElementTree as ET
P = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(P / 'src'))
from jbp_pinout import JBP
from serwis_pinout import SERWIS
parts = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))


def w(name, head, rows):
    with (P / 'docs' / name).open('w', newline='', encoding='utf-8-sig') as f:
        c = csv.writer(f, delimiter=';'); c.writerow(head); c.writerows(rows)


w('J_BP.csv', ['zlacze', 'pin', 'siec', 'kierunek', 'plytka_docelowa', 'uwagi'], [[j, p, *JBP[j][p]] for j in JBP for p in range(1, 21)])
rows = []
for j, m in SERWIS.items():
    rows.append([j, 1, 'GND', '-', 'masa sondy'])
    for p in range(2, 13):
        node, val, why = m[p]
        r = next(r for r, x in parts.items() if x['source_ref'] == 'ADDED_R6_SERVICE_SERIES' and x['pins'] == {'1': node, '2': 'SV_' + node})
        rows.append([j, p, node, f"{r} {parts[r]['value']}", why])
    rows.append([j, 13, 'GND', '-', 'masa sondy'])
w('SERWIS.csv', ['zlacze', 'pin', 'siec', 'rezystor', 'cel_pomiaru'], rows)
x = ET.parse(P / 'verification/P03.xml').getroot()
pins = sorted(((n.get('ref'), n.get('pin'), 'NC' if net.get('name').split('/')[-1].startswith('unconnected-') else net.get('name').split('/')[-1])
               for net in x.findall('./nets/net') for n in net.findall('node')))
w('netlist-pinowa.csv', ['ref', 'pin', 'net'], pins)
print('tables:', len(JBP) * 20, 'J_BP rows,', len(rows), 'service rows,', len(pins), 'netlist rows')
