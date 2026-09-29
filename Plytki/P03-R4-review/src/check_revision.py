"""Constrain the R4 delta against the frozen R3 release (reference/R3-parts.json, reference/R3.kicad_pcb).
R4 = Schmitt buffer SN74LVC1G17 (U6) with R41 220R and C15 100 nF between the common reset SUP_N and J4.15 (P04), user
decision after the final R2 review (P3-01; Claude, 27.09.2026). Allowed: the three new parts, J4.15 SUP_N -> SUP_N_OUT,
the J4 note, the copper of the change (locked, inside the change area, on the nets of the change), the three R3
segments it replaces and the lock of the kept R3 segments of the two replaced wires, the silk title line. Everything else (other parts, positions, pads, copper, zones) as in R3.
The R3 package itself must be untouched when it sits next to this one (reference/P03-R3-release-manifest.json).
"""
from pathlib import Path
import hashlib, json, pcbnew as p
P = Path(__file__).resolve().parents[1]
old = json.loads((P / 'reference/R3-parts.json').read_text(encoding='utf-8')); new = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
NEW_PARTS = {'U6', 'R41', 'C15'}
pinchanges = {f'{r}.{n}': [net, new.get(r, {}).get('pins', {}).get(n)] for r in old for n, net in old[r]['pins'].items() if new.get(r, {}).get('pins', {}).get(n) != net}
changed = {k: sorted(r for r in old if r in new and old[r].get(k) != new[r].get(k)) for k in ('display', 'mpn', 'footprint', 'note', 'url', 'source_ref', 'sheet')}
b0 = p.LoadBoard(str(P / 'reference/R3.kicad_pcb')); b1 = p.LoadBoard(str(P / 'eda/P03.kicad_pcb'))
# the change: area and nets of the copper laid by route_critical.py (R4 block)
AREA = (6.0, 58.0, 31.0, 84.0)
NETS = {'SUP_N', 'SUP_N_DRV', 'SUP_N_OUT', 'HW_ARMED_CORE', '3V3_CORE', 'GND'}
# the three R3 router segments replaced by it (net, end, end, width, layer)
REPLACED = {('HW_ARMED_CORE', ((6.6987, 72.9625), (12.4245, 78.6883)), .3, 'F.Cu'), ('HW_ARMED_CORE', ((12.4245, 78.6883), (15.8083, 78.6883)), .3, 'F.Cu'),
            ('SUP_N', ((6.5, 58.2327), (6.5, 83.37)), .3, 'B.Cu')}


def xy(v):
    return (round(p.ToMM(v.x), 4), round(p.ToMM(v.y), 4))


def n(item):
    return item.GetNetname().split('/')[-1]


def copper(b):
    return sorted(('via', n(t), xy(t.GetPosition()), round(p.ToMM(t.GetWidth(p.F_Cu)), 3), round(p.ToMM(t.GetDrill()), 3), t.IsLocked()) if isinstance(t, p.PCB_VIA) else
                  ('trk', n(t), tuple(sorted([xy(t.GetStart()), xy(t.GetEnd())])), round(p.ToMM(t.GetWidth()), 3), b.GetLayerName(t.GetLayer()), t.IsLocked())
                  for t in b.GetTracks())


def geometry(b):
    fp = {f.GetReference(): (xy(f.GetPosition()), round(f.GetOrientationDegrees(), 3), f.GetFPIDAsString(),
                             tuple(sorted((a.GetNumber(), n(a), xy(a.GetPosition()), xy(a.GetDrillSize()), int(a.GetLocalZoneConnection())) for a in f.Pads())))
          for f in b.GetFootprints()}
    values = {f.GetReference(): f.GetValue() for f in b.GetFootprints()}
    zones = sorted((z.GetNetname(), z.GetZoneName(), z.GetIsRuleArea(), tuple(sorted(b.GetLayerName(l) for l in z.GetLayerSet().Seq())),
                    tuple(xy(z.Outline().Outline(0).CPoint(j)) for j in range(z.Outline().Outline(0).PointCount()))) for z in b.Zones())
    fill = {b.GetLayerName(L): round(sum(z.GetFilledPolysList(L).Area() for z in b.Zones() if not z.GetIsRuleArea() and z.IsOnLayer(L)) / 1e12, 3)
            for L in (p.F_Cu, p.B_Cu)}
    texts = {(g.GetText(), xy(g.GetPosition())) for g in b.GetDrawings() if isinstance(g, p.PCB_TEXT)}
    edge = sorted((xy(g.GetStart()), xy(g.GetEnd())) for g in b.GetDrawings() if g.GetLayer() == p.Edge_Cuts)
    return fp, values, zones, fill, texts, edge


g0, g1 = geometry(b0), geometry(b1)
c0, c1 = copper(b0), copper(b1)
geo0, geo1 = {x[:-1]: x[-1] for x in c0}, {x[:-1]: x[-1] for x in c1}  # geometry -> locked
assert len(geo0) == len(c0) and len(geo1) == len(c1), 'duplicate copper items'
only0 = [k + (geo0[k],) for k in geo0 if k not in geo1]; only1 = [k + (geo1[k],) for k in geo1 if k not in geo0]
relocked = [k + (geo1[k],) for k in geo0 if k in geo1 and geo0[k] != geo1[k]]


