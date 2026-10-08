"""Rough fit check for class 2/3 (106.5 x 100 mm, slots S2-S3 of level 5): sum of courtyard bounding boxes of all footprints vs. the
usable area after the 8 M3 zones (d 7 mm), the two edge-A connector strips and the two edge-B service strips (33 x 10 mm each).
No placement, no routing (layout: local session). Reference fill of finished S1 boards: P06 R2 / P05 R3 in the same way."""
import json
from pathlib import Path
import pcbnew
P = Path(__file__).resolve().parents[1]; parts = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
tot = 0; rows = []; top_tht = 0
for r, p in parts.items():
    lib, name = p['footprint'].split(':'); f = pcbnew.FootprintLoad(str(P / 'eda/libraries' / (lib + '.pretty')), name)
    poly = f.GetCourtyard(pcbnew.F_CrtYd)
    b = poly.BBox() if poly.OutlineCount() else f.GetBoundingBox(False, False)
    a = b.GetWidth() * b.GetHeight() / 1e12; tot += a; rows.append((r, name, round(a, 1)))
W, H = 106.5, 100.0
usable = W * H - 8 * 3.14159 * 3.5 ** 2 - 2 * 33 * 10 - 2 * 33 * 10
big = sorted(rows, key=lambda x: -x[2])[:10]
edge = sum(a for r, n, a in rows if r.startswith(('J_BP', 'J_SV')))           # these sit in the subtracted edge strips
smd = sum(a for r, n, a in rows if n.startswith(('R_1206', 'C_1206')) and parts[r].get('farads', 0) < 4e-6)   # 1206 parts that may go to the bottom (<= 1.5 mm)
inner = tot - edge
res = {'board_mm2': W * H, 'usable_mm2': round(usable), 'courtyard_bbox_sum_mm2': round(tot), 'fill_percent': round(100 * tot / usable),
       'interior_fill_percent': round(100 * inner / usable), 'interior_fill_with_1206_bottom_percent': round(100 * (inner - smd) / usable),
       'largest': big, 'note': 'Suma prostokatow courtyard (z kotwami przewodow), bez odstepow i trasowania. fill_percent liczony jak w P06 R2 (tam 41 %, wnetrze 29 %); interior_* bez J_BP / J_SV (stoja w odjetych pasach krawedzi).'}
(P / 'verification/powierzchnia.json').write_text(json.dumps(dict(res, per_part=rows), indent=1) + '\n')
print(json.dumps({k: v for k, v in res.items() if k != 'largest'}))
