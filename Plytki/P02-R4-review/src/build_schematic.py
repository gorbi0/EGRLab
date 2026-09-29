"""P02-R4 schematic: four A3 sheets WEJ (root file P02.kicad_sch), STER, LV, MON.
Method as P02 R3 (build_schematic_r2.py): parts placed on a grid, every pin gets a stub and a label of its net
(global label when the net crosses sheets). Connectivity comes only from parts.py; verify_schematic.py checks it pin by pin.
"""
from parts import *
import cadlib, collections, copy

TITLES = [('WEJ', 'Wejscie pakietu 4S, Q9/Q1/Q2, VSW, VMOTOR, podtrzymanie C_H'),
          ('STER', 'Sterowanie: AUX5, REF, UVLO, OK, ENABLE, PFAIL_N, SAFE_N/PG, LED'),
          ('LV', 'Przetwornice TSR i rozdzial LV'),
          ('MON', 'PSU_OK, VBAT auta, zlacza do P04/P05')]
S = {n: Sheet(n, t, i, None if i == 1 else uid('WEJ')) for i, (n, t) in enumerate(TITLES, 1)}
SHORT = {'J1': 'BAT', 'J2': 'VMOTOR', 'J11': 'VSENSE', 'J12': 'PSUOK', 'J13': 'PG', 'J14': 'PWR', 'J15': 'VBAT_IN', 'J16': 'PFAIL'}


def put(sh, r, x, y, a=0, u=1):
    p = copy.copy(PARTS[r]); p['sch_value'] = p['display'].split(' / ')[0]
    if r in SHORT: p['sch_value'] = SHORT[r]
    if r.startswith('U'): p['fields'] = (-5, -14) if u in (1, 2) else (4, -9)
    if r.startswith('J'): p['fields'] = (-5, -12)
    if r.startswith('TP'): p['fields'] = (3, -4); p['sch_value'] = ''
    if r.startswith('Q'): p['fields'] = (5.5, -7)
    if r.startswith(('U1', 'U3', 'U4', 'U7', 'U8')) and len(r) == 2: p['fields'] = (9, -9)
    if r in ('U5', 'U6'): p['fields'] = (-9, -10)
    if r == 'D13': p['fields'] = (4, -6)
    S[sh].place(p, x, y, a, u)


def row(sh, y, items, x0=10, head=None):
    """items: (ref, width_units[, angle[, unit]]); parts centred in their cell."""
    x = x0
    if head: S[sh].text(head, x0 - 4, y - 8.5, 1.6)
    for it in items:
        ref, w, *rest = it; a = rest[0] if rest else 0; u = rest[1] if len(rest) > 1 else 1
        if ref: put(sh, ref, x + w / 2, y, a, u)
        x += w
    return x


V, D, Z = 0, 270, 270   # vertical 2-pin parts (R/C/F: 0; diodes: 270 -> cathode on top)
# ---------------- WEJ ----------------
row('WEJ', 20, [('J1', 14), ('TP1', 8), ('Q9', 14), ('R35', 10), ('D10', 10, Z), ('C1', 10), ('C2', 10)], head='Pakiet 4S -> J1 -> Q9 (Q_REV: ochrona polaryzacji, zrodla Q9/Q1 w SW_COM)')
row('WEJ', 36, [('Q1', 14), ('D4', 10, Z), ('C5', 10), ('C6', 10), ('R22', 10), ('R21', 10), ('TP2', 8), ('Q3', 14), ('R17', 10), ('R18', 10)],
    head='Q1 (Q_SW) - wlacznik; zalaczanie przez Q3/R21, narastanie VSW ustala C5 (jak P01 R3)')
row('WEJ', 52, [('Q2', 14), ('R27', 10), ('R24', 10), ('R23', 10), ('D9', 10, Z), ('Q4', 14), ('R25', 10), ('R26', 10), ('Q5', 14), ('R19', 10), ('R20', 10)],
    head='Q2 (Q_OFF) - szybkie wylaczanie; Q4/Q5 zwalniaja Q2 przy ENABLE. R23 = 22k / 0,5W (decyzja 29.09)')
row('WEJ', 68, [('D3', 10, Z), ('C3', 10), ('C4', 10), ('TP3', 8), ('F1', 10), ('J2', 16), ('D1', 16, Z), ('C20', 10), ('TP5', 8)],
    head='VSW: TVS, C, VMOTOR przez F1 5A; D1a/D1b -> VLOG')
