"""Move C5's low-current VPROT branch off the Kelvin pad onto the force pad."""
from pathlib import Path
import pcbnew as p
P=Path(__file__).resolve().parents[1];fn=P/'eda/P01.kicad_pcb';b=p.LoadBoard(str(fn))
def xy(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
selected=[t for t in b.GetTracks() if not isinstance(t,p.PCB_VIA) and t.GetLayer()==p.B_Cu and t.GetNetname()=='/VPROT' and {tuple(t.GetStart()),tuple(t.GetEnd())}=={tuple(xy(130.5,42)),tuple(xy(133.5,39))}]
assert len(selected)==1
net=selected[0].GetNet();b.Remove(selected[0])
for a,c in [((130.5,42),(136,42)),((136,42),(136,36))]:
 t=p.PCB_TRACK(b);t.SetNet(net);t.SetLayer(p.B_Cu);t.SetWidth(p.FromMM(.5));t.SetStart(xy(*a));t.SetEnd(xy(*c));t.SetLocked(True);b.Add(t)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(fn),b,True)
print('C5 return moved to LK1 force pad; Kelvin branch remains measurement-only.')
