"""P00 R2 parts: source_ref tracks v6.1 or the revision that introduced the part.
R2 corrects the input range to 6..15 V and adds R5/R6 after the R1 review.
Footprints come from KiCad 10.0.6 or the local hashed input library; no sibling project is read.
"""
from cadlib import *
import shutil, json, csv, hashlib
FP = P / 'eda/libraries/P00.pretty'; FP.mkdir(parents=True, exist_ok=True)
LOCAL_INPUTS = P / 'input/footprints'
FP_HASHES = json.loads((P / 'input/footprints-sha256.json').read_text())


def copyfp(lib, name):
    src = K / 'footprints' / (lib + '.pretty') / (name + '.kicad_mod'); assert src.exists(), src
    dest = P / 'eda/libraries' / (lib + '.pretty'); dest.mkdir(parents=True, exist_ok=True); shutil.copy2(src, dest / src.name)
    return lib + ':' + name


def localfp(name):
    source = LOCAL_INPUTS / (name + '.kicad_mod')
    assert hashlib.sha256(source.read_bytes()).hexdigest() == FP_HASHES[source.name], source
    shutil.copy2(source, FP / source.name)
    return 'P00:' + name


RFP = copyfp('Resistor_THT', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal')  # Yageo MF0207 body 6.3 x 2.5 mm
C100N = localfp('C_Vishay_K15_H5_P5'); TO220 = localfp('TO220_3_P2.54_Drill1.4'); TP1FP = localfp('TestPad_1')
CP5 = copyfp('Capacitor_THT', 'CP_Radial_D5.0mm_P2.00mm'); LED = copyfp('LED_THT', 'LED_D3.0mm')
DIP8 = copyfp('Package_DIP', 'DIP-8_W7.62mm'); DO41 = copyfp('Diode_THT', 'D_DO-41_SOD81_P10.16mm_Horizontal')
SLIDE = copyfp('Button_Switch_THT', 'SW_Slide-03_Wuerth-WS-SLTV_10x2.5x6.4_P2.54mm')
HDR2 = copyfp('Connector_PinHeader_2.54mm', 'PinHeader_1x02_P2.54mm_Vertical')
MKDS = copyfp('TerminalBlock_Phoenix', 'TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal')

S_R = symbol('Device', 'R'); S_C = symbol('Device', 'C'); S_CP = symbol('Device', 'C_Polarized'); S_LED = symbol('Device', 'LED')
S_DS = symbol('Device', 'D_Schottky'); S_TP = symbol('Connector', 'TestPoint'); S_555 = symbol('Timer', 'TLC555xP', 'TLC555CP')
S_LDO = symbol('Regulator_Linear', 'LM2937xT', 'LM2937ET-3.3'); S_J2 = symbol('Connector_Generic', 'Conn_01x02')
# Wurth WS-SLTV 450301014042: COM is the MIDDLE pin 1, throws are 2 (left) and 3 (right) - datasheet and KiCad
# footprint agree. The generic KiCad SW_SPDT symbol has its common on pin 2, so its pins are renumbered:
# B (common) -> 1, A -> 2, C -> 3. Without this the symbol would wire a throw to the common pad.
S_SW = symbol('Switch', 'SW_SPDT', 'SW_SPDT_WS-SLTV')
for pin in pin_defs(S_SW).values():
    n = one(pin, 'number'); n[1] = {'2': '1', '1': '2', '3': '3'}[n[1]]
URL = {'tlc555': 'https://www.ti.com/lit/ds/symlink/tlc555.pdf', 'lm2937': 'https://www.mouser.com/datasheet/2/405/lm2937-3.3-484674.pdf',
       'wsltv': 'https://www.we-online.com/components/products/datasheet/450301014042.pdf', '1n5819': 'https://www.vishay.com/docs/88525/1n5817.pdf',
       'k15': 'https://www.vishay.com/docs/45171/kseries.pdf', 'fr': 'https://industrial.panasonic.com/sa/products/pt/aluminum-cap-lead',
       'l934': 'https://www.kingbrightusa.com/images/catalog/SPEC/L-934GD.pdf', 'mkds': 'https://www.phoenixcontact.com/en-pl/products/pcb-terminal-block-mkds-15-2-508-1715721',
       'mf0207': 'https://yageogroup.com/content/Resource%20Library/Datasheet/YAGEO-MFR_DATASHEET.pdf',
       'l934id': 'https://asset.conrad.com/media10/add/160267/c1/-/gl/812265765DS00/datenblatt-2888735-kingbright-l-934id-led-bedrahtet-rot-rund-3-mm-20-mcd-40-30-ma-2-v.pdf',
       'l934yd': 'https://www.activecomponents.com/dbdocument/1208518/K491106-DS.pdf'}
PARTS = {}


def add(ref, src, sym, fp, display, mpn, pins, url='', note='', sheet='P00'):
    PARTS[ref] = {'ref': ref, 'source_ref': src, 'symbol': sym, 'footprint': fp, 'display': display, 'value': display, 'mpn': mpn,
                  'pins': {str(k): v for k, v in pins.items()}, 'url': url, 'note': note, 'qty': 1, 'sheet': sheet, 'on_board': True}


def res(ref, src, value, mpn, pins, note=''):
    add(ref, src, S_R, RFP, value, mpn, pins, URL['mf0207'], note)


# ---- power: VIN 6..15 V -> reverse-polarity Schottky -> LM2937 3.3 V ------------------------------
add('J10', 'J_PWR', S_J2, MKDS, 'VIN 6-15V / MKDS 2p', 'Phoenix MKDS 1,5/2-5,08 (1715721)', {1: 'P00_VIN', 2: 'GND'}, URL['mkds'],
    'R2 correction after review: bench supply 6..15 V; recommended 9..12 V. 1 = +VIN, 2 = GND.')
add('D1', 'ADDED_P00R1_LDO', S_DS, DO41, '1N5819', '1N5819', {1: 'P00_VIN_P', 2: 'P00_VIN'}, URL['1n5819'],
    'Reverse-polarity protection of C4 and the rail (LM2937 itself survives reverse input). Band = cathode.')
add('C4', 'ADDED_P00R1_LDO', S_CP, CP5, '10u / 50V', 'EEUFR1H100', {1: 'P00_VIN_P', 2: 'GND'}, URL['fr'], 'Input bulk after D1.')
add('C5', 'ADDED_P00R1_LDO', S_C, C100N, '100nF / X7R', 'K104K15X7RF53H5', {1: 'P00_VIN_P', 2: 'GND'}, URL['k15'], 'At U2 input (datasheet: 0.1 uF).')
add('U2', 'ADDED_P00R1_LDO', S_LDO, TO220, 'LM2937ET-3.3', 'LM2937ET-3.3/NOPB', {1: 'P00_VIN_P', 2: 'GND', 3: 'P00_V33'}, URL['lm2937'],
    'TO-220: 1 = IN, 2 = GND (tab), 3 = OUT. TI SNVS015F: VIN at U2 >= 4.75 V, IOUT >= 5 mA. J10 range 6..15 V; Cout >= 10 uF, branch ESR 0.01..3 ohm.')
add('C6', 'ADDED_P00R1_LDO', S_CP, CP5, '22u / 50V', 'EEUFR1H220', {1: 'P00_V33', 2: 'P00_COUT_RET'}, 'https://industrial.panasonic.com/ww/products/pt/aluminum-cap-lead/models/EEUFR1H220', 'D5 x L11, pitch 2 mm. R6 adds 1 ohm series resistance in the C6 return; qualify stability at the bench.')
add('C7', 'ADDED_P00R1_LDO', S_C, C100N, '100nF / X7R', 'K104K15X7RF53H5', {1: 'P00_V33', 2: 'GND'}, URL['k15'], 'At U2 output.')
res('RL10', 'ADDED_P00R1_LED', '1K / 1%', 'MFR-25FRF52-1K', {1: 'P00_V33', 2: 'P00_LED_PWR'}, 'Power LED ~1.4 mA.')
add('LED10', 'ADDED_P00R1_LED', S_LED, LED, 'RED 3mm / 3V3', 'L-934ID', {1: 'GND', 2: 'P00_LED_PWR'}, URL['l934id'], 'On = 3.3 V present.')
res('R5', 'ADDED_P00R2_PRELOAD', '560R / 1%', 'MFR-25FRF52-560R', {1: 'P00_V33', 2: 'GND'}, 'Permanent minimum load. >= 5.55 mA at 3.14 V and +1% R; 0.25 W DIN0207.')
res('R6', 'ADDED_P00R2_COUT_ESR', '1R / 1%', 'MFR-25FRF52-1R', {1: 'P00_COUT_RET', 2: 'GND'}, '1 ohm in C6 return sets a positive lower bound of branch ESR. Not in the DC supply path. 0.25 W DIN0207.')
# ---- heartbeat (v6.1: TLC555 astable ~102 Hz) + R1 run/stop switch ---------------------------------
add('U1', 'U1', S_555, DIP8, 'TLC555CP', 'TLC555CP', {1: 'GND', 2: 'P00_RC', 3: 'P00_OSC', 4: 'P00_RESET', 5: 'P00_CTRL', 6: 'P00_RC', 7: 'P00_DIS', 8: 'P00_V33'},
    URL['tlc555'], 'In a DIP8 socket (insert after checking the 3.3 V rail). f = 1.44/((R1 + 2 R2) C1) = 102 Hz.')
res('R1', 'R1', '4K7 / 1%', 'MFR-25FRF52-4K7', {1: 'P00_V33', 2: 'P00_DIS'})
res('R2', 'R2', '68K / 1%', 'MFR-25FRF52-68K', {1: 'P00_DIS', 2: 'P00_RC'})
add('C1', 'C1', S_C, C100N, '100nF / X7R', 'K104K15X7RF53H5', {1: 'P00_RC', 2: 'GND'}, URL['k15'], 'Timing; X7R +-10 %: measure f (ODBIOR P00).')
add('C2', 'C2', S_C, C100N, '10nF / X7R', 'K103K15X7RF53H5', {1: 'P00_CTRL', 2: 'GND'}, URL['k15'])
add('C3', 'C3', S_C, C100N, '100nF / X7R', 'K104K15X7RF53H5', {1: 'P00_V33', 2: 'GND'}, URL['k15'], 'At U1 pin 8.')
res('R3', 'R3', '1K / 1%', 'MFR-25FRF52-1K', {1: 'P00_OSC', 2: 'P00_HEART'}, 'Series 1 k of the heartbeat output (v6.1).')
res('R4', 'ADDED_P00R1_HBSTOP', '100K / 1%', 'MFR-25FRF52-100K', {1: 'P00_V33', 2: 'P00_RESET'}, 'Keeps RESET high while SW9 moves (break-before-make).')
add('SW9', 'ADDED_P00R1_HBSTOP', S_SW, SLIDE, 'HEART RUN/STOP', 'Wurth 450301014042 (WS-SLTV)', {1: 'P00_RESET', 2: 'P00_V33', 3: 'GND'}, URL['wsltv'],
    'R1 addition: RUN = RESET high (v6.1 behaviour), STOP = RESET low -> output held LOW (stuck heartbeat for the watchdog test).')
res('RL9', 'ADDED_P00R1_LED', '1K / 1%', 'MFR-25FRF52-1K', {1: 'P00_OSC', 2: 'P00_LED_HB'}, 'Heartbeat LED on the 555 output, before R3.')
add('LED9', 'ADDED_P00R1_LED', S_LED, LED, 'YELLOW 3mm / HEART', 'L-934YD', {1: 'GND', 2: 'P00_LED_HB'}, URL['l934yd'], 'Lit at ~50 % while running.')
add('J9', 'J_HEART', S_J2, HDR2, 'HEART / pin header 1x2', 'pin header 1x2, 2.54 mm (goldpin)', {1: 'P00_HEART', 2: 'GND'}, '',
    'R1 (user 25.09): 2.54 mm header for Dupont leads. 1 = heartbeat via 1 k, 2 = GND.')
# ---- eight 3.3 V / GND sources (v6.1) + state LED (R1) ---------------------------------------------
for i in range(1, 9):
    add(f'SW{i}', f'SW{i}', S_SW, SLIDE, f'CH{i} H/L', 'Wurth 450301014042 (WS-SLTV)', {1: f'P00_S{i}', 2: 'P00_V33', 3: 'GND'}, URL['wsltv'],
        'COM = pin 1 (middle). Opposite-side connection: slider towards pin 3 = COM-pin 2 (3V3) = H.')
    res(f'RS{i}', f'RS{i}', '1K / 1%', 'MFR-25FRF52-1K', {1: f'P00_S{i}', 2: f'P00_OUT{i}'}, 'Series 1 k: nominal ground-short current 3.3 mA; <= 3.51 mA including voltage, 1% tolerance and 100ppm/C over 10..40C. Intended for 3.3 V logic inputs.')
    res(f'RL{i}', 'ADDED_P00R1_LED', '1K / 1%', 'MFR-25FRF52-1K', {1: f'P00_S{i}', 2: f'P00_LED{i}'}, 'State LED from the switch node, not from the output.')
    add(f'LED{i}', 'ADDED_P00R1_LED', S_LED, LED, f'GREEN 3mm / CH{i}', 'L-934GD', {1: 'GND', 2: f'P00_LED{i}'}, URL['l934'], 'On = channel HIGH.')
    add(f'J{i}', f'J{i}', S_J2, HDR2, f'CH{i} / pin header 1x2', 'pin header 1x2, 2.54 mm (goldpin)', {1: f'P00_OUT{i}', 2: 'GND'}, '',
        'R1 (user 25.09): 2.54 mm header for Dupont leads. 1 = output via 1 k, 2 = GND.')
for idx, net in enumerate(['P00_V33', 'GND', 'P00_VIN_P'], 1):
    r = f'TP{idx}'
    PARTS[r] = {'ref': r, 'source_ref': 'ADDED_TESTPAD', 'value': net, 'display': net.replace('P00_', ''), 'pins': {'1': net}, 'symbol': S_TP,
                'footprint': TP1FP, 'mpn': 'PCB test pad', 'qty': 1, 'url': '', 'sheet': 'P00', 'on_board': True, 'note': 'Probe access; no circuit function.'}


def write_tables():
    clean = {r: {k: v for k, v in p.items() if k != 'symbol'} for r, p in PARTS.items()}
    (P / 'docs/parts.json').write_text(json.dumps(clean, ensure_ascii=False, indent=2), encoding='utf-8')
    fields = ['ref', 'source_ref', 'display', 'mpn', 'qty', 'footprint', 'url', 'note']
    with (P / 'docs/BOM.csv').open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fields, delimiter=';', extrasaction='ignore'); w.writeheader(); w.writerows(PARTS.values())
    libs = {p['symbol'][1]: p['symbol'] for p in PARTS.values()}; libs[PRJ + ':PWR_FLAG'] = symbol('power', 'PWR_FLAG')
    (P / 'eda/libraries/P00.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor")' + ''.join(dump([s[0], s[1].split(':')[1]] + s[2:]) for s in libs.values()) + ')', encoding='utf-8')
    (P / 'eda/sym-lib-table').write_text('(sym_lib_table (lib (name "P00") (type "KiCad") (uri "${KIPRJMOD}/libraries/P00.kicad_sym") (options "") (descr "P00 symbols")))', encoding='utf-8')
    flibs = sorted({p['footprint'].split(':')[0] for p in PARTS.values() if p['footprint']})
    (P / 'eda/fp-lib-table').write_text('(fp_lib_table ' + ''.join(f'(lib (name {q(l)}) (type "KiCad") (uri "${{KIPRJMOD}}/libraries/{l}.pretty") (options "") (descr "P00 selected footprint"))' for l in flibs) + ')', encoding='utf-8')
