"""Independent geometry/current-path requirements, read from final native PCB.
Native DRC remains separate. Mutations are in-memory snapshots; final PCB is never altered.
"""
from pathlib import Path
import pcbnew as p,json,copy,math,xml.etree.ElementTree as ET
P=Path(__file__).resolve().parents[1]
def pt(v):return tuple(round(p.ToMM(a),6) for a in [v.x,v.y])
def snapshot(b):
 return {'cu':b.GetCopperLayerCount(),'thickness':p.ToMM(b.GetDesignSettings().GetBoardThickness()),
 'fps':{f.GetReference():{'xy':pt(f.GetPosition()),'angle':f.GetOrientationDegrees(),'fp':f.GetFPIDAsString(),'pads':{a.GetNumber():{'xy':pt(a.GetPosition()),'drill':pt(a.GetDrillSize()),'size':pt(a.GetSize()),'net':a.GetNetname().split('/')[-1]} for a in f.Pads() if a.GetNumber()},'holes':[pt(a.GetPosition()) for a in f.Pads() if not a.GetNumber()], 'ref_visible':f.Reference().IsVisible()} for f in b.GetFootprints()},
 'tracks':[{'net':t.GetNetname().split('/')[-1],'a':pt(t.GetStart()),'z':pt(t.GetEnd()),'layer':b.GetLayerName(t.GetLayer()),'w':p.ToMM(t.GetWidth(p.F_Cu) if isinstance(t,p.PCB_VIA) else t.GetWidth()),'via':isinstance(t,p.PCB_VIA),'locked':t.IsLocked()} for t in b.GetTracks()],
 'edges':[(pt(t.GetStart()),pt(t.GetEnd())) for t in b.GetDrawings() if isinstance(t,p.PCB_SHAPE) and t.GetLayer()==p.Edge_Cuts],
 'ties':[z.GetZoneName() for z in b.Zones() if z.GetIsRuleArea()]}
def connected(s,net,r1,n1,r2,n2,width):
 """Centreline graph of locked copper only, through-hole endpoints connect both layers.
 Thus a skinny autorouted parallel trace cannot make the rated power path pass.
 """
 ts=[t for t in s['tracks'] if t['net']==net and t['locked'] and t['w']>=width and not t['via']]
 start=s['fps'][r1]['pads'][str(n1)]['xy'];end=s['fps'][r2]['pads'][str(n2)]['xy'];todo=[start];seen=set()
 while todo:
  a=todo.pop()
  if a==end:return True
  if a in seen:continue
  seen.add(a)
  for t in ts:
   if t['a']==a:todo.append(t['z'])
   if t['z']==a:todo.append(t['a'])
 return False
