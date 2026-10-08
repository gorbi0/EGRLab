"""M1-R1 explicit circuit (single source): one board for LOGGER + TESTER, simplified S1 (Plytki/M1-specyfikacja/AUDYT.md, SPECYFIKACJA.md,
user decisions D-M1-1...13, 8.10.2026). Aware user: no user-error protection, no inter-board interfaces, no service strips (test pads),
no per-board supervisors / LDOs. Wires soldered to the board (pads + tie anchors), one screw strip X1 in the enclosure, glands outside.
Parts carried over from S1 keep their S1 reference in source_ref ('P05:U1' = P05 R3 U1, 'P07:RSH1', ...); 'M1:NEW' = new in M1.

Kept functions (F1-F10): AD7606B 8 channels (P05) with the motor current from the INA240 on CH6 (P06 / P07 shunt, one path for
LOGGER and TESTER - D-M1-7), 2 x MAX31856 modules (P09), passive CAN (P10), IBT-2 control through a 74AHCT125 (P07), switched 5 V
sensor supply TPS2553 (P08), ESP32-S3 DEV-KIT + microSD module (P03), TSR 2-2450 / 2-2433 + MINI fuse (P02).
GPIO numbering as firmware 6.2-s1 board.c where the signal survived (SPECYFIKACJA.md 3); LPWM on GPIO21 (GPIO38 drives the module RGB LED)."""
from cadlib import *
import csv, shutil
FP = P / 'eda/libraries/M1.pretty'; FP.mkdir(parents=True, exist_ok=True); PARTS = {}
G = 'GND'; V5 = '5V'; V3 = '3V3'; VB = 'VBUS'; A5 = '5VA'
NEW = 'nowe'; REG = 'rejestr'


def copyfp(lib, name):
    src = K / 'footprints' / (lib + '.pretty') / (name + '.kicad_mod'); assert src.exists(), src
    dest = P / 'eda/libraries' / (lib + '.pretty'); dest.mkdir(parents=True, exist_ok=True); shutil.copy2(src, dest / src.name)
    return lib + ':' + name


def custom(name, units):
    # rows: (pin, name, electrical type) left / right; explicit function symbols (P07 S1 cadlib style), physical pin numbers
    s = f'(symbol "M1:{name}" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)'
    for u, (left, right) in enumerate(units, 1):
        h = max(len(left), len(right)) + 1; half = 12.7
        s += f'(symbol "{name}_{u}_1" (rectangle (start {-half} {h * 1.27}) (end {half} {-h * 1.27}) (stroke (width .254) (type default)) (fill (type background))))'
        s += f'(symbol "{name}_{u}_0"'
        for side, items in [(-1, left), (1, right)]:
            for j, (n, label, typ) in enumerate(items):
                s += (f'(pin {typ} line (at {side * (half + 5.08)} {(h - 2 - j * 2) * 1.27} {0 if side == -1 else 180}) (length 5.08) '
                      f'(name {q(label)} (effects (font (size 1.0 1.0)))) (number "{n}" (effects (font (size 1 1)))))')
        s += ')'
    return parse(s + ')')


def tail(name, n, pitch, drill, pad, anchors=True):
    """Soldered wire pads in one row (P06 R2 / P07 tail): pad 1 square; optional two tie-anchor holes 12 mm behind the row."""
    pts = [(i + 1, i * pitch, 0, drill, pad) for i in range(n)]
    if anchors:
        pts += [('', -3.5, -12, 3.2, 3.2), ('', (n - 1) * pitch + 3.5, -12, 3.2, 3.2)]
    xmax = (n - 1) * pitch
    s = f'(footprint {q(name)} (version 20240108) (generator "pcbnew") (layer "F.Cu") (attr through_hole)'
    for num, x, y, d, w in pts:
        s += f'(pad "{num}" {"thru_hole" if num else "np_thru_hole"} {"rect" if num == 1 else "circle"} (at {x} {y}) (size {w} {w}) (drill {d}) (layers "*.Cu" "*.Mask"))'
    s += f'(fp_rect (start -5.5 {-14 if anchors else -pad / 2 - .5}) (end {xmax + 5.5} {pad / 2 + .5}) (stroke (width .05) (type default)) (fill none) (layer "F.CrtYd"))'
    s += f'(fp_text reference "REF**" (at {xmax / 2} {pad / 2 + 2}) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15)))))'
    (FP / (name + '.kicad_mod')).write_text(s); return 'M1:' + name


R1206 = copyfp('Resistor_SMD', 'R_1206_3216Metric_Pad1.30x1.75mm_HandSolder'); C1206 = copyfp('Capacitor_SMD', 'C_1206_3216Metric_Pad1.33x1.80mm_HandSolder')
C1210 = copyfp('Capacitor_SMD', 'C_1210_3225Metric')   # as P05 R3 (its U1 layout is reused; the hand-solder pads collide there)
SO8 = copyfp('Package_SO', 'SOIC-8_3.9x4.9mm_P1.27mm'); SO14 = copyfp('Package_SO', 'SOIC-14_3.9x8.7mm_P1.27mm'); SOT23 = copyfp('Package_TO_SOT_SMD', 'SOT-23')
SOT236 = copyfp('Package_TO_SOT_SMD', 'SOT-23-6'); QFP = copyfp('Package_QFP', 'LQFP-64_10x10mm_P0.5mm')
TSR = copyfp('Converter_DCDC', 'Converter_DCDC_TRACO_TSR2-xxxx_THT'); BLADE = copyfp('Fuse', 'Fuseholder_Blade_Mini_Keystone_3568')
TP = copyfp('TestPoint', 'TestPoint_Pad_D1.5mm')
ESPFP = 'M1:Waveshare_ESP32-S3-DEV-KIT_2x22_W22.86'; SDFP = 'M1:Adafruit_4682_microSD_1x09'; TCFP = 'M1:MAX31856_XU'
SHUNT_FP = 'M1:R_Shunt_Vishay_WSK2512_T1.19mm_SenseE1.70'


