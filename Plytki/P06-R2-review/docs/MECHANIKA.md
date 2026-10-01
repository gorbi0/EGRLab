# Mechanika, złącza i montaż P06-R2 (format S1)

*R2 (1.10.2026): obrys R1 120 × 100 mm z czterema otworami, PBV stojący, wiązki W1 LV06 i W2 ILOG oraz NKK S6A znikają. Obowiązuje `Plytki/Format-S1/SPECYFIKACJA-FORMATU-S1.md` (S1-3). Layoutu w tym pakiecie nie ma — poniżej wymagania dla sesji lokalnej.*

## Płytka

Klasa 2/3: 106,5 × 100,0 mm, sloty S1–S2 poziomu 4 (S3 tego poziomu zajmuje P10), narożniki R 1 mm, FR-4 1,6 mm, 2 warstwy, **miedź 35 µm**, JLCPCB. Osiem otworów M3 Ø 3,2 mm w x = 4,0 / 49,0 / 57,5 / 102,5 i y = 14,0 / 86,0, strefa Ø 7 mm bez miedzi innych sieci i bez elementów. Brzeg x = 0 to strona panelu. Dystanse 20 mm: elementy od góry ≤ 16,5 mm, **od spodu tylko SMD ≤ 1,5 mm, bez SOIC** (poziom 4), ≥ 1 mm od pól THT; wyprowadzenia THT przycięte do ≤ 1,5 mm. Reguły jak w P02-R3 (pierścień PTH i przelotek ≥ 0,25 mm).

## Krawędź A (y = 0) — J_BP do P12

| Złącze | Slot | Środek x | Typ | Uwagi |
|---|---|---:|---|---|
| J_BP | S2 | 80,0 mm | IDC 2×8 kątowe obudowane, Au | ADC_SCLK 2, ADC_DOUTA 4 (jak J_BP2 P03 R6 / P05 R3 — tory P12 pionowo), CS_ILOG_N 6, LOGGER_CURRENT_OK 8, 5V_SYS 10/12, 3V3_IO 14; nieparzyste i 16 GND |

Strona wtyku równo z krawędzią, pin 1 od strony mniejszego x, pas y = 0–10 mm zastrzeżony tylko na długości złącza (x = 63,5–96,5 mm). Taśma IDC ok. 30 mm do P12. W slocie S1 krawędzi A złącza nie ma.

## Krawędź B (y = 100) — listwy serwisowe

J_SV1 (1 × 7) w slocie S1 (x = 10–43 mm): węzły analogowe I_L_OUT, ADC_AIN, REF_BUF, REF25 przez 10 kΩ, GND na 1, 4, 7. J_SV2 (1 × 13) w slocie S2 (x = 63,5–96,5 mm): szyny i logika, GND na 1, 5, 13. Goldpin kątowy, kołki ok. 6 mm za krawędzią. Rezystory R25–R38 (1206) **przy węźle**, nie przy listwie — tor od rezystora do kołka może być długi, bo po stronie kołka nie płynie prąd; mogą stać od spodu. Tory analogowe do J_SV1 z dala od toru mocy i R21. Nadruk: nazwa sieci przy każdym kołku, czytelna od strony B. Pin 1 kątowej listwy widziany z góry leży przy większym x.

## Strona panelu (x = 0) — tor mocy

J3 (ISERIES, 2 × 2,5 mm²), J4 (BYPASS tor mocy, 2 × 2,5 mm²) i J5 (status BYPASS, 3 × AWG22) przy brzegu x = 0, pola PTH J3 i J4 tuż przy RSH1. Pigtaile jak w R1: J3/J4 otwory 2,4 mm, pady 4,5 mm (J3 raster 7,62 mm, pola 3/4 puste; J4 raster 17,78 mm), J5 otwory 1,1 mm, pady 2,2 mm, raster 3,5 mm; dwa otwory kotwy Ø 3,2 mm 12 mm od rzędu, opaska 2,5 mm na izolacji.

Tor 5–6 A (10 A w próbie biernej E15) na 35 µm: pola ≥ 4 mm na **obu** warstwach, zszyte przelotkami, możliwie krótkie, J3 → RSH1.1 i RSH1.4 → J4 (J3.1 i J4.1 to ten sam węzeł ECU_P1, J3.2 i J4.2 — EGR_P1). Bez przelotek w polach RSH1, bez innych sieci pod bocznikiem.

**RSH1** — SMD 2512 z czterema polami (propozycja Vishay WSK2512R0050FEA, footprint `Resistor_SMD:R_Shunt_Vishay_WSK2512_6332Metric_T1.19mm`): pola 1 i 4 prądowe (2,29 × 2,03 mm), 2 i 3 pomiarowe (1,40 × 0,76 mm), pola 1/2 po stronie ECU_P1, 3/4 po stronie EGR_P1. Wymiary pól sprawdzić z kartą przed layoutem. Ścieżki Kelvina z pól 2/3 do R1/R2 (1206 0,1 %) i dalej do U1.8/U1.1 osobno, parą, symetrycznie, od pola pomiarowego, a nie z wylewki prądowej.

**SW1 BYPASS** — na panelu, poza PCB: DPDT ON-ON ≥ 10 A DC z oczkami lutowniczymi, tuleja z nakrętką; zarezerwować miejsce za panelem z lutami i łukiem przewodów (R1 dla S6A: 40 × 35 × 45 mm — dla wybranego typu sprawdzić na makiecie). Wspólne oczka i położenia BYPASS/MEASURE ustalić omomierzem (ODBIOR E03).

## Elementy wymagające szczególnej kontroli

- U1 INA240A2 SOIC-8, U5/U6 74LVC125AD SO-14 — raster 1,27 mm, lutowane wprost, **tylko od góry**. Bez podstawki pod INA240.
- U2 MCP6022 i U3 MCP3201 DIP8 (opcjonalnie w posiadanych podstawkach Kamami 1207058, ok. 8 mm), U7 SN74HC08N DIP14 (podstawka Kamami 648). U4 MCP1702, U8/U9 MCP120 (bondout D: 1 RESET, 2 VDD, 3 GND), U10 MCP1525 (TO-92: 1 GND, 2 VOUT, 3 VIN).
- R6 KNP01U-1R 1 W leżący (DIN0411, raster 15,24 mm). R21 PR02 39 Ω 2 W leżący (footprint `R_PR02_P17.78` z P02 R4), 3–5 mm nad laminatem, daleko od RSH1, U1 i U10. R11 47 kΩ posiadany MF0207 na stojąco (raster 5,08 mm).
- C3 220 µF / 16 V D6,3 × 11,2 mm, raster 2,5 mm (najwyższy element od góry). C4/C5 4,7 µF X7R 1206: C5 w promieniu 5 mm od U10 (karta MCP1525), C4 przy U4.
- D1 1N5819 DO-41 (raster 10,16), D2 BAT85 DO-35 (raster 7,62); pasek = katoda = pad 1.
- Pozostałe R i C — 1206 (mogą być od spodu, ≤ 1,5 mm).
