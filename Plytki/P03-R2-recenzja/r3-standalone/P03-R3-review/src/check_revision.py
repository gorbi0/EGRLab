"""Constrain the R3 delta against the frozen R2 release (reference/R2-parts.json, reference/R2.kicad_pcb).
R3 = review P3-01..P3-06 (Claude, 27.09.2026): R14 0R -> 1K (value/MPN/note), checks, documents and the silk title line.
Copper, placement, zones and pad nets must stay as in R2. The R2 package itself must be untouched when it sits next to
this one (reference/P03-R2-release-manifest.json); a rebuild elsewhere records 'not present'.
"""
from pathlib import Path
import hashlib, json, pcbnew as p
P = Path(__file__).resolve().parents[1]
old = json.loads((P / 'reference/R2-parts.json').read_text(encoding='utf-8')); new = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
pinchanges = {f'{r}.{n}': [net, new.get(r, {}).get('pins', {}).get(n)] for r in old for n, net in old[r]['pins'].items() if new.get(r, {}).get('pins', {}).get(n) != net}
changed = {k: sorted(r for r in old if r in new and old[r].get(k) != new[r].get(k)) for k in ('display', 'mpn', 'footprint', 'note', 'url', 'source_ref', 'sheet')}
b0 = p.LoadBoard(str(P / 'reference/R2.kicad_pcb')); b1 = p.LoadBoard(str(P / 'eda/P03.kicad_pcb'))


def xy(v):
    return (round(p.ToMM(v.x), 4), round(p.ToMM(v.y), 4))


def geometry(b):
    fp = {f.GetReference(): (xy(f.GetPosition()), round(f.GetOrientationDegrees(), 3), f.GetFPIDAsString(),
                             tuple(sorted((a.GetNumber(), a.GetNetname(), xy(a.GetPosition()), xy(a.GetDrillSize()), int(a.GetLocalZoneConnection())) for a in f.Pads())))
          for f in b.GetFootprints()}
    values = {f.GetReference(): f.GetValue() for f in b.GetFootprints()}
    cu = sorted(('via', t.GetNetname(), xy(t.GetPosition()), round(p.ToMM(t.GetWidth(p.F_Cu)), 3), round(p.ToMM(t.GetDrill()), 3)) if isinstance(t, p.PCB_VIA) else
                ('trk', t.GetNetname(), tuple(sorted([xy(t.GetStart()), xy(t.GetEnd())])), round(p.ToMM(t.GetWidth()), 3), t.GetLayer(), t.IsLocked())
                for t in b.GetTracks())
    zones = sorted((z.GetNetname(), z.GetZoneName(), z.GetIsRuleArea(), tuple(sorted(b.GetLayerName(l) for l in z.GetLayerSet().Seq())),
                    tuple(xy(z.Outline().Outline(0).CPoint(j)) for j in range(z.Outline().Outline(0).PointCount()))) for z in b.Zones())
    fill = {b.GetLayerName(L): round(sum(z.GetFilledPolysList(L).Area() for z in b.Zones() if not z.GetIsRuleArea() and z.IsOnLayer(L)) / 1e12, 3)
            for L in (p.F_Cu, p.B_Cu)}
    texts = {(g.GetText(), xy(g.GetPosition())) for g in b.GetDrawings() if isinstance(g, p.PCB_TEXT)}
    edge = sorted((xy(g.GetStart()), xy(g.GetEnd())) for g in b.GetDrawings() if g.GetLayer() == p.Edge_Cuts)
    return fp, values, cu, zones, fill, texts, edge


g0, g1 = geometry(b0), geometry(b1)
vchanged = sorted(r for r in g0[1] if g0[1][r] != g1[1].get(r))
removed, added = sorted(g0[5] - g1[5]), sorted(g1[5] - g0[5])
manifest = json.loads((P / 'reference/P03-R2-release-manifest.json').read_text(encoding='utf-8'))['files']
r2 = P.parent / 'P03-R2-review'
r2_changed = sorted(rel for rel, h in manifest.items() if not (r2 / rel).exists() or hashlib.sha256((r2 / rel).read_bytes()).hexdigest() != h) if r2.exists() else []
checks = [('Same part set as R2 (no part added or removed)', set(old) == set(new)),
          ('No pin/net change against R2', not pinchanges),
          ('Value and MPN change only on R14 (0R -> 1K)', changed['display'] == ['R14'] and changed['mpn'] == ['R14'] and new['R14']['display'].startswith('1K')),
          ('No footprint, datasheet, source or sheet change; note changed only on R14', not any(changed[k] for k in ('footprint', 'url', 'source_ref', 'sheet')) and changed['note'] == ['R14']),
          ('Board values differ only on R14', vchanged == ['R14']),
          ('Footprints, positions, pads, drills, nets and zone connections identical to R2', g0[0] == g1[0]),
          ('Copper identical to R2 (every track and via, width, layer, lock)', g0[2] == g1[2]),
          ('Zones, rule areas and filled copper area identical to R2', g0[3] == g1[3] and g0[4] == g1[4]),
          ('Board outline identical to R2', g0[6] == g1[6]),
          ('Silk text changes only the title line (PCB R2 -> PCB R3)', {t for t, _ in removed} == {'EGRLab P03 CORE / PCB R2 / 2026-09'} and {t for t, _ in added} == {'EGRLab P03 CORE / PCB R3 / 2026-09'}),
          ('R2 package unchanged (release manifest)' + ('' if r2.exists() else ' - not present next to this copy, not checked'), not r2_changed)]
rep = {'checks': [{'check': n, 'pass': bool(ok)} for n, ok in checks], 'pin_changes': pinchanges, 'field_changes': changed, 'board_value_changes': vchanged,
       'copper_items': len(g1[2]), 'filled_area_mm2': g1[4], 'silk_removed': removed, 'silk_added': added,
       'r2_package_checked': r2.exists(), 'r2_package_changed_files': r2_changed, 'passed': all(ok for _, ok in checks)}
(P / 'verification/revision-checks.json').write_text(json.dumps(rep, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
for n, ok in checks:
    print('PASS' if ok else 'FAIL', n)
print('R2 -> R3:', sum(ok for _, ok in checks), '/', len(checks))
raise SystemExit(0 if rep['passed'] else 1)
