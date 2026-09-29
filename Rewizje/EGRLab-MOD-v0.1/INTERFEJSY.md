# Interfejsy MOD v0.1

Kontrakt funkcjonalny do schematów PCB. Tylko C-ADC ma poniżej proponowaną numerację pinów. Dla pozostałych wiązek podano komplet grup funkcjonalnych; fizyczna numeracja, rodzina złącza i kodowanie wymagają zamknięcia w schemacie każdej pary PCB. To nie lista gotowych przewodów do zaciskania.

## 1. Reguły wspólne

- Zasilanie rozprowadzamy osobnymi złączami. IDC cyfrowe przenosi wyłącznie logikę 3,3 V i odniesienie GND. Na IDC nie występuje 12 V, VMOTOR ani surowy sygnał z EGR.
- Połączenia cyfrowe punkt-punkt, bez odgałęzień podłączanych metodą Y. Wyjątek: współdzielony SPI3 jest rozdzielony na CORE; ścieżka SD lokalna, jedna krótka gałąź do TEMP.
- Napięcia i stany logiczne określa odbiornik, a nie sam opis wyjścia. Każde wejście wykonawcze ma lokalny pull-down; reset ADC aktywny HIGH ma stan zapewniający bezpieczną inicjalizację, a CS ma pull-up przy odbiorniku. Ostateczne wartości uwzględniają rezystory już obecne na nośnikach.
- Rezystory tłumiące dzwonienie zegara umieścić przy nadajniku; przewidzieć footprint na 22-47 Ω i dobierać pomiarem. Nie dodawać ich automatycznie do istniejących 330 Ω w sterowaniu mostka. Powroty zegarów nie mogą przebiegać przez ścieżkę prądu silnika.
- Zasilanie każdego modułu ma rozłączalny punkt pomiaru prądu. Zworki zastępują tylko zasilanie danego modułu; nie mostkują STOP, watchdog ani lokalnego OC.
- Wszystkie gniazda oznaczamy nazwą funkcji, numerem pin 1 i napięciem. Rysunek wiązki musi wskazywać widok od strony styków. Dwa takie same korpusy IDC dla różnych funkcji otrzymują odmienne kodowanie mechaniczne.
- Serwisowe zasilanie laboratoryjne zastępuje zasilanie systemowe; nie jest do niego równolegle dołączane. Nie zakładamy odporności na wkładanie/wyjmowanie wtyków pod napięciem.

## 2. Grupy połączeń