def add(ref, src, sym, fp, value, mpn, pins, sheet, url='', note='', zrodlo=NEW, **extra):
    PARTS[ref] = dict(ref=ref, source_ref=src, symbol=sym, footprint=fp, display=value, value=value, mpn=mpn, pins={str(k): v for k, v in pins.items()},
                      sheet=sheet, url=url, note=note, qty=1, on_board=True, zrodlo=zrodlo, **extra)


SR = symbol('Device', 'R'); SC = symbol('Device', 'C'); STP = symbol('Connector', 'TestPoint')


def code(value): return value.replace('.', 'K', 1)[:-1] if value.endswith('K') and '.' in value else value


def res(r, src, val, ohms, a, b, sh, tol=.01, note=''):
    if tol == .001:
        add(r, src, SR, R1206, val, 'RT1206BRD07' + code(val) + 'L', {1: a, 2: b}, sh, note=note or 'Thin film 1206 0.1 % 25 ppm/K (Yageo RT, as P05 R3).', ohms=ohms, tolerance=tol, tcr_ppm=25)
    else:
        add(r, src, SR, R1206, val, 'RC1206FR-07' + code(val) + 'L', {1: a, 2: b}, sh, note=note, ohms=ohms, tolerance=tol)


def cap(r, src, val, farad, a, b, sh, mpn=None, note='', volts=50, fp=None):
    add(r, src, SC, fp or C1206, val, mpn or ('SMD 1206 C0G 50V 5% ' if farad < 1.1e-8 else 'SMD 1206 X7R 50V 10% ') + val, {1: a, 2: b}, sh, farads=farad, volts=volts, note=note)


# ================= sheet M1 (root, ZASILANIE): pack in, MINI fuse, TSR 5 V / 3.3 V, VMOTOR out (F9) =================
add('J1', 'P02:J1', symbol('Connector_Generic', 'Conn_01x02'), tail('PAD_BAT', 2, 7.62, 2.4, 4.5), 'BAT / pola', '2 x 2.0 mm2 from X1.1 / X1.2 (pack behind the BMS)',
    {1: 'BAT_P', 2: G}, 'M1', note='X1.1 BAT+ (via the power switch on the enclosure, off board), X1.2 BAT-. Pack minus = board GND (single ground, D-M1-7 note).')
add('F1', 'P02:F1', symbol('Device', 'Fuse'), BLADE, '7.5A / MINI 32V', 'Littelfuse 0297007.WXNV + Keystone 3568 (MINI holder, soldered)', {1: 'BAT_P', 2: VB},
    'M1', note='D-M1-13: MINI 7.5 A in a soldered holder (as the 5.10 decision for P02). The only protection kept on the supply (A: wiring / pack fire).')
add('J2', 'P02:J2', symbol('Connector_Generic', 'Conn_01x01'), tail('PAD_VMOTOR', 1, 7.62, 2.4, 4.5), 'VMOTOR / pole', '2.0 mm2 to X1.3 -> IBT-2 B+',
    {1: VB}, 'M1', note='IBT-2 B+ behind F1; IBT-2 B- goes to the pack minus on X1 (motor return current never crosses the board).')
tsr = custom('TSR2_SIP3', [([(1, '+VIN', 'power_in'), (2, 'GND', 'power_in')], [(3, '+VOUT', 'power_out')])])
add('U1', 'P02:U5', tsr, TSR, 'TSR 2-2450', 'TRACO TSR 2-2450 (5 V 2 A, 6.5-36 V in)', {1: VB, 2: G, 3: V5}, 'M1', 'https://www.tracopower.com/products/tsr2.pdf',
    'Was P02 R4 U5 (5V_SYS). Load ~0.45 A peak (SPECYFIKACJA 4).')
add('U2', 'P02:U6', tsr, TSR, 'TSR 2-2433', 'TRACO TSR 2-2433 (3.3 V 2 A)', {1: VB, 2: G, 3: V3}, 'M1', 'https://www.tracopower.com/products/tsr2.pdf',
    'Peripherals 3.3 V (SD, MAX31856, AD7606B VDRIVE, TCAN1051 VIO). ESP32 runs from its module LDO (5 V in).')
