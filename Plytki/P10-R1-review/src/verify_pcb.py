"""Independent final-board geometry, including CAN entry/TVS and three soldered-harness anchors."""
from pathlib import Path
import pcbnew as p,json,copy,math,xml.etree.ElementTree as ET
P=Path(__file__).resolve().parents[1]
def pt(v):return tuple(round(p.ToMM(a),6) for a in [v.x,v.y])
def snapshot(b):
 return {'cu':b.GetCopperLayerCount(),'thickness':p.ToMM(b.GetDesignSettings().GetBoardThickness()),
 'fps':{f.GetReference():{'xy':pt(f.GetPosition()),'fp':f.GetFPIDAsString(),'pads':{a.GetNumber():{'xy':pt(a.GetPosition()),'drill':pt(a.GetDrillSize()),'size':pt(a.GetSize()),'net':a.GetNetname().split('/')[-1]} for a in f.Pads() if a.GetNumber()},'holes':[pt(a.GetPosition()) for a in f.Pads() if not a.GetNumber()],'ref_visible':f.Reference().IsVisible()} for f in b.GetFootprints()},
 'tracks':[{'net':t.GetNetname().split('/')[-1],'a':pt(t.GetStart()),'z':pt(t.GetEnd()),'w':p.ToMM(t.GetWidth(p.F_Cu) if isinstance(t,p.PCB_VIA) else t.GetWidth()),'via':isinstance(t,p.PCB_VIA),'layer':b.GetLayerName(t.GetLayer()),'locked':t.IsLocked()} for t in b.GetTracks()],
 'edges':[(pt(t.GetStart()),pt(t.GetEnd())) for t in b.GetDrawings() if isinstance(t,p.PCB_SHAPE) and t.GetLayer()==p.Edge_Cuts],
 'rules':[z.GetZoneName() for z in b.Zones() if z.GetIsRuleArea()],
 'pours':[z.GetNetname() for z in b.Zones() if not z.GetIsRuleArea()]}
def checks(s):
 out=[];f=s['fps']
 def ok(k,v):out.append({'id':k,'pass':bool(v)})
 def dist(a,i,b,j):return math.dist(f[a]['pads'][str(i)]['xy'],f[b]['pads'][str(j)]['xy'])
 ok('BOARD-SIZE',set(q for e in s['edges'] for q in e)=={(0.,0.),(80.,0.),(80.,70.),(0.,70.)} and len(s['edges'])==4)
 ok('TWO-LAYER-1.6',s['cu']==2 and abs(s['thickness']-1.6)<1e-6)
 for r,min_drill in [('J1',1.1),('J2',.8),('J3',1.)]:
  ys=[q[1] for q in f[r]['holes']];py=[q['xy'][1] for q in f[r]['pads'].values()]
  ok('TIE-'+r,len(ys)==2 and all(10<=abs(y-h)<=15 for y in py for h in ys) and 'TIE '+r in s['rules'])
  ok('PTH-'+r,all(v['drill'][0]>=min_drill for v in f[r]['pads'].values()))
 for u,pin,c in [('U1',3,'C1'),('U1',5,'C2'),('U2',14,'C3')]:ok('DECOUPLING-'+c,dist(u,pin,c,1)<5)
 ok('TVS-AT-ENTRY',dist('J3',1,'D1',2)<3.5 and dist('J3',2,'D1',1)<3.5)
 for net in ['CAN_H','CAN_L']:
  ts=[t for t in s['tracks'] if t['net']==net]
  ok('SHORT-LOCKED-FRONT-'+net,ts and all(not t['via'] and t['layer']=='F.Cu' and t['locked'] for t in ts) and sum(math.dist(t['a'],t['z']) for t in ts)<15)
 ok('TVS-GND-VIA',any(t['via'] and t['net']=='GND' and t['locked'] and math.dist(t['a'],f['D1']['pads']['3']['xy'])<1.5 for t in s['tracks']))
 ok('MIN-TRACK',all(t['w']>=.299 for t in s['tracks'] if not t['via']))
 ok('GND-POURS',set(s['pours'])=={'GND'})
 root=ET.parse(P/'verification/P10.xml').getroot();expected={}
 for n in root.findall('./nets/net'):
  for q in n.findall('node'):expected[q.get('ref'),q.get('pin')]=n.get('name').split('/')[-1]
 ok('PCB-PAD-PARITY',all(a['net']==expected.get((r,n)) for r,d in f.items() for n,a in d['pads'].items() if not r.startswith('H')))
 ok('ALL-REFS-VISIBLE',all(d['ref_visible'] for r,d in f.items() if not r.startswith('H')))
 ok('M3-HOLES',all(f['H'+str(i)]['holes']==[q] and 'M3 H'+str(i) in s['rules'] for i,q in enumerate([(5,5),(75,5),(5,65),(75,65)],1)))
 ok('THT-RESISTORS',all('DIN0207' in d['fp'] for r,d in f.items() if r.startswith('R')))
 return out
if __name__=='__main__':
 s=snapshot(p.LoadBoard(str(P/'eda/P10.kicad_pcb')));base=checks(s);neg=[]
 def trial(name,fn):
  cc=copy.deepcopy(s);fn(cc);bad=[t['id'] for t in checks(cc) if not t['pass']];neg.append({'mutation':name,'detected':bool(bad),'by':bad})
 trial('wrong-net',lambda c:c['fps']['J3']['pads']['1'].update(net='GND'))
 trial('small-wire-drill',lambda c:c['fps']['J1']['pads']['1'].update(drill=(.6,.6)))
 trial('missing-anchor',lambda c:c['fps']['J3']['holes'].pop())
 trial('tie-no-keepout',lambda c:c['rules'].remove('TIE J2'))
 trial('remote-cap',lambda c:c['fps']['C2']['pads']['1'].update(xy=(10,60)))
 trial('remote-TVS',lambda c:c['fps']['D1']['pads']['1'].update(xy=(10,60)))
 trial('CAN-on-bottom',lambda c:next(t for t in c['tracks'] if t['net']=='CAN_H').update(layer='B.Cu'))
 trial('unlocked-CAN',lambda c:next(t for t in c['tracks'] if t['net']=='CAN_L').update(locked=False))
 trial('no-local-ground-via',lambda c:c.update(tracks=[t for t in c['tracks'] if not (t['via'] and t['net']=='GND' and t['locked'])]))
 trial('thin-track',lambda c:next(t for t in c['tracks'] if not t['via']).update(w=.2))
 trial('missing-ref',lambda c:c['fps']['U1'].update(ref_visible=False))
 trial('4-layer',lambda c:c.update(cu=4))
 (P/'verification/pcb-checks.json').write_text(json.dumps({'checks':base,'negative_controls':neg,'tracks':len(s['tracks']),'footprints':len(s['fps']),'hardware_tested':False},indent=2)+'\n')
 print('PCB',len(base),'checks;',len(neg),'mutations')
 assert all(t['pass'] for t in base),[t for t in base if not t['pass']]
 assert all(t['detected'] for t in neg),neg
