# P00-R3 — wiązka stanowiskowa do P04-R2.1

Dotyczy zamkniętej **P04-R2.1**. Zastępuje mapę P04 v6.1 z P00-R2 (J13–J20). Mapę sprawdza `src/check_harness.py` względem zamrożonej netlisty `reference/P04-R2.1-parts.json`: sieć, pulldown, rodzaj wejścia, poziom H i zgodność tych tabel. Po stronie P04 obowiązuje `docs/P00-P04.md` z pakietu P04-R2.1 (kopia: `reference/P04-R2.1-P00-P04.md`). Tutaj opisano tylko okablowanie. Kolejne próby są w P04 `docs/ODBIOR.md` (E01–E22; kopia: `reference/P04-R2.1-ODBIOR.md`).

## Zasady

**Zasilanie osobno.** P00 z własnego zasilacza 9–12 V na J10. P04 z zasilacza 3,3 V z ograniczeniem 50 mA przez wtyk J1: J1.3 = 3V3_IO, J1.2 i J1.4 = GND, J1.1 (5V_SYS) niepodłączony. **Nie łączyć szyn 3V3 obu płytek.** P00 nie zasila P04.

**TP1 w tym dokumencie to TP1 na P04** (3V3_IO), źródło gałęzi 1 kΩ. TP1 na P00 to szyna samego P00; nie jest źródłem gałęzi ani zasilaniem P04. J8.1 na P04 (PANEL_3V3 za R40 100 Ω) też nie jest źródłem gałęzi. Pięć gałęzi obniżyłoby tam napięcie i zaniżyło SAFE_N w E05.

**Masa pierwsza.** Najpierw GND, potem sygnały. Każde Jn.2 P00 to GND. HB prowadzić skręcony z przewodem GND.

**Przewody** do 20 cm, opisane na obu końcach. Po stronie P00 żeńskie Dupont 2,54 mm. Po stronie P04 oprawione wtyki: IDC do J2–J6, Mini-Fit Jr do J1, J7 i J8. Luźny Dupont nie trzyma się na Mini-Fit. Kierować się numerami pinów producenta, nie położeniem lewo/prawo.

Do odbioru P04 odłączyć CORE, DAQ, DRIVE, SENSOR, PG, panel i aktuator. P00 i wiązka zastępują ich wejścia.

## Kanały P00 → wejścia P04

H min: szyna P00 3,14 V, rezystory ±1 %.

| P00 | P04-R2.1 | Sieć P04 | Odbiornik w P04 | H min na bramce |
|---|---|---|---|---|
| J1.1 PSU (SW1) | J6.1 | PSU_OK | U9 74LVC125A, R18 10 kΩ | 2,85 V (VIH 2,0 V) |
| J2.1 DAQ (SW2) | J5.1 | DAQ_OK | U9 74LVC125A, R19 10 kΩ | 2,85 V |
| J3.1 DRIVE (SW3) | J3.7 | DRIVE_OK | U10 74LVC125A, R20 10 kΩ | 2,85 V |
| J4.1 SENSOR (SW4) | J4.3 | SENSOR_OK | U10 74LVC125A, R21 10 kΩ | 2,85 V |
| J5.1 CORE (SW5) | J2.13 | CORE_LINK | U9 74LVC125A, R16 10 kΩ | 2,85 V |
| J6.1 PG (SW6) | J7.5 | PG_LINK | U10 74LVC125A, R22 10 kΩ | 2,85 V |
| J7.1 KEY (SW7) | J8.3 | TEST_KEY | R41 1 kΩ, bramki U4/U7 74HC08, R23 10 kΩ | 2,61 V (ok. 2,36 V) |
| J8.1 MECH (SW8) | J8.4 | MECH_OK | R42 1 kΩ, bramka U7 74HC08, R24 10 kΩ (jeden pulldown) | 2,61 V |
| J9.1 HB (U1) | J2.3 | HEARTBEAT | U8 74LVC125A, R13 10 kΩ | typowo ok. 2,45 V; odbiór P00: ≥ 2,4 V na J9 z 10 kΩ |

## Gałęzie 1 kΩ z TP1 P04

Jeden przewód z TP1 P04 rozgałęziony na pięć gałęzi. Każda ma własny rezystor 1 kΩ / 1 % / 0,25 W (izolowany, opisany) i rozłączenie. To wyposażenie stanowiska, nie elementy PCB.

