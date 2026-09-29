"""Placement helper, step 1 (working tool, not part of the release chain): dump footprint-local pad positions and
courtyards from a built board. usage (KiCad Python): geom.py eda/P03.kicad_pcb geom.json"""
import pcbnew as p, json, math, sys
b = p.LoadBoard(sys.argv[1]); out = {}
def inv(f, v):
    a = math.radians(f.GetOrientationDegrees()); c = f.GetPosition()
    dx, dy = p.ToMM(v.x - c.x), p.ToMM(v.y - c.y)
    # board = pos + R(a)*local with R: (x,y)->(x cos a + y sin a, -x sin a + y cos a); inverse = R(-a)
    return (dx * math.cos(a) - dy * math.sin(a), dx * math.sin(a) + dy * math.cos(a))
for f in b.GetFootprints():
    r = f.GetReference()
    if r.startswith('H') and not r.startswith('HB'):
        continue
    pads = {}
    for a in f.Pads():
        if a.GetNumber():
            pads[a.GetNumber()] = [round(v, 4) for v in inv(f, a.GetPosition())] + [a.GetNetname().split('/')[-1]]
    f.BuildCourtyardCaches(); cy = f.GetCourtyard(p.F_CrtYd); pts = []
    for i in range(cy.OutlineCount()):
        ol = cy.Outline(i)
        pts += [inv(f, ol.CPoint(k)) for k in range(ol.PointCount())]
    xs = [q[0] for q in pts]; ys = [q[1] for q in pts]
    out[r] = {'pads': pads, 'cy': [round(min(xs), 3), round(min(ys), 3), round(max(xs), 3), round(max(ys), 3)]}
json.dump(out, open(sys.argv[2], 'w'), indent=1)
print(len(out), 'footprints')