| Wiązka | Końce | Sygnały / funkcja | Proponowane wykonanie |
|---|---|---|---|
| P-IN | F1 → P01 | BAT_FUSED, GND | Para mocy, złącze blokowane; F1 przy źródle |
| P-OUT | P01 → P02 | VPROT, GND | Para mocy, obciążalność z zapasem powyżej 5 A |
| P-MOTOR | P02 → P07 | VPROT, PGND | Dedykowana gruba para; F4 i KPWR na P07 |
| P-LOGIC | P02 → P03/P04/P05/P08/P09/P10 | Potrzebne 5V_SYS i/lub 3V3_IO oraz GND | Osobne wyjścia gwiazdowe; złącza bezpieczne przy zamianie identycznych gałęzi |
| P-DRIVE-LOGIC | P02 → P07 | 5V_SYS, 3V3_IO, GND | Osobno od VMOTOR; obecność szyn warunkiem DRIVE_OK |
| A-LOGGER | P05 ↔ P06 | 5V_A, GND odniesienia, I_L_OUT po RO2, LOGGER_CURRENT_OK | Krótka kodowana wiązka, analog z własnym powrotem; nie podawać surowych końców Kelvin |
| A-TEST | P05 ↔ P07 | 5V_A, GND odniesienia, I_T_OUT po RO1 | Krótka kodowana wiązka; lokalne OC przed RO1 |
| C-ADC | P03 ↔ P05 | SPI ADC, CONVST/BUSY/RESET, MEAS_EN, MEAS_BANK, LOGGER_CURRENT_OK | IDC20, sygnał/GND, docelowo ≤10 cm |
| C-SAFE | P03 ↔ P04 | PWM, HEARTBEAT, MCU_ARM, HW_ARMED, INTERLOCK, SENSOR_ENABLE, MOTOR_INA/B, ENA/B_DIAG, SENSOR_FAULT_N, TEST_KEY, LOGGER_CLEAR, TEST_PRESENT, STOP_PRESSED; pętla obecności CORE | IDC z rezerwą, około 36 styków, każda funkcja z GND; docelowo ≤20 cm |
| C-DRIVE | P04 ↔ P07 | PWM_OUT, MOTOR_PERMIT, MOTOR_INA/B, ENA/B_DIAG, DRIVE_OK, DRIVE_FAULT_OC | IDC16 kodowane, sygnał/GND, ≤20 cm; wszystkie polecenia P07 w jednej wiązce |
| C-SENSOR | P04 ↔ P08 | SENSOR_PERMIT, SENSOR_FAULT_N, SENSOR_OK | IDC6 kodowane lub blokowane 6p; sygnał/GND |
| C-DAQ-SAFE | P05 ↔ P04 | DAQ_OK, DAQ_FAULT_OC | Kodowane 4p z dwoma przewodami GND |
| C-PSU-SAFE | P02 ↔ P04 | PSU_OK oraz pętla obecności złącza | Nadzór 5V_SYS/3V3_IO, stan po wypięciu = 0 |
| C-PG-SAFE | P01 ↔ P04 | Z istniejącego PG.J4: 3V3_IO, FAULT_OC, GND; dodatkowo pętla obecności w modularnym złączu | Przy projektowaniu PCB P01 dodać dwa styki pętli do dotychczasowych trzech; nie zmieniać toru OVP |
| C-TEMP | P03 ↔ P09 | SCLK, MOSI, MISO, TC1_CS, TC2_CS | IDC10 kodowane, sygnał/GND, ≤10 cm; napięcie osobno |
| C-CAN | P03 ↔ P10 | CAN_TX, CAN_RX | Kodowane 4p z GND; silent lokalnie na P10 |
| C-PANEL | P11 / przyciski ↔ P04 | Surowe styki STOP NC/NO, ARM, KEY, LOG1/LOG2 A/B, TEST presence i pętla T | Oddzielne kodowane złącza; wymagane styki mechaniczne, niezależne od MCP |
| C-MARK | Przycisk panelu ↔ P03 | MARK, GND | GPIO41, lokalny pull-up i filtr na P03 |
| A-TAPS | T/L1/L2 → P05 | TAP_P1/P3/P4/P5/P6 i ekran zgodnie z adapterem | Krótki odcinek wewnętrzny, ≤5 cm jako cel; brak zasilania w tym złączu |
| A-AUX | Panel → P05 | AUX HOT i ekran AGND | Krótki przewód; DPDT zakresów i dzielniki na P05 przy panelu |
| M-TEST | P07 → T | MOTOR_A po RSH_T, MOTOR_B | Para mocy, bez IDC |
| M-L1 | L1 ↔ P06 | ECU_P1, EGR_P1 | Krótki tor szeregowy; brak połączenia do VPROT lub mostka |
| S-TEST | P08 → T | 5V_SENSOR, AGND_SENSOR | Osobne kodowane 2p; oba przewody odłączane przez KSENSOR |
| CAN-BUS | P10 → OBD | CAN_H, CAN_L | Skręcona para; OBD tylko 6/14, bez 4/5/16 |
| TC-K | Termopary → P09 | TC1+/-, TC2+/- | Złącza K i przewody kompensacyjne, bez zwykłego IDC |

Nie każda PCB wymaga obu szyn P-LOGIC: TEMP potrzebuje 3V3_IO; P06 dostaje 5V_A z P05. P07 analog i stopień mocy mają osobne trasy zasilania, lecz urządzenie pozostaje nieizolowane. Każdy wykorzystany przewód GND jest rzeczywistym połączeniem; uwzględniamy go w analizie prądów powrotnych.

