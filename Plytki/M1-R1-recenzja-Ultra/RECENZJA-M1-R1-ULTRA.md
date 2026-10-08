# EGRLab M1-R1 — drugi przegląd, Ultra

**Data:** 8.10.2026. **Recenzent:** Codex. **Przedmiot:** dokładnie ten sam pakiet wykonany przez Opusa, co w pierwszym przeglądzie. **Werdykt: wymagane poprawki przed zamknięciem rewizji.**

Drugi przegląd wykazał **5 dodatkowych błędów: 4 ważne i 1 drobny**. Są opisane jako M1-08…M1-12, z zachowaniem numerów M1-01…M1-07 z pierwszej recenzji. Najpoważniejsze nowe wyniki dotyczą zawieszenia ocen sterowania przy zajętym mutexie, niewłaściwej ważności danych po błędzie ADC oraz utraty prądu przy eksporcie logów. Nie wykazałem nowej pewnej usterki połączeń PCB ani plików CAM. Nie zgłaszam nowej wady kategorii „krytyczne”.

Poprzednie siedem zgłoszeń pozostaje otwarte; doprecyzowania M1-01 i M1-03 podaję niżej. Łącznie rejestr obu przeglądów zawiera **10 ważnych i 2 drobne** uwagi, o różnym rodzaju dowodu. Nie wszystkie powstały wraz z M1: „dodatkowe” oznacza znalezione dopiero w tej recenzji.

Najkrótsze zestawienie zmian oceny znajduje się w [POROWNANIE-RECENZJI.md](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-recenzja-Ultra/POROWNANIE-RECENZJI.md). Próby i ich granice opisuje [ODTWORZENIE.md](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-recenzja-Ultra/ODTWORZENIE.md). Nie wprowadzano poprawek do projektu.

## Identyfikacja i metoda

Źródło: [M1-R1-do-recenzji](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji). Gałąź `m1`, commit `8b08953e6ecce4de4a27a26b1fe7559a885ddbe3`. Porównano **531 plików** z wejściem poprzedniego przeglądu; wszystkie były identyczne. **529 pozycji manifestu źródła** zgadza się z SHA-256.

- PCB: `2b39a9ef6a1859437d935b1c7fb7464b49a346cf886a65b2d6c3c769a95a4c8b`.
- Produkcyjny ZIP: `824058fb1497f3f717d213b366616b3687a044896e8437c0ed62d6853e908ac4`.
- Poprzedni raport: `cc929bb05931dd06b53e151227fe5d33a6c733713051cccd9036ac1e9f98fbbf`.

Obowiązują zatwierdzone D-M1-1…13: pojedyncza czterowarstwowa PCB, własny pakiet 4S, zewnętrzny IBT-2, ręczne przepinanie oraz uproszczone zabezpieczenia. Nie kwestionuję tych decyzji i nie żądam powrotu do S1. Brak fizycznego ARM, przekaźników czy sprzętowego okna OC nie jest tutaj zgłoszeniem.

Przeprowadzono oddzielne analizy firmware, analogu/PCB/CAM oraz zasilania/interfejsów. Trzy analizy pomocnicze rozpoczęły się bez czytania pierwszej recenzji. Audyt główny objął również cały przepływ producent danych → zapis binarny → eksporter oraz zmianę kalibracji. Wyniki skonfrontowano ze źródłami i z poprzednim raportem. Autor głównej recenzji miał kontekst wcześniejszej pracy; nie jest to ślepy eksperyment porównujący wyłącznie ustawienie rozumowania. Wynik pozwala stwierdzić, że **ten dodatkowy przegląd wykrył więcej usterek**, ale nie dowodzi, że jedyną przyczyną różnicy jest Ultra.

## M1-08 — ważne: zajęty mutex blokuje limity ruchu i odczyt STOP, ale nie karmienie watchdogów

**Miejsce:** [app_main.c:293](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Rewizje/EGRLab-v6.3-m1/firmware/main/app_main.c:293), w szczególności linie 295–297, 301–328, 331; [print_profile:440](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Rewizje/EGRLab-v6.3-m1/firmware/main/app_main.c:440), `execute_locked` linia 485 i manager linie 568–570. Napęd: `DRIVE_EN` / GPIO39, `RPWM` / GPIO1, `LPWM` / GPIO21; [board.c:132](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Rewizje/EGRLab-v6.3-m1/firmware/main/board.c:132).

