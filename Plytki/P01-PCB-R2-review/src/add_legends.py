from pathlib import Path
import pcbnew as p
P=Path(__file__).resolve().parents[1];fn=P/'eda/P01.kicad_pcb';b=p.LoadBoard(str(fn))
labels=[('B+',15,29.6),('GND',27.5,25),('OUT+',141,32),('GND',141,26.92),('NC',141,21.84)]
labels += [(str(i),146.3,112-(i-1)*2.54) for i in range(1,7)]
for text,x,y in labels:
 t=p.PCB_TEXT(b);t.SetText(text);t.SetTextSize(p.VECTOR2I(p.FromMM(1),p.FromMM(1)));t.SetTextThickness(p.FromMM(.15));t.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y)));t.SetLayer(p.F_SilkS);b.Add(t)
p.SaveBoard(str(fn),b,True)