## 3. Proponowany pinout C-ADC

Złącze 2 x 10, numeracja zgodna z oznaczeniami producenta; pin 1 zaznaczony na PCB i przewodzie. Kabel 1:1, nie lustrzany. Numer GPIO nie jest numerem fizycznej listwy Waveshare.

| Pin nieparzysty | Sygnał | Nadajnik → odbiornik | Pin parzysty |
|---:|---|---|---|
|1|ADC_SCLK|P03 GPIO9 → P05|2 GND|
|3|ADC_SDI|P03 GPIO2 → P05|4 GND|
|5|ADC_DOUTA|P05 → P03 GPIO11|6 GND|
|7|ADC_CS|P03 GPIO12 → P05|8 GND|
|9|ADC_CONVST|P03 GPIO13 → P05|10 GND|
|11|ADC_BUSY|P05 → P03 GPIO14|12 GND|
|13|ADC_RESET|P03 MCP.A0 → P05|14 GND|
|15|MEAS_EN|P03 MCP.A1 → lokalny driver P05|16 GND|
|17|MEAS_BANK|P03 MCP.A2 → lokalny driver P05|18 GND|
|19|LOGGER_CURRENT_OK|P05 → P03 MCP.B7, nowa funkcja MOD|20 GND|

MCP.B7 jest w v4.1 nieużywanym wyjściem. W MOD będzie wejściem z fizycznym pull-downem, a firmware ma uznawać prąd LOGGER za nieważny po zaniku tego sygnału. Nie wolno wpiąć wyjścia READY w pin nadal skonfigurowany jako wyjście. Bez odebranej P06 albo przy bypass prąd LOGGER pozostaje nieważny. P05 przekazuje LOGGER_CURRENT_OK z P06 z dodatkowym warunkiem własnej poprawnej 5V_A; nie tworzy fikcyjnego stanu dobrego przez sam pull-up.

Sterowanie pinem 19 nie jest jeszcze kodem firmware w tym pakiecie. Przed montażem MOD należy zaktualizować konfigurację portu MCP i obliczanie current_valid. Sam AD7606B zachowuje mapę pinów v4.1: CONVST=9 i WR=10; tabeli złącza IDC nie należy mylić z nóżkami ADC.

## 4. Kontrakt READY oraz błędów

`*_OK` jest sprzętowym sygnałem aktywnym HIGH, odnoszonym do 3V3_IO. Odbiornik ma pull-down 10 kΩ. Źródło ma prawo podnieść linię dopiero po potwierdzeniu własnych napięć i braku określonej awarii. Po odłączeniu własnego zasilania wyjście nie może być zasilane przez kabel; wymagana kontrola prądu wstecznego i stanu wejścia odbiornika. Domyślne 0 nie jest generowane przez samą deklarację w firmware.

| Sygnał | Warunek HIGH | Odbiornik i reakcja |
|---|---|---|
|PSU_OK|5V_SYS i 3V3_IO w przyjętych oknach, zakończony reset|P04; LOW kasuje ARM i blokuje zezwolenia|
|DAQ_OK|Lokalne 5V_A w oknie i VDRIVE poprawne|P04; LOW blokuje TEST; świeżość próbek nadal sprawdza heartbeat|
|DRIVE_OK|Lokalne zasilanie INA/OC i logiki poprawne, brak zatrzaśniętego OC|P04; LOW kasuje ARM; lokalnie P07 wyłącza mostek|
|SENSOR_OK|Zasilanie sterowania P08 poprawne; brak lokalnej awarii wymagającej wyłączenia|P04; LOW blokuje sensor i motor; nie zależy od włączenia KSENSOR|
|LOGGER_CURRENT_OK|INA na P06 ma poprawne zasilanie; także poprawna 5V_A na P05|P03 MCP.B7; LOW daje current_valid=false w LOGGER|

