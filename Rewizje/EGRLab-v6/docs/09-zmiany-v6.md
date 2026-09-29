# Rejestr decyzji V6

Ocena Opusa oraz nasza odpowiedź na nią są zachowane w `reference/`. Poniżej rozstrzygnięcia wdrożone do modelu połączeń, generatora, zakupów i programu.

| Uwagi / decyzja | Realizacja V6 |
|---|---|
| Symbol ADC wskazywał starszy AD7606 | P05 U1 = **AD7606BBSTZ**, LQFP64, raster 0,5 mm; bez kupnego modułu ADC. CONVST=9, WR=10, VDRIVE=23=3,3 V. |
| Niepełny kod TLV1702 | P05 U6 i P07 U4 = **TLV1702AQDGKRQ1**, VSSOP8/DGK, 0,65 mm; bez adaptera na tych PCB. |
| Wykonanie i liczba adapterów | P01/P05/P07: PCB 2L; pozostałe trwała uniwersalna/nośnik. 26 układów 74LVC125AD, z tego 18 adapterów SO14, pozostałe 8 bezpośrednio na P05/P07. Pełna lista innych adapterów w adaptery.csv. |
| Samotne wyjścia analogowe | Usunięte P06 RO2/I_LOG_SER oraz P07 RO1/I_TEST_SER. Punkty J_ANALOG_TP pozostają. |
| Dodatkowa poprawka wykryta podczas V6: P01 FAULT | R30 otrzymuje rzeczywiste 3V3_IO z PG pin 1. Dawna lokalna nazwa P01_BOARD_3V3 odcinała polaryzację Q7 od tego zasilania. J1/J2/J4/J_PRES są teraz tylko polami kontrolnymi, bez dodatkowych gniazd w BOM; robocze połączenia prowadzą przez BAT/SUPPLY/PG. |
| STOP_PRESSED | Pomocniczy NO niepodłączony, bez fikcyjnej sieci i bez GPB7. Sprzętowy tor NC pozostaje. |
| LOCAL_ARM_CLK | Nieużyta bramka U_GATE: 4/5=GND, 6=NC. Zatrzask ma nadal CLK=ARM_CLK_P07 i D=PERMIT_N. |
| VREF MCP3201 | MCP1525 → VREF bez rezystora szeregowego; C_REF=4,7 µF oraz 100 nF równolegle do masy, lokalnie. Firmware ma 100 ms budżetu ustalania na starcie. Odbiór obejmuje także powrót po zaniku zasilania. |
| Zegary na pierwsze uruchomienie | AD: 1 MHz, SD: 4 MHz, MCP3201: 500 kHz. Pierwsze dwa ustawiane przez Kconfig; limity czasowe próbek nadal obowiązują. |
| ARM po zmianie banku/konfiguracji | Opisane ponowne fizyczne ARM po wznowieniu akwizycji; pauza może wygasić watchdog. Bez automatycznego ponownego uzbrojenia. |
| Przerwa kierunku | Wyłączenie mostka → potwierdzony zapis INA/INB → 5 ms → zezwolenie. Jest to zwłoka po zmianie wejść przy wyłączonym mostku. |
| Kolejka i eksport starszych logów | Zachowane rozwiązania V5: bufor zdarzeń 256 KiB, osobna kolejka konfiguracji; ostrzeżenia przy niepełnych metadanych; brak pozornych wartości fizycznych. |
| Test interlocku | Nadal odczytuje rzeczywiste piny bramek z netlisty i sprawdza wszystkie 128 kombinacji gotowości. |
| Złącza i naprawa | Lutowane PTH po stronie modułu; wymiana modułu razem z jego krótką wiązką. Wyjątki: DAQ B2B, fabryczne moduły, adaptery zewnętrzne. |

## Pojedyncze większe rezystory

Zastąpiono **18 par = 36 rezystorów przez 18 elementów**. Pełna mapa oznaczeń i usuniętych węzłów: `hardware/rezystory-zamiany.csv`. Scalanie obejmuje wyłącznie połączenia szeregowe bez odczepu. Rezystory dzielników, sprzężeń zwrotnych i filtrów pozostają oddzielne, ponieważ ich wspólny punkt jest używany.

