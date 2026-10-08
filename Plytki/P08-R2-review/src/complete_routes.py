"""Complete connections missed by router/plane fill. Exact paths are stored for review.
Conservative raster path search only proposes copper. Native KiCad DRC is authoritative.
Default replays reviewed completion-routes.json. --plan regenerates the candidate paths.
R2: --plan takes the pairs from a fresh native DRC (unconnected items, matched by UUID) instead of a
hard-coded list, because every new router run leaves different gaps; starved thermals are handled by
run_layout.py (cleanup.py with the pads named by DRC), not here.
P02 R4 (29.09, klasa L): the path starts and ends only on the copper layers of its end items (an SMD pad exists on one
layer); before, a B.Cu path could end in the centre of an F.Cu SMD pad without a via (three such stubs in the first run).
The records are written also when items stay unconnected (exit 3), so a partial completion can be replayed.
"""
from pathlib import Path
import pcbnew as p,json,math,heapq,sys,os,subprocess
from PIL import Image,ImageDraw,ImageFilter
import numpy as np
P=Path(__file__).resolve().parents[1]
from board import NAME, SIGNAL_W, CORE, PWR as BOARD_PWR, PLANNER_KEEPOUT, TOP_ONLY
from build_board import W as BW,Hh as BH
fn=P/f'eda/{NAME}.kicad_pcb';b=p.LoadBoard(str(fn));mm=p.FromMM
# 30.09 evening: 0.05 mm raster (was 0.1) and exact obstacle growth. The old 0.5 mm dilation of every obstacle kept a 0.2 mm
# track 0.4 mm from other copper (0.25 needed) and hid the last paths in the dense areas once signals went to 0.2 mm.
R=int(os.environ.get('EGRLAB_PLAN_RES','20'));W=int(BW*R)+1;H=int(BH*R)+1
MARGIN=.05;VIA_R=.45;PWRN=tuple(BOARD_PWR)   # widths and clearances from board.py (P03 R6 had them fixed)
import board as _bd;ISO={k:min(v,.5) for k,v in getattr(_bd,'ISOLATE',{}).items()}   # 2.10: own clearance of P05 VBAT_SENSE (router 0.8; the planner
# had routed it 0.35 mm from a TAP and finds no path at 0.8 through the left column: 0.5 here)
def clr(name):return max(.30 if name in PWRN else .25,ISO.get(name.split('/')[-1],0))
def width_of(name):return .6 if name in PWRN else (.3 if name in tuple(CORE) else SIGNAL_W)   # 2.10: PWR class 0.6 mm (C17 link on P06 came out 0.3)
def grown(ps,d):
 q=p.SHAPE_POLY_SET(ps);q.Inflate(mm(d),p.CORNER_STRATEGY_ROUND_ALL_CORNERS,mm(.005));return q
f={q.GetReference():q for q in b.GetFootprints()}
def pad(ref,n):return next(q for q in f[ref].Pads() if q.GetNumber()==str(n))
def xy(v):return [p.ToMM(v.x),p.ToMM(v.y)]
def drawpoly(d,ps,holes=False):
 for k in range(ps.OutlineCount()):
  o=ps.Outline(k);d.polygon([(p.ToMM(o.CPoint(i).x)*R,p.ToMM(o.CPoint(i).y)*R) for i in range(o.PointCount())],fill=255)
  if holes:
   for h in range(ps.HoleCount(k)):
    o=ps.Hole(k,h);d.polygon([(p.ToMM(o.CPoint(i).x)*R,p.ToMM(o.CPoint(i).y)*R) for i in range(o.PointCount())],fill=0)
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
  if best is not None:drawpoly(d,grown(best,-.6),holes=True)   # 0.6 mm inside the fill edge
  masks.append(np.array(im)!=0)
 return masks
