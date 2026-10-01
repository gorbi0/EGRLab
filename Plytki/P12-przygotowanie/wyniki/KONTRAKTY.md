# Kontrakty krawędzi A (J_BP) — mapa dla P12

*Plik generowany przez `src/kontrakty.py` z `zrodla.json`; nie edytować ręcznie.*

**Wynik:** 0 błędów, 0 uwag; sieci: OK 17, czeka 29, UWAGA 0, BŁĄD 0.

## Źródła

| Płytka | Stan | Pinout |
|---|---|---|
| P02 R4 | PCB scalona (PR #4), paczka produkcyjna | origin/main @ 9b50f9c, blob c2cfb86198 |
| P03 R6 | PCB do recenzji (gałąź p03-r6-pcb) | origin/p03-r6-pcb @ b094fa7, blob 6993dda42a |
| P05 R3 | schemat R3 do recenzji (PR #7, gałąź p05-s1; poprawki lokalne 1.10) | origin/p05-s1 @ 9417a37, blob f064b12b9c |
| P09 R2 | PCB do recenzji (gałąź p09-r2-pcb) | origin/p09-r2-pcb @ 7ac6d99, blob e325a5ac53 |
| P06 | czeka na decyzje: bocznik 2512, przełącznik BYPASS, klasa 1/3 albo 2/3 | — |
| P10 R2 | PCB do recenzji (gałąź p10-r2-pcb) | origin/p10-r2-pcb @ 6ab03fb, blob 22cf0803e6 |
| P11 | czeka: nowy panel, taśma do P12 (S1 §8: 1 × 2×10) | — |
| P04 | wariant pełny; S1 §7: na poziomie 4 zostaje tylko S2 | — |
| P07 | wariant pełny | — |
| P08 | wariant pełny | — |

## Złącza na krawędzi A (miejsca dla P12)

x — środek złącza w układzie stosu (x = 0 od strony panelu); z — spód płytki nad dnem obudowy (dno 8 mm, płytki 1,6 mm, dystanse z S1 §7).

| Poziom | Slot | x stosu [mm] | z spodu [mm] | Płytka | Złącze | Typ | x zmierzone w układzie płytki [mm] | Piny nieparzyste ≠ GND |
|---|---|---|---|---|---|---|---|---|
| 1 | S3 | 133,5 | 8 | P02 R4 | J_BP | IDC 2×10 | 133,5 | 15 P04_3V3; 17 PG_SEND |
| 2 | S1 | 26,5 | 34,6 | P03 R6 | J_BP1 | IDC 2×10 | 26,5 | 11 LOGGER_CURRENT_OK (statyczny; wyjatek od GND na nieparzystym); 13 MARK (przycisk; statyczny; wyjatek); 15 LOGGER_CLEAR (przycisk; statyczny; wyjatek); 17 ENA_DIAG (statyczny; wyjatek); 19 MOTOR_INA (MCP23017, statyczny; wyjatek) |
| 2 | S2 | 80 | 34,6 | P03 R6 | J_BP2 | IDC 2×10 | 80 | 17 5V_SYS (trzecia zyla zasilania P03 (30.09); wyjatek od GND na nieparzystym); 19 5V_SYS (zasilanie P03; wyjatek od GND na nieparzystym) |
| 2 | S3 | 133,5 | 34,6 | P03 R6 | J_BP3 | IDC 2×10 | 133,5 | 5 3V3_IO (zasilanie OE U14; wyjatek (zasilanie odsprzezone)); 9 SENSOR_ENABLE (MCP23017, statyczny; wyjatek); 13 CORE_LINK (3V3_CORE przez R14 1k, statyczny; wyjatek); 17 HW_ARMED (statyczny; wyjatek) |
| 3 | S1 | 26,5 | 56,2 | P05 R3 | J_BP1 | IDC 2×5 | — | — |
| 3 | S2 | 80 | 56,2 | P05 R3 | J_BP2 | IDC 2×10 | — | — |
| 3 | S3 | 133,5 | 56,2 | P09 R2 | J1 | IDC 2×8 | 26,5 | — |
| 4 | S1 | — | 77,8 | P06 | ? | ? | — | — |
| 4 | S3 | 133,5 | 77,8 | P10 R2 | J1 | IDC 2×5 | 26,5 | — |
| 5 | S1 | — | 99,4 | P08 | ? | ? | — | — |
| 5 | S2/S3 | — | 99,4 | P07 | ? | ? | — | — |

## Sieci (bez GND)

| Sieć | Stan | Końce | Czeka na | Uwagi |
|---|---|---|---|---|
| ADC_DOUTA | czeka | P03 R6 J_BP2.4 IN; P05 R3 J_BP2.4 OUT | P06, P07 | wspólna linia danych AD7606B / MCP3201 (P05, P06, P07), nadajnik wybierany przez CS |
| ADC_SCLK | czeka | P03 R6 J_BP2.2 OUT; P05 R3 J_BP2.2 IN | P06, P07 | — |
| CORE_LINK | czeka | P03 R6 J_BP3.13 OUT | P04 | — |
| CS_ILOG_N | czeka | P03 R6 J_BP1.2 OUT | P06 | — |
| CS_ITEST_N | czeka | P03 R6 J_BP1.4 OUT | P07 | — |
| DAQ_OK | czeka | P05 R3 J_BP1.6 OUT | P04 | — |
| ENA_DIAG | czeka | P03 R6 J_BP1.17 IN | P07 | — |
| ENB_DIAG | czeka | P03 R6 J_BP1.18 IN | P07 | — |
| HEARTBEAT | czeka | P03 R6 J_BP3.16 OUT | P04 | — |
| HW_ARMED | czeka | P03 R6 J_BP3.17 IN | P04 | — |
| INTERLOCK | czeka | P03 R6 J_BP3.20 IN | P04 | — |
| LOGGER_CLEAR | czeka | P03 R6 J_BP1.15 IN | P11 | — |
| LOGGER_CURRENT_OK | czeka | P03 R6 J_BP1.11 IN | P06 | — |
| MARK | czeka | P03 R6 J_BP1.13 IN | P11 | — |
| MCU_ARM | czeka | P03 R6 J_BP3.18 OUT | P04 | — |
| MOTOR_INA | czeka | P03 R6 J_BP1.19 OUT | P07 | — |
| MOTOR_INB | czeka | P03 R6 J_BP1.20 OUT | P07 | — |
| N_J_SCOPE_HOT | czeka | P03 R6 J_BP1.10 OUT | P11 | — |
| P04_3V3 | czeka | P02 R4 J_BP.15 PWR | P04 | — |
| PG_LINK | czeka | P02 R4 J_BP.18 PETLA | P04 | — |
| PG_SEND | czeka | P02 R4 J_BP.17 PETLA | P04 | — |
| PSU_OK | czeka | P02 R4 J_BP.12 OUT | P04 | — |
| PWM | czeka | P03 R6 J_BP3.14 OUT | P04 | — |
| SAFE_N | czeka | P02 R4 J_BP.16 OUT | P04 | — |
| SENSOR_ENABLE | czeka | P03 R6 J_BP3.9 OUT | P04 | — |
| SENSOR_HEALTHY | czeka | P03 R6 J_BP1.12 IN | P08 | — |
| SUP_N_OUT | czeka | P03 R6 J_BP3.12 OUT | P04 | — |
| TEST_KEY | czeka | P03 R6 J_BP1.14 IN | P11 | — |
| TEST_PRESENT | czeka | P03 R6 J_BP1.16 IN | P11 | — |
| 3V3_IO | OK | P02 R4 J_BP.8 ZRODLO; P02 R4 J_BP.10 ZRODLO; P03 R6 J_BP3.5 PWR; P09 R2 J1.4 PWR; P10 R2 J1.4 PWR | — | — |
| 5V_SYS | OK | P02 R4 J_BP.2 ZRODLO; P02 R4 J_BP.4 ZRODLO; P02 R4 J_BP.6 ZRODLO; P03 R6 J_BP2.17 PWR; P03 R6 J_BP2.19 PWR; P03 R6 J_BP2.20 PWR; P05 R3 J_BP1.2 PWR; P05 R3 J_BP1.4 PWR; P09 R2 J1.2 PWR; P09 R2 J1.16 PWR; P10 R2 J1.2 PWR; P10 R2 J1.10 PWR | — | — |
| ADC_BUSY | OK | P03 R6 J_BP2.12 IN; P05 R3 J_BP2.12 OUT | — | — |
| ADC_CONVST | OK | P03 R6 J_BP2.10 OUT; P05 R3 J_BP2.10 IN | — | — |
| ADC_CS | OK | P03 R6 J_BP2.8 OUT; P05 R3 J_BP2.8 IN | — | — |
| ADC_RESET | OK | P03 R6 J_BP2.18 OUT; P05 R3 J_BP2.18 IN | — | — |
| ADC_SDI | OK | P03 R6 J_BP2.6 OUT; P05 R3 J_BP2.6 IN | — | — |
| CAN_RX | OK | P03 R6 J_BP1.8 IN; P10 R2 J1.8 OUT | — | — |
| CAN_TX | OK | P03 R6 J_BP1.6 OUT; P10 R2 J1.6 IN | — | — |
| MEAS_EN | OK | P03 R6 J_BP2.14 OUT; P05 R3 J_BP2.14 IN | — | — |
| PFAIL_N | OK | P02 R4 J_BP.14 OUT; P03 R6 J_BP2.16 IN | — | — |
| SPI3_MISO | OK | P03 R6 J_BP3.6 IN; P09 R2 J1.10 OUT | — | MISO MAX31856 przez bufor Hi-Z na P09, wspólne z kartą SD na P03 |
| SPI3_MOSI | OK | P03 R6 J_BP3.4 OUT; P09 R2 J1.8 IN | — | — |
| SPI3_SCLK | OK | P03 R6 J_BP3.2 OUT; P09 R2 J1.6 IN | — | — |
| TC1_CS | OK | P03 R6 J_BP3.8 OUT; P09 R2 J1.12 IN | — | — |
| TC2_CS | OK | P03 R6 J_BP3.10 OUT; P09 R2 J1.14 IN | — | — |
| VBAT_SENSE | OK | P02 R4 J_BP.20 OUT; P05 R3 J_BP1.10 IN | — | — |

## Zasilanie przez P12

Styki IDC: ok. 1 A na styk (S1 §5).

- **5V_SYS:** P02 R4 3 piny (źródło), styki do 3 A; P03 R6 3 piny, styki do 3 A; P05 R3 2 piny, styki do 2 A; P09 R2 2 piny, styki do 2 A; P10 R2 2 piny, styki do 2 A
- **3V3_IO:** P02 R4 2 piny (źródło), styki do 2 A; P03 R6 1 pin, styki do 1 A; P09 R2 1 pin, styki do 1 A; P10 R2 1 pin, styki do 1 A

Budżety 5V_SYS z dokumentów płytek (LOGGER): P03 R6 500 mA, P05 R3 140 mA, P09 R2 200 mA, P06 180 mA, P10 R2 70 mA — **razem 1090 mA**. Źródło: TSR 2-2450, 2 A (F2 T1A po stronie wejścia); styki J_BP P02 R4: 3 A. Budżetów 3V3_IO płytki nie podają.

- P03 R6: Plytki/P03-R5-review/docs/ZASILANIE-RESET.md: do 0,5 A średnio i 0,8 A w impulsie (limit roboczy CORE)
- P05 R3: Plytki/P05-R2-review/docs/PROJEKT.md: cewki K1–K3 ok. 60 mA + budżet gałęzi filtrowanej 80 mA
- P09 R2: Plytki/P09-R2-review/docs/PROJEKT.md: rezerwa 200 mA dla obu modułów i logiki (5V_SYS albo 3V3_IO według JP1/JP2)
- P06: Plytki/P06-R1-review/docs/PROJEKT.md: 180 mA z 5V_SYS w MEASURE
- P10 R2: Plytki/P10-R2-review/README.md: ok. 70 mA z 5 V (transceiver)

## Pojemność na szynach 5 V

Sieci: 5V_SYS (wprost), 5V_M1 (P03: za kluczem Q1), 5VA_P05 (P05: za R1 1 Ω), 5VA_P06 (P06: za R6 1 Ω). Limit: 600 µF (karta TRACO TSR 2 (Plytki/P02-R3-review/reference/TRACO_TSR2.txt): „Capacitive Load … 5 Vout models: 600 µF max”, start 5 ms typ., przeciążenie: foldback).

| Płytka | µF | Największe | Źródło |
|---|---|---|---|
| P02 R4 | 22,1 | C22 22u / 16V (5V_SYS), C26 100nF / X7R (5V_SYS) | origin/main @ 9b50f9c, blob c2cfb86198 |
| P03 R6 | 11 | C14 10uF / 16V X7R (5V_M1), C13 1uF / 25V X7R (5V_SYS) | origin/p03-r6-pcb @ b094fa7, blob eb3e1536f1 |
| P05 R3 | 222,7 | C1 220u / 16V (5VA_P05), C2 1u (5VA_P05), C23 1u (5V_SYS) | origin/p05-s1 @ 9417a37, blob 3c516582ab |
| P06 (R1; C3 220 µF według decyzji 1.10, do rewizji S1) | 220,3 | C3 220u / 16V (5VA_P06), C6 100n (5VA_P06), C9 100n (5VA_P06) | origin/main @ 9b50f9c, blob bfe61cbcca |
| P09 R2 | 4,7 | C5 4u7 (5V_SYS) | origin/p09-r2-pcb @ 7ac6d99, blob 8e5d587aa7 |
| P10 R2 | 4,8 | C4 4u7 (5V_SYS), C1 100n (5V_SYS) | origin/p10-r2-pcb @ 6ab03fb, blob d226cd47a3 |

**Razem 485,6 µF.**

## Opisy położeń w specyfikacji S1

- Plytki/Format-S1/SPECYFIKACJA-FORMATU-S1.md: „Pinout P02 R4 J_BP (2×10, slot S3, środek x = 133,5 mm” — OK (slot ma środek 133,5 mm, płytka 133,5 mm)

