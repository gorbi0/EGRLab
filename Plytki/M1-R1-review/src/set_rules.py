"""Apply project rules after every board write; never waive individual DRCs (P07 S1 classes / vias + P05 R3 fine-pitch rules).
Default track board.SIGNAL_W (0.2 mm), clearance 0.25; class PWR (board.PWR) 0.5 mm; vias 0.6 / 0.3 (signal / fan-out), 0.9 / 0.4 (PWR,
stitching). U3 AD7606B (LQFP-64, 0.5 mm pitch, 0.2 mm between pads): custom rules (eda/M1.kicad_dru) as P05 R3 - clearance 0.15 only
between two items that both touch the U3 courtyard, track >= 0.2 there, pours 0.15 mm only to copper wholly inside the pad ring
(rule area DRC_ONLY_U3, import_routing.py). JLCPCB 4-layer minimum 0.09 / 0.09 mm."""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from board import NAME, PWR, SIGNAL_W, PWR_W, PWR_CLR, SIG_VIA, FINE, FINE_CLEARANCE, FINE_TRACK
P = Path(__file__).resolve().parents[1]; fn = P / f'eda/{NAME}.kicad_pro'
d = json.loads(fn.read_text())
d.setdefault('board', {}).setdefault('design_settings', {}).setdefault('rules', {})
d['board']['design_settings']['rules'].update(
    min_clearance=FINE_CLEARANCE, min_track_width=min(SIGNAL_W, FINE_TRACK), min_via_annular_width=round((SIG_VIA[0] - SIG_VIA[1]) / 2, 3),
    min_via_diameter=SIG_VIA[0], min_through_hole_diameter=SIG_VIA[1], min_hole_clearance=.25, min_hole_to_hole=.3, min_copper_edge_clearance=.5,
    min_silk_clearance=.15, min_text_height=1.0, min_text_thickness=.15)
d['board']['design_settings']['drc_exclusions'] = []
ns = d.setdefault('net_settings', {'meta': {'version': 5}, 'classes': []})
base = dict(clearance=.25, via_diameter=SIG_VIA[0], via_drill=SIG_VIA[1], microvia_diameter=.3, microvia_drill=.1, bus_width=12, wire_width=6,
            diff_pair_width=.5, diff_pair_gap=.3, diff_pair_via_gap=.3, pcb_color='rgba(0, 0, 0, 0.000)', schematic_color='rgba(0, 0, 0, 0.000)',
            line_style=0, priority=2147483647)
ns['classes'] = [dict(base, name='Default', track_width=SIGNAL_W), dict(base, name='PWR', track_width=PWR_W, clearance=PWR_CLR, via_diameter=.9, via_drill=.4, priority=0)]
ns['netclass_assignments'] = None
ns['netclass_patterns'] = [{'netclass': 'PWR', 'pattern': n} for n in PWR]
fn.write_text(json.dumps(d, indent=2) + '\n')
touch = lambda who: ' || '.join(f"A.intersectsCourtyard('{r}')" for r in who)
both = ' || '.join(f"(A.intersectsCourtyard('{r}') && B.intersectsCourtyard('{r}'))" for r in FINE)
ring = ' || '.join(f"B.enclosedByArea('DRC_ONLY_{r}')" for r in FINE)
(P / f'eda/{NAME}.kicad_dru').write_text(f'''(version 1)
(rule "drobny raster {' / '.join(FINE)}: odstep {FINE_CLEARANCE:.2f} mm miedzy elementami w obrysie ukladu (bez wylewek)"
  (condition "A.Type != 'Zone' && B.Type != 'Zone' && ({both})")
  (constraint clearance (min {FINE_CLEARANCE:.2f}mm)))
(rule "drobny raster {' / '.join(FINE)}: wylewka {FINE_CLEARANCE:.2f} mm tylko do miedzi calej w pierscieniu padow"
  (condition "A.Type == 'Zone' && ({ring})")
  (constraint clearance (min {FINE_CLEARANCE:.2f}mm)))
''', encoding='utf-8')
print(f'Rules: clearance 0.25 (fine pitch {FINE}: {FINE_CLEARANCE} / track {FINE_TRACK}), track {SIGNAL_W:.2f} (Default) / PWR {PWR_W:.2f}, vias {SIG_VIA[0]}/{SIG_VIA[1]} (PWR 0.9/0.4); no DRC exclusions.')
