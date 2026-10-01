"""P06 R2 (1.10): foreign router copper at the shunt or the Kelvin pair? Run after every SES import (run_layout.py). Freerouting gets
DSN keepouts there (board.ROUTER_KEEPOUT), but they are not trusted blindly (P05 lesson: the router echoes copper and may graze):
an attempt is rejected when unlocked copper of a net other than the force / Kelvin nets touches the RSH1 courtyard (either layer)
or one of board.ROUTER_KEEPOUT (README: nothing foreign at the shunt, the Kelvin lines stay a clean pair). Echoes of the locked copper
(own nets) do not count. Exit 0 = clean, 4 = intrusion (run_layout.py starts a new router run). Report: routing/intrusion.json."""
from pathlib import Path
import pcbnew as p, json, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from board import NAME, SHUNT, FORCE, KELVIN, ROUTER_KEEPOUT
P = Path(__file__).resolve().parents[1]
b = p.LoadBoard(str(P / f'eda/{NAME}.kicad_pcb'))
sh = next(f for f in b.GetFootprints() if f.GetReference() == SHUNT); sh.BuildCourtyardCaches(); cy = sh.GetCourtyard(p.F_CrtYd)
own = set(FORCE) | set(KELVIN)
areas = []   # (name, layer or None for both, polygon)
areas.append((f'{SHUNT} courtyard', None, cy))
for L, x0, y0, x1, y1 in ROUTER_KEEPOUT:
    ps = p.SHAPE_POLY_SET(); ps.NewOutline()
    for x, y in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]:
        ps.Append(p.FromMM(x), p.FromMM(y))
    areas.append((f'keepout {L} {x0}..{x1} x {y0}..{y1}', p.F_Cu if L == 'F.Cu' else p.B_Cu, ps))
hits = []
for t in b.GetTracks():
    if t.IsLocked() or t.GetNetname().split('/')[-1] in own:
        continue
    for L in ((p.F_Cu, p.B_Cu) if isinstance(t, p.PCB_VIA) else (t.GetLayer(),)):
        q = p.SHAPE_POLY_SET(); t.TransformShapeToPolygon(q, L, 0, p.FromMM(.005), p.ERROR_INSIDE)
        for name, al, area in areas:
            if al is not None and al != L:
                continue
            x = p.SHAPE_POLY_SET(q); x.BooleanIntersection(area)
            if x.OutlineCount() and x.Area() > 0:
                pos = t.GetPosition() if isinstance(t, p.PCB_VIA) else t.GetStart()
                hits.append({'net': t.GetNetname(), 'layer': b.GetLayerName(L), 'via': isinstance(t, p.PCB_VIA), 'area': name,
                             'at': [round(p.ToMM(pos.x), 3), round(p.ToMM(pos.y), 3)]})
                break
(P / 'routing/intrusion.json').write_text(json.dumps(hits, indent=1) + '\n')
print(f'foreign router copper at {SHUNT} / Kelvin pair: {len(hits)}', [(h['net'], h['area']) for h in hits][:10])
sys.exit(4 if hits else 0)
