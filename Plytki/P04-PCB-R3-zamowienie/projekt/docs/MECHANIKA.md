# Mechanika i wymagania dla layoutu P04-R3 (format S1)

*R3 (5.10.2026): obrys R2.2 160 × 120 mm z Mini-Fit, pigtailami i kotwami znika. Obowiązuje `Plytki/Format-S1/SPECYFIKACJA-FORMATU-S1.md` (S1-3, §7: P04 na poziomie 6, klasa L — decyzja użytkownika 5.10.2026). Layout robi sesja lokalna; ten pakiet zawiera tylko schemat.*

*5.10.2026: layout zrobiony (README, sekcja „PCB”); wymagania niżej sprawdza `src/verify_pcb.py`. Limit 16,5 mm nad poziomem 6 potwierdzony decyzją użytkownika 5.10; wszystkie części od góry.*

## Płytka

Klasa L: 160,0 × 100,0 mm, sloty S1–S3 poziomu 6, narożniki R 1 mm, FR-4 1,6 mm, 2 warstwy, miedź 35 µm, JLCPCB. Dwanaście otworów M3 Ø 3,2 mm w x = 4,0 / 49,0 / 57,5 / 102,5 / 111,0 / 156,0 i y = 14,0 / 86,0, strefa Ø 7 mm bez miedzi innych sieci i bez elementów. Reguły jak w P02-R3 (pierścień PTH i przelotek ≥ 0,25 mm).

Poziom 6 jest najwyższy; pod nim P08 (S1) i P07 (S2–S3) poziomu 5 na dystansach 20 mm. **Założenie do potwierdzenia:** nad P04 limit jak dla poziomu standardowego, elementy od góry ≤ 16,5 mm (pokrywa). Od spodu tylko SMD ≤ 1,5 mm, bez SOIC (poziom ≠ 1), ≥ 1 mm od pól THT; wyprowadzenia THT przycięte do ≤ 1,5 mm.

Najwyższe elementy (szacunek): C1 WIMA MKS2 1 µF / 100 V (7,2 × 7,2 mm, wys. ok. 13 mm — sprawdzić w karcie przy przymiarce), C2 MKS2 1 µF / 63 V (H 10 mm), U1–U7 w podstawkach ok. 8 mm, C3 Ø 5 × 11 mm, IDC kątowe ok. 9 mm.

## Krawędź A (y = 0) — J_BP1…J_BP3 do P12

| Złącze | Slot | Środek x | Typ | Treść |
|---|---|---|---|---|
| J_BP1 | S1 | 26,5 mm | IDC 2×8 kątowe obudowane | PANELSAFE z P11 (piny 2/4/6/8/14 jak J_P12), SENSOR do P08, DAQ_OK z P05 |
| J_BP2 | S2 | 80,0 mm | IDC 2×10 | DRIVE do P07 (czeka na P07), P02 R4: PSU_OK, P04_3V3, SAFE_N, pętla PG; 3V3_IO |
| J_BP3 | S3 | 133,5 mm | IDC 2×10 | P03 R6 (piny 12–20 jak J_BP3 P03), 5V_SYS (tylko kołek serwisowy), 3V3_IO |

Pin 1 od strony mniejszego x, strona wtyku równo z krawędzią A, pas y = 0–10 mm zastrzeżony tylko na długości złącza (x = 10–43 mm w slocie). Wszystkie nieparzyste piny to GND — każdy sygnał w taśmie ma masę po obu stronach (PWM, PWM_OUT, HEARTBEAT). Pinout: `docs/J_BP.csv`.

## Krawędź B (y = 100) — listwy serwisowe

| Listwa | Slot | x | Piny | Treść |
|---|---|---|---|---|
| J_SV1 | S1 | 10–43 mm | 1×13 | łańcuch SAFE / ARM / watchdog |
| J_SV2 | S2 | 63,5–96,5 mm | 1×7 | zgody i interlock |
| J_SV3 | S3 | 117–150 mm | 1×7 | szyny i wyjścia 3,3 V przez rezystory |

Goldpin kątowy, kołki ok. 6 mm za krawędzią B; pin 1 kątowej listwy widzianej z góry leży przy większym x (footprint KiCada). Rezystory R43–R61 **przy węzłach** (SMD, mogą być od spodu), ścieżka od rezystora do kołka może być długa. Nadruk: nazwa sieci przy każdym kołku, czytelna od strony B. Pinout i rezystory: `docs/SERWIS.csv`.

## Rozmieszczenie (wskazówki, nie wymagania)

- C18 1 nF przy U2.11, R5 przy U2 (jak R2.2, R4-04); C1 między U1.15 i U1.14 możliwie krótko, z dala od PWM.
- Bufory U8–U10 (SOIC-14, od góry) blisko J_BP3/J_BP2, rezystory domyślne R12–R22 po stronie złącza, R25–R35 po stronie bramek.
- R41/R42 przy J_BP1 (linie panelu), R40 przy J_BP1.2, R38/R39 przy J_BP2.
- SAFE_N ma dojść do J_BP2.16, Q1–Q3, R4, R5, C18, U2.11 i R43 bez pętli wokół PWM.
- LED1 widoczna z góry; płytka jest najwyżej, więc LED da się obserwować po zdjęciu pokrywy.
