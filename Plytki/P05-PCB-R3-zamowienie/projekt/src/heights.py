"""P05 R3: part heights above the board (mm) for the S1 level-3 limit (16.5 mm top, 1.5 mm bottom; SPECYFIKACJA-FORMATU-S1.md §4).
Values with their source; 'szacunek' = estimate to confirm at the 1:1 fit. Used by verify_pcb.py and make_pdf.py.
(Structure from P09 R2 / P10 R2 heights.py.) Bottom-side capacitors are listed by reference: their BOM note asks for <= 1.5 mm.
"""
import os as _os
HEIGHTS = {  # footprint id or reference -> (height mm, source)
    'Connector_IDC:IDC-Header_2x05_P2.54mm_Horizontal': (9.2, 'typowe gniazdo IDC kątowe obudowane: 8,9-9,2 mm'),
    'Connector_IDC:IDC-Header_2x10_P2.54mm_Horizontal': (9.2, 'typowe gniazdo IDC kątowe obudowane: 8,9-9,2 mm'),
    'Connector_PinHeader_2.54mm:PinHeader_1x13_P2.54mm_Horizontal': (2.6, 'listwa kątowa 2,54 mm: korpus 2,54 mm'),
    'P05:PTH_TAPS_12': (6.0, 'szacunek: przewody TAPS lutowane do otworów, łuk i opaska na kotwach (jak P10 OBD)'),
    'P05:PTH_AUX_2': (6.0, 'szacunek: koncentryk AUX lutowany do otworów, opaska na kotwach'),
    'P05:ESW_100DP_M6': (11.43, 'E-Switch 100, rysunek M6 (reference/E-Switch-100-series.pdf, s. 11): korpus 11,43 mm nad płytką'),
    'P05:TestPad_1': (0.0, 'pole testowe na płytce (bez elementu)'),
    'Package_QFP:LQFP-64_10x10mm_P0.5mm': (1.6, 'JEDEC MS-026 (LQFP 1,4 mm): max 1,6 mm'),
    'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm': (1.75, 'JEDEC MS-012 max'),
    'Package_SO:SOIC-14_3.9x8.7mm_P1.27mm': (1.75, 'JEDEC MS-012 max'),
    'Package_SO:VSSOP-8_3x3mm_P0.65mm': (1.1, 'TI DGK (VSSOP-8): max 1,1 mm'),
    'Package_DIP:DIP-14_W7.62mm': (5.08, 'JEDEC MS-001 (SN74HC08N): max 5,08 mm nad płytką'),
    'Package_DIP:DIP-18_W7.62mm': (5.08, 'TBD62083APG (DIP18): max ok. 5 mm; przyjęte jak MS-001'),
    'Package_TO_SOT_THT:TO-92_Inline_Wide': (7.0, 'szacunek: TO-92 korpus 4,6-5,3 mm + ok. 1,5 mm wyprowadzeń nad płytką'),
    'Relay_THT:Relay_DPDT_Omron_G6K-2P-Y': (5.2, 'Omron G6K-2P (K106-E1): 10,0 x 6,5 x 5,2 mm'),
    'Resistor_THT:R_Axial_DIN0411_L9.9mm_D3.6mm_P15.24mm_Horizontal': (4.0, 'KNP01 1 W leżący: średnica 3,6 mm + ok. 0,4 mm odstępu'),
    'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P5.08mm_Vertical': (9.0, 'szacunek: MF0207 na stojąco, korpus 6,3 mm + ok. 2 mm wyprowadzeń'),
    'Capacitor_THT:CP_Radial_D6.3mm_P2.50mm': (11.7, 'EEUFR1C221 (D6,3 x 11,2 mm) + ok. 0,5 mm odstępu; README: ok. 11,2 mm korpusu'),
    'Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm': (7.0, 'szacunek: posiadany dysk 1 nF, 5 mm + ok. 2 mm wyprowadzeń'),
    'Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal': (2.3, '1N4148 DO-35 leżąca: średnica max 2,0 mm + ok. 0,3 mm'),
    'Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder': (0.7, 'RC1206: 0,55 +/- 0,1 mm'),
    'Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder': (1.8, 'max z kart GRM31 (1-2,2 uF: 1,6 +/- 0,2 mm); od góry'),
    'Capacitor_SMD:C_1210_3225Metric': (2.7, 'C3225X7R1E226M250AB: 2,5 +/- 0,2 mm'),
    # bottom side (S1-2: <= 1.5 mm): 100 nF / 10 nF 1206 with the BOM thickness note (GRM31M class, 1.15 +/- 0.1 mm)
    'C5': (1.25, 'od spodu: 100 nF 1206 o grubości <= 1,5 mm (uwaga w BOM; np. GRM31MR71H104KA01, 1,15 +/- 0,1 mm)'),
    'C7': (1.25, 'od spodu: jak C5'), 'C8': (1.25, 'od spodu: jak C5'), 'C11': (1.25, 'od spodu: jak C5'),
    'C26': (1.25, 'od spodu: 10 nF 1206 (typowo 0,6-0,85 mm; uwaga w BOM: <= 1,5 mm)'),
    'C25': (1.25, 'od spodu: jak C26'),
}


def height(ref, parts):
    if ref in HEIGHTS:
        return HEIGHTS[ref][0]
    return HEIGHTS[parts[ref]['footprint']][0]


for _item in filter(None, _os.environ.get('EGRLAB_HEIGHT_OVERRIDE', '').split(',')):   # negative controls only: 'REF=mm,...'
    _r, _h = _item.split('='); HEIGHTS[_r] = (float(_h), 'override (negative control)')
