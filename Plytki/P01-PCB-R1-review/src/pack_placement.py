"""Resolve placement overlaps inside fixed functional/mechanical anchors.
Only places components; native DRC and human visual review follow.
"""
from pathlib import Path
import pcbnew as p,json,math,ast
P=Path(__file__).resolve().parents[1]
b=p.LoadBoard(str(P/'eda/P01.kicad_pcb'));fps={f.GetReference():f for f in b.GetFootprints() if not f.GetReference().startswith('H') or f.GetReference().startswith('HS')}
ls=p.LSET();ls.AddLayer(p.F_CrtYd)
def box(f):
 a=f.GetLayerBoundingBox(ls)
 return tuple(p.ToMM(v) for v in [a.GetLeft(),a.GetTop(),a.GetRight(),a.GetBottom()])
data={x['ref']:x for x in json.loads((P/'verification/placement.json').read_text())}
tree=ast.parse((P/'src/build_board.py').read_text())
targets=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='pos' for t in n.targets))
targets.update({'J6':(148,32,90),'J5':(143,112,90),'D1':(12,37,0),'TP1':(112,26.5,0),
 'R27':(84,47,0),'Q2':(81.46,53.5,0),'D4':(106,48,0),'R22':(100,55,0),
 'U2':(72,70,0),'C11':(86,72,270),'C12':(65,72,90),'C13':(84,83,180),
 'C3':(136,58,0),'C4':(150,55,90),'Q7':(114,87,90),'Q8':(105,89,0),
 'R30':(112,70,270),'R31':(122,94,90),'R32':(100,94,90),'R33':(106,74,90),'R34':(130,70,180)})
fixed=['HS1','HS2','D2','Q1','TP1','TP2','J7','J6','J5','LK1','D1','D3','C6','R27','Q2','D4','C5','R22','C3','C4']
placed={};rect={}
geom={}
for r,f in fps.items():
 f.SetPosition(p.VECTOR2I(0,0))
 for a in [0,90,180,270]:f.SetOrientationDegrees(a);geom[r,a]=box(f)
def at(r,x,y,a):
 l,t,rr,bb=geom[r,a];return(l+x,t+y,rr+x,bb+y)
def overlaps(a,b,g=.4):return a[0]<b[2]+g and a[2]>b[0]-g and a[1]<b[3]+g and a[3]>b[1]-g
for i,(x,y) in enumerate([(5,5),(155,5),(5,115),(155,115)]):rect['M'+str(i)]=(x-4,y-4,x+4,y+4)
for r in fixed:
 x,y,a=targets[r];placed[r]=(x,y,a);rect[r]=at(r,x,y,a)
todo=[r for r in targets if r not in fixed]
priority=['U2','C11','C12','C13','U3','U1','C8','C7','C9','R2','C10','C1','C2','Q4','D9','Q7','Q8','Q6','D7','D8','U4','RV1']
todo.sort(key=lambda r:(priority.index(r) if r in priority else 30,-(geom[r,0][2]-geom[r,0][0])*(geom[r,0][3]-geom[r,0][1])))
for r in todo:
 tx,ty,ta=targets[r];candidates=[]
 # Half-millimetre refinement is unnecessary at this first placement stage.
 for a in [0,90,180,270]:
  for x in range(4,157,2):
   for y in range(4,117,2):
    bb=at(r,x,y,a)
    if bb[0]<2 or bb[1]<2 or bb[2]>158 or bb[3]>118:continue
    if any(overlaps(bb,q) for q in rect.values()):continue
    cost=(x-tx)**2+(y-ty)**2+(0 if a==ta else 16)
    candidates.append((cost,x,y,a,bb))
 if not candidates:raise RuntimeError('No space for '+r)
 _,x,y,a,bb=min(candidates);placed[r]=(x,y,a);rect[r]=bb
# Swap equal mechanical footprints to reduce displacement globally, preserving
# every occupied rectangle. This avoids sacrificing the last resistor placed.
for it in range(100):
 best=None
 for i,r in enumerate(todo):
  for t in todo[i+1:]:
   if fps[r].GetFPIDAsString()!=fps[t].GetFPIDAsString():continue
   pr,pt=placed[r],placed[t];tr,tt=targets[r],targets[t]
   old=math.dist(pr[:2],tr[:2])**2+math.dist(pt[:2],tt[:2])**2
   new=math.dist(pt[:2],tr[:2])**2+math.dist(pr[:2],tt[:2])**2
   if old-new>.01 and (best is None or old-new>best[0]):best=(old-new,r,t)
 if best is None:break
 _,r,t=best;placed[r],placed[t]=placed[t],placed[r]
out={k:list(v) for k,v in sorted(placed.items())}
(P/'src/placement.json').write_text(json.dumps(out,indent=2)+'\n')
print('All footprints placed. Largest movements:')
for v in sorted([(round(math.dist(placed[r][:2],targets[r][:2]),1),r) for r in todo],reverse=True)[:12]:print(v)
