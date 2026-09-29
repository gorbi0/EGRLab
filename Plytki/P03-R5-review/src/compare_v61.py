"""Compare the P03 R4 netlist with the v6.1 import (reference/v6.1-P03-import.xml), part by part and pin by pin.
Every difference must be one of the documented R1 decisions (EXPECTED); anything else fails.
Mapping: v6.1 parts by SourceRef; M1 pins by GPIO number -> physical header pin (DevKitC-1 table);
SD1 pins by function name -> Adafruit 4682 header pin.
"""
from pathlib import Path
import json, sys, xml.etree.ElementTree as ET
P = Path(__file__).resolve().parents[1]
old = ET.parse(P / 'reference/v6.1-P03-import.xml').getroot(); new = ET.parse(P / 'verification/P03.xml').getroot()
parts = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))


def pinmap(root):
    out = {}
    for n in root.findall('./nets/net'):
        name = n.get('name').split('/')[-1].replace('P03_', '')
        for x in n.findall('node'):
            out[(x.get('ref'), x.get('pin'))] = 'NC' if name.startswith('unconnected-') else name
    return out


o, nw = pinmap(old), pinmap(new)
src_old = {c.get('ref'): {f.get('name'): f.text for f in c.findall('./fields/field')}.get('SourceRef') for c in old.findall('./components/comp')}
ref_new = {p['source_ref']: r for r, p in parts.items()}
GPIO_TO_PIN = {'1': 'J3-4', '2': 'J3-5', '4': 'J1-4', '5': 'J1-5', '6': 'J1-6', '7': 'J1-7', '8': 'J1-12', '9': 'J1-15', '10': 'J1-16', '11': 'J1-17',
               '12': 'J1-18', '13': 'J1-19', '14': 'J1-20', '15': 'J1-8', '16': 'J1-9', '17': 'J1-10', '18': 'J1-11', '21': 'J3-18', '38': 'J3-10',
               '39': 'J3-9', '40': 'J3-8', '41': 'J3-7', '42': 'J3-6', '5V': 'J1-21', '3V3': 'J1-1', 'GND': 'J1-22'}
SD_TO_PIN = {'VDD': '1', 'GND': '2', 'CLK': '3', 'DO': '4', 'DI': '5', 'CS': '6'}
EXPECTED = {('M1','J1-21'):'R2 isolated local 5V_M1', ('U3','1'):'R2 reset buffer input', ('R13','1'):'R2 raw reset pullup',
            ('U21','6'):'R2 source series R36',('U21','8'):'R2 source series R39',('U21','11'):'R2 source series R37',
            ('U23','3'):'R2 source series R38',('U23','6'):'R2 source series R40',
            ('J4','15'):'R4 reset to P04 buffered: SUP_N -> U6 (SN74LVC1G17) -> R41 220R -> SUP_N_OUT',('J8', '4'): 'CAN: 2x3 box header, pin 4 = key (v6.1 4p had no pin 4 in use)',
            ('J8', '5'): 'CAN: added position, NC', ('J8', '6'): 'CAN: added position, NC'}
diffs, checked = [], 0
for (oref, pin), net in sorted(o.items()):
    src = src_old.get(oref); nref = ref_new.get(src)
    if nref is None:
        diffs.append({'v61': f'{oref}.{pin}', 'source_ref': src, 'problem': 'part missing in R1'}); continue
    npin = GPIO_TO_PIN.get(pin, pin) if src == 'M1' else SD_TO_PIN.get(pin, pin) if src == 'SD1' else pin
    got = nw.get((nref, npin)); checked += 1
    if got != net and not (net == 'NC' and got == 'NC'):
        diffs.append({'v61': f'{oref}.{pin}', 'r1': f'{nref}.{npin}', 'v61_net': net, 'r1_net': got, 'expected': EXPECTED.get((nref, npin))})
new_only = sorted({f'{r}.{p}' for (r, p) in nw if r in ref_new.values() and not any(ref_new.get(src_old.get(orf)) == r for orf in {k[0] for k in o})})
unexpected = [d for d in diffs if not d.get('expected')]
added_pins = [f'{r}.{p}' for (r, p), n in nw.items() if r == 'J8' and (r, p) in EXPECTED and n != 'NC']
res = {'v61_pins_checked': checked, 'differences': diffs, 'unexpected': unexpected, 'parts_added_in_r1': sorted(r for r, p in parts.items() if p['source_ref'].startswith('ADDED')),
       'expected_pins_not_nc': added_pins}
(P / 'verification/v61-compare.json').write_text(json.dumps(res, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(f"v6.1 pins checked {checked}; differences {len(diffs)}; unexpected {len(unexpected)}; added parts {res['parts_added_in_r1']}")
for d in unexpected[:30]:
    print(' ', d)
sys.exit(1 if unexpected or added_pins else 0)
