"""P02 R1 schematic: two A3 sheets (P02 power root, MON supervision). Functional blocks;
local wires only where they add clarity, every other pin gets an explicit net label (cadlib.finish).
Run with KiCad Python and KICAD_LIBRARY_ROOT pointing at share/kicad. Refuses nothing: regenerates eda/*.kicad_sch.
"""
from parts import *
import cadlib, collections
S = {'P02': Sheet('P02', 'Tor mocy, HOLD, przetwornice, rozdzial LV', 1), 'MON': Sheet('MON', 'Nadzor szyn, PSU_OK, HOLD_READY', 2, uid('P02'))}


def put(r, x, y, a=0, u=1):
    p = PARTS[r]; S[p['sheet']].place(p, x, y, a, u)


# Positions in 2.54 mm units, grouped by function (boxes drawn below).
for r, x, y, a in [('J1', 12, 22, 0), ('TP1', 24, 18, 0), ('J2', 12, 40, 0), ('F4', 28, 52, 90), ('J11', 44, 44, 0),
                   ('J13', 60, 22, 0), ('R17', 72, 22, 90), ('D2', 86, 22, 0), ('D1', 86, 44, 0), ('F1', 102, 22, 90),
                   ('C1', 118, 26, 0), ('C2', 128, 26, 0), ('C3', 138, 26, 0), ('R1', 148, 26, 0), ('TP3', 156, 18, 0),
                   ('C4', 102, 48, 0), ('TP2', 112, 42, 0),
                   ('F2', 20, 70, 90), ('C5', 34, 74, 0), ('U1', 50, 70, 0), ('C6', 64, 74, 0), ('TP4', 74, 66, 0),
                   ('F3', 96, 70, 90), ('C7', 110, 74, 0), ('U2', 126, 70, 0), ('C8', 140, 74, 0), ('TP5', 150, 66, 0),
                   ('TP6', 150, 88, 0)]:
    put(r, x, y, a)
for i in range(8):
    put(f'J{3 + i}', 12 + 16 * i, 98)
for r, x, y, a, u in [('U4', 14, 22, 0, 1), ('R3', 28, 20, 0, 1), ('C10', 36, 24, 0, 1),
                      ('U5', 56, 22, 0, 1), ('U5', 74, 22, 0, 5), ('C11', 84, 24, 0, 1),
                      ('U3', 100, 22, 0, 1), ('R2', 114, 20, 0, 1), ('C9', 122, 24, 0, 1),
                      ('U6', 60, 44, 0, 1), ('U6', 140, 22, 0, 5), ('C12', 150, 24, 0, 1), ('R4', 80, 46, 0, 1),
                      ('TP7', 96, 40, 0, 1), ('J12', 150, 46, 0, 1),
                      ('TP9', 22, 62, 0, 1), ('R5', 14, 66, 0, 1), ('U8', 14, 80, 0, 1),
                      ('R6', 34, 70, 0, 1), ('R7', 34, 84, 0, 1), ('C14', 42, 84, 0, 1), ('R8', 50, 66, 90, 1),
                      ('U7', 64, 76, 0, 1), ('R12', 78, 66, 0, 1), ('U7', 90, 64, 0, 3), ('C13', 100, 66, 0, 1),
                      ('R9', 34, 94, 0, 1), ('R10', 34, 108, 0, 1), ('C15', 42, 108, 0, 1), ('R11', 50, 90, 90, 1),
                      ('U7', 64, 98, 0, 2), ('R13', 78, 88, 0, 1),
                      ('U6', 104, 82, 0, 2), ('U6', 124, 82, 0, 3), ('R14', 140, 80, 90, 1), ('TP8', 150, 76, 0, 1),
                      ('R15', 132, 92, 0, 1), ('R16', 142, 92, 0, 1), ('LED1', 150, 84, 90, 1),
                      ('U6', 70, 108, 0, 4), ('U5', 84, 108, 0, 2), ('U5', 98, 108, 0, 3), ('U5', 112, 108, 0, 4), ('TP10', 120, 66, 0, 1)]:
    S['MON'].place(PARTS[r], x, y, a, u)

# Nets crossing sheets become global labels.
ns = collections.defaultdict(set)
for name, s in S.items():
    for p, pins in s.parts.values():
        for n in pins:
            ns[p['pins'][n]].add(name)
cadlib.CROSS = {n for n, v in ns.items() if len(v) > 1 and n != 'NC'}

