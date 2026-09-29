# Zakupy P08-R1 — jedna płytka

Ilości netto. J1–J3 to pola lutownicze wiązek, TP1–TP13 to punkty PCB — bez dodatkowych goldpinów. Wszystkie rezystory są pojedyncze, przewlekane DIN0207, 1%, 0,25 W; raster 10,16 mm.

| Nazwa / typ | Ilość szt. | Referencje / obudowa |
|---|---:|---|
| 1N4148 | 1 | D1 / D_DO-35_SOD27_P7.62mm_Horizontal |
| 74LVC125AD,118 (Nexperia) | 2 | U4, U5 / SOIC-14_3.9x8.7mm_P1.27mm |
| EEUFR1E220 | 1 | C10 / CP_Radial_D5.0mm_P2.00mm |
| G6K-2P-Y DC5 | 1 | K1 / G6K_2P_Y_verified |
| MCP120-300DI/TO | 2 | U6, U8 / TO-92_Inline_Wide |
| MCP120-450DI/TO | 1 | U7 / TO-92_Inline_Wide |
| Metal film 100R 1% 0.25W | 2 | R11, R13 / R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal |
| Metal film 10K 1% 0.25W | 13 | R2, R3, R4, R5, R6, R7, R8, R9, R10, R12, R14, R17, R18 / R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal |
| Metal film 232K 1% 0.25W | 1 | R1 / R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal |
| Metal film 4K7 1% 0.25W | 1 | R15 / R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal |
| Metal film 6K8 1% 0.25W | 1 | R16 / R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal |
| Molex 39-29-6028 | 1 | J4 / Molex_Mini-Fit_Jr_5566-02A_2x01_P4.20mm_Vertical |
| SN74HC08N | 1 | U3 / DIP-14_W7.62mm |
| TBD62083APG | 1 | U2 / DIP-18_W7.62mm |
| TPS2553DBVR | 1 | U1 / SOT-23-6 |
| X7R 25V 10% 0805 100n | 6 | C3, C4, C5, C6, C7, C8 / C_0805_2012Metric |
| X7R 25V 10% 0805 1u | 3 | C1, C2, C9 / C_0805_2012Metric |

U1: SOT-23-6, raster 0,95 mm; U4/U5: SO14, raster 1,27 mm. Lutowanie bezpośrednio do PCB. G6K-2P-Y jest przewlekany; G6K-2F-Y, G6K-2P bez Y i G6KU nie pasują do tego wykonania. U6/U7/U8 muszą mieć bondout D (RESET/VDD/GND), nie F/G/H. U8 musi być MCP120, bez wewnętrznego pull-up. Nie zamieniać TPS2553 na TPS2552, TPS2553-1 ani WSON/DRV. Kondensatory 0805: X7R, 25 V, ±10%; po uwzględnieniu DC bias C1/C2/C9 ≥0,47 µF. C10: D5 mm, raster 2 mm, wysokość do 11 mm.

| Wiązka / mechanika | Ilość | Długość / wykonanie |
|---|---:|---|
| W1 LV08 | 1 kpl. | 200 mm, 4 × AWG22; lut PTH na P08 → Mini-Fit Jr żeński 4p Au do P02/J8 |
| W2 SENSOR | 1 kpl. | 150 mm, taśma 6 × AWG28, raster 1,27 mm; lut PTH na P08 → IDC 2×3 / 2,54 mm Au, odciążka, KEY2 |
| W3 SFAULT | 1 kpl. | 150 mm, taśma 6 × AWG28, raster 1,27 mm; lut PTH na P08 → IDC 2×3 / 2,54 mm Au, odciążka, KEY3 |
| Opaska poliamidowa 2,5 mm | 3 szt. | Kotwy 12–14,54 mm od pól lutowniczych |
| PCB P08-R1 | 1 szt. | 100 × 80 mm, 2 warstwy, FR4 1,6 mm, Cu 35 µm, soldermaska, opis |
| Dystans M3 ≥10 mm + śruba + podkładka OD ≤8 mm | 4 kpl. | Dobrać do obudowy |
| Podstawka DIP14 / DIP18, opcjonalnie | 1 / 1 szt. | U3 / U2; osobno od ilości układów |

W1: przykładowa obudowa Molex 39-01-2040 i 4 styki żeńskie Au 39-00-0074 (AWG18–24). W2/W3 muszą pasować do 6-pinowych listew sąsiednich PCB, mieć złocone kontakty oraz zaślepienie właściwej pozycji. Nie używać starego SENSOR 4p. Kupując gotowe przewody, sprawdzić numerację omomierzem. Materiały wiązek liczyć raz: netto 0,8 m przewodu AWG22 i 0,30 m taśmy 6-żyłowej, plus zapas do zarobienia.

W4 TSENSOR należy do BOM przyszłej P11: 150 mm, 2 × AWG22, lut na P11 → Mini-Fit Jr żeński 2p Au do J4 P08 (obudowa 39-01-2020, 2 styki 39-00-0074). Na P08 kupujemy tylko J4, już ujęte w tabeli. Do prób samej P08 można wykonać W4 jako przewód testowy; nie zamawiać drugi raz przy P11.
