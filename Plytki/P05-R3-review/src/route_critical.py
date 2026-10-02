"""P05 R3: locked copper at U1 (AD7606B, LQFP-64 0.5 mm) before the router, then the Specctra DSN export.
README layout requirements and review P5-01 (R2 pattern `Plytki/P05-R2-review/wip-layout-obrys-R1/`, adapted to 1206 / 1210 and S1):
- decoupling on the shortest copper: REGCAP_A 36 -> C9 and REGCAP_D 39 -> C10 (1 uF, top, <= 3 mm, no via), REFIN/OUT 42 -> C12
  (22 uF 1210, top, <= 6 mm) and -> C11 (100 nF, bottom, via inside the pad ring, <= 3 mm), REFCAP 44/45 -> C13 (22 uF 1210, top,
  <= 6 mm, no via: one 0.2 mm track along the pad tips under C12), AVCC 48 -> C7 and 37/38 -> C5 (100 nF, bottom, via inside the
  ring, <= 3 mm), AVCC 1 -> C4 (top, below the corner, <= 3 mm), VDRIVE 23 -> C8 (bottom, via inside, <= 4 mm);
- test pads TP2-TP5 on 0.3 mm stubs off the capacitor pads (never on the decoupling path; TP2 / TP4 through the 0.85 mm gaps);
- every GND pin of U1 connects inwards to the F.Cu pour inside the pad ring (solid pad connection), tied to B.Cu by 4 vias; the
  100 nF ground pads sit on the B.Cu pour under the body;
- inputs: 45 deg fan from the pins 49-63 to the filter column C27-C34 (pitch 2.65 mm) and a source stub from each capacitor pad
  through the gap below it to the left (input resistors or x = 39 for the router); DOUT leaves on F.Cu to the right (P5-01: not
  under U1 on B.Cu), the serial pins at the bottom diverge from 0.5 mm to a 1 mm pitch;
- 5VA_P05 of C7 / C5 leaves on B.Cu straight up between the top capacitors to a join above them, fed by C6 (review 2.10: was a
  0.5 mm bar across the returns at y 45 and a spine under the input pins), 3V3_DAQ of VDRIVE / REFSEL (pins 23 / 34, C8) on B.Cu to
  x 66.2, the strap pins 3-8 on an F.Cu bar below the pins (10 joined inside the ring around pin 9, via there to C8);
- review 2.10 (MAJOR-1): GND vias under the top capacitors' bodies, at the AGND / REFGND pins, between the pads of each bottom 100 nF,
  a column inside the left pins and one at the pin 16 / 17 corner on C8; decoupling GND pads with solid pour connection.
Clearances inside the U1 courtyard: custom rules of set_rules.py (0.15 / track 0.2 only between items both touching it).
"""
from pathlib import Path
import pcbnew as p, sys, json
sys.path.insert(0, str(Path(__file__).resolve().parent))
from board import NAME
P = Path(__file__).resolve().parents[1]; path = P / f'eda/{NAME}.kicad_pcb'
REPORT = []


def xy(x, y):
    return p.VECTOR2I(p.FromMM(x), p.FromMM(y))


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

    def track(self, net, pts, w=.3, layer=p.F_Cu):
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if (round(x0, 4), round(y0, 4)) == (round(x1, 4), round(y1, 4)):
                continue
            t = p.PCB_TRACK(self.b); t.SetLayer(layer); t.SetWidth(p.FromMM(w)); t.SetStart(xy(x0, y0)); t.SetEnd(xy(x1, y1))
            t.SetNet(self.net(net)); t.SetLocked(True); self.b.Add(t)
        REPORT.append({'net': net, 'layer': 'F.Cu' if layer == p.F_Cu else 'B.Cu', 'width_mm': w, 'points_mm': [list(q) for q in pts]})

    def via(self, net, x, y):
        v = p.PCB_VIA(self.b); v.SetPosition(xy(x, y)); v.SetWidth(p.FromMM(.9)); v.SetDrill(p.FromMM(.4)); v.SetViaType(p.VIATYPE_THROUGH)
        v.SetLayerPair(p.F_Cu, p.B_Cu); v.SetNet(self.net(net)); v.SetLocked(True); self.b.Add(v)
        REPORT.append({'net': net, 'via_mm': [x, y]})


