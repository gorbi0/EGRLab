# Zakupy P04-R3 — ilości na jedną płytkę (S1)

*Plik generowany przez `src/make_tables.py` z `src/parts.py`.* Źródło: **rejestr** = pozycja z `Zamowione/zamowione.csv` (posiadane); **nowe** = do kupienia (po akceptacji, wspólne zamówienie wariantu pełnego). Płytka z JLCPCB (klasa L, 160 × 100 mm); w tym pakiecie tylko schemat.

| Źródło | Nazwa (MPN) | Wartość | Ilość | Referencje / obudowa |
|---|---|---|---:|---|
| nowe | 2N3904BU | 2N3904 | 3 | Q1, Q2, Q3 / TO-92_Inline_Wide |
| nowe | CD74HC123E | CD74HC123E | 1 | U1 / DIP-16_W7.62mm |
| nowe | IDC header 2x10 2.54mm angled shrouded, Au | J_BP2 / IDC 2x10 | 1 | J_BP2 / IDC-Header_2x10_P2.54mm_Horizontal |
| nowe | IDC header 2x10 2.54mm angled shrouded, Au | J_BP3 / IDC 2x10 | 1 | J_BP3 / IDC-Header_2x10_P2.54mm_Horizontal |
| nowe | IDC header 2x8 2.54mm angled shrouded, Au | J_BP1 / IDC 2x8 | 1 | J_BP1 / IDC-Header_2x08_P2.54mm_Horizontal |
| nowe | L-934GD | POWER / green | 1 | LED1 / LED_D3.0mm |
| nowe | MCP100-300DI/TO | MCP100-300DI/TO | 1 | U11 / TO-92_Inline_Wide |
| nowe | MKS2C041001F00KSSD | 1u / PET | 1 | C2 / C_Rect_L7.2mm_W5.0mm_P5.00mm |
| nowe | Pin header 1x13, 2.54 mm, right angle, Au | J_SV1 SERWIS 1x13 | 1 | J_SV1 / PinHeader_1x13_P2.54mm_Horizontal |
| nowe | Pin header 1x7, 2.54 mm, right angle, Au | J_SV2 SERWIS 1x7 | 1 | J_SV2 / PinHeader_1x07_P2.54mm_Horizontal |
| nowe | Pin header 1x7, 2.54 mm, right angle, Au | J_SV3 SERWIS 1x7 | 1 | J_SV3 / PinHeader_1x07_P2.54mm_Horizontal |
| nowe | RC1206FR-07100KL | 100K / 1% | 6 | R5, R9, R10, R11, R28, R30 / R_1206_3216Metric_Pad1.30x1.75mm_HandSolder |
| nowe | RC1206FR-07100RL | 100R / 1% | 1 | R40 / R_1206_3216Metric_Pad1.30x1.75mm_HandSolder |
| nowe | RC1206FR-0710KL | 10K / 1% | 28 | R2, R4, R6, R7, R8, R12, R13, R14, R15, R16, R17, R18, R19, R20, R21, R22, R23, R24, R25, R29, R31, R32, R33, R34, R35, R36, R43, R44 / R_1206_3216Metric_Pad1.30x1.75mm_HandSolder |
| nowe | RC1206FR-071KL | 1K / 1% | 23 | R3, R37, R38, R39, R41, R42, R45, R46, R47, R48, R49, R50, R51, R52, R53, R54, R55, R56, R57, R58, R59, R60, R61 / R_1206_3216Metric_Pad1.30x1.75mm_HandSolder |
| nowe | RC1206FR-07220KL | 220K / 1% | 1 | R1 / R_1206_3216Metric_Pad1.30x1.75mm_HandSolder |
| nowe | RC1206FR-0747KL | 47K / 1% | 2 | R26, R27 / R_1206_3216Metric_Pad1.30x1.75mm_HandSolder |
| nowe | SMD 1206 X7R 50V 10% 100n | 100n / X7R | 14 | C4, C5, C6, C7, C8, C9, C10, C11, C12, C13, C14, C15, C16, C17 / C_1206_3216Metric_Pad1.33x1.80mm_HandSolder |
| nowe | SN74HC14N | SN74HC14N | 1 | U2 / DIP-14_W7.62mm |
| nowe | SN74HC74N | SN74HC74N | 1 | U3 / DIP-14_W7.62mm |
| rejestr | 74LVC125AD,118 (Nexperia) | 74LVC125AD | 3 | U8, U9, U10 / SOIC-14_3.9x8.7mm_P1.27mm |
| rejestr | C320C102J1G5TA (KEMET C0G 1n, owned; lead pitch to check on the 1:1 print) | 1n / C0G | 1 | C18 / C_Disc_D5.0mm_W2.5mm_P5.00mm |
| rejestr | EEU-EB1J100SH | 10u / 63V | 1 | C3 / CP_Radial_D5.0mm_P2.00mm |
| rejestr | MKS2D041001K00JO00 | 1u / PET | 1 | C1 / C_WIMA_MKS2_1u100V_L7.2_W7.2_P5 |
| rejestr | SN74HC08N | SN74HC08N | 4 | U4, U5, U6, U7 / DIP-14_W7.62mm |