cap('C1', 'M1:NEW', '4.7u', 4.7e-6, VB, G, 'M1', mpn='SMD 1206 X7R 50V 10% 4.7u', note='TSR inputs (pack wires ~0.5 m).')
cap('C2', 'M1:NEW', '10u', 1e-5, V5, G, 'M1', mpn='SMD 1206 X7R 16V 10% 10u', volts=16)
cap('C3', 'M1:NEW', '10u', 1e-5, V3, G, 'M1', mpn='SMD 1206 X7R 16V 10% 10u', volts=16)
# ================= sheet MCU: ESP32-S3 DEV-KIT (owned), microSD module (owned) (F8, F10) =================
J1N = ['3V3', '3V3', 'RST', 'GPIO4', 'GPIO5', 'GPIO6', 'GPIO7', 'GPIO15', 'GPIO16', 'GPIO17', 'GPIO18', 'GPIO8', 'GPIO3', 'GPIO46', 'GPIO9',
       'GPIO10', 'GPIO11', 'GPIO12', 'GPIO13', 'GPIO14', '5V', 'GND']
J3N = ['GND', 'GPIO43_TX', 'GPIO44_RX', 'GPIO1', 'GPIO2', 'GPIO42', 'GPIO41', 'GPIO40', 'GPIO39', 'GPIO38_RGB', 'GPIO37', 'GPIO36', 'GPIO35', 'GPIO0',
       'GPIO45', 'GPIO48', 'GPIO47', 'GPIO21', 'GPIO20_DP', 'GPIO19_DM', 'GND', 'GND']
# GPIO -> net (SPECYFIKACJA 3); forbidden pins stay NC (verify_m1.py checks the list)
GPIO = {4: 'SPI3_SCK', 5: 'SPI3_MOSI', 6: 'SPI3_MISO', 7: 'SD_CS', 8: 'TC1_CS', 16: 'TC2_CS', 9: 'ADC_SCLK', 11: 'ADC_DOUTA', 2: 'ADC_SDI', 12: 'ADC_CS',
        13: 'ADC_CONVST', 14: 'ADC_BUSY', 10: 'ADC_RESET', 17: 'NC', 18: 'CAN_RXD', 1: 'RPWM', 21: 'LPWM', 39: 'DRIVE_EN', 40: 'SENS_EN',
        42: 'SENS_FAULT_N', 15: 'BTN', 41: 'SCOPE_TRIG', 3: 'GPIO3_TP'}


def pinnet(nm):
    if nm in ('5V',): return V5
    if nm == 'GND': return G
    if nm.startswith('GPIO'):
        n = int(nm[4:].split('_')[0]); return GPIO.get(n, 'NC')
    return 'NC'   # 3V3 (module LDO output: not fed back), RST


espsym = custom('Waveshare_ESP32-S3-DEV-KIT', [([(f'J1-{i + 1}', n, 'power_in' if n in ('5V', 'GND') else ('passive' if n in ('3V3', 'RST') else 'bidirectional')) for i, n in enumerate(J1N)],
                                                [(f'J3-{i + 1}', n, 'power_in' if n == 'GND' else 'bidirectional') for i, n in enumerate(J3N)])])
add('M1', 'P03:M1', espsym, ESPFP, 'Waveshare ESP32-S3-DEV-KIT-N32R16V', 'owned (Waveshare ESP32-S3-DEV-KIT-N32R16V), soldered on 2 x 1x22 pin headers (D-M1-12)',
    {f'J1-{i + 1}': pinnet(n) for i, n in enumerate(J1N)} | {f'J3-{i + 1}': pinnet(n) for i, n in enumerate(J3N)}, 'MCU', 'https://www.waveshare.com/wiki/ESP32-S3-DEV-KIT-N8R8',
    'GPIO map SPECYFIKACJA 3 (6.2-s1 numbering). 5 V in at J1-21; module 3V3 not connected to the board 3.3 V. Status LED = module RGB on GPIO38.', zrodlo=REG)
sdsym = custom('Adafruit_4682_microSD', [([(1, '3V', 'power_in'), (2, 'GND', 'power_in'), (3, 'CLK', 'input'), (5, 'SI', 'input'), (6, 'CS', 'input')],
                                          [(4, 'SO', 'tri_state'), (7, 'D1', 'passive'), (8, 'DAT2', 'passive'), (9, 'DET', 'passive')])])
add('SD1', 'P03:SD1', sdsym, SDFP, 'Adafruit 4682 microSD (3V)', 'owned Adafruit 4682, soldered by its 1x9 header (D-M1-11)',
    {1: V3, 2: G, 3: 'SPI3_SCK', 4: 'SPI3_MISO', 5: 'SPI3_MOSI', 6: 'SD_CS', 7: 'NC', 8: 'NC', 9: 'NC'}, 'MCU', 'https://www.adafruit.com/product/4682', zrodlo=REG)
res('R1', 'M1:NEW', '10K', 10000, 'SD_CS', V3, 'MCU', note='SD CS idle high at reset.')
res('R2', 'P07:R3', '4.7K', 4700, 'DRIVE_EN', G, 'MCU', note='D-M1-4: bridge disabled while the ESP32 is in reset / booting. 4.7k, not 100k: GPIO39 (MTCK) has the '
    'internal ~45k pull-up after reset (ESP32-S3 datasheet v2.2 table 2-1 note 7, EFUSE_DIS_PAD_JTAG = 0) until the firmware takes the pin; 100k gave ~2.3 V '
    '(HIGH for the 74AHCT125, VIH 2.0 V). 4.7k: <= 0.63 V even with a 20k pull-up (VIL 0.8 V). Review of firmware PR #17, 8.10.')
