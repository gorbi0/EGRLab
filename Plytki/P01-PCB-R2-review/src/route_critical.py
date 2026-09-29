"""Explicit high-current paths and local gate/Kelvin paths, before signal routing."""
from pathlib import Path
import pcbnew as p,json
P=Path(__file__).resolve().parents[1];path=P/'eda/P01.kicad_pcb';b=p.LoadBoard(str(path))
mm=p.FromMM
def xy(x,y):return p.VECTOR2I(mm(x),mm(y))
net={n.GetNetname().split('/')[-1]:n for n in b.GetNetInfo().NetsByNetcode().values()}
def tr(n,pts,w,layer):
 for a,c in zip(pts,pts[1:]):
  t=p.PCB_TRACK(b);t.SetStart(xy(*a));t.SetEnd(xy(*c));t.SetWidth(mm(w));t.SetLayer(layer);t.SetNet(net[n]);t.SetLocked(True);b.Add(t)
F=p.F_Cu;B=p.B_Cu
tr('BAT_FUSED',[(15,31.5),(44,31.5)],5,F)
tr('BAT_FUSED',[(44,31.5),(49,28),(52.46,26.5),(52.46,22.3)],2,F)
tr('BAT_FUSED',[(52.46,26.5),(57.54,26.5),(57.54,22.3)],2,F)
tr('BAT_FUSED',[(15,31.5),(12,37)],3,F)
tr('P01_VS',[(55,22.3),(55,28),(55,34)],2,B)
tr('P01_VS',[(55,34),(110.54,34)],5,B)
tr('P01_VS',[(55,34),(94,34)],5,F)
tr('P01_VS',[(110.54,34),(110.54,27),(110.54,22.3)],2,B)
tr('P01_Q1_DRAIN',[(108,22.3),(108,30),(115,30),(118,34)],2,F)
tr('P01_Q1_DRAIN',[(118,34),(122,36),(126,36)],4,F)
tr('VPROT',[(136,36),(144,36)],5,F)
tr('VPROT',[(144,36),(148,32)],2,F)
tr('VPROT',[(144,36),(144,44),(140,48),(130,48)],3,F)
tr('VPROT',[(130,48),(132,54),(136,58)],1.5,F)
# Input/output power return. The logic lies below this corridor.
tr('GND',[(32.32,37),(28,37),(22.62,31)],4,B)
tr('GND',[(22.62,19),(31,19),(34,9.5),(146,9.5),(153,16.5),(153,44),(150.32,48)],5,B)
tr('GND',[(153,26.92),(148,26.92)],2,B)
# Probe branches terminate at device pads and carry no load current.
tr('P01_VS',[(110.54,22.3),(110.54,25.04),(112,26.5)],.5,F)
tr('P01_GATE',[(105.46,22.3),(105.46,23.54),(103,26)],.5,F)
tr('P01_GATE',[(103,26),(99,30),(98,34),(98,40),(100,40)],.8,F)
tr('P01_GATE',[(100,40),(100,44.5),(101.78,47)],.8,F)
tr('P01_GATE',[(100,44.5),(115,44.5),(115,42)],.6,F)
tr('P01_OFF_COL',[(84,53.5),(84,47)],1,F)
tr('P01_VS',[(86.54,53.5),(88,50),(88,34)],.8,B)
tr('P01_VS',[(110.54,34),(105,40),(106,48)],.8,B)
tr('P01_Q1_DRAIN',[(126,36),(128.5,39)],.4,F)
tr('VPROT',[(136,36),(133.5,39)],.4,F)
for x in [55,70,94]:
 v=p.PCB_VIA(b);v.SetPosition(xy(x,34));v.SetWidth(mm(1.2));v.SetDrill(mm(.6));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(F,B);v.SetNet(net['P01_VS']);v.SetLocked(True);b.Add(v)

def zone(n,points,layer,priority=0,thermal=.5,gap=.3):
 z=p.ZONE(b);z.SetLayer(layer);z.SetNet(net[n]);z.SetAssignedPriority(priority)
 z.SetLocalClearance(mm(.3));z.SetMinThickness(mm(.25));z.SetPadConnection(p.ZONE_CONNECTION_THERMAL)
 z.SetThermalReliefGap(mm(gap));z.SetThermalReliefSpokeWidth(mm(thermal));z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
 o=z.Outline();o.NewOutline()
 for x,y in points:o.Append(mm(x),mm(y))
 b.Add(z)
for layer in [F,B]:zone('BAT_FUSED',[(10,20.5),(19.5,20.5),(19.5,34),(10,34)],layer,10,1.2)
nc=b.GetDesignSettings().m_NetSettings.GetDefaultNetclass();nc.SetClearance(mm(.3));nc.SetTrackWidth(mm(.5));nc.SetViaDiameter(mm(1));nc.SetViaDrill(mm(.5))
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(path),b)
assert p.ExportSpecctraDSN(b,str(P/'routing/P01.dsn'))
print('Critical tracks locked; BAT thermal island filled; DSN exported.')
