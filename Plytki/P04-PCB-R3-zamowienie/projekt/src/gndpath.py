"""Shortest path through the copper of one net (review 2.10, P05 R3 / P06 R2): the reviews measured how far a decoupling capacitor's
GND pad is from its IC's GND pin through GND copper (pours, tracks, pads, vias on both layers), not only the supply side. This module
gives verify_pcb.py the same measure without scipy / scikit-image (not in the KiCad image): the copper of the net is drawn on a raster
(RES = 0.2 mm) per layer, a via or a PTH pad joins the layers, and a breadth-first wave walks the raster, 8- and 4-connected in turn
(octagonal metric, within about 8 % of the straight distance). Result in mm, None when the copper does not join the two points.
"""
import math
import numpy as np
import pcbnew as p
from PIL import Image, ImageDraw

RES = .2   # mm; a 0.3 mm track stays connected (8-neighbour steps), the 0.25 mm clearance gaps between pieces stay open


def _draw(d, ps, res):
    for k in range(ps.OutlineCount()):
        o = ps.Outline(k)
        d.polygon([(p.ToMM(o.CPoint(i).x) / res, p.ToMM(o.CPoint(i).y) / res) for i in range(o.PointCount())], fill=1)
        for h in range(ps.HoleCount(k)):
            o = ps.Hole(k, h)
            d.polygon([(p.ToMM(o.CPoint(i).x) / res, p.ToMM(o.CPoint(i).y) / res) for i in range(o.PointCount())], fill=0)


def copper(b, net, W, H, res=RES):
    """Boolean rasters (F.Cu, B.Cu) of the net's copper and the mask where the layers join (vias, PTH pads of the net)."""
    w, h = int(W / res) + 2, int(H / res) + 2
    ims = [Image.new('1', (w, h), 0) for _ in range(3)]; dr = [ImageDraw.Draw(i) for i in ims]
    for z in b.Zones():
        if z.GetIsRuleArea() or z.GetNetname() != net:
            continue
        for k, L in enumerate((p.F_Cu, p.B_Cu)):
            if z.IsOnLayer(L):
                _draw(dr[k], z.GetFilledPolysList(L), res)
    for t in b.GetTracks():
        if t.GetNetname() != net:
            continue
        for k, L in enumerate((p.F_Cu, p.B_Cu)):
            if t.IsOnLayer(L):
                ps = p.SHAPE_POLY_SET(); t.TransformShapeToPolygon(ps, L, 0, p.FromMM(.005), p.ERROR_OUTSIDE); _draw(dr[k], ps, res)
        if isinstance(t, p.PCB_VIA):
            ps = p.SHAPE_POLY_SET(); t.TransformShapeToPolygon(ps, p.F_Cu, 0, p.FromMM(.005), p.ERROR_OUTSIDE); _draw(dr[2], ps, res)
    for f in b.GetFootprints():
        for a in f.Pads():
            if a.GetNetname() != net:
                continue
            for k, L in enumerate((p.F_Cu, p.B_Cu)):
                if a.IsOnLayer(L):
                    ps = p.SHAPE_POLY_SET(); a.TransformShapeToPolygon(ps, L, 0, p.FromMM(.005), p.ERROR_OUTSIDE); _draw(dr[k], ps, res)
            if a.GetDrillSize().x > 0 and a.IsOnLayer(p.F_Cu) and a.IsOnLayer(p.B_Cu):
                ps = p.SHAPE_POLY_SET(); a.TransformShapeToPolygon(ps, p.F_Cu, 0, p.FromMM(.005), p.ERROR_OUTSIDE); _draw(dr[2], ps, res)
    m = [np.array(i, dtype=bool) for i in ims]
    return np.stack([m[0], m[1]]), m[2] & m[0] & m[1]


def _grow(a, diag):
    o = a.copy()
    o[:, 1:, :] |= a[:, :-1, :]; o[:, :-1, :] |= a[:, 1:, :]; o[:, :, 1:] |= a[:, :, :-1]; o[:, :, :-1] |= a[:, :, 1:]
    if diag:
        o[:, 1:, 1:] |= a[:, :-1, :-1]; o[:, 1:, :-1] |= a[:, :-1, 1:]; o[:, :-1, 1:] |= a[:, 1:, :-1]; o[:, :-1, :-1] |= a[:, 1:, 1:]
    return o


def distances(cu, via, src, targets, res=RES, limit_mm=250.0):
    """src / targets: (x, y, layer index 0 F.Cu / 1 B.Cu / None = either). Returns {name: mm or None}. The start and the goal points
    snap to the nearest copper pixel of their layer within 0.3 mm (a pad centre is copper; a rounded track end may fall between pixels)."""
    def snap(x, y, k):
        r = int(math.ceil(.3 / res)); cx, cy = int(round(x / res)), int(round(y / res)); best = None
        for L in ((0, 1) if k is None else (k,)):
            for j in range(-r, r + 1):
                for i in range(-r, r + 1):
                    yy, xx = cy + j, cx + i
                    if 0 <= yy < cu.shape[1] and 0 <= xx < cu.shape[2] and cu[L, yy, xx] and (best is None or i * i + j * j < best[0]):
                        best = (i * i + j * j, L, yy, xx)
        return best and best[1:]
    s = snap(*src)
    if s is None:
        return {n: None for n in targets}
    goal = {n: snap(*t) for n, t in targets.items()}
    out = {n: None for n, g in goal.items() if g is None}
    seen = np.zeros_like(cu); seen[s] = True; front = seen.copy(); k = 0
    todo = {n: g for n, g in goal.items() if g is not None}
    for n, g in list(todo.items()):
        if g == s:
            out[n] = 0.0; del todo[n]
    kmax = int(limit_mm / res)
    while todo and front.any() and k < kmax:
        k += 1
        nb = _grow(front, k % 2 == 1)
        nb[0] |= front[1] & via; nb[1] |= front[0] & via    # a via / PTH pad joins the layers
        nb &= cu & ~seen; seen |= nb; front = nb
        for n, g in list(todo.items()):
            if nb[g]:
                out[n] = round(k * res, 1); del todo[n]
    out.update({n: None for n in todo})
    return out


def pad_point(b, ref, num):
    a = next(q for f in b.GetFootprints() if f.GetReference() == ref for q in f.Pads() if q.GetNumber() == str(num))
    k = None if (a.IsOnLayer(p.F_Cu) and a.IsOnLayer(p.B_Cu)) else (0 if a.IsOnLayer(p.F_Cu) else 1)
    return (p.ToMM(a.GetPosition().x), p.ToMM(a.GetPosition().y), k)
