"""Apply project rules after every board write; never waive individual DRCs (rules as P02 R3 / R4, annular ring >= 0.25 mm per S1).
Net classes (P03 R6): PWR 0.6 mm / clearance 0.3 for 5V_SYS and 5V_M1 (the main 5 V path is the locked 1.5 mm copper of
route_critical.py; the router adds only U5, R44, R45, TP1, TP7). 3V3_CORE stays in Default (0.3 mm): a wider track does not pass
between pins at 2.54 mm pitch (1.7 mm pads leave 0.84 mm; 0.5 mm + 2 x 0.25 mm needs 1.0 mm), so in the first router runs the
3.3 V supply of the right half had to go round M1 and its antenna keepout (30.09). 0.3 mm over ~150 mm at 100 mA (SD card): ~25 mV.
R5 had one 'Power' class 0.6 mm with vias 1.0 / 0.5 for the four supply nets; vias are now 0.9 / 0.4 everywhere (ring 0.25)."""
from pathlib import Path
import json
P = Path(__file__).resolve().parents[1]; fn = P / 'eda/P03.kicad_pro'
PWR = ['5V_SYS', '5V_M1']
d = json.loads(fn.read_text())
d.setdefault('board', {}).setdefault('design_settings', {}).setdefault('rules', {})
d['board']['design_settings']['rules'].update(
    min_clearance=.25, min_track_width=.3, min_via_annular_width=.25, min_via_diameter=.9, min_through_hole_diameter=.4,
    min_hole_clearance=.25, min_hole_to_hole=.3, min_copper_edge_clearance=.5, min_silk_clearance=.15, min_text_height=.8,
    min_text_thickness=.12)
d['board']['design_settings']['drc_exclusions'] = []
ns = d.setdefault('net_settings', {'meta': {'version': 5}, 'classes': []})
base = dict(clearance=.25, via_diameter=.9, via_drill=.4, microvia_diameter=.3, microvia_drill=.1, bus_width=12, wire_width=6,
            diff_pair_width=.5, diff_pair_gap=.3, diff_pair_via_gap=.3, pcb_color='rgba(0, 0, 0, 0.000)', schematic_color='rgba(0, 0, 0, 0.000)',
            line_style=0, priority=2147483647)
ns['classes'] = [dict(base, name='Default', track_width=.3), dict(base, name='PWR', track_width=.6, clearance=.3, priority=0)]
ns['netclass_assignments'] = None
ns['netclass_patterns'] = [{'netclass': 'PWR', 'pattern': n} for n in PWR]
fn.write_text(json.dumps(d, indent=2) + '\n')
print('Rules: clearance 0.25 / PWR 0.30, track 0.30 / PWR 0.60, vias 0.9/0.4 (ring 0.25); no DRC exclusions.')
