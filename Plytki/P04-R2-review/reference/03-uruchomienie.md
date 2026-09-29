# Uruchamianie etapami

Wynik każdej próby wpisz w `verification/ODBIOR.csv`: data, numer PCB/rewizji, przyrząd, wynik, plik przebiegu. Domyślny status to NIEWYKONANE. Przy zmianie modułu powtarzaj jego odbiór i testy interfejsu; nie ma potrzeby ponownie kalibrować niezmienionych termopar tylko dlatego, że zmienił się pomiar prądu.

## 0 — stół, P00 i podstawowa dokumentacja

Potrzebne: zasilacz z ograniczeniem prądu, multimetr, oscyloskop, obciążenie rezystorowe/elektroniczne; do toru prądu źródło/wymuszenie obu kierunków i pomiar odniesienia. Oznacz płytki, ustaw klucz LOGGER, wyjmij F4 motoru. Układy scalone w podstawkach/na adapterach montuj po sprawdzeniu samych szyn.

P00 może być małą płytką ze złączami pomiarowymi, przełącznikami 3,3 V/GND dla sygnałów gotowości i gniazdem generatora 3,3 V. Dla watchdog potrzebne impulsy co około 10 ms. Jeśli nie masz generatora, TLC555CP w DIP8: p1 GND, p8 i p4 3,3 V, p2+p6 węzeł RC, p7 pomiędzy 4,7 kΩ do VCC i 68 kΩ do RC, RC→100 nF→GND, p5→10 nF→GND, p3 wyjście przez 1 kΩ. Przy tych wartościach około 102 Hz; zmierz częstotliwość. Niezależne wyjście do testowania watchdog, nie sztuczny heartbeat w gotowym urządzeniu.

P00 nie pozostaje w docelowym zestawie. Przełączniki zastępują źródła sygnałów tylko podczas odbioru pojedynczej PCB. Podczas prób blokad motor zastępuje obciążenie. Nie pozostawiaj zworek symulujących gotowość w kompletnym TESTER-ze.

## 1 — P01 PROTECT

Wykonaj całą instrukcję `P01-PROTECT/URUCHOMIENIE.md`: poprawna i odwrotna polaryzacja, progi UV/OV, histereza, start, inhibit, prąd wsteczny, obciążenie i termika. Najpierw mały limit prądu. OVP nominalnie 18 V, powrót około 16,66 V; UV około 9,37 V / start 9,85 V po regulacji. Własne sterowanie ma działać bez CORE.

Pojemność bezpośrednio na VPROT do 220 µF, wraz z 100 µF P01 i wejściami PSU. Motorowe 1000 µF jest za otwartym KPWR. Prąd startowy elektroniki przy otwartym KPWR ≤1,5 A — kryterium do pomiaru. Obciążenie ciągłe P01 do 5 A kwalifikuj wraz z radiatorami; nie zakładaj wyniku na podstawie obliczonej mocy.

## 2 — P02 PSU

Najpierw bez reszty płytek. Sprawdź 5V_SYS i 3V3_IO, tętnienia i spadki pod obciążeniem. Przewidywany limit planistyczny sumy gałęzi: 5 V do 1,5 A, 3,3 V do 0,5 A; to budżet, nie wynik pomiaru. Przetwornice TSR są 2 A. Oceń bezpieczniki F2/F3 przy rzeczywistym starcie i minimalnym VPROT; nie zwieraj ich podczas eksploatacji.

PSU_OK ma przechodzić na 0 po zaniku dowolnej szyny; sprawdź również odłączony przewód gotowości. Poszczególne LV odłączaj bez napięcia. Dopiero po odbiorze dodawaj kolejne gałęzie.

## 3 — P03 CORE

Wgraj wariant `core`. W tym wariancie program nie rozpoczyna akwizycji ani sterowania, inicjalizuje CORE i montuje SD, tworzy `core_probe.tmp`. Sprawdź plik na karcie. Test PSRAM wykonuje inicjalizacja ESP-IDF z MEMTEST; odczytaj wykrytą pojemność 16 MiB. To podstawowy test, nie wielogodzinny test przepustowości.

