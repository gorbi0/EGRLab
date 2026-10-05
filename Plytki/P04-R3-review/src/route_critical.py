"""P04 R3: locked copper before the router (P04 R2.2 route_critical.py idea, rewritten for the S1 board). Run after build_board.py /
set_rules.py; fanout_gnd.py follows (it exports the DSN again). Report: routing/critical.json.
1. Supply escapes of the J_BP supply pins, 0.4 mm (board.PWR_W; task 5.10: P04_3V3, 5V_SYS, PANEL_3V3 >= 0.4 mm, 3V3_IO in the same class).
   The even IDC row (y 10.79) sits between edge A and the GND row (y 13.33): 0.84 mm between GND pads takes a 0.3 mm track, not
   0.4, and F.Cu under the connector holds the GND comb (fanout_gnd.py). So J_BP2.10 (3V3_IO), J_BP2.14 (P04_3V3), J_BP3.8 (5V_SYS) and
   J_BP3.10 (3V3_IO) leave on B.Cu towards edge A, run under the connector body (lanes y 5.0-6.5, below the comb vias at y 8) to its
   end and up; J_BP2.10 ends on the bulk capacitor C3 (THT), the others in a via at y 16.6 and on F.Cu to their resistor.
   J_BP1.2 (PANEL_3V3, end pin) leaves on F.Cu round pin 1 to R40.
2. SUP_N_OUT (reset from P03, KONTRAKT-RESET): J_BP3.12 -> B.Cu between the GND pins 9 / 11 -> via -> F.Cu to U9.5 directly
   below (README: short, GND beside it).
3. Watchdog timing (P04 R2.2, MECHANIKA): WD_RC U1.15 -> C1.1 and R1.2 -> C1.1, WD_C U1.14 -> C1.2, F.Cu, no vias.
4. Decoupling: 3V3_IO from the supply pin of every IC to its 100 nF (board.DEC_CAPS), F.Cu 0.4 mm, straight or one 45 deg jog;
   a link that would touch copper of another net is left to the router (listed in the report).
5. GND spines of the DIP decoupling (board.DIP_SPINES): capacitor GND pad -> via 1.2 mm above the pin row on the body centre line ->
   B.Cu 0.4 mm down the centre line -> 45 deg to the GND pin 7 / 8 (run 3: returns through the cut B.Cu plane 35-130 mm).
Every locked track is checked against the copper of other nets (clearance 0.25 mm + half width) and the rule areas; a collision in
steps 1-3 stops the script (placement and coordinates belong together).
"""
from pathlib import Path
import pcbnew as p, json, math, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from board import NAME, PWR_W, SIGNAL_W, DEC_CAPS
P = Path(__file__).resolve().parents[1]; fn = P / f'eda/{NAME}.kicad_pcb'
b = p.LoadBoard(str(fn)); mm = p.FromMM; F, B = p.F_Cu, p.B_Cu
f = {q.GetReference(): q for q in b.GetFootprints()}
CLR = .25
rules = [z for z in b.Zones() if z.GetIsRuleArea()]
report = {'escapes': {}, 'sup_n_out': None, 'watchdog': {}, 'decoupling': {}, 'decoupling_left_to_router': []}


def pad(ref, n):
    return next(q for q in f[ref].Pads() if q.GetNumber() == str(n))


def pxy(ref, n):
    v = pad(ref, n).GetPosition(); return (round(p.ToMM(v.x), 4), round(p.ToMM(v.y), 4))


def V(q):
    return p.VECTOR2I(mm(q[0]), mm(q[1]))


def net(name):
    ns = [n for n in b.GetNetsByNetcode().values() if n.GetNetname().split('/')[-1] == name]; assert len(ns) == 1, (name, len(ns)); return ns[0]


def obstacles(layer, netcode):
    out = []
    for g in b.GetFootprints():
        for a in g.Pads():
            if a.GetNetCode() != netcode and a.IsOnLayer(layer):
                ps = p.SHAPE_POLY_SET(); a.TransformShapeToPolygon(ps, layer, 0, mm(.005), p.ERROR_OUTSIDE); out.append(ps)
            if a.GetDrillSize().x > 0 and a.GetNetCode() != netcode:   # hole of any other pad
                pass
    for t in b.GetTracks():
        if t.GetNetCode() != netcode and (isinstance(t, p.PCB_VIA) or t.GetLayer() == layer):
            ps = p.SHAPE_POLY_SET(); t.TransformShapeToPolygon(ps, layer, 0, mm(.005), p.ERROR_OUTSIDE); out.append(ps)
    return out


