"""Apply project-specific rules after board import; never waive individual DRCs (same rules as P01)."""
from pathlib import Path
import json
P = Path(__file__).resolve().parents[1]; fn = P / 'eda/P06.kicad_pro'
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
classes = ns.setdefault('classes', [])
if not classes or classes[0].get('name') != 'Default':
    classes.insert(0, {'name': 'Default'})
classes[0].update(clearance=.25, track_width=.3, via_diameter=.8, via_drill=.4, microvia_diameter=.3, microvia_drill=.1,
                  bus_width=12, wire_width=6, diff_pair_width=.5, diff_pair_gap=.3, diff_pair_via_gap=.3)
ns.setdefault('netclass_assignments', {}); ns.setdefault('netclass_patterns', [])
d.setdefault('meta', {'filename': 'P06.kicad_pro', 'version': 3})
fn.write_text(json.dumps(d, indent=2) + '\n')
print('Applied explicit 0.25 mm net clearance; no DRC exclusions.')
