import io, os, csv, math, sys
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1]
ns = {}
exec(open(os.path.join(HERE, 'items.py'), encoding='utf-8').read(), ns)
exec(open(os.path.join(HERE, 'items2.py'), encoding='utf-8').read(), ns)
exec(open(os.path.join(HERE, 'tme.py'), encoding='utf-8').read(), ns)
exec(open(os.path.join(HERE, 'other.py'), encoding='utf-8').read(), ns)
I, TME, KAMAMI, WIRES, SUPP, OPEN, HOLD, OPTIONAL = (ns[k] for k in ('I', 'TME', 'KAMAMI', 'WIRES', 'SUPP', 'OPEN', 'HOLD', 'OPTIONAL'))
tme = {s: q for s, q, *_ in TME}
kam = {s: q for s, _, q, *_ in KAMAMI}
supp = {s: q for s, q, *_ in SUPP}

# pokrycie: klucz pozycji -> [(źródło, symbol, ile sztuk tej pozycji pokrywa)]
M = {
 'TLC555CP': [('T', 'TLC555CP', 1)], 'LM2937': [('T', 'LM2937ET-3.3/NOPB', 1)], 'CD74HC123E': [('T', 'CD74HC123E', 1)],
 'SN74HC14N': [('T', 'CD74HC14E', 1)], 'SN74HC74N': [('T', 'SN74HC74N', 1)], 'MCP100-300': [('S', 'MCP100-300DI/TO', 1)],
 'SN74HC139N': [('T', 'SN74HC139N', 1)], 'SN74LVC1G37': [('S', 'SN74LVC1G37DBVRQ1 (zamiast SN74LVC1G37DBVR)', 1)], 'SN74LVC1G17': [('T', 'SN74LVC1G17DBVR', 1)],
 'LTC4412': [('S', 'LTC4412IS6#TRPBF', 1)], 'AO3401A': [('T', 'AO3401A', 1)], 'ADR4525BRZ': [('S', 'REF5025AIDR (zamiast ADR4525BRZ)', 1)],
 'TLV1702': [('T', 'TLV1702AIDGKR', 1)], 'TBD62083APG': [('S', 'TBD62083APG', 2)], 'MCP1700-33': [('T', 'MCP1700-3302E/TO', 1)],
 'TPS2553DBVR': [('T', 'TPS2553DBVR', 1)], 'MCP120-300': [('S', 'MCP120-300DI/TO', 1)], 'MCP120-450': [],
 'TCAN1051V': [('T', 'TCAN1051VDRQ1', 1)], 'PESD2CAN': [('T', 'PESD2CAN.215', 1)], 'STPS20100CT': [('S', 'STPS20100CT', 1)],
 '1N5819': [('T', '1N5819-E3/73', 2)], '1N5817': [('T', '1N5817-E3/73', 1)], 'BAT85': [('T', 'BAT85S-TAP', 1)], '1N4148': [],
 'LM2903P': [], 'TL431BILP': [], '2N3904': [('T', '2N3904BU', 3)], 'G6K-2P-Y': [('S', 'G6K-2P-Y DC5', 4)],
 'L-934GD': [('T', 'L-934GD', 10)], 'L-934YD': [('T', 'L-934YD', 1)], 'L-934ID': [('T', 'L-934ID', 1)],
 'R-10K': [('T', 'MF0207FTE-10K', 107)], 'R-1K': [('T', 'MF0207FTE-1K', 36)], 'R-100K': [('T', 'MF0207FTE-100K', 15)],
 'R-4K7': [('T', 'MF0207FTE-4K7', 3)], 'R-47K': [('T', 'MF0207FTE-47K', 2)], 'R-100R': [('T', 'MF0207FTE-100R', 7)],
 'R-330R': [('T', 'MBB02070C3300FCT00', 2)], 'R-1M': [('T', 'MF0207FTE-1M', 2)], 'R-470R': [('T', 'MF0207FTE-470R', 1)],
 'R-220R': [('T', 'MF0207FTE-220R', 1)], 'R-33R': [('T', 'MBB02070C3309FCT00', 5)], 'R-47R': [('T', 'MF0207FTE-47R', 6)],
 'R-220K': [('T', 'MF0207FTE-220K', 1)], 'R-68K': [('T', 'MF0207FTE-68K', 1)], 'R-560R': [('T', 'LR1F560R', 1)],
 'R-232K': [('S', 'YR1B232KCC (232k 0,1 % zamiast 1 %)', 1)], 'R-6K8': [], 'R-1R-0207': [], 'R-1R-1W': [('T', 'KNP01U-1R', 2)],
 'R-39R-2W': [('T', 'PR02-39R', 1)], 'R-1K-2W': [('T', 'PMR2S-1K', 1)],
 'R01-30K1': [('T', 'MRA0207-30K1', 1)], 'R01-38K3': [('S', 'YR1B38K3CC (38,3k 0,1 %)', 1)], 'R01-10K': [('T', 'MBB0207VD1002BC100', 3)],
 'R01-15K': [('S', 'YR1B15KCC (15k 0,1 %)', 1)], 'R01-6K04': [('S', 'YR1B6K04CC (6,04k 0,1 %)', 1)], 'R01-20K': [('T', 'MBB0207VD2002BC100', 1)],
 'R01-5K11': [('S', 'YR1B5K11CC (5,11k 0,1 %)', 1)], 'R01-24K9': [('S', 'YR1B24K9CC (24,9k 0,1 %)', 1)], 'R01-100K': [('T', 'MBB0207VD1003BC100', 5)],
 'R01-499K': [('S', 'YR1B499KCC (499k 0,1 %)', 1)], 'R01-300K': [('S', 'RN55E3003BB14 (300k 0,1 %)', 1)], 'R01-10R': [('S', 'YR1B10RCC (10R 0,1 %)', 2)],
 'R01-5K1': [('S', 'YR1B5K11CC (5,11k 0,1 %)', 2)],
 'R-33R-0805': [('T', 'RC0805FR-0733R', 2)], 'R-220R-1206': [('T', 'RC1206FR-07220R', 1)],
 'C-100n-0805': [('T', 'GRM21BR71H104KA01L', 33)], 'C-100n-0603': [('T', 'GCM188R71H104KA57D', 6)], 'C-1u-0805': [('T', 'GCM21BR71E105KA56L', 10)],
 'C-4u7-0805': [('T', 'GRM21BR71E475KA73L', 4)], 'C-2u2-0805': [('T', 'GCM21BR71E225KA73L', 1)], 'C-10n-0805': [('T', 'GRM216R71H103KA01D', 2)],
 'C-1n-0805': [('T', 'C0805C102K5RAC', 1)], 'C-220p-0805': [('T', 'GRM2165C1H221JA01D', 7)], 'C-22u-1210': [('T', 'CL32B226KAJNNNE', 2)],
 'C-10u-1206': [('T', 'GRM31CR71C106KA12L', 1)], 'C-1u-1206': [('T', 'C3216X7R1H105KAB', 1)], 'C-100n-1206': [('T', 'C1206C104K5RAC', 2)],
 'K104': [('T', 'K104K15X7RF5TH5', 34)], 'K103': [('T', 'RDER71H103K0K1H03B', 3)], 'K102': [('T', 'RDE5C1H102J0M1H03A', 1)],
 'K471': [('T', 'RDE5C1H471J0M1H03A', 1)], 'EEUFR1H100': [('T', 'EEUFR1H100', 4)], 'EEUFR1H220': [('T', 'EEUFR1H220', 1)],
 'EEUFR1C220': [('T', 'EEUFR1H220', 2)], 'EEUFR1C471': [('T', 'EEUFR1C471', 2)], 'EEUFR1E220': [('T', 'EEUFR1H220', 1)],
 'EEUFR1H4R7': [('T', 'EEUEB1H4R7SH', 2)], 'MKS2-1u63': [('T', 'MKS2-1U/63-R', 2)], 'MKS2-470n63': [('T', 'MKS2-470N/63', 1)],
 'HC1V229': [('T', 'HC1V229M35045HA', 3)], 'PBV': [('O', 'PBV', 1)], 'HSA2547': [('T', 'HS25-47RF', 1)],
 'WS-SLTV': [('S', 'Würth 450301014042 (WS-SLTV)', 9)], 'MKDS2': [('T', 'MKDS1.5/2-5.08', 1)], 'GMSTBA3': [('S', 'Phoenix 1766246 GMSTBA 2,5/3-G-7,62', 1)],
 'MSTBVA4': [('T', 'MSTBVA2.5/4G5.0', 1)], 'MF-6048': [('S', 'Molex 39-29-6048 (4p Au, bez kołków)', 9)], 'MF-6148': [('S', 'Molex 39-29-6148 (14p Au)', 1)],
 'MF-6088': [('S', 'Molex 39-29-6088 (8p Au, bez kołków)', 1)], 'MF-6028': [('T', 'MX-39-29-6028', 1)], 'MF-9069': [('S', 'Molex 39-29-9069 (6p z kołkami)', 1)],
 'MF-9109': [('S', 'Molex 39-29-9109 (10p z kołkami)', 1)], 'MF-9129': [('S', 'Molex 39-29-6128 (12p Au, bez kołków) zamiast 39-29-9129', 1)],
 'IDC-H6': [('T', 'T821-1-06-S1', 6)], 'IDC-H8': [('T', 'T821-1-08-S1', 2)], 'IDC-H10': [('T', 'T821-1-10-S1', 2)], 'IDC-H16': [('T', 'T821-1-16-S1', 2)],
 'B2B-RA': [('H', 'SSW-108-02-G-D-RA', 1)], 'B2B-NA': [('H', 'TSW-108-08-G-D-RA', 1)],
 'F-1x22': [('T', 'ZL262-40SG', 2)], 'F-1x9': [('T', 'ZL262-9SG', 3)], 'F-1x7': [('T', 'ZL262-7SG', 6)],
 'DIP14': [('K', '648', 2)], 'DIP8': [('K', '1207058', 1)], 'DIP18': [('X', 'ICVT-18P', 2)], 'DIP16': [('K', '649', 1)],
 'SPDT-7201': [('S', 'C&K 7201SYCBE', 1)], 'S6A': [('T', 'S6A', 1)], 'SCHURTER-2507': [('T', '0001.2507', 1)], 'SCHURTER-2504': [('T', '0001.2504', 2)],
 'SCHURTER-2501': [('T', '0001.2501', 1)], 'PTF78': [('T', 'ZHL78', 4)], 'ADA4682': [('S', 'Adafruit 4682 (microSD)', 1)],
 'MF-2040': [('T', 'MX-5557-04R', 7)], 'MF-2140': [('T', 'MX-5557-14R', 1)], 'MF-2120': [('T', 'MX-5557-12R', 1)], 'MF-2100': [('T', 'MX-5557-10R', 2)],
 'MF-2080': [('T', 'MX-5557-08R', 1)], 'MF-2060': [('T', 'MX-5557-06R', 1)], 'MF-2020': [('T', 'MX-5557-02R', 1)], 'MF-0074': [('T', 'MX-39-00-0074', 68)],
 'IDC-F16': [('T', 'T812-1-16', 1)], 'IDC-F10': [('T', 'T812-1-10', 2)], 'IDC-F8': [('T', 'T812-1-08', 1)], 'IDC-F6': [('T', 'T812-1-06', 8)],
 'MSTB3-ST': [('T', 'MSTB2.5/3-ST-5.08', 1)], 'MSTB4-ST': [('T', 'MSTB2.5/4-ST-5.08', 1)], 'DT04-12PA': [('T', 'DT04-12PA', 1)],
 'DT04-12PB': [('S', 'TE DEUTSCH DT04-12PB', 1)], 'DT04-12PC': [('S', 'TE DEUTSCH DT04-12PC', 1)], 'W12P': [('T', 'W12P', 3)],
 'DT-PIN': [('T', '04602021631-TEC-0', 25)], 'DT-PLUG': [('T', '114017', 11)], 'BNC-ISO': [('T', 'BNC-056', 2)], 'OBD-M': [('K', '1191911', 1)],
 'EAO-412K': [('O', 'EAO', 1)], 'EAO-473': [('O', 'EAO', 1)], 'EAO-435': [('O', 'EAO', 3)], 'EAO-432': [('O', 'EAO', 2)],
 'BTN-NO': [('K', '1184699', 1), ('K', '1184697', 1)], 'DUPONT-FF': [('K', '204596', 25)],
 'AWG22': [('W', 'LGY0.35/25-BK', 25)], 'AWG24': [('O', 'AWG24', 0)], 'AWG20': [('W', 'LGY0.50/25-BK', 0.4)], '0.5mm2': [('W', 'LGY0.50/25-BK', 3.15)],
 '1.5mm2': [('W', 'LGY1.5/10-BK', 10)], '2.5mm2': [('P', 'zakup lokalny jak w P01', 0.9)], 'RIBBON': [('W', 'DS1057-16A282R', 30.5)],
 'CAN-PAIR': [('T', 'BUS-CAN-1X2X0.22', 1)], 'RG174': [('P', 'posiadane', 0.15)],
 'M3-STANDOFF': [('T', 'TFF-M3X10/DR185', 40)], 'M3-SCREW': [], 'M3-WASHER': [], 'M25-STANDOFF': [('T', 'TFF-M2.5X12/DR182', 6), ('T', 'M2.5X6/D7985B', 12)],
 'TIE-2.5': [], 'FERRULE-2.5': [], 'TC-K': [('X', '7J360100020100A000', 2)], 'CLAMP35': [('X', 'OBJ35', 3)],
}
used = {}
problems = []
for it in I:
    need = sum(it['boards'].values()) - it['cover'][0]
    if it['key'] not in M:
        problems.append('BRAK MAPOWANIA ' + it['key']); continue
    got = sum(q for _, _, q in M[it['key']])
    if need > 0 and not M[it['key']]:
        problems.append(f"{it['key']}: potrzeba {need}, brak źródła")
    if M[it['key']] and M[it['key']][0][0] not in 'OHXP' and got + 1e-9 < need:
        problems.append(f"{it['key']}: potrzeba {need}, pokryte {got}")
    for src, sym, q in M[it['key']]:
        used[(src, sym)] = used.get((src, sym), 0) + q
