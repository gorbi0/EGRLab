"""Short IC supply paths locked before routing. No motor or thermocouple analog signal travels on this carrier."""
from pathlib import Path
import pcbnew as p,json,math
P=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(P/'eda/P09.kicad_pcb'));mm=p.FromMM
f={x.GetReference():x for x in b.GetFootprints()}
def pad(r,n):return next(a for a in f[r].Pads() if a.GetNumber()==str(n))
def point(r,n):
 a=pad(r,n).GetPosition();return (round(p.ToMM(a.x),5),round(p.ToMM(a.y),5))
def xy(a):return p.VECTOR2I(mm(a[0]),mm(a[1]))
records=[];links=[]
for u,c,n,rail in [('U1','C1',14,'3V3_IO'),('U2','C2',14,'3V3_IO'),('U3','C3',16,'3V3_IO'),('J3','C6',1,'TC1_VIN'),('J4','C7',1,'TC2_VIN')]:
 a=point(u,n);z=point(c,1);dx,dy=z[0]-a[0],z[1]-a[1];k=min(abs(dx),abs(dy));mid=(a[0]+math.copysign(k,dx),a[1]+math.copysign(k,dy));pts=[a,mid,z]
 net=next(n for n in b.GetNetsByNetcode().values() if n.GetNetname().split('/')[-1]==rail)
 for x,y in zip(pts,pts[1:]):
  if x==y:continue
  t=p.PCB_TRACK(b);t.SetNet(net);t.SetWidth(mm(.3));t.SetLayer(p.F_Cu);t.SetStart(xy(x));t.SetEnd(xy(y));t.SetLocked(True);b.Add(t)
 records.append({'net':rail,'layer':'F.Cu','width_mm':.3,'points':pts});links.append({'ic':u,'cap':c,'distance_mm':round(math.dist(a,z),3)})
nc=b.GetDesignSettings().m_NetSettings.GetDefaultNetclass();nc.SetClearance(mm(.25));nc.SetTrackWidth(mm(.3));nc.SetViaDiameter(mm(.8));nc.SetViaDrill(mm(.4))
b.BuildConnectivity();p.SaveBoard(str(P/'eda/P09.kicad_pcb'),b);assert p.ExportSpecctraDSN(b,str(P/'routing/P09.dsn'))
(P/'verification/critical-paths.json').write_text(json.dumps(records,indent=2));(P/'verification/decoupling-targets.json').write_text(json.dumps(links,indent=2))