def route_u1(B):
    pin = lambda n: B.pp('U1', n)
    # ---- top row: supply / reference pins 33-48 (y 48.325) ----
    x36, y = pin(36); B.track('REGCAP_A', [(x36, y), (x36, 47.45), (x36 + .5, 46.95), (x36 + .5, 46.6)])     # -> C9 pad 1
    x39, _ = pin(39); B.track('REGCAP_D', [(x39, y), (x39, 46.6)])                                          # -> C10 pad 1
    x42, _ = pin(42); B.track('ADC_REF', [(x42, y), (x42, 46.5)])                                           # -> C12 pad 1 (right edge)
    x44, _ = pin(44); x45, _ = pin(45); yr = 47.225                                                          # REFCAP along the tips
    c13x, c13y = B.pp('C13', 1)
    B.track('REFCAP', [(x44, y), (x44, yr)], w=.2); B.track('REFCAP', [(x45, y), (x45, yr)], w=.2)
    B.track('REFCAP', [(x44, yr), (54.0, yr)], w=.2)                                                         # inside the courtyard
    B.track('REFCAP', [(54.0, yr), (c13x + .9, yr - .7)])   # x < 53.85: courtyard corner (body edge), S1 width -> C13 pad 1
    # inward vias of the bottom-side 100 nF: 48 (C7), 42 (C11), 37/38 (C5), 34 REFSEL (3V3_DAQ, to C8 / VDRIVE)
    yv = 49.75
    x48, _ = pin(48); B.track('5VA_P05', [(x48, y), (x48, 49.2), (x48 - .25, yv)], w=.2); B.via('5VA_P05', x48 - .25, yv)
    B.track('ADC_REF', [(x42, y), (x42, yv)], w=.2); B.via('ADC_REF', x42, yv)
    x37, _ = pin(37); x38, _ = pin(38); xm = (x37 + x38) / 2
    B.track('5VA_P05', [(x37, y), (x37, 49.3), (xm, yv)], w=.2); B.track('5VA_P05', [(x38, y), (x38, 49.3), (xm, yv)], w=.2)
    B.via('5VA_P05', xm, yv)
    x34, _ = pin(34); xv34, yv34 = x34 - .05, 49.66   # 2.10: 0.09 mm up / 0.05 left, clear of C5 moved right (pitch 2.35)
    B.track('3V3_DAQ', [(x34, y), (x34, 49.2), (xv34, yv34)], w=.2); B.via('3V3_DAQ', xv34, yv34)
    # bottom side: vias -> 100 nF pads 1; 5VA up to the bar under the top capacitors and out to x 51.2 (router); 3V3 -> VDRIVE
    for net, (vx, vy), cap in [('5VA_P05', (x48 - .25, yv), 'C7'), ('ADC_REF', (x42, yv), 'C11'), ('5VA_P05', (xm, yv), 'C5')]:
        B.track(net, [(vx, vy), B.pp(cap, 1)], layer=p.B_Cu)
    # review 2.10 (MAJOR-1): the 0.5 mm 5VA bar at y 45 crossed every return from the top capacitors to U1 and the spine at x 52.6 every
    # input return (B.Cu). Now two 0.3 mm stubs run straight up between the capacitors (parallel to the returns) to a join above their
    # GND vias, fed by C6 through a via; AVCC 1 joins pin 48 by a spine inside the pad ring (x 54.65), east of the GND via column.
    xs48, xs37, yj = x48 - .25, 60.1, 41.9
    c6 = B.pp('C6', 1)
    B.track('5VA_P05', [(xs48, yv), (xs48, yj)], layer=p.B_Cu)
    B.track('5VA_P05', [(xm, yv), (xs37, yv - .6), (xs37, yj)], layer=p.B_Cu)
    B.track('5VA_P05', [(xs48, yj), (xs37, yj)], layer=p.B_Cu)
    B.via('5VA_P05', c6[0], yj); B.track('5VA_P05', [(c6[0], yj), c6])                                       # -> C6 pad 1 (router on from C6)
    x23, y23 = pin(23); xv23 = 62.25
    B.track('3V3_DAQ', [(x23, y23), (xv23, y23)], w=.2); B.via('3V3_DAQ', xv23, y23)
    c8 = B.pp('C8', 1)
    B.track('3V3_DAQ', [(xv34, yv34), (xv34 + .65, yv34 + .65), (xv34 + .65, y23 - .6), (xv23, y23)], layer=p.B_Cu)
    B.track('3V3_DAQ', [(xv23, y23), (c8[0], c8[1] - .4)], layer=p.B_Cu)
    B.track('3V3_DAQ', [(c8[0] + .6, c8[1]), (66.2, c8[1])], layer=p.B_Cu)                                 # router continues
    # test pads on stubs (0.3 mm, S1) off the capacitor pads 1
    c12 = B.pp('C12', 1); tp2 = B.pp('TP2', 1); B.track('ADC_REF', [(c12[0] - 1.05, c12[1]), (tp2[0], c12[1]), (tp2[0], tp2[1] + .3)])
    c10 = B.pp('C10', 1); tp4 = B.pp('TP4', 1); B.track('REGCAP_D', [(c10[0] + .6, c10[1]), (tp4[0], c10[1]), (tp4[0], tp4[1] + .3)])
    tp5 = B.pp('TP5', 1); B.track('REFCAP', [(c13x - 1.0, c13y), (c13x - 1.8, c13y), (tp5[0] + .7, tp5[1] + .6)])
    c9 = B.pp('C9', 1); tp3 = B.pp('TP3', 1); B.track('REGCAP_A', [(c9[0] + .65, c9[1]), (c9[0] + 1.85, c9[1]), (tp3[0] - .5, tp3[1] + .5)])
    # review 2.10 (MAJOR-1): GND via of each top capacitor under its body, between the pads (0.45 mm to each), on a 0.5 mm track from
    # pad 2: the return drops to B.Cu right under the supply path (before: beyond pad 2, behind the 5VA bar, 15-23 mm to U1's GND pins)
    for cap in ('C13', 'C12', 'C10', 'C9'):
        g2, c = B.pp(cap, 2), B.f[cap].GetPosition(); cc = (round(p.ToMM(c.x), 4), round(p.ToMM(c.y), 4))
        B.track('GND', [g2, cc], w=.5); B.via('GND', *cc)
        B.pad(cap, 2).SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
    # ---- bottom row: pins 1-16 (y 59.675) ----
    x1, yb = pin(1); c4 = B.pp('C4', 1); B.track('5VA_P05', [(x1, yb), (x1, 60.75), (c4[0], 61.4)])                    # -> C4 pad 1
    # AVCC 1 joins the other AVCC pins on B.Cu (run 2: the router took a 0.6 mm 5VA track across the inner GND pour): via V1 inside the
    # ring next to pin 1, B.Cu along the left pad row to V48 (C7 / the 5VA bar)
    xv1, yv1 = x1 - .25, 58.25; B.track('5VA_P05', [(x1, yb), (x1, 58.7), (xv1, yv1)], w=.2); B.via('5VA_P05', xv1, yv1)
    xsp = 54.65   # inner spine: 0.2 mm off C7 (x >= 54.85 after placement 2.10), 0.35 mm off the GND via column at x 53.7
    B.track('5VA_P05', [(x48 - .25, yv), (xsp, yv + .65), (xsp, yv1 - .65), (xv1, yv1)], layer=p.B_Cu)
    g4 = B.pp('C4', 2); B.track('GND', [g4, (g4[0], g4[1] + 1.4)], w=.5); B.via('GND', g4[0], g4[1] + 1.4)
    c4c = B.f['C4'].GetPosition(); c4c = (round(p.ToMM(c4c.x), 4), round(p.ToMM(c4c.y), 4))                  # and under its body
    B.track('GND', [g4, c4c], w=.5); B.via('GND', *c4c); B.pad('C4', 2).SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
    xs = [pin(n)[0] for n in range(3, 9)]; yb3 = 60.8   # bar edge 60.65 inside the courtyard (y <= 60.7 along the pad rows)
    for xn in xs:
        B.track('3V3_DAQ', [(xn, yb), (xn, yb3)])
    B.track('3V3_DAQ', [(xs[0], yb3), (xs[-1], yb3)])
    # run 3: the router left this group and the C8 group apart (both hemmed in by the U1 keepouts) -> joined here: via below the bar,
    # B.Cu to C8 pad 1; the only 3V3 exit of U1 is the B.Cu stub of C8 to x 66.2
    x8, _ = pin(8); x10, _ = pin(10); B.track('3V3_DAQ', [(x8, 59.0), (x8, 58.4), (x10, 58.4), (x10, 59.0)], w=.2)  # 10 around 9
    # review 2.10 (MAJOR-1): the strap group took 3V3 through a via below the bar and a B.Cu L along y 61.8 / x 60.3 that walled C8's
    # GND pad in (23 mm to AGND 26); now a via on the loop round pin 9 and 4 mm of B.Cu inside the ring to C8 pad 1
    xv9 = (x8 + x10) / 2; B.track('3V3_DAQ', [(xv9, 58.4), (xv9, 57.8)], w=.2); B.via('3V3_DAQ', xv9, 57.8)
    c8_ = B.pp('C8', 1); B.track('3V3_DAQ', [(xv9, 57.8), (59.6, 57.8), (c8_[0] - .7, c8_[1] + .2)], layer=p.B_Cu)
    nets_b = {9: 'ADC_CONVST_P05', 11: 'ADC_RESET_P05', 12: 'ADC_SCLK_P05', 13: 'ADC_CS_P05', 14: 'AD_BUSY_LOCAL'}
    x9, _ = pin(9); B.track(nets_b[9], [(x9, yb), (x9, 63.6)])
    for k, n in enumerate((11, 12, 13, 14)):   # diverge from 0.5 to 1.0 mm inside / just outside the courtyard
        xn, _ = pin(n); xe = x9 + 1.2 + k
        B.track(nets_b[n], [(xn, yb), (xn, 60.6), (xe, 63.0)], w=.2)   # starts inside the courtyard: fine-pitch rule
        B.track(nets_b[n], [(xe, 63.0), (xe, 63.6)])
    # ---- right column: DOUT 24 and SDI 29 out to the right on F.Cu ----
    for n, net in [(24, 'AD_DOUT_LOCAL'), (29, 'ADC_SDI_P05')]:
        xn, yn = pin(n); B.track(net, [(xn, yn), (66.2, yn)])
    # ---- left column: inputs 49..63 -> filter column, source stubs ----
    src = {'C27': ('R28', '1'), 'C28': ('R29', '1'), 'C32': ('R30', '1'), 'C33': ('R31', '2'), 'C34': ('R33', '2')}
    stub_dy = {c: (1.375 if c == 'C32' else 1.325) for c in ('C27', 'C28', 'C29', 'C30', 'C31', 'C32', 'C33', 'C34')}
    for i, cap in enumerate(('C27', 'C28', 'C29', 'C30', 'C31', 'C32', 'C33', 'C34')):
        xn, yn = pin(49 + 2 * i); cx, cy = B.pp(cap, 1); net = f'ADC_CH{i + 1}'; dy = cy - yn; xb = 51.0
        B.track(net, [(xn, yn), (xb, yn), (xb - abs(dy), cy), (cx, cy)])
        ys = cy + stub_dy[cap]; xe = B.pp(*src[cap])[0] if cap in src else 39.0
        B.track(net, [(cx, cy), (cx, ys), (xe, ys)])
    # ---- GND inside the ring: solid pad connection to the F.Cu pour, 4 vias to B.Cu ----
    for a in B.f['U1'].Pads():
        if a.GetNetname().split('/')[-1] == 'GND':
            a.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
    # review 2.10 (MAJOR-1 / -2): 4 vias tied the inner pour to B.Cu, all at y >= 52.6. Now: a column just inside the left pins (x 53.7,
    # the input returns climb here from B.Cu instead of going round a spine), two at the top-row AGND / REFGND pins (y 49.66), one under
    # each bottom 100 nF between its pads, two more in the lower half, and one at the pin 16 / 17 corner on C8's GND pad (both pins GND)
    vias = [(53.7, 51.4), (53.7, 53.4), (53.7, 55.4), (53.7, 57.2), (55.35, 49.66), (58.4, 49.66), (62.3, 49.66),
            (56.6, 56.8), (59.0, 56.8)]
    vias += [(round(p.ToMM(B.f[c].GetPosition().x), 4), round(p.ToMM(B.f[c].GetPosition().y), 4)) for c in ('C7', 'C11', 'C5')]
    for gx, gy in vias:
        B.via('GND', gx, gy)
    for c in ('C7', 'C11', 'C5', 'C8'):
        B.pad(c, 2).SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
    (x16, y16), (x17, y17) = pin(16), pin(17); vc = (round(x17 - .8, 3), round(y16 - .1, 3))
    B.via('GND', *vc); B.track('GND', [(x16, y16), (x16 + .45, y16), vc], w=.2); B.track('GND', [(x17, y17), (x17 - .45, y17), vc], w=.2)


