from pathlib import Path
from sexpr import parse,dump,one,sub
P=Path(__file__).resolve().parents[1];fn=P/'eda/P00.kicad_pcb'
s=parse(fn.read_text());setup=one(s,'setup')
for x in sub(setup,'stackup'):setup.remove(x)
setup.insert(1,parse('''(stackup
 (layer "F.SilkS" (type "Top Silk Screen"))
 (layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))
 (layer "F.Cu" (type "copper") (thickness 0.035))
 (layer "dielectric 1" (type "core") (thickness 1.53) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
 (layer "B.Cu" (type "copper") (thickness 0.035))
 (layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))
 (layer "B.SilkS" (type "Bottom Silk Screen"))
 (copper_finish "HASL lead-free") (dielectric_constraints no))'''))
fn.write_text(dump(s)+'\n')
print('2-layer stackup: Cu35/FR4 1.53/Cu35; nominal laminate incl Cu = 1.60 mm, mask separate.')
