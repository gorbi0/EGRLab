# Firmware i format danych

Projekt źródłowy dla ESP-IDF 5.4.x i ESP32-S3. **Nie został skompilowany ani uruchomiony na urządzeniu** — w środowisku, w którym powstał, nie ma toolchainu ani sprzętu. Testy plików logów i kontrola składni źródeł C są wykonane i przechodzą; testy logiki w C oraz pomiary czasu wykonania pozostają do uruchomienia.

## Moduły

| Plik | Odpowiedzialność |
|---|---|
| `control.c` | czysta logika: stany, mapowanie pinów, regulator, procedury, limity, kampania HOT-SOAK, budowa migawki konfiguracji. Bez ESP-IDF, testowalna na PC |
| `board.c` | GPIO, ekspander, ADC (tryb wybierany przy kompilacji), SD, MAX31856, pasywny TWAI, PWM, SCOPE_TRIG |
| `trigger.c` | detektory zdarzeń i podsumowania 1 Hz |
| `storage.c` | bufor zapisu, bloki z CRC, zdarzenia NDJSON, zdarzenia `config` |
| `webui.c` | opcjonalny SoftAP i strona na telefon |
| `app_main.c` | zadania FreeRTOS, dispatcher poleceń, publikacja konfiguracji, konsola, profil w NVS |
| `commissioning.h` | jawna blokada przed odbiorem sprzętu |

`board_kill()` natychmiast zeruje MCU_ARM i PWM. Wyłączenie obu EN i przekaźnika mocy robi sprzęt. Do zdjęcia MCU_ARM nie jest potrzebna żadna operacja I²C ani SD. Zanik programu wykrywa zewnętrzny monostabilny, a przeciążenie — niezależny komparator.

## Stany

```text
BOOT → SAFE → LOGGER → IDENTIFY → LOGGER
          └→ SENSOR_CHECK → READY → MANUAL / GOTO / SWEEP / FRICTION / CYCLE / THERMAL
                               ↑                         │ sukces
                               └─────────────────────────┘
FAULT ← dowolny błąd; FAULT → SAFE wyłącznie świadomym STOP
```

LOGGER nigdy nie włącza własnego napędu. TEST wymaga: zapisanego mapowania pinów, zatwierdzonego sprzętu, **potwierdzonej konfiguracji przetwornika**, wpiętego adaptera TEST przy niewpiętym LOGGER, zamkniętego interlock, poprawnych napięć, świeżych danych ADC i sprawnego zapisu. Ruch dodatkowo wymaga fizycznego ARM, poprawnej TC1 i **potwierdzonego zapisu kierunku** do ekspandera. Zanik dowolnego warunku przerywa próbę i zdejmuje zasilanie czujnika.

Nowe w v3 powody przerwania: `ADC_CONFIG` (przetwornik nie potwierdził konfiguracji — skala napięć jest nieznana) i `DRIVE_IO` (zapis kierunku przez I²C się nie powiódł).

HOT-SOAK nie jest osobnym stanem — to warstwa kampanii, która z poziomu READY wydaje **te same rozkazy, które mógłbyś wydać ręcznie**. Odrzucony rozkaz albo dowolny FAULT natychmiast ją kasuje.

## Zadania i własność zasobów

| Zadanie | Rdzeń / priorytet | Co robi |
|---|---|---|
| `adc` | 1 / 23 | jedna konwersja na powiadomienie timera, przeliczenie, detektory, zapis do bufora |
| `safety` | 0 / 20 | co 1 ms: `control_step`, sterowanie napędem, heartbeat, polityka radia co 200 ms |
| `writer` | 0 / 8 | bloki z CRC na kartę, kolejka zdarzeń |
| `config` | 0 / 6 | **jedyny właściciel konfiguracji przetwornika** |
| `aux` | 0 / 5 | CAN, termopary, podsumowania sekundowe |
| `console` | 0 / 3 | parsowanie linii, dispatcher |

**Zmiana konfiguracji przetwornika ma dokładnie jednego właściciela.** Zadanie `config` zatrzymuje timer próbkowania, zgłasza `board_adc_set_running(false)`, czeka 20 ms na wygaszenie akwizycji, ustawia i weryfikuje zakresy, buduje nową migawkę w nieaktywnym buforze, przestawia indeks, konfiguruje detektory i dopiero wtedy wznawia próbkowanie. `board_adc_ranges()` **odmawia**, dopóki akwizycja jest zgłoszona jako pracująca. W v2 zmiana zakresów szła z zadania bezpieczeństwa równolegle z odczytem na drugim rdzeniu.

