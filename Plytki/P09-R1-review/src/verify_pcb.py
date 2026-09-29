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
 def ok(k,v):out.append({'id':k,'pass':bool(v)})
 def dist(a,i,b,j):return math.dist(f[a]['pads'][str(i)]['xy'],f[b]['pads'][str(j)]['xy'])
 ok('BOARD-SIZE',set(q for e in s['edges'] for q in e)=={(0.,0.),(100.,0.),(100.,100.),(0.,100.)} and len(s['edges'])==4)
 ok('TWO-LAYER-1.6',s['cu']==2 and abs(s['thickness']-1.6)<1e-6)
 for r in ['J1','J2']:
  ys=[q[1] for q in f[r]['holes']];py=[q['xy'][1] for q in f[r]['pads'].values()]
  ok('TIE-'+r,len(ys)==2 and all(10<=y-h<=15 for y in py for h in ys) and 'TIE '+r in s['rules'])
  ok('PTH-'+r,all(v['drill'][0]>=(1.1 if r=='J1' else .8) for v in f[r]['pads'].values()))
 for r in ['J3','J4']:
  a=f[r]['pads']['1']['xy']
  ok('MODULE-PITCH-'+r,all(math.dist(f[r]['pads'][str(i)]['xy'],(a[0]-(i-1)*2.54,a[1]))<1e-5 for i in range(1,10)))
  ok('MODULE-DRILL-'+r,all(v['drill']==(1.,1.) for v in f[r]['pads'].values()))
  ok('MODULE-SUPPORT-'+r,set(f[r]['holes'])=={(a[0],a[1]+16),(round(a[0]-20.32,6),a[1]+16)} and s['rules'].count('NYLON '+r)==2)
 ok('LOGIC-DECOUPLING',all(dist(u,pin,c,1)<5 for u,pin,c in [('U1',14,'C1'),('U2',14,'C2'),('U3',16,'C3')]))
 ok('MODULE-DECOUPLING',dist('J3',1,'C6',1)<5 and dist('J4',1,'C7',1)<5)
 ok('MIN-TRACK',all(t['w']>=.299 for t in s['tracks'] if not t['via']))
 ok('GND-POURS',set(s['pours'])=={'GND'})
 root=ET.parse(P/'verification/P09.xml').getroot();expected={}
 for n in root.findall('./nets/net'):
  for q in n.findall('node'):expected[q.get('ref'),q.get('pin')]=n.get('name').split('/')[-1]
 ok('PCB-PAD-PARITY',all(a['net']==expected.get((r,n)) for r,d in f.items() for n,a in d['pads'].items() if not r.startswith('H')))
 ok('ALL-REFS-VISIBLE',all(d['ref_visible'] for r,d in f.items() if not r.startswith('H')))
 ok('M3-HOLES',all(f['H'+str(i)]['holes']==[q] and 'M3 H'+str(i) in s['rules'] for i,q in enumerate([(5,5),(95,5),(5,95),(95,95)],1)))
 ok('THT-RESISTORS',all('DIN0207' in d['fp'] for r,d in f.items() if r.startswith('R')))
 return out
if __name__=='__main__':
 s=snapshot(p.LoadBoard(str(P/'eda/P09.kicad_pcb')));base=checks(s);neg=[]
 def trial(name,fn):
  c=copy.deepcopy(s);fn(c);bad=[x['id'] for x in checks(c) if not x['pass']];neg.append({'mutation':name,'detected':bool(bad),'by':bad})
 trial('reverse-module',lambda c:c['fps']['J3']['pads']['1'].update(xy=(20,74)))
 trial('small-socket-drill',lambda c:c['fps']['J4']['pads']['1'].update(drill=(.6,.6)))
 trial('wrong-net',lambda c:c['fps']['J3']['pads']['2'].update(net='3V3_IO'))
 trial('missing-anchor',lambda c:c['fps']['J2']['holes'].pop())
 trial('tie-no-keepout',lambda c:c['rules'].remove('TIE J1'))
 trial('support-no-keepout',lambda c:c['rules'].remove('NYLON J3'))
 trial('remote-cap',lambda c:c['fps']['C1']['pads']['1'].update(xy=(90,90)))
 trial('thin-track',lambda c:next(x for x in c['tracks'] if not x['via']).update(w=.2))
 trial('missing-ref',lambda c:c['fps']['U1'].update(ref_visible=False))
 trial('4-layer',lambda c:c.update(cu=4))
 (P/'verification/pcb-checks.json').write_text(json.dumps({'checks':base,'negative_controls':neg,'tracks':len(s['tracks']),'footprints':len(s['fps']),'hardware_tested':False},indent=2)+'\n')
 print('PCB',len(base),'checks;',len(neg),'mutations')
 assert all(x['pass'] for x in base),[x for x in base if not x['pass']]
 assert all(x['detected'] for x in neg),neg
