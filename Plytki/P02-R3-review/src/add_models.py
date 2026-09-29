"""Portable VRML clearance models, dimensions in mm; not manufacturing CAD.
Critical SK129 envelope and 17 mm bay follow the archived Fischer drawing.
All models are local; no dependency on a system 3D-library installation.
"""
from pathlib import Path
import pcbnew as p,json,math,hashlib
from sexpr import parse,dump,sub
P=Path(__file__).resolve().parents[1];bp=P/'eda/P02.kicad_pcb'
b=p.LoadBoard(str(bp));models=P/'eda/models';models.mkdir(exist_ok=True)
gray=(.58,.60,.63);black=(.13,.14,.16);red=(.65,.12,.12);metal=(.70,.70,.68)
def fmt(a):return ' '.join(f'{v/2.54:.7f}' for v in a)
def box(x,y,z,dx,dy,dz,color):
 return f'Transform {{ translation {fmt((x,-y,z))} children [ Shape {{ appearance Appearance {{ material Material {{ diffuseColor {" ".join(map(str,color))} }} }} geometry Box {{ size {fmt((dx,dy,dz))} }} }} ] }}\n'
def cyl(x,y,z,r,h,color,axis='z'):
 # KiCad's VRML reader does not render Cylinder primitives in this runtime.
 # Explicit indexed triangles retain all component bodies in native renders.
 n=24;verts=[]
 for end in (-h/2,h/2):
  for i in range(n):
   u=r*math.cos(i*math.tau/n);v=r*math.sin(i*math.tau/n)
   verts.append((x+u,-y-v,z+end) if axis=='z' else (x+end,-y-u,z+v))
 verts.extend([(x,-y,z-h/2),(x,-y,z+h/2)] if axis=='z' else [(x-h/2,-y,z),(x+h/2,-y,z)])
 faces=[]
 for i in range(n):
  j=(i+1)%n;faces.extend([[i,j,j+n],[i,j+n,i+n],[2*n,j,i],[2*n+1,i+n,j+n]])
 faces=[list(reversed(face)) for face in faces]
 return 'Shape { appearance Appearance { material Material { diffuseColor '+' '.join(map(str,color))+' } } geometry IndexedFaceSet { solid FALSE coord Coordinate { point [ '+', '.join(fmt(q) for q in verts)+' ] } coordIndex [ '+', '.join(' '.join(map(str,q+[-1])) for q in faces)+' ] } }\n'
def prism(points,height,color):
 vertices=[(x,-y,z) for z in (0,height) for x,y in points];n=len(points)
 faces=[list(range(n-1,-1,-1)),list(range(n,n*2))]+[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)]
 return 'Shape { appearance Appearance { material Material { diffuseColor '+ ' '.join(map(str,color))+' } } geometry IndexedFaceSet { solid FALSE coord Coordinate { point [ '+', '.join(fmt(q) for q in vertices)+' ] } coordIndex [ '+', '.join(' '.join(map(str,q+[-1])) for q in faces)+' ] } }\n'
def axial(pitch,length,diam,color,lift=.5):
 z=lift+diam/2
 return cyl(pitch/2,0,z,diam/2,length,color,'x')+box(pitch/2,0,z,pitch,.55,.55,metal)+cyl(0,0,(z-1.6)/2,.28,z+1.6,metal)+cyl(pitch,0,(z-1.6)/2,.28,z+1.6,metal)
def film(pitch,dx,dy,h,color):
 return box(pitch/2,0,h/2,dx,dy,h,color)+cyl(0,0,-.8,.3,1.6,metal)+cyl(pitch,0,-.8,.3,1.6,metal)
def to220():
 # Tab back y=-3.15; nominal insulating pad 0.25 mm to sink face.
 # A square 3.2 mm hole envelope represents the M3 passage at z=13.5 mm.
 s=box(2.54,-.315,7.6,10,3.13,9.2,black)
 s+=box(2.54,-2.515,6.575,10,1.27,10.65,gray)
 s+=box(2.54,-2.515,16,10,1.27,1.8,gray)
 for x in (-.76,5.84):s+=box(x,-2.515,13.5,3.4,1.27,3.2,gray)
 for x in (0,2.54,5.08):s+=box(x,0,1,.8,.5,5.2,metal)
 return s
def heatsink():
 upper=[(-8.5,-12.5),(-9.5,-12.5),(-10.3,-7.2),(-12.5,-6.75),(-15.6,-12.3),(-16.5,-12),(-15.75,-9.05),(-16.15,-8.8),(-20.2,-12.4),(-20.9,-12.3),(-20.8,-11.6),(-16.55,-6.65),(-16.8,-6.25),(-20.45,-7.5),(-21,-7.05),(-20.8,-6.6),(-13.54,-1.01),(-12.9,0)]
 wing=upper+[(x,-y) for x,y in reversed(upper[:-1])]
 s=prism(wing,63.5,black)+prism([(-x,y) for x,y in wing],63.5,black)
 # Central plate with conservative square hole envelopes matching height 13.5/18.3/25.4.
 last=0
 for h in (13.5,18.3,25.4):
  s+=box(0,0,(last+h-1.6)/2,17,1.8,h-1.6-last,black)
  for x in (-5.05,5.05):s+=box(x,0,h,6.9,1.8,3.2,black)
  last=h+1.6
 s+=box(0,0,(last+63.5)/2,17,1.8,63.5-last,black)
 for x in (-12.7,12.7):s+=cyl(x,0,-2.25,1.15,4.5,metal)
 return s