Zmierz osobno 3V3_CORE i 3V3_IO; nie łącz wyjść regulatorów. Sprawdź GPIO38 po odłączeniu RGB, GPIO41/SCOPE, adres 0x20, kierunki A4/B7. Test pinów rób przy wypiętych modułach wykonawczych. USB bez dodatkowej masy do auta; na stole zasilanie USB ma zastępować, a nie równolegle zasilać 5V_SYS.

## 4 — P05 DAQ i minimalny logger

Wariant `minimal`: P01/P02/CORE/DAQ, karta SD, panel MARK; P06–P10 mogą być nieobecne. GPIO i programowe żądania TEST pozostają wyłączone. Wprowadź identyfikatory `bind` i `daqmodule` przed kalibracją.

Zadaj znane napięcia po stronie adaptera: np. 0/5/12 V na motorowych, 0/2,5/5 V na sensorowych, 0/12/16 V na odgałęzienie VPROT na P02, przed F_VSENSE (cały tor VSENSE, nigdy LV05), znane napięcia na AUX HI i LO. Rejestruj raw; wszystkie nowe kalibracje początkowo są niezaakceptowane. Sprawdź oba banki adapterów i wszystkie używane zakresy ADC. Sprawdź RESET/CONVST/BUSY oscyloskopem, OS=111 i odczyt rejestrów. Na kanale AD indeks 5 ma być około zera, bo lokalny prąd jest osobnym polem logu.

Po zapisaniu `cal` i `auxcal` wydaj `vcalok 0 1` dla odebranego banku LOGGER; dla TEST osobno `vcalok 1 1`. Bez tej deklaracji V6 pozostawia fizyczne napięcia nieważne, raw nadal się zapisuje. Kalibracja AUX zmienia oba banki, więc deklaracje vcalok wykonuje się na końcu.

Sprawdź minimalny zapis przez godzinę, CRC, ciągłość numeracji, odstępy czasowe i zapis MARK. Wymuś odłączenie BUSY/MISO, pełną kartę i błąd zapisu; program ma wykazać problem. Na tym etapie nie jest potrzebny EGR.

## 5 — P09 TEMP i pierwszy użyteczny LOGGER

Zamontuj TEMP i użyj wariantu z EGR_TEMP_PRESENT. Odczyt obu termopar, odłączenie każdej z nich, porównanie z termometrem odniesienia, test wspólnych transferów TEMP+SD. Termopary izolowane elektrycznie od badanego korpusu. Temperatura zimnego złącza ma odpowiadać otoczeniu modułu, nie powietrzu ogrzanemu radiatorem.

Pierwszy pomiar w aucie L2: wyłącznie odczepy chronione. Zapisz temperatury i napięcia z zimnego i rozgrzanego silnika. W tym etapie brak prądu jest oczekiwanym, jawnym stanem. Nie trzeba czekać na gotowy aktywny tester.

## 6 — P06 I-LOGGER

Bez ECU. Sprawdź 5VA_P06, lokalne 3,3 V, odniesienie 2,5 V. Wartość raw przy zerowym prądzie nominalnie około 2048. Sprawdź znaki i skalę przy 0, ±0,5, ±1, ±2 i ±3 A. Kalibruj cały tor, nie tylko rezystor. Wykonaj próbę temperatury płytki i zera; wynik zapisz z numerem modułu.

Wyjście INA nie jedzie kablem do DAQ. Oba REF INA korzystają z lokalnego bufora 2,5 V. BYPASS ma jednocześnie zwierać bocznik i zdejmować LOGGER_CURRENT_OK; potwierdź miernikiem, że tor ECU–EGR pozostaje ciągły w obu położeniach. W logu status bieżącej próbki ma zmieniać się na ABSENT, nie na „0 A”.

