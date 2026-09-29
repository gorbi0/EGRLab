"""P03 R4: after import_routing.py, unlock the copper seeded from R3 (routing/seed.json), so cleanup.py treats it as
router copper exactly as in R3. Copper locked by route_critical.py stays locked. Run once, right after the import."""
from pathlib import Path
import pcbnew as p, json
from seed_sig import sig
P = Path(__file__).resolve().parents[1]; fn = P / 'eda/P03.kicad_pcb'; b = p.LoadBoard(str(fn))
want = {json.dumps(x) for x in json.loads((P / 'routing/seed.json').read_text())['seeded']}; n = 0; found = set()
for t in b.GetTracks():
    k = json.dumps(sig(t))
    if k in want and t.IsLocked():
        t.SetLocked(False); n += 1; found.add(k)
missing = want - found
assert not missing, f'{len(missing)} seeded items not found on the imported board'
p.SaveBoard(str(fn), b)
print('unlocked', n, 'seeded R3 items')