# Boxes and notes.
P0, M = S['P02'], S['MON']
P0.text('P02 / 01   TOR MOCY, HOLD, PRZETWORNICE, ROZDZIAL LV', 8, 5, 2)
P0.box(6, 10, 48, 50, 'Wejscie SUPPLY, VMOTOR, VSENSE')
P0.box(56, 10, 104, 50, 'Rezerwa HOLD (C1): D_OR, ladowanie, bank 3 x 22 mF')
P0.box(6, 62, 154, 24, 'Przetwornice z VLOG_RES')
P0.box(6, 90, 132, 16, 'Rozdzial LV03-LV10: 1=5V_SYS 2=GND 3=3V3_IO 4=GND')
P0.text('J1: wiazka H_SUPPLY 2 x 2,5 mm2 do P01 J6 (1=VPROT 2=GND 3=NC). J2 VMOTOR: VPROT bez buforowania, do 5 A.', 8, 118, 1.1)
P0.text('R17 = R_CHARGE HSA2547RJ POZA PLYTKA (osobna blacha), przewody do J13. D1: anody ODDZIELNE, K = VLOG_RES.', 58, 58, 1.1)
P0.text('Bank HOLD_STORE: energia do >40 J przy 32 V. Nie zwierac zaciskow; rozladowanie serwisowe 100R/10W.', 58, 60.5, 1.1)
P0.text('F2/F3 zasilane z VLOG_RES (nie z VPROT). Bank nie jest widziany bezposrednio przez P01 (limit 220 uF).', 8, 87.5, 1.1)
M.text('P02 / 02   NADZOR SZYN, PSU_OK, HOLD_READY', 8, 5, 2)
M.box(6, 10, 154, 44, 'PSU_OK (v6.1): MCP120-300 na 3V3_IO, MCP120-450 na 5V_SYS przez 74LVC125A (Ioff) -> 74HC08A')
M.box(6, 58, 110, 55, 'HOLD_READY (R1): bank >=9,5 V i VPROT >=11,6 V (LM2903, TL431) i PSU_OK -> LED, TP, PSUOK pin 3')
M.box(118, 58, 42, 42, 'Wyjscie HOLD_READY: U6B/U6C, LED1, TP8, J12.3')
M.text('Progi: bank 9,50 V w gore / 9,08 V w dol; VPROT 11,60 / 11,07 V. Kwalifikacja 15 s stabilnego VPROT: firmware CORE.', 8, 114.5, 1.1)
M.text('J12 PSUOK: 1=PSU_OK 2=GND 3=HOLD_READY (rezerwa, na P04 NC) 4=NC 5=klucz 6=NC.', 108, 56, 1.05)

# Local wires inside functional blocks (labels carry everything else).
P0.node('HOLD_STORE', [('C1', 1), ('C2', 1), ('C3', 1), ('R1', 1)], 18)
P0.node('GND', [('C1', 2), ('C2', 2), ('C3', 2), ('R1', 2)], 34)

# Hierarchical sheet MON on the root; cross-sheet nets are global labels.
x, y = mm(118), mm(4); shid = uid('sheet/MON')
P0.items.append(f'(sheet (at {x} {y}) (size 76.2 12.7) (fields_autoplaced yes) (stroke (width 0.15) (type default)) (fill (color 0 0 0 0)) (uuid {shid}) (property "Sheetname" "MON" (at {x} {y - 1.27} 0) (effects (font (size 1 1)) (justify left bottom))) (property "Sheetfile" "MON.kicad_sch" (at {x} {y + 13.97} 0) (effects (font (size 1 1)) (justify left top))) (instances (project "P02" (path {q("/" + uid("P02"))} (page "2")))))')
old = M.path; new = '/' + uid('P02') + '/' + shid
M.items = [t.replace(q(old), q(new)) for t in M.items]; M.path = new

flag = symbol('power', 'PWR_FLAG')
for idx, (net, px, py) in enumerate([('VPROT', 18, 14), ('GND', 18, 30), ('P02_VIN_DC5', 28, 64), ('P02_VIN_DC33', 104, 64)], 1):
    p = {'ref': '#FLG' + str(idx), 'display': 'PWR_FLAG', 'source_ref': 'ERC_SOURCE', 'mpn': '', 'footprint': '', 'symbol': flag, 'pins': {'1': net}, 'qty': 0, 'url': ''}
    P0.place(p, px, py)
for s in S.values():
    s.finish(); s.save()
write_tables()
(P / 'eda/P02.kicad_pro').write_text('{}', encoding='utf-8')
(P / 'verification/sheet-parts.json').write_text(json.dumps({n: [k for k in s.parts] for n, s in S.items()}, indent=2), encoding='utf-8')
print('Placed', len(PARTS), 'components,', sum(len(s.parts) for s in S.values()), 'symbol units; 2 A3 sheets')
