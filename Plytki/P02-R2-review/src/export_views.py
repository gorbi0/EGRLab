"""Native KiCad plots/renders. Only duplicate Fab texts are hidden in a plot copy.
No hand-redrawn copper or pad geometry. The actual PCB remains untouched.
"""
from pathlib import Path
import subprocess,sys,json,os
from sexpr import parse,dump,sub,one
P=Path(__file__).resolve().parents[1];cli=Path(sys.executable).with_name('kicad-cli.exe')
env=dict(os.environ);env['KICAD_CONFIG_HOME']=str(P/'verification/tool-config')
root=parse((P/'eda/P02.kicad_pcb').read_text())
for fp in sub(root,'footprint'):
 ref=next(v[2] for v in sub(fp,'property') if v[1]=='Reference')
 for t in list(sub(fp,'fp_text')):
  layer=one(t,'layer')[1]
  if layer in ('F.Fab','B.Fab') and not(ref=='D4' and t[2]=='${REFERENCE}'):fp.remove(t)
out=P/'output';source=out/'plot-source.kicad_pcb';source.write_text(dump(root)+'\n')
def run(args,name):
 r=subprocess.run([str(cli),*args],capture_output=True,text=True,env=env)
 (P/'verification'/('export-'+name+'.log')).write_text(r.stdout+'\n'+r.stderr)
 if r.returncode:raise RuntimeError(name+' export failed')
for name,layers,mirror,pcb in [
 ('assembly','F.Fab,F.Silkscreen,B.Fab,Edge.Cuts',False,source),
 ('bottom','B.Silkscreen,B.Fab,Edge.Cuts',True,source),
 ('copper-front','F.Cu,Edge.Cuts',False,P/'eda/P02.kicad_pcb'),
 ('copper-back','B.Cu,Edge.Cuts',True,P/'eda/P02.kicad_pcb')]:
 args=['pcb','export','svg','--layers',layers,'--mode-single','--page-size-mode','2','--exclude-drawing-sheet','--black-and-white','--sketch-pads-on-fab-layers','-o',str(out/'svg'/(name+'.svg'))]
 if mirror:args+=['--mirror']
 run(args+[str(pcb)],name)
for name,extra in [
 ('isometric',['--side','top','--rotate','325,0,15','--zoom','.74']),
 ('top',['--side','top','--zoom','.90']),
 ('bottom-3d',['--side','bottom','--zoom','.90'])]:
 run(['pcb','render',*extra,'--width','1800','--height','1500','--quality','basic','--background','opaque','-o',str(out/'previews'/(name+'.png')),str(P/'eda/P02.kicad_pcb')],name)
print('Native assembly/bottom/copper SVG and three 3D views exported.')
