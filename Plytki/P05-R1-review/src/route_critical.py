"""Hand-planned ADC escape, local decoupling, input filters and ground returns.
Remaining signals are routed only after native DRC checks these fixed paths.
"""
from pathlib import Path
import pcbnew as p,json,math
P=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(P/'eda/P05.kicad_pcb'));mm=p.FromMM
f={q.GetReference():q for q in b.GetFootprints()};report=[]
def pad(r,n):return next(q for q in f[r].Pads() if q.GetNumber()==str(n))
def xy(v):return [round(p.ToMM(v.x),6),round(p.ToMM(v.y),6)]
def pp(r,n):return xy(pad(r,n).GetPosition())
def net(n):return next(x for x in b.GetNetsByNetcode().values() if x.GetNetname().split('/')[-1]==n)
def route(n,pts,w=.2):
 for a,c in zip(pts,pts[1:]):
  if a==c:continue
  t=p.PCB_TRACK(b);t.SetStart(p.VECTOR2I(mm(a[0]),mm(a[1])));t.SetEnd(p.VECTOR2I(mm(c[0]),mm(c[1])))
  t.SetLayer(p.F_Cu);t.SetWidth(mm(w));t.SetNet(net(n));t.SetLocked(True);b.Add(t)
 report.append({'net':n,'points':pts,'width':w})
def via(n,x,y):
 v=p.PCB_VIA(b);v.SetPosition(p.VECTOR2I(mm(x),mm(y)));v.SetWidth(mm(.6));v.SetDrill(mm(.3));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(net(n));v.SetLocked(True);b.Add(v)
def gpin(n,target):route('GND',[pp('U1',n),target]);via('GND',*target)
# Input signals fan toward C0G filters; interleaved VxGND pins go inward, straight to ground plane.
for i in range(8):
 a=pp('U1',49+2*i);c=pp(f'C{27+i}',1);escape=[a[0],37.3];mid=[c[0],37.3-abs(c[0]-a[0])]
 route(f'ADC_CH{i+1}',[a,escape,mid,c]);gpin(50+2*i,[pp('U1',50+2*i)[0],40])
# Ground groups in digital bottom and reference right side.
route('GND',[pp('U1',16),[101.3,47.75],[101.3,50.3],[103.625,50.3],pp('U1',17)])
route('GND',[pp('U1',17),pp('U1',22),[106.75,50.2],[105.5,51.45]]);via('GND',105.5,51.45)
gpin(26,[108.75,51.3]);route('GND',[pp('U1',30),pp('U1',32),[111.75,51.3]]);via('GND',111.75,51.3)
route('GND',[pp('U1',33),pp('U1',32)])
gpin(2,[104,40.75]);gpin(35,[111.75,46.5])
route('GND',[pp('U1',40),pp('U1',41),[112.4,43.75]]);via('GND',112.4,43.75)
gpin(43,[112.5,42.75]);route('GND',[pp('U1',46),pp('U1',47),[112.25,40.75]]);via('GND',112.25,40.75)
# Logic strap bus inside QFP body, without a plane split.
route('3V3_DAQ',[pp('U1',3),pp('U1',8)])
route('3V3_DAQ',[pp('U1',5),[103.3,42.25],[105,42.25],[107.25,44.5],[107.25,47.25],pp('U1',34)])
route('3V3_DAQ',[pp('U1',10),[104,44.75],[104,42.25]])
route('3V3_DAQ',[pp('U1',23),[107.25,47.25]])
route('3V3_DAQ',[pp('U1',23),pp('C8',1)])
# AVCC/reference local paths, ordered to avoid crossing one another.
route('5VA_P05',[pp('U1',1),pp('C4',1)],.25)
route('5VA_P05',[pp('U1',48),[115.5,40.25],[116,39.75],pp('C7',1)],.25)
route('REFCAP',[pp('U1',44),pp('U1',45),[116.5,41.75],[121.6,36.65],pp('C13',1)],.25)
route('ADC_REF',[pp('U1',42),[116,43.25],[118.25,41],pp('C11',1)],.25)
route('ADC_REF',[pp('C11',1),[127.225,39],[130.525,39],pp('C12',1)],.25)
route('REGCAP_D',[pp('U1',39),[116.5,44.75],[118.75,47],pp('C10',1)],.25)
route('5VA_P05',[pp('U1',38),pp('U1',37),[116.5,45.75],[120.75,50],pp('C5',1)],.25)
route('5VA_P05',[pp('C5',1),pp('C6',1)],.25)
route('REGCAP_A',[pp('U1',36),[115,46.25],[115,49.95],pp('C9',1)],.25)
# A dedicated nearby ground via for every ADC capacitor; direct SMD ground connection is intentional.
for i in range(4,14):
 a=pad(f'C{i}',2);v=pp(f'C{i}',2)
 # Put via beyond the ground pad, away from positive pin and the analog fan.
 target=[v[0]+.9,v[1]] if i not in [4,7,8] else [v[0]-(.9 if i==4 else 0),v[1]+(1 if i==8 else -1 if i==7 else 0)]
 route('GND',[v,target],.25);via('GND',*target);a.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
# IC decoupling other than QFP; these paths are short and stay on component side.
dec=[('U2',2,'C14'),('U3',8,'C15'),('U5',14,'C16'),('U6',2,'C17'),('U7',2,'C18'),('U8',14,'C19'),('U9',14,'C20'),('U10',14,'C21'),('U11',14,'C22')]
for r,pn,c in dec:
 a=pp(r,pn);z=pp(c,1)
 pts=[a,z]
 if r=='U2':pts=[a,[23.8,a[1]],[23.8,50],z]
 if r in ['U6','U7']:pts=[a,[a[0],a[1]-2],[z[0],a[1]-2],z]
 route(pad(r,pn).GetNetname().split('/')[-1],pts,.25)
# Digital escape vias lie outside the protected analog plane. These provide the
# router with clear exits instead of asking it to cross the analog front end.
for pin,x,y in [(9,100.5,44.25),(11,99.75,44.95),(12,99,45.75),(13,99.75,46.55),(14,100.5,47.25)]:
 n=pad('U1',pin).GetNetname().split('/')[-1];a=pp('U1',pin)
 route(n,[a,[101.25,a[1]],[x,y]]);via(n,x,y)
route('AD_DOUT_LOCAL',[pp('U1',24),[107.75,50.5],[108,50.75],[108,51.15]]);via('AD_DOUT_LOCAL',108,51.15)
route('ADC_SDI_P05',[pp('U1',29),[110.25,51.25]]);via('ADC_SDI_P05',110.25,51.25)
route('3V3_DAQ',[pp('C8',1),[106,54.475],[106,55]]);via('3V3_DAQ',106,55)
route('5VA_P05',[pp('C7',1),[118,32.775],[120,32.775],[120,26]],.25);via('5VA_P05',120,26)
for i in range(27,35):
 a=pad(f'C{i}',2);x,y=pp(f'C{i}',2);route('GND',[[x,y],[x,y-1]],.25);via('GND',x,y-1);a.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
nc=b.GetDesignSettings().m_NetSettings.GetDefaultNetclass();nc.SetClearance(mm(.15));nc.SetTrackWidth(mm(.2));nc.SetViaDiameter(mm(.6));nc.SetViaDrill(mm(.3))
b.BuildConnectivity();p.SaveBoard(str(P/'eda/P05.kicad_pcb'),b)
assert p.ExportSpecctraDSN(b,str(P/'routing/P05.dsn'))
(P/'verification/critical-routes.json').write_text(json.dumps(report,indent=2))
print('Locked',len(report),'critical paths; DSN exported.')




