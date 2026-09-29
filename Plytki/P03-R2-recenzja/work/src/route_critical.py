"""P03 R2: supply feed and decoupling stubs locked before autorouting.
- 5V_SYS (1.0 mm, F.Cu): J10.1 (LV03 pin 1) -> M1.J1-21, kept left of the LV03 tie band and clear of the anchor holes;
  stub J10.1 -> TP1.
- 100 nF decoupling (0.6 mm, F.Cu): every IC supply pin -> pad 1 of its capacitor, straight or with one 45-degree bend;
  of the two possible bends the one with more clearance to the other pads is used.
- GND of every decoupling capacitor: 0.6 mm stub from pad 2 to a locked via 2.2 mm further out, so both pours reach the
  capacitor even where routed tracks surround its pad (first P03 routing left C5.2 cut off from the pour).
Every stub ends on a pad centre (Freerouting does not see a stub ending in the middle of a segment).
Freerouting routes the rest; GND is made by the two pours after import.
"""
from pathlib import Path
import pcbnew as p, math
P = Path(__file__).resolve().parents[1]; path = P / 'eda/P03.kicad_pcb'; b = p.LoadBoard(str(path))
mm = p.FromMM; F = p.F_Cu


def xy(x, y):
    return p.VECTOR2I(mm(x), mm(y))


def net(n):
    hits=[v for v in b.GetNetsByNetcode().values() if v.GetNetname().split('/')[-1]==n and v.GetNetCode()>0]
    if len(hits)==1:return hits[0]
    raise KeyError(n)


fmap = {f.GetReference(): f for f in b.GetFootprints()}


def pc(ref, num):
    v = next(a for a in fmap[ref].Pads() if a.GetNumber() == num).GetPosition(); return (p.ToMM(v.x), p.ToMM(v.y))


def tr(n, pts, w, layer=F):
    for a, c in zip(pts, pts[1:]):
        t = p.PCB_TRACK(b); t.SetStart(xy(*a)); t.SetEnd(xy(*c)); t.SetWidth(mm(w)); t.SetLayer(layer); t.SetNet(net(n)); t.SetLocked(True); b.Add(t)


def seg_dist(q, a, c):
    ax, ay = a; cx, cy = c; dx, dy = cx - ax, cy - ay; L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((q[0] - ax) * dx + (q[1] - ay) * dy) / L))
    return math.dist(q, (ax + t * dx, ay + t * dy))


OTHER = [(p.ToMM(a.GetPosition().x), p.ToMM(a.GetPosition().y), p.ToMM(max(a.GetSize(F).x, a.GetSize(F).y)) / 2, a.GetNetname().split('/')[-1])
         for f in b.GetFootprints() for a in f.Pads() if a.IsOnLayer(F)]


def clearance(pts, n, w):
    return min(seg_dist((x, y), a, c) - r - w / 2 for a, c in zip(pts, pts[1:]) for x, y, r, nn in OTHER if nn != n)


def stub(n, a, c, w=.6):
    dx, dy = c[0] - a[0], c[1] - a[1]
    if abs(dx) < 1e-6 or abs(dy) < 1e-6:
        opts = [[a, c]]
    else:
        k = min(abs(dx), abs(dy)); sx, sy = math.copysign(1, dx), math.copysign(1, dy)
        opts = [[a, (a[0] + sx * k, a[1] + sy * k), c], [a, (c[0] - sx * k, c[1] - sy * k), c]]
    best = max(opts, key=lambda o: clearance(o, n, w)); cl = clearance(best, n, w)
    assert cl >= .3, (n, a, c, round(cl, 3))
    tr(n, [tuple(round(v, 4) for v in q) for q in best], w)
    return round(cl, 2)


