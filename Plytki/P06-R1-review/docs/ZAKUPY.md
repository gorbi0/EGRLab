# Zakupy P06-R1 / jedna płytka

Ilości netto, bez zapasu. Elementy P06 oraz SW1 na panelu. Pola J1-J5 są miejscami lutowania wiązek, a TP1-TP15 są padami PCB; nie kupować pod nie goldpinów. Rezystory są pojedyncze o pełnej wartości. Wersje 0,1%: TCR ≤25 ppm/K.

| Nazwa / typ | Ilość szt. | Referencje / obudowa |
|---|---:|---|
| 1N5819 | 1 | D1 / D_DO-41_SOD81_P10.16mm_Horizontal |
| 74LVC125AD,118 (Nexperia) | 2 | U5, U6 / SOIC-14_3.9x8.7mm_P1.27mm |
| BAT85,133 (Nexperia) | 1 | D2 / D_DO-35_SOD27_P7.62mm_Horizontal |
| C0G 50V 5% 470p / C0G | 1 | C2 / C_Vishay_K15_H5_P5 |
| EEUFR1C471 | 1 | C3 / CP_Radial_D8.0mm_P3.50mm |
| EEUFR1H4R7 | 2 | C4, C5 / CP_Radial_D5.0mm_P2.00mm |
| INA240A2EDRQ1 | 1 | U1 / SOIC-8_3.9x4.9mm_P1.27mm |
| MCP120-300DI/TO | 1 | U8 / TO-92_Inline_Wide |
| MCP120-450DI/TO | 1 | U9 / TO-92_Inline_Wide |
| MCP1525-I/TO | 1 | U10 / TO-92_Inline_Wide |
| MCP1702-3302E/TO | 1 | U4 / TO-92_Inline_Wide |
| MCP3201-BI/P | 1 | U3 / DIP-8_W7.62mm |
| MCP6022-I/P | 1 | U2 / DIP-8_W7.62mm |
| MKS2C034701C00KSSD | 1 | C1 / C_Rect_L7.2mm_W5.0mm_P5.00mm |
| Metal film 100K 1% 0.25W | 3 | R8, R10, R23 / R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal |
| Metal film 100R 1% 0.25W | 1 | R19 / R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal |
| Metal film 10K 1% 0.25W | 9 | R7, R9, R13, R14, R15, R16, R17, R18, R20 / R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal |
| Metal film 10R 0.1% 0.25W | 2 | R1, R2 / R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal |
| Metal film 1K 1% 0.25W | 2 | R22, R24 / R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal |
| Metal film 1R 1% 1W | 1 | R6 / R_Axial_DIN0411_L9.9mm_D3.6mm_P15.24mm_Horizontal |
| Metal film 39R 1% 2W | 1 | R21 / R_Axial_DIN0617_L17.0mm_D6.0mm_P25.40mm_Horizontal |
| Metal film 47K 1% 0.25W | 1 | R11 / R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal |
| Metal film 47R 1% 0.25W | 2 | R5, R12 / R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal |
| Metal film 5K1 0.1% 0.25W | 2 | R3, R4 / R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal |
| PBV-R005-F1-0.5 | 1 | RSH1 / PBV_2317_F1 |
| S6A (NKK) | 1 | SW1 / OFFBOARD |
| SN74HC08N | 1 | U7 / DIP-14_W7.62mm |
| X7R 50V 10% 100n | 11 | C16, C6, C7, C8, C9, C10, C11, C12, C13, C14, C15 / C_0805_2012Metric |

Przy zamówieniu generycznych elementów porównać wymiary z footprintem. R6: 1 Ω / 1 W, wymagana dopuszczalna energia impulsu ≥10 mJ przy czasie około 0,5 ms, korpus ≤9,9 × 3,6 mm. Sam napis 1 W nie kwalifikuje zamiennika. R21: 39 Ω / 2 W, korpus ≤17 × 6 mm. C2: 470 pF C0G, raster 5 mm, obrys ≤5 × 3 mm. C6-C16: 100 nF X7R 0805, 50 V. C1: WIMA PET 470 nF, 63 V, 10%, raster 5 mm; wskazany MPN mieści się w obrysie 7,2 × 5 mm.

## Wiązki i mechanika

| Nazwa | Ilość | Długość / wtyk i uwagi |
|---|---:|---|
| W1 / LV06, kompletna wiązka | 1 szt. | 200 mm, 4 × AWG22; P06 lut PTH, drugi koniec Mini-Fit Jr żeński 4p, styki Au AWG22, pasujący do P02/J6 Molex 39-29-6048 |
| W2 / ILOG, kompletna wiązka | 1 szt. | 100 mm, taśma 8 × AWG28 / 1,27 mm; P06 lut PTH, IDC żeński 2×4 / 2,54 mm Au z odciążką, pozycja 2 zaślepiona |
| W3 / ISERIES, kompletna wiązka | 1 szt. | 150 mm, 2 × linka 2,5 mm²; P06 lut PTH, MSTB 2,5/4-ST-5,08, minimum 12 A; 2 tulejki 2,5 mm², pozycje 3/4 puste |
| W4 / SW1-A, kompletna wiązka | 1 szt. | 100 mm, 2 × 2,5 mm²; PTH ↔ lutowane oczka S6A, koszulki |
| W5 / SW1-B, kompletna wiązka | 1 szt. | 150 mm, 3 × AWG22; PTH ↔ lutowane oczka S6A, koszulki |
| Opaska poliamidowa szerokości 2,5 mm | 5 szt. | po jednej na kotwę każdej wiązki |
| PCB P06-R1 | 1 szt. | 120 × 100 mm, FR4 1,6 mm, 2 × 70 µm, otwory PTH i NPTH |
| Dystans M3 ≥10 mm, śruba M3, podkładka | 4 kpl. | dobrać do obudowy, podkładka OD ≤8 mm; odstęp lutów od podłoża |
| Podstawka DIP8 / DIP14, opcjonalnie | 2 / 1 szt. | U2/U3 oraz U7; sprawdzić wysokość pod pokrywą |

Wtyki na drugim końcu W1-W3 nie są dodatkowymi gniazdami na P06. Materiały zawarte w kompletnych wiązkach liczyć jeden raz. Rezerwa materiału bez zapasu montażowego: 1,25 m AWG22, 0,50 m linki 2,5 mm², 0,10 m taśmy 8-żyłowej. Kupując odcinki dodać zapas na zarobienie i próby. Dokładny model wtyku IDC oraz elementów Mini-Fit wybrać do istniejących gniazd; zachować złocenie, dopuszczalny przewód i polaryzację. P11 wymaga jeszcze zatwierdzenia mechaniki MSTB.

SW1 S6A jest już w tabeli elementów - nie zamawiać ponownie jako część wiązki. Położenie dźwigni BYPASS/MEASURE oznaczyć po sprawdzeniu styków omomierzem.
