"""PCB1-02: TO-220 orientation on the silkscreen.
Adds to the local TO220_3_P2.54_Drill1.4 footprint a body outline that avoids the
pads, with a thick line on the tab side (metal back, F.Fab y = -3.15 mm).
Pads, courtyard and F.Fab stay unchanged (verify_pcb compares pad geometry with R3).
Run before r2_build_board.py. Idempotent.
"""
from pathlib import Path
from sexpr import parse, dump, sub, one
P = Path(__file__).resolve().parents[1]
path = P / 'eda/libraries/P01.pretty/TO220_3_P2.54_Drill1.4.kicad_mod'
f = parse(path.read_text(encoding='utf-8'))
f = [g for g in f if not (isinstance(g, list) and g and g[0] in ('fp_line', 'fp_text') and sub(g, 'layer') and one(g, 'layer')[1] == 'F.SilkS')]
L, R, BACK, FRONT = -2.66, 7.74, -3.35, 1.45
lines = [((L, BACK), (R, BACK), .40),          # tab side: thick
         ((L, BACK), (L, FRONT), .15), ((R, BACK), (R, FRONT), .15),
         ((L, FRONT), (-1.35, FRONT), .15), ((6.43, FRONT), (R, FRONT), .15)]
for (a, c, w) in lines:
    f.append(parse(f'(fp_line (start {a[0]} {a[1]}) (end {c[0]} {c[1]}) (stroke (width {w}) (type solid)) (layer "F.SilkS"))'))
path.write_text(dump(f) + '\n', encoding='utf-8')
print('TO-220 silkscreen: body outline with 0.4 mm tab-side line; pads untouched.')