# ilości w koszyku muszą pokryć sumę przypisań
for (src, sym), q in used.items():
    if src == 'T' and tme.get(sym, 0) + 1e-9 < q: problems.append(f'TME {sym}: w koszyku {tme.get(sym)}, przypisane {q}')
    if src == 'K' and kam.get(sym, 0) * {'204596': 40}.get(sym, 1) + 1e-9 < q: problems.append(f'Kamami {sym}: w koszyku {kam.get(sym)}, przypisane {q}')
    if src == 'S' and supp.get(sym, 0) + 1e-9 < q: problems.append(f'uzupełnienie {sym}: {supp.get(sym)}, przypisane {q}')
for sym in tme:
    if ('T', sym) not in used: problems.append('TME bez przypisania: ' + sym)
print('\n'.join(problems) or 'pokrycie OK')

def zl(x): return f'{x:,.2f}'.replace(',', ' ').replace('.', ',')
tme_total = sum(q * p for _, q, p, *_ in TME)
kam_total = sum(q * p for _, _, q, p, *_ in KAMAMI)
wire_total = sum(q * p for _, q, p, *_ in WIRES) + 94.97
far = [(s, q, f) for s, q, _, f, m, d, _ in SUPP if d == 'F']
mou = [(s, q, m) for s, q, _, f, m, d, _ in SUPP if d == 'M']
far_total = sum(f[1] * f[2] for _, _, f in far)
mou_known = sum(q * m[1] for _, q, m in mou if m[1])
print('TME', zl(tme_total), 'Kamami', zl(kam_total), 'przewody', zl(wire_total), 'Farnell', zl(far_total), 'Mouser (znane ceny)', zl(mou_known))
if problems: sys.exit(1)

