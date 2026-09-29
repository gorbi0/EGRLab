"""Net BOM and soldered-harness ownership for one P09."""
from pathlib import Path
import json,csv,collections
P=Path(__file__).resolve().parents[1];parts=json.loads((P/'docs/parts.json').read_text());g=collections.defaultdict(list)
for r,p in parts.items():
 if r.startswith('TP') or r in ['J1','J2']:continue
 g[p['mpn'],p['footprint'].split(':')[-1]].append(r)
rows=['# Zakupy P09-R1 — ilości netto','','Dwa moduły z kupionej oferty są częścią zestawu; nie zamawiać ich ponownie, jeśli już są. J1/J2 oraz TP to pola PCB, bez osobnych złączy. Wszystkie rezystory: pojedynczy DIN0207, 0,25 W, 1%, raster 10,16 mm.','','| Nazwa | Ilość szt. | Referencje / obudowa |','|---|---:|---|']
for (name,fp),refs in sorted(g.items()):rows.append(f'| {name} | {len(refs)} | {", ".join(refs)} / {fp} |')
rows+=['','J3/J4: kupić łącznie 2 gniazda żeńskie 1×9 / 2,54 mm ze stykami Au; ich opis obejmuje również posiadane moduły. Listwy męskie na modułach pozostają fabryczne. Zweryfikować długość pinów i wysokość gniazd z dostarczonym egzemplarzem. JP1/JP2: 2 listwy 1×3 oraz 2 pojedyncze zwory; początkowo zwór NIE zakładać. U1/U2 SO14 z Ioff, nie HC125. U3 DIP16, opcjonalna podstawka DIP16 osobno. Kondensatory 0805 X7R 25 V ±10%; C4/C5 po DC bias ≥2,2 µF, C6/C7 ≥0,47 µF.','','| Wiązka / mechanika / czujniki | Ilość | Specyfikacja |','|---|---:|---|',
'| W1 LV09 | 1 kpl. | 200 mm, 4×AWG22; PTH P09 → Mini-Fit Jr żeński 4p Au do P02/J9 |',
'| W2 TEMP | 1 kpl. | 100 mm, taśma 10×AWG28 / 1,27 mm; PTH P09 → IDC 2×5 / 2,54 mm Au, odciążka, KEY4 do P03/J7 |',
'| Opaska 2,5 mm | 2 szt. | Kotwa 12 mm przed pierwszym rzędem lutów |',
'| PCB P09-R1 | 1 szt. | 100×100 mm, 2 warstwy, FR4 1,6 mm, Cu 35 µm |',
'| Dystans M3 ≥10 mm + śruba + podkładka OD≤8 mm | 4 kpl. | Mocowanie nośnika w obudowie |',
'| Dystans nylonowy M2.5 + śruby/nakrętki + 2 podkładki OD8 mm | 4 kpl. | Podparcie modułów, wysokość dobrać do realnego gniazda; nośnik ma otwory regulacyjne Ø6 mm |',
'| Termopara K, izolowana spoina pomiarowa | 2 szt. | Sonda do obudowy EGR i drugi punkt odniesienia; zakres dobrany do miejsca montażu |',
'','W1 przykładowo obudowa Molex 39-01-2040 + 4 żeńskie styki Au 39-00-0074 (AWG18–24), pasujące do P02/J9. Materiały wiązek liczyć raz: netto 0,8 m przewodu AWG22 i 0,10 m taśmy 10-żyłowej plus zapas do zarobienia. Właściciel BOM obu wiązek: P09. W2 raster żył 1,27 mm, raster styków 2,54 mm. Żyłę4 zakończyć i zaizolować na końcu P09; pole4 pozostaje NC. Nie wykonywać zastępczego kabla odwracającego numerację.']
(P/'docs/ZAKUPY.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
with (P/'docs/interfejsy.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['ID','P09','drugi_koniec','ktory_koniec_lutowany','dlugosc_mm','przewod','wtyk','kotwa_mm','piny','wlasciciel_BOM'])
 w.writerow(['W1/LV09','J1','P02-R3/J9','P09',200,'4xAWG22','Mini-Fit Jr 4p Au',12,'1=5V_SYS;2=GND;3=3V3_IO;4=GND','P09'])
 w.writerow(['W2/TEMP','J2','P03-R2/J7','P09',100,'10xAWG28 ribbon 1.27mm','IDC10 Au KEY4','12/14.54','1=SCLK;2=GND;3=MOSI;4=NC/KEY;5=MISO;6=GND;7=TC1_CS;8=GND;9=TC2_CS;10=GND','P09'])
print('BOM and harness contracts written')
