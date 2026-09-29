"""Independent energy lower bound and charging envelope, not a converter SPICE model."""
from pathlib import Path
import json,math
P=Path(__file__).resolve().parents[1]
c=json.loads((P/'integration/P02-HOLD/contract.json').read_text())
v0=c['minimum_cap_initial_V']-c['path_drop_acceptance_max_V']
energy=.5*c['C_effective_acceptance_min_F']*(v0*v0-c['minimum_bus_during_hold_V']**2)
duration=energy/(c['power_limit_at_VLOG_RES_W']+c['leakage_plus_bleeder_reserve_W'])
# Drop treated as a constant maximum; stored usable energy on the load side.
# No contribution from P01, no output-cap credit, no claimed SD shutdown reserve.
rmin=c['R_charge_ohm']*(1-c['R_charge_tolerance'])
result={'source':'integration/P02-HOLD/contract.json','usable_load_energy_J':energy,
        'hold_lower_bound_ms':duration*1000,'required_ms':c['hold_required_ms'],
        'charging_I_upper_at_18V_A':18/rmin,'charging_R_power_upper_at_18V_W':18**2/rmin,
        'charging_R_power_upper_at_32V_W':32**2/rmin,
        'RC_5tau_max_s':5*c['R_charge_ohm']*1.05*c['C_nominal_F']*1.2,
        'max_stored_energy_32V_J':.5*c['C_nominal_F']*1.2*32**2,
        'bleed_to_1V_from_18V_s':c['R_bleed_ohm']*1.05*c['C_nominal_F']*1.2*math.log(18),
        'pass':duration*1000>=c['hold_required_ms'],
        'conditions':'Actual capacitance, total path drop and input power must meet contract over 0..50C; no power-fail SD commit guarantee.'}
assert result['pass']
(P/'verification/hold-budget.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
