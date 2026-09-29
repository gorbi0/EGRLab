"""Studium formatu płytek EGRLab: potrzebna powierzchnia płytek w wariantach harness / magistrala / magistrala+SMD.

Dane: Plytki/Kaseta-R1/dane/plytki.json (obrysy części z PCB R1–R5). P02 R4 nie ma PCB — szacunek z BOM etapu 1.
Model: A_potrzebna = k × (suma obrysów części − złącza między płytkami + złącze magistrali [− oszczędność SMD]),
k = 1,8 (2 warstwy, mieszane THT/SMD), k = 2,0 dla P05 (analog).
"""
import json, re, sys
from pathlib import Path

ROOT = Path(sys.argv[1])
d = json.load(open(ROOT / 'Plytki/Kaseta-R1/dane/plytki.json', encoding='utf-8'))


def area(b):
    return 0 if not b else max(0, b[2] - b[0]) * max(0, b[3] - b[1])


# złącza między płytkami (zastępuje je magistrala w stosie); zewnętrzne i panelowe zostają
INTER = {
    'P03': ['J1', 'J2', 'J3', 'J4', 'J5', 'J6', 'J7', 'J8', 'J9', 'J10'],
    'P04': ['J1', 'J3', 'J4', 'J5', 'J6'],
    'P05': ['J1', 'J2', 'J3', 'J5'],
    'P06': ['J1', 'J2', 'J5'],
    'P08': ['J1', 'J2', 'J3'],
    'P09': ['J1', 'J2'],
    'P10': ['J1', 'J2'],
}
BUS = 4.0          # cm2: listwa 2×20 2,54 mm z odstępem
AX_SMD = 0.13      # cm2: 1206 z padami i odstępem
K = {'P05': 2.0}

rows = {}
for b in ['P03', 'P04', 'P05', 'P06', 'P08', 'P09', 'P10']:
    v = d[b]
    parts = [p for p in v['parts'] if not p['lib'].startswith(('MountingHole', 'Fiducial'))]
    tot = sum(area(p.get('box')) for p in parts) / 100
    inter = sum(area(p.get('box')) for p in parts if p['ref'] in INTER[b]) / 100
    ax = [p for p in parts if re.search(r'R_Axial|R_MFR|Axial', p['lib'])]
    ax_a = sum(area(p.get('box')) for p in ax) / 100
    rows[b] = dict(now=v['W'] * v['H'] / 100, tot=tot, inter=inter, ax_n=len(ax), ax_a=ax_a)

# P02 R4: szacunek z BOM etapu 1 (cm2): 38 × MFR-50 P15,24 po 0,6; 8 × Mini-Fit LV po 1,2; pigtaile PSUOK/PG 4,2+4,2;
# PFAIL 0,6, J11 0,8; reszta (TO-220 ×5 stojące, C_H Ø16, TSR ×2, oprawki MINI ×3, P600, DIP, adapter SO14, TO-92 ×11,
# diody, kondensatory, J1/J2/J14/J15, TP ×17) ok. 39.
rows['P02R4'] = dict(now=115 * 85 / 100, tot=23 + 9.6 + 8.4 + 1.4 + 39 + 4.6, inter=9.6 + 8.4 + 1.4, ax_n=38, ax_a=23)

print(f"{'płytka':6} {'dziś':>5} {'części':>6} {'między':>6} {'R osiowe':>9} | {'wiązki':>6} {'wiąz.+SMD':>9} {'magistr.':>8} {'mag.+SMD':>8}  [cm2]")
need = {}
for b, r in rows.items():
    k = K.get(b, 1.8)
    smd = r['ax_a'] - r['ax_n'] * AX_SMD
    h = k * r['tot']
    hs = k * (r['tot'] - smd)
    m = k * (r['tot'] - r['inter'] + BUS)
    s = k * (r['tot'] - r['inter'] + BUS - smd)
    need[b] = (h, hs, m, s)
    print(f"{b:6} {r['now']:5.0f} {r['tot']:6.0f} {r['inter']:6.1f} {r['ax_n']:3d}/{r['ax_a']:4.0f} | {h:6.0f} {hs:9.0f} {m:8.0f} {s:8.0f}")

json.dump({b: dict(zip(['wiazki', 'wiazki_smd', 'magistrala', 'magistrala_smd'], [round(x, 1) for x in v])) for b, v in need.items()},
          open(Path(sys.argv[2]), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
