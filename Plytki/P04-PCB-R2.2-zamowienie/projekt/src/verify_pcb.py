"""Fresh native DRC plus independently specified mechanical/electrical PCB checks.
R2: values of the parts changed by the review, the connector-side series resistors (R4-03, R4-07), the SAFE_N end
at U2 (R4-04), KEY marks (R4-05) and GND stitching (R4-06), each with a mutation that the named check must catch."""
from pathlib import Path
import json,math,xml.etree.ElementTree as ET
import pcbnew as p
from provenance import run_fresh_drc
P=Path(__file__).resolve().parents[1]
CK_VAL='R2 values and MPN: U11 MCP100-300 (R4-01), R38/R39 1K and R40 100R (R4-03), C18 1n C0G (R4-04), R41/R42 1K (R4-07)'
CK_SER='Series resistors sit at their connector pin: the connector-side net carries only pin + resistor pad, copper within the limit (R4-03, R4-07)'
CK_END='SAFE_N ends at U2.11: C18 (1 nF) within 5 mm, R5 (100 k) within 16 mm; both on SAFE_N / GND (R4-04)'
CK_KEY='KEY n beside every IDC header, in line with its key pin (<= 1.0 mm along the header), <= 3 mm outside the box, nearest to its own header (R4-05)'
CK_BAND='J2 harness GND row: band without tracks and vias, GND pour allowed, on both layers'
CK_GND='GND pours stitched (R4-06): >= 40 locked GND vias 0.8/0.4; largest island >= 75 % of each pour (as P03)'
def mut_track(bb,n):
 """A 20 mm extra segment on the connector-side net: the detour a resistor placed away from its connector pin needs."""
 t=p.PCB_TRACK(bb);q=next(a for a in bb.GetPads() if a.GetNetname()==n).GetPosition()
 t.SetStart(q);t.SetEnd(p.VECTOR2I(q.x+p.FromMM(20),q.y));t.SetWidth(p.FromMM(.3));t.SetLayer(p.B_Cu);t.SetNet(bb.FindNet(n));return t
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
 zones=[z for z in b.Zones() if z.GetIsRuleArea() and z.GetZoneName()!='GND ROW J2']
 ck('Tie straps and M3 keep copper off both faces',len(zones)==6 and all(z.GetDoNotAllowTracks() and z.GetDoNotAllowVias() and z.GetDoNotAllowZoneFills() and z.IsOnLayer(p.F_Cu) and z.IsOnLayer(p.B_Cu) for z in zones))
 band=[z for z in b.Zones() if z.GetIsRuleArea() and z.GetZoneName()=='GND ROW J2']
 inband=[t.GetNetname() for t in b.GetTracks() for q in ([t.GetPosition()] if isinstance(t,p.PCB_VIA) else [t.GetStart(),t.GetEnd()]) if band and band[0].Outline().Contains(q)]  # crossings: native DRC (keepout)
 ck(CK_BAND,len(band)==1 and band[0].GetDoNotAllowTracks() and band[0].GetDoNotAllowVias() and not band[0].GetDoNotAllowZoneFills() and band[0].IsOnLayer(p.F_Cu) and band[0].IsOnLayer(p.B_Cu) and not inband,{'track_or_via_ends_in_band':inband})
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
 ck('Harness and connector ground pads retain thermals (no solid zone connection)',all(a.GetLocalZoneConnection()!=p.ZONE_CONNECTION_FULL for r in ['J1','J2','J3','J4','J5','J6','J7','J8'] for a in f[r].Pads() if a.GetNumber() and a.GetNetname()=='GND'))
 cfg=json.loads((P/'eda/P04.kicad_pro').read_text());ck('No DRC exclusions; minimum clearance 0.25 mm',not cfg['board']['design_settings']['drc_exclusions'] and cfg['board']['design_settings']['rules']['min_clearance']>=.25)
 ck('Every main part has visible reference',all(f[r].Reference().IsVisible() for r in expected if not r.startswith('H')))
 # ---- R2 ----
 val={'U11':('MCP100-300DI/TO','MCP100-300DI/TO'),'R38':('1K','MFR-25FRF52-1K'),'R39':('1K','MFR-25FRF52-1K'),'R41':('1K','MFR-25FRF52-1K'),
      'R42':('1K','MFR-25FRF52-1K'),'R40':('100R','MFR-25FRF52-100R'),'C18':('1n','K102J15C0GF53H5')}
 got={r:(f[r].GetValue(),f[r].GetFieldText('MPN')) for r in val}
 ck(CK_VAL,got==val,got)
 def cu(n):return round(sum(p.ToMM(t.GetLength()) for t in b.GetTracks() if not isinstance(t,p.PCB_VIA) and t.GetNetname().split('/')[-1]==n),1)
 ser={}
 for n,(r,rp),(j,jp),lim in [('PANEL_3V3',('R40',2),('J8',1),12),('TEST_KEY',('R41',1),('J8',3),8),('MECH_OK',('R42',1),('J8',4),8),('PG_3V3',('R39',2),('J7',1),15)]:
  ser[n]={'resistor_pad':f'{r}.{rp}','connector_pin':f'{j}.{jp}',
   'pads_on_net':sorted(f'{q.GetParentFootprint().GetReference()}.{q.GetNumber()}' for q in b.GetPads() if q.GetNetname().split('/')[-1]==n),
   'distance_mm':round(near(pad(r,rp).GetPosition(),pad(j,jp).GetPosition()),2),'copper_mm':cu(n),'limit_mm':lim}
 ck(CK_SER,all(v['pads_on_net']==sorted([v['resistor_pad'],v['connector_pin']]) and v['copper_mm']<=v['limit_mm'] for v in ser.values()),ser)
 u=pad('U2',11).GetPosition()
 end={'C18.1':round(near(pad('C18',1).GetPosition(),u),2),'R5.1':round(near(pad('R5',1).GetPosition(),u),2),'SAFE_N_copper_mm':cu('SAFE_N')}
 ck(CK_END,net('C18',1)==net('R5',1)=='SAFE_N' and net('C18',2)==net('R5',2)=='GND' and end['C18.1']<=5 and end['R5.1']<=16,end)
 texts=[t for t in b.GetDrawings() if isinstance(t,p.PCB_TEXT) and t.GetLayer()==p.F_SilkS]
 def cbb(r):
  f[r].BuildCourtyardCaches();q=f[r].GetCourtyard(p.F_CrtYd).BBox()
  return (p.ToMM(q.GetLeft()),p.ToMM(q.GetTop()),p.ToMM(q.GetRight()),p.ToMM(q.GetBottom()))
 def rdist(c,bx):return math.hypot(max(bx[0]-c[0],0,c[0]-bx[2]),max(bx[1]-c[1],0,c[1]-bx[3]))
 IDC={'J3':'2','J4':'2','J5':'4','J6':'5'};boxes={r:cbb(r) for r in IDC};keys={}
 for r,key in IDC.items():
  kp=xy(pad(r,key).GetPosition());bx=boxes[r];ed={'T':bx[1],'B':120-bx[3],'L':bx[0],'R':160-bx[2]};e=min(ed,key=ed.get);ax=0 if e in 'TB' else 1;best=None
  for t in texts:
   if t.GetText()!=f'KEY {key}':continue
   q=t.GetBoundingBox();c=(p.ToMM(q.GetCenter().x),p.ToMM(q.GetCenter().y));owner=min(IDC,key=lambda o:rdist(c,boxes[o]))
   cand={'along_offset_mm':round(abs(c[ax]-kp[ax]),2),'gap_to_header_mm':round(rdist(c,bx),2),'nearest_header':owner}
   if owner==r and (best is None or cand['along_offset_mm']<best['along_offset_mm']):best=cand
  keys[r]={'key_pin':key,'text':best}
 ck(CK_KEY,all(v['text'] and v['text']['along_offset_mm']<=1.0 and 0<v['text']['gap_to_header_mm']<=3 for v in keys.values()),keys)
 share={};fill={}
 for L in (p.F_Cu,p.B_Cu):
  areas=[]
  for z in pours:
   if not z.IsOnLayer(L):continue
   ps=z.GetFilledPolysList(L)
   for i in range(ps.OutlineCount()):
    s1=p.SHAPE_POLY_SET();s1.AddOutline(ps.Outline(i))
    for h in range(ps.HoleCount(i)):s1.AddHole(ps.Hole(i,h))
    areas.append(s1.Area()/1e12)
  share[b.GetLayerName(L)]={'islands':len(areas),'largest_percent':round(100*max(areas)/sum(areas),1) if areas else 0}
  fill[b.GetLayerName(L)]=round(sum(areas)/(160*120)*100,1)
 stitch=[t for t in vias if t.GetNetname()=='GND' and t.IsLocked() and abs(p.ToMM(t.GetWidth(p.F_Cu))-.8)<1e-6]
 ck(CK_GND,len(stitch)>=40 and all(v['largest_percent']>=75 for v in share.values()),{'stitching_vias':len(stitch),'pour':share,'filled_percent_of_board':fill})
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
  ('Grounded timing capacitor','C1 lands on U1 timing nodes, not ground',lambda bb:next(a for f in bb.GetFootprints() if f.GetReference()=='C1' for a in f.Pads() if a.GetNumber()=='2').SetNet(bb.FindNet('GND'))),
  ('Panel 3V3 resistor R40 fitted as 0R',CK_VAL,lambda bb:bb.FindFootprintByReference('R40').SetValue('0R')),
  ('TEST_KEY carries a 20 mm detour (R41 away from J8.3)',CK_SER,lambda bb:bb.Add(mut_track(bb,'TEST_KEY'))),
  ('C18 moved to the far end of SAFE_N',CK_END,lambda bb:bb.FindFootprintByReference('C18').SetPosition(p.VECTOR2I(p.FromMM(40),p.FromMM(40)))),
  ('KEY 4 of J5 moved to the pin-1 row',CK_KEY,lambda bb:[t.SetPosition(p.VECTOR2I(t.GetPosition().x,t.GetPosition().y-p.FromMM(2.54))) for t in bb.GetDrawings() if isinstance(t,p.PCB_TEXT) and t.GetText()=='KEY 4']),
  ('Track band under the J2 GND row disabled',CK_BAND,lambda bb:next(z for z in bb.Zones() if z.GetZoneName()=='GND ROW J2').SetDoNotAllowTracks(False)),
  ('Stitching vias on 3V3_IO instead of GND',CK_GND,lambda bb:[v.SetNet(bb.FindNet('3V3_IO')) for v in bb.GetTracks() if isinstance(v,p.PCB_VIA) and v.GetNetname()=='GND' and v.IsLocked()])
 ]:
  m=p.LoadBoard(str(fn));keepalive.append(m);change(m);detected=not next(q['pass'] for q in checks(m) if q['name']==target);neg.append({'mutation':name,'target_check':target,'detected':detected})
 (P/'verification/pcb-checks.json').write_text(json.dumps({'checks':out,'negative_controls':neg},indent=2)+'\n')
 bad=[c['name'] for c in out if not c['pass']];miss=[n['mutation'] for n in neg if not n['detected']]
 print('PCB',len(out)-len(bad),'/',len(out),'negative',len(neg)-len(miss),'/',len(neg));assert not bad and not miss,(bad,miss)
if __name__=='__main__':main()
