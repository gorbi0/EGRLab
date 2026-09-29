"""Independent checks of the finished PCB, frozen schematic and filled copper.
Usage: KiCad Python verify_pcb.py [alternative_board]
The alternative-board argument supports negative controls without edits to release.
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
check('Four mounting keepouts on both copper layers',len(keep)==4 and all(set(z.GetLayerSet().Seq())=={p.F_Cu,p.B_Cu} and z.GetDoNotAllowTracks() and z.GetDoNotAllowVias() and z.GetDoNotAllowZoneFills() for z in keep))
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
if len(sys.argv)==1:
 drc=json.loads((P/'verification/drc.json').read_text())
 check('Native KiCad DRC/parity all zero',all(not drc[k] for k in ['violations','unconnected_items','schematic_parity']))
out={'board_sha256':sha(path),'checks':checks,'details':details,'pass':all(c['pass'] for c in checks),'tracks_and_vias':len(list(b.GetTracks()))}
target=P/'verification/pcb-checks.json' if len(sys.argv)==1 else path.with_suffix('.checks.json')
target.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print(json.dumps({'pass':out['pass'],'checks':len(checks),'failed':[c['check'] for c in checks if not c['pass']]},indent=2))
sys.exit(0 if out['pass'] else 1)