def clash(pts, layer, w, netcode, vias=()):
    """First conflict of the polyline (and vias) with other-net copper, rule areas or the board edge, else None."""
    ob = obstacles(layer, netcode)
    for a, c in zip(pts, pts[1:]):
        s = p.SEG(V(a), V(c))
        for ps in ob:
            if ps.Collide(s, mm(CLR + w / 2 - .001)):
                return ('copper', a, c)
        n = max(2, int(math.dist(a, c) / .1))
        for k in range(n + 1):
            q = (a[0] + (c[0] - a[0]) * k / n, a[1] + (c[1] - a[1]) * k / n)
            if not (.5 + w / 2 <= q[0] <= 160 - .5 - w / 2 and .5 + w / 2 <= q[1] <= 100 - .5 - w / 2):
                return ('edge', q)
            if any(z.IsOnLayer(layer) and z.Outline().Contains(V(q)) for z in rules):
                return ('rule area', q)
    for q in vias:
        for L in (F, B):
            for ps in obstacles(L, netcode):
                if ps.Collide(V(q), mm(CLR + .45 - .001)):
                    return ('via copper', q)
    return None


def lock(netname, pts, layer, w, vias=(), must=True, label=None):
    n = net(netname); bad = clash(pts, layer, w, n.GetNetCode(), vias)
    if bad:
        assert not must, (label or netname, bad)
        return False
    for a, c in zip(pts, pts[1:]):
        if math.dist(a, c) < 1e-6:
            continue
        t = p.PCB_TRACK(b); t.SetStart(V(a)); t.SetEnd(V(c)); t.SetLayer(layer); t.SetWidth(mm(w)); t.SetNet(n); t.SetLocked(True); b.Add(t)
    for q in vias:
        v = p.PCB_VIA(b); v.SetPosition(V(q)); v.SetWidth(mm(.9)); v.SetDrill(mm(.4)); v.SetViaType(p.VIATYPE_THROUGH)
        v.SetLayerPair(F, B); v.SetNet(n); v.SetLocked(True); b.Add(v)
    return True


def length(pts):
    return round(sum(math.dist(a, c) for a, c in zip(pts, pts[1:])), 2)


# ---- 1. supply escapes ----
W_ = PWR_W
esc = []
j = pxy('J_BP1', 2); r40 = pxy('R40', 2)   # PANEL_3V3: F.Cu round pin 1 (x 15.4) to R40.2
pts = [j, (15.4, j[1]), (15.4, r40[1]), r40]; lock('PANEL_3V3', pts, F, W_, label='PANEL_3V3'); esc.append(('PANEL_3V3', 'J_BP1.2', pts, [], 'F.Cu'))
j = pxy('J_BP2', 10); c3 = pxy('C3', 1)    # 3V3_IO: B.Cu lane y 6.0 to x 66.9, up, to C3.1 (THT)
pts = [j, (j[0], 6.0), (66.9, 6.0), (66.9, 17.0), (c3[0], 17.0 + (66.9 - c3[0])), c3]; lock('3V3_IO', pts, B, W_, label='3V3_IO J_BP2'); esc.append(('3V3_IO', 'J_BP2.10', pts, [], 'B.Cu'))
j = pxy('J_BP2', 14); r39 = pxy('R39', 2); r60 = pxy('R60', 1)   # P04_3V3: B.Cu lane y 6.0 to x 93.1, up, via, F.Cu to R39.2 and R60.1
pts = [j, (j[0], 6.0), (93.1, 6.0), (93.1, 16.6)]; lock('P04_3V3', pts, B, W_, vias=[(93.1, 16.6)], label='P04_3V3')
top = [(93.1, 16.6), (r39[0], 16.6 + abs(r39[0] - 93.1)), r39, r60]; lock('P04_3V3', top, F, W_, label='P04_3V3 top')
esc.append(('P04_3V3', 'J_BP2.14', pts, top, 'B.Cu + via + F.Cu'))
j = pxy('J_BP3', 8); r57 = pxy('R57', 1)   # 5V_SYS: B.Cu lane y 6.5 to x 120.7, up, via, F.Cu to R57.1 (service pin only)
pts = [j, (j[0], 6.5), (120.7, 6.5), (120.7, 16.6)]; lock('5V_SYS', pts, B, W_, vias=[(120.7, 16.6)], label='5V_SYS')
top = [(120.7, 16.6), r57]; lock('5V_SYS', top, F, W_, label='5V_SYS top'); esc.append(('5V_SYS', 'J_BP3.8', pts, top, 'B.Cu + via + F.Cu'))
j = pxy('J_BP3', 10)                      # 3V3_IO: B.Cu lane y 5.0 to x 119.3, up, via (the router continues on either layer)
pts = [j, (j[0], 5.0), (119.3, 5.0), (119.3, 16.6)]; lock('3V3_IO', pts, B, W_, vias=[(119.3, 16.6)], label='3V3_IO J_BP3')
esc.append(('3V3_IO', 'J_BP3.10', pts, [], 'B.Cu + via'))
for netname, pin, a, c, lay in esc:
    report['escapes'][pin] = {'net': netname, 'layers': lay, 'width_mm': W_, 'length_mm': round(length(a) + length(c), 2)}
