"""P06 R2: part heights above the board (mm) for the S1 level-4 limit (16.5 mm top, 1.5 mm bottom; SPECYFIKACJA-FORMATU-S1.md §4).
Values with their source; 'szacunek' = estimate to confirm at the 1:1 fit. Used by verify_pcb.py and make_pdf.py.
(Structure from P05 R3 heights.py.) Bottom-side capacitors are listed by reference: their BOM note asks for <= 1.5 mm.
"""
import os as _os
HEIGHTS = {  # footprint id or reference -> (height mm, source)
    'Connector_IDC:IDC-Header_2x08_P2.54mm_Horizontal': (9.2, 'typowe gniazdo IDC kątowe obudowane: 8,9-9,2 mm'),
    'Connector_PinHeader_2.54mm:PinHeader_1x07_P2.54mm_Horizontal': (2.6, 'listwa kątowa 2,54 mm: korpus 2,54 mm'),
    'Connector_PinHeader_2.54mm:PinHeader_1x13_P2.54mm_Horizontal': (2.6, 'listwa kątowa 2,54 mm: korpus 2,54 mm'),
    'P06:PTH_ISERIES': (6.0, 'szacunek: przewody 2,5 mm² lutowane do otworów, łuk i opaska na kotwach (jak P05 TAPS)'),
    'P06:PTH_BYPASS': (6.0, 'szacunek: przewody 2,5 mm² lutowane do otworów, opaska na kotwach'),
    'P06:PTH_SWSTATUS': (4.0, 'szacunek: przewody AWG22 lutowane do otworów, opaska na kotwach'),
    'P06:R_PR02_P17.78': (9.0, 'PR02 leżący 3-5 mm nad laminatem (README), korpus D 3,9 mm: ok. 9 mm'),
    'P06:R_Shunt_Vishay_WSK2512_T1.19mm_SenseE1.70': (0.9, 'Vishay WSK2512 (karta 30108): H 0,635 +/- 0,254 mm'),
    'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm': (1.75, 'JEDEC MS-012 max'),
    'Package_SO:SOIC-14_3.9x8.7mm_P1.27mm': (1.75, 'JEDEC MS-012 max'),
    'Package_DIP:DIP-8_W7.62mm': (8.0, 'README: w posiadanej podstawce Kamami 1207058 ok. 8 mm'),
    'Package_DIP:DIP-14_W7.62mm': (8.0, 'szacunek: SN74HC08N w podstawce Kamami 648, jak DIP8 ok. 8 mm'),
    'Package_TO_SOT_THT:TO-92_Inline_Wide': (7.0, 'szacunek: TO-92 korpus 4,6-5,3 mm + ok. 1,5 mm wyprowadzeń nad płytką'),
    'Resistor_THT:R_Axial_DIN0411_L9.9mm_D3.6mm_P15.24mm_Horizontal': (4.0, 'KNP01 1 W leżący: średnica 3,6 mm + ok. 0,4 mm odstępu'),
    'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P5.08mm_Vertical': (9.0, 'szacunek: MF0207 na stojąco, korpus 6,3 mm + ok. 2 mm wyprowadzeń'),
    'Capacitor_THT:CP_Radial_D6.3mm_P2.50mm': (11.7, 'EEUFR1C221 (D6,3 x 11,2 mm) + ok. 0,5 mm odstępu'),
    'Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal': (3.0, '1N5819 DO-41 leżąca: średnica max 2,7 mm + ok. 0,3 mm'),
    'Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal': (2.3, 'BAT85 DO-34/35 leżąca: średnica max 2,0 mm + ok. 0,3 mm'),
    'Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder': (0.7, 'RC1206: 0,55 +/- 0,1 mm'),
    'Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder': (1.8, 'max z kart GRM31 (1-4,7 uF: do 1,6 +/- 0,2 mm); od góry'),
    # bottom side (S1-2: <= 1.5 mm): 100 nF 1206 with the BOM thickness note (GRM31M class, 1.15 +/- 0.1 mm)
    'C8': (1.25, 'od spodu: 100 nF 1206 o grubości <= 1,5 mm (uwaga w BOM; np. GRM31MR71H104KA01, 1,15 +/- 0,1 mm)'),
}


def height(ref, parts):
    if ref in HEIGHTS:
        return HEIGHTS[ref][0]
    return HEIGHTS[parts[ref]['footprint']][0]


for _item in filter(None, _os.environ.get('EGRLAB_HEIGHT_OVERRIDE', '').split(',')):   # negative controls only: 'REF=mm,...'
    _r, _h = _item.split('='); HEIGHTS[_r] = (float(_h), 'override (negative control)')