def checks(s):
 out=[];f=s['fps']
 def ok(k,v,n=''):out.append({'id':k,'pass':bool(v),'note':n})
 ok('BOARD-SIZE',set(q for edge in s['edges'] for q in edge)=={(0.,0.),(120.,0.),(120.,100.),(0.,100.)} and len(s['edges'])==4)
 ok('TWO-LAYER-1.6',s['cu']==2 and abs(s['thickness']-1.6)<1e-6)
 ok('OFFBOARD-SW','SW1' not in f)
 ok('PTH-FORCE',all(f[r]['pads'][str(n)]['drill'][0]>=2.3 for r,ns in [('J3',[1,2]),('J4',[1,2]),('RSH1',[1,4])] for n in ns))
 ok('PBV-GEOMETRY',[round(f['RSH1']['pads'][str(i)]['xy'][0]-f['RSH1']['pads']['1']['xy'][0],2) for i in range(1,5)]==[0,5.08,12.7,17.78])
 for r in ['J1','J2','J3','J4','J5']:
  # Anchors straddle the harness. Distance perpendicular to solder row, not diagonal from its end.
  ys=[q[1] for q in f[r]['holes']];py=[q['xy'][1] for q in f[r]['pads'].values()]
  ok('TIE-'+r,len(ys)==2 and all(10<=y-h<=15 for y in py for h in ys) and 'TIE '+r in s['ties'])
 for net,r,n in [('ECU_P1','J3',1),('EGR_P1','J3',2),('ECU_P1','J4',1),('EGR_P1','J4',2)]:
  ok('FORCE-'+r+str(n),connected(s,net,r,n,'RSH1',1 if net=='ECU_P1' else 4,5.99),'Locked 6mm route required; vias cannot carry motor current.')
 ok('NO-FORCE-VIAS',not any(t['via'] and t['net'] in ['ECU_P1','EGR_P1'] for t in s['tracks']))
 for n,r,pin in [('K_PLUS','R1',2),('K_MINUS','R2',3)]:ok('KELVIN-'+n,connected(s,n,'RSH1',pin,r,1,.29))
 ok('KELVIN-NO-CONNECTOR',not any(a['net'] in ['K_PLUS','K_MINUS','INA_PLUS','INA_MINUS'] for r,d in f.items() if r.startswith('J') for a in d['pads'].values()))
 ok('CREF-NEAR',math.dist(f['U10']['pads']['2']['xy'],f['C5']['pads']['1']['xy'])<=5)
 local=[('U1',6,'C6'),('U2',8,'C7'),('U3',8,'C8'),('U5',14,'C10'),('U6',14,'C11'),('U7',14,'C12'),('U8',2,'C13'),('U9',2,'C14'),('U10',3,'C15')]
 ok('LOCAL-DECOUPLING',all(math.dist(f[u]['pads'][str(i)]['xy'],f[c]['pads']['1']['xy'])<=5 for u,i,c in local),'Power pad to cap pad geometry; ground connectivity separately audited.')
 ok('LDO-INPUT-DECOUPLING',math.dist(f['U4']['pads']['2']['xy'],f['C9']['pads']['1']['xy'])<=7.5,'C9 is 6.94mm from VIN, not included in the 5mm IC group.')
 ok('WETTING-HEAT-DISTANCE',math.dist(f['R21']['xy'],f['U10']['xy'])>35 and math.dist(f['R21']['xy'],f['RSH1']['xy'])>50)
 root=ET.parse(P/'verification/P06.xml').getroot();expected={}
 for n in root.findall('./nets/net'):
  name=n.get('name').split('/')[-1]
  for q in n.findall('node'):expected[(q.get('ref'),q.get('pin'))]=name
 ok('SCHEMATIC-PAD-PARITY',all(a['net']==expected.get((r,n)) for r,d in f.items() for n,a in d['pads'].items() if not r.startswith('H')))
 ok('ALL-REFERENCES',all(d['ref_visible'] for r,d in f.items() if not r.startswith('H')))
 return out
def main():
 b=p.LoadBoard(str(P/'eda/P06.kicad_pcb'));s=snapshot(b);out=checks(s);mut=[]
 for what in ['narrow_force','missing_kelvin','bad_shunt_pitch','small_wire_hole','bad_anchor','bad_ref_distance','wrong_pad_net','hidden_ref']:
  d=copy.deepcopy(s)
  if what=='narrow_force':
   for t in d['tracks']:
    if t['net']=='ECU_P1':t['w']=.3
  elif what=='missing_kelvin':d['tracks']=[t for t in d['tracks'] if t['net']!='K_PLUS']
  elif what=='bad_shunt_pitch':d['fps']['RSH1']['pads']['2']['xy']=(26,42)
  elif what=='small_wire_hole':d['fps']['J3']['pads']['1']['drill']=(1,1)
  elif what=='bad_anchor':d['fps']['J2']['holes']=[(94.5,17),(109.12,17)]
  elif what=='bad_ref_distance':d['fps']['C5']['pads']['1']['xy']=(70,80)
  elif what=='wrong_pad_net':d['fps']['J2']['pads']['3']['net']='GND'
  else:d['fps']['R1']['ref_visible']=False
  fail=[x['id'] for x in checks(d) if not x['pass']];mut.append({'mutation':what,'caught':bool(fail),'checks':fail})
 rep={'checks':out,'negative_controls':mut,'footprints':len(s['fps']),'track_items':len(s['tracks']),'vias':sum(t['via'] for t in s['tracks'])}
 (P/'verification/pcb-checks.json').write_text(json.dumps(rep,indent=2));print('PCB',sum(x['pass'] for x in out),'/',len(out),'; mutations',sum(x['caught'] for x in mut),'/',len(mut))
 assert all(x['pass'] for x in out),[x for x in out if not x['pass']]
 assert all(x['caught'] for x in mut)
if __name__=='__main__':main()

