"""Apply project-specific rules after board import; never waive individual DRCs."""
from pathlib import Path
import json
P=Path(__file__).resolve().parents[1];fn=P/'eda/P01.kicad_pro';d=json.loads(fn.read_text())
r=d['board']['design_settings']['rules']
r.update(min_clearance=.25,min_track_width=.3,min_via_annular_width=.2,min_via_diameter=.8,
 min_through_hole_diameter=.4,min_hole_clearance=.25,min_hole_to_hole=.3,
 min_copper_edge_clearance=.5,min_silk_clearance=.15,min_text_height=.8,min_text_thickness=.12)
d['board']['design_settings']['drc_exclusions']=[]
c=d['net_settings']['classes'][0];assert c['name']=='Default'
c.update(clearance=.3,track_width=.5,via_diameter=1,via_drill=.5)
fn.write_text(json.dumps(d,indent=2)+'\n')
print('Applied explicit 0.30 mm net clearance; no DRC exclusions.')
