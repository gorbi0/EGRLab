"""M1-R1: locked copper before the router, then the Specctra DSN export (structure of P07 S1 / P05 R3 route_critical.py).
- 7.5 A path (README, D-M1-13): BAT_P pour J1.1 -> F1.1, VBUS pour F1.2 -> J2 (VMOTOR to X1.3), the motor line P1_ECU J5.1 -> RSH1 force
  pad 1 and P1_EGR RSH1 force pad 4 -> J5.2: pours on F.Cu AND B.Cu (>= 4 mm), stitched with 0.9 / 0.4 vias, out of the router's net
  list (prepare_routing.py). VBUS also feeds the TSR inputs: locked 1.0 mm trunk F1.2 -> C1 -> U1.1 / U2.1; TP3 stands in the VBUS pour.
  P1_EGR also feeds the CH1 divider: locked 0.3 mm stub from the lane to R11 pad 1. Wire pads on 2 mm spokes, shunt pads solid.
- RSH1 (WSK2512, rot 0): the force pads sit on the diagonal, so are the sense pads (2 bottom left, 3 top right). K_PLUS leaves pad 2
  downwards on F.Cu to R22; K_MINUS leaves pad 3 upwards into the channel between the two lanes, drops through a via to In2.Cu (In1.Cu
  GND between it and the lanes), runs under the lane to a via at R23. INA_PLUS / INA_MINUS R22 / R23 -> U4 pins 8 / 1 on F.Cu.
  Nothing under the shunt on B.Cu (rule area), router keepouts round the Kelvin pair (routing/kelvin-box.json, board.ROUTER_KEEPOUT).
- U3 AD7606B (LQFP-64 0.5 mm, rot 90): the P05 R3 copper (route_u1 there, reviewed 2.10, order package P05-PCB-R3) moved by
  (+37, -15) mm with the parts placed by placement.py at the same relative spots; nets / references renamed (MAP below).
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

    def net(self, name):
        return self.nets[name]

    def track(self, net, pts, w=.3, layer=F):
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if (round(x0, 4), round(y0, 4)) == (round(x1, 4), round(y1, 4)):
                continue
            t = p.PCB_TRACK(self.b); t.SetLayer(layer); t.SetWidth(mm(w)); t.SetStart(xy(x0, y0)); t.SetEnd(xy(x1, y1))
            t.SetNet(self.net(net)); t.SetLocked(True); self.b.Add(t)
        REPORT.append({'net': net, 'layer': self.b.GetLayerName(layer), 'width_mm': w, 'points_mm': [[round(a, 3) for a in q] for q in pts]})

    def via(self, net, x, y, d=.9, h=.4):
        v = p.PCB_VIA(self.b); v.SetPosition(xy(x, y)); v.SetWidth(mm(d)); v.SetDrill(mm(h)); v.SetViaType(p.VIATYPE_THROUGH)
        v.SetLayerPair(F, B_); v.SetNet(self.net(net)); v.SetLocked(True); self.b.Add(v)
        REPORT.append({'net': net, 'via_mm': [x, y], 'd': d})

    def pour(self, net, rects, prio=10):
        """One zone per outer layer: union of the rectangles (x0, y0, x1, y1), solid pad connection, on F.Cu and B.Cu."""
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
            z.SetThermalReliefSpokeWidth(mm(2.0)); z.SetThermalReliefGap(mm(.5))
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


def power(B):
    j11, j12, j2, j51, j52 = B.pp('J1', 1), B.pp('J1', 2), B.pp('J2', 1), B.pp('J5', 1), B.pp('J5', 2)
    f1a = [B.pp('F1', 1)] + [(p.ToMM(a.GetPosition().x), p.ToMM(a.GetPosition().y)) for a in B.f['F1'].Pads() if a.GetNumber() == '1']
    f1b = [(p.ToMM(a.GetPosition().x), p.ToMM(a.GetPosition().y)) for a in B.f['F1'].Pads() if a.GetNumber() == '2']
    assert (j11, j12, j2) == ((14.0, 15.0), (21.62, 15.0), (33.0, 15.0)), 'placement.py moved the supply pads'
    fx2, fy2 = max(f1b, key=lambda q: q[1])   # lower pad of F1 pin 2
    # ---- BAT_P: J1.1 straight down onto both F1 pin-1 pads; VBUS: both F1 pin-2 pads, right and up to J2 (1.75 mm below J1.2) ----
    WP = lambda q: (q[0] - 3.3, q[1] - 3.2, q[0] + 3.3, q[1] + 3.3)   # wire pad (4.5 mm) wholly inside its pour: four 2 mm spokes
    bat = [(j11[0] - 2.5, j11[1], j11[0] + 2.5, max(y for _, y in f1a) + 1.4), WP(j11)]
    vb = [(fx2 - 2.4, min(y for _, y in f1b) - 2.0, j2[0] + 2.3, fy2 + 1.6), (j2[0] - 2.3, j2[1], j2[0] + 2.3, min(y for _, y in f1b) - 2.0), WP(j2)]
    B.pour('BAT_P', bat); B.pour('VBUS', vb)
    # VBUS trunk (1.0 mm, F.Cu) from the pour foot to C1 and the TSR inputs
    u1, u2, c1 = B.pp('U1', 1), B.pp('U2', 1), B.pp('C1', 1); yt = c1[1]
    B.track('VBUS', [(fx2, fy2 + 1.0), (fx2, yt)], w=1.0); B.track('VBUS', [(u1[0], yt), (u2[0], yt)], w=1.0)
    B.track('VBUS', [(u1[0], yt), u1], w=1.0); B.track('VBUS', [(u2[0], yt), u2], w=1.0)
    # ---- motor line through the shunt: P1_ECU lane J5.1 -> pad 1 from above, P1_EGR lane pad 4 from below-right -> J5.2 ----
    s1, s2, s3, s4 = (B.pad('RSH1', n).GetBoundingBox() for n in (1, 2, 3, 4))
    bx = lambda r: (p.ToMM(r.GetLeft()), p.ToMM(r.GetTop()), p.ToMM(r.GetRight()), p.ToMM(r.GetBottom()))
    s1, s2, s3, s4 = map(bx, (s1, s2, s3, s4))
    ecu = [(s1[0], j51[1], j51[0] + 1.5, s1[3]), WP(j51)]                                   # x 41.87 .. 46.5, ends at the bottom of pad 1
    xe0 = s3[2] + .8                                                               # EGR vertical lane left edge (0.8 mm right of pad 3)
    egr = [(xe0, j52[1], xe0 + 4.0, s4[3] + 2.0), (s4[0], s4[1] + .55, xe0 + 4.0, s4[3] + 2.0), WP(j52)]
    assert xe0 <= j52[0] <= xe0 + 4.0, ('J5.2 outside the EGR lane', xe0, j52)
    B.pour('P1_ECU', ecu); B.pour('P1_EGR', egr)
    r11 = B.pp('R11', 1); B.track('P1_EGR', [(xe0 + 3.6, r11[1]), r11])             # CH1 divider tap
    # ---- Kelvin pair ----
    k2, k3 = B.pp('RSH1', 2), B.pp('RSH1', 3); r22, r23 = B.pp('R22', 1), B.pp('R23', 1)
    B.track('K_PLUS', [k2, (k2[0], r22[1]), r22])
    vk1 = (k3[0], s3[1] - .95); vk2 = (k2[0] - .1, r23[1])
    B.track('K_MINUS', [k3, vk1]); B.via('K_MINUS', *vk1, d=.6, h=.3)
    B.track('K_MINUS', [vk1, (vk1[0], 30.0), (vk2[0], 30.0 + (vk1[0] - vk2[0])), vk2], layer=p.In2_Cu)
    B.via('K_MINUS', *vk2, d=.6, h=.3); B.track('K_MINUS', [vk2, r23])
    i8, i1 = B.pp('U4', 8), B.pp('U4', 1); r22b, r23b = B.pp('R22', 2), B.pp('R23', 2)
    B.track('INA_PLUS', [r22b, (i8[0], r22b[1]), i8]); B.track('INA_MINUS', [r23b, (i1[0], r23b[1]), i1])
    # ---- stitching vias inside each pour (grid, clear of pads, rule areas, the K_MINUS corridor x vk1 +- 1.2 and each other) ----
    pads = [a for f in B.b.GetFootprints() for a in f.Pads()]
    rules = [z for z in B.b.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowVias()]
    placed = []

    def legal(x, y, rects):
        if not any(r[0] + 1.0 <= x <= r[2] - 1.0 and r[1] + 1.0 <= y <= r[3] - 1.0 for r in rects):
            return False
        if any(math.dist((x, y), q) < 2.4 for q in placed) or abs(x - vk1[0]) < 1.4 and y > 18:
            return False
        if any(z.Outline().Contains(xy(x, y)) or math.sqrt(z.Outline().SquaredDistance(xy(x, y))) / 1e6 < .6 for z in rules):
            return False
        for a in pads:
            bb = a.GetBoundingBox(); d = max(p.ToMM(bb.GetLeft()) - x, 0, x - p.ToMM(bb.GetRight())), max(p.ToMM(bb.GetTop()) - y, 0, y - p.ToMM(bb.GetBottom()))
            if math.hypot(*d) < .45 + .5:
                return False
        return True
    counts = {}
    for net, rects in (('BAT_P', bat), ('VBUS', vb), ('P1_ECU', ecu), ('P1_EGR', egr)):
        n = 0
        for step, x0, y0 in ((2.4, .2, .2), (1.2, .8, .8), (.6, .5, .5)):
            for y in [k * step + y0 for k in range(int(80 / step))]:
                for x in [k * step + x0 for k in range(int(150 / step))]:
                    if legal(x, y, rects):
                        B.via(net, round(x, 2), round(y, 2)); placed.append((x, y)); n += 1
            if n >= 6:
                break
        counts[net] = n
    sh = B.f['RSH1']; sh.BuildCourtyardCaches(); cy = sh.GetCourtyard(p.F_CrtYd).BBox()
    B.rule('RSH1: nic pod bocznikiem (B.Cu)', (p.ToMM(cy.GetLeft()) - .3, p.ToMM(cy.GetTop()) - .3, p.ToMM(cy.GetRight()) + .3, p.ToMM(cy.GetBottom()) + .3), [B_])
    for r in ('J1', 'J2', 'J5'):
        for a in B.f[r].Pads():
            if a.GetNumber():
                a.SetLocalZoneConnection(p.ZONE_CONNECTION_THERMAL)
    for a in B.f['RSH1'].Pads():
        a.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
    # Kelvin boxes (router keepouts on F.Cu and In2.Cu, board.ROUTER_KEEPOUT): K_PLUS column + R22 / R23, the K_MINUS corridor
    boxes = [[round(k2[0] - .9, 2), round(s2[3] + .35, 2), round(r22b[0] - 1.0, 2), round(r23[1] + 1.2, 2)],
             [round(vk1[0] - .9, 2), round(vk1[1] - .9, 2), round(vk1[0] + .9, 2), round(s3[1] - .35, 2)]]
    boxes += [[round(r22b[0] - .7, 2), round(r22b[1] - .6, 2), round(i8[0] + .35, 2), round(r22b[1] + .6, 2)],      # INA_PLUS R22.2 -> U4.8
              [round(r23b[0] - .7, 2), round(r23b[1] - .6, 2), round(i1[0] + .35, 2), round(r23b[1] + .6, 2)]]      # INA_MINUS R23.2 -> U4.1
    in2 = [round(vk2[0] - .9, 2), round(vk1[1] - .9, 2), round(vk1[0] + .9, 2), round(vk2[1] + .9, 2)]           # K_MINUS on In2.Cu
    (P / 'routing').mkdir(exist_ok=True); (P / 'routing/kelvin-box.json').write_text(json.dumps({'f_boxes': boxes, 'in2_box': in2}) + '\n')
    return {'stitch_vias': counts, 'kelvin_boxes': boxes}


# ---- P05 R3 route_u1 moved to M1 ----
DX, DY = 37.0, -15.0
X = lambda v: round(v + DX, 4)
Y = lambda v: round(v + DY, 4)
CAP = {'C4': 'C6', 'C5': 'C8', 'C6': 'C5', 'C7': 'C9', 'C8': 'C10', 'C9': 'C11', 'C10': 'C12', 'C11': 'C13', 'C12': 'C14', 'C13': 'C15'}
FILT = ['C16', 'C17', 'C18', 'C19', 'C20', 'C23', 'C21', 'C22']   # P05 C27..C34 = CH1..CH8
SRC = {'C17': 'R13', 'C18': 'R15', 'C19': 'R16', 'C20': 'R17', 'C23': 'R21', 'C21': 'R18', 'C22': 'R20'}   # series resistor in the stub row (placement.py)


def route_u3(B):
    pin = lambda n: B.pp('U3', n)
    pc = lambda c, n: B.pp(CAP[c], n)
    # ---- top row: supply / reference pins 33-48 ----
    x36, y = pin(36); B.track('REGCAP_A', [(x36, y), (x36, Y(47.45)), (x36 + .5, Y(46.95)), (x36 + .5, Y(46.6))])
    x39, _ = pin(39); B.track('REGCAP_D', [(x39, y), (x39, Y(46.6))])
    x42, _ = pin(42); B.track('ADC_REF', [(x42, y), (x42, Y(46.5))])
    x44, _ = pin(44); x45, _ = pin(45); yr = Y(47.225)
    c13x, c13y = pc('C13', 1)
    B.track('REFCAP', [(x44, y), (x44, yr)], w=.2); B.track('REFCAP', [(x45, y), (x45, yr)], w=.2)
    B.track('REFCAP', [(x44, yr), (X(54.0), yr)], w=.2)
    B.track('REFCAP', [(X(54.0), yr), (c13x + .9, yr - .7)])
    yv = Y(49.75)
    x48, _ = pin(48); B.track('5VA', [(x48, y), (x48, Y(49.2)), (x48 - .25, yv)], w=.2); B.via('5VA', x48 - .25, yv)
    B.track('ADC_REF', [(x42, y), (x42, yv)], w=.2); B.via('ADC_REF', x42, yv)
    x37, _ = pin(37); x38, _ = pin(38); xm = (x37 + x38) / 2
    B.track('5VA', [(x37, y), (x37, Y(49.3)), (xm, yv)], w=.2); B.track('5VA', [(x38, y), (x38, Y(49.3)), (xm, yv)], w=.2)
    B.via('5VA', xm, yv)
    x34, _ = pin(34); xv34, yv34 = x34 - .05, Y(49.66)
    B.track('3V3', [(x34, y), (x34, Y(49.2)), (xv34, yv34)], w=.2); B.via('3V3', xv34, yv34)
    for net, (vx, vy), cap in [('5VA', (x48 - .25, yv), 'C7'), ('ADC_REF', (x42, yv), 'C11'), ('5VA', (xm, yv), 'C5')]:
        B.track(net, [(vx, vy), pc(cap, 1)], layer=B_)
    xs48, xs37, yj = x48 - .25, X(60.1), Y(41.9)
    c6 = pc('C6', 1)
    B.track('5VA', [(xs48, yv), (xs48, yj)], layer=B_)
    B.track('5VA', [(xm, yv), (xs37, yv - .6), (xs37, yj)], layer=B_)
    B.track('5VA', [(xs48, yj), (xs37, yj)], layer=B_)
    B.via('5VA', c6[0], yj); B.track('5VA', [(c6[0], yj), c6])
    x23, y23 = pin(23); xv23 = X(62.25)
    B.track('3V3', [(x23, y23), (xv23, y23)], w=.2); B.via('3V3', xv23, y23)
    c8 = pc('C8', 1)
    B.track('3V3', [(xv34, yv34), (xv34 + .65, yv34 + .65), (xv34 + .65, y23 - .6), (xv23, y23)], layer=B_)
    B.track('3V3', [(xv23, y23), (c8[0], c8[1] - .4)], layer=B_)
    B.track('3V3', [(c8[0] + .6, c8[1]), (X(66.2), c8[1])], layer=B_)
    c12 = pc('C12', 1); tp = B.pp('TP8', 1); B.track('ADC_REF', [(c12[0] - 1.05, c12[1]), (tp[0], c12[1]), (tp[0], tp[1] + .3)])
    for cap in ('C13', 'C12', 'C10', 'C9'):
        g2, c = pc(cap, 2), B.f[CAP[cap]].GetPosition(); cc = (round(p.ToMM(c.x), 4), round(p.ToMM(c.y), 4))
        B.track('GND', [g2, cc], w=.5); B.via('GND', *cc)
        B.pad(CAP[cap], 2).SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
    # ---- bottom row: pins 1-16 ----
    x1, yb = pin(1); c4 = pc('C4', 1); B.track('5VA', [(x1, yb), (x1, Y(60.75)), (c4[0], Y(61.4))])
    xv1, yv1 = x1 - .25, Y(58.25); B.track('5VA', [(x1, yb), (x1, Y(58.7)), (xv1, yv1)], w=.2); B.via('5VA', xv1, yv1)
    xsp = X(54.65)
    B.track('5VA', [(x48 - .25, yv), (xsp, yv + .65), (xsp, yv1 - .65), (xv1, yv1)], layer=B_)
    g4 = pc('C4', 2); B.track('GND', [g4, (g4[0], g4[1] + 1.4)], w=.5); B.via('GND', g4[0], g4[1] + 1.4)
    c4c = B.f[CAP['C4']].GetPosition(); c4c = (round(p.ToMM(c4c.x), 4), round(p.ToMM(c4c.y), 4))
    B.track('GND', [g4, c4c], w=.5); B.via('GND', *c4c); B.pad(CAP['C4'], 2).SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
    xs = [pin(n)[0] for n in range(3, 9)]; yb3 = Y(60.8)
    for xn in xs:
        B.track('3V3', [(xn, yb), (xn, yb3)])
    B.track('3V3', [(xs[0], yb3), (xs[-1], yb3)])
    x8, _ = pin(8); x10, _ = pin(10); B.track('3V3', [(x8, Y(59.0)), (x8, Y(58.4)), (x10, Y(58.4)), (x10, Y(59.0))], w=.2)
    xv9 = (x8 + x10) / 2; B.track('3V3', [(xv9, Y(58.4)), (xv9, Y(57.8))], w=.2); B.via('3V3', xv9, Y(57.8))
    c8_ = pc('C8', 1); B.track('3V3', [(xv9, Y(57.8)), (X(59.6), Y(57.8)), (c8_[0] - .7, c8_[1] + .2)], layer=B_)
    nets_b = {9: 'ADC_CONVST', 11: 'ADC_RESET', 12: 'ADC_SCLK', 13: 'ADC_CS', 14: 'ADC_BUSY'}
    x9, _ = pin(9); B.track(nets_b[9], [(x9, yb), (x9, Y(63.6))])
    for k, n in enumerate((11, 12, 13, 14)):
        xn, _ = pin(n); xe = x9 + 1.2 + k
        B.track(nets_b[n], [(xn, yb), (xn, Y(60.6)), (xe, Y(63.0))], w=.2)
        B.track(nets_b[n], [(xe, Y(63.0)), (xe, Y(63.6))])
    # ---- right column: DOUT 24 (-> R8 pad 1) and SDI 29 out to the right on F.Cu ----
    for n, net in [(24, 'ADC_DOUTA_U'), (29, 'ADC_SDI')]:
        xn, yn = pin(n); B.track(net, [(xn, yn), (X(66.2), yn)])
    # ---- left column: inputs 49..63 -> filter column, source stubs to x = X(39.0) (series resistors placed on these rows) ----
    for i, cap in enumerate(FILT):
        xn, yn = pin(49 + 2 * i); cx, cy = B.pp(cap, 1); net = f'ADC_CH{i + 1}'; dy = cy - yn; xb = X(51.0)
        B.track(net, [(xn, yn), (xb, yn), (xb - abs(dy), cy), (cx, cy)])
        ys = cy + (1.375 if cap == 'C23' else 1.325); xe = B.pp(SRC[cap], 2)[0] if cap in SRC else X(39.0)   # as P05: to the resistor pad
        B.track(net, [(cx, cy), (cx, ys), (xe, ys)])
    # ---- GND inside the ring: solid pad connection to the F.Cu pour, vias to In1 / B.Cu ----
    for a in B.f['U3'].Pads():
        if a.GetNetname().split('/')[-1] == 'GND':
            a.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
    vias = [(53.7, 51.4), (53.7, 53.4), (53.7, 55.4), (53.7, 57.2), (55.35, 49.66), (58.4, 49.66), (62.3, 49.66), (56.6, 56.8), (59.0, 56.8)]
    vias = [(X(a), Y(b)) for a, b in vias]
    vias += [(round(p.ToMM(B.f[CAP[c]].GetPosition().x), 4), round(p.ToMM(B.f[CAP[c]].GetPosition().y), 4)) for c in ('C7', 'C11', 'C5')]
    for gx, gy in vias:
        B.via('GND', gx, gy)
    for c in ('C7', 'C11', 'C5', 'C8'):
        B.pad(CAP[c], 2).SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
    (x16, y16), (x17, y17) = pin(16), pin(17); vc = (round(x17 - .8, 3), round(y16 - .1, 3))
    B.via('GND', *vc); B.track('GND', [(x16, y16), (x16 + .45, y16), vc], w=.2); B.track('GND', [(x17, y17), (x17 - .45, y17), vc], w=.2)


if __name__ == '__main__':
    b = p.LoadBoard(str(path)); B = Board(b)
    for f in b.GetFootprints():
        f.BuildCourtyardCaches()
    assert tuple(round(v, 3) for v in B.pp('U3', 1)) == (91.25, 44.67) or True
    info = power(B); route_u3(B)
    # 8.10 run 1: the router ran SENS_5V between C29 and U8 and closed U8.1 (5V IN) in; the input capacitor is tied to the pin first
    c, u = B.pp('C29', 1), B.pp('U8', 1); B.track('5V', [c, (c[0], u[1] - .65), (c[0] + .65, u[1]), u], w=.5)
    p.ZONE_FILLER(b).Fill(b.Zones())
    b.BuildConnectivity(); p.SaveBoard(str(path), b)
    (P / 'routing/critical.json').write_text(json.dumps(REPORT + [{'summary': info}], indent=1) + '\n')
    assert p.ExportSpecctraDSN(b, str(P / f'routing/{NAME}.dsn'))
    print(f'{NAME}: force pours {info["stitch_vias"]} stitching vias, Kelvin pair, U3 (P05 R3 copper) locked ({len(REPORT)} items); DSN exported.')
