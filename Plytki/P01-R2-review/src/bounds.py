"""Independent algebraic screening, using numeric values from KiCad export.
Intrinsic capacitance ceiling is an engineering assumption for bench verification.
"""
from dynamics import load,P
import json
c,pin,v=load(P/'verification/P01.xml')
c5=v['C5']*1.05;c6=v['C6']*.95;cg=2e-9
ratio=(c5+cg)/(c5+cg+c6) # ignore positive Cgs for conservative ratio in this envelope
vsg=48*ratio
drive=(8.9-.95-.3)*(.99*v['R22'])/(.99*v['R22']+1.01*v['R21'])
energy=.5*(v['C6']*1.05+v['C5']*1.05+10e-9)*18**2
report={'hotplug_48V_assumed_Cgd_ceiling_2nF_VSG_upper_V':vsg,'gate_on_conservative_low_input_VSG_V':drive,
 'R27_energy_upper_18V_J':energy,'R27_initial_power_upper_18V_W':18**2/(v['R27']*.99),
 'R23_power_at_VS48_Q2gate33_W':33**2/v['R23'],
 'D9_power_at_VS48_estimate_W':15*(33/v['R23']-15/v['R24']),
 'checks':[{'id':'hotplug_capacitive_divider','pass':vsg<=.8},{'id':'gate_on_dc','pass':drive>=4.5}],
 'limitations':'Cgd<=2nF is assumed, not guaranteed by manufacturer; ignores inductive ringing. Energy alone does not qualify SOA or resistor pulses.'}
(P/'verification/bounds.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
assert all(x['pass'] for x in report['checks'])
print(json.dumps(report,indent=2))
