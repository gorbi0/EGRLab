"""P07 S1: locked copper of the 10 A path, the PGND return and the Kelvin pair before the router, then the Specctra DSN export.
README layout requirements (S1 section 3, 35 um copper; decisions 5.10; user decision 6.10 evening: J1 / J2 / J3 at the right edge):
- 10 A path J1 -> K1 -> J2 / B+ and J3 / M+ -> RSH1 -> J4, and the PGND return J2.2 -> J1.2: pours on BOTH layers, >= 4 mm wide, stitched
  with vias, out of the router's net list (prepare_routing.py). Right tail column at x = 84.8 (placement.py), top-down J1.2 PGND, J1.1
  VMOTOR, J2.1 MOD_BP, J2.2 PGND, (J5), J3.2 T_EGR_P3, J3.1 MOD_MP; J4 at x = 21.7 on the left (J4.2 T_EGR_P3 above J4.1 T_EGR_P1):
  * relay block (top right): K1 lying, coil on the left, contact columns NC / COM / NO towards the tails; VMOTOR band from J1.1 over the
    contact rows (y 25.4..31.4) and down the COM column; MOD_BP from J2.1 round the NO pins and as a tongue under the relay; R4 (1 k
    precharge, bottom) below the relay across the COM / tongue boundary; D1 / C1 / C2 / C3 / R1 on the VMOTOR / PGND boundary y 25.1;
  * PGND: J1.2 region above the VMOTOR band, J2.2 region and the strip right of the pad row (x 89.1..95.5) joining them, R5 / C4 below the
    tongue;
  * two motor lanes across the bottom (both layers, >= 4.5 mm, stitched): T_EGR_P3 (upper) J3.2 -> J4.2, MOD_MP (lower) J3.1 -> the upper
    force pad of RSH1 next to J4, going down right of the M3 zone at (57.5, 86); T_EGR_P1 from the lower force pad to J4.1. No via in
    the shunt pads, solid shunt pads, wire pads on four 2 mm spokes per layer (P06 R2, review F5);
- RSH1 (WSK2512, turned 270, as P06 R2): Kelvin pair from the sense pads, K_PLUS down from its pad and under the body between the
  force pads to the right, K_MINUS straight right; both into R6 / R7 (10 R, 0.1 %) and on to U1.8 / U1.1, parallel, F.Cu only, no via;
- nothing under the shunt on B.Cu (rule area over its courtyard); router keepouts between and around the Kelvin lines (board.ROUTER_KEEPOUT,
  routing/kelvin-box.json); check_intrusion.py after every router run.
GND and PGND are not joined anywhere on P07 (common point on P02 R4): the GND pours of import_routing.py keep 0.3 mm from these pours.
"""
from pathlib import Path
import pcbnew as p, sys, json, math
sys.path.insert(0, str(Path(__file__).resolve().parent))
from board import NAME
P = Path(__file__).resolve().parents[1]; path = P / f'eda/{NAME}.kicad_pcb'
REPORT = []
mm = p.FromMM
F, B_ = p.F_Cu, p.B_Cu


def xy(x, y):
    return p.VECTOR2I(mm(x), mm(y))


