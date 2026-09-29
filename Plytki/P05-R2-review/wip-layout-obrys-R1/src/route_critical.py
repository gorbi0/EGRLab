"""P05 R2. Hand-planned ADC escape, local decoupling, input filters and ground returns.
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
# Ground groups in digital bottom (as R1).
route('GND',[pp('U1',16),[101.3,47.75],[101.3,50.3],[103.625,50.3],pp('U1',17)])
route('GND',[pp('U1',17),pp('U1',22),[106.75,50.2],[105.5,51.45]]);via('GND',105.5,51.45)
gpin(26,[108.75,51.3]);route('GND',[pp('U1',30),pp('U1',32),[111.75,51.3]]);via('GND',111.75,51.3)
route('GND',[pp('U1',33),pp('U1',32)])
gpin(35,[111.75,46.5])
# R2: pin 2 (AGND) goes outward to its own via, so the AVCC spine below can leave pin 1 under the body.
route('GND',[pp('U1',2),[101.3,40.75],[100.9,41.0]]);via('GND',100.9,41.0)
# R2 (P5-01): every right-side ground pin has its own via inward (REFGND 43/46, AGND 40/41/47).
for n,tg in [(47,[112.3,40.75]),(46,[111.65,41.6]),(43,[112.2,42.75]),(41,[112.3,43.85]),(40,[111.65,44.55])]:
 a=pp('U1',n);route('GND',[a,[112.7,a[1]],tg]);via('GND',*tg)
# Logic strap bus inside QFP body, without a plane split (as R1).
route('3V3_DAQ',[pp('U1',3),pp('U1',8)])
route('3V3_DAQ',[pp('U1',5),[103.3,42.25],[105,42.25],[107.25,44.5],[107.25,47.25],pp('U1',34)])
route('3V3_DAQ',[pp('U1',10),[104,44.75],[104,42.25]])
route('3V3_DAQ',[pp('U1',23),[107.25,47.25]])
route('3V3_DAQ',[pp('U1',23),pp('C8',1)])
route('5VA_P05',[pp('U1',1),pp('C4',1)],.25)
# R2: AVCC spine 0.5 mm under the body, pin 1 -> pins 37/38, below the input ground-via row (y 40) and
# inside the right-pin ground vias. Pins 37/38 have no other free side: column A holds their capacitor.
route('5VA_P05',[pp('U1',1),[103.45,40.25],[104.1,40.9]],.3)
route('5VA_P05',[[104.1,40.9],[110.8,40.9],[110.8,45.5],[112.6,45.5]],.5)
route('5VA_P05',[[112.6,45.5],pp('U1',38)],.3);route('5VA_P05',[[112.6,45.5],pp('U1',37)],.3)
route('5VA_P05',[pp('U1',38),pp('U1',37)],.25)
# R2 right side (P5-01). Neck 0.25-0.3 mm inside the 0.5 mm pad row (x <= 114.6), then >= 0.4 mm.
# AVCC 48 -> C7 in the free top-right corner (outside the U1 courtyard); C7 is fed from above through C6.
route('5VA_P05',[pp('U1',48),[114.1,40.25],[114.1,38.0]],.4)
# REFCAP 44+45 -> junction (114.6, 42.0) -> C13 (column B, 1210).
route('REFCAP',[pp('U1',44),[114.35,42.25],[114.6,42.0]],.25);route('REFCAP',[pp('U1',45),[114.35,41.75],[114.6,42.0]],.25)
route('REFCAP',[[114.6,42.0],[116.9,39.7],pp('C13',1)],.4)
# REFIN/REFOUT 42 -> C11 (column A) and, below C11, a straight lane to C12 (column B, 1210).
route('ADC_REF',[pp('U1',42),[114.6,43.25]],.3)
route('ADC_REF',[[114.6,43.25],[115.3,42.55],pp('C11',1)],.4)
route('ADC_REF',[[114.6,43.25],[114.875,42.975],pp('C12',1)],.4)
# REGCAP_D 39 -> C10, AVCC 37/38 -> C5, REGCAP_A 36 -> C9.
route('REGCAP_D',[pp('U1',39),[114.6,44.75]],.3);route('REGCAP_D',[[114.6,44.75],[115.3,44.07],pp('C10',1)],.4)
route('5VA_P05',[pp('U1',37),[114.6,45.75]],.3);route('5VA_P05',[[114.6,45.75],[115.9,45.75],pp('C5',1)],.4)
route('REGCAP_A',[pp('U1',36),[114.6,46.25]],.25);route('REGCAP_A',[[114.6,46.25],pp('C9',1)],.3)
# Test pads beside their own capacitors (0.2 mm stubs; not on the decoupling path).
route('ADC_REF',[pp('C12',1),[119.545,41.25],[124.3,41.25]],.2)
route('REGCAP_D',[pp('C10',1),[115.95,45.17],[120.5,45.17],[120.5,45.6]],.2)
route('REGCAP_A',[pp('C9',1),[115.95,49.45]],.2)
route('REFCAP',[pp('C13',1),[117.295,37.8],[119.3,35.8]],.2)
# 5VA feed: the R1 via at (120,26) -> C6 -> C7 (pin 48 capacitor).
route('5VA_P05',[[120,26],[120,29.5],[116.8,32.7],[115.725,33.775],pp('C6',1)],.5);via('5VA_P05',120,26)
route('5VA_P05',[pp('C6',1),[114.1,36.525],pp('C7',1)],.5)
# R2: own ground via for every ADC capacitor (C4/C8 as in R1; right side placed against column B).
GV={'C4':None,'C8':None,'C5':[118.45,46.05],'C6':[118.25,34.9],'C7':[115.65,39.15],'C9':[118.8,47.71],'C10':[118.6,44.6],'C11':[118.3,42.1],
 'C12':[123.85,43.2],'C13':[121.4,39.6]}
for c,tg in GV.items():
 a=pad(c,2);v=pp(c,2)
 if tg is None:tg=[v[0]-.9,v[1]] if c=='C4' else [v[0],v[1]+1]
 route('GND',[v,tg],.3 if c not in ('C4','C8') else .25);via('GND',*tg);a.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
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
for i in range(27,35):
 a=pad(f'C{i}',2);x,y=pp(f'C{i}',2);route('GND',[[x,y],[x,y-1]],.25);via('GND',x,y-1);a.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
nc=b.GetDesignSettings().m_NetSettings.GetDefaultNetclass();nc.SetClearance(mm(.15));nc.SetTrackWidth(mm(.2));nc.SetViaDiameter(mm(.6));nc.SetViaDrill(mm(.3))
b.BuildConnectivity();p.SaveBoard(str(P/'eda/P05.kicad_pcb'),b)
assert p.ExportSpecctraDSN(b,str(P/'routing/P05.dsn'))
(P/'verification/critical-routes.json').write_text(json.dumps(report,indent=2))
print('Locked',len(report),'critical paths; DSN exported.')