Zmierz CS/SCLK i rzeczywisty moment próbkowania przy równoczesnym działaniu AD7606B. Zapis start/end obejmuje transakcję programową; kwalifikacja ma potwierdzić, że przedział się zgadza i nie przekracza 100 µs, a koniec jest do 400 µs po starcie AD. W przeciwnym razie nie zwiększaj progów w ciemno: popraw transfery/okablowanie.

Po L2 porównaj L1 z bocznikiem i BYPASS. Wkład interfejsu do spadku napięcia ma być zmierzony. Dopiero wtedy uznaj dane prądu w aucie za miarodajne.

## 7 — P10 CAN

Na stole odbiór znanych ramek przy 500 kbit/s, brak własnych ramek i ACK. Bez dodatkowej terminacji na sprawnej magistrali auta. OBD tylko 6/14; masa zasilania urządzenia jest odrębną ustaloną drogą, styki OBD4/5/16 nie są dodatkowym zasilaniem. Sprawdź błędy i `can_drop` przy obciążonej magistrali. RPM pojawi się dopiero z potwierdzonego źródła — kod dekoduje obserwowaną odpowiedź OBD 0x41/0x0C, sam jej nie żąda.

## 8 — P04 SAFE

Na P00: wszystkie kombinacje wymaganych sygnałów dodatnich, oba gniazda LOGGER, klucz, pętla TEST, STOP, odłączenie heartbeat. Zmierz czas watchdog; cel bazowy 50–150 ms. Przywrócenie zasilania/gotowości nie może samo odtworzyć HW_ARMED. Potrzebne nowe zbocze przycisku ARM. SUP_N nie jest SAFE_N: supervisor resetuje watchdog niezależnie od rozbrojenia.

SENSOR_PERMIT może działać bez uzbrojenia motoru. MOTOR_PERMIT wymaga klucza, pętli TEST, braku LOGGER, wszystkich wymaganych modułów, watchdog i ARM. Sygnały READY nie zależą od włączenia przekaźnika, którym mają zezwolić sterować.

## 9 — P08 SENSOR

Obciążenie rezystorowe zamiast EGR; zmierz napięcie, prąd zwarcia/ograniczenia, FAULT i rozłączenie obu przewodów KSENSOR. Około 100 mA z TPS2553/R_ILIM jest limitem toru, nie oczekiwanym poborem konkretnego sensora. Pierwsze sprawdzenie rozpoznanego czujnika można wykonać z zewnętrznym limitem 20 mA.

Zanim podasz własne zasilanie, pasywnie rozpoznaj trzy styki na aucie i ustaw dwie zwory adaptera T. Brak zgody lub niejednoznaczność identyfikacji oznacza brak aktywnego TEST. Pin 4 ma odpowiadać feedbackowi badanego typu; inny wynik wymaga wyjaśnienia oznaczeń/perspektywy złącza.

## 10 — P07 DRIVE bez motoru, potem obciążenie

Najpierw sekcja pomiarowa jak P06, potem okno OC. Przy 0 A INA≈2,5 V; OC_LOW≈1,5 V, OC_HIGH≈3,504 V. Nominalne progi -4,00/+4,02 A. Zmierz rzeczywiste tolerancje i czas wyłączenia. OC ma wyłączać lokalne VDD/EN i PWM, a także centralny ARM, bez działania ESP. KPWR otwiera tor zasilania; pojemność motorowa rozładowuje się własnym rezystorem.

Obciążenie na początku 12 Ω / co najmniej 50 W zamocowane zgodnie z wymaganiami radiatora; ograniczony prąd zasilacza. Sprawdź kierunki, blokady, reset CORE, urwany przewód permit, zanik lokalnej szyny i OC podczas PWM. Odbierz też zmianę kierunku: mostek wyłączony, zapis INA/INB potwierdzony, następnie 5 ms przerwy, dopiero ponowne zezwolenie.

Po każdej zmianie banku, kalibracji lub dłuższej pauzie zapisu konfiguracji licz się z rozbrojeniem watchdog. **Przed następnym ruchem ponownie naciśnij ARM.** Sam wynik OK komendy `zero` nie znaczy, że motor jest uzbrojony.