class Board:
    def __init__(self, b):
        self.b = b; self.f = {f.GetReference(): f for f in b.GetFootprints()}
        self.nets = {n.GetNetname().split('/')[-1]: n for n in b.GetNetsByNetcode().values()}

    def pad(self, ref, num):
        return next(a for a in self.f[ref].Pads() if a.GetNumber() == str(num))

    def pp(self, ref, num):
        a = self.pad(ref, num).GetPosition(); return (round(p.ToMM(a.x), 4), round(p.ToMM(a.y), 4))

    def pbox(self, ref, num):
        """Pad copper box (x0, y0, x1, y1) in mm."""
        r = self.pad(ref, num).GetBoundingBox(); return (p.ToMM(r.GetLeft()), p.ToMM(r.GetTop()), p.ToMM(r.GetRight()), p.ToMM(r.GetBottom()))

    def net(self, name):
        return self.nets[name]

    def track(self, net, pts, w=.3, layer=F):
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if (round(x0, 4), round(y0, 4)) == (round(x1, 4), round(y1, 4)):
                continue
            t = p.PCB_TRACK(self.b); t.SetLayer(layer); t.SetWidth(mm(w)); t.SetStart(xy(x0, y0)); t.SetEnd(xy(x1, y1))
            t.SetNet(self.net(net)); t.SetLocked(True); self.b.Add(t)
        REPORT.append({'net': net, 'layer': 'F.Cu' if layer == F else 'B.Cu', 'width_mm': w, 'points_mm': [[round(a, 3) for a in q] for q in pts]})

    def via(self, net, x, y):
        v = p.PCB_VIA(self.b); v.SetPosition(xy(x, y)); v.SetWidth(mm(.9)); v.SetDrill(mm(.4)); v.SetViaType(p.VIATYPE_THROUGH)
        v.SetLayerPair(F, B_); v.SetNet(self.net(net)); v.SetLocked(True); self.b.Add(v)
        REPORT.append({'net': net, 'via_mm': [x, y]})

    def pour(self, net, rects, prio=10):
        """One zone per layer: union of the rectangles (x0, y0, x1, y1), solid pad connection, on F.Cu and B.Cu."""
        u = p.SHAPE_POLY_SET()
        for x0, y0, x1, y1 in rects:
            one = p.SHAPE_POLY_SET(); one.NewOutline()
            for x, y in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]:
                one.Append(mm(x), mm(y))
            u.BooleanAdd(one)
        u.Simplify()
        assert u.OutlineCount() == 1 and u.HoleCount(0) == 0, (net, u.OutlineCount())
        o = u.Outline(0); pts = [(p.ToMM(o.CPoint(i).x), p.ToMM(o.CPoint(i).y)) for i in range(o.PointCount())]
        for L in (F, B_):
            z = p.ZONE(self.b); z.SetLayer(L); z.SetNet(self.net(net)); z.SetAssignedPriority(prio)
            z.SetZoneName(f'FORCE {net} {self.b.GetLayerName(L)}'); z.SetLocalClearance(mm(.3)); z.SetMinThickness(mm(.25))
            z.SetPadConnection(p.ZONE_CONNECTION_FULL); z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
            z.SetThermalReliefSpokeWidth(mm(2.0)); z.SetThermalReliefGap(mm(.5))   # 2.10: spokes of the J3 / J4 wire pads (below)
            ol = z.Outline(); ol.NewOutline()
            for x, y in pts:
                ol.Append(mm(x), mm(y))
            z.SetLocked(True); self.b.Add(z)
        REPORT.append({'pour': net, 'layers': ['F.Cu', 'B.Cu'], 'outline_mm': [[round(a, 3) for a in q] for q in pts]})

    def rule(self, name, rect, layers):
        z = p.ZONE(self.b); z.SetIsRuleArea(True); ls = p.LSET()
        for L in layers:
            ls.AddLayer(L)
        z.SetLayerSet(ls); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True); z.SetDoNotAllowZoneFills(True)
        z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False); z.SetZoneName(name)
        o = z.Outline(); o.NewOutline(); x0, y0, x1, y1 = rect
        for x, y in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]:
            o.Append(mm(x), mm(y))
        self.b.Add(z); REPORT.append({'rule_area': name, 'rect_mm': [round(v, 3) for v in rect]})


GAP = .6       # between two force pours (each keeps 0.3 to foreign copper)
CL = .35       # pour outline to a sense pad / Kelvin track edge
XL = 11.0      # pour edge towards the wall (anchor rule areas, x <= 12.7 at the anchors, cut the fill there)