# R2 supply path has no direct SYS->M1 copper; the PMOS is between the two nets.
tr('5V_SYS', [pc('J10','1'), (44,12.5), (59,12.5), (62,9.5), (67,9.5), (67,18), pc('Q1','3')], 1.0)
tr('5V_SYS', [pc('J10','1'), pc('TP1','1')], 1.0)
tr('5V_M1', [pc('Q1','2'), (61.5,18.95), (58,22.45), (58,24), (37.5,24), (37.5,5.95), pc('M1','J1-21')], 1.0)
tr('GND',[pc('TP6','1'),pc('J10','4')],.6)

def gnd_via(c):
    """Locked GND via 2.2 mm beyond pad 2 of a decoupling capacitor (outwards along its axis, else sideways), joined by
    a short 0.6 mm track: both pours reach the capacitor even if routed tracks enclose its pad (P03 R2: C5.2 was cut off)."""
    a, g = pc(c, '1'), pc(c, '2'); ux, uy = (g[0] - a[0]) / math.dist(a,g), (g[1] - a[1]) / math.dist(a,g)
    for dx, dy in [(ux, uy), (-uy, ux), (uy, -ux)]:
        q = (round(g[0] + 2.2 * dx, 4), round(g[1] + 2.2 * dy, 4))
        cl = min(math.dist(q, (x, y)) - r - .5 for x, y, r, nn in OTHER if nn != 'GND')
        edge = min(q[0], 160 - q[0], q[1], 120 - q[1]) - .5
        if cl >= .35 and edge >= .5 and not any(z.GetIsRuleArea() and z.Outline().Contains(xy(*q)) for z in b.Zones()):
            v = p.PCB_VIA(b); v.SetPosition(xy(*q)); v.SetWidth(mm(1.0)); v.SetDrill(mm(.5)); v.SetViaType(p.VIATYPE_THROUGH)
            v.SetLayerPair(F, p.B_Cu); v.SetNet(net('GND')); v.SetLocked(True); b.Add(v)
            tr('GND', [g, q], .6)
            return round(cl, 2)
    raise AssertionError(('no room for the GND via of', c))


report, vias = {}, {}
for c, u, un in [('C5', 'U11', '14'), ('C6', 'U12', '14'), ('C7', 'U13', '14'), ('C8', 'U14', '14'), ('C9', 'U21', '14'), ('C10', 'U22', '14'),
                 ('C11', 'U23', '14'), ('C2', 'U1', '9'), ('C1', 'U2', '16'), ('C3', 'U3', '6')]:
    report[f'{u}.{un}-{c}.1'] = stub('3V3_CORE', pc(u, un), pc(c, '1'))
    vias[c] = gnd_via(c)
# Short 1206 bypass at the reset buffer; its GND is also tied to both planes.
report['U4.5-C12.1'] = stub('3V3_CORE',pc('U4','5'),pc('C12','1'),.6)
vias['C12'] = gnd_via('C12')

# Source termination stubs, before any long interconnect. Frozen independently of autorouter.
for r,u,pn,n in [('R36','U21','6','ADC_SCLK_DRV'),('R37','U21','11','ADC_CONVST_DRV'),
                 ('R38','U23','3','SPI3_SCLK_DRV'),('R39','U21','8','ADC_SDI_DRV')]:
    report[n]=stub(n,pc(u,pn),pc(r,'1'),.3)
tr('SPI3_MOSI_DRV',[pc('U23','6'),(60.05,78.7),(62.75,78.7),(65.45,76),pc('R40','1')],.3)

ds = b.GetDesignSettings().m_NetSettings.GetDefaultNetclass(); ds.SetClearance(mm(.25)); ds.SetTrackWidth(mm(.3)); ds.SetViaDiameter(mm(.8)); ds.SetViaDrill(mm(.4))
b.BuildConnectivity(); p.SaveBoard(str(path), b)
(P / 'routing').mkdir(exist_ok=True)
assert p.ExportSpecctraDSN(b, str(P / 'routing/P03.dsn'))
print('5V_SYS feed,', len(report), 'decoupling stubs and', len(vias), 'capacitor GND vias locked (min clearance to other pads, mm):', report, vias, '; DSN exported.')
