"""Net purchasing quantities and harness ownership for one P10."""
from pathlib import Path
import json,csv,collections
P=Path(__file__).resolve().parents[1];parts=json.loads((P/'docs/parts.json').read_text());g=collections.defaultdict(list)
for r,p in parts.items():
 if r.startswith(('TP','J')):continue
 g[p['mpn'],p['footprint'].split(':')[-1]].append(r)
rows=['# Zakupy P10-R1 — ilości netto','','J1/J2/J3 i TP są polami PCB, bez osobnych gniazd. Jedna płytka: 10 montowanych elementów elektronicznych + trzy wiązki.','','| Nazwa | Ilość szt. | Referencje / obudowa |','|---|---:|---|']
for (name,fp),refs in sorted(g.items()):rows.append(f'| {name} | {len(refs)} | {", ".join(refs)} / {fp} |')
rows+=['','U1 koniecznie wariant **V** z VIO na pinie5: TCAN1051VDRQ1, SOIC8. U2 Nexperia 74LVC125AD,118 z Ioff, SO14; HC125 nie jest zamiennikiem. D1 PESD2CAN,215, SOT23. Rezystory pojedyncze THT DIN0207 0,25 W, 1%, raster10,16 mm. Kondensatory 0805 X7R 25 V ±10%; C4/C5 efektywna pojemność przy napięciu roboczym ≥2,2 µF. Nie kupować terminatora CAN do montażu na P10.','','| Wiązka / mechanika | Ilość | Specyfikacja |','|---|---:|---|',
'| W1 LV10 | 1 kpl. | 200 mm, 4×AWG22; lut PTH P10 → Mini-Fit Jr żeński 4p Au do P02-R3/J10 |',
'| W2 CORE CAN | 1 kpl. | 150 mm, 6×AWG28 taśma raster żył1,27 mm; PTH → IDC2×3 raster styków2,54 mm Au, odciążka, KEY4 do P03-R2/J8 |',
'| W3 OBD CAN | 1 kpl. | 300 mm całkowitej długości od lutów do styków OBD; skrętka CAN120 Ω 2×AWG24; PTH → wtyk OBD-II męski TypeA 16p z obudową, obsadzone wyłącznie6/14 |',
'| Opaska nylonowa 2,5 mm | 3 szt. | Kotwy PTH wiązek, 12 mm przed pierwszym rzędem |',
'| PCB P10-R1 | 1 szt. | 80×70 mm, FR4 1,6 mm, 2 warstwy Cu35 µm |',
'| Dystans M3 ≥10 mm + śruba + podkładka OD≤8 mm | 4 kpl. | Mocowanie PCB w obudowie |',
'','W1: przykładowo Molex39-01-2040 +4 styki żeńskie Au39-00-0074 dla AWG18–24, do istniejącego P02/J10. W2: gniazdo zaciskowe IDC6 i odciążka oraz zaślepka pozycji4; nie zamieniać na kabel 10p z wcześniejszych kart. W3: użyć kabla o deklarowanej impedancji120 Ω i izolacji do instalacji samochodowej. Wtyk/obudowa ma obejmę kabla; numerację styków sprawdzić miernikiem. Jeśli kabel ekranowany, ekran zaizolować na obu końcach w tym wariancie.','','Materiały liczyć raz, w BOM P10: 0,80 m AWG22, 0,15 m taśmy6p, 0,30 m pary CAN plus zapas do zarobienia. Żyły4/5/6 W2 zaizolować na końcu P10; nie lutować do innych sygnałów. Zaślepka KEY4 we wtyku do P03. OBD4/5/16 i pozostałe piny pozostają NC. Masa robocza pochodzi z P01/P02 — wymagany wspólny punkt odniesienia z pojazdem.']
(P/'docs/ZAKUPY.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
with (P/'docs/interfejsy.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['ID','P10','drugi_koniec','ktory_koniec_lutowany','dlugosc_mm','przewod','wtyk','kotwa_mm','piny','wlasciciel_BOM'])
 w.writerow(['W1/LV10','J1','P02-R3/J10','P10',200,'4xAWG22','Mini-Fit Jr 4p Au',12,'1=5V_SYS;2=GND;3=3V3_IO;4=GND','P10'])
 w.writerow(['W2/CORE CAN','J2','P03-R2/J8','P10',150,'6xAWG28 ribbon1.27mm','IDC6 Au KEY4','12/14.54','1=TX->TP6 only;2=GND;3=RX;4=NC/KEY;5=NC;6=NC','P10'])
 w.writerow(['W3/OBD CAN','J3','OBD male TypeA pins6/14','P10',300,'120ohm twisted pair2xAWG24','OBD male16p; populated6/14',12,'J3.1=H->6;J3.2=L->14;all other OBD pins NC','P10'])
print('P10 BOM and three harnesses written')
