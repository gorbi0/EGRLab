# Budowa i odbiór etapami

## P00 - mały przyrząd uruchomieniowy

P00 to płytka wyprowadzająca złącza modułów na opisane punkty i przełączniki. Nie jest częścią urządzenia używanego w aucie. Ma wejście zasilacza laboratoryjnego, rozłączne gałęzie, rezystory ograniczające sygnały testowe i miejsca pod obciążenia.

Funkcje: wymuszenie poziomu 0/3,3 V przez rezystory, styk ARM, rozwieranie STOP/pętli obecności, wejście z generatora heartbeat 0-3,3 V, wyjścia znanych napięć do pomiaru multimetrem, monitorowanie PERMIT/SAFE/HW_ARMED. Do ADC można użyć potencjometru i mierzyć faktyczne napięcie dobrym multimetrem. Sam potencjometr ani tanie źródło odniesienia nie stanowią wzorca kalibracyjnego.

P00 ma fizycznie oddzielone części: LOGIC oraz LOAD. W wariancie testu SAFE nie ma możliwości dołączenia przewodów motoru. Generator heartbeat zastępuje MCU wyłącznie podczas odbioru samej logiki. Przed testem z mostkiem wracamy do rzeczywistego heartbeat i blokad aplikacji. Nie zostawiamy zwory BYPASS SAFETY w urządzeniu.

Obciążenia: 1 kΩ do pierwszych prób, obciążenie elektroniczne lub bank rezystorów do P01/P02 oraz dotychczasowe 12 Ω/25 W na radiatorze do mostka. Przy 14,4 V rezystor 12 Ω wydziela około 17 W, więc nie może leżeć luzem na PCB. Prąd obu znaków dla INA wymuszamy przez bezpieczną zmianę kierunku źródła laboratoryjnego, przy odłączonym ECU.

## Etapy