## 11 — kompletny TEST i dalsze próby

Zakończ formularz; dopiero wtedy ustaw `EGR_HARDWARE_ACCEPTED=1`, zbuduj firmware, wprowadź kalibracje, `metric 1` po odebraniu metryki i `qualify 1`, następnie `save`. Ten etap nie zwalnia ze sprzętowego ARM. Pierwsze impulsy małe, np. duty 0,05 / 20 ms, w znanym kierunku; zwiększaj według wyniku, nie od razu do maksimum.

Na koniec pełny zestaw 2 h SD + ADC + TEMP + CAN, zakłócenia od motoru, zimny start i rozgrzanie. Zarchiwizuj sesję, konfigurację firmware, kalibracje oraz fotografie. TESTER i LOGGER mają własne odbiory; powodzenie jednego nie zastępuje drugiego.

## Uzupełnienie V6

Na pierwszy start AD SPI=1 MHz (`CONFIG_EGR_ADC_SPI_HZ`), SD=4 MHz (`CONFIG_EGR_SD_KHZ`), lokalny prąd=500 kHz. Zapis 2 kS/s to 80 kB/s samych próbek; odebrać ciągły zapis wraz ze zdarzeniami i CAN. Nie usuwać limitów 500 µs okresu / 400 µs odczytu prądu, aby ukryć zbyt wolny transfer.

Po zmianie trybu/banku lub zatwierdzeniu konfiguracji akwizycja zatrzymuje się, a watchdog może rozbroić latch. Poczekać na poprawne świeże próbki i ponownie nacisnąć **fizyczny ARM**, także gdy poprzednie polecenie `zero` wymusiło taki cykl. W razie REJECTED sprawdzić HW_ARMED, gotowość i kalibrację; nie obchodzić zatrzasku. Kierunek: mostek wyłączony → potwierdzony INA/INB → 5 ms → ponowne zezwolenie.

Profile JSON/NVS mają wersję 6; zmiana nominałów wymaga nowych pomiarów i identyfikatorów modułów. Format próbek pozostaje wersją 5 (40 B), a schemat zdarzenia config/metadanych pozostaje 5. Numer rewizji urządzenia nie jest numerem formatu logu.


## Odbiór dodany w 6.1-rc1

VSENSE: bez napięcia sprawdź P02/F_VSENSE → H_VSENSE.1 → P05/RV1.1 i powrót GND. Sprawdź zabezpieczenie przewodu przez F100mA na źródle. Zmierz cały tor dla 0/12/16V; uwzględnij rzeczywistą rezystancję bezpiecznika w kalibracji. Odpięcie VSENSE musi dać nieprawidłowe VBAT i odmowę TEST. Porównaj mechaniczną niezamienność z LV. Przy samodzielnym uruchamianiu P05 używaj dedykowanej pary ze źródłem zabezpieczonym 100mA.

SFAULT: przy sprawnym SENSOR i zasilonym P08 przerwij tylko żyłę SENSOR_HEALTHY; następnie wyłącz P08; następnie wymuś lokalny FAULT bez przerwania kabla. W każdej próbie odczyt ma wskazywać błąd, aktywny TEST przechodzi w FAULT i wyłącza sensor/motor. Przywrócenie przewodu nie wznawia ruchu. Sprawdź SENSOR_CHECK, READY i mały impuls MANUAL z atrapą. Zatrzymanie zadania odczytu wejść na >100ms przy działającym ADC ma dać INPUTS_STALE. Czas faktycznego wyłączenia (od odczytu / deglitch TPS / wykonania polecenia) wymaga pomiaru; nie utożsamiaj progu 100ms z bezwarunkowym czasem całej reakcji urządzenia.

Po błędzie: usuń przyczynę, STOP, ponowna kwalifikacja TEST/SENSOR_CHECK i fizyczne ARM przed ruchem. W trybie LOGGER brak P08 nie przerywa pasywnego logowania.