def in_area(x):
    pts = [x[2]] if x[0] == 'via' else list(x[2])
    return all(AREA[0] <= u <= AREA[2] and AREA[1] <= v <= AREA[3] for u, v in pts)


fp_same = {r: g0[0][r] == g1[0][r] for r in g0[0]}
j4_old, j4_new = g0[0]['J4'], g1[0]['J4']
j4_pads = [(a, c) for a, c in zip(j4_old[3], j4_new[3]) if a != c]
vchanged = sorted(r for r in g0[1] if g0[1][r] != g1[1].get(r))
removed, added = sorted(g0[4] - g1[4]), sorted(g1[4] - g0[4])
manifest = json.loads((P / 'reference/P03-R3-release-manifest.json').read_text(encoding='utf-8'))['files']
r3 = P.parent / 'P03-R3-review'
r3_changed = sorted(rel for rel, h in manifest.items() if not (r3 / rel).exists() or hashlib.sha256((r3 / rel).read_bytes()).hexdigest() != h) if r3.exists() else []
checks = [('Part set = R3 + U6, R41, C15 (nothing removed)', set(new) == set(old) | NEW_PARTS and not NEW_PARTS & set(old)),
          ('Only pin change against R3: J4.15 SUP_N -> SUP_N_OUT', pinchanges == {'J4.15': ['SUP_N', 'SUP_N_OUT']}),
          ('New parts: U6 SN74LVC1G17DBVR (SOT-23-5), R41 220R 1206, C15 100 nF 1206', new['U6']['mpn'] == 'SN74LVC1G17DBVR' and new['U6']['footprint'].endswith('SOT-23-5')
           and new['R41']['display'].startswith('220R') and new['C15']['display'].startswith('100nF')),
          ('No value, MPN, footprint, datasheet, source or sheet change on R3 parts; note changed only on J4', not any(changed[k] for k in ('display', 'mpn', 'footprint', 'url', 'source_ref', 'sheet'))
           and changed['note'] == ['J4']),
          ('Board values of R3 parts unchanged', not vchanged),
          ('R3 footprints: positions, pads, drills, nets and zone connections identical, except the net of J4.15',
           set(g1[0]) == set(g0[0]) | NEW_PARTS and all(fp_same[r] for r in g0[0] if r != 'J4') and j4_old[:3] == j4_new[:3]
           and len(j4_pads) == 1 and j4_pads[0][0][0] == '15' and j4_pads[0][0][1] == 'SUP_N' and j4_pads[0][1][1] == 'SUP_N_OUT' and j4_pads[0][0][2:] == j4_pads[0][1][2:]),
          ('R3 copper removed: exactly the three replaced segments (HW_ARMED_CORE x2, SUP_N branch end to J4.15)',
           {(x[1], x[2], x[3], x[4]) for x in only0} == REPLACED and len(only0) == 3),
          ('R4 copper added: locked, inside the change area 6-31 x 58-84 mm, only on the nets of the change',
           only1 and all(x[-1] and in_area(x) and x[1] in NETS for x in only1)),
          ('Lock state changed only on the kept R3 segments of the two replaced wires (SUP_N, HW_ARMED_CORE; now laid and locked by route_critical.py)',
           relocked and all(x[1] in ('SUP_N', 'HW_ARMED_CORE') and x[0] == 'trk' and x[-1] for x in relocked)),
          ('Zones and rule areas identical to R3', g0[2] == g1[2]),
          ('Board outline identical to R3', g0[5] == g1[5]),
          ('Silk text changes only the title line (PCB R3 -> PCB R4)', {t for t, _ in removed} == {'EGRLab P03 CORE / PCB R3 / 2026-09'} and {t for t, _ in added} == {'EGRLab P03 CORE / PCB R4 / 2026-09'}),
          ('R3 package unchanged (release manifest)' + ('' if r3.exists() else ' - not present next to this copy, not checked'), not r3_changed)]
rep = {'checks': [{'check': k, 'pass': bool(ok)} for k, ok in checks], 'pin_changes': pinchanges, 'field_changes': changed, 'board_value_changes': vchanged,
       'copper_items': {'R3': len(c0), 'R4': len(c1)}, 'copper_removed': only0, 'copper_added': only1, 'copper_relocked': relocked,
       'filled_area_mm2': {'R3': g0[3], 'R4': g1[3]}, 'silk_removed': removed, 'silk_added': added,
       'r3_package_checked': r3.exists(), 'r3_package_changed_files': r3_changed, 'passed': all(ok for _, ok in checks)}
(P / 'verification/revision-checks.json').write_text(json.dumps(rep, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
for k, ok in checks:
    print('PASS' if ok else 'FAIL', k)
print('R3 -> R4:', sum(ok for _, ok in checks), '/', len(checks), '| copper', len(c0), '->', len(c1), '(-', len(only0), '+', len(only1), ', relocked', len(relocked), ')')
raise SystemExit(0 if rep['passed'] else 1)
