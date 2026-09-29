"""Fresh native DRC plus independently specified mechanical/electrical PCB checks."""
from pathlib import Path
import json,math,xml.etree.ElementTree as ET
import pcbnew as p
from provenance import run_fresh_drc
P=Path(__file__).resolve().parents[1]
def checks(b):
 f={q.GetReference():q for q in b.GetFootprints()};out=[]
 def ck(n,v,d=None):out.append({'name':n,'pass':bool(v),'detail':d})
 def pad(r,n):return next(a for a in f[r].Pads() if a.GetNumber()==str(n))
 def xy(q):return [p.ToMM(q.x),p.ToMM(q.y)]
 def near(a,c):return math.dist(xy(a),xy(c))
 def net(r,n):return pad(r,n).GetNetname().split('/')[-1]
 ck('Two layers and 1.6 mm FR4',b.GetCopperLayerCount()==2 and abs(p.ToMM(b.GetDesignSettings().GetBoardThickness())-1.6)<.001)
 bb=b.GetBoardEdgesBoundingBox();ck('160 x 120 mm outline',abs(p.ToMM(bb.GetWidth())-160)<.06 and abs(p.ToMM(bb.GetHeight())-120)<.06)
 holes=[xy(next(iter(f['H'+str(i)].Pads())).GetPosition()) for i in range(1,5)]
 ck('Four M3 holes at 5 mm offsets',holes==[[5,5],[155,5],[5,115],[155,115]])
 parts=json.loads((P/'docs/parts.json').read_text());expected={r for r,v in parts.items() if v['on_board']}|{'H1','H2','H3','H4'}
 ck('Main carrier inventory; adapter capacitors excluded',set(f)==expected and not {'C15','C16','C17'}&set(f),{'footprints':len(f)})
 pin={}
 for n in ET.parse(P/'verification/P04.xml').getroot().findall('./nets/net'):
  for q in n.findall('node'):pin[q.get('ref'),q.get('pin')]=n.get('name')
 wrong=[];count=0
 for r in sorted(expected-{'H1','H2','H3','H4'}):
  for a in f[r].Pads():
   if a.GetNumber():
    count+=1
    if a.GetNetname()!=pin.get((r,a.GetNumber())):wrong.append([r,a.GetNumber(),a.GetNetname()])
 ck('Every numbered pad matches exported XML',not wrong,{'pads':count,'wrong':wrong})
 ck('MCP100 D and 2N3904 physical pin assignment',all(net('U11',k)==v for k,v in {1:'LOCAL_SUP_N',2:'3V3_IO',3:'GND'}.items()) and all(net('Q'+str(i),1)=='GND' and net('Q'+str(i),3)=='SAFE_N' for i in range(1,4)))
 ck('IDC finished drill 1.2 mm, pad 1.9 mm',all(abs(p.ToMM(a.GetDrillSize().x)-1.2)<.001 and p.ToMM(a.GetSize().x)>=1.9 for r in ['J3','J4','J5','J6'] for a in f[r].Pads() if a.GetNumber()))
 ck('Keys and SENSOR spare pads are NC',all(net(r,n).startswith('unconnected-') for r,n in [('J2',4),('J3',2),('J4',2),('J4',5),('J4',6),('J5',4),('J6',5)]))
 ck('Harness PTHs for AWG22 and AWG28',all(abs(p.ToMM(a.GetDrillSize().x)-d)<.001 for r,d in [('J1',1.1),('J2',.8)] for a in f[r].Pads() if a.GetNumber()))
 anc={};ok=True
 for r in ['J1','J2']:
  aa=[a for a in f[r].Pads() if not a.GetNumber()];signal=[a for a in f[r].Pads() if a.GetNumber()]
  dd=sorted({round(abs(p.ToMM(a.GetPosition().y-q.GetPosition().y)),3) for a in aa for q in signal});anc[r]=dd
  ok &= len(aa)==2 and all(10<=v<=15 for v in dd) and all(abs(p.ToMM(a.GetDrillSize().x)-3.2)<.001 for a in aa)
 ck('Cable tie anchors 10-15 mm from solder rows',ok,anc)
 zones=[z for z in b.Zones() if z.GetIsRuleArea()]
 ck('Tie straps and M3 keep copper off both faces',len(zones)==6 and all(z.GetDoNotAllowTracks() and z.GetDoNotAllowVias() and z.GetDoNotAllowZoneFills() and z.IsOnLayer(p.F_Cu) and z.IsOnLayer(p.B_Cu) for z in zones))
 dec={}
 for i in range(1,12):dec[f'U{i}/C{i+3}']=round(near(pad('U'+str(i),16 if i==1 else 2 if i==11 else 14).GetPosition(),pad('C'+str(i+3),1).GetPosition()),3)
 ck('Carrier decouplers at most 8 mm from supply pin',max(dec.values())<=8,dec)
 wd={}
 for n in ['WD_RC','WD_C']:
  tracks=[t for t in b.GetTracks() if t.GetNetname().split('/')[-1]==n]
  wd[n]={'length_mm':round(sum(p.ToMM(t.GetLength()) for t in tracks if not isinstance(t,p.PCB_VIA)),3),'vias':sum(isinstance(t,p.PCB_VIA) for t in tracks),'all_front_locked':all(t.GetLayer()==p.F_Cu and t.IsLocked() for t in tracks)}
 ck('Watchdog RC traces short, locked and without vias',all(v['length_mm']<=15 and v['vias']==0 and v['all_front_locked'] for v in wd.values()),wd)
 ck('C1 lands on U1 timing nodes, not ground',net('C1',1)==net('U1',15)=='WD_RC' and net('C1',2)==net('U1',14)=='WD_C')
 widths=[p.ToMM(t.GetWidth()) for t in b.GetTracks() if not isinstance(t,p.PCB_VIA)]
 vias=[t for t in b.GetTracks() if isinstance(t,p.PCB_VIA)]
 ck('Tracks >=0.30 mm; vias 0.8/0.4 mm',min(widths)>=.29999 and all(p.ToMM(t.GetWidth(p.F_Cu))>=.8 and p.ToMM(t.GetDrill())>=.4 for t in vias),{'minimum_track_mm':min(widths),'vias':len(vias)})
 pours=[z for z in b.Zones() if not z.GetIsRuleArea()]
 ck('Ground pours on both sides, no isolated islands',len(pours)==2 and {z.GetLayer() for z in pours}=={p.F_Cu,p.B_Cu} and all(z.GetNetname()=='GND' and z.GetIslandRemovalMode()==p.ISLAND_REMOVAL_MODE_ALWAYS and z.GetFilledPolysList(z.GetLayer()).OutlineCount()>0 for z in pours))
 ck('Harness and connector ground pads retain thermals',all(a.GetLocalZoneConnection()!=p.ZONE_CONNECTION_FULL for r in ['J1','J2','J3','J4','J5','J6','J7','J8'] for a in f[r].Pads() if a.GetNumber() and a.GetNetname()=='GND'))
 cfg=json.loads((P/'eda/P04.kicad_pro').read_text());ck('No DRC exclusions; minimum clearance 0.25 mm',not cfg['board']['design_settings']['drc_exclusions'] and cfg['board']['design_settings']['rules']['min_clearance']>=.25)
 ck('Every main part has visible reference',all(f[r].Reference().IsVisible() for r in expected if not r.startswith('H')))
 return out
