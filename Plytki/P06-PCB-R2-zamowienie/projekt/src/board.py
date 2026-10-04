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
# review 2.10 (F2 / F3): the router ran service and supply tracks between the pin rows of U2 / U3 (SRV_ADC_AIN and SRV_I_L_OUT 22 mm
# under U2, SRV_CLK_LOCAL - the 500 kHz ADC clock behind 1k - and SRV_5VA_P06 under U3) and cut the B.Cu plane under both into a
# 191 mm2 island. Pin-free areas (0.1 mm off the DIP pads, U2 / U3 at x 45 / 52.62 and 57 / 64.62, pins y 27..34.62): both interiors
# on both layers, on B.Cu also the strip between them; C2 (bottom, under U3 at its IN+ / IN- pins, placement.py) keeps a pocket open
# towards them. No track and no via other than GND inside (verify_pcb.py); the GND pours fill them.
ANALOG_KEEPOUT = [('F.Cu', 45.9, 25.8, 51.72, 35.8), ('B.Cu', 45.9, 25.8, 51.72, 35.8),    # U2 interior
                  ('F.Cu', 57.9, 25.8, 63.72, 35.8),                                      # U3 interior
                  ('B.Cu', 57.9, 25.8, 63.72, 28.1), ('B.Cu', 61.7, 28.1, 63.72, 35.8),  # U3 interior on B.Cu round the pocket of C2
                  ('B.Cu', 57.9, 33.6, 61.7, 35.8),                                      # (bottom, at U3.2 / U3.3: placement.py)
                  ('B.Cu', 53.5, 26.2, 56.1, 35.8),                                       # strip between U2 and U3 (B.Cu)
                  ('B.Cu', 43.5, 35.9, 56.1, 38.5)]   # 2.10: below the U2 pin rows (SRV_I_L_OUT / SRV_ADC_AIN / REF25 cut C1 -> U2.4, 36 mm)
ROUTER_KEEPOUT += ANALOG_KEEPOUT
PLANNER_KEEPOUT = list(ROUTER_KEEPOUT)   # the completion planner (complete_routes.py) keeps out too
TOP_ONLY = []                # nets in a DSN class limited to F.Cu (use_layer; prepare_routing.py, complete_routes.py). Tried 2.10 for SW_SENSE
                             # (review F3: 163 mm, most on B.Cu below the analog block): on F.Cu alone the router and the planner could not reach
                             # U6.5 between R15 / R16 (no complete board); SW_SENSE stays on both layers (static, 1k / 100k)
# review 2.10 (F2): GND vias placed by stitch.py after the completion planner, nearest legal spot to each target (both pours, own pad's
# pour piece): ('pad', ref, num, radius) - at a capacitor GND pad; ('at', x, y, radius) - a free spot (the B.Cu island under U2 / U3 had
# one via). Every SMD decoupling / filter capacitor gets one (verify_pcb.py measures the return to its part's GND pin).
EXTRA_GND_VIAS = [('pad', c, '2', 2.0) for c in ('C1', 'C2', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'C11', 'C12', 'C13', 'C14', 'C15', 'C16', 'C17')] + \
                 [('pad', 'U1', '2', 2.0), ('at', 54.8, 31.4, 2.0), ('at', 60.8, 33.5, 2.0)]   # U1.2: INA240 GND (C6 return)
SHUNT = 'RSH1'               # check_intrusion.py: no router copper of another net in its courtyard (README: nothing under the shunt)
# 2.10 (verify_pcb.py return-path check): capacitor -> GND pin of its part; complete_routes.py --ties plans a GND track where the
# GND copper path is longer than 1.3 x straight + 3 mm
RETURN_PAIRS = {'C1': ('U2', '4'), 'C2': ('U3', '3'), 'C4': ('U4', '1'), 'C5': ('U10', '1'), 'C6': ('U1', '2'), 'C7': ('U2', '4'), 'C8': ('U3', '4'),
                'C9': ('U4', '1'), 'C10': ('U5', '7'), 'C11': ('U6', '7'), 'C12': ('U7', '7'), 'C13': ('U8', '3'), 'C14': ('U9', '3'),
                'C15': ('U10', '1'), 'C16': ('U3', '4')}
RETURN_ACCEPT = {'C6': 14.0}   # accepted exception (verify_pcb.py ACCEPT): C6 -> U1.2 round REF_BUF pin 3, NC pin 4 and R27