| Etap | Zespół | Podłączasz | Mierzysz i zapisujesz | Warunek dalszej pracy |
|---:|---|---|---|---|
|0|P00, wiązki, adaptery|Wyłącznie omomierz i źródło z ograniczeniem|Pin po pinie, klucze, izolacja, orientacja OEM, mostek tylko w AT|Brak zwarć; motor/ECU nie mogą trafić do gniazda logiki|
|1|P01 PROTECT|Zasilacz i obciążenie, bez innych PCB|Procedura PWR-THT: OVP/UVLO, start, wyłączenie, prąd wsteczny, temperatura|Wypełniony protokół PWR-THT; próby impulsowe przed użyciem w aucie|
|2|P02 PSU|Odebrana P01, sztuczne obciążenia 5 V/3,3 V|Regulacja, tętnienia, skoki obciążenia, PSU_OK, suma pojemności i prądu startowego|Szyny mieszczą się w wymaganiach odbiorników; brak przeciążenia P01|
|3|P04 SAFE|P02, P00 i generator; bez CORE i DRIVE|START, ARM, STOP, wszystkie wejścia READY, interlock, timeout heartbeat, powrót warunków|Watchdog 50-150 ms po pomiarze; każdy badany błąd kasuje ARM; brak automatycznego restartu|
|4|P03 CORE|Najpierw sam Waveshare, potem nośnik z MCP/SD; P00 zamiast innych modułów|Flash/PSRAM, I2C, reset, stan GPIO, test zapisu, zanik jednej szyny|Brak zasilania pasożytniczego w obu kierunkach; poprawna pamięć i logi|
|5|P09 TEMP|CORE, dwie termopary; wejścia silnika niepodłączone|TC1/TC2, rozwarcie, pomiar porównawczy, równoczesny zapis SD|Błędy dają nieważną temperaturę; brak konfliktu MISO i zakłóceń SD|
|6|P05 DAQ|CORE, źródła laboratoryjne, opcjonalnie P04|8 kanałów, zakresy i znaki, KMEAS/KCUR, AUX HI/LO, VPROT, szum, DAQ_OK|Kanały zgodne, zakres bez cichego clippingu, przejście konfiguracji zsynchronizowane|
|7|P06 I-LOGGER|P05 lub zasilacz 5V_A, źródło prądu i multimetr|Zero, oba znaki i nachylenie, spadek bocznika, LOGGER_CURRENT_OK, brak zasilania|Kalibracja ważna; po zaniku zasilania current_valid=false; continuity L1 zachowana|
|8|P10 CAN|CORE i testowa magistrala CAN|Odbiór i fizyczne silent; brak nadawania/ACK; równoległy zapis|Brak dodatkowej terminacji w przewodzie do auta; zgodność pinów 6/14|
|9|P08 SENSOR|P04/P00, rezystor zamiast zaworu|Limit prądu, fault, SENSOR_OK, rozłączenie obu przewodów, wypięcie sterowania|KSENSOR otwarty bez zezwolenia; rzeczywisty limit zapisany; brak napięcia na nieznanych pinach|
|10A|P07 pomiar i safety|Tylko zasilanie logiki/INA, VMOTOR odłączony|Prąd wzorcowy, oba progi OC, lokalny latch, DRIVE_OK, zaniki szyn|OC odcina lokalnie; przerwanie kabla analogowego nie wyłącza OC|
|10B|P07 mostek|Odebrane P01-P05, P09, P08 lub jego obciążenie; 12 Ω zamiast EGR|Kierunki, prąd, czas od OC do PWM/EN LOW, KPWR, rozładowanie VMOTOR, impuls regeneracji|Wszystkie blokady działają; brak powrotu ruchu po błędzie; odbiór temperatury|
|11|Integracja i P11|Cały zestaw, nadal obciążenia zamiast ECU/EGR|Odłączanie modułów/wiązek po wyłączeniu oraz kontrolowane przerwania wybranych sygnałów; pełny zapis logów|Testy opisane niżej przechodzą; brak nowych resetów i fałszywych pomiarów|
|12|L2 w aucie|Odebrany zestaw pomiarowy, napęd TEST odłączony|Wpływ sond, identyfikacja pinów, napięcia na zimno/ciepło|Brak zmiany pracy zaworu po podłączeniu; identyfikacja jednoznaczna|
|13|L1 w aucie|Najpierw mostek bocznika, potem pomiar prądu|Różnica fabryczna wiązka/L1 z mostkiem/L1 z bocznikiem|Dodatkowe przewody i złącza nie wywołują objawu; właściwy znak prądu|
|14|TEST zaworu|ECU fizycznie odłączone; znana mapa sensora, TC1|Zasilenie sensora z limitem 20 mA na pierwszą próbę, krótkie impulsy motoru z małymi limitami|Przejście odbioru v4.1 przed LEARN/SWEEP/FRICTION/CYCLE/THERMAL|

Kolejność nie oznacza konieczności montowania całego układu dla testu jednego modułu. P04 można sprawdzić na samym zasilaczu i P00; P06 na wzorcowym prądzie; P08 na rezystorze. Zależności pełnego TEST dotyczą dopiero współpracy elementów wykonawczych.

## Minimalne zestawy użytkowe

**Pierwszy logger napięciowy:** P01 + P02 + P03 + P05 + AL2 oraz styki panelu doprowadzone bezpośrednio albo przez P11. P07/P08 i adapter T są fizycznie niepodłączone. Ten zestaw wymaga wariantu uruchomieniowego/logger-only, który jawnie akceptuje brak opcjonalnych modułów, a ruch jest wyłączony kompilacyjnie. Nie zakładamy, że niezmieniona aplikacja v4.1 poprawnie wystartuje z każdym dowolnym podzbiorem.

**Logger do analizy termicznej:** poprzedni zestaw + P09. P10 dostarcza kontekst CAN, gdy znane ramki są dostępne. Sam nasłuch nie gwarantuje RPM: PID0C wymaga odpowiedzi wywołanej przez inny tester, albo odrębnie potwierdzonej mapy ramek. Nie nadawać zapytań automatycznie w imię kompletności logu.

