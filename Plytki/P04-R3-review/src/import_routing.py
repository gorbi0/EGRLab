"""Import the Freerouting result (SES) and fill the two GND pours (from P04 R2). Run once per SES."""
from pathlib import Path
import pcbnew as p,json,re
from sexpr import parse,dump,one,sub
from board import NAME
P=Path(__file__).resolve().parents[1]
from build_board import W,Hh as H
b=p.LoadBoard(str(P/'routing/prerouted.kicad_pcb'))
# Freerouting repeats identical via padstack definitions. Normalize these;
# no geometry, units, nets or placements are changed by this normalization.
s=parse((P/f'routing/{NAME}.ses').read_text());lib=one(one(s,'routes'),'library_out');seen={}
for item in list(sub(lib,'padstack')):
 if item[1] in seen:
  assert item==seen[item[1]],'Conflicting via definitions'
  lib.remove(item)
 else:seen[item[1]]=item
normalized=P/f'routing/{NAME}-normalized.ses';normalized.write_text(dump(s))
# KiCad 10 Python's SES importer returns False without an error explanation.
# Import the strictly checked path-only subset explicitly. The native DRC and
# schematic parity check independently validate the resulting board.
route=one(s,'routes');assert one(route,'resolution')[1:]==['um','10']
placement=one(s,'placement');assert one(placement,'resolution')[1:]==['um','10']
placements=0
for comp in sub(placement,'component'):
 for place in sub(comp,'place'):
  f=b.FindFootprintByReference(place[1]);assert f is not None
  x,y=float(place[2])/10000,-float(place[3])/10000
  assert abs(p.ToMM(f.GetPosition().x)-x)<.0002 and abs(p.ToMM(f.GetPosition().y)-y)<.0002
  assert place[4]==('back' if f.IsFlipped() else 'front')  # S1-2: SMD on the bottom allowed (P03 R6: none so far)
  assert f.IsFlipped() or abs((f.GetOrientationDegrees()-float(place[5])+180)%360-180)<.001
  placements+=1
def point(x,y):return p.VECTOR2I(p.FromMM(float(x)/10000),p.FromMM(-float(y)/10000))
counts={'placements_checked':placements,'segments_added':0,'vias_added':0}
for nn in sub(one(route,'network_out'),'net'):
 n=b.FindNet(nn[1]);assert n is not None and n.GetNetCode()!=0
 for item in nn[2:]:
  if item[0]=='wire':
   assert all(i[0] in ['path','type'] for i in item[1:]),item
   path=one(item,'path');assert path[1] in ['F.Cu','B.Cu'] and (len(path)-3)%2==0
   layer=p.F_Cu if path[1]=='F.Cu' else p.B_Cu
   for k in range(3,len(path)-2,2):
    t=p.PCB_TRACK(b);t.SetNet(n);t.SetLayer(layer);t.SetWidth(p.FromMM(float(path[2])/10000))
    t.SetStart(point(*path[k:k+2]));t.SetEnd(point(*path[k+2:k+4]));b.Add(t);counts['segments_added']+=1
  elif item[0]=='via':
   assert len(item)==4,item
   ps=seen[item[1]];shapes=sub(ps,'shape');assert len(shapes)==2
   circles=[one(sh,'circle') for sh in shapes]
   assert {c[1] for c in circles}=={'F.Cu','B.Cu'} and circles[0][2:]==circles[1][2:]
   drill=float(re.search(r':([0-9.]+)_um',item[1])[1])/1000
   v=p.PCB_VIA(b);v.SetPosition(point(*item[2:4]));v.SetWidth(p.FromMM(float(circles[0][2])/10000));v.SetDrill(p.FromMM(drill))
   v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(n);b.Add(v);counts['vias_added']+=1
  else:raise ValueError(item)
net=b.FindNet('GND')
assert net is not None
for layer in [p.F_Cu,p.B_Cu]:
 z=p.ZONE(b);z.SetLayer(layer);z.SetNet(net)
 z.SetLocalClearance(p.FromMM(.3));z.SetMinThickness(p.FromMM(.25))
 z.SetPadConnection(p.ZONE_CONNECTION_THERMAL)
 z.SetThermalReliefGap(p.FromMM(.25));z.SetThermalReliefSpokeWidth(p.FromMM(.35))
 z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
 o=z.Outline();o.NewOutline()
 for x,y in [(.3,.3),(W-.3,.3),(W-.3,H-.3),(.3,H-.3)]:o.Append(p.FromMM(x),p.FromMM(y))  # S1 outline (fill keeps 0.5 mm from the edge)
 b.Add(z)
# 2.10 (review MINOR-1): named rule areas over the pad rings of the fine-pitch parts, no restriction in them; set_rules.py gives the GND
# pours 0.15 mm only to items wholly inside (pads, inner stubs and vias), 0.3 mm to the escapes that leave. Made after the router (a DSN
# keepout holding pins breaks it); complete_routes.py / stitch.py ignore areas named DRC_ONLY_*.
from board import FINE
for ref in FINE:
 f_=b.FindFootprintByReference(ref);f_.BuildCourtyardCaches();bb=f_.GetCourtyard(p.F_CrtYd).BBox()
 z=p.ZONE(b);z.SetIsRuleArea(True);z.SetZoneName(f'DRC_ONLY_{ref}');ls=p.LSET();ls.AddLayer(p.F_Cu);ls.AddLayer(p.B_Cu);z.SetLayerSet(ls)
 z.SetDoNotAllowTracks(False);z.SetDoNotAllowVias(False);z.SetDoNotAllowZoneFills(False);z.SetDoNotAllowPads(False);z.SetDoNotAllowFootprints(False)
 o=z.Outline();o.NewOutline()
 for x,y in [(bb.GetLeft(),bb.GetTop()),(bb.GetRight(),bb.GetTop()),(bb.GetRight(),bb.GetBottom()),(bb.GetLeft(),bb.GetBottom())]:o.Append(int(x),int(y))
 b.Add(z)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones())
p.SaveBoard(str(P/f'eda/{NAME}.kicad_pcb'),b)
(P/'verification/ses-import.json').write_text(json.dumps(counts,indent=2))
print('SES imported; GND planes filled; saved native board.')
