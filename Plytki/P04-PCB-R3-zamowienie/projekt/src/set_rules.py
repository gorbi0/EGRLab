"""Apply project rules after every board write; never waive individual DRCs (rules as P02 R3 / R4, annular ring >= 0.25 mm per S1).
P04 R3 (5.10.2026, from P05 R3 set_rules.py): no fine-pitch part, so no custom rules file (eda/P04.kicad_dru is removed if present).
Default: track board.SIGNAL_W (0.3 mm, S1 section 3), clearance 0.25; class PWR (board.PWR: 3V3_IO, P04_3V3, PANEL_3V3, 5V_SYS)
track board.PWR_W (0.4 mm, task 5.10) with the S1 clearance; vias 0.9 / 0.4 (ring 0.25); silkscreen >= 1.0 / 0.15 mm (JLCPCB)."""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from board import NAME, PWR, CORE, SIGNAL_W, PWR_W, PWR_CLR
P = Path(__file__).resolve().parents[1]; fn = P / f'eda/{NAME}.kicad_pro'
d = json.loads(fn.read_text())
d.setdefault('board', {}).setdefault('design_settings', {}).setdefault('rules', {})
d['board']['design_settings']['rules'].update(
    min_clearance=.25, min_track_width=SIGNAL_W, min_via_annular_width=.25, min_via_diameter=.9, min_through_hole_diameter=.4,
    min_hole_clearance=.25, min_hole_to_hole=.3, min_copper_edge_clearance=.5, min_silk_clearance=.15, min_text_height=1.0,
    min_text_thickness=.15)
d['board']['design_settings']['drc_exclusions'] = []
ns = d.setdefault('net_settings', {'meta': {'version': 5}, 'classes': []})
base = dict(clearance=.25, via_diameter=.9, via_drill=.4, microvia_diameter=.3, microvia_drill=.1, bus_width=12, wire_width=6,
            diff_pair_width=.5, diff_pair_gap=.3, diff_pair_via_gap=.3, pcb_color='rgba(0, 0, 0, 0.000)', schematic_color='rgba(0, 0, 0, 0.000)',
            line_style=0, priority=2147483647)
ns['classes'] = [dict(base, name='Default', track_width=SIGNAL_W), dict(base, name='PWR', track_width=PWR_W, clearance=PWR_CLR, priority=0)]
ns['netclass_assignments'] = None
ns['netclass_patterns'] = [{'netclass': 'PWR', 'pattern': n} for n in PWR]
fn.write_text(json.dumps(d, indent=2) + '\n')
(P / f'eda/{NAME}.kicad_dru').unlink(missing_ok=True)
print(f'Rules: clearance 0.25, track {SIGNAL_W:.2f} (Default) / PWR {PWR_W:.2f} ({", ".join(PWR)}), vias 0.9/0.4 (ring 0.25); no custom rules, no DRC exclusions.')
