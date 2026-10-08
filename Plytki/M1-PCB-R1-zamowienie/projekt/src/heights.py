"""M1-R1: part heights above the board (mm) for the enclosure design (no S1 level limit; the enclosure follows the board, user 8.10).
Values with their source; 'szacunek' = estimate to confirm at the 1:1 fit. Used by make_pdf.py. (Structure from P07 S1 heights.py.)
"""
import os as _os
HEIGHTS = {  # footprint id or reference -> (height mm, source)
    'M1:Waveshare_ESP32-S3-DEV-KIT_2x22_W22.86': (11.0, 'szacunek: listwa kołkowa 2,5 + płytka modułu 1,6 + moduł WROOM / USB-C ok. 3,5 + zapas (D-M1-12: wlutowany na kołkach)'),
    'M1:Adafruit_4682_microSD_1x09': (6.5, 'szacunek: listwa 2,5 + płytka 1,6 + gniazdo microSD ok. 2'),
    'M1:MAX31856_XU': (14.1, 'P09 R2 src/heights.py: plastik listwy 2,5 + płytka modułu 1,6 + terminal do 10 (szacunek górny)'),
    'Converter_DCDC:Converter_DCDC_TRACO_TSR2-xxxx_THT': (10.2, 'szacunek: TRACO TSR 2 SIP-3 stojący, korpus ok. 10 mm nad płytką'),
    'Fuse:Fuseholder_Blade_Mini_Keystone_3568': (16.0, 'szacunek: oprawka Keystone 3568 + wkładka MINI (ok. 11 mm wysokości wkładki)'),
    'M1:PAD_BAT': (6.0, 'szacunek: przewody 2,0 mm² lutowane, łuk i opaska na kotwach'),
    'M1:PAD_VMOTOR': (6.0, 'szacunek: jak PAD_BAT'), 'M1:PAD_P1': (6.0, 'szacunek: jak PAD_BAT'),
    'M1:PAD_SIG': (3.0, 'szacunek: przewody 0,25-0,5 mm², opaska'), 'M1:PAD_IBT': (3.0, 'szacunek: przewody 0,25 mm², opaska'),
    'M1:PAD_BTN': (2.0, 'szacunek: dwa cienkie przewody'),
    'M1:R_Shunt_Vishay_WSK2512_T1.19mm_SenseE1.70': (0.9, 'Vishay WSK2512 (karta 30108): H 0,635 +/- 0,254 mm'),
    'Package_QFP:LQFP-64_10x10mm_P0.5mm': (1.6, 'LQFP-64: max 1,6 mm'),
    'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm': (1.75, 'JEDEC MS-012 max'),
    'Package_SO:SOIC-14_3.9x8.7mm_P1.27mm': (1.75, 'JEDEC MS-012 max'),
    'Package_TO_SOT_SMD:SOT-23': (1.2, 'SOT-23: max 1,1-1,2 mm'),
    'Package_TO_SOT_SMD:SOT-23-6': (1.45, 'SOT-23-6: max 1,45 mm'),
    'Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder': (0.7, 'RC1206: 0,55 +/- 0,1 mm'),
    'Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder': (1.8, 'max z kart GRM31 (4,7-10 uF: do 1,6 +/- 0,2 mm); od góry'),
    'Capacitor_SMD:C_1210_3225Metric': (2.7, 'C3225 22 uF: max 2,5-2,7 mm'),
    'TestPoint:TestPoint_Pad_D1.5mm': (0.05, 'pole miedzi'),
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
