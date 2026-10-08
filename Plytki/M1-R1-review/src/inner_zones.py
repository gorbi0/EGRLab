"""M1-R1: In2.Cu carries signals only (board.IN2_SUPPLY is empty: supplies are PWR tracks, In1.Cu a solid GND plane). Kept as a step of the
P07 S1 chain (run_layout.py calls it); nothing to do here."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from board import IN2_SUPPLY
assert not IN2_SUPPLY, 'M1 has no In2 supply zones; restore the P07 S1 inner_zones.py if this changes'
print('In2 supply zones: none (M1)')
