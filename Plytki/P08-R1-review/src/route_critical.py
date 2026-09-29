"""Lock short TPS paths and IC decoupling before autorouting. All units mm."""
from pathlib import Path
import pcbnew as p,json,math
P=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(P/'eda/P08.kicad_pcb'));mm=p.FromMM
f={x.GetReference():x for x in b.GetFootprints()}
def pad(r,n):return next(a for a in f[r].Pads() if a.GetNumber()==str(n))
def point(r,n):
 a=pad(r,n).GetPosition();return (round(p.ToMM(a.x),5),round(p.ToMM(a.y),5))
def xy(a):return p.VECTOR2I(mm(a[0]),mm(a[1]))
records=[]
def route(net,pts,w=.3):
 n=next(n for n in b.GetNetsByNetcode().values() if n.GetNetname().split('/')[-1]==net)
 for a,c in zip(pts,pts[1:]):
  if a==c:continue
  t=p.PCB_TRACK(b);t.SetNet(n);t.SetWidth(mm(w));t.SetLayer(p.F_Cu);t.SetStart(xy(a));t.SetEnd(xy(c));t.SetLocked(True);b.Add(t)
 records.append({'net':net,'layer':'F.Cu','width_mm':w,'points':pts})
def link(net,u,n,c,cn=1,w=.3):
 a=point(u,n);z=point(c,cn);dx,dy=z[0]-a[0],z[1]-a[1];k=min(abs(dx),abs(dy));mid=(a[0]+math.copysign(k,dx),a[1]+math.copysign(k,dy))
 route(net,[a,mid,z],w)
route('ILIM_232K',[point('U1',5),(30,30),(31,31),point('R1',1)])
route('SENSOR_FAULT_LOCAL_N',[point('U1',4),(29,30.95),(29,34.5)])
route('TPS_EN',[point('U1',3),(23,30.95),(22.25,31.7)])
route('GND',[point('U1',2),(23.8,30)])
v=p.PCB_VIA(b);v.SetPosition(xy((23.8,30)));v.SetWidth(mm(.8));v.SetDrill(mm(.4));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(b.FindNet('GND'));v.SetLocked(True);b.Add(v)
links=[]
for u,c,n,rail in [('U1','C1',1,'5V_SYS'),('U1','C2',6,'SENSOR_LIMITED'),('U3','C3',14,'3V3_IO'),('U4','C4',14,'3V3_IO'),('U5','C5',14,'3V3_IO'),('U6','C6',2,'3V3_IO'),('U7','C7',2,'5V_SYS'),('U8','C8',2,'3V3_IO'),('K1','C9',1,'5V_SYS')]:
 link(rail,u,n,c);links.append({'ic':u,'cap':c,'distance_mm':round(math.dist(point(u,n),point(c,1)),3)})
nc=b.GetDesignSettings().m_NetSettings.GetDefaultNetclass();nc.SetClearance(mm(.25));nc.SetTrackWidth(mm(.3));nc.SetViaDiameter(mm(.8));nc.SetViaDrill(mm(.4))
b.BuildConnectivity();p.SaveBoard(str(P/'eda/P08.kicad_pcb'),b)
assert p.ExportSpecctraDSN(b,str(P/'routing/P08.dsn'))
(P/'verification/critical-paths.json').write_text(json.dumps(records,indent=2));(P/'verification/decoupling-targets.json').write_text(json.dumps(links,indent=2))
print('TPS and decoupling routes locked; DSN exported')