Skutek uboczny, o którym trzeba wiedzieć: przez czas zmiany konfiguracji (rzędu 20–70 ms) zadanie bezpieczeństwa nie dostaje mutexu, więc **heartbeat nie jest odświeżany**. Zadanie w tym czasie zeruje napęd, czyli jest bezpiecznie, ale jeśli ustawisz monostabilny na dolnym końcu zakresu (50 ms), latch może się rozbroić i trzeba będzie nacisnąć ARM ponownie. Dobierz stałą czasową bliżej **100–150 ms** i pamiętaj, że po `zero`, `aux`, `bypass` czy `learn` uzbrojenie może wymagać powtórzenia. Zmiany konfiguracji robi się i tak przy nieruszającym się zaworze.

Znacznik czasu oznacza rzeczywisty start konwersji, nie idealną pozycję na siatce. Nadmiar powiadomień to utracone terminy — ustawia GAP, blokuje TEST i liczy się w `lost_ticks`.

Wi-Fi jest wyłączone zawsze, gdy stan to LOGGER albo IDENTIFY, gdy nie ma wpiętego adaptera TEST i gdy urządzenie jest w FAULT.

## Jedna ścieżka poleceń

Konsola i strona WWW przechodzą przez **ten sam dispatcher**. Zmiana wyjść (bank pomiarowy, zasilanie czujnika, zezwolenie napędu) dzieje się w jednym miejscu, więc `stop` z telefonu robi dokładnie to samo co `stop` z konsoli — v2 miała tu dwie ścieżki i webowy STOP nie odcinał czujnika. Strona ma białą listę poleceń: bez `learn`, `save`, `bind`, `zero`, `aux` i `bypass`.

| Komenda | Działanie |
|---|---|
| `status` | stan, `config_id`, mapowanie, bank, napięcia, prąd z flagą ważności, ratio, pozycja, AUX z pozycją zworki, temperatury, adapter, ARM, tryb i stan ADC, liczniki strat |
| `bind <zawór> <adapter>` | w SAFE wiąże profil z egzemplarzem; zmiana unieważnia mapowanie i LEARN |
| `logger` | bank LOGGER, napęd i zasilanie czujnika OFF |
| `identify` | 2 s stabilnego pomiaru, sześć permutacji, timeout 30 s |
| `aux 0` / `aux 1` | zgłasza pozycję zworki JP_AUX (HI / LO); przestawia zakres i wybiera właściwą parę współczynników |
| `bypass 0` / `bypass 1` | ważność prądu aktywnego banku: `1` = mostek bocznikujący albo sondy back-probe, prąd nieznany |
| `zero` | zapisuje **zmierzone** zero toru prądowego aktywnego banku z ostatniego podsumowania 1 Hz |
| `test` | bank TEST, sprawdzenie własnego zasilania czujnika |
| `learn <rc> <ro> <znak>` | zapisuje zweryfikowane pomiarowo punkty pozycji |
| `manual <duty> <ms>` | jeden impuls, maks. 250 ms |
| `goto <p>` | dojście do pozycji 0,1…0,9 |
| `sweep` · `cycle <n>` · `thermal` | procedury z `02-procedury.md` |
| `friction 1` / `friction -1` | jedna rampa oporów ruchu |
| `hotsoak <okres_s> <serie>` · `hotsoak_stop` | kampania na stygnącym silniku |
| `mark` · `stop` · `save` | znacznik, zatrzymanie, zapis profilu do NVS |

Każde `aux`, `bypass`, `zero`, `learn`, `bind`, `test` i `logger` kończy się **publikacją nowej migawki konfiguracji**, więc zmiana jest widoczna w pliku od następnej próbki.

## Migawka konfiguracji i `config_id`

To jest najważniejsza zmiana v3. W v2 kalibracja szła do `meta.json` raz, na starcie, dla banku 0 — a potem IDENTIFY zmieniał zakresy, TEST zmieniał bank, `zero` i `aux` zmieniały współczynniki. Eksporter o tym nie wiedział, więc **20 mV na masie czujnika eksportowało się jako 80 mV** po przejściu kanału na ±2,5 V, a zerowy prąd banku TEST jako 0,4 A.

