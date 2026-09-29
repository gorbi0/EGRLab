"""Candidate route completion. Default replays reviewed completion-routes.json. --plan searches paths for native DRC gaps; it is a routing aid, not a release gate. If a new layout cannot be completed, inspect the reported endpoints/layers and route manually. P10-R1 reviewed SES has no missing connections, so the stored completion list is empty."""
from pathlib import Path
import pcbnew as p,json,math,heapq,sys,os,subprocess
from PIL import Image,ImageDraw,ImageFilter
import numpy as np
P=Path(__file__).resolve().parents[1];fn=P/'eda/P10.kicad_pcb';b=p.LoadBoard(str(fn));mm=p.FromMM
R=10;W=80*R;H=70*R
f={q.GetReference():q for q in b.GetFootprints()}
def pad(ref,n):return next(q for q in f[ref].Pads() if q.GetNumber()==str(n))
def xy(v):return [p.ToMM(v.x),p.ToMM(v.y)]
def drawpoly(d,ps):
 for k in range(ps.OutlineCount()):
  o=ps.Outline(k);d.polygon([(p.ToMM(o.CPoint(i).x)*R,p.ToMM(o.CPoint(i).y)*R) for i in range(o.PointCount())],fill=255)
def fillmask(net):
 """Largest filled polygon of the net on each layer, 0.6 mm inside its edge: where a completion track may end."""
 masks=[]
 for layer in [p.F_Cu,p.B_Cu]:
  im=Image.new('L',(W,H));d=ImageDraw.Draw(im);best=None
  for z in b.Zones():
   if z.GetIsRuleArea() or z.GetNetCode()!=net or not z.IsOnLayer(layer):continue
   ps=z.GetFilledPolysList(layer)
   for i in range(ps.OutlineCount()):
    one=p.SHAPE_POLY_SET();one.AddOutline(ps.Outline(i))
    for h in range(ps.HoleCount(i)):one.AddHole(ps.Hole(i,h))
    if best is None or one.Area()>best.Area():best=one
  if best is not None:
   o=best.Outline(0);d.polygon([(p.ToMM(o.CPoint(i).x)*R,p.ToMM(o.CPoint(i).y)*R) for i in range(o.PointCount())],fill=255)
   for h in range(best.HoleCount(0)):
    o=best.Hole(0,h);d.polygon([(p.ToMM(o.CPoint(i).x)*R,p.ToMM(o.CPoint(i).y)*R) for i in range(o.PointCount())],fill=0)
  masks.append(np.array(im.filter(ImageFilter.MinFilter(13)))!=0)
 return masks
def plan(net,sxy,gxy):
 """gxy None: the goal is the net's main pour (a pad cut off from the fill, reported by DRC against the zone)."""
 goal=fillmask(net) if gxy is None else None
 images=[]
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
 s=tuple(round(v*R) for v in sxy);g=tuple(round(v*R) for v in gxy) if goal is None else None
 def h(x,y):
  if g is None:return 0
  dx=abs(x-g[0]);dy=abs(y-g[1]);return max(dx,dy)+.41421356*min(dx,dy)
 def key(x,y,l):return (l*H+y)*W+x
 starts={key(*s,0),key(*s,1)};todo=[(h(*s),0,q) for q in starts];heapq.heapify(todo);cost={q:0 for q in starts};prev={};end=None
 while todo:
  _,dist,q=heapq.heappop(todo)
  if dist!=cost.get(q):continue
  x=q%W;y=(q//W)%H;l=q//(W*H)
  if (x,y)==g if goal is None else goal[l][y,x]:end=q;break
  nxt=[]
  for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
   nx,ny=x+dx,y+dy
   if 0<=nx<W and 0<=ny<H and not obs[l][ny,nx] and not obs[l][y,nx] and not obs[l][ny,x]:nxt.append((nx,ny,l,1.41421356237 if dx and dy else 1))
  if not via[y,x]:nxt.append((x,y,1-l,80))
  for nx,ny,nl,dc in nxt:
   nk=key(nx,ny,nl);nd=dist+dc
   if nd<cost.get(nk,1e99):cost[nk]=nd;prev[nk]=q;heapq.heappush(todo,(nd+h(nx,ny),nd,nk))
 if end is None:print(f'no completion path for net {net} {sxy} -> {gxy}');sys.exit(3)
 path=[]
 while True:
  path.append([end%W/R,((end//W)%H)/R,end//(W*H)])
  if end in starts:break
  end=prev[end]
 path.reverse();path=[[*sxy,path[0][2]]]+path+([[*gxy,path[-1][2]]] if goal is None else [])
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
def endpoint(uuid,pos):
 """Pad centre for a pad, the DRC marker position for a track/via end; (item label, xy, net code)."""
 for fp in b.GetFootprints():
  for q in fp.Pads():
   if q.m_Uuid.AsString()==uuid:return f'{fp.GetReference()}.{q.GetNumber()}',xy(q.GetPosition()),q.GetNetCode()
 for t in b.GetTracks():
  if t.m_Uuid.AsString()==uuid:
   ends=[xy(t.GetPosition())] if isinstance(t,p.PCB_VIA) else [xy(t.GetStart()),xy(t.GetEnd())]
   return ('via' if isinstance(t,p.PCB_VIA) else 'track')+'@'+t.GetNetname(),min(ends,key=lambda e:math.dist(e,pos)),t.GetNetCode()
 for z in b.Zones():
  if z.m_Uuid.AsString()==uuid:return 'pour@'+z.GetNetname(),None,z.GetNetCode()
 sys.exit(f'unconnected item {uuid} is neither a pad, a track nor a zone: plan by hand')
if '--plan' in sys.argv:
 # Rounds: a pad cluster joined to the pour can reveal the next cluster (DRC reports one edge per cluster), so
 # plan, refill, save and ask native DRC again until nothing is left unconnected.
 CLI=os.environ.get('KICAD_CLI',str(Path(sys.executable).with_name('kicad-cli.exe')));rep=P/'routing/precompletion-drc.json'
 for rnd in range(1,7):
  subprocess.run([CLI,'pcb','drc','--format','json','--severity-all','--refill-zones','-o',str(rep),str(fn)],check=True,stdout=subprocess.DEVNULL)
  todo=json.loads(rep.read_text())['unconnected_items']
  if not todo:break
  done=set()  # DRC can list one pad against the pour of each layer: one completion per pad and round is enough
  for u in todo:
   (la,sa,na),(lz,sz,nz)=sorted([endpoint(i['uuid'],(i['pos']['x'],i['pos']['y'])) for i in u['items']],key=lambda e:e[1] is None);assert na==nz and sa,(la,lz)
   if sz is None and la in done:continue
   done.add(la)
   points=plan(na,sa,sz);net=b.GetNetsByNetcode()[na]
   rec={'round':rnd,'net':net.GetNetname(),'from':la,'to':lz,'points_mm_layer':points};records.append(rec);add(net,points)
   print('Completion round',rnd,la,lz,len(points),'vertices',flush=True)
  b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(fn),b)
 else:print('unconnected items remain after 6 completion rounds');sys.exit(3)
 target.write_text(json.dumps(records,indent=2))
else:
 for rec in json.loads(target.read_text()):add(b.FindNet(rec['net']),rec['points_mm_layer'])
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(fn),b)
