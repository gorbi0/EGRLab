"""R6: human-facing tables from the generator sources and the exported netlist. Checked independently by verification/check_tables.py.
docs/J_BP.csv (for P12): zlacze;pin;siec;kierunek;plytka_docelowa;uwagi
docs/SERWIS.csv: zlacze;pin;siec;rezystor;cel_pomiaru   (siec = node measured; rezystor = reference and value)
docs/netlist-pinowa.csv: ref;pin;net from verification/P03.xml
docs/STANY-DOMYSLNE.csv (1.10, review: was hand-written and kept the pre-swap gates): from the SOURCE / RECEIVER tables that
verify_function.py checks against the netlist
docs/NAKLEJKA-SERWIS.md (1.10, user decision): the legend of the service-pin labels as a sticker for the service wall
"""
from pathlib import Path
import csv, json, sys, xml.etree.ElementTree as ET
P = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(P / 'src'))
from jbp_pinout import JBP
from serwis_pinout import SERWIS
from verify_function import SOURCE, RECEIVER
import ast
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
w('STANY-DOMYSLNE.csv', ['sygnal', 'wejscie', 'rezystor_do', 'poziom', 'rezystancja', 'grupa', 'znaczenie'],
  [[sig, f'{u}.{n}', rail, 0 if rail == 'GND' else 1, '10k', grp, 'idle/reset; nie potwierdza obecnosci modulu']
   for grp, tab in (('zrodlo', SOURCE), ('odbiornik', RECEIVER)) for sig, (u, n, rail) in tab.items()])
# sticker: labels as printed (LABEL / ABBR parsed from silkscreen.py, which needs pcbnew to run)
tabs = {n.targets[0].id: ast.literal_eval(n.value) for n in ast.parse((P / 'src/silkscreen.py').read_text(encoding='utf-8')).body
        if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') in ('LABEL', 'ABBR')}
def cell(j, p):
    node = 'GND' if p in (1, 13) else SERWIS[j][p][0]
    t = tabs['LABEL' if j == 'J_SV1' else 'ABBR'][node]
    return node if t == node else f'**{t}** = {node}'
L = ['# Naklejka na ścianę serwisową P03 R6 — opisy kołków J_SV1–J_SV3', '',
     'Plik generowany przez `src/write_tables.py` z `src/serwis_pinout.py` i tabel opisów w `src/silkscreen.py` (decyzja 1.10.2026: legenda skrótów '
     'na naklejce zamiast na płytce, gdzie po złożeniu stosu leżała pod płytką poziomu 3). Wydrukować i nakleić na ściance serwisowej obudowy (strona krawędzi B) na wysokości poziomu 2.', '',
     'Patrząc od krawędzi B (od strony serwisu): J_SV1 po lewej (slot S1), J_SV3 po prawej (slot S3); w każdej listwie pin 1 po prawej '
     '(większe x). Każdy kołek poza GND przez rezystor przy węźle (1 kΩ; 10 kΩ dla linii z podciąganiem / otwartym drenem i SUP_N_OUT).', '',
     '| Kołek | J_SV1 (S1) | J_SV2 (S2) | J_SV3 (S3) |', '|---:|---|---|---|']
L += [f'| {p} | ' + ' | '.join(cell(j, p) for j in ('J_SV1', 'J_SV2', 'J_SV3')) + ' |' for p in range(1, 14)]
(P / 'docs/NAKLEJKA-SERWIS.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