def plan(net,sxy,gxy,goalmask=None,slay=(0,1),glay=(0,1)):
 """gxy None: the goal is the net's main pour (a pad cut off from the fill, reported by DRC against the zone).
 goalmask (P02 R4): per-layer boolean masks of the copper the path may end on.
 slay / glay (P02 R4): copper layers (0 F.Cu, 1 B.Cu) of the start and end items; the path starts and ends only there."""
 goal=goalmask if goalmask is not None else (fillmask(net) if gxy is None else None)
 if goalmask is not None:gxy=None
 name=b.GetNetsByNetcode()[net].GetNetname();w=width_of(name);cn=clr(name);obs=[];vmask=[]
 for layer in [p.F_Cu,p.B_Cu]:
  it=Image.new('L',(W,H));dt=ImageDraw.Draw(it);iv=Image.new('L',(W,H));dv=ImageDraw.Draw(iv)  # forbidden for a track centre / a via centre
  def block(o):
   c=max(cn,clr(o.GetNetname()))
   ps=p.SHAPE_POLY_SET();o.TransformShapeToPolygon(ps,layer,mm(c+w/2+MARGIN),mm(.005),p.ERROR_OUTSIDE);drawpoly(dt,ps)
   ps=p.SHAPE_POLY_SET();o.TransformShapeToPolygon(ps,layer,mm(c+VIA_R+MARGIN),mm(.005),p.ERROR_OUTSIDE);drawpoly(dv,ps)
  def hole(q,r):   # a new via keeps 0.3 mm hole to hole also from the holes of its own net (30.09: one landed 0.25 mm from a fan-out via)
   x,y=xy(q.GetPosition());rr=r/2+.2+.3+MARGIN;dv.ellipse([(x-rr)*R,(y-rr)*R,(x+rr)*R,(y+rr)*R],fill=255)
  for fp in b.GetFootprints():
   for q in fp.Pads():
    if q.GetNetCode()!=net and q.IsOnLayer(layer):block(q)
    elif q.GetNetCode()==net:
     if q.GetDrillSize().x>0:hole(q,p.ToMM(q.GetDrillSize().x))
     elif q.IsOnLayer(layer):ps=p.SHAPE_POLY_SET();q.TransformShapeToPolygon(ps,layer,mm(VIA_R+.1),mm(.005),p.ERROR_OUTSIDE);drawpoly(dv,ps)   # no via in its own SMD pad
  for t in b.GetTracks():
   if t.GetNetCode()!=net and (isinstance(t,p.PCB_VIA) or t.GetLayer()==layer):block(t)
   elif t.GetNetCode()==net and isinstance(t,p.PCB_VIA):hole(t,p.ToMM(t.GetDrillValue()))
  for zone in b.Zones():
   if zone.GetIsRuleArea() and zone.GetZoneName().startswith('DRC_ONLY'):continue   # 2.10: DRC rule areas (import_routing.py), no restriction
   if zone.GetIsRuleArea() and zone.IsOnLayer(layer):drawpoly(dt,grown(zone.Outline(),w/2+MARGIN));drawpoly(dv,grown(zone.Outline(),VIA_R+MARGIN))  # P02 R4: only on the layers of the rule area
   elif not zone.GetIsRuleArea() and zone.GetNetCode()!=net and zone.GetNetname()!='GND' and zone.IsOnLayer(layer):  # P02 R4: never cut a power pour
    c=max(cn,clr(zone.GetNetname()));fl=zone.GetFilledPolysList(layer);drawpoly(dt,grown(fl,c+w/2+MARGIN));drawpoly(dv,grown(fl,c+VIA_R+MARGIN))
  for kl,x0,y0,x1,y1 in PLANNER_KEEPOUT:   # P05 R3: the router-only keepouts of board.py (U1 interior, analog B.Cu) bind the planner too
   if (kl=='F.Cu')==(layer==p.F_Cu):
    gt=w/2+MARGIN;gv=VIA_R+MARGIN;dt.rectangle([(x0-gt)*R,(y0-gt)*R,(x1+gt)*R,(y1+gt)*R],fill=255);dv.rectangle([(x0-gv)*R,(y0-gv)*R,(x1+gv)*R,(y1+gv)*R],fill=255)
  dt.rectangle([0,0,W-1,H-1],outline=255,width=int(math.ceil((.5+w/2+MARGIN)*R)))   # copper 0.5 mm from the board edge
  dv.rectangle([0,0,W-1,H-1],outline=255,width=int(math.ceil((.5+VIA_R+MARGIN)*R)))
  obs.append(np.array(it)!=0);vmask.append(np.array(iv)!=0)
 via=vmask[0]|vmask[1]
 if name.split('/')[-1] in TOP_ONLY:obs[1][:]=True;via[:]=True   # review 2.10: board.TOP_ONLY nets stay on F.Cu (no B.Cu, no via)
 s=tuple(round(v*R) for v in sxy);g=tuple(round(v*R) for v in gxy) if goal is None else None
 def h(x,y):
  if g is None:return 0
  dx=abs(x-g[0]);dy=abs(y-g[1]);return max(dx,dy)+.41421356*min(dx,dy)
 def key(x,y,l):return (l*H+y)*W+x
 starts={key(*s,l) for l in slay};todo=[(h(*s),0,q) for q in starts];heapq.heapify(todo);cost={q:0 for q in starts};prev={};end=None
 while todo:
  _,dist,q=heapq.heappop(todo)
  if dist!=cost.get(q):continue
  x=q%W;y=(q//W)%H;l=q//(W*H)
  if ((x,y)==g and l in glay) if goal is None else goal[l][y,x]:end=q;break
  nxt=[]
  for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
   nx,ny=x+dx,y+dy
   if 0<=nx<W and 0<=ny<H and not obs[l][ny,nx] and not obs[l][y,nx] and not obs[l][ny,x]:nxt.append((nx,ny,l,1.41421356237 if dx and dy else 1))
  if not via[y,x]:nxt.append((x,y,1-l,8*R))   # a via costs 8 mm of track
  for nx,ny,nl,dc in nxt:
   nk=key(nx,ny,nl);nd=dist+dc
   if nd<cost.get(nk,1e99):cost[nk]=nd;prev[nk]=q;heapq.heappush(todo,(nd+h(nx,ny),nd,nk))
 if end is None:
  print(f'no completion path for net {net} {sxy} -> {gxy}');return None
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
   assert a[:2]==c[:2];t=p.PCB_VIA(b);t.SetPosition(p.VECTOR2I(mm(a[0]),mm(a[1])));t.SetWidth(mm(.9));t.SetDrill(mm(.4));t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu)
  else:
   t=p.PCB_TRACK(b);t.SetStart(p.VECTOR2I(mm(a[0]),mm(a[1])));t.SetEnd(p.VECTOR2I(mm(c[0]),mm(c[1])));t.SetWidth(mm(width_of(net.GetNetname())));t.SetLayer(p.F_Cu if a[2]==0 else p.B_Cu)  # width from board.py (P03 R6 30.09: signals 0.2 mm, obstacles still kept for 0.3)
  t.SetNet(net);t.SetLocked(True);b.Add(t)