Dla aktywnego TEST: `MODULES_OK = PSU_OK AND DAQ_OK AND DRIVE_OK AND SENSOR_OK AND CORE_LINK AND PG_LINK`. Pętle CORE_LINK/PG_LINK wykrywają rozłączenie odpowiedniego złącza; nie dowodzą ciągłości każdego pinu. `INTERLOCK = MECH_OK AND MODULES_OK`. Brak CAN nie blokuje standalone TEST. Brak P06 nie blokuje TEST. Brak ważnej TC1 blokuje ruch w firmware tak jak dotychczas; sam działający SPI nie jest potwierdzeniem ważnej temperatury.

Wyjścia `*_FAULT_OC` są wyłącznie otwartymi kolektorami/drenami do wspólnego SAFE_N. Nie podajemy na tę sieć push-pull ani dodatkowego pull-up z modułu. Gotowość i błąd służą różnym celom: bezpośredni błąd szybko kasuje zatrzask, a gotowość blokuje pracę przy braku płytki/zasilania. Progi i opóźnienia nowych nadzorów muszą znaleźć się w schematach P02/P05/P06/P07/P08; ten dokument nie zastępuje tych obwodów.

P07: `DRIVE_ENABLE = MOTOR_PERMIT AND LOCAL_RAILS_OK AND NOT OC_LATCH`. `PWM_TO_BRIDGE = PWM_OUT AND DRIVE_ENABLE`. VDD pull-upów ENA/ENB nośnika oraz driver KPWR zależą od DRIVE_ENABLE. Nie wymuszać poziomu HIGH na wyjściach diagnostycznych ENA/ENB. Kierunki i PWM mają lokalne stany spoczynkowe. Zanik pojedynczego kierunku może zmienić zachowanie mostka i nie jest automatycznie wykrywany przez pętlę obecności; testujemy również tę usterkę i nie obiecujemy pełnego pokrycia wszystkich przewodów.

Lokalny OC_LATCH musi powstać w hardware. Reset dopiero po niskim MOTOR_PERMIT i ustąpieniu lokalnej przyczyny; stan startowy nie dopuszcza ruchu. Nie wykorzystujemy automatycznie powracającego komparatora jako regulatora cyklicznego prądu. Docelowy czas od OC do PWM/ENA/ENB LOW nadal podlega pomiarowi, z celem <20 µs z v4.1. Czas odpadnięcia KPWR nie zastępuje szybkiego odcięcia elektronicznego.

## 5. SPI, zasilanie i ciepło

P09 dzieli SPI3 z SD na P03. Rozważane bufory muszą zachować trójstan MISO, gdy oba CS termopar są HIGH. Niedopuszczalny jest stale aktywny bufor, który wymusza swój stan podczas odczytu SD. Odbiór obejmuje pracę każdego peryferium osobno, obu termopar i SD łącznie oraz odłączanie zasilania P09 przy zatrzymanych transmisjach.

Buforów `Ioff` nie utożsamiamy z izolatorami galwanicznymi, translatorami I2C ani pełnym rozwiązaniem brownout. Dobór OE, progu resetu i miejsc zasilania wymaga sprawdzenia kart katalogowych. Nie zwiększamy dowolnie pojemności przewodów: dodatkowa pojemność wysokoimpedancyjnych odczepów zmienia pasmo pomiaru, dlatego kalibracja DC nie zastępuje próby impulsowej.

Lokalne kondensatory i powielone drivery zwiększają pobór i prąd startowy. W schemacie każdej PCB trzeba wpisać prąd ciągły, szczytowy, pojemność wejściową i bezpiecznik gałęzi. Suma mieści się w ograniczeniu P01/F1 5 A oraz możliwościach TSR; granic nie mnożymy przez liczbę płytek. Rezystor 1 Ω filtru 5V_A liczymy z sumarycznym obciążeniem ADC i obu INA. Poprawność 5V_SYS na PSU nie gwarantuje 5V_A na końcu najdalszej wiązki.
