"""Excellon z paczek: narzędzia, otwory NPTH (M3) i najmniejszy odstęp otwór–otwór (krawędź–krawędź)."""
import re, sys, math, itertools, json
def parse(fn):
    tools, cur, holes, unit = {}, None, [], 1.0
    for ln in open(fn):
        ln = ln.strip()
        m = re.match(r'T(\d+)C([\d.]+)', ln)
        if m: tools[m.group(1)] = float(m.group(2)); continue
        m = re.match(r'T(\d+)$', ln)
        if m: cur = m.group(1); continue
        m = re.match(r'X([-\d.]+)Y([-\d.]+)$', ln)
        if m and cur: holes.append((float(m.group(1)), float(m.group(2)), tools[cur]))
        if ln.startswith('G85'): print('SLOT!', fn)
    return holes
out = {}
for b in sys.argv[1:]:
    import glob
    pth = parse(glob.glob(b + '/gerber/*-PTH.drl')[0]); npth = parse(glob.glob(b + '/gerber/*-NPTH.drl')[0])
    allh = [(x, y, d, 'P') for x, y, d in pth] + [(x, y, d, 'N') for x, y, d in npth]
    best = (9e9, None)
    for a, c in itertools.combinations(allh, 2):
        g = math.hypot(a[0]-c[0], a[1]-c[1]) - (a[2]+c[2])/2
        if g < best[0]: best = (g, (a, c))
    xs = [h[0] for h in allh]; ys = [h[1] for h in allh]
    print('==', b.split('/')[-1], 'PTH', len(pth), 'NPTH', len(npth), 'min drill PTH', min(h[2] for h in pth),
          'tools PTH', sorted(set(h[2] for h in pth)), 'NPTH', sorted(set(h[2] for h in npth)))
    print('   min hole-hole edge gap %.3f' % best[0], best[1])
    print('   NPTH:', sorted((round(x,2), round(y,2), d) for x, y, d in npth))
