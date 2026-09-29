# Zakupy P09-R1 — ilości netto

Dwa moduły z kupionej oferty są częścią zestawu; nie zamawiać ich ponownie, jeśli już są. J1/J2 oraz TP to pola PCB, bez osobnych złączy. Wszystkie rezystory: pojedynczy DIN0207, 0,25 W, 1%, raster 10,16 mm.

| Nazwa | Ilość szt. | Referencje / obudowa |
|---|---:|---|
| 74LVC125AD,118 Nexperia | 2 | U1, U2 / SOIC-14_3.9x8.7mm_P1.27mm |
| Header 1x3 + one shunt (not fitted initially) | 2 | JP1, JP2 / PinHeader_1x03_P2.54mm_Vertical |
| Metal film 100K 1% 0.25W | 7 | R3, R4, R7, R8, R9, R10, R13 / R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal |
| Metal film 100R 1% 0.25W | 2 | R11, R12 / R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal |
| Metal film 10K 1% 0.25W | 6 | R1, R2, R5, R6, R18, R19 / R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal |
| Metal film 47R 1% 0.25W | 4 | R14, R15, R16, R17 / R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal |
| SN74HC139N | 1 | U3 / DIP-16_W7.62mm |
| Socket 1x9 2.54mm Au + owned MAX31856 module | 2 | J3, J4 / MAX31856_XU_socket |
| X7R 25V 10% 0805 100n | 3 | C1, C2, C3 / C_0805_2012Metric |
| X7R 25V 10% 0805 1u | 2 | C6, C7 / C_0805_2012Metric |
| X7R 25V 10% 0805 4u7 | 2 | C4, C5 / C_0805_2012Metric |

J3/J4: kupić łącznie 2 gniazda żeńskie 1×9 / 2,54 mm ze stykami Au; ich opis obejmuje również posiadane moduły. Listwy męskie na modułach pozostają fabryczne. Zweryfikować długość pinów i wysokość gniazd z dostarczonym egzemplarzem. JP1/JP2: 2 listwy 1×3 oraz 2 pojedyncze zwory; początkowo zwór NIE zakładać. U1/U2 SO14 z Ioff, nie HC125. U3 DIP16, opcjonalna podstawka DIP16 osobno. Kondensatory 0805 X7R 25 V ±10%; C4/C5 po DC bias ≥2,2 µF, C6/C7 ≥0,47 µF.

| Wiązka / mechanika / czujniki | Ilość | Specyfikacja |
|---|---:|---|
| W1 LV09 | 1 kpl. | 200 mm, 4×AWG22; PTH P09 → Mini-Fit Jr żeński 4p Au do P02/J9 |
| W2 TEMP | 1 kpl. | 100 mm, taśma 10×AWG28 / 1,27 mm; PTH P09 → IDC 2×5 / 2,54 mm Au, odciążka, KEY4 do P03/J7 |
| Opaska 2,5 mm | 2 szt. | Kotwa 12 mm przed pierwszym rzędem lutów |
| PCB P09-R1 | 1 szt. | 100×100 mm, 2 warstwy, FR4 1,6 mm, Cu 35 µm |
| Dystans M3 ≥10 mm + śruba + podkładka OD≤8 mm | 4 kpl. | Mocowanie nośnika w obudowie |
| Dystans nylonowy M2.5 + śruby/nakrętki + 2 podkładki OD8 mm | 4 kpl. | Podparcie modułów, wysokość dobrać do realnego gniazda; nośnik ma otwory regulacyjne Ø6 mm |
| Termopara K, izolowana spoina pomiarowa | 2 szt. | Sonda do obudowy EGR i drugi punkt odniesienia; zakres dobrany do miejsca montażu |

W1 przykładowo obudowa Molex 39-01-2040 + 4 żeńskie styki Au 39-00-0074 (AWG18–24), pasujące do P02/J9. Materiały wiązek liczyć raz: netto 0,8 m przewodu AWG22 i 0,10 m taśmy 10-żyłowej plus zapas do zarobienia. Właściciel BOM obu wiązek: P09. W2 raster żył 1,27 mm, raster styków 2,54 mm. Żyłę4 zakończyć i zaizolować na końcu P09; pole4 pozostaje NC. Nie wykonywać zastępczego kabla odwracającego numerację.
