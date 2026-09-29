"""Placement helper, step 2 (working tool, not part of the release chain): simulated annealing of src/placement.json.
Cost = weighted MST length of all non-GND nets + overlap penalties (courtyards incl. 1 mm gap, holes, antenna
keepout, board outline). Connectors and SD1 stay on an edge (T/B/L); ICs carry their decoupling capacitor.
usage: python place_anneal.py geom.json start.json out.json iterations seed [gap_mm] [T0]
Run on 25.09 with 150k iterations from the hand placement, then 100k with a 3 mm gap from the best result; FIXED below
are the positions of that run (the test pads were moved by hand afterwards, see docs/LAYOUT.md).
"""
import json, math, random, sys, collections, time
G = json.load(open(sys.argv[1])); start = json.load(open(sys.argv[2])); OUT = sys.argv[3]
ITER = int(sys.argv[4]); random.seed(int(sys.argv[5]))
W, H = 160.0, 120.0; M = 0.3; GAP = float(sys.argv[6]) if len(sys.argv) > 6 else 0.5; T0ARG = float(sys.argv[7]) if len(sys.argv) > 7 else 30.0
BLOCKED = [(h[0] - 4.5, h[1] - 4.5, h[0] + 4.5, h[1] + 4.5) for h in [(5, 5), (155, 5), (5, 115), (155, 115), (155, 38)]]
BLOCKED.append((7.11, 58.25, 38.61, 72.75))  # ANTENNA M1


def rot(x, y, a):
    r = math.radians(a); c, s = round(math.cos(r)), round(math.sin(r))
    return (x * c + y * s, -x * s + y * c)


def cy_rot(ref, a):
    x0, y0, x1, y1 = G[ref]['cy']; pts = [rot(x, y, a) for x, y in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]]
    return (min(q[0] for q in pts), min(q[1] for q in pts), max(q[0] for q in pts), max(q[1] for q in pts))


FIXED = {'M1': (34.29, 56.75, 180), 'J1': (147, 31, 180), 'J10': (44, 16, 0), 'TP1': (41, 19.5, 0), 'TP3': (45.5, 19.5, 0),
         'TP4': (50, 19.5, 0), 'TP2': (54.5, 19.5, 0)}
CAPB = lambda u, c: [(u, 0, 0, 0), (c, 19.24, 2, 90)]
BLOCKS = {'U11': CAPB('U11', 'C5'), 'U12': CAPB('U12', 'C6'), 'U13': CAPB('U13', 'C7'), 'U14': CAPB('U14', 'C8'), 'U21': CAPB('U21', 'C9'),
          'U22': CAPB('U22', 'C10'), 'U23': CAPB('U23', 'C11'), 'U1': [('U1', 0, 0, 0), ('C2', -4.5, 18.5, 270)],
          'U2': [('U2', 0, 0, 0), ('C1', 11.2, 3, 90)], 'U3': [('U3', 0, 0, 0), ('C3', -4.5, 5.08, 90), ('R13', 0, -4.5, 0), ('TP5', 13, -4.5, 0)],
          'SD1': [('SD1', 0, 0, 0), ('R11', 2.54, 5, 0)], 'LED': [('R4', 0, 0, 0), ('LED1', 16.5, 0, 180)], 'MARK': [('R5', 0, 0, 0), ('C4', 10.16, 3.5, 0)],
          'I2C': [('R9', 0, 0, 0), ('R10', 0, 3.5, 0)], 'PD13': [('R6', 0, 0, 0), ('R8', 0, 3.5, 0)]}
for r in ['R1', 'R2', 'R3', 'R7', 'R12', 'R14', 'TP6', 'J2', 'J3', 'J4', 'J5', 'J6', 'J7', 'J8', 'J9']:
    BLOCKS[r] = [(r, 0, 0, 0)]
EDGE = {'J2', 'J3', 'J4', 'J5', 'J6', 'J7', 'J8', 'J9', 'SD1'}
EROT = {'IDC': {'T': [90], 'B': [270], 'L': [180]}, 'J9': {'T': [0, 180], 'B': [0, 180], 'L': [90, 270]}, 'SD1': {'T': [0], 'B': [180], 'L': [90]}}


