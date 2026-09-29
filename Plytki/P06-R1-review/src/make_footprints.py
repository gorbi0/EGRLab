"""Dimensioned P06 PTH footprints. PBV drawing Z-DW-132b, manufacturer PDF p2.
Pins are numbered in this library, not claimed as manufacturer's terminal numbers.
"""
from cadlib import P,q
F=P/'eda/libraries/P06.pretty';F.mkdir(parents=True,exist_ok=True)
def frame(name,pads,box,body=None):
 s=f'(footprint {q(name)} (version 20240108) (generator "pcbnew") (layer "F.Cu") (attr through_hole)'
 for num,x,y,d,w in pads:
  s+=f'(pad "{num}" {"thru_hole" if num else "np_thru_hole"} {"rect" if num==1 else "circle"} (at {x} {y}) (size {w} {w}) (drill {d}) (layers "*.Cu" "*.Mask"))'
 x0,y0,x1,y1=box
 s+=f'(fp_rect (start {x0} {y0}) (end {x1} {y1}) (stroke (width .05) (type default)) (fill none) (layer "F.CrtYd"))'
 if body:
  a,b,c,d=body
  s+=f'(fp_rect (start {a} {b}) (end {c} {d}) (stroke (width .15) (type default)) (fill none) (layer "F.Fab"))'
 s+=f'(fp_text reference "REF**" (at {(x0+x1)/2} {y1+1.5}) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15)))))'
 (F/(name+'.kicad_mod')).write_text(s)
def tail(name,n,pitch,drill,pad,ribbon=False):
 pts=[(i+1,i//2*pitch,i%2*pitch,drill,pad) for i in range(n)] if ribbon else [(i+1,i*pitch,0,drill,pad) for i in range(n)]
 xmax=max(p[1] for p in pts);ymax=max(p[2] for p in pts)
 pts += [('',-3.5,-12,3.2,3.2),('',xmax+3.5,-12,3.2,3.2)]
 frame(name,pts,(-5.5,-14,xmax+5.5,ymax+pad/2+.5))
tail('PTH_LV06',4,3.5,1.1,2.2)
tail('PTH_ILOG',8,2.54,.8,1.8,True)
tail('PTH_ISERIES',4,7.62,2.4,4.5)
tail('PTH_BYPASS',2,17.78,2.4,4.5)
tail('PTH_SWSTATUS',3,3.5,1.1,2.2)
# PBV F1 max force pin rectangular section 1.7 x 1.2 mm: diagonal 2.08 < finished drill 2.3.
# Sense max 1.3 x 1.2 mm: diagonal 1.77 < finished drill 2.0. Body 22.5 x 4.45 mm.
frame('PBV_2317_F1',[(1,0,0,2.3,4.2),(2,5.08,0,2,3.5),(3,12.7,0,2,3.5),(4,17.78,0,2.3,4.2)],(-3.4,-3.5,21.18,3.5),(-2.36,-2.55,20.14,1.9))

frame("OFFBOARD",[],(-1,-1,1,1))
