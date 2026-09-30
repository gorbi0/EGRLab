"""P10 R2 board configuration for the layout chain. The generic layout scripts (build_board, fanout_gnd, prepare_routing, run_layout,
import_routing, stitch, complete_routes, cleanup, ...) come from P03 R6 via P09 R2 (30.09.2026, Ubuntu 24/7 session) and read their
board specific values from here.
"""
NAME = 'P10'                 # eda/P10.kicad_pcb, routing/P10.dsn / P10.ses, verification/P10.xml
REV = 'P10 R2'
TITLE = 'EGRLab P10 R2 CAN / format S1, klasa 1/3, slot S3 poziomu 4'
CLASS = '1/3'                # Plytki/Format-S1/format-s1.json 'klasy'
SLOTS = ['S3']               # S1-3 (SPECYFIKACJA-FORMATU-S1.md section 7): level 4, slot S3 at the input wall
JBP = ['J1']                 # edge-A IDC (odd pins GND): GND comb in fanout_gnd.py
JSV = ['J2']                 # edge-B service header
GND_REF = ('J1', '1')        # reference pad of the main GND cluster (stitch.py)
PWR = []                     # nets of class PWR (0.6 mm, clearance 0.3)
CORE = []                    # nets of class CORE3V3 (0.3 mm)
SIGNAL_W = .3                # Default track: S1 section 3 (rules as P02-R3)
SUPPORT_KEEPOUT = {'J3': 3.0}   # NPTH anchor holes of the OBD tail (cable tie): no copper within 3 mm of their centres
