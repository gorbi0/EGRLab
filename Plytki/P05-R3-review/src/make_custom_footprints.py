from pathlib import Path
P=Path(__file__).resolve().parents[1];F=P/'eda/libraries/P05.pretty';F.mkdir(parents=True,exist_ok=True)
# R3: the B2B TSW-108-08-G-D-NA footprint is gone (J_BP1/J_BP2 use stock KiCad IDC footprints).
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
