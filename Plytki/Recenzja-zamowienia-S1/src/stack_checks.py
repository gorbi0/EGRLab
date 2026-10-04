"""Kontrole stosu S1 na zrzutach dump_board.py: strefy Ø7 wokół M3 (obrys części i miedź),
części od spodu (tylko SMD, bez SOIC poza poziomem 1, >= 1 mm od pól THT), położenie J_BP."""
import json, math, sys, glob
FMT = json.load(open(sys.argv[1]))
LEVEL1 = {"P02"}
def circ_rect(cx, cy, r, b):
    dx = max(b[0] - cx, 0, cx - b[2]); dy = max(b[1] - cy, 0, cy - b[3]); return math.hypot(dx, dy) < r
for fn in sorted(glob.glob(sys.argv[2] + "/P*.json")):
    n = fn.split("/")[-1][:3]; d = json.load(open(fn)); o = 0.025
    holes = [f for f in d["footprints"] if f["ref"].startswith("H")]
    hc = [(h["pos"][0] - o, h["pos"][1] - o) for h in holes]
    issues = []
    for f in d["footprints"]:
        if f["ref"].startswith("H"): continue
        cy = f["courtyard"] and [v - o for v in f["courtyard"]]
        for (x, y) in hc:
            if cy and circ_rect(x, y, 3.5, cy): issues.append(f"Ø7: obrys {f['ref']} w strefie M3 ({x:.1f},{y:.1f})")
        if f["side"] == "B":
            if f["tht"]: issues.append(f"spód: THT {f['ref']}")
            if "SOIC" in f["fpid"] and n not in LEVEL1: issues.append(f"spód: SOIC {f['ref']} poza poziomem 1")
            for g in d["footprints"]:
                for p in g["pads"]:
                    if p["drill"][0] > 0 and cy:
                        px, py = p["pos"][0] - o, p["pos"][1] - o; r = max(p["size"]) / 2
                        if circ_rect(px, py, r + 1.0, cy) and g["ref"] != f["ref"]:
                            dist = max(cy[0] - px, 0, px - cy[2]), max(cy[1] - py, 0, py - cy[3])
                            issues.append(f"spód: {f['ref']} obrys {math.hypot(*dist) - r:.2f} mm od pola THT {g['ref']}.{p['num']}")
    # miedź w strefie Ø7
    for s in d.get("segments", []):
        for (x, y) in hc:
            for pt in (s[3], s[4]):
                if math.hypot(pt[0] - o - x, pt[1] - o - y) < 3.5 + s[2] / 2: issues.append(f"Ø7: ścieżka {s[0]} przy M3 ({x},{y})")
    for v in d["vias"]:
        for (x, y) in hc:
            if math.hypot(v["pos"][0] - o - x, v["pos"][1] - o - y) < 3.5 + v["d"] / 2: issues.append(f"Ø7: przelotka {v['net']} przy M3 ({x},{y})")
    for z in d["zones"]:
        pass
    print("==", n, "M3:", sorted(hc))
    for i in sorted(set(issues)): print("  ", i)
