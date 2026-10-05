# Moduł 2 × BTS7960B — zdjęcia i pomiary przed projektem P07 S1 (5.10.2026)

Decyzja użytkownika (EGRLab-AKTYWNE, „P07 DRIVE — WSTRZYMANE”): P07 projektujemy pod moduł z dwoma BTS7960B dopiero po sprawdzeniu jego rzeczywistego wykonania. Moduł jest u użytkownika (5.10). Wyniki wpisz w tabelach albo prześlij zdjęcia i liczby — Claude przeniesie je do tego pliku.

## Ustalone ze zdjęć sprzedawcy (5.10.2026)
- Moduł IBT-2 / HW-39: 2 × BTS7960B (U2, U3), bufor **74HC244D** (U1), złącze sterujące 2 × 4 kątowe: RPWM / LPWM, R_EN / L_EN, R_IS / L_IS, VCC / GND; zaciski B−, B+, M+, M−; elektrolit 330 µF na B+.
- Płytka 49,6 × 49,3 mm, 4 otwory w narożnikach; **radiator pod płytką, 22,8 mm wysokości**, 31,9 mm szerokości.
- **Wniosek:** moduł nie mieści się w stosie S1 (16,5 mm nad płytką; moduł ok. 40–45 mm z radiatorem, zaciskami i elektrolitem) i potrzebuje przepływu powietrza → **moduł poza stosem** (ścianka obudowy, radiator do wentylacji), **P07 S1** w stosie (poziom 5, S2–S3) z logiką, bocznikiem, INA240, MCP3201, OC z zatrzaskiem, KPWR i buforem 3,3 → 5 V (74HC244 przy VCC 5 V wymaga VIH ok. 3,5 V); P07 ↔ moduł: wiązka 8 żył sterowania + przewody mocy.
- **Minimum do zmierzenia przed projektem P07:** C2 (OE 74HC244), C3 (rezystory R_IS / L_IS), C4 (podciągnięcia wejść), B2 (otwory montażowe). Pozostałe punkty — przy odbiorze.

## Wyniki pomiarów użytkownika (5.10.2026, moduł bez zasilania)
| Pomiar | Wynik | Wniosek dla P07 |
|---|---|---|
| 74HC244 pin 1 (1OE) i pin 19 (2OE) ↔ GND | 0 Ω | bufor zawsze aktywny — brak blokady na module; blokada RPWM/LPWM/EN po stronie P07 (SAFE_N, MOTOR_PERMIT z P04) |
| 74HC244 pin 20 ↔ VCC złącza | 0 Ω | bufor zasilany z VCC złącza (5 V z P07) |
| R_IS / L_IS ↔ GND | 10 kΩ / 10 kΩ | V_IS ≈ I_L / 8500 × 10 kΩ ≈ 1,2 V/A (6 A → ok. 7 V) — na P07 dzielnik + ogranicznik, tylko diagnostyka; pomiar prądu: własny bocznik + INA240 |
| RPWM, LPWM, R_EN, L_EN ↔ GND | ok. 30 kΩ każde | wejścia ściągnięte w dół — wolne wejście = mostek wyłączony |
| te same ↔ VCC (COM na VCC, tryb diody) | 0,67 V każde | tylko dioda ESD bufora, bez podciągania do VCC; sterowanie 5 V (74HC244 przy 5 V: VIH ≥ 3,5 V) |
| GND złącza ↔ B− (COM na B−) | 508 mV | **do sprawdzenia ciągłością / Ω** — odczyt wygląda na tryb diody |
| Otwory montażowe | Ø3, rozstaw 40 × 40 mm | montaż na ściance, 4 × M3 |
| R_EN ↔ L_EN | niepołączone | każda połowa mostka wyłączana osobno |
| RPWM → 74HC244 | pin 2 (1A1) | — |