row('WEJ', 84, [('R40', 10), ('D2', 16, Z), ('C12', 12), ('R41', 10), ('TP4', 8), ('TP6', 8)],
    head='Podtrzymanie: R40 22R bezpiecznikowy -> D2 -> C_H 2200u (-> D1b -> VLOG)')
# ---------------- STER ----------------
row('STER', 20, [('D11', 10, Z), ('D12', 10, Z), ('R1', 10), ('C7', 10), ('C8', 10), ('U1', 22), ('R2', 10), ('C9', 10), ('C10', 10), ('C11', 10), ('TP7', 8)],
    head='AUX5: LM2936 zasilany z SW_COM lub VLOG (D11/D12) - trwa przez podtrzymanie')
row('STER', 38, [('R3', 10), ('R4', 10), ('U3', 12), ('TP8', 8), ('R5', 10), ('J14', 14), ('R9', 10), ('R10', 10), ('C13', 10), ('TP9', 8), ('R12', 10), ('R11', 10)],
    head='REF 2,495 V; UVLO: SW_COM - R5 - PWR (J14) - R9 - UV_DIV (R10, C13) - R12 - UV_CMP <- R11 <- OK')
row('STER', 56, [('U2', 26, 0, 2), ('U2', 26, 0, 1), ('U2', 12, 0, 3), ('R6', 10), ('R7', 10), ('R13', 10), ('U4', 16), ('R36', 10), ('R37', 10), ('TP11', 8)],
    head='U2B: UVLO -> OK (histereza R11).  U2A: PFAIL_N = bufor OK (0,6 x OK wobec REF) -> R37 -> J16.1, J12.3')
row('STER', 72, [('R14', 10), ('D7', 10, Z), ('D8', 10, Z), ('R15', 10), ('Q6', 14), ('R16', 10), ('TP10', 8), ('J16', 14), ('R29', 10), ('LED1', 10, Z)],
    head='ENABLE = OK przez D7/D8 i wtornik Q6 (jak P01 R3); LED PWR na VSW')
row('STER', 88, [('Q7', 14), ('R30', 10), ('R31', 14), ('Q8', 16), ('R32', 10), ('R33', 10), ('R34', 10), ('J13', 16), ('TP12', 8)],
    head='SAFE_N i PG do P04 (z P01 R3): Q7 zasilany z P04_3V3 (J13.1), Q8 zwalnia przy ENABLE; R34 zwora PG_SEND-PG_LINK')
# ---------------- LV ----------------
row('LV', 22, [('F2', 10), ('C21', 10), ('U5', 26), ('C22', 10), ('TP13', 10), ('F3', 10), ('C23', 10), ('U6', 26), ('C24', 10), ('TP14', 10)],
    head='VLOG -> F2/F3 1A MINI -> TSR 2-2450 (5V_SYS), TSR 2-2433 (3V3_IO) - jak R3')
row('LV', 50, [('J3', 30), ('J4', 30), ('J5', 30), ('J6', 30)], x0=12, head='LV03..LV10: 1=5V_SYS 2=GND 3=3V3_IO 4=GND (bez zmian)')
row('LV', 72, [('J7', 30), ('J8', 30), ('J9', 30), ('J10', 30)], x0=12)
# ---------------- MON ----------------
row('MON', 22, [('U8', 16), ('R43', 10), ('C26', 10), ('U9', 26, 0, 1), ('U7', 16), ('R42', 10), ('C25', 10)], head='Nadzor szyn (jak R3): U8 5V_SYS, U7 3V3_IO, U9A przesuwa poziom')
row('MON', 44, [('U10', 26, 0, 1), ('R44', 10), ('TP15', 10), ('U10', 26, 0, 2), ('U10', 26, 0, 3), ('U10', 26, 0, 4)], head='PSU_OK = SUP3_N & SUP5_N (U10A); bramki B-D nieuzywane, wejscia do GND')
row('MON', 66, [('U9', 26, 0, 2), ('U9', 26, 0, 3), ('U9', 26, 0, 4), ('U9', 12, 0, 5), ('C27', 10), ('C28', 10), ('U10', 12, 0, 5), ('C29', 10)], head='U9B-D nieuzywane (wejscia do GND, OE# do 3V3_IO); zasilanie U9/U10')
row('MON', 88, [('J12', 18), ('J15', 16), ('R38', 10), ('D13', 10, 90), ('J11', 16), ('TP16', 10), ('TP17', 10)],
    head='J12 PSUOK do P04 (pin 3 = PFAIL_N); VBAT auta: J15 - R38 10k - D13 P6KE24CA - J11 VSENSE do P05 CH7')