Zadanie `safety` karmi watchdog na początku obiegu. Dopiero później próbuje bez czekania przejąć `control_mutex`. Przy niepowodzeniu pomija `control_step`, wydanie nowych wartości napędu i `button_tick`. Jeżeli nie ustawiono `stop_pending` ani `transitioning`, mostek zachowuje poprzednie zezwolenie i PWM. Watchdog widzi działające zadanie, mimo braku postępu ocen sterowania.

To ma zwykły wyzwalacz: `profile` jest dozwolone podczas MANUAL/GOTO/SWEEP. Manager wypisuje profil pod tym samym mutexem. Dla profilu użytego w próbie rzeczywisty `print_profile` emituje 544 bajty, czyli 575 po LF→CRLF. Przy skonfigurowanym UART 115200 bit/s nawet odjęcie całych 128 bajtów FIFO daje co najmniej **38,8 ms** obsługi transmisji. Lokalny ESP-IDF potwierdza synchroniczne oczekiwanie na FIFO; wtórna konsola USB może dokładać oczekiwanie. To nie jest zmierzona latencja płytki — jest to dolne oszacowanie dla wskazanej ścieżki UART.

**Dowód:** próba wykonała niezmienione funkcje `safety`, `button_tick`, bramki napędu oraz `control.c`, z atrapą platformy i wstrzykniętym zajęciem mutexu. Po rozpoczęciu MANUAL na 10 ms zablokowano mutex na 400 ms:

```text
mutex_blocked: elapsed_us=400000 deadline=110000 now=505000
state=MANUAL DRIVE_EN=1 RPWM=306 LPWM=0
watchdog_feeds=400 physical_button_reads=0
mutex_released: state=READY DRIVE_EN=0 RPWM=0
```

400 ms jest kontrolowanym wstrzyknięciem blokady, a nie deklarowanym czasem zwykłego `profile`. Potwierdza, że w kodzie nie ma ograniczenia takiego okna. W jego trakcie nie jest oceniany koniec impulsu, limit prądu profilu ani temperatura. Odczyt fizycznego przycisku jest pomijany. Niezależny limit 8 A w akwizycji pozostaje czynny; nie twierdzę, że przestają działać wszystkie sposoby zatrzymania.

**Proponowana zmiana:** kopiować profil/status pod krótkim mutexem, a formatować i wypisywać po jego zwolnieniu. Odczyt i awaryjne zatrzymanie fizycznym STOP oddzielić od dostępności managera. Wprowadzić granicę czasu od ostatniej skutecznej oceny sterowania; przekroczenie zatrzymuje napęd. Odświeżanie watchdogów powiązać z postępem tego mechanizmu albo ze świadomie bezpiecznym stanem.

**Warunek zamknięcia:** próba blokady mutexu i wolnej konsoli podczas MANUAL, GOTO i SWEEP, z przyciskiem oraz terminem ruchu wypadającymi wewnątrz blokady. Wykazać czas wyłączenia na GPIO. Aktualne obrazy z `EGR_HARDWARE_ACCEPTED=0` nie dopuszczają jeszcze TEST; błąd dotyczy kodu przeznaczonego do pracy po odbiorze.

Dowody: [wynik próby](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-recenzja-Ultra/evidence/firmware/independent_firmware_probe-results.txt), [skrypt](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-recenzja-Ultra/evidence/firmware/probe_independent.py), [pełna analiza](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-recenzja-Ultra/evidence/firmware/findings-firmware.md).

## M1-09 — ważne: po błędzie ADC LOGGER nadal zapisuje dane jako ważne

**Miejsce:** [board.c:346](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Rewizje/EGRLab-v6.3-m1/firmware/main/board.c:346), [app_main.c:122](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Rewizje/EGRLab-v6.3-m1/firmware/main/app_main.c:122), linie 125–130 oraz 156–161; [control.c:255](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Rewizje/EGRLab-v6.3-m1/firmware/main/control.c:255). Dotyczy wszystkich kanałów U3 / AD7606B oraz `config_id` i `SAMPLE_INVALID`.