def copy_poly(src, dst):
    """Point-by-point copy of a SHAPE_POLY_SET with holes into a zone outline (SetOutline() with a temporary crashed KiCad 10)."""
    for k in range(src.OutlineCount()):
        dst.NewOutline(); o = src.Outline(k); oi = dst.OutlineCount() - 1
        for i in range(o.PointCount()):
            dst.Append(o.CPoint(i).x, o.CPoint(i).y, oi)
        for h in range(src.HoleCount(k)):
            dst.NewHole(oi); hh = src.Hole(k, h)
            for i in range(hh.PointCount()):
                dst.Append(hh.CPoint(i).x, hh.CPoint(i).y, oi, h)


def power(B):
    """User decision 6.10 evening: J1 / J2 / J3 at the right edge (pad row x = TXR), J4 at x = 0; see the module docstring."""
    T = {k: B.pp(*k) for k in [('J1', 2), ('J1', 1), ('J2', 1), ('J2', 2), ('J4', 1), ('J4', 2)]}
    ys = [T[k][1] for k in T]; tx = T[('J1', 2)][0]
    assert all(T[k][0] == tx for k in T) and ys == sorted(ys), ('right tail column order (placement.py)', T)
    nets = [B.pad(*k).GetNetname().split('/')[-1] for k in T]
    assert nets == ['PGND', 'VMOTOR', 'MOD_BP', 'PGND', 'T_EGR_P1', 'T_EGR_P3'], nets
    j31, j32 = B.pp('J3', 1), B.pp('J3', 2)
    assert j31[1] == j32[1] and j31[0] < j32[0] and j31[1] > 80 and j32[0] < tx, ('J3 at edge B, pad 1 (MOD_MP) left of pad 2 (T_EGR_P3)', j31, j32)
    hp = (B.pbox('J1', 1)[2] - B.pbox('J1', 1)[0]) / 2
    j12, j11, j21, j22, j41, j42 = ys
    no, com, nc = B.pp('K1', '14'), B.pp('K1', '11'), B.pp('K1', '12')
    kpins = [(round(p.ToMM(a.GetPosition().x), 3), round(p.ToMM(a.GetPosition().y), 3), a.GetNumber()) for a in B.f['K1'].Pads()]
    rows = sorted({y for x, y, n in kpins if n in ('11', '12', '14')}); cols = {n: sorted({x for x, y, m in kpins if m == n}) for n in ('11', '12', '14')}
    assert len(rows) == 2 and all(len(v) == 1 for v in cols.values()) and cols['12'][0] < cols['11'][0] < cols['14'][0] < tx - hp - 2, ('K1 lying, NC / COM / NO columns towards the tails', kpins)
    xr_pad = tx - hp                          # 82.55: left edge of the tail pad rings
    xs = tx + hp + 2.05                       # 89.1: PGND strip inner edge (right of the pad rings, between pads and anchors)
    XR = B.b.GetBoardEdgesBoundingBox().GetRight() / 1e6 - 11.0   # 95.5: pour edge towards the edge (anchor rule areas cut the fill)
    xb = xs - GAP                             # 88.5: right end of the VMOTOR / MOD_BP regions
    pr = 1.0                                  # relay pin radius (2 mm pads)
    xc0, xc1 = cols['11'][0] - 2.0, cols['11'][0] + 2.1             # COM column 72.0 .. 76.1
    xn0 = xc1 + GAP                                                 # NO / MOD_BP region from 76.7
    y_pg = j12 + hp + 1.3                                           # PGND top region bottom (24.35; 7.10: the 3.12 mm between J1.2 and J1.1 split so both keep a spoke)
    y_vm = (y_pg + GAP, rows[0] - pr - .35)                         # VMOTOR band above the contact rows (24.95 .. 31.65; 0.35 from the NO pins, J1.1 bottom spoke)
    assert y_vm[0] < j11 - hp - .5, (y_pg, y_vm)                    # J1.1 inside the band
    r4b = B.pbox('R4', '1'); r5b = B.pbox('R5', '1'); c4b = B.pbox('C4', '1')
    y_tg = max(r4b[3], r5b[3], c4b[3]) + .3                         # MOD_BP tongue / COM column / VMOTOR foot bottom (48.6)
    x_tg = xr_pad - .65                                             # tongue right edge (81.9), 0.65 from the J2.2 ring
    y_bp1 = j22 - hp - .69                                          # MOD_BP region bottom right of the tongue (44.6), 0.69 above the J2.2 ring
    kbot = max(y for x, y, n in kpins) + pr                         # relay pin bottom edge (41.5)
    y_ft = kbot + 2.1                                               # VMOTOR foot top (43.6), below the relay body
    x_ft = min(B.pbox('R1', '1')[0], B.pbox('C1', '1')[0], B.pbox('C2', '1')[0]) - 1.0    # foot left end (56.3)
    y_pb = max(B.pbox('D1', '2')[3], B.pbox('C1', '2')[3]) + .35    # PGND strip bottom (53.9)
    for r_, n_ in (('D1', '1'), ('C1', '1'), ('C2', '1'), ('C3', '1'), ('R1', '1')):
        assert B.pbox(r_, n_)[1] > y_ft and B.pbox(r_, n_)[3] < y_tg, ('VMOTOR foot pads', r_, B.pbox(r_, n_))
    for r_, n_ in (('D1', '2'), ('C1', '2'), ('C2', '2'), ('C3', '2'), ('R1', '2')):
        assert B.pbox(r_, n_)[1] > y_tg + GAP, ('PGND strip pads', r_, B.pbox(r_, n_))
    pg = [(xr_pad - .55, j12 - hp - 3.25, XR, y_pg),                # J1.2 region
          (xs, j12 - hp - 3.25, XR, j22 + hp + 3.25),               # strip between the pad row and the anchors
          (xr_pad - .05, y_bp1 + GAP, XR, j22 + hp + 3.25),          # J2.2 region
          (x_ft, y_tg + GAP, xs, y_pb)]                             # strip below the relay (D1 / C1 / C2 / C3 / R1 returns, R5 / C4)
    vm = [(xc0, y_vm[0], xb, y_vm[1]),                              # band J1.1 -> over the contact rows
          (xc0, y_vm[1] - .1, xc1, y_tg),                           # down the COM column (R4 pad 1 at its foot)
          (x_ft, y_ft, xc1, y_tg)]                                  # foot below the relay: D1 / C1 / C2 / C3 / R1
    bp = [(xn0, y_vm[1] + GAP, xb, y_bp1),                          # NO pins and J2.1
          (xn0, y_vm[1] + GAP, x_tg, y_tg)]                         # tongue under the relay (R4 pad 2, R5 / C4 pad 1)
    # ---- motor block in the bottom right corner (7.10): RSH1 turned 90 right above J3.1 (the 2-layer block turned by 180): MOD_MP force pad
    # down onto J3.1, T_EGR_P1 force pad up into a band that runs right and down onto J4.1, T_EGR_P3 from J3.2 right to J4.2 below it;
    # Kelvin pair to the left (R6 / R7 / U1) ----
    s1, s2, s3, s4 = (B.pbox('RSH1', k) for k in (1, 2, 3, 4))   # force MOD_MP down left, sense K_PLUS down right, sense K_MINUS up left, force T_EGR_P1 up right
    c_ = lambda q: ((q[0] + q[2]) / 2, (q[1] + q[3]) / 2)
    assert s1[1] > s4[3] and c_(s2)[0] > c_(s1)[0] and c_(s3)[0] < c_(s4)[0] and c_(s2)[1] > c_(s3)[1], 'RSH1 orientation (placement.py: 90)'
    sx, sy = (c_(s1)[0] + c_(s4)[0]) / 2, (s4[3] + s1[1]) / 2
    w = .3
    r61, r62, r71, r72 = B.pp('R6', 1), B.pp('R6', 2), B.pp('R7', 1), B.pp('R7', 2)
    u8, u1 = B.pp('U1', 8), B.pp('U1', 1)
    kp, km = c_(s2), c_(s3)
    yk = r61[1]
    assert s4[3] + w / 2 + .3 < yk < s1[1] - w / 2 - .3, ('K_PLUS row between the force pads', yk)
    B.track('K_PLUS', [kp, (kp[0], yk), r61], w)                    # up from its pad, then left under the body between the force pads
    assert abs(km[1] - r71[1]) < .01, 'K_MINUS row = R7 row'
    B.track('K_MINUS', [km, r71], w)

    def into(a, c):   # R pad -> U1 pin: horizontal to the left, then 45 deg onto the pin row
        d = abs(c[1] - a[1]); return [a, (c[0] + d, a[1]), c]
    B.track('INA_PLUS', into(r62, u8), w); B.track('INA_MINUS', into(r72, u1), w)
    q41, q42 = T[('J4', 1)], T[('J4', 2)]                           # J4.1 T_EGR_P1 / J4.2 T_EGR_P3 pad centres
    YB = 68.6                                                       # top of the T_EGR_P1 band (below the logic U13 / U14 / U16)
    x_l = 62.0                                                      # MOD_MP left edge (M3 zone at (57.5, 86): r 3.5 + 0.8)
    yB = j31[1] + hp + 3.75                                         # pour bottom towards edge B (91.0; the anchor rule areas start at y 94)
    xr6 = max(B.pbox('R6', 1)[2], B.pbox('R7', 1)[2]) + CL          # right of the Kelvin resistors
    mp = [(xr6, yk + w / 2 + CL + .3, s2[0] - CL, j31[1]),          # beside the force pad, left of the K_PLUS pad, below the K_PLUS row
          (x_l, B.pbox('R6', 1)[3] + CL + .3, xr6 + .6, yB + 1.5),  # left strip below R6 (room for the stitching vias)
          (x_l, s2[3] + CL, j31[0] + hp + 1.0, yB + 1.5)]           # J3.1 (below the K_PLUS pad), down to y 92.5 as T_EGR_P3
    y41b = q41[1] + hp + 1.3                                        # band bottom at J4.1 (7.10: J4.1 / J4.2 share the 3.12 mm between them, a spoke each)
    p1 = [(s3[2] + CL, YB, q41[0] + hp + .75, min(s4[3] + .5, yk - w / 2 - CL - .1)),   # band from the force pad to the right (right of the K_MINUS pad)
          (q41[0] - hp - 2.5, YB, q41[0] + hp + 2.5, y41b)]                             # down onto J4.1 (left / right spokes: 2.5 mm past the pad)
    p3 = [(mp[2][2] + GAP, y41b + GAP, q42[0] + hp + 2.5, 93.6),                       # J3.2 -> J4.2 (7.10: down to the J3 anchor rule area at y 94,
          (j32[0] + 6.8, y41b + GAP, q42[0] + hp + 2.5, 98.4)]                         # and right of the J3 anchor down to 98.4: >= 4 mm under both pads)
    assert p3[0][0] < j32[0] - hp and p3[0][1] < j32[1] - hp and p3[0][3] > q42[1] + hp - .1, (p3, j32, q42)
    # the two NC pins of K1 (both numbered 12, one schematic pin): KiCad joins them in one net and DRC wants them connected -> short F.Cu tie
    ncp = [a for a in B.f['K1'].Pads() if a.GetNumber() == '12']
    nc = sorted((round(p.ToMM(a.GetPosition().x), 4), round(p.ToMM(a.GetPosition().y), 4)) for a in ncp)
    assert len(nc) == 2, nc
    B.track(ncp[0].GetNetname().split('/')[-1], nc, .3)
    B.pour('PGND', pg); B.pour('MOD_BP', bp); B.pour('VMOTOR', vm)
    B.pour('MOD_MP', mp); B.pour('T_EGR_P3', p3); B.pour('T_EGR_P1', p1)
    # ---- 4 layers (user decision 6.10): In1.Cu under the relay block (its pours + the cable area of J1 / J2) is a separate PGND area, never
    # GND; In2.Cu there has no tracks and no zone fills (vias of the force nets pass). Under the motor lanes, J3 / J4 and the shunt In1.Cu is
    # the GND plane (the lanes carry the motor current, not the PGND return; the plane stays one piece across the board) and In2.Cu only
    # carries signals crossing the lanes (no supply zone fill under them) ----
    blk = p.SHAPE_POLY_SET()
    for x0, y0, x1, y1 in pg + bp + vm + [(xb, j12 - hp - 3.25, B.b.GetBoardEdgesBoundingBox().GetRight() / 1e6 - .6, j22 + hp + 3.25)]:
        one = p.SHAPE_POLY_SET(); one.NewOutline()
        for x, y in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]:
            one.Append(mm(x), mm(y))
        blk.BooleanAdd(one)
    blk.Inflate(mm(.4), p.CORNER_STRATEGY_CHAMFER_ALL_CORNERS, mm(.01)); blk.Deflate(mm(.4), p.CORNER_STRATEGY_CHAMFER_ALL_CORNERS, mm(.01))   # close the 0.6 mm gaps
    blk.Simplify()
    z = p.ZONE(B.b); z.SetLayer(p.In1_Cu); z.SetNet(B.net('PGND')); z.SetAssignedPriority(10); z.SetZoneName('PGND In1.Cu (pod torem mocy)')
    z.SetLocalClearance(mm(.3)); z.SetMinThickness(mm(.25)); z.SetPadConnection(p.ZONE_CONNECTION_FULL); z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
    z.SetThermalReliefSpokeWidth(mm(2.0)); z.SetThermalReliefGap(mm(.5)); copy_poly(blk, z.Outline()); z.SetLocked(True); B.b.Add(z)
    # (7.10, user decision: logic tracks may run on In2.Cu under the power block, over the In1 PGND area; no In2 keepout here any more.
    # The analog / Kelvin nets must not (verify_pcb.py, board.ANALOG_NETS); the In2 supply zones (board.IN2_SUPPLY) stay outside the block.)
    # (the In2 'no supply fill under the motor lanes' rule area is made by inner_zones.py after the routing: KiCad exports every rule
    # area to the DSN as a keepout, and the router must be free to cross the lanes on In2)
    REPORT.append({'in1_pgnd_mm2': round(blk.Area() / 1e12, 1), 'outlines': blk.OutlineCount()})
    # ---- stitching vias: a grid inside each pour, clear of every pad (any layer), hole, rule area and of each other ----
    pads = [(a, f.GetReference()) for f in B.b.GetFootprints() for a in f.Pads()]
    rules = [z for z in B.b.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowVias()]   # 6.10: the In2 area under the power block allows vias
    placed = []
    sh = B.f['RSH1']; sh.BuildCourtyardCaches(); shc = sh.GetCourtyard(p.F_CrtYd)

    def legal(x, y, rects):
        c = xy(x, y)
        if not any(r[0] + 1.0 <= x <= r[2] - 1.0 and r[1] + 1.0 <= y <= r[3] - 1.0 for r in rects):
            return False
        if any(math.dist((x, y), q) < 2.6 for q in placed) or shc.Contains(c) or math.dist((x, y), (sx, sy)) < 5.0:   # 7.10: 5 mm (was 6; the MOD_MP pour under the shunt got 6 vias)
            return False
        if any(z.Outline().Contains(c) or math.sqrt(z.Outline().SquaredDistance(c)) / 1e6 < .6 for z in rules):
            return False
        for a, ref in pads:
            bb = a.GetBoundingBox(); d = max(p.ToMM(bb.GetLeft()) - x, 0, x - p.ToMM(bb.GetRight())), max(p.ToMM(bb.GetTop()) - y, 0, y - p.ToMM(bb.GetBottom()))
            if math.hypot(*d) < .45 + .5:
                return False
        return True
    counts = {}
    for net, rects in (('PGND', pg), ('MOD_BP', bp), ('VMOTOR', vm), ('MOD_MP', mp), ('T_EGR_P3', p3), ('T_EGR_P1', p1)):
        n = 0
        for step, x0, y0 in ((2.9, 11.5, 15.0), (1.45, 12.225, 15.725), (.725, 11.8625, 15.3625)):   # finer offset grids while < 8 vias
            for y in [k * step + y0 for k in range(int(80 / step))]:
                for x in [k * step + x0 for k in range(int(95 / step))]:   # whole board width (6.10 evening: blocks right and across)
                    if legal(x, y, rects):
                        B.via(net, round(x, 2), round(y, 2)); placed.append((x, y)); n += 1
            if n >= 8:
                break
        counts[net] = n
    # ---- nothing under the shunt on B.Cu (its courtyard + 0.3) ----
    cy = shc.BBox()
    B.rule('RSH1: nic pod bocznikiem (B.Cu)', (p.ToMM(cy.GetLeft()) - .3, p.ToMM(cy.GetTop()) - .3, p.ToMM(cy.GetRight()) + .3, p.ToMM(cy.GetBottom()) + .3), [B_])
    # tail wire pads on four 2 mm spokes per layer (P06 R2, review F5); shunt and relay pins solid
    for r in ('J1', 'J2', 'J3', 'J4'):
        for a in B.f[r].Pads():
            if a.GetNumber():
                a.SetLocalZoneConnection(p.ZONE_CONNECTION_THERMAL)
    for a in B.f['RSH1'].Pads():
        a.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
    # Kelvin box for the router / planner keepouts (board.ROUTER_KEEPOUT): pin-free, between the force pours and the U1 pin column
    kx0, kx1 = u8[0] + .9, s3[0] - CL; ky0, ky1 = r71[1] - 1.0, yk + 1.0   # 7.10: the pair runs to the left
    box = {'f_box': [round(kx0, 2), round(ky0, 2), round(kx1, 2), round(ky1, 2)], 'b_box': [round(kx0, 2), round(ky0, 2), round(kx1, 2), round(ky1, 2)],
           # 6.10 evening (4 layers): the RSH1 courtyard + 0.3 mm as a router keepout too (F.Cu, and through board.py also In2.Cu: one
           # router run put I_FILT on In2 under the shunt); no routable pin inside (force / Kelvin nets are out of the DSN)
           'shunt_box': [round(p.ToMM(cy.GetLeft()) - .3, 2), round(p.ToMM(cy.GetTop()) - .3, 2), round(p.ToMM(cy.GetRight()) + .3, 2), round(p.ToMM(cy.GetBottom()) + .3, 2)]}
    (P / 'routing').mkdir(exist_ok=True); (P / 'routing/kelvin-box.json').write_text(json.dumps(box) + '\n')
    return {'pgnd': pg, 'mod_bp': bp, 'vmotor': vm, 'mod_mp': mp, 't_egr_p3': p3, 't_egr_p1': p1, 'k_row': yk, 'stitch_vias': counts, 'kelvin_box': box}


if __name__ == '__main__':
    b = p.LoadBoard(str(path)); B = Board(b)
    for f in b.GetFootprints():
        f.BuildCourtyardCaches()
    info = power(B)
    p.ZONE_FILLER(b).Fill(b.Zones())
    b.BuildConnectivity(); p.SaveBoard(str(path), b)
    (P / 'routing').mkdir(exist_ok=True)
    (P / 'routing/critical.json').write_text(json.dumps(REPORT + [{'summary': info}], indent=1) + '\n')
    assert p.ExportSpecctraDSN(b, str(P / f'routing/{NAME}.dsn'))
    print(f'{NAME}: force pours (both layers) {list(info["stitch_vias"].items())} stitching vias, Kelvin pair, B.Cu rule area under RSH1 locked ({len(REPORT)} items); DSN exported.')
