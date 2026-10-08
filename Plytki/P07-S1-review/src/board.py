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
JSV = ['J_SV2']              # edge-B service header (one strip in slot S3, simplification 1 of 6.10)
GND_REF = ('J_BP1', '1')     # reference pad of the main GND cluster (stitch.py)
# Supply nets in class PWR: 5V_SYS (~110 mA with the KPWR coil, decision 5.10), the local rails and the logic supply. 0.4 mm with the
# S1 clearance 0.25 passes between DIP / SOIC-to-DIP pads (P04 R3).
PWR = ['5V_SYS', '5V_MOD', '5VA_P07', '3V3A_P07', '3V3_IO']
PWR_W, PWR_CLR = .4, .25
CORE = []
SIG_VIA = (.6, .3)           # 7.10 (sporne): signal / GND fan-out vias 0.6 / 0.3 (ring 0.15; JLCPCB 4-layer standard), were 0.9 / 0.4 of the 2-layer
                             # boards; power stitching (route_critical / stitch) and the PWR class keep 0.9 / 0.4
SIGNAL_W = .2                # Default track. 7.10 (sporne): 0.2 mm instead of 0.3 of P02-R3 (S1 has no number; JLCPCB 4 layers 0.09): the channel
                             # left of the relay did not take the logic links at 0.3 in 14 layout runs; clearance stays 0.25, PWR 0.4
# 10 A path (README: J1 -> K1 -> J2 / B+, J3 / M+ -> RSH1 -> J4) and the PGND return: locked pours on both layers (route_critical.py),
# out of the router's net list (prepare_routing.py), their pours exported as keepouts
FORCE = ['VMOTOR', 'PGND', 'MOD_BP', 'MOD_MP', 'T_EGR_P1', 'T_EGR_P3']
KELVIN = ['K_PLUS', 'K_MINUS', 'INA_PLUS', 'INA_MINUS']
# 7.10 (user decision): logic may cross the power block on In2.Cu (over the In1 PGND area); these analog nets (sheet ANA) may not
ANALOG_NETS = ['ADC_BUF', 'I_DIV', 'I_FILT', 'I_T_OUT', 'OC_FB', 'OC_HIGH', 'OC_LOW', 'REF25', 'REF_BUF', 'ADC_AIN', '3V3A_P07', '5VA_P07'] + KELVIN   # locked pair RSH1 -> R6 / R7 -> U1 (route_critical.py)
TAILS = ['J1', 'J2', 'J3', 'J4']                          # soldered 2.0 mm2 wires: J1 / J2 / J4 at x = 106.5, J3 at edge B (decisions 6.10 evening / 7.10)
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
ROUTER_KEEPOUT = ([('F.Cu', *_K['f_box']), ('B.Cu', *_K['b_box'])] + ([('F.Cu', *_K['shunt_box'])] if 'shunt_box' in _K else [])) if _K else []
ANALOG_KEEPOUT = []
PLANNER_KEEPOUT = list(ROUTER_KEEPOUT)
# Decoupling (cap: (IC, supply pin, GND pin)): GND via at every 100 nF (stitch.py stage 4) and the return-path check (gndpath.py)
DEC_CAPS = {'C22': ('U1', '6', '2'), 'C23': ('U3', '8', '4'), 'C24': ('U4', '8', '4'), 'C25': ('U5', '8', '4'), 'C26': ('U6', '8', '4'),
            'C27': ('U7', '14', '7'), 'C28': ('U8', '2', '3'), 'C29': ('U9', '2', '3'), 'C30': ('U10', '14', '7'), 'C31': ('U11', '14', '7'),
            'C32': ('U12', '14', '7'), 'C33': ('U13', '14', '7'), 'C34': ('U14', '14', '7'), 'C35': ('U15', '14', '7'), 'C36': ('U16', '14', '7'),
            'C37': ('U2', '3', '1')}
EXTRA_GND_VIAS = [('pad', c, '2', 2.0) for c in DEC_CAPS]
FANOUT_REFS = []
FANOUT_MODE = 'all'   # 7.10: every top GND pad gets a via to the In1 GND plane before the router (GND islands were half of the open items left)
FANOUT_SKIP = []   # 7.10: U11 had GND on pins 7 and 13 (a bar across the body walled off SAFE_BAD U11.6 -> U11.9); pin 13 (unused 6A) now on 3V3_IO
# 7.10: locked links under a SOIC body before the router (fanout_gnd.py), (net, points); a point is a pad number (str) or footprint-local (x, y) mm.
# U16 has DRIVE_EN on 9 / 12 and DRV_OFF on 1 / 4 / 10 / 13: the router joined them round the outside of the pin rows and closed LEN_D (pin 11) in.
PRE_TIES = {'U16': [('DRIVE_EN', ['12', (.9, -1.27), (.9, 2.54), '9']),
                    ('DRV_OFF', ['13', (-.9, -2.54), (-.9, -3.81), '1']), ('DRV_OFF', [(-.9, -2.54), (-.9, 0.0), '4'])]}
SOIC_TIES = {}
RETURN_PAIRS = {c: (u, g) for c, (u, v, g) in DEC_CAPS.items()}
RETURN_ACCEPT = {}
# 7.10: force path exceptions ((net, layer): reason); checked on F.Cu, which carries the path to the shunt
FORCE_PATH_ACCEPT = {('MOD_MP', 'B.Cu'): 'J3.1 sits 6 mm under the shunt: on B.Cu its thermal gap and the rule area under RSH1 (F.Cu SMD) take the whole '
                                          '2.3 mm between them; the 4.5 mm PTH pad and its spokes carry the current to F.Cu, where the 4 mm corridor reaches the force pad'}
# 7.10: decoupling exceptions (cap: (accepted mm, reason)); moving them now means a new router draw
DEC_ACCEPT = {'C35': (7.0, 'U15 HC74 (ARM / latch, slow edges): 6.5 mm from pin 14, GND via at the pad (fan-out), In1 plane under both'),
              'C21': (12.0, 'second 100 nF on 3V3_IO at J_BP2 (C20 is the one at the pin); 11.4 mm, In1 plane under both')}
# In2.Cu supply regions (user decision 6.10: In2 = supplies + signals; 6.10 evening layout): DSN planes for the router (prepare_routing.py,
# as the GND plane of P03 R6: the router joins each supply pin to its plane with a via and routes other nets across it) and the real
# zones filled round the In2 signal tracks after the import (inner_zones.py). Each net: disjoint rectangles (x0, y0, x1, y1).
IN2_SUPPLY = {'3V3A_P07': [(0.6, 14.8, 30.0, 56.0)],                                     # 7.10 placement: ADC chain top left
              '5VA_P07': [(0.6, 56.5, 49.5, 92.0), (49.5, 68.0, 63.0, 82.0)],             # OC window / supervisors bottom left, INA240
              '3V3_IO': [(30.5, 14.8, 71.5, 31.0), (49.5, 54.5, 76.0, 67.5)]}             # logic under J_BP2 / under the relay
