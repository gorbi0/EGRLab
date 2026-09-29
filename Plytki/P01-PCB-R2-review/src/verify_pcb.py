"""Independent checks of the finished PCB, frozen schematic and filled copper.
Usage: KiCad Python verify_pcb.py [alternative_board]
The alternative-board argument supports negative controls without edits to release.
PCB R2: the R1 checks plus the review items PCB1-01..06 as measurable rules (block 'R2').
"""
from pathlib import Path
import pcbnew as p,json,sys,math,hashlib,collections,heapq,xml.etree.ElementTree as ET
from sexpr import parse,one,sub
P=Path(__file__).resolve().parents[1];path=Path(sys.argv[1]) if len(sys.argv)>1 else P/'eda/P01.kicad_pcb'
b=p.LoadBoard(str(path));root=ET.parse(P/'reference/R3-P01.xml').getroot()
checks=[];details={}
def check(name,ok,detail=None):
 checks.append({'check':name,'pass':bool(ok)})
 if detail is not None:details[name]=detail
def pos(v):return tuple(round(p.ToMM(t),5) for t in (v.x,v.y))
def xy(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
fmap={f.GetReference():f for f in b.GetFootprints()}
baseline={n.get('ref'):n for n in root.findall('./components/comp')}
manifest=json.loads((P/'reference/R3-release-manifest.json').read_text())['files']
check('89 electrical + 2 heatsinks + 4 mounting footprints',len(baseline)==89 and set(fmap)==set(baseline)|{'HS1','HS2','H1','H2','H3','H4'})
pin={}
for n in root.findall('./nets/net'):
 for node in n.findall('node'):pin[node.get('ref'),node.get('pin')]=n.get('name')
errors=[];pad_count=0
if sha(P/'reference/R3-P01.xml')!=manifest['verification/P01.xml']:errors.append('R3 XML digest')
for ref,comp in baseline.items():
 f=fmap[ref]
 if f.GetValue()!=comp.findtext('value') or f.GetFPIDAsString()!=comp.findtext('footprint'):errors.append(ref+' fields')
 for pad in f.Pads():
  num=pad.GetNumber()
  if num:
   pad_count+=1
   if pad.GetNetname()!=pin.get((ref,num),''):errors.append(f'{ref}.{num} net')
 # Compare actual pad geometry, including duplicate Kelvin pads, with frozen R3.
 lib,fp=comp.findtext('footprint').split(':')
 source=P/'reference/R3-pad-libraries'/f'{lib}.pretty'
 if sha(source/(fp+'.kicad_mod'))!=manifest[f'eda/libraries/{lib}.pretty/{fp}.kicad_mod']:errors.append(ref+' R3 library digest')
 rf=p.FootprintLoad(str(source),fp);assert rf is not None
 rf.SetPosition(f.GetPosition());rf.SetOrientation(f.GetOrientation())
 def geom(ff):
  return sorted((a.GetNumber(),pos(a.GetPosition()),pos(a.GetSize()),pos(a.GetDrillSize()),int(a.GetAttribute()),int(a.GetShape())) for a in ff.Pads())
 if geom(f)!=geom(rf):errors.append(ref+' pad geometry')
check('All R3 values, footprint IDs, pad nets and pad geometry preserved',not errors,{'errors':errors,'electrical_physical_pads':pad_count})
sch=[f for f in (P/'eda').glob('*.kicad_sch')]
check('Frozen R3 schematic bytes unchanged',len(sch)==3 and all(sha(f)==manifest['eda/'+f.name] for f in sch))
check('2 copper layers / 1.6 mm nominal board',b.GetCopperLayerCount()==2 and abs(p.ToMM(b.GetDesignSettings().GetBoardThickness())-1.6)<.00001)
s=parse(path.read_text());stack=one(one(s,'setup'),'stackup')
cu={x[1]:float(one(x,'thickness')[1]) for x in sub(stack,'layer') if x[1] in ['F.Cu','B.Cu']}
check('Both copper layers explicitly 70 um',cu=={'F.Cu':.07,'B.Cu':.07})
edge=[g for g in b.GetDrawings() if g.GetLayer()==p.Edge_Cuts]
pts={pos(g.GetStart()) for g in edge}|{pos(g.GetEnd()) for g in edge}
check('Closed rectangular outline 160 x 120',len(edge)==4 and pts=={(0,0),(160,0),(160,120),(0,120)})
holes=[]
for r,q in zip(['H1','H2','H3','H4'],[(5,5),(155,5),(5,115),(155,115)]):
 f=fmap[r];a=list(f.Pads())[0];holes.append(pos(f.GetPosition())==q and a.GetAttribute()==p.PAD_ATTRIB_NPTH and pos(a.GetDrillSize())==(3.2,3.2))
check('Four NPTH 3.2 mm mounting holes at defined centres',all(holes))
keep=[z for z in b.Zones() if z.GetIsRuleArea()]
mount=[z for z in keep if z.GetZoneName().startswith('M3 ')];hskeep=[z for z in keep if z.GetZoneName().endswith('F.Cu keepout')]
check('Four mounting keepouts on both copper layers',len(mount)==4 and len(keep)==6 and all(set(z.GetLayerSet().Seq())=={p.F_Cu,p.B_Cu} and z.GetDoNotAllowTracks() and z.GetDoNotAllowVias() and z.GetDoNotAllowZoneFills() for z in mount))
# Locked topology is compared with a different artifact: pre-routing PCB.
def sig(t):
 if isinstance(t,p.PCB_VIA):return ('via',t.GetNetname(),pos(t.GetPosition()),p.ToMM(t.GetWidth(p.F_Cu)),p.ToMM(t.GetDrill()))
 return ('track',t.GetNetname(),tuple(sorted([pos(t.GetStart()),pos(t.GetEnd())])),p.ToMM(t.GetWidth()),int(t.GetLayer()))
pre=p.LoadBoard(str(P/'routing/prerouted.kicad_pcb'))
need=collections.Counter(sig(t) for t in pre.GetTracks());have=collections.Counter(sig(t) for t in b.GetTracks())
missing=list((need-have).elements())
check('Every pre-routed critical segment and via retained',not missing,{'missing':missing,'count':sum(need.values())})
def shortest(net,start,end):
 graph=collections.defaultdict(list)
 for t in b.GetTracks():
  if not isinstance(t,p.PCB_VIA) and t.GetNetname()==net:
   a,c=pos(t.GetStart()),pos(t.GetEnd());dist=math.dist(a,c);graph[a].append((c,dist));graph[c].append((a,dist))
 todo=[(0,start)];visited=set()
 while todo:
  dist,q=heapq.heappop(todo)
  if q==end:return dist
  if q in visited:continue
  visited.add(q)
  for v,d in graph[q]:heapq.heappush(todo,(dist+d,v))
 return None
probe={}
for ref,num in [('TP1','3'),('TP2','1')]:
 a=next(a for a in fmap['Q1'].Pads() if a.GetNumber()==num);c=list(fmap[ref].Pads())[0]
 probe[ref]=shortest(a.GetNetname(),pos(a.GetPosition()),pos(c.GetPosition()))
check('Actual Q1 source/gate probe tracks <= 5 mm',all(x is not None and x<=5 for x in probe.values()),probe)
lk={a.GetNumber():a.GetNetname().split('/')[-1] for a in fmap['LK1'].Pads()}
check('LK1 sides on distinct DRAIN and VPROT nets',lk=={'1':'P01_Q1_DRAIN','2':'VPROT'})
sense=[]
for a in fmap['LK1'].Pads():
 if abs(p.ToMM(a.GetDrillSize().x)-1)<.001:
  touching=[t for t in b.GetTracks() if not isinstance(t,p.PCB_VIA) and pos(a.GetPosition()) in [pos(t.GetStart()),pos(t.GetEnd())]]
  sense.append(len(touching)==1 and abs(p.ToMM(touching[0].GetWidth())-.4)<.00001)
check('Kelvin sense pads have only a dedicated 0.4 mm terminal branch',len(sense)==2 and all(sense))
# Sample *filled polygons*, including centre/edge of each thermal spoke.
thermal=[]
for pad in fmap['J7'].Pads():
 if not pad.GetNumber():continue
 x,y=pos(pad.GetPosition());angle=pad.GetThermalSpokeAngleDegrees()
 for layer in [p.F_Cu,p.B_Cu]:
  zs=[z for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname()==pad.GetNetname() and z.IsOnLayer(layer)]
  def filled(q):return any(z.GetFilledPolysList(layer).Contains(xy(*q)) for z in zs)
  samples=[];gap_samples=[]
  for k in range(4):
   th=math.radians(angle+90*k);co,si=math.cos(th),math.sin(th)
   # at 0.15 mm into the nominal 0.30 mm air gap
   r=3.15
   for off in [-.45,0,.45]:samples.append(filled((x+r*co-off*si,y+r*si+off*co)))
   for off in [-.85,.85]:gap_samples.append(filled((x+r*co-off*si,y+r*si+off*co)))
  thermal.append({'pad':pad.GetNumber(),'layer':b.GetLayerName(layer),'12_samples':samples,
   'gap_samples_must_be_false':gap_samples,
   'spoke_mm':p.ToMM(pad.GetLocalThermalSpokeWidthOverride()),'gap_mm':p.ToMM(pad.GetLocalThermalGapOverride())})
check('J7 four thermals present, >=0.9 mm sampled width, F and B',len(thermal)==4 and all(all(t['12_samples']) and not any(t['gap_samples_must_be_false']) and t['spoke_mm']==1.2 and t['gap_mm']==.3 for t in thermal),thermal)
check('Heatsink pads remain net-free',all(not a.GetNetname() for r in ['HS1','HS2'] for a in fmap[r].Pads()))
anchors={}
for ref in ['J5','J7']:
 f=fmap[ref];power=[pos(a.GetPosition()) for a in f.Pads() if a.GetNumber()];anc=[pos(a.GetPosition()) for a in f.Pads() if not a.GetNumber()]
 # Perpendicular distance between pad row and anchor row, independent of orientation.
 dx,dy=power[-1][0]-power[0][0],power[-1][1]-power[0][1];norm=math.hypot(dx,dy)
 distances=[abs(dx*(a[1]-power[0][1])-dy*(a[0]-power[0][0]))/norm for a in anc]
 anchors[ref]=distances
check('Harness anchors 12.5 mm from solder row',all(len(v)==2 and all(abs(x-12.5)<.001 for x in v) for v in anchors.values()),anchors)
pro=json.loads((P/'eda/P01.kicad_pro').read_text());ds=pro['board']['design_settings'];rules=ds['rules']
check('Explicit DRC rules active; no waivers',rules['min_clearance']>=.25 and rules['min_silk_clearance']>=.15 and not ds['drc_exclusions'] and pro['net_settings']['classes'][0]['clearance']>=.3)
# ---------------- R2: review items PCB1-01..06 as measurable rules ----------------
def local(f,v):
 d=v-f.GetPosition();a=math.radians(f.GetOrientationDegrees());x,y=p.ToMM(d.x),p.ToMM(d.y)
 return (x*math.cos(a)-y*math.sin(a),x*math.sin(a)+y*math.cos(a))
def board_pt(f,lx,ly):
 a=math.radians(f.GetOrientationDegrees());x0,y0=pos(f.GetPosition())
 return (x0+lx*math.cos(a)+ly*math.sin(a),y0-lx*math.sin(a)+ly*math.cos(a))
def pad_xy(ref,num):return pos(next(a for a in fmap[ref].Pads() if a.GetNumber()==num).GetPosition())
# PCB1-01: metal envelope of the SK129 profile standing on the board = courtyard +-21.3 x +-12.8 mm,
# TO-220 bay = between the wall faces (|x|<8.5) below the plate face (y>+1.0). No F.Cu copper inside.
envs={}
for r in ['HS1','HS2']:
 hx,hy=pos(fmap[r].GetPosition());s=p.SHAPE_POLY_SET();s.NewOutline()
 for dx,dy in [(-21.3,-12.8),(21.3,-12.8),(21.3,12.8),(8.5,12.8),(8.5,1.0),(-8.5,1.0),(-8.5,12.8),(-21.3,12.8)]:s.Append(p.FromMM(hx+dx),p.FromMM(hy+dy))
 envs[r]=s
def in_env(q):
 v=xy(*q);return [r for r,s in envs.items() if s.Contains(v)]
hits=[]
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):
  c=pos(t.GetPosition());r=p.ToMM(t.GetWidth(p.F_Cu))/2
  for k in range(8):
   q=(c[0]+r*math.cos(k*math.pi/4),c[1]+r*math.sin(k*math.pi/4))
   if in_env(q):hits.append(('via',t.GetNetname(),c));break
  continue
 if t.GetLayer()!=p.F_Cu:continue
 a,c=pos(t.GetStart()),pos(t.GetEnd());w=p.ToMM(t.GetWidth())/2;L=math.dist(a,c);n=max(1,int(L/.2))
 ux,uy=((c[0]-a[0])/L,(c[1]-a[1])/L) if L else (1,0)
 for k in range(n+1):
  m=(a[0]+(c[0]-a[0])*k/n,a[1]+(c[1]-a[1])*k/n)
  if any(in_env((m[0]+o*-uy,m[1]+o*ux)) for o in (-w,0,w)):hits.append(('track',t.GetNetname(),m));break
