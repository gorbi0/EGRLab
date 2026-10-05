"""P04 R3: part heights above the board (mm) for the S1 limit above level 6 (16.5 mm top, user decision 5.10; 1.5 mm bottom;
SPECYFIKACJA-FORMATU-S1.md section 4). Values with their source; 'szacunek' = estimate to confirm at the 1:1 fit (docs/MECHANIKA.md).
Used by verify_pcb.py and make_pdf.py. (Structure from P05 R3 heights.py.)
"""
import os as _os
HEIGHTS = {  # footprint id or reference -> (height mm, source)
    'Connector_IDC:IDC-Header_2x08_P2.54mm_Horizontal': (9.2, 'typowe gniazdo IDC kątowe obudowane: 8,9-9,2 mm'),
    'Connector_IDC:IDC-Header_2x10_P2.54mm_Horizontal': (9.2, 'typowe gniazdo IDC kątowe obudowane: 8,9-9,2 mm'),
    'Connector_PinHeader_2.54mm:PinHeader_1x13_P2.54mm_Horizontal': (2.6, 'listwa kątowa 2,54 mm: korpus 2,54 mm'),
    'Connector_PinHeader_2.54mm:PinHeader_1x07_P2.54mm_Horizontal': (2.6, 'listwa kątowa 2,54 mm: korpus 2,54 mm'),
    'Package_DIP:DIP-14_W7.62mm': (8.5, 'szacunek: DIP-14 w podstawce (MECHANIKA: ok. 8 mm); MS-001 max 5,08 mm + podstawka ok. 3,5 mm'),
    'Package_DIP:DIP-16_W7.62mm': (8.5, 'szacunek: DIP-16 w podstawce, jak DIP-14'),
    'Package_SO:SOIC-14_3.9x8.7mm_P1.27mm': (1.75, 'JEDEC MS-012 max (od góry, lutowany wprost)'),
    'Package_TO_SOT_THT:TO-92_Inline_Wide': (7.0, 'szacunek: TO-92 korpus 4,6-5,3 mm + ok. 1,5 mm wyprowadzeń nad płytką'),
    'P04:C_WIMA_MKS2_1u100V_L7.2_W7.2_P5': (13.0, 'C1 WIMA MKS2 1 uF / 100 V: ok. 13 mm (MECHANIKA; decyzja użytkownika 5.10: w limicie 16,5 mm)'),
    'Capacitor_THT:C_Rect_L7.2mm_W5.0mm_P5.00mm': (10.0, 'C2 MKS2 1 uF / 63 V: H 10 mm (MECHANIKA)'),
    'Capacitor_THT:CP_Radial_D5.0mm_P2.00mm': (11.5, 'C3 EEU-EB1J100SH: D5 x 11 mm + ok. 0,5 mm odstępu'),
    'Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm': (7.0, 'szacunek: C18 dysk 1 nF (C320C102J1G5TA), ok. 5 mm + ok. 2 mm wyprowadzeń'),
    'LED_THT:LED_D3.0mm': (6.5, 'szacunek: LED 3 mm, korpus 5,3 mm + ok. 1 mm wyprowadzeń'),
    'Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder': (0.7, 'RC1206: 0,55 +/- 0,1 mm'),
    'Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder': (1.8, 'max z kart 1206 X7R (do 1,6 +/- 0,2 mm); od góry'),
}


def height(ref, parts):
    if ref in HEIGHTS:
        return HEIGHTS[ref][0]
    return HEIGHTS[parts[ref]['footprint']][0]


for _item in filter(None, _os.environ.get('EGRLAB_HEIGHT_OVERRIDE', '').split(',')):   # negative controls only: 'REF=mm,...'
    _r, _h = _item.split('='); HEIGHTS[_r] = (float(_h), 'override (negative control)')
