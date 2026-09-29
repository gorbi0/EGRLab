# Zakupy P09-R2 — ilości na jedną płytkę (S1)

Źródło: **rejestr** = pozycja z `Zamowione/zamowione.csv` (posiadane, montaż THT na stojąco); **nowe** = do kupienia (lista zakupowa 2 do przeliczenia po decyzjach S1). Dwa moduły MAX31856 XU są posiadane (Allegro). Płytka z JLCPCB (klasa 1/3, 53 × 100 mm); tu tylko schemat.

| Źródło | Nazwa | Ilość | Referencje / obudowa |
|---|---|---:|---|
| nowe | Goldpin 1x13 2.54mm angled (buy angled strip, owned 1x40 is straight) | 1 | J2 / PinHeader_1x13_P2.54mm_Horizontal |
| nowe | Header 1x3 + one shunt (not fitted initially) | 2 | JP1, JP2 / PinHeader_1x03_P2.54mm_Vertical |
| nowe | IDC header 2x8 2.54mm angled shrouded, Au (type to be chosen in the purchase list) | 1 | J1 / IDC-Header_2x08_P2.54mm_Horizontal |
| nowe | SMD 1206 1% 0.25W 100R | 2 | R11, R12 / R_1206_3216Metric_Pad1.30x1.75mm_HandSolder |
| nowe | SMD 1206 1% 0.25W 1K | 11 | R20, R21, R22, R23, R24, R25, R26, R27, R28, R29, R30 / R_1206_3216Metric_Pad1.30x1.75mm_HandSolder |
| nowe | SMD 1206 1% 0.25W 47R | 4 | R14, R15, R16, R17 / R_1206_3216Metric_Pad1.30x1.75mm_HandSolder |
| nowe | SMD 1206 X7R 25V 10% 1u | 2 | C6, C7 / C_1206_3216Metric_Pad1.33x1.80mm_HandSolder |
| nowe | SMD 1206 X7R 25V 10% 4u7 | 2 | C4, C5 / C_1206_3216Metric_Pad1.33x1.80mm_HandSolder |
| nowe | SN74HC139N | 1 | U3 / DIP-16_W7.62mm |
| nowe | Socket 1x9 2.54mm Au + owned MAX31856 module | 2 | J3, J4 / MAX31856_XU_socket |
| rejestr | 74LVC125AD,118 Nexperia | 2 | U1, U2 / SOIC-14_3.9x8.7mm_P1.27mm |
| rejestr | K104K15X7RF5TH5 Vishay 100n X7R 50V radial 5mm (owned) | 3 | C1, C2, C3 / C_Disc_D5.0mm_W2.5mm_P5.00mm |
| rejestr | MF0207 Yageo 100K 1% 0.6W (owned, standing) | 7 | R3, R4, R7, R8, R9, R10, R13 / R_Axial_DIN0207_L6.3mm_D2.5mm_P5.08mm_Vertical |
| rejestr | MF0207 Yageo 10K 1% 0.6W (owned, standing) | 6 | R1, R2, R5, R6, R18, R19 / R_Axial_DIN0207_L6.3mm_D2.5mm_P5.08mm_Vertical |

**Zapotrzebowanie na części z rejestru** (stan rejestru 24.09: MF0207 10 k — 7 szt., 100 k — 7 szt., K104K15X7RF5TH5 100 n — 5 szt.; P01 miała z tego 5 / 5 / 3, ale P01 stała się zbędna po decyzji o pakiecie 18650):

| Część | P09 R2 potrzebuje | Rejestr |
|---|---:|---:|
| MF0207 10 k | 6 | 7 |
| MF0207 100 k | 7 | 7 |
| K104K15X7RF5TH5 100 n | 3 | 5 |

Razem z P10 R2 (3 × 10 k — R2 i dwa rezystory serwisowe CAN, 3 × 100 n): 10 k — 9 wobec 7, 100 k — 7 z 7, 100 n — 6 wobec 5 (zob. opis PR i `P10-R2-review/docs/ZAKUPY.md`).

Uwagi do zakupów:
- J1 (J_BP): obudowane złącze kątowe IDC 2×8, raster 2,54 mm, styki Au; z płytką połączeń P12 łączy je krótka taśma IDC 2×8 (dwa gniazda zaciskowe, jedno do J_BP, drugie do P12).
- J2 (SERWIS): goldpin **kątowy** 1×13 (posiadana listwa 1×40 z Kamami jest prosta i nie wystarczy).
- J3/J4: gniazda 1×9 Au (ZL262-9SG z listy 2), JP1/JP2: listwy 1×3 i zwora (zapas), początkowo bez zworek.
- U1/U2 SO14 z Ioff (74LVC125AD, nie HC125), lutowane wprost do płytki (S1 dopuszcza SOIC); U3 DIP16 z podstawką opcjonalnie.
- Kondensatory SMD 1206 X7R 25 V ±10 %; C4/C5 po DC bias ≥ 2,2 µF, C6/C7 ≥ 0,47 µF (1206 zachowuje pojemność lepiej niż 0805).
- Rezystory serwisowe R20…R30: 1 kΩ 1206, od spodu płytki pod listwą (S1 §9).
- Termopary K z izolowaną spoiną, mocowanie nylonowe M2.5 modułów, dystanse M3 20 mm (poziom 3) — bez zmian względem R1, poza dystansem (R1 miała M3 ≥ 10 mm).
