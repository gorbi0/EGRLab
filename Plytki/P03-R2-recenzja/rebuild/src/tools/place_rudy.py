"""Placement helper, step 3 (working tool): RUDY congestion estimate of a placement. usage (KiCad Python):
place_rudy.py geom.json placement.json [map.png]"""
import json, sys, math, collections
import numpy as np
G = json.load(open(sys.argv[1])); PL = json.load(open(sys.argv[2]))
CELL = 4.0; NX, NY = 40, 30
def rot(x, y, a):
    r = math.radians(a); c, s = round(math.cos(r)), round(math.sin(r)); return (x * c + y * s, -x * s + y * c)
nets = collections.defaultdict(list)
for ref, g in G.items():
    x, y, a = PL[ref][:3]
    for num, (px, py, n) in g['pads'].items():
        if n in ('GND', '') or n.startswith('unconnected'):
            continue
        ox, oy = rot(px, py, a); nets[n].append((x + ox, y + oy))
D = np.zeros((NY, NX))
for n, pts in nets.items():
    if len(pts) < 2:
        continue
    x0 = min(q[0] for q in pts); x1 = max(q[0] for q in pts); y0 = min(q[1] for q in pts); y1 = max(q[1] for q in pts)
    w = max(x1 - x0, 2.0); h = max(y1 - y0, 2.0); cx = (x0 + x1) / 2; cy = (y0 + y1) / 2; x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    dens = (w + h) / (w * h) * (0.25 if n == '3V3_CORE' else 1.0)
    for j in range(max(0, int(y0 // CELL)), min(NY, int(y1 // CELL) + 1)):
        for i in range(max(0, int(x0 // CELL)), min(NX, int(x1 // CELL) + 1)):
            ov = max(0, min(x1, (i + 1) * CELL) - max(x0, i * CELL)) * max(0, min(y1, (j + 1) * CELL) - max(y0, j * CELL))
            D[j, i] += dens * ov / (CELL * CELL)
print(sys.argv[2], 'max %.2f  p95 %.2f  mean %.2f  overflow(>1.0) %.1f  overflow(>0.8) %.1f' % (D.max(), np.percentile(D, 95), D.mean(), (np.clip(D - 1.0, 0, None) ** 2).sum(), (np.clip(D - .8, 0, None) ** 2).sum()))
if len(sys.argv) > 3:
    from PIL import Image
    im = Image.fromarray(np.uint8(np.clip(D / 2.0, 0, 1) * 255)).resize((NX * 16, NY * 16), Image.NEAREST); im.save(sys.argv[3])