for f in b.GetFootprints():
 if f.GetReference() in ('HS1','HS2'):continue
 for a in f.Pads():
  if not a.IsOnLayer(p.F_Cu):continue
  bb=a.GetBoundingBox();pts=[(p.ToMM(bb.GetLeft()),p.ToMM(bb.GetTop())),(p.ToMM(bb.GetRight()),p.ToMM(bb.GetTop())),(p.ToMM(bb.GetLeft()),p.ToMM(bb.GetBottom())),(p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom())),pos(a.GetPosition())]
  if any(in_env(q) for q in pts):hits.append(('pad',f.GetReference()+'.'+a.GetNumber(),pos(a.GetPosition())))
fill_hits=[]
for z in b.Zones():
 if z.GetIsRuleArea() or not z.IsOnLayer(p.F_Cu):continue
 fp=z.GetFilledPolysList(p.F_Cu)
 for r,s in envs.items():
  inter=p.SHAPE_POLY_SET(fp);inter.BooleanIntersection(s)
  if inter.Area()>0:fill_hits.append((z.GetNetname(),r,p.ToMM(p.ToMM(inter.Area()))))
check('R2/PCB1-01: no F.Cu copper under the heatsink profiles (tracks, vias, pads, zone fill)',not hits and not fill_hits,{'items':[list(map(str,h)) for h in hits],'zone_fill':fill_hits})
kz={}
for z in hskeep:
 ref=z.GetZoneName().split()[0];o=z.Outline()
 hx,hy=pos(fmap[ref].GetPosition())
 border=[(hx+dx,hy+dy) for dx in (-21.3,-10,0,10,21.3) for dy in (-12.8,0)]+[(hx+dx,hy+12.8) for dx in (-21.3,-15,-9,9,15,21.3)]+[(hx+sx*9.0,hy+dy) for sx in (-1,1) for dy in (2,6,10)]
 kz[ref]=set(z.GetLayerSet().Seq())=={p.F_Cu} and z.GetDoNotAllowTracks() and z.GetDoNotAllowVias() and z.GetDoNotAllowZoneFills() and all(o.Contains(xy(*q)) for q in border)