Po błędzie transferu `board_adc` ustawia `config_ok=false` oraz `adc_reset_needed=true`. Akwizycja zatrzymuje napęd, zapisuje `adc_error`, po czym przechodzi do następnej konwersji. Driver nie blokuje kolejnych odczytów tylko dlatego, że konfiguracja jest nieważna. Jeżeli późniejszy transfer się uda, akwizycja używa nadal wcześniejszej migawki `active_cfg`, zawierającej `adc_config_ok=true`.

Z tej starej flagi wyznacza `SAMPLE_INVALID`, przelicza napięcia i uruchamia triggery. LOGGER nie wymusza rekonfiguracji przez `control_step`, bo wychodzi z tej funkcji przed kontrolą `adc_ok`. Można zatem mieć jednocześnie driver wymagający resetu i rekordy z dawnym identyfikatorem konfiguracji, bez flagi nieważności.

**Dowód:** uruchomiono niezmienioną pętlę `acquisition` oraz opakowanie `board_adc`, wstrzykując prawidłowy odczyt → TIMEOUT → dwa prawidłowe transfery:

```text
board_config_ok=0 adc_reset_needed=1 acquisition_healthy=0
active_cfg_id=17 active_cfg_ok=1 state=LOGGER
record[1]: sequence=2 config_id=17 flags=0 SAMPLE_INVALID=0 SAMPLE_GAP=0
record[2]: sequence=3 config_id=17 flags=0 SAMPLE_INVALID=0 SAMPLE_GAP=0
latest_voltage_CH6_finite=1
```

Przerwa numeracji i zdarzenie błędu pozwalają zauważyć utracony odczyt. Nie unieważniają jednak kolejnych rekordów w eksporterze. **Nie zakładano, że każdy TIMEOUT zmienia zakresy ADC.** Pewną wadą jest przywrócenie deklaracji wiarygodności bez ponownego potwierdzenia konfiguracji. Jeśli przyczyną był rzeczywisty reset lub spadek zasilania przetwornika, dodatkowo możliwa jest interpretacja surowych liczb z nieprawidłową skalą.

**Proponowana zmiana:** zatrzasnąć nieważność pomiarów po błędzie, oznaczać takie próbki jako nieważne i nie interpretować ich fizycznie. Właściciel ADC powinien przeprowadzić odzyskanie/reset i odczyt konfiguracji, a następnie opublikować nowy `config_id` przed wznowieniem ważnych danych. Próby i zdarzenia odzyskania powinny mieć czas i identyfikator konfiguracji. Zachować kontrolowaną lukę w ciągłości.

**Warunek zamknięcia:** TIMEOUT/BUSY/SPI error → pozornie poprawne transfery nie mogą samodzielnie przywracać ważności. Dopiero udana rekonfiguracja ma przywracać wartości fizyczne. Sprawdzić to również w CSV, osobno LOGGER i TEST.

Dowody: [wynik](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-recenzja-Ultra/evidence/firmware/adc_metadata_probe-results.txt), [próba rzeczywistej pętli](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-recenzja-Ultra/evidence/firmware/probe_adc_metadata.py).

## M1-10 — ważne: eksporter usuwa prawidłowy prąd M1 z CSV i raportu HTML

**Miejsce:** [egrlog.py:151](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Rewizje/EGRLab-v6.3-m1/tools/egrlog.py:151), szczególnie linia 154; producent: [app_main.c:135](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Rewizje/EGRLab-v6.3-m1/firmware/main/app_main.c:135), `jsonlog.c`, `control_build_config`. Tor: RSH1 → U4 INA240A2 → U3 CH6 → `raw[5]`.

M1 zapisuje prąd w CH6 AD7606B. Zachowuje rekord v5, ale jego dawne pola MCP3201 są oznaczone jako nieobecne (`65535`, status 2), a konfiguracja ma `local_current=false`. Eksporter najpierw poprawnie przelicza osiem kanałów, następnie dla **każdego rekordu v5** zastępuje `v[5]` wynikiem starego lokalnego ADC albo `NaN`. W M1 zawsze wybiera tę drugą możliwość.

