"""P11 R2: no locked routes (no protection or differential path on this board: contact logic below 1 mA, README). Only the
Specctra DSN export for Freerouting, the step that route_critical.py performs in the P10 R2 chain (kept under the same name so
run_layout.py keeps the P10 order)."""
from pathlib import Path
import pcbnew as p, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from board import NAME
P = Path(__file__).resolve().parents[1]; path = P / f'eda/{NAME}.kicad_pcb'
b = p.LoadBoard(str(path)); b.BuildConnectivity()
(P / 'routing').mkdir(exist_ok=True)
assert p.ExportSpecctraDSN(b, str(P / f'routing/{NAME}.dsn'))
print(f'{NAME}: DSN exported (no locked routes).')
