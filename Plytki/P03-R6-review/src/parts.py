"""P03 R6 parts: R5 CORE moved to format S1 (Plytki/Format-S1/SPECYFIKACJA-FORMATU-S1.md, S1-2), schematic only.
R6 changes against R5 (circuit functions unchanged; see docs/ZMIANY-R6.md):
- J1 (DAQ B2B), J2..J8 (IDC), J9 (PANELCORE Mini-Fit) and J10 (LV03 pigtail) -> three right-angle IDC 2x10 box headers
  J_BP1..J_BP3 on edge A, one per slot; pinout in src/jbp_pinout.py; 5V_SYS and 3V3_IO now arrive from P02 R4 through P12;
- new input PFAIL_N (P02 R4, D-02): J_BP2.16 -> R42 1K -> GPIO3 (J1-13), R43 100K to 3V3_CORE on the connector side (30.09: was 10K);
- three 1x13 right-angle service headers J_SV1..J_SV3 on edge B, every non-GND pin through a series resistor at the node;
- passives: all SMD 1206 (30.09: the owned MF0207 10K/4K7 and K15 stock is used up by P09 R2 and P10 R2, so P03 buys everything;
  user rule: owned THT stays THT, new purchases SMD); every 100 nF uses the C12/C15 code GRM31CR71H104KA01L;
- 74LVC125A soldered as SOIC-14 and TPS3808 as SOT-23-6 directly (fab board; Kamami/PA0085 adapters not needed).
R5 history: U4 LVC1G37 replaces LVC1G07 (R5); Schmitt buffer U6 SN74LVC1G17, R41 220R and C15 on the reset line to P04 (R4).
source_ref maps each part to the v6.1 P03 BOM or marks it as added. Pin nets follow the v6.1 import
(reference/v6.1-P03-import.xml) except the user decisions of 25.09.2026 (M1 Waveshare N32R16V on 2x 1x22 headers, rows 22.86 mm;
SD1 Adafruit 4682) and the documented R2..R6 deltas.
"""
from cadlib import *
import shutil, json, csv
FP = P / 'eda/libraries/P03.pretty'; FP.mkdir(parents=True, exist_ok=True)
P02LIB = P / 'reference/footprints'  # frozen local resources; no neighbouring project


def copyfp(lib, name):
    src = K / 'footprints' / (lib + '.pretty') / (name + '.kicad_mod'); assert src.exists(), src
    dest = P / 'eda/libraries' / (lib + '.pretty'); dest.mkdir(parents=True, exist_ok=True); shutil.copy2(src, dest / src.name)
    return lib + ':' + name


def copyp02(name):  # reviewed in P01/P02, copied byte for byte
    shutil.copy2(P02LIB / (name + '.kicad_mod'), FP / (name + '.kicad_mod')); return 'P03:' + name


def fpfile(name, body):
    (FP / (name + '.kicad_mod')).write_text(f'(footprint {q(name)} (version 20240108) (generator "pcbnew") (layer "F.Cu") (attr through_hole) ' + body + ')', encoding='utf-8')
    return 'P03:' + name


def rect(layer, x0, y0, x1, y1, w):
    return f'(fp_rect (start {x0} {y0}) (end {x1} {y1}) (stroke (width {w}) (type default)) (fill none) (layer "{layer}"))'


def txt(layer, t, x, y, size=1.0):
    return f'(fp_text user {q(t)} (at {x} {y}) (layer "{layer}") (effects (font (size {size} {size}) (thickness {size * .15:.2f}))))'


def pad(num, x, y, shape='circle', size=1.7, drill=1.0):
    return f'(pad {q(num)} thru_hole {shape} (at {x} {y}) (size {size} {size}) (drill {drill}) (layers "*.Cu" "*.Mask"))'


def waveshare_fp():
    """Two 1x22 female headers, rows 22.86 mm apart (measured on the owned board). J1 left, J3 right, pin 1 of
    both rows at the module/antenna end (y = 0), pins 21/22 at the USB end. Outline 25.5 x 64 mm (DevKitC-1 class,
    confirm at the 1:1 fit). Antenna region beyond pin 1: copper keepout on both layers (rule area in the board)."""
    name = 'Waveshare_ESP32-S3-DEV-KIT_2x22_W22.86'; b = f'(descr "Waveshare ESP32-S3-DEV-KIT-N32R16V on 2x 1x22 female headers, rows 22.86 mm, DevKitC-1 pinout")'
    for i in range(22):
        b += pad(f'J1-{i + 1}', 0, round(i * 2.54, 2), 'rect' if i == 0 else 'circle')
        b += pad(f'J3-{i + 1}', 22.86, round(i * 2.54, 2), 'rect' if i == 0 else 'circle')
    x0, x1, y0, y1 = -1.32, 24.18, -8.0, 56.5
    b += rect('F.Fab', x0, y0, x1, y1, .1) + rect('F.CrtYd', x0 - .25, y0 - .25, x1 + .25, y1 + .25, .05)
    b += rect('F.SilkS', x0 - .12, y0 - .12, x1 + .12, y1 - .6, .12)  # stops 0.6 mm short of the USB end, which sits on the board edge
    b += rect('F.Fab', x0, y0, x1, -1.5, .1) + txt('F.Fab', 'ANTENNA', 11.43, -4.8) + txt('F.Fab', 'USB-C', 11.43, 55)
    b += txt('F.SilkS', 'J1', -2.6, 0, .8) + txt('F.SilkS', 'J3', 25.4, 0, .8)
    b += f'(fp_text reference "REF**" (at 11.43 26) (layer "F.SilkS") (effects (font (size 1.2 1.2) (thickness .18))))'
    return fpfile(name, b)