**Bezpieczeństwo:** kroki A–C bez zasilania. W kroku D tylko 5 V logiki z zasilacza z ograniczeniem prądu 50 mA, bez napięcia silnika. Krok E (napięcie silnika) dopiero po D i z ograniczeniem prądu 0,5 A, bez silnika albo z małym obciążeniem.

## A. Zdjęcia (ostre, z linijką w kadrze)
1. Góra i spód modułu, na wprost.
2. Zbliżenia oznaczeń: oba BTS7960B, układ bufora (74HC244 lub inny), ewentualny stabilizator, rezystory przy wyprowadzeniach IS.
3. Złącze sterujące (zwykle 8 pinów: RPWM, LPWM, R_EN, L_EN, R_IS, L_IS, VCC, GND) z widocznymi opisami.
4. Zaciski mocy (B+, B−, M+, M−) i radiator z boku (wysokość).

## B. Wymiary (suwmiarka)
| # | Co | Wynik |
|---|---|---|
| B1 | Obrys płytki modułu (dł. × szer.) | |
| B2 | Otwory montażowe: liczba, średnica, położenie od dwóch krawędzi | |
| B3 | Wysokość: najwyższy element nad płytką (radiator), wyprowadzenia pod płytką | |
| B4 | Złącze sterujące: raster, liczba pinów, położenie pinu 1 od krawędzi, kierunek (pionowe / kątowe) | |
| B5 | Zaciski mocy: raster, położenie, maks. przekrój przewodu (opis na zacisku) | |

## C. Połączenia bez zasilania (omomierz / ciągłość)
| # | Sprawdzić | Wynik |
|---|---|---|
| C1 | Każdy pin złącza sterującego → do którego pinu bufora (lub bezpośrednio do BTS7960B: IN, INH, IS) | |
| C2 | Zasilanie bufora: pin VCC bufora → VCC złącza? Pin OE (1G, 2G) → GND czy inny sygnał? | |
| C3 | R_IS / L_IS: rezystor do GND na module? wartość; czy IS idzie przez bufor, czy wprost | |
| C4 | Rezystory podciągające / ściągające na RPWM, LPWM, R_EN, L_EN (wartość, do VCC czy GND) | |
| C5 | Czy GND logiki jest połączony z B− (masa mocy) i gdzie | |
| C6 | Czy R_EN i L_EN są połączone ze sobą na module | |

## D. Zasilanie tylko logiki (VCC = 5 V, limit 50 mA, bez B+)
| # | Sprawdzić | Wynik |
|---|---|---|
| D1 | Pobór prądu VCC (wejścia wolne / wszystkie na GND) | |
| D2 | Napięcie na wejściach IN/INH BTS7960B przy RPWM/LPWM/EN = 0 V i = 3,3 V (czy 3,3 V z ESP32 wystarcza) | |
| D3 | Stan wejść przy pinach sterujących niepodłączonych (pływające → jaki stan na INH?) | |

## E. Z napięciem silnika (B+ = 12 V, limit 0,5 A; najpierw bez obciążenia, potem rezystor mocy lub żarówka)
| # | Sprawdzić | Wynik |
|---|---|---|
| E1 | Pobór B+ w spoczynku (EN = 0) | |
| E2 | EN = 1, RPWM = 1, LPWM = 0: napięcie M+ / M− | |
| E3 | Napięcie R_IS przy znanym prądzie obciążenia (np. 0,2 / 0,4 A) — przelicznik kILIS | |
| E4 | PWM 1–20 kHz na RPWM (generator lub ESP32): przebieg M+ na oscyloskopie, czasy narastania | |
| E5 | Hamowanie: EN = 1, RPWM = LPWM = 1 oraz RPWM = LPWM = 0 — co dzieje się na M+ / M− | |

Po tych danych: projekt P07 S1 (poziom 5, sloty S2–S3, klasa 2/3) jako płytka nośna modułu z własnym bocznikiem, INA240, MCP3201, lokalnym zabezpieczeniem nadprądowym, zatrzaskiem i KPWR (wymagania z EGRLab-AKTYWNE).
