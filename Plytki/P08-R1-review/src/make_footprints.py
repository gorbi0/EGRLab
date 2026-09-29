"""P08 solder tails and relay footprint, dimensions from Omron G6K p6."""
from cadlib import P,q,K,parse,dump,subs,one,A
F=P/'eda/libraries/P08.pretty';F.mkdir(parents=True,exist_ok=True)
def tail(name,n,pitch,drill,pad,ribbon=False):
 pts=[(i+1,i//2*pitch,i%2*pitch,drill,pad) for i in range(n)] if ribbon else [(i+1,i*pitch,0,drill,pad) for i in range(n)]
 xmax=max(p[1] for p in pts);ymax=max(p[2] for p in pts)
 pts += [('',-3.5,-12,3.2,3.2),('',xmax+3.5,-12,3.2,3.2)]
 s=f'(footprint {q(name)} (version 20240108) (generator "pcbnew") (layer "F.Cu") (attr through_hole)'
 for num,x,y,d,w in pts:s+=f'(pad "{num}" {"thru_hole" if num else "np_thru_hole"} {"rect" if num==1 else "circle"} (at {x} {y}) (size {w} {w}) (drill {d}) (layers "*.Cu" "*.Mask"))'
 s+=f'(fp_rect (start -5.5 -14) (end {xmax+5.5} {ymax+pad/2+.5}) (stroke (width .05) (type default)) (fill none) (layer "F.CrtYd"))'
 s+='(fp_text reference "REF**" (at 2 -6) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15)))))'
 (F/(name+'.kicad_mod')).write_text(s)
tail('PTH_LV08',4,3.5,1.1,2.2)
tail('PTH_IDC6',6,2.54,.8,1.8,True)
src=K/'footprints/Relay_THT.pretty/Relay_DPDT_Omron_G6K-2P-Y.kicad_mod'
t=parse(src.read_text());t[1]='G6K_2P_Y_verified'
for pad in subs(t,'pad'):
 if pad[1] in ['2','7']:one(pad,'at')[2]=A('3.2')
one(t,'descr')[1]='Omron G6K-2P-Y; corrected pads 2/7 at 3.2 mm from coil; manufacturer PDF p6. Top view.'
(F/'G6K_2P_Y_verified.kicad_mod').write_text(dump(t))