target=P/'routing/completion-routes.json';records=[];gnd_islands=[]
def cluster_mask(code,uuid):
 """Copper of net `code` that is not connected to the item `uuid` (KiCad connectivity), per layer, 0.1 mm inside its edge."""
 start=None
 for fp in b.GetFootprints():
  for q in fp.Pads():
   if q.m_Uuid.AsString()==uuid:start=q
 for t in b.GetTracks():
  if t.m_Uuid.AsString()==uuid:start=t
 if start is None:return None
 b.BuildConnectivity();con={x.m_Uuid.AsString() for x in b.GetConnectivity().GetConnectedItems(start)}|{uuid}
 masks=[];anything=False
 for layer in [p.F_Cu,p.B_Cu]:
  im=Image.new('L',(W,H));d=ImageDraw.Draw(im)
  items=[q for fp in b.GetFootprints() for q in fp.Pads()]+list(b.GetTracks())
  for it in items:
   if it.GetNetCode()!=code or it.m_Uuid.AsString() in con:continue
   if isinstance(it,p.PAD) and not it.IsOnLayer(layer):continue
   if isinstance(it,p.PCB_TRACK) and not isinstance(it,p.PCB_VIA) and it.GetLayer()!=layer:continue
   ps=p.SHAPE_POLY_SET();it.TransformShapeToPolygon(ps,layer,0,mm(.005),p.ERROR_INSIDE);drawpoly(d,grown(ps,-.3));anything=True
  for z in b.Zones():  # P02 R4: pour islands of the net that are not connected to the start count as goal too
   if z.GetIsRuleArea() or z.GetNetCode()!=code or not z.IsOnLayer(layer) or z.m_Uuid.AsString() in con:continue
   drawpoly(d,grown(z.GetFilledPolysList(layer),-.3));anything=True
  masks.append(np.array(im)!=0)   # 0.3 mm inside the copper edge
 return masks if anything else None
