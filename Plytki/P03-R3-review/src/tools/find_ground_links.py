from pathlib import Path
import pcbnew as p,math,json
P=Path(__file__).resolve().parents[2];b=p.LoadBoard(str(P/'eda/P03.kicad_pcb'))
def xy(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
fills={L:[z.GetFilledPolysList(L) for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname()=='GND' and z.IsOnLayer(L)] for L in [p.F_Cu,p.B_Cu]}
rows=[]
for r,pn,bounds in [('C13','2',(58.775,19.75,62.985,25.631)),('U5','2',(66.725,14.078,69.278,22.235))]:
 f=b.FindFootprintByReference(r);a=next(a for a in f.Pads() if a.GetNumber()==pn);pos=(p.ToMM(a.GetPosition().x),p.ToMM(a.GetPosition().y))
 qs=[]
 for ix in range(math.ceil(bounds[0]*4),math.floor(bounds[2]*4)+1):
  for iy in range(math.ceil(bounds[1]*4),math.floor(bounds[3]*4)+1):
   q=(ix/4,iy/4)
   pts=[xy(q[0]+.45*math.cos(i*math.tau/16),q[1]+.45*math.sin(i*math.tau/16)) for i in range(16)]
   via=p.SHAPE_CIRCLE(xy(*q),p.FromMM(.4))
   if any(pad.GetEffectiveShape(p.F_Cu).Collide(via,p.FromMM(.2)) for f in b.GetFootprints() for pad in f.Pads()):continue
   if all(any(all(ps.Contains(v) for v in pts) for ps in fills[L]) for L in fills):qs.append(q)
 assert qs,r
 q=min(qs,key=lambda q:math.dist(q,pos));print(r,q,math.dist(q,pos));rows.append({'x':q[0],'y':q[1],'reason':r+' isolated local GND island'})
(P/'src/ground-links.json').write_text(json.dumps(rows,indent=2)+'\n')
