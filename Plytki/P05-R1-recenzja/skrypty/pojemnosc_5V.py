"""Recenzja P05-R1, P5-07: suma kondensatorow na szynach 5 V w najnowszych pakietach plytek wobec
dopuszczalnego obciazenia pojemnosciowego TRACO TSR 2-2450 (600 uF dla modeli 5 V).
Uruchomienie z katalogu Plytki: python P05-R1-recenzja/skrypty/pojemnosc_5V.py
Pomija plytki bez docs/parts.json (P01) i pojemnosc wlasna modulu Waveshare na P03.
"""
import json, re
from pathlib import Path

latest = {}
for d in sorted(Path('.').glob('P[01][0-9]-*review')):
    m = re.match(r'(P\d\d)-(?:PCB-)?R([\d.]+)-review', d.name)
    if not m:
        continue
    key = tuple(int(x) for x in m.group(2).split('.'))
    if m.group(1) not in latest or key > latest[m.group(1)][0]:
        latest[m.group(1)] = (key, d)


def farad(v):
    m = re.match(r'\s*([\d.]+)\s*([munp]?)', v.replace('µ', 'u'))
    return float(m.group(1)) * {'m': 1e-3, 'u': 1e-6, 'n': 1e-9, 'p': 1e-12, '': 1}[m.group(2)] if m else 0.0


total = 0.0
for board, (_, d) in sorted(latest.items()):
    pj = d / 'docs/parts.json'
    if not pj.exists():
        print(board, d.name, 'brak parts.json'); continue
    s = 0.0
    for ref, part in json.loads(pj.read_text(encoding='utf-8')).items():
        nets = set((part.get('pins') or {}).values())
        if ref.startswith('C') and nets & {'5V_SYS', '5VA_P05', '5V_M1'} and 'GND' in nets:
            s += farad(part.get('display') or '')
    total += s
    print(f'{board} {d.name:22} {s * 1e6:7.1f} uF')
print(f'razem {total * 1e6:.1f} uF; TSR 2-2450: maks. 600 uF')