def main_mask(code):
 """Copper of the largest cluster of net `code` (pads, tracks, vias, pour pieces), per layer, 0.3 mm inside its edge: an orphan
 island must reach this, not another island (30.09: U4.3 was joined to a second island and came back next round)."""
 b.BuildConnectivity();con=b.GetConnectivity();pads=[q for fp in b.GetFootprints() for q in fp.Pads() if q.GetNetCode()==code];best=None
 for q in pads:
  ids={x.m_Uuid.AsString() for x in con.GetConnectedItems(q)}|{q.m_Uuid.AsString()}
  n=sum(1 for x in pads if x.m_Uuid.AsString() in ids)
  if best is None or n>best[0]:best=(n,ids)
 if best is None:return None
 ids=best[1];masks=[]
 for layer in [p.F_Cu,p.B_Cu]:
  im=Image.new('L',(W,H));d=ImageDraw.Draw(im)
  for it in pads+[t for t in b.GetTracks() if t.GetNetCode()==code]:
   if it.m_Uuid.AsString() not in ids:continue
   if isinstance(it,p.PAD) and not it.IsOnLayer(layer):continue
   if isinstance(it,p.PCB_TRACK) and not isinstance(it,p.PCB_VIA) and it.GetLayer()!=layer:continue
   ps=p.SHAPE_POLY_SET();it.TransformShapeToPolygon(ps,layer,0,mm(.005),p.ERROR_INSIDE);drawpoly(d,grown(ps,-.3))
  for z in b.Zones():   # pour pieces that touch the main cluster
   if z.GetIsRuleArea() or z.GetNetCode()!=code or not z.IsOnLayer(layer):continue
   fl=z.GetFilledPolysList(layer)
   for k in range(fl.OutlineCount()):
    one=p.SHAPE_POLY_SET();one.AddOutline(fl.Outline(k))
    for h in range(fl.HoleCount(k)):one.AddHole(fl.Hole(k,h))
    if any(it.m_Uuid.AsString() in ids and (isinstance(it,p.PCB_VIA) or (isinstance(it,p.PAD) and it.IsOnLayer(layer))) and one.Contains(it.GetPosition()) for it in pads+list(b.GetTracks())):
     drawpoly(d,grown(one,-.3),holes=True)
  masks.append(np.array(im)!=0)
 return masks
def gnd_orphans():
 """GND pads that KiCad connectivity does not join to the largest GND pad cluster (geometric order)."""
 b.BuildConnectivity();con=b.GetConnectivity();pads=[q for fp in b.GetFootprints() for q in fp.Pads() if q.GetNetname()=='GND'];seen={};cls=[]
 for q in sorted(pads,key=lambda q:xy(q.GetPosition())):
  u=q.m_Uuid.AsString()
  if u in seen:continue
  ids={x.m_Uuid.AsString() for x in con.GetConnectedItems(q)}|{u};grp=[x for x in pads if x.m_Uuid.AsString() in ids]
  for x in grp:seen[x.m_Uuid.AsString()]=len(cls)
  cls.append(grp)
 if len(cls)<2:return []
 big=max(range(len(cls)),key=lambda k:len(cls[k]))
 return [cl[0] for k,cl in enumerate(cls) if k!=big]   # one pad per orphan cluster
