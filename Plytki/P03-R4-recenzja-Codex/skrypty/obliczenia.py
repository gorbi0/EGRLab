"""Powtarzalne oszacowania recenzji; nie symulacja ani pomiary sprzętowe.

Uruchom: python obliczenia.py <P03-R4-review> <P04-R2.1-review> <wynik.json>
Stałe z kart producentów są jawnie oddzielone od danych projektu.
"""
from pathlib import Path
import hashlib, json, math, sys

p03, p04, output = map(Path, sys.argv[1:])
a = json.loads((p03 / 'docs/parts.json').read_text(encoding='utf-8'))
b = json.loads((p04 / 'docs/parts.json').read_text(encoding='utf-8'))
selected = {f'P03/{r}': a[r] for r in ['U3', 'U4', 'U6', 'R13', 'R34', 'R35', 'R41']}
selected.update({f'P04/{r}': b[r] for r in ['U9', 'R17']})
assert a['U4']['pins']['2'] == 'SUP_RAW_N'
assert set(a['R13']['pins'].values()) == {'SUP_RAW_N', '3V3_CORE'}
assert a['R13']['value'].upper() == '10K / 1%'
assert b['R17']['value'].upper() == '100K / 1%'
assert b['U9']['pins']['5'] == 'SUP_N'
assert set(b['R17']['pins'].values()) == {'SUP_N', 'GND'}

tau_ns = 10_000 * 4e-12 * 1e9
dt_ns = tau_ns * math.log((3.3 - 0.8) / (3.3 - 2.0))
result = {
    'kind': 'Analytical estimates, NOT hardware measurements',
    'project_parts': selected,
    'source_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in [p03/'docs/parts.json', p04/'docs/parts.json']},
    'U4_rise': {
        'R13_ohm': 10000, 'Ci_typical_only_pF': 4, 'Vcc_nominal_V': 3.3,
        'omitted_capacitance': 'TPS3808 output, PCB, test point and probe',
        'tau_ns': tau_ns, 'time_0p8_to_2p0_V_ns': dt_ns,
        'average_ns_per_V': dt_ns / 1.2,
        'local_ns_per_V_at_2p0_V': tau_ns / 1.3,
        'datasheet_limit_ns_per_V': 10,
    },
    'P04_default_low': {
        'assumption': 'Conservative same-sign magnitude sum; not a prediction of actual leakage direction or measured voltage',
        'Ioff_U6_max_uA': 10,
        'Iin_U9_max_uA_up_to_85C': 5, 'Iin_U9_max_uA_up_to_125C': 20,
        'resistor_tolerance': 0.01,
        'R17_100k_V_85C': 15e-6 * 101000,
        'R17_100k_V_125C': 30e-6 * 101000,
        'R17_10k_V_85C': 15e-6 * 10100,
        'R17_10k_V_125C': 30e-6 * 10100,
        'VIL_max_V': 0.8,
    },
    'SUP_N_low': {
        'assumption': 'Conservative VOL=0.4 V; two nominal 10k pull-ups, R34=220 ohm',
        'V_at_Vcc_3p3': (0.4 * 5000 + 3.3 * 220) / 5220,
        'V_at_Vcc_3p0': (0.4 * 5000 + 3.0 * 220) / 5220,
        'V_at_Vcc_3p0_resistor_extremes_1percent': (0.4 * 4950 + 3 * 222.2) / (4950 + 222.2),
    },
    'R41_ideal_only': {
        'R_ohm': 220, 'C_assumed_pF': 20,
        'tau_ns': 220 * 20e-12 * 1e9,
        't10_90_ns': math.log(9) * 220 * 20e-12 * 1e9,
        'C_pF_at_ideal_falling_limit': 10e-9 * 0.8 / 220 * 1e12,
        'omitted': 'Driver output impedance, finite slew, nonzero VOL, cable shape, probe load; hence NOT a guaranteed C limit',
    },
    'sources': [
        'https://www.ti.com/lit/ds/symlink/sn74lvc1g07.pdf',
        'https://www.ti.com/lit/ds/symlink/sn74lvc1g17.pdf',
        'https://assets.nexperia.com/documents/data-sheet/74LVC125A.pdf',
        'https://www.ti.com/lit/gpn/TPS3808',
        'https://www.ti.com/lit/gpn/SN74LVC1G37',
    ],
}
output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Zapisano obliczenia:', output)
