"""Carrier pads and envelope. Bought-module outline is provisional; independent physical fit remains required."""
from cadlib import P,q
F=P/'eda/libraries/P09.pretty';F.mkdir(parents=True,exist_ok=True)
def tail(name,n,pitch,drill,pad,ribbon=False):
 pts=[(i+1,i//2*pitch,i%2*pitch,drill,pad) for i in range(n)] if ribbon else [(i+1,i*pitch,0,drill,pad) for i in range(n)]
 xmax=max(p[1] for p in pts);ymax=max(p[2] for p in pts);pts += [('',-3.5,-12,3.2,3.2),('',xmax+3.5,-12,3.2,3.2)]
 s=f'(footprint {q(name)} (version 20240108) (generator "pcbnew") (layer "F.Cu") (attr through_hole)'
 for num,x,y,d,w in pts:s+=f'(pad "{num}" {"thru_hole" if num else "np_thru_hole"} {"rect" if num==1 else "circle"} (at {x} {y}) (size {w} {w}) (drill {d}) (layers "*.Cu" "*.Mask"))'
 s+=f'(fp_rect (start -5.5 -14) (end {xmax+5.5} {ymax+pad/2+.5}) (stroke (width .05) (type default)) (fill none) (layer "F.CrtYd"))'
 s+='(fp_text reference "REF**" (at 2 -6) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15)))))'
 (F/(name+'.kicad_mod')).write_text(s)
tail('PTH_LV09',4,3.5,1.1,2.2);tail('PTH_TEMP',10,2.54,.8,1.8,True)
s='(footprint "MAX31856_XU_socket" (version 20240108) (generator "pcbnew") (layer "F.Cu") (attr through_hole)'
for i in range(9):s+=f'(pad "{i+1}" thru_hole {"rect" if i==0 else "oval"} (at {-i*2.54} 0) (size 1.7 2) (drill 1) (layers "*.Cu" "*.Mask"))'
for x in [0,-20.32]:s+=f'(pad "" np_thru_hole circle (at {x} 16) (size 6 6) (drill 6) (layers "*.Cu" "*.Mask"))'
s+='(fp_rect (start -24.82 -2.5) (end 4.5 21.5) (stroke (width .05) (type default)) (fill none) (layer "F.CrtYd"))'
s+='(fp_rect (start -22.32 -2) (end 2 19) (stroke (width .1) (type default)) (fill none) (layer "F.Fab"))'
s+='(fp_rect (start -21.7 -1.5) (end 1.5 1.5) (stroke (width .15) (type default)) (fill none) (layer "F.SilkS"))'
s+='(fp_text reference "REF**" (at -10 5) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15)))))'
(F/'MAX31856_XU_socket.kicad_mod').write_text(s)