W v3 każda próbka niesie `config_id`, a migawka trafia do `events.ndjson`:

```json
{"type":"config","config_id":2,"bank":1,"ch_supply":2,"ch_ground":4,"ch_feedback":3,
 "full_scale":[10,10,5,5,2.5,5,10,10],"gain":[...],"offset":[...],
 "current_zero":2.553,"current_valid":false,"closed":0.15,"open":0.85,
 "opening_sign":1,"learned":true,"aux_position":"LO",
 "adc_software_mode":true,"adc_config_ok":true}
```

Eksporter dobiera konfigurację **per próbka**. Brak zdarzenia dla danego `config_id` daje ostrzeżenie i użycie konfiguracji zapasowej, a nie ciche przeliczenie czymkolwiek. Pola `full_scale` opisują zakres **faktycznie potwierdzony przez sprzęt**, nie żądany przez profil.

## Triggery

Liczone z każdej próbki w zadaniu akwizycji. Każdy typ ma zatrzask trzymający przez pełne 250 ms — **niezależnie od tego, czy warunek w międzyczasie ustąpił**, bo inaczej seria naprzemiennych glitchy obchodzi limit.

| Nazwa | Warunek | Co oznacza |
|---|---|---|
| `ref` | referencja poza 4,5–5,5 V | H4 — zapad zasilania czujnika |
| `ground` | \|masa czujnika\| > 0,30 V | H2 — ten sam próg co Krok 2 procedury v3 |
| `ground_warn` | \|masa czujnika\| > 0,05 V | próg ostrzegawczy — **dobierz po pomiarze szumu własnego toru** |
| `feedback` | sygnał poza 0,2–4,8 V | H3 — przerwa albo zwarcie w torze sygnału |
| `jump` | skok ratio > 5 % **w oknie 1 ms** | glitch w torze pozycji |
| `stall` | \|I\| > 0,3 A i pozycja stoi przez 200 ms | H5 — zacięcie albo kłamiący sygnał pozycji |
| `open` | \|U(pin1) − U(pin3)\| > 2 V przy \|I\| < 0,1 A przez 50 ms | przerwa w torze napędu |

Okno skoku jest wyrażone **w czasie, nie w sąsiednich próbkach**: przy 2 kS/s to dwie próbki, przy 20 kS/s dwadzieścia. `stall` i `open` **milczą, gdy prąd jest nieważny** (`bypass 1` albo sondy back-probe) — v2 zgłaszała przerwę w torze napędu na kanale bez informacji.

Dwie uwagi interpretacyjne. Próg 0,05 V na masie nie wynika z tego, że przetwornik ma 76 µV rozdzielczości — rozdzielczość to nie wykrywalność; ustaw go po zmierzeniu szumu w etapie 5 odbioru. A `stall` widzi to samo, co normalne utrzymywanie pozycji pod obciążeniem, więc sam w sobie nie jest objawem usterki.

Każdy trigger ustawia bit `SAMPLE_TRIGGER` w rekordzie, dopisuje linię do NDJSON z wartościami i `config_id` w chwili zdarzenia, **i wystawia impuls 20 µs na SCOPE_TRIG**.

## Podsumowania 1 Hz

Raz na sekundę do NDJSON idzie `{"type":"summary","config_id":N,"ch":[[min,mean,max], ...]}` dla ośmiu kanałów plus licznik triggerów. To zamienia wielogodzinny plik w coś, co da się przejrzeć: `egrlog.py scan` czyta sam NDJSON i pokazuje, gdzie w sesji coś się działo.

Bufor podsumowania jest **mniejszy niż limit zdarzenia**, a każde formatowanie sprawdza wynik. Gdy linia i tak by się nie zmieściła, do logu idzie `summary_dropped`, a zapis jest oznaczony jako niezdrowy. v2 składała 420 B w limit 254 B bez kontroli, więc czytnik dostawał uszkodzoną linię, a firmware raportował zdrowie.

## Format EGRLOG1 wersja 3

Little-endian. Nagłówek 32 B: `EGRLOG1`, wersja **3**, długość nagłówka 32, częstotliwość, długość rekordu 32, flagi (bit 0 = dane syntetyczne), identyfikator sesji.

