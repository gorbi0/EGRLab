"""P09-R2 (S1): only the module socket footprint is generated; harness pads and test pads are gone (J_BP and the service strip use KiCad library footprints).
The bought-module outline is still provisional; independent physical fit remains required."""
from cadlib import P,q
F=P/'eda/libraries/P09.pretty';F.mkdir(parents=True,exist_ok=True)
s='(footprint "MAX31856_XU_socket" (version 20240108) (generator "pcbnew") (layer "F.Cu") (attr through_hole)'
for i in range(9):s+=f'(pad "{i+1}" thru_hole {"rect" if i==0 else "oval"} (at {-i*2.54} 0) (size 1.7 2) (drill 1) (layers "*.Cu" "*.Mask"))'
for x in [0,-20.32]:s+=f'(pad "" np_thru_hole circle (at {x} 16) (size 6 6) (drill 6) (layers "*.Cu" "*.Mask"))'
s+='(fp_rect (start -24.82 -2.5) (end 4.5 21.5) (stroke (width .05) (type default)) (fill none) (layer "F.CrtYd"))'
s+='(fp_rect (start -22.32 -2) (end 2 19) (stroke (width .1) (type default)) (fill none) (layer "F.Fab"))'
s+='(fp_rect (start -21.7 -1.5) (end 1.5 1.5) (stroke (width .15) (type default)) (fill none) (layer "F.SilkS"))'
s+='(fp_text reference "REF**" (at -10 5) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15)))))'
(F/'MAX31856_XU_socket.kicad_mod').write_text(s)
