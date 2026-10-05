"""P12 R1 silkscreen (top = side facing the stack; KiCad view = view from the stack, z up). Texts >= 1.0 mm / 0.15 mm (JLCPCB).
- every connector: "Jn  Pxx <connector> (poziom k, Sx)" centred above its body, "1" left of the body at the pin-1 row (the footprint's
  own pin-1 mark stays);
- test pads: net name above each pad; references of connectors and pads hidden (the label carries the reference);
- title, orientation ("STRONA STOSU", "GORA", x = 0 panel / x = 160 inputs) on top; on the bottom a mirrored note "TYL - SCIANA A".
Writes routing/silkscreen.json (texts and their positions) for verify_pcb.py / negative_controls.py.
"""
from pathlib import Path
import pcbnew as p, json, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from board import NAME, REV, kxy, W, H, TP_XZ
P = Path(__file__).resolve().parents[1]; fn = P / f'eda/{NAME}.kicad_pcb'
K = json.loads((P / 'docs/kontrakt-P12.json').read_text(encoding='utf-8'))
TS, TT = 1.2, .18
TP_LABEL = {'TP1': 'GND', 'TP2': '5V_SYS', 'TP3': '3V3_IO', 'TP4': 'GND'}
TITLE = f'{REV} S1 LOGGER'


def label(z):
    if z['poziom'] == 'panel':
        return f"{z['ref']}  P11 J_P12 (panel, tasma z P11)"
    return f"{z['ref']}  {z['plytka'].split()[0]} {z['zlacze']} (poziom {z['poziom']}, {z['slot']})"


def text(b, s, x, y, size=TS, layer=p.F_SilkS, angle=0, mirror=False):
    t = p.PCB_TEXT(b); t.SetText(s); t.SetLayer(layer); t.SetTextSize(p.VECTOR2I(p.FromMM(size), p.FromMM(size)))
    t.SetTextThickness(p.FromMM(TT)); t.SetPosition(p.VECTOR2I(p.FromMM(x), p.FromMM(y)))
    t.SetHorizJustify(p.GR_TEXT_H_ALIGN_CENTER); t.SetVertJustify(p.GR_TEXT_V_ALIGN_CENTER)
    t.SetTextAngle(p.EDA_ANGLE(angle, p.DEGREES_T)); t.SetMirrored(mirror); b.Add(t); return t


if __name__ == '__main__':
    from sexpr import parse, dump   # idempotent: our texts are the only board texts; removed at file level (pcbnew Remove() breaks SWIG)
    tree = parse(fn.read_text(encoding='utf-8')); tree = [g for g in tree if not (isinstance(g, list) and g and g[0] == 'gr_text')]
    fn.write_text(dump(tree) + chr(10), encoding='utf-8'); b = p.LoadBoard(str(fn))
    if any(isinstance(d, p.PCB_TEXT) for d in b.GetDrawings()):
        raise SystemExit('old texts left')
    fmap = {f.GetReference(): f for f in b.GetFootprints()}; out = {'labels': {}, 'pin1': {}, 'tp': {}, 'other': []}
    for f in fmap.values():
        f.Reference().SetVisible(False); f.Value().SetVisible(False)
    for z in K['zlacza']:
        f = fmap[z['ref']]; pads = {a.GetNumber(): (p.ToMM(a.GetPosition().x), p.ToMM(a.GetPosition().y)) for a in f.Pads()}
        xs = [v[0] for v in pads.values()]; cx = (min(xs) + max(xs)) / 2; x1, y1 = pads['1']
        f.BuildCourtyardCaches(); cy = f.GetCourtyard(p.F_CrtYd).BBox()
        top, left = p.ToMM(cy.GetTop()), p.ToMM(cy.GetLeft())
        s = label(z); ly = top - 1.2; text(b, s, cx, ly); out['labels'][z['ref']] = {'text': s, 'at': [round(cx, 3), round(ly, 3)]}
        text(b, '1', left - .9, y1); out['pin1'][z['ref']] = [round(left - .9, 3), round(y1, 3)]   # left of the body, at the pin-1 row
    for r, s in TP_LABEL.items():
        a = list(fmap[r].Pads())[0]; x, y = p.ToMM(a.GetPosition().x), p.ToMM(a.GetPosition().y)
        text(b, s, x, y - 2.4, 1.0); out['tp'][r] = {'text': s, 'at': [x, round(y - 2.4, 3)]}
    tx, ty = kxy(30.0, 88.0)
    for k, (s, size) in enumerate([(TITLE, 1.6), ('plytka polaczen krawedzi A', 1.2), ('STRONA STOSU (zlacza)  /  GORA ^', 1.2)]):
        text(b, s, tx, ty + k * 2.4, size); out['other'].append(s)
    for s, x, ang in [('x = 0  PANEL', 2.2, 90), ('x = 160  WEJSCIA', W - 2.2, 270)]:
        text(b, s, x, kxy(0, 40.0)[1] if x < 10 else kxy(0, 66.0)[1], 1.0, angle=ang); out['other'].append(s)
    bx, by = kxy(80.0, 27.0)   # between levels 1 and 2, clear of the M3 holes (4.10: at z 51.45 the text ran through H5 / H6)
    text(b, f'{REV} TYL - SCIANA A (zlacza po drugiej stronie)', bx, by, 1.5, p.B_SilkS, mirror=True); out['other'].append('TYL')
    out['title'] = TITLE
    p.SaveBoard(str(fn), b)
    (P / 'routing/silkscreen.json').write_text(json.dumps(out, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    print('silkscreen:', len(out['labels']), 'connector labels,', len(out['pin1']), 'pin-1 marks,', len(out['tp']), 'test-pad labels')