| Gałąź | Połączenie | Sieć P04 | H min | Próby P04 |
|---|---|---|---|---|
| H_SUP | TP1 → 1 kΩ → zworka → J2.15 | SUP_N | 3,10 V (R17 100 kΩ) | E04, E05, E12 |
| H_MCU | TP1 → 1 kΩ → zworka → J2.5 | MCU_ARM | 2,84 V | E04, E06, E07 |
| H_HB | TP1 → 1 kΩ → wybierak → J2.3 | HEARTBEAT | 2,84 V | E11 (stałe H), E13 |
| H_PWM | TP1 → 1 kΩ → zworka → J2.1 | PWM | 2,84 V | E04, E06; w E19 zamiast niej generator 3,3 V przez 1 kΩ |
| H_SENSOR | TP1 → 1 kΩ → zworka → J2.11 | SENSOR_ENABLE | 2,84 V | E04, E08 |

**Wybierak HB:** listwa 1×3 ze zworką. Środek idzie do J2.3 P04, jeden skraj do J9.1 P00, drugi do gałęzi H_HB. Zworka fizycznie wyklucza równoległe połączenie obu źródeł. Nie uzyskiwać H przez zwieranie J9 do 3V3.

## Styki

| Styk | Połączenie | Sieci | Użycie |
|---|---|---|---|
| STOP (NC) | J8.1 – J8.7 | PANEL_3V3 – STOP_NC_OUT | zamknięty w pracy; otwarcie w E10 |
| ARM (NO, chwilowy) | J8.9 – J8.10 | ARM_CONTACT – GND | E06, E14, E15 |
| SAFE_N_TEST (NO, chwilowy) | J7.2 – J7.3 | SAFE_N – GND | E10; nigdy nie podawać H na SAFE_N |

## Tylko pomiar

Wyjścia P04 mierzyć sondą o dużej impedancji. Nie podłączać do nich źródeł P00 ani gałęzi:

| Sieć | Pin P04 | Źródło w P04 |
|---|---|---|
| MOTOR_PERMIT | J3.1 | U5 74HC08 |
| PWM_OUT | J3.3 | U4 74HC08 |
| ARM_CLK | J3.5 | U2 74HC14 |
| SENSOR_PERMIT | J4.1 | U5 74HC08 |
| HW_ARMED | J2.7 | U3 74HC74 |
| INTERLOCK | J2.9 | U7 74HC08 |
| SAFE_N | J3.9, J7.2 | otwarte kolektory Q1–Q3 (tylko styk do GND) |

Nie pomylić J3.7 (wejście DRIVE_OK) z J3.1, J3.3, J3.5 i J3.9.

GND na P04: J2.2/6/8/10/12/14/16, J3.4/6/8/10, J4.4, J5.2, J6.2, J7.3/6, J8.2/10, J1.2/4. Pozycje kluczy J2.4, J3.2, J4.2, J5.4 i J6.5 są NC. W adapterach testowych zaślepka klucza nie jest potrzebna.

## Przebieg

1. Bez zasilania: ciągłość każdej żyły i brak połączenia między szynami 3V3. P00 wszystko w L, SW9 STOP, zworki gałęzi otwarte, wybierak HB na J9.1, STOP zamknięty.
2. Połączyć GND. Zasilić P04 (E01), potem P00. Mierzyć H/L na P04, nie tylko patrzeć na LED P00. LED pokazuje stan źródła przed 1 kΩ.
3. Próby według P04 `ODBIOR.md`. Przy każdym wyniku zapisać położenie przełączników, zworek i wybieraka HB.

| Próba P04 | Co z P00 i wiązki |
|---|---|
| E03 | Wszystkie źródła L, STOP zamknięty, SW9 STOP |
| E04 | Po jednym: J1–J6, J9 (HB) oraz H_SUP, H_MCU, H_PWM, H_SENSOR — H, L i odpięcie (11 buforów) |
| E05 | J1–J8 w H, H_SUP włączona, STOP zamknięty, SW9 RUN |
| E06–E08 | H_MCU, ARM, H_PWM, H_SENSOR |
| E09 | Kolejno J1–J8 na L; powrót nie może uzbroić bez ARM |
| E10 | Otwarcie STOP; osobno SAFE_N_TEST |
| E11 | SW9 RUN → STOP (stałe L); odpięcie J9.1; wybierak na H_HB (stałe H) |
| E12 | H_SUP rozłączona (SUP_N w L przez R17) |
| E13 | Start z wybierakiem na H_HB |
| E14, E15 | ARM |
| E17 | Wyjątek: wyłączyć P04 przy źródłach P00 w H |
| E18 | Wyjmowanie adapterów po wyłączeniu |
| E19 | Generator 3,3 V przez 1 kΩ zamiast H_PWM |
| E21 | Dodatkowo zwora TP15–GND na P04 (poza wiązką) |

4. Poza E17 przed wyłączeniem P04 ustawić źródła P00 w L i SW9 STOP, rozłączyć gałęzie.
5. Po odbiorze zdjąć zworki i wiązkę przed integracją systemu. Styki obecności LOGGER sprawdza się później z P11; P00 ich nie zastępuje.