def adafruit4682_fp():
    """Adafruit 4682 on a 1x9 female header: pad n = header pin n (3V GND CLK SO SI CS D1 DAT2 DET), 2.54 mm.
    Module 25.4 x 22.86 mm, header row 2.54 mm from its bottom edge, two 2.5 mm plated holes 2.54 mm from the
    top corners (fab print, reference/adafruit-4682-fab-print.png); card slot at the top edge, card sticks out 2.54 mm.
    NPTH 2.7 mm under the module holes for M2.5 spacers."""
    name = 'Adafruit_4682_microSD_1x09'; b = '(descr "Adafruit 4682 microSD SPI/SDIO 3V breakout on a 1x9 female header")'
    for i, n in enumerate(['3V', 'GND', 'CLK', 'SO', 'SI', 'CS', 'D1', 'DAT2', 'DET']):
        b += pad(str(i + 1), round(i * 2.54, 2), 0, 'rect' if i == 0 else 'circle') + txt('F.Fab', n, round(i * 2.54, 2), -2.2, .5)
    for x in (0, 20.32):
        b += f'(pad "" np_thru_hole circle (at {x} -17.78) (size 2.7 2.7) (drill 2.7) (layers "*.Cu" "*.Mask"))'
    b += rect('F.Fab', -2.54, -20.32, 22.86, 2.54, .1) + rect('F.Fab', 4.5, -22.86, 15.5, -20.32, .1) + txt('F.Fab', 'CARD', 10.16, -21.6, .7)
    b += rect('F.CrtYd', -2.79, -23.11, 23.11, 2.79, .05) + rect('F.SilkS', -2.66, -20.44, 22.98, 2.66, .12)
    b += f'(fp_text reference "REF**" (at 10.16 -10) (layer "F.SilkS") (effects (font (size 1.2 1.2) (thickness .18))))'
    return fpfile(name, b)


def pa0085_fp():
    """Chip Quik PA0085 SOT23-6 -> DIP-6: board 17.78 x 7.62 mm, two rows of 3 pins 15.24 mm apart (measured by the
    user), pitch 2.54. Pin n = SOT pin n, counter-clockwise (4 opposite 3) - confirm on the adapter silkscreen."""
    name = 'Adapter_SOT23-6_DIP6_W15.24_ChipQuik_PA0085'; b = '(descr "SOT23-6 on Chip Quik PA0085, rows 15.24 mm")'
    for i in range(3):
        b += pad(str(i + 1), 0, i * 2.54, 'rect' if i == 0 else 'circle') + pad(str(6 - i), 15.24, i * 2.54)
    b += rect('F.Fab', -1.27, -1.27, 16.51, 6.35, .1) + rect('F.CrtYd', -1.52, -1.52, 16.76, 6.6, .05) + rect('F.SilkS', -1.4, -1.4, 16.64, 6.48, .12)
    b += '(fp_circle (center -2.2 -1.1) (end -1.85 -1.1) (stroke (width 0.3) (type default)) (fill none) (layer "F.SilkS"))'
    b += txt('F.Fab', 'SOT23-6', 7.62, 2.54, .8) + f'(fp_text reference "REF**" (at 7.62 -2.6) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))'
    return fpfile(name, b)


def pigtail_fp(name, count, pitch, drill, padd, label):
    """Soldered harness end with a cable-tie anchor 12.5 mm from the solder row (as P01/P02)."""
    b = ''
    for i in range(count):
        b += pad(str(i + 1), round(i * pitch, 2), 0, 'rect' if i == 0 else 'circle', padd, drill)
    for x in [-3, (count - 1) * pitch + 3]:
        b += f'(pad "" np_thru_hole circle (at {x} -12.5) (size 3.2 3.2) (drill 3.2) (layers "*.Cu" "*.Mask"))'
    b += txt('F.SilkS', 'TIE / 12.5 mm', (count - 1) * pitch / 2, -9.8, 1)  # inside the outline, between the tie line and the solder row
    b += rect('F.CrtYd', -6, -15.5, (count - 1) * pitch + 6, padd / 2 + .5, .05) + txt('F.Fab', label, (count - 1) * pitch / 2, 3.2)
    b += f'(fp_text reference "REF**" (at {(count - 1) * pitch / 2} 5) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))'
    return fpfile(name, b)