**Logger z prądem:** poprzedni zestaw + P06 + AL1. Obowiązkowo porównanie z L2 oraz z mostkiem bocznika przed przypisaniem szarpania samemu EGR.

**Aktywny tester:** P01/P02/P03/P04/P05/P07/P08/P09 oraz AT i panel/styki. P06 i P10 nie są konieczne. Sprzętowe MODULES_OK, świeży ADC i ważna TC1 muszą działać. Pominięcie P06 w TEST nie jest obejściem pomiaru prądu: używany jest lokalny INA na P07.

## Próby integracyjne konieczne po podziale

1. SAFE bez heartbeat nie daje zezwolenia. Powrót heartbeat ani powrót READY nie odtwarzają ARM.
2. Wypnij kolejno każde złącze przy wyłączonym zasilaniu, potem uruchom układ. Brak wymaganej PCB/wiązki uniemożliwia TEST. Nie testować hot-plug jako zwykłej procedury.
3. Przy obciążeniu zastępczym otwieraj wybrane przewody za pomocą przygotowanego przyrządu: PERMIT, PWM, HEARTBEAT, READY, STOP, pętla AT. Rejestruj rzeczywisty stan mostka i rozładowanie VMOTOR. Sam status aplikacji nie wystarcza.
4. Odłącz zasilanie każdego modułu z pozostawionymi sygnałami, zgodnie z przygotowaną procedurą pomiarową. Sprawdź podnoszenie nieaktywnej szyny, prądy przez IO, stan EN/CS i ewentualny reset pozostałych modułów. Zweryfikuj także odwróconą kolejność zasilania.
5. Wywołaj OC obu znaków, następnie usuń przyczynę przy nadal aktywnym poleceniu z MCU. Brak ponownego ruchu; potrzebne cofnięcie zezwolenia i nowe ARM.
6. Porównaj szum napięć i zera INA: SD bez zapisu/zapis, CAN odłączony/odbiór, przekaźniki, PWM, zimna/gorąca obudowa. Dla wykrywania odchyłki masy 50 mV cel roboczy szumu i dryftu całego toru <10 mVpp z v4.1. Nie uznawaj tego za katalogową dokładność ADC.
7. Przenieś prąd powrotny silnika kontrolowanym obciążeniem i zmierz różnice potencjałów mas P03/P05/P07. Sygnał INA ma nachylenie około 0,25 V/A, więc błąd odniesienia 10 mV odpowiada około 40 mA pozornego prądu.
8. Sprawdź pełną aplikację przy docelowych długościach wiązek, zegarach i obciążeniu SD; długi zapis, CRC, timeouty, błędy TC i bank/config/zero. Zmiana banku lub dłuższa pauza może rozbroić watchdog; wymaganie ponownego ARM pozostaje.
9. Powtórz kwalifikację metryki FRICTION/średniej prądu przy PWM. Pojemność przewodów i nowe filtry mogą zmieniać pasmo. Dopóki kwalifikacja nie przejdzie, metryka pozostaje nieważna.
10. Cały moduł mocy pozostaje poza komorą grzania EGR. Obserwuj temperaturę elektroniki osobno od TC1/TC2 zaworu, aby dryft testera nie wyglądał jak usterka zaworu.

## Dokument odbioru każdego egzemplarza

Zapisz numer PCB i rewizję, obsadzone warianty, numer seryjny, datę, wersję programu, długości wiązek, przyrządy, temperaturę, pobór prądu, wyniki i zrzuty oscyloskopu. Statusy: NIE ZBADANO, W TRAKCIE, ZALICZONO albo DO POPRAWY. Zaliczenie programu na komputerze nie wypełnia kolumny pomiaru sprzętowego.

Każda późniejsza zmiana radiatora, długości kabla, filtru lub zasilania wskazuje, które próby trzeba powtórzyć. Nie wymagamy powtarzania całego projektu dla zmiany opisu na PCB; powtarzamy kontrole odpowiadające rzeczywistemu wpływowi zmiany.
