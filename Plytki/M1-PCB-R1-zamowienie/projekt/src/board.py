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
PWR = ['5V', '3V3', '5VA', 'SENS_5V', 'TC1_VIN', 'TC2_VIN']
PWR_W, PWR_CLR = .5, .25
CORE = []
SIG_VIA = (.6, .3)           # as P07 S1 (JLCPCB 4-layer standard): signal / GND fan-out vias 0.6 / 0.3; power stitching 0.9 / 0.4
SIGNAL_W = .2                # default track (as P07 S1), clearance 0.25
# 7.5 A path (BAT_P: J1.1 -> F1, VBUS: F1 -> J2 VMOTOR) and the motor line (P1_ECU: J5.1 -> RSH1, P1_EGR: RSH1 -> J5.2): locked pours on
# F.Cu and B.Cu (route_critical.py), out of the router's net list (prepare_routing.py), their pours exported as keepouts.
# VBUS also feeds the TSR inputs: locked 1.0 mm trunk to C1 / U1.1 / U2.1, TP3 in the pour (VBUS complete before the router).
FORCE = ['BAT_P', 'VBUS', 'P1_ECU', 'P1_EGR']
KELVIN = ['K_PLUS', 'K_MINUS', 'INA_PLUS', 'INA_MINUS']
ANALOG_NETS = KELVIN + ['I_MOT', 'ADC_REF', 'REFCAP', 'REGCAP_A', 'REGCAP_D'] + [f'ADC_CH{i}' for i in range(1, 9)]
TAILS = ['J1', 'J2', 'J4', 'J5', 'J6']                    # soldered wires with cable-tie anchors (J3: two thin button wires, no anchors)
SUPPORT_KEEPOUT = {r: 3.0 for r in TAILS}                 # NPTH cable-tie anchors: no copper within 3 mm of their centres
PIN_MARKS = {'J1': {'1': 'B+', '2': 'B-'}, 'J2': {'1': 'VM'}, 'J5': {'1': 'ECU', '2': 'EGR'},
             'J6': {'1': 'P3', '2': 'P4', '3': 'P5', '4': 'P6', '5': '5S', '6': 'G', '7': 'VB', '8': 'H', '9': 'L', '10': 'G'},
             'J4': {'1': 'RP', '2': 'LP', '3': 'RE', '4': 'LE', '5': '5V', '6': 'G'}, 'J3': {'1': 'BT', '2': 'G'}}
X1_EDGE = {'J1': (1, 2), 'J2': (3,), 'J5': (5, 6), 'J6': tuple(range(7, 17))}   # X1 screws per tail, left to right along the top edge
FINE = ['U3']                # LQFP-64 0.5 mm: clearance 0.15 / track 0.2 only inside its courtyard (P05 R3 rules, set_rules.py)
FINE_CLEARANCE, FINE_TRACK = .15, .2
TOP_ONLY = []
ISOLATE = {}
SHUNT = 'RSH1'
import json as _json, pathlib as _pl
_kb = _pl.Path(__file__).resolve().parents[1] / 'routing/kelvin-box.json'
_K = _json.loads(_kb.read_text()) if _kb.exists() else None
# U3 (P05 R3 copper moved by +37 / -15 mm, route_critical.route_u3): P05 board.py keepouts with the same offset
_D = lambda L, x0, y0, x1, y1: (L, x0 + 37, y0 - 15, x1 + 37, y1 - 15)
U3_KEEPOUT = [_D('F.Cu', 53.25, 49.25, 62.75, 58.75),                                   # inside the U3 pad ring
              _D('B.Cu', 51.3, 47.3, 64.7, 49.2), _D('B.Cu', 51.3, 59.95, 64.7, 60.7),   # B.Cu bands round the 100 nF under U3
              _D('B.Cu', 51.3, 47.3, 52.3, 60.7), _D('B.Cu', 63.0, 47.3, 64.7, 60.7)]
KELVIN_KEEPOUT = ([('F.Cu', *bx) for bx in _K['f_boxes']] + [('In2.Cu', *_K['in2_box'])]) if _K else []
ROUTER_KEEPOUT = U3_KEEPOUT + KELVIN_KEEPOUT
ANALOG_KEEPOUT = []
PLANNER_KEEPOUT = [_D('F.Cu', 51.3, 47.3, 64.7, 60.7), _D('B.Cu', 44.0, 43.0, 65.0, 62.0), _D('B.Cu', 50.4, 40.2, 63.1, 47.3)] + KELVIN_KEEPOUT
GND_INNER = ['U3']           # U3 GND pins tied inwards to the F.Cu pour inside the pad ring (route_u3): out of the DSN GND net
# Decoupling (cap: (IC, supply pin, GND pin)): return-path check (return_check.py / gndpath.py). The U3 capacitors follow P05 R3 (locked GND
# vias of route_u3), not listed here.
DEC_CAPS = {'C24': ('U4', '6', '2'), 'C25': ('U5', '14', '7'), 'C26': ('U6', '3', '2'), 'C27': ('U6', '5', '2'), 'C28': ('U7', '14', '7'),
            'C29': ('U8', '1', '2')}
# GND via at every SMD capacitor outside U3 (stitch.py stage 4), as P05 R3 EXTRA_GND_VIAS
EXTRA_GND_VIAS = [('pad', c, '2', 2.0) for c in ['C1', 'C2', 'C3', 'C4', 'C5', 'C7', 'C16', 'C17', 'C18', 'C19', 'C20', 'C21', 'C22', 'C23',
                                                 'C24', 'C25', 'C26', 'C27', 'C28', 'C29', 'C30']]
FANOUT_REFS = []
FANOUT_MODE = 'all'          # as P07 S1: every top GND pad gets a via to the In1 GND plane before the router
FANOUT_SKIP = ['U3', 'C6', 'C11', 'C12', 'C14', 'C15']   # U3 GND inwards (route_u3), its top capacitors have locked GND vias
PRE_TIES = {}
SOIC_TIES = {}
RETURN_PAIRS = {c: (u, g) for c, (u, v, g) in DEC_CAPS.items()}
RETURN_ACCEPT = {}
FORCE_PATH_ACCEPT = {}
DEC_ACCEPT = {}
IN2_SUPPLY = {}              # In2.Cu = signals only (supplies routed as PWR tracks); In1.Cu = solid GND
