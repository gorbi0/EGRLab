"""P03 R6 (30.09, Ubuntu): GND fan-out before the router (STAN-PRAC proposal 2; the P02 R4 anchors, for every SMD GND pad).
With GND out of the router's net list the two pours made after the import did not reach about 60 GND pads squeezed between
signal pins (SOIC pins 1/4/7/10/13, caps, pull-downs): a pour cannot pass between 1.27 mm pads, and the tracks of the
neighbouring pins close the outer end. Every SMD GND pad now gets locked copper to a via before the DSN export, so the
B.Cu pour reaches it whatever the router does on F.Cu:
- SOIC-14: an F.Cu bar under the body (x = 0 of the footprint) joins the inner ends of all GND pads of the part, with two
  vias on the bar. Nothing else can use that F.Cu: 1.27 mm pitch leaves 0.67 mm between pads, a track needs 0.8 mm.
- SOT-23 GND pads: a straight stub to the nearest legal via position (the middle pin of a side, walled in by its neighbours).
- J_BP1..3: the odd-row GND pins joined by a comb on F.Cu under the connector body, vias at both ends (see below).
- 1206 GND pads only with EGRLAB_FANOUT=all: they sit at the outer end of the part, where the pours reach them; in the
  30.09 trials the 39 extra vias (row under J_BP1, between parts) cost the router 22-30 open signal connections instead of
  6-13 (E: IC-only fan-out, 50 open after 3 passes like the base run; B: all pads, 72).
Legal via: clearance of the other copper (0.25, PWR 0.30) + 0.05 mm from every pad (any net: no via under another pad),
track and via; >= 0.15 mm from its own pad (no via in pad); outside the rule areas (M3 zones, antenna, SD1) and the
courtyards of other parts (M1 and SD1 allowed: modules on headers); >= 1.0 mm from the board edge; >= 1.0 mm between
fan-out vias of different pads. Stubs (0.3 mm) keep the same clearances. Run after route_critical.py: exports the DSN
again (prepare_routing.py follows). Report: routing/fanout.json.
"""
from pathlib import Path
import pcbnew as p, json, math
P = Path(__file__).resolve().parents[1]
from board import NAME, JBP, PWR as PWR_NETS   # board values from board.py (script taken from P03 R6 via P09 R2)
path = P / f'eda/{NAME}.kicad_pcb'
from build_board import W, Hh as H
mm = p.FromMM; F, B = p.F_Cu, p.B_Cu
VIA_D, VIA_DRILL, TW, CLR, PWR_CLR, EXTRA, OWN_GAP, VIA_GAP, EDGE = .9, .4, .3, .25, .30, .05, .15, 1.0, 1.0
PWR = set(PWR_NETS)
import os
MODE = os.environ.get('EGRLAB_FANOUT', 'ic')    # 'ic' (default): SOIC bars + SOT-23 stubs; 'all': also every 1206 GND pad
PLANE = os.environ.get('EGRLAB_GND_MODE', 'plane') == 'plane'   # prepare_routing.py default: SOT-23 stubs only when GND is out of the router
MODULES = {'M1', 'SD1'}


def V(x, y):
    return p.VECTOR2I(mm(x), mm(y))


def tomm(v):
    return (p.ToMM(v.x), p.ToMM(v.y))


def fp2board(f, x, y):
    """Footprint-local mm -> board mm (as build_board.fp2board)."""
    a = math.radians(f.GetOrientationDegrees()); c = f.GetPosition()
    return (p.ToMM(c.x) + x * math.cos(a) + y * math.sin(a), p.ToMM(c.y) - x * math.sin(a) + y * math.cos(a))


def poly(item, layer):
    ps = p.SHAPE_POLY_SET(); item.TransformShapeToPolygon(ps, layer, 0, mm(.002), p.ERROR_OUTSIDE); return ps


def bbox(ps):
    r = ps.BBox(); return (p.ToMM(r.GetLeft()), p.ToMM(r.GetTop()), p.ToMM(r.GetRight()), p.ToMM(r.GetBottom()))


def clearance(net):
    return (PWR_CLR if net in PWR else CLR) + EXTRA


