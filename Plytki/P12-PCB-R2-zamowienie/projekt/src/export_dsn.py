"""P12 R2 (as R1): no locked routes and no SMD fan-out (THT connectors only); export the Specctra DSN for Freerouting (prepare_routing.py follows)."""
from pathlib import Path
import pcbnew as p, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from board import NAME
P = Path(__file__).resolve().parents[1]; b = p.LoadBoard(str(P / f'eda/{NAME}.kicad_pcb'))
(P / 'routing').mkdir(exist_ok=True)
assert p.ExportSpecctraDSN(b, str(P / f'routing/{NAME}.dsn'))
print(f'{NAME}: DSN exported.')
