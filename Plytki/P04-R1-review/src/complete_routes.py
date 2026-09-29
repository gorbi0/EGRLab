"""Complete connections missed by router/plane fill. Exact paths are stored for review.
Conservative raster path search only proposes copper. Native KiCad DRC is authoritative.
Default replays reviewed completion-routes.json. --plan regenerates the candidate paths.
"""
from pathlib import Path
import pcbnew as p,json,math,heapq,sys
from PIL import Image,ImageDraw,ImageFilter
import numpy as np
P=Path(__file__).resolve().parents[1];fn=P/'eda/P04.kicad_pcb';b=p.LoadBoard(str(fn));mm=p.FromMM
R=10;W=160*R;H=120*R
f={q.GetReference():q for q in b.GetFootprints()}
def pad(ref,n):return next(q for q in f[ref].Pads() if q.GetNumber()==str(n))
def xy(v):return [p.ToMM(v.x),p.ToMM(v.y)]
def drawpoly(d,ps):
 for k in range(ps.OutlineCount()):
  o=ps.Outline(k);d.polygon([(p.ToMM(o.CPoint(i).x)*R,p.ToMM(o.CPoint(i).y)*R) for i in range(o.PointCount())],fill=255)
def plan(a,z):
 net=a.GetNetCode();images=[]
 for layer in [p.F_Cu,p.B_Cu]:
  im=Image.new('L',(W,H));d=ImageDraw.Draw(im)
  for fp in b.GetFootprints():
   for q in fp.Pads():
    if q.GetNetCode()==net:continue
    if q.IsOnLayer(layer):
     ps=p.SHAPE_POLY_SET();q.TransformShapeToPolygon(ps,layer,0,mm(.005),p.ERROR_OUTSIDE);drawpoly(d,ps)
  for t in b.GetTracks():
   if t.GetNetCode()==net:continue
   if isinstance(t,p.PCB_VIA) or t.GetLayer()==layer:
    ps=p.SHAPE_POLY_SET();t.TransformShapeToPolygon(ps,layer,0,mm(.005),p.ERROR_OUTSIDE);drawpoly(d,ps)
  for zone in b.Zones():
   if zone.GetIsRuleArea():drawpoly(d,zone.Outline())
  # 0.5mm conservative added radius = 0.25 clearance + 0.15 track + raster margin.
  d.rectangle([0,0,W-1,H-1],outline=255,width=10)
  images.append(im)
 obs=[np.array(im.filter(ImageFilter.MaxFilter(11)))!=0 for im in images]
 via=np.array(images[0].filter(ImageFilter.MaxFilter(17)))|np.array(images[1].filter(ImageFilter.MaxFilter(17)))
 s=tuple(round(v*R) for v in xy(a.GetPosition()));g=tuple(round(v*R) for v in xy(z.GetPosition()))
 def h(x,y):dx=abs(x-g[0]);dy=abs(y-g[1]);return max(dx,dy)+.41421356*min(dx,dy)
 def key(x,y,l):return (l*H+y)*W+x
 starts={key(*s,0),key(*s,1)};todo=[(h(*s),0,q) for q in starts];heapq.heapify(todo);cost={q:0 for q in starts};prev={};end=None
 while todo:
  _,dist,q=heapq.heappop(todo)
  if dist!=cost.get(q):continue
  x=q%W;y=(q//W)%H;l=q//(W*H)
  if (x,y)==g:end=q;break
  nxt=[]
  for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
   nx,ny=x+dx,y+dy
   if 0<=nx<W and 0<=ny<H and not obs[l][ny,nx] and not obs[l][y,nx] and not obs[l][ny,x]:nxt.append((nx,ny,l,1.41421356237 if dx and dy else 1))
  if not via[y,x]:nxt.append((x,y,1-l,80))
  for nx,ny,nl,dc in nxt:
   nk=key(nx,ny,nl);nd=dist+dc
   if nd<cost.get(nk,1e99):cost[nk]=nd;prev[nk]=q;heapq.heappush(todo,(nd+h(nx,ny),nd,nk))
 assert end is not None,('No route',a.GetParentFootprint().GetReference(),a.GetNumber())
 path=[]
 while True:
  path.append([end%W/R,((end//W)%H)/R,end//(W*H)])
  if end in starts:break
  end=prev[end]
 path.reverse();path=[[*xy(a.GetPosition()),path[0][2]]]+path+[[*xy(z.GetPosition()),path[-1][2]]]
 # Drop collinear intermediate points but preserve layer changes.
 keep=[path[0]]
 for i in range(1,len(path)-1):
  aa,bb,cc=keep[-1],path[i],path[i+1]
  if aa[2]==bb[2]==cc[2] and abs((bb[0]-aa[0])*(cc[1]-bb[1])-(bb[1]-aa[1])*(cc[0]-bb[0]))<1e-7:continue
  if bb!=keep[-1]:keep.append(bb)
 if path[-1]!=keep[-1]:keep.append(path[-1])
 return keep
def add(net,points):
 for a,c in zip(points,points[1:]):
  if a==c:continue
  if a[2]!=c[2]:
   assert a[:2]==c[:2];t=p.PCB_VIA(b);t.SetPosition(p.VECTOR2I(mm(a[0]),mm(a[1])));t.SetWidth(mm(.8));t.SetDrill(mm(.4));t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu)
  else:
   t=p.PCB_TRACK(b);t.SetStart(p.VECTOR2I(mm(a[0]),mm(a[1])));t.SetEnd(p.VECTOR2I(mm(c[0]),mm(c[1])));t.SetWidth(mm(.3));t.SetLayer(p.F_Cu if a[2]==0 else p.B_Cu)
  t.SetNet(net);t.SetLocked(True);b.Add(t)
target=P/'routing/completion-routes.json';records=[]
if '--plan' in sys.argv:
 for src,dst in [(('U10',6),('R34',1)),(('U8',10),('U8',7)),(('U9',4),('U9',7))]:
  a,z=pad(*src),pad(*dst);assert a.GetNetCode()==z.GetNetCode();points=plan(a,z)
  rec={'net':a.GetNetname(),'from':src,'to':dst,'points_mm_layer':points};records.append(rec);add(a.GetNet(),points);print('Completion',src,dst,len(points),'vertices',flush=True)
 target.write_text(json.dumps(records,indent=2))
else:
 for rec in json.loads(target.read_text()):add(b.FindNet(rec['net']),rec['points_mm_layer'])
for ref,n in [('U8',4),('U8',7),('R17',2)]:pad(ref,n).SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(fn),b)