# ---- 2. SUP_N_OUT ----
j = pxy('J_BP3', 12); u = pxy('U9', 5); assert abs(j[0] - u[0]) < .01, (j, u)   # U9.5 straight below J_BP3.12 (placement.py)
gx = j[0] - 1.27                                                     # gap between the GND pins 9 and 11
bot = [j, (gx, j[1] + 1.27), (gx, 16.4)]; lock('SUP_N_OUT', bot, B, SIGNAL_W, vias=[(gx, 16.4)], label='SUP_N_OUT B')
topp = [(gx, 16.4), (u[0], 16.4 + 1.27), u]; lock('SUP_N_OUT', topp, F, SIGNAL_W, label='SUP_N_OUT F')
report['sup_n_out'] = {'b_cu_mm': length(bot), 'f_cu_mm': length(topp), 'vias': 1}
# ---- 3. watchdog ----
u15, c11, u14, c12, r12 = pxy('U1', 15), pxy('C1', 1), pxy('U1', 14), pxy('C1', 2), pxy('R1', 2)
assert abs(u15[1] - c11[1]) < .01 and abs(r12[0] - c11[0]) < .01, (u15, c11, r12)
lock('WD_RC', [u15, c11], F, SIGNAL_W, label='WD_RC'); lock('WD_RC', [r12, c11], F, SIGNAL_W, label='WD_RC R1')
k = c12[1] - u14[1]; wdc = [u14, (c12[0] - k, u14[1]), c12]; lock('WD_C', wdc, F, SIGNAL_W, label='WD_C')
report['watchdog'] = {'WD_RC_mm': round(length([u15, c11]) + length([r12, c11]), 2), 'WD_C_mm': length(wdc)}
# ---- 4. decoupling ----
for cap, (ic, vcc, gnd) in DEC_CAPS.items():
    a = pxy(ic, vcc); c = pxy(cap, 1); assert pad(cap, 1).GetNetname() == '3V3_IO', cap
    dx, dy = c[0] - a[0], c[1] - a[1]; k = min(abs(dx), abs(dy))
    ways = [[a, c]] if k < .01 else [[a, (a[0] + math.copysign(k, dx), a[1] + math.copysign(k, dy)), c],
                                     [a, (c[0] - math.copysign(k, dx), c[1] - math.copysign(k, dy)), c]]
    for pts in ways:
        if lock('3V3_IO', pts, F, W_, must=False):
            report['decoupling'][cap] = {'ic_pin': f'{ic}.{vcc}', 'length_mm': length(pts)}; break
    else:
        report['decoupling_left_to_router'].append(cap)
# ---- 5. GND spines of the DIP decoupling (board.DIP_SPINES, run 3) ----
from board import DIP_SPINES
report['gnd_spines'] = {}
for cap, ic in DIP_SPINES.items():
    gpin = DEC_CAPS[cap][2]; g7 = pxy(ic, gpin); p1 = pxy(ic, 1); cg = pxy(cap, 2); assert pad(cap, 2).GetNetname() == 'GND' and pad(ic, gpin).GetNetname() == 'GND'
    xm = p1[0] + 3.81; v = (xm, p1[1] - 1.2)                               # via inside the courtyard, 1.2 mm above the pin row
    top = [cg, v]; lock('GND', top, F, .4, vias=[v], label=f'{cap} spine top')
    spine = [v, (xm, g7[1] - 3.81), g7]; lock('GND', spine, B, .4, label=f'{cap} spine')
    report['gnd_spines'][cap] = {'ic_pin': f'{ic}.{gpin}', 'length_mm': round(length(top) + length(spine), 2)}
b.BuildConnectivity(); p.SaveBoard(str(fn), b)
(P / 'routing').mkdir(exist_ok=True)
(P / 'routing/critical.json').write_text(json.dumps(report, indent=1) + '\n')
assert p.ExportSpecctraDSN(b, str(P / f'routing/{NAME}.dsn'))
print('locked: escapes', {k: v['length_mm'] for k, v in report['escapes'].items()}, '| SUP_N_OUT', report['sup_n_out'], '| watchdog', report['watchdog'],
      '| decoupling', len(report['decoupling']), 'locked, left to router:', report['decoupling_left_to_router'])
