"""P09 R2 board configuration for the layout chain. The generic layout scripts (build_board, fanout_gnd, prepare_routing, run_layout,
import_routing, stitch, complete_routes, cleanup, ...) were taken from P03 R6 (30.09.2026, Ubuntu 24/7 session) and read their board
specific values from here, so P10 R2 can reuse them with its own board.py.
"""
NAME = 'P09'                 # eda/P09.kicad_pcb, routing/P09.dsn / P09.ses, verification/P09.xml
REV = 'P09 R2'
TITLE = 'EGRLab P09 R2 TEMP / format S1, klasa 1/3, slot S3 poziomu 3'
CLASS = '1/3'                # Plytki/Format-S1/format-s1.json 'klasy'
SLOTS = ['S3']               # the board's own x starts at 0 in every class; holes repeat per slot of the board
JBP = ['J1']                 # edge-A IDC (odd pins GND): GND comb in fanout_gnd.py
JSV = ['J2']                 # edge-B service header
GND_REF = ('J1', '1')        # reference pad of the main GND cluster (stitch.py)
PWR = []                     # nets of class PWR (0.6 mm, clearance 0.3)
CORE = []                    # nets of class CORE3V3 (0.3 mm)
SIGNAL_W = .3                # Default track: S1 section 3 (rules as P02-R3); the 0.2 mm of P03 R6 was a P03-only user decision
SUPPORT_KEEPOUT = {'J3': 4.0, 'J4': 4.0}   # NPTH support holes of the module sockets: nylon M2.5 + 8 mm washer -> no copper within 4 mm