Blok: `BLK1`, `count:u32`, `payload_bytes:u32`, `crc32:u32`, potem `count` rekordów. Count 1…256, firmware używa 64. CRC32 IEEE obejmuje cały payload. Urwany ostatni blok odrzuca tryb recovery; **nie dopisujemy zer i nie przechodzimy po cichu przez błędne CRC**.

Rekord: `t_us:u64`, `sequence:u32`, `raw[8]:i16`, `flags:u16`, **`config_id:u16`**.

Flagi: bit 0 GAP, 1 bank TEST, 2 zasilanie czujnika, 3 zezwolenie napędu, 4 MARK, 5 trigger.

**Zmiany względem wersji 2:** pole `reserved` stało się `config_id`. Układ rekordu i rozmiar są te same, więc pliki 1 i 2 czytają się dalej — czytnik rozpoznaje wersję z nagłówka, nadaje kolumnom właściwe nazwy i dla starszych plików bierze kalibrację z `meta.json` albo z `--meta`.

`meta.json` w v3 opisuje **tylko sesję** (schemat, firmware, częstotliwość, pojazd). Kalibracja, zakresy, bank i mapowanie żyją w zdarzeniach `config`, bo mogą się zmieniać w trakcie.

`sequence` liczy dostarczone próbki. Utracone wyzwolenia timera **nie dostają fikcyjnych próbek** — ujawniają je `lost_ticks` i flaga GAP. Rzeczywiste odstępy wyznaczaj z `t_us`. Znacznik czasu ramki CAN to czas odbioru w zadaniu, nie sprzętowy znacznik początku ramki. Temperatury mają własny czas odczytu, wartość albo `null` i kod błędu.

Sesja: `session_<n>/samples.egr`, `events.ndjson`, `meta.json`. Istniejący katalog nigdy nie jest nadpisywany.

## Pamięć i przepustowość

Bufor zapisu to **8 MiB w PSRAM** (262 144 rekordy, ok. 131 s przy 2 kS/s). To odporność na zadławienie karty, niezależna od formatu pliku; v2 ścięła go do 1 MiB (16 s) przy okazji usuwania pretriggera, choć to dwie osobne decyzje. Pretriggera nadal nie ma i nie jest potrzebny — historia jest w ciągłym pliku.

Przy 2 kS/s strumień to 64 kB/s próbek plus nagłówki bloków (16 B na 64 rekordy, ok. 0,8 %), czyli limit 4 GiB FAT32 wypada po **około 18,4 h**. Przy 20 kS/s to samo oznacza ok. 1 h 51 min. Prototyp nie ma rotacji plików — zatrzymaj sesję wcześniej. **To nie jest bezobsługowy rejestrator wielodniowy** ani zapis odporny na dowolny zanik zasilania.

## Odczyt na komputerze

```text
python tools/egrlog.py inspect examples/samples.egr
python tools/egrlog.py scan   examples/events.ndjson
python tools/egrlog.py export examples/samples.egr --csv out.csv
python tools/egrlog.py report examples/samples.egr --html out.html
python -m unittest discover -s tests -p "test_*.py" -v
```

`export` i `report` **nie wymagają już `--meta`**, jeśli plik ma zdarzenia `config`; opcja została jako konfiguracja zapasowa dla plików v1/v2. `scan` wypisuje listę konfiguracji, triggery, znaczniki, punkty HOT-SOAK, sekundowe ekstrema oraz osobną listę problemów (`adc_error`, `adc_config_error`, `summary_dropped`, `can_drop`) — i ostrzega, gdy któraś konfiguracja miała `adc_config_ok: false`.

Prąd bez ważnej informacji eksportuje się jako **pusta komórka**, nie zero. Nieprawidłowe mapowanie albo referencja poza zakresem dają puste ratio i pozycję, a nie fałszywe 0 %.

Python korzysta wyłącznie z biblioteki standardowej. Dane w `examples/` są oznaczone jako syntetyczne i nie pochodzą z auta.

## Czego firmware nie obejmuje

Graficznego GUI poza prostą stroną SoftAP, RTC, OTA, aktywnego OBD/UDS i ISO-TP, regulacji grzałki, rotacji plików FAT ani produkcyjnego odzyskiwania systemu plików. Częstotliwości powyżej ok. 5 kS/s wymagają timera sprzętowego z przerwaniem zamiast `esp_timer` z dyspozycją w zadaniu — **nie jest to zadeklarowane**.
