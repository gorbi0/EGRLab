"""P09 R2: no locked power path (the P03 R6 chain drew its 5 V path here); only the Specctra DSN export for Freerouting.
The supplies of P09 (3V3_IO, 5V_SYS, TCx_VIN) carry a few mA (MAX31856 modules, buffers) and are routed as signals.
"""
from pathlib import Path
import pcbnew as p, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from board import NAME
P = Path(__file__).resolve().parents[1]; path = P / f'eda/{NAME}.kicad_pcb'

if __name__ == '__main__':
    b = p.LoadBoard(str(path)); b.BuildConnectivity(); p.SaveBoard(str(path), b)
    (P / 'routing').mkdir(exist_ok=True)
    assert p.ExportSpecctraDSN(b, str(P / f'routing/{NAME}.dsn'))
    print('No locked copper on P09; DSN exported.')
