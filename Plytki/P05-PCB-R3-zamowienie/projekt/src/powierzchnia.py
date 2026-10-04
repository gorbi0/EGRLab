"""Rough fit check for the S1 class: sum of courtyard bounding boxes of all footprints vs. the usable area of a 53 x 100 mm board (no placement, no routing)."""
import json,sys
from pathlib import Path
import pcbnew
P=Path(__file__).resolve().parents[1];parts=json.loads((P/'docs/parts.json').read_text(encoding='utf-8'))
tot=0;rows=[]
for r,p in parts.items():
 lib,name=p['footprint'].split(':');f=pcbnew.FootprintLoad(str(P/'eda/libraries'/(lib+'.pretty')),name)
 bb=f.GetBoundingBox(False,False) if f is None else None
 poly=f.GetCourtyard(pcbnew.F_CrtYd)
 b=poly.BBox() if poly.OutlineCount() else f.GetBoundingBox(False,False)
 a=b.GetWidth()*b.GetHeight()/1e12;tot+=a;rows.append((r,name,round(a,1)))
usable=53*100-4*3.14159*3.5**2-33*10-33*10
print(json.dumps({'parts':len(rows),'courtyard_bbox_sum_mm2':round(tot),'board_mm2':5300,'usable_after_holes_and_edge_strips_mm2':round(usable),'fill_percent':round(100*tot/usable)}))
(P/'verification/powierzchnia.json').write_text(json.dumps({'courtyard_bbox_sum_mm2':round(tot),'usable_mm2':round(usable),'fill_percent':round(100*tot/usable),'per_part':rows},indent=1))
