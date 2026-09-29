# Zamówione części — EGRLab

Rejestr części **faktycznie zamówionych**. To nie jest plan zakupów: plany, warianty i uzasadnienia zamienników są w `Plytki/P01-zakupy/ZAKUPY-P01.md`. Wersja do filtrowania i sumowania: `zamowione.csv` (średnik, UTF-8). Kolumna „zapas” to różnica między ilością zamówioną a potrzebną według BOM.

## Zamówienia

| Dostawca | Data | Status | Pozycji | Moduły |
|---|---|---|---:|---|
| TME | 24.09.2026 | w drodze (kurier) | 54 (49 + 5 opcjonalnych) | P01, jedna sztuka dla P02 |
| Mouser | 24.09.2026 | zamówione (FedEx z USA) | 22 (65 szt.) | P01, P02, P03, P04, P05, P06, P08, P09, P10 + 2 szt. dla P07 |
| Kamami | 24.09.2026 | zamówione | 8 (74,81 zł) | adaptery, piny i podstawki P02–P06, P08–P10; 1N4148 dla P05/P08 |

## Stan kompletacji według modułów

Braki dla P02–P11 są liczone według BOM v6.1-rc1, czyli przed recenzją tych modułów. Recenzja może je jeszcze zmienić.

| Moduł | Zamówione | Czego jeszcze brakuje |
|---|---|---|
| P01 PROTECT | **wszystkie części z BOM** (TME + Mouser) | **płytka PCB** (PCB-R3, wydanie R3.1; przed przymiarką 1:1); zakupy lokalne: przewód 2,5 mm² czerwony/czarny, AWG22, drut Cu 2,5 mm² na LK1, drut 0,6 mm na R34, bezpiecznik 5 A z oprawką, zaciskarka Mini-Fit Jr |
| P02 PSU | TSR 2-2450, TSR 2-2433, MCP120-300, MCP120-450 (TME), 74HC08, 74LVC125AD; adapter SO14 i podstawka DIP14 (Kamami) | pasywne, bezpieczniki F2/F3/F_VSENSE z oprawkami, złącza (Phoenix PC 4/3-G-7,62, Mini-Fit Jr 4p ×8 i 14p); obwód HOLD (3 kondensatory 22 mF, STPS20100CT ×2 — 1 szt. jest z zapasu TME, R_CHARGE, R_BLEED, C_BUS, F_HOLD) |
| P03 CORE | MCP23017, 74HC139, 74LVC125AD ×7, TPS3808 (+1 zapas), adapter PA0085; adaptery SO14 ×7, podstawki DIP16 i 2× DIP14 pod MCP23017 (Kamami); moduł ESP32-S3 już masz | pasywne, LED, moduł microSD, złącza (Samtec SSW-108-01-G-D, IDC ×7, Mini-Fit Jr 8p) |
| P04 SAFE | 74HC08 ×4, 74LVC125AD ×3; adaptery SO14 ×3, podstawki DIP14 ×4 i DIP16 pod CD74HC123E (Kamami) | CD74HC123E, 74HC14, 74HC74, 2N7002 ×3, pasywne, złącza; opcjonalnie podstawki DIP14 ×2 pod 74HC14/74HC74 |
| P05 DAQ | MCP120-300, MCP120-450, 74HC08, 74LVC125AD ×4; 1N4148 ×3 i podstawka DIP14 (Kamami, podstawka tylko jeśli PCB ją przewidzi); przetwornik AD już masz | ADR4525BRZ, TBD62083APG, TLV1702, przekaźniki ×3, rezystory 0,1%, Samtec TSW-108-07-G-D, pasywne |
| P06 I-LOGGER | **wszystkie układy scalone**: INA240, MCP3201, MCP6022, MCP1525, MCP1702, MCP120 ×2, 74HC08, 74LVC125AD ×2; adaptery SOIC8 ×1 i SO14 ×2, podstawki DIP8 ×2 i DIP14 (Kamami) | bocznik 5 mΩ, rezystory 0,1% (RC3, RC4, R_DIV), przełącznik SW_BYPASS, pasywne |
| P07 DRIVE (wstrzymany) | INA240, MCP3201 | reszta po decyzji w sprawie sterownika (m.in. 74LVC125AD ×4, MCP120 ×2, MCP6022 ×2) |
| P08 SENSOR | MCP120-300, MCP120-450, 74HC08, 74LVC125AD ×2; adaptery SO14 ×2, 1N4148 (D8), podstawka DIP14 (Kamami) | TPS2553DBVR, TBD62083APG, przekaźnik, pasywne, **adapter SOT23-6** (Kamami ma tylko 3-pinowy SOT23; kupić razem z TPS2553) |
| P09 TEMP | 74LVC125AD ×2; adaptery SO14 ×2 (Kamami) | moduły MAX31856 ×2 |
| P10 CAN | 74LVC125AD; adaptery SOIC8, SOT23 i SO14 (Kamami) | TCAN1051VDRQ1, PESD2CAN, złącze OBD |
| P11 PANEL | — | całość (przełączniki, złącza Deutsch DT04, BNC, Mini-Fit Jr 12p, MSTB 4p) |

