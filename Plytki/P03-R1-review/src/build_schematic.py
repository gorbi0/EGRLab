"""P03 R1 schematic: two A3 sheets (P03 = CORE: MCU board, SD, expander, decoder, supervisor; IO = buffers and
harness connectors). Every pin carries an explicit net label (cadlib.finish); nets used on both sheets are global.
Run with KiCad Python and KICAD_LIBRARY_ROOT pointing at share/kicad. Regenerates eda/*.kicad_sch.
"""
from parts import *
import cadlib, collections
S = {'P03': Sheet('P03', 'CORE: ESP32-S3, SD, MCP23017, dekoder CS, nadzor', 1), 'IO': Sheet('IO', 'Bufory 74LVC125 i zlacza wiazek', 2, uid('P03'))}


def put(r, x, y, a=0, u=1, mirror=None):
    p = PARTS[r]; S[p['sheet']].place(p, x, y, a, u, mirror)


# ---- sheet P03 (units of 2.54 mm; A3 = 165 x 117) ----
put('M1', 38, 56); put('SD1', 88, 26); put('J10', 12, 20, 0)
put('U1', 94, 70)
for u, (x, y) in enumerate([(132, 18), (132, 36), (150, 30)], 1):
    put('U2', x, y, 0, u)
put('U3', 134, 70); put('C3', 146, 70); put('R13', 124, 62)
put('C1', 156, 30); put('R1', 118, 20); put('C2', 112, 84)
put('R9', 74, 62); put('R10', 78, 62); put('R11', 104, 22); put('R12', 70, 82, 90)
put('R5', 150, 78); put('C4', 158, 84); put('R4', 136, 88, 90); put('LED1', 146, 88, 180); put('R14', 70, 96, 90)
put('TP1', 24, 12); put('TP2', 24, 30); put('TP3', 30, 12); put('TP4', 30, 30); put('TP5', 124, 54)
# ---- sheet IO: inputs 2x2 grid left, outputs right/middle, DAQ group right, harness row at the bottom ----
for ref, x, y0, cap in [('U11', 12, 14, 'C5'), ('U12', 50, 14, 'C6'), ('U13', 12, 58, 'C7'), ('U14', 50, 58, 'C8'),
                        ('U21', 92, 14, 'C9'), ('U22', 130, 14, 'C10'), ('U23', 92, 58, 'C11')]:
    for u in range(1, 5):
        put(ref, x, y0 + 9 * (u - 1), 0, u)
    put(ref, x + 16, y0 + 2, 0, 5); put(cap, x + 26, y0 + 2)
put('J1', 146, 64); put('J2', 146, 82); put('J3', 146, 94)
for ref, x in [('J4', 18), ('J5', 38), ('J6', 56), ('J7', 74), ('J8', 92), ('J9', 106)]:
    put(ref, x, 106)
for ref, x, y in [('R2', 106, 76), ('R7', 112, 76), ('R3', 118, 76), ('R8', 106, 88), ('R6', 112, 88), ('TP6', 118, 88)]:
    put(ref, x, y)

# nets crossing sheets become global labels
ns = collections.defaultdict(set)
for name, s in S.items():
    for p, pins in s.parts.values():
        for n in pins:
            ns[p['pins'][n]].add(name)
cadlib.CROSS = {n for n, v in ns.items() if len(v) > 1 and n != 'NC'} | {'GND'}

P0, IO = S['P03'], S['IO']
P0.text('P03 / 01   CORE: ESP32-S3 (Waveshare N32R16V), microSD, MCP23017 0x20, 74HC139, TPS3808', 8, 5.2, 2)
P0.box(4, 8, 58, 104, 'M1 na listwach 2x22 (22,86 mm), zasilanie LV03')
P0.box(64, 8, 50, 30, 'microSD: Adafruit 4682 (3 V), SPI3 za buforem')
P0.box(116, 8, 46, 38, 'Dekoder CS pradu: 74HC139')
P0.box(64, 48, 98, 50, 'MCP23017 (I2C lokalnie), nadzor 3V3_CORE, LED, MARK, SCOPE')
P0.text('GPIO47/48 nieuzywane (1,8 V w N32R16V). RGB LED na GPIO38 odlaczyc na plytce Waveshare. 3V3_CORE nie laczyc z 3V3_IO.', 6, 113.5, 1.1)
IO.text('P03 / 02   BUFORY 74LVC125 (Nexperia, Ioff) I ZLACZA WIAZEK', 8, 5.2, 2)
IO.box(4, 8, 80, 88, 'Wejscia do CORE: U11-U14')
IO.box(86, 8, 76, 88, 'Wyjscia z CORE: U21-U23; odbiorcze pull-downy')
IO.box(124, 56, 38, 42, 'DAQ (B2B katowe do P05), ILOG, ITEST')
IO.box(4, 98, 112, 14, 'Zlacza wiazek: SAFE, DIR, SFAULT, TEMP, CAN, PANELCORE')
IO.text('Klucze v6.1: SAFE/DIR/TEMP/CAN pin 4, ILOG/ITEST pin 2, SFAULT pin 3, DAQ pozycja 2 zaslepiona. CAN: 2x3 zamiast 2x2 (decyzja 25.09).', 6, 113.5, 1.1)

x, y = mm(10), mm(96); shid = uid('sheet/IO')
P0.items.append(f'(sheet (at {x} {y}) (size 40.64 7.62) (fields_autoplaced yes) (stroke (width 0.15) (type default)) (fill (color 0 0 0 0)) (uuid {shid}) (property "Sheetname" "IO" (at {x} {y - 1.27} 0) (effects (font (size 1 1)) (justify left bottom))) (property "Sheetfile" "IO.kicad_sch" (at {x} {y + 8.89} 0) (effects (font (size 1 1)) (justify left top))) (instances (project "P03" (path {q("/" + uid("P03"))} (page "2")))))')
old = IO.path; new = '/' + uid('P03') + '/' + shid
IO.items = [t.replace(q(old), q(new)) for t in IO.items]; IO.path = new
flag = symbol('power', 'PWR_FLAG')
for idx, (net, px, py) in enumerate([('5V_SYS', 18, 12), ('GND', 18, 30), ('3V3_IO', 36, 12)], 1):
    p = {'ref': '#FLG' + str(idx), 'display': 'PWR_FLAG', 'source_ref': 'ERC_SOURCE', 'mpn': '', 'footprint': '', 'symbol': flag, 'pins': {'1': net}, 'qty': 0, 'url': ''}
    P0.place(p, px, py)
for s in S.values():
    s.finish(); s.save()
write_tables()
(P / 'eda/P03.kicad_pro').write_text('{}', encoding='utf-8')
print('Placed', len(PARTS), 'components,', sum(len(s.parts) for s in S.values()), 'symbol units; 2 A3 sheets')
