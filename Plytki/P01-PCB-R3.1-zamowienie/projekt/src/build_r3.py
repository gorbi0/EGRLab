"""Deterministic local layout revision from the frozen, reviewed R2 PCB.
No autorouter. Existing functional placement/routing remains the reference.
Run with KiCad Python. Does not modify the reference or project rules.
"""
from pathlib import Path
import pcbnew as p,json,hashlib,math
from sexpr import parse,dump,sub
P=Path(__file__).resolve().parents[1]
mm=p.FromMM
def xy(a,b):return p.VECTOR2I(mm(a),mm(b))
def pos(v):return (round(p.ToMM(v.x),5),round(p.ToMM(v.y),5))
bp=P/'eda/P01.kicad_pcb';pro=P/'eda/P01.kicad_pro'
prohash=hashlib.sha256(pro.read_bytes()).hexdigest()
b=p.LoadBoard(str(P/'reference/R2-layout/P01.kicad_pcb'))
b.SetFileName(str(bp));f={a.GetReference():a for a in b.GetFootprints()}
move={'D4':(113.08,26.5,180),'C6':(105.5,32.1,0),'TP1':(114.6,24.5,0),'TP2':(101.4,24.5,0)}
for r,(x,y,a) in move.items():f[r].SetPosition(xy(x,y));f[r].SetOrientationDegrees(a)
for r in ('TP1','TP2'):f[r].Flip(f[r].GetPosition(),False)

# Capture the placement stage before any new routing.
placement={r:{'xy':pos(fp.GetPosition()),'angle':fp.GetOrientationDegrees(),
 'pads':{a.GetNumber():pos(a.GetPosition()) for a in fp.Pads() if a.GetNumber()}} for r,fp in f.items()}
(P/'verification/placement-r3.json').write_text(json.dumps(placement,indent=2)+'\n')
stage=P/'mechanical/placement.kicad_pcb'
p.SaveBoard(str(stage),b,True)
root=parse(stage.read_text())
root=[x for x in root if not (isinstance(x,list) and (x[0] in ('segment','via') or (x[0]=='zone' and not sub(x,'keepout'))))]
stage.write_text(dump(root)+'\n')

# Remove only paths tied to the four relocated parts. Remaining tracks cannot
# be silently adjusted by a global cleanup or packing pass.
removed=[];removed_objects=[]
def erase(n,a,c):
 matches=[t for t in b.GetTracks() if not isinstance(t,p.PCB_VIA) and t.GetNetname().split('/')[-1]==n and {pos(t.GetStart()),pos(t.GetEnd())}=={a,c}]
 assert len(matches)==1,(n,a,c,len(matches))
 t=matches[0];removed.append({'net':n,'start':a,'end':c});removed_objects.append(t);b.RemoveNative(t)
erase('P01_VS',(110.54,22.3),(113.9,25.6))
erase('P01_GATE',(105.46,22.3),(101.9,25.6))
erase('P01_GATE',(105.46,22.3),(105.5,30.0))
erase('P01_GATE',(105.5,30.0),(105.5,48.5))
erase('P01_GATE',(103.96,39.5),(105.5,39.5))
erase('P01_VS',(93.8,39.5),(93.8,34.0))
erase('P01_VS',(94.0,34.0),(110.54,34.0))
erase('P01_VS',(110.54,34.0),(110.54,22.3))
erase('P01_VS',(110.6,40.8),(110.54,34.0))
erase('P01_GATE',(105.5,38.905),(104.555,38.905))
erase('P01_GATE',(104.555,38.905),(103.96,39.5))
erase('P01_GATE',(108.46,44.0),(103.96,39.5))
erase('P01_GATE',(116.0,44.0),(108.46,44.0))

added=[]
def tr(n,points,w,layer):
 net=next(v for v in b.GetNetInfo().NetsByNetcode().values() if v.GetNetname().split('/')[-1]==n)
 for a,c in zip(points,points[1:]):
  t=p.PCB_TRACK(b);t.SetStart(xy(*a));t.SetEnd(xy(*c));t.SetWidth(mm(w));t.SetLayer(layer)
  b.Add(t);t.SetNet(net);t.SetLocked(True)
  added.append({'net':net.GetNetname(),'start':a,'end':c,'width':w,'layer':int(layer)})
