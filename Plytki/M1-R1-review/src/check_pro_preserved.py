"""8.10 (recenzja M1-05): build_schematic.py nie moze kasowac ustawien projektu KiCad. Proba: do eda/M1.kicad_pro dopisuje klase sieci
REVIEW_M105, zmieniona regule (min_clearance) i dodatkowe pole; uruchamia sam generator schematu; sprawdza, ze sekcje board / net_settings
/ inne sa takie jak przed generatorem (zmieniaja sie tylko meta i sheets). Oryginalny plik zawsze przywracany. Exit 0 = zachowane."""
from pathlib import Path
import json, subprocess, sys, shutil
P = Path(__file__).resolve().parents[1]; pro = P / 'eda/M1.kicad_pro'; keep = pro.read_bytes()
try:
    d = json.loads(keep)
    d.setdefault('net_settings', {}).setdefault('classes', []).append({'name': 'REVIEW_M105', 'clearance': 0.33, 'track_width': 0.33})
    d.setdefault('board', {}).setdefault('design_settings', {}).setdefault('rules', {})['min_clearance'] = 0.123
    d['review_m105_marker'] = {'kept': True}
    pro.write_text(json.dumps(d, indent=2) + '\n')
    before = {k: v for k, v in d.items() if k not in ('meta', 'sheets')}
    r = subprocess.run([sys.executable, str(P / 'src/build_schematic.py')], cwd=P, capture_output=True, text=True)
    if r.returncode: sys.exit('build_schematic failed: ' + r.stderr[-400:])
    after = json.loads(pro.read_text())
    lost = sorted(k for k in before if after.get(k) != before[k])
    print('project sections kept by the schematic generator:', 'all' if not lost else 'LOST ' + ', '.join(lost))
finally:
    pro.write_bytes(keep)
sys.exit(1 if lost else 0)