os.makedirs(OUT, exist_ok=True)
def w(name, text):
    with open(os.path.join(OUT, name), 'w', encoding='utf-8', newline='\r\n') as f: f.write(text)
w('TME-wklej.txt', ''.join(f'{s} {q}\n' for s, q, *_ in TME))
w('TME-przewody-wklej.txt', ''.join(f'{s} {q}\n' for s, q, *_ in WIRES) + 'DS1057-16A282R 1\n')
w('FARNELL-wklej.txt', ''.join(f'{f[0]},{f[2]}\n' for s, q, f in far))
w('MOUSER-wklej.txt', ''.join(f'{m[0]},{q}\n' for s, q, m in mou))
# CSV zbiorczy
buf = io.StringIO(); cw = csv.writer(buf, delimiter=';', lineterminator='\n')
cw.writerow(['dostawca', 'symbol', 'ilosc', 'cena_szt_zl', 'cena_typ', 'stan', 'plytki', 'uwagi'])
for s, q, p, st, b, u in TME: cw.writerow(['TME', s, q, f'{p:.4f}'.replace('.', ','), 'netto', st, b, u.replace(';', ',')])
for s, n, q, p, st, b, u in KAMAMI: cw.writerow(['Kamami', f'{s} {n}', q, f'{p:.2f}'.replace('.', ','), 'brutto', st, b, u.replace(';', ',')])
for s, q, p, st, b, u in WIRES: cw.writerow(['TME przewody', s, q, f'{p:.2f}'.replace('.', ','), 'netto', st, b.replace(';', ','), u.replace(';', ',')])
cw.writerow(['TME przewody', 'DS1057-16A282R', 1, '94,97', 'netto', 258, 'taśmy IDC', 'rolka 30,5 m'])
for s, q, b, f, m, d, u in SUPP:
    if d == 'F': cw.writerow(['Farnell', f'{f[0]} {s}', f[2], f'{f[1]:.2f}'.replace('.', ','), 'netto', f[3], b, u.replace(';', ',')])
    else: cw.writerow(['Mouser', f'{m[0]} {s}', q, f'{m[1]:.2f}'.replace('.', ','), 'netto', m[2], b, u.replace(';', ',')])
w('zakupy-2.csv', '﻿' + buf.getvalue())
print('zapisano', OUT)
