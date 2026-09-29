import pcbnew as p
b = p.LoadBoard('eda/P05.kicad_pcb')
u1 = next(f for f in b.GetFootprints() if f.GetReference() == 'U1')
box = (101.9, 38.9, 114.1, 49.1)   # LQFP body 10 x 10 mm around (108, 44)
def inside(x, y): return box[0] <= x <= box[2] and box[1] <= y <= box[3]
hits = []
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        x, y = p.ToMM(t.GetPosition().x), p.ToMM(t.GetPosition().y)
        if inside(x, y): hits.append(('via', t.GetNetname(), round(x, 2), round(y, 2)))
        continue
    if t.GetLayer() != p.B_Cu: continue
    s, e = t.GetStart(), t.GetEnd()
    for k in range(21):
        x = p.ToMM(s.x + (e.x - s.x) * k / 20); y = p.ToMM(s.y + (e.y - s.y) * k / 20)
        if inside(x, y): hits.append(('B.Cu', t.GetNetname().split('/')[-1], round(x, 2), round(y, 2))); break
print(len(hits)); import collections; print(collections.Counter((h[0], h[1]) for h in hits))
