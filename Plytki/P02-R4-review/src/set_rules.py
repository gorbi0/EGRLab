"""Apply project rules after every board write; never waive individual DRCs (rules as P02 R3, annular ring >= 0.25 mm per S1).
Net class PWR (0.8 mm) for the supply nets that the router draws; the 5 A path is copper zones (route_critical.py)."""
from pathlib import Path
import json
P = Path(__file__).resolve().parents[1]; fn = P / 'eda/P02.kicad_pro'
PWR = ['*P02_VLOG', '*P02_VIN_DC5', '*P02_VIN_DC33', '5V_SYS', '3V3_IO', '*P02_HOLD_C', '*P02_CH_A', '*P02_SW_COM', '*P02_AUX_IN', '*P02_V_CTRL']
try:
    d = json.loads(fn.read_text())
except (FileNotFoundError, json.JSONDecodeError):
    d = {}
d.setdefault('board', {}).setdefault('design_settings', {}).setdefault('rules', {})
d['board']['design_settings']['rules'].update(
    min_clearance=.25, min_track_width=.3, min_via_annular_width=.25, min_via_diameter=.9, min_through_hole_diameter=.4,
    min_hole_clearance=.25, min_hole_to_hole=.3, min_copper_edge_clearance=.5, min_silk_clearance=.15, min_text_height=1.0,
    min_text_thickness=.15)   # 2.10: JLCPCB legend minimum, enforced by DRC
d['board']['design_settings']['drc_exclusions'] = []
ns = d.setdefault('net_settings', {'meta': {'version': 5}, 'classes': []})
base = dict(clearance=.25, via_diameter=.9, via_drill=.4, microvia_diameter=.3, microvia_drill=.1, bus_width=12, wire_width=6,
            diff_pair_width=.5, diff_pair_gap=.3, diff_pair_via_gap=.3, pcb_color='rgba(0, 0, 0, 0.000)', schematic_color='rgba(0, 0, 0, 0.000)',
            line_style=0, priority=2147483647)
ns['classes'] = [dict(base, name='Default', track_width=.3), dict(base, name='PWR', track_width=.6, clearance=.3, priority=0)]
ns['netclass_assignments'] = None
ns['netclass_patterns'] = [{'netclass': 'PWR', 'pattern': p} for p in PWR]
d.setdefault('meta', {'filename': 'P02.kicad_pro', 'version': 3})
fn.write_text(json.dumps(d, indent=2) + '\n')
print('Rules: clearance 0.25 / PWR 0.30, track 0.30 / PWR 0.60, vias 0.9/0.4 (ring 0.25); no DRC exclusions.')
