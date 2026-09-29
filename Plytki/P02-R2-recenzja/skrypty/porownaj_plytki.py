"""Porównanie geometrii dwóch płytek P02 (pozycje, pady, ścieżki, przelotki, strefy, teksty), bez UUID."""
import sys, json
import pcbnew as p


def data(fn):
    b = p.LoadBoard(fn)
    def xy(v): return (round(p.ToMM(v.x), 4), round(p.ToMM(v.y), 4))
    d = {'fp': set(), 'trk': set(), 'via': set(), 'txt': set(), 'zone': set(), 'padconn': set()}
    for f in b.GetFootprints():
        d['fp'].add((f.GetReference(), f.GetValue(), xy(f.GetPosition()), round(f.GetOrientationDegrees(), 3)))
        for a in f.Pads():
            if a.GetLocalZoneConnection() != p.ZONE_CONNECTION_INHERITED:
                d['padconn'].add((f.GetReference(), a.GetNumber(), int(a.GetLocalZoneConnection())))
    for t in b.GetTracks():
        if isinstance(t, p.PCB_VIA):
            d['via'].add((t.GetNetname(), xy(t.GetPosition()), round(p.ToMM(t.GetWidth(p.F_Cu)), 3)))
        else:
            d['trk'].add((t.GetNetname(), tuple(sorted([xy(t.GetStart()), xy(t.GetEnd())])), round(p.ToMM(t.GetWidth()), 3), t.GetLayer()))
    for g in b.GetDrawings():
        if isinstance(g, p.PCB_TEXT):
            d['txt'].add((g.GetText(), xy(g.GetPosition())))
    for z in b.Zones():
        d['zone'].add((z.GetNetname(), z.GetZoneName(), z.GetIsRuleArea(), z.Outline().OutlineCount()))
    return d


A, B = data(sys.argv[1]), data(sys.argv[2])
out = {}
for k in A:
    out[k] = {'only_first': sorted(map(str, A[k] - B[k]))[:12], 'only_second': sorted(map(str, B[k] - A[k]))[:12], 'n_first': len(A[k]), 'n_second': len(B[k])}
print(json.dumps(out, indent=1, ensure_ascii=False))
