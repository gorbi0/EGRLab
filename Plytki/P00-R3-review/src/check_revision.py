"""Constrain the R3 delta against the frozen R2 release (reference/R2-parts.json, reference/R2.kicad_pcb).
R3 = review P0-01..P0-08 (Claude, 27.09.2026): documents, checks, part notes of R6/RL9/TP3, the supply legend moved
under J10, TP3 labelled 'ZA D1' and the title line. Values, MPNs, footprints, copper and placement must stay as in R2.
Additionally the R2 package itself must be untouched (reference/P00-R2-release-manifest.json).
"""
from pathlib import Path
import hashlib, json, math, pcbnew as p
P = Path(__file__).resolve().parents[1]
old = json.loads((P / 'reference/R2-parts.json').read_text(encoding='utf-8')); new = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
pinchanges = {f'{r}.{n}': [net, new.get(r, {}).get('pins', {}).get(n)] for r in old for n, net in old[r]['pins'].items()
              if new.get(r, {}).get('pins', {}).get(n) != net}
changed = {k: sorted(r for r in old if r in new and old[r][k] != new[r][k]) for k in ('display', 'mpn', 'footprint', 'note', 'url', 'source_ref')}
b0 = p.LoadBoard(str(P / 'reference/R2.kicad_pcb')); b1 = p.LoadBoard(str(P / 'eda/P00.kicad_pcb'))


def xy(v):
    return (round(p.ToMM(v.x), 4), round(p.ToMM(v.y), 4))


def geometry(b):
    fp = {f.GetReference(): (xy(f.GetPosition()), round(f.GetOrientationDegrees(), 3), f.GetFPIDAsString(), f.GetValue(),
                             tuple(sorted((a.GetNumber(), a.GetNetname(), xy(a.GetPosition()), xy(a.GetDrillSize()), int(a.GetLocalZoneConnection())) for a in f.Pads())))
          for f in b.GetFootprints()}
    cu = sorted(('via', t.GetNetname(), xy(t.GetPosition()), round(p.ToMM(t.GetWidth(p.F_Cu)), 3), round(p.ToMM(t.GetDrill()), 3)) if isinstance(t, p.PCB_VIA) else
                ('trk', t.GetNetname(), tuple(sorted([xy(t.GetStart()), xy(t.GetEnd())])), round(p.ToMM(t.GetWidth()), 3), t.GetLayer(), t.IsLocked())
                for t in b.GetTracks())
    zones = sorted((z.GetNetname(), z.GetZoneName(), z.GetIsRuleArea(), tuple(sorted(b.GetLayerName(l) for l in z.GetLayerSet().Seq())),
                    tuple(xy(z.Outline().Outline(0).CPoint(j)) for j in range(z.Outline().Outline(0).PointCount()))) for z in b.Zones())
    fill = {b.GetLayerName(L): round(sum(z.GetFilledPolysList(L).Area() for z in b.Zones() if not z.GetIsRuleArea() and z.IsOnLayer(L)) / 1e12, 3)
            for L in (p.F_Cu, p.B_Cu)}
    texts = {(g.GetText(), xy(g.GetPosition())) for g in b.GetDrawings() if isinstance(g, p.PCB_TEXT)}
    edge = sorted((xy(g.GetStart()), xy(g.GetEnd())) for g in b.GetDrawings() if g.GetLayer() == p.Edge_Cuts)
    return fp, cu, zones, fill, texts, edge


g0, g1 = geometry(b0), geometry(b1)
removed, added = sorted(g0[4] - g1[4]), sorted(g1[4] - g0[4])
t_removed, t_added = {t for t, _ in removed}, {t for t, _ in added}
vin_old = next(q for t, q in g0[4] if t == '+VIN 6-15V'); vin_new = next(q for t, q in g1[4] if t == '+VIN 6-15V')
manifest = json.loads((P / 'reference/P00-R2-release-manifest.json').read_text(encoding='utf-8'))['files']
r2 = P.parent / 'P00-R2-review'
# The R2 package is compared when it sits next to this one (release run in Plytki/); a clean rebuild elsewhere records 'not present'.
r2_changed = sorted(rel for rel, h in manifest.items() if not (r2 / rel).exists() or hashlib.sha256((r2 / rel).read_bytes()).hexdigest() != h) if r2.exists() else []
checks = [('Same part set as R2 (no part added or removed)', set(old) == set(new)),
          ('No pin/net change against R2', not pinchanges),
          ('No value, MPN, footprint, datasheet or source change', not any(changed[k] for k in ('display', 'mpn', 'footprint', 'url', 'source_ref'))),
          ('Part notes changed only for R6, RL9 and TP3', changed['note'] == ['R6', 'RL9', 'TP3']),
          ('Footprints, values, positions, pads, drills, nets and zone connections identical to R2', g0[0] == g1[0]),
          ('Copper identical to R2 (every track and via, width, layer, lock)', g0[1] == g1[1]),
          ('Zones, rule areas and filled copper area identical to R2', g0[2] == g1[2] and g0[3] == g1[3]),
          ('Board outline identical to R2', g0[5] == g1[5]),
          ('Silk text changes only: +VIN legend moved under J10, TP3 VIN -> ZA D1, title R2 -> R3',
           t_removed == {'+VIN 6-15V', 'VIN', 'EGRLab P00 FIXTURE / PCB R2 / 2026-09 - przyrzad stanowiskowy'}
           and t_added == {'+VIN 6-15V', 'ZA D1', 'EGRLab P00 FIXTURE / PCB R3 / 2026-09 - przyrzad stanowiskowy'}),
          ('R2 package unchanged (release manifest)' + ('' if r2.exists() else ' - not present next to this copy, not checked'), not r2_changed)]
rep = {'checks': [{'check': n, 'pass': bool(ok)} for n, ok in checks], 'pin_changes': pinchanges, 'field_changes': changed,
       'copper_items': len(g1[1]), 'filled_area_mm2': g1[3], 'silk_removed': removed, 'silk_added': added,
       '+VIN_moved_mm': round(math.dist(vin_old, vin_new), 2), 'r2_package_checked': r2.exists(), 'r2_package_changed_files': r2_changed, 'passed': all(ok for _, ok in checks)}
(P / 'verification/revision-checks.json').write_text(json.dumps(rep, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
for n, ok in checks:
    print('PASS' if ok else 'FAIL', n)
print('R2 -> R3:', sum(ok for _, ok in checks), '/', len(checks))
raise SystemExit(0 if rep['passed'] else 1)
