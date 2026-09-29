"""Net quantities and harness contracts for one P08 board. J1-J3 are solder fields."""
from pathlib import Path
import json,csv,collections
P=Path(__file__).resolve().parents[1];parts=json.loads((P/'docs/parts.json').read_text(encoding='utf-8'))
group=collections.defaultdict(list)
for r,p in parts.items():
 if r.startswith('TP') or r in ['J1','J2','J3']:continue
 group[(p['mpn'],p['footprint'].split(':')[-1])].append(r)
rows=['# Zakupy P08-R1 — jedna płytka','','Ilości netto. J1–J3 to pola lutownicze wiązek, TP1–TP13 to punkty PCB — bez dodatkowych goldpinów. Wszystkie rezystory są pojedyncze, przewlekane DIN0207, 1%, 0,25 W; raster 10,16 mm.','','| Nazwa / typ | Ilość szt. | Referencje / obudowa |','|---|---:|---|']
for (name,fp),refs in sorted(group.items()):rows.append(f'| {name} | {len(refs)} | {", ".join(refs)} / {fp} |')
rows+=['','U1: SOT-23-6, raster 0,95 mm; U4/U5: SO14, raster 1,27 mm. Lutowanie bezpośrednio do PCB. G6K-2P-Y jest przewlekany; G6K-2F-Y, G6K-2P bez Y i G6KU nie pasują do tego wykonania. U6/U7/U8 muszą mieć bondout D (RESET/VDD/GND), nie F/G/H. U8 musi być MCP120, bez wewnętrznego pull-up. Nie zamieniać TPS2553 na TPS2552, TPS2553-1 ani WSON/DRV. Kondensatory 0805: X7R, 25 V, ±10%; po uwzględnieniu DC bias C1/C2/C9 ≥0,47 µF. C10: D5 mm, raster 2 mm, wysokość do 11 mm.','','| Wiązka / mechanika | Ilość | Długość / wykonanie |','|---|---:|---|',
'| W1 LV08 | 1 kpl. | 200 mm, 4 × AWG22; lut PTH na P08 → Mini-Fit Jr żeński 4p Au do P02/J8 |',
'| W2 SENSOR | 1 kpl. | 150 mm, taśma 6 × AWG28, raster 1,27 mm; lut PTH na P08 → IDC 2×3 / 2,54 mm Au, odciążka, KEY2 |',
'| W3 SFAULT | 1 kpl. | 150 mm, taśma 6 × AWG28, raster 1,27 mm; lut PTH na P08 → IDC 2×3 / 2,54 mm Au, odciążka, KEY3 |',
'| Opaska poliamidowa 2,5 mm | 3 szt. | Kotwy 12–14,54 mm od pól lutowniczych |',
'| PCB P08-R1 | 1 szt. | 100 × 80 mm, 2 warstwy, FR4 1,6 mm, Cu 35 µm, soldermaska, opis |',
'| Dystans M3 ≥10 mm + śruba + podkładka OD ≤8 mm | 4 kpl. | Dobrać do obudowy |',
'| Podstawka DIP14 / DIP18, opcjonalnie | 1 / 1 szt. | U3 / U2; osobno od ilości układów |',
'','W1: przykładowa obudowa Molex 39-01-2040 i 4 styki żeńskie Au 39-00-0074 (AWG18–24). W2/W3 muszą pasować do 6-pinowych listew sąsiednich PCB, mieć złocone kontakty oraz zaślepienie właściwej pozycji. Nie używać starego SENSOR 4p. Kupując gotowe przewody, sprawdzić numerację omomierzem. Materiały wiązek liczyć raz: netto 0,8 m przewodu AWG22 i 0,30 m taśmy 6-żyłowej, plus zapas do zarobienia.','','W4 TSENSOR należy do BOM przyszłej P11: 150 mm, 2 × AWG22, lut na P11 → Mini-Fit Jr żeński 2p Au do J4 P08 (obudowa 39-01-2020, 2 styki 39-00-0074). Na P08 kupujemy tylko J4, już ujęte w tabeli. Do prób samej P08 można wykonać W4 jako przewód testowy; nie zamawiać drugi raz przy P11.']
(P/'docs/ZAKUPY.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
with (P/'docs/interfejsy.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['ID','P08','drugi_koniec','ktory_koniec_lutowany','dlugosc_mm','przewod','wtyk','kotwa_mm','piny','wlasciciel_BOM'])
 for row in [
 ['W1/LV08','J1','P02-R3/J8','P08',200,'4xAWG22','Mini-Fit Jr 4p Au','12','1=5V_SYS;2=GND;3=3V3_IO;4=GND','P08'],
 ['W2/SENSOR','J2','P04-R2.1/J4','P08',150,'6xAWG28 ribbon 1.27mm','IDC6 Au KEY2','12/14.54','1=SENSOR_PERMIT;2=NC/KEY;3=SENSOR_OK;4=GND;5/6=NC','P08'],
 ['W3/SFAULT','J3','P03-R2/J6','P08',150,'6xAWG28 ribbon 1.27mm','IDC6 Au KEY3','12/14.54','1=SENSOR_HEALTHY;2=GND;3=NC/KEY;4/5/6=NC','P08'],
 ['W4/TSENSOR','J4','P11/J_TSENSORB (przyszla plytka)','P11',150,'2xAWG22','Mini-Fit Jr 2p Au przy P08','P11:12 docelowo','1=5V_SENSOR;2=AGND_SENSOR','P11; na P08 tylko J4']]:w.writerow(row)
print('Shopping list and four harness contracts generated')
