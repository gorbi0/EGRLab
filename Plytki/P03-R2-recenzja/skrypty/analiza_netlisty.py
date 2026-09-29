"""Niezależna analiza netlisty P03-R2 (recenzja Claude, 27.09.2026) — nie korzysta z verify_function.py.

1. Każdy pin złącza: czy sieć jest szyną zasilania albo łączy się z nią przez rezystor < 100 Ω (bez ograniczenia prądu).
2. Sieci wychodzące na złącza, które łączą się z pinem EN modułu (pojemność 1 µF na module = wolne zbocze).
3. Wejścia buforów 74LVC125A: rezystor ustalający (liczba i kierunek) oraz czy stoi po stronie złącza.
4. Porównanie z P04-R2.1 J2 (H_SAFE) i P02-R3 J3 (LV03), P05-R1 J1 (B2B): pin w pin.
"""
from pathlib import Path
import json, re, sys, xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent; PL = HERE.parents[1]
root = ET.parse(PL / 'P03-R2-review/verification/P03.xml').getroot()
val = {c.get('ref'): c.findtext('value') for c in root.findall('./components/comp')}
nodes = {}
pin = {}
for net in root.findall('./nets/net'):
    n = net.get('name').split('/')[-1]
    for nd in net.findall('node'):
        k = nd.get('ref') + '.' + nd.get('pin'); pin[k] = n; nodes.setdefault(n, []).append(k)
RAILS = {'3V3_CORE', '3V3_IO', '5V_SYS', '5V_M1'}


def ohms(v):
    t = v.split('/')[0].strip().upper(); m = re.fullmatch(r'(\d+)([RKM]?)(\d*)', t)
    return float(m[1] + ('.' + m[3] if m[3] else '')) * {'': 1, 'R': 1, 'K': 1e3, 'M': 1e6}[m[2]] if m else None


out = {'rail_on_connector': [], 'en_on_connector': [], 'buffer_inputs': {}, 'interfaces': {}}
conn = sorted({k.split('.')[0] for k in pin if re.fullmatch(r'J\d+', k.split('.')[0])})
for k, n in pin.items():
    ref = k.split('.')[0]
    if ref not in conn or n in ('GND',) or n.startswith('unconnected') or n == 'NC':
        continue
    if n in RAILS and ref != 'J10':
        out['rail_on_connector'].append([k, n, 'direct'])
    for m in nodes[n]:
        r = m.split('.')[0]
        if r.startswith('R'):
            other = [x for x in nodes[pin[m]] if False]  # placeholder
            far = [pin[f'{r}.{p}'] for p in ('1', '2') if f'{r}.{p}' in pin and pin[f'{r}.{p}'] != n]
            if far and far[0] in RAILS and (ohms(val[r]) or 0) < 100:
                out['rail_on_connector'].append([k, n, f'{r} {val[r]} to {far[0]}'])
    if 'M1.J1-3' in nodes[n]:
        out['en_on_connector'].append([k, n, sorted(nodes[n])])
LVC_IN = {'2', '5', '9', '12'}
for u in ('U11', 'U12', 'U13', 'U14', 'U21', 'U22', 'U23'):
    for p_ in LVC_IN:
        n = pin.get(f'{u}.{p_}')
        if not n or n == 'GND':
            continue
        rs = [(m.split('.')[0], val[m.split('.')[0]], [pin[f"{m.split('.')[0]}.{q}"] for q in ('1', '2') if pin[f"{m.split('.')[0]}.{q}"] != n][0])
              for m in nodes[n] if m.split('.')[0].startswith('R')]
        pulls = [r for r in rs if r[2] in ('GND', '3V3_CORE')]
        out['buffer_inputs'][f'{u}.{p_}'] = {'net': n, 'pulls': pulls, 'connector_side': any(x.split('.')[0] in conn for x in nodes[n])}


def other(pkg, ref):
    p = json.loads((PL / pkg / 'docs/parts.json').read_text(encoding='utf-8'))
    p = p if isinstance(p, dict) else {x['ref']: x for x in p}
    return p[ref]['pins']


for name, (pkg, ref, mine) in {'H_SAFE P03 J4 - P04 J2': ('P04-R2.1-review', 'J2', 'J4'), 'LV03 P03 J10 - P02 J3': ('P02-R3-review', 'J3', 'J10'),
                               'DAQ P03 J1 - P05 J1': ('P05-R1-review', 'J1', 'J1')}.items():
    o = other(pkg, ref); m = {k.split('.')[1]: v for k, v in pin.items() if k.split('.')[0] == mine}
    diff = {k: [m.get(k), v] for k, v in o.items() if not (m.get(k) == v or (v == 'NC' and (m.get(k) or '').startswith('unconnected')))}
    out['interfaces'][name] = {'pins': len(o), 'differences': diff}
print(json.dumps({k: v for k, v in out.items() if k != 'buffer_inputs'}, indent=1, ensure_ascii=False))
bad = {k: v for k, v in out['buffer_inputs'].items() if len(v['pulls']) != 1}
print('buffer inputs', len(out['buffer_inputs']), 'without exactly one pull:', bad)
(HERE / 'analiza_netlisty.json').write_text(json.dumps(out, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
