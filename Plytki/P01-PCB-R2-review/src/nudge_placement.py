from pathlib import Path
import pcbnew as p,json,math
P=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(P/'eda/P01.kicad_pcb'))
fs={f.GetReference():f for f in b.GetFootprints()};ls=p.LSET();ls.AddLayer(p.F_CrtYd)
d=json.loads((P/'src/placement.json').read_text())
def box(f):
 a=f.GetLayerBoundingBox(ls);return [p.ToMM(v) for v in [a.GetLeft(),a.GetTop(),a.GetRight(),a.GetBottom()]]
def hit(a,b,g=.4):return a[0]<b[2]+g and a[2]>b[0]-g and a[1]<b[3]+g and a[3]>b[1]-g
targets={'Q6':(42,42,0),'TP7':(43,45,0),'D8':(50,44,0),'R8':(80,28,90),'J2':(155,65,90)}
rect={r:box(f) for r,f in fs.items() if r not in targets and r in d}
rect.update({'BAT power':(10,28,48,35),'VS power':(52,30.5,114,37)})
for i,(x,y) in enumerate([(5,5),(155,5),(5,115),(155,115)]):rect['M'+str(i)]=(x-4,y-4,x+4,y+4)
for r,(tx,ty,ta) in targets.items():
 f=fs[r];options=[]
 for a in [ta,(ta+180)%360,90 if ta%180==0 else 0]:
  f.SetOrientationDegrees(a);f.SetPosition(p.VECTOR2I(0,0));base=box(f)
  for x in range(3,158):
   for y in range(3,118):
    q=[base[0]+x,base[1]+y,base[2]+x,base[3]+y]
    if q[0]<2 or q[1]<2 or q[2]>158 or q[3]>118 or any(hit(q,b) for b in rect.values()):continue
    options.append(((x-tx)**2+(y-ty)**2+(a!=ta)*16,x,y,a,q))
 _,x,y,a,q=min(options);d[r]=[x,y,a];rect[r]=q;print(r,d[r])
(P/'src/placement.json').write_text(json.dumps(d,indent=2))
