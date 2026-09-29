"""P05 R2: close the links broken by the local change (seed_r1.py) with audited, locked completion tracks.
--plan: native DRC (zones refilled) lists unconnected pairs; each pair gets a raster A* path (planner of
        complete_routes.py, generalised from pad-pad to item-item points and to a track width per net),
        repeated until DRC reports none. Paths are stored in routing/completion-routes-r2.json.
default: replay routing/completion-routes-r2.json (deterministic rebuild).
Native KiCad DRC is authoritative; the raster only proposes copper."""
from pathlib import Path
import pcbnew as p, json, heapq, sys, os, subprocess, math
from PIL import Image, ImageDraw
import numpy as np
P = Path(__file__).resolve().parents[1]; fn = P / 'eda/P05.kicad_pcb'; mm = p.FromMM
CLI = os.environ.get('KICAD_CLI', str(Path(sys.executable).with_name('kicad-cli.exe')))
R = 20; W = 160 * R; H = 120 * R
WIDTH = {'5V_SYS': .3, '5VA_P05': .3, '3V3_DAQ': .25}
target = P / 'routing/completion-routes-r2.json'


def drawpoly(d, ps):
    for k in range(ps.OutlineCount()):
        o = ps.Outline(k); d.polygon([(p.ToMM(o.CPoint(i).x) * R, p.ToMM(o.CPoint(i).y) * R) for i in range(o.PointCount())], fill=255)


def dilate(a, r):
    out = a.copy()
    for d in range(1, r + 1): out[d:, :] |= a[:-d, :]; out[:-d, :] |= a[d:, :]
    a = out.copy()
    for d in range(1, r + 1): out[:, d:] |= a[:, :-d]; out[:, :-d] |= a[:, d:]
    return out


