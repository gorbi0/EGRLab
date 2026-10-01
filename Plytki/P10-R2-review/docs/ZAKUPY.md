# Zakupy P10-R2 — ilości na jedną płytkę (S1)

Źródło: **rejestr** = pozycja z `Zamowione/zamowione.csv` (posiadane; rezystory MF0207 i kondensatory radialne montowane na stojąco, 74LVC125AD z zamówienia P10); **nowe** = do kupienia (lista zakupowa 2 do przeliczenia po decyzjach S1). Płytka z JLCPCB (klasa 1/3, 53 × 100 mm, slot S3 poziomu 4); PCB w README, sekcja „PCB”.

| Źródło | Nazwa | Ilość | Referencje / obudowa |
|---|---|---:|---|
| nowe | Goldpin 1x9 2.54mm angled (buy angled strip, owned 1x40 is straight) | 1 | J2 / PinHeader_1x09_P2.54mm_Horizontal |
| nowe | IDC header 2x5 2.54mm angled shrouded, Au (type to be chosen in the purchase list) | 1 | J1 / IDC-Header_2x05_P2.54mm_Horizontal |
| nowe | PESD2CAN,215 Nexperia | 1 | D1 / SOT-23 |
| nowe | SMD 1206 1% 0.25W 100R | 1 | R1 / R_1206_3216Metric_Pad1.30x1.75mm_HandSolder |
| nowe | SMD 1206 1% 0.25W 1K | 5 | R3, R4, R5, R6, R7 / R_1206_3216Metric_Pad1.30x1.75mm_HandSolder |
| nowe | SMD 1206 X7R 25V 10% 4u7 | 2 | C4, C5 / C_1206_3216Metric_Pad1.33x1.80mm_HandSolder |
| nowe | Soldered 120ohm twisted pair | 1 | J3 / PTH_OBD |
| nowe | TCAN1051VDRQ1 | 1 | U1 / SOIC-8_3.9x4.9mm_P1.27mm |
| rejestr | 74LVC125AD,118 Nexperia | 1 | U2 / SOIC-14_3.9x8.7mm_P1.27mm |
| rejestr | K104K15X7RF5TH5 Vishay 100n X7R 50V radial 5mm (owned) | 3 | C1, C2, C3 / C_Disc_D5.0mm_W2.5mm_P5.00mm |
| rejestr | MF0207 Yageo 10K 1% 0.6W (owned, standing) | 3 | R2, R8, R9 / R_Axial_DIN0207_L6.3mm_D2.5mm_P5.08mm_Vertical |

**Części z rejestru, o które konkuruje P09** (stan rejestru 24.09: MF0207 10 k — 7 szt., K104K15X7RF5TH5 100 n — 5 szt.):

| Część | P10 R2 | P09 R2 | Razem | Rejestr |
|---|---:|---:|---:|---:|
| MF0207 10 k | 3 (R2, R8, R9 — dwa ostatnie to rezystory serwisowe CAN_H/CAN_L) | 6 | 9 | 7 |
| K104K15X7RF5TH5 100 n | 3 | 3 | 6 | 5 |

Oba pakiety razem przekraczają rejestr: 10 k o dwie sztuki, 100 n o jedną (decyzja użytkownika w opisie PR).

Uwagi do zakupów:
- U1 koniecznie wariant **V** (VIO na pinie 5): TCAN1051VDRQ1, SOIC-8; U2 Nexperia 74LVC125AD,118 z Ioff (HC125 nie jest zamiennikiem); D1 PESD2CAN,215, SOT-23. Nie kupować terminatora CAN do montażu na P10.
- J1 (J_BP): obudowane złącze kątowe IDC 2×5, raster 2,54 mm, styki Au; taśma IDC 2×5 do P12 (dwa gniazda zaciskowe).
- J2 (SERWIS): goldpin **kątowy** 1×9 (posiadana listwa 1×40 z Kamami jest prosta).
- Kondensatory SMD 1206 X7R 25 V ±10 %; C4/C5 po DC bias ≥ 2,2 µF.
- Rezystory serwisowe 1 kΩ 1206 (R3–R7) od góry, przy swoich węzłach (S1 §6); CAN_H/CAN_L przez 10 kΩ (R8, R9, MF0207 z rejestru), przy J3.
- W3 OBD CAN (jedyna wiązka, która została): 300 mm skrętka CAN 120 Ω (LAPP UNITRONIC BUS CAN z listy 2), wtyk OBD-II męski typ A 16p z obudową, obsadzone tylko 6/14; opaski nylonowe 2,5 mm na kotwę J3 — bez zmian względem R1 (`P10-R1-review/docs/WIAZKI.md`, W3).
- W1 (LV10) i W2 (CORE CAN) z R1 znikają: zastępuje je J_BP i płytka połączeń P12.