def erot(name):
    return EROT['J9'] if name == 'J9' else EROT['SD1'] if name == 'SD1' else EROT['IDC']


# block local courtyard (union bbox of member courtyards at block rotation) and member transforms
def members(name, a):
    out = []
    for ref, dx, dy, ra in BLOCKS[name]:
        ox, oy = rot(dx, dy, a); out.append((ref, ox, oy, (ra + a) % 360))
    return out


def bbox(name, x, y, a):
    bs = []
    for ref, ox, oy, ra in members(name, a):
        c = cy_rot(ref, ra); bs.append((x + ox + c[0], y + oy + c[1], x + ox + c[2], y + oy + c[3]))
    return bs


state = {}
for name in BLOCKS:
    ref = BLOCKS[name][0][0]; x, y, a = start[ref][:3]; state[name] = [x, y, a]


def snap_edge(name, st):
    """For edge blocks: put the courtyard's outer side on the edge implied by the rotation."""
    x, y, a = st[:3]; e = st[3] if len(st) > 3 else None
    b = bbox(name, 0, 0, a); x0 = min(q[0] for q in b); y0 = min(q[1] for q in b); x1 = max(q[2] for q in b); y1 = max(q[3] for q in b)
    if e == 'T':
        y = M - y0
    elif e == 'B':
        y = H - M - y1
    elif e == 'L':
        x = M - x0
    return [x, y, a, e]


def edge_of(name, st):
    b = bbox(name, st[0], st[1], st[2]); x0 = min(q[0] for q in b); y0 = min(q[1] for q in b); y1 = max(q[3] for q in b)
    d = {'T': y0, 'B': H - y1, 'L': x0}
    return min(d, key=d.get)


for name in EDGE:
    e = edge_of(name, state[name]); rots = erot(name)[e]
    if state[name][2] not in rots:
        state[name][2] = rots[0]
    state[name] = snap_edge(name, state[name] + [e])

# nets
net_pins = collections.defaultdict(list)  # net -> list of (block or fixed ref, member ref, pad local)
for ref, g in G.items():
    for num, (px, py, net) in g['pads'].items():
        if net in ('GND', '') or net.startswith('unconnected'):
            continue
        net_pins[net].append((ref, px, py))
owner = {}
for name, mem in BLOCKS.items():
    for ref, *_ in mem:
        owner[ref] = name
WEIGHT = collections.defaultdict(lambda: 1.0, {'3V3_CORE': 0.25})
block_nets = collections.defaultdict(set)
for net, pins in net_pins.items():
    for ref, *_ in pins:
        if ref in owner:
            block_nets[owner[ref]].add(net)


def pad_xy(ref, px, py):
    if ref in FIXED:
        x, y, a = FIXED[ref]; ox, oy = rot(px, py, a); return (x + ox, y + oy)
    name = owner[ref]; x, y, a = state[name][:3]
    for r, ox, oy, ra in members(name, a):
        if r == ref:
            qx, qy = rot(px, py, ra); return (x + ox + qx, y + oy + qy)


def mst(pts):
    if len(pts) < 2:
        return 0.0
    dist = {i: abs(pts[0][0] - pts[i][0]) + abs(pts[0][1] - pts[i][1]) for i in range(1, len(pts))}; tot = 0.0
    while dist:
        j = min(dist, key=dist.get); tot += dist.pop(j)
        for k in dist:
            e = abs(pts[j][0] - pts[k][0]) + abs(pts[j][1] - pts[k][1])
            if e < dist[k]:
                dist[k] = e
    return tot


def net_cost(net):
    return WEIGHT[net] * mst([pad_xy(r, px, py) for r, px, py in net_pins[net]])


FIXED_BOXES = []
for ref, (x, y, a) in FIXED.items():
    c = cy_rot(ref, a); FIXED_BOXES.append((x + c[0], y + c[1], x + c[2], y + c[3]))


def ov(a, b, g=0.0):
    w = min(a[2], b[2]) + g - max(a[0], b[0]); h = min(a[3], b[3]) + g - max(a[1], b[1])
    return w * h if w > 0 and h > 0 else 0.0


