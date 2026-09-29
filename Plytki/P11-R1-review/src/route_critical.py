"""Four isolated motor traces, 3mm/70um, no vias. Autorouter cannot thin these paths."""
from pathlib import Path
import pcbnew as p,json
P=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(P/'eda/P11.kicad_pcb'));mm=p.FromMM
f={x.GetReference():x for x in b.GetFootprints()};report=[]
def pad(r,n):return next(a for a in f[r].Pads() if a.GetNumber()==str(n))
for net,r1,r2,n in [('ECU_P1','J2','J1',1),('EGR_P1','J2','J1',2),('T_EGR_P1','J8','J9',1),('T_EGR_P3','J8','J9',2)]:
 a=pad(r1,n);z=pad(r2,n);assert a.GetNetname()==z.GetNetname()
 t=p.PCB_TRACK(b);t.SetNet(a.GetNet());t.SetStart(a.GetPosition());t.SetEnd(z.GetPosition());t.SetWidth(mm(3));t.SetLayer(p.F_Cu);t.SetLocked(True);b.Add(t)
 report.append({'net':net,'from':r1+'.'+str(n),'to':r2+'.'+str(n),'width_mm':3,'length_mm':p.ToMM(t.GetLength()),'layer':'F.Cu'})
nc=b.GetDesignSettings().m_NetSettings.GetDefaultNetclass();nc.SetClearance(mm(.25));nc.SetTrackWidth(mm(.3));nc.SetViaDiameter(mm(.8));nc.SetViaDrill(mm(.4))
b.BuildConnectivity();p.SaveBoard(str(P/'eda/P11.kicad_pcb'),b);assert p.ExportSpecctraDSN(b,str(P/'routing/P11.dsn'))
(P/'verification/critical-paths.json').write_text(json.dumps(report,indent=2))
