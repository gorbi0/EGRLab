"""Small auditable KiCad s-expression helpers; no schematic connectivity inferred.
M1-R1: unchanged helpers from P07-S1 (P06-R2 (P06-R1 <- P02-R1 <- P01-R3 generator by Astra); project name, library prefix,
UUID namespace and title block are parameters (PRJ, REV, TITLE, COMMENT).
"""
import re,json,copy,math,uuid,functools,os
from pathlib import Path
P=Path(__file__).resolve().parents[1]
K=Path(os.environ.get('KICAD_LIBRARY_ROOT','C:/Program Files/KiCad/10.0/share/kicad'))
PRJ='M1';REV='M1-R1';DATE='2026-10-08';TITLE='EGRLab M1 (jedna plytka: LOGGER + TESTER)';COMMENT='Wariant M1: uproszczony S1, swiadomy uzytkownik; przewody lutowane, listwa X1 w obudowie; schemat'
class A(str):pass
def parse(t):
 toks=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',t);i=0
 def read():
  nonlocal i
  v=toks[i];i+=1
  if v=='(':
   out=[]
   while toks[i]!=')':out.append(read())
   i+=1;return out
  return json.loads(v) if v.startswith('"') else A(v)
 return read()
def dump(x):
 if isinstance(x,list):return '('+' '.join(map(dump,x))+')'
 if isinstance(x,A):return str(x)
 return json.dumps(x,ensure_ascii=False)
def subs(x,n):return [v for v in x if isinstance(v,list) and v and v[0]==n]
def one(x,n):return next(v for v in x if isinstance(v,list) and v and v[0]==n)
def uid(x):return str(uuid.uuid5(uuid.NAMESPACE_URL,'egrlab/'+REV.lower()+'/'+x))
def q(x):return json.dumps(str(x),ensure_ascii=False)
def mm(x):return round(x*2.54,5)
@functools.lru_cache(None)
def library(lib):return {x[1]:x for x in subs(parse((K/'symbols'/(lib+'.kicad_sym')).read_text(encoding='utf-8')),'symbol')}
def symbol(lib,name,newname=None):
 x=copy.deepcopy(library(lib)[name]);target=newname or name
 if subs(x,'extends'):
  base=symbol(lib,one(x,'extends')[1],target)
  props={p[1]:p for p in subs(base,'property')};props.update({p[1]:p for p in subs(x,'property')})
  base=[v for v in base if not(isinstance(v,list) and v and v[0]=='property')]+list(props.values());x=base
 old=x[1];x[1]=PRJ+':'+target
 for s in subs(x,'symbol'):s[1]=target+s[1][s[1].rfind('_',0,s[1].rfind('_')):]
 x=[v for v in x if not(isinstance(v,list) and v and v[0] in ['extends','property'])]
 return x
def pin_defs(sym,unit=1):
 out={}
 for s in subs(sym,'symbol'):
  u=int(s[1].split('_')[-2])
  if u not in [0,unit]:continue
  for p in subs(s,'pin'):out[one(p,'number')[1]]=p
 return out