res('R3', 'M1:NEW', '100K', 100000, 'RPWM', G, 'MCU'); res('R4', 'M1:NEW', '100K', 100000, 'LPWM', G, 'MCU')
res('R5', 'P08:NEW', '100K', 100000, 'SENS_EN', G, 'MCU', note='Sensor 5 V off while the ESP32 is in reset (no 5 V onto an ECU line in LOGGER).')
add('J3', 'M1:NEW', symbol('Connector_Generic', 'Conn_01x02'), tail('PAD_BTN', 2, 2.54, 1.0, 1.8, anchors=False), 'BTN / pola', '2 x 0.25 mm2 to the START/STOP push button on the enclosure',
    {1: 'BTN', 2: G}, 'MCU', note='Soldered wires (no connector).')
res('R6', 'M1:NEW', '10K', 10000, 'BTN', V3, 'MCU'); cap('C4', 'M1:NEW', '100n', 1e-7, 'BTN', G, 'MCU', note='RC 1 ms against bounce / pickup on the wire.')
# ================= sheet ADC: AD7606B, 8 channels (F1, F2, F5) — P05 R3 strapping =================
di = [(i, n, 'input') for i, n in [(3, 'OS0'), (4, 'OS1'), (5, 'OS2'), (6, 'SER'), (7, 'STBY'), (8, 'RANGE'), (9, 'CONVST'), (10, 'WR'), (11, 'RESET'), (12, 'SCLK'), (13, 'CS_N'), (29, 'SDI')]]
do = [(14, 'BUSY', 'output'), (15, 'FRSTDATA', 'output'), (24, 'DOUTA', 'tri_state'), (25, 'DOUTB', 'tri_state'), (27, 'DOUTC', 'tri_state'), (28, 'DOUTD', 'tri_state')]
unused = [(i, 'DB' + str({**{x: x - 16 for x in range(16, 23)}, 30: 12, 31: 13, 32: 14, 33: 15}[i]) + '_SER_GND', 'passive') for i in [16, 17, 18, 19, 20, 21, 22, 30, 31, 32, 33]]
ap = [(49 + 2 * i, 'V' + str(i + 1), 'input') for i in range(8)]; ag = [(50 + 2 * i, 'V' + str(i + 1) + 'GND', 'input') for i in range(8)]
pl = [(1, 'AVCC1', 'power_in'), (37, 'AVCC37', 'power_in'), (38, 'AVCC38', 'power_in'), (48, 'AVCC48', 'power_in'), (23, 'VDRIVE', 'power_in'), (34, 'REF_SEL', 'input'),
      (42, 'REFIN_OUT', 'passive'), (36, 'REGCAP_A', 'passive'), (39, 'REGCAP_D', 'passive'), (44, 'REFCAPA', 'passive'), (45, 'REFCAPB', 'passive')]
pr = [(i, 'AGND', 'power_in') for i in [2, 26, 35, 40, 41, 47]] + [(43, 'REFGND', 'power_in'), (46, 'REFGND', 'power_in')]
adc = custom('AD7606BBSTZ_SERIAL', [(di, do + unused), (ap, ag), (pl, pr)])
ap_ = {str(i): G for i in [2, 26, 35, 40, 41, 47, 43, 46] + [16, 17, 18, 19, 20, 21, 22, 30, 31, 32, 33] + list(range(50, 65, 2))}
ap_.update({str(i): V3 for i in [3, 4, 5, 6, 7, 8, 10, 23, 34]})          # OS = 111 (x8), SER, STBY, RANGE (+-10 V), WR (software mode), VDRIVE, REF_SEL (internal)
ap_.update({'1': A5, '37': A5, '38': A5, '48': A5, '9': 'ADC_CONVST', '11': 'ADC_RESET', '12': 'ADC_SCLK', '13': 'ADC_CS', '14': 'ADC_BUSY', '15': 'NC',
            '24': 'ADC_DOUTA', '25': 'NC', '27': 'NC', '28': 'NC', '29': 'ADC_SDI', '36': 'REGCAP_A', '39': 'REGCAP_D', '42': 'ADC_REF', '44': 'REFCAP', '45': 'REFCAP'})
ap_.update({str(49 + 2 * i): f'ADC_CH{i + 1}' for i in range(8)})
add('U3', 'P05:U1', adc, QFP, 'AD7606BBSTZ', 'AD7606BBSTZ', ap_, 'ADC', 'https://www.analog.com/media/en/technical-documentation/data-sheets/AD7606B.pdf',
    'As P05 R3 U1: OS=111 serial software mode, internal reference, one DOUTA line; DOUTA straight to the ESP32 (no bus, no buffer).', zrodlo=REG)
res('R7', 'P05:R1', '1R', 1, V5, A5, 'ADC', note='AVCC filter (P05 R3 R1, here 1206: ~25 mA).')
cap('C5', 'P05:C35', '10u', 1e-5, A5, G, 'ADC', mpn='SMD 1206 X7R 16V 10% 10u', volts=16)
for i, pin in enumerate([1, 37, 38, 48, 23], 6):
    cap(f'C{i}', f'P05:C{i - 2}', '100n', 1e-7, V3 if pin == 23 else A5, G, 'ADC', note=f'At U3 pin {pin}.')
