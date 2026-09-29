# EGRLab v3 — ponowna weryfikacja projektu
Data: 22.09.2026. Samochód: Kia Sportage 1.7 CRDi, 2013; EGR 28410-2A850.

**Werdykt: v3 jest wyraźnie lepszą podstawą od v2, ale nie jest jeszcze kompletnym projektem do wykonania i uruchomienia aktywnego TEST.** Wiele poprawek jest rzeczywistych. Nie potwierdzam jednak deklaracji „naprawiono wszystkie”: pozostały błędy blokady sprzętowej, przełączania konfiguracji i wiarygodności danych. Część z nich ujawnia się dopiero po kalibracji albo podczas zmiany trybu, więc poprawne testy syntetyczne ich nie wykluczają.

Posiadany Waveshare ESP32-S3 N32R16-M pozostaje sensownym MCU. W tym przeglądzie nie znalazłem powodu do zakupu innego procesora. Najpilniejsze problemy dotyczą obwodów bezpieczeństwa i integracji oprogramowania. Pamięć i wariant modułu należy potwierdzić dla posiadanej rewizji według [dokumentacji Waveshare](https://www.waveshare.com/wiki/ESP32-S3-DEV-KIT-N8R8).

## Zakres i dowody

Przejrzałem dokumentację zmian, projekt połączeń, BOM, pinout, procedury, plan uruchomienia, źródła firmware i narzędzia do logów. Porównałem je z uwagami F01–F13 do v2 oraz dokumentacją producentów. Pliki źródłowe v3 pozostały niezmienione.

| Weryfikacja wykonana | Wynik |
|---|---|
| Manifest SHA256 dostarczony z v3 | 38/38 zgodnych plików |
| Testy Python dołączone do v3 | 23/23 przeszły |
| Oryginalne testy `tests/test_control.c` i oryginalny `control.c`, uruchomione na PC | 11 grup, 107 asercji, 0 niepowodzeń |
| Rzeczywista funkcja `storage_config()`, wyjęta bez zmian do programu na PC | Konfiguracja z niezerowymi offsetami: **559 B**, limit zdarzenia **512 B** |
| Rzeczywista `board_adc_ranges()`, z zasymulowanym timeoutem mutexu | Błąd zwrócony, ale `applied[]` nietknięte i `config_ok=true` |
| Oryginalny eksporter, brak konfiguracji dla próbki | **19,999 mV → 79,996 mV** z ostrzeżeniem |
| Oryginalny eksporter, `learned=false` | Nadal wylicza pozycję: **około 50%** |
| Oryginalny eksporter, `adc_config_ok=false` | Nadal wylicza napięcia i prąd bez jakości w wierszu CSV |
| Oryginalny generator HTML, skok w jednej próbce | W pliku **399,978 mV**, na wykresie maksimum **20 mV** |

**Granice tych wyników:** testy C uruchomiłem kompilatorem TinyCC na Windows, z małym nagłówkiem zastępującym niezgodne funkcje matematyczne starego pakietu kompilatora. Źródeł v3 nie poprawiałem. Próby funkcji sprzętowych używają atrap otoczenia, a nie ESP-IDF. Nie jest to kompilacja całego firmware dla ESP32, test współbieżności FreeRTOS, pomiar elektryczny ani potwierdzenie EMC.

Odtwarzalne materiały:
- [Skrypt prób](C:/Users/tgorbacz/.codex/.chatgpt-projects/g-p-6a8827e57cc881919b26f761377a7bd3/EGRLab-v3-review/check_review.py)
- [Wyniki i kontrprzykłady](C:/Users/tgorbacz/.codex/.chatgpt-projects/g-p-6a8827e57cc881919b26f761377a7bd3/EGRLab-v3-review/counterexamples.json)
- [Wynik formatowania konfiguracji w C](C:/Users/tgorbacz/.codex/.chatgpt-projects/g-p-6a8827e57cc881919b26f761377a7bd3/EGRLab-v3-review/host-probes.txt)
- [Manifest przejrzanych plików](C:/Users/tgorbacz/.codex/.chatgpt-projects/g-p-6a8827e57cc881919b26f761377a7bd3/EGRLab-v3-review/reviewed-files.sha256.json)
- [Przykład wykresu pomijającego skok](C:/Users/tgorbacz/.codex/.chatgpt-projects/g-p-6a8827e57cc881919b26f761377a7bd3/EGRLab-v3-review/fixtures/decimation/report.html)

Priorytet **P1** oznacza poprawkę potrzebną przed uznaniem odpowiedniej funkcji za gotową do pracy z zaworem/wiarygodnej diagnostyki. **P2** oznacza istotny błąd funkcjonalny lub brak projektu. Nie nadaję P0: aktywny TEST jest domyślnie zablokowany, a urządzenie nie zostało uruchomione.

## Stan wcześniejszych uwag F01–F13

| Uwaga z v2 | Ocena v3 | Uzasadnienie |
|---|---|---|
| F01 — SAFE_N, STOP i bramki | **Częściowo** | Usunięto push-pull i dodatkowy pull-up; rozpisano sześć bramek. Pozostaje sprzężenie resetu watchdoga i niedokończony interlock: R01–R02. |
| F02 — polaryzacja i OVP | **Poprawiona koncepcja** | Bazowy LM74800EVM-CD i pomiar nastawy OVP są właściwym kierunkiem. Alternatywny PMOS ma poprawioną orientację. To nadal nie jest wynik prób przepięciowych. |
| F03 — wspólna cewka KMEAS3 | **Poprawione** | KCUR jest oddzielnym przekaźnikiem. |
| F04 — AD7606B i fallback | **Częściowo** | Format rejestrów, CONFIG, OS i wyjście z register mode poprawne. Obsługa błędów zakresów nadal potrafi opublikować niewiarygodną konfigurację: R05. |
| F05 — pamięć kierunku | **Główny błąd poprawiony** | Znak aktualizowany po sukcesie zapisu, resetowany przy zerowaniu portu. Pozostaje niezgodność deklarowanego czasu przerwy: R13. |
| F06 — kalibracja w logach | **Częściowo** | `config_id` jest dobrym rozwiązaniem, ale zapis, przełączenie i odtworzenie konfiguracji nie tworzą jeszcze spójnego procesu: R03–R07. |
| F07 — konfiguracja kontra akwizycja | **Częściowo** | Jest osobne zadanie, ale odczekanie 20 ms nie potwierdza zakończenia odczytu; przekaźniki nadal przełączane poza tą procedurą: R04–R05. |
| F08 — uszkodzony literał C | **Konkretny błąd poprawiony** | Kontrola leksykalna przechodzi. Cały projekt nadal wymaga kompilacji ESP-IDF. |
| F09 — obcinanie summary | **Konkretny błąd poprawiony** | Sprawdzanie długości i `summary_dropped` usuwają ciche ucinanie. Nowy, większy obiekt `config` ma osobny problem R03. |
| F10 — AP i webowy STOP | **Częściowo** | Stany adapterów publikowane; wspólny dispatcher poprawia STOP. Pozostają wejścia adapterów i cykl życia AP: R02, R09. |
| F11 — kanał DHO804/opóźnienie | **Poprawione w dokumentacji** | Zajęty kanał i opóźnienia triggerów opisano jasno. |
| F12 — AUX | **Główny błąd poprawiony** | DPDT odłącza RB4, oddzielne kalibracje HI/LO, spójny stan początkowy. Wymagany końcowy schemat i pomiar obu ustawień. |
| F13 — detektory | **Częściowo** | Ważność prądu, blokada 250 ms i okno nominalnie 1 ms są zasadne. Zapis zdarzeń L2 jest wadliwy: R08. |

**Korekta mojego poprzedniego opisu F13:** dokument `v2/docs/04-firmware-logi.md` rzeczywiście podawał 0,5 ms między sąsiednimi próbkami. Sformułowanie z mojego przeglądu o jednoznacznie deklarowanym 1 ms było zbyt szerokie; informacja o 1 ms pozostała w historii zmian v2. Przy jasnej specyfikacji sam wybór sąsiednich próbek nie stanowi błędu. W v3 okno zależy od nominalnej częstotliwości, a nie od różnicy rzeczywistych znaczników czasu; nie należy mylić tych dwóch rzeczy przy jitterze lub GAP.

## Usterki i wymagane poprawki

### R01 — P1: watchdog może utrzymywać własny reset

Źródła: [połączenie U5 z SAFE_N](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/hardware/connections.csv:109), [schemat wspólnego węzła](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/docs/01-projekt.md:176), [reset watchdoga](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/docs/01-projekt.md:224).

Dokumentacja łączy wyjście supervisora `SUP_3V3` bezpośrednio z `SAFE_N`, a następnie podłącza do `SUP_3V3` wejście /CLR układu 74HC123. Połączenie przewodem oznacza ten sam węzeł, niezależnie od dwóch nazw.

Dla dosłownego wykonania rysunku:
1. Q watchdoga = 0.
2. Inwerter podaje 1 na Q8; Q8 ściąga SAFE_N do masy.
3. /CLR watchdoga także ma 0.
4. Reset wymusza Q = 0, więc heartbeat nie zwalnia tego stanu.

To stabilne samopodtrzymanie resetu: może uniemożliwić start oraz powrót po STOP/timeout. Jest to wniosek z połączeń, nie wynik pomiaru płytki. Dominujący reset i stan Q przy resecie potwierdza [dokumentacja TI 74HC123, tabela funkcji na stronie 2](https://www.ti.com/lit/ds/symlink/cd74hc123.pdf).

**Poprawka:** rozdzielić samodzielny sygnał nadzoru zasilania od zbiorczej linii SAFE_N. Nadzór może resetować monostabilny i przez odpowiednio odseparowany stopień otwarty wpływać na SAFE_N. Nie wolno „naprawiać” tego drugim pull-upem na SAFE_N, bo odtworzyłby obejście STOP z v2.

**Odbiór:** zimny start, STOP na ponad 150 ms, timeout heartbeat, powrót heartbeat. SAFE_N ma odzyskać gotowość, ale HW_ARMED ma pozostać 0 do nowego naciśnięcia ARM.

### R02 — P1: interlock i wejścia obecności adapterów nie mają spójnej realizacji

Źródła: [opis pętli](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/docs/01-projekt.md:57), [INTERLOCK_LOOP](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/hardware/connections.csv:113), [wejścia MCP](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/hardware/connections.csv:145), [pull-upy portu B](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/firmware/main/board.c:212), [interpretacja stanów](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/firmware/main/board.c:298).

Zapis „pętla zwiera do masy przy rozwarciu” opisuje oczekiwaną funkcję, lecz pasywny szeregowy obwód NC sam jej nie realizuje. Potrzebny jest konkretny układ odwracający stan oraz jawne połączenie z GPIO42. Q8 w BOM jest już wykorzystany przez watchdog.

Jednocześnie firmware włącza pull-upy na całym porcie B i interpretuje B5=1 jako TEST obecny. Przy otwartej pętli TEST i braku osobno określonego pull-downu B5 również ma 1. Dla B4 nazwano sygnał LOG_PRESENT_N i użyto negacji, ale krańcówki są NC rozwierane przez wtyk. Przy zwykłym połączeniu takiej pętli do masy kod zgłasza LOGGER wtedy, gdy gniazda są puste. Schemat nie określa innego stopnia, który usuwa tę niezgodność.

**Poprawka:** narysować kompletny obwód z rezystorami, stykami, polaryzacjami i przetworzeniem na wyjście otwarte. Dodać fizyczne źródło TEST_KEY; samo `MCP.B0` w równaniu bramki nie wystarcza.

**Odbiór:** tabela prawdy dla braku adapterów, tylko TEST, każdego gniazda LOGGER osobno, L1/L2, obu adapterów i każdego przerwanego przewodu. Wszystkie te stany sprawdzić także przy zatrzymanym MCU. Brak pełnego schematu jest tutaj usterką projektu, a nie dowodem, że jakaś istniejąca płytka na pewno zachowuje się niebezpiecznie.

### R03 — P1: skalibrowana konfiguracja nie mieści się w kolejce zdarzeń

Źródła: [limit 512](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/firmware/main/storage.h:26), [formatowanie konfiguracji](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/firmware/main/storage.c:102), [ignorowany wynik zapisu](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/firmware/main/app_main.c:145).

Próba z rzeczywistą funkcją C daje:
- konfiguracja startowa bez offsetów: 449 B;
- nominalna po LEARN: 465 B;
- ta sama konfiguracja z ośmioma offsetami około 1,2–9,9 mV: **559 B**.

Bufor musi pomieścić również końcowe zero, więc `storage_event()` odrzuca ostatnią linię i ustawia zapis jako niezdrowy. Skutki są dwa: TEST może kończyć się błędem zapisu, a próbki LOGGER mogą powstawać z `config_id`, którego nie ma w NDJSON. Kod wcześniej publikuje nową konfigurację, nie sprawdza wyniku `storage_config()` i wznawia akwizycję.

To nie jest problem każdego startu: nominalny profil się mieści. Problem pojawia się właśnie po wpisaniu rzeczywistych współczynników, czego wymaga procedura odbioru.

**Poprawka:** przyjąć i przetestować górną granicę rozmiaru całego obiektu, np. odpowiednio większy bufor z kontrolą długości, albo zastosować dedykowany rekord konfiguracji. Publikację nowego ID uzależnić od skutecznego przyjęcia metadanych do zapisu; brak trwałego wpisu musi być wykrywalny przy odczycie. Uwzględnić kolejność zapisu i awarię zasilania między dwoma plikami.

**Odbiór:** konfiguracja z niezerowymi gain/offset, długim timestampem, wszystkimi flagami, ID i wartościami krańcowymi przechodzi rzeczywisty serializer C → NDJSON → Python.

### R04 — P1: przekaźniki zmieniają tor przed zatrzymaniem akwizycji i zmianą config_id

Źródła: [dispatcher](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/firmware/main/app_main.c:333), [board_mode](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/firmware/main/board.c:278), [pobranie konfiguracji próbki](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/firmware/main/app_main.c:75).

Dispatcher wywołuje `board_mode()` bez zatrzymania próbkowania. Funkcja zeruje port, czeka 100 ms, ustawia nowy bank i — przy włączeniu czujnika — czeka kolejne 100 ms. Dopiero po jej zakończeniu wysyłane jest żądanie do `config_task`.

Przy 2 kS/s daje to rząd 200–400 próbek z rozłączonego lub już zmienionego toru, nadal z poprzednim ID i kalibracją. Dokładna liczba zależy od planisty i przekaźników. Możliwe skutki: fałszywe triggery, błędny prąd, obliczenia z odłączonych wejść. Podwójny bufor konfiguracji tego nie usuwa.

**Poprawka:** jednym procesem objąć zatrzymanie odczytów, przełączenie banku i czujnika, czas ustalania, zakresy ADC, reset detektorów, metadane oraz wznowienie. Okno przełączenia oznaczyć jako przerwę/stan przejściowy. Awaryjne wyłączenie napędu musi pozostać natychmiastowe i niezależne od tego procesu.

**Odbiór:** różne znane napięcia/prądy w obu bankach, wielokrotne LOGGER → TEST → STOP → LOGGER; żadna próbka nowego toru nie może mieć starej konfiguracji.

### R05 — P1: pozorna synchronizacja ADC i błędna obsługa nieudanego przełączenia

Źródła: [config_task](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/firmware/main/app_main.c:126), [ustawienie flagi](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/firmware/main/board.c:83), [board_adc_ranges](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/firmware/main/board.c:142), [summary](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/firmware/main/trigger.c:132).

`board_adc_set_running(false)` tylko zapisuje zmienną. Nie zatrzymuje ani nie potwierdza zatrzymania zadania akwizycji. `esp_timer_stop()` i opóźnienie 20 ms nie dowodzą, że nie ma zaległego powiadomienia lub rozpoczętej transakcji. `board_adc()` nie bierze wspólnej blokady chroniącej sekwencję konfiguracji.

Dodatkowo funkcja zakresów przy timeout mutexu wraca przed wypełnieniem `applied[]` i przed ustawieniem `config_ok=false`. Wywołujący deklaruje tę tablicę bez inicjalizacji, a mimo błędu buduje z niej nową konfigurację. W próbie funkcji z mutexem odrzucającym wejście otrzymałem:
`error=3 config_ok=1 applied=a5,a5,a5,a5,a5,a5,a5,a5`.
Wartości A5 są celowym znacznikiem z próby; w aplikacji byłyby nieokreśloną zawartością stosu.

Na innej ścieżce błędu funkcja wpisuje wszystkie zakresy ±10 V, choć nie resetuje ADC do takiego stanu. Po częściowo udanych zapisach sprzęt może mieć mieszane zakresy. Wtedy `config_ok=false` blokuje TEST, co jest dobre, ale liczby w LOGGER nadal nie reprezentują potwierdzonego pomiaru.

Jest też współdzielony stan detektorów: `trigger_sample()`, `trigger_configure()` i `trigger_take_summary()` działają z różnych zadań bez pełnego protokołu przekazania. Podsumowanie nie niesie własnego ID, tylko dostaje aktualne ID podczas zapisu.

**Poprawka:** PAUSE/ACK od akwizycji, zakończenie ostatniej transakcji i opróżnienie powiadomień; dopiero potem zmiana. Wyjściowa konfiguracja ma być zawsze jawnie zainicjalizowana. Nieudana częściowa zmiana wymaga resetu i ponownego potwierdzenia albo oznaczenia skali jako nieznanej. Summary przekazywać jako kompletny komunikat z ID i bankiem.

**Odbiór:** wymuszone opóźnienia akwizycji, timeout blokady, błędy SPI po każdym kolejnym rejestrze i równoczesny odbiór summary. Nigdy nie publikować konfiguracji oznaczonej jako poprawna z niezainicjalizowanymi zakresami.

### R06 — P1: zero prądu może pochodzić z poprzedniego banku

Źródła: [zero](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/firmware/main/app_main.c:319), [summary_t](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/firmware/main/trigger.h:26), [zapamiętywanie podsumowania](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/firmware/main/app_main.c:250).

`zero` pobiera ostatnie globalne podsumowanie i zapisuje jego średnią do banku wybranego aktualnie w `ctrl`. Nie sprawdza banku, ID, wieku ani tego, czy całe okno obejmowało pewny zerowy prąd. `have_summary` nie jest unieważniane przy przejściu na inny bank.

Przykład: LOGGER ma zero 2,50 V, TEST 2,60 V. Po przełączeniu i wydaniu `zero` przed nowym pełnym podsumowaniem do profilu TEST trafi 2,50 V. Wtedy rzeczywiste 0 A będzie pokazywane jako **+0,40 A**. To model ścieżki kodu i rachunek, nie przeprowadzony pomiar fizyczny.

**Poprawka:** zero zbierać jako osobną operację po ustaleniu toru; akceptować wyłącznie nowe próbki aktywnego ID/banku z potwierdzonym odłączeniem napędu. Unieważniać stare summary. Profil kalibracji toru nie powinien przypadkowo zmieniać się przy wiązaniu nowego zaworu.

**Odbiór:** różne offsety obu INA, szybkie przełączenie banku i natychmiastowe `zero`; polecenie ma poczekać albo odmówić, nigdy użyć poprzedniego banku.

### R07 — P1: analiza nadal wylicza wiarygodnie wyglądające wartości bez ważnej konfiguracji

Źródła: [fallback konfiguracji](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/tools/egrlog.py:210), [przeliczanie fizyczne](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/tools/egrlog.py:120).

Brak pasującego ID daje ostrzeżenie, ale eksporter mimo to bierze konfigurację zapasową. CSV zawiera normalne liczby i nie ma kolumny jakości wyliczenia. Sprawdziłem oryginalnym kodem: około 20 mV z zakresu ±2,5 V po użyciu poprzedniego ±10 V daje około **80 mV**. To nadal potrafi przekroczyć ostrzegawczy próg 50 mV i zasugerować nieistniejący problem masy. Ostrzeżenie jest lepsze niż milczenie, lecz nie czyni błędnej wartości pomiarem.

Dwa dalsze przypadki:
- `adc_config_ok=false` nie wstrzymuje przeliczeń;
- `learned=false` nie blokuje pozycji, jeśli w obiekcie zostały liczby closed/open. Po zmianie egzemplarza i ponownym IDENTIFY mogą pozostać krańce poprzedniego zaworu.

**Poprawka:** w formacie v3 brak konfiguracji lub niepotwierdzone zakresy mają dawać surowe kody oraz jawną nieważność wielkości fizycznych, ewentualnie błąd całego eksportu. Tryb odzyskiwania z założoną skalą tylko jako wyraźnie wybrana opcja i z jakością przy każdym wierszu. Pozycję liczyć wyłącznie przy ważnym LEARN. Zgodność ze starszymi plikami obsłużyć odrębnie.

**Odbiór:** usunięcie jednego wpisu config, błąd ADC i unieważnienie LEARN nie mogą dawać zwykłej liczby traktowanej jako poprawny wynik.

### R08 — P1 dla LOGGER L2: nieważny prąd psuje JSON zdarzeń

Źródło: [serializacja triggerów](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/firmware/main/app_main.c:106).

Przy `bypass 1` prąd ustawiany jest na NAN. To poprawna reprezentacja wewnętrzna braku pomiaru. Jednak zdarzenie triggera wpisuje go przez `%.4f` jako token liczbowy. Wynik formatu NaN nie jest poprawną liczbą JSON.

W próbie oryginalny detektor dla L2 prawidłowo zgłosił oba progi masy (`mask=6`), a formatter systemowy Windows wyprodukował `1.#QNB`. Implementacje drukujące `nan`/ `NaN` także nie tworzą standardowego JSON; lowercase `nan` jest odrzucane przez używany czytnik Pythona. Nie twierdzę, że tekst Windows jest dokładnie tekstem biblioteki ESP-IDF.

Skutek: ważne zdarzenia napięcia/masy/pozycji L2 mogą znikać z `scan` i tabel raportu. Surowe próbki oraz bit SAMPLE_TRIGGER nadal mogą istnieć, więc nie oznacza to utraty całego pomiaru.

**Poprawka:** nieważne wielkości zapisywać jako `null` i osobną informację o ważności. Ten wzorzec już istnieje dla zdarzeń temperatury w tym samym pliku. Zastosować go także do HOT-SOAK, gdzie TC2 może być nieważna przy poprawnej TC1.

**Odbiór:** komplet zdarzeń przy `bypass 1` i brakującej TC2 przechodzi ścisły parser JSON; brak pomiaru nie usuwa całego zdarzenia.

### R09 — P2: SoftAP nie ma poprawnego restartu i blokuje zadanie bezpieczeństwa

Źródła: [webui_start/stop](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/firmware/main/webui.c:74), [wywołanie z safety](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/firmware/main/app_main.c:220).

Każdy start tworzy nowy domyślny interfejs AP. Stop zatrzymuje HTTP/Wi-Fi, lecz nie niszczy interfejsu sieciowego i nie przechowuje jego uchwytu. Sekwencja TEST → LOGGER → TEST ponownie wywołuje tworzenie domyślnego AP. Producent wprost zabrania ponownego tworzenia takiego interfejsu bez zniszczenia poprzedniego: [ESP-NETIF, Wi-Fi Default Initialization](https://docs.espressif.com/projects/esp-idf/en/v5.3/esp32s3/api-reference/network/esp_netif.html#wi-fi-default-initialization).

Ponadto start/stop HTTP i Wi-Fi wykonuje bezpośrednio `safety`, trzymając `control_mutex`. Są to operacje potencjalnie blokujące, a ten sam task ma co 1 ms kontrolować napęd i odświeżać heartbeat. Zakończenie HTTP może także czekać na handler, który czeka na ten mutex. Nie jest to potwierdzony pomiarem deadlock; jest to zła zależność czasowa, mogąca powodować przestoje i timeout watchdoga.

**Poprawka:** zachować jeden interfejs przez cały cykl życia albo poprawnie go usuwać; zarządzanie radiem przenieść do osobnego zadania. Safety publikuje tylko żądany stan, bez czekania na sieć.

**Odbiór:** wielokrotny start/stop AP, równoczesne komendy HTTP i pomiar maksymalnego odstępu safety/heartbeat. Test z włączonym opcjonalnym Wi-Fi jest konieczny osobno od domyślnego buildu.

### R10 — P2: raport HTML usuwa krótkie zdarzenia przez wybór co N-tej próbki

Źródło: [report](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/tools/egrlog.py:319).

Raport wybiera `rows[::step]`. To wybór pojedynczych punktów, bez zachowania minimum/maksimum w pomijanym przedziale. Na przygotowanym pliku 6002 rekordów skok masy do **399,978 mV** wypada między wybranymi punktami; wykres pokazuje tylko **20 mV**. Dla 30 minut przy 2 kS/s wybór jest znacznie rzadszy.

Ten błąd nie usuwa surowych danych. Jest istotny, bo użytkownik szukający krótkich zaników i skoków może uznać wykres za czysty. Dodatkowo funkcja ładuje wszystkie rekordy do listy, więc pamięć rośnie wraz z całą sesją.

**Poprawka:** strumieniowa agregacja zachowująca min/max i punkty triggerów; możliwość pokazania pełnej rozdzielczości wokół zdarzenia. Widoczna informacja o rozdzielczości wykresu. Do pracy bez internetu dołączyć lokalną bibliotekę wykresów zamiast wyłącznej zależności od CDN.

**Odbiór:** pojedyncze impulsy umieszczone we wszystkich fazach względem grupowania muszą pozostawać widoczne; sesja wielogodzinna nie może wymagać wczytania wszystkich rekordów naraz.

### R11 — P2: BOM i instrukcje wykonania nadal nie zamykają projektu

Źródła: [BOM](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/hardware/BOM.csv:10), [etap zasilania](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/docs/03-uruchomienie.md:13), [deklaracja wpisania kalibracji](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/docs/03-uruchomienie.md:128).

Konkretne braki:
- MCP23017 jest wymagany w firmware i połączeniach, ale **nie występuje w BOM**. U10 w v3 oznacza już bramki AND.
- STOP w połączeniach ma styk pomocniczy `SW_STOP.aux`, a BOM zamawia tylko grzybek NC. Trzeba określić liczbę i rodzaj styków.
- Etap 2 nadal każe montować P-MOS, chociaż bazowa wersja v3 wymaga modułu OVP LM74800EVM-CD.
- Nie ma kompletnego połączenia kluczyka TEST, polaryzacji wejść interlock, zasilania wszystkich układów nadzoru ani jednoznacznego pinowego schematu adaptera z przestawianymi zworkami.
- Procedura wymaga wpisania zmierzonych gain/offset i limitów do profilu. Konsola ma `zero` i `learn`, lecz nie ma importu `profile.template.json` ani poleceń ustawiających ogólne gain/offset/limity. Sam plik JSON nie jest wczytywany przez firmware. Ręczna edycja źródła jest możliwa, ale nie została opisana jako pełna procedura, a istniejący profil NVS nadpisuje wartości domyślne.

**Poprawka:** zaktualizować BOM, wybrać jeden bazowy wariant zasilania i dostarczyć schemat z numerami wyprowadzeń. Dodać kontrolowaną drogę załadowania i odczytu kalibracji z numerem wersji, walidacją i potwierdzeniem zapisu; ewentualnie bardzo konkretną procedurę kompilacji/wyczyszczenia lub migracji NVS.

To znaczący brak wobec celu „cały gotowy projekt na start”, nawet jeśli dokumentacja uczciwie przyznaje brak PCB i Gerberów.

### R12 — P2: zakres ±5 V maskuje część przepięć na zasilaniu czujnika

Źródła: [dobór zakresów](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/firmware/main/control.c:39), [próg triggera ref](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/firmware/main/trigger.c:102).

Po IDENTIFY zasilanie czujnika trafia na ±5 V. Przy przeliczniku około 1,01996 maksymalna rekonstruowana wartość dodatnia wynosi około **5,10 V**. Jednocześnie górny próg `ref` wynosi 5,5 V. Gdy pin zasilania wzrośnie np. do 6 V przy masie bliskiej zera, ADC się nasyci, ale przeliczenie pozostanie około 5,10 V i nie uruchomi górnego progu 5,5 V. W kodzie nie ma odpowiadającej temu kontroli nasycenia.

**Poprawka:** dla kanału zasilania sensora pozostawić ±10 V albo tak dobrać front-end, aby zakres obejmował próg błędu z zapasem; dodatkowo wykrywać kody bliskie nasyceniu i oznaczać pomiar jako poza zakresem. Masa może nadal korzystać z ±2,5 V.

**Odbiór:** kontrolowane napięcia przed, na i ponad pełną skalą na symulatorze czujnika; brak „prawidłowych 5,1 V” dla rzeczywistych 6 V.

### R13 — P2: przerwa kierunku jest liczona sprzed operacji I²C

Źródło: [board_drive](C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/EGRLab-v3/firmware/main/board.c:99).

Kod zapisuje `now` przed oczekiwaniem na mutex i zapisem ekspandera, a po sukcesie ustawia `reverse_until = now + 5000`. Komentarz obiecuje pełne 5 ms od potwierdzenia. Gdy uzyskanie dostępu i zapis zajmą łącznie ponad 5 ms, przy następnej iteracji nie ma już wymaganej przerwy od rzeczywistego ustawienia INA/INB.

Nie oznacza to automatycznie zwarcia mostka; jego własne zabezpieczenia nadal istnieją. Oznacza brak gwarancji sekwencji, na której opiera się projekt, zwłaszcza z przekaźnikiem zasilania.

**Poprawka:** rozdzielić wyłączenie, ewentualny czas zaniku prądu, potwierdzoną zmianę kierunku i czas przed zezwoleniem; znacznik czasu pobierać we właściwym punkcie. Doprecyzować, czy 5 ms jest wymagane przed zmianą kierunku, po niej, czy w obu etapach — tekst procedury i kod nie są dziś identyczne.

**Odbiór:** sztucznie opóźniony zapis I²C oraz pomiar PWM, EN, INA/INB i VMOTOR przy zmianie znaku.

## Co potwierdzam jako zasadne

- **Oddzielny KCUR** naprawia rzeczywistą sprzeczność przekaźników.
- **SAFE_N z wyjściami otwartymi i jednym pull-upem przez STOP** to właściwa poprawka poprzedniego zwarcia/obejścia. Trzeba jeszcze usunąć R01 i R02.
- **Przywrócenie OVP oraz nadzoru 5V_A** jest zasadne. Szyna 5V_A wpływa na tor prądu i jego progi; niezależne odniesienie okna ma uzasadnienie. [Instrukcja TI LM74800EVM-CD](https://www.ti.com/lit/ug/slvubu3a/slvubu3a.pdf) podaje fabryczny próg OVP 37,5 V, więc wymagane w v3 przestawienie i pomiar 17,5–18,5 V są rzeczywiście konieczne; samo zakupienie EVM nie realizuje tej nastawy.
- **Powrót bufora 8 MiB** ma sens przy 16 MiB PSRAM: 262144 rekordy po 32 B, około 131 s przy 2 kS/s. To bufor opóźnień zapisu, nie gwarancja 131 s historii po utracie zasilania.
- **Identyfikator konfiguracji w każdej próbce** jest właściwą architekturą, pod warunkiem poprawienia całego procesu R03–R07.
- **AUX z DPDT i oddzielną kalibracją** oraz **L2 przed rozpięciem CUD87** zachowują wartość diagnostyczną.
- **Brak automatycznego poszukiwania krańców przez długie przeciążanie** i ręczne potwierdzenie LEARN są rozsądne dla nieznanego egzemplarza.

Sprawdziłem stałe interfejsu ADC w [AD7606B Rev. B](https://www.analog.com/media/en/technical-documentation/data-sheets/AD7606B.pdf): prefiks odczytu 0x4000, sześciobitowy adres, CONFIG=0 dla jednej linii DOUT, adresy zakresów 0x03–0x06, kody 0/1/2 oraz OS=3 dla ×8 są zgodne. Zapis 0x00 opuszcza tryb rejestrów. Pojedynczy zapis z trybu danych jest dopuszczony; nie zarzucam więc v3 błędu tylko dlatego, że pierwsza operacja konfiguracji jest zapisem. Ta weryfikacja nie zastępuje próby SPI z ośmioma różnymi napięciami.

## Przydatność do P0404 zależnego od temperatury i szarpania 1500–1700 rpm

Kierunek diagnostyczny pozostaje dobry: jednoczesny pomiar zasilania, masy i feedbacku, odniesienie do temperatury, możliwość L2 oraz prąd w L1/TEST pozwalają rozdzielać hipotezy. V3 nadal wymaga następujących doprecyzowań:

1. **Prąd zerwania:** firmware zapisuje bieżącą próbkę prądu przy wykryciu ruchu. Przy PWM 1 kHz i próbkowaniu 2 kS/s nie jest to pewna średnia ani RMS. Dopisane zastrzeżenie jest trafne, ale wiarygodny wykres trendu wymaga zdefiniowanego pomiaru prądu w oknie, synchronizacji z PWM lub sprawdzonego uśredniania. Osobno porównywać ten sam kierunek, napięcie i temperaturę.
2. **HOT-SOAK:** tabela w procedurze nadal mówi o „oczyszczonym zaworze” oraz zakresie 100–40°C, choć niżej poprawnie temu zaprzeczono i domyślny limit wynosi 60°C. Zastąpić stare wiersze, nie dopisywać tylko zastrzeżenia. Ujemny wynik zmniejsza podejrzenie wyłącznie w zbadanych warunkach; nie odtwarza obciążenia spalinami.
3. **RPM/OBD:** kod biernie rozpoznaje odpowiedź PID 0C, kiedy jakiś inny tester o nią pyta. Sam listen-only jej nie wywoła. Bez znanego identyfikatora fabrycznego RPM lub drugiego testera nie ma automatycznej korelacji z pasmem 1500–1700 rpm. Ta zależność powinna być w procedurze sesji.
4. **Masa odniesienia:** dokument deklaruje jedyne połączenie z B−, a jednocześnie przewiduje OBD pin 4 jako masę. Przy nieizolowanym CAN i wspólnej masie jest to kolejna droga do masy samochodu. Trzeba jednoznacznie narysować powroty i sprawdzić ich wpływ na pomiar dziesiątek mV; nie zakładać, że sama nazwa GND_STAR usuwa pętlę.
5. **Interpretacja triggerów:** `stall` jest kandydatem na problem, bo prąd przy nieruchomej pozycji może występować przy normalnym utrzymywaniu zaworu. Ten komentarz w v3 jest prawidłowy. Sygnał pozycji pozostaje pomiarem czujnika, nie niezależną obserwacją mechaniki.
6. **Wielogodzinny zapis:** CRC zabezpiecza wykrywanie uszkodzonych bloków, ale nie zastępuje synchronizacji metadanych ani gwarancji zachowania ogona pliku po zaniku zasilania. Rozmiar bloków zależy od aktualnego zapełnienia bufora; czas do 4 GiB policzony dla pełnych bloków 64 rekordów jest wartością optymistyczną, nie gwarantowanym czasem sesji. Przetestować rzeczywistą szybkość wzrostu pliku i rozważyć rotację.

Nie znalazłem powodu do zmiany ESP32-S3. Pozostawiłbym też AD7606B i osobne adaptery. Największy wzrost użyteczności zapewni teraz dopracowanie toru pomiar → konfiguracja → plik → wykres, zamiast dokładania następnych trybów.

## Kolejność poprawek i warunki następnego odbioru

1. **Schemat bezpieczeństwa:** R01–R02 i kompletny BOM/schemat R11. Test na stole bez mostka i bez zaworu, z rzeczywistymi stykami oraz przerwami przewodów.
2. **Pomiary i konfiguracje:** R03–R07, R12. Jeden właściciel przełączeń, potwierdzenie zatrzymania, jawna nieważność danych i poprawne zero.
3. **Zapis i analiza:** R08, R10. Próby wykorzystujące wyjście rzeczywistego serializera C, a nie tylko ręcznie utworzony JSON Pythona.
4. **Sterowanie i UI:** R09, R13; pełna kompilacja ESP-IDF 5.4.x dla konfiguracji LOGGER, TEST bez Wi-Fi i TEST z Wi-Fi.
5. **Integracja stanowiskowa:** osiem różnych napięć, oba znaki prądu, wymuszone błędy SPI/I²C, powtarzane zmiany trybów, odłączenia czujników i zasilania, minimum 30 minut jednoczesnego ADC/SD/CAN/TC.
6. **Dopiero potem zawór i auto:** kontrolowane impulsy na stole, kwalifikacja profilu, L2 bez zmiany złącza, potem L1 z porównaniem bypass/shunt, następnie procedury termiczne w potwierdzonych granicach.

**Ocena końcowa:** zachowałbym architekturę v3 i wprowadził następną rewizję naprawczą. Nie wracałbym do v1/v2. Nie zdejmowałbym jeszcze blokady `EGR_HARDWARE_ACCEPTED`: 107 poprawnych asercji logiki sterowania potwierdza część projektu, ale nie usuwa wykazanych błędów sprzętu i integracji.

