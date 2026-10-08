"""M1-R1 board configuration for the layout chain (generic scripts copied from P07 S1: build_board, fanout_gnd, prepare_routing, run_layout,
import_routing, stitch, complete_routes, cleanup, trim_stubs, silkscreen, ...). One 4-layer board, free outline (no enclosure yet: the
enclosure follows the board, user 8.10). Geometry of the force path: placement.py and route_critical.py (docstrings)."""
NAME = 'M1'                  # eda/M1.kicad_pcb, routing/M1.dsn / M1.ses, verification/M1.xml
REV = 'M1-R1'
TITLE = 'EGRLab M1 (jedna plytka: LOGGER + TESTER), 4 warstwy'
DATE = '2026-10-08'
W, H = 150.0, 80.0           # outline (mm), corner radius R
R = 1.0
HOLES = [(4.0, 4.0), (W - 4.0, 4.0), (4.0, H - 4.0), (W - 4.0, H - 4.0)]   # M3 NPTH 3.2 mm, D7 standoff zones
HOLE_D, HOLE_ZONE_D = 3.2, 7.0
CLASS = None; SLOTS = []
JBP = []; JSV = []
GND_REF = ('J1', '2')        # reference pad of the main GND cluster (stitch.py): pack minus
# supply nets in class PWR (track 0.5 mm): 5 V ~0.5 A peak (ESP32 Wi-Fi), the rest small
PWR = ['5V', '3V3', '5VA', 'VBUS', 'SENS_5V', 'TC1_VIN', 'TC2_VIN']
PWR_W, PWR_CLR = .5, .25
CORE = []
SIG_VIA = (.6, .3)           # as P07 S1 (JLCPCB 4-layer standard): signal / GND fan-out vias 0.6 / 0.3; power stitching 0.9 / 0.4
SIGNAL_W = .2                # default track (as P07 S1), clearance 0.25
# 7.5 A path (BAT_P: J1.1 -> F1, VBUS: F1 -> J2 VMOTOR) and the motor line (P1_ECU: J5.1 -> RSH1, P1_EGR: RSH1 -> J5.2): locked pours on
# F.Cu and B.Cu (route_critical.py), out of the router's net list (prepare_routing.py), their pours exported as keepouts.
# VBUS also feeds the TSR inputs: the router joins U1.1 / U2.1 / C1 to the locked VBUS pour (VBUS stays routable, not in FORCE).
FORCE = ['BAT_P', 'P1_ECU', 'P1_EGR']
KELVIN = ['K_PLUS', 'K_MINUS', 'INA_PLUS', 'INA_MINUS']
ANALOG_NETS = KELVIN + ['I_MOT', 'ADC_REF', 'REFCAP', 'REGCAP_A', 'REGCAP_D'] + [f'ADC_CH{i}' for i in range(1, 9)]
TAILS = ['J1', 'J2', 'J4', 'J5', 'J6']                    # soldered wires with cable-tie anchors (J3: two thin button wires, no anchors)
SUPPORT_KEEPOUT = {r: 3.0 for r in TAILS}                 # NPTH cable-tie anchors: no copper within 3 mm of their centres
PIN_MARKS = {'J1': {'1': 'B+', '2': 'B-'}, 'J2': {'1': 'VM'}, 'J5': {'1': 'ECU', '2': 'EGR'},
             'J6': {'1': 'P3', '2': 'P4', '3': 'P5', '4': 'P6', '5': '5S', '6': 'G', '7': 'VB', '8': 'H', '9': 'L', '10': 'G'},
             'J4': {'1': 'RP', '2': 'LP', '3': 'RE', '4': 'LE', '5': '5V', '6': 'G'}, 'J3': {'1': 'BT', '2': 'G'}}
X1_EDGE = {'J1': (1, 2), 'J2': (3,), 'J5': (5, 6), 'J6': tuple(range(7, 17))}   # X1 screws per tail, left to right along the top edge
FINE = []
FINE_CLEARANCE, FINE_TRACK = .25, .3
GND_INNER = []
TOP_ONLY = []
ISOLATE = {}
SHUNT = 'RSH1'
import json as _json, pathlib as _pl
_kb = _pl.Path(__file__).resolve().parents[1] / 'routing/kelvin-box.json'
_K = _json.loads(_kb.read_text()) if _kb.exists() else None
ROUTER_KEEPOUT = ([('F.Cu', *_K['f_box']), ('B.Cu', *_K['b_box'])]) if _K else []
ANALOG_KEEPOUT = []
PLANNER_KEEPOUT = list(ROUTER_KEEPOUT)
# Decoupling (cap: (IC, supply pin, GND pin)): GND via at every cap (stitch.py stage 4) and the return-path check (gndpath.py)
DEC_CAPS = {'C6': ('U3', '1', '2'), 'C7': ('U3', '37', '35'), 'C8': ('U3', '38', '40'), 'C9': ('U3', '48', '47'), 'C10': ('U3', '23', '26'),
            'C24': ('U4', '6', '2'), 'C25': ('U5', '14', '7'), 'C26': ('U6', '3', '2'), 'C27': ('U6', '5', '2'), 'C28': ('U7', '14', '7'),
            'C29': ('U8', '1', '2')}
EXTRA_GND_VIAS = [('pad', c, '2', 2.0) for c in DEC_CAPS]
FANOUT_REFS = []
FANOUT_MODE = 'all'          # as P07 S1: every top GND pad gets a via to the In1 GND plane before the router
FANOUT_SKIP = []
PRE_TIES = {}
SOIC_TIES = {}
RETURN_PAIRS = {c: (u, g) for c, (u, v, g) in DEC_CAPS.items()}
RETURN_ACCEPT = {}
FORCE_PATH_ACCEPT = {}
DEC_ACCEPT = {}
IN2_SUPPLY = {}              # In2.Cu = signals only (supplies routed as PWR tracks); In1.Cu = solid GND
