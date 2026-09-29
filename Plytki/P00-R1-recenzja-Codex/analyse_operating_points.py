"""Independent review calculations. No imports from the P00 generator.

Run with Python 3, optionally providing an exported KiCad XML netlist.
This is arithmetic/topology inspection, not a SPICE or hardware validation.
"""
from pathlib import Path
import json
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
NETLIST = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'evidence/P00.xml'
xml = ET.parse(NETLIST).getroot()
components = {c.attrib['ref']: c.findtext('value') for c in xml.findall('./components/comp')}
pins = {(n.attrib['ref'], n.attrib['pin']): net.attrib['name'].lstrip('/')
        for net in xml.findall('./nets/net') for n in net.findall('node')}

def resistance(ref):
    token = components[ref].split('/')[0].strip().upper()
    m = re.fullmatch(r'(\d+)([RKMG]?)(\d*)', token)
    if not m:
        raise ValueError((ref, token))
    return float(m[1] + ('.' + m[3] if m[3] else '')) * {'': 1, 'R': 1, 'K': 1e3, 'M': 1e6, 'G': 1e9}[m[2]]

expected_pins = {
    ('U2', '1'): 'P00_VIN_P', ('U2', '2'): 'GND', ('U2', '3'): 'P00_V33',
    ('D1', '1'): 'P00_VIN_P', ('D1', '2'): 'P00_VIN',
    ('R1', '1'): 'P00_V33', ('R1', '2'): 'P00_DIS',
    ('RL10', '1'): 'P00_V33', ('RL10', '2'): 'P00_LED_PWR',
    ('R4', '1'): 'P00_V33', ('R4', '2'): 'P00_RESET',
    ('U1', '7'): 'P00_DIS', ('U1', '4'): 'P00_RESET',
}
for pin, net in expected_pins.items():
    if pins.get(pin) != net:
        raise ValueError(f'Topology changed: {pin}, expected {net}, got {pins.get(pin)}')

ra, rb = resistance('R1'), resistance('R2')
c = 100e-9  # explicitly read C1 from the exported netlist below
if not components['C1'].lower().startswith('100nf'):
    raise ValueError(components['C1'])
v = 3.3
f = 1.44 / ((ra + 2 * rb) * c)
stop_model = {
    'LED10_mA': (v - 1.9) / resistance('RL10') * 1000,
    'R1_to_DISCH_LOW_mA': v / ra * 1000,
    'R4_to_RESET_LOW_mA': v / resistance('R4') * 1000,
    'TLC555_assumed_mA': 0.2,
}
result = {
    'netlist': str(NETLIST),
    'method': 'Read native netlist; arithmetic with explicit assumptions. No hardware test.',
    'topology_checks': len(expected_pins),
    'ldo_reference': 'TI SNVS015F, pp. 4-5: VIN >= 4.75 V, output characteristics for IOUT >= 5 mA.',
    'VIN_example': {'at_J10_V': 5.0, 'assumed_D1_drop_V': 0.35, 'at_U2_V': 5.0 - 0.35,
                    'required_U2_min_V': 4.75, 'margin_V': 5.0 - 0.35 - 4.75,
                    'note': 'Illustrative plausible diode drop, not guaranteed VF of an assembled part.'},
    'stop_all_low_no_external_load': {
        'assumptions': 'V33=3.3 V, LED10 VF=1.9 V, TLC555 Iq=0.2 mA, DISCH near 0 V. Typical estimate only.',
        'load_components': stop_model, 'estimated_total_mA': sum(stop_model.values()),
        'datasheet_min_mA': 5.0,
        'note': 'LM2937 ground/quiescent current does NOT count as its output load. Removing U1 for bring-up lowers load further.',
    },
    'proposed_preload': {'R_ohm': 560, 'tolerance': 0.01,
                         'minimum_mA_at_3V14_Rmax': 3.14 / (560 * 1.01) * 1000,
                         'maximum_mW_at_3V46_Rmin': 3.46**2 / (560 * 0.99) * 1000,
                         'temperature_drift_included': False},
    'heartbeat': {'RA_ohm': ra, 'RB_ohm': rb, 'C_F': c, 'nominal_Hz': f,
                  'H_duty': (ra + rb) / (ra + 2 * rb),
                  'R_1pct_C_10pct_only_min_Hz': f / (1.01 * 1.10),
                  'R_1pct_C_10pct_only_max_Hz': f / (0.99 * 0.90),
                  'note': 'Excludes timer thresholds, X7R temperature/bias effects and output-load waveform.'},
    'channels_loaded': {
        'nominal_H_with_10k_pulldown_V': v * 10000 / (resistance('RS1') + 10000),
        'nominal_H_with_two_10k_pulldowns_V': v * 5000 / (resistance('RS1') + 5000),
        'H_3V14_1pct_Rs_Rpd10k_V': 3.14 * 9900 / (resistance('RS1') * 1.01 + 9900),
        'H_3V14_1pct_Rs_Rpd5k_V': 3.14 * 4950 / (resistance('RS1') * 1.01 + 4950),
        'note': 'Resistive DC model, ignores contact resistance and input leakage; heartbeat additionally depends on TLC555 VOH.'},
    'ground_short_current_mA_at_3V46_Rmin': 3.46 / (resistance('RS1') * 0.99) * 1000,
}
(ROOT / 'operating-points.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, ensure_ascii=False, indent=2))
