import pcbnew, sys, collections
b = pcbnew.LoadBoard(sys.argv[1]); MM = pcbnew.ToMM
SILK = (pcbnew.F_SilkS, pcbnew.B_SilkS)
cnt = collections.Counter(); small = []
for fp in b.GetFootprints():
    ref = fp.GetReference()
    items = [g for g in fp.GraphicalItems() if g.GetLayer() in SILK]
    texts = [t for t in list(fp.GraphicalItems()) + [fp.Reference(), fp.Value()] if isinstance(t, pcbnew.PCB_TEXT) and t.GetLayer() in SILK and t.IsVisible()]
    shapes = [g for g in items if isinstance(g, pcbnew.PCB_SHAPE)]
    if ref in ('Q1','Q2','D2','U2','U1','U3','U4','Q3','Q4','Q5','Q6','Q7','Q8','C1','C3','C7','C9','D1','D3','D4','D5','D6','D9','LED1','J5','J6','J7','RV1','LK1'):
        print(f"{ref:5s} silk shapes={len(shapes):2d} texts={[ (t.GetText(), round(MM(t.GetTextHeight()),2), round(MM(t.GetTextThickness()),2)) for t in texts]}")
    for t in texts:
        if MM(t.GetTextHeight()) < 1.0: small.append((ref, t.GetText(), round(MM(t.GetTextHeight()),2)))
for d in b.GetDrawings():
    if isinstance(d, pcbnew.PCB_TEXT) and d.GetLayer() in SILK:
        cnt['board_text'] += 1
        if MM(d.GetTextHeight()) < 1.0: small.append(('board', d.GetText()[:30], round(MM(d.GetTextHeight()),2)))
print('board-level silk texts:', cnt['board_text'], '| texts < 1.0 mm:', small[:20])
