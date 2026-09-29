"""Apply project-specific rules after board import; never waive individual DRCs.
Board minimums as P01/P02/P00 (0.25 mm clearance, 0.3 mm track). Net classes differ from P00/P02 on purpose:
- Default (signals): 0.30 mm track / 0.25 mm clearance, so one track fits between two 2.54 mm THT pads
  (header and DIP rows of P03 are dense; 0.5/0.3 would force every signal around the rows);
- Power (5V_SYS, 3V3_CORE, 3V3_IO): 0.60 mm track / 0.30 mm clearance, via 1.0/0.5.
"""
from pathlib import Path
import json
P = Path(__file__).resolve().parents[1]; fn = P / 'eda/P03.kicad_pro'
try:
    d = json.loads(fn.read_text())
except (FileNotFoundError, json.JSONDecodeError):
    d = {}
d.setdefault('board', {}).setdefault('design_settings', {}).setdefault('rules', {})
d['board']['design_settings']['rules'].update(
    min_clearance=.25, min_track_width=.3, min_via_annular_width=.2, min_via_diameter=.8, min_through_hole_diameter=.4,
    min_hole_clearance=.25, min_hole_to_hole=.3, min_copper_edge_clearance=.5, min_silk_clearance=.15, min_text_height=.8,
    min_text_thickness=.12)
d['board']['design_settings']['drc_exclusions'] = []
ns = d.setdefault('net_settings', {'meta': {'version': 5}, 'classes': []})
common = dict(microvia_diameter=.3, microvia_drill=.1, bus_width=12, wire_width=6, diff_pair_width=.3, diff_pair_gap=.25, diff_pair_via_gap=.25)
ns['classes'] = [dict(name='Default', clearance=.25, track_width=.3, via_diameter=.8, via_drill=.4, **common),
                 dict(name='Power', clearance=.3, track_width=.6, via_diameter=1.0, via_drill=.5, **common)]
ns['netclass_assignments'] = {}
ns['netclass_patterns'] = [{'netclass': 'Power', 'pattern': n} for n in ('/5V_SYS', '3V3_CORE', '3V3_IO')]
d.setdefault('meta', {'filename': 'P03.kicad_pro', 'version': 3})
fn.write_text(json.dumps(d, indent=2) + '\n')
print('Rules: Default 0.30/0.25 mm, Power (5V_SYS, 3V3_CORE, 3V3_IO) 0.60/0.30 mm; no DRC exclusions.')
