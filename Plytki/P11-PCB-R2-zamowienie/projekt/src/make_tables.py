"""P11-R2 review tables from parts.py (single source): P12 contract docs/J_P12.csv (format of J_BP.csv of the other boards), BOM with the
variant column, wire list with cross sections, port cavity list (wires that bypass P11), pin netlist and the R1 -> R2 net list.
verify_p12.py compares J_P12.csv with the EXPORTED netlist, not with this generator."""
from parts import *
import xml.etree.ElementTree as ET
def table(name, fields, rows):
    with (P / 'docs' / name).open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f, delimiter=';'); w.writerow(fields); w.writerows(rows)
INFO = {2: ('pwr', 'P04 (pelny) / P11 R1 (LOGGER)', 'zasilanie stykow: LOGGER - z 3V3_IO przez R1 100R na P11; z P04 - P04 R40 100R, R1 DNP'),
        4: ('out', 'P04 (PANELSAFE)', 'petla MECH: kluczyk, NC L1/L2, mostek 10-11 adaptera AT; w LOGGER bez odbiornika'),
        6: ('out', 'P04 (PANELSAFE)', 'STOP NC -> SAFE_N (R4 10k na P04 R2.1); w LOGGER bez odbiornika'),
        8: ('out', 'P04 (PANELSAFE)', 'ARM do GND; podciaganie na P04 (R2 10k + R3 1k w R2.1); w LOGGER bez odbiornika'),
        10: ('in', 'P03 R6 (J_BP1.10)', 'SCOPE_TRIG przez R12 330R na P03; do BNC przez J6; GND po obu stronach'),
        13: ('out', 'P03 R6 (J_BP1.13)', 'przycisk MARK do GND; 10k do 3V3_CORE + 100n na P03; wyjatek od GND na nieparzystym (jak P03)'),
        14: ('out', 'P03 R6 (J_BP1.14), P04 (PANELSAFE)', 'kluczyk TEST; 10k do GND na P03 (R27); na P04 1k + 10k'),
        15: ('out', 'P03 R6 (J_BP1.15)', 'petla DIAG NC L1/L2; 10k do GND na P03 (R6); wyjatek od GND na nieparzystym (jak P03)'),
        16: ('out', 'P03 R6 (J_BP1.16)', 'detektor TEST NO; 10k do GND na P03 (R8)'),
        20: ('pwr', 'P02 R4 (J_BP 8/10)', '3V3_IO tylko do R1 (LOGGER); przy P04 R1 DNP - pin bez odbiorcy; z dala od PANEL_3V3')}
rows = []
for p in sorted(PARTS['J_P12']['pins'], key=int):
    n = PARTS['J_P12']['pins'][p]; k, tgt, uw = INFO.get(int(p), ('gnd', 'P12 (wszystkie)', 'GND (rezerwa sygnalowa odrzucona 4.10)' if int(p) in (12, 18) else ''))
    rows.append(['J_P12', p, n, k, tgt, uw])
table('J_P12.csv', ['zlacze', 'pin', 'siec', 'kierunek', 'plytka_docelowa', 'uwagi'], rows)
# --- BOM (one board + off-board panel parts)
SEC = {'J_P12': 'tasma IDC 1,27 mm (AWG28) z gniazda katowego w strone sciany A, dlugosc do P12 z makiety', 'J11': 'AWG24 (0,25 mm2), linka', 'J8': 'AWG24 (0,25 mm2), linka',
       'J6': 'RG174 ok. 100 mm', 'X6': 'RG174 (koniec od J6)'}
table('BOM.csv', ['ref', 'source_ref', 'display', 'mpn', 'qty', 'footprint', 'on_board', 'wariant_LOGGER', 'wariant_pelny', 'przewod', 'note'],
      [[r, v['source_ref'], v['display'], v['mpn'], 1, v['footprint'], 'tak' if v['on_board'] else 'nie (panel)',
        v.get('variant', {}).get('LOGGER', 'fitted'), v.get('variant', {}).get('FULL', 'fitted'), SEC.get(r, 'AWG24 do J11' if r.startswith('X1') else ''), v['note']]
       for r, v in PARTS.items()])
# --- wire list: P11 fields -> panel parts (functional terminals, R1 WIAZKI order)
W = []
for p, n in PARTS['J11']['pins'].items():
    ends = [f'{r}.{q_}' for r, v in PARTS.items() if r.startswith('X1') for q_, m in v['pins'].items() if m == n]
    W.append(['J11', p, n, ' / '.join(ends), 'AWG24 0,25 mm2'])
