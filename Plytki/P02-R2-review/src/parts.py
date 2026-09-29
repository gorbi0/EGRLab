"""P02 R2 parts: explicit list. source_ref maps every part to the v6.1 BOM or to HOLD C1.
Footprints are copied from KiCad 10.0.6 libraries or generated here; nothing is inferred.
"""
from cadlib import *
import shutil, json, csv, copy
FP = P / 'eda/libraries/P02.pretty'; FP.mkdir(parents=True, exist_ok=True)


def copyfp(lib, name):
    src = K / 'footprints' / (lib + '.pretty') / (name + '.kicad_mod'); assert src.exists(), src
    dest = P / 'eda/libraries' / (lib + '.pretty'); dest.mkdir(parents=True, exist_ok=True); shutil.copy2(src, dest / src.name)
    return lib + ':' + name


def simplepads(name, count, pitch, drill, pad, anchor=False, label=''):
    s = f'(footprint {q(name)} (version 20240108) (generator "pcbnew") (layer "F.Cu") (attr through_hole)'
    for i in range(count):
        s += f'(pad "{i + 1}" thru_hole {"rect" if i == 0 else "circle"} (at {i * pitch} 0) (size {pad} {pad}) (drill {drill}) (layers "*.Cu" "*.Mask"))'
    if anchor:
        hole = 4.2 if drill > 2 else 3.2
        for px in [-3, (count - 1) * pitch + 3]:
            s += f'(pad "" np_thru_hole circle (at {px} -12.5) (size {hole} {hole}) (drill {hole}) (layers "*.Cu" "*.Mask"))'
        s += f'(fp_text user "TIE / 12.5 mm" (at {(count - 1) * pitch / 2} -16) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))'
    x0 = -6 if anchor else -pad / 2 - 0.5; x1 = (count - 1) * pitch - x0
    y0 = -15.5 if anchor else -pad / 2 - 0.5; y1 = pad / 2 + 0.5
    s += f'(fp_rect (start {x0} {y0}) (end {x1} {y1}) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))'
    if label:
        s += f'(fp_text user {q(label)} (at {(count - 1) * pitch / 2} 3.2) (layer "F.Fab") (effects (font (size 1 1) (thickness .15))))'
    s += f'(fp_text reference "REF**" (at {(count - 1) * pitch / 2} 5) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))'
    (FP / (name + '.kicad_mod')).write_text(s + ')', encoding='utf-8'); return 'P02:' + name


def caprect(name, L, W, pitch):
    s = f'(footprint {q(name)} (version 20240108) (generator "pcbnew") (layer "F.Cu") (attr through_hole)'
    for layer, margin, width in [('F.Fab', 0, 0.1), ('F.SilkS', 0.1, 0.12), ('F.CrtYd', 0.5, 0.05)]:
        s += f'(fp_rect (start {(pitch - L) / 2 - margin} {-W / 2 - margin}) (end {(pitch + L) / 2 + margin} {W / 2 + margin}) (stroke (width {width}) (type default)) (fill none) (layer "{layer}"))'
    for n, x in [(1, 0), (2, pitch)]:
        s += f'(pad "{n}" thru_hole circle (at {x} 0) (size 1.8 1.8) (drill 0.9) (layers "*.Cu" "*.Mask"))'
    s += f'(fp_text reference "REF**" (at {pitch / 2} {-W / 2 - 1.5}) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))'
    (FP / (name + '.kicad_mod')).write_text(s + ')', encoding='utf-8'); return 'P02:' + name