check('R2/PCB1-01: F.Cu rule areas cover both heatsink envelopes, bay open',set(kz)=={'HS1','HS2'} and all(kz.values()),kz)
# PCB1-02: tab side of every TO-220 marked by a thick silkscreen line; Q2 also labelled TAB.
marks={};tabmid={}
for r in ['Q1','Q2','D2']:
 f=fmap[r];ok=False
 for g in f.GraphicalItems():
  if isinstance(g,p.PCB_SHAPE) and g.GetLayer()==p.F_SilkS and g.GetShape()==p.SHAPE_T_SEGMENT and p.ToMM(g.GetWidth())>=.35:
   a,c=local(f,g.GetStart()),local(f,g.GetEnd())
   if abs(a[1]-c[1])<.01 and a[1]<-3.0 and abs(a[0]-c[0])>=9:ok=True;tabmid[r]=pos(g.GetStart()),pos(g.GetEnd())
 marks[r]=ok
tabtxt=[pos(t.GetPosition()) for t in b.GetDrawings() if isinstance(t,p.PCB_TEXT) and t.GetLayer()==p.F_SilkS and t.GetText()=='TAB']
q2tab=None
if 'Q2' in tabmid:
 (a,c)=tabmid['Q2'];m=((a[0]+c[0])/2,(a[1]+c[1])/2);q2tab=min([math.dist(m,t) for t in tabtxt],default=None)
