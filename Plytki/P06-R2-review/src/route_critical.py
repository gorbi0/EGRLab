"""P06 R2: locked copper of the motor current path and the Kelvin pair before the router, then the Specctra DSN export.
README layout requirements (S1 section 3, 35 um copper):
- force path 5-6 A (10 A in the passive test E15): ECU_P1 and EGR_P1 as pours on BOTH layers, >= 4 mm wide, stitched with vias,
  short: the measuring loop J3.1 -> RSH1 -> J3.2 is one pad pitch long (placement.py). J3 is numbered from the far end, so after
  the 90 deg turn the column at x = 15 reads J3.1 ECU, J3.2 EGR, J4.2 EGR, J4.1 ECU: EGR_P1 is one block in the middle, ECU_P1 of
  J3 and J4 is joined by a 5 mm strip between the cable anchors and the pad rows (x 6..11; the cables lie on the solder mask above
  it). No via in the shunt pads, solid pad connections (no thermals) on the force pads;
- RSH1 (WSK2512, turned 270): ECU force pad up, EGR force pad down, sense pads on the diagonal. The ECU pour reaches its pad from
  above (the K_PLUS sense pad sits left of it), the EGR pour from the left and below (K_MINUS sense pad right of it);
- Kelvin pair from the sense pads, not from the pours: K_PLUS straight down from its pad and under the body between the force pads
  (3.7 mm gap) to the right, K_MINUS straight right from its pad; both into R1 / R2 (10 Ohm, 0.1 %) and on to U1.8 / U1.1 - parallel,
  3 mm apart, no connector and no via on the way;
- nothing under the shunt on B.Cu (rule area over its courtyard), no foreign router copper in its courtyard or between the Kelvin
  lines (DSN keepouts, board.ROUTER_KEEPOUT; check_intrusion.py after every router run).
"""
from pathlib import Path
import pcbnew as p, sys, json
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


GAP = .6       # between the ECU_P1 and EGR_P1 pours (each keeps 0.3 to foreign copper)
CL = .35       # pour outline to a sense pad / Kelvin track edge