def adapter_so14():
    """Kamami 575068 'Adapter PCB SOP14 na DIP14': 18 x 18 mm board, pin rows 15.24 mm apart
    (photo checked 24.09.2026), square goldpins 0.64 mm -> 1.0 mm holes. Pin n = SO pin n."""
    name = 'Adapter_SO14_DIP14_W15.24_Kamami575068'
    s = f'(footprint {q(name)} (version 20240108) (generator "pcbnew") (layer "F.Cu") (attr through_hole) (descr "SO14 on Kamami 575068 adapter, rows 15.24 mm, board 18x18 mm")'
    for i in range(7):
        s += f'(pad "{i + 1}" thru_hole {"rect" if i == 0 else "oval"} (at 0 {i * 2.54}) (size 1.7 1.7) (drill 1.0) (layers "*.Cu" "*.Mask"))'
        s += f'(pad "{14 - i}" thru_hole oval (at 15.24 {i * 2.54}) (size 1.7 1.7) (drill 1.0) (layers "*.Cu" "*.Mask"))'
    cx, cy = 7.62, 7.62
    for layer, margin, width in [('F.Fab', 0, 0.1), ('F.SilkS', 0.3, 0.12), ('F.CrtYd', 0.6, 0.05)]:
        s += f'(fp_rect (start {cx - 9 - margin} {cy - 9 - margin}) (end {cx + 9 + margin} {cy + 9 + margin}) (stroke (width {width}) (type default)) (fill none) (layer "{layer}"))'
    s += '(fp_circle (center -1.7 -1.2) (end -1.3 -1.2) (stroke (width 0.3) (type default)) (fill none) (layer "F.SilkS"))'
    s += f'(fp_text user "SO14 ADAPTER" (at {cx} {cy}) (layer "F.Fab") (effects (font (size 1 1) (thickness .15))))'
    s += f'(fp_text reference "REF**" (at {cx} {cy - 10.8}) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))'
    (FP / (name + '.kicad_mod')).write_text(s + ')', encoding='utf-8'); return 'P02:' + name


