"""P03 R6: part heights above the board (mm) for the S1 level-2 limit (16.5 mm, SPECYFIKACJA-FORMATU-S1.md §4).
Values with their source; 'szacunek' = estimate to confirm at the 1:1 fit. Used by verify_pcb.py and make_pdf.py.
"""
HEIGHTS = {  # footprint id or reference -> (height mm, source)
    'M1': (13.8, 'szacunek: listwa żeńska 8,5 mm + płytka Waveshare 1,6 + moduł WROOM / USB-C 3,7; README R6: potwierdzić na module'),
    'SD1': (12.2, 'szacunek: listwa żeńska 8,5 + płytka Adafruit 1,6 + gniazdo microSD 2,1'),
    'Package_DIP:DIP-28_W7.62mm': (8.0, 'szacunek: podstawka DIP ok. 4 mm + układ DIP 4 mm (karta MCP23017: max 4,95 mm nad płaszczyzną osadzenia)'),
    'Package_DIP:DIP-16_W7.62mm': (8.0, 'szacunek: podstawka DIP ok. 4 mm + układ DIP 4 mm (karta SN74HC139N: max 5,08 mm)'),
    'Connector_IDC:IDC-Header_2x10_P2.54mm_Horizontal': (9.2, 'typowe gniazdo IDC kątowe obudowane 2x10: 8,9-9,2 mm'),
    'Connector_PinHeader_2.54mm:PinHeader_1x13_P2.54mm_Horizontal': (2.6, 'listwa kątowa 2,54 mm: korpus 2,54 mm'),
    'LED_THT:LED_D3.0mm': (6.0, 'dioda 3 mm: 5,3 mm korpus + ok. 0,7 mm nad płytką'),
    'Package_SO:SOIC-14_3.9x8.7mm_P1.27mm': (1.75, 'JEDEC MS-012 max'),
    'Package_TO_SOT_SMD:SOT-23': (1.45, 'max karty (AO3401A 1,45 mm)'),
    'Package_TO_SOT_SMD:SOT-23-5': (1.45, 'max karty DBV'),
    'Package_TO_SOT_SMD:SOT-23-6': (1.45, 'max karty (LTC4412 S6 1,0 mm, TPS3808 DBV 1,45 mm)'),
    'Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder': (0.7, 'RC1206: 0,55 +/- 0,1 mm'),
    'Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder': (1.8, 'max z kart GRM31 (10 uF: 1,6 +/- 0,2 mm)'),
    'P03:TestPad_1': (0.0, 'pole na płytce'),
}


def height(ref, parts):
    if ref in HEIGHTS:
        return HEIGHTS[ref][0]
    return HEIGHTS[parts[ref]['footprint']][0]


import os as _os
for _item in filter(None, _os.environ.get('P03_HEIGHT_OVERRIDE', '').split(',')):   # negative controls only: 'REF=mm,...'
    _r, _h = _item.split('='); HEIGHTS[_r] = (float(_h), 'override (negative control)')
