# Połączenia i mechanika M1

Źródłem pełnej numeracji jest `hardware/wiring.csv`. Każdy przewód ma oba moduły, nazwy złączy, numery styków i nazwę sieci. Kable proste 1→1, widok w czoło gniazda PCB; pin 1 oznaczony trójkątem. Rysunek producenta konkretnego korpusu ma pierwszeństwo przed intuicyjną numeracją rzędu styków. Przy pomiarze omomierzem potwierdź numerację końca wtyczki.

Wiersz NC oznacza wolną pozycję, bez podłączania do innych NC ani do masy. Wskazanej pozycji klucza nie ma w pinowej netliście: jest fizycznie zablokowana zgodnie z `hardware/connectors.csv`.

IDC służy wyłącznie sygnałom cyfrowym i masie odniesienia. Analog ma osobne korpusy opisane ANALOG; moc jest osobno. Przewodów mocy nie prowadź w taśmie IDC. Każda linia CLK ma obok masę. SPI2 ma krótkie odgałęzienia od CORE do DAQ/I-LOGGER/DRIVE; przy zamontowanych wszystkich trzech torach odbierz dzwonienie i poziomy także przy 8 MHz. Taśmy ≤10 cm są założeniem montażowym do sprawdzenia, nie gwarancją integralności sygnału.

## ESP32: numery GPIO

| GPIO | Funkcja v5 |
|---|---|
| 1 | PWM do SAFE |
| 2 | MOSI/SDI AD7606B |
| 4 / 5 / 6 | SPI3 SCLK / MOSI / MISO: SD oraz TEMP |
| 7 / 8 / 16 | CS SD / TC1 / TC2 |
| 9 / 11 / 12 | SPI2 SCLK / MISO wspólne / CS AD7606B |
| 13 / 14 | CONVST / BUSY AD7606B |
| 10 / 15 | I²C SDA / SCL, lokalnie na CORE |
| 17 / 18 | TX / RX CAN; nadajnik fizycznie silent |
| 21 | Heartbeat |
| 38 | CS lokalnego ADC prądu przez 74HC139; odłączyć wbudowaną RGB |
| 39 / 40 | Żądanie MCU_ARM / odczyt HW_ARMED |
| 41 | Wyjście SCOPE_TRIG przez 330 Ω |
| 42 | INTERLOCK |

19/20 USB, 43/44 UART pozostają przeznaczone do obsługi płytki. 0/3/45/46 są pomijane ze względu na boot/strapping. 35–37 zajmuje pamięć. **47/48 nie używamy: w N32R16V domena tych GPIO ma 1,8 V.** Dopasuj footprint do posiadanej rewizji Waveshare po zmierzeniu rozstawu obu listew; nazwy GPIO są kontraktem elektrycznym.

MCP23017, adres 0x20: A0 RESET ADC, A1 MEAS_EN, A2 bank/dekoder CS, A3 SENSOR_ENABLE, **A4 LOGGER_CURRENT_OK wejście**, A5/A6 kierunek, A7 LED. B0 TEST_KEY, B1 SENSOR_FAULT_N, B2/B3 ENA/ENB, B4 LOGGER_CLEAR, B5 TEST_PRESENT, **B6 MARK**, B7 nieużywane wyjście. IODIRA=0x10, IODIRB=0x7f. GPA7/GPB7 nie są używane jako wejścia. Styk pomocniczy NO STOP jest punktem kontrolnym; NC STOP nadal sprzętowo odcina SAFE_N.

Dekoder 74HC139 na CORE: /G=GPIO38, A=MEAS_BANK, B=GND, Y0=CS_ILOG_N, Y1=CS_ITEST_N. Oba ADC korzystają z tego samego urządzenia SPI w firmware. Bank zmienia się wyłącznie po zatrzymaniu akwizycji. Zmiana banku nie wymaga ciągłego przełączania I²C między próbkami.

## Domeny zasilania

Waveshare dostaje 5V_SYS i wytwarza własne 3V3_CORE. MCP23017, dekoder CS, reset CORE i bufory po stronie MCU korzystają z 3V3_CORE. **Nie łącz 3V3_CORE z 3V3_IO przetwornicy.** P06/P07 mają jeszcze własne LDO 3,3 V dla lokalnych ADC.

Bufory 74LVC125AD **Nexperia**, SO14 na adapterze, mają Ioff według ich dokumentacji. Nie zamieniaj ich automatycznie na dowolny SN74LVC125A innego producenta. MISO jest w stanie wysokiej impedancji, gdy jego CS jest HIGH. Bufory ograniczają zasilanie przez sygnały przy VCC=0; stany przy powolnym zaniku zasilania sprawdza się pomiarem wraz z nadzorami szyn. I²C jest lokalne na CORE, nie przechodzi przez takie bufory jednokierunkowe.

