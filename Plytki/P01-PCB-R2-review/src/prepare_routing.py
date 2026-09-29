from pathlib import Path
import json,shutil,copy
P=Path(__file__).resolve().parents[1]
f=P/'routing/P01.dsn';d=f.read_text()
assert 'BAT_FUSED GND' in d and '\n  )\n  (wiring' in d
d=d.replace('BAT_FUSED GND','BAT_FUSED',1)
d=d.replace('\n  )\n  (wiring','\n    (class GROUND GND (circuit (use_via "Via[0-1]_1000:500_um")) (rule (width 500) (clearance 300)))\n  )\n  (wiring',1)
f.write_text(d)
shutil.copy2(P/'eda/P01.kicad_pcb',P/'routing/prerouted.kicad_pcb')
settings={
 'board':{'design_settings':{'rules':{'min_clearance':.25,'min_track_width':.3,'min_via_annular_width':.2,'min_via_diameter':.8,'min_through_hole_diameter':.4,'min_hole_clearance':.25,'min_hole_to_hole':.3,'min_copper_edge_clearance':.5,'min_silk_clearance':.15,'min_text_height':.8,'min_text_thickness':.12},'drc_exclusions':[]}},
 'net_settings':{'meta':{'version':5},'classes':[{'name':'Default','clearance':.3,'track_width':.5,'via_diameter':1,'via_drill':.5,'microvia_diameter':.3,'microvia_drill':.1,'bus_width':12,'wire_width':6,'diff_pair_width':.5,'diff_pair_gap':.3,'diff_pair_via_gap':.3}], 'netclass_assignments':{},'netclass_patterns':[]},
 'meta':{'filename':'P01.kicad_pro','version':3}}
(P/'eda/P01.kicad_pro').write_text(json.dumps(settings,indent=2))
print('DSN: GROUND excluded from signal autorouting; geometry locked.')
