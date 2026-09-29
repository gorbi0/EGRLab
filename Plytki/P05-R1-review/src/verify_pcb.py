"""Native KiCad DRC and independent mechanical/copper acceptance with fault injection."""
from pathlib import Path
import json,math,xml.etree.ElementTree as ET
import pcbnew as p
from provenance import run_fresh_drc
P=Path(__file__).resolve().parents[1]
def checks(b):
 f={x.GetReference():x for x in b.GetFootprints()};out=[]
 def ck(n,v,d=None):out.append({'name':n,'pass':bool(v),'detail':d})
 def pad(r,n):return next(a for a in f[r].Pads() if a.GetNumber()==str(n))
 def xy(v):return [p.ToMM(v.x),p.ToMM(v.y)]
 def net(r,n):return pad(r,n).GetNetname().split('/')[-1]
 ck('Two layers, 160x120, thickness 1.6',b.GetCopperLayerCount()==2 and abs(p.ToMM(b.GetDesignSettings().GetBoardThickness())-1.6)<.001 and abs(p.ToMM(b.GetBoardEdgesBoundingBox().GetWidth())-160)<.06)
 ck('M3 mounting grid',all(xy(next(iter(f['H'+str(i)].Pads())).GetPosition())==pos for i,pos in enumerate([[5,5],[155,5],[5,115],[155,115]],1)))
 expect={r for r in json.loads((P/'docs/parts.json').read_text())}|{'H1','H2','H3','H4'}
 ck('Complete board inventory',set(f)==expect,{'footprints':len(f)})
 nn={}
 for n in ET.parse(P/'verification/P05.xml').getroot().findall('./nets/net'):
  for a in n.findall('node'):nn[a.get('ref'),a.get('pin')]=n.get('name')
 wrong=[]
 for r in expect-{'H1','H2','H3','H4'}:
  for a in f[r].Pads():
   if a.GetNumber() and a.GetNetname()!=nn.get((r,a.GetNumber())):wrong.append([r,a.GetNumber()])
 ck('Every pad matches schematic export',not wrong,wrong)
 anchor={}
 for r in ['J2','J3','J4','J5','J6']:
  aa=[a for a in f[r].Pads() if not a.GetNumber()];ss=[a for a in f[r].Pads() if a.GetNumber()]
  # Project the tie-to-pad vector on the local row-normal, rotation invariant.
  theta=math.radians(f[r].GetOrientationDegrees());normal=[math.sin(theta),math.cos(theta)]
  dd=sorted({round(abs(sum((u-v)*w for u,v,w in zip(xy(a.GetPosition()),xy(q.GetPosition()),normal))),4) for a in aa for q in ss})
  anchor[r]=dd
 ck('Tie distance 10..15 mm on all five harnesses',all(len(v)>0 and min(v)>=10 and max(v)<=15 for v in anchor.values()),anchor)
 ck('Harness PTH drill and anchor count',all(sum(not a.GetNumber() for a in f[r].Pads())==2 and all(abs(p.ToMM(a.GetDrillSize().x)-(.8 if r=='J3' else 1.1))<.001 for a in f[r].Pads() if a.GetNumber()) for r in ['J2','J3','J4','J5','J6']))
 zones=[z for z in b.Zones() if z.GetIsRuleArea()];tie=[z for z in zones if z.GetZoneName().startswith(('TIE','M3'))]
 ck('No copper beneath ties or M3 washers',len(tie)==9 and all(z.GetDoNotAllowTracks() and z.GetDoNotAllowVias() and z.GetDoNotAllowZoneFills() and z.IsOnLayer(p.F_Cu) and z.IsOnLayer(p.B_Cu) for z in tie))
 ag=[z for z in zones if z.GetZoneName().startswith('ANALOG_GND_PLANE_')]
 ck('Analog bottom-plane protection',len(ag)==3 and all(z.IsOnLayer(p.B_Cu) and not z.IsOnLayer(p.F_Cu) and z.GetDoNotAllowTracks() and not z.GetDoNotAllowZoneFills() for z in ag))
 ck('C1 actual 470uF Panasonic pitch',f['C1'].GetFPIDAsString().endswith('CP_Radial_D8.0mm_P3.50mm') and abs(math.dist(xy(pad('C1',1).GetPosition()),xy(pad('C1',2).GetPosition()))-3.5)<.001)
 ck('Switch C-terminal drill and pitch',all(abs(p.ToMM(a.GetDrillSize().x)-1.85)<.001 for a in f['SW1'].Pads()) and abs(math.dist(xy(pad('SW1',1).GetPosition()),xy(pad('SW1',4).GetPosition()))-4.83)<.001)
 ck('AD7606B reference pins and VDRIVE',net('U1',10)==net('U1',23)=='3V3_DAQ' and net('U1',44)==net('U1',45)=='REFCAP' and net('U1',36)!=net('U1',39))
 ck('B2B pin1 in far column matching P03 height',xy(pad('J1',1).GetPosition())==[6.5,31] and xy(pad('J1',2).GetPosition())==[3.96,31] and net('J1',2).startswith('unconnected-'))
 dec={}
 for c,n in [('C4',1),('C5',37),('C6',38),('C7',48),('C8',23),('C9',36),('C10',39),('C11',42),('C13',44)]:dec[c]=round(math.dist(xy(pad('U1',n).GetPosition()),xy(pad(c,1).GetPosition())),3)
 ck('ADC local capacitors within 15 mm',max(dec.values())<=15,dec)
 refnets={}
 for name in ['REGCAP_A','REGCAP_D','REFCAP','ADC_REF']:
  tt=[t for t in b.GetTracks() if t.GetNetname().split('/')[-1]==name]
  refnets[name]={'length_mm':sum(p.ToMM(t.GetLength()) for t in tt if not isinstance(t,p.PCB_VIA)),'vias':sum(isinstance(t,p.PCB_VIA) for t in tt)}
 ck('Reference and regulator traces have no vias',all(x['vias']==0 for x in refnets.values()),refnets)
 widths=[p.ToMM(t.GetWidth()) for t in b.GetTracks() if not isinstance(t,p.PCB_VIA)]
 ck('Track fabrication minima',bool(widths) and min(widths)>=.14999,{'minimum_mm':min(widths) if widths else None})
 pours=[z for z in b.Zones() if not z.GetIsRuleArea()]
 ck('Ground pours both faces, isolated islands removed',len(pours)==2 and {z.GetLayer() for z in pours}=={p.F_Cu,p.B_Cu} and all(z.GetNetname()=='GND' and z.GetIslandRemovalMode()==p.ISLAND_REMOVAL_MODE_ALWAYS for z in pours))
 ck('Harness grounds retain thermals',all(a.GetLocalZoneConnection()!=p.ZONE_CONNECTION_FULL for r in ['J1','J2','J3','J4','J5','J6'] for a in f[r].Pads() if a.GetNetname()=='GND'))
 cfg=json.loads((P/'eda/P05.kicad_pro').read_text());ck('No DRC exclusions',not cfg['board']['design_settings']['drc_exclusions'])
 ck('All component references visible',all(f[r].Reference().IsVisible() for r in expect if not r.startswith('H')))
 return out