W += [['J8', '1', 'LOOP_OUT', 'port TEST (X8) komora 10', 'AWG24 0,25 mm2 (styk AT wielkosc 16 z redukcja albo wielkosc 20 - do zakupow)'],
      ['J8', '2', 'MECH_OK', 'port TEST (X8) komora 11', 'AWG24 0,25 mm2 (jw.)'],
      ['J6', '1', 'N_J_SCOPE_HOT', 'BNC X6 srodek', 'RG174 zyla'], ['J6', '2', 'GND', 'BNC X6 obudowa', 'RG174 ekran']]
table('lista-przewodow.csv', ['pole', 'pad', 'siec', 'drugi_koniec', 'przewod'], W)
MOT = '2,0 mm2 (AWG14) na calej dlugosci; styki zlocone AT60-215-1631 (pin) / AT62-209-1631 (gniazdo)'
DEST = {'ECU_P1': ('P06 J3.1', MOT + ' (prad silnika do 6 A, 10 A w probie biernej)'), 'EGR_P1': ('P06 J3.2', MOT),
        'T_EGR_P1': ('P07 (HOLD)', MOT), 'T_EGR_P3': ('P07 (HOLD)', MOT), '5V_SENSOR': ('P08 (pelny)', 'AWG22'), 'AGND_SENSOR': ('P08 (pelny)', 'AWG22'),
        'GND': ('P05 J4 GND (para TAPS)', 'AWG22'), 'LOOP_OUT': ('P11 J8.1', 'AWG24'), 'MECH_OK': ('P11 J8.2', 'AWG24')}
rows = []
for r, (name, key, pp) in PORTS.items():
    for cav, lab in pp:
        net = lab.split(' -> ')[0]
        if net == '-': rows.append([name, key, cav, '-', 'pusta (zaslepka komory)', '-']); continue
        d, wire = DEST.get(net, ('P05 J4 (TAPS)', 'AWG22')) if not net.startswith('TAP') else ('P05 J4 (TAPS)', 'AWG22; mostek z tym samym TAPem pozostalych portow przy portach, jedna wiazka 5 par do P05 J4')
        rows.append([name, key, cav, net, d, wire])
table('PORTY.csv', ['port', 'klucz', 'komora', 'siec', 'drugi_koniec', 'przewod'], rows)
table('netlist-pinowa.csv', ['ref', 'pin', 'net'], [[r, p, n] for r, v in PARTS.items() for p, n in v['pins'].items()])
# --- R1 -> R2 nets (from the frozen R1 netlist): every R1 net, where it is now and why
root = ET.parse(P / 'reference/P11-R1.xml').getroot()
r1 = sorted({n.get('name').split('/')[-1] for n in root.findall('./nets/net') if not n.get('name').split('/')[-1].startswith('unconnected-')})
r2 = {n for v in PARTS.values() for n in v['pins'].values()} - {'NC'}
WHY = {'ECU_P1': 'P11-4: przewod port L1.1 -> P06 J3.1 (bez J1 MSTB)', 'EGR_P1': 'P11-4: przewod port L1.2 -> P06 J3.2',
       'T_EGR_P1': 'P11-4: przewod port TEST.1 -> P07 (HOLD), bez J9', 'T_EGR_P3': 'P11-4: przewod port TEST.2 -> P07 (HOLD), bez J9',
       '5V_SENSOR': 'P11-1: przewod port TEST.3 -> P08 (pelny), bez J10', 'AGND_SENSOR': 'P11-1: przewod port TEST.4 -> P08 (pelny), bez J10'}
rows = []
for n in sorted(set(r1) | r2):
    if n in r1 and n in r2: rows.append([n, 'tak', 'tak', 'bez zmian (logika stykow R1)' if n not in ('PANEL_3V3', 'GND') else
                                         ('zrodlo: LOGGER R1 100R z 3V3_IO, pelny P04 R40 (P11-3)' if n == 'PANEL_3V3' else 'masa: J_P12 (9 pinow), J11, J6')])
    elif n in r1: rows.append([n, 'tak', 'nie', WHY.get(n, 'P11-5: TAPy przewodami port -> P05 J4, bez J7 Mini-Fit' if n.startswith('TAP') else 'usunieta')])
    else: rows.append([n, 'nie', 'tak', 'P11-3: zasilanie stykow w LOGGER (J_P12.20 -> R1)' if n == '3V3_IO' else 'nowa'])
table('sieci-R1-R2.csv', ['siec', 'R1', 'R2', 'uzasadnienie'], rows)
print('J_P12.csv, BOM.csv, lista-przewodow.csv, PORTY.csv, sieci-R1-R2.csv written;', len(rows), 'nets R1+R2')
