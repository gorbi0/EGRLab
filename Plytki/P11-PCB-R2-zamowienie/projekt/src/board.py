"""P11 R2 board configuration for the layout chain (4.10.2026, local Ubuntu session). The generic layout scripts (build_board,
prepare_routing, run_layout, import_routing, cleanup, stitch, complete_routes, ...) are copies of P10 R2 (chain of P03 R6) and read
the board specific values from here.

P11 is not a stack board (no S1 class or slot): it lies flat on the bottom of the panel zone, 50 mm in front of the S1 stack
(Plytki/Panel-S1-makieta/README.md, decision P11-6, user 4.10: max approx. 45 x 130 mm, long side along the panel wall).
Board coordinates: x 0..W across (x = 0 = long edge facing the panel: wire fields), y 0..H along (y = 0 = short edge facing wall A:
J_P12, the ribbon to P12).
"""
NAME = 'P11'                 # eda/P11.kicad_pcb, routing/P11.dsn / P11.ses, verification/P11.xml
REV = 'P11 R2'
TITLE = 'EGRLab P11 R2 PANEL (styki panelu, tasma do P12)'
W, H = 36.0, 100.0           # outline (mm); limit from the user 4.10: 45 x 130
LIMIT = (45.0, 130.0)
R_CORNER = 1.0               # outline corner radius (as S1)
THICKNESS = 1.6              # FR4 1.6 mm, 2 x 35 um (as S1)
CU_UM = 35
EDGE_CU = .5                 # copper to board edge (as S1)
HOLE_D, HOLE_ZONE_D = 3.2, 7.0   # M3 NPTH and standoff zone without copper and parts (as S1)
# 4 M3 holes in the corners, 4 mm from the long edges. The top pair sits behind J_P12: the 2x10 box header (body 33 mm) fills the
# short edge y = 0, so a hole at y = 4 would need W >= 49 mm (over the 45 mm limit).
HOLES = [(4.0, 19.0), (W - 4.0, 19.0), (4.0, H - 4.0), (W - 4.0, H - 4.0)]
JBP = ['J_P12']              # the board-to-board connector (odd pins GND except 13 / 15, docs/J_P12.csv)
JSV = []                     # no service header (README question 6)
FIELDS = ['J11', 'J8', 'J6']  # soldered wire fields at the panel edge x = 0
GND_REF = ('J_P12', '1')     # reference pad of the main GND cluster (stitch.py)
PWR = []                     # no 0.6 mm class: all currents are below 1 mA (README, QA.md)
CORE = []
WIDE = {'PANEL_3V3': .4, '3V3_IO': .4}   # user 4.10: supplies of the contacts >= 0.4 mm; everything else >= 0.3 mm
SIGNAL_W = .3
SUPPORT_KEEPOUT = {'J11': 3.0, 'J8': 3.0, 'J6': 3.0}   # NPTH cable-tie anchors of the wire fields: no copper within 3 mm (as P10 J3)
PIN_MARKS = {}               # pin 1 of J_P12 is marked by silkscreen.py ('1'); field labels in silkscreen.py (FIELD_LABELS)
PAD_KEEPOUT = {}
