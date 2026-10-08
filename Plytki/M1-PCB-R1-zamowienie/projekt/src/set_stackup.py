"""P07 S1 (user decision 6.10): 4-layer JLCPCB standard stack JLC04161H-7628, 1.6 mm: outer copper 1 oz (35 um), inner 0.5 oz (15.2 um as
JLCPCB lists it), prepreg 7628 0.2104 mm on both sides of a 1.065 mm core. In1.Cu = GND plane (logic / analog) with a separate PGND area
under the 10 A path, In2.Cu = signals + supply zones (route_critical.py, import_routing.py, inner_zones.py). The 10 A path stays on the outer
layers; the inner 0.5 oz copper is not counted in its cross-section."""
from pathlib import Path
from sexpr import parse,dump,one,sub
import sys;sys.path.insert(0,str(Path(__file__).resolve().parent))
from board import NAME
P=Path(__file__).resolve().parents[1];fn=P/f'eda/{NAME}.kicad_pcb'
s=parse(fn.read_text());setup=one(s,'setup')
for x in sub(setup,'stackup'):setup.remove(x)
setup.insert(1,parse('''(stackup
 (layer "F.SilkS" (type "Top Silk Screen"))
 (layer "F.Paste" (type "Top Solder Paste"))
 (layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))
 (layer "F.Cu" (type "copper") (thickness 0.035))
 (layer "dielectric 1" (type "prepreg") (thickness 0.2104) (material "7628") (epsilon_r 4.4) (loss_tangent 0.02))
 (layer "In1.Cu" (type "copper") (thickness 0.0152))
 (layer "dielectric 2" (type "core") (thickness 1.065) (material "FR4") (epsilon_r 4.6) (loss_tangent 0.02))
 (layer "In2.Cu" (type "copper") (thickness 0.0152))
 (layer "dielectric 3" (type "prepreg") (thickness 0.2104) (material "7628") (epsilon_r 4.4) (loss_tangent 0.02))
 (layer "B.Cu" (type "copper") (thickness 0.035))
 (layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))
 (layer "B.Paste" (type "Bottom Solder Paste"))
 (layer "B.SilkS" (type "Bottom Silk Screen"))
 (copper_finish "HASL lead-free") (dielectric_constraints no))'''))
fn.write_text(dump(s)+'\n')
print('4-layer stackup JLC04161H-7628: Cu35 / 7628 0.2104 / In1 15.2 um / core 1.065 / In2 15.2 um / 7628 0.2104 / Cu35 = 1.586 mm + mask, nominal 1.6 mm.')
