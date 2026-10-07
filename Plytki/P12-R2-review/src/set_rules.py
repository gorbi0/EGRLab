"""Apply project rules after every board write; never waive individual DRCs (rules as P02 R3 / R4, annular ring >= 0.25 mm per S1).
P12 R2 (as R1, from P10 R2): Default track board.SIGNAL_W (0.3 mm), clearance 0.25; class PWR 1.0 mm / clearance 0.3 for 5V_SYS (~1.40 A of the
full stack, README) and P3V3 0.5 mm for 3V3_IO; vias 0.9 / 0.4 (ring 0.25)."""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from board import NAME, PWR, CORE, SIGNAL_W, P3V3
P = Path(__file__).resolve().parents[1]; fn = P / f'eda/{NAME}.kicad_pro'
d = json.loads(fn.read_text())
d.setdefault('board', {}).setdefault('design_settings', {}).setdefault('rules', {})
d['board']['design_settings']['rules'].update(
    min_clearance=.25, min_track_width=min(SIGNAL_W, .3), min_via_annular_width=.25, min_via_diameter=.9, min_through_hole_diameter=.4,
    min_hole_clearance=.25, min_hole_to_hole=.3, min_copper_edge_clearance=.5, min_silk_clearance=.15, min_text_height=1.0,
    min_text_thickness=.15)   # 2.10: JLCPCB legend minimum, enforced by DRC
d['board']['design_settings']['drc_exclusions'] = []
ns = d.setdefault('net_settings', {'meta': {'version': 5}, 'classes': []})
base = dict(clearance=.25, via_diameter=.9, via_drill=.4, microvia_diameter=.3, microvia_drill=.1, bus_width=12, wire_width=6,
            diff_pair_width=.5, diff_pair_gap=.3, diff_pair_via_gap=.3, pcb_color='rgba(0, 0, 0, 0.000)', schematic_color='rgba(0, 0, 0, 0.000)',
            line_style=0, priority=2147483647)
ns['classes'] = [dict(base, name='Default', track_width=SIGNAL_W), dict(base, name='CORE3V3', track_width=.3, priority=1),
                 dict(base, name='PWR', track_width=1.0, clearance=.3, priority=0), dict(base, name='P3V3', track_width=.5, priority=1)]
ns['netclass_assignments'] = None
ns['netclass_patterns'] = [{'netclass': 'PWR', 'pattern': n} for n in PWR] + [{'netclass': 'CORE3V3', 'pattern': n} for n in CORE] + \
    [{'netclass': 'P3V3', 'pattern': n} for n in P3V3]
fn.write_text(json.dumps(d, indent=2) + '\n')
print(f'Rules: clearance 0.25 / PWR 0.30, track {SIGNAL_W:.2f} (Default) / P3V3 0.50 (3V3_IO) / PWR 1.00 (5V_SYS), vias 0.9/0.4 (ring 0.25); no DRC exclusions.')
