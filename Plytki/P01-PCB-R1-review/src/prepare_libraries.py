"""PCB-only mechanical courtyard refinement for the heatsink's mounting bay.
Electrical pads and nominal metal outline remain unchanged from R3.
"""
from pathlib import Path
from sexpr import parse,dump,sub,one
P=Path(__file__).resolve().parents[1];lib=P/'eda/libraries/P01.pretty'
name='HS_Fischer_SK129_63.5_STS_D2.8'
path=lib/(name+'.kicad_mod');f=parse(path.read_text())
f=[g for g in f if not(isinstance(g,list) and g and g[0].startswith('fp_') and sub(g,'layer') and one(g,'layer')[1]=='F.CrtYd')]
# Outer envelope with the front central device bay left open. Physical metal
# face is y=+0.9; tab y=+1.15 includes the 0.25 mm isolator. F.Fab is unaltered.
pts=[(-21.3,-12.8),(21.3,-12.8),(21.3,12.8),(8.3,12.8),(8.3,.8),(-8.3,.8),(-8.3,12.8),(-21.3,12.8)]
for a,b in zip(pts,pts[1:]+pts[:1]):
 f.append(parse(f'(fp_line (start {a[0]} {a[1]}) (end {b[0]} {b[1]}) (stroke (width .05) (type solid)) (layer "F.CrtYd"))'))
path.write_text(dump(f),encoding='utf-8')
print('HS courtyard reflects open central mounting bay; pads and fab unchanged.')
