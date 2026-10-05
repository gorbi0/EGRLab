"""P12 R1 board configuration for the layout chain (scripts from P10 R2 / P03 R6, board values here).
Board coordinates: x = x of the stack (0 = panel side), z = height above the enclosure floor. KiCad: X = x, Y = ZTOP - z (Y down),
so the top side (F.Cu, connectors) is the side that faces the stack and the KiCad view is the view from the stack with z up.
"""
NAME = 'P12'
REV = 'P12 R1'
TITLE = 'EGRLab P12 R1 plytka polaczen krawedzi A (LOGGER)'
X0, X1 = 0.0, 160.0          # board along x (stack coordinates)
Z0, ZTOP = 4.0, 96.0         # board along z (height above the floor of the enclosure)
W, H = X1 - X0, ZTOP - Z0    # 160 x 92 mm
CLASS = None
SLOTS = []
# M3 (D3.2 NPTH, standoff zone D7) in (x, z): corners and the two gaps between the slots (no connector, no ribbon there)
HOLES_XZ = [(4.5, 8.5), (4.5, 91.5), (155.5, 8.5), (155.5, 91.5), (53.25, 51.45), (106.75, 51.45)]
TP_XZ = {'TP1': (94.0, 14.05), 'TP2': (100.0, 14.05), 'TP3': (106.0, 14.05), 'TP4': (112.0, 14.05)}
GND_REF = ('J1', '1')        # reference GND pad (P02 J_BP pin 1, the GND source)
PWR = ['5V_SYS']             # class PWR: 1.0 mm (budget ~1.09 A, README)
P3V3 = ['3V3_IO']            # class P3V3: 0.5 mm
CORE = []
SIGNAL_W = .3                # Default track (>= 0.25 required)
WIDTHS = {'5V_SYS': 1.0, '3V3_IO': .5}
SUPPORT_KEEPOUT = {}
PAD_KEEPOUT = {}


def kxy(x, z):
    """Stack (x, z) -> KiCad board (X, Y) in mm."""
    return (round(x - X0, 4), round(ZTOP - z, 4))


def xz(X, Y):
    return (round(X + X0, 4), round(ZTOP - Y, 4))