cap('C11', 'P05:C9', '1u', 1e-6, 'REGCAP_A', G, 'ADC'); cap('C12', 'P05:C10', '1u', 1e-6, 'REGCAP_D', G, 'ADC')
cap('C13', 'P05:C11', '100n', 1e-7, 'ADC_REF', G, 'ADC')
cap('C14', 'P05:C12', '22u', 22e-6, 'ADC_REF', G, 'ADC', mpn='C3225X7R1E226M250AB (TDK 22u 25V X7R 1210)', volts=25, fp=C1210)
cap('C15', 'P05:C13', '22u', 22e-6, 'REFCAP', G, 'ADC', mpn='C3225X7R1E226M250AB (TDK 22u 25V X7R 1210)', volts=25, fp=C1210)
res('R8', 'P05:R26', '33R', 33, 'ADC_DOUTA_U', 'ADC_DOUTA', 'ADC', note='DOUTA source damping at the ADC (P05 R26).')
PARTS['U3']['pins']['24'] = 'ADC_DOUTA_U'
res('R9', 'P05:R17', '10K', 10000, 'ADC_RESET', G, 'ADC', note='Reset held low while the ESP32 boots (P05 R3 R17).')
res('R10', 'P05:R13', '47K', 47000, 'ADC_CS', V3, 'ADC')
# channels (P05 R3 electrical-checks: MOTOR 300k / 100k, SENSOR 100k series, VSENSE 499k / 100k; 220p at the pin; AD7606B 1 Mohm input)
CH = [(1, 'P1_EGR', 'MOTOR'), (2, 'P3', 'MOTOR'), (3, 'P4', 'SENSOR'), (4, 'P5', 'SENSOR'), (5, 'P6', 'SENSOR'), (7, 'VBAT_CAR', 'VSENSE'), (8, 'SENS_5V', 'SENSOR')]
nr, nc = 11, 16
for ch, src, cls in CH:
    top = {'MOTOR': ('300K', 300000), 'SENSOR': ('100K', 100000), 'VSENSE': ('499K', 499000)}[cls]
    res(f'R{nr}', 'P05:TAPS', top[0], top[1], src, f'ADC_CH{ch}', 'ADC', tol=.001, note=f'CH{ch} {cls} series (in S1 on the TAPS adapter / P05).'); nr += 1
    if cls in ('MOTOR', 'VSENSE'):
        res(f'R{nr}', 'P05:RB', '100K', 100000, f'ADC_CH{ch}', G, 'ADC', tol=.001, note=f'CH{ch} {cls} divider bottom.'); nr += 1
    cap(f'C{nc}', 'P05:CF', '220p', 220e-12, f'ADC_CH{ch}', G, 'ADC'); nc += 1
res(f'R{nr}', 'M1:NEW', '1K', 1000, 'I_MOT', 'ADC_CH6', 'ADC', note='INA240 output to CH6 (was the 10k-terminated reserve in S1).'); RCH6 = f'R{nr}'; nr += 1
cap(f'C{nc}', 'M1:NEW', '1n', 1e-9, 'ADC_CH6', G, 'ADC', note='RC 1 us with the 1k (anti-alias above the AD7606B x8 filter).'); nc += 1
# ================= sheet PRAD: shunt + Kelvin + INA240 (F2, F6) — P06 R2 / P07 S1 =================
add('RSH1', 'P07:RSH1', symbol('Device', 'R_Shunt', 'R_Shunt_2512_Kelvin'), SHUNT_FP, '5m / 1% / 2512 Kelvin', 'WSK25125L000FEA (Vishay WSK2512, 5 mOhm 1 %, 1 W at 70 C)',
    {1: 'P1_ECU', 2: 'K_PLUS', 3: 'K_MINUS', 4: 'P1_EGR'}, 'PRAD', note='In P1 between X1.5 and X1.6: ECU (LOGGER) or IBT-2 M+ (TESTER) -> valve. 3.5 A: 61 mW; 10 A: 0.5 W.',
    ohms=.005, tolerance=.01, power_w=1.0)
res(f'R{nr}', 'P07:R6', '10R', 10, 'K_PLUS', 'INA_PLUS', 'PRAD', tol=.001); RK1 = f'R{nr}'; nr += 1
res(f'R{nr}', 'P07:R7', '10R', 10, 'K_MINUS', 'INA_MINUS', 'PRAD', tol=.001); RK2 = f'R{nr}'; nr += 1
ina = custom('INA240A2_D_SOIC', [([(8, 'IN+', 'input'), (1, 'IN-', 'input'), (6, 'VS', 'power_in'), (7, 'REF1', 'input'), (3, 'REF2', 'input')], [(5, 'OUT', 'output'), (2, 'GND', 'power_in'), (4, 'NC', 'no_connect')])])
add('U4', 'P07:U1', ina, SO8, 'INA240A2', 'INA240A2EDRQ1', {1: 'INA_MINUS', 2: G, 3: G, 4: 'NC', 5: 'I_MOT', 6: V5, 7: V5, 8: 'INA_PLUS'}, 'PRAD',
    'https://www.ti.com/lit/ds/symlink/ina240.pdf', 'Owned (register). 50 V/V; REF1 = VS, REF2 = GND -> output at VS / 2 (bidirectional, data sheet 8.3.3); '
    '0.25 V/A, linear about +-9 A (output 0.2 V from the rails), above F1 7.5 A. Zero recorded by firmware with the motor off (no reference buffer).', zrodlo=REG)