def has_pour(code):
 return any(not z.GetIsRuleArea() and z.GetNetCode()==code for z in b.Zones())
def orphan_pads(code):
 """Pads of a net that lie on neither the largest F.Cu nor the largest B.Cu fill polygon of that net."""
 big={}
 for layer in [p.F_Cu,p.B_Cu]:
  best=None
  for z in b.Zones():
   if z.GetIsRuleArea() or z.GetNetCode()!=code or not z.IsOnLayer(layer):continue
   ps=z.GetFilledPolysList(layer)
   for i in range(ps.OutlineCount()):
    one=p.SHAPE_POLY_SET();one.AddOutline(ps.Outline(i))
    for h in range(ps.HoleCount(i)):one.AddHole(ps.Hole(i,h))
    if best is None or one.Area()>best.Area():best=one
  big[layer]=best
 out=[]
 for fp in sorted(b.GetFootprints(),key=lambda f:f.GetReference()):
  for q in fp.Pads():
   if q.GetNetCode()!=code:continue
   on=[L for L in big if big[L] is not None and q.IsOnLayer(L) and big[L].Contains(q.GetPosition())]
   if not on:out.append((q,(f'{fp.GetReference()}.{q.GetNumber()}',xy(q.GetPosition()),pad_layers(q))))
 return out
def pad_layers(q):
 return tuple(i for i,L in enumerate([p.F_Cu,p.B_Cu]) if q.IsOnLayer(L))
def endpoint(uuid,pos):
 """Pad centre for a pad, the DRC marker position for a track/via end; (item label, xy, net code, copper layers)."""
 for fp in b.GetFootprints():
  for q in fp.Pads():
   if q.m_Uuid.AsString()==uuid:return f'{fp.GetReference()}.{q.GetNumber()}',xy(q.GetPosition()),q.GetNetCode(),pad_layers(q)
 for t in b.GetTracks():
  if t.m_Uuid.AsString()==uuid:
   ends=[xy(t.GetPosition())] if isinstance(t,p.PCB_VIA) else [xy(t.GetStart()),xy(t.GetEnd())]
   lay=(0,1) if isinstance(t,p.PCB_VIA) else ((0,) if t.GetLayer()==p.F_Cu else (1,))
   return ('via' if isinstance(t,p.PCB_VIA) else 'track')+'@'+t.GetNetname(),min(ends,key=lambda e:math.dist(e,pos)),t.GetNetCode(),lay
 for z in b.Zones():
  if z.m_Uuid.AsString()==uuid:return 'pour@'+z.GetNetname(),None,z.GetNetCode(),(0,1)
 sys.exit(f'unconnected item {uuid} is neither a pad, a track nor a zone: plan by hand')
def blocked(pt,lay):
 """P05 R3: a point inside a router-only keepout (board.PLANNER_KEEPOUT) on every one of its copper layers."""
 return all(any(x0<=pt[0]<=x1 and y0<=pt[1]<=y1 for kl,x0,y0,x1,y1 in PLANNER_KEEPOUT if (kl=='F.Cu')==(L==0)) for L in lay)
def escape(uid,sxy,lay,toward):
 """P05 R3: an end inside the keepouts (a U1 pin) starts from the free end of its own locked escape instead: the copper end of its
 cluster outside the keepouts nearest to the other end (the planner may not draw inside them)."""
 if sxy is None or not blocked(sxy,lay):return sxy,lay
 item=next((q for fp in b.GetFootprints() for q in fp.Pads() if q.m_Uuid.AsString()==uid),None) or next((t for t in b.GetTracks() if t.m_Uuid.AsString()==uid),None)
 if item is None:return sxy,lay
 b.BuildConnectivity();cands=[]
 for x in b.GetConnectivity().GetConnectedItems(item):
  if isinstance(x,p.PCB_VIA):
   if not blocked(xy(x.GetPosition()),(0,1)):cands.append((xy(x.GetPosition()),(0,1)))
  elif isinstance(x,p.PCB_TRACK):
   L=(0,) if x.GetLayer()==p.F_Cu else (1,)
   for e in (x.GetStart(),x.GetEnd()):
    if not blocked(xy(e),L):cands.append((xy(e),L))
 if not cands:return sxy,lay
 return min(cands,key=lambda c:math.dist(c[0],toward) if toward else 0)
