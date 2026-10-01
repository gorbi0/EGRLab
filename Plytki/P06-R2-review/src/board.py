"""P06 R2 board configuration for the layout chain. The generic layout scripts (build_board, fanout_gnd, prepare_routing, run_layout,
import_routing, stitch, complete_routes, cleanup, trim_stubs, silkscreen, ...) come from P05 R3 (P03 R6 -> P09 R2 / P10 R2 -> P05 R3,
1.10.2026, Ubuntu 24/7 session) and read their board specific values from here.
"""
NAME = 'P06'                 # eda/P06.kicad_pcb, routing/P06.dsn / P06.ses, verification/P06.xml
REV = 'P06 R2'
TITLE = 'EGRLab P06 R2 I-LOGGER / format S1, klasa 2/3, sloty S1-S2 poziomu 4'
CLASS = '2/3'                # Plytki/Format-S1/format-s1.json 'klasy'
SLOTS = ['S1', 'S2']         # S1 section 7: P06 on level 4, slots S1-S2 (P10 in S3)
JBP = ['J_BP']               # edge-A IDC (odd pins GND): GND comb in fanout_gnd.py
JSV = ['J_SV1', 'J_SV2']     # edge-B service headers
GND_REF = ('J_BP', '1')      # reference pad of the main GND cluster (stitch.py)
PWR = ['5V_SYS', '5VA_P06', 'SW_RAW']   # class PWR (0.6 mm, clearance 0.3): J_BP -> R6 1 Ohm -> 5VA_P06 (180 mA in MEASURE, of it
                             # about 130 mA through the BYPASS status contact: J5.1 -> SW1 pole B -> J5.2 = SW_RAW -> R21 39 Ohm -> GND)
CORE = ['3V3_P06']           # class CORE3V3 (0.3 mm): LDO U4 output
SIGNAL_W = .3                # Default track: S1 section 3 (rules as P02-R3)
FORCE = ['ECU_P1', 'EGR_P1']  # motor current 5-6 A (10 A passive test E15): locked pours on both layers (route_critical.py), router keepouts
KELVIN = ['K_PLUS', 'K_MINUS', 'INA_PLUS', 'INA_MINUS']   # locked pair RSH1 -> R1 / R2 -> U1 (route_critical.py), out of the router's list
SUPPORT_KEEPOUT = {'J3': 3.0, 'J4': 3.0, 'J5': 3.0}   # NPTH cable-tie anchors of the three tails: no copper within 3 mm of their centres
PIN_MARKS = {'J3': {'1': 'ECU', '2': 'EGR'}, 'J4': {'1': 'ECU', '2': 'EGR'}, 'J5': {'1': '5VA', '2': 'SW', '3': 'GND'}}   # S1 section 9
FINE = []                    # no fine-pitch parts (SOIC 1.27 mm: S1 values reach every pin)
FINE_CLEARANCE, FINE_TRACK = .25, SIGNAL_W
GND_INNER = []               # (P05 R3: GND pins tied by an inner pour, out of the router's GND list)
# RSH1 at (22.0, 28.135) turned 270 (placement.py): courtyard x 20.08..23.93, y 23.73..32.54; Kelvin lines at y 28.135 / 31.415 into U1
# pins 8 / 1 at x 34.7. Keepouts hold only pins of the locked nets (force, Kelvin), which leave the router's net list (prepare_routing.py).
ROUTER_KEEPOUT = [('F.Cu', 19.8, 23.4, 24.2, 32.9),    # RSH1 courtyard (README: nothing foreign at the shunt)
                  ('F.Cu', 24.2, 27.3, 34.3, 32.4),    # between and around the Kelvin lines up to the U1 pins
                  ('B.Cu', 19.8, 27.3, 34.3, 32.4)]    # under the Kelvin lines: GND pour only, no router tracks
PLANNER_KEEPOUT = list(ROUTER_KEEPOUT)   # the completion planner (complete_routes.py) keeps out too
SHUNT = 'RSH1'               # check_intrusion.py: no router copper of another net in its courtyard (README: nothing under the shunt)
