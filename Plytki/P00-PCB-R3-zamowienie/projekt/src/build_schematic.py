"""P00 R3 schematic: one A3 sheet in three functional blocks (power, heartbeat, eight sources).
Local wires inside each block; every other pin gets an explicit net label (cadlib.finish).
Run with KiCad Python and KICAD_LIBRARY_ROOT pointing at share/kicad. Regenerates eda/P00.kicad_sch.
"""
from parts import *
import cadlib
S = Sheet('P00', 'Zasilanie, heartbeat, 8 zrodel 3V3/GND', 1)


def put(r, x, y, a=0, mirror=None):
    S.place(PARTS[r], x, y, a, 1, mirror)


# ---- power (units of 2.54 mm; A3 = 165 x 117) ----
# explicit text offsets (units) where the default position would sit on a pin label or a box edge
TEXT_AT = {'J10': (5, -4), 'LED10': (-2, -4), 'R1': (3, -1), 'R2': (3, -1), **{f'LED{i}': (0, -4) for i in range(1, 10)}, **{f'SW{i}': (-3, -4.5) for i in range(1, 10)}}
for r, off in TEXT_AT.items():
    PARTS[r]['text_at'] = off
put('J10', 10, 22, 0, 'y'); put('D1', 22, 22, 180); put('C4', 29, 27); put('C5', 38, 27); put('U2', 50, 22)
put('C6', 60, 27); put('R6', 60, 36); put('R5', 76, 36); put('C7', 69, 27); put('RL10', 74, 22, 90); put('LED10', 82, 22, 180)
put('TP3', 28, 15); put('TP1', 70, 15); put('TP2', 46, 40)
S.node('P00_VIN', [('J10', 1), ('D1', 2)])
S.node('P00_VIN_P', [('D1', 1), ('C4', 1), ('C5', 1), ('U2', 1)], 22)
S.node('P00_V33', [('U2', 3), ('C6', 1), ('C7', 1), ('RL10', 1)], 22)
S.node('P00_COUT_RET', [('C6', 2), ('R6', 1)])
S.node('P00_LED_PWR', [('RL10', 2), ('LED10', 2)])
# ---- heartbeat ----
PARTS['U1']['text_at'] = (5, 6)
put('R4', 104, 16); put('R1', 96, 22); put('R2', 96, 32); put('C1', 96, 42); put('U1', 120, 32); PARTS['U1'].pop('text_at')
put('C2', 112, 20, 180); put('C3', 121, 20, 180); put('R3', 134, 32, 90); put('J9', 146, 32)
put('RL9', 134, 42, 90); put('LED9', 142, 42, 180); put('SW9', 104, 52, 180)
S.node('P00_DIS', [('R1', 2), ('R2', 1)])
S.node('P00_RC', [('R2', 2), ('C1', 1)])
S.node('P00_CTRL', [('C2', 1), ('U1', 5)], 24)
S.node('P00_V33', [('C3', 1), ('U1', 8)])
S.node('P00_OSC', [('U1', 3), ('R3', 1)])
S.node('P00_HEART', [('R3', 2), ('J9', 1)])
S.node('P00_LED_HB', [('RL9', 2), ('LED9', 2)])
# ---- eight sources, two rows of four ----
for i in range(1, 9):
    x0 = 8 + 38 * ((i - 1) % 4); y0 = 70 if i <= 4 else 86
    put(f'SW{i}', x0 + 4, y0, 180); put(f'RS{i}', x0 + 14, y0, 90); put(f'J{i}', x0 + 23, y0)
    put(f'RL{i}', x0 + 14, y0 + 7, 90); put(f'LED{i}', x0 + 22, y0 + 7, 180)
    S.node(f'P00_S{i}', [(f'SW{i}', 1), (f'RS{i}', 1)])
    S.node(f'P00_OUT{i}', [(f'RS{i}', 2), (f'J{i}', 1)])
    S.node(f'P00_LED{i}', [(f'RL{i}', 2), (f'LED{i}', 2)])

S.text('P00 / 01   ZASILANIE, HEARTBEAT, 8 ZRODEL 3V3/GND (przyrzad stanowiskowy, nie wchodzi do auta)', 8, 5.2, 2)
S.box(4, 8, 84, 44, 'Zasilanie: VIN 6-15 V -> D1 (odwrotna polaryzacja) -> LM2937 3,3 V')
S.box(90, 8, 70, 52, 'Heartbeat: TLC555 ok. 102 Hz, SW9 RUN/STOP, wyjscie przez 1 k')
S.box(4, 62, 156, 37, 'Osiem zrodel: SWn 3V3/GND -> RSn 1 k -> Jn; LEDn ze wspolnego wezla przelacznika')
S.text('J10: 6..15 V; zalecane 9..12 V. TP3 = za D1. U2 VIN >= 4,75 V. R5 zapewnia >= 5 mA. C6 + R6: galaz Cout, ESR 0,01..3 ohm.', 6, 48.5, 1.1)
S.text('SW1-SW9 Wurth WS-SLTV 450301014042: pin 1 = COM (srodkowy), 2/3 = styki. Opposite side connection: suwak od strony pinu 3 = COM-2 (3V3).', 6, 102, 1.1)
S.text('Jn: 1 = wyjscie przez 1 k (nominalnie 3,3 mA do GND), 2 = GND. GND przyrzadu laczyc z GND badanej plytki. f(HB) = 1,44/((R1 + 2 R2) C1).', 6, 104.5, 1.1)
S.text('LED wskazuje zrodlo przed RSn; napiecie na odbiorniku zmierzyc pod obciazeniem. Kierunek suwaka potwierdzic omomierzem na pierwszym przelaczniku przed montazem.', 6, 107, 1.1)

flag = symbol('power', 'PWR_FLAG')
for idx, (net, px, py) in enumerate([('P00_VIN', 19, 15), ('GND', 16, 32), ('P00_VIN_P', 36, 15)], 1):
    p = {'ref': '#FLG' + str(idx), 'display': 'PWR_FLAG', 'source_ref': 'ERC_SOURCE', 'mpn': '', 'footprint': '', 'symbol': flag, 'pins': {'1': net}, 'qty': 0, 'url': ''}
    S.place(p, px, py)
cadlib.CROSS = {'GND'}  # global label: net named GND (pours and DSN use it by name)
for r in TEXT_AT:
    PARTS[r].pop('text_at')  # layout hint only; not a part property
S.finish(); S.save()
write_tables()
(P / 'eda/P00.kicad_pro').write_text('{}', encoding='utf-8')
print('Placed', len(PARTS), 'components on 1 A3 sheet')