cap(f'C{nc}', 'P07:C22', '100n', 1e-7, V5, G, 'PRAD', note='At U4 VS.'); nc += 1
# ================= sheet TEMP_CAN: 2 x MAX31856 modules (F3), MISO buffer, passive CAN (F4) =================
mod = custom('MAX31856_MODULE', [([(1, 'VIN', 'power_in'), (3, 'GND', 'power_in'), (4, 'SCK', 'input'), (6, 'SDI', 'input'), (7, 'CS_N', 'input')],
                                  [(2, '3Vo', 'passive'), (5, 'SDO', 'tri_state'), (8, 'FLT_N', 'output'), (9, 'DRDY_N', 'output')])])
for k in (1, 2):
    add(f'TC{k}', f'P09:J{k + 2}', mod, TCFP, f'TC{k} / MAX31856 XU', 'owned MAX31856 XU module, soldered directly by its 1x9 header (measured 8.10: fits)',
        {1: f'TC{k}_VIN', 2: 'NC', 3: G, 4: 'SPI3_SCK', 5: f'TC{k}_SDO', 6: 'SPI3_MOSI', 7: f'TC{k}_CS', 8: 'NC', 9: 'NC'}, 'TEMP_CAN',
        'https://allegro.pl/oferta/max31856-modul-termopary-dla-typow-k-j-n-r-s-t-e-b-19-bitowy-modul-xu-18805671895',
        'Thermocouple wires through their own gland straight to the module terminal (D-M1-8), not through X1.', zrodlo=REG)
    res(f'R{nr}', 'P09:JP', '0R', 0, V3, f'TC{k}_VIN', 'TEMP_CAN', note='VIN = 3.3 V (fit). MODUL-KWALIFIKACJA 2-3: if 3Vo < 3.0 V at VIN 3.3 V, fit the 5 V link instead.'); nr += 1
    res(f'R{nr}', 'P09:JP', '0R', 0, V5, f'TC{k}_VIN', 'TEMP_CAN', note='DNP by default (VIN = 5 V option, see the 3.3 V link).'); PARTS[f'R{nr}']['dnp'] = True; nr += 1
lvc = custom('74LVC125A_SO14', [([(2, '1A', 'input'), (1, '1OE_N', 'input'), (5, '2A', 'input'), (4, '2OE_N', 'input'), (9, '3A', 'input'), (10, '3OE_N', 'input'),
                                  (12, '4A', 'input'), (13, '4OE_N', 'input'), (14, 'VCC', 'power_in')], [(3, '1Y', 'tri_state'), (6, '2Y', 'tri_state'), (8, '3Y', 'tri_state'), (11, '4Y', 'tri_state'), (7, 'GND', 'power_in')])])
add('U5', 'P09:U1', lvc, SO14, '74LVC125AD', '74LVC125AD,118 (Nexperia)', {1: 'TC1_CS', 2: 'TC1_SDO', 3: 'SPI3_MISO', 4: 'TC2_CS', 5: 'TC2_SDO', 6: 'SPI3_MISO',
    7: G, 8: 'NC', 9: G, 10: V3, 11: 'NC', 12: G, 13: V3, 14: V3}, 'TEMP_CAN', 'https://assets.nexperia.com/documents/data-sheet/74LVC125A.pdf',
    'Function, not protection: the module SDO (level shifter) is not guaranteed Hi-Z with CS high; the shared SPI3 MISO (SD card) needs it (P09 R2 reason). OE = CS of each module.', zrodlo=REG)
cap(f'C{nc}', 'P09:C1', '100n', 1e-7, V3, G, 'TEMP_CAN', note='At U5.'); nc += 1
for k in (1, 2):
    res(f'R{nr}', 'P09:R', '10K', 10000, f'TC{k}_CS', V3, 'TEMP_CAN', note='Module CS idle high (buffer off).'); nr += 1
tcan = custom('TCAN1051V_SOIC8', [([(1, 'TXD', 'input'), (8, 'S', 'input'), (3, 'VCC', 'power_in'), (5, 'VIO', 'power_in')], [(4, 'RXD', 'output'), (7, 'CANH', 'bidirectional'), (6, 'CANL', 'bidirectional'), (2, 'GND', 'power_in')])])
add('U6', 'P10:U1', tcan, SO8, 'TCAN1051V', 'TCAN1051VDRQ1', {1: V3, 2: G, 3: V5, 4: 'CAN_RX_U', 5: V3, 6: 'CAN_L', 7: 'CAN_H', 8: V3}, 'TEMP_CAN',
    'https://www.ti.com/lit/ds/symlink/tcan1051-q1.pdf', 'As P10 R2: S and TXD hard-wired to VIO (silent, cannot transmit); V variant (VIO 3.3 V).', zrodlo=REG)
