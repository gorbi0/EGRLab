# Recenzja M1-R1 — EGRLab, wykonanie Opusa

**Recenzent:** Codex. **Data:** 8.10.2026. Nazwa katalogu „recenzja-Astra” zachowana zgodnie z instrukcją paczki; nie oznacza identyfikacji modelu recenzenta.

**Werdykt: wymagane poprawki przed zamknięciem rewizji.** Znalazłem **6 uwag ważnych i 1 drobną**. Nie stwierdziłem potwierdzonej wady kategorii krytycznej. Najistotniejsze problemy dotyczą zasilania z samego USB, pomiaru napięcia w TEST oraz ponownego odblokowania napędu po błędzie inicjalizacji watchdogów. Obecne pliki CAD i produkcyjne przechodzą kontrole. Nie ma podstaw do uznania całej płytki za wymagającą zaprojektowania od nowa.

Przed zamówieniem warto rozstrzygnąć M1-01 i M1-02, bo wybrana naprawa może zmienić połączenia. Pozostałe poprawki dotyczą głównie firmware, instrukcji i narzędzi. Ten raport nie jest odbiorem sprzętu ani gwarancją wykrycia każdej możliwej wady.

## Zakres i identyfikacja

Sprawdziłem [paczkę źródłową](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji), jej specyfikację, audyt decyzji, schematy, BOM, projekt PCB, Gerbery/Excellon, generator, firmware i testy. Respektuję D-M1-1…13: cztery warstwy, ręczny montaż, zasilanie 4S+BMS, zewnętrzny IBT-2, ręczne przepięcia X1 oraz rezygnację ze sprzętowych zabezpieczeń S1. Nie zgłaszam braku SAFE, przekaźników, UVLO ani okna OC jako usterek M1.

Źródło z manifestu: gałąź `m1`, commit `8b08953e6ecce4de4a27a26b1fe7559a885ddbe3`. Oryginał miał i nadal ma **531 plików**. Wszystkie **529 pozycji manifestu** zgadzały się z SHA-256. Końcowa kontrola nie wykazała zmienionych, usuniętych ani dodanych plików w oryginale. Wszystkie przebiegi generatorów i testów wykonywałem w kopiach roboczych.

- PCB: SHA-256 `2b39a9ef6a1859437d935b1c7fb7464b49a346cf886a65b2d6c3c769a95a4c8b`.
- ZIP dla producenta: SHA-256 `824058fb1497f3f717d213b366616b3687a044896e8437c0ed62d6853e908ac4`.
- Kopia `Plytki/M1-PCB-R1-zamowienie/projekt/` jest bajtowo zgodna z wydaniem `Plytki/M1-R1-review/`.

## Zgłoszenia do poprawienia

### M1-01 — ważne: tryb „tylko USB” zasila sygnałami domenę bez VDRIVE

**Miejsce:** U3 pin 23 `VDRIVE`, wejścia RESET/SCLK/CS/SDI; U2 `TSR 2-2433`; [board.c:238](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Rewizje/EGRLab-v6.3-m1/firmware/main/board.c:238), [board.c:178](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Rewizje/EGRLab-v6.3-m1/firmware/main/board.c:178); [README:21](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Rewizje/EGRLab-v6.3-m1/README.md:21), punkt odbioru 7; D-M1-6 w [AUDYT.md:89](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Plytki/M1-specyfikacja/AUDYT.md:89).

