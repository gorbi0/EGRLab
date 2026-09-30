"""P02 R4: explicit power copper before signal autorouting (all locked; S1 board, class L; geometry of the 2/3 pilot moved by DX = 53.5).
5 A path as F.Cu zones with full pad connection: J1.1 -> BAT_IN pour -> Q9 (D) ... Q9 (S) -> SW_COM pour (+ B.Cu copy under the
sources) -> Q1 (S) ... Q1 (D) -> VSW pour -> F1 -> VMOTOR pour -> J2.1. The return J2.2 -> J1.2 runs in the B.Cu GND pour inside a
corridor where no track or via may go (rule area).
TO-220 tabs (standing, leads cut to 4 mm): the strip under each tab carries only copper of the tab net (pin 2): a small own-net zone
plus a rule area that keeps tracks and vias out (Q9 BAT_IN and Q1 VSW lie inside their power pours; Q2 OFF_D, D1 VLOG, D2 HOLD_C).
Several rectangles of one net overlap into one pour. Locked tracks join what the pours do not reach (REV_G, OFF_D, VLOG and HOLD_C
anchors, SW_COM stub to R22.2). The router sees the pours as planes (own-net conduction areas) and may cross them outside the
5 A bands; the bands, tab strips and the corridor are rule areas (no tracks/vias), exported to the DSN as keepouts.
"""
from pathlib import Path
import pcbnew as p, json, math
P = Path(__file__).resolve().parents[1]; path = P / 'eda/P02.kicad_pcb'
mm = p.FromMM; F, B = p.F_Cu, p.B_Cu

# ---- geometry (board mm); names are checked by verify_pcb.py ----
POURS = {  # net -> [(layer, x0, y0, x1, y1), ...]
    # 29.09 (klasa L, verify_pcb §7): the Q9 tab strip reaches y = 29.0 and the Q1 strip starts at y = 32.04, beyond the BAT_IN / VSW
    # rectangles; a GND sliver filled the gap under both tab ends. Own-net rectangles now cover the strip ends, and the SW_COM
    # rectangles next to them keep 0.30-0.35 mm (PWR clearance), too little for any GND fill.
    'P02_BAT_IN': [(F, 75.4, 17.4, 93.6, 28.4), (F, 75.8, 28.0, 77.6, 29.15)],
    'P02_SW_COM': [(F, 62.4, 19.4, 72.3, 31.55), (F, 62.4, 27.9, 75.5, 31.55), (F, 75.2, 29.45, 86.2, 36.2), (B, 70.0, 25.0, 78.0, 36.2)],
    'P02_VSW': [(F, 70.4, 31.9, 72.3, 33.3), (F, 58.5, 33.2, 73.0, 42.2), (F, 44.0, 33.2, 58.5, 37.9), (F, 53.9, 37.9, 56.5, 42.3), (F, 58.5, 42.2, 76.5, 46.3),
                (F, 61.0, 46.3, 68.0, 58.0), (F, 61.0, 56.5, 76.8, 66.0), (F, 68.0, 66.0, 73.5, 71.0), (B, 61.0, 46.3, 68.0, 66.0)],
    'VMOTOR': [(F, 83.2, 59.0, 95.3, 72.0), (F, 89.0, 70.0, 98.4, 79.5)],
    '/P02_OFF_D': [(F, 80.54, 53.85, 90.54, 55.3), (F, 84.8, 53.85, 86.3, 56.2), (F, 86.8, 53.3, 88.2, 53.9)],  # Q2 tab + necks to pin 2 and the R27 track
    'P02_VLOG': [(F, 56.85, 40.54, 58.15, 52.3), (F, 56.2, 44.8, 57.2, 46.3)],                          # D1 tab + neck to pin 2
    'P02_HOLD_C': [(F, 51.85, 38.54, 53.15, 51.9), (F, 51.2, 42.8, 52.1, 44.3), (F, 53.15, 47.2, 53.8, 49.0), (F, 51.1, 48.5, 53.15, 51.9)],
}
TABS = ['Q9', 'Q1', 'Q2', 'D1', 'D2']      # tab strip = F.Fab rectangle behind the pads (local y -3.15..-1.85)
BANDS = {  # 5 A bands kept free of foreign tracks/vias (rule areas); the width check in verify_pcb.py samples inside them
    'BAND BAT_IN J1.1-Q9.D': ([F], [(77.5, 21.5), (88.0, 21.5), (88.0, 26.5), (77.5, 26.5)]),
    'BAND SW_COM Q9.S-Q1.S (F)': ([F], [(72.3, 27.7), (75.4, 27.7), (75.4, 33.3), (72.3, 33.3)]),
    'BAND SW_COM Q9.S-Q1.S (B)': ([B], [(70.5, 25.5), (77.5, 25.5), (77.5, 35.7), (70.5, 35.7)]),
    'BAND VSW Q1.D-F1.1': ([F], [(66.0, 36.2), (72.4, 36.2), (72.4, 46.2), (67.5, 46.2), (67.5, 57.0), (76.5, 57.0), (76.5, 64.8), (62.0, 64.8),
                                  (62.0, 46.2), (66.0, 46.2)]),
    'BAND VMOTOR F1.2-J2.1': ([F], [(86.6, 59.8), (95.0, 59.8), (95.0, 66.8), (94.2, 66.8), (94.2, 78.5), (89.5, 78.5), (89.5, 70.5), (86.6, 70.5)]),
}
CORRIDOR = [(86, 28), (106, 28), (106, 72), (94.5, 72), (94.5, 64), (101.5, 64), (101.5, 44), (97.5, 44), (97.5, 37.5), (86, 37.5)]
TRACKS = [  # net, points, width
    ('/P02_REV_G', [(71.08, 16.3), (71.08, 26.5)], .5), ('/P02_REV_G', [(71.08, 21.46), (74.0, 21.46)], .5),
    ('/P02_OFF_D', [(87.5, 50.4), (87.5, 53.3)], .8),
    ('P02_VLOG', [(57.5, 52.0), (59.8, 51.96)], .8), ('P02_VLOG', [(57.5, 52.0), (57.5, 53.2), (56.4, 54.3), (56.0, 54.3)], .8),
    ('P02_HOLD_C', [(51.85, 49.3), (40.7, 49.3), (40.7, 49.5), (38.5, 51.7), (37.0, 53.2), (37.0, 55.3)], .8),   # D2 tab -> R67, R41 -> C_H (+)
    ('P02_SW_COM', [(86.0, 35.8), (89.5, 39.3), (91.78, 39.3)], .8),
    ('GND', [(66.3, 13.32), (83.81, 13.32)], .5),              # J_BP GND pins 1..13 (odd) tied along their row, via to B.Cu below
    ('GND', [(91.43, 13.32), (93.4, 13.32)], .5),              # J_BP pin 19 to its own via
]
VIAS = [('GND', (66.3, 13.32)), ('GND', (93.4, 13.32))]