def plan(b, net, s, sl, g, gl, w):
    code = b.FindNet(net).GetNetCode(); images = []
    for layer in [p.F_Cu, p.B_Cu]:
        im = Image.new('L', (W, H)); d = ImageDraw.Draw(im)
        for fp in b.GetFootprints():
            for q in fp.Pads():
                if q.GetNetCode() != code and q.IsOnLayer(layer):
                    # ground pads keep room for their thermal spokes (0.2 gap + 0.35 spoke), else the pour starves them
                    grow = .45 if q.GetNetname() == 'GND' and q.GetAttribute() == p.PAD_ATTRIB_PTH else .005
                    ps = p.SHAPE_POLY_SET(); q.TransformShapeToPolygon(ps, layer, mm(grow), mm(.005), p.ERROR_OUTSIDE); drawpoly(d, ps)
                if q.GetAttribute() in (p.PAD_ATTRIB_NPTH,) and q.GetNetCode() != code:
                    ps = p.SHAPE_POLY_SET(); q.TransformShapeToPolygon(ps, layer, 0, mm(.005), p.ERROR_OUTSIDE); drawpoly(d, ps)
        for t in b.GetTracks():
            if t.GetNetCode() != code and (isinstance(t, p.PCB_VIA) or t.GetLayer() == layer):
                ps = p.SHAPE_POLY_SET(); t.TransformShapeToPolygon(ps, layer, 0, mm(.005), p.ERROR_OUTSIDE); drawpoly(d, ps)
        for zone in b.Zones():
            if zone.GetIsRuleArea() and zone.IsOnLayer(layer) and zone.GetDoNotAllowTracks(): drawpoly(d, zone.Outline())
        d.rectangle([0, 0, W - 1, H - 1], outline=255, width=12)
        images.append(im)
    inf = int(math.ceil((w / 2 + .15) * R)) + 1
    obs = [dilate(np.array(im) != 0, inf) for im in images]
    via = dilate((np.array(images[0]) | np.array(images[1])) != 0, 9)
    S = tuple(round(v * R) for v in s); G = tuple(round(v * R) for v in g)
    def h(x, y): dx = abs(x - G[0]); dy = abs(y - G[1]); return max(dx, dy) + .41421356 * min(dx, dy)
    def key(x, y, l): return (l * H + y) * W + x
    starts = {key(*S, l) for l in sl}; todo = [(3 * h(*S), 0, q) for q in starts]; heapq.heapify(todo); cost = {q: 0 for q in starts}; prev = {}; end = None
    near = 0  # strict: a start/goal inside another net's keep-out has no route (its free stub is removed instead)
    while todo:
        _, dist, q = heapq.heappop(todo)
        if dist != cost.get(q): continue
        x = q % W; y = (q // W) % H; l = q // (W * H)
        if (x, y) == G and l in gl: end = q; break
        nxt = []
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < W and 0 <= ny < H): continue
            free = lambda X, Y: not obs[l][Y, X] or max(abs(X - S[0]), abs(Y - S[1])) <= near or max(abs(X - G[0]), abs(Y - G[1])) <= near
            if free(nx, ny) and free(nx, y) and free(x, ny): nxt.append((nx, ny, l, 1.41421356237 if dx and dy else 1))
        if not via[y, x]: nxt.append((x, y, 1 - l, 80))
        for nx, ny, nl, dc in nxt:
            nk = key(nx, ny, nl); nd = dist + dc
            if nd < cost.get(nk, 1e99): cost[nk] = nd; prev[nk] = q; heapq.heappush(todo, (nd + 3 * h(nx, ny), nd, nk))
    if end is None: return None
    path = []
    while True:
        path.append([end % W / R, ((end // W) % H) / R, end // (W * H)])
        if end in starts: break
        end = prev[end]
    path.reverse(); path = [[s[0], s[1], path[0][2]]] + path + [[g[0], g[1], path[-1][2]]]
    keep = [path[0]]
    for i in range(1, len(path) - 1):
        a, bb, c = keep[-1], path[i], path[i + 1]
        if a[2] == bb[2] == c[2] and abs((bb[0] - a[0]) * (c[1] - bb[1]) - (bb[1] - a[1]) * (c[0] - bb[0])) < 1e-7: continue
        if bb != keep[-1]: keep.append(bb)
    if path[-1] != keep[-1]: keep.append(path[-1])
    return keep


def add(b, net, points, w):
    n = b.FindNet(net)
    for a, c in zip(points, points[1:]):
        if a == c: continue
        if a[2] != c[2]:
            assert a[:2] == c[:2]; t = p.PCB_VIA(b); t.SetPosition(p.VECTOR2I(mm(a[0]), mm(a[1]))); t.SetWidth(mm(.6)); t.SetDrill(mm(.3))
            t.SetViaType(p.VIATYPE_THROUGH); t.SetLayerPair(p.F_Cu, p.B_Cu)
        else:
            t = p.PCB_TRACK(b); t.SetStart(p.VECTOR2I(mm(a[0]), mm(a[1]))); t.SetEnd(p.VECTOR2I(mm(c[0]), mm(c[1]))); t.SetWidth(mm(w)); t.SetLayer(p.F_Cu if a[2] == 0 else p.B_Cu)
        t.SetNet(n); t.SetLocked(True); b.Add(t)


def seg(t):
    return [int(t.GetLayer()), round(p.ToMM(t.GetWidth()), 4)] + sorted([[round(p.ToMM(v.x), 4), round(p.ToMM(v.y), 4)] for v in (t.GetStart(), t.GetEnd())])


def remove(b, t):
    t.SetWidth(0)  # marker: purge() drops zero-width segments on file level (pcbnew Remove() is unsafe)


def layers(b, uuid):
    for t in b.GetTracks():
        if t.m_Uuid.AsString() == uuid: return [0, 1] if isinstance(t, p.PCB_VIA) else [0 if t.GetLayer() == p.F_Cu else 1]
    for f in b.GetFootprints():
        for a in f.Pads():
            if a.m_Uuid.AsString() == uuid: return [l for l, L in ((0, p.F_Cu), (1, p.B_Cu)) if a.IsOnLayer(L)]
    raise KeyError(uuid)


def purge():
    # drop zero-width marked tracks on file level (see remove())
    from sexpr import parse, dump
    tree = parse(fn.read_text(encoding='utf-8'))
    def zero(g):
        if not (isinstance(g, list) and g and g[0] == 'segment'): return False
        w = next((x for x in g if isinstance(x, list) and x and x[0] == 'width'), None)
        return w is not None and float(w[1]) == 0
    fn.write_text(dump([g for g in tree if not zero(g)]) + '\n', encoding='utf-8')


if '--plan' in sys.argv:
    records = []
    for rnd in range(12):
        rep = P / 'routing/complete-drc.json'
        subprocess.run([CLI, 'pcb', 'drc', '--format', 'json', '--severity-all', '--refill-zones', '-o', str(rep), str(fn)], check=True, capture_output=True)
        pairs = json.loads(rep.read_text())['unconnected_items']
        if not pairs: break
        b = p.LoadBoard(str(fn))
        for u in sorted(pairs, key=lambda u: json.dumps(u['items'], sort_keys=True)):
            a, c = u['items']; net = next(t.GetNetname() for t in list(b.GetTracks()) + [x for f in b.GetFootprints() for x in f.Pads()] if t.m_Uuid.AsString() == a['uuid'])
            w = WIDTH.get(net, .2); s = [round(a['pos']['x'], 3), round(a['pos']['y'], 3)]; g = [round(c['pos']['x'], 3), round(c['pos']['y'], 3)]
            sl, gl = layers(b, a['uuid']), layers(b, c['uuid'])
            if net == 'AD_DOUT_LOCAL' and math.dist(s, [107.75, 49.675]) < .01: s, sl = [108.0, 51.15], [0, 1]  # leave from the R1 escape via, not inside the pin row
            if net == '5VA_P05' and 101 < s[0] < 115 and 37 < s[1] < 51: s, sl = [99.975, 40.25], [0]  # spine cluster: leave from C4 pad 1 (pin 1), outside U1
            pts = plan(b, net, s, sl, g, gl, w)
            if pts is None:  # a free end squeezed against other copper: drop that unlocked stub and ask DRC again
                t0 = next((t for t in b.GetTracks() for u in (a, c) if t.m_Uuid.AsString() == u['uuid'] and not t.IsLocked() and not isinstance(t, p.PCB_VIA)), None)
                if t0 is None: raise SystemExit(f'No route and no free stub to drop: {net} {s} -> {g}')
                records.append({'round': rnd, 'net': net, 'remove': seg(t0)}); remove(b, t0); print('round', rnd, net, 'removed stub', seg(t0), flush=True)
                break
            add(b, net, pts, w); records.append({'round': rnd, 'net': net, 'width': w, 'points_mm_layer': pts})
            print('round', rnd, net, s, '->', g, len(pts), 'vertices', flush=True)
            break  # one link per DRC round: the next DRC sees the new copper
        b.BuildConnectivity(); p.ZONE_FILLER(b).Fill(b.Zones()); p.SaveBoard(str(fn), b); purge()
        target.write_text(json.dumps(records, indent=1) + '\n')
    else:
        raise SystemExit('unconnected items remain after 12 rounds')
    target.write_text(json.dumps(records, indent=1) + '\n')
else:
    for r in json.loads(target.read_text()):
        b = p.LoadBoard(str(fn))
        if 'remove' in r:
            L, w, *ends = r['remove']
            t0 = [t for t in b.GetTracks() if not isinstance(t, p.PCB_VIA) and not t.IsLocked() and seg(t) == r['remove']]
            assert len(t0) == 1, ('replay: stub to remove not found once', r)
            remove(b, t0[0])
        else:
            add(b, r['net'], r['points_mm_layer'], r['width'])
        b.BuildConnectivity(); p.SaveBoard(str(fn), b); purge()
    b = p.LoadBoard(str(fn)); b.BuildConnectivity(); p.ZONE_FILLER(b).Fill(b.Zones()); p.SaveBoard(str(fn), b)
print('completion routes:', len(json.loads(target.read_text())))