def main():
 fn=P/'eda/P05.kicad_pcb';drc,_=run_fresh_drc(fn,P/'verification/drc.json');b=p.LoadBoard(str(fn));out=checks(b)
 out.insert(0,{'name':'Native all-severity DRC, unconnected and parity','pass':not any(drc[k] for k in ['violations','unconnected_items','schematic_parity']),'detail':{k:len(drc[k]) for k in ['violations','unconnected_items','schematic_parity']}})
 neg=[];keep=[b]
 for title,target,change in [
  ('Wrong C1 footprint','C1 actual 470uF Panasonic pitch',lambda bb:bb.FindFootprintByReference('C1').SetFPIDAsString('Capacitor_THT:CP_Radial_D10.0mm_P5.00mm')),
  ('Disabled analog plane rule','Analog bottom-plane protection',lambda bb:next(z for z in bb.Zones() if z.GetZoneName().startswith('ANALOG_GND_PLANE_')).SetDoNotAllowTracks(False)),
  ('Disabled cable tie rule','No copper beneath ties or M3 washers',lambda bb:next(z for z in bb.Zones() if z.GetZoneName()=='TIE J2').SetDoNotAllowVias(False)),
  ('Capacitor far from ADC','ADC local capacitors within 15 mm',lambda bb:bb.FindFootprintByReference('C4').SetPosition(p.VECTOR2I(p.FromMM(20),p.FromMM(15)))),
  ('Hidden component reference','All component references visible',lambda bb:bb.FindFootprintByReference('U1').Reference().SetVisible(False))]:
  m=p.LoadBoard(str(fn));keep.append(m);change(m);neg.append({'mutation':title,'detected':not next(c['pass'] for c in checks(m) if c['name']==target)})
 (P/'verification/pcb-checks.json').write_text(json.dumps({'checks':out,'negative_controls':neg},indent=2)+'\n')
 bad=[c['name'] for c in out if not c['pass']];miss=[c['mutation'] for c in neg if not c['detected']]
 print('PCB',len(out)-len(bad),'/',len(out),'mutations',len(neg)-len(miss),'/',len(neg));assert not bad and not miss,(bad,miss)
if __name__=='__main__':main()
