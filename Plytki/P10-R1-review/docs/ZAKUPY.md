# Zakupy P10-R1 — ilości netto

J1/J2/J3 i TP są polami PCB, bez osobnych gniazd. Jedna płytka: 10 montowanych elementów elektronicznych + trzy wiązki.

| Nazwa | Ilość szt. | Referencje / obudowa |
|---|---:|---|
| 74LVC125AD,118 Nexperia | 1 | U2 / SOIC-14_3.9x8.7mm_P1.27mm |
| Metal film 100R 1% 0.25W | 1 | R1 / R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal |
| Metal film 10K 1% 0.25W | 1 | R2 / R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal |
| PESD2CAN,215 Nexperia | 1 | D1 / SOT-23 |
| TCAN1051VDRQ1 | 1 | U1 / SOIC-8_3.9x4.9mm_P1.27mm |
| X7R 25V 10% 0805 100n | 3 | C1, C2, C3 / C_0805_2012Metric |
| X7R 25V 10% 0805 4u7 | 2 | C4, C5 / C_0805_2012Metric |

U1 koniecznie wariant **V** z VIO na pinie5: TCAN1051VDRQ1, SOIC8. U2 Nexperia 74LVC125AD,118 z Ioff, SO14; HC125 nie jest zamiennikiem. D1 PESD2CAN,215, SOT23. Rezystory pojedyncze THT DIN0207 0,25 W, 1%, raster10,16 mm. Kondensatory 0805 X7R 25 V ±10%; C4/C5 efektywna pojemność przy napięciu roboczym ≥2,2 µF. Nie kupować terminatora CAN do montażu na P10.

| Wiązka / mechanika | Ilość | Specyfikacja |
|---|---:|---|
| W1 LV10 | 1 kpl. | 200 mm, 4×AWG22; lut PTH P10 → Mini-Fit Jr żeński 4p Au do P02-R3/J10 |
| W2 CORE CAN | 1 kpl. | 150 mm, 6×AWG28 taśma raster żył1,27 mm; PTH → IDC2×3 raster styków2,54 mm Au, odciążka, KEY4 do P03-R2/J8 |
| W3 OBD CAN | 1 kpl. | 300 mm całkowitej długości od lutów do styków OBD; skrętka CAN120 Ω 2×AWG24; PTH → wtyk OBD-II męski TypeA 16p z obudową, obsadzone wyłącznie6/14 |
| Opaska nylonowa 2,5 mm | 3 szt. | Kotwy PTH wiązek, 12 mm przed pierwszym rzędem |
| PCB P10-R1 | 1 szt. | 80×70 mm, FR4 1,6 mm, 2 warstwy Cu35 µm |
| Dystans M3 ≥10 mm + śruba + podkładka OD≤8 mm | 4 kpl. | Mocowanie PCB w obudowie |

W1: przykładowo Molex39-01-2040 +4 styki żeńskie Au39-00-0074 dla AWG18–24, do istniejącego P02/J10. W2: gniazdo zaciskowe IDC6 i odciążka oraz zaślepka pozycji4; nie zamieniać na kabel 10p z wcześniejszych kart. W3: użyć kabla o deklarowanej impedancji120 Ω i izolacji do instalacji samochodowej. Wtyk/obudowa ma obejmę kabla; numerację styków sprawdzić miernikiem. Jeśli kabel ekranowany, ekran zaizolować na obu końcach w tym wariancie.

Materiały liczyć raz, w BOM P10: 0,80 m AWG22, 0,15 m taśmy6p, 0,30 m pary CAN plus zapas do zarobienia. Żyły4/5/6 W2 zaizolować na końcu P10; nie lutować do innych sygnałów. Zaślepka KEY4 we wtyku do P03. OBD4/5/16 i pozostałe piny pozostają NC. Masa robocza pochodzi z P01/P02 — wymagany wspólny punkt odniesienia z pojazdem.
