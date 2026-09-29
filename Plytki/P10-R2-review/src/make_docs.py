"""Contracts for the P12 connection board (docs/J_BP.csv, docs/SERWIS.csv) and the net purchase list, all from parts.py (single source)."""
from parts import *
import collections
def w(name,head,rows):
 with (P/'docs'/name).open('w',newline='',encoding='utf-8-sig') as f:
  x=csv.writer(f,delimiter=';');x.writerow(head);x.writerows(rows)
rows=[]
for p in range(1,11):
 if p%2:rows.append([p,'GND','masa','wszystkie (P12)','powrót sygnału; piny nieparzyste zawsze GND'])
 else:
  n,kier,cel,uw=next((n,k,c,u) for pp,n,k,c,u in JBP if pp==p);rows.append([p,n,kier,cel,uw])
w('J_BP.csv',['pin','siec','kierunek','plytka_docelowa','uwagi'],rows)
last=len(SRV)+2
w('SERWIS.csv',['pin','siec','rezystor','cel_pomiaru'],
  [[1,'GND','—','masa sondy (pierwszy pin listwy)']]+[[k,net,f"{srv_r[net]} {'1' if o==1000 else '10'} kΩ",cel] for k,(net,o,cel) in enumerate(SRV,2)]+[[last,'GND','—','masa sondy (ostatni pin listwy)']])
g=collections.defaultdict(list)
for r,p in PARTS.items():g[p['zrodlo'],p['mpn'],p['footprint'].split(':')[-1]].append(r)
n10=sum(1 for p in PARTS.values() if p['value']=='10K' and p['zrodlo']=='rejestr');n100=sum(1 for p in PARTS.values() if p['value']=='100n')
L=['# Zakupy P10-R2 — ilości na jedną płytkę (S1)','',
'Źródło: **rejestr** = pozycja z `Zamowione/zamowione.csv` (posiadane; rezystory MF0207 i kondensatory radialne montowane na stojąco, 74LVC125AD z zamówienia P10); **nowe** = do kupienia (lista zakupowa 2 do przeliczenia po decyzjach S1). Płytka z JLCPCB (klasa 1/3, 53 × 100 mm); tu tylko schemat.','',
'| Źródło | Nazwa | Ilość | Referencje / obudowa |','|---|---|---:|---|']
for (z,name,fp),refs in sorted(g.items()):L.append(f'| {z} | {name} | {len(refs)} | {", ".join(refs)} / {fp} |')
L+=['','**Części z rejestru, o które konkuruje P09** (stan rejestru 24.09: MF0207 10 k — 7 szt., K104K15X7RF5TH5 100 n — 5 szt.):','',
'| Część | P10 R2 | P09 R2 | Razem | Rejestr |','|---|---:|---:|---:|---:|',
f'| MF0207 10 k | {n10} (R2, R8, R9 — dwa ostatnie to rezystory serwisowe CAN_H/CAN_L) | 6 | {n10+6} | 7 |',
f'| K104K15X7RF5TH5 100 n | {n100} | 3 | {n100+3} | 5 |','',
'Oba pakiety razem przekraczają rejestr: 10 k o dwie sztuki, 100 n o jedną (decyzja użytkownika w opisie PR).','',
'Uwagi do zakupów:',
'- U1 koniecznie wariant **V** (VIO na pinie 5): TCAN1051VDRQ1, SOIC-8; U2 Nexperia 74LVC125AD,118 z Ioff (HC125 nie jest zamiennikiem); D1 PESD2CAN,215, SOT-23. Nie kupować terminatora CAN do montażu na P10.',
'- J1 (J_BP): obudowane złącze kątowe IDC 2×5, raster 2,54 mm, styki Au; taśma IDC 2×5 do P12 (dwa gniazda zaciskowe).',
'- J2 (SERWIS): goldpin **kątowy** 1×9 (posiadana listwa 1×40 z Kamami jest prosta).',
'- Kondensatory SMD 1206 X7R 25 V ±10 %; C4/C5 po DC bias ≥ 2,2 µF.',
'- Rezystory serwisowe 1 kΩ 1206 (R3–R7), od spodu płytki pod listwą (S1 §9); CAN_H/CAN_L przez 10 kΩ (R8, R9, MF0207 z rejestru).',
'- W3 OBD CAN (jedyna wiązka, która została): 300 mm skrętka CAN 120 Ω (LAPP UNITRONIC BUS CAN z listy 2), wtyk OBD-II męski typ A 16p z obudową, obsadzone tylko 6/14; opaski nylonowe 2,5 mm na kotwę J3 — bez zmian względem R1 (`P10-R1-review/docs/WIAZKI.md`, W3).',
'- W1 (LV10) i W2 (CORE CAN) z R1 znikają: zastępuje je J_BP i płytka połączeń P12.']
(P/'docs/ZAKUPY.md').write_text('\n'.join(L)+'\n',encoding='utf-8')
with (P/'docs/interfejsy.csv').open('w',newline='',encoding='utf-8-sig') as f:
 x=csv.writer(f,delimiter=';');x.writerow(['ID','P10','drugi_koniec','ktory_koniec_lutowany','dlugosc_mm','przewod','wtyk','kotwa_mm','piny','wlasciciel_BOM'])
 x.writerow(['W3/OBD CAN','J3','OBD male TypeA pins6/14','P10',300,'120ohm twisted pair 2xAWG24','OBD male 16p; populated 6/14',12,'J3.1=H->6;J3.2=L->14;all other OBD pins NC','P10'])
print('J_BP.csv, SERWIS.csv, ZAKUPY.md, interfejsy.csv written')
