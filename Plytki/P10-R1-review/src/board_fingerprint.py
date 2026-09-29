"""Semantic PCB digest for clean-room regeneration; ignores random UUIDs."""
from pathlib import Path
import hashlib,json,sys
import pcbnew as p
P=Path(__file__).resolve().parents[1]
b=p.LoadBoard(str(P/'eda/P10.kicad_pcb'))
def xy(v):return [round(p.ToMM(v.x),6),round(p.ToMM(v.y),6)]
def number(v):return round(p.ToMM(v),6)
data={'footprints':[],'tracks':[],'drawings':[],'zones':[]}
for f in b.GetFootprints():
    data['footprints'].append([f.GetReference(),f.GetValue(),f.GetFPIDAsString(),xy(f.GetPosition()),round(f.GetOrientationDegrees(),6),
        sorted([[a.GetNumber(),a.GetNetname(),xy(a.GetPosition()),xy(a.GetSize()),xy(a.GetDrillSize()),int(a.GetLocalZoneConnection())] for a in f.Pads()]),
        [f.Reference().IsVisible(),xy(f.Reference().GetPosition()),xy(f.Reference().GetTextSize()),f.Reference().GetTextAngle().AsDegrees()],
        sorted([[g.GetText(),xy(g.GetPosition()),xy(g.GetTextSize()),g.GetTextAngle().AsDegrees(),b.GetLayerName(g.GetLayer())] for g in f.GraphicalItems() if isinstance(g,p.PCB_TEXT)])])
for t in b.GetTracks():
    if isinstance(t,p.PCB_VIA):data['tracks'].append(['via',t.GetNetname(),xy(t.GetPosition()),number(t.GetWidth(p.F_Cu)),number(t.GetDrill())])
    else:data['tracks'].append(['track',t.GetNetname(),sorted([xy(t.GetStart()),xy(t.GetEnd())]),number(t.GetWidth()),b.GetLayerName(t.GetLayer())])
for g in b.GetDrawings():
    if isinstance(g,p.PCB_TEXT):data['drawings'].append(['text',g.GetText(),xy(g.GetPosition()),xy(g.GetTextSize()),b.GetLayerName(g.GetLayer())])
    elif isinstance(g,p.PCB_SHAPE):data['drawings'].append(['shape',int(g.GetShape()),xy(g.GetStart()),xy(g.GetEnd()),number(g.GetWidth()),b.GetLayerName(g.GetLayer())])
for z in b.Zones():
    data['zones'].append([z.GetNetname(),z.GetZoneName(),z.GetIsRuleArea(),sorted(b.GetLayerName(l) for l in z.GetLayerSet().Seq()),
        [[xy(z.Outline().Outline(i).CPoint(j)) for j in range(z.Outline().Outline(i).PointCount())] for i in range(z.Outline().OutlineCount())]])
for k in data:data[k].sort(key=lambda r:json.dumps(r,sort_keys=True))
digest=hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()
out={'sha256':digest,'counts':{k:len(v) for k,v in data.items()},'scope':'Footprint fields/positions/pads, tracks/vias, board drawings, zone outlines. Ignores random UUIDs; native DRC and separate geometry checks also required.'}
(P/'verification/geometry-fingerprint.json').write_text(json.dumps(out,indent=2)+'\n')
print('Geometry fingerprint',digest)