check('R2/PCB1-02: TO-220 tab side marked on silkscreen (Q1, Q2, D2); TAB text at Q2',all(marks.values()) and q2tab is not None and q2tab<=4.0,{'thick_tab_line':marks,'TAB_text_to_Q2_tab_line_mm':q2tab})
# PCB1-03: sensitive comparator nets short and away from the power copper.
seglen=collections.Counter()
for t in b.GetTracks():
 if not isinstance(t,p.PCB_VIA):seglen[t.GetNetname().split('/')[-1]]+=p.ToMM(t.GetLength())
limits={'P01_OV_REF':20,'P01_OV_SENSE':40,'P01_UV_SENSE':40,'P01_REF':70}
def sd(a1,a2,b1,b2):
 def pd(q,s0,s1):
  vx,vy=s1[0]-s0[0],s1[1]-s0[1];L2=vx*vx+vy*vy;u=0 if L2==0 else max(0,min(1,((q[0]-s0[0])*vx+(q[1]-s0[1])*vy)/L2))
  return math.dist(q,(s0[0]+u*vx,s0[1]+u*vy))
 def cross(p1,p2,p3,p4):
  d=(p2[0]-p1[0])*(p4[1]-p3[1])-(p2[1]-p1[1])*(p4[0]-p3[0])
  if d==0:return False
  u=((p3[0]-p1[0])*(p4[1]-p3[1])-(p3[1]-p1[1])*(p4[0]-p3[0]))/d;v=((p3[0]-p1[0])*(p2[1]-p1[1])-(p3[1]-p1[1])*(p2[0]-p1[0]))/d
  return 0<=u<=1 and 0<=v<=1
 return 0.0 if cross(a1,a2,b1,b2) else min(pd(a1,b1,b2),pd(a2,b1,b2),pd(b1,a1,a2),pd(b2,a1,a2))