def force_and_kelvin(B):
    (j31x, j31y), (j32x, j32y), (j42x, j42y), (j41x, j41y) = B.pp('J3', 1), B.pp('J3', 2), B.pp('J4', 2), B.pp('J4', 1)
    assert j31x == j32x == j42x == j41x and j31y < j32y < j42y < j41y, 'tail column order (placement.py)'
    hp = (B.pbox('J3', 1)[2] - B.pbox('J3', 1)[0]) / 2           # tail pad radius (4.5 mm pads)
    s2, s3 = B.pbox('RSH1', 2), B.pbox('RSH1', 3)                 # sense pads: K_PLUS top left, K_MINUS bottom right
    s1, s4 = B.pbox('RSH1', 1), B.pbox('RSH1', 4)                 # force pads: ECU top, EGR bottom
    assert s2[2] < s1[2] and s2[1] < s4[1] and s3[0] > s4[0] and s1[3] < s4[1], 'RSH1 orientation (placement.py: 270)'
    sx, sy = B.f['RSH1'].GetPosition().x, B.f['RSH1'].GetPosition().y; sx, sy = p.ToMM(sx), p.ToMM(sy)
    w = .3
    # ---- Kelvin pair ----
    r11, r12, r21, r22 = B.pp('R1', 1), B.pp('R1', 2), B.pp('R2', 1), B.pp('R2', 2)
    u8, u1 = B.pp('U1', 8), B.pp('U1', 1)
    kp = ((s2[0] + s2[2]) / 2, (s2[1] + s2[3]) / 2); km = ((s3[0] + s3[2]) / 2, (s3[1] + s3[3]) / 2)
    yk = r11[1]                                                   # K_PLUS row under the body (R1 row)
    assert s1[3] + w / 2 + .3 < yk < s4[1] - w / 2 - .3, ('K_PLUS row between the force pads', yk)
    B.track('K_PLUS', [kp, (kp[0], yk), r11], w)
    assert abs(km[1] - r21[1]) < .01, 'K_MINUS row = R2 row'
    B.track('K_MINUS', [km, r21], w)

    def into(a, c):   # R pad -> U1 pin: horizontal, then 45 deg onto the pin row
        d = abs(c[1] - a[1]); return [a, (c[0] - d, a[1]), c]
    B.track('INA_PLUS', into(r12, u8), w); B.track('INA_MINUS', into(r22, u1), w)
    # ---- force pours (both layers): rectangles in mm ----
    xl, xs = 6.0, 11.0                                            # ECU strip between the anchors' 3 mm zones (x <= 6) and the pad rows
    xp = j31x + hp + .5                                           # right of the tail pads
    xr = min(B.pbox('R1', 1)[0], B.pbox('R2', 1)[0]) - .9         # left of R1 / R2
    ytop = j31y - hp - 2.65                                       # 18.6: J3 courtyard top
    k_top = s2[1] - CL                                            # above the K_PLUS sense pad
    ecu = [(xl, ytop, xr, k_top),                                                 # band over J3.1 and the shunt
           (s2[2] + CL, k_top, xr, yk - w / 2 - CL - .2),                         # right of the K_PLUS pad down to the ECU force pad
           (xl, k_top, kp[0] - w / 2 - CL - .2, j32y - hp - .9),                  # J3.1 and the area left of the K_PLUS track
           (xl, k_top, xs, j41y + hp + .15),                                      # strip down to J4.1
           (xl, j42y + hp + GAP, xr, j41y + hp + .15)]                            # J4.1 and right of it
    e_top = yk + w / 2 + CL + .15                                 # below the K_PLUS row
    egr = [(xs + GAP, e_top, s3[0] - CL, s3[3] + .7),                             # J3.2 -> EGR force pad (left of the K_MINUS pad)
           (xs + GAP, s3[3] + .7, xr, j42y + hp)]                                 # below the shunt down to J4.2
    B.pour('ECU_P1', ecu); B.pour('EGR_P1', egr)
    # stitching vias (not in any pad, outside the B.Cu rule area under the shunt)
    for x, y in [(xp + .8, ytop + 1.4), (xp + 3.6, ytop + 1.4), (xr - 1.0, ytop + 1.4), (xr - 1.0, k_top - 1.4), (xp + 3.6, k_top - 1.4),
                 (xr - 1.0, s1[3] - .4), (xl + 2.5, j31y + 6.0), (xl + 2.5, j31y + 11.5), (xl + 2.5, j31y + 17.0), (xl + 2.5, j31y + 22.5),
                 (xp + 1.5, j41y - 1.5), (xp + 4.5, j41y - 1.5), (xr - 1.0, j41y - 1.5), (xp + 1.5, j41y + 1.5), (xr - 1.0, j41y + 1.5)]:
        B.via('ECU_P1', round(x, 2), round(y, 2))
    for x, y in [(xs + 2.0, j32y + 4.3), (xp - 1.5, j32y + 4.3), (xs + 2.0, j32y + 8.0), (xp - 1.5, j32y + 8.0),
                 (s4[0] - 1.2, s3[3] + 1.8), (sx + 1.2, s3[3] + 1.8), (xr - 1.0, s3[3] + 1.8),
                 (xp + 2.0, j32y + 7.5), (xr - 1.0, j32y + 7.5), (xp + 2.0, j42y - 1.5), (xr - 1.0, j42y - 1.5), (xp + 2.0, j42y + 1.4)]:
        B.via('EGR_P1', round(x, 2), round(y, 2))
    # ---- nothing under the shunt on B.Cu (its courtyard + 0.3) ----
    cy = B.f['RSH1'].GetCourtyard(p.F_CrtYd).BBox()
    B.rule('RSH1: nic pod bocznikiem (B.Cu)', (p.ToMM(cy.GetLeft()) - .3, p.ToMM(cy.GetTop()) - .3, p.ToMM(cy.GetRight()) + .3, p.ToMM(cy.GetBottom()) + .3), [B_])
    for a in list(B.f['J3'].Pads()) + list(B.f['J4'].Pads()) + list(B.f['RSH1'].Pads()):
        if a.GetNetname().split('/')[-1] in ('ECU_P1', 'EGR_P1'):
            a.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
    return {'ecu': ecu, 'egr': egr, 'k_row': yk}


if __name__ == '__main__':
    b = p.LoadBoard(str(path)); B = Board(b)
    for f in b.GetFootprints():
        f.BuildCourtyardCaches()
    info = force_and_kelvin(B)
    p.ZONE_FILLER(b).Fill(b.Zones())
    b.BuildConnectivity(); p.SaveBoard(str(path), b)
    (P / 'routing').mkdir(exist_ok=True)
    (P / 'routing/critical.json').write_text(json.dumps(REPORT, indent=1) + '\n')
    assert p.ExportSpecctraDSN(b, str(P / f'routing/{NAME}.dsn'))
    print(f'{NAME}: force pours ECU_P1 / EGR_P1 (both layers), Kelvin pair and the B.Cu rule area under RSH1 locked ({len(REPORT)} items); DSN exported.')
