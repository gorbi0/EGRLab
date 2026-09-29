"""Lock short watchdog analog tracks and local VDD-to-decoupler traces before general routing."""
from pathlib import Path
import pcbnew as p,json,math
P=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(P/'eda/P04.kicad_pcb'));mm=p.FromMM
f={q.GetReference():q for q in b.GetFootprints()}
def pad(ref,n):return next(q for q in f[ref].Pads() if q.GetNumber()==str(n))
def xy(q):return tuple(round(p.ToMM(v),5) for v in (q.x,q.y))
def route(net,pts,w=.4):
 ns=[n for n in b.GetNetsByNetcode().values() if n.GetNetname().split('/')[-1]==net];assert len(ns)==1,(net,len(ns));n=ns[0]
 for a,c in zip(pts,pts[1:]):
  if a==c:continue
  t=p.PCB_TRACK(b);t.SetStart(p.VECTOR2I(mm(a[0]),mm(a[1])));t.SetEnd(p.VECTOR2I(mm(c[0]),mm(c[1])))
  t.SetLayer(p.F_Cu);t.SetWidth(mm(w));t.SetNet(n);t.SetLocked(True);b.Add(t)
route('WD_RC',[(121.62,55.54),(127,55.54)])
route('WD_RC',[(127,55.54),(127,51),(126,50)])
route('WD_C',[(121.62,58.08),(123.5,58.08),(125.96,60.54),(127,60.54)])
links=[]
for i in range(1,12):
 vp=16 if i==1 else (2 if i==11 else 14)
 a=xy(pad(f'U{i}',vp).GetPosition());c=xy(pad(f'C{i+3}',1).GetPosition())
 # 45-degree jog followed by orthogonal finish; deliberately short, verify native DRC before routing.
 dx,dy=c[0]-a[0],c[1]-a[1];k=min(abs(dx),abs(dy));mid=(a[0]+math.copysign(k,dx),a[1]+math.copysign(k,dy))
 route('3V3_IO',[a,mid,c],.4);links.append({'ic':f'U{i}','cap':f'C{i+3}','distance_mm':round(math.dist(a,c),3)})
nc=b.GetDesignSettings().m_NetSettings.GetDefaultNetclass();nc.SetClearance(mm(.25));nc.SetTrackWidth(mm(.3));nc.SetViaDiameter(mm(.8));nc.SetViaDrill(mm(.4))
b.BuildConnectivity();p.SaveBoard(str(P/'eda/P04.kicad_pcb'),b)
assert p.ExportSpecctraDSN(b,str(P/'routing/P04.dsn'))
(P/'verification/decoupling-targets.json').write_text(json.dumps(links,indent=2))
print('Critical analog and local VDD tracks locked; DSN exported.')
