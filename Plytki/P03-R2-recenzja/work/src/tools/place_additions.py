"""One-time placement of R2 additions around the frozen R1 modules/connectors.
Writes placement.json, which is the reviewed release input. Not called during reproduction.
"""
from pathlib import Path
import pcbnew as p,json,math,numpy as np
P=Path(__file__).resolve().parents[2];b=p.LoadBoard(str(P/'eda/P03.kicad_pcb'))
fmap={f.GetReference():f for f in b.GetFootprints()};d=json.loads((P/'src/placement.json').read_text())
parts=json.loads((P/'docs/parts.json').read_text())
new={r for r,v in parts.items() if v['source_ref'].startswith('ADDED_R2')}
fixed=set(fmap)-new
def xy(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def pos(a):return np.array([p.ToMM(a.x),p.ToMM(a.y)])
def box(f):
 f.BuildCourtyardCaches();a=f.GetCourtyard(p.F_CrtYd).BBox()
 return [p.ToMM(a.GetLeft()),p.ToMM(a.GetTop()),p.ToMM(a.GetRight()),p.ToMM(a.GetBottom())]
def put(r,x,y,ang=0):
 f=fmap[r];f.SetPosition(xy(x,y));f.SetOrientationDegrees(ang);d[r]=[x,y,ang]
put('R13',117.6,61.8,90)
for r,x,y,a in [('U5',67,21,180),('Q1',63.5,18,0),('C13',61.5,24,90),('C14',68,26.5,0),
                 ('U4',134,57,0),('C12',138.8,56.05,0)]:
 put(r,x,y,a);fixed.add(r);new.remove(r)
obs=[box(fmap[r]) for r in fixed if not r.startswith('H')]
for z in b.Zones():
 if z.GetIsRuleArea():
  bb=z.Outline().BBox();obs.append([p.ToMM(bb.GetLeft()),p.ToMM(bb.GetTop()),p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom())])
for r in [f'H{i}' for i in range(1,6)]:
 q=pos(fmap[r].GetPosition());obs.append([q[0]-4.5,q[1]-4.5,q[0]+4.5,q[1]+4.5])
g=np.array([(x,y) for x in np.arange(7,153,.5) for y in np.arange(8,110,.5)])
order=['R36','R37','R38','R39','R40','R34','R35','TP7','TP8']+sorted(new-{'R36','R37','R38','R39','R40','R34','R35','TP7','TP8'})
for r in order:
 f=fmap[r];best=None
 # Aim at the functional buffer pin, not at distant MCU or ground connections.
 n=parts[r]['pins']['1'];goals=[]
 for rr in fixed:
  if not rr.startswith(('U','Q','M')):continue
  for a in fmap[rr].Pads():
   if a.GetNetname().split('/')[-1]==n:goals.append((0 if rr.startswith(('U','Q')) else 1,pos(a.GetPosition())))
 if goals:
  goals.sort(key=lambda a:a[0]);target=goals[0][1]
 else:target=pos(f.GetPosition())
 for ang in [0,90,180,270]:
  f.SetPosition(xy(0,0));f.SetOrientationDegrees(ang);bx=np.array(box(f))
  pin=next(a for a in f.Pads() if a.GetNumber()=='1');po=pos(pin.GetPosition())
  boxes=np.c_[g[:,0]+bx[0],g[:,1]+bx[1],g[:,0]+bx[2],g[:,1]+bx[3]]
  valid=(boxes[:,0]>=1)&(boxes[:,1]>=1)&(boxes[:,2]<=159)&(boxes[:,3]<=119)
  for o in obs:
   gap=.65
   valid &= (boxes[:,2]+gap<=o[0])|(boxes[:,0]-gap>=o[2])|(boxes[:,3]+gap<=o[1])|(boxes[:,1]-gap>=o[3])
  ds=np.linalg.norm(g+po-target,axis=1)
  if r in ['R36','R37','R38','R39','R40']:valid&=ds<=11.5
  ix=np.flatnonzero(valid)
  if len(ix)==0:continue
  # Prefer a short first connection and modest relocation, horizontal body if tied.
  cost=ds[ix]+.03*np.linalg.norm(g[ix]-np.array(d[r][:2]),axis=1)+(.1 if ang%180 else 0)
  k=ix[cost.argmin()];v=(cost.min(),g[k,0],g[k,1],ang)
  if best is None or v<best:best=v
 assert best,(r,'no placement')
 _,x,y,ang=best;put(r,float(x),float(y),ang);fixed.add(r);obs.append(box(f));print(r,d[r], 'pin1 distance',round(np.linalg.norm(pos(next(a for a in f.Pads() if a.GetNumber()=='1').GetPosition())-target),2))
(P/'src/placement.json').write_text(json.dumps(d,indent=2)+'\n')
