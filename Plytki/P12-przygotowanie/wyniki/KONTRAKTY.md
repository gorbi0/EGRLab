# Kontrakty krawędzi A (J_BP) — mapa dla P12

*Plik generowany przez `src/kontrakty.py` z `zrodla.json`; nie edytować ręcznie.*

**Wynik:** 0 błędów, 0 uwag; sieci: OK 56, czeka 0, UWAGA 0, BŁĄD 0.

## Źródła

| Płytka | Stan | Pinout |
|---|---|---|
| P02 R4 | PCB scalona (PR #4), paczka produkcyjna | main @ cc0c43b, blob ddb6f8c3d4 |
| P03 R6 | PCB scalona lokalnie 1.10 (gałąź p03-r6-pcb; main czeka na push) | main @ cc0c43b, blob 6993dda42a |
| P05 R3 | PCB po recenzji niezależnej i poprawkach 2.10 (gałąź p05-r3-pcb: schemat z PR #7 + layout lokalny) | main @ cc0c43b, blob f064b12b9c |
| P09 R2 | PCB scalona lokalnie 1.10 (gałąź p09-r2-pcb; main czeka na push) | main @ cc0c43b, blob e325a5ac53 |
| P06 R2 | PCB po recenzji niezależnej i poprawkach 2.10 (gałąź p06-r2-pcb: schemat z PR #8 + przegląd i layout lokalny) | main @ cc0c43b, blob 508a9de996 |
| P10 R2 | PCB scalona lokalnie 1.10 (gałąź p10-r2-pcb; main czeka na push) | main @ cc0c43b, blob 22cf0803e6 |
| P11 R2 | schemat R2 scalony 4.10 (PCB w toku) | main @ cc0c43b, blob 89005c5eb4 |
| P04 R3 | PCB R3 z paczką zamówieniową (gałąź p04-r3-pcb, 5.10) | origin/p04-r3-pcb @ 702732a, blob 6552088694 |
| P07 S1 | schemat S1 (gałąź p07-s1-pcb, 5.10; PCB jeszcze nie ma — środki złączy z wymagań layoutu w README P07) | origin/p07-s1-pcb @ 584c1c8, blob ec769d1707 |
| P08 R2 | PCB R2 z paczką zamówieniową (gałąź p08-r2-pcb, 5.10) | origin/p08-r2-pcb @ d553f67, blob 85e1d6e64b |

## Złącza na krawędzi A (miejsca dla P12)

x — środek złącza w układzie stosu (x = 0 od strony panelu); z — spód płytki nad dnem obudowy (dno 8 mm, płytki 1,6 mm, dystanse z S1 §7).

| Poziom | Slot | x stosu [mm] | z spodu [mm] | Płytka | Złącze | Typ | x zmierzone w układzie płytki [mm] | Piny nieparzyste ≠ GND |
|---|---|---|---|---|---|---|---|---|
| 1 | S3 | 133,5 | 8 | P02 R4 | J_BP | IDC 2×10 | 133,5 | 15 P04_3V3; 17 PG_SEND |
| 2 | S1 | 26,5 | 34,6 | P03 R6 | J_BP1 | IDC 2×10 | 26,5 | 11 LOGGER_CURRENT_OK (statyczny; wyjatek od GND na nieparzystym); 13 MARK (przycisk; statyczny; wyjatek); 15 LOGGER_CLEAR (przycisk; statyczny; wyjatek); 17 ENA_DIAG (statyczny; wyjatek); 19 MOTOR_INA (MCP23017, statyczny; wyjatek) |
| 2 | S2 | 80 | 34,6 | P03 R6 | J_BP2 | IDC 2×10 | 80 | 17 5V_SYS (trzecia zyla zasilania P03 (30.09); wyjatek od GND na nieparzystym); 19 5V_SYS (zasilanie P03; wyjatek od GND na nieparzystym) |
| 2 | S3 | 133,5 | 34,6 | P03 R6 | J_BP3 | IDC 2×10 | 133,5 | 5 3V3_IO (zasilanie OE U14; wyjatek (zasilanie odsprzezone)); 9 SENSOR_ENABLE (MCP23017, statyczny; wyjatek); 13 CORE_LINK (3V3_CORE przez R14 1k, statyczny; wyjatek); 17 HW_ARMED (statyczny; wyjatek) |
| 3 | S1 | 26,5 | 56,2 | P05 R3 | J_BP1 | IDC 2×5 | 26,5 | — |
| 3 | S2 | 80 | 56,2 | P05 R3 | J_BP2 | IDC 2×10 | 80 | — |
| 3 | S3 | 133,5 | 56,2 | P09 R2 | J1 | IDC 2×8 | 26,5 | — |
| 4 | S2 | 80 | 77,8 | P06 R2 | J_BP | IDC 2×8 | 80 | — |
| 4 | S3 | 133,5 | 77,8 | P10 R2 | J1 | IDC 2×5 | 26,5 | — |
| 5 | S1 | 26,5 | 99,4 | P08 R2 | J_BP | IDC 2×8 | 26,5 | — |
| 5 | S2 | 80 | 99,4 | P07 S1 | J_BP1 | IDC 2×8 | — | — |
| 5 | S3 | 133,5 | 99,4 | P07 S1 | J_BP2 | IDC 2×8 | — | — |
| 6 | S1 | 26,5 | 121 | P04 R3 | J_BP1 | IDC 2×8 | 26,5 | — |
| 6 | S2 | 80 | 121 | P04 R3 | J_BP2 | IDC 2×10 | 80 | — |
| 6 | S3 | 133,5 | 121 | P04 R3 | J_BP3 | IDC 2×10 | 133,5 | — |
| panel | — | — | — | P11 R2 | J_P12 | IDC 2×10 | — | — |

## Sieci (bez GND)

| Sieć | Stan | Końce | Czeka na | Uwagi |
|---|---|---|---|---|
| 3V3_IO | OK | P02 R4 J_BP.8 ZRODLO; P02 R4 J_BP.10 ZRODLO; P03 R6 J_BP3.5 PWR; P09 R2 J1.4 PWR; P06 R2 J_BP.14 PWR; P10 R2 J1.4 PWR; P11 R2 J_P12.20 PWR; P04 R3 J_BP2.10 PWR; P04 R3 J_BP3.10 PWR; P07 S1 J_BP2.14 PWR; P08 R2 J_BP.4 PWR | — | — |
| 5V_SYS | OK | P02 R4 J_BP.2 ZRODLO; P02 R4 J_BP.4 ZRODLO; P02 R4 J_BP.6 ZRODLO; P03 R6 J_BP2.17 PWR; P03 R6 J_BP2.19 PWR; P03 R6 J_BP2.20 PWR; P05 R3 J_BP1.2 PWR; P05 R3 J_BP1.4 PWR; P09 R2 J1.2 PWR; P09 R2 J1.16 PWR; P06 R2 J_BP.10 PWR; P06 R2 J_BP.12 PWR; P10 R2 J1.2 PWR; P10 R2 J1.10 PWR; P04 R3 J_BP3.8 PWR; P07 S1 J_BP2.10 PWR; P07 S1 J_BP2.12 PWR; P08 R2 J_BP.2 PWR; P08 R2 J_BP.16 PWR | — | — |
| ADC_BUSY | OK | P03 R6 J_BP2.12 IN; P05 R3 J_BP2.12 OUT | — | — |
| ADC_CONVST | OK | P03 R6 J_BP2.10 OUT; P05 R3 J_BP2.10 IN | — | — |
| ADC_CS | OK | P03 R6 J_BP2.8 OUT; P05 R3 J_BP2.8 IN | — | — |
| ADC_DOUTA | OK | P03 R6 J_BP2.4 IN; P05 R3 J_BP2.4 OUT; P06 R2 J_BP.4 OUT; P07 S1 J_BP1.4 OUT | — | wspólna linia danych AD7606B / MCP3201 (P05, P06, P07), nadajnik wybierany przez CS |
| ADC_RESET | OK | P03 R6 J_BP2.18 OUT; P05 R3 J_BP2.18 IN | — | — |
| ADC_SCLK | OK | P03 R6 J_BP2.2 OUT; P05 R3 J_BP2.2 IN; P06 R2 J_BP.2 IN; P07 S1 J_BP1.2 IN | — | — |
| ADC_SDI | OK | P03 R6 J_BP2.6 OUT; P05 R3 J_BP2.6 IN | — | — |
| ARM_CLK | OK | P04 R3 J_BP2.6 OUT; P07 S1 J_BP2.6 IN | — | — |
| ARM_CONTACT | OK | P11 R2 J_P12.8 OUT; P04 R3 J_BP1.8 IN | — | — |
| CAN_RX | OK | P03 R6 J_BP1.8 IN; P10 R2 J1.8 OUT | — | — |
| CAN_TX | OK | P03 R6 J_BP1.6 OUT; P10 R2 J1.6 IN | — | — |
| CORE_LINK | OK | P03 R6 J_BP3.13 OUT; P04 R3 J_BP3.4 IN | — | — |
| CS_ILOG_N | OK | P03 R6 J_BP1.2 OUT; P06 R2 J_BP.6 IN | — | — |
| CS_ITEST_N | OK | P03 R6 J_BP1.4 OUT; P07 S1 J_BP1.6 IN | — | — |
| DAQ_OK | OK | P05 R3 J_BP1.6 OUT; P04 R3 J_BP1.16 IN | — | — |
| DRIVE_OK | OK | P04 R3 J_BP2.8 IN; P07 S1 J_BP2.8 OUT | — | — |
| ENA_DIAG | OK | P03 R6 J_BP1.17 IN; P07 S1 J_BP1.12 OUT | — | — |
| ENB_DIAG | OK | P03 R6 J_BP1.18 IN; P07 S1 J_BP1.14 OUT | — | — |
| HEARTBEAT | OK | P03 R6 J_BP3.16 OUT; P04 R3 J_BP3.16 IN | — | — |
| HW_ARMED | OK | P03 R6 J_BP3.17 IN; P04 R3 J_BP3.6 OUT | — | — |
| INTERLOCK | OK | P03 R6 J_BP3.20 IN; P04 R3 J_BP3.20 OUT | — | — |
| LOGGER_CLEAR | OK | P03 R6 J_BP1.15 IN; P11 R2 J_P12.15 OUT | — | — |
| LOGGER_CURRENT_OK | OK | P03 R6 J_BP1.11 IN; P06 R2 J_BP.8 OUT | — | — |
| MARK | OK | P03 R6 J_BP1.13 IN; P11 R2 J_P12.13 OUT | — | — |
| MCU_ARM | OK | P03 R6 J_BP3.18 OUT; P04 R3 J_BP3.18 IN | — | — |
| MEAS_EN | OK | P03 R6 J_BP2.14 OUT; P05 R3 J_BP2.14 IN | — | — |
| MECH_OK | OK | P11 R2 J_P12.4 OUT; P04 R3 J_BP1.4 IN | — | — |
| MOTOR_INA | OK | P03 R6 J_BP1.19 OUT; P07 S1 J_BP1.8 IN | — | — |
| MOTOR_INB | OK | P03 R6 J_BP1.20 OUT; P07 S1 J_BP1.10 IN | — | — |
| MOTOR_PERMIT | OK | P04 R3 J_BP2.2 OUT; P07 S1 J_BP2.2 IN | — | — |
| N_J_SCOPE_HOT | OK | P03 R6 J_BP1.10 OUT; P11 R2 J_P12.10 IN | — | — |
| P04_3V3 | OK | P02 R4 J_BP.15 PWR; P04 R3 J_BP2.14 ZRODLO | — | — |
| PANEL_3V3 | OK | P11 R2 J_P12.2 PWR; P04 R3 J_BP1.2 ZRODLO | — | — |
| PFAIL_N | OK | P02 R4 J_BP.14 OUT; P03 R6 J_BP2.16 IN | — | — |
| PG_LINK | OK | P02 R4 J_BP.18 PETLA; P04 R3 J_BP2.18 PETLA | — | — |
| PG_SEND | OK | P02 R4 J_BP.17 PETLA; P04 R3 J_BP2.20 PETLA | — | — |
| PSU_OK | OK | P02 R4 J_BP.12 OUT; P04 R3 J_BP2.12 IN | — | — |
| PWM | OK | P03 R6 J_BP3.14 OUT; P04 R3 J_BP3.14 IN | — | — |
| PWM_OUT | OK | P04 R3 J_BP2.4 OUT; P07 S1 J_BP2.4 IN | — | — |
| SAFE_N | OK | P02 R4 J_BP.16 OUT; P04 R3 J_BP2.16 IN; P07 S1 J_BP2.16 IN | — | — |
| SENSOR_ENABLE | OK | P03 R6 J_BP3.9 OUT; P04 R3 J_BP3.2 IN | — | — |
| SENSOR_HEALTHY | OK | P03 R6 J_BP1.12 IN; P08 R2 J_BP.10 OUT | — | — |
| SENSOR_OK | OK | P04 R3 J_BP1.12 IN; P08 R2 J_BP.8 OUT | — | — |
| SENSOR_PERMIT | OK | P04 R3 J_BP1.10 OUT; P08 R2 J_BP.6 IN | — | — |
| SPI3_MISO | OK | P03 R6 J_BP3.6 IN; P09 R2 J1.10 OUT | — | MISO MAX31856 przez bufor Hi-Z na P09, wspólne z kartą SD na P03 |
| SPI3_MOSI | OK | P03 R6 J_BP3.4 OUT; P09 R2 J1.8 IN | — | — |
| SPI3_SCLK | OK | P03 R6 J_BP3.2 OUT; P09 R2 J1.6 IN | — | — |
| STOP_NC_OUT | OK | P11 R2 J_P12.6 OUT; P04 R3 J_BP1.6 IN | — | — |
| SUP_N_OUT | OK | P03 R6 J_BP3.12 OUT; P04 R3 J_BP3.12 IN | — | — |
| TC1_CS | OK | P03 R6 J_BP3.8 OUT; P09 R2 J1.12 IN | — | — |
| TC2_CS | OK | P03 R6 J_BP3.10 OUT; P09 R2 J1.14 IN | — | — |
| TEST_KEY | OK | P03 R6 J_BP1.14 IN; P11 R2 J_P12.14 OUT; P04 R3 J_BP1.14 IN | — | — |
| TEST_PRESENT | OK | P03 R6 J_BP1.16 IN; P11 R2 J_P12.16 OUT | — | — |
| VBAT_SENSE | OK | P02 R4 J_BP.20 OUT; P05 R3 J_BP1.10 IN | — | — |

## Zasilanie przez P12

Styki IDC: ok. 1 A na styk (S1 §5).

- **5V_SYS:** P02 R4 3 piny (źródło), styki do 3 A; P03 R6 3 piny, styki do 3 A; P05 R3 2 piny, styki do 2 A; P09 R2 2 piny, styki do 2 A; P06 R2 2 piny, styki do 2 A; P10 R2 2 piny, styki do 2 A; P04 R3 1 pin, styki do 1 A; P07 S1 2 piny, styki do 2 A; P08 R2 2 piny, styki do 2 A
- **3V3_IO:** P02 R4 2 piny (źródło), styki do 2 A; P03 R6 1 pin, styki do 1 A; P09 R2 1 pin, styki do 1 A; P06 R2 1 pin, styki do 1 A; P10 R2 1 pin, styki do 1 A; P11 R2 1 pin, styki do 1 A; P04 R3 2 piny, styki do 2 A; P07 S1 1 pin, styki do 1 A; P08 R2 1 pin, styki do 1 A

Budżety 5V_SYS z dokumentów płytek (LOGGER): P03 R6 500 mA, P05 R3 140 mA, P09 R2 200 mA, P06 R2 180 mA, P10 R2 70 mA — **razem 1090 mA**. Źródło: TSR 2-2450, 2 A (F2 T1A po stronie wejścia); styki J_BP P02 R4: 3 A. Budżetów 3V3_IO płytki nie podają.

- P03 R6: Plytki/P03-R5-review/docs/ZASILANIE-RESET.md: do 0,5 A średnio i 0,8 A w impulsie (limit roboczy CORE)
- P05 R3: Plytki/P05-R2-review/docs/PROJEKT.md: cewki K1–K3 ok. 60 mA + budżet gałęzi filtrowanej 80 mA
- P09 R2: Plytki/P09-R2-review/docs/PROJEKT.md: rezerwa 200 mA dla obu modułów i logiki (5V_SYS albo 3V3_IO według JP1/JP2)
- P06 R2: Plytki/P06-R2-review/docs/PROJEKT.md: 180 mA z 5V_SYS w MEASURE
- P10 R2: Plytki/P10-R2-review/README.md: ok. 70 mA z 5 V (transceiver)

**Wariant pełny** dodatkowo: P04 R3 0 mA, P07 S1 110 mA, P08 R2 200 mA — **razem cały stos 1400 mA** wobec 1800 mA (90 % przetwornicy 2 A). 3V3_IO (płytki, które podają budżet): P04 R3 30 mA, P07 S1 5 mA, P08 R2 15 mA.

- P04 R3: Plytki/P04-R3-review/docs/PROJEKT.md: 5V_SYS bez odbiorcy (tylko kołek serwisowy przez 1 k), 3V3_IO rezerwa 30 mA
- P07 S1: Plytki/P07-S1-review/docs/PROJEKT.md: ok. 30 mA bez KPWR + ok. 80 mA cewki KPWR (G2RL-1-E DC5) = ok. 110 mA; 3V3_IO ≤ 5 mA
- P08 R2: Plytki/P08-R2-review/docs/PROJEKT.md: budżet 200 mA z 5 V (TPS2553, cewka K1, sensor), 15 mA z 3,3 V

## Pojemność na szynach 5 V

Sieci: 5V_SYS (wprost), 5V_M1 (P03: za kluczem Q1), 5VA_P05 (P05: za R1 1 Ω), 5VA_P06 (P06: za R6 1 Ω). Limit: 600 µF (karta TRACO TSR 2 (Plytki/P02-R3-review/reference/TRACO_TSR2.txt): „Capacitive Load … 5 Vout models: 600 µF max”, start 5 ms typ., przeciążenie: foldback).

| Płytka | µF | Największe | Źródło |
|---|---|---|---|
| P02 R4 | 22,1 | C22 22u / 16V (5V_SYS), C26 100nF / X7R (5V_SYS) | origin/main @ e77b317, blob ddb6f8c3d4 |
| P03 R6 | 11 | C14 10uF / 16V X7R (5V_M1), C13 1uF / 25V X7R (5V_SYS) | origin/p03-r6-pcb @ 7afd1b9, blob 8d637f6465 |
| P05 R3 | 222,7 | C1 220u / 16V (5VA_P05), C2 1u (5VA_P05), C23 1u (5V_SYS) | origin/p05-r3-pcb @ 88515c1, blob 74a6903ebc |
| P06 R2 | 220,3 | C3 220u / 16V (5VA_P06), C6 100n (5VA_P06), C9 100n (5VA_P06) | origin/p06-r2-pcb @ fcb65ad, blob 81dcb701df |
| P09 R2 | 4,7 | C5 4u7 (5V_SYS) | origin/p09-r2-pcb @ 7ac6d99, blob 8e5d587aa7 |
| P10 R2 | 4,8 | C4 4u7 (5V_SYS), C1 100n (5V_SYS) | origin/p10-r2-pcb @ 6ab03fb, blob d226cd47a3 |
| P04 R3 | 0 |  | origin/p04-r3-pcb @ 702732a, blob ef4db09be9 |
| P07 S1 | 10 | C9 10u (5V_SYS) | origin/p07-s1-pcb @ 584c1c8, blob 9957f9ae7a |
| P08 R2 | 24,1 | C10 22u / 25V (5V_SYS), C1 1u (5V_SYS), C9 1u (5V_SYS) | origin/p08-r2-pcb @ d553f67, blob f87d903f2b |

**Razem 519,7 µF.**

## Opisy położeń w specyfikacji S1

- Plytki/Format-S1/SPECYFIKACJA-FORMATU-S1.md: „Pinout P02 R4 J_BP (2×10, slot S3, środek x = 133,5 mm” — OK (slot ma środek 133,5 mm, płytka 133,5 mm)