ns = collections.defaultdict(set)
for name, sh in S.items():
    for part, pins in sh.parts.values():
        for n in pins: ns[part['pins'][n]].add(name)
cadlib.CROSS = {n for n, v in ns.items() if len(v) > 1 and n != 'NC'}
flag = symbol('power', 'PWR_FLAG')
for i, (sh, net, x, y) in enumerate([('WEJ', 'GND', 150, 20), ('LV', 'P02_VIN_DC5', 18, 36), ('LV', 'P02_VIN_DC33', 94, 36), ('STER', 'P02_AUX_IN', 150, 20)], 1):
    part = {'ref': f'#FLG{i}', 'display': 'PWR_FLAG', 'source_ref': 'ERC_SOURCE', 'mpn': '', 'footprint': '', 'symbol': flag, 'pins': {'1': net}, 'qty': 0, 'url': ''}
    S[sh].place(part, x, y)
for name, sh in S.items(): sh.text(f'P02-R4 / {sh.num:02d}   {name}: {sh.title.upper()}', 8, 5, 2)
W = S['WEJ']
W.text('Z-06: pojemnosc zalaczana przez Q1 <= 220 uF lacznie: C3 47u + VLOG (C20 22u, C21/C23 10u) + wejscie P07 <= 131 uF.', 8, 91, 1.3)
W.text('C_H ladowany osobno przez R40 + D2 (nie liczy sie do 220 uF). Hold-up po PFAIL_N: docs/OBLICZENIA-R4.md.', 8, 93.5, 1.3)
St = S['STER']
St.text('PWR rozwarty albo przerwany przewod = UV_DIV do masy = wylaczone. UVLO 13,53 / 12,51 V (nominalnie).', 8, 97, 1.3)
St.text('P04_3V3 (J13.1) to 3V3 wracajace z P04 - celowo NIE polaczone z lokalnym 3V3_IO (SAFE_N = L bez ENABLE).', 8, 99.5, 1.3)
St.text('Odstepstwo od D-06 (dosl.): U2A buforuje OK zamiast porownywac UV_CMP - PFAIL_N nie moze rozjechac sie ze stanem Q1.', 8, 102, 1.3)
S['LV'].text('BUDZET LACZNY <= 6 W na VLOG (ze stratami przetwornic). F2/F3: MINI 1A 32 VDC (D-04).', 8, 90, 1.3)
S['LV'].text('Dodatkowa pojemnosc obciazenia: suma <= 600 uF na 5V i <= 900 uF na 3V3 (wlicz C22/C24).', 8, 92.5, 1.3)
S['MON'].text('U9A: wejscie toleruje 5 V; zasilanie 3V3. C28 na adapterze przy samym IC (nie na plycie).', 8, 100, 1.3)
S['MON'].text('VBAT: jeden przewod od klemy + akumulatora (bezpiecznik 0,5 A przy klemie), bez przewodu masy (D-01).', 8, 102.5, 1.3)
for i, name in enumerate(['STER', 'LV', 'MON'], 2):
    sh = S[name]; x, y = mm(8 + (i - 2) * 34), mm(98); sid = uid('sheet/' + name)
    W.items.append(f'(sheet (at {x} {y}) (size 76.2 15.24) (stroke (width .15) (type default)) (fill (color 0 0 0 0)) (uuid {sid}) (property "Sheetname" "{name}" (at {x} {y - 1.27} 0) (effects (font (size 1.3 1.3)) (justify left bottom))) (property "Sheetfile" "{name}.kicad_sch" (at {x} {y + 16.51} 0) (effects (font (size 1.3 1.3)) (justify left top))) (instances (project "P02" (path {q("/" + uid("WEJ"))} (page "{i}")))))')
    old = sh.path; sh.path = '/' + uid('WEJ') + '/' + sid; sh.items = [t.replace(q(old), q(sh.path)) for t in sh.items]
for sh in S.values(): sh.finish(); sh.save()
write_tables()
(P / 'verification/sheet-parts.json').write_text(json.dumps({n: list(s.parts) for n, s in S.items()}, indent=2) + '\n')
placed = {k.split(':')[0] for s in S.values() for k in s.parts}
missing = sorted(set(PARTS) - placed); assert not missing, missing
print(f'{len(PARTS)} parts; sheets: ' + ', '.join(f'{n} ({len(s.parts)})' for n, s in S.items()))
