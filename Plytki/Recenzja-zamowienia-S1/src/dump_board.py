"""Zrzut geometrii płytki (KiCad 10 pcbnew) do JSON do recenzji zamówienia S1.

Użycie (w obrazie egrlab-kicad): python3 dump_board.py <plik.kicad_pcb> <wyjście.json>
Tylko odczyt: płytka nie jest zapisywana. Współrzędne względem lewego górnego rogu obrysu
(x od strony panelu, y od krawędzi A — jak w format-s1.json), mm.
"""
import json, sys, pcbnew

src, out = sys.argv[1], sys.argv[2]
b = pcbnew.LoadBoard(src)
mm = pcbnew.ToMM
bb = b.GetBoardEdgesBoundingBox()
X0, Y0 = mm(bb.GetX()), mm(bb.GetY())
def P(p): return [round(mm(p.x) - X0, 4), round(mm(p.y) - Y0, 4)]

res = {"file": src, "edge_bbox": [0, 0, round(mm(bb.GetWidth()), 4), round(mm(bb.GetHeight()), 4)],
       "origin_abs": [X0, Y0], "footprints": [], "tracks": {}, "vias": [], "zones": []}
for fp in b.GetFootprints():
    d = {"ref": fp.GetReference(), "value": fp.GetValue(), "fpid": fp.GetFPIDAsString(),
         "pos": P(fp.GetPosition()), "rot": fp.GetOrientationDegrees(),
         "side": "B" if fp.IsFlipped() else "F", "attr": int(fp.GetAttributes()),
         "tht": bool(fp.GetAttributes() & pcbnew.FP_THROUGH_HOLE),
         "smd": bool(fp.GetAttributes() & pcbnew.FP_SMD), "pads": [], "models": []}
    try:
        cy = fp.GetCourtyard(pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd)
        cb = cy.BBox()
        d["courtyard"] = [round(mm(cb.GetX()) - X0, 3), round(mm(cb.GetY()) - Y0, 3),
                          round(mm(cb.GetRight()) - X0, 3), round(mm(cb.GetBottom()) - Y0, 3)]
    except Exception as e:
        d["courtyard"] = None
    fb = fp.GetBoundingBox(False)
    d["bbox"] = [round(mm(fb.GetX()) - X0, 3), round(mm(fb.GetY()) - Y0, 3),
                 round(mm(fb.GetRight()) - X0, 3), round(mm(fb.GetBottom()) - Y0, 3)]
    for m in fp.Models():
        d["models"].append({"file": m.m_Filename, "off": [m.m_Offset.x, m.m_Offset.y, m.m_Offset.z],
                            "rot": [m.m_Rotation.x, m.m_Rotation.y, m.m_Rotation.z]})
    for pad in fp.Pads():
        ds = pad.GetDrillSize()
        sz = pad.GetSize(pcbnew.F_Cu) if hasattr(pad, "GetSize") else pad.GetSize()
        d["pads"].append({"num": pad.GetNumber(), "pos": P(pad.GetPosition()),
                          "size": [round(mm(sz.x), 4), round(mm(sz.y), 4)],
                          "drill": [round(mm(ds.x), 4), round(mm(ds.y), 4)],
                          "attr": int(pad.GetAttribute()), "shape": int(pad.GetShape(pcbnew.F_Cu)),
                          "net": pad.GetNetname(), "orient": pad.GetOrientationDegrees(),
                          "fp_side": d["side"]})
    try:
        d["fields"] = {f.GetName(): f.GetText() for f in fp.GetFields()
                       if f.GetName() not in ("Reference", "Value", "Footprint", "Datasheet", "Description")}
    except Exception: pass
    res["footprints"].append(d)
for t in b.GetTracks():
    if t.GetClass() == "PCB_VIA":
        res["vias"].append({"pos": P(t.GetPosition()), "d": round(mm(t.GetWidth(pcbnew.F_Cu)), 4),
                            "drill": round(mm(t.GetDrillValue()), 4), "net": t.GetNetname()})
    else:
        k = t.GetNetname(); w = round(mm(t.GetWidth()), 4)
        L = pcbnew.LayerName(t.GetLayer()) if hasattr(pcbnew, "LayerName") else str(t.GetLayer())
        e = res["tracks"].setdefault(k, {})
        e.setdefault(str(w), 0.0); e[str(w)] += round(mm(t.GetLength()), 3)
        res.setdefault("segments", []).append([k, b.GetLayerName(t.GetLayer()), w, P(t.GetStart()), P(t.GetEnd())])
for z in b.Zones():
    bz = z.GetBoundingBox()
    area = {}
    for L in (pcbnew.F_Cu, pcbnew.B_Cu):
        if z.IsOnLayer(L) and z.IsFilled():
            try:
                area[b.GetLayerName(L)] = round(z.GetFilledPolysList(L).Area() / 1e12, 2)
            except Exception: pass
    res["zones"].append({"net": z.GetNetname(), "rule_area": bool(z.GetIsRuleArea()),
                         "name": z.GetZoneName(), "layers": [b.GetLayerName(L) for L in z.GetLayerSet().Seq()],
                         "bbox": [round(mm(bz.GetX()) - X0, 2), round(mm(bz.GetY()) - Y0, 2),
                                  round(mm(bz.GetRight()) - X0, 2), round(mm(bz.GetBottom()) - Y0, 2)],
                         "filled_mm2": area, "min_w": round(mm(z.GetMinThickness()), 3),
                         "clear": round(mm(z.GetLocalClearance() or 0), 3) if not isinstance(z.GetLocalClearance(), type(None)) else None})
json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
print("OK", len(res["footprints"]), "fp", len(res["vias"]), "vias")