Gotowość jest aktywna HIGH, z pull-downem przed wejściowym buforem SAFE. Przewód odłączony ma dawać 0. Linie open-drain mają lokalny pull-up właściwej domeny; SAFE_N ma jeden pull-up przez STOP. CORE_LINK oznacza obecność zasilania CORE, a watchdog sprawdza działanie programu. PG_LINK jest osobną pętlą obecności P01. Nie jest to układ wykrywający każde możliwe zwarcie przewodu sygnałowego.

## Klucze i obsługa serwisowa

Korpusy: sygnały IDC 2,54 mm w osłonach z polaryzacją i blokadą, niskie napięcia Micro-Fit 3.0, moc rozłączne MSTB 5,08 mm o deklaracji ≥12 A dla wybranego przekroju. W BOM-ie są rodziny i wymagania; konkretny numer producenta i footprint dobiera się przy layoutcie. Kolory: BAT czarny, VMOTOR czerwony, SENSOR niebieski, odczepy żółty, cyfrowe szary.

Zewnętrzne porty 12-pin: TEST = DEUTSCH DT04-12PA / DT06-12SA, L1 = wersje PB/SB, L2 = PC/SC. Różne klucze A/B/C zapobiegają zamianie adapterów. Styki size16 dobierz do przewodu, uszczelnień i prądu (rodzina do 13 A na styk; dla przejść mocy przewód 1,5 mm²). DT04 jest korpusem kablowym: wymaga osobnego uchwytu na panelu.

**Złącza DT nie mają styków wykrywających wtyk.** SW_LOG1 i SW_LOG2 to oddzielne zespoły mechaniczne, każdy z dwoma stykami NC rozwieranymi przez wsunięty wtyk; SW_TEST jest osobnym NO. Uchwyty i popychacze trzeba dopasować do kupionych korpusów i odebrać na stole. BOM liczy zespół dwóch NC jako jeden komplet. Pętla TEST na pinach 10–11 jest dodatkowym połączeniem w adapterze. Przed odebraniem tej mechaniki pełny TESTER nie jest gotowy do pracy. LOGGER uruchamiany bez DRIVE nie wymaga jej do pierwszych pomiarów.

Macierz kluczy jest w `hardware/connectors.csv`. IDC ma polaryzowany korpus i dodatkowy klucz: wskazany pin usuń z obu gniazd, a tę pozycję zaślep w obu wtykach taśmy. W netliście i wiązce pozycja klucza nie przewodzi. Inne piny NC pozostają fizycznie obecne, aby blokowały wtyk o innym kluczu. Przy tej samej liczbie pozycji funkcje mają różne klucze. Dodatkowe pozycje NC w krótkich złączach są celowe.

BAT ma 2 pozycje MSTB 5,08 mm; SUPPLY/VMOTOR po 3, ISERIES 4, TMOTOR 5. SUPPLY i VMOTOR mają zgodny pinout. Analog TAPS używa 6 pozycji MSTB **3,81 mm**, a PG 6 pozycji Micro-Fit: nie są zamienne. Gałęzie LVxx są celowo identyczne i zgodne elektrycznie. Pozostałe złącza Micro-Fit różnią się liczbą pozycji. Podczas zakupu utrzymaj te rodziny i polaryzację; odbierz na stole wszystkie pary z macierzy. Nie wyłamuj kołków innych niż wskazany klucz. To konkretny kontrakt kodowania, ale nie zastępuje kontroli zakupionych korpusów ani ich footprintów w przyszłym CAD.

Moduły wymieniamy bez zasilania. Kabel oznacz na obu końcach, np. C-DAQ A/P03 i B/P05. Oznaczenie płytki: `EGRLab P06 I-LOGGER / HW5.0 / IF M1 / SN IL_001`. Zachowaj zdjęcie ustawień JP, numer adaptera i plik kalibracji.

## Rozmieszczenie

Obrysy i cztery otwory M3 w `hardware/modules.json` są rezerwą miejsca. CORE umieść obok DAQ, I-LOGGER, DRIVE i TEMP, z ich złączami cyfrowymi zwróconymi do siebie. PROTECT i radiatory przy boku obudowy, z dala od termopar/cold-junction. DRIVE z kondensatorem, shuntem i mostkiem na jednej płytce; SENSOR przy złączu TEST. Dla pracy na stole wystarcza wspólny nośnik i dystanse; nie trzeba zaczynać od zamkniętej obudowy.

Rezerwa obudowy orientacyjnie 400×300×150 mm lub układ dwóch poziomów. Obrys CORE potwierdź pomiarem Waveshare, DRIVE realnym nośnikiem i radiatorem. Zostaw dostęp do gniazd sond i śrub. To założenia rozmieszczenia, nie wykonany model 3D.

Powroty motoru i zasilania prowadź grubymi parami do PSU; powroty sygnałów są dodatkowo w taśmach. Układ ma wspólną masę i nie jest izolowany galwanicznie. Połączenia GND w netliście oznaczają tę samą sieć elektryczną, ale nie dowolną wspólną cienką ścieżkę dla prądu motoru i pomiaru.
