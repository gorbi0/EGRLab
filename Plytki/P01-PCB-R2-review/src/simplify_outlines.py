"""Keep full assembly geometry on Fab; omit impractical silk for three packages.
Local libraries and board are changed together. Pad/courtyard geometry unchanged.
"""
from pathlib import Path
import pcbnew as p
from sexpr import parse,dump,sub
P=Path(__file__).resolve().parents[1];fn=P/'eda/P01.kicad_pcb'
names={'P01:C_Vishay_K15_H5_P5','P01:TO220_3_P2.54_Drill1.4','P01:HS_Fischer_SK129_63.5_STS_D2.8'}
for name in names:
 lib,fp=name.split(':');path=P/'eda/libraries'/f'{lib}.pretty'/f'{fp}.kicad_mod'
 s=parse(path.read_text())
 for node in list(s):
  if isinstance(node,list) and node[0] in ['fp_line','fp_rect','fp_arc','fp_circle','fp_poly'] and ['layer','F.SilkS'] in node:s.remove(node)
 path.write_text(dump(s)+'\n')
s=parse(fn.read_text())
for f in sub(s,'footprint'):
 if f[1] in names:
  for g in list(f):
   if isinstance(g,list) and g[0] in ['fp_line','fp_rect','fp_arc','fp_circle','fp_poly'] and ['layer','F.SilkS'] in g:f.remove(g)
for g in list(s):
 if isinstance(g,list) and g[0] in ['gr_line','gr_rect','gr_arc','gr_circle','gr_poly'] and ['layer','F.SilkS'] in g:s.remove(g)
fn.write_text(dump(s)+'\n')
print('Three local footprint silhouettes now Fab-only; reference labels retained.')
