"""PTH harnesses. Anchor line 10.5 mm before row1, <=14.7 mm from row2."""
from cadlib import P,q
F=P/'eda/libraries/P11.pretty';F.mkdir(parents=True,exist_ok=True)
def tail(name,n,pitch=3.5,rows=2,dy=3.5,power=(),after=False):
 cols=(n+rows-1)//rows
 pts=[(i+1,(i%cols)*pitch,(i//cols)*dy,2.2 if i+1 in power else 1.1,3.8 if i+1 in power else 2.3) for i in range(n)]
 if name=='PTH_DT12':pts=[(i,x,dy-y,d,w) for i,x,y,d,w in pts]
 xmax=max(t[1] for t in pts); ymax=max(t[2] for t in pts);ay=12 if after else -10.5
 pts += [('',-3.5,ay,3.2,3.2),('',xmax+3.5,ay,3.2,3.2)]
 s=f'(footprint {q(name)} (version 20240108) (generator "pcbnew") (layer "F.Cu") (attr through_hole)'
 for num,x,y,d,w in pts:s+=f'(pad "{num}" {"thru_hole" if num else "np_thru_hole"} {"rect" if num==1 else "circle"} (at {x} {y}) (size {w} {w}) (drill {d}) (layers "*.Cu" "*.Mask"))'
 s+=f'(fp_rect (start -5.5 {min(ay-2,-2.4)}) (end {xmax+5.5} {max(ay+2,ymax+2.4)}) (stroke (width .05) (type default)) (fill none) (layer "F.CrtYd"))'
 s+='(fp_text reference "REF**" (at 2 -5) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15)))))'
 (F/(name+'.kicad_mod')).write_text(s)
tail('PTH_DT12',12,5.08,2,4.2,(1,2))
tail('PTH_CORE8',8);tail('PTH_SAFE10',10);tail('PTH_CONTACT20',20)
tail('PTH_PAIR2',2,3.5,1)
tail('PTH_MOTOR5',5,5.08,1,power=(1,2),after=True)
(F/'OFFBOARD.kicad_mod').write_text('(footprint "OFFBOARD" (version 20240108) (generator "pcbnew") (layer "F.Cu") (attr board_only exclude_from_pos_files))')
