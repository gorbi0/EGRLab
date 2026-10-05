# Moduł 2 × BTS7960B — zdjęcia i pomiary przed projektem P07 S1 (5.10.2026)

Decyzja użytkownika (EGRLab-AKTYWNE, „P07 DRIVE — WSTRZYMANE”): P07 projektujemy pod moduł z dwoma BTS7960B dopiero po sprawdzeniu jego rzeczywistego wykonania. Moduł jest u użytkownika (5.10). Wyniki wpisz w tabelach albo prześlij zdjęcia i liczby — Claude przeniesie je do tego pliku.

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
