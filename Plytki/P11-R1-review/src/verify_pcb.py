"""Final native copper geometry and real header footprints, independent of the routing generator."""
from pathlib import Path
import pcbnew as p,json,copy,math,xml.etree.ElementTree as ET
from sexpr import parse,one,sub
P=Path(__file__).resolve().parents[1]
def pt(v):return tuple(round(p.ToMM(a),6) for a in [v.x,v.y])
def snapshot(b):
 return {'cu':b.GetCopperLayerCount(),'thickness':p.ToMM(b.GetDesignSettings().GetBoardThickness()),'fps':{f.GetReference():{'xy':pt(f.GetPosition()),'fp':f.GetFPIDAsString(),'pads':{a.GetNumber():{'xy':pt(a.GetPosition()),'drill':pt(a.GetDrillSize()),'size':pt(a.GetSize()),'net':a.GetNetname().split('/')[-1]} for a in f.Pads() if a.GetNumber()},'holes':[pt(a.GetPosition()) for a in f.Pads() if not a.GetNumber()],'ref_visible':f.Reference().IsVisible()} for f in b.GetFootprints()},'tracks':[{'net':t.GetNetname().split('/')[-1],'a':pt(t.GetStart()),'z':pt(t.GetEnd()),'w':p.ToMM(t.GetWidth(p.F_Cu) if isinstance(t,p.PCB_VIA) else t.GetWidth()),'via':isinstance(t,p.PCB_VIA),'layer':b.GetLayerName(t.GetLayer()),'locked':t.IsLocked()} for t in b.GetTracks()],'edges':[(pt(t.GetStart()),pt(t.GetEnd())) for t in b.GetDrawings() if isinstance(t,p.PCB_SHAPE) and t.GetLayer()==p.Edge_Cuts],'rules':[z.GetZoneName() for z in b.Zones() if z.GetIsRuleArea()],'pours':[z.GetNetname() for z in b.Zones() if not z.GetIsRuleArea()]}
def checks(s):
 out=[];f=s['fps']
 def ok(k,v):out.append({'id':k,'pass':bool(v)})
 ok('BOARD-SIZE',set(q for e in s['edges'] for q in e)=={(0.,0.),(160.,0.),(160.,110.),(0.,110.)} and len(s['edges'])==4)
 ok('TWO-LAYER-1.6',s['cu']==2 and abs(s['thickness']-1.6)<1e-6)
 stack=one(one(parse((P/'eda/P11.kicad_pcb').read_text()),'setup'),'stackup')
 thick={x[1]:float(one(x,'thickness')[1]) for x in sub(stack,'layer') if x[1] in ['F.Cu','B.Cu']}
 ok('CU70-STACKUP',thick=={'F.Cu':.07,'B.Cu':.07})
 for r in ['J2','J3','J4','J5','J6','J8','J9','J10','J11']:
  ys=[q[1] for q in f[r]['holes']];py=[q['xy'][1] for q in f[r]['pads'].values()]
  ok('TIE-'+r,len(ys)==2 and all(10<=abs(y-h)<=15 for y in py for h in ys) and 'TIE '+r in s['rules'])
  ok('PTH-'+r,all(v['drill'][0]>=1.099 for v in f[r]['pads'].values()))
 for r in ['J2','J8','J9']:ok('POWER-PTH-'+r,all(f[r]['pads'][n]['drill'][0]>=2.199 for n in ['1','2']))
 for net in ['ECU_P1','EGR_P1','T_EGR_P1','T_EGR_P3']:
  ts=[t for t in s['tracks'] if t['net']==net]
  ok('POWER-'+net,bool(ts) and all(not t['via'] and t['w']>=2.999 and t['layer']=='F.Cu' and t['locked'] for t in ts) and sum(math.dist(t['a'],t['z']) for t in ts)<=15)
 ok('MIN-TRACK',all(t['w']>=.299 for t in s['tracks'] if not t['via']))
 ok('GND-POURS-ONLY',set(s['pours'])=={'GND'})
 root=ET.parse(P/'verification/P11.xml').getroot();expected={}
 for n in root.findall('./nets/net'):
  for q in n.findall('node'):expected[q.get('ref'),q.get('pin')]=n.get('name').split('/')[-1]
 ok('PCB-PAD-PARITY',all(a['net']==expected.get((r,n)) for r,d in f.items() for n,a in d['pads'].items() if not r.startswith('H')))
 ok('ALL-REFS-VISIBLE',all(d['ref_visible'] for r,d in f.items() if not r.startswith('H')))
 ok('M3-HOLES',all(f['H'+str(i)]['holes']==[q] and 'M3 H'+str(i) in s['rules'] for i,q in enumerate([(5,5),(155,5),(5,105),(155,105)],1)))
 ok('NO-OFFBOARD-PARTS-ON-PCB',set(f)=={'J'+str(i) for i in range(1,12)}|{'H1','H2','H3','H4'})
 j=f['J1']['pads'];ok('PHOENIX-DRILL-PITCH',all(abs(x['drill'][0]-1.4)<.001 for x in j.values()) and all(abs(math.dist(j[str(i)]['xy'],j[str(i+1)]['xy'])-5.08)<.001 for i in range(1,4)))
 j=f['J7'];ps=j['pads'];ok('MOLEX-12A2-PEGS',len(ps)==12 and len(j['holes'])==2 and '12A2' in j['fp'] and all(abs(x['drill'][0]-1.4)<.001 for x in ps.values()) and abs(math.dist(ps['1']['xy'],ps['2']['xy'])-4.2)<.001 and abs(math.dist(ps['1']['xy'],ps['7']['xy'])-5.5)<.001)
 return out
if __name__=='__main__':
 s=snapshot(p.LoadBoard(str(P/'eda/P11.kicad_pcb')));base=checks(s);neg=[]
 def trial(name,fn):
  cc=copy.deepcopy(s);fn(cc);bad=[t['id'] for t in checks(cc) if not t['pass']];neg.append({'mutation':name,'detected':bool(bad),'by':bad})
 trial('sensor-ground-bond',lambda c:c['fps']['J10']['pads']['2'].update(net='GND'))
 trial('small-power-hole',lambda c:c['fps']['J8']['pads']['1'].update(drill=(1.1,1.1)))
 trial('missing-tie',lambda c:c['fps']['J11']['holes'].pop())
 trial('tie-no-keepout',lambda c:c['rules'].remove('TIE J5'))
 for key,val in [('w',.3),('via',True),('locked',False),('layer','B.Cu')]:trial('motor-'+key,lambda c,key=key,val=val:next(t for t in c['tracks'] if t['net']=='ECU_P1').update({key:val}))
 trial('missing-motor',lambda c:c.update(tracks=[t for t in c['tracks'] if t['net']!='T_EGR_P1']))
 trial('wrong-header-drill',lambda c:c['fps']['J1']['pads']['1'].update(drill=(1,1)))
 trial('no-Molex-pegs',lambda c:c['fps']['J7'].update(holes=[]))
 trial('invisible-ref',lambda c:c['fps']['J7'].update(ref_visible=False))
 trial('4-layer',lambda c:c.update(cu=4))
 (P/'verification/pcb-checks.json').write_text(json.dumps({'checks':base,'negative_controls':neg,'tracks':len(s['tracks']),'footprints':len(s['fps']),'hardware_tested':False},indent=2)+'\n')
 print('PCB',len(base),'checks;',len(neg),'mutations');assert all(t['pass'] for t in base),[t for t in base if not t['pass']];assert all(t['detected'] for t in neg)
