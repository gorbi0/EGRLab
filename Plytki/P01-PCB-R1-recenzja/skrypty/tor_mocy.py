import pcbnew, sys
b = pcbnew.LoadBoard(sys.argv[1]); MM = pcbnew.ToMM
L = {pcbnew.F_Cu: 'F', pcbnew.B_Cu: 'B'}
want = sys.argv[2].split(',')
minw = float(sys.argv[3]) if len(sys.argv) > 3 else 0
for t in b.GetTracks():
    n = t.GetNetname()
    if n not in want: continue
    if t.Type() == pcbnew.PCB_VIA_T:
        print(f"{n:16s} VIA  at ({MM(t.GetPosition().x):.2f},{MM(t.GetPosition().y):.2f}) d={MM(t.GetWidth(pcbnew.F_Cu)):.2f} drill={MM(t.GetDrillValue()):.2f}")
        continue
    w = MM(t.GetWidth())
    if w < minw: continue
    s, e = t.GetStart(), t.GetEnd()
    print(f"{n:16s} {L.get(t.GetLayer(),'?')} w={w:4.2f} ({MM(s.x):7.2f},{MM(s.y):6.2f})->({MM(e.x):7.2f},{MM(e.y):6.2f}) len={MM(t.GetLength()):6.2f}")
