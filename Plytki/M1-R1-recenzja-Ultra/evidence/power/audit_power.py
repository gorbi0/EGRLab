"""Independent read-only netlist/PCB pin checks; outputs only under this file's directory."""
from pathlib import Path
import xml.etree.ElementTree as ET
import re, json, hashlib

BASE = Path(r'C:\Users\tgorbacz\Documents\GORBI\Priv\Kia\Sportage\EGRLab\Plytki\M1-R1-do-recenzji\Plytki\M1-R1-review')
OUT = Path(__file__).resolve().parent

def sexpr(text):
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', text)
    i = 0
    def get():
        nonlocal i
        token = tokens[i]; i += 1
        if token == '(':
            result = []
            while tokens[i] != ')': result.append(get())
            i += 1
            return result
        return json.loads(token) if token.startswith('"') else token
    return get()

def children(item, name):
    return [x for x in item if isinstance(x, list) and x and x[0] == name]

def normalize(name):
    return 'NC' if not name or name.startswith('unconnected-') else name.rsplit('/',1)[-1]

expected = {
 'U1': ['VBUS','GND','5V'],
 'U2': ['VBUS','GND','3V3'],
 'U5': ['TC1_CS','TC1_SDO','SPI3_MISO','TC2_CS','TC2_SDO','SPI3_MISO','GND','NC','GND','3V3','NC','GND','3V3','3V3'],
 'U6': ['3V3','GND','5V','CAN_RX_U','3V3','CAN_L','CAN_H','3V3'],
 'U7': ['GND','RPWM','IBT_RPWM','GND','LPWM','IBT_LPWM','GND','IBT_REN','DRIVE_EN','GND','IBT_LEN','DRIVE_EN','GND','5V'],
 'U8': ['5V','GND','SENS_EN','SENS_FAULT_N','ILIM','SENS_5V'],
 'D1': ['CAN_L','CAN_H','GND'],
 'SD1': ['3V3','GND','SPI3_SCK','SPI3_MISO','SPI3_MOSI','SD_CS','NC','NC','NC'],
 'TC1': ['TC1_VIN','NC','GND','SPI3_SCK','TC1_SDO','SPI3_MOSI','TC1_CS','NC','NC'],
 'TC2': ['TC2_VIN','NC','GND','SPI3_SCK','TC2_SDO','SPI3_MOSI','TC2_CS','NC','NC'],
 'R31': ['ILIM','GND'], 'R32': ['SENS_FAULT_N','3V3']
}
expected = {r:{str(i+1):n for i,n in enumerate(v)} for r,v in expected.items()}
expected['M1'] = dict(zip(['J1-'+str(i+1) for i in range(22)], ['NC','NC','NC','SPI3_SCK','SPI3_MOSI','SPI3_MISO','SD_CS','BTN','TC2_CS','NC','CAN_RXD','TC1_CS','GPIO3_TP','NC','ADC_SCLK','ADC_RESET','ADC_DOUTA','ADC_CS','ADC_CONVST','ADC_BUSY','5V','GND']))
expected['M1'].update(dict(zip(['J3-'+str(i+1) for i in range(22)], ['GND','NC','NC','RPWM','ADC_SDI','SENS_FAULT_N','SCOPE_TRIG','SENS_EN','DRIVE_EN','NC','NC','NC','NC','NC','NC','NC','NC','LPWM','NC','NC','GND','GND'])))

net = {}
for elem in ET.parse(BASE/'verification/M1.xml').getroot().findall('./nets/net'):
    for pin in elem.findall('node'):
        net.setdefault(pin.get('ref'),{})[pin.get('pin')] = normalize(elem.get('name'))
pcb = sexpr((BASE/'eda/M1.kicad_pcb').read_text(encoding='utf-8'))
pcb_pins = {}
for fp in children(pcb,'footprint'):
    ref = next(p[2] for p in children(fp,'property') if p[1]=='Reference')
    pcb_pins[ref] = {}
    for pad in children(fp,'pad'):
        if not pad[1]: continue
        ns=children(pad,'net')
        name=ns[0][-1] if ns else ''
        pcb_pins[ref][pad[1]]=normalize(name)
result = {'pins_checked':sum(map(len,expected.values())), 'mismatches':[]}
for ref, pins in expected.items():
    for pin, wanted in pins.items():
        for kind, actual in [('netlist', net),('pcb',pcb_pins)]:
            found=actual.get(ref,{}).get(pin,'NC')
            if found != wanted: result['mismatches'].append([kind,ref,pin,wanted,found])

result['tps2553_R31_232k_1pct_mA'] = {
 'min':25230/(232*1.01)**1.016,
 'typ':23950/232**0.977,
 'max':22980/(232*0.99)**0.94
}
result['drive_enable_pulldown'] = {
 'nominal_V_3V3_45k':3.3*4700/(45000+4700),
 'V_3V6_RpdPlus1pct_Rpu20k':3.6*4747/(20000+4747),
 'Rpu_required_at_3V6_VIL0V8_ohm':4747*(3.6/.8-1),
 'Rpu_min_guaranteed_by_ESP_datasheet':None
}
result['rail_corners'] = []
for temp in [-40,0,25,50,85]:
    allowance=.02+.005+.01+.0002*abs(temp-25)
    result['rail_corners'].append({'tempC':temp, 'U1_min':5*(1-allowance), 'U1_max':5*(1+allowance), 'U2_min':3.3*(1-allowance), 'U2_max':3.3*(1+allowance), 'ADC_AVCC_min_at_25mA_R7plus1pct':5*(1-allowance)-.025*1.01})
result['hashes'] = {str(path.relative_to(BASE)):hashlib.sha256(path.read_bytes()).hexdigest() for path in [BASE/'src/parts.py', BASE/'docs/parts.json', BASE/'verification/M1.xml', BASE/'eda/M1.kicad_pcb']}
(OUT/'audit-results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
