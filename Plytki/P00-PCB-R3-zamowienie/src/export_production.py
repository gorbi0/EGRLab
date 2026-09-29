"""Eksport plików produkcyjnych z niezmienionej kopii wydania płytki.
Uruchomienie: Python z KiCad 10.0.6 (ten sam katalog co kicad-cli.exe):
    python src/export_production.py
Konfiguracja płytki: src/config.json. Pliku PCB nie zapisuje; sprawdza to sumami SHA-256.
"""
from pathlib import Path
import datetime, hashlib, json, subprocess, sys
import pcbnew as pcb

R = Path(__file__).resolve().parents[1]
CFG = json.loads((R/'src'/'config.json').read_text(encoding='utf-8'))
NAME = CFG['name']
P = R/'projekt'
V, G, PV = R/'verification', R/'gerber', R/'podglad'
board = P/'eda'/f'{NAME}.kicad_pcb'
cli = Path(sys.executable).with_name('kicad-cli.exe')


def sha(f):
    return hashlib.sha256(Path(f).read_bytes()).hexdigest()


def run(name, cmd):
    cmd = [str(c) for c in cmd]
    r = subprocess.run(cmd, capture_output=True, text=True)
    (V/f'{name}.log').write_text(r.stdout + '\n' + r.stderr, encoding='utf-8')
    if r.returncode:
        raise RuntimeError(f'{name}: exit {r.returncode}')
    print(name, 'PASS', flush=True)
    return cmd


def eda_hashes():
    return {f.name: sha(f) for f in sorted((P/'eda').iterdir()) if f.is_file() and not f.name.endswith('.lck')}


for d in (G, PV):
    for f in d.iterdir():
        f.unlink()
before = eda_hashes()
snap = json.loads((V/'source-snapshot.json').read_text(encoding='utf-8'))
assert sha(board) == snap['sha256'][f'eda/{NAME}.kicad_pcb'], 'Kopia PCB różni się od wydania źródłowego'

cmds = []
cmds.append(run('drc', [cli, 'pcb', 'drc', '--refill-zones', '--schematic-parity', '--severity-all',
                        '--format', 'json', '--units', 'mm', '--output', V/'drc.json', board]))
drc = json.loads((V/'drc.json').read_text(encoding='utf-8'))
counts = {'violations': len(drc.get('violations', [])),
          'unconnected_items': len(drc.get('unconnected_items', [])),
          'schematic_parity': len(drc.get('schematic_parity', []))}
(V/'drc-counts.json').write_text(json.dumps(counts, indent=2) + '\n', encoding='utf-8')
assert all(v == 0 for v in counts.values()), f'DRC nie jest czysty: {counts}'
assert eda_hashes() == before, 'DRC zmienił pliki projektu'

cmds.append(run('gerber-export', [cli, 'pcb', 'export', 'gerbers', '--layers',
                                  ','.join(CFG['layers']), '--precision', '6',
                                  '--subtract-soldermask', '--disable-aperture-macros', '--check-zones',
                                  '--output', str(G) + '/', board]))
cmds.append(run('drill-export', [cli, 'pcb', 'export', 'drill', '--format', 'excellon', '--drill-origin', 'absolute',
                                 '--excellon-zeros-format', 'decimal', '--excellon-units', 'mm', '--excellon-separate-th',
                                 '--generate-map', '--map-format', 'svg', '--generate-report',
                                 '--report-path', V/'drill-report.txt', '--output', str(G) + '/', board]))
for f in list(G.glob('*.svg')):
    f.replace(PV/f.name)
for f in list(G.glob('*.gbrjob')):
    f.replace(V/f.name)  # obwiednia kreski obrysu, nie wymiar płytki — poza ZIP, jak w P01
assert eda_hashes() == before, 'Eksport zmienił pliki projektu'

b = pcb.LoadBoard(str(board))


def mm(v):
    return round(pcb.ToMM(v), 6)


pads, holes = [], []
for fp in b.GetFootprints():
    for p in fp.Pads():
        pos = p.GetPosition(); d = p.GetDrillSize()
        on = [l for l, i in (('F.Cu', pcb.F_Cu), ('B.Cu', pcb.B_Cu)) if p.IsOnLayer(i)]
        mask = [l for l, i in (('F.Mask', pcb.F_Mask), ('B.Mask', pcb.B_Mask)) if p.IsOnLayer(i)]
        pads.append({'ref': fp.GetReference(), 'pin': p.GetNumber(), 'x': mm(pos.x), 'y': -mm(pos.y),
                     'attr': int(p.GetAttribute()), 'net': p.GetNetname(), 'copper': on, 'mask': mask})
        if d.x or d.y:
            assert d.x == d.y, f'Otwór podłużny {fp.GetReference()}.{p.GetNumber()} wymaga osobnej kontroli'
            holes.append({'ref': fp.GetReference(), 'pin': p.GetNumber(), 'x': mm(pos.x), 'y': -mm(pos.y),
                          'diameter': mm(d.x), 'plated': p.GetAttribute() != pcb.PAD_ATTRIB_NPTH})
vias = [t for t in b.GetTracks() if isinstance(t, pcb.PCB_VIA)]
for t in vias:
    pos = t.GetPosition()
    holes.append({'ref': 'VIA', 'pin': '', 'x': mm(pos.x), 'y': -mm(pos.y), 'diameter': mm(t.GetDrill()), 'plated': True})
widths = [mm(t.GetWidth()) for t in b.GetTracks() if not isinstance(t, pcb.PCB_VIA)]
zones = {'F.Cu': 0, 'B.Cu': 0}
zone_outlines = {'F.Cu': 0, 'B.Cu': 0}
filler = pcb.ZONE_FILLER(b)
filler.Fill(b.Zones())  # jak --check-zones przy eksporcie; tylko w pamięci, pliku nie zapisujemy
for z in b.Zones():
    for l, i in (('F.Cu', pcb.F_Cu), ('B.Cu', pcb.B_Cu)):
        if z.IsOnLayer(i) and not z.GetIsRuleArea():
            zones[l] += 1
            zone_outlines[l] += z.GetFilledPolysList(i).OutlineCount()
data = {'name': NAME, 'board_sha256': sha(board), 'board_mm': CFG['board_mm'], 'thickness_mm': CFG['thickness_mm'],
        'copper_um_each': CFG['copper_um'], 'min_track_mm': min(widths) if widths else None, 'tracks': len(widths),
        'vias': len(vias), 'footprints': len(list(b.GetFootprints())), 'zones': zones, 'zone_outlines': zone_outlines,
        'holes': holes, 'pads': pads,
        'drc': counts}
(V/'board-fabrication-data.json').write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
job = next(V.glob('*.gbrjob'))
(V/'export-receipt.json').write_text(json.dumps({
    'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'kicad': '10.0.6',
    'board_sha256': sha(board), 'drc_sha256': sha(V/'drc.json'), 'drc': counts, 'inputs_unchanged': True,
    'commands': cmds, 'files': {f.name: sha(f) for f in sorted(G.iterdir()) if f.is_file()},
    'native_job_sha256': sha(job)}, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'board_sha256': data['board_sha256'], 'min_track_mm': data['min_track_mm'], 'tracks': len(widths),
                  'vias': len(vias), 'footprints': data['footprints'], 'holes': len(holes), 'zones': zones,
                  'zone_outlines': zone_outlines, 'drc': counts}))