res(f'R{nr}', 'P10:R1', '100R', 100, 'CAN_RX_U', 'CAN_RXD', 'TEMP_CAN'); nr += 1
add('D1', 'P10:D1', custom('PESD2CAN_SOT23', [([(1, 'L1', 'passive'), (2, 'L2', 'passive')], [(3, 'COM', 'passive')])]), SOT23, 'PESD2CAN', 'PESD2CAN,215 Nexperia',
    {1: 'CAN_L', 2: 'CAN_H', 3: G}, 'TEMP_CAN', note='Kept (A, 2 parts): ESD at the bus entry.', zrodlo=REG)
cap(f'C{nc}', 'P10:C1', '100n', 1e-7, V5, G, 'TEMP_CAN', note='At U6 VCC.'); nc += 1
cap(f'C{nc}', 'P10:C2', '100n', 1e-7, V3, G, 'TEMP_CAN', note='At U6 VIO.'); nc += 1
# ================= sheet NAPED: IBT-2 control (F6), sensor 5 V (F7) =================
ahct = custom('74AHCT125_SO14', [([(2, '1A', 'input'), (1, '1OE_N', 'input'), (5, '2A', 'input'), (4, '2OE_N', 'input'), (9, '3A', 'input'), (10, '3OE_N', 'input'),
                                   (12, '4A', 'input'), (13, '4OE_N', 'input'), (14, 'VCC', 'power_in')], [(3, '1Y', 'tri_state'), (6, '2Y', 'tri_state'), (8, '3Y', 'tri_state'), (11, '4Y', 'tri_state'), (7, 'GND', 'power_in')])])
add('U7', 'P07:U16', ahct, SO14, '74AHCT125D', '74AHCT125D,118 (Nexperia; TTL inputs, VCC 5 V)', {1: G, 2: 'RPWM', 3: 'IBT_RPWM', 4: G, 5: 'LPWM', 6: 'IBT_LPWM', 7: G,
    8: 'IBT_REN', 9: 'DRIVE_EN', 10: G, 11: 'IBT_LEN', 12: 'DRIVE_EN', 13: G, 14: V5}, 'NAPED', 'https://assets.nexperia.com/documents/data-sheet/74AHCT125.pdf',
    '3.3 -> 5 V for the module 74HC244 (VIH ~3.5 V at 5 V). Always enabled; ESP32 pins pulled down (R2-R4): all module inputs low in reset.')
cap(f'C{nc}', 'P07:C36', '100n', 1e-7, V5, G, 'NAPED', note='At U7.'); nc += 1
add('J4', 'P07:J5', symbol('Connector_Generic', 'Conn_01x06'), tail('PAD_IBT', 6, 2.54, 1.0, 1.8), 'IBT-2 / pola', '6 x 0.25 mm2 to the IBT-2 2x4 header (soldered)',
    {1: 'IBT_RPWM', 2: 'IBT_LPWM', 3: 'IBT_REN', 4: 'IBT_LEN', 5: V5, 6: G}, 'NAPED',
    note='IBT-2 header: 1 RPWM, 2 LPWM, 3 R_EN, 4 L_EN, 7 VCC, 8 GND (R_IS / L_IS 5 / 6 unused: current from the INA240). No connector on the board.')
tps = custom('TPS2553_SOT23_6', [([(1, 'IN', 'power_in'), (3, 'EN', 'input'), (5, 'ILIM', 'passive')], [(6, 'OUT', 'power_out'), (4, 'FAULT_N', 'open_collector'), (2, 'GND', 'power_in')])])
add('U8', 'P08:U1', tps, SOT236, 'TPS2553DBVR', 'TPS2553DBVR', {1: V5, 2: G, 3: 'SENS_EN', 4: 'SENS_FAULT_N', 5: 'ILIM', 6: 'SENS_5V'}, 'NAPED',
    'https://www.ti.com/lit/ds/symlink/tps2553.pdf', 'Sensor 5 V for TESTER, current limited, enabled from GPIO40 (off in LOGGER). Active-high EN version.', zrodlo=REG)
res(f'R{nr}', 'P08:R', '232K', 232000, 'ILIM', G, 'NAPED', note='Current limit as P08 R2 (R_ILIM 232k).'); nr += 1
res(f'R{nr}', 'P08:R', '10K', 10000, 'SENS_FAULT_N', V3, 'NAPED'); nr += 1
cap(f'C{nc}', 'P08:C', '100n', 1e-7, V5, G, 'NAPED', note='At U8 IN.'); nc += 1
cap(f'C{nc}', 'P08:C', '1u', 1e-6, 'SENS_5V', G, 'NAPED', note='At U8 OUT.'); nc += 1
# ================= sheet LISTWA: wire pads in X1 order (contract docs/X1.csv) =================
add('J5', 'M1:NEW', symbol('Connector_Generic', 'Conn_01x02'), tail('PAD_P1', 2, 7.62, 2.4, 4.5), 'P1 ECU / EGR / pola', '2 x 2.0 mm2 to X1.5 / X1.6',
    {1: 'P1_ECU', 2: 'P1_EGR'}, 'LISTWA', note='The only line through the board (shunt). LOGGER: X1.5 from the ECU; TESTER: X1.5 = IBT-2 M+.')
