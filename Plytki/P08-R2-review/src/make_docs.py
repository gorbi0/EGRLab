"""Contracts for the P12 connection board (docs/J_BP.csv), the service strip (docs/SERWIS.csv), the remaining wire (docs/interfejsy.csv) and the
net purchase list (docs/ZAKUPY.md), all from parts.py (single source)."""
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
last=len(SRV)+2
w('SERWIS.csv',['pin','siec','rezystor','cel_pomiaru'],
  [[1,'GND','—','masa sondy (pierwszy pin listwy)']]+[[k,net,f"{srv_r[net]} {'1' if o==1000 else '10'} kΩ",cel] for k,(net,o,cel) in enumerate(SRV,2)]+[[last,'GND','—','masa sondy (ostatni pin listwy)']])
with (P/'docs/interfejsy.csv').open('w',newline='',encoding='utf-8-sig') as f:
 x=csv.writer(f,delimiter=';');x.writerow(['ID','P08','drugi_koniec','ktory_koniec_lutowany','dlugosc_mm','przewod','wtyk','kotwa_mm','piny','wlasciciel_BOM'])
 x.writerow(['W4/TSENSOR','J4','port TEST na panelu (P11 / panel S1)','oba (P08: PTH J4; panel: wg projektu portu TEST)','do makiety','2xAWG22 skręcone','—',12,'1=5V_SENSOR;2=AGND_SENSOR','P08 (przewód); port TEST: panel'])
g=collections.defaultdict(list)
for r,p in PARTS.items():g[p['zrodlo'],p['mpn'],p['footprint'].split(':')[-1]].append(r)
L=['# Zakupy P08-R2 — ilości na jedną płytkę (S1)','',
'Źródło: **rejestr** = pozycja z `Zamowione/zamowione.csv` (posiadane; przydział P08 z zamówień 24.09 albo zapas po P02 R4, P05 R3, P06 R2, P09 R2, P10 R2); **nowe** = do kupienia. Płytka z JLCPCB (klasa 1/3, 53 × 100 mm, slot S1 poziomu 5). Schemat bez PCB.','',
'| Źródło | Nazwa | Ilość | Referencje / obudowa |','|---|---|---:|---|']
for (z,name,fp),refs in sorted(g.items()):L.append(f'| {z} | {name} | {len(refs)} | {", ".join(refs)} / {fp} |')
L+=['','## Bilans części posiadanych, które bierze P08','',
'| Część z rejestru | Rejestr | Zużycie innych płytek (BOM-y S1) | Zostaje | P08 R2 bierze | Uwagi |','|---|---:|---|---:|---:|---|',
'| MF0207FTE-4K7 | 6 | P02 R4: 3, P05 R3: 1 | 2 | 1 | R15 (dzielnik EN), na stojąco |',
'| MF0204FTE52-6K8 | 2 | P02 R4: 1 | 1 | 1 | R16 (dzielnik EN), na stojąco, raster 2,54 mm — ostatnia sztuka |',
'| MCP120-300DI/TO (Mouser, 4 szt.: P02, P05, P06, P08) | 4 | P02 R4: 1, P05 R3: 1, P06 R2: 1 | 1 | 1 | U6; **U8 (MCP120-300) nowy** — R1 dodała drugi nadzorca 3,3 V, którego zamówienie z 24.09 nie obejmowało |',
'| MCP120-450DI/TO (TME 2 + Mouser 3) | 5 | P02 R4: 2, P05 R3: 1, P06 R2: 1 | 1 | 1 | U7 |',
'| SN74HC08N + podstawka DIP14 (Kamami 648) | 8 / 10 | P02 R4, P05 R3, P06 R2: po 1; P04 (R2.2): 4 | 1 | 1 | U3 w podstawce |',
'| 74LVC125AD,118 (Nexperia) | 25 | 17 (szkic listy 3) + P04: 3 | 5 | 2 | U4, U5; SOIC lutowane wprost od góry (poziom 5: od spodu bez SOIC) |',
'| 1N4148 (Kamami 1187768) | 10 | P05 R3: 3 | 7 | 1 | D1 |','',
'MF0207 10 k / 100 k i K104K15X7RF5TH5 100 n nie mają zapasu (zużywają je P02 R4, P09 R2, P10 R2), więc wszystkie 10 k i 100 n P08 są nowe 1206. Dwa EEUFR1H220 z rejestru bierze P02 R4 — C10 jest nowy. Bilans wiążący: lista zakupowa 3/4 (przydział także względem równoległej P04 R3).','',
'Uwagi do zakupów:',
'- U1 TPS2553**DBVR** (aktywny wysoki EN, stałe ograniczenie; TPS2552 i TPS2553-1 nie są zamiennikami), SOT-23-6 od góry. Adapter SOT-23-6 niepotrzebny (płytka z fabryki).',
'- U2 TBD62083APG (DIP18; nie ULN2803), K1 Omron **G6K-2P-Y DC5** (monostabilny; nie G6KU).',
'- R1 232 kΩ 1 % 1206 (limit prądu TPS: 99–139 mA obliczeniowo).',
'- J1 (J_BP): obudowane złącze kątowe IDC 2×8, raster 2,54 mm, styki Au (ten sam typ co J1 P09 R2); taśma IDC 2×8 do P12 (dwa gniazda zaciskowe).',
'- J2 (SERWIS): goldpin **kątowy** 1×13 (posiadana listwa 1×40 jest prosta).',
'- J4 (TSENSOR): bez złącza na płytce — 2 × AWG22 lutowane w PTH, opaska nylonowa 2,5 mm na kotwę; długość do portu TEST z makiety panelu.',
'- Z wersji R1 znikają: Molex 39-29-6028 (Mini-Fit 2p), wiązki W1 LV08 (Mini-Fit 4p), W2 SENSOR i W3 SFAULT (taśmy IDC6), adaptery Kamami SO14/SOT-23 z przydziału P08, rezystory DIN0207 leżące, kondensatory 0805.']
(P/'docs/ZAKUPY.md').write_text('\n'.join(L)+'\n',encoding='utf-8')
print('J_BP.csv, SERWIS.csv, interfejsy.csv, ZAKUPY.md written')
