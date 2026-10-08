"""Placement review (step 5 of the M1 plan): build the board without copper and plot courtyards / fab / pads + a 3D top view."""
import subprocess, sys, os
from pathlib import Path
P = Path(__file__).resolve().parents[1]; PY = sys.executable
CLI = os.environ.get('KICAD_CLI', str(Path(PY).with_name('kicad-cli.exe')))
for s in ['placement.py', 'build_board.py', 'set_stackup.py', 'set_rules.py']:
    subprocess.run([PY, s], cwd=P / 'src', check=True)
pcb = str(P / 'eda/M1.kicad_pcb'); out = P / 'output/previews'
subprocess.run([CLI, 'pcb', 'export', 'svg', '--layers', 'Edge.Cuts,F.Courtyard,F.Fab,F.Cu,F.Silkscreen,User.Comments', '--mode-single', '--page-size-mode', '2',
                '--exclude-drawing-sheet', '-o', str(out / 'placement.svg'), pcb], check=True)
subprocess.run([CLI, 'pcb', 'export', 'svg', '--layers', 'Edge.Cuts,B.Courtyard,B.Fab,B.Cu', '--mode-single', '--page-size-mode', '2', '--mirror',
                '--exclude-drawing-sheet', '-o', str(out / 'placement-back.svg'), pcb], check=True)
for name, extra in [('placement-3d', ['--side', 'top', '--zoom', '.95']), ('placement-iso', ['--side', 'top', '--rotate', '325,0,15', '--zoom', '.85'])]:
    subprocess.run([CLI, 'pcb', 'render', *extra, '--width', '2000', '--height', '1200', '--quality', 'basic', '--background', 'opaque', '-o', str(out / (name + '.png')), pcb], check=True)