SIG = [(1, 'P3'), (2, 'P4'), (3, 'P5'), (4, 'P6'), (5, 'SENS_5V'), (6, G), (7, 'VBAT_CAR'), (8, 'CAN_H'), (9, 'CAN_L'), (10, G)]
add('J6', 'M1:NEW', symbol('Connector_Generic', 'Conn_01x10'), tail('PAD_SIG', 10, 5.08, 1.2, 2.4), 'X1.7-16 / pola', '10 thin wires (0.25-0.5 mm2) to X1.7 ... X1.16',
    {k: n for k, n in SIG}, 'LISTWA', note='Taps P3-P6 (ECU and valve wires share one X1 screw each), SENS_5V, GND (car ground reference in LOGGER), VBAT_CAR, CAN H / L / GND.')
TPS_ = [('TP1', V5), ('TP2', V3), ('TP3', VB), ('TP4', G), ('TP5', 'I_MOT'), ('TP6', 'SCOPE_TRIG'), ('TP7', 'GPIO3_TP'), ('TP8', 'ADC_REF'), ('TP9', 'SENS_5V'), ('TP10', G)]
for r, n in TPS_:
    add(r, 'M1:NEW', STP, TP, 'TP ' + n, 'Test pad 1.5 mm (no part)', {1: n}, 'LISTWA', note='Replaces the S1 service strips (audit: S).', in_bom=False)
X1 = [  # (X1 screw, net on the board, board pad, wire, note)
    (1, 'BAT_P', 'J1.1', '2.0 mm2', 'pakiet + (za BMS, przez wylacznik na obudowie)'), (2, G, 'J1.2', '2.0 mm2', 'pakiet -; tu tez IBT-2 B-'),
    (3, VB, 'J2.1', '2.0 mm2', 'VMOTOR za F1 -> IBT-2 B+'), (4, '-', '-', '2.0 mm2', 'IBT-2 B-; mostek do X1.2 na listwie (bez PCB)'),
    (5, 'P1_ECU', 'J5.1', '2.0 mm2', 'silnik od ECU (LOGGER) / IBT-2 M+ (TESTER)'), (6, 'P1_EGR', 'J5.2', '2.0 mm2', 'silnik do zaworu'),
    (7, 'P3', 'J6.1', '0.25 mm2', 'silnik pin 3: ECU i zawor na jednej srubie; TESTER: IBT-2 M-'), (8, 'P4', 'J6.2', '0.25 mm2', 'czujnik'), (9, 'P5', 'J6.3', '0.25 mm2', 'czujnik'),
    (10, 'P6', 'J6.4', '0.25 mm2', 'czujnik'), (11, 'SENS_5V', 'J6.5', '0.5 mm2', 'TESTER: do pinu zasilania czujnika'), (12, G, 'J6.6', '0.5 mm2', 'LOGGER: masa auta (odniesienie pomiarow)'),
    (13, 'VBAT_CAR', 'J6.7', '0.25 mm2', 'akumulator auta (pomiar)'), (14, 'CAN_H', 'J6.8', 'skretka', ''), (15, 'CAN_L', 'J6.9', 'skretka', ''), (16, G, 'J6.10', '0.25 mm2', 'CAN GND')]
OFFBOARD = [dict(ref='X1', source_ref='M1:NEW', display='listwa srubowa 16 tor', mpn='Screw terminal strip 16 ways, >= 10 A, DIN rail or panel (MPN to choose)', qty=1, footprint='-', zrodlo=NEW, url='',
                 note='In the enclosure; board wires soldered, outside cables through glands (SPECYFIKACJA 5).')]


def write_tables():
    clean = {r: {k: v for k, v in p.items() if k != 'symbol'} for r, p in PARTS.items()}
    (P / 'docs/parts.json').write_text(json.dumps(clean, indent=2, ensure_ascii=False), encoding='utf-8')
    with (P / 'docs/BOM.csv').open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, ['ref', 'source_ref', 'display', 'mpn', 'qty', 'footprint', 'zrodlo', 'url', 'note'], delimiter=';', extrasaction='ignore'); w.writeheader()
        w.writerows(sorted(PARTS.values(), key=lambda p: (re.sub(r'\d', '', p['ref']), int(re.sub(r'\D', '', p['ref']) or 0)))); w.writerows(OFFBOARD)
    libs = {p['symbol'][1]: p['symbol'] for p in PARTS.values()}; libs[PRJ + ':PWR_FLAG'] = symbol('power', 'PWR_FLAG')
    (P / 'eda/libraries/M1.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor")' + ''.join(dump([s[0], s[1].split(':')[1]] + s[2:]) for s in libs.values()) + ')', encoding='utf-8')
    (P / 'eda/sym-lib-table').write_text('(sym_lib_table (lib (name "M1") (type "KiCad") (uri "${KIPRJMOD}/libraries/M1.kicad_sym") (options "") (descr "M1 symbols")))')
    flibs = sorted({p['footprint'].split(':')[0] for p in PARTS.values()})
    (P / 'eda/fp-lib-table').write_text('(fp_lib_table ' + ''.join(f'(lib (name {q(l)}) (type "KiCad") (uri "${{KIPRJMOD}}/libraries/{l}.pretty") (options "") (descr "M1 local library"))' for l in flibs) + ')')


if __name__ == '__main__': write_tables(); print(len(PARTS), 'parts')
