# P02 R1 — stan części względem rejestru zamówień

25.09.2026 · Claude. Porównanie BOM P02-R1 (`docs/BOM.csv`) z `Zamowione/zamowione.csv` (zamówienia TME, Mouser, Kamami z 24.09.2026). „Zapas P01” oznacza sztuki kupione ponad potrzebę P01 — jeśli mają zostać zapasem, trzeba je dokupić.

## Kupione z myślą o P02

| Pozycja | Część | Szt. | Źródło |
|---|---|---|---|
| U1 | TSR 2-2450 | 1 | Mouser 24.09 |
| U2 | TSR 2-2433 | 1 | Mouser 24.09 |
| U3 | MCP120-300DI/TO | 1 | Mouser 24.09 (4 szt. na P02, P05, P06, P08) |
| U4 | MCP120-450DI/TO | 1 | TME 24.09 (druga sztuka zamówienia P01) |
| U5 | 74LVC125AD,118 + adapter Kamami 575068 + kołki goldpin | 1 | Mouser, Kamami 24.09 |
| U6 | SN74HC08N + podstawka DIP14 (Kamami 648) | 1 | Mouser, Kamami 24.09 |

## Pokryte zapasem P01

| Pozycja | Część | Potrzeba | Zapas P01 | Brakuje |
|---|---|---|---|---|
| D1, D2 | STPS20100CT | 2 | 1 | **1** |
| U7 | LM2903P | 1 | 1 | 0 |
| U8 | TL431BILP | 1 | 1 | 0 |
| LED1 | L-934GD | 1 | 1 | 0 |
| C4 | EEUFR1H220 (22 µF / 50 V) | 1 | 1 | 0 |
| C9–C15 | 100 nF X7R, Vishay K (5 mm) | 7 | 2 | **5** |
| R2, R3, R4, R12, R13, R15 | MF0207 10 k 1 % | 6 | 2 | **4** |
| R7, R10 | MF0207 100 k 1 % | 2 | 2 | 0 |
| R1 | MF0207 4k7 1 % | 1 | 2 | 0 |

## Niekupione

| Pozycja | Część | Szt. | Uwaga |
|---|---|---|---|
| C1–C3 | Samwha HC1V229M35045HA, 22 mF / 35 V, snap-in P10, Ø35 × 45 | 3 | |
| R17 (poza płytką) | TE HSA2547RJ, 47 Ω / 25 W + blacha aluminiowa | 1 | nie zastępować 0,5 W |
| R5, R14, R16 | MF0207 1 k 1 % | 3 | |
| R6 / R9 | MF0207 267 k / 348 k 1 % | 1 / 1 | progi komparatora — tolerancja 1 % |
| R8, R11 | MF0207 2M2 1 % | 2 | histereza |
| C5, C7 | EEUFR1H100 (10 µF / 50 V) | 2 | |
| C6, C8 | EEUFR1C220 (22 µF / 16 V) | 2 | |
| F1–F4 | oprawka Stelvio-Kontek PTF78 | 4 | |
| F1 / F2, F3 / F4 | wkładka 5 × 20: T2A / F1A / F100mA, parametr DC ≥ 32 V | 1 / 2 / 1 | typ wkładek do doboru (DC) |
| J2 | Phoenix GMSTBA 2,5/3-G-7,62 (1766246) + wtyk GMSTB 2,5/3-ST-7,62 do wiązki P07 | 1 + 1 | odstępstwo od PC 4 z v6.1 |
| J3–J10 | Molex Mini-Fit Jr 5566-04A pionowe, styki Au | 8 | dokładny MPN przy zakupie |
| J11 | Molex Mini-Fit Jr 5566-14A pionowe, styki Au | 1 | jw. |

Wiązki (poza BOM płytki): H_SUPPLY 2 × 2,5 mm² z wtykiem MSTB 2,5/3-ST-5,08 (1757022) do P01 J6 — wtyku nie ma w rejestrze; H_PSUOK taśma 6 × AWG28 z IDC 6p; para AWG20 do R_CHARGE; kabel VMOTOR; wtyki Mini-Fit 5557 ze stykami do LV03–LV10 i VSENSE. Opaski 2,5 i 3,6 mm są z zamówienia P01.