M1FP = waveshare_fp(); SDFP = adafruit4682_fp()
C100N = copyp02('C_Vishay_K15_H5_P5'); TPFP = copyp02('TestPad_1')
RTHT = copyfp('Resistor_THT', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P5.08mm_Vertical'); LED = copyfp('LED_THT', 'LED_D3.0mm')
RSMD = copyfp('Resistor_SMD', 'R_1206_3216Metric_Pad1.30x1.75mm_HandSolder')
DIP28 = copyfp('Package_DIP', 'DIP-28_W7.62mm'); DIP16 = copyfp('Package_DIP', 'DIP-16_W7.62mm')
SO14 = copyfp('Package_SO', 'SOIC-14_3.9x8.7mm_P1.27mm'); SOT236 = copyfp('Package_TO_SOT_SMD', 'SOT-23-6')
IDC20 = copyfp('Connector_IDC', 'IDC-Header_2x10_P2.54mm_Horizontal')
SV13 = copyfp('Connector_PinHeader_2.54mm', 'PinHeader_1x13_P2.54mm_Horizontal')
# S1 §9 / task §4: resistor values owned in Zamowione/zamowione.csv (MF0207, TME 24.09) stay THT, mounted vertically.
# 30.09 (review PR #6): the owned MF0207 10K/4K7 and K15 are used up by P09 R2 and P10 R2, so every P03 resistor and 100 nF is a
# purchase -> SMD 1206 (user rule: owned THT stays, new parts SMD).
OWNED_R = {}
SMD_R = {'1K': 'RC1206FR-071KL', '330R': 'RC1206FR-07330RL', '220R': 'RC1206FR-07220RL', '33R': 'RC1206FR-0733RL',
         '10K': 'RC1206FR-0710KL', '4K7': 'RC1206FR-074K7L', '100K': 'RC1206FR-07100KL'}
CSMD = copyfp('Capacitor_SMD', 'C_1206_3216Metric_Pad1.33x1.80mm_HandSolder')


def custom_symbol(name, left, right, half_w, pitch=2.54):
    """Rectangle symbol; left/right = lists of (number, name, type) from top to bottom; None = gap."""
    n = max(len(left), len(right)); top = (n - 1) * pitch / 2
    body = f'(symbol "{name}_0_1" (rectangle (start {-half_w} {top + pitch}) (end {half_w} {-top - pitch}) (stroke (width 0.254) (type default)) (fill (type background))))'
    pins = ''
    for side, lst in ((-1, left), (1, right)):
        for i, p in enumerate(lst):
            if p is None:
                continue
            num, nm, typ = p; y = round(top - i * pitch, 3); x = side * (half_w + 5.08)
            pins += (f'(pin {typ} line (at {x} {y} {0 if side < 0 else 180}) (length 5.08) (name {q(nm)} (effects (font (size 1.27 1.27)))) '
                     f'(number {q(num)} (effects (font (size 1.27 1.27)))))')
    s = parse(f'(symbol "{name}" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes) {body} (symbol "{name}_1_1" {pins}))')
    s[1] = PRJ + ':' + name
    return s


J1N = ['3V3', '3V3', 'RST', 'GPIO4', 'GPIO5', 'GPIO6', 'GPIO7', 'GPIO15', 'GPIO16', 'GPIO17', 'GPIO18', 'GPIO8', 'GPIO3', 'GPIO46', 'GPIO9',
       'GPIO10', 'GPIO11', 'GPIO12', 'GPIO13', 'GPIO14', '5V', 'GND']
J3N = ['GND', 'GPIO43_TX', 'GPIO44_RX', 'GPIO1', 'GPIO2', 'GPIO42', 'GPIO41', 'GPIO40', 'GPIO39', 'GPIO38_RGB', 'GPIO37', 'GPIO36', 'GPIO35', 'GPIO0',
       'GPIO45', 'GPIO48', 'GPIO47', 'GPIO21', 'GPIO20_DP', 'GPIO19_DM', 'GND', 'GND']


def typ(nm, first=True):
    return ('power_out' if first else 'passive') if nm == '3V3' else 'power_in' if nm in ('5V', 'GND') else 'bidirectional'


S_M1 = custom_symbol('Waveshare_ESP32-S3-DEV-KIT', [(f'J1-{i + 1}', n, typ(n, i == 0)) for i, n in enumerate(J1N)], [(f'J3-{i + 1}', n, typ(n)) for i, n in enumerate(J3N)], 12.7)
S_SD = custom_symbol('Adafruit_4682_microSD', [(str(i + 1), n, 'power_in' if n in ('3V', 'GND') else 'bidirectional') for i, n in enumerate(['3V', 'GND', 'CLK', 'SO', 'SI', 'CS', 'D1', 'DAT2', 'DET'])], [], 7.62)
S_R = symbol('Device', 'R'); S_C = symbol('Device', 'C'); S_LED = symbol('Device', 'LED'); S_TP = symbol('Connector', 'TestPoint')
S_MCP = symbol('Interface_Expansion', 'MCP23017x-x-SP', 'MCP23017-E_SP'); S_139 = symbol('74xx', '74LS139', '74HC139')
S_TPS = symbol('Power_Supervisor', 'TPS3808DBV', 'TPS3808G33DBV'); S_BUF = symbol('74xx', '74LVC125')


def conn(n, style='Odd_Even'):
    return symbol('Connector_Generic', f'Conn_02x{n:02d}_{style}')


URL = {'ws': 'https://docs.waveshare.com/ESP32-S3-DEV-KIT-N8R8', 'devkit': 'https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide_v1.1.html',
       'ada': 'https://www.adafruit.com/product/4682', 'mcp': 'https://ww1.microchip.com/downloads/en/devicedoc/20001952c.pdf',
       'hc139': 'https://www.ti.com/lit/ds/symlink/sn74hc139.pdf', 'tps': 'https://www.ti.com/lit/ds/symlink/tps3808.pdf', 'pa0085': 'https://www.digikey.com/en/products/detail/chip-quik-inc/PA0085/5014712',
       'lvc125': 'https://assets.nexperia.com/documents/data-sheet/74LVC125A.pdf', 'k15': 'https://www.vishay.com/docs/45171/kseries.pdf',
       'mf0207': 'https://www.yageo.com/upload/media/product/productsearch/datasheet/lr/Yageo_LR_MFR_1.pdf', 'l934': 'https://www.kingbrightusa.com/images/catalog/SPEC/L-934GD.pdf',
       'minifit': 'http://www.molex.com/pdm_docs/sd/039281083_sd.pdf', 'ssw': 'https://www.samtec.com/products/ssw'}
PARTS = {}


def add(ref, src, sym, fp, display, mpn, pins, url='', note='', sheet='P03'):
    PARTS[ref] = {'ref': ref, 'source_ref': src, 'symbol': sym, 'footprint': fp, 'display': display, 'value': display, 'mpn': mpn,
                  'pins': {str(k): v for k, v in pins.items()}, 'url': url, 'note': note, 'qty': 1, 'sheet': sheet, 'on_board': True}


def res(ref, src, value, mpn, pins, note='', sheet='P03'):
    """R6: footprint and MPN follow the value (owned THT values vertical, all other values SMD 1206); mpn argument = R5 history."""
    v = value.split('/')[0].strip()
    if v in OWNED_R:
        add(ref, src, S_R, RTHT, value, OWNED_R[v], pins, URL['mf0207'], note, sheet)
    else:
        add(ref, src, S_R, RSMD, v + ' / 1% 1206', SMD_R[v], pins, '', note, sheet)


def cap(ref, src, pins, note='', sheet='P03'):
    add(ref, src, S_C, CSMD, '100nF / 50V X7R', 'GRM31CR71H104KA01L', pins, '', note, sheet)  # 30.09: purchase -> SMD 1206, same code as C12/C15 (K15 stock used by P09/P10)


# ---- sheet P03 (CORE): MCU board, SD, expander, decoder, supervisor, local pull-ups -------------------------
GPIO = {'J1-4': 'SPI3_SCLK_SRC', 'J1-5': 'SPI3_MOSI_SRC', 'J1-6': 'SPI3_MISO_CORE', 'J1-7': 'SD_CS', 'J1-8': 'I2C_SCL', 'J1-9': 'TC2_CS_SRC',
        'J1-10': 'CAN_TX', 'J1-11': 'CAN_RX_CORE', 'J1-12': 'TC1_CS_SRC', 'J1-15': 'ADC_SCLK_SRC', 'J1-16': 'I2C_SDA', 'J1-17': 'ADC_DOUTA_CORE',
        'J1-18': 'ADC_CS_SRC', 'J1-19': 'ADC_CONVST_SRC', 'J1-20': 'ADC_BUSY_CORE', 'J3-4': 'PWM', 'J3-5': 'ADC_SDI_SRC', 'J3-6': 'INTERLOCK_CORE',
        'J3-7': 'SCOPE_TRIG', 'J3-8': 'HW_ARMED_CORE', 'J3-9': 'MCU_ARM', 'J3-10': 'CURRENT_CS_N', 'J3-18': 'HEARTBEAT', 'J1-13': 'PFAIL_N_CORE',
        'J1-1': '3V3_CORE', 'J1-2': '3V3_CORE', 'J1-3': 'SUP_N', 'J1-21': '5V_M1', 'J1-22': 'GND', 'J3-1': 'GND', 'J3-21': 'GND', 'J3-22': 'GND'}
m1pins = {f'J{r}-{i}': GPIO.get(f'J{r}-{i}', 'NC') for r in (1, 3) for i in range(1, 23)}
add('M1', 'M1', S_M1, M1FP, 'Waveshare ESP32-S3-DEV-KIT-N32R16V', 'owned (Waveshare ESP32-S3-DEV-KIT-N32R16V) on 2x 1x22 female headers', m1pins, URL['ws'],
    'Rows 22.86 mm (measured). GPIO numbers are the v6.1 contract; R6: GPIO3 = PFAIL_N_CORE (JTAG strap only with EFUSE_STRAP_JTAG_SEL=1, never burn). Remove the on-board RGB LED on GPIO38 (v6.1). GPIO47/48 1.8 V: unused. 3V3 = 3V3_CORE; never tie to 3V3_IO.')
add('SD1', 'SD1', S_SD, SDFP, 'Adafruit 4682 microSD (3V)', 'Adafruit 4682 on a 1x9 female header + 2x M2.5 spacer',
    {1: '3V3_CORE', 2: 'GND', 3: 'SPI3_SCLK', 4: 'SPI3_MISO', 5: 'SPI3_MOSI', 6: 'SD_CS', 7: 'NC', 8: 'NC', 9: 'NC'}, URL['ada'],
    'User decision 25.09: Adafruit 4682 (3 V only, no regulator/level shifter). SO = card out (MISO), SI = card in (MOSI). D1, DAT2, DET unused.')
add('U1', 'U17', S_MCP, DIP28, 'MCP23017-E/SP', 'MCP23017-E/SP', {1: 'TEST_KEY_CORE', 2: 'SENSOR_HEALTHY_CORE', 3: 'ENA_DIAG_CORE', 4: 'ENB_DIAG_CORE', 5: 'LOGGER_CLEAR_CORE',
    6: 'TEST_PRESENT_CORE', 7: 'MARK', 8: 'NC', 9: '3V3_CORE', 10: 'GND', 11: 'NC', 12: 'I2C_SCL', 13: 'I2C_SDA', 14: 'NC', 15: 'GND', 16: 'GND', 17: 'GND',
    18: 'SUP_N', 19: 'NC', 20: 'NC', 21: 'ADC_RESET_SRC', 22: 'MEAS_EN_SRC', 23: 'MEAS_BANK', 24: 'SENSOR_ENABLE', 25: 'LOGGER_CURRENT_OK_CORE', 26: 'MOTOR_INA',
    27: 'MOTOR_INB', 28: 'STATUS_LED'}, URL['mcp'], 'Address 0x20 (A2..A0 = GND). IODIRA 0x10, IODIRB 0x7F (v6.1). In 2x DIP14 precision sockets end to end (bought).')
cap('C2', 'C_DEC_U17_9', {1: '3V3_CORE', 2: 'GND'}, 'At U1 pin 9.')
add('U2', 'U_CS', S_139, DIP16, 'SN74HC139N', 'SN74HC139N', {1: 'CURRENT_CS_N', 2: 'MEAS_BANK', 3: 'GND', 4: 'CS_ILOG_N_SRC', 5: 'CS_ITEST_N_SRC', 6: 'NC', 7: 'NC', 8: 'GND',
    9: 'NC', 10: 'NC', 11: 'NC', 12: 'NC', 13: 'GND', 14: 'GND', 15: '3V3_CORE', 16: '3V3_CORE'}, URL['hc139'], '/G = GPIO38, A = MEAS_BANK, B = GND (v6.1). Second half disabled. DIP16 socket (bought).')
cap('C1', 'C_CS', {1: '3V3_CORE', 2: 'GND'}, 'At U2 pin 16.')
res('R1', 'R_CS_IDLE', '10K / 1%', 'MF0207FTE-10K', {1: 'CURRENT_CS_N', 2: '3V3_CORE'}, 'Decoder disabled while GPIO38 floats.')
add('U3', 'U5', S_TPS, SOT236, 'TPS3808G33DBVR', 'TPS3808G33DBVR', {1: 'SUP_RAW_N', 2: 'GND', 3: '3V3_CORE', 4: 'NC', 5: '3V3_CORE', 6: '3V3_CORE'},
    URL['tps'], 'R6: SOT23-6 soldered directly on the fab board (PA0085 adapter not used). CT open = fixed delay.')
cap('C3', 'C_DEC_U5_6', {1: '3V3_CORE', 2: 'GND'}, 'At U3 pin 6.')
res('R13', 'R_SUP_PU', '10K / 1%', 'MF0207FTE-10K', {1: 'SUP_RAW_N', 2: '3V3_CORE'}, 'Supervisor pull-up before U4; does not discharge Waveshare EN capacitor.')
res('R9', 'R_PU_I2C_SCL', '4K7 / 1%', 'MF0207FTE-4K7', {1: '3V3_CORE', 2: 'I2C_SCL'})
res('R10', 'R_PU_I2C_SDA', '4K7 / 1%', 'MF0207FTE-4K7', {1: '3V3_CORE', 2: 'I2C_SDA'})
res('R11', 'R_PU_SD_CS', '10K / 1%', 'MF0207FTE-10K', {1: '3V3_CORE', 2: 'SD_CS'}, 'Card deselected while GPIO7 floats.')
res('R12', 'R_SCOPE', '330R / 1%', 'MF0207FTE-330R', {1: 'SCOPE_TRIG', 2: 'N_J_SCOPE_HOT'}, 'SCOPE_TRIG series resistor to PANELCORE pin 7.')
res('R5', 'R_MARK', '10K / 1%', 'MF0207FTE-10K', {1: '3V3_CORE', 2: 'MARK'})
cap('C4', 'C_MARK', {1: 'MARK', 2: 'GND'}, 'MARK button debounce.')
res('R4', 'R_LED', '1K / 1%', 'MF0207FTE-1K', {1: 'STATUS_LED', 2: 'LED_A'})
add('LED1', 'LED1', S_LED, LED, 'GREEN 3mm / STATUS', 'L-934GD', {1: 'GND', 2: 'LED_A'}, URL['l934'], 'MCP23017 GPA7.')
res('R14', 'W_LINK', '1K / 1%', 'MF0207FTE-1K', {1: '3V3_CORE', 2: 'CORE_LINK'}, 'CORE_LINK = presence of 3V3_CORE through 1 k (R3, review P3-02): a harness short to GND draws 3.3 mA; P04 R16 10 k sees >= 2.85 V (74LVC125A VIH 2.0 V). v6.1 had a wire link.')
# ---- sheet IO: buffers and harness connectors --------------------------------------------------------------
BUF = {'U11': ('U_IN1', {1: 'GND', 2: 'ADC_DOUTA', 3: 'ADC_DOUTA_CORE', 4: 'GND', 5: 'ADC_BUSY', 6: 'ADC_BUSY_CORE', 7: 'GND', 8: 'SPI3_MISO_CORE', 9: 'SPI3_MISO', 10: 'GND', 11: 'CAN_RX_CORE', 12: 'CAN_RX', 13: 'GND', 14: '3V3_CORE'}),
       'U12': ('U_IN2', {1: 'GND', 2: 'HW_ARMED', 3: 'HW_ARMED_CORE', 4: 'GND', 5: 'INTERLOCK', 6: 'INTERLOCK_CORE', 7: 'GND', 8: 'LOGGER_CURRENT_OK_CORE', 9: 'LOGGER_CURRENT_OK', 10: 'GND', 11: 'SENSOR_HEALTHY_CORE', 12: 'SENSOR_HEALTHY', 13: 'GND', 14: '3V3_CORE'}),
       'U13': ('U_IN3', {1: 'GND', 2: 'ENA_DIAG', 3: 'ENA_DIAG_CORE', 4: 'GND', 5: 'ENB_DIAG', 6: 'ENB_DIAG_CORE', 7: 'GND', 8: 'LOGGER_CLEAR_CORE', 9: 'LOGGER_CLEAR', 10: 'GND', 11: 'TEST_PRESENT_CORE', 12: 'TEST_PRESENT', 13: 'GND', 14: '3V3_CORE'}),
       'U14': ('U_IN4', {1: 'GND', 2: 'TEST_KEY', 3: 'TEST_KEY_CORE', 4: '3V3_IO', 5: 'GND', 6: 'NC', 7: 'GND', 8: 'NC', 9: 'GND', 10: '3V3_IO', 11: 'NC', 12: 'GND', 13: '3V3_IO', 14: '3V3_CORE'}),
       'U21': ('U_OUT1', {1: 'GND', 2: 'ADC_CS_SRC', 3: 'ADC_CS', 4: 'GND', 5: 'ADC_SCLK_SRC', 6: 'ADC_SCLK', 7: 'GND', 8: 'ADC_SDI', 9: 'ADC_SDI_SRC', 10: 'GND', 11: 'ADC_CONVST', 12: 'ADC_CONVST_SRC', 13: 'GND', 14: '3V3_CORE'}),
       'U22': ('U_OUT2', {1: 'GND', 2: 'ADC_RESET_SRC', 3: 'ADC_RESET', 4: 'GND', 5: 'MEAS_EN_SRC', 6: 'MEAS_EN', 7: 'GND', 8: 'CS_ILOG_N', 9: 'CS_ILOG_N_SRC', 10: 'GND', 11: 'CS_ITEST_N', 12: 'CS_ITEST_N_SRC', 13: 'GND', 14: '3V3_CORE'}),
       'U23': ('U_OUT3', {1: 'GND', 2: 'SPI3_SCLK_SRC', 3: 'SPI3_SCLK', 4: 'GND', 5: 'SPI3_MOSI_SRC', 6: 'SPI3_MOSI', 7: 'GND', 8: 'TC1_CS', 9: 'TC1_CS_SRC', 10: 'GND', 11: 'TC2_CS', 12: 'TC2_CS_SRC', 13: 'GND', 14: '3V3_CORE'})}
for i, (ref, (src, pins)) in enumerate(BUF.items()):
    add(ref, src, S_BUF, SO14, '74LVC125A / SOIC-14', '74LVC125AD,118 (Nexperia)', pins, URL['lvc125'],
        'Nexperia only (Ioff), v6.1. Unused OE# = 3V3_IO in U_IN4 as in v6.1.' if src == 'U_IN4' else 'Nexperia only (Ioff), v6.1.', 'IO')
    cap(f'C{5 + i}', f'C_{src}', {1: '3V3_CORE', 2: 'GND'}, f'At {ref} pin 14.', 'IO')
res('R2', 'R_CURRENT_OK', '10K / 1%', 'MF0207FTE-10K', {1: 'LOGGER_CURRENT_OK', 2: 'GND'}, 'Receiver pull-down: open cable = not OK.', 'IO')
res('R3', 'R_HW_PD', '10K / 1%', 'MF0207FTE-10K', {1: 'HW_ARMED', 2: 'GND'}, 'Receiver pull-down.', 'IO')
res('R6', 'R_PD_LOGGER_CLEAR', '10K / 1%', 'MF0207FTE-10K', {1: 'LOGGER_CLEAR', 2: 'GND'}, 'Receiver pull-down.', 'IO')
res('R7', 'R_PD_SENSOR_HEALTHY', '10K / 1%', 'MF0207FTE-10K', {1: 'SENSOR_HEALTHY', 2: 'GND'}, 'Receiver pull-down: cable open or transmitter unpowered = fault (v6.1).', 'IO')
res('R8', 'R_PD_TEST_PRESENT', '10K / 1%', 'MF0207FTE-10K', {1: 'TEST_PRESENT', 2: 'GND'}, 'Receiver pull-down.', 'IO')
# R6: edge-A connectors J_BP1..J_BP3 replace J1..J10 (format S1 §5); pinout and reasons in src/jbp_pinout.py
from jbp_pinout import JBP
for j, slot in [('J_BP1', 'S1'), ('J_BP2', 'S2'), ('J_BP3', 'S3')]:
    add(j, 'ADDED_R6_EDGE_A', conn(10), IDC20, f'{j} / IDC 2x10 RA ({slot})', 'IDC box header 2x10, 2.54 mm, right angle, Au (MPN to be selected)',
        {p_: v[0] for p_, v in JBP[j].items()}, '', f'Format S1 edge A, slot {slot}, centre x = 26.5 mm in the slot, pin 1 towards smaller x. Short ribbon to P12.', 'LINKS')
for idx, (net, sheet) in enumerate([('5V_SYS', 'P03'), ('3V3_CORE', 'P03'), ('3V3_IO', 'P03'), ('GND', 'P03'), ('SUP_N', 'P03'), ('GND', 'IO')], 1):
    r = f'TP{idx}'
    PARTS[r] = {'ref': r, 'source_ref': 'ADDED_TESTPAD', 'value': net, 'display': net, 'pins': {'1': net}, 'symbol': S_TP, 'footprint': TPFP,
                'mpn': 'PCB test pad', 'qty': 1, 'url': '', 'sheet': sheet, 'on_board': True, 'note': 'Probe access; no circuit function.'}



# R2: state defaults are at the INPUT of each always-enabled buffer.
source_defaults = [
 ('ADC_CS_SRC','3V3_CORE'),('ADC_SCLK_SRC','GND'),('ADC_SDI_SRC','GND'),('ADC_CONVST_SRC','GND'),
 ('ADC_RESET_SRC','GND'),('MEAS_EN_SRC','GND'),('SPI3_SCLK_SRC','GND'),('SPI3_MOSI_SRC','GND'),
 ('TC1_CS_SRC','3V3_CORE'),('TC2_CS_SRC','3V3_CORE'),('MEAS_BANK','GND')]
for i,(n,rail) in enumerate(source_defaults,15):
    res(f'R{i}','ADDED_R2_SOURCE_DEFAULT','10K / 1%','MF0207FTE-10K',{1:n,2:rail},
        'Source-side reset/boot default. Required even when downstream has a pull resistor.', 'P03' if n=='MEAS_BANK' else 'OUT')
receiver_defaults=[('INTERLOCK','GND'),('TEST_KEY','GND'),('ENA_DIAG','GND'),('ENB_DIAG','GND'),
                   ('CAN_RX','3V3_CORE'),('ADC_BUSY','GND'),('ADC_DOUTA','GND'),('SPI3_MISO','GND')]
for i,(n,rail) in enumerate(receiver_defaults,26):
    res(f'R{i}','ADDED_R2_RECEIVER_DEFAULT','10K / 1%','MF0207FTE-10K',{1:n,2:rail},
        'Receiver-side default before buffer. Not a device-presence detector.', 'IO')

# Reset fanout: non-inverting OPEN DRAIN, limited capacitive sink current.
S_OD=custom_symbol('SN74LVC1G37DBV',[('2','A','input'),('3','GND','power_in'),('1','NC','no_connect')],
                   [('4','Y_OD','open_collector'),('5','VCC','power_in')],7.62)
add('U4','ADDED_R2_RESET_BUFFER',S_OD,copyfp('Package_TO_SOT_SMD','SOT-23-5'),'SN74LVC1G37DBVR','SN74LVC1G37DBVR',
    {1:'NC',2:'SUP_RAW_N',3:'GND',4:'RESET_DRV_N',5:'3V3_CORE'},
    'https://www.ti.com/lit/gpn/SN74LVC1G37',
    'DBV SOT23-5, 0.95 mm pitch; direct hand soldering. R5: non-inverting Schmitt input, open-drain output; replaces LVC1G07 without changing pads. Never substitute push-pull or a non-Schmitt input.', 'POWER')
res('R34','ADDED_R2_RESET_LIMIT','220R / 1%','MF0207FTE-220R',{1:'RESET_DRV_N',2:'SUP_N'},
    'Limits discharge of the module EN capacitor to <16 mA at 3.465 V. Final SUP_N goes to MCU EN, MCP reset and P04.', 'POWER')
res('R35','ADDED_R2_RESET_PULLUP','10K / 1%','MF0207FTE-10K',{1:'SUP_N',2:'3V3_CORE'},
    'Final common reset pull-up, parallel to the module 10K. Module 1 uF EN capacitor retained.', 'POWER')
C1206=copyfp('Capacitor_SMD','C_1206_3216Metric_Pad1.33x1.80mm_HandSolder')
add('C12','ADDED_R2_RESET_DECAP',S_C,C1206,'100nF / 50V X7R','GRM31CR71H104KA01L',{1:'3V3_CORE',2:'GND'},
    '', '1206, at U4 pin 5, local ground via.', 'POWER')

# USB backfeed blocker. The PMOS BODY DIODE must point from SYS to M1.
S_ID=custom_symbol('LTC4412S6',[('1','VIN','power_in'),('2','GND','power_in'),('3','CTL','input')],
                   [('6','SENSE','input'),('5','GATE','output'),('4','STAT_OD','open_collector')],7.62)
add('U5','ADDED_R2_USB_BLOCK',S_ID,copyfp('Package_TO_SOT_SMD','SOT-23-6'),'LTC4412IS6','LTC4412IS6#TRPBF',
    {1:'5V_SYS',2:'GND',3:'GND',4:'NC',5:'PWR_GATE',6:'5V_M1'},
    'https://www.analog.com/media/en/technical-documentation/data-sheets/ltc4412.pdf',
    'TSOT23-6, direct hand soldering. CTL=0 always enabled. Reverse-current blocker, not a current limiter.', 'POWER')
add('Q1','ADDED_R2_USB_PMOS',symbol('Transistor_FET','Q_PMOS_GSD'),copyfp('Package_TO_SOT_SMD','SOT-23'),
    'AO3401A','AO3401A',{1:'PWR_GATE',2:'5V_M1',3:'5V_SYS'},
    'https://www.aosmd.com/pdfs/datasheet/AO3401A.pdf',
    'G=1, S=2 (M1), D=3 (SYS); body diode D to S. Do not reverse source/drain. Direct SOT23 hand soldering.', 'POWER')
for r,value,mpn,n in [('C13','1uF / 25V X7R','GRM31CR71E105KA12L','5V_SYS'),
                       ('C14','10uF / 16V X7R','GRM31CR71C106KA12L','5V_M1')]:
    add(r,'ADDED_R2_PWR_DECAP',S_C,C1206,value,mpn,{1:n,2:'GND'},'', '1206 local bypass. Module bulk capacitance remains.', 'POWER')

# Provision for source termination of the fastest outputs; initial 33 ohm, tune after scope measurements.
for ref,u,pin,external in [('R36','U21','6','ADC_SCLK'),('R37','U21','11','ADC_CONVST'),
                          ('R38','U23','3','SPI3_SCLK'),('R39','U21','8','ADC_SDI'),('R40','U23','6','SPI3_MOSI')]:
    internal=external+'_DRV';PARTS[u]['pins'][pin]=internal
    res(ref,'ADDED_R2_SOURCE_TERMINATION','33R / 1%','MF0207FTE-33R',{1:internal,2:external},
        'Source termination at buffer output. Initial 33R; tune 22..47R or 0R only after end-of-link waveform measurement.', 'OUT')
# R4: the common reset node (module EN with its 1 uF) reaches P04 only through a Schmitt-trigger buffer (review P3-01):
# 74LVC125A in P04 needs <= 10 ns/V at its input, SUP_N rises with tau ~ 5 ms. SN74LVC1G17: no input transition limit,
# hysteresis 0.51..0.83 V at 3 V, push-pull output with Ioff (unpowered CORE -> P04 pull-down R17 gives LOW).
S_ST=custom_symbol('SN74LVC1G17DBV',[('2','A','input'),('3','GND','power_in'),('1','NC','no_connect')],
                   [('4','Y','output'),('5','VCC','power_in')],7.62)
add('U6','ADDED_R4_RESET_SCHMITT',S_ST,copyfp('Package_TO_SOT_SMD','SOT-23-5'),'SN74LVC1G17DBVR','SN74LVC1G17DBVR',
    {1:'NC',2:'SUP_N',3:'GND',4:'SUP_N_DRV',5:'3V3_CORE'},'https://www.ti.com/lit/ds/symlink/sn74lvc1g17.pdf',
    'DBV SOT23-5, 0.95 mm pitch; direct hand soldering. Schmitt-trigger buffer, push-pull. Drives J_BP3.12 (P04 SUP_N) through R41.', 'POWER')
add('R41','ADDED_R4_RESET_SERIES',S_R,copyfp('Resistor_SMD','R_1206_3216Metric_Pad1.30x1.75mm_HandSolder'),'220R / 1% 1206','RC1206FR-07220RL',
    {1:'SUP_N_DRV',2:'SUP_N_OUT'},'',
    'Series resistor U6.4 -> J_BP3.12 (R6; R5: J4.15): short to GND <= 16 mA (3.465 V). Initial value; R6 path ribbon 30 mm + P12 + ribbon 30 mm to P04. Verify <=10 ns/V at P04 U9.5 with actual load/probe; ideal RC is not a guaranteed capacitance limit.', 'POWER')
add('C15','ADDED_R4_RESET_DECAP',S_C,C1206,'100nF / 50V X7R','GRM31CR71H104KA01L',{1:'3V3_CORE',2:'GND'},
    '', '1206, at U6 pin 5, local ground via.', 'POWER')
for idx,n in [(7,'5V_M1'),(8,'SUP_RAW_N')]:
    add(f'TP{idx}','ADDED_R2_TESTPAD',S_TP,TPFP,n,'PCB test pad',{1:n},'', 'Probe access.', 'POWER')


# ---- R6: PFAIL_N input from P02 R4 (D-02) ------------------------------------------------------------------
# P02 R4 drives PFAIL_N from an LM2903 open collector (R36 10K to its 3V3_IO, R37 1K series). The 10K pull-up sits on the
# connector side: LOW at the GPIO = VOL + (3V3_CORE - VOL) * 1K / 11K (0.68 V at VOL 0.4 V, 3.465 V) < VIL 0.825 V;
# on the GPIO side the same 10K would give 0.91 V (fails). J_BP2 open (no P02/P12): 10K pulls HIGH = supply OK.
res('R42', 'ADDED_R6_PFAIL_SERIES', '1K / 1%', '', {1: 'PFAIL_N', 2: 'PFAIL_N_CORE'}, 'PFAIL_N series resistor at M1 GPIO3 (J1-13): limits clamp current when P02 is live and CORE is not.')
res('R43', 'ADDED_R6_PFAIL_PULLUP', '100K / 1%', '', {1: 'PFAIL_N', 2: '3V3_CORE'}, 'PFAIL_N default HIGH (supply OK) with J_BP2 open; connector side of R42. '
    '30.09: 100K (was 10K): with LM2903 VOL 0.7 V over temperature the GPIO low level is 0.73 V < VIL 0.825 V (10K gave 0.95 V).')

# ---- R6: service headers on edge B (format S1 §6) -----------------------------------------------------------
from serwis_pinout import SERWIS
SERIES = {}
_n = 44
for j, slot in [('J_SV1', 'S1'), ('J_SV2', 'S2'), ('J_SV3', 'S3')]:
    pins = {1: 'GND', 13: 'GND'}
    for p_ in range(2, 13):
        node, val, why = SERWIS[j][p_]; r = f'R{_n}'; _n += 1
        pins[p_] = 'SV_' + node; SERIES[(j, p_)] = r
        res(r, 'ADDED_R6_SERVICE_SERIES', val + ' / 1%', '', {1: node, 2: 'SV_' + node}, f'{j}.{p_} series resistor, placed at the {node} node (S1 §6): {why}.', 'SERWIS')
    add(j, 'ADDED_R6_SERVICE', symbol('Connector_Generic', 'Conn_01x13'), SV13, f'{j} / goldpin 1x13 RA ({slot})', 'Pin header 1x13, 2.54 mm, right angle, Au',
        pins, '', f'Format S1 edge B, slot {slot}, x = 10..43 mm in the slot; pins protrude ~6 mm beyond the edge. GND on pins 1 and 13. Silkscreen: signal name at every pin, readable from edge B.', 'SERWIS')

for r in ['U3','C3','R13','U4','R34','R35','C12','U5','Q1','C13','C14','TP1','TP2','TP3','TP4','TP5']:
    PARTS[r]['sheet']='POWER'
for r in ['U21','U22','U23','C9','C10','C11']:PARTS[r]['sheet']='OUT'
# Short visible values; exact purchasing data stays in MPN and BOM.
PARTS['M1']['display']=PARTS['M1']['value']='Waveshare N32R16V'
PARTS['SD1']['display']=PARTS['SD1']['value']='Adafruit 4682'
PARTS['U3']['display']=PARTS['U3']['value']='TPS3808G33'
for r in BUF:PARTS[r]['display']=PARTS[r]['value']='74LVC125A'


def write_tables():
    clean = {r: {k: v for k, v in p.items() if k != 'symbol'} for r, p in PARTS.items()}
    (P / 'docs/parts.json').write_text(json.dumps(clean, ensure_ascii=False, indent=2), encoding='utf-8')
    fields = ['ref', 'source_ref', 'display', 'mpn', 'qty', 'footprint', 'url', 'note']
    with (P / 'docs/BOM.csv').open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fields, delimiter=';', extrasaction='ignore'); w.writeheader(); w.writerows(PARTS.values())
    purchase = {}
    for ref, part in PARTS.items():
        if not ref.startswith('TP'):purchase.setdefault(part['mpn'], []).append(ref)
    with (P / 'docs/zakupy.csv').open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f, delimiter=';');w.writerow(['nazwa','ilosc_szt','oznaczenia'])
        for mpn, refs in purchase.items():w.writerow([mpn,len(refs),', '.join(refs)])
    libs = {p['symbol'][1]: p['symbol'] for p in PARTS.values()}; libs[PRJ + ':PWR_FLAG'] = symbol('power', 'PWR_FLAG')
    (P / 'eda/libraries/P03.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator "kicad_symbol_editor")' + ''.join(dump([s[0], s[1].split(':')[1]] + s[2:]) for s in libs.values()) + ')', encoding='utf-8')
    (P / 'eda/sym-lib-table').write_text('(sym_lib_table (lib (name "P03") (type "KiCad") (uri "${KIPRJMOD}/libraries/P03.kicad_sym") (options "") (descr "P03 symbols")))', encoding='utf-8')
    flibs = sorted({p['footprint'].split(':')[0] for p in PARTS.values() if p['footprint']})
    (P / 'eda/fp-lib-table').write_text('(fp_lib_table ' + ''.join(f'(lib (name {q(l)}) (type "KiCad") (uri "${{KIPRJMOD}}/libraries/{l}.pretty") (options "") (descr "P03 selected footprint"))' for l in flibs) + ')', encoding='utf-8')