## Bilans posiadanych części (rejestr 24.09)

Zużycie innych płytek policzone z ich `docs/parts.json` na gałęzi `pelny-s1` (P02 R4, P03 R6, P05 R3, P06 R2, P09 R2, P10 R2). P08 R2 powstaje równolegle — jeśli sięgnie po te same pozycje, trzeba rozstrzygnąć przydział (pytanie w PR).

| Część z rejestru | Rejestr | Zużyte przez inne płytki | Zostaje | P04 R3 bierze | Uwagi |
|---|---:|---|---:|---:|---|
| 74LVC125AD,118 (Nexperia) | 25 | P02 1, P03 7, P05 4, P06 2, P09 2, P10 1 | 8 | 3 | U8–U10 lutowane wprost; zostaje 5 (P08 R1: 2, P07: do ustalenia) |
| SN74HC08N + podstawka DIP14 (Kamami 648) | 8 / 10 | P02 1, P05 1, P06 1 | 5 | 4 | U4–U7 w podstawkach (przydział P04 z 24.09); zostaje 1 (P08) |
| podstawka DIP16 (Kamami 649) | 2 | P03 1 | 1 | 1 | U1 CD74HC123E (układ nowy) |
| adapter SO14→DIP14 (Kamami 575068) | 18 (P04: 3) | — | 3 | 0 | niepotrzebne: SOIC lutowane wprost (S1 §9); do dyspozycji P07/P08 |
| WIMA MKS2 1 µF / 100 V 5 % (MKS2D041001K00JO00) | 2 | P02 R4 C6 | 1 | 1 | C1 (watchdog, PET) — ostatnia sztuka; korpus 7,2 × 7,2 mm (footprint z P02 R4) |
| KEMET C320C102J1G5TA C0G 1 nF | 2 | P05 R3 C32 | 1 | 1 | C18 (filtr SAFE_N) — ostatnia sztuka; raster sprawdzić na wydruku 1:1 |
| Panasonic EEU-EB1J100SH 10 µF / 63 V | 2 | P02 R4 C1 | 1 | 1 | C3 (bulk 3V3_IO) — ostatnia sztuka; w R2.2 EEUFR1H100 10 µF / 50 V, ten sam D5 P2 |
| Kingbright L-934GD | 2 | P02 R4, P03 R6 | 0 | 0 | LED1 jako nowa |
| MF0207 (10K, 100K, 47K, 220K, 1K, 100R) | — | — | 0 | 0 | brak zapasu tych wartości (bilans w P06 R2 `docs/ZAKUPY.md`); wszystkie rezystory P04 jako nowe 1206 |

## Uwagi do zakupów

- **Rezystory:** wszystkie nowe Yageo RC1206FR-07…L (1 %, 1206), także 19 rezystorów listew serwisowych (R43–R61).
- **C2:** WIMA MKS2 1 µF / 63 V (MKS2C041001F00KSSD) jak w R2.2 — filtr ARM; foliowy THT, bo 1 µF X7R zmienia pojemność z napięciem i temperaturą, a S1 §9 mówi o nowych ceramicznych.
- **C4–C17:** 100 nF X7R 1206 50 V; C15–C17 to druga para 100 nF przy U8–U10 (w R2.2 na adapterach) — do decyzji przy recenzji, czy zostają.
- **U1 CD74HC123E, U2 SN74HC14N, U3 SN74HC74N, Q1–Q3 2N3904BU, U11 MCP100-300DI/TO:** nowe, obudowy jak w R2.2 (DIP, TO-92). Podstawki DIP14 pod U2/U3 opcjonalne (nowe).
- **J_BP1:** obudowane kątowe IDC 2×8; **J_BP2, J_BP3:** 2×10; styki Au. Taśmy IDC ok. 30 mm do P12 (po dwa gniazda zaciskowe) — z zamówieniem P12 dla wariantu pełnego.
- **J_SV1:** goldpin kątowy 1×13, **J_SV2 i J_SV3:** 1×7 (posiadana listwa 1×40 Kamami jest prosta).
- Z R2.2 znikają: Mini-Fit J7/J8 (39-29-9069, 39-29-9109) i ich wiązki, IDC J3–J6 (Würth 612…), pigtaile J1/J2 z kotwami, adaptery SO14 (zostają w rejestrze), K104K15X7RF53H5, K102J15C0GF53H5 (zastąpiony posiadanym C320), EEUFR1H100, MFR-25 (zastąpione 1206), pola TP1–TP15.