def main():
 fn=P/'eda/P04.kicad_pcb';drc,_=run_fresh_drc(fn,P/'verification/drc.json');b=p.LoadBoard(str(fn));out=checks(b)
 out.insert(0,{'name':'Native DRC / unconnected / schematic parity','pass':not any(drc[k] for k in ['violations','unconnected_items','schematic_parity']),'detail':{k:len(drc[k]) for k in ['violations','unconnected_items','schematic_parity']}})
 neg=[]; keepalive=[b]
 for name,target,change in [
  ('Swap local supervisor ground','MCP100 D and 2N3904 physical pin assignment',lambda bb:next(a for f in bb.GetFootprints() if f.GetReference()=='U11' for a in f.Pads() if a.GetNumber()=='3').SetNet(bb.FindNet('3V3_IO'))),
  ('Wrong IDC hole','IDC finished drill 1.2 mm, pad 1.9 mm',lambda bb:next(a for f in bb.GetFootprints() if f.GetReference()=='J3' for a in f.Pads()).SetDrillSize(p.VECTOR2I(p.FromMM(.8),p.FromMM(.8)))),
  ('Disabled tie keepout','Tie straps and M3 keep copper off both faces',lambda bb:next(z for z in bb.Zones() if z.GetZoneName()=='TIE J2').SetDoNotAllowTracks(False)),
  ('Decoupler moved away','Carrier decouplers at most 8 mm from supply pin',lambda bb:bb.FindFootprintByReference('C4').SetPosition(p.VECTOR2I(p.FromMM(30),p.FromMM(10)))),
  ('Grounded timing capacitor','C1 lands on U1 timing nodes, not ground',lambda bb:next(a for f in bb.GetFootprints() if f.GetReference()=='C1' for a in f.Pads() if a.GetNumber()=='2').SetNet(bb.FindNet('GND')))
 ]:
  m=p.LoadBoard(str(fn));keepalive.append(m);change(m);detected=not next(q['pass'] for q in checks(m) if q['name']==target);neg.append({'mutation':name,'target_check':target,'detected':detected})
 (P/'verification/pcb-checks.json').write_text(json.dumps({'checks':out,'negative_controls':neg},indent=2)+'\n')
 bad=[c['name'] for c in out if not c['pass']];miss=[n['mutation'] for n in neg if not n['detected']]
 print('PCB',len(out)-len(bad),'/',len(out),'negative',len(neg)-len(miss),'/',len(neg));assert not bad and not miss,(bad,miss)
if __name__=='__main__':main()
