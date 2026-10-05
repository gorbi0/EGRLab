"""P07 S1: locked copper of the 10 A path, the PGND return and the Kelvin pair before the router, then the Specctra DSN export.
README layout requirements (S1 section 3, 35 um copper; decisions 5.10):
- 10 A path J1 -> K1 -> J2 / B+ and J3 / M+ -> RSH1 -> J4, and the PGND return J2.2 -> J1.2: pours on BOTH layers, >= 4 mm wide, stitched
  with vias, out of the router's net list (prepare_routing.py). Tail column at x = 21.7 (placement.py), top-down J2.2 PGND, J2.1 MOD_BP,
  J1.1 VMOTOR, J1.2 PGND, J3.1 MOD_MP, J3.2 T_EGR_P3, J4.2 T_EGR_P3, J4.1 T_EGR_P1:
  * MOD_BP band y 24.3..32.5 from J2.1 to the NO pins of K1 (y 29.5) and VMOTOR band y 33.1..43.0 from J1.1 to the COM pins (y 34.5),
    on to D1 / C1 / C2 / C3 / R1 right of K1; R4 (1 k precharge, bottom) between the pin columns across the MOD_BP / VMOTOR boundary;
  * PGND: J2.2 region above the MOD_BP band, J1.2 region below the VMOTOR band (with the TVS / bulk / bleed returns), joined by a strip
    between the cable anchors and the pad row (x 11..17.9);
  * MOD_MP band at J3.1 and down right of the T_EGR_P3 block to the upper force pad of RSH1; T_EGR_P1 from the lower force pad down
    to the band at J4.1; T_EGR_P3 one block J3.2 - J4.2 left of the shunt. No via in the shunt pads, solid shunt pads, wire pads on
    four 2 mm spokes per layer (P06 R2, review F5);
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


def power(B):
    T = {k: B.pp(*k) for k in [('J2', 2), ('J2', 1), ('J1', 1), ('J1', 2), ('J3', 1), ('J3', 2), ('J4', 2), ('J4', 1)]}
    ys = [T[k][1] for k in T]; tx = T[('J2', 2)][0]
    assert all(T[k][0] == tx for k in T) and ys == sorted(ys), ('tail column order (placement.py)', T)
    nets = [B.pad(*k).GetNetname().split('/')[-1] for k in T]
    assert nets == ['PGND', 'MOD_BP', 'VMOTOR', 'PGND', 'MOD_MP', 'T_EGR_P3', 'T_EGR_P3', 'T_EGR_P1'], nets
    hp = (B.pbox('J2', 1)[2] - B.pbox('J2', 1)[0]) / 2
    j22, j21, j11, j12, j31, j32, j42, j41 = ys
    no, com, a2 = B.pp('K1', '14'), B.pp('K1', '11'), B.pp('K1', 'A2')
    assert abs(no[1] - j21) < 1.5 and abs(com[1] - no[1] - 5.0) < .01, ('K1 contacts level with J2.1 / J1.1', no, com)
    xs = tx - hp - 2.05                      # 17.4: PGND strip edge (left of the MOD_BP / VMOTOR pad rings)
    xb = xs + GAP                            # MOD_BP / VMOTOR bands start
    kr = max(B.pbox('K1', '14')[2], B.pbox('R59', '1')[2]) + .3   # right of the K1 contact pins and the MOD_BP service pad
    y_bp = (j22 + hp + 1.1, (no[1] + com[1]) / 2 - GAP / 2)        # MOD_BP band
    y_vm = (y_bp[1] + GAP, j11 + hp + .83)                         # VMOTOR band (to 43.0)
    xr = max(B.pbox('C3', '1')[2], B.pbox('C1', '1')[2]) + .4     # right end of the VMOTOR band / PGND under D1 .. C3
    pg = [(XL, j22 - hp - 3.25, kr, y_bp[0] - GAP),                 # J2.2 region (R5 / C4 returns)
          (XL, j22 - hp - 3.25, xs, j12 + hp + .8),                 # strip between the anchors and the pad row
          (XL, y_vm[1] + GAP, B.pbox('D1', '2')[2] + 1.0, j12 + hp + .8),   # J1.2 region with D1
          (XL, y_vm[1] + GAP, xr, max(B.pbox('C1', '2')[3], B.pbox('C3', '2')[3]) + .9)]   # C1 / C2 / R1 / C3 returns (stays above U4)
    bp = [(xb, y_bp[0], kr, y_bp[1])]
    vm = [(xb, y_vm[0], xr, y_vm[1])]
    # ---- bottom block: RSH1 (turned 270) between MOD_MP (up) and T_EGR_P1 (down), T_EGR_P3 left of it ----
    s1, s2, s3, s4 = (B.pbox('RSH1', k) for k in (1, 2, 3, 4))   # force MOD_MP up, sense K_PLUS up left, sense K_MINUS down right, force T_EGR_P1 down
    assert s2[2] < s1[2] and s2[1] < s4[1] and s3[0] > s4[0] and s1[3] < s4[1], 'RSH1 orientation (placement.py: 270)'
    sx, sy = B.pp('RSH1', '1')[0] - .64, (s1[3] + s4[1]) / 2
    w = .3
    r61, r62, r71, r72 = B.pp('R6', 1), B.pp('R6', 2), B.pp('R7', 1), B.pp('R7', 2)
    u8, u1 = B.pp('U1', 8), B.pp('U1', 1)
    kp = ((s2[0] + s2[2]) / 2, (s2[1] + s2[3]) / 2); km = ((s3[0] + s3[2]) / 2, (s3[1] + s3[3]) / 2)
    yk = r61[1]
    assert s1[3] + w / 2 + .3 < yk < s4[1] - w / 2 - .3, ('K_PLUS row between the force pads', yk)
    B.track('K_PLUS', [kp, (kp[0], yk), r61], w)
    assert abs(km[1] - r71[1]) < .01, 'K_MINUS row = R7 row'
    B.track('K_MINUS', [km, r71], w)

    def into(a, c):   # R pad -> U1 pin: horizontal, then 45 deg onto the pin row
        d = abs(c[1] - a[1]); return [a, (c[0] - d, a[1]), c]
    B.track('INA_PLUS', into(r62, u8), w); B.track('INA_MINUS', into(r72, u1), w)
    p3r = s2[0] - CL - .5                                           # T_EGR_P3 block right edge (left of the K_PLUS pad and track)
    xm = s2[2] + CL                                                 # MOD_MP down strip left edge (right of the K_PLUS pad)
    xe = min(B.pbox('R6', 1)[0], B.pbox('R7', 1)[0]) - 1.6          # right end of the force pours (left of R6 / R7)
    mp_top = max(a2[1] + 1.0 + .3, j31 - hp - 2.0)                  # below the K1 coil pins
    mp = [(XL, mp_top, xe, j31 + hp + 1.2),                         # band over J3.1
          (xm, mp_top, xe, yk - w / 2 - CL - .7)]                   # down to the MOD_MP force pad (above the K_PLUS row)
    p3 = [(XL, j31 + hp + 1.2 + GAP, p3r, j42 + hp + .8)]
    e_top = yk + w / 2 + CL + .7                                    # below the K_PLUS row
    k_bot = s3[3] + CL                                              # below the K_MINUS pad (and its track)
    y41b = max(j41 + hp + 2.6, B.pbox('R61', 1)[3] + .5)
    p1 = [(p3r + GAP, e_top, s3[0] - CL, k_bot),                    # beside the T_EGR_P1 force pad (left of the K_MINUS pad)
          (p3r + GAP, k_bot, xe, y41b),                             # below the shunt down to the band
          (XL, j42 + hp + .8 + GAP, xe, y41b)]                      # band over J4.1 (with the service pad of R61)
    B.pour('PGND', pg); B.pour('MOD_BP', bp); B.pour('VMOTOR', vm)
    B.pour('MOD_MP', mp); B.pour('T_EGR_P3', p3); B.pour('T_EGR_P1', p1)
    # ---- stitching vias: a grid inside each pour, clear of every pad (any layer), hole, rule area and of each other ----
    pads = [(a, f.GetReference()) for f in B.b.GetFootprints() for a in f.Pads()]
    rules = [z for z in B.b.Zones() if z.GetIsRuleArea()]
    placed = []
    sh = B.f['RSH1']; sh.BuildCourtyardCaches(); shc = sh.GetCourtyard(p.F_CrtYd)

    def legal(x, y, rects):
        c = xy(x, y)
        if not any(r[0] + 1.0 <= x <= r[2] - 1.0 and r[1] + 1.0 <= y <= r[3] - 1.0 for r in rects):
            return False
        if any(math.dist((x, y), q) < 2.6 for q in placed) or shc.Contains(c) or math.dist((x, y), (sx, sy)) < 6.0:
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
                for x in [k * step + x0 for k in range(int(46 / step))]:
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
    kx0, kx1 = xe + .4, u8[0] - .9; ky0, ky1 = yk - 1.0, r71[1] + 1.0
    box = {'f_box': [round(kx0, 2), round(ky0, 2), round(kx1, 2), round(ky1, 2)], 'b_box': [round(kx0, 2), round(ky0, 2), round(kx1, 2), round(ky1, 2)]}
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
