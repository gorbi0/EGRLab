"""Fresh native DRC bound to the exact inputs (adapted from P01 R3.1 provenance.py)."""
from pathlib import Path
import hashlib, json, subprocess, sys, os, datetime
P = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def inputs(board=None):
    result = {}
    for folder in ('eda', 'src', 'reference', 'input', 'requirements'):
        for f in sorted((P / folder).rglob('*')):
            if f.is_file() and f.suffix not in ('.pyc', '.kicad_prl') and '__pycache__' not in f.parts and not f.name.endswith('.lck'):
                result[f.relative_to(P).as_posix()] = sha(f)
    for rel in ('docs/parts.json', 'routing/prerouted.kicad_pcb', 'routing/P06.ses', 'routing/completion-routes.json', 'verification/P06.xml'):
        f = P / rel
        if f.exists():
            result[rel] = sha(f)
    if board is not None:
        result['eda/P06.kicad_pcb'] = sha(board)
    return result


def run_fresh_drc(board, report):
    before = inputs(board)
    cli = Path(sys.executable).with_name('kicad-cli.exe')
    report = Path(report).resolve(); report.parent.mkdir(parents=True, exist_ok=True)
    if report.exists():
        report.unlink()  # never reuse a stale result
    command = [str(cli), 'pcb', 'drc', '--format', 'json', '--severity-all', '--all-track-errors', '--schematic-parity', '--refill-zones',
               '-o', str(report), str(Path(board).resolve())]
    run = subprocess.run(command, capture_output=True, text=True)
    report.with_suffix('.log').write_text(run.stdout + '\n' + run.stderr)
    if run.returncode or not report.exists():
        raise RuntimeError('Native DRC did not complete; see ' + str(report.with_suffix('.log')))
    drc = json.loads(report.read_text())
    if not all(isinstance(drc.get(k), list) for k in ('violations', 'unconnected_items', 'schematic_parity')):
        raise RuntimeError('Incomplete DRC JSON')
    after = inputs(board)
    if before != after:
        raise RuntimeError('Inputs changed while DRC was running')
    receipt = {'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'inputs': after, 'drc_path': report.name,
               'drc_sha256': sha(report), 'command': ['kicad-cli'] + command[1:-1] + [Path(board).name],
               'counts': {k: len(drc[k]) for k in ('violations', 'unconnected_items', 'schematic_parity')}}
    report.with_suffix('.provenance.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return drc, receipt
