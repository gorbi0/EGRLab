"""Export the checked, immutable R3.1 board. Run with KiCad's Python."""
from pathlib import Path
import datetime, hashlib, json, os, subprocess, sys, collections
import pcbnew as pcb

R = Path(__file__).resolve().parents[1]
P = R/'projekt'
sys.path.insert(0, str(P/'src'))
from provenance import inputs, current_receipt

def sha(f): return hashlib.sha256(f.read_bytes()).hexdigest()
def run(name, command):
    result = subprocess.run(list(map(str, command)), capture_output=True, text=True)
    (R/'verification'/f'{name}.log').write_text(result.stdout+'\n'+result.stderr, encoding='utf-8')
    if result.returncode: raise RuntimeError(f'{name}: exit {result.returncode}')
    print(name+' PASS', flush=True)
    return command

receipt = json.loads((P/'verification/drc.provenance.json').read_text())
assert current_receipt(receipt), 'Stale DRC'
assert all(n == 0 for n in receipt['counts'].values())
assert json.loads((P/'verification/pcb-checks.json').read_text())['pass']
before = inputs()
run('negative-controls', [sys.executable, P/'src/negative_controls.py'])
board = P/'eda/P01.kicad_pcb'
cli = Path(sys.executable).with_name('kicad-cli.exe')
commands = []
commands.append(run('gerber-export', [cli, 'pcb', 'export', 'gerbers', '--layers', 'F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,Edge.Cuts', '--precision', '6', '--subtract-soldermask', '--disable-aperture-macros', '--check-zones', '--output', str(R/'gerber')+os.sep, board]))
commands.append(run('drill-export', [cli, 'pcb', 'export', 'drill', '--format', 'excellon', '--drill-origin', 'absolute', '--excellon-zeros-format', 'decimal', '--excellon-units', 'mm', '--excellon-separate-th', '--generate-map', '--map-format', 'svg', '--generate-report', '--report-path', R/'verification/drill-report.txt', '--output', str(R/'gerber')+os.sep, board]))
for f in (R/'gerber').glob('*.svg'):
    f.replace(R/'podglad'/f.name)
# Native job metadata uses the outline stroke's bounding box (160.05 x 120.05),
# not the routed centreline dimensions. Keep it as evidence, outside upload ZIP.
for f in (R/'gerber').glob('*.gbrjob'):
    f.replace(R/'verification'/f.name)
assert current_receipt(receipt) and before == inputs(), 'Inputs changed during export'

b = pcb.LoadBoard(str(board))
def mm(v): return round(pcb.ToMM(v),6)
holes = []
pad_centres = []
for f in b.GetFootprints():
    for pad in f.Pads():
        pos=pad.GetPosition(); d=pad.GetDrillSize()
        pad_centres.append({'ref':f.GetReference(),'pin':pad.GetNumber(),'x':mm(pos.x),'y':-mm(pos.y),'attr':int(pad.GetAttribute()),'net':pad.GetNetname()})
        if d.x or d.y:
            assert d.x == d.y, 'Slot requires additional verification'
            holes.append({'ref':f.GetReference(),'pin':pad.GetNumber(),'x':mm(pos.x),'y':-mm(pos.y),'diameter':mm(d.x),'plated':pad.GetAttribute()!=pcb.PAD_ATTRIB_NPTH})
for t in b.GetTracks():
    if isinstance(t,pcb.PCB_VIA):
        pos=t.GetPosition()
        holes.append({'ref':'VIA','pin':'','x':mm(pos.x),'y':-mm(pos.y),'diameter':mm(t.GetDrill()),'plated':True})
widths=[mm(t.GetWidth()) for t in b.GetTracks() if not isinstance(t,pcb.PCB_VIA)]
data={'board_sha256':sha(board),'board_mm':[160,120],'thickness_mm':1.6,'copper_um_each':70,'finish':'HASL lead-free','min_track_mm':min(widths),'holes':holes,'pads':pad_centres,'footprints':len(list(b.GetFootprints())),'tracks':len(widths),'vias':sum(x['ref']=='VIA' for x in holes)}
(R/'verification/board-fabrication-data.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
(R/'verification/export-receipt.json').write_text(json.dumps({'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'board_sha256':sha(board),'drc_sha256':sha(P/'verification/drc.json'),'inputs_unchanged':True,'commands':[[str(x) for x in c] for c in commands],'files':{f.name:sha(f) for f in (R/'gerber').iterdir() if f.is_file()},'native_job_sha256':sha(R/'verification/P01-job.gbrjob')},indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:data[k] for k in ['board_sha256','min_track_mm','footprints','tracks','vias']}))
