"""P02 R4 parts: power from a Li-ion 4S pack (12.0-16.8 V). Explicit list; nothing is inferred.
Source: Plytki/P02-R4-specyfikacja (SPECYFIKACJA-P02-R4.md, STAN-PRAC.md, interfejsy.csv, ZADANIE-P02-R4-ETAP2.md v2)
and Plytki/Format-S1/SPECYFIKACJA-FORMATU-S1.md (S1-1).
- Gate block and control (Q1..Q8, R13..R34, C5/C6, D4/D7..D9, U1..U4) keep the P01 R3 designators and values
  (P01-R3-review/docs/parts.json), except R23 = 22k (user decision 29.09.2026) and the UVLO divider.
- LV converters and PSU_OK logic come from P02 R3 (P02-R3-review/docs/parts.json) with new designators.
- Etap 2 (format S1): D3 5KP24A (R4E1-01); J3..J13 and J16 replaced by J_BP (IDC 2x10, pinout S1 section 8);
  service headers J_SV1/J_SV2 on edge B with series resistors R50..R71 (S1 section 6); TP1..TP17 removed;
  owned THT resistors (Zamowione/zamowione.csv, P01 purchase) stand vertically, new resistors and ceramics are SMD 1206;
  U9 is soldered directly as SOIC-14 (C28 on the board); C_H lies flat (own footprint).
- source_ref names the origin: 'P01R3:<ref>', 'P02R3:<ref>' or 'R4:NEW'.
- height_mm: height above the board (S1 level 1: <= 21.5 mm); height_src says where the number comes from.
Footprints: copied from KiCad 10.0.6 libraries, from the reviewed P01 R3 / P02 R3 libraries, or generated here.
"""
from cadlib import *
import shutil, json, csv
FP = P / 'eda/libraries/P02.pretty'; FP.mkdir(parents=True, exist_ok=True)


def copyfp(lib, name):
    src = K / 'footprints' / (lib + '.pretty') / (name + '.kicad_mod'); assert src.exists(), src
    dest = P / 'eda/libraries' / (lib + '.pretty'); dest.mkdir(parents=True, exist_ok=True); shutil.copy2(src, dest / src.name)
    return lib + ':' + name


def localfp(name):
    assert (FP / (name + '.kicad_mod')).exists(), name  # copied from P01 R3 / P02 R3 libraries (see README)
    return 'P02:' + name


def simplepads(name, count, pitch, drill, pad, anchor=False, label='', back=12.5):
    """Soldered-wire termination (same generator as P02 R3): pads in a row, optional strain-relief holes `back` mm behind
    (R3: 12.5 mm; R4 in S1: 7.0 mm for the thin AWG22 wires J14/J15, to fit the 2/3 board)."""
    s = f'(footprint {q(name)} (version 20240108) (generator "pcbnew") (layer "F.Cu") (attr through_hole)'
    for i in range(count):
        s += f'(pad "{i + 1}" thru_hole {"rect" if i == 0 else "circle"} (at {i * pitch} 0) (size {pad} {pad}) (drill {drill}) (layers "*.Cu" "*.Mask"))'
    if anchor:
        hole = 3.2
        for px in [-3, (count - 1) * pitch + 3]:
            s += f'(pad "" np_thru_hole circle (at {px} {-back}) (size {hole} {hole}) (drill {hole}) (layers "*.Cu" "*.Mask"))'
        s += f'(fp_text user "TIE / {back} mm" (at {(count - 1) * pitch / 2} {-back - 3.5}) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))'
    x0 = -6 if anchor else -pad / 2 - 0.5; x1 = (count - 1) * pitch - x0
    y0 = -back - 3.0 if anchor else -pad / 2 - 0.5; y1 = pad / 2 + 0.5
    s += f'(fp_rect (start {x0} {y0}) (end {x1} {y1}) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))'
    if label:
        s += f'(fp_text user {q(label)} (at {(count - 1) * pitch / 2} 3.2) (layer "F.Fab") (effects (font (size 1 1) (thickness .15))))'
    s += f'(fp_text reference "REF**" (at {(count - 1) * pitch / 2} 5) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))'
    (FP / (name + '.kicad_mod')).write_text(s + ')', encoding='utf-8'); return 'P02:' + name




def cap_lying():
    """C_H 2200 uF / 35 V, D16 x L25 mm radial can laid flat (S1: height <= 21.5 mm, standing can is 25 mm + leads).
    Leads P7.5 bent 90 deg 1.5 mm behind the can end; body outline on F.Fab/F.SilkS so nothing else is placed under it.
    Pad 1 (+, square) at the origin, pad 2 at x = 7.5; the can lies along +y. Glue or tie the can to the board."""
    name = 'CP_Radial_D16.0mm_L25mm_P7.50mm_Lying'
    x0, x1, y0, y1 = 3.75 - 8.0, 3.75 + 8.0, 1.5, 26.5
    s = f'(footprint {q(name)} (version 20240108) (generator "pcbnew") (layer "F.Cu") (attr through_hole) (descr "Radial electrolytic D16 x L25 mm, P7.5 mm, laid flat; leads bent 1.5 mm behind the can")'
    s += '(pad "1" thru_hole rect (at 0 0) (size 2.2 2.2) (drill 1.1) (layers "*.Cu" "*.Mask"))'
    s += '(pad "2" thru_hole circle (at 7.5 0) (size 2.2 2.2) (drill 1.1) (layers "*.Cu" "*.Mask"))'
    for layer, m, w in [('F.Fab', 0, 0.1), ('F.SilkS', 0.15, 0.12), ('F.CrtYd', 0.5, 0.05)]:
        s += f'(fp_rect (start {x0 - m} {y0 - (m if layer != "F.CrtYd" else 3.0)}) (end {x1 + m} {y1 + m}) (stroke (width {w}) (type default)) (fill none) (layer "{layer}"))'
    s += '(fp_line (start -2.5 -1.8) (end -1.3 -1.8) (stroke (width 0.2) (type default)) (layer "F.SilkS"))'
    s += '(fp_line (start -1.9 -2.4) (end -1.9 -1.2) (stroke (width 0.2) (type default)) (layer "F.SilkS"))'
    s += f'(fp_line (start {x0} {y0 + 4}) (end {x1} {y0 + 4}) (stroke (width 0.1) (type default)) (layer "F.Fab"))'
    s += f'(fp_text user "2200u 35V - lying" (at 3.75 14) (layer "F.Fab") (effects (font (size 1 1) (thickness .15))))'
    s += f'(fp_text reference "REF**" (at 3.75 12) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))'
    (FP / (name + '.kicad_mod')).write_text(s + ')', encoding='utf-8'); return 'P02:' + name


