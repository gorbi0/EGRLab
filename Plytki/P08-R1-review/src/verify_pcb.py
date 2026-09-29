"""Independent geometry checks on the final native board, with deliberate regressions."""
from pathlib import Path
import pcbnew as p,json,copy,math,xml.etree.ElementTree as ET
P=Path(__file__).resolve().parents[1]
def pt(v):return tuple(round(p.ToMM(a),6) for a in [v.x,v.y])
def snapshot(b):
 return {'cu':b.GetCopperLayerCount(),'thickness':p.ToMM(b.GetDesignSettings().GetBoardThickness()),
 'fps':{f.GetReference():{'xy':pt(f.GetPosition()),'fp':f.GetFPIDAsString(),'pads':{a.GetNumber():{'xy':pt(a.GetPosition()),'drill':pt(a.GetDrillSize()),'size':pt(a.GetSize()),'net':a.GetNetname().split('/')[-1]} for a in f.Pads() if a.GetNumber()},'holes':[pt(a.GetPosition()) for a in f.Pads() if not a.GetNumber()],'ref_visible':f.Reference().IsVisible()} for f in b.GetFootprints()},
 'tracks':[{'net':t.GetNetname().split('/')[-1],'a':pt(t.GetStart()),'z':pt(t.GetEnd()),'w':p.ToMM(t.GetWidth(p.F_Cu) if isinstance(t,p.PCB_VIA) else t.GetWidth()),'via':isinstance(t,p.PCB_VIA),'locked':t.IsLocked()} for t in b.GetTracks()],
 'edges':[(pt(t.GetStart()),pt(t.GetEnd())) for t in b.GetDrawings() if isinstance(t,p.PCB_SHAPE) and t.GetLayer()==p.Edge_Cuts],
 'rules':[z.GetZoneName() for z in b.Zones() if z.GetIsRuleArea()],
 'pours':[z.GetNetname() for z in b.Zones() if not z.GetIsRuleArea()]}
def checks(s):
 out=[];f=s['fps']
 def ok(k,v,n=''):out.append({'id':k,'pass':bool(v),'note':n})
 def dist(a,i,b,j):return math.dist(f[a]['pads'][str(i)]['xy'],f[b]['pads'][str(j)]['xy'])
 ok('BOARD-SIZE',set(q for edge in s['edges'] for q in edge)=={(0.,0.),(100.,0.),(100.,80.),(0.,80.)} and len(s['edges'])==4)
 ok('TWO-LAYER-1.6',s['cu']==2 and abs(s['thickness']-1.6)<1e-6)
 for r in ['J1','J2','J3']:
  ys=[q[1] for q in f[r]['holes']];py=[q['xy'][1] for q in f[r]['pads'].values()]
  ok('TIE-'+r,len(ys)==2 and all(10<=y-h<=15 for y in py for h in ys) and 'TIE '+r in s['rules'])
  ok('PTH-'+r,all(v['drill'][0]>= (1.1 if r=='J1' else .8) for v in f[r]['pads'].values()))
 ok('RELAY-ROW-COORDS',[round(f['K1']['pads'][str(i)]['xy'][1]-f['K1']['pads']['1']['xy'][1],3) for i in range(1,5)]==[0,3.2,5.4,7.6])
 ok('RELAY-OPPOSITE-ROW',all(abs(dist('K1',i,'K1',9-i)-5.08)<1e-5 for i in range(1,5)))
 ok('RELAY-DRILL',all(v['drill']==(.85,.85) for v in f['K1']['pads'].values()))
 ok('MINIFIT-ROW-SPACING',abs(dist('J4',1,'J4',2)-5.5)<1e-5,'Molex SD-5566-002: PCB rows 5.5 mm; 4.2 mm is mating pitch.')
 ok('MINIFIT-DRILL',all(v['drill']==(1.4,1.4) for v in f['J4']['pads'].values()))
 ok('TPS-DECOUPLING',dist('U1',1,'C1',1)<4 and dist('U1',6,'C2',1)<4)
 ok('LOGIC-DECOUPLING',all(dist(u,i,c,1)<5 for u,i,c in [('U3',14,'C3'),('U4',14,'C4'),('U5',14,'C5')]))
 ok('TO92-DECOUPLING',all(dist(u,2,c,1)<6 for u,c in [('U6','C6'),('U7','C7'),('U8','C8')]),'6mm allowance for TO92 body/lead spread; copper path also locally locked.')
 ok('COIL-CAP-NEAR',dist('K1',1,'C9',1)<5)
 ok('FLYBACK-NEAR',dist('K1',8,'D1',2)<8 and dist('K1',1,'D1',1)<8)
 ts=[x for x in s['tracks'] if x['net']=='ILIM_232K']
 ok('ILIM-LOCAL',bool(ts) and all(x['locked'] and not x['via'] for x in ts) and sum(math.dist(x['a'],x['z']) for x in ts)<7)
 ok('MIN-TRACK',all(x['w']>=.299 for x in s['tracks'] if not x['via']))
 ok('NO-SENSOR-GROUND-POUR',set(s['pours'])=={'GND'},'AGND_SENSOR remains a separate routed return, never a GND pour.')
 root=ET.parse(P/'verification/P08.xml').getroot();expected={}
 for n in root.findall('./nets/net'):
  name=n.get('name').split('/')[-1]
  for q in n.findall('node'):expected[(q.get('ref'),q.get('pin'))]=name
 ok('PCB-PAD-PARITY',all(a['net']==expected.get((r,n)) for r,d in f.items() for n,a in d['pads'].items() if not r.startswith('H')))
 ok('ALL-REFS-VISIBLE',all(d['ref_visible'] for r,d in f.items() if not r.startswith('H')))
 ok('M3-HOLES',all(f['H'+str(i)]['holes']==[q] and 'M3 H'+str(i) in s['rules'] for i,q in enumerate([(5,5),(95,5),(5,75),(95,75)],1)))
 ok('THT-RESISTORS',all('DIN0207' in v['fp'] for k,v in f.items() if k.startswith('R')))
 return out
