"""2.10: decoupling returns of a finished router attempt (run_layout.py rejects the attempt, exit 5, when one is too long). Each pair of
board.RETURN_PAIRS: GND copper path (gndpath.py) capacitor GND pad -> GND pin of its part <= 1.3 x straight + 3 mm, or the limit in
board.RETURN_ACCEPT (accepted exceptions, same values as verify_pcb.py). Report: routing/return-check.json."""
from pathlib import Path
import pcbnew as p, json, math, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gndpath
from board import NAME, RETURN_PAIRS
try:
    from board import RETURN_ACCEPT
except ImportError:
    RETURN_ACCEPT = {}
from build_board import W, Hh as H
P = Path(__file__).resolve().parents[1]
b = p.LoadBoard(str(P / f'eda/{NAME}.kicad_pcb')); p.ZONE_FILLER(b).Fill(b.Zones())
cu, via = gndpath.copper(b, 'GND', W, H); rep = {}
for c, spec in RETURN_PAIRS.items():
    u, n = spec[:2]; g = next(a for f in b.GetFootprints() if f.GetReference() == c for a in f.Pads() if a.GetNetname() == 'GND')
    s_, t_ = gndpath.pad_point(b, c, g.GetNumber()), gndpath.pad_point(b, u, n); st = math.dist(s_[:2], t_[:2])
    d = gndpath.distances(cu, via, s_, {'d': t_}, limit_mm=150)['d']; lim = RETURN_ACCEPT.get(c, round(1.3 * st + 3, 1))
    rep[f'{c}-{u}.{n}'] = {'path_mm': d, 'limit_mm': lim, 'ok': d is not None and d <= lim}
(P / 'routing/return-check.json').write_text(json.dumps(rep, indent=1) + '\n')
bad = {k: v['path_mm'] for k, v in rep.items() if not v['ok']}
print('return check:', 'all within limits' if not bad else f'too long {bad}')
sys.exit(5 if bad else 0)
