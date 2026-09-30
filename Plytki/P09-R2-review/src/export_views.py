"""Native KiCad plots/renders for the review PDF (from P02 R3 export_views.py). The PCB file is never changed; F.Fab reference
texts are dropped only in a plot copy. SVGs cover the board area only (page-size-mode 2), so they print at 1:1.
"""
from pathlib import Path
import subprocess, sys, os
from sexpr import parse, dump, sub, one
sys.path.insert(0, str(Path(__file__).resolve().parent))
from board import NAME
P = Path(__file__).resolve().parents[1]; cli = os.environ.get('KICAD_CLI', str(Path(sys.executable).with_name('kicad-cli.exe')))
env = dict(os.environ); env['KICAD_CONFIG_HOME'] = str(P / 'verification/tool-config')
root = parse((P / f'eda/{NAME}.kicad_pcb').read_text())
for fp in sub(root, 'footprint'):
    for t in list(sub(fp, 'fp_text')):
        if one(t, 'layer')[1] in ('F.Fab', 'B.Fab'):
            fp.remove(t)
out = P / 'output'; (out / 'svg').mkdir(parents=True, exist_ok=True); (out / 'previews').mkdir(parents=True, exist_ok=True)
source = out / 'plot-source.kicad_pcb'; source.write_text(dump(root) + '\n')


def run(args, name):
    r = subprocess.run([cli, *args], capture_output=True, text=True, env=env)
    (P / 'verification' / ('export-' + name + '.log')).write_text(r.stdout + '\n' + r.stderr)
    if r.returncode:
        raise RuntimeError(name + ' export failed')


for name, layers, mirror, pcb in [
        ('assembly', 'F.Fab,F.Silkscreen,Edge.Cuts', False, source),
        ('copper-front', 'F.Cu,Edge.Cuts', False, P / f'eda/{NAME}.kicad_pcb'),
        ('copper-back', 'B.Cu,Edge.Cuts', True, P / f'eda/{NAME}.kicad_pcb'),
        ('fit', 'Edge.Cuts,F.Courtyard,F.Fab', False, source)]:
    args = ['pcb', 'export', 'svg', '--layers', layers, '--mode-single', '--page-size-mode', '2', '--exclude-drawing-sheet', '--black-and-white',
            '--sketch-pads-on-fab-layers', '-o', str(out / 'svg' / (name + '.svg'))]
    if mirror:
        args += ['--mirror']
    run(args + [str(pcb)], name)
for name, extra in [('isometric', ['--side', 'top', '--rotate', '325,0,15', '--zoom', '.85']), ('top', ['--side', 'top', '--zoom', '.95'])]:
    run(['pcb', 'render', *extra, '--width', '1800', '--height', '1500', '--quality', 'basic', '--background', 'opaque', '-o',
         str(out / 'previews' / (name + '.png')), str(P / f'eda/{NAME}.kicad_pcb')], name)
source.unlink()
print('Native assembly / copper / fit SVG and two 3D views exported.')
