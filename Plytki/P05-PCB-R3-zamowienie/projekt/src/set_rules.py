"""Apply project rules after every board write; never waive individual DRCs (rules as P02 R3 / R4, annular ring >= 0.25 mm per S1).
P05 R3 (1.10.2026): first S1 board with fine-pitch parts - U1 AD7606B LQFP-64 (0.5 mm pitch, 0.2 mm between pads) and U3 TLV1702
VSSOP-8 (0.65 mm, 0.15 mm between pads); the S1 values (clearance 0.25, track 0.3) cannot reach their pins. Custom rules
(eda/P05.kicad_dru): clearance 0.15 only between two items that both touch the courtyard of U1 (or both of U3), track >= 0.2 only
for tracks touching those courtyards, track >= 0.3 everywhere else (S1). Board minimums 0.15 / 0.2 are the floor for these rules;
both stay above the JLCPCB 2-layer minimum (0.1 / 0.1). README: exception with reason.
P10 R2 (from P03 R6 via P09 R2, 30.09.2026): Default track board.SIGNAL_W (0.3 mm, S1 section 3), clearance 0.25; classes PWR (0.6 / 0.3)
and CORE3V3 (0.3) only for the nets listed in board.py (none on P10: 5V_SYS carries ~70 mA for the transceiver, README); vias 0.9 / 0.4 (ring 0.25)."""
from pathlib import Path
import json, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from board import NAME, PWR, CORE, SIGNAL_W, FINE, FINE_CLEARANCE, FINE_TRACK
P = Path(__file__).resolve().parents[1]; fn = P / f'eda/{NAME}.kicad_pro'
d = json.loads(fn.read_text())
d.setdefault('board', {}).setdefault('design_settings', {}).setdefault('rules', {})
d['board']['design_settings']['rules'].update(
    min_clearance=FINE_CLEARANCE, min_track_width=FINE_TRACK, min_via_annular_width=.25, min_via_diameter=.9, min_through_hole_diameter=.4,
    min_hole_clearance=.25, min_hole_to_hole=.3, min_copper_edge_clearance=.5, min_silk_clearance=.15, min_text_height=1.0,
    min_text_thickness=.15)   # review 2.10 (MINOR-5): JLCPCB legend minimum, enforced by DRC
d['board']['design_settings']['drc_exclusions'] = []
ns = d.setdefault('net_settings', {'meta': {'version': 5}, 'classes': []})
base = dict(clearance=.25, via_diameter=.9, via_drill=.4, microvia_diameter=.3, microvia_drill=.1, bus_width=12, wire_width=6,
            diff_pair_width=.5, diff_pair_gap=.3, diff_pair_via_gap=.3, pcb_color='rgba(0, 0, 0, 0.000)', schematic_color='rgba(0, 0, 0, 0.000)',
            line_style=0, priority=2147483647)
ns['classes'] = [dict(base, name='Default', track_width=SIGNAL_W), dict(base, name='CORE3V3', track_width=.3, priority=1),
                 dict(base, name='PWR', track_width=.6, clearance=.3, priority=0)]
ns['netclass_assignments'] = None
ns['netclass_patterns'] = [{'netclass': 'PWR', 'pattern': n} for n in PWR] + [{'netclass': 'CORE3V3', 'pattern': n} for n in CORE]
fn.write_text(json.dumps(d, indent=2) + '\n')
touch = lambda who: ' || '.join(f"A.intersectsCourtyard('{r}')" for r in who)
both = ' || '.join(f"(A.intersectsCourtyard('{r}') && B.intersectsCourtyard('{r}'))" for r in FINE)
# review 2.10 (MINOR-1): the pours are zones that always touch the courtyards, so the item rule gave them 0.15 mm everywhere (GND pour
# 0.15 mm from copper up to 3.9 mm outside U1 / U3). Items: no zone in that rule. Pours: 0.15 mm only to copper wholly inside the pad
# ring (rule areas DRC_ONLY_U1 / _U3: pads, inner stubs and vias - with 0.3 to the vias the pour lost U1.35 / U1.43 in six runs);
# 0.30 (zone) to the escapes that leave the ring and to everything else.
ring = ' || '.join(f"B.enclosedByArea('DRC_ONLY_{r}')" for r in FINE)   # rule areas made by import_routing.py
(P / f'eda/{NAME}.kicad_dru').write_text(f'''(version 1)
(rule "S1 tor >= {SIGNAL_W:.2f} mm poza drobnym rastrem"
  (condition "A.Type == 'Track' && !({touch(FINE)})")
  (constraint track_width (min {SIGNAL_W:.2f}mm)))
(rule "drobny raster {' / '.join(FINE)}: tor >= {FINE_TRACK:.2f} mm"
  (condition "A.Type == 'Track' && ({touch(FINE)})")
  (constraint track_width (min {FINE_TRACK:.2f}mm)))
(rule "drobny raster {' / '.join(FINE)}: odstep {FINE_CLEARANCE:.2f} mm miedzy elementami w obrysie ukladu (bez wylewek)"
  (condition "A.Type != 'Zone' && B.Type != 'Zone' && ({both})")
  (constraint clearance (min {FINE_CLEARANCE:.2f}mm)))
(rule "drobny raster {' / '.join(FINE)}: wylewka {FINE_CLEARANCE:.2f} mm tylko do miedzi calej w pierscieniu padow"
  (condition "A.Type == 'Zone' && ({ring})")
  (constraint clearance (min {FINE_CLEARANCE:.2f}mm)))
''', encoding='utf-8')
print(f'Rules: clearance 0.25 / PWR 0.30 (fine pitch {FINE}: {FINE_CLEARANCE} / track {FINE_TRACK}), track {SIGNAL_W:.2f} (Default) / CORE3V3 0.30 / PWR 0.60, vias 0.9/0.4 (ring 0.25); no DRC exclusions.')
