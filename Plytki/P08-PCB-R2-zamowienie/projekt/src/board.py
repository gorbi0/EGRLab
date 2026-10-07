"""P08 R2 board configuration for the layout chain. The generic layout scripts (build_board, fanout_gnd, prepare_routing, run_layout,
import_routing, stitch, complete_routes, cleanup, trim_stubs, ...) come from P05 R3 (2.10, review fixes: --ties, --targeted, trim_stubs),
the 1/3 parts (silkscreen, verify_pcb, negative_controls, make_pdf) from P10 R2 / P09 R2 (5.10.2026, Ubuntu 24/7 session).
"""
NAME = 'P08'                 # eda/P08.kicad_pcb, routing/P08.dsn / P08.ses, verification/P08.xml
REV = 'P08 R2'
TITLE = 'EGRLab P08 R2 SENSOR / format S1, klasa 1/3, slot S1 poziomu 5'
CLASS = '1/3'                # Plytki/Format-S1/format-s1.json 'klasy'
SLOTS = ['S1']               # S1 section 7 (wariant pełny): level 5, slot S1 (P07 in S2-S3)
JBP = ['J1']                 # edge-A IDC (odd pins and the spare 12 / 14 GND): GND comb in fanout_gnd.py
JSV = ['J2']                 # edge-B service header
GND_REF = ('J1', '1')        # reference pad of the main GND cluster (stitch.py)
# class PWR (0.6 mm, clearance 0.3): 5V_SYS (TPS2553 limit ~0.1 A + coil 30 mA + logic) and the switched sensor path through K1
# (task 5.10: 5V_SENSOR / AGND_SENSOR >= 0.5 mm, 5V_SYS >= 0.6 mm; one class for all four keeps the planner and the router simple)
PWR = ['5V_SYS', 'SENSOR_LIMITED', '5V_SENSOR', 'AGND_SENSOR']
SENSOR_PATH = ['SENSOR_LIMITED', '5V_SENSOR', 'AGND_SENSOR']   # verify_pcb.py: every track >= 0.5 mm, short
CORE = []                    # nets of class CORE3V3 (0.3 mm)
SIGNAL_W = .3                # Default track: S1 section 3 (rules as P02-R3)
SUPPORT_KEEPOUT = {'J4': 3.0}   # NPTH anchor holes of the TSENSOR wire field (cable tie): no copper within 3 mm of their centres
PIN_MARKS = {'J4': {'1': '1'}}  # S1 section 9: pin 1 (5V_SENSOR) of the soldered TSENSOR pair
FINE = []                    # no fine-pitch parts (SOIC-14 and SOT-23-6 meet the S1 rules)
FINE_CLEARANCE, FINE_TRACK = .25, .3
GND_INNER = []
TOP_ONLY = []
ISOLATE = {}
ROUTER_KEEPOUT = []
PLANNER_KEEPOUT = []
# GND vias at the SMD decoupling capacitors (stitch.py stage 4, after the completion planner; as P05 R3 / P06 R2 review 2.10)
EXTRA_GND_VIAS = [('pad', c, '2', 2.0) for c in ('C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9')]
# capacitor -> GND pin of its part (verify_pcb.py return path; complete_routes.py --ties plans a GND track when the copper path is long)
RETURN_PAIRS = {'C1': ('U1', '2'), 'C2': ('U1', '2'), 'C3': ('U3', '7'), 'C4': ('U4', '7'), 'C5': ('U5', '7'), 'C6': ('U6', '3'),
                'C7': ('U7', '3'), 'C8': ('U8', '3')}