# ---- footprints ------------------------------------------------------------------------------
TO220 = localfp('TO220_3_P2.54_Drill1.4'); RPR02 = localfp('R_PR02_P17.78')
CK15 = localfp('C_Vishay_K15_H5_P5'); CB32 = localfp('C_TDK_B32529_L7.3_W2.5_P5'); CMKS = localfp('C_WIMA_MKS2_1u100V_L7.2_W7.2_P5')
TVS600 = localfp('TVS_P600_P20.32'); BATFP = localfp('Pigtail_PWR_2x2.5mm2')
PWRFP = simplepads('Pigtail_PWR_SW_2xAWG22_T7', 2, 3.81, 1.1, 2.0, True, 'PWR 1..2', 7.0)
VBATFP = simplepads('Pigtail_VBAT_1xAWG22', 1, 2.54, 1.1, 2.0, False, 'VBAT')   # no anchor: the wire is tied to the J1 anchor (2/3 board)
CH16 = cap_lying()
TO92 = copyfp('Package_TO_SOT_THT', 'TO-92_Inline_Wide')
D35 = copyfp('Diode_THT', 'D_DO-35_SOD27_P5.08mm_Vertical_CathodeUp'); D15 = copyfp('Diode_THT', 'D_DO-15_P5.08mm_Vertical_CathodeUp')
DIP14 = copyfp('Package_DIP', 'DIP-14_W7.62mm'); DIP8 = copyfp('Package_DIP', 'DIP-8_W7.62mm'); SOIC14 = copyfp('Package_SO', 'SOIC-14_3.9x8.7mm_P1.27mm')
CP5 = copyfp('Capacitor_THT', 'CP_Radial_D5.0mm_P2.00mm'); CP63 = copyfp('Capacitor_THT', 'CP_Radial_D6.3mm_P2.50mm')
C1206 = copyfp('Capacitor_SMD', 'C_1206_3216Metric')
RV07 = copyfp('Resistor_THT', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P5.08mm_Vertical'); RV04 = copyfp('Resistor_THT', 'R_Axial_DIN0204_L3.6mm_D1.6mm_P2.54mm_Vertical')
R1206 = copyfp('Resistor_SMD', 'R_1206_3216Metric'); LINK = copyfp('Resistor_THT', 'R_Axial_DIN0204_L3.6mm_D1.6mm_P5.08mm_Horizontal')
BLADE = copyfp('Fuse', 'Fuseholder_Blade_Mini_Keystone_3568')
TSR = copyfp('Converter_DCDC', 'Converter_DCDC_TRACO_TSR2-xxxx_THT')
GMSTB = copyfp('Connector_Phoenix_GMSTB', 'PhoenixContact_GMSTBA_2,5_3-G-7,62_1x03_P7.62mm_Horizontal')
IDC = copyfp('Connector_IDC', 'IDC-Header_2x10_P2.54mm_Horizontal')
SVH = copyfp('Connector_PinHeader_2.54mm', 'PinHeader_1x13_P2.54mm_Horizontal')
LED = copyfp('LED_THT', 'LED_D3.0mm')

# ---- symbols ---------------------------------------------------------------------------------
S_R = symbol('Device', 'R'); S_C = symbol('Device', 'C'); S_CP = symbol('Device', 'C_Polarized'); S_F = symbol('Device', 'Fuse')
S_D = symbol('Device', 'D'); S_DZ = symbol('Device', 'D_Zener'); S_TVS = symbol('Device', 'D_TVS')
S_D2 = symbol('Device', 'D_Schottky_Dual_CommonCathode_AKA'); S_LED = symbol('Device', 'LED'); S_TP = symbol('Connector', 'TestPoint')
S_PMOS = symbol('Transistor_FET', 'Q_PMOS_GDS'); S_NPN = symbol('Transistor_BJT', 'Q_NPN_EBC'); S_PNP = symbol('Transistor_BJT', 'Q_PNP_EBC')
S_TSR50 = symbol('Converter_DCDC', 'TSR2-2450')
try:
    S_TSR33 = symbol('Converter_DCDC', 'TSR2-2433')
except KeyError:
    S_TSR33 = symbol('Converter_DCDC', 'TSR2-2450', 'TSR2-2433')
S_SUP = symbol('Power_Supervisor', 'MCP120-xxxDxTO'); S_CMP = symbol('Comparator', 'LM2903')
S_AND = symbol('74xx', '74LS08', '74HC08'); S_BUF = symbol('74xx', '74LVC125')
S_LDO = symbol('Regulator_Linear', 'LM2936-5.0_TO92')
S_REF = symbol('Reference_Voltage', 'TL431LP', 'TL431BILP')
# TI LP bond-out differs from the generic KiCad TL431LP symbol: K=1, A=2, REF=3 (same as P01 U3 and P02 R3 U8).
for pin in pin_defs(S_REF).values():
    n = one(pin, 'number'); n[1] = {'1': '3', '3': '1'}.get(n[1], n[1])


def conn(n):
    return symbol('Connector_Generic', f'Conn_01x{n:02d}')


URL = {'stps': 'https://www.st.com/resource/en/datasheet/stps20100c.pdf', 'tsr2': 'https://www.tracopower.com/products/tsr2.pdf',
       'mcp120': 'https://ww1.microchip.com/downloads/en/devicedoc/11184d.pdf', 'lm2903': 'https://www.ti.com/lit/ds/symlink/lm2903.pdf',
       'tl431': 'https://www.ti.com/lit/ds/symlink/tl431.pdf', 'hc08': 'https://www.ti.com/lit/ds/symlink/sn74hc08.pdf',
       'lvc125': 'https://assets.nexperia.com/documents/data-sheet/74LVC125A.pdf', 'lm2936': 'https://www.ti.com/lit/ds/symlink/lm2936.pdf',
       'minifit': 'http://www.molex.com/pdm_docs/sd/039281043_sd.pdf',
       'gmstb': 'https://www.phoenixcontact.com/en-pl/products/pcb-header-gmstba-25-3-g-762-1766246',
       'fr': 'https://industrial.panasonic.com/sa/products/pt/aluminum-cap-lead', 'k15': 'https://www.vishay.com/docs/45171/kseries.pdf',
       'b32529': 'https://www.tdk-electronics.tdk.com/inf/20/20/db/fc_2009/B32520_529.pdf',
       'mks2': 'https://www.tme.eu/Document/a1d7ff07b330f8f08de986bd168d8c92/WIMA_MKS_2.pdf',
       'l934': 'https://www.kingbrightusa.com/images/catalog/SPEC/L-934GD.pdf', 'mfr': 'https://www.yageo.com/upload/media/product/productsearch/datasheet/lr/Yageo_LR_MFR_1.pdf',
       'pr02': 'https://www.vishay.com/docs/28729/pr010203.pdf', 'sup53': 'https://www.vishay.com/docs/72131/sup53p06.pdf',
       'npn': 'https://www.onsemi.com/download/data-sheet/pdf/2n5550-d.pdf', 'pnp': 'https://www.onsemi.com/download/data-sheet/pdf/2n5401-d.pdf',
       'zener': 'https://www.vishay.com/docs/85604/bzx55.pdf', '4148': 'https://www.vishay.com/docs/81857/1n4148.pdf',
       '5kp': 'https://www.littelfuse.com/assetdocs/tvs-diodes-5kp-datasheet?assetguid=b1ddd6a2-fccb-4327-bea1-7d77c0793479',
       'p6ke': 'https://www.littelfuse.com/assetdocs/tvs-diodes-p6ke-datasheet', 'mini': 'https://www.littelfuse.com/products/fuses/automotive-passenger-car/blade-fuses/297',
       'k3568': 'https://www.keyelco.com/product.cfm/product_id/755', 'idc': 'https://www.we-online.com/components/products/datasheet/61202021621.pdf',
       'hdr': 'https://www.we-online.com/components/products/datasheet/61301311021.pdf', 'rc1206': 'https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-RC_Group_51_RoHS_L_12.pdf',
       'erjp08': 'https://industrial.panasonic.com/cdbs/www-data/pdf/RDO0000/AOA0000C331.pdf', 'mf0207': 'https://www.yageo.com/upload/media/product/productsearch/datasheet/lr/Yageo_LR_MF_1.pdf',
       'yr1b': 'https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocNm=1773204&DocType=DS', 'x7r1206': 'https://www.kemet.com/en/us/capacitors/ceramic.html'}
PARTS = {}
# heights above the board, mm (S1 level 1: <= 21.5). 'karta' = data sheet outline, 'szac.' = estimate to confirm at the 1:1 fit.
H = {'TO220': (20.5, 'karta TO-220: korpus z blaszka <= 16,5 + nozki skrocone do 4,0'), 'TO92': (8.5, 'karta TO-92 5,2 + nozki ok. 3'),
     'DIP': (8.5, 'podstawka 4,2 + DIP ok. 4,3'), 'SOIC': (1.75, 'karta SOIC-14'), 'R1206': (0.7, 'karta RC1206'), 'C1206': (1.8, 'karta X7R 1206 (max)'),
     'RV07': (10.0, 'szac.: DIN0207 6,3 pionowo + petla nozki'), 'RV04': (7.0, 'szac.: DIN0204 3,6 pionowo + petla nozki'),
     'D35': (7.0, 'szac.: DO-35 4,0 pionowo + petla nozki'), 'D15': (10.5, 'szac.: DO-15 7,6 pionowo + petla nozki'),
     'PR02': (5.0, 'karta PR02 D 3,9 lezacy + 1 mm od plytki'), 'P600': (9.1, 'karta P600 D 9,1 max, lezacy'),
     'CP5': (11.5, 'karta D5 x 11 + 0,5'), 'CP63': (11.7, 'karta D6,3 x 11,2 + 0,5'), 'CH16': (16.5, 'karta D16 x 25 lezacy + koszulka'),
     'K15': (6.5, 'karta Vishay K15 H5 + zagiecie'), 'B32': (6.5, 'karta TDK B32529 H6,5'), 'MKS2': (10.0, 'szac. z karty WIMA MKS2 1 uF/100 V P5'),
     'TSR': (10.7, 'karta TRACO TSR 2: 10,2 + 0,5'), 'BLADE': (17.5, 'szac.: bezpiecznik MINI 16,3 w zaciskach Keystone 3568'),
     'GMSTB': (16.0, 'szac.: GMSTBA z wtykiem GMSTB 2,5/3-ST-7,62 wlozonym poziomo'), 'IDC': (9.5, 'karta IDC 2x10 katowe 8,9 + wtyk tasmy'),
     'SVH': (3.0, 'karta goldpin katowy 1x13'), 'LED': (8.6, 'karta L-934 5,3 + 1 mm nozek + soczewka'), 'WIRE': (6.0, 'szac.: przewody lutowane w PTH'),
     'LINK': (1.0, 'drut 0,6 mm')}


def add(ref, src, sym, fp, display, mpn, pins, url='', note='', sheet='WEJ', on_board=True, vr=None, h=None):
    PARTS[ref] = {'ref': ref, 'source_ref': src, 'symbol': sym, 'footprint': fp, 'display': display, 'value': display, 'mpn': mpn,
                  'pins': {str(k): v for k, v in pins.items()}, 'url': url, 'note': note, 'qty': 1, 'sheet': sheet, 'on_board': on_board,
                  'v_rating': vr, 'height_mm': H[h][0] if h else None, 'height_src': H[h][1] if h else None}


# Resistor kinds. 'mf0207'/'yr1b'/'mf0204': owned THT from the P01 purchase (Zamowione/zamowione.csv), standing (S1 section 9);
# 'smd': new Yageo RC1206 1 %; 'erjp08': Panasonic ERJ-P08 anti-surge 1206 (0.66 W). Model tolerance stays 1 % / 100 ppm/K for all
# (as etap 1; the UVLO envelope accepted by the user is not narrowed by the 0.1 % YR1B parts).
RK = {'mf0207': (RV07, 'MF0207FTE52-{v}', '0.6W', .6, 250, 'RV07', 'mf0207', 'Owned THT (P01 purchase, TME MF0207FTE-{v}); standing.'),
      'yr1b': (RV07, 'YR1B{v}CC', '0.25W 0.1%', .25, 250, 'RV07', 'yr1b', 'Owned THT (P01 purchase, Mouser 279-YR1B{v}CC, 0.1 %); standing.'),
      'mf0204': (RV04, 'MF0204FTE52-{v}', '0.4W', .4, 200, 'RV04', 'mf0207', 'Owned THT (P01 purchase, TME MF0204FTE52-{v}); standing.'),
      'smd': (R1206, 'RC1206FR-07{v}L', '1206', .25, 200, 'R1206', 'rc1206', 'New SMD 1206 (S1 section 9).'),
      'erjp08': (R1206, 'ERJ-P08F{v}V', '1206 0.66W', .66, 200, 'R1206', 'erjp08', 'New SMD 1206 anti-surge 0.66 W (short of the PWR wire, L02).')}


def res(ref, src, val, a, b, sheet, note='', kind='smd'):
    fp, mpn, w, pw, vr, h, url, knote = RK[kind]
    code = {'1K': '1001', '10K': '1002'}.get(val, val) if kind == 'erjp08' else val
    add(ref, src, S_R, fp, f'{val} / {w}', mpn.format(v=code), {1: a, 2: b}, URL[url], (note + ' ' + knote.format(v=val)).strip(), sheet, vr=vr, h=h)
    PARTS[ref].update(tolerance=.01, tcr_ppm=100, p_rating_W=pw, r_kind=kind)


# ============ sheet WEJ: pack input, Q9 (Q_REV), Q1 (Q_SW), Q2 (Q_OFF), VSW, VMOTOR, hold-up C_H ============
add('J1', 'R4:NEW', conn(2), BATFP, 'BAT / soldered wires', 'PCB termination; 2 x 1.5 mm2 to XT60 (wall)', {1: 'P02_BAT_IN', 2: 'GND'},
    note='Pack 4S: XT60 male in the enclosure wall -> 2 x 1.5 mm2 -> J1 with strain-relief anchor 12.5 mm (footprint of P02 R3 J1). S1: at the input wall x = 106.5.', h='WIRE')
add('Q9', 'R4:NEW', S_PMOS, TO220, 'SUP53P06-20 / Q_REV', 'SUP53P06-20-E3', {1: 'P02_REV_G', 2: 'P02_BAT_IN', 3: 'P02_SW_COM'}, URL['sup53'],
    'Reverse-polarity switch, back-to-back with Q1 (sources at SW_COM). Drain at the pack: correct polarity -> body diode conducts, '
    'gate pulled to GND -> on; reversed pack -> VGS = 0, body diode blocks. No heatsink: 0.37 W at 3.5 A. Standing, leads cut to 4 mm.', vr=60, h='TO220')
res('R35', 'R4:NEW', '100K', 'P02_REV_G', 'GND', 'WEJ', 'Q9 gate to GND.', 'mf0207')
add('D10', 'R4:NEW', S_DZ, D35, 'BZX55C15 / Q9 VGS', 'BZX55C15-TAP', {1: 'P02_SW_COM', 2: 'P02_REV_G'}, URL['zener'], 'Clamp VSG of Q9 <= 15 V (K = source).', h='D35')
add('C1', 'P01R3:C1', S_CP, CP5, '10u / 63V', 'EEU-EB1J100SH', {1: 'P02_SW_COM', 2: 'GND'}, 'https://industrial.panasonic.com/cdbs/www-data/pdf/RDF0000/ABA0000C1209.pdf',
    'Local reservoir at SW_COM (P01 C1 at VS). Owned (P01 purchase).', vr=63, h='CP5')
add('C2', 'P01R3:C2', S_C, CB32, '100nF / 100V', 'B32529C1104J000', {1: 'P02_SW_COM', 2: 'GND'}, URL['b32529'], 'At Q1/Q2 sources. Owned.', vr=100, h='B32')
add('Q1', 'P01R3:Q1', S_PMOS, TO220, 'SUP53P06-20 / Q_SW', 'SUP53P06-20-E3', {1: 'P02_GATE', 2: 'P02_VSW', 3: 'P02_SW_COM'}, URL['sup53'],
    'Main switch (P01 Q1). Drain now to VSW directly (P01: via LK1 to VPROT). No heatsink: 0.37 W at 3.5 A. Standing, leads cut to 4 mm.', vr=60, h='TO220')
add('D4', 'P01R3:D4', S_DZ, D35, 'BZX55C15 / Q1 VSG', 'BZX55C15-TAP', {1: 'P02_SW_COM', 2: 'P02_GATE'}, URL['zener'], 'P01 D4.', h='D35')
add('C5', 'P01R3:C5', S_C, CB32, '10nF / 100V', 'B32529C1103J289', {1: 'P02_GATE', 2: 'P02_VSW'}, URL['b32529'],
    'Miller capacitor GATE-VSW (P01: GATE-VPROT); sets VSW slew ~12 V/ms with R21. Never above 22 nF (P01 R1 hot-plug blocker). Owned.', vr=100, h='B32')
add('C6', 'P01R3:C6', S_C, CMKS, '1uF / 100V', 'MKS2D041001K00JO00', {1: 'P02_GATE', 2: 'P02_SW_COM'}, URL['mks2'],
    'G-S capacitor; keeps VSG <= 0.3 V at hot plug (C5/(C5+C6)). Owned.', vr=100, h='MKS2')
res('R22', 'P01R3:R22', '470K', 'P02_GATE', 'P02_SW_COM', 'WEJ', 'Gate pull-up.', 'mf0207')
res('R21', 'P01R3:R21', '100K', 'P02_GATE', 'P02_ON_COL', 'WEJ', 'Turn-on current source with C5 (slew).', 'mf0207')
add('Q3', 'P01R3:Q3', S_NPN, TO92, '2N5551G', '2N5551G', {1: 'GND', 2: 'P02_ON_B', 3: 'P02_ON_COL'}, URL['npn'], 'Turn-on of Q1. Owned (2N5551TA).', h='TO92')
res('R17', 'P01R3:R17', '4K7', 'P02_ENABLE', 'P02_ON_B', 'WEJ', '', 'mf0207')
res('R18', 'P01R3:R18', '47K', 'P02_ON_B', 'GND', 'WEJ', '', 'mf0207')
add('Q2', 'P01R3:Q2', S_PMOS, TO220, 'SUP53P06-20 / Q_OFF', 'SUP53P06-20-E3', {1: 'P02_OFF_G', 2: 'P02_OFF_D', 3: 'P02_SW_COM'}, URL['sup53'],
    'Fast turn-off: pulls GATE to SW_COM through R27 when ENABLE is lost (P01 Q2). Standing, leads cut to 4 mm.', vr=60, h='TO220')
add('R27', 'P01R3:R27', S_R, RPR02, '10R / 2W', 'PR02000201009JA100', {1: 'P02_OFF_D', 2: 'P02_GATE'}, URL['pr02'], 'Limits C6 discharge current (P01 R27). Owned, lying.', vr=250, h='PR02')
PARTS['R27'].update(tolerance=.01, tcr_ppm=250, p_rating_W=2.0, r_kind='pr02')
res('R24', 'P01R3:R24', '100K', 'P02_OFF_G', 'P02_SW_COM', 'WEJ', '', 'mf0207')
res('R23', 'P01R3:R23', '22K', 'P02_OFF_G', 'GND', 'WEJ',
    'R4 change (user decision 29.09.2026): P01 2K2/2W -> 22K. Q2 is on while ENABLE is low; static loss 13 mW instead of 128 mW. '
    'Turn-off delay grows (docs/OBLICZENIA-R4.md); no OVP needs speed on a 4S pack.', 'smd')
add('D9', 'P01R3:D9', S_DZ, D35, 'BZX55C15 / Q2 VSG', 'BZX55C15-TAP', {1: 'P02_SW_COM', 2: 'P02_OFF_G'}, URL['zener'], 'P01 D9.', h='D35')
add('Q4', 'P01R3:Q4', S_PNP, TO92, '2N5401YBU', '2N5401YBU', {1: 'P02_SW_COM', 2: 'P02_REL_PB', 3: 'P02_OFF_G'}, URL['pnp'],
    'Holds Q2 off while ENABLE is high. onsemi 2N5401YBU E-B-C; never the -C bondout (P01 R3 note).', h='TO92')
res('R25', 'P01R3:R25', '47K', 'P02_REL_PB', 'P02_SW_COM', 'WEJ', '', 'mf0207')
res('R26', 'P01R3:R26', '10K', 'P02_REL_PB', 'P02_REL_COL', 'WEJ', '', 'mf0207')
add('Q5', 'P01R3:Q5', S_NPN, TO92, '2N5551G', '2N5551G', {1: 'GND', 2: 'P02_REL_B', 3: 'P02_REL_COL'}, URL['npn'], h='TO92')
res('R19', 'P01R3:R19', '4K7', 'P02_ENABLE', 'P02_REL_B', 'WEJ', '', 'mf0207')
res('R20', 'P01R3:R20', '47K', 'P02_REL_B', 'GND', 'WEJ', '', 'mf0207')
add('D3', 'P01R3:D3', S_DZ, TVS600, '5KP24A / VSW', '5KP24A (Littelfuse)', {1: 'P02_VSW', 2: 'GND'}, URL['5kp'],
    'Unidirectional TVS on VSW. R4E1-01 (user decision 29.09.2026): 5KP24A instead of 5KP18A: VR 24 V, VBR min 26.7 V, so a steady 25 V '
    '(5S pack by mistake, Z-01) does not drive it into breakdown; clamps to ~30-39 V at amps, below 50 V caps and 60 V MOSFETs. Lying P600.', vr=24, h='P600')
PARTS['D3']['vbr_min_V'] = 26.7
add('C3', 'R4:NEW', S_CP, CP63, '47u / 50V', 'EEUFR1H470', {1: 'P02_VSW', 2: 'GND'}, URL['fr'],
    'VSW reservoir (spec: <= 100 uF). Counts to the 220 uF budget together with VLOG caps and P07 input (docs/OBLICZENIA-R4.md). Owned (P01 C9 pair).', vr=50, h='CP63')
add('C4', 'P01R3:C4', S_C, CB32, '100nF / 100V', 'B32529C1104J000', {1: 'P02_VSW', 2: 'GND'}, URL['b32529'], 'At Q1 drain. Owned.', vr=100, h='B32')
add('F1', 'R4:NEW', S_F, BLADE, '5A / MINI 32V', 'Littelfuse 0297005.WXNV + Keystone 3568', {1: 'P02_VSW', 2: 'VMOTOR'}, URL['mini'],
    'F_M (D-04): automotive MINI blade 5 A, 32 VDC, in a PCB holder. VMOTOR <= 3.5 A continuous (firmware), OC 4 A.', vr=32, h='BLADE')
add('J2', 'P02R3:J2', conn(3), GMSTB, 'VMOTOR / GMSTBA 3p 7.62', 'Phoenix GMSTBA 2,5/3-G-7,62 (1766246)', {1: 'VMOTOR', 2: 'GND', 3: 'NC'}, URL['gmstb'],
    'P07 plug as R3. VMOTOR is now the switched pack (12-16.8 V) behind F1. S1: mating face at the input wall x = 106.5.', h='GMSTB')
add('D1', 'P02R3:D1', S_D2, TO220, 'STPS20100CT / D1a+D1b', 'STPS20100CT', {1: 'P02_VSW', 2: 'P02_VLOG', 3: 'P02_HOLD_C'}, URL['stps'],
    'OR of VSW (A1, D1a) and C_H (A2, D1b) into VLOG; K+tab = VLOG. Never a common-anode variant. Owned. Standing, leads cut to 4 mm.', vr=100, h='TO220')
add('R40', 'R4:NEW', S_R, RPR02, '22R / 2W fusible', 'Fusible flameproof 22R 2W (MPN to confirm, R4E1-05)', {1: 'P02_VSW', 2: 'P02_CH_A'}, URL['pr02'],
    'R_ch: charges C_H, tau 48 ms, peak 0.76 A, 0.31 J per charge. Must be a fusible (flameproof) type that survives the charge pulse; '
    'a shorted C_H would dissipate 12.8 W here. PR02 footprint (body 2 W class), lying 1 mm above the board.', vr=250, h='PR02')
PARTS['R40'].update(tolerance=.05, tcr_ppm=250, p_rating_W=2.0, r_kind='pr02')
add('D2', 'P02R3:D2', S_D2, TO220, 'STPS20100CT / D_ch', 'STPS20100CT', {1: 'P02_CH_A', 2: 'P02_HOLD_C', 3: 'P02_CH_A'}, URL['stps'],
    'Charge diode of C_H; anodes 1+3 tied on the PCB, K+tab = HOLD_C. Keeps C_H out of VSW, P07 and a VSW short. Owned. Standing.', vr=100, h='TO220')
add('C12', 'R4:NEW', S_CP, CH16, '2200u / 35V', 'EEUFR1V222 (16x25, P7.5) or equivalent low-ESR 105 C', {1: 'P02_HOLD_C', 2: 'GND'}, URL['fr'],
    'C_H hold-up (user decision 29.09.2026). 16 x 25 mm laid flat (S1: standing can + leads > 21.5 mm); glue or tie to the board.', vr=35, h='CH16')
res('R41', 'R4:NEW', '10K', 'P02_HOLD_C', 'GND', 'WEJ', 'C_H bleeder, 28 mW at 16.8 V, tau 22 s.', 'mf0207')
add('C20', 'P02R3:C4', S_CP, CP5, '22u / 50V', 'EEUFR1H220', {1: 'P02_VLOG', 2: 'GND'}, URL['fr'], 'VLOG bus at D1 cathode (R3 C4). Owned (P01 C7 pair).', vr=50, h='CP5')

# ============ sheet STER: AUX5, REF, UVLO, OK, ENABLE, PFAIL_N, SAFE_N/PG, LED ============
def ster(ref, *a, **k):
    add(ref, *a, sheet='STER', **k)


ster('D11', 'R4:NEW', S_D, D35, '1N4148 / SW_COM', '1N4148-TAP', {1: 'P02_V_CTRL', 2: 'P02_SW_COM'}, URL['4148'], 'V_CTRL = SW_COM OR VLOG: AUX5 lasts through hold-up.', vr=100, h='D35')
ster('D12', 'R4:NEW', S_D, D35, '1N4148 / VLOG', '1N4148-TAP', {1: 'P02_V_CTRL', 2: 'P02_VLOG'}, URL['4148'], vr=100, h='D35')
res('R1', 'P01R3:R1', '47R', 'P02_V_CTRL', 'P02_AUX_IN', 'STER',
    'P01: 150R/2W against car surges. Pack has none: 47R keeps AUX5 regulating down to VLOG ~6.5 V (9 mA, 4 mW).', 'smd')
ster('C7', 'P01R3:C7', S_CP, CP5, '22u / 50V', 'EEUFR1H220', {1: 'P02_AUX_IN', 2: 'GND'}, URL['fr'], 'Owned.', vr=50, h='CP5')
ster('C8', 'P01R3:C8', S_C, CK15, '100nF / X7R', 'K104K15X7RF5TH5', {1: 'P02_AUX_IN', 2: 'GND'}, URL['k15'], 'At U1 input. Owned.', vr=50, h='K15')
ster('U1', 'P01R3:U1', S_LDO, TO92, 'LM2936Z-5.0', 'LM2936Z-5.0/NOPB', {1: 'P02_AUX5', 2: 'GND', 3: 'P02_AUX_IN'}, URL['lm2936'], 'AUX5 for comparator, TL431, OK pull-up.', vr=40, h='TO92')
res('R2', 'P01R3:R2', '1R', 'P02_AUX5', 'P02_C_AUX_TOP', 'STER', 'ESR for LM2936 output stability (P01 R2).', 'mf0207')
ster('C9', 'P01R3:C9', S_CP, CP63, '47u / 50V', 'EEUFR1H470', {1: 'P02_C_AUX_TOP', 2: 'GND'}, URL['fr'], 'Owned.', vr=50, h='CP63')
ster('C10', 'P01R3:C10', S_C, CK15, '100nF / X7R', 'K104K15X7RF5TH5', {1: 'P02_AUX5', 2: 'GND'}, URL['k15'], 'At U1 output. Owned.', vr=50, h='K15')
ster('C11', 'P01R3:C11', S_C, CK15, '100nF / X7R', 'K104K15X7RF5TH5', {1: 'P02_AUX5', 2: 'GND'}, URL['k15'], 'At U2 pin 8. Owned.', vr=50, h='K15')
res('R3', 'P01R3:R3', '820R', 'P02_AUX5', 'P02_REF', 'STER', 'TL431 cathode current ~2.8 mA.', 'mf0207')
res('R4', 'P01R3:R4', '10K', 'P02_REF', 'GND', 'STER', '', 'yr1b')
ster('U3', 'P01R3:U3', S_REF, TO92, 'TL431BILP', 'TL431BILP', {1: 'P02_REF', 2: 'GND', 3: 'P02_REF'}, URL['tl431'], 'TI LP: 1=K 2=A 3=REF; 2.495 V.', h='TO92')
res('R5', 'R4:NEW', '1K', 'P02_SW_COM', 'P02_PWR_A', 'STER',
    'R_T1: limits current if the PWR wire shorts to GND (16.8 mA, 0.28 W: anti-surge 1206 rated 0.66 W). Part of the UVLO top branch; placed at SW_COM.', 'erjp08')
ster('J14', 'R4:NEW', conn(2), PWRFP, 'PWR / soldered wires', 'PCB termination; 2 x AWG22 to panel switch', {1: 'P02_PWR_A', 2: 'P02_PWR_B'},
     note='Panel switch in the UVLO top branch (Z-04): closed = on; open or broken wire = off. ~0.3 mA: gold-plated contacts (R4E1-04).', h='WIRE')
res('R9', 'R4:NEW', '41K2', 'P02_PWR_B', 'P02_UV_DIV', 'STER', 'R_T2 (STAN-PRAC: 41.2k).', 'smd')
res('R10', 'R4:NEW', '10K', 'P02_UV_DIV', 'GND', 'STER', 'R_B.', 'yr1b')
ster('C13', 'R4:NEW', S_C, C1206, '10nF / X7R', 'C1206C103K5RACTU', {1: 'P02_UV_DIV', 2: 'GND'}, URL['x7r1206'],
     'Filter before R12 (tau ~79 us), not on the feedback node (R3 lesson). New SMD 1206.', vr=50, h='C1206')
res('R12', 'R4:NEW', '10K', 'P02_UV_DIV', 'P02_UV_CMP', 'STER', 'R_iso: separates C13 from the hysteresis feedback.', 'yr1b')
res('R11', 'R4:NEW', '464K', 'P02_OK', 'P02_UV_CMP', 'STER', 'Rh: hysteresis from OK (0 / ~4.8 V).', 'smd')
ster('U2', 'P01R3:U2', S_CMP, DIP8, 'LM2903P', 'LM2903P',
     {1: 'P02_PFAIL_OC', 2: 'P02_REF', 3: 'P02_PF_IN', 4: 'GND', 5: 'P02_UV_CMP', 6: 'P02_REF', 7: 'P02_OK', 8: 'P02_AUX5'}, URL['lm2903'],
     'B: UVLO (P01 layout: 5=+ 6=REF 7=OK). A: PFAIL_N buffer of OK (3 = OK x 0.6, 2 = REF). Deviation from literal D-06 wording: '
     'A follows OK itself, so PFAIL_N can never disagree with the switch state (see docs/OBLICZENIA-R4.md). Owned, in the owned DIP-8 socket.', h='DIP')
res('R6', 'R4:NEW', '100K', 'P02_OK', 'P02_PF_IN', 'STER', 'OK divider for U2A: 0.6 x OK.', 'mf0207')
res('R7', 'R4:NEW', '150K', 'P02_PF_IN', 'GND', 'STER', '', 'smd')
res('R13', 'P01R3:R13', '2K2', 'P02_AUX5', 'P02_OK', 'STER', 'OK pull-up (P01).', 'mf0207')
ster('U4', 'P01R3:U4', S_SUP, TO92, 'MCP120-450DI/TO', 'MCP120-450DI/TO', {1: 'P02_OK', 2: 'P02_AUX5', 3: 'GND'}, URL['mcp120'],
     'POR of OK: holds OK low until AUX5 > 4.5 V + reset timeout (P01 U4).', h='TO92')
res('R14', 'P01R3:R14', '4K7', 'P02_OK', 'P02_BUF_D1', 'STER', '', 'mf0207')
ster('D7', 'P01R3:D7', S_D, D35, '1N4148', '1N4148-TAP', {1: 'P02_BUF_D2', 2: 'P02_BUF_D1'}, URL['4148'], vr=100, h='D35')
ster('D8', 'P01R3:D8', S_D, D35, '1N4148', '1N4148-TAP', {1: 'P02_BUF_BASE', 2: 'P02_BUF_D2'}, URL['4148'], vr=100, h='D35')
res('R15', 'P01R3:R15', '100K', 'P02_BUF_BASE', 'GND', 'STER', '', 'mf0207')
ster('Q6', 'P01R3:Q6', S_NPN, TO92, '2N5551G', '2N5551G', {1: 'P02_ENABLE', 2: 'P02_BUF_BASE', 3: 'P02_AUX5'}, URL['npn'], 'ENABLE emitter follower.', h='TO92')
res('R16', 'P01R3:R16', '10K', 'P02_ENABLE', 'GND', 'STER', '', 'mf0207')
res('R36', 'R4:NEW', '10K', '3V3_IO', 'P02_PFAIL_OC', 'STER', 'PFAIL_N pull-up to local 3V3_IO (low whenever 3V3_IO is absent).', 'smd')
res('R37', 'R4:NEW', '1K', 'P02_PFAIL_OC', 'PFAIL_N', 'STER', 'Series protection of J_BP.14.', 'smd')
ster('Q7', 'P01R3:Q7', S_NPN, TO92, '2N5551G', '2N5551G', {1: 'GND', 2: 'P02_FAULT_B', 3: 'SAFE_N'}, URL['npn'], 'SAFE_N open collector (P01 Q7).', h='TO92')
res('R30', 'P01R3:R30', '10K', 'P04_3V3', 'P02_FAULT_B', 'STER',
    'Fed from J_BP.15 (3V3 returned by P04), not from local 3V3_IO: SAFE_N = L whenever P04 is powered and ENABLE is absent (P01 behaviour).', 'mf0207')
res('R31', 'P01R3:R31', '100K', 'P02_FAULT_B', 'GND', 'STER', '', 'mf0207')
ster('Q8', 'P01R3:Q8', S_NPN, TO92, '2N5551G', '2N5551G', {1: 'GND', 2: 'P02_FAULT_REL_B', 3: 'P02_FAULT_B'}, URL['npn'], 'Releases SAFE_N on ENABLE.', h='TO92')
res('R32', 'P01R3:R32', '10K', 'P02_ENABLE', 'P02_FAULT_REL_B', 'STER', '', 'mf0207')
res('R33', 'P01R3:R33', '47K', 'P02_FAULT_REL_B', 'GND', 'STER', '', 'mf0207')
add('R34', 'P01R3:R34', S_R, LINK, '0R / link', 'Tinned copper wire 0.6 mm', {1: 'PG_SEND', 2: 'PG_LINK'}, '',
    'Presence link PG_SEND-PG_LINK (P01 R34), stays on this board (S1 section 8).', 'STER', h='LINK')
res('R29', 'P01R3:R29', '6K8', 'P02_VSW', 'P02_LED_A', 'STER', 'LED PWR ~2 mA at 16.8 V; also bleeds VSW when Q1 is off.', 'mf0204')
ster('LED1', 'P01R3:LED1', S_LED, LED, 'GREEN 3mm / PWR', 'L-934GD', {1: 'GND', 2: 'P02_LED_A'}, URL['l934'], 'Lit while Q1 is on (VSW present).', h='LED')

# ============ sheet LV: TSR converters and J_BP (edge A, pinout S1 section 8) ============
def lv(ref, *a, **k):
    add(ref, *a, sheet='LV', **k)


lv('F2', 'P02R3:F2', S_F, BLADE, '1A / MINI 32V', 'Littelfuse 0297001.WXNV + Keystone 3568', {1: 'P02_VLOG', 2: 'P02_VIN_DC5'}, URL['mini'],
   'D-04: automotive MINI 1 A, 32 VDC (R3: Schurter SPT T1A). <= 0.86 A at 7 V for the 6 W budget.', vr=32, h='BLADE')
lv('F3', 'P02R3:F3', S_F, BLADE, '1A / MINI 32V', 'Littelfuse 0297001.WXNV + Keystone 3568', {1: 'P02_VLOG', 2: 'P02_VIN_DC33'}, URL['mini'], 'D-04.', vr=32, h='BLADE')
lv('U5', 'P02R3:U1', S_TSR50, TSR, 'TSR 2-2450', 'TSR 2-2450', {1: 'P02_VIN_DC5', 2: 'GND', 3: '5V_SYS'}, URL['tsr2'], 'Input 6.5-36 V; design floor 7 V.', vr=36, h='TSR')
lv('U6', 'P02R3:U2', S_TSR33, TSR, 'TSR 2-2433', 'TSR 2-2433', {1: 'P02_VIN_DC33', 2: 'GND', 3: '3V3_IO'}, URL['tsr2'], '3V3_IO only; never tie to 3V3_CORE of P03.', vr=36, h='TSR')
lv('C21', 'P02R3:C5', S_CP, CP5, '10u / 50V', 'EEUFR1H100', {1: 'P02_VIN_DC5', 2: 'GND'}, URL['fr'], vr=50, h='CP5')
lv('C22', 'P02R3:C6', S_CP, CP5, '22u / 16V', 'EEUFR1C220', {1: '5V_SYS', 2: 'GND'}, URL['fr'], vr=16, h='CP5')
lv('C23', 'P02R3:C7', S_CP, CP5, '10u / 50V', 'EEUFR1H100', {1: 'P02_VIN_DC33', 2: 'GND'}, URL['fr'], vr=50, h='CP5')
lv('C24', 'P02R3:C8', S_CP, CP5, '22u / 16V', 'EEUFR1C220', {1: '3V3_IO', 2: 'GND'}, URL['fr'], vr=16, h='CP5')
JBP = {1: 'GND', 2: '5V_SYS', 3: 'GND', 4: '5V_SYS', 5: 'GND', 6: '5V_SYS', 7: 'GND', 8: '3V3_IO', 9: 'GND', 10: '3V3_IO',
       11: 'GND', 12: 'PSU_OK', 13: 'GND', 14: 'PFAIL_N', 15: 'P04_3V3', 16: 'SAFE_N', 17: 'PG_SEND', 18: 'PG_LINK', 19: 'GND', 20: 'VBAT_SENSE'}
lv('J_BP', 'R4:NEW', symbol('Connector_Generic', 'Conn_02x10_Odd_Even'), IDC, 'J_BP / IDC 2x10 angled', 'Wurth 61202021621 (shrouded IDC 2x10, right angle, Au) or equivalent',
   JBP, URL['idc'], 'Edge A, slot S3 of the board (x = 80.0 mm), taped to P12 (S1 section 5). Pinout S1 section 8; replaces LV03..LV10, J11, J12, J13 and J16 of etap 1. '
   '5V_SYS on 3 pins (IDC ~1 A per contact).', vr=250, h='IDC')

# ============ sheet MON: PSU_OK (P02 R3), VBAT of the car (J15) ============
def mon(ref, *a, **k):
    add(ref, *a, sheet='MON', **k)


mon('U7', 'P02R3:U3', S_SUP, TO92, 'MCP120-300DI/TO', 'MCP120-300DI/TO', {1: 'P02_SUP3_N', 2: '3V3_IO', 3: 'GND'}, URL['mcp120'], 'Variant D: 1=RST 2=VDD 3=VSS; open drain. Owned.', h='TO92')
mon('U8', 'P02R3:U4', S_SUP, TO92, 'MCP120-450DI/TO', 'MCP120-450DI/TO', {1: 'P02_SUP5_RAW', 2: '5V_SYS', 3: 'GND'}, URL['mcp120'], 'Variant D: 1=RST 2=VDD 3=VSS; open drain. Owned.', h='TO92')
res('R42', 'P02R3:R2', '10K', 'P02_SUP3_N', '3V3_IO', 'MON', '', 'mf0207')
res('R43', 'P02R3:R3', '10K', 'P02_SUP5_RAW', '5V_SYS', 'MON', '', 'mf0207')
mon('C25', 'P02R3:C9', S_C, CK15, '100nF / X7R', 'K104K15X7RF5TH5', {1: '3V3_IO', 2: 'GND'}, URL['k15'], 'At U7. Owned.', vr=50, h='K15')
mon('C26', 'P02R3:C10', S_C, CK15, '100nF / X7R', 'K104K15X7RF5TH5', {1: '5V_SYS', 2: 'GND'}, URL['k15'], 'At U8. Owned.', vr=50, h='K15')
mon('U9', 'P02R3:U5', S_BUF, SOIC14, '74LVC125A / SO14', '74LVC125AD,118 (Nexperia)',
    {1: 'GND', 2: 'P02_SUP5_RAW', 3: 'P02_SUP5_N', 4: '3V3_IO', 5: 'GND', 6: 'NC', 7: 'GND', 8: 'NC', 9: 'GND', 10: '3V3_IO', 11: 'NC', 12: 'GND', 13: '3V3_IO', 14: '3V3_IO'},
    URL['lvc125'], 'As R3 U5: 5 V RST to 3.3 V logic. Unused OE#=3V3_IO, inputs=GND. S1: SOIC-14 soldered directly (no adapter; S1 section 9). Owned.', h='SOIC')
mon('C27', 'P02R3:C11', S_C, C1206, '100nF / X7R', 'C1206C104K5RACTU', {1: '3V3_IO', 2: 'GND'}, URL['x7r1206'], 'At U9 pin 14. New SMD 1206.', vr=50, h='C1206')
mon('C28', 'P02R3:C16', S_C, C1206, '100nF / X7R', 'C1206C104K5RACTU', {1: '3V3_IO', 2: 'GND'}, URL['x7r1206'],
    'Second 100 nF at U9 (was on the SO14 adapter in R3); now on the board next to pin 14. New SMD 1206.', vr=50, h='C1206')
mon('U10', 'P02R3:U6', S_AND, DIP14, 'SN74HC08N', 'SN74HC08N',
    {1: 'P02_SUP3_N', 2: 'P02_SUP5_N', 3: 'PSU_OK', 4: 'GND', 5: 'GND', 6: 'NC', 7: 'GND', 8: 'NC', 9: 'GND', 10: 'GND', 11: 'NC', 12: 'GND', 13: 'GND', 14: '3V3_IO'},
    URL['hc08'], 'Gate A = PSU_OK (as R3). HOLD_READY gates of R3 removed: gates B-D inputs to GND, outputs open. Owned, in an owned DIP-14 socket.', h='DIP')
mon('C29', 'P02R3:C12', S_C, CK15, '100nF / X7R', 'K104K15X7RF5TH5', {1: '3V3_IO', 2: 'GND'}, URL['k15'], 'At U10. Owned.', vr=50, h='K15')
res('R44', 'P02R3:R4', '10K', 'PSU_OK', 'GND', 'MON', 'PSU_OK low while U10 is unpowered.', 'yr1b')
mon('J15', 'R4:NEW', conn(1), VBATFP, 'VBAT_IN / soldered wire', 'PCB termination; 1 x AWG22', {1: 'VBAT_CAR'},
    note='D-01/Z-12: one wire from the car battery + terminal in the engine bay, 1 A in-line fuse <= 10 cm from the terminal (R4E1-06); NO ground wire. '
         'S1: top corner at the input wall; no own anchor, tie the wire to the J1 anchor next to it.', h='WIRE')
res('R38', 'R4:NEW', '10K', 'VBAT_CAR', 'VBAT_SENSE', 'MON', 'Limits TVS current; CH7 multiplier 6.0898 -> 6.1918 (+1.67 %, recalibrate).', 'smd')
mon('D13', 'R4:NEW', S_TVS, D15, 'P6KE24CA / VBAT', 'P6KE24CA', {1: 'VBAT_SENSE', 2: 'GND'}, URL['p6ke'], 'Bidirectional, VWM 20.5 V, VC 33.2 V.', vr=20.5, h='D15')

# ============ sheet SERW: service headers on edge B (S1 section 6) ============
# pin -> (node net, series resistor, class); pin 1 and 13 are GND. Classes (S1 section 6): 1K logic / rails <= 5 V,
# 4K7 pack rails (<= 16.8 V: 3.6 mA, 60 mW into a short), 10K high-impedance nodes (dividers, gates, references).
SV = {'J_SV1': {2: ('P02_ENABLE', 'R55', '1K'), 3: ('P02_SUP5_N', 'R60', '1K'), 4: ('PSU_OK', 'R71', '1K'), 5: ('SAFE_N', 'R57', '1K'),
                6: ('P04_3V3', 'R58', '1K'), 7: ('P02_UV_CMP', 'R53', '10K'), 8: ('P02_OK', 'R54', '1K'), 9: ('P02_AUX5', 'R50', '1K'),
                10: ('PFAIL_N', 'R56', '1K'), 11: ('P02_REF', 'R51', '10K'), 12: ('P02_UV_DIV', 'R52', '10K')},
      'J_SV2': {2: ('P02_GATE', 'R63', '10K'), 3: ('VBAT_SENSE', 'R59', '10K'), 4: ('VMOTOR', 'R66', '4K7'), 5: ('P02_BAT_IN', 'R61', '4K7'),
                6: ('3V3_IO', 'R70', '1K'), 7: ('P02_OFF_G', 'R64', '10K'), 8: ('P02_SW_COM', 'R62', '4K7'), 9: ('P02_VSW', 'R65', '4K7'),
                10: ('P02_VLOG', 'R68', '4K7'), 11: ('5V_SYS', 'R69', '1K'), 12: ('P02_HOLD_C', 'R67', '4K7')}}
# Pin order follows the x position of the nodes on the board (pin 1 of the angled header is at the larger x), so the
# service lines do not cross; left-half nodes go to J_SV1 (slot S2), right-half nodes to J_SV2 (slot S3).


def svnet(node):
    return 'P02_SV_' + node.removeprefix('P02_')


for hdr, pins in SV.items():
    for n, (node, r, val) in pins.items():
        res(r, 'R4:NEW', val, node, svnet(node), 'SERW', f'Series resistor of {hdr}.{n} ({node.removeprefix("P02_")}), placed at the node (S1 section 6).', 'smd')
    slot = 'S2' if hdr == 'J_SV1' else 'S3'
    add(hdr, 'R4:NEW', conn(13), SVH, f'{hdr} / goldpin 1x13 angled', 'Goldpin 1x13 2.54 mm right angle (e.g. Wurth 61301311021 or cut from 1x40)',
        {1: 'GND', **{n: svnet(v[0]) for n, v in pins.items()}, 13: 'GND'}, URL['hdr'],
        f'Service header, edge B, slot {slot} of the level (S1 section 6): pins 1 and 13 GND, every other pin behind a series resistor; pins stick out ~6 mm.',
        'SERW', vr=250, h='SVH')

# voltage ratings (Z-14) of parts without one above: 2N5551 VCEO 160 V, 2N5401 VCEO 150 V, GMSTBA 320 V
for r in ('Q3', 'Q5', 'Q6', 'Q7', 'Q8'): PARTS[r]['v_rating'] = 160
PARTS['Q4']['v_rating'] = 150; PARTS['J2']['v_rating'] = 320
PARTS['R34'].update(tolerance=0, tcr_ppm=0, r_kind='link')
assert all(p['height_mm'] for p in PARTS.values() if p['on_board']), [r for r, p in PARTS.items() if not p['height_mm']]


def write_tables():
    clean = {r: {k: v for k, v in p.items() if k != 'symbol'} for r, p in PARTS.items()}
    (P / 'docs/parts.json').write_text(json.dumps(clean, ensure_ascii=False, indent=2), encoding='utf-8')
    fields = ['ref', 'source_ref', 'display', 'mpn', 'qty', 'footprint', 'height_mm', 'sheet', 'on_board', 'url', 'note']
    with (P / 'docs/BOM.csv').open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fields, delimiter=';', extrasaction='ignore'); w.writeheader(); w.writerows(PARTS.values())
    libs = {p['symbol'][1]: p['symbol'] for p in PARTS.values()}; libs['P02:PWR_FLAG'] = symbol('power', 'PWR_FLAG')
    (P / 'eda/libraries/P02.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor")' + ''.join(dump([s[0], s[1].split(':')[1]] + s[2:]) for s in libs.values()) + ')', encoding='utf-8')
    (P / 'eda/sym-lib-table').write_text('(sym_lib_table (lib (name "P02") (type "KiCad") (uri "${KIPRJMOD}/libraries/P02.kicad_sym") (options "") (descr "P02 symbols")))', encoding='utf-8')
    flibs = sorted({p['footprint'].split(':')[0] for p in PARTS.values() if p['footprint']})
    (P / 'eda/fp-lib-table').write_text('(fp_lib_table ' + ''.join(f'(lib (name {q(l)}) (type "KiCad") (uri "${{KIPRJMOD}}/libraries/{l}.pretty") (options "") (descr "P02 selected footprint"))' for l in flibs) + ')', encoding='utf-8')