if __name__ == '__main__':
    b = p.LoadBoard(str(path)); gnd = b.FindNet('GND')
    fps = sorted(b.GetFootprints(), key=lambda f: f.GetReference())
    # obstacles per copper layer: (polygon, clearance mm, pad uuid or None)
    obst = {F: [], B: []}
    holes = []   # (x, y, radius) of every drilled pad: via copper >= 0.25 and via hole >= 0.3 from the hole edge
    for f in fps:
        for a in f.Pads():
            for L in (F, B):
                if a.IsOnLayer(L):
                    ps = poly(a, L); obst[L].append((ps, clearance(a.GetNetname()), a.m_Uuid.AsString(), bbox(ps)))
            if a.GetDrillSize().x > 0:
                holes.append((*tomm(a.GetPosition()), p.ToMM(a.GetDrillSize().x) / 2))
    for t in b.GetTracks():
        for L in (F, B):
            if isinstance(t, p.PCB_VIA) or t.GetLayer() == L:
                ps = poly(t, L); obst[L].append((ps, clearance(t.GetNetname()), None, bbox(ps)))
    rules = [z for z in b.Zones() if z.GetIsRuleArea()]
    yards = {f.GetReference(): f.GetCourtyard(p.F_CrtYd) for f in fps if f.GetReference() not in MODULES}
    added_vias = []   # (x, y, pad label)

    def near(c, R=7.0):
        return {L: [o for o in obst[L] if o[3][0] - R < c[0] < o[3][2] + R and o[3][1] - R < c[1] < o[3][3] + R] for L in (F, B)}

    LOCAL = {}

    def via_ok(q, own_pad, own_ref, label):
        x, y = q; ob = LOCAL['obst']
        if not (EDGE <= x <= W - EDGE and EDGE <= y <= H - EDGE):
            return False
        c = V(x, y); r = VIA_D / 2
        for L in (F, B):
            for ps, cl, uid, _ in ob[L]:
                need = OWN_GAP if uid == own_pad else cl
                if ps.Collide(c, mm(r + need)):
                    return False
        for hx, hy, hr in holes:
            if math.dist(q, (hx, hy)) < hr + max(r + CLR, VIA_DRILL / 2 + .3) + EXTRA:
                return False
        ring = [c] + [V(x + (r + EXTRA) * math.cos(k * math.pi / 8), y + (r + EXTRA) * math.sin(k * math.pi / 8)) for k in range(16)]
        if any(z.Outline().Contains(v) for z in rules for v in ring):
            return False
        if any(ref != own_ref and cy.Collide(c, mm(r)) for ref, cy in yards.items()):
            return False
        if any(math.dist(q, (vx, vy)) < VIA_GAP for vx, vy, lab in added_vias if lab != label):
            return False
        return True

    def stub_ok(a_xy, q, layer, own_pads, extra=EXTRA):
        s = p.SEG(V(*a_xy), V(*q))
        for ps, cl, uid, _ in LOCAL['obst'][layer]:
            if uid in own_pads:
                continue
            if ps.Collide(s, mm(cl - EXTRA + extra + TW / 2)):
                return False
        n = max(2, int(math.dist(a_xy, q) / .05))
        pts = [V(a_xy[0] + (q[0] - a_xy[0]) * k / n, a_xy[1] + (q[1] - a_xy[1]) * k / n) for k in range(n + 1)]
        return not any(z.Outline().Contains(v) for z in rules for v in pts)

    def track(a, c, layer=F):
        t = p.PCB_TRACK(b); t.SetStart(V(*a)); t.SetEnd(V(*c)); t.SetWidth(mm(TW)); t.SetLayer(layer); t.SetNet(gnd); t.SetLocked(True); b.Add(t)
        ps = poly(t, layer); obst[layer].append((ps, CLR + EXTRA, 'fanout', bbox(ps)))

    def via(q, label):
        v = p.PCB_VIA(b); v.SetPosition(V(*q)); v.SetWidth(mm(VIA_D)); v.SetDrill(mm(VIA_DRILL)); v.SetViaType(p.VIATYPE_THROUGH)
        v.SetLayerPair(F, B); v.SetNet(gnd); v.SetLocked(True); b.Add(v); added_vias.append((*q, label))

    report = {'soic_bars': {}, 'stubs': {}, 'failed': []}
    for f in fps:
        ref = f.GetReference(); name = f.GetFPID().GetLibItemName().wx_str()
        pads = [a for a in f.Pads() if a.GetNetname() == 'GND' and a.GetAttribute() == p.PAD_ATTRIB_SMD]
        if not pads:
            continue
        assert all(a.IsOnLayer(F) for a in pads), (ref, 'SMD GND pad on the bottom: fan-out not written for it')
        if MODE == 'ic' and not (name.startswith('SOIC') or name.startswith('SOT')):
            continue   # passives: their GND pads sit at the outer end of the part, the pours reach them
        if PLANE and name.startswith('SOT'):
            continue   # 30.09: with the GND plane the router joins these pins; a pre-placed via ended in a cut-off pour piece in 4 of 6 failed runs
        if name.startswith('SOIC-14'):
            loc = sorted(((p.ToMM(a.GetFPRelativePosition().x), p.ToMM(a.GetFPRelativePosition().y), a) for a in pads), key=lambda t: t[1])
            y0, y1 = loc[0][1], loc[-1][1]
            own = {a.m_Uuid.AsString() for *_, a in loc}; LOCAL['obst'] = near(tomm(f.GetPosition()), 9.0)
            # both bar ends first, then inwards in 0.1 mm steps, until each end has a legal via
            ends = []
            for ys in ([y0 + k * .1 for k in range(int((y1 - y0) / .2))], [y1 - k * .1 for k in range(int((y1 - y0) / .2))]):
                q = next((fp2board(f, 0, yy) for yy in ys if via_ok(fp2board(f, 0, yy), None, ref, ref)), None)
                if q:
                    ends.append(q); via(q, ref)
            if not ends:
                report['failed'].append(ref + ' bar'); continue
            track(fp2board(f, 0, y0), fp2board(f, 0, y1))
            for x, y, a in loc:
                track(tomm(a.GetPosition()), fp2board(f, 0, y))
            report['soic_bars'][ref] = {'pads': sorted(a.GetNumber() for *_, a in loc), 'vias': [[round(u, 3) for u in q] for q in ends]}
            continue
        for a in sorted(pads, key=lambda a: a.GetNumber()):
            label = f'{ref}.{a.GetNumber()}'; c = tomm(a.GetPosition()); fc = tomm(f.GetPosition())
            outward = math.dist(c, fc); LOCAL['obst'] = near(c)
            cand = []
            for i in range(-45, 46):
                for j in range(-45, 46):
                    q = (c[0] + i * .1, c[1] + j * .1); d = math.dist(q, c)
                    if d > 4.5:
                        continue
                    cand.append((d + (.6 if math.dist(q, fc) < outward else 0), round(q[0], 3), round(q[1], 3)))
            cand.sort()
            q = next(((x, y) for _, x, y in cand if via_ok((x, y), a.m_Uuid.AsString(), ref, label) and stub_ok(c, (x, y), F, {a.m_Uuid.AsString()})), None)
            if q is None:
                report['failed'].append(label); continue
            track(c, q); via(q, label)
            report['stubs'][label] = {'via': [round(q[0], 3), round(q[1], 3)], 'stub_mm': round(math.dist(c, q), 2)}
    # ---- J_BP GND comb (default; EGRLAB_JBP_COMB=0 switches it off): the odd-row GND pins of each edge-A connector joined on F.Cu under the connector
    # body (y = RAIL_Y, between edge A and the even row), each by a 0.3 mm stub through the even-row gap on its right; vias at
    # both rail ends. The signals of the even row leave southwards through the odd-row gaps; in E2 (30.09) the router turned
    # them sideways right below the odd row on both layers and cut 13 GND pins of J_BP1/J_BP2 off the pours (J_BP2: the
    # antenna keepout below the band has no copper at all). In the six trial runs with the comb (30.09) no J_BP GND pin was cut off.
    if os.environ.get('EGRLAB_JBP_COMB', '1') == '1':
        RAIL_Y = 8.0; report['jbp_comb'] = {}
        for ref in JBP:
            f = next(g for g in fps if g.GetReference() == ref)
            gp = sorted((a for a in f.Pads() if a.GetNetname() == 'GND'), key=lambda a: a.GetPosition().x)
            xs = [p.ToMM(a.GetPosition().x) for a in f.Pads()]; LOCAL['obst'] = near(((min(xs) + max(xs)) / 2, 10.0), 26.0)
            tops = []
            for a in gp:
                x, y = tomm(a.GetPosition()); gx = round(x + 1.27, 3)
                pts = [(x, y), (gx, round(y - 1.27, 3)), (gx, RAIL_Y)]
                if all(stub_ok(u, v, F, {a.m_Uuid.AsString()}, extra=0.0) for u, v in zip(pts, pts[1:])):
                    for u, v in zip(pts, pts[1:]):
                        track(u, v, F)
                    tops.append(gx)
                else:
                    report['failed'].append(f'{ref}.{a.GetNumber()} comb')
            if not tops:
                continue
            ends = []
            for xe, step in ((min(tops) - 1.5, -.1), (max(tops) + 1.5, .1)):
                q = next(((round(xe + k * step, 3), RAIL_Y) for k in range(30) if via_ok((round(xe + k * step, 3), RAIL_Y), None, ref, ref + str(step))), None)
                if q is None:
                    report['failed'].append(f'{ref} comb via {xe:.1f}'); q = (round(xe, 3), RAIL_Y)
                else:
                    via(q, ref + str(step))
                ends.append(q)
            track(ends[0], ends[1], F)
            report['jbp_comb'][ref] = {'pins': [a.GetNumber() for a in gp], 'rail_x': [ends[0][0], ends[1][0]], 'rail_y': RAIL_Y}
    b.BuildConnectivity(); p.SaveBoard(str(path), b)
    assert p.ExportSpecctraDSN(b, str(P / f'routing/{NAME}.dsn'))
    report['vias'] = len(added_vias)
    (P / 'routing/fanout.json').write_text(json.dumps(report, indent=1) + '\n')
    longest = sorted(report['stubs'].items(), key=lambda kv: -kv[1]['stub_mm'])[:5]
    print(f"GND fan-out: {len(report['soic_bars'])} SOIC bars, {len(report['stubs'])} stubs, {len(added_vias)} vias; failed: {report['failed'] or 'none'}; "
          f"longest stubs: {[(k, v['stub_mm']) for k, v in longest]}; DSN exported again.")