if '--ties' in sys.argv:
 # 2.10 (review F2 / MAJOR-1, return-path check of verify_pcb.py): a decoupling capacitor whose GND pad reaches the GND pin of its part only
 # through more than 1.3 x the straight distance + 3 mm of GND copper (gndpath.py) gets a planned GND track pad -> pin, kept when the
 # track itself is within that limit. --ties --plan plans and records routing/return-ties.json; --ties alone replays it.
 from board import RETURN_PAIRS
 tgt=P/'routing/return-ties.json';ties=[]
 if '--plan' in sys.argv:
  import gndpath
  def pp(r,n_):q=pad(r,n_);return xy(q.GetPosition()),pad_layers(q)
  for cap,spec in RETURN_PAIRS.items():
   u,n_=spec[:2]
   p.ZONE_FILLER(b).Fill(b.Zones());cu,via=gndpath.copper(b,'GND',BW,BH)
   g=next(q for q in f[cap].Pads() if q.GetNetname()=='GND');(sxy,sl),(gxy,gl)=(xy(g.GetPosition()),pad_layers(g)),pp(u,n_)
   if len(spec)>2:gxy,gl=list(spec[2]),(0,1)   # goal: a GND via tied to the pin (pin in the planner keepouts)
   lim=1.3*math.dist(sxy,gxy)+3;now=gndpath.distances(cu,via,gndpath.pad_point(b,cap,g.GetNumber()),{'d':gndpath.pad_point(b,u,n_)},limit_mm=150)['d']
   if now is not None and now<=lim:continue
   pts=plan(g.GetNetCode(),sxy,gxy,slay=sl,glay=gl)
   L=None if pts is None else sum(math.dist(a[:2],c[:2]) for a,c in zip(pts,pts[1:]))
   print('return tie',cap,'->',f'{u}.{n_}','copper',now,'limit',round(lim,1),'planned',None if L is None else round(L,1),flush=True)
   if pts is None or (L>lim and not (now is None or L<.8*now)):continue   # kept when within the limit or 20 % shorter than the copper path
   ties.append({'from':f'{cap}.{g.GetNumber()}','to':f'{u}.{n_}','copper_before_mm':now,'points_mm_layer':pts});add(g.GetNet(),pts)
  tgt.write_text(json.dumps(ties,indent=2))
 else:
  for t in json.loads(tgt.read_text()):add(b.FindNet('GND'),t['points_mm_layer'])