powernets={'BAT_FUSED','P01_VS','P01_Q1_DRAIN','VPROT'}
ptr=[t for t in b.GetTracks() if not isinstance(t,p.PCB_VIA) and t.GetNetname().split('/')[-1] in powernets]
gap={}
for t in b.GetTracks():
 n=t.GetNetname().split('/')[-1]
 if isinstance(t,p.PCB_VIA) or n not in limits:continue
 for q in ptr:
  dd=sd(pos(t.GetStart()),pos(t.GetEnd()),pos(q.GetStart()),pos(q.GetEnd()))-p.ToMM(t.GetWidth())/2-p.ToMM(q.GetWidth())/2
  gap[n]=min(gap.get(n,1e9),round(dd,2))
lens={n:round(seglen[n],1) for n in limits}
check('R2/PCB1-03: OV_REF<=20, OV_SENSE/UV_SENSE<=40, REF<=70 mm routed; >=5 mm from power tracks on both layers',all(lens[n]<=limits[n] for n in limits) and all(gap.get(n,1e9)>=5 for n in limits),{'routed_mm':lens,'min_edge_gap_to_power_mm':gap})
prox={('C6.1','Q1.1'):10,('C6.2','Q1.3'):10,('D9.2','Q2.1'):12,('D9.1','Q2.3'):12,('R21.2','Q3.3'):8,('R7.2','U2.3'):12,('R8.2','U2.3'):12,
      ('R14.2','D7.2'):8,('D7.1','D8.2'):8,('D8.1','Q6.2'):8,('R15.1','Q6.2'):8,('R11.2','U2.5'):15,('R13.2','U4.1'):20,
      ('C10.1','U2.8'):8,('C11.1','U4.2'):8}  # BOM R3 notes: C10 at U2, C11 at U4 (AUX5 pads)