**Dowód pełnej ścieżki:** konfigurację wytworzono rzeczywistymi `control_build_config` i `json_config`. Przy ważnej kalibracji napięć i prądu zapisano prawidłowy, syntetyczny plik v5 dla −1 / 0 / +1 A. `inspect` potwierdził trzy rekordy, CRC, identyfikator konfiguracji i odstępy 500 µs. Oczekiwane wartości po kwantyzacji wynosiły −0,999787 / +0,000169 / +1,000125 A. Eksport dał:

```text
local_current=false voltage_calibrated=true
current_calibrated=true current_valid=true
exported_current_A=["", "", ""]
exported_current_out_V=["", "", ""]
export_warnings=[] report_warnings=[]
```

Raport HTML również nie zawiera użytecznych wartości prądu. Pozostałe kanały są przeliczane. Nie jest to tylko nieaktualny podpis ani brak kalibracji. Ten wynik **koryguje wcześniejszą pozytywną ocenę zgodności czytnika**: zachowanie rozmiaru rekordu v5 nie oznacza zachowania semantyki CH6.

**Proponowana zmiana:** nadpisywać CH6 z MCP3201 wyłącznie dla konfiguracji z `local_current=true`. Dla M1 zachować napięcie z `raw[5]` i zastosować jego zero/V/A oraz flagi kalibracji. Przy okazji respektować `ch8=SENS_5V` w nazwach kolumn/wykresów — obecne `aux_v` jest pozostałością S1. Nie usuwać obsługi starszych sesji.

**Warunek zamknięcia:** regresja producent C → kompletny plik → `inspect` → CSV/HTML, dla −I/0/+I; osobno M1, starszy MCP3201, `current_valid=false`, brak kalibracji i `SAMPLE_INVALID`. Nie wystarczy sprawdzić, że tekst `local_current=false` istnieje w źródłach.

Dowody: [wynik JSON](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-recenzja-Ultra/evidence/m1-reader-repro.json), [CSV](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-recenzja-Ultra/evidence/m1-current-export.csv), [raport HTML](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-recenzja-Ultra/evidence/m1-current-report.html), [próba](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-recenzja-Ultra/evidence/probe_reader.py). Sesja jest jawnie oznaczona jako syntetyczna; nie jest pomiarem zaworu.

## M1-11 — ważne: zmiana kalibracji CH6 pozostawia dawną akceptację toru prądu

**Miejsce:** [profile.c:38](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Rewizje/EGRLab-v6.3-m1/firmware/main/profile.c:38) i linia 60; [app_main.c:481](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Rewizje/EGRLab-v6.3-m1/firmware/main/app_main.c:481); opis M1 w [05-profile.md:3](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Rewizje/EGRLab-v6.3-m1/docs/05-profile.md:3).

`cal <bank> 5 gain offset` jest teraz kalibracją napięcia używanego do obliczenia prądu. Komenda kasuje `voltage_calibrated` oraz `qualified`, ale pozostawia `current_calibrated` i `current_window_qualified`. Zapisane wcześniej `current_zero` i `current_volts_per_amp` odnoszą się do poprzedniego przekształcenia CH6. Po samym `vcalok` warunek `qualify` ponownie przechodzi bez nowego odbioru prądu. Dla porównania `ivpa` prawidłowo kasuje obie akceptacje prądowe.

**Dowód:** rzeczywiste `profile_command` wykonuje `cal 1 5 0.8 0.5` na odebranym profilu:

```text
AFTER_CH6_CAL accepted=1 vcal=0 ical=1 metric=1 qualified=0
AFTER_VCAL accepted=1 qualify_predicate_without_HARDWARE_ACCEPTED=1
```

Przykład zależności: stary wzór `I=(V−2,5)/0,25` daje 1 A przy 2,75 V. Nowe przekształcenie `0,8·V+0,5` zachowuje zero, ale z dawnym V/A daje **0,8 A**. Jest to kontrolowany przykład matematyczny, nie oszacowanie typowego błędu rzeczywistej płytki. Pokazuje, że sam pomiar zerowy nie wykryje nieaktualnej skali. Zależne są także metryki tarcia i progi prądu. Użytkownik nadal musi wykonać `vcalok` i `qualify`; błąd nie obchodzi tych poleceń, lecz pozwala im polegać na nieaktualnym `icalok`.