def route_u3(B):
    """U3 TLV1702 (VSSOP-8, 0.65 mm): neither the router nor the completion planner (S1 widths) reaches its pins. Under the body: RAIL_SENSE
    3 <-> 6 and DAQ_RAIL_N 1 <-> 7 (no exposed pad); outwards 0.3 mm stubs 0.7 mm beyond the courtyard (pins 1, 2, 3 left, 8, 5 right; the
    router continues at 0.65 mm pitch), GND pin 4 to its own via."""
    pin = lambda n: B.pp('U3', n)
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = pin(1), pin(2), pin(3), pin(4)
    (x5, y5), (x6, y6), (x7, y7), (x8, y8) = pin(5), pin(6), pin(7), pin(8)
    B.track('RAIL_SENSE', [(x3, y3), (x6, y6)])
    B.track('DAQ_RAIL_N', [(x1, y1), (x1 + 1.2, y1), (x7 - 1.2, y7), (x7, y7)])
    xl, xr = x1 - 1.8, x8 + 1.8
    for (x, y), net in [((x1, y1), 'DAQ_RAIL_N'), ((x2, y2), 'RAIL_LOW'), ((x3, y3), 'RAIL_SENSE')]:
        B.track(net, [(x, y), (xl, y)])
    B.track('GND', [(x4, y4), (xl, y4), (xl - .6, y4 + .6)]); B.via('GND', xl - .6, y4 + .6)
    for (x, y), net in [((x8, y8), '5V_SYS'), ((x5, y5), 'RAIL_HIGH')]:
        B.track(net, [(x, y), (xr, y)])


if __name__ == '__main__':
    b = p.LoadBoard(str(path)); B = Board(b)
    route_u1(B); route_u3(B)
    b.BuildConnectivity(); p.SaveBoard(str(path), b)
    (P / 'routing').mkdir(exist_ok=True)
    (P / 'routing/critical.json').write_text(json.dumps(REPORT, indent=1) + '\n')
    assert p.ExportSpecctraDSN(b, str(P / f'routing/{NAME}.dsn'))
    print(f'{NAME}: U1 decoupling, escapes and input fan locked ({len(REPORT)} items); DSN exported.')
