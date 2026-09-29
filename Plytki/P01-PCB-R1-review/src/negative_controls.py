"""Three intentional errors in disposable copies; prove the checks can fail."""
from pathlib import Path
import pcbnew as p,subprocess,sys,json,shutil
P=Path(__file__).resolve().parents[1];out=P/'verification/negative-controls';out.mkdir(exist_ok=True)
(out/'fp-lib-table').write_text((P/'eda/fp-lib-table').read_text().replace('${KIPRJMOD}/libraries','${KIPRJMOD}/../../eda/libraries'))
cli=Path(sys.executable).with_name('kicad-cli.exe');results=[]
for case in ['probe_open','mount_shift','lk1_bypass']:
 b=p.LoadBoard(str(P/'eda/P01.kicad_pcb'));target=out/(case+'.kicad_pcb')
 if case=='probe_open':
  t=next(t for t in b.GetTracks() if not isinstance(t,p.PCB_VIA) and t.GetNetname()=='/P01_GATE' and t.GetEnd()==p.VECTOR2I(p.FromMM(103),p.FromMM(26)))
  b.Remove(t)
 elif case=='mount_shift':
  f=b.FindFootprintByReference('H3');f.SetPosition(p.VECTOR2I(p.FromMM(6),p.FromMM(115)))
 else:
  t=p.PCB_TRACK(b);t.SetNet(b.FindNet('/VPROT'));t.SetWidth(p.FromMM(2));t.SetLayer(p.F_Cu)
  t.SetStart(p.VECTOR2I(p.FromMM(126),p.FromMM(36)));t.SetEnd(p.VECTOR2I(p.FromMM(136),p.FromMM(36)));b.Add(t)
 p.SaveBoard(str(target),b,True);shutil.copy2(P/'eda/P01.kicad_pro',target.with_suffix('.kicad_pro'))
 if case!='lk1_bypass':
  run=subprocess.run([sys.executable,str(P/'src/verify_pcb.py'),str(target)],capture_output=True,text=True)
  report=json.loads(target.with_suffix('.checks.json').read_text())
  failed=[c['check'] for c in report['checks'] if not c['pass']]
  wanted='Every pre-routed critical segment and via retained' if case=='probe_open' else 'Four NPTH 3.2 mm mounting holes at defined centres'
  detected=run.returncode==1 and wanted in failed
 else:
  report_path=out/'lk1_bypass-drc.json'
  run=subprocess.run([str(cli),'pcb','drc','--format','json','--severity-all','--all-track-errors','--refill-zones','-o',str(report_path),str(target)],capture_output=True,text=True)
  report=json.loads(report_path.read_text());failed=[v['type'] for v in report['violations']]
  detected=run.returncode==0 and 'shorting_items' in failed
 (out/(case+'.log')).write_text(run.stdout+'\n'+run.stderr)
 results.append({'mutation':case,'detected':detected,'failures':failed})
print(json.dumps(results,indent=2));(P/'verification/negative-controls.json').write_text(json.dumps(results,indent=2)+'\n')
assert all(r['detected'] for r in results)
