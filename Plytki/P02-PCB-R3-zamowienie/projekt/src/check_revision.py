"""Constrain the R3 delta against the frozen R2 release (reference/R2-parts.json, reference/R2.kicad_pcb).
R3 = review P2-01..P2-08 (Claude, 26.09.2026): values/MPNs of F2, F3, F4, R16 (and F1 datasheet link),
schematic graphics, silk legends of the fuse ratings and the title. Copper and placement must stay as in R2.
The R1 -> R2 scope check of the previous release is kept in the R2 package (verification/revision-checks.json there).
"""
from pathlib import Path
import json, pcbnew as p
P = Path(__file__).resolve().parents[1]
old = json.loads((P / 'reference/R2-parts.json').read_text(encoding='utf-8')); new = json.loads((P / 'docs/parts.json').read_text(encoding='utf-8'))
pinchanges = {f'{r}.{n}': [net, new.get(r, {}).get('pins', {}).get(n)] for r in old for n, net in old[r]['pins'].items()
              if new.get(r, {}).get('pins', {}).get(n) != net}
changedvalues = sorted(r for r in old if r in new and old[r]['display'] != new[r]['display'])
changedmpn = sorted(r for r in old if r in new and old[r]['mpn'] != new[r]['mpn'])
b0 = p.LoadBoard(str(P / 'reference/R2.kicad_pcb')); b1 = p.LoadBoard(str(P / 'eda/P02.kicad_pcb'))


def xy(v):
    return (round(p.ToMM(v.x), 4), round(p.ToMM(v.y), 4))


def geometry(b):
    fp = {f.GetReference(): (xy(f.GetPosition()), round(f.GetOrientationDegrees(), 3), f.GetFPIDAsString(),
                             tuple(sorted((a.GetNumber(), a.GetNetname(), xy(a.GetPosition()), int(a.GetLocalZoneConnection())) for a in f.Pads())))
          for f in b.GetFootprints()}
    cu = sorted(('via', t.GetNetname(), xy(t.GetPosition()), round(p.ToMM(t.GetWidth(p.F_Cu)), 3)) if isinstance(t, p.PCB_VIA) else
                ('trk', t.GetNetname(), tuple(sorted([xy(t.GetStart()), xy(t.GetEnd())])), round(p.ToMM(t.GetWidth()), 3), t.GetLayer())
                for t in b.GetTracks())
    zones = sorted((z.GetNetname(), z.GetZoneName(), z.GetIsRuleArea(),
                    tuple(xy(z.Outline().Outline(0).CPoint(j)) for j in range(z.Outline().Outline(0).PointCount()))) for z in b.Zones())
    texts = sorted((g.GetText(), xy(g.GetPosition())) for g in b.GetDrawings() if isinstance(g, p.PCB_TEXT))
    return fp, cu, zones, texts


g0, g1 = geometry(b0), geometry(b1)
texts0, texts1 = {t for t, _ in g0[3]}, {t for t, _ in g1[3]}
checks = [('Same part set as R2 (no part added or removed)', set(old) == set(new)),
          ('No pin/net change against R2', not pinchanges),
          ('Value changes only F2, F3, F4, R16', changedvalues == ['F2', 'F3', 'F4', 'R16']),
          ('MPN changes only F2, F3, F4, R16', changedmpn == ['F2', 'F3', 'F4', 'R16']),
          ('Footprints, positions, pads, nets and zone connections identical to R2', g0[0] == g1[0]),
          ('Copper identical to R2 (every track and via)', g0[1] == g1[1]),
          ('Zones and rule areas identical to R2', g0[2] == g1[2]),
          ('Silk text changes only the fuse ratings and the title line', (texts0 - texts1) == {'F1A', 'F100mA', 'PCB R2 / SCH P02-R2 / 2026-09'}
           and (texts1 - texts0) == {'T1A', 'T500mA', 'PCB R3 / SCH P02-R3 / 2026-09'})]
rep = {'checks': [{'check': n, 'pass': bool(ok)} for n, ok in checks], 'pin_changes': pinchanges, 'value_changes': changedvalues, 'mpn_changes': changedmpn,
       'copper_items': len(g1[1]), 'silk_removed': sorted(texts0 - texts1), 'silk_added': sorted(texts1 - texts0), 'passed': all(ok for _, ok in checks)}
(P / 'verification/revision-checks.json').write_text(json.dumps(rep, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(json.dumps(rep['checks'], indent=2)); assert rep['passed']