F=p.F_Cu
tr('P01_VS',[(110.54,22.3),(114.6,24.5)],.5,F)
tr('P01_GATE',[(105.46,22.3),(101.4,24.5)],.5,F)
tr('P01_GATE',[(105.46,22.3),(105.5,26.5),(105.5,32.1),(105.5,44),(105.5,48.5)],.8,F)
tr('P01_GATE',[(102.92,26.5),(105.5,26.5)],.8,F)
tr('P01_VS',[(110.54,22.3),(113.08,24.84),(113.08,26.5)],.8,F)
tr('P01_VS',[(93.8,34),(93.8,36.75)],.8,F)
tr('P01_VS',[(94,34),(96,36),(110.54,36)],5,p.B_Cu)
tr('P01_VS',[(110.54,22.3),(110.54,36)],2,p.B_Cu)
tr('P01_VS',[(110.6,40.8),(110.54,36)],.8,p.B_Cu)
tr('P01_GATE',[(105.5,44),(116,44)],.5,F)

# Move relocated references to explicit positions, preserving orientation marks.
for r,x,y in [('C6',108,37.0),('D4',108,25.0),('TP1',115,22),('TP2',101,22)]:
 f[r].Reference().SetPosition(xy(x,y));f[r].Reference().SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T))
f['D4'].Reference().SetLayer(p.B_SilkS);f['D4'].Reference().SetMirrored(True);f['D4'].Reference().SetPosition(xy(108,26.5))
for g in b.GetDrawings():
 if isinstance(g,p.PCB_TEXT):
  s=g.GetText()
  if 'PCB R2' in s:g.SetText(s.replace('PCB R2','PCB R3'))
  # Cathode marker at the old D4 position is retired, not falsely left there.
  if s=='K' and math.dist(pos(g.GetPosition()),(93.8,37))<4:g.SetText('')
def text(s,x,y,layer=p.B_SilkS,size=.9):
 t=p.PCB_TEXT(b);t.SetText(s);t.SetPosition(xy(x,y));t.SetTextSize(xy(size,size));t.SetTextThickness(mm(.13));t.SetLayer(layer);t.SetMirrored(layer==p.B_SilkS);b.Add(t)
text('TP1 S',116,28.5);text('TP2 G',100,28.5)
text('VGS: G-S / S IS NOT GND',108,16.0,size=.85)
text('PCB R3 / VIEW FROM BOTTOM',80,117,size=1)
# Additional service references, visible after the axial resistors are fitted.
for r,fp in f.items():
 if r.startswith('R') and r[1:].isdigit():
  pads=[a for a in fp.Pads() if a.GetNumber()]
  x=sum(pos(a.GetPosition())[0] for a in pads)/len(pads)
  y=sum(pos(a.GetPosition())[1] for a in pads)/len(pads)
  text(r,x,y,size=.85)
tb=b.GetTitleBlock();tb.SetRevision('PCB-R3 / SCH-R3 / ASM-A1');tb.SetTitle('EGRLab P01 PROTECT / PCB R3')
tb.SetComment(0,'Local gate clamp; bottom probe access; fresh verification required');b.SetTitleBlock(tb)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(bp),b,True)
pre=parse(bp.read_text())
pre=[x for x in pre if not (isinstance(x,list) and x[0] in ('segment','via') and not sub(x,'locked'))]
(P/'routing/prerouted.kicad_pcb').write_text(dump(pre)+'\n')
assert hashlib.sha256(pro.read_bytes()).hexdigest()==prohash,'Project rules changed during board save'
check=p.LoadBoard(str(bp))
for a in added:
 ts=[t for t in check.GetTracks() if not isinstance(t,p.PCB_VIA) and {pos(t.GetStart()),pos(t.GetEnd())}=={tuple(a['start']),tuple(a['end'])} and int(t.GetLayer())==a['layer']]
 assert len(ts)==1 and ts[0].GetNetname()==a['net'],a
(P/'verification/layout-delta.json').write_text(json.dumps({'moved':move,'removed':removed,'added':added,'project_unchanged':True},indent=2)+'\n')
print('R3 local layout saved; track nets and project rules checked after reload.')
