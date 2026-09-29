"""Remove native-DRC-identified short unlocked 3V3_IO dead copper tails.
No clearance exceptions. Every removal is logged and followed by connectivity/DRC.
"""
from pathlib import Path
import pcbnew as p,json,subprocess,sys
from sexpr import parse,dump,one
P=Path(__file__).resolve().parents[1];fn=P/'eda/P08.kicad_pcb';records=[]
for step in range(5):
 report=P/'routing/tail-drc.json'
 subprocess.run([str(Path(sys.executable).with_name('kicad-cli.exe')),'pcb','drc','--format','json','--severity-all','--refill-zones','-o',str(report),str(fn)],check=True,stdout=subprocess.DEVNULL)
 d=json.loads(report.read_text());ids={i['uuid'] for v in d['violations'] if v['type']=='track_dangling' for i in v['items']}
 if not ids:break
 b=p.LoadBoard(str(fn));tracks={t.m_Uuid.AsString():t for t in b.GetTracks()}
 for id in ids:
  t=tracks[id];assert not isinstance(t,p.PCB_VIA)
  assert t.GetNetname().split('/')[-1]=='3V3_IO' and not t.IsLocked(),'Unexpected dangling critical net'
  assert p.ToMM(t.GetLength())<3
  records.append(dict(net=t.GetNetname(),a=[p.ToMM(t.GetStart().x),p.ToMM(t.GetStart().y)],z=[p.ToMM(t.GetEnd().x),p.ToMM(t.GetEnd().y)]))
 tree=parse(fn.read_text());tree=[g for g in tree if not (isinstance(g,list) and g[0]=='segment' and one(g,'uuid')[1] in ids)]
 fn.write_text(dump(tree)+'\n');b=p.LoadBoard(str(fn));p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity()
 assert b.GetConnectivity().GetUnconnectedCount(True)==0,'Removal opened a connection'
 p.SaveBoard(str(fn),b)
else:raise RuntimeError('Dangling copper did not converge')
(P/'routing/trimmed-tails.json').write_text(json.dumps(records,indent=2)+'\n');print('Trimmed',len(records),'native DRC dead tails')
