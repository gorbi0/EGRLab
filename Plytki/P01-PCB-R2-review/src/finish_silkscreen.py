"""Trim only mask-conflicting outlines; place all references legibly, no waivers."""
from pathlib import Path
import pcbnew as p,json,math
P=Path(__file__).resolve().parents[1];fn=P/'eda/P01.kicad_pcb';b=p.LoadBoard(str(fn))
mm=p.FromMM
def xy(x,y):return p.VECTOR2I(mm(x),mm(y))
def pt(v):return p.ToMM(v.x),p.ToMM(v.y)
def box(v,extra=0):
 q=v.GetBoundingBox();return (p.ToMM(q.GetLeft())-extra,p.ToMM(q.GetTop())-extra,p.ToMM(q.GetRight())+extra,p.ToMM(q.GetBottom())+extra)
def intersects(a,c):return a[0]<c[2] and a[2]>c[0] and a[1]<c[3] and a[3]>c[1]
pads=[box(pad,.3) for f in b.GetFootprints() for pad in f.Pads()]
def clear(x,y):return not any(a<=x<=c and d<=y<=e for a,d,c,e in pads)
d=json.loads((P/'verification/drc.json').read_text())
bad={i['uuid'] for v in d['violations'] if v['type']=='silk_over_copper' for i in v['items']}
trimmed=[]
for f in b.GetFootprints():
 for g in list(f.GraphicalItems()):
  if g.GetLayer()!=p.F_SilkS or not isinstance(g,p.PCB_SHAPE) or g.m_Uuid.AsString() not in bad:continue
  a,c=pt(g.GetStart()),pt(g.GetEnd());shape=g.GetShape()
  if shape==p.SHAPE_T_SEGMENT:paths=[[a,c]]
  elif shape==p.SHAPE_T_RECT:paths=[[a,(c[0],a[1]),c,(a[0],c[1]),a]]
  else:raise ValueError((f.GetReference(),shape))
  width=g.GetWidth();f.Remove(g);trimmed.append(f.GetReference())
  for path in paths:
   for a,c in zip(path,path[1:]):
    n=max(1,math.ceil(math.dist(a,c)/.08));start=None;prev=None
    for k in range(n+2):
     q=(a[0]+(c[0]-a[0])*min(k,n)/n,a[1]+(c[1]-a[1])*min(k,n)/n)
     ok=k<=n and clear(*q)
     if ok and start is None:start=q
     if start is not None and not ok:
      if math.dist(start,prev)>.25:
       line=p.PCB_SHAPE(b);line.SetShape(p.SHAPE_T_SEGMENT);line.SetStart(xy(*start));line.SetEnd(xy(*prev));line.SetWidth(width);line.SetLayer(p.F_SilkS);b.Add(line)
      start=None
     prev=q
# Text inside the harness footprints becomes a compact label elsewhere. The
# original 12.5 mm anchor geometry is preserved on F.Fab and in the fit drawing.
texts=[]
for f in b.GetFootprints():
 for g in f.GraphicalItems():
  if isinstance(g,p.PCB_TEXT) and g.GetLayer()==p.F_SilkS:
   if g.GetText().startswith('TIE'):g.SetText('TIE')
   texts.append((f.GetReference()+'/'+g.GetText(),g,pt(g.GetPosition())))
 for field in [f.Reference()]:
  if field.IsVisible():texts.append((f.GetReference(),field,pt(field.GetPosition())))
for t in b.GetDrawings():
 if isinstance(t,p.PCB_TEXT) and t.GetLayer()==p.F_SilkS:texts.append(('title',t,pt(t.GetPosition())))
obstacles=list(pads)
for f in b.GetFootprints():
 for g in f.GraphicalItems():
  if g.GetLayer()==p.F_SilkS and isinstance(g,p.PCB_SHAPE):obstacles.append(box(g,.19))
for g in b.GetDrawings():
 if g.GetLayer()==p.F_SilkS and isinstance(g,p.PCB_SHAPE):obstacles.append(box(g,.19))
# Wide text first; fixed ordering gives reproducible results.
texts.sort(key=lambda t:(-len(t[1].GetText()),t[0]))
report=[]
for name,t,old in texts:
 t.SetTextSize(xy(1,1));t.SetTextThickness(mm(.15));t.SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T))
 candidates=[(old[0]+dx*.5,old[1]+dy*.5) for dx in range(-22,23) for dy in range(-18,19)]
 candidates.sort(key=lambda q:math.dist(q,old))
 for q in candidates:
  t.SetPosition(xy(*q));bb=box(t,.18)
  if bb[0]<1 or bb[1]<1 or bb[2]>159 or bb[3]>119:continue
  if any(intersects(bb,ob) for ob in obstacles):continue
  obstacles.append(bb);report.append({'ref':name,'xy':q,'shift_mm':math.dist(q,old)});break
 else:raise ValueError('No clear label location: '+name)
p.SaveBoard(str(fn),b)
(P/'verification/silkscreen-placement.json').write_text(json.dumps({'trimmed_outlines':trimmed,'labels':report},indent=2))
print('Placed',len(texts),'silkscreen labels; max shift',max(x['shift_mm'] for x in report))
