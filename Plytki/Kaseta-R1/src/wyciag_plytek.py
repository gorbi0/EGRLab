"""Wyciąg geometrii płytek do koncepcji kasety: obrys, otwory M3, położenie i obrys (courtyard) elementów.
Uruchomienie: Python KiCada 10.0.6 z katalogu Plytki/Kaseta-R1:  python src/wyciag_plytek.py
Pliki płytek tylko czyta (LoadBoard bez zapisu); sumy SHA-256 źródeł trafiają do dane/plytki.json.
"""
import hashlib, json
from pathlib import Path
import pcbnew as pcb

R = Path(__file__).resolve().parents[1]
SRC = {'P01': 'P01-PCB-R3.1-review', 'P02': 'P02-R3-review', 'P03': 'P03-R5-review', 'P04': 'P04-R2.2-review',
       'P05': 'P05-R1-review', 'P06': 'P06-R1-review', 'P08': 'P08-R1-review', 'P09': 'P09-R1-review',
       'P10': 'P10-R1-review', 'P11': 'P11-R1-review'}
out = {}
for name, pkg in SRC.items():
    f = R.parent/pkg/'eda'/f'{name}.kicad_pcb'
    b = pcb.LoadBoard(str(f))
    bb = b.GetBoardEdgesBoundingBox()
    x0, y0 = pcb.ToMM(bb.GetX()), pcb.ToMM(bb.GetY())
    W, H = round(pcb.ToMM(bb.GetWidth()) - 0.05, 2), round(pcb.ToMM(bb.GetHeight()) - 0.05, 2)  # obrys po osi linii 0,05 mm
    rel = lambda p: [round(pcb.ToMM(p.x) - x0 - 0.025, 2), round(pcb.ToMM(p.y) - y0 - 0.025, 2)]
    holes, parts = [], []
    for fp in b.GetFootprints():
        ref, lib = fp.GetReference(), str(fp.GetFPID().GetLibItemName())
        if ref.startswith('H'):
            for p in fp.Pads():
                if p.GetDrillSize().x >= 3000000:
                    holes.append({'ref': ref, 'xy': rel(p.GetPosition()), 'd': round(pcb.ToMM(p.GetDrillSize().x), 2)})
        cy = fp.GetCourtyard(pcb.B_CrtYd if fp.IsFlipped() else pcb.F_CrtYd)
        box = None
        if cy.OutlineCount():
            cb = cy.BBox()
            box = [round(pcb.ToMM(cb.GetX()) - x0, 1), round(pcb.ToMM(cb.GetY()) - y0, 1),
                   round(pcb.ToMM(cb.GetRight()) - x0, 1), round(pcb.ToMM(cb.GetBottom()) - y0, 1)]
        parts.append({'ref': ref, 'lib': lib, 'val': fp.GetValue(), 'xy': rel(fp.GetPosition()),
                      'rot': round(fp.GetOrientationDegrees()), 'box': box, 'side': 'B' if fp.IsFlipped() else 'F'})
    out[name] = {'source': f'Plytki/{pkg}/eda/{name}.kicad_pcb', 'sha256': hashlib.sha256(f.read_bytes()).hexdigest(),
                 'W': W, 'H': H, 'holes': holes, 'parts': parts}
    print(name, W, 'x', H, len(parts), 'elementów, otwory', len(holes))
(R/'dane'/'plytki.json').write_text(json.dumps(out, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
