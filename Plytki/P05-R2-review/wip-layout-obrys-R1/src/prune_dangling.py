"""Remove only free router stubs identified by native DRC, preserving connectivity.
Locked deliberate copper is never removed. Each removed segment is recorded.
"""
from pathlib import Path
import pcbnew as p,json,subprocess,sys
P=Path(__file__).resolve().parents[1];fn=P/'eda/P05.kicad_pcb'
cli=Path(sys.executable).with_name('kicad-cli.exe');report=P/'routing/prune-drc.json';removed=[];keep=[]
for attempt in range(10):
 subprocess.run([str(cli),'pcb','drc','--format','json','--severity-all','--all-track-errors','--refill-zones','-o',str(report),str(fn)],check=True,capture_output=True)
 d=json.loads(report.read_text());assert not d['unconnected_items'],'Pruning requires complete connectivity'
 ids={i['uuid'] for v in d['violations'] if v['type']=='track_dangling' for i in v['items']}
 if not ids:break
 b=p.LoadBoard(str(fn));keep.append(b);found=0
 for t in list(b.GetTracks()):
  if t.m_Uuid.AsString() in ids:
   assert not t.IsLocked() and not isinstance(t,p.PCB_VIA),'Review deliberate copper instead of pruning it'
   removed.append({'net':t.GetNetname(),'layer':b.GetLayerName(t.GetLayer()),'start_mm':[p.ToMM(t.GetStart().x),p.ToMM(t.GetStart().y)],'end_mm':[p.ToMM(t.GetEnd().x),p.ToMM(t.GetEnd().y)]})
   b.Remove(t);keep.append(t);found+=1
 assert found==len(ids)
 filler=p.ZONE_FILLER(b);filler.Fill(b.Zones());keep.append(filler)
 candidate=P/'routing/prune-candidate.kicad_pcb';p.SaveBoard(str(candidate),b)
 subprocess.run([str(cli),'pcb','drc','--format','json','--severity-all','--refill-zones','-o',str(report),str(candidate)],check=True,capture_output=True)
 assert not json.loads(report.read_text())['unconnected_items'],'Pruning changed connectivity; original board not replaced'
 fn.write_bytes(candidate.read_bytes())
else:raise RuntimeError('Too many dangling branches: manual review required')
(P/'verification/pruned-stubs.json').write_text(json.dumps(removed,indent=2)+'\n')
print('Native DRC identified and removed',len(removed),'free stub segments; connectivity intact.')
