"""R2: unambiguous reference labels (run after finish_silkscreen.py and r2_legends.py).
Resistors stand in dense rows; a label outside the body ends up next to the neighbour's
label ("R12 R5" above one part). Axial resistor labels therefore go inside the body
outline, along the body. D7/D8 labels go to the left end of each diode; J5 label moves off the pin-number row.
"""
from pathlib import Path
import pcbnew as p
P = Path(__file__).resolve().parents[1]; fn = P / 'eda/P01.kicad_pcb'; b = p.LoadBoard(str(fn))
mm = p.FromMM
moved = []
for f in b.GetFootprints():
    fid = f.GetFPIDAsString().split(':')[-1]
    if fid in ('R_MFR50_H4_P15.24', 'R_PR02_P17.78'):
        pads = [pd for pd in f.Pads() if pd.GetNumber() in ('1', '2')]
        a, c = pads[0].GetPosition(), pads[1].GetPosition()
        ref = f.Reference(); ref.SetPosition(p.VECTOR2I((a.x + c.x) // 2, (a.y + c.y) // 2))
        vertical = abs(a.x - c.x) < abs(a.y - c.y)
        ref.SetTextAngle(p.EDA_ANGLE(90 if vertical else 0, p.DEGREES_T))
        ref.SetTextSize(p.VECTOR2I(mm(1), mm(1))); ref.SetTextThickness(mm(.15))
        moved.append(f.GetReference())
    if f.GetReference() in ('D7', 'D8'):  # two diodes stacked 3.5 mm apart: label each at its own left end
        y = {'D7': 99.3, 'D8': 102.8}[f.GetReference()]
        f.Reference().SetPosition(p.VECTOR2I(mm(66.6), mm(y))); f.Reference().SetTextAngle(p.EDA_ANGLE(0, p.DEGREES_T)); moved.append(f.GetReference())
    if f.GetReference() == 'Q6':  # its label would sit on D8's; Q6 label to the left of Q6
        f.Reference().SetPosition(p.VECTOR2I(mm(64.6), mm(108.0))); f.Reference().SetTextAngle(p.EDA_ANGLE(0, p.DEGREES_T)); moved.append('Q6')
    if f.GetReference() == 'J5':
        f.Reference().SetPosition(p.VECTOR2I(mm(128.5), mm(101.0)))
        f.Reference().SetTextAngle(p.EDA_ANGLE(0, p.DEGREES_T)); moved.append('J5')
p.SaveBoard(str(fn), b, True)
print('References centred in body outline:', len(moved), moved)
