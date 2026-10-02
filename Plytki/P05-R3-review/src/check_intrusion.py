"""P05 R3 (1.10): router copper inside the U1 courtyard? Freerouting runs without DSN keepouts (keepouts holding pins crippled it,
board.ROUTER_KEEPOUT), so after each import this check rejects an attempt whose unlocked copper is of another net anywhere in the U1 courtyard or
(own nets too, echoes of the locked copper aside) on F.Cu inside the pad ring, where the GND pour must stay one piece (README,
review P5-01); U1's own nets may join their escapes in the pad-row band and use B.Cu under it. Exit 0 = clean, 4 = intrusion (run_layout.py starts a new router run). Report: routing/intrusion.json."""
from pathlib import Path
import pcbnew as p, json, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from board import NAME
P = Path(__file__).resolve().parents[1]
b = p.LoadBoard(str(P / f'eda/{NAME}.kicad_pcb'))
u1 = next(f for f in b.GetFootprints() if f.GetReference() == 'U1'); u1.BuildCourtyardCaches(); cy = u1.GetCourtyard(p.F_CrtYd)
own = {a.GetNetname() for a in u1.Pads()}
c = u1.GetPosition(); cx, cy_ = p.ToMM(c.x), p.ToMM(c.y)
inner = p.SHAPE_POLY_SET(); inner.NewOutline()   # inside the pad ring (pad inner ends 4.9 mm from the centre, 0.15 mm in)
for x, y in [(-4.75, -4.75), (4.75, -4.75), (4.75, 4.75), (-4.75, 4.75)]:
    inner.Append(p.FromMM(cx + x), p.FromMM(cy_ + y))
locked = {}
for t in b.GetTracks():   # the copper of route_critical.py / fanout_gnd.py, 1 mm around it: the router echoes it in the SES
    if t.IsLocked():
        for L in ((p.F_Cu, p.B_Cu) if isinstance(t, p.PCB_VIA) else (t.GetLayer(),)):
            ps = locked.setdefault((t.GetNetname(), L), p.SHAPE_POLY_SET()); t.TransformShapeToPolygon(ps, L, p.FromMM(1.0), p.FromMM(.005), p.ERROR_OUTSIDE)
hits = []
for t in b.GetTracks():
    if t.IsLocked():
        continue
    for L in ((p.F_Cu, p.B_Cu) if isinstance(t, p.PCB_VIA) else (t.GetLayer(),)):
        ps = p.SHAPE_POLY_SET(); t.TransformShapeToPolygon(ps, L, 0, p.FromMM(.005), p.ERROR_INSIDE)
        def touch(area, q=ps):
            x = p.SHAPE_POLY_SET(q); x.BooleanIntersection(area); return x.OutlineCount() > 0 and x.Area() > 0
        rest = p.SHAPE_POLY_SET(ps)
        if (t.GetNetname(), L) in locked:
            rest.BooleanSubtract(locked[(t.GetNetname(), L)])
        why = ('other net in the courtyard' if t.GetNetname() not in own and touch(cy) else
               'inside the pad ring' if L == p.F_Cu and rest.OutlineCount() and touch(inner, rest) else None)
        if why:   # U1's own nets may join their escapes in the pad-row band and run on B.Cu under it (verify_pcb.py: pour pieces stitched)
            hits.append({'net': t.GetNetname(), 'layer': b.GetLayerName(L), 'via': isinstance(t, p.PCB_VIA), 'why': why,
                         'at': [round(p.ToMM(t.GetPosition().x if isinstance(t, p.PCB_VIA) else t.GetStart().x), 3),
                                round(p.ToMM(t.GetPosition().y if isinstance(t, p.PCB_VIA) else t.GetStart().y), 3)]})
            break
(P / 'routing/intrusion.json').write_text(json.dumps(hits, indent=1) + '\n')
print(f'router copper inside the U1 courtyard: {len(hits)}', [(h['net'], h['why']) for h in hits][:10])
sys.exit(4 if hits else 0)
