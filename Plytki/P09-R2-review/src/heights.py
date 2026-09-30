"""P09 R2: part heights above the board (mm) for the S1 level-3 limit (16.5 mm top, 1.5 mm bottom; SPECYFIKACJA-FORMATU-S1.md §4).
Values with their source; 'szacunek' = estimate to confirm at the 1:1 fit (docs/MODUL-KWALIFIKACJA.md step 1 measures the socket
and terminal height). Used by verify_pcb.py and make_pdf.py. (Structure from P03 R6 heights.py.)
"""
import os as _os
HEIGHTS = {  # footprint id or reference -> (height mm, source)
    'P09:MAX31856_XU_socket': (16.5, 'szacunek: gniazdo żeńskie 1x9 ok. 8,5 mm + płytka modułu ok. 1,0 mm (deklarowane 24x21x1 mm) + terminal '
                               'termopary ok. 7 mm; równo z limitem poziomu 3 — potwierdzić pomiarem (MODUL-KWALIFIKACJA krok 1)'),
    'Package_DIP:DIP-16_W7.62mm': (5.1, 'karta SN74HC139N: max 5,08 mm; U3 lutowany wprost (BOM bez podstawki)'),
    'Connector_IDC:IDC-Header_2x08_P2.54mm_Horizontal': (9.2, 'typowe gniazdo IDC kątowe obudowane: 8,9-9,2 mm'),
    'Connector_PinHeader_2.54mm:PinHeader_1x13_P2.54mm_Horizontal': (2.6, 'listwa kątowa 2,54 mm: korpus 2,54 mm'),
    'Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical': (9.0, 'szacunek: listwa prosta 8,5 mm nad płytką + zworka'),
    'Package_SO:SOIC-14_3.9x8.7mm_P1.27mm': (1.75, 'JEDEC MS-012 max'),
    'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P5.08mm_Vertical': (9.0, 'szacunek: MF0207 na stojąco, korpus 6,3 mm + ok. 2 mm wyprowadzeń'),
    'Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm': (7.0, 'szacunek: K104 radialny, dysk 5 mm + ok. 2 mm wyprowadzeń'),
    'Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder': (0.7, 'RC1206: 0,55 +/- 0,1 mm'),
    'Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder': (1.8, 'max z kart GRM31 (4,7 uF: 1,6 +/- 0,2 mm)'),
}


def height(ref, parts):
    if ref in HEIGHTS:
        return HEIGHTS[ref][0]
    return HEIGHTS[parts[ref]['footprint']][0]


for _item in filter(None, _os.environ.get('EGRLAB_HEIGHT_OVERRIDE', '').split(',')):   # negative controls only: 'REF=mm,...'
    _r, _h = _item.split('='); HEIGHTS[_r] = (float(_h), 'override (negative control)')