dist={f'{a}-{c}':round(math.dist(pad_xy(*a.split('.')),pad_xy(*c.split('.'))),2) for (a,c) in prox}
check('R2/PCB1-03,05,06: functional neighbours (C6 at Q1, D9 at Q2, R21 at Q3, R7/R8 at U2.3, buffer around Q6, C10 at U2, C11 at U4)',all(dist[f'{a}-{c}']<=lim for (a,c),lim in prox.items()),dist)
# PCB1-04: J5 harness leaves the pad row towards the nearest (bottom) edge, no parts under the wires.
j5=fmap['J5'];jp=[pos(a.GetPosition()) for a in j5.Pads() if a.GetNumber()];ja=[pos(a.GetPosition()) for a in j5.Pads() if not a.GetNumber()]
row_y=sum(q[1] for q in jp)/len(jp);anc_y=sum(q[1] for q in ja)/len(ja)
lane=(min(q[0] for q in jp)-1.5,row_y+1.5,max(q[0] for q in jp)+1.5,anc_y)
ls2=p.LSET();ls2.AddLayer(p.F_CrtYd);blockers=[]
for f in b.GetFootprints():
 if f.GetReference() in ('J5',) or not f.GetReference() or f.GetReference().startswith('H'):continue
 bb=f.GetLayerBoundingBox(ls2)
 if p.ToMM(bb.GetWidth())==0:continue
 q=(p.ToMM(bb.GetLeft()),p.ToMM(bb.GetTop()),p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom()))
 if q[0]<lane[2] and q[2]>lane[0] and q[1]<lane[3] and q[3]>lane[1]:blockers.append(f.GetReference())
check('R2/PCB1-04: J5 wires run from the pad row towards the bottom edge, no component under them',anc_y>row_y and 120-anc_y<=8 and not blockers,{'pad_row_y':row_y,'anchor_y':anc_y,'blockers':blockers})
# PCB1-06: net names at the test pads used by ODBIOR.
want={('J1','1'):'BAT',('J1','2'):'GND',('J2','1'):'OUT+',('J2','2'):'GND',('J4','1'):'3V3',('J4','2'):'SAFE_N',('J4','3'):'GND',('J8','1'):'S',('J8','2'):'L'}
def bbdist(q,t):
 bb=t.GetBoundingBox();x0,y0,x1,y1=p.ToMM(bb.GetLeft()),p.ToMM(bb.GetTop()),p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom())
 return math.dist(q,(min(max(q[0],x0),x1),min(max(q[1],y0),y1)))
texts=[t for t in b.GetDrawings() if isinstance(t,p.PCB_TEXT) and t.GetLayer()==p.F_SilkS]
leg={f'{r}.{n}':min([round(bbdist(pad_xy(r,n),t),2) for t in texts if t.GetText()==txt],default=None) for (r,n),txt in want.items()}
check('R2/PCB1-06: test pads J1/J2/J4/J8 carry net legends (text box within 3 mm of the pad centre)',all(v is not None and v<=3.0 for v in leg.values()),leg)
if len(sys.argv)==1:
 drc=json.loads((P/'verification/drc.json').read_text())
 check('Native KiCad DRC/parity all zero',all(not drc[k] for k in ['violations','unconnected_items','schematic_parity']))
out={'board_sha256':sha(path),'checks':checks,'details':details,'pass':all(c['pass'] for c in checks),'tracks_and_vias':len(list(b.GetTracks()))}
target=P/'verification/pcb-checks.json' if len(sys.argv)==1 else path.with_suffix('.checks.json')
target.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print(json.dumps({'pass':out['pass'],'checks':len(checks),'failed':[c['check'] for c in checks if not c['pass']]},indent=2))
sys.exit(0 if out['pass'] else 1)
