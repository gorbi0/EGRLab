"""Locked force copper, four-wire sensing, analog feedback and local decoupling.
Only these explicit paths carry motor current; router must not create their geometry.
"""
from pathlib import Path
import pcbnew as p,json,math
P=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(P/'eda/P06.kicad_pcb'));mm=p.FromMM
f={x.GetReference():x for x in b.GetFootprints()}
def pad(r,n):return next(a for a in f[r].Pads() if a.GetNumber()==str(n))
def point(r,n):
 a=pad(r,n).GetPosition();return (round(p.ToMM(a.x),5),round(p.ToMM(a.y),5))
def xy(a):return p.VECTOR2I(mm(a[0]),mm(a[1]))
records=[]
def route(net,pts,w=.3,L=p.F_Cu):
 ns=[n for n in b.GetNetsByNetcode().values() if n.GetNetname().split('/')[-1]==net];assert len(ns)==1,(net,len(ns));n=ns[0]
 for a,c in zip(pts,pts[1:]):
  if a==c:continue
  t=p.PCB_TRACK(b);t.SetNet(n);t.SetWidth(mm(w));t.SetLayer(L);t.SetStart(xy(a));t.SetEnd(xy(c));t.SetLocked(True);b.Add(t)
 records.append({'net':net,'layer':b.GetLayerName(L),'width_mm':w,'points':pts})
def via(net,q):
 n=next(n for n in b.GetNetsByNetcode().values() if n.GetNetname().split('/')[-1]==net)
 v=p.PCB_VIA(b);v.SetPosition(xy(q));v.SetWidth(mm(.8));v.SetDrill(mm(.4));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(n);v.SetLocked(True);b.Add(v)
# Main path from P11, both sides of the shunt use 6 mm / 70 um copper.
route('ECU_P1',[point('J3',1),point('RSH1',1)],6)
route('EGR_P1',[point('J3',2),(27.62,28),(37.78,38.16),point('RSH1',4)],6)
# Offboard parallel bypass, separated from analog block and tie anchors.
route('ECU_P1',[point('RSH1',1),(11,51),(11,88),(17,94),point('J4',1)],6)
route('EGR_P1',[point('RSH1',4),(37.78,36),(30,28.22),(11,28.22),(11,88),(37.78,88),point('J4',2)],6,p.B_Cu)
# Sense taps ONLY on inner PBV pins. Equal top geometry up to the input resistors.
route('K_PLUS',[point('RSH1',2),point('R1',1)])
route('K_MINUS',[point('RSH1',3),point('R2',1)])
for net,r,x,pin in [('INA_PLUS','R1',25.08,8),('INA_MINUS','R2',32.7,1)]:
 q=(x,68);route(net,[point(r,2),q],.3,p.B_Cu);via(net,q)
 a=point('U1',pin);route(net,[q,(a[0],68),a])
route('I_L_OUT',[point('U1',5),(25,62.095),(25,60),(37.8,60),(37.8,48.2),point('R3',1)])
route('I_DIV',[point('R3',2),(44,57.16),point('C1',1)])
route('I_DIV',[point('R4',1),(44,62),(44,57.16)])
route('I_DIV',[(44,62),(46,64),(46,66.08),point('U2',3)])
route('ADC_BUF',[point('U2',1),(47.8,61),(47.8,63.54),point('U2',2)])
route('REF_BUF',[point('U2',7),point('U2',6)])
# Local IC decoupling connections are fixed before routing.
links=[]
for u,c,n,pin in [('U1','C6','5VA_P06',6),('U2','C7','3V3_P06',8),('U3','C8','3V3_P06',8),('U5','C10','3V3_P06',14),('U6','C11','3V3_P06',14),('U7','C12','3V3_P06',14),('U8','C13','3V3_P06',2),('U9','C14','5VA_P06',2),('U10','C15','3V3_P06',3)]:
 a=point(u,pin);cxy=point(c,1);dx,dy=cxy[0]-a[0],cxy[1]-a[1];k=min(abs(dx),abs(dy));mid=(a[0]+math.copysign(k,dx),a[1]+math.copysign(k,dy))
 route(n,[a,mid,cxy]);links.append({'ic':u,'cap':c,'distance_mm':round(math.dist(a,cxy),3)})
route('REF25',[point('U10',2),(45.54,80.44),point('C5',1)])
route('REF25',[point('U3',1),(63.2,41),point('C16',1)])
# No ground plane under the main motor conductor area. Other-net track spacing is enforced by DRC.
z=p.ZONE(b);z.SetIsRuleArea(True);ls=p.LSET();ls.AddLayer(p.F_Cu);ls.AddLayer(p.B_Cu);z.SetLayerSet(ls)
z.SetDoNotAllowTracks(False);z.SetDoNotAllowVias(False);z.SetDoNotAllowPads(False);z.SetDoNotAllowFootprints(False);z.SetDoNotAllowZoneFills(True);z.SetZoneName('MOTOR_NO_GND')
o=z.Outline();o.NewOutline()
for q in [(6,14),(43,14),(43,46),(6,46)]:o.Append(mm(q[0]),mm(q[1]))
b.Add(z)
nc=b.GetDesignSettings().m_NetSettings.GetDefaultNetclass();nc.SetClearance(mm(.25));nc.SetTrackWidth(mm(.3));nc.SetViaDiameter(mm(.8));nc.SetViaDrill(mm(.4))
b.BuildConnectivity();p.SaveBoard(str(P/'eda/P06.kicad_pcb'),b)
assert p.ExportSpecctraDSN(b,str(P/'routing/P06.dsn'))
(P/'verification/critical-paths.json').write_text(json.dumps(records,indent=2));(P/'verification/decoupling-targets.json').write_text(json.dumps(links,indent=2))
print('Force/Kelvin/analog paths locked, DSN exported.')
