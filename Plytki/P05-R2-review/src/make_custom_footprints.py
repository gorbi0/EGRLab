from pathlib import Path
P=Path(__file__).resolve().parents[1];F=P/'eda/libraries/P05.pretty';F.mkdir(parents=True,exist_ok=True)
# TSW-108-08-G-D-NA: 0.64 mm square tails, 2.54 mm grid, straight body 2.54 mm thick.
# Logical numbering mirrors column assignment to mate same-number P03 SSW socket contacts.
# Physical Samtec odd tails are logical even; physical even tails are logical odd.
s='(footprint "DAQ_TSW_NA_2x8" (version 20240108) (generator "pcbnew") (layer "F.Cu") (attr through_hole)'
for row in range(8):
 for col in range(2):
  n=row*2+col+1;x=0 if col==0 else 2.54;y=row*2.54
  s+=f'(pad "{n}" thru_hole {"rect" if n==1 else "circle"} (at {x} {y}) (size 1.9 1.9) (drill 1.05) (layers "*.Cu" "*.Mask"))'
  s+=f'(fp_line (start {x} {y}) (end 12.42 {y}) (stroke (width .35) (type default)) (layer "F.Fab"))'
s+='(fp_rect (start 4.04 -1.27) (end 6.58 19.05) (stroke (width .1) (type default)) (fill none) (layer "F.Fab"))'
s+='(fp_rect (start -1.2 -1.6) (end 12.8 19.4) (stroke (width .05) (type default)) (fill none) (layer "F.CrtYd"))'
s+='(fp_rect (start 4.04 -1.4) (end 6.2 19.18) (stroke (width .15) (type default)) (fill none) (layer "F.SilkS"))'
s+='(fp_text reference "REF**" (at 3 -3) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))'
(F/'DAQ_TSW_NA_2x8.kicad_mod').write_text(s+')')
# C&K 7201SYCBE, C terminals. Pitch 4.70 along poles, 4.83 between poles; hole 1.85 per manufacturer.
s='(footprint "CK_7201SYCBE" (version 20240108) (generator "pcbnew") (layer "F.Cu") (attr through_hole)'
for col in range(2):
 for row in range(3):
  n=col*3+row+1
  s+=f'(pad "{n}" thru_hole {"rect" if n==1 else "circle"} (at {col*4.83} {row*4.7}) (size 2.8 2.8) (drill 1.85) (layers "*.Cu" "*.Mask"))'
s+='(fp_rect (start -3.3 -1.65) (end 8.13 11.05) (stroke (width .1) (type default)) (fill none) (layer "F.Fab"))'
s+='(fp_rect (start -3.8 -2.15) (end 8.63 11.55) (stroke (width .05) (type default)) (fill none) (layer "F.CrtYd"))'
s+='(fp_text reference "REF**" (at 2.4 -3.4) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))'
(F/'CK_7201SYCBE.kicad_mod').write_text(s+')')