def block_pen(name, boxes=None):
    bs = boxes or bbox(name, *state[name][:3]); pen = 0.0
    for b in bs:
        pen += max(0, M - b[0]) * 10 + max(0, M - b[1]) * 10 + max(0, b[2] - (W - M)) * 10 + max(0, b[3] - (H - M)) * 10
        for k in BLOCKED:
            pen += ov(b, k)
        for k in FIXED_BOXES:
            pen += ov(b, k, GAP)
    return pen


def pair_pen(n1, n2, b1=None, b2=None):
    b1 = b1 or bbox(n1, *state[n1][:3]); b2 = b2 or bbox(n2, *state[n2][:3]); return sum(ov(a, c, GAP) for a in b1 for c in b2)


PEN = 200.0
cost_net = {n: net_cost(n) for n in net_pins}
names = list(BLOCKS)


def total():
    wl = sum(cost_net.values()); pen = sum(block_pen(n) for n in names) + sum(pair_pen(a, b) for i, a in enumerate(names) for b in names[i + 1:])
    return wl, pen


wl, pen = total(); print('start: wirelength %.0f, penalty %.1f' % (wl, pen))
T0, T1 = T0ARG, 0.05; t0 = time.time(); accepted = 0


def local_cost(name):
    bs = bbox(name, *state[name][:3]); pen = block_pen(name, bs) + sum(pair_pen(name, o, bs) for o in names if o != name)
    return sum(cost_net[n] for n in block_nets[name]), pen


for it in range(ITER):
    T = T0 * (T1 / T0) ** (it / ITER); sigma = max(.25, 25 * (T / T0) ** .5)
    name = random.choice(names); old = list(state[name]); wl_old, pen_old = local_cost(name)
    r = random.random()
    if r < .04:  # teleport: escapes local traps (e.g. a connector squeezed beside M1)
        e = random.choice('TBL') if name in EDGE else None
        if name in EDGE:
            a = random.choice(erot(name)[e]); state[name] = snap_edge(name, [random.uniform(5, W - 5), random.uniform(5, H - 5), a, e])
        else:
            state[name][0] = random.uniform(5, W - 5); state[name][1] = random.uniform(5, H - 5)
    elif name in EDGE:
        if r < .1:
            e = random.choice('TBL'); a = random.choice(erot(name)[e]); state[name] = snap_edge(name, [old[0], old[1], a, e])
        elif r < .15 and len(erot(name)[old[3]]) > 1:
            a = random.choice(erot(name)[old[3]]); state[name] = snap_edge(name, [old[0], old[1], a, old[3]])
        else:
            if old[3] == 'L':
                state[name] = snap_edge(name, [old[0], old[1] + random.gauss(0, sigma), old[2], old[3]])
            else:
                state[name] = snap_edge(name, [old[0] + random.gauss(0, sigma), old[1], old[2], old[3]])
    else:
        if r < .12 and name not in ('TP6',):
            state[name][2] = random.choice([0, 90, 180, 270])
        else:
            state[name][0] += random.gauss(0, sigma); state[name][1] += random.gauss(0, sigma)
    new_costs = {n: net_cost(n) for n in block_nets[name]}
    bs = bbox(name, *state[name][:3]); pen_new = block_pen(name, bs) + sum(pair_pen(name, o, bs) for o in names if o != name)
    d = sum(new_costs.values()) - wl_old + PEN * (pen_new - pen_old)
    if d <= 0 or random.random() < math.exp(-d / T):
        cost_net.update(new_costs); accepted += 1
    else:
        state[name] = old
    if it % max(1, ITER // 10) == 0:
        wl, pen = total(); print(f'it {it} T {T:.2f} wl {wl:.0f} pen {pen:.2f} acc {accepted} {time.time() - t0:.0f}s', flush=True)
wl, pen = total(); print('end: wirelength %.0f, penalty %.2f' % (wl, pen))
place = {}
for ref, v in FIXED.items():
    place[ref] = list(v)
for name in names:
    x, y, a = state[name][:3]
    for ref, ox, oy, ra in members(name, a):
        place[ref] = [round((x + ox) * 20) / 20, round((y + oy) * 20) / 20, ra]
json.dump(place, open(OUT, 'w'), indent=1)
print('edges:', {n: state[n][3] for n in EDGE})