| Dawna para | V6, jeden element | Liczba | Współczynnik nominalny |
|---|---|---:|---|
| 150 kΩ + 150 kΩ | 300 kΩ | 7 | 4,06 przy dolnej gałęzi 100 kΩ i wejściu ADC 5 MΩ |
| 49,9 kΩ + 49,9 kΩ | 100 kΩ | 10 | 1,02, obciążenie wejściem ADC 5 MΩ |
| 249 kΩ + 249 kΩ | 499 kΩ | 1 | 6,0898 przy 100 kΩ równolegle z 5 MΩ |

Wykonanie: przewlekany **MBB/SMA 0207 Precision** lub równoważny rezystor metalizowany 0,1%, ≤25 ppm/K, moc znamionowa ≥0,40 W, napięcie robocze ≥350 V. Korpus około 6,3 × 2,5 mm, miejsce na raster wyprowadzeń 10,16 mm. Nie zastępować przypadkowym „0,5 W” bez sprawdzenia napięcia, tolerancji i TCR. Kody w BOM odpowiadają nomenklaturze serii; dostępność konkretnego wariantu/opakowania trzeba potwierdzić przy zamówieniu. Dopuszczalny zamiennik o identycznych parametrach nie wymaga zmiany układu, lecz wymaga kalibracji.

Kontrola statyczna przy 60 V na całym rezystorze: 100 kΩ → 36 mW; 300 kΩ → 12 mW; 499 kΩ → 7,22 mW. To duży zapas względem mocy znamionowej w chłodnym otoczeniu; obowiązuje obniżanie dopuszczalnej mocy z temperaturą. Nie jest to kwalifikacja odporności na impulsy automotive. Rezystory nadal muszą być przy źródle odczepu, żeby zwarcie dalszego przewodu pomiarowego miało ograniczony prąd. **Jeden rezystor nie zachowuje odporności na zwarcie pojedynczego elementu, którą dawała para** — przyjęto to uproszczenie prototypu zgodnie z decyzją o pojedynczych elementach. Większy korpus nie zastępuje tej redundancji.

Współczynniki są wartościami startowymi obliczonymi z nominalnego obciążenia ADC. Nie są kalibracją ani gwarancją dokładności. Zmiana 99,8 → 100 kΩ i 498 → 499 kΩ jest uwzględniona w control.c; stare logi zachowują współczynniki zapisane w swoich zdarzeniach config. Profile NVS mają nowe magic EGR6; generator profili wymaga schema=6 i zmierzonych wartości.

## Granice wykonania

P01/P07: FR4 1,6 mm, dwie warstwy, początkowo miedź 70 µm. P05: dwie warstwy, 35 µm; ciągła masa pod ADC, rozdział analogu i cyfry rozmieszczeniem, bez szczeliny w powrocie masy. Dobrać szerokości/przewężenia miedzi do prądów i temperatury. Na uniwersalnych P02/P11 prąd motoru prowadzić przewodami/szyną, nie cienkimi mostkami między polami. P06: bocznik i INA z jedną krótką parą Kelvin lokalnie; nie ma jej w wiązce między PCB.

Montaż P04 wymaga krótkich CLK i /CLR oraz 100 nF przy każdym scalaku mimo małej częstotliwości funkcji. P05/P07 mają bezpośrednie pola SMD pod układy; zakaz lutowania przewodów do pól SMD dotyczy zakończeń wiązek, nie montażu układów scalonych.

Rysunki `montaz/` pokazują strefy i regułę kotwienia. Nie są szczegółowym rozmieszczeniem wszystkich elementów na uniwersalnej ani layoutem produkcyjnym. Tę część zalecenia montażowego pozostawiono do wykonania po doborze rzeczywistych podstawek, gniazd i nośników; deklarowane obrysy są rezerwą miejsca, nie gotową płytką do zamówienia.

Źródła: [AD7606B](https://www.analog.com/media/en/technical-documentation/data-sheets/AD7606B.pdf), [TLV1702AQDGKRQ1](https://www.ti.com/product/TLV1702-Q1/part-details/TLV1702AQDGKRQ1), [MCP1525](https://ww1.microchip.com/downloads/en/devicedoc/21653c.pdf), [rezystory MBB/SMA Precision](https://www.vishay.com/docs/28767/mbsmapre.pdf).