# klasa L (29.09): cała geometria bloku mocy przesunięta razem z placement.py (DX = 53,5 mm)
DX = 53.5
POURS = {n: [(Ly, x0 + DX, y0, x1 + DX, y1) for Ly, x0, y0, x1, y1 in r] for n, r in POURS.items()}
BANDS = {k: (ls, [(x + DX, y) for x, y in pts]) for k, (ls, pts) in BANDS.items()}
CORRIDOR = [(x + DX, y) for x, y in CORRIDOR]
TRACKS = [(n, [(x + DX, y) for x, y in pts], w) for n, pts, w in TRACKS]
VIAS = [(n, (x + DX, y)) for n, (x, y) in VIAS]
# 30.09: grupa podtrzymania przesunięta w placement.py o DH w lewo: jej wylewki VLOG i HOLD_C oraz ścieżki kotwic jadą z nią;
# przedłużenie VSW do R40 wydłuża się w lewo o |DH|, przedłużenie do pinu VSW D1 przesuwa się razem z D1.
DH = -8.0
POURS['P02_VLOG'] = [(Ly, x0 + DH, y0, x1 + DH, y1) for Ly, x0, y0, x1, y1 in POURS['P02_VLOG']]
POURS['P02_HOLD_C'] = [(Ly, x0 + DH, y0, x1 + DH, y1) for Ly, x0, y0, x1, y1 in POURS['P02_HOLD_C']]
TRACKS = [(n, [(x + DH, y) for x, y in pts], w) if n in ('P02_VLOG', 'P02_HOLD_C') else (n, pts, w) for n, pts, w in TRACKS]
_vsw = []
for Ly, x0, y0, x1, y1 in POURS['P02_VSW']:
    if (round(x0 - DX, 2), round(x1 - DX, 2)) == (44.0, 58.5):      # pod R40 do głównej wylewki VSW
        x0 += DH
    elif (round(x0 - DX, 2), round(x1 - DX, 2)) == (53.9, 56.5):    # do pinu VSW D1
        x0 += DH; x1 += DH
    _vsw.append((Ly, x0, y0, x1, y1))
