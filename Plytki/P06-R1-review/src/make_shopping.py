"""BOM of purchased parts plus complete module harness materials."""
from pathlib import Path
import json,csv,collections
P=Path(__file__).resolve().parents[1];parts=json.loads((P/'docs/parts.json').read_text(encoding='utf-8'))
group=collections.defaultdict(list)
for r,p in parts.items():
 if r.startswith(('TP','J')):continue
 group[(p['mpn'],p['footprint'].split(':')[-1])].append(r)
rows=['# Zakupy P06-R1 / jedna płytka','','Ilości netto, bez zapasu. Elementy P06 oraz SW1 na panelu. Pola J1-J5 są miejscami lutowania wiązek, a TP1-TP15 są padami PCB; nie kupować pod nie goldpinów. Rezystory są pojedyncze o pełnej wartości. Wersje 0,1%: TCR ≤25 ppm/K.','','| Nazwa / typ | Ilość szt. | Referencje / obudowa |','|---|---:|---|']
for (name,fp),refs in sorted(group.items()):rows.append(f'| {name} | {len(refs)} | {", ".join(refs)} / {fp} |')
rows += ['', 'Przy zamówieniu generycznych elementów porównać wymiary z footprintem. R6: 1 Ω / 1 W, wymagana dopuszczalna energia impulsu ≥10 mJ przy czasie około 0,5 ms, korpus ≤9,9 × 3,6 mm. Sam napis 1 W nie kwalifikuje zamiennika. R21: 39 Ω / 2 W, korpus ≤17 × 6 mm. C2: 470 pF C0G, raster 5 mm, obrys ≤5 × 3 mm. C6-C16: 100 nF X7R 0805, 50 V. C1: WIMA PET 470 nF, 63 V, 10%, raster 5 mm; wskazany MPN mieści się w obrysie 7,2 × 5 mm.', '', '## Wiązki i mechanika', '', '| Nazwa | Ilość | Długość / wtyk i uwagi |', '|---|---:|---|',
 '| W1 / LV06, kompletna wiązka | 1 szt. | 200 mm, 4 × AWG22; P06 lut PTH, drugi koniec Mini-Fit Jr żeński 4p, styki Au AWG22, pasujący do P02/J6 Molex 39-29-6048 |',
 '| W2 / ILOG, kompletna wiązka | 1 szt. | 100 mm, taśma 8 × AWG28 / 1,27 mm; P06 lut PTH, IDC żeński 2×4 / 2,54 mm Au z odciążką, pozycja 2 zaślepiona |',
 '| W3 / ISERIES, kompletna wiązka | 1 szt. | 150 mm, 2 × linka 2,5 mm²; P06 lut PTH, MSTB 2,5/4-ST-5,08, minimum 12 A; 2 tulejki 2,5 mm², pozycje 3/4 puste |',
 '| W4 / SW1-A, kompletna wiązka | 1 szt. | 100 mm, 2 × 2,5 mm²; PTH ↔ lutowane oczka S6A, koszulki |',
 '| W5 / SW1-B, kompletna wiązka | 1 szt. | 150 mm, 3 × AWG22; PTH ↔ lutowane oczka S6A, koszulki |',
 '| Opaska poliamidowa szerokości 2,5 mm | 5 szt. | po jednej na kotwę każdej wiązki |',
 '| PCB P06-R1 | 1 szt. | 120 × 100 mm, FR4 1,6 mm, 2 × 70 µm, otwory PTH i NPTH |',
 '| Dystans M3 ≥10 mm, śruba M3, podkładka | 4 kpl. | dobrać do obudowy, podkładka OD ≤8 mm; odstęp lutów od podłoża |',
 '| Podstawka DIP8 / DIP14, opcjonalnie | 2 / 1 szt. | U2/U3 oraz U7; sprawdzić wysokość pod pokrywą |',
 '', 'Wtyki na drugim końcu W1-W3 nie są dodatkowymi gniazdami na P06. Materiały zawarte w kompletnych wiązkach liczyć jeden raz. Rezerwa materiału bez zapasu montażowego: 1,25 m AWG22, 0,50 m linki 2,5 mm², 0,10 m taśmy 8-żyłowej. Kupując odcinki dodać zapas na zarobienie i próby. Dokładny model wtyku IDC oraz elementów Mini-Fit wybrać do istniejących gniazd; zachować złocenie, dopuszczalny przewód i polaryzację. P11 wymaga jeszcze zatwierdzenia mechaniki MSTB.', '', 'SW1 S6A jest już w tabeli elementów - nie zamawiać ponownie jako część wiązki. Położenie dźwigni BYPASS/MEASURE oznaczyć po sprawdzeniu styków omomierzem.']
(P/'docs/ZAKUPY.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
with (P/'docs/interfejsy.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['ID','P06','drugi_koniec','ktory_koniec_lutowany','dlugosc_mm','przewod','wtyk_drugi_koniec','kotwa_mm','piny'])
 for row in [
 ['W1/LV06','J1','P02/J6','P06',200,'4xAWG22','Mini-Fit Jr 4p Au do 39-29-6048','12','1=5V_SYS;2=GND;3=3V3_IO;4=GND'],
 ['W2/ILOG','J2','P03-R2/J2','P06',100,'8xAWG28 ribbon 1.27mm','IDC 2x4 2.54mm Au KEY2','12/14.54','1=SCLK;2=NC;3=DOUTA;4=GND;5=CS_ILOG_N;6=GND;7=READY;8=GND'],
 ['W3/ISERIES','J3','P11/J_ISERIESA (do zatwierdzenia)','P06',150,'2x2.5mm2','MSTB 2.5/4-ST-5.08 >=12A','12','1=ECU_P1;2=EGR_P1;3/4=NC'],
 ['W4/SW1-A','J4','SW1.2/3','oba',100,'2x2.5mm2','brak - lutowane oczka NKK S6A','12','1->SW1.2;2->SW1.3'],
 ['W5/SW1-B','J5','SW1.4/5/6','oba',150,'3xAWG22','brak - lutowane oczka NKK S6A','12','1->SW1.4;2->SW1.5;3->SW1.6']]:w.writerow(row)
print('Shopping list and five harness contracts written.')