**Dowód:** własna szyna 3V3 peryferiów pochodzi z U2 zasilanego pakietem. Wyjście 3V3 modułu ESP jest niepołączone z tą szyną. USB może uruchomić ESP, a `board_init()` ustawia wyjścia, uruchamia SPI w mode 2 i wykonuje RESET ADC przed uznaniem odczytów za niepoprawne. Przy braku pakietu nie ma prawidłowego źródła VDRIVE dla U3. Dla VDRIVE = 0 V dopuszczalne maksimum wejścia cyfrowego to 0,3 V, podczas gdy GPIO podaje około 3,3 V. To przekroczenie o około **3 V**, a nie tylko brak danych. Możliwy jest prąd przez zabezpieczenia wejść i pasożytnicze zasilanie; jego wartości ani skutków termicznych nie ustalono pomiarem. [AD7606B, tabela 6, s. 12](https://www.analog.com/media/en/technical-documentation/data-sheets/AD7606B.pdf).

W oficjalnym schemacie rodziny Waveshare USB przez D1 zasila także `VDDUSB`, połączone z pinem 5V listwy. Nie należy więc opisywać tego stanu jako pewnego braku wszystkich napięć ADC: jego AVCC może otrzymać napięcie z USB, podczas gdy VDRIVE pozostaje bez właściwego zasilania. Konkretną rewizję posiadanego modułu trzeba potwierdzić. [Schemat Waveshare](https://files.waveshare.com/wiki/ESP32-S3-DEV-KIT-N8R8/ESP32-S3-DEV-KIT-N8R8-schematic.pdf).

**Proponowana zmiana:** najkrótsza naprawa zgodna z D-M1-6 to wycofać deklarację obsługi USB bez pakietu oraz taki test odbiorczy. Wprost wymagać: pakiet włączony przed USB; USB odłączone przed wyłączeniem pakietu. „Brak karty” można obsługiwać programowo przy prawidłowym zasilaniu wszystkich domen, ale nie utożsamiać go z elektrycznie dopuszczalnym „tylko USB”. Jeśli USB-only ma jednak zostać, potrzebne jest prawidłowe zasilanie domen lub izolacja wejść przy wyłączonym zasilaniu, obejmująca SPI i RESET. Nie wystarczy późniejszy komunikat `adc_error`, opóźnienie RESET ani równoległe zwarcie dwóch wyjść 3V3.

**Warunek zamknięcia:** tabela stanów pakiet/USB i pomiar GPIO względem VDRIVE w każdej obsługiwanej sekwencji. Dodatkowo sprawdzić rozruch i wyłączenie dwóch niezależnych TSR: karta ADC wymaga też `VDRIVE ≤ AVCC + 0,3 V`. Brak pomiaru tej sekwencji jest luką kwalifikacji, nie dowodem, że podczas każdego normalnego startu już występuje przekroczenie. Obecne opóźnienie programowe nie ustala kolejności narastania szyn.

### M1-02 — ważne: TEST sprawdza VBAT auta zamiast napięcia własnego napędu

**Miejsce:** CH7 / X1.13 `VBAT_CAR`; [SPECYFIKACJA.md:60](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Plytki/M1-specyfikacja/SPECYFIKACJA.md:60), [SPECYFIKACJA.md:80](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Plytki/M1-specyfikacja/SPECYFIKACJA.md:80); [control.c:267](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Rewizje/EGRLab-v6.3-m1/firmware/main/control.c:267).

**Dowód:** TEST jest zasilany z własnego pakietu 4S, określonego jako 10–16,8 V. CH7 mierzy akumulator samochodu; instrukcja TEST nie każe podłączać do niego pakietu. Mimo to `control_step()` wymaga na CH7 napięcia 9–16,5 V. Przy otwartym X1.13 otrzymamy niski odczyt i FAULT `SUPPLY`. Sama zworka do pakietu też nie rozwiązuje wszystkiego: prawidłowe 16,8 V przekracza obecny próg.

Test C z niezmienionym `control.c`, przy prawidłowych pozostałych warunkach, dał:

| Podane CH7 | Polecenie `test` | Stan po sprawdzeniu czujnika |
|---|---|---|
| 0 V | przyjęte | FAULT / SUPPLY |
| 13,5 V | przyjęte | READY |
| 16,8 V | przyjęte | FAULT / SUPPLY |

Dowód: `evidence/probe_review.c`, `probe_review.txt`. To test logiki, nie odczyt z fizycznego ADC. Profil testowy jest świadomie dopuszczony do TEST; dostarczone obrazy z `EGR_HARDWARE_ACCEPTED=0` mają dodatkową zamierzoną blokadę.

**Proponowana zmiana:** określić CH7 jako pomiar napięcia źródła napędu zależnie od trybu. W LOGGER mierzyć auto; w TEST — VMOTOR za F1. Wariant bez zmiany PCB: w TEST całkowicie odłączyć przewód auta od X1.13 i połączyć X1.13 z X1.3. Nigdy nie łączyć tych źródeł równolegle. Zapisać źródło napięcia w `config`/eksporterze. Dla TEST przyjąć zakres obejmujący 16,8 V i błąd pomiaru, np. **9,0–17,3 V** jako początkowe progi programowe; to nie zastępuje BMS ani nie zmienia nominalnego zakresu pakietu. Górny zapas 0,5 V jest większy od 1% z 16,8 V + 50 mV. Docelowy próg powiązać z przyjętym błędem po kalibracji.

**Warunek zamknięcia:** regresja dla CH7 odłączonego, 8,9 / 10 / 13,5 / 16,8 / 17,4 V, osobno LOGGER i TEST; zgodny opis `vbat` w punktach HOT-SOAK. Jest to również błąd znaczenia danych: napięcie auta nie opisuje warunków zasilania silnika na stole.

### M1-03 — ważne: błąd uruchomienia watchdogów nie utrzymuje blokady TEST

**Miejsce:** [app_main.c:293](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Rewizje/EGRLab-v6.3-m1/firmware/main/app_main.c:293), końcowa bramka [commit_locked():224](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Rewizje/EGRLab-v6.3-m1/firmware/main/app_main.c:224), [board_watchdogs_start():402](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Rewizje/EGRLab-v6.3-m1/firmware/main/board.c:402).

**Dowód:** po błędzie startu wykonywane jest tylko `board_emergency_stop()`. Nie zostaje ustawiony trwały stan „watchdog niesprawny” ani FAULT kontrolera. Kolejny `commit_locked()` pobiera już aktualny token zatrzymania i może wykonać `board_release(gate)`. `board_mode()` przywraca też `drive_ok`. Żaden z tych warunków nie zależy od powodzenia inicjalizacji watchdogów. Jeżeli błąd nastąpi przed linią 408 `board.c`, kod nie uruchamia także RTC WDT.

Wstrzyknąłem błędy kolejno do `esp_task_wdt_reconfigure`, `esp_task_wdt_init` i `esp_task_wdt_add`. Próba kompiluje rzeczywiste funkcje `board.c` oraz dokładne warunki z gałęzi błędu i zwolnienia bramki w `app_main.c`; HAL jest atrapą. We wszystkich trzech przypadkach: blokada tuż po błędzie = 1, RTC nieuruchomiony, po następnej poprawnej konfiguracji **DRIVE_EN = 1, RPWM = 204/1023**. Dowód: `evidence/probe_watchdog_review.py`, `watchdog_probe.c`, `watchdog-probe.txt`.

Nie jest to symulacja całego planisty ani fizycznego mostka. Odtwarza konkretny błąd kontraktu blokady w kodzie, przy założeniu spełnienia pozostałych warunków ruchu.

**Proponowana zmiana:** `watchdogs_ok=false` od startu; ustawienie true dopiero po pełnym udanym uruchomieniu obu mechanizmów. Sprawdzać go przy dopuszczeniu TEST i bezpośrednio przed wydaniem zezwolenia napędowi. Niepowodzenie powinno pozostawiać FAULT wymagający skutecznej ponownej inicjalizacji albo restartu. Zwykłe `stop`, `test`, zmiana banku czy kalibracja nie mogą go kasować.

**Warunek zamknięcia:** trzy próby błędów jak powyżej + następne poprawne konfiguracje i polecenia ruchu; wynik zawsze EN=0/PWM=0 do odzyskania sprawnych watchdogów. Osobno nadal potrzebne są sprzętowe próby TWDT, RTC WDT i panic handlera.

### M1-04 — ważne: „najwyżej 1 s utraty logu” nie wynika z `fsync` co sekundę

**Miejsce:** [README:20](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Rewizje/EGRLab-v6.3-m1/README.md:20) i punkt odbioru 10; [04-firmware-logi.md:110](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Rewizje/EGRLab-v6.3-m1/docs/04-firmware-logi.md:110); [storage.c:22](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Rewizje/EGRLab-v6.3-m1/firmware/main/storage.c:22), [storage_writer():229](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Rewizje/EGRLab-v6.3-m1/firmware/main/storage.c:229).

**Dowód:** bufor 8 MiB mieści `floor(8388608/40)=209715` próbek, czyli **104,8575 s** przy 2 kS/s. Writer zdejmuje do 64 próbek na obieg; `fsync` dotyczy danych już przekazanych do plików, nie całej kolejki w PSRAM. Pięciosekundowe zatrzymanie zapisu może pozostawić około 10000 próbek / 400000 B w RAM. Wyłączenie zasilania w takim momencie traci więcej niż sekundę mimo ustawienia `CONFIG_EGR_SD_SYNC_MS=1000`.

Również `stop` i odczekanie 2 s nie potwierdza opróżnienia kolejki. Samo `stop` nie oznacza końca akwizycji. Pojemność 104,86 s nie jest gwarantowaną górną granicą strat całego systemu plików; pozostają opóźnienia i zachowanie kontrolera karty.

**Proponowana zmiana:** opisać 1 s jako okres synchronizacji w normalnym przebiegu, bez gwarancji maksymalnej straty. Dodać stan: liczba i wiek niezapisanych próbek, czas ostatniej udanej synchronizacji oraz czas trwania `fsync`. Jeżeli ma istnieć procedura bezpiecznego wyłączenia, niech zatrzymuje akwizycję, opróżnia próbki i zdarzenia, synchronizuje/zamyka pliki i dopiero potwierdza zakończenie. Nie wymaga to przywracania PFAIL ani podtrzymania z S1.

**Warunek zamknięcia:** test opóźnień writera 3 i 10 s, zaniku zapisu oraz odczytu urwanego ostatniego bloku; raport ma wskazać faktyczny koniec danych, nie deklarowany limit 1 s.

### M1-05 — ważne: ponowne generowanie schematu usuwa ustawienia projektu KiCad

**Miejsce:** [build_schematic.py:86](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Plytki/M1-R1-review/src/build_schematic.py:86), `eda/M1.kicad_pro`.

**Dowód:** generator bezwarunkowo zapisuje minimalny nowy słownik projektu. Uruchomiony osobno na kopii R1 zakończył się kodem 0, ale usunął m.in. `board` i `net_settings`: reguły płytki i klasy sieci. Dowód: `evidence/project-rules-regeneration.json`, `schematic-regeneration.log`.

Pełny `run_release.py` przechodzi, ponieważ następnie uruchamia `set_rules.py`, który ponownie ustawia reguły zapisane w generatorze. To tłumaczy dodatni wynik pełnego odtworzenia; nie usuwa błędu samodzielnego eksportu ani utraty ustawień wprowadzonych ręcznie.

**Proponowana zmiana:** tworzyć projekt tylko, gdy nie istnieje. Dla istniejącego pliku aktualizować wyłącznie jawnie zarządzane pola schematu, zachowując pozostałe sekcje. Nie zastępować projektu pustym lub minimalnym JSON-em.

**Warunek zamknięcia:** test z dodatkową regułą i klasą sieci oraz zmienioną wartością prześwitu. Po samym generowaniu schematu i po pełnym wydaniu ustawienia mają zostać zachowane albo jawnie odrzucone jako sprzeczne z polityką projektu; nie mogą zniknąć po cichu. Porównanie `board.design_settings` i `net_settings` przed/po powinno być obowiązkową bramką.

### M1-06 — ważne: szczegółowa instrukcja przepięcia nie wymienia wszystkich przewodów ECU

**Miejsce:** [SPECYFIKACJA.md:68](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Plytki/M1-specyfikacja/SPECYFIKACJA.md:68) i [linia 83](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Plytki/M1-specyfikacja/SPECYFIKACJA.md:83); [06-diagnostyka.md:15](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Rewizje/EGRLab-v6.3-m1/docs/06-diagnostyka.md:15).

**Dowód:** P3 oraz P4/P5/P6 są połączone przelotowo na wspólnych zaciskach. Opis TEST wymienia odłączenie przewodu ECU z X1.5, a następnie podłączenie IBT-2 do X1.5/X1.7 i zasilania czujnika. Literalne wykonanie tylko tej szczegółowej listy pozostawia ECU P3 na wyjściu M− mostka i ECU na trzech liniach czujnika. W innym miejscu występuje ogólne „Odłącz ECU”, więc nie twierdzę, że projekt świadomie każe łączyć oba sterowniki. Problemem jest niepełna instrukcja wykonawcza i brak jednoznacznej tabeli stanu wszystkich pięciu żył.

Kontrola napięć przed `test` tego nie rozwiązuje: wyłączone ECU może mieć 0 V, co dokumentacja sama prawidłowo zaznacza. Pozostałe połączenie jest bezpośrednie przez zacisk, bez ograniczenia prądu przez rezystory odczepów ADC. Nie określam hipotetycznego prądu uszkodzenia ECU bez jego modelu.

**Proponowana zmiana:** tabela LOGGER→TEST: odłączyć i odizolować wszystkie pięć przewodów strony ECU z **X1.5, X1.7, X1.8, X1.9 i X1.10**; pozostawić odpowiednie przewody zaworu, podłączyć IBT-2 oraz SENS_5V/GND według potwierdzonej mapy. Dodać osobny krok dla X1.13 według M1-02 i tabelę powrotu do LOGGER, z usunięciem zworek TEST. Usunąć sprzeczne pozostałości o wymaganym fizycznym ARM. To doprecyzowanie zatwierdzonego ręcznego przepinania, bez żądania nowych przekaźników.

**Warunek zamknięcia:** przegląd schematu obu wiązek i pomiar ciągłości przy odłączonych źródłach: żadna z pięciu żył strony ECU nie może pozostać połączona z obwodem TEST. Sprawdzenie braku napięcia nie zastępuje tego warunku.

### M1-07 — drobne: paczka nie pozwala samodzielnie odtworzyć wszystkich testów Python

**Miejsce:** [ZAKRES-RECENZJI-M1-R1.md](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/ZAKRES-RECENZJI-M1-R1.md), [test_v5.py:126](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Rewizje/EGRLab-v6.3-m1/tests/test_v5.py:126), [test_v63_m1.py:158](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Rewizje/EGRLab-v6.3-m1/tests/test_v63_m1.py:158) i linia 191.

**Dowód:** po dołożeniu dostępnych lokalnie referencji v6.1-rc1 uruchomienie 102 testów daje **96 poprawnych i 6 błędów FileNotFoundError**. Brakuje `EGRLab-v6.2-s1/profiles/{hardware,valve,session}.json` i `Plytki/P09-R1-review/firmware/board.c`. Tych konkretnych referencji nie znalazłem również w wskazanym lokalnym EGRLab. Zależność od v6.2-s1 jest opisana, ale zależność od kodu P09 nie jest wymieniona w wykazie potrzebnych katalogów.

**Proponowana zmiana:** dostarczyć minimalne, wersjonowane fixture'y z SHA-256 w katalogu testów albo jednoznacznie wskazać commit i sposób ich pobrania. Testy powinny mieć preflight zależności. Nie zastępować brakujących plików obecnymi profilami M1, bo zniszczyłoby to sens regresji zgodności wersji.

**Warunek zamknięcia:** 102/102 i próba zerowa testów mutacyjnych w nowym, samowystarczalnym katalogu. Nie odtworzyłem deklaracji **31/31 mutacji firmware**, ponieważ nie miałem kompletnej bazy testów. Brak fixture'ów nie dowodzi błędu działania termopar ani profili; ogranicza odtwarzalność recenzji.

## Odpowiedź na 13 wskazanych ryzyk

| Obszar | Ocena i konkretne ustalenia |
|---|---|
| 1. Piny ESP w resecie | R2=4,7 kΩ usuwa wcześniejszy problem 100 kΩ na GPIO39. Z typowym pull-up 45 kΩ otrzymujemy `3,3·4,7/(45+4,7)=0,312 V`, poniżej VIL=0,8 V AHCT. To obliczenie typowe, nie gwarantowany rozrzut rezystora wewnętrznego. Przy VDD=3,6 V i R2+1% wymagane RPU>16,615 kΩ. GPIO1/21/40 mają zewnętrzne pull-down; CS SD/TC/ADC mają pull-up. GPIO3 pozostaje tylko punktem testowym, bez wymuszenia strapu. Reset/programowanie i rampy napięć sprawdzić oscyloskopem. [ESP32-S3](https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf), [AHCT125](https://assets.nexperia.com/documents/data-sheet/74AHC_AHCT125.pdf). |
| 2. Tor prądu | Mapowanie U4: IN+8 / IN−1, VS6, REF1=5V na 7, REF2=GND na 3, OUT5 — spójne. Nominalnie 0,25 V/A. R22/R23=10 Ω dają współczynnik `3000/3010`, czyli ok. 0,24917 V/A; poprawia to kalibracja `ivpa`. Nominalny liniowy zakres około ±9,2 A ma zapas do progu 8 A. [INA240](https://www.ti.com/lit/ds/symlink/ina240.pdf). |
| 3. Kelvin | Połączenia są rzeczywiście Kelvinowskie, z dedykowanych pól bocznika, bez prądu obciążenia w sense. Pomiar geometrii: K_PLUS 8,960 mm na F.Cu; K_MINUS 25,019 mm, dwie przelotki, odcinek na In2.Cu. Trasy są znacznie rozdzielone. In1 ogranicza sprzężenie elektryczne, ale nie daje dowodu braku indukcji magnetycznej. Nie stwierdzam z samej długości pewnej wady funkcjonalnej. Przed zmianą układu warto zbliżyć przebiegi i skrócić K_MINUS, jeśli nie pogorszy to toru mocy; o przydatności rozstrzyga próba PWM. |
| 4. AD7606B i CH1 | Pin 9=CONVST, pin 10=WR; pinout B jest użyty poprawnie. REGCAP-y są rozdzielone, REFCAP-y połączone zgodnie ze schematem, kondensatory miejscowe są obecne, cztery od spodu. Sam montaż od spodu jest dopuszczalnym rozwiązaniem. CH1 ma dłuższy węzeł o dużej impedancji, co kwalifikuję do próby przesłuchu, nie jako dowiedziony błąd odczytu. Węzeł ≈74 kΩ oznacza, że dodatkowe 10 pF zmienia stałą czasową o ok. 0,74 µs. [AD7606B](https://www.analog.com/media/en/technical-documentation/data-sheets/AD7606B.pdf). |
| 5. Moc i masa | Wylewki górne/dolne i połączenia pól obecne; DRC nie wykazuje przerw. RSH=5 mΩ: 0,28125 W przy 7,5 A, 0,5 W przy 10 A. To jest poniżej 1 W przy 70°C dla właściwego WSK2512; nie stanowi kwalifikacji nagrzewania całej drogi ani bezpiecznika. Powrót IBT-2 na listwie jest poprawnie oddzielony od prądu płynącego przez masę PCB. [WSK2512](https://www.vishay.com/docs/30108/wsk2512.pdf). |
| 6. TPS2553 | R31=232 kΩ jest wartością przewidzianą przez producenta. Z równań IOS i ±1% rezystora wychodzi około **98,7–138,6 mA**, nominalnie **117,0 mA**. Nie należy nazywać tego gwarantowanym limitem 100 mA. CH8 mierzy rzeczywiste wyjście, FAULT_N ma pull-up do 3V3. [TPS2553, s. 15](https://www.ti.com/lit/ds/symlink/tps2553.pdf). |
| 7. MAX31856 / SD | Bramka U5 włącza SDO danego modułu tylko przy jego CS=0; nieużywane bramki wyłączone. To sensowne rozwiązanie dla niepewnego stanu Z modułów XU. Trzeba zmierzyć napięcie za regulatorem każdego posiadanego modułu przy VIN=3,3 V. Warianty R24/R25 i R26/R27 są wzajemnie wykluczające; nie montować obu zworek jednej pary. Fizyczny rozstaw i wersja modułów nadal wymagają przymiarki. |
| 8. CAN | TCAN1051V: VCC=5V, VIO=3V3, TXD i S wymuszone wysoko; tor nadawania fizycznie zablokowany. Nie ma błędnego dodatkowego terminatora 120 Ω na odczepie. PESD2CAN ma wspólny pin do GND. Odbiornik i firmware LOGGER nie odczytują samodzielnie DTC ani nie wykonują adaptacji. [TCAN1051V](https://www.ti.com/lit/ds/symlink/tcan1051-q1.pdf). |
| 9. Mechanika i antena | PCB ma 150×80 mm, cztery warstwy; pola przewodów, USB/SD/termopary rozmieszczono zgodnie z aktualnym layoutem. W zadanej strefie anteny nie ma miedzi na żadnej warstwie. Nie potwierdzam sprawności RF w obudowie ani wymiarów posiadanych modułów z samego PDF. Wysokości nadal są szacunkami. |
| 10. Nadruk i GND | Cztery ukryte oznaczenia są dostępne na F.Fab. Obejrzałem wszystkie 7 stron schematu, 7 stron PCB oraz obrazy CAM top/bottom/In1/In2. Nie stwierdziłem oczywistego zwarcia, brakującego otworu ani kolizji obrysów modułów. Przerwa wyspy na B.Cu pod ESP nie przecina ciągłej płaszczyzny In1. |
| 11. Firmware M-01…13 | Zmiany prześledzone w kodzie i testach; uwagi M1-01…04 i M1-06. Pięć wariantów kompiluje się. Sprzętowe czasy watchdogów, panic handler i programowe OC pozostają do zmierzenia. GPIO38/WS2812B odpowiada oficjalnemu schematowi rodziny Waveshare, ale identyfikacja posiadanego egzemplarza nadal jest potrzebna. |
| 12. Impedancja i skale | Dla nominalnego wejścia 5 MΩ skale 4,06 / 4,06 / 1,02 / 1,02 / 1,02 / 1,0002 / 6,0898 / 1,02 są spójne z obwodami. To wartości nominalne, nie zastępstwo kalibracji offsetu i wzmocnienia. Zgodność skal sprawdzają też dostarczone kontrole. |
| 13. Produkcja | Dane odpowiadają czterem warstwom; minimalna ścieżka w gotowej PCB wynosi 0,20 mm, pierścień przelotki 0,15 mm, otwory 253 PTH + 16 NPTH. To aktualne dane geometryczne z projektu, a nie ogólna deklaracja zgodności z każdym producentem. Parametry stosu z paczki należy zachować przy zamówieniu JLCPCB. |

### Dwa szczególnie istotne pomiary analogowe

**Dryft zera INA240:** odniesienie VS/2 jest zgodne z zatwierdzoną decyzją i sposobem pracy INA240. Jednak zero zapisane przed nagrzaniem nie śledzi późniejszych zmian 5V. Każde **10 mV zmiany 5V daje około 20 mA pozornej zmiany prądu**, ponieważ `(10 mV/2)/0,24917 V/A ≈ 20,07 mA`. Zmiana 50 mV odpowiada około 0,10 A. Dla diagnostyki tarcia zależnego od temperatury trzeba oddzielić dryft przyrządu od wzrostu prądu zaworu. Przed serią wykonać zero, następnie nagrzać sam przyrząd z zerowym prądem i zmieniać obciążenie 5V; rejestrować wynik i napięcie zasilania. Dopiero wynik rozstrzygnie, czy potrzebna jest kompensacja lub inne odniesienie. Nie zgłaszam zastosowania VS/2 jako błędu samo w sobie. Parametry samego TSR nie określają końcowego błędu całego toru. [TSR 2](https://www.tracopower.com/products/tsr2.pdf).

**PWM, Kelvin i metryka prądu:** 1 mV błędu różnicowego na boczniku 5 mΩ odpowiada 0,2 A. Prąd jest mierzony z wyjścia INA, więc krótkie zakłócenie może zostać przefiltrowane, wzmocnione albo trafić w chwilę próbki — nie da się rozstrzygnąć tego z DRC. Porównać CH6 ze wzorcem dla stałych ±1/±3/±7 A, następnie PWM w obu kierunkach i podczas hamowania. Sprawdzić różne wypełnienia oraz fazę względem 2 kS/s. Dwie kolejne próbki >8 A są zamierzoną regułą, nie gwarancją wykrycia każdego impulsu >8 A: sekwencja 8,1/7,9 A jej nie wyzwala. Nie zgłaszam tego jako błędu, ale czas „1 ms” odnosi się do odpowiednio trwałego przekroczenia w próbkach, nie do dowolnego zdarzenia elektrycznego. Flaga `current_window_qualified` słusznie wymaga osobnej kwalifikacji metryki.

## Kontrole faktycznie wykonane

| Kontrola | Wynik niezależnego uruchomienia |
|---|---|
| Manifest i integralność źródeł | 529/529 wpisów; oryginał 531/531 niezmienionych plików |
| Kopia projektu w paczce produkcyjnej | zgodna bajtowo, bez dodatkowych plików |
| ERC | 0 naruszeń na 7 arkuszach |
| Netlista vs model części | 93 części, 357 sprawdzonych pinów, 99 sieci, 0 błędów |
| Kontrole M1 | 8/8; 16/16 mutacji + czysta próba zerowa |
| Natywny DRC | 0 naruszeń, 0 niepołączonych, 0 niezgodności ze schematem |
| Kontrole PCB | 11/11; 13/13 pozycji prób ujemnych, **w tym próba zerowa** |
| Odtworzenie z generatorów | cały `run_release.py` przeszedł: schemat, layout z zapisanego SES, nadruk, reguły, DRC, podglądy i PDF |
| Geometria po odtworzeniu | zgodne pola/footprinty, ścieżki/przelotki, granice stref i liczba warstw; 953 ścieżki+przelotki, 97 footprintów z 4 otworami montażowymi |
| Świeży eksport CAM | ponowny eksport z niezmienionej PCB, świeże dane geometrii identyczne z dołączonymi; CAM 24/24 |
| Próby ujemne CAM | 9/9 wad wykrytych + próba zerowa |
| Oryginalny ZIP | CRC poprawne, zawartość bajtowo zgodna z jego katalogiem Gerber |
| ESP-IDF 5.4.3 | **5/5:** test, logger, core, minimal, wifi — wszystkie exit 0 |
| Host C | control 131; runtime 66; health 58; OBD 23; ADC fault injection 118; storage 39; drive 45 — wszystkie dodatnie |
| Python | **96/102**, pozostałe 6 — brak fixture'ów, opis M1-07 |
| Próby własne | odtworzony FAULT SUPPLY w standalone; 3/3 błędy inicjalizacji watchdogów pozwalają na późniejsze zwolnienie bramki; odtworzona utrata reguł `.kicad_pro` |

Porównanie świeżego CAM nie jest porównaniem bajtowym: zmieniły się daty oraz śladowe zaokrąglenia konturów F.Cu/B.Cu. Pola, apertury i rysowane odcinki są identyczne. Suma różnic pól regionów wynosi około **1,37×10⁻⁷ mm²** na F.Cu i **7,01×10⁻¹² mm²** na B.Cu; maksymalna odległość obrysów to około **0,000001 mm**. To różnica numeryczna wypełnienia. Dla otworów różniły się wyłącznie nagłówki czasowe. Nie przypisuję pełnemu odtworzeniu tożsamości plików ani nie traktuję obrazu PNG jako pomiaru geometrii.

Testy C uruchomiłem TinyCC na Windows; lokalna nakładka testowa uzupełnia `isinf`/`lroundf` i usuwa linuksowe `-lm`. Nie zmieniałem implementacji firmware. Wynik kompilacji docelowej pochodzi niezależnie z ESP-IDF i kompilatora Xtensa. Narzędzia i logi opisano w [ODTWORZENIE.md](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-recenzja-Astra/ODTWORZENIE.md).

## Jak zamknąć kolejną iterację bez mnożenia rewizji

1. **Najpierw poprawić kontrakty:** M1-01 (źródła i sekwencje zasilania), M1-02 (co mierzy CH7), M1-06 (pełne przepięcie X1). Dopiero po wyborze rozwiązania zmieniać schemat lub przewody.
2. **Przenieść próby z tej recenzji do regresji:** Vbat 0/16,8 V, trzy błędy inicjalizacji WDT, samodzielny eksport schematu zachowujący reguły. Dołożyć test opóźnionego writera. Test ma wywoływać rzeczywistą implementację i móc wykryć wadę, nie sprawdzać obecności tekstu w źródle.
3. **Odtworzyć z pustego katalogu roboczego:** komplet fixture'ów, schemat/PCB/CAM, wszystkie warianty firmware, testy dodatnie i zerowa próba mutacji. Porównać geometrię i kontrakty, a następnie zamrozić manifest.
4. **Odbiór sprzętu prowadzić osobno:** przymiarka 1:1; same zasilania i sekwencje; ADC i kalibracja; tor prądu DC/PWM/dryft; SD i opóźnienia; termopary; CAN; dopiero na końcu napęd. Kryteria analogowe powiązać z potrzebną rozdzielczością diagnozy, np. czy rozróżniamy zmianę prądu tarcia o 0,1 A. Nie nadawać wszystkim tym pozycjom PASS na podstawie kompilacji lub DRC.

**Stan końcowy recenzji:** oryginały zachowane. Pliki CAD/CAM sprawdzone i odtwarzalne w opisanym zakresie. Wymienione błędy logiki i dokumentacji pozostają w R1. Sprzęt, dopasowanie modułów, obudowa, rzeczywiste czasy reakcji i jakość pomiarów: **NIE ZBADANO**.