**Proponowana zmiana:** zmiana gain/offset CH6 musi unieważniać odbiór prądu danego banku i kwalifikację jego metryki; nie dopuszczać używania toru jako odebranego do ponownego potwierdzenia. Zweryfikować również zależności przy `daqmodule`, skoro ADC należy teraz do toru prądu. Alternatywne algebraiczne przeliczenie zero/V/A wymaga jawnie określonego kontraktu; nie powinno po cichu udawać nowego pomiaru odbiorczego.

**Warunek zamknięcia:** test zmian każdego współczynnika CH6 oraz wymiany DAQ. Po samej akceptacji napięć `qualify` ma odmawiać do wykonania wymaganego odbioru prądu. Kanały nieprądowe nie powinny bez powodu kasować jego kalibracji.

Dowód: [probe_producer.c](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-recenzja-Ultra/evidence/probe_producer.c), [wynik kalibracji](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-recenzja-Ultra/evidence/producer-and-trigger.txt).

## M1-12 — drobne: brak wiarygodnego pomiaru generuje zdarzenia usterki REF i FEEDBACK

**Miejsce:** [trigger.c:108](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Rewizje/EGRLab-v6.3-m1/firmware/main/trigger.c:108) i linia 111, [app_main.c:158](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Rewizje/EGRLab-v6.3-m1/firmware/main/app_main.c:158), `trigger_configure` linie 52–53, `daqmodule` linie 466–475.

Przy nieodebranej kalibracji akwizycja przekazuje `NaN` zamiast napięć. Mapa może jednak pozostać znana, np. po `daqmodule` lub edycji `cal` w zapisanym profilu. `cfg.ready` wymaga tylko mapy. Warunki `!(ref>=4.5 && ref<=5.5)` i analogiczny dla feedbacku są prawdziwe również dla `NaN`. Logger zgłasza więc oba zdarzenia, mimo braku podstaw do oceny tych napięć.

**Dowód:** rzeczywisty `trigger_sample` dla ośmiu `NaN`, znanej mapy i `voltage_calibrated=false` zwraca maskę **9 = REF + FEEDBACK**. Próba kontrolna z rzeczywistym REF=4 V i poprawnym feedbackiem zwraca tylko REF. Każdy fałszywy warunek może być ponawiany co 250 ms. Zdarzenia zawierają wartości `null`, więc nie powstaje zmyślona liczba napięcia; mimo to nazwy zdarzeń mylą stan „brak pomiaru” z usterką obwodu.

**Proponowana zmiana:** oddzielić niedostępność/nieodebranie pomiaru od zdarzenia „zmierzone napięcie poza zakresem”. Warunki REF/FEEDBACK poprzedzić kontrolą ważności i skończoności odpowiednich danych. Pozostawić osobne zdarzenie jakości danych, jeśli ma wyzwalać zapis.

**Warunek zamknięcia:** NaN/invalid/nieodebrany bank nie wyzwala REF/FEEDBACK; prawdziwe 4 V oraz feedback poza zakresem nadal je wyzwalają. Dowody: ta sama [próba C](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-recenzja-Ultra/evidence/probe_producer.c) i [wynik](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-recenzja-Ultra/evidence/producer-and-trigger.txt).

## Poprzednie zgłoszenia — aktualna ocena

Pełne opisy i dowody pozostają w [pierwszej recenzji](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-recenzja-Astra/RECENZJA-M1-R1.md). To są otwarte punkty, nie dodatkowe nowe błędy:

| ID | Waga | Stan po drugim przeglądzie |
|---|---|---|
| M1-01 | ważne | Podtrzymane: brak prawidłowo określonego zasilania wszystkich domen w USB-only. Doprecyzowanie poniżej. |
| M1-02 | ważne | Odtworzone ponownie: TEST bez VBAT_CAR kończy się SUPPLY; 16,8 V wykracza ponad próg 16,5 V. |
| M1-03 | ważne | Podtrzymana luka trwałej blokady po błędzie inicjalizacji WDT; zakres dowodu doprecyzowany poniżej. |
| M1-04 | ważne | Podtrzymane: fsync co 1 s nie ogranicza utraty kolejki PSRAM do 1 s. |
| M1-05 | ważne | Kod nadal nadpisuje projekt KiCad; wcześniejsza reprodukcja dotyczy identycznych plików. Samodzielnej destrukcyjnej próby generatora nie powtarzano. |
| M1-06 | ważne | Szczegółowa instrukcja TEST nadal nie wylicza odłączenia wszystkich pięciu żył ECU; ogólny zakaz jest, lista wykonawcza niepełna. |
| M1-07 | drobne | Brak fixture'ów w niezmienionej paczce; wynik 96/102 pochodzi z pierwszej recenzji, nie z ponownego uruchomienia całej suity Python. |

**M1-01 — uściślenie elektryczne.** Oficjalny schemat rodziny Waveshare pokazuje USB VBUS → D1 B5819WS → VDDUSB → pin 5V modułu. To zasila szynę 5V M1, także po wyłączeniu pakietu. Dioda należy do modułu Waveshare, nie jest diodą CAN o tym samym numerze na M1. Blokuje zasilanie hosta z płytki; nie ma podstaw do twierdzenia, że następuje zwarcie USB do wyjścia TSR.