if __name__=='__main__':
 b=p.LoadBoard(str(P/'eda/P08.kicad_pcb'));s=snapshot(b);base=checks(s);neg=[]
 def trial(name,fn):
  c=copy.deepcopy(s);fn(c);bad=[x['id'] for x in checks(c) if not x['pass']];neg.append({'mutation':name,'detected':bool(bad),'by':bad})
 trial('relay-pitch-regression',lambda c:c['fps']['K1']['pads']['2'].update(xy=(29,58)))
 trial('wrong-MiniFit-pitch',lambda c:c['fps']['J4']['pads']['2'].update(xy=(35.2,74)))
 trial('sensor-ground-short',lambda c:c['fps']['J4']['pads']['2'].update(net='GND'))
 trial('ground-pour-bypass',lambda c:c['pours'].append('AGND_SENSOR'))
 trial('missing-anchor',lambda c:c['fps']['J2']['holes'].pop())
 trial('no-tie-keepout',lambda c:c['rules'].remove('TIE J3'))
 trial('M3-no-keepout',lambda c:c['rules'].remove('M3 H1'))
 trial('wrong-drill',lambda c:c['fps']['J1']['pads']['1'].update(drill=(.6,.6)))
 trial('missing-ref',lambda c:c['fps']['U1'].update(ref_visible=False))
 trial('remote-TPS-cap',lambda c:c['fps']['C1']['pads']['1'].update(xy=(50,75)))
 trial('remote-supervisor-cap',lambda c:c['fps']['C7']['pads']['1'].update(xy=(50,75)))
 trial('remote-flyback',lambda c:c['fps']['D1']['pads']['2'].update(xy=(50,75)))
 trial('unlocked-ILIM',lambda c:next(x for x in c['tracks'] if x['net']=='ILIM_232K').update(locked=False))
 trial('thin-track',lambda c:next(x for x in c['tracks'] if not x['via']).update(w=.2))
 trial('4-layer',lambda c:c.update(cu=4))
 result=dict(checks=base,negative_controls=neg,tracks=len(s['tracks']),footprints=len(s['fps']),hardware_tested=False)
 (P/'verification/pcb-checks.json').write_text(json.dumps(result,indent=2)+'\n')
 print('PCB checks',len(base),'negative controls',len(neg))
 for x in base:
  if not x['pass']:print('FAIL',x)
 assert all(x['pass'] for x in base) and all(x['detected'] for x in neg)
