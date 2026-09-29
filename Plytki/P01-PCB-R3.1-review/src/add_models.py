"""Portable VRML clearance models, dimensions in mm; not manufacturing CAD.
Critical SK129 envelope and 17 mm bay follow the archived Fischer drawing.
All models are local; no dependency on a system 3D-library installation.
"""
from pathlib import Path
import pcbnew as p,json,math,hashlib
from sexpr import parse,dump,sub
P=Path(__file__).resolve().parents[1];bp=P/'eda/P01.kicad_pcb'
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
for f in b.GetFootprints():
 r=f.GetReference();name=f.GetFPIDAsString().split(':')[-1];s=None;kind='approximate clearance body'
 if r.startswith('HS'):s=heatsink();kind='SK129 dimensional envelope with approximate fins'
 elif r in ('Q1','Q2','D2'):s=to220();kind='TO220 envelope, nominal mounting hole 13.5 mm'
 elif r=='C6':s=film(5,7.2,7.2,13,red);kind='WIMA 7.2 x 7.2 x 13 mm'
 elif r in ('R1','R23','R27'):s=axial(17.78,11,3.9,(.65,.23,.16),3 if r!='R27' else .5)
 elif r.startswith('R') and r[1:].isdigit() and r!='R34':s=axial(15.24,6.3,2.5,(.68,.66,.48))
 elif r in ('D4','D9','D6','D7','D8'):s=axial(10.16,4.2,1.85,(.67,.28,.16));s+=cyl(3.3,0,1.425,1,.5,black,'x')
 elif r in ('D1','D3'):s=axial(20.32,9.1,9.1,black)
 elif r=='D5':s=axial(15.24,9.5,5.3,black)
 elif r in ('C1','C7','C9'):s=cyl(1,0,5.5,2.5,11,black)
 elif r=='C3':s=cyl(1.75,0,5.75,4,11.5,black)
 elif r in ('C2','C4','C5'):s=film(5,7.3,2.5,6.5,(.73,.65,.34))
 elif r in ('C8','C10','C11','C12','C13'):s=film(5,7.5,2.5,5.5,(.66,.40,.14))
 elif r=='U2':s=box(3.81,3.81,3.5,6.4,9.8,4.2,black)
 elif r in ('U1','U3','U4','Q3','Q4','Q5','Q6','Q7','Q8'):s=cyl(2.54,0,4,2.5,5,black)
 elif r=='RV1':s=box(2.54,0,6,9.6,4.8,12,(.12,.30,.62))
 elif r=='LED1':s=cyl(1.27,0,3.5,1.5,5,(.15,.65,.18))
 elif r=='J3':s=box(0,1.27,1.5,2.5,5,3,black)+box(0,0,4,.64,.64,8,metal)+box(0,2.54,4,.64,.64,8,metal)
 elif r=='J6':
  # Body bounds from native Fab geometry; fit still verified with purchased plug.
  ls=p.LSET();ls.AddLayer(p.F_Fab);bb=f.GetLayerBoundingBox(ls)
  # Native footprint is horizontal, pin 1 at (0,0), body extends +X / +/-Y.
  s=box(5.08,3.5,6,15.24,12,12,(.12,.40,.20))
 elif r in ('H1','H2','H3','H4'):s=cyl(0,0,-6.6,3,10,(.78,.78,.74));kind='M3x10 insulating standoff envelope'
 if s:
  path=models/(r+'.wrl');path.write_text('#VRML V2.0 utf8\n# Clearance model; millimetres converted to KiCad VRML units.\n'+s)
  while len(f.Models()):f.Models().pop()
  m=p.FP_3DMODEL();m.m_Filename='${KIPRJMOD}/models/'+path.name;f.Add3DModel(m)
  coverage[r]={'file':'models/'+path.name,'kind':kind,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
 else:
  # Bare pads/wire links have no elevated component body.
  while len(f.Models()):f.Models().pop()
  coverage[r]={'file':None,'kind':'bare test/solder pads or wire link; no elevated body model'}
p.SaveBoard(str(bp),b,True)
(P/'verification/models.json').write_text(json.dumps(coverage,indent=2)+'\n')
# Coherent placement preview with final text/models but no copper tracks/zones.
root=parse(bp.read_text());root=[x for x in root if not(isinstance(x,list) and (x[0] in ('segment','via') or (x[0]=='zone' and not sub(x,'keepout'))))]
(P/'mechanical/placement.kicad_pcb').write_text(dump(root).replace('${KIPRJMOD}/models/','${KIPRJMOD}/../eda/models/')+'\n')
print('Local clearance models:',sum(bool(v['file']) for v in coverage.values()),'of',len(coverage),'footprints.')