Nie można przesądzić, że VDRIVE wynosi dokładnie zero: możliwe są nieokreślone drogi zasilania wstecznego. Pewne jest, że U2 nie ma wtedy zaprojektowanego źródła pakietowego. Dla GPIO≈3,3 V warunek wejścia ADC `VIN≤VDRIVE+0,3 V` jest naruszony, **jeżeli VDRIVE spadnie poniżej około 3,0 V**. To wymaga pomiaru; w pierwszym raporcie wartość 0 V była przypadkiem granicznym, nie wynikiem pomiaru. [Schemat Waveshare](https://files.waveshare.com/wiki/ESP32-S3-DEV-KIT-N8R8/ESP32-S3-DEV-KIT-N8R8-schematic.pdf), [AD7606B, tabela 6](https://www.analog.com/media/en/technical-documentation/data-sheets/AD7606B.pdf).

Jeśli pozostaje decyzja „USB wyłącznie do danych”, rozwiązaniem do weryfikacji jest odcięcie **drogi zasilania przez D1 na konkretnym module**, z zachowaniem VBUS dla detekcji huba/konwertera. Nie zalecam w ciemno kabla bez 5 V ani odlutowania elementu bez sprawdzenia rewizji posiadanej płytki. Alternatywą jest zdefiniowane zasilanie całego M1 z USB. W obu wariantach trzeba odebrać BAT/USB włączone i wyłączone oraz kolejność zaniku szyn.

**M1-03 — granice dowodu.** Próba potwierdza, że błąd nie ustawia trwałego warunku `watchdogs_ok=false`, a istniejąca bramka może być zwolniona przez następny commit. Nie symuluje całego ESP-IDF po błędzie: powtarzane logowanie błędu TWDT może samo spowalniać zadania. Nie należy zatem twierdzić, że na gotowej płytce już zmierzono możliwość jazdy bez watchdogów. To wciąż błąd obsługi awarii w kodzie, do naprawienia i próby integracyjnej.

## Co sprawdzono ponownie i co przeszło

| Kontrola wykonana w tym przeglądzie | Wynik |
|---|---|
| Integralność wejścia względem pierwszego przeglądu | 531/531 identycznych plików, 529/529 wpisów manifestu |
| Świeży KiCad ERC | 0 naruszeń, 7 arkuszy |
| Świeża netlista → części | 93 elementy, 357 sprawdzonych pinów, 99 sieci, 0 rozbieżności |
| `verify_m1.py` | 8/8 kontroli, 16/16 mutacji + kontrola zerowa |
| Świeży DRC z wypełnieniem stref i zgodnością schematu | 0 naruszeń, 0 niepołączonych, 0 rozbieżności |
| `verify_pcb.py` | 11/11 kontroli, 13/13 prób ujemnych, w tym zerowa; zakres tych prób opisano niżej |
| Dodatkowa niezależna mapa zasilania/interfejsów | 126 porównań oczekiwanych pinów/sieci z XML i PCB, 0 rozbieżności |
| Odtworzenie CAM z finalnego PCB | 11 plików ZIP zgodnych z katalogiem produkcyjnym; brak istotnej różnicy świeżego eksportu |
| Oryginalne regresje C | control: 131, runtime: 66, health: 58, OBD: 23 — bez błędów |
| Nowe próby integracyjne | Odtwarzają M1-08…M1-12 zgodnie z opisanymi granicami |

KiCad zgłosił także ostrzeżenie Fontconfig o katalogu cache; nie było naruszeniem ERC/DRC i nie zatrzymało kontroli. W wynikach DRC nie było nawet wyjątku `lib_footprint_mismatch`, który skrypt potrafi tolerować.

Oględziny czterech warstw miedzi połączono z odczytem geometrii finalnego PCB. In1 pozostaje ciągłą masą poza świadomymi wyłączeniami; zachowano strefę anteny. Po świeżym eksporcie maski, nadruki, obrys, In1/In2 oraz wiercenia odpowiadają paczce po odjęciu metadanych. Różnice wierzchołków F/B wynoszą maksymalnie **1 nm**, bez znaczenia produkcyjnego. Nie należy przedstawiać ich jako nowego błędu CAM.

Pełne kompilacje pięciu wariantów ESP-IDF oraz pełny łańcuch odtwarzania layoutu były wykonane w pierwszym przeglądzie na identycznych źródłach. **Nie liczę ich jako ponownie wykonanych w tej sesji.** Przekazany firmware nie został zmieniony; nowe próby kompilują wybrane rzeczywiste funkcje na hoście i zastępują platformę. Nie zastępują ESP32 ani stanowiska.

## Kwalifikacja analogu i zalecenia procesu — poza liczbą pięciu błędów

Poniższe punkty mają znaczenie dla P0404 i testów termicznych, ale nie wykazują kolejnych pewnych usterek:

1. **PWM a 2 kS/s.** OS8 AD7606B zbiera osiem szybkich próbek w około 10 µs; nie uśrednia całych 500 µs. Zewnętrzne filtry kanałów silnika mają około 9,79 kHz, czujnika około 7,38 kHz. Surowych próbek nie wolno utożsamiać z dokładnym duty ani średnią dowolnego PWM. Potrzebne porównanie z oscyloskopem przy kilku fazach i częstotliwościach; średnia prądu wymaga własnego odbioru. Nie wykazano tu algorytmu błędnie obliczającego duty. [AD7606B, filtr i tabela 17](https://www.analog.com/media/en/technical-documentation/data-sheets/AD7606B.pdf).
2. **Zero prądu zależy od 5 V.** Przy REF=VS/2 i nominalnych 0,25 V/A zmiana VS o 50 mV daje około 0,10 A przesunięcia. To obliczenie czułości, nie pomiar tętnień. Należy porównać zero przy SD/WiFi, PWM i temperaturze. Dwupunktowa kalibracja napięć obejmuje również statyczny bias wejść ADC; samego biasu nie kwalifikuję jako nowego błędu. [INA240, odniesienie i praca dwukierunkowa](https://www.ti.com/lit/ds/symlink/ina240.pdf).
3. **Odsprzęganie trzeba oceniać pełną pętlą.** Pomiar geometrii daje C24→U4.6 około 6,9 mm, powrót do U4.2 około 7,7 mm; C6→U3.1 około 2 mm i powrót około 10 mm. Metoda rastrowa ma ograniczoną dokładność i nie mierzy impedancji HF. To powód do skrócenia pętli przy następnej zmianie layoutu i próby oscyloskopem, nie dowód niestabilności. C8 lokalnie obsługuje zwarte AVCC37/38 — odległy C7 nie dowodzi braku odsprzęgania pin37.
4. **Zakres kontroli powrotów jest węższy niż sugeruje PASS.** `return_check` pomija C6…C15, bada tylko stronę GND, a limit rośnie z odległością kondensatora. Próby ujemne PCB zmieniają gotowy opis wyniku/geometrii, nie fizyczny plik i całe ponowne wydobycie cech. Dodać stałe limity par zasilanie/GND, liczbę przelotek oraz kilka mutacji rzeczywistej kopii PCB. Obecne testy są użyteczne, lecz nie stanowią pełnego dowodu jakości odsprzęgania.
5. **Kelvin i tor mocy.** Nie znaleziono pomylenia sense/force ani znaków INA240. K_PLUS ma około 8,96 mm, K_MINUS 25,02 mm i dwie przelotki. Masa pomiędzy warstwami nie zastępuje próby zakłóceń. Potrzebny prąd DC/PWM ze wzorcem oraz skok wspólny przy zerowym prądzie. F1 nie znajduje się w torze LOGGER ECU→EGR, więc jego 7,5 A nie jest uzasadnieniem zakresu pomiarowego LOGGER. Nie wykazano, że rzeczywisty wymagany zakres przekracza około ±9 A.
6. **AVCC i zakres temperatur przyrządu.** Wąski limit 4,75…5,25 V wymaga budżetu dokładności TSR i spadku na R7, a nie tylko zapasu 2 A. Konserwatywny narożnik szerokiego zakresu temperatur może wyjść poza limit; dokumentacja M1 nie deklaruje jednak pracy elektroniki od −40 do +85°C. Traktuję to jako warunek odbioru deklarowanego zakresu, nie pewną wadę stołową. Szczegółowe liczby i założenia są w notatce zasilania. [TRACO TSR2](https://www.tracopower.com/products/tsr2.pdf).
7. **TPS2553.** R31=232 kΩ 1% daje obliczeniowo około 98,7…138,6 mA, typowo 117 mA. To nie twarde maksimum 100 mA. Zapas źródła jest nadal wystarczający; wystarczy poprawić opis/budżet, jeżeli taki zakres jest zamierzony. Nominalny 232 kΩ 1% nie narusza sam w sobie dopuszczalnego doboru. [TPS2553, sekcja 9.5.1](https://www.ti.com/lit/ds/symlink/tps2553.pdf).
8. **GPIO i moduły.** Nie znaleziono kolejnego odpowiednika błędu pull-up GPIO39. 45 kΩ jest wartością typową; przyjęte 20 kΩ nie jest gwarantowanym minimum producenta. Nadal pozostają pomiary resetu, przymiarka 1:1 posiadanych modułów oraz sprawdzenie 3Vo i poziomów cyfrowych konkretnych MAX31856 XU. Schemat Adafruit nie może zastąpić schematu modułu XU.

Pełne obliczenia i granice metod: [analog/PCB/CAM](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-recenzja-Ultra/evidence/analog/ANALOG-PCB-CAM-NOTATKA.md), [zasilanie i interfejsy](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-recenzja-Ultra/evidence/power/NOTATKI-ZASILANIE-I-INTERFEJSY.txt). To materiały pomocnicze; klasyfikacja zgłoszeń w niniejszym raporcie ma pierwszeństwo.

## Kolejność zamykania

Najpierw rozstrzygnąć połączenia USB i źródło napięcia CH7 w TEST, bo mogą wpływać na hardware. Równolegle poprawić M1-08…M1-12 wraz z trwałą obsługą błędu WDT. Następnie ujednolicić instrukcję przepięć, zakończenia logowania i testy zależności.

Do bramki wydania dodać trzy kontrole obejmujące więcej niż pojedynczy moduł: realny producent config/rekordu → czytnik; błąd peryferium → odzyskanie → ważność danych; wolna konsola/zajęty mutex → czas zatrzymania. Do tego macierz unieważniania kalibracji po zmianie parametrów. Testy mają najpierw odtworzyć problem na R1, a następnie przejść po poprawce bez zmiany bodźca.

Po tych poprawkach powtórzyć ERC/DRC/CAM tylko dla zmienionego hardware, a odpowiednie kompilacje i regresje dla firmware. Nadal wymagane są rzeczywiste próby zasilania, napędu, ADC, SD, termopar i dokładności cieplnej. **Sprzęt: NIE ZBADANO.** Wynik recenzji nie jest odbiorem zmontowanego urządzenia ani gwarancją wyczerpania wszystkich błędów.
