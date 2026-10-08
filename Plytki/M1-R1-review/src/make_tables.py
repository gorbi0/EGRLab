"""M1-R1 tables from parts.py (single source): X1 contract docs/X1.csv, GPIO map docs/GPIO.csv, pin list, purchase list docs/zakupy.csv.
verify_m1.py compares X1.csv / GPIO.csv with the EXPORTED netlist."""
from parts import *
import collections


def table(name, fields, rows):
    with (P / 'docs' / name).open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f, delimiter=';'); w.writerow(fields); w.writerows(rows)


table('X1.csv', ['x1', 'siec', 'pole_pcb', 'przewod', 'uwagi'], X1)
NAMES = {**{f'J1-{i + 1}': n for i, n in enumerate(J1N)}, **{f'J3-{i + 1}': n for i, n in enumerate(J3N)}}
table('GPIO.csv', ['gpio', 'pin_modulu', 'siec'], sorted([[int(n[4:].split('_')[0]), pad, PARTS['M1']['pins'][pad]] for pad, n in NAMES.items() if n.startswith('GPIO')]))
table('netlist-pinowa.csv', ['ref', 'pin', 'net'], [[r, p, n] for r, v in PARTS.items() for p, n in v['pins'].items()])
g = collections.defaultdict(list)
for r, v in PARTS.items():
    if v.get('dnp'): continue
    g[(v['zrodlo'], v['mpn'], v['display'], v['footprint'].split(':')[-1])].append(r)
key = lambda s: (re.sub(r'\d', '', s), int(re.sub(r'\D', '', s) or 0))
table('zakupy.csv', ['zrodlo', 'nazwa', 'wartosc', 'ilosc_szt', 'referencje', 'obudowa'], [[z, m, d, len(rr), ', '.join(sorted(rr, key=key)), f] for (z, m, d, f), rr in sorted(g.items())]
      + [[o['zrodlo'], o['mpn'], o['display'], o['qty'], o['ref'], 'obudowa (poza plytka)'] for o in OFFBOARD])
print('X1.csv, GPIO.csv, netlist-pinowa.csv, zakupy.csv written;', sum(1 for p in PARTS.values() if not p.get('dnp')), 'fitted parts,', len(g), 'lines')