assert sum(1 for a, c in zip(POURS['P02_VSW'], _vsw) if a != c) == 2
POURS['P02_VSW'] = _vsw


def xy(x, y):
    return p.VECTOR2I(mm(x), mm(y))


def tab_strip(f):
    """Board polygon of the tab strip of a standing TO-220 (local x -2.46..7.54, y -3.15..-1.85)."""
    t = math.radians(f.GetOrientationDegrees()); ox, oy = p.ToMM(f.GetPosition().x), p.ToMM(f.GetPosition().y)
    return [(round(ox + lx * math.cos(t) + ly * math.sin(t), 4), round(oy - lx * math.sin(t) + ly * math.cos(t), 4))
            for lx, ly in [(-2.46, -3.15), (7.54, -3.15), (7.54, -1.85), (-2.46, -1.85)]]


if __name__ == '__main__':
    b = p.LoadBoard(str(path))

    def net(n):
        v = b.FindNet(n); assert v is not None and v.GetNetCode() > 0, n; return v

    def poly(obj, pts):
        o = obj.Outline(); o.NewOutline()
        for x, y in pts:
            o.Append(mm(x), mm(y))

    for n, rects in POURS.items():
        for L in (F, B):
            rr = [r for r in rects if r[0] == L]
            if not rr:
                continue
            u = p.SHAPE_POLY_SET()  # union of the rectangles: one zone per net and layer (overlapping zones are a DRC error)
            for _, x0, y0, x1, y1 in rr:
                one = p.SHAPE_POLY_SET(); one.NewOutline()
                for x, y in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]:
                    one.Append(mm(x), mm(y))
                u.BooleanAdd(one)
            assert u.OutlineCount() == 1 and u.HoleCount(0) == 0, (n, L, u.OutlineCount())
            z = p.ZONE(b); z.SetLayer(L); z.SetNet(net(n)); z.SetAssignedPriority(20 if n in ('/P02_OFF_D', 'P02_VLOG', 'P02_HOLD_C') else 10)
            z.SetZoneName(f'PWR {n.lstrip("/")} {b.GetLayerName(L)}'); z.SetLocalClearance(mm(.3)); z.SetMinThickness(mm(.25))
            z.SetPadConnection(p.ZONE_CONNECTION_FULL); z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
            o = u.Outline(0); poly(z, [(p.ToMM(o.CPoint(i).x), p.ToMM(o.CPoint(i).y)) for i in range(o.PointCount())]); z.SetLocked(True); b.Add(z)

    def rule(pts, layers, name):
        z = p.ZONE(b); z.SetIsRuleArea(True); ls = p.LSET()
        for L in layers:
            ls.AddLayer(L)
        z.SetLayerSet(ls); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True); z.SetDoNotAllowZoneFills(False)
        z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False); z.SetZoneName(name); poly(z, pts); b.Add(z)

    fp = {f.GetReference(): f for f in b.GetFootprints()}
    for r in TABS:
        rule(tab_strip(fp[r]), [F], f'TAB {r} (only tab-net copper, no tracks/vias)')
    rule(CORRIDOR, [B], 'B.Cu GND return J2.2-J1.2 (no tracks/vias)')
    for name, (layers, pts) in BANDS.items():
        rule(pts, layers, name)
    for n, pts, w in TRACKS:
        for a, c in zip(pts, pts[1:]):
            t = p.PCB_TRACK(b); t.SetStart(xy(*a)); t.SetEnd(xy(*c)); t.SetWidth(mm(w)); t.SetLayer(F); t.SetNet(net(n)); t.SetLocked(True); b.Add(t)
    for n, (x, y) in VIAS:
        v = p.PCB_VIA(b); v.SetPosition(xy(x, y)); v.SetWidth(mm(.9)); v.SetDrill(mm(.4)); v.SetViaType(p.VIATYPE_THROUGH)
        v.SetLayerPair(F, B); v.SetNet(net(n)); v.SetLocked(True); b.Add(v)
    b.BuildConnectivity(); p.ZONE_FILLER(b).Fill(b.Zones()); p.SaveBoard(str(path), b)
    (P / 'routing').mkdir(exist_ok=True)
    assert p.ExportSpecctraDSN(b, str(P / 'routing/P02.dsn'))
    print('Power pours, tab strips, GND corridor and anchor tracks locked; DSN exported.')