coverage={}
parts=json.loads((P/'docs/parts.json').read_text(encoding='utf-8'))
for f in b.GetFootprints():
 r=f.GetReference();s=None;kind='model gabarytowy; nie model produkcyjny'
 # Fab body bounds read from a fresh local footprint, excluding Fab text.
 if r in parts:
  lib,name=parts[r]['footprint'].split(':');ff=p.FootprintLoad(str(P/'eda/libraries'/(lib+'.pretty')),name)
  shapes=[g.GetBoundingBox() for g in ff.GraphicalItems() if isinstance(g,p.PCB_SHAPE) and g.GetLayer()==p.F_Fab]
  if shapes:
   x0=min(p.ToMM(q.GetLeft()) for q in shapes);x1=max(p.ToMM(q.GetRight()) for q in shapes)
   y0=min(p.ToMM(q.GetTop()) for q in shapes);y1=max(p.ToMM(q.GetBottom()) for q in shapes)
  else:x0,y0,x1,y1=0,0,0,0
 if r.startswith('R'):s=axial(17.78 if r=='R20' else 10.16,10 if r=='R20' else 6.3,3.9 if r=='R20' else 2.5,(.55,.37,.23),1)
 elif r in ['C1','C2','C3']:s=cyl(5,0,22.5,17.5,45,(.12,.22,.32))+cyl(5,0,45,17.3,.3,metal);kind='bank D35 x H45 mm, P10; bez obejmy'
 elif r in ['C4','C5','C6','C7','C8']:s=cyl(1,0,5.5,2.5,11,black)
 elif r.startswith('C'):s=film(5,7.5,2.5,5.5,(.73,.45,.20))
 elif r in ['D1','D2']:s=to220()
 elif r in ['U1','U2']:s=box((x0+x1)/2,(y0+y1)/2,5.05,x1-x0,y1-y0,10.1,black);kind='TSR2: obrys F.Fab, H10.1mm'
 elif r in ['U3','U4','U8']:s=cyl(2.54,0,4,2.5,5,black)
 elif r=='U5':
  s=box(7.62,7.62,5.8,18,18,1.6,(.10,.40,.23))+box(7.62,7.62,7.6,6,10,2,black)
  for x in [0,15.24]:s+=box(x,7.62,2.5,2.54,17.8,5,black)
  kind='adapter 18x18, rzedy15.24, nominalna wysokosc8.6mm; sprawdz kolki i C16'
 elif r in ['U6','U7']:s=box((x0+x1)/2,(y0+y1)/2,4,x1-x0,y1-y0,5,black)
 elif r.startswith('F'):s=box((x0+x1)/2,(y0+y1)/2,5,x1-x0,y1-y0,10,(.2,.2,.2))+cyl(11.3,0,8,2.5,20,(.9,.9,.85),'x')
 elif r=='LED1':s=cyl(1.27,0,3.5,1.5,5,(.1,.8,.15))
 elif r=='J2':s=box((x0+x1)/2,(y0+y1)/2,7,x1-x0,y1-y0,14,(.08,.45,.20));kind='obrys gniazda, H14mm obwiednia; wtyk poza lewa krawedzia'
 elif r.startswith('J') and r not in ['J1','J12','J13']:
  s=box((x0+x1)/2,(y0+y1)/2,6.4,x1-x0,y1-y0,12.8,(.83,.83,.78))
  s+=box((x0+x1)/2,(y0+y1)/2,20,x1-x0,y1-y0,14.4,(.65,.68,.75));kind='Mini-Fit header H12.8 plus obwiednia wtyku do27.2mm; nie zatwierdza dopasowania'
 elif r.startswith('H'):s=cyl(0,0,-6.6,3,10,(.7,.7,.7));kind='dystans M3x10'
 while len(f.Models()):f.Models().pop()
 if r in parts:
  f.GetField(p.FIELD_T_DATASHEET).SetText(parts[r]['url'])
  field=next((fld for fld in f.GetFields() if fld.GetName()=='MPN'),None)
  if field:field.SetText(parts[r]['mpn'])
 if s:
  path=models/(r+'.wrl');path.write_text('#VRML V2.0 utf8\n'+s)
  m=p.FP_3DMODEL();m.m_Filename='${KIPRJMOD}/models/'+path.name;f.Add3DModel(m)
  coverage[r]={'file':'models/'+path.name,'kind':kind,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
 else:coverage[r]={'file':None,'kind':'pole pomiarowe/lutownicze; bez korpusu'}
p.SaveBoard(str(bp),b,True)
(P/'verification/models.json').write_text(json.dumps(coverage,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('Local body envelopes:',sum(bool(v['file']) for v in coverage.values()))

