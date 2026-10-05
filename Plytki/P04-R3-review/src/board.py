"""P04 R3 board configuration for the layout chain (format S1, class L, level 6). The generic layout scripts (build_board, fanout_gnd,
prepare_routing, run_layout, import_routing, stitch, complete_routes, cleanup, trim_stubs, silkscreen, gndpath, ...) are copies of
P05 R3 src (P03 R6 chain via P09 R2 / P10 R2; 5.10.2026, Ubuntu 24/7 session) and read their board specific values from here.
"""
NAME = 'P04'                 # eda/P04.kicad_pcb, routing/P04.dsn / P04.ses, verification/P04.xml
REV = 'P04 R3'
TITLE = 'EGRLab P04 R3 SAFE / format S1, klasa L, sloty S1-S3 poziomu 6'
DATE = '2026-10-05'
CLASS = 'L'                  # Plytki/Format-S1/format-s1.json 'klasy'
SLOTS = ['S1', 'S2', 'S3']   # S1 section 7: P04 on level 6, slots S1-S3 (user decision 5.10.2026)
JBP = ['J_BP1', 'J_BP2', 'J_BP3']   # edge-A IDC (odd pins GND): GND comb in fanout_gnd.py
JSV = ['J_SV1', 'J_SV2', 'J_SV3']   # edge-B service headers
GND_REF = ('J_BP2', '1')     # reference pad of the main GND cluster (stitch.py)
# Supply nets (task 5.10: P04_3V3, 5V_SYS, PANEL_3V3 >= 0.4 mm; 3V3_IO, the supply of the whole board, in the same class).
# 0.4 mm with the S1 clearance 0.25 still passes between DIP pads (gap 0.94 mm), not between the odd-row IDC pads (0.84 mm): the
# even-row supply pins of J_BP2 / J_BP3 leave on B.Cu towards edge A and round the connector end (route_critical.py, locked).
PWR = ['3V3_IO', 'P04_3V3', 'PANEL_3V3', '5V_SYS']
PWR_W, PWR_CLR = .4, .25     # class PWR: track 0.4 mm, clearance as S1 (0.25)
CORE = []                    # no CORE3V3 class on P04
SIGNAL_W = .3                # Default track: S1 section 3 (rules as P02-R3)
SUPPORT_KEEPOUT = {}
PIN_MARKS = {}               # pin 1 of J_BP / J_SV is marked by silkscreen.py itself
FINE = []                    # no fine-pitch parts (SOIC-14 only): no custom DRC rules
FINE_CLEARANCE, FINE_TRACK = .25, .3
GND_INNER = []
TOP_ONLY = []
ISOLATE = {}
# decoupling: a GND via at the GND pad of every 100 nF and of the bulk C3 (stitch.py stage 4, after the completion planner)
DEC_CAPS = {'C4': ('U1', '16', '8'), 'C5': ('U2', '14', '7'), 'C6': ('U3', '14', '7'), 'C7': ('U4', '14', '7'), 'C8': ('U5', '14', '7'),
            'C9': ('U6', '14', '7'), 'C10': ('U7', '14', '7'), 'C11': ('U8', '14', '7'), 'C12': ('U9', '14', '7'), 'C13': ('U10', '14', '7'),
            'C14': ('U11', '2', '3'), 'C15': ('U8', '14', '7'), 'C16': ('U9', '14', '7'), 'C17': ('U10', '14', '7')}   # cap: (IC, VCC pin, GND pin)
EXTRA_GND_VIAS = [('pad', c, '2', 2.0) for c in DEC_CAPS]
# P04 R3 run 1: C10.2 (between the U7 / U2 pin columns) was enclosed by router tracks on both layers -> every 100 nF gets a locked GND
# stub + via before the router (fanout_gnd.py, like the SOIC bars); the router sees them as fixed copper of the GND plane
# run 3 (5.10): the router's B.Cu tracks cut the plane, the GND return of the DIP decoupling (VCC pin 14 / 16 and GND pin 7 / 8 at opposite
# corners) ran 35-130 mm. Each DIP gets its 100 nF above the body (placement.py) and a locked GND spine (route_critical.py): cap GND pad ->
# via inside the courtyard -> B.Cu along the body centre line -> 45 deg to the GND pin. The other 100 nF keep the fan-out via.
DIP_SPINES = {'C4': 'U1', 'C5': 'U2', 'C6': 'U3', 'C7': 'U4', 'C8': 'U5', 'C9': 'U6', 'C10': 'U7'}
FANOUT_REFS = [c for c in DEC_CAPS if c not in DIP_SPINES]
SOIC_TIES = {c: DEC_CAPS[c][0] for c in ('C11', 'C12', 'C13', 'C15', 'C16', 'C17')}   # run 4: fan-out via -> GND bar via on B.Cu (fanout_gnd.py)
# run 5 (5.10): an INTERLOCK track of the router on B.Cu (y 17.26) ran right under the F.Cu part of SUP_N_OUT (GND reference 50 %). Router
# keepouts without pins (P05 R3 lesson: DSN keepouts holding pins break Freerouting): B.Cu under the F.Cu end (via -> U9.5 -> R17.1),
# F.Cu over the B.Cu leg between the GND pins J_BP3.9 / .11 (pads end at x 133.08 / 133.92). The planner keeps out of them too.
SUPN_KEEPOUT = [('B.Cu', 132.9, 16.95, 137.6, 19.3), ('F.Cu', 133.1, 14.3, 133.9, 15.8)]
PLANNER_KEEPOUT = list(SUPN_KEEPOUT)
ROUTER_KEEPOUT = list(SUPN_KEEPOUT)
# capacitor -> GND pin of its IC (complete_routes.py --ties plans a GND track where the copper return is longer than 1.3 x straight + 3 mm)
RETURN_PAIRS = {c: (u, g) for c, (u, v, g) in DEC_CAPS.items()}