## TME — zamówienie z 24.09.2026

| Symbol TME | Szt. | Moduł | Pozycje | BOM | Zapas | Uwagi |
|---|---:|---|---|---:|---:|---|
| SUP53P06-20-E3 | 3 | P01 | Q1, Q2 | 2 | 1 | P-MOSFET, TO-220 |
| STPS20100CT | 2 | P01 | D2 | 1 | 1 | zapas pokrywa 1 z 2 szt. potrzebnych w P02-HOLD |
| 5KP18A-DIO | 2 | P01 | D3 | 1 | 1 | Diotec zamiast Littelfuse 5KP18A-B |
| 1.5KE18A-E3/54 | 2 | P01 | D5 | 1 | 1 | |
| BZX55C15-TAP | 4 | P01 | D4, D9 | 2 | 2 | |
| 1N4148-TAP | 5 | P01 | D6–D8 | 3 | 2 | |
| 2N5551TA | 7 | P01 | Q3, Q5–Q8 | 5 | 2 | zamiast 2N5551G, nóżki pod 2,54 |
| 2N5401YBU | 3 | P01 | Q4 | 1 | 2 | |
| LM2936Z-5.0/NOPB | 2 | P01 | U1 | 1 | 1 | |
| LM2903P | 2 | P01 | U2 | 1 | 1 | |
| MCP120-450DI/TO | 2 | P01, P02 | P01 U4, P02 U_SUP5 | 2 | 0 | druga sztuka na P02 |
| L-934GD | 2 | P01 | LED1 | 1 | 1 | |
| EEUEB1J100SH | 2 | P01 | C1 | 1 | 1 | zamiast UPW1J100MDD |
| B32529C1104J000 | 3 | P01 | C2, C4 | 2 | 1 | |
| EEUFR1H101 | 2 | P01 | C3 | 1 | 1 | |
| B32529C1103J289 | 2 | P01 | C5 | 1 | 1 | inny kod wyprowadzeń niż …J000 |
| MKS2-1U/100-5%-R | 2 | P01 | C6 | 1 | 1 | WIMA MKS2D041001K00JO00 |
| EEUFR1H220 | 2 | P01 | C7 | 1 | 1 | |
| K104K15X7RF5TH5 | 5 | P01 | C8, C10, C11 | 3 | 2 | |
| EEUFR1H470 | 2 | P01 | C9 | 1 | 1 | |
| RDE5C1H101J0M1H03A | 2 | P01 | C12 | 1 | 1 | Murata zamiast Vishay K101… |
| C320C102J1G5TA | 2 | P01 | C13 | 1 | 1 | KEMET zamiast Vishay K102… |
| PR02-150R | 2 | P01 | R1 | 1 | 1 | ±5% zamiast ±1% |
| PR02-2K2 | 2 | P01 | R23 | 1 | 1 | ±5% zamiast ±1% |
| PR02000201009JA100 | 2 | P01 | R27 | 1 | 1 | 10 Ω, ±5% zamiast ±1% |
| MF0207FTE-1R | 2 | P01 | R2 | 1 | 1 | Yageo zamiast MFR-50 |
| MF0207FTE-820R | 2 | P01 | R3 | 1 | 1 | |
| MF0207FTE-10K | 7 | P01 | R4, R16, R26, R30, R32 | 5 | 2 | |
| MF0207FTE-100K | 7 | P01 | R12, R15, R21, R24, R31 | 5 | 2 | |
| MF0207FTE-2K2 | 2 | P01 | R13 | 1 | 1 | |
| MF0207FTE-4K7 | 6 | P01 | R14, R17, R19, R28 | 4 | 2 | |
| MF0207FTE-47K | 6 | P01 | R18, R20, R25, R33 | 4 | 2 | |
| MF0207FTE-470K | 2 | P01 | R22 | 1 | 1 | |
| MF0204FTE52-6K8 | 2 | P01 | R29 | 1 | 1 | 0204 zamiast 0207 |
| 3296W-1-502LF | 1 | P01 | RV1 | 1 | 0 | |
| MSTBA2.5/3G5.08 | 1 | P01 | J6 | 1 | 0 | Phoenix 1757255 |
| IC2.5/2-ST-5.08 | 1 | P01 | H_BAT | 1 | 0 | Phoenix 1786174 |
| MSTB2.5/2-ST-5.08 | 1 | P01 | EXT przy źródle | 1 | 0 | Phoenix 1757019 |
| MX-5557-06R | 1 | P01 | H_PG | 1 | 0 | Molex 39-01-2060 |
| MX-5556GSL7F | 10 | P01 | H_PG | 6 | 4 | Molex 39-00-0429, Au |
| SK129-63STS | 2 | P01 | HS1, HS2 | 2 | 0 | |
| ZL201-02G | 50 | P01 | J3 | 1 | 49 | minimum 50 szt. |
| JUMPER-KPL | 20 | P01 | J3 | 1 | 19 | minimum 20 szt. |
| IB-6 | 4 | P01 | Q1, D2 | 2 | 2 | |
| SMICA-TO220 | 10 | P01 | Q1, D2 | 2 | 8 | minimum 10 szt. |
| TFF-M3X10/DR185 | 10 | P01 | mocowanie PCB | 4 | 6 | minimum 10 szt. |
| FIX-2.5X100-ST/BK | 100 | P01 | kotwa J5 | 1 | 99 | |
| FIX-3.6X150-ST/BK | 100 | P01 | kotwa J7 | 1 | 99 | |
| 216-206 | 6 | P01 | H_BAT, EXT | 4 | 2 | WAGO |
| M3X10/D7985B | 100 | P01 | TO-220 (Q1, D2) | 2 | 98 | opcjonalne |
| M3X6/D7985B | 100 | P01 | dystanse PCB | 8 | 92 | opcjonalne |
| B3/BN117 | 100 | P01 | TO-220 (Q1, D2) | 2 | 98 | opcjonalne |
| B3/BN1074 | 100 | P01 | TO-220 (Q1, D2) | 2 | 98 | opcjonalne |
| 1-2199298-2 | 1 | P01 | U2 | 1 | 0 | opcjonalne, podstawka DIP-8 |

