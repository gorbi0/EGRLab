"""P08 R2: part heights above the board (mm) for the S1 level-5 limit (16.5 mm top, 1.5 mm bottom; SPECYFIKACJA-FORMATU-S1.md §4).
Values with their source; 'szacunek' = estimate to confirm at the 1:1 fit (docs/ODBIOR.md M01). Used by verify_pcb.py and make_pdf.py.
(Structure from P09 R2 / P10 R2 heights.py.)
"""
import os as _os
HEIGHTS = {  # footprint id or reference -> (height mm, source)
    'P08:PTH_TSENSOR_2': (6.0, 'szacunek: para 2×AWG22 lutowana do otworów, mały łuk i opaska na kotwie (łeb ok. 5 mm), jak P10 OBD'),
    'P08:G6K_2P_Y_verified': (5.2, 'Omron G6K karta s. 1: 5,2 (H) × 6,5 × 10 mm'),
    'Package_DIP:DIP-18_W7.62mm': (5.33, 'JEDEC MS-001 A max 5,33 mm (TBD62083APG DIP18, lutowany wprost)'),
    'Package_DIP:DIP-14_W7.62mm': (8.5, 'szacunek: podstawka DIP14 (Kamami 648) ok. 4,3 mm + SN74HC08N A max 5,08 mm, zagłębienie ok. 1 mm'),
    'Package_TO_SOT_THT:TO-92_Inline_Wide': (8.0, 'szacunek: korpus TO-92 ok. 5,2 mm + ok. 3 mm wyprowadzeń nad płytką'),
    'Package_TO_SOT_SMD:SOT-23-6': (1.45, 'TPS2553 DBV: max 1,45 mm'),
    'Package_SO:SOIC-14_3.9x8.7mm_P1.27mm': (1.75, 'JEDEC MS-012 max'),
    'Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal': (2.0, 'DO-35 leżąca: średnica korpusu max 2,0 mm'),
    'Capacitor_THT:CP_Radial_D5.0mm_P2.00mm': (12.5, 'szacunek: EEUFR1E220 5 × 11 mm + ok. 1,5 mm wyprowadzeń / koszulki'),
    'Connector_IDC:IDC-Header_2x08_P2.54mm_Horizontal': (9.2, 'typowe gniazdo IDC kątowe obudowane: 8,9-9,2 mm'),
    'Connector_PinHeader_2.54mm:PinHeader_1x13_P2.54mm_Horizontal': (2.6, 'listwa kątowa 2,54 mm: korpus 2,54 mm'),
    'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P5.08mm_Vertical': (9.0, 'szacunek: MF0207 na stojąco, korpus 6,3 mm + ok. 2 mm wyprowadzeń'),
    'Resistor_THT:R_Axial_DIN0204_L3.6mm_D1.6mm_P2.54mm_Vertical': (6.0, 'szacunek: MF0204 na stojąco, korpus 3,6 mm + ok. 2 mm wyprowadzeń'),
    'Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder': (0.7, 'RC1206: 0,55 +/- 0,1 mm'),
    'Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder': (1.8, 'max z kart GRM31 (1 uF / 4,7 uF: do 1,6 +/- 0,2 mm); tylko od góry'),
}


def height(ref, parts):
    if ref in HEIGHTS:
        return HEIGHTS[ref][0]
    return HEIGHTS[parts[ref]['footprint']][0]


for _item in filter(None, _os.environ.get('EGRLAB_HEIGHT_OVERRIDE', '').split(',')):   # negative controls only: 'REF=mm,...'
    _r, _h = _item.split('='); HEIGHTS[_r] = (float(_h), 'override (negative control)')
