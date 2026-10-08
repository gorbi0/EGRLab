"""P07 S1: part heights above the board (mm) for the S1 level-5 limit (16.5 mm top, 1.5 mm bottom; SPECYFIKACJA-FORMATU-S1.md §4).
Values with their source; 'szacunek' = estimate to confirm at the 1:1 fit. Used by verify_pcb.py and make_pdf.py.
(Structure from P06 R2 heights.py.) Bottom-side capacitors: 100 nF / 1 uF / 10 nF / 1 nF 1206 with the BOM thickness note (<= 1.5 mm).
"""
import os as _os
HEIGHTS = {  # footprint id or reference -> (height mm, source)
    'Connector_IDC:IDC-Header_2x08_P2.54mm_Horizontal': (9.2, 'typowe gniazdo IDC kątowe obudowane: 8,9-9,2 mm'),
    'Connector_IDC:IDC-Header_2x04_P2.54mm_Horizontal': (9.2, 'IDC 2x4 kątowe obudowane (box header): jak 2x8, 8,9-9,2 mm'),
    'Connector_PinHeader_2.54mm:PinHeader_1x13_P2.54mm_Horizontal': (2.6, 'listwa kątowa 2,54 mm: korpus 2,54 mm'),
    'Connector_PinHeader_2.54mm:PinHeader_1x12_P2.54mm_Horizontal': (2.6, 'listwa kątowa 2,54 mm: korpus 2,54 mm (J_SV2 12 kołków od 6.10)'),
    'P07:PTH_VMOTOR': (6.0, 'szacunek: przewody 2,0 mm² lutowane do otworów, łuk i opaska na kotwach (jak P06 R2)'),
    'P07:PTH_MODPWR': (6.0, 'szacunek: przewody 2,0 mm² lutowane do otworów, opaska na kotwach'),
    'P07:PTH_MODOUT': (6.0, 'szacunek: przewody 2,0 mm² lutowane do otworów, opaska na kotwach'),
    'P07:PTH_TEST': (6.0, 'szacunek: przewody 2,0 mm² lutowane do otworów, opaska na kotwach'),
    'Relay_THT:Relay_SPDT_Omron_G2RL-1-E': (15.7, 'Omron G2RL-1-E: wysokość korpusu 15,7 mm (karta, README)'),
    'Capacitor_THT:CP_Radial_D8.0mm_P3.50mm': (13.5, 'EEU-FR1V221 D8 x 11,5 mm + ok. 2 mm (README: stojący)'),
    'Diode_SMD:D_SMC': (2.62, 'DO-214AB (SMC): max 2,62 mm'),
    'P07:R_Shunt_Vishay_WSK2512_T1.19mm_SenseE1.70': (0.9, 'Vishay WSK2512 (karta 30108): H 0,635 +/- 0,254 mm'),
    'Resistor_SMD:R_2512_6332Metric_Pad1.40x3.35mm_HandSolder': (0.7, 'RC2512: 0,55 +/- 0,1 mm'),
    'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm': (1.75, 'JEDEC MS-012 max'),
    'Package_SO:SOIC-14_3.9x8.7mm_P1.27mm': (1.75, 'JEDEC MS-012 max'),
    'Package_DIP:DIP-8_W7.62mm': (8.0, 'README P06 R2: w podstawce ok. 8 mm'),
    'Package_TO_SOT_THT:TO-92_Inline_Wide': (7.0, 'szacunek: TO-92 korpus 4,6-5,3 mm + ok. 1,5 mm wyprowadzeń nad płytką'),
    'Package_TO_SOT_SMD:SOT-23': (1.2, 'SOT-23: max 1,1-1,2 mm'),
    'Package_TO_SOT_SMD:SOT-23-6': (1.45, 'SOT-23-6 / SC-74: max 1,45 mm'),
    'Diode_SMD:D_SOD-123': (1.35, 'SOD-123: max 1,35 mm'),
    'Fuse:Fuse_1206_3216Metric_Pad1.42x1.75mm_HandSolder': (0.85, 'MF-NSMF012: max 0,85 mm'),
    'Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder': (0.7, 'RC1206: 0,55 +/- 0,1 mm'),
    'Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder': (1.8, 'max z kart GRM31 (4,7-10 uF: do 1,6 +/- 0,2 mm); od góry'),
}
# bottom side: capacitors <= 1 uF 1206 with the BOM thickness note (GRM31M class 1.15 +/- 0.1 mm; C0G 0.6-1.15 mm)
BOTTOM_C = (1.25, 'od spodu: kondensator 1206 <= 1 uF o grubości <= 1,5 mm (uwaga w BOM; np. GRM31M, 1,15 +/- 0,1 mm)')


def height(ref, parts):
    if ref in HEIGHTS:
        return HEIGHTS[ref][0]
    return HEIGHTS[parts[ref]['footprint']][0]


import json as _json, pathlib as _pl
_pl_ = _pl.Path(__file__).resolve().parent / 'placement.json'
for _r, _v in (_json.loads(_pl_.read_text()).items() if _pl_.exists() else []):   # bottom-side capacitors from the placement
    if _r.startswith('C') and len(_v) > 3 and _v[3] == 'B':
        HEIGHTS[_r] = BOTTOM_C


for _item in filter(None, _os.environ.get('EGRLAB_HEIGHT_OVERRIDE', '').split(',')):   # negative controls only: 'REF=mm,...'
    _r, _h = _item.split('='); HEIGHTS[_r] = (float(_h), 'override (negative control)')
