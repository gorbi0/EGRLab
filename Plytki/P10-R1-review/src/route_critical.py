"""Locked short CAN entry/TVS paths and local supply capacitors; no termination or filter stubs."""
from pathlib import Path
import pcbnew as p,json,math
P=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(P/'eda/P10.kicad_pcb'));mm=p.FromMM
f={x.GetReference():x for x in b.GetFootprints()}
def pad(r,n):return next(a for a in f[r].Pads() if a.GetNumber()==str(n))
def pt(r,n):a=pad(r,n).GetPosition();return (round(p.ToMM(a.x),5),round(p.ToMM(a.y),5))
def xy(a):return p.VECTOR2I(mm(a[0]),mm(a[1]))
records=[]
def route(net,pts,w=.3):
 n=next(n for n in b.GetNetsByNetcode().values() if n.GetNetname().split('/')[-1]==net)
 for a,z in zip(pts,pts[1:]):
  if a==z:continue
  t=p.PCB_TRACK(b);t.SetNet(n);t.SetWidth(mm(w));t.SetLayer(p.F_Cu);t.SetStart(xy(a));t.SetEnd(xy(z));t.SetLocked(True);b.Add(t)
 records.append({'net':net,'layer':'F.Cu','width_mm':w,'points':pts})
route('CAN_H',[pt('J3',1),(45,51.4875),pt('D1',2),(44.9,49.4875),(44.9,47.965),(43.635,46.7),pt('U1',7)])
route('CAN_L',[pt('J3',2),(41.5,50.9875),pt('D1',1),(41.1,49.4875),(41.1,47.965),(42.365,46.7),pt('U1',6)])
route('GND',[pt('D1',3),(42.8625,48.7),(42.1,48.7)],.6)
v=p.PCB_VIA(b);v.SetPosition(xy((42.1,48.7)));v.SetWidth(mm(.8));v.SetDrill(mm(.4));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(b.FindNet('GND'));v.SetLocked(True);b.Add(v)
links=[]
for u,pin,c,rail in [('U1',3,'C1','5V_SYS'),('U1',5,'C2','3V3_IO'),('U2',14,'C3','3V3_IO')]:
 a=pt(u,pin);z=pt(c,1);k=min(abs(z[0]-a[0]),abs(z[1]-a[1]));mid=(a[0]+math.copysign(k,z[0]-a[0]),a[1]+math.copysign(k,z[1]-a[1]));route(rail,[a,mid,z]);links.append({'ic':u,'pin':pin,'cap':c,'distance_mm':round(math.dist(a,z),3)})
nc=b.GetDesignSettings().m_NetSettings.GetDefaultNetclass();nc.SetClearance(mm(.25));nc.SetTrackWidth(mm(.3));nc.SetViaDiameter(mm(.8));nc.SetViaDrill(mm(.4))
b.BuildConnectivity();p.SaveBoard(str(P/'eda/P10.kicad_pcb'),b);assert p.ExportSpecctraDSN(b,str(P/'routing/P10.dsn'))
(P/'verification/critical-paths.json').write_text(json.dumps(records,indent=2));(P/'verification/decoupling-targets.json').write_text(json.dumps(links,indent=2))
