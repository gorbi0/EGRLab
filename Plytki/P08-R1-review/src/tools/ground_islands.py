"""Diagnostic: build a geometric graph of GND fill polygons and copper items on both layers."""
from pathlib import Path
import pcbnew as p,collections,json
P=Path(__file__).resolve().parents[2];b=p.LoadBoard(str(P/'eda/P08.kicad_pcb'))
nodes=[]
def bbox(sh):
 a=sh.BBox();return [round(p.ToMM(x),3) for x in [a.GetLeft(),a.GetTop(),a.GetRight(),a.GetBottom()]]
for z in b.Zones():
 if z.GetIsRuleArea() or z.GetNetname()!='GND':continue
 L=z.GetLayer();ps=z.GetFilledPolysList(L)
 for i in range(ps.OutlineCount()):
  s=p.SHAPE_POLY_SET();s.AddOutline(ps.Outline(i))
  for h in range(ps.HoleCount(i)):s.AddHole(ps.Hole(i,h))
  nodes.append((f'{b.GetLayerName(L)}:{i}',{L:s}))
polygon_count=len(nodes)
items=[a for f in b.GetFootprints() for a in f.Pads() if a.GetNetname()=='GND']+[t for t in b.GetTracks() if t.GetNetname()=='GND']
for a in items:
 name=(a.GetParentFootprint().GetReference()+'.'+a.GetNumber()) if isinstance(a,p.PAD) else a.GetClass()+':'+str(tuple(round(p.ToMM(x),3) for x in [a.GetPosition().x,a.GetPosition().y]))
 nodes.append((name,{L:a.GetEffectiveShape(L) for L in [p.F_Cu,p.B_Cu] if a.IsOnLayer(L)}))
par=list(range(len(nodes)))
def root(i):
 while par[i]!=i:par[i]=par[par[i]];i=par[i]
 return i
for i,(_,ss) in enumerate(nodes):
 for j in range(i):
  if i<polygon_count and j<polygon_count:continue # disjoint fill outlines by definition
  if root(i)==root(j):continue
  for L,sh in ss.items():
   if L in nodes[j][1] and sh.Collide(nodes[j][1][L],p.FromMM(.002)):
    par[root(i)]=root(j);break
groups=collections.defaultdict(list)
for i,(name,ss) in enumerate(nodes):groups[root(i)].append((name,{b.GetLayerName(L):bbox(s) for L,s in ss.items()}))
for v in sorted(groups.values(),key=len):
 print('CLUSTER',len(v));print(json.dumps(v if len(v)<40 else [v[0]],indent=1))
print('clusters',len(groups))
(P/'verification/ground-islands.json').write_text(json.dumps(sorted(groups.values(),key=len),indent=1))
assert len(groups)==1, 'Disconnected GND copper: inspect the reported local islands'