class Sheet:
 def __init__(self,name,title,num,root=None):
  self.name=name;self.title=title;self.num=num;self.root=root or uid(name);self.path='/'+(root+'/' if root else '')+uid(name)
  self.items=[];self.parts={};self.libs={};self.connected=set();self.wires=[];self.labels=[];self.junctions=set()
 def text(self,t,x,y,size=1.27):self.items.append(f'(text {q(t)} (at {mm(x)} {mm(y)} 0) (effects (font (size {size} {size})) (justify left top)) (uuid {uid(self.name+"txt"+str(len(self.items)))}))')
 def box(self,x,y,w,h,title):
  self.items.append(f'(polyline (pts (xy {mm(x)} {mm(y)}) (xy {mm(x+w)} {mm(y)}) (xy {mm(x+w)} {mm(y+h)}) (xy {mm(x)} {mm(y+h)}) (xy {mm(x)} {mm(y)})) (stroke (width 0.15) (type dash)) (fill (type none)) (uuid {uid(self.name+"box"+str(len(self.items)))}))');self.text(title,x+2,y+2,1.5)
 def place(self,part,x,y,a=0,unit=1,mirror=None):
  ref=part['ref'];sym=part['symbol'];name=sym[1];self.libs[name]=sym;coords={};pins=pin_defs(sym,unit)
  for n,p in pins.items():
   px,py,pa=map(float,one(p,'at')[1:]);theta=math.radians(a)
   if mirror=='x':py=-py;pa=-pa
   if mirror=='y':px=-px;pa=180-pa
   dx=px*math.cos(theta)-py*math.sin(theta);dy=px*math.sin(theta)+py*math.cos(theta)
   coords[n]=(round(mm(x)+dx,5),round(mm(y)-dy,5),(pa+a)%360)
  k=ref+':'+str(unit);self.parts[k]=(part,coords)
  value=part['display'];orient=a%180
  tx,ty=mm(x)+3.81,mm(y)-1.27
  if ref.startswith(('R','C','D','LED')) and orient==90:tx,ty=mm(x),mm(y)-5.08
  if ref.startswith(('D','LED')) and orient==90:tx,ty=mm(x)+5.08,mm(y)-1.27
  if ref.startswith('D') and orient==0:tx,ty=mm(x),mm(y)-6.35
  if ref.startswith('Q'):tx,ty=mm(x)+7.62,mm(y)-5.08
  if ref.startswith('U'):tx,ty=mm(x),mm(y)-12.7
  if ref in ['Q1']:tx,ty=mm(x)+7.62,mm(y)-3.81
  if 'text_at' in part:tx,ty=mm(x+part['text_at'][0]),mm(y+part['text_at'][1])  # explicit offset in 2.54 mm units
  effects='(effects (font (size 1.27 1.27)) (justify '+('right' if a in [90,180] else 'left')+'))'
  ob='yes' if part.get('on_board',True) else 'no'
  sn=f'(symbol (lib_id {q(name)}) (at {mm(x)} {mm(y)} {a}) '+(f'(mirror {mirror}) ' if mirror else '')+f'(unit {unit}) (in_bom yes) (on_board {ob}) (dnp {"yes" if part.get("dnp") else "no"}) (uuid {uid(k)}) '
  fa=90 if a%180 else 0
  sn+=f'(property "Reference" {q(ref)} (at {tx} {ty} {fa}) {effects}) (property "Value" {q(value)} (at {tx} {ty+2.54} {fa}) {effects})'
  for prop,val in [('Footprint',part['footprint']),('MPN',part['mpn']),('BaselineRef',part['source_ref']),('Datasheet',part.get('url',''))]:
   sn+=f'(property {q(prop)} {q(val)} (at {mm(x)} {mm(y)} 0) (effects (font (size 1 1)) hide))'
  sn+=''.join(f'(pin {q(n)} (uuid {uid(k+"/"+n)}))' for n in pins)
  sn+=f'(instances (project {q(PRJ)} (path {q(self.path)} (reference {q(ref)}) (unit {unit})))))'
  self.items.append(sn);return coords
 def pin(self,ref,n):
  for k,(part,pins) in self.parts.items():
   if part['ref']==ref and str(n) in pins:return pins[str(n)][:2]
  raise KeyError((ref,n))
 def wire(self,*pts):
  for a,b in zip(pts,pts[1:]):
   a=tuple(round(float(v),5) for v in a);b=tuple(round(float(v),5) for v in b)
   if a==b:continue
   assert a[0]==b[0] or a[1]==b[1],(a,b)
   self.wires.append((a,b));self.items.append(f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0) (type default)) (uuid {uid(self.name+"wire"+str(len(self.wires)))}))')
 def label(self,net,pt,side='left',global_=False):
  typ='global_label' if global_ else 'label';shape='(shape passive)' if global_ else ''
  self.items.append(f'({typ} {q(net)} {shape} (at {pt[0]} {pt[1]} 0) (effects (font (size 1 1)) (justify {side} bottom)) (uuid {uid(self.name+"label"+str(len(self.labels)))}))');self.labels.append((net,pt))
 def node(self,net,refs,bus=None,axis='y',label=True):
  pp=[self.pin(r,n) for r,n in refs]
  if bus is None:
   if len(set(p[0] for p in pp))==1:axis='x';bus=pp[0][0]/2.54
   elif len(set(p[1] for p in pp))==1:axis='y';bus=pp[0][1]/2.54
   else:raise ValueError((net,refs,pp))
  val=mm(bus);junctions=[]
  for r,n in refs:self.connected.add((r,str(n)))
  for p in pp:
   j=(p[0],val) if axis=='y' else (val,p[1]);self.wire(p,j);junctions.append(j)
  points=sorted(set(junctions),key=lambda p:p[0] if axis=='y' else p[1]);self.wire(*points)
  self.junctions.update(points[1:-1]);
  if label:self.label(net,points[0],global_=net in CROSS)
 def finish(self):
  for k,(part,pins) in self.parts.items():
   for n,(x,y,a) in pins.items():
    if (part['ref'],n) in self.connected:continue
    net=part['pins'][n]
    if net=='NC':self.items.append(f'(no_connect (at {x} {y}) (uuid {uid(k+"NC"+n)}))');continue
    rad=math.radians(a);end=(round(x-5.08*math.cos(rad),5),round(y+5.08*math.sin(rad),5));self.wire((x,y),end);self.label(net,end,'right' if a==0 else 'left',net in CROSS)
  for p in self.junctions:self.items.append(f'(junction (at {p[0]} {p[1]}) (diameter 0) (color 0 0 0 0) (uuid {uid(self.name+"j"+str(p))}))')
 def save(self):
  text=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {uid(self.name)}) (paper "A3") (title_block (title {q(TITLE)}) (date {q(DATE)}) (rev {q(REV)}) (company "Prototype / schematic + PCB review") (comment 1 {q(COMMENT)}))'
  text+='(lib_symbols '+''.join(dump(v) for v in self.libs.values())+')'+''.join(self.items)
  if not self.root or self.root==uid(self.name):text+=f'(sheet_instances (path "/" (page "1")))'
  (P/'eda'/(self.name+'.kicad_sch')).write_text(text+')',encoding='utf-8')
CROSS=set()