elif '--plan' in sys.argv:
 # Rounds: a pad cluster joined to the pour can reveal the next cluster (DRC reports one edge per cluster), so
 # plan, refill, save and ask native DRC again until nothing is left unconnected.
 CLI=os.environ.get('KICAD_CLI',str(Path(sys.executable).with_name('kicad-cli.exe')));rep=P/'routing/precompletion-drc.json'
 for rnd in range(1,11):
  subprocess.run([CLI,'pcb','drc','--format','json','--severity-all','--refill-zones','-o',str(rep),str(fn)],check=True,stdout=subprocess.DEVNULL)
  todo=json.loads(rep.read_text())['unconnected_items']
  todo=[u for u in todo if not all('[GND]' in i['description'] and ('Strefa' in i['description'] or 'Zone' in i['description']) for i in u['items'])]
  orphans=gnd_orphans()   # 30.09: GND pads outside the main GND cluster (a pour island DRC reports only as zone <-> zone)
  if not todo and not orphans:break
  done=set()  # DRC can list one pad against the pour of each layer: one completion per pad and round is enough
  ok_n=0;fail=[]
  for q in orphans:
   lab=f'{q.GetParentFootprint().GetReference()}.{q.GetNumber()}';m=main_mask(q.GetNetCode());done.add(lab);points=None
   b.BuildConnectivity();own=[x for x in b.GetConnectivity().GetConnectedItems(q) if isinstance(x,p.PCB_VIA)]
   for sxy,sl in [(xy(q.GetPosition()),pad_layers(q))]+sorted((xy(v.GetPosition()),(0,1)) for v in own):   # the pad first, then the vias of its cluster
    points=plan(q.GetNetCode(),sxy,None,m,slay=sl) if m is not None else None
    if points is not None:break
   if points is None:fail.append(lab);print('skipped (no path this round): GND island',lab,flush=True);continue
   records.append({'round':rnd,'net':'GND','from':lab,'to':'main GND cluster','points_mm_layer':points});add(q.GetNet(),points);ok_n+=1
   print('Completion round',rnd,lab,'-> main GND cluster',len(points),'vertices',flush=True);break   # one per round: the next DRC sees the joined island
  for u in todo:
   ends=sorted([endpoint(i['uuid'],(i['pos']['x'],i['pos']['y']))+(i['uuid'],) for i in u['items']],key=lambda e:e[1] is None)
   (la,sa,na,ya,ua),(lz,sz,nz,yz,uz)=ends;assert na==nz,(la,lz);net=b.GetNetsByNetcode()[na]
   sa,ya=escape(ua,sa,ya,sz);sz,yz=escape(uz,sz,yz,sa)   # P05 R3: U1 pins sit inside the keepouts
   if sa is None and net.GetNetname()=='GND':
    gnd_islands.append(rnd);continue   # P02 R4: GND pour islands are tied by stitch.py (run_layout.py re-checks with DRC)
   if sa is None:
    # P02 R4: pour <-> pour: every pad of the net that no largest island (F.Cu or B.Cu) reaches is joined to it
    for q,(lab,pxy,play) in orphan_pads(na):
     if lab in done:continue
     done.add(lab);points=plan(na,pxy,None,slay=play)
     if points is None:fail.append(lab);continue
     records.append({'round':rnd,'net':net.GetNetname(),'from':lab,'to':'largest pour island','points_mm_layer':points});add(net,points);ok_n+=1
     print('Completion round',rnd,lab,'-> largest island',len(points),'vertices',flush=True)
    continue
   if sz is None and la in done:continue
   done.add(la);points=plan(na,sa,sz,slay=ya,glay=yz);to=lz
   if points is None:  # P02 R4: any copper of the other part of the net (KiCad connectivity), from either end
    for lab,pxy,uid_,lay_ in [(la,sa,ua,ya)]+([(lz,sz,uz,yz)] if sz is not None else []):
     m=cluster_mask(na,uid_)
     if m is not None:
      points=plan(na,pxy,None,m,slay=lay_)
      if points is not None:to='other part of '+net.GetNetname();la=lab;break
   if points is None and has_pour(na):
    points=plan(na,sa,None,slay=ya);to='largest pour island'
   if points is None:fail.append(la);print('skipped (no path this round):',net.GetNetname(),la,flush=True);continue
   records.append({'round':rnd,'net':net.GetNetname(),'from':la,'to':to,'points_mm_layer':points});add(net,points);ok_n+=1
   print('Completion round',rnd,la,to,len(points),'vertices',flush=True)
  if fail and not ok_n:print('no completion path for',fail);target.write_text(json.dumps(records,indent=2));sys.exit(3)
  b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(fn),b)
 else:print('unconnected items remain after 10 completion rounds');target.write_text(json.dumps(records,indent=2));sys.exit(3)
 target.write_text(json.dumps(records,indent=2))
else:
 for rec in json.loads(target.read_text()):add(b.FindNet(rec['net']),rec['points_mm_layer'])
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(fn),b)
