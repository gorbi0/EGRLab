"""P05 R3 board configuration for the layout chain. The generic layout scripts (build_board, fanout_gnd, prepare_routing, run_layout,
import_routing, stitch, complete_routes, cleanup, silkscreen, ...) come from P03 R6 via P09 R2 / P10 R2 (1.10.2026, Ubuntu 24/7 session)
and read their board specific values from here.
"""
NAME = 'P05'                 # eda/P05.kicad_pcb, routing/P05.dsn / P05.ses, verification/P05.xml
REV = 'P05 R3'
TITLE = 'EGRLab P05 R3 DAQ / format S1, klasa 2/3, sloty S1-S2 poziomu 3'
CLASS = '2/3'                # Plytki/Format-S1/format-s1.json 'klasy'
SLOTS = ['S1', 'S2']         # S1 section 7: P05 on level 3, slots S1-S2 (P09 in S3)
JBP = ['J_BP1', 'J_BP2']     # edge-A IDC (odd pins GND): GND comb in fanout_gnd.py
JSV = ['J_SV1', 'J_SV2']     # edge-B service headers
GND_REF = ('J_BP2', '1')     # reference pad of the main GND cluster (stitch.py)
PWR = ['5VA_P05']            # class PWR (0.6 mm, clearance 0.3): R1 1 Ohm -> C1 -> analog side of U1 and LDO U12 (about 60 mA).
                             # 5V_SYS (about 150 mA: coils 3 x 30 mA, R1 60 mA) is routed at 0.3 mm like P09 / P10: a 0.6 mm
                             # track cannot reach U3.8 (VSSOP 0.65 mm); 100 mm of 0.3 mm copper drops about 25 mV at 150 mA
CORE = ['3V3_DAQ']           # class CORE3V3 (0.3 mm): LDO U12 output to the logic side of U1 and the buffers
SIGNAL_W = .3                # Default track: S1 section 3 (rules as P02-R3)
SUPPORT_KEEPOUT = {}         # no NPTH support holes (SW1 support legs are plated pads of its footprint)
PIN_MARKS = {'J4': {'1': '1'}, 'J6': {'1': '1'}}   # S1 section 9: pin 1 of the soldered TAPS / AUX tails
FINE = ['U1', 'U3']           # fine-pitch parts (LQFP-64 0.5 mm, VSSOP-8 0.65 mm): custom rules in set_rules.py / eda/P05.kicad_dru
FINE_CLEARANCE, FINE_TRACK = .15, .2   # only between items inside their courtyards (README: exception to S1 section 3, with reason)
GND_INNER = ['U1']            # GND pins tied by the pour inside the pad ring (route_critical.py): out of the router's GND net list
TOP_ONLY = []                # nets in a DSN class limited to F.Cu (complete_routes.py; P06 R2 tool). 2.10 trial on P05 with the eight longest
                             # B.Cu nets: 61 open connections after 9 passes instead of 7 (their service-resistor pads sit on the bottom)
ISOLATE = {'VBAT_SENSE': .8}   # review 2.10 (MINOR-2): DSN class clearance in mm (prepare_routing.py; verify_pcb.py measures VBAT -> TAP_*):
                             # VBAT_SENSE ran 13.7 mm at 0.26 mm beside TAP_P6 (CH5, 100 kOhm / 220 pF); KiCad keeps the S1 rules (J_BP1 pins)
# review 2.10 (MAJOR-2): a GND via at every SMD decoupling / filter capacitor outside U1 (stitch.py stage 4, after the completion planner;
# U1's capacitors have theirs from route_critical.py); verify_pcb.py measures the return to the part's GND pin
EXTRA_GND_VIAS = [('pad', c, '2', 2.0) for c in ('C2', 'C3', 'C6', 'C14', 'C15', 'C16', 'C17', 'C18', 'C19', 'C20', 'C21', 'C22', 'C23', 'C24',
                                                 'C25', 'C26', 'C27', 'C28', 'C29', 'C30', 'C31', 'C33', 'C34')]
PLANNER_KEEPOUT = [('F.Cu', 51.3, 47.3, 64.7, 60.7),   # completion planner (complete_routes.py) and placement: no new copper in U1 /
                   ('F.Cu', 38.3, 33.73, 44.7, 37.27),  # U3, none on B.Cu under U1 and the input fan / filter column; the planner starts
                   ('B.Cu', 44.0, 43.0, 65.0, 62.0),    # at the free end of a locked escape (U1 / U3 pins sit inside)
                   ('B.Cu', 50.4, 40.2, 63.1, 47.3)]    # review 2.10: B.Cu under the top capacitors (their GND vias, 5VA stubs)
ROUTER_KEEPOUT = [('F.Cu', 53.25, 49.25, 62.75, 58.75),   # inside the U1 pad ring (no pin in it; run 7 took SCLK through it)
                  ('B.Cu', 51.3, 47.3, 64.7, 49.2), ('B.Cu', 51.3, 59.95, 64.7, 60.7),   # B.Cu bands around the 100 nF under U1
                  ('B.Cu', 51.3, 47.3, 52.3, 60.7), ('B.Cu', 63.0, 47.3, 64.7, 60.7),    # (run 8: ADC_DOUTA grazed the courtyard)
                  # review 2.10 (MAJOR-1 / -2): B.Cu stays GND under the input fan (the returns of C27-C34 cross it to the via column
                  # inside the left pins) and under the top capacitors (their GND vias drop straight to U1); pin-free on B.Cu (C32 and
                  # TP5 / TP3 / TP2 / TP4 are THT: the boxes stop 0.1 mm short of their pads)
                  ('B.Cu', 45.4, 46.4, 51.3, 64.5), ('B.Cu', 50.4, 40.2, 63.1, 47.3),
                  ('B.Cu', 42.4, 46.4, 45.4, 56.9), ('B.Cu', 42.4, 59.0, 45.4, 64.5)]   # 2.10: on to the filter GND pads (C32 THT pad left out)
                             # 1.10 run 6: DSN keepouts holding pins (U1, U3, the 100 nF under U1) left Freerouting 20-105 open
                             # connections (3V3_DAQ almost unrouted); without them 0 signal gaps. run_layout.py rejects an attempt
                             # whose router copper touches the U1 courtyard instead (inner GND pour, review P5-01)
# 2.10 (verify_pcb.py return-path checks): capacitor -> GND pin of its part; complete_routes.py --ties plans a GND track where the GND copper
# path is longer than 1.3 x straight + 3 mm (U1's pins sit in the planner keepouts: its capacitors rely on route_critical.py); a third
# item is the goal point when the pin itself is out of the planner's reach (C15: the GND via of U3.4, route_critical.py route_u3)
RETURN_PAIRS = {'C2': ('U12', '1'), 'C3': ('U12', '1'), 'C14': ('U2', '4'), 'C24': ('U2', '4'), 'C15': ('U3', '4', (37.0, 37.08)), 'C16': ('U5', '7'),
                'C17': ('U6', '3'), 'C18': ('U7', '3'), 'C19': ('U8', '7'), 'C20': ('U9', '7'), 'C21': ('U10', '7'), 'C22': ('U11', '7')}