TO220 = 'P02:TO220_3_P2.54_Drill1.4'; TP1FP = 'P02:TestPad_1'
PWR2 = 'P02:Pigtail_PWR_2x2.5mm2'
RCH = simplepads('Pigtail_RCHARGE_2xAWG20', 2, 5.08, 1.3, 2.6, True, 'R_CHARGE 47R/25W')
PSUOK = simplepads('Pigtail_PSUOK_6x_P2.54', 6, 2.54, 1.1, 2.0, True, 'PSUOK 1..6')
ADP = adapter_so14()
C100N = 'P02:C_Vishay_K15_H5_P5'  # copied verbatim from P01 R3.1 library (reviewed there)
TO92 = copyfp('Package_TO_SOT_THT', 'TO-92_Inline_Wide')
RFP = copyfp('Resistor_THT', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal')  # Yageo MF0207 body 6.3 x 2.5 mm
DIP14 = copyfp('Package_DIP', 'DIP-14_W7.62mm'); DIP8 = copyfp('Package_DIP', 'DIP-8_W7.62mm')
CP5 = copyfp('Capacitor_THT', 'CP_Radial_D5.0mm_P2.00mm'); SNAP = copyfp('Capacitor_THT', 'CP_Radial_D35.0mm_P10.00mm_SnapIn')
FUSE = copyfp('Fuse', 'Fuseholder_Cylinder-5x20mm_Stelvio-Kontek_PTF78_Horizontal_Open')
TSR = copyfp('Converter_DCDC', 'Converter_DCDC_TRACO_TSR2-xxxx_THT')
LV = copyfp('Connector_Molex', 'Molex_Mini-Fit_Jr_5566-04A_2x02_P4.20mm_Vertical')
VS14 = copyfp('Connector_Molex', 'Molex_Mini-Fit_Jr_5566-14A_2x07_P4.20mm_Vertical')
GMSTB = copyfp('Connector_Phoenix_GMSTB', 'PhoenixContact_GMSTBA_2,5_3-G-7,62_1x03_P7.62mm_Horizontal')
LED = copyfp('LED_THT', 'LED_D3.0mm')

S_R = symbol('Device', 'R'); S_C = symbol('Device', 'C'); S_CP = symbol('Device', 'C_Polarized'); S_F = symbol('Device', 'Fuse')
S_D2 = symbol('Device', 'D_Schottky_Dual_CommonCathode_AKA'); S_LED = symbol('Device', 'LED'); S_TP = symbol('Connector', 'TestPoint')
S_TSR50 = symbol('Converter_DCDC', 'TSR2-2450')
try:
    S_TSR33 = symbol('Converter_DCDC', 'TSR2-2433')
except KeyError:
    S_TSR33 = symbol('Converter_DCDC', 'TSR2-2450', 'TSR2-2433')
S_SUP = symbol('Power_Supervisor', 'MCP120-xxxDxTO'); S_CMP = symbol('Comparator', 'LM2903')
S_AND = symbol('74xx', '74LS08', '74HC08'); S_BUF = symbol('74xx', '74LVC125')
S_REF = symbol('Reference_Voltage', 'TL431LP', 'TL431BILP')
# TI LP bond-out differs from the generic KiCad TL431LP symbol: K=1, A=2, REF=3 (same as P01 U3).
for pin in pin_defs(S_REF).values():
    n = one(pin, 'number'); n[1] = {'1': '3', '3': '1'}.get(n[1], n[1])


def conn(n):
    return symbol('Connector_Generic', f'Conn_01x{n:02d}')


URL = {'stps': 'https://www.st.com/resource/en/datasheet/stps20100c.pdf', 'tsr2': 'https://www.tracopower.com/products/tsr2.pdf',
       'mcp120': 'https://ww1.microchip.com/downloads/en/devicedoc/11184d.pdf', 'lm2903': 'https://www.ti.com/lit/ds/symlink/lm2903.pdf',
       'tl431': 'https://www.ti.com/lit/ds/symlink/tl431.pdf', 'hc08': 'https://www.ti.com/lit/ds/symlink/sn74hc08.pdf',
       'lvc125': 'https://assets.nexperia.com/documents/data-sheet/74LVC125A.pdf', 'hc': 'https://www.tme.eu/Document/52dbc9ab47efa879b9859910ffff5ecc/hc.pdf',
       'ptf78': 'https://www.tme.eu/en/Document/3b48dbe2b9714a62652c97b08fcd464b/PTF78.pdf', 'minifit': 'http://www.molex.com/pdm_docs/sd/039281043_sd.pdf',
       'gmstb': 'https://www.phoenixcontact.com/en-pl/products/pcb-header-gmstba-25-3-g-762-1766246', 'hsa25': 'https://www.te.com/en/product-5-1625971-1.html',
       'fr': 'https://industrial.panasonic.com/sa/products/pt/aluminum-cap-lead', 'k15': 'https://www.vishay.com/docs/45171/kseries.pdf',
       'l934': 'https://www.kingbrightusa.com/images/catalog/SPEC/L-934GD.pdf', 'mf0207': 'https://www.yageo.com/upload/media/product/productsearch/datasheet/lr/Yageo_LR_MFR_1.pdf'}
PARTS = {}


def add(ref, src, sym, fp, display, mpn, pins, url='', note='', sheet='P02', on_board=True):
    PARTS[ref] = {'ref': ref, 'source_ref': src, 'symbol': sym, 'footprint': fp, 'display': display, 'value': display, 'mpn': mpn,
                  'pins': {str(k): v for k, v in pins.items()}, 'url': url, 'note': note, 'qty': 1, 'sheet': sheet, 'on_board': on_board}


# ---- sheet P02: power, HOLD, distribution --------------------------------------------------
add('J1', 'J_SUPPLYB', conn(2), PWR2, 'SUPPLY / soldered wires', 'PCB termination; H_SUPPLY', {1: 'VPROT', 2: 'GND'},
    note='H_SUPPLY 2 x 2.5 mm2, 200 mm, MSTB 2,5/3-ST-5,08 (1757022) plug to P01 J6: 1=VPROT 2=GND 3=NC. Anchor 12.5 mm.')
add('J2', 'J_VMOTORA', conn(3), GMSTB, 'VMOTOR / GMSTBA 3p 7.62', 'Phoenix GMSTBA 2,5/3-G-7,62 (1766246)', {1: 'VPROT', 2: 'GND', 3: 'NC'}, URL['gmstb'],
    'R1 deviation: v6.1 PC 4/3-G-7,62 replaced by GMSTBA 7.62 (verified footprint); P07 plug must follow. 12 A >= 5 A system fuse.')
for i, lv in enumerate(range(3, 11)):
    add(f'J{3 + i}', f'J_LV{lv:02d}A', symbol('Connector_Generic', 'Conn_02x02_Odd_Even'), LV, f'LV{lv:02d} / Mini-Fit Jr 4p', 'Molex Mini-Fit Jr 5566-04A vertical, Au (39-28-x04x)',
        {1: '5V_SYS', 2: 'GND', 3: '3V3_IO', 4: 'GND'}, URL['minifit'], f'LV{lv:02d}: 1=5V_SYS 2=GND 3=3V3_IO 4=GND; mechanical key per v6.1 connectors.csv.')
add('J11', 'J_VSENSEA', symbol('Connector_Generic', 'Conn_02x07_Odd_Even'), VS14, 'VSENSE / Mini-Fit Jr 14p', 'Molex Mini-Fit Jr 5566-14A vertical, Au (39-28-x14x)',
    {1: 'VPROT_SENSE', 2: 'GND', **{k: 'NC' for k in range(3, 15)}}, URL['minifit'], 'Dedicated 14p body, not interchangeable with LV; only pins 1/2 wired.')
add('J13', 'ADDED_HOLD_RCHARGE', conn(2), RCH, 'R_CHARGE / wires', 'PCB termination; wires to HSA2547RJ', {1: 'VPROT', 2: 'CHARGE_D'},
    note='AWG20 pair to off-board R_CHARGE on its own aluminium plate; anchor 12.5 mm.')
add('R17', 'R_CHARGE', S_R, '', '47R / 25W (off-board)', 'HSA2547RJ (TE 5-1625971-1)', {1: 'VPROT', 2: 'CHARGE_D'}, URL['hsa25'],
    'Mounted off-board on an aluminium plate per TE conditions; <=7.26 W at 18 V, <=22.94 W at 32 V. Never replace with a 0.5 W part.', on_board=False)
add('D1', 'D_OR', S_D2, TO220, 'STPS20100CT / D_OR', 'STPS20100CT', {1: 'VPROT', 2: 'VLOG_RES', 3: 'HOLD_FUSED'}, URL['stps'],
    'Separate anodes: A1=VPROT, A2=HOLD_FUSED; K+tab=VLOG_RES. Never a common-anode variant.')
add('D2', 'D_CHARGE', S_D2, TO220, 'STPS20100CT / D_CHARGE', 'STPS20100CT', {1: 'CHARGE_D', 2: 'HOLD_FUSED', 3: 'CHARGE_D'}, URL['stps'],
    'Anodes 1+3 tied on the PCB; K+tab=HOLD_FUSED.')
add('F1', 'F_HOLD', S_F, FUSE, 'T2A / 5x20 DC', 'Stelvio-Kontek PTF78 + fuse T2A DC-rated (select)', {1: 'HOLD_FUSED', 2: 'HOLD_STORE'}, URL['ptf78'],
    'At the bank positive output; limits energy into an external short. DC rating and I2t confirmed at acceptance.')
for i in range(3):
    add(f'C{1 + i}', f'C_H{1 + i}', S_CP, SNAP, '22000u / 35V', 'HC1V229M35045HA', {1: 'HOLD_STORE', 2: 'GND'}, URL['hc'],
        'Samwha HC snap-in P10, D35x45 mm; keep vent clear; Ceff/ESR measured 0..50 C.')
add('R1', 'R_BLEED', S_R, RFP, '4K7 / 1%', 'MF0207FTE-4K7', {1: 'HOLD_STORE', 2: 'GND'}, URL['mf0207'], 'Bleeder: up to 22 min from 32 V (C +20%, R +1%). Measure before service.')
add('C4', 'C_BUS', S_CP, CP5, '22u / 50V', 'EEUFR1H220', {1: 'VLOG_RES', 2: 'GND'}, URL['fr'], 'Counts towards the P01 220 uF VPROT budget; at D1 cathode.')
add('F2', 'F2', S_F, FUSE, '1A / 5x20', 'Stelvio-Kontek PTF78 + fuse F1A DC-rated (select)', {1: 'VLOG_RES', 2: 'P02_VIN_DC5'}, URL['ptf78'], 'Input moved from VPROT to VLOG_RES (HOLD C1).')
add('F3', 'F3', S_F, FUSE, '1A / 5x20', 'Stelvio-Kontek PTF78 + fuse F1A DC-rated (select)', {1: 'VLOG_RES', 2: 'P02_VIN_DC33'}, URL['ptf78'], 'Input moved from VPROT to VLOG_RES (HOLD C1).')
add('F4', 'F_VSENSE', S_F, FUSE, 'F100mA / 5x20', 'Stelvio-Kontek PTF78 + fuse F100mA >=32 V DC (select)', {1: 'VPROT', 2: 'VPROT_SENSE'}, URL['ptf78'], 'At the VPROT branch, before the VSENSE harness.')
add('U1', 'M3', S_TSR50, TSR, 'TSR 2-2450', 'TSR 2-2450', {1: 'P02_VIN_DC5', 2: 'GND', 3: '5V_SYS'}, URL['tsr2'], 'Minimum input 6.5 V; design margin 7 V.')
add('U2', 'M4', S_TSR33, TSR, 'TSR 2-2433', 'TSR 2-2433', {1: 'P02_VIN_DC33', 2: 'GND', 3: '3V3_IO'}, URL['tsr2'], '3V3_IO only; never tie to 3V3_CORE of P03.')
add('C5', 'C_DCDC_5V_SYS_IN', S_CP, CP5, '10u / 50V', 'EEUFR1H100', {1: 'P02_VIN_DC5', 2: 'GND'}, URL['fr'])
add('C6', 'C_DCDC_5V_SYS_OUT', S_CP, CP5, '22u / 16V', 'EEUFR1C220', {1: '5V_SYS', 2: 'GND'}, URL['fr'], 'v6.1: 22 uF / 10 V; 16 V chosen.')
add('C7', 'C_DCDC_3V3_IO_IN', S_CP, CP5, '10u / 50V', 'EEUFR1H100', {1: 'P02_VIN_DC33', 2: 'GND'}, URL['fr'])
add('C8', 'C_DCDC_3V3_IO_OUT', S_CP, CP5, '22u / 16V', 'EEUFR1C220', {1: '3V3_IO', 2: 'GND'}, URL['fr'], 'v6.1: 22 uF / 10 V; 16 V chosen.')

# ---- sheet MON: supervision, PSU_OK, HOLD_READY ----------------------------------------------
def mon(ref, *a, **k):
    add(ref, *a, sheet='MON', **k)


mon('U3', 'U_SUP3', S_SUP, TO92, 'MCP120-300DI/TO', 'MCP120-300DI/TO', {1: 'P02_SUP3_N', 2: '3V3_IO', 3: 'GND'}, URL['mcp120'], 'Variant D: 1=RST 2=VDD 3=VSS; open drain.')
mon('U4', 'U_SUP5', S_SUP, TO92, 'MCP120-450DI/TO', 'MCP120-450DI/TO', {1: 'P02_SUP5_RAW', 2: '5V_SYS', 3: 'GND'}, URL['mcp120'], 'Variant D: 1=RST 2=VDD 3=VSS; open drain.')
mon('R2', 'R_U_SUP3', S_R, RFP, '10K / 1%', 'MF0207FTE-10K', {1: 'P02_SUP3_N', 2: '3V3_IO'}, URL['mf0207'])
mon('R3', 'R_SUP5', S_R, RFP, '10K / 1%', 'MF0207FTE-10K', {1: 'P02_SUP5_RAW', 2: '5V_SYS'}, URL['mf0207'])
mon('C9', 'C_U_SUP3', S_C, C100N, '100nF / X7R', 'K104K15X7RF53H5', {1: '3V3_IO', 2: 'GND'}, URL['k15'], 'At U3.')
mon('C10', 'C_SUP5', S_C, C100N, '100nF / X7R', 'K104K15X7RF53H5', {1: '5V_SYS', 2: 'GND'}, URL['k15'], 'At U4.')
mon('U5', 'U_SUPBUF', S_BUF, ADP, '74LVC125A / SO14 adapter', '74LVC125AD,118 (Nexperia) on Kamami 575068',
    {1: 'GND', 2: 'P02_SUP5_RAW', 3: 'P02_SUP5_N', 4: '3V3_IO', 5: 'GND', 6: 'NC', 7: 'GND', 8: 'NC', 9: 'GND', 10: '3V3_IO', 11: 'NC', 12: 'GND', 13: '3V3_IO', 14: '3V3_IO'},
    URL['lvc125'], 'Ioff, 5 V tolerant input: 5 V domain RST to 3.3 V logic. Unused OE#=3V3_IO, inputs=GND.')
mon('C11', 'C_U_SUPBUF', S_C, C100N, '100nF / X7R', 'K104K15X7RF53H5', {1: '3V3_IO', 2: 'GND'}, URL['k15'], 'At adapter pins; C16 is additionally fitted directly on the U5 adapter.')
mon('U6', 'U_READY', S_AND, DIP14, 'SN74HC08N', 'SN74HC08N',
    {1: 'P02_SUP3_N', 2: 'P02_SUP5_N', 3: 'PSU_OK', 4: 'P02_BANK_OK', 5: 'P02_VPROT_OK', 6: 'P02_HOLD_QUAL', 7: 'GND',
     8: 'P02_HOLD_READY_INT', 9: 'P02_HOLD_QUAL', 10: 'PSU_OK', 11: 'NC', 12: 'GND', 13: 'GND', 14: '3V3_IO'},
    URL['hc08'], 'Gate A = PSU_OK (v6.1). Gates B/C = HOLD_READY = BANK_OK & VPROT_OK & PSU_OK (R1). Gate D inputs to GND.')
mon('C12', 'C_U_READY', S_C, C100N, '100nF / X7R', 'K104K15X7RF53H5', {1: '3V3_IO', 2: 'GND'}, URL['k15'], 'At U6.')
mon('R4', 'R_READY_PD', S_R, RFP, '10K / 1%', 'MF0207FTE-10K', {1: 'PSU_OK', 2: 'GND'}, URL['mf0207'], 'PSU_OK low while U6 is unpowered.')
mon('U7', 'ADDED_HOLD_READY', S_CMP, DIP8, 'LM2903P', 'LM2903P',
    {1: 'P02_BANK_OK', 2: 'P02_REF25', 3: 'P02_BANK_CMP', 4: 'GND', 5: 'P02_VPROT_CMP', 6: 'P02_REF25', 7: 'P02_VPROT_OK', 8: '5V_SYS'},
    URL['lm2903'], 'Supply 5V_SYS; open-collector outputs pulled up to 3V3_IO. Inputs may exceed V+ (up to 36 V abs max) with IN- inside CM range.')
mon('C13', 'ADDED_HOLD_READY', S_C, C100N, '100nF / X7R', 'K104K15X7RF53H5', {1: '5V_SYS', 2: 'GND'}, URL['k15'], 'At U7.')
mon('U8', 'ADDED_HOLD_READY', S_REF, TO92, 'TL431BILP', 'TL431BILP', {1: 'P02_REF25', 2: 'GND', 3: 'P02_REF25'}, URL['tl431'], 'TI LP: 1=K 2=A 3=REF; K+REF tied = 2.495 V.')
mon('R5', 'ADDED_HOLD_READY', S_R, RFP, '330R / 1%', 'MF0207FTE-330R', {1: '5V_SYS', 2: 'P02_REF25'}, URL['mf0207'], 'TL431 cathode current about 7.6 mA. No capacitor on REF25.')
mon('R6', 'ADDED_HOLD_READY', S_R, RFP, '30K1 / 0.1%', 'MBB0207VD3012BC100', {1: 'HOLD_STORE', 2: 'P02_BANK_DIV'}, 'https://www.vishay.com/doc?28767', 'Precision 0.1%, 25 ppm/K; required for corner limits.')
mon('R7', 'ADDED_HOLD_READY', S_R, RFP, '10K / 0.1%', 'MBB0207VD1002BC100', {1: 'P02_BANK_DIV', 2: 'GND'}, 'https://www.vishay.com/doc?28767', 'Precision 0.1%, 25 ppm/K.')
mon('R8', 'ADDED_HOLD_READY', S_R, RFP, '1M / 1%', 'MF0207FTE-1M', {1: 'P02_BANK_OK', 2: 'P02_BANK_CMP'}, URL['mf0207'], 'Positive feedback to comparator side of R18; no capacitor here.')
mon('C14', 'ADDED_HOLD_READY', S_C, C100N, '10nF / X7R', 'K103K15X7RF53H5', {1: 'P02_BANK_DIV', 2: 'GND'}, URL['k15'], 'Filter BEFORE R18; tau approx 75 us, not the regeneration node.')
mon('R9', 'ADDED_HOLD_READY', S_R, RFP, '38K3 / 0.1%', 'MBB0207VD3832BC100', {1: 'VPROT', 2: 'P02_VPROT_DIV'}, 'https://www.vishay.com/doc?28767', 'Precision 0.1%, 25 ppm/K; required for corner limits.')
mon('R10', 'ADDED_HOLD_READY', S_R, RFP, '10K / 0.1%', 'MBB0207VD1002BC100', {1: 'P02_VPROT_DIV', 2: 'GND'}, 'https://www.vishay.com/doc?28767', 'Precision 0.1%, 25 ppm/K.')
mon('R11', 'ADDED_HOLD_READY', S_R, RFP, '1M / 1%', 'MF0207FTE-1M', {1: 'P02_VPROT_OK', 2: 'P02_VPROT_CMP'}, URL['mf0207'], 'Feedback to comparator side of R19.')
mon('C15', 'ADDED_HOLD_READY', S_C, C100N, '10nF / X7R', 'K103K15X7RF53H5', {1: 'P02_VPROT_DIV', 2: 'GND'}, URL['k15'], 'Filter BEFORE R19; tau approx 79 us.')
mon('R18', 'R2_FILTER_ISOLATION', S_R, RFP, '10K / 1%', 'MF0207FTE-10K', {1: 'P02_BANK_DIV', 2: 'P02_BANK_CMP'}, URL['mf0207'], 'Separates filter capacitance from positive feedback.')
mon('R19', 'R2_FILTER_ISOLATION', S_R, RFP, '10K / 1%', 'MF0207FTE-10K', {1: 'P02_VPROT_DIV', 2: 'P02_VPROT_CMP'}, URL['mf0207'], 'Separates filter capacitance from positive feedback.')
add('R20', 'R2_PROTECTED_TESTPOINT', S_R, 'P02:R_PR02_P17.78', '1K / 2W / 5%', 'PR02000201001JA100', {1: 'HOLD_STORE', 2: 'HOLD_TP'}, 'https://www.vishay.com/docs/28729/pr010203.pdf', 'Local current limiter before TP3; no raw bank test pad. Short at 32 V <=34 mA, <=1.09 W.')
mon('C16', 'R2_U5_LOCAL_BYPASS', S_C, '', '100nF / adapter U5', 'GRM21BR71H104KA01L (0805)', {1: '3V3_IO', 2: 'GND'}, 'https://www.murata.com', 'Fitted on U5 adapter, short local connections to IC pins 14 and 7; inspect before installing adapter.', on_board=False)
mon('R12', 'ADDED_HOLD_READY', S_R, RFP, '10K / 1%', 'MF0207FTE-10K', {1: 'P02_BANK_OK', 2: '3V3_IO'}, URL['mf0207'], 'Pull-up of U7A output.')
mon('R13', 'ADDED_HOLD_READY', S_R, RFP, '10K / 1%', 'MF0207FTE-10K', {1: 'P02_VPROT_OK', 2: '3V3_IO'}, URL['mf0207'], 'Pull-up of U7B output.')
mon('R14', 'ADDED_HOLD_READY', S_R, RFP, '1K / 1%', 'MF0207FTE-1K', {1: 'P02_HOLD_READY_INT', 2: 'HOLD_READY'}, URL['mf0207'], 'Series protection of the reserved PSUOK pin 3.')
mon('R15', 'ADDED_HOLD_READY', S_R, RFP, '10K / 1%', 'MF0207FTE-10K', {1: 'P02_HOLD_READY_INT', 2: 'GND'}, URL['mf0207'], 'Defined LOW while U6 is unpowered.')
mon('R16', 'ADDED_HOLD_READY', S_R, RFP, '1K / 1%', 'MF0207FTE-1K', {1: 'P02_HOLD_READY_INT', 2: 'P02_LED_A'}, URL['mf0207'], 'LED ~1.3 mA.')
mon('LED1', 'ADDED_HOLD_READY', S_LED, LED, 'GREEN 3mm / HOLD READY', 'L-934GD', {1: 'GND', 2: 'P02_LED_A'}, URL['l934'], 'Local voltage status ONLY. Manual 15 s qualification and load acceptance remain required; not integrated into CORE.')
mon('J12', 'J_PSUOKB', conn(6), PSUOK, 'PSUOK / soldered ribbon', 'PCB termination; H_PSUOK',
    {1: 'PSU_OK', 2: 'GND', 3: 'HOLD_READY', 4: 'NC', 5: 'NC', 6: 'NC'},
    note='H_PSUOK 6 x AWG28 ribbon, 150 mm, IDC 6p KEY 5 at P04. Pin 3 HOLD_READY reserved (NC on P04 until integration).')
for idx, (net, sheet) in enumerate([('VPROT', 'P02'), ('VLOG_RES', 'P02'), ('HOLD_TP', 'P02'), ('5V_SYS', 'P02'), ('3V3_IO', 'P02'), ('GND', 'P02'),
                                    ('PSU_OK', 'MON'), ('HOLD_READY', 'MON'), ('P02_REF25', 'MON'), ('GND', 'MON')], 1):
    r = f'TP{idx}'
    PARTS[r] = {'ref': r, 'source_ref': 'ADDED_TESTPAD', 'value': net, 'display': net.replace('P02_', ''), 'pins': {'1': net}, 'symbol': S_TP,
                'footprint': TP1FP, 'mpn': 'PCB test pad', 'qty': 1, 'url': '', 'sheet': sheet, 'on_board': True,
                'note': 'TP3: protected by R20=1k/2W; DMM >=10 Mohm. Bank energy up to 41 J.' if net == 'HOLD_TP' else 'Probe access; no circuit function.'}

for j in range(3,11):
    PARTS[f'J{j}']['mpn']='Molex 39-29-6048 (Au, vertical, no snap pegs)'
    PARTS[f'J{j}']['url']='https://www.molex.com/en-us/products/part-detail/39296048'
PARTS['J11']['mpn']='Molex 39-29-6148 (Au, vertical, no snap pegs)'
PARTS['J11']['url']='https://www.molex.com/en-us/products/part-detail/39296148?display=pdf'

for r, part in PARTS.items():
    if r.startswith('R'):
        part['tolerance'] = .001 if r in ('R6','R7','R9','R10') else (.05 if r in ('R17','R20') else .01)
        part['tcr_ppm'] = 25 if r in ('R6','R7','R9','R10') else (250 if r=='R20' else 100)
PARTS['F1']['mpn']='Schurter 0001.2507 (T2A) + PTF78 holder'
PARTS['F1']['url']='https://www.schurter.com/en/datasheet/typ_SPT_5x20.pdf'
PARTS['F1']['note']='300 VDC / 1500 A; melting I2t typ 9.2 A2s (not a guaranteed clearing limit). Verify pulse coordination on bench.'



def write_tables():
    clean = {r: {k: v for k, v in p.items() if k != 'symbol'} for r, p in PARTS.items()}
    (P / 'docs/parts.json').write_text(json.dumps(clean, ensure_ascii=False, indent=2), encoding='utf-8')
    fields = ['ref', 'source_ref', 'display', 'mpn', 'qty', 'footprint', 'url', 'note']
    with (P / 'docs/BOM.csv').open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fields, delimiter=';', extrasaction='ignore'); w.writeheader(); w.writerows(PARTS.values())
    libs = {p['symbol'][1]: p['symbol'] for p in PARTS.values()}; libs['P02:PWR_FLAG'] = symbol('power', 'PWR_FLAG')
    (P / 'eda/libraries/P02.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor")' + ''.join(dump([s[0], s[1].split(':')[1]] + s[2:]) for s in libs.values()) + ')', encoding='utf-8')
    (P / 'eda/sym-lib-table').write_text('(sym_lib_table (lib (name "P02") (type "KiCad") (uri "${KIPRJMOD}/libraries/P02.kicad_sym") (options "") (descr "P02 symbols")))', encoding='utf-8')
    flibs = sorted({p['footprint'].split(':')[0] for p in PARTS.values() if p['footprint']})
    (P / 'eda/fp-lib-table').write_text('(fp_lib_table ' + ''.join(f'(lib (name {q(l)}) (type "KiCad") (uri "${{KIPRJMOD}}/libraries/{l}.pretty") (options "") (descr "P02 selected footprint"))' for l in flibs) + ')', encoding='utf-8')
