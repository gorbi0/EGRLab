"""P07 S1 board configuration for the layout chain (format S1, class 2/3, slots S2-S3 of level 5). The generic layout scripts
(build_board, fanout_gnd, prepare_routing, run_layout, import_routing, stitch, complete_routes, cleanup, trim_stubs, silkscreen,
gndpath, ...) are copies of P06 R2 / P04 R3 src (P03 R6 chain via P09 R2 / P10 R2 / P05 R3; 5.10.2026, Ubuntu 24/7 session) and read
their board specific values from here. Geometry of the power block: placement.py and route_critical.py (docstrings).
"""
NAME = 'P07'                 # eda/P07.kicad_pcb, routing/P07.dsn / P07.ses, verification/P07.xml
REV = 'P07 S1'
TITLE = 'EGRLab P07 S1 DRIVE (IBT-2) / format S1, klasa 2/3, sloty S2-S3 poziomu 5'
DATE = '2026-10-05'
CLASS = '2/3'                # Plytki/Format-S1/format-s1.json 'klasy'
SLOTS = ['S2', 'S3']         # S1 section 7: P07 on level 5, slots S2-S3 (P08 in S1)
JBP = ['J_BP1', 'J_BP2']     # edge-A IDC (odd pins GND): GND comb in fanout_gnd.py
JSV = ['J_SV1', 'J_SV2']     # edge-B service headers
GND_REF = ('J_BP1', '1')     # reference pad of the main GND cluster (stitch.py)
# Supply nets in class PWR: 5V_SYS (~110 mA with the KPWR coil, decision 5.10), the local rails and the logic supply. 0.4 mm with the
# S1 clearance 0.25 passes between DIP / SOIC-to-DIP pads (P04 R3).
PWR = ['5V_SYS', '5V_MOD', '5VA_P07', '3V3A_P07', '3V3_IO']
PWR_W, PWR_CLR = .4, .25
CORE = []
SIGNAL_W = .3                # Default track: S1 section 3 (rules as P02-R3)
# 10 A path (README: J1 -> K1 -> J2 / B+, J3 / M+ -> RSH1 -> J4) and the PGND return: locked pours on both layers (route_critical.py),
# out of the router's net list (prepare_routing.py), their pours exported as keepouts
FORCE = ['VMOTOR', 'PGND', 'MOD_BP', 'MOD_MP', 'T_EGR_P1', 'T_EGR_P3']
KELVIN = ['K_PLUS', 'K_MINUS', 'INA_PLUS', 'INA_MINUS']   # locked pair RSH1 -> R6 / R7 -> U1 (route_critical.py)
TAILS = ['J1', 'J2', 'J3', 'J4']                          # soldered 2.0 mm2 wires at x = 0 (decision 5.10 (6))
SUPPORT_KEEPOUT = {r: 3.0 for r in TAILS}                 # NPTH cable-tie anchors: no copper within 3 mm of their centres
PIN_MARKS = {'J1': {'1': 'VM', '2': 'PG'}, 'J2': {'1': 'B+', '2': 'B-'}, 'J3': {'1': 'M+', '2': 'M-'}, 'J4': {'1': 'P1', '2': 'P3'}}   # S1 section 9
FINE = []                    # no fine-pitch parts
FINE_CLEARANCE, FINE_TRACK = .25, .3
GND_INNER = []
TOP_ONLY = []
ISOLATE = {}
SHUNT = 'RSH1'
# Router keepouts (pin-free): the strip between the Kelvin lines and around them up to the U1 pins (route_critical.py writes the exact
# box to routing/kelvin-box.json; placement.py fixes RSH1 / R6 / R7 / U1, so the values are constant here). Filled in below.
import json as _json, pathlib as _pl
_kb = _pl.Path(__file__).resolve().parents[1] / 'routing/kelvin-box.json'
_K = _json.loads(_kb.read_text()) if _kb.exists() else None
ROUTER_KEEPOUT = [('F.Cu', *_K['f_box']), ('B.Cu', *_K['b_box'])] if _K else []
ANALOG_KEEPOUT = []
PLANNER_KEEPOUT = list(ROUTER_KEEPOUT)
# Decoupling (cap: (IC, supply pin, GND pin)): GND via at every 100 nF (stitch.py stage 4) and the return-path check (gndpath.py)
DEC_CAPS = {'C22': ('U1', '6', '2'), 'C23': ('U3', '8', '4'), 'C24': ('U4', '8', '4'), 'C25': ('U5', '8', '4'), 'C26': ('U6', '8', '4'),
            'C27': ('U7', '14', '7'), 'C28': ('U8', '2', '3'), 'C29': ('U9', '2', '3'), 'C30': ('U10', '14', '7'), 'C31': ('U11', '14', '7'),
            'C32': ('U12', '14', '7'), 'C33': ('U13', '14', '7'), 'C34': ('U14', '14', '7'), 'C35': ('U15', '14', '7'), 'C36': ('U16', '14', '7'),
            'C37': ('U17', '5', '2'), 'C38': ('U2', '3', '1')}
EXTRA_GND_VIAS = [('pad', c, '2', 2.0) for c in DEC_CAPS]
FANOUT_REFS = []
SOIC_TIES = {}
RETURN_PAIRS = {c: (u, g) for c, (u, v, g) in DEC_CAPS.items()}
RETURN_ACCEPT = {}