## Mouser — zamówienie z 24.09.2026

Źródło: `Plytki/P01-zakupy/MOUSER-P01-P03-wklej.txt` bez 910-PA0003 plus `MOUSER-dobor-P04-P10-wklej.txt`. Pozycje powtarzające się w obu listach są zsumowane. Ilości przyjęte z list; jeśli potwierdzenie Mousera pokazuje inne, trzeba je tu poprawić.

| Nr Mouser | Szt. | Moduł | Pozycje | BOM | Zapas | Uwagi |
|---|---:|---|---|---:|---:|---|
| 576-15KPA24CA | 1 | P01 | D1 | 1 | 0 | Littelfuse, TVS dwukierunkowa |
| 595-TL431BILP | 2 | P01 | U3 | 1 | 1 | TI |
| 279-YR1B54K9CC | 1 | P01 | R5 | 1 | 0 | TE YR1B 0,1% 15 ppm zamiast H4 |
| 279-YR1B10KCC | 4 | P01 | R6, R7, R10 | 3 | 1 | j.w. |
| 279-YR1B221KCC | 1 | P01 | R8 | 1 | 0 | **221k zamiast 220k** — wpisać do BOM i rejestru zmian |
| 279-YR1B26K1CC | 1 | P01 | R9 | 1 | 0 | j.w. |
| 279-YR1B249KCC | 1 | P01 | R11 | 1 | 0 | j.w. |
| 495-TSR2-2450 | 1 | P02 | M3 | 1 | 0 | Traco, 5 V |
| 495-TSR2-2433 | 1 | P02 | M4 | 1 | 0 | Traco, 3,3 V |
| 579-MCP120-300DI/TO | 4 | P02, P05, P06, P08 | U_SUP3 w każdym | 4 | 0 | P07 niepokryty |
| 579-MCP120-450DI/TO | 3 | P05, P06, P08 | U_SUP5 w każdym | 3 | 0 | P02 U_SUP5 z TME |
| 595-SN74HC08N | 8 | P02, P04, P05, P06, P08 | P02 U_READY; P04 U10, U12, U_LINK, U_LINK2; P05, P06, P08 U_READY | 8 | 0 | |
| 579-MCP23017-E/SP | 1 | P03 | U17 | 1 | 0 | |
| 595-SN74HC139N | 1 | P03 | U_CS | 1 | 0 | |
| 771-74LVC125AD-T | 25 | P02–P06, P08–P10 | P02 1, P03 7, P04 3, P05 4, P06 2, P08 2, P09 2, P10 1 | 22 | 3 | Nexperia; P07 (4 szt.) niepokryty; każdy wymaga adaptera SO14→DIP |
| 595-TPS3808G33DBVR | 2 | P03 | U5 | 1 | 1 | SOT23-6 |
| 910-PA0085 | 1 | P03 | ADP_U5 | 1 | 0 | Chip Quik, SOT23-6→DIP-6 |
| 595-INA240A2EDRQ1 | 2 | P06, P07 | P06 U3; P07 U2 | 2 | 0 | P07 wstrzymany; jeśli jego wariant odpadnie, sztuka jest zapasem |
| 579-MCP3201-BI/P | 2 | P06, P07 | P06 U_ADC; P07 U_ADC | 2 | 0 | j.w. |
| 579-MCP6022IP | 1 | P06 | U_BUF | 1 | 0 | |
| 579-MCP1525ITO | 1 | P06 | U_REF | 1 | 0 | |
| 579-MCP1702-3302E/TO | 1 | P06 | U_LDO | 1 | 0 | |

