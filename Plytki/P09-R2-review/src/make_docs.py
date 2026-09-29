"""Contracts for the P12 connection board (docs/J_BP.csv, docs/SERWIS.csv) and the net purchase list, all from parts.py (single source)."""
from parts import *
import collections
def w(name,head,rows):
 with (P/'docs'/name).open('w',newline='',encoding='utf-8-sig') as f:
  x=csv.writer(f,delimiter=';');x.writerow(head);x.writerows(rows)
rows=[]
for p in range(1,17):
 if p%2:rows.append([p,'GND','masa','wszystkie (P12)','powrót sygnału; piny nieparzyste zawsze GND'])
 else:
  n,kier,cel,uw=next((n,k,c,u) for pp,n,k,c,u in JBP if pp==p);rows.append([p,n,kier,cel,uw])
w('J_BP.csv',['pin','siec','kierunek','plytka_docelowa','uwagi'],rows)
w('SERWIS.csv',['pin','siec','rezystor','cel_pomiaru'],
  [[1,'GND','—','masa sondy (pierwszy pin listwy)']]+[[k,net,f'{srv_r[net]} 1 kΩ 1206',cel] for k,(net,cel) in enumerate(SRV,2)]+[[13,'GND','—','masa sondy (ostatni pin listwy)']])
g=collections.defaultdict(list)
for r,p in PARTS.items():
 g[p['zrodlo'],p['mpn'],p['footprint'].split(':')[-1]].append(r)
L=['# Zakupy P09-R2 — ilości na jedną płytkę (S1)','',
'Źródło: **rejestr** = pozycja z `Zamowione/zamowione.csv` (posiadane, montaż THT na stojąco); **nowe** = do kupienia (lista zakupowa 2 do przeliczenia po decyzjach S1). Dwa moduły MAX31856 XU są posiadane (Allegro). Płytka z JLCPCB (klasa 1/3, 53 × 100 mm); tu tylko schemat.','',
'| Źródło | Nazwa | Ilość | Referencje / obudowa |','|---|---|---:|---|']
for (z,name,fp),refs in sorted(g.items()):L.append(f'| {z} | {name} | {len(refs)} | {", ".join(refs)} / {fp} |')
def n(zr,pref):return sum(1 for r,p in PARTS.items() if p['zrodlo']==zr and r.startswith(pref) and p['value'] in ('10K','100K','100n'))
L+=['','**Zapotrzebowanie na części z rejestru** (stan rejestru 24.09: MF0207 10 k — 7 szt., 100 k — 7 szt., K104K15X7RF5TH5 100 n — 5 szt.; P01 miała z tego 5 / 5 / 3, ale P01 stała się zbędna po decyzji o pakiecie 18650):','',
f'| Część | P09 R2 potrzebuje | Rejestr |','|---|---:|---:|',
f"| MF0207 10 k | {sum(1 for p in PARTS.values() if p['value']=='10K' and p['zrodlo']=='rejestr')} | 7 |",
f"| MF0207 100 k | {sum(1 for p in PARTS.values() if p['value']=='100K' and p['zrodlo']=='rejestr')} | 7 |",
f"| K104K15X7RF5TH5 100 n | {sum(1 for p in PARTS.values() if p['value']=='100n')} | 5 |",'',
'Razem z P10 R2 (3 × 10 k — R2 i dwa rezystory serwisowe CAN, 3 × 100 n): 10 k — 9 wobec 7, 100 k — 7 z 7, 100 n — 6 wobec 5 (zob. opis PR i `P10-R2-review/docs/ZAKUPY.md`).','',
'Uwagi do zakupów:',
'- J1 (J_BP): obudowane złącze kątowe IDC 2×8, raster 2,54 mm, styki Au; z płytką połączeń P12 łączy je krótka taśma IDC 2×8 (dwa gniazda zaciskowe, jedno do J_BP, drugie do P12).',
'- J2 (SERWIS): goldpin **kątowy** 1×13 (posiadana listwa 1×40 z Kamami jest prosta i nie wystarczy).',
'- J3/J4: gniazda 1×9 Au (ZL262-9SG z listy 2), JP1/JP2: listwy 1×3 i zwora (zapas), początkowo bez zworek.',
'- U1/U2 SO14 z Ioff (74LVC125AD, nie HC125), lutowane wprost do płytki (S1 dopuszcza SOIC); U3 DIP16 z podstawką opcjonalnie.',
'- Kondensatory SMD 1206 X7R 25 V ±10 %; C4/C5 po DC bias ≥ 2,2 µF, C6/C7 ≥ 0,47 µF (1206 zachowuje pojemność lepiej niż 0805).',
'- Rezystory serwisowe R20…R30: 1 kΩ 1206, od spodu płytki pod listwą (S1 §9).',
'- Termopary K z izolowaną spoiną, mocowanie nylonowe M2.5 modułów, dystanse M3 20 mm (poziom 3) — bez zmian względem R1, poza dystansem (R1 miała M3 ≥ 10 mm).']
(P/'docs/ZAKUPY.md').write_text('\n'.join(L)+'\n',encoding='utf-8');print('J_BP.csv, SERWIS.csv, ZAKUPY.md written')