## Kamami — zamówienie z 24.09.2026

Wartość pozycji 74,81 zł bez wysyłki, ceny z koszyka. Adaptery Kamami są sprzedawane bez pinów, stąd goldpiny.

| Indeks Kamami | Produkt | Szt. | Moduł | Pozycje | BOM | Zapas | Uwagi |
|---|---|---:|---|---|---:|---:|---|
| 575068 | Adapter PCB SOP14 na DIP14 | 18 | P02–P04, P06, P08–P10 | P02 1, P03 7, P04 3, P06 2, P08 2, P09 2, P10 1 | 18 | 0 | płytka 18×18 mm, rzędy co 15,24 mm (0,6"): **nie wchodzi w podstawkę DIP14**; na płytce uniwersalnej rezerwować 18×18 mm |
| 575072 | Adapter PCB SOP8/SOIC8 na DIP8 | 2 | P06, P10 | P06 ADP_U3 (INA240), P10 ADP_U16 (TCAN1051) | 2 | 0 | 12×12 mm, rzędy co 7,62 mm |
| 581189 | Adapter PCB SOT23 na DIP | 2 | P10 | ADP_D3 (PESD2CAN) | 1 | 1 | tylko 3 piny (SOT23-3); **nie pasuje do SOT23-6 w P08 U11** |
| 1207864 | Goldpin czarny 1x40 prosty 2,54 mm | 9 | P02–P04, P06, P08–P10 | piny adapterów: SO14 ×18, SOIC8 ×2, SOT23, PA0085 | 8 | 1 | potrzeba ok. 290 pinów; szacunek, nie pozycja BOM |
| 648 | Podstawka DIP14 precyzyjna | 10 | P02–P06, P08 | 74HC08N ×8 (P02, P04 ×4, P05, P06, P08); P03 U17 MCP23017 — 2 szt. jedna za drugą jako DIP28 0,3" | 10 | 0 | w P05 tylko, jeśli layout PCB przewidzi podstawkę |
| 649 | Podstawka DIP16 precyzyjna | 2 | P03, P04 | P03 U_CS (74HC139N), P04 U7 (CD74HC123E, jeszcze niekupiony) | 2 | 0 | |
| 1207058 | Podstawka precyzyjna DIP-8P, złocone styki | 2 | P06 | U_BUF (MCP6022), U_ADC (MCP3201) | 2 | 0 | |
| 1187768 | Dioda 1N4148 THT, op. 10 szt. | 10 | P05, P08 | P05 D4–D6, P08 D8 | 4 | 6 | 1 opakowanie; dodatkowo 2 szt. zapasu z TME |

## Do kupienia osobno (adaptery)

Wszystkie adaptery z BOM v6.1-rc1 (bez P07) są zamówione, z wyjątkiem **SOT23-6→DIP ×1 dla P08 U11**. Kamami nie ma adaptera SOT23-6, a jego „SOT23 na DIP” ma 3 piny. Kupić przy następnym zamówieniu TME/Mouser, np. drugi Chip Quik PA0085, razem z TPS2553DBVR.
