# Firmware i format danych

Projekt źródłowy dla ESP-IDF 5.4.x i ESP32-S3. **Nie został skompilowany ani uruchomiony na urządzeniu** — w środowisku, w którym powstał, nie ma toolchainu ani sprzętu. Testy plików logów są wykonane i przechodzą; testy C i pomiary czasu wykonania pozostają do uruchomienia.

## Moduły

| Plik | Odpowiedzialność |
|---|---|
| `control.c` | czysta logika: stany, mapowanie pinów, regulator, procedury, limity, kampania HOT-SOAK. Bez ESP-IDF, testowalna na PC |
| `board.c` | GPIO, ekspander, ADC (software/hardware mode), SD, MAX31856, pasywny TWAI, PWM, SCOPE_TRIG |
| `trigger.c` | detektory zdarzeń i podsumowania 1 Hz |
| `storage.c` | bufor zapisu, bloki z CRC, zdarzenia NDJSON |
| `webui.c` | opcjonalny SoftAP i strona na telefon |
| `app_main.c` | zadania FreeRTOS, konsola, profil w NVS, orkiestracja |
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

LOGGER nigdy nie włącza własnego napędu. TEST wymaga: zapisanego mapowania pinów, zatwierdzonego sprzętu, wpiętego adaptera TEST przy **niewpiętym** LOGGER, zamkniętego interlock, poprawnych napięć, świeżych danych ADC i sprawnego zapisu. Ruch dodatkowo wymaga fizycznego ARM i poprawnej TC1. Zanik dowolnego warunku przerywa próbę i zdejmuje zasilanie czujnika.

HOT-SOAK nie jest osobnym stanem — to warstwa kampanii, która z poziomu READY wydaje **te same rozkazy, które mógłbyś wydać ręcznie**. Odrzucony rozkaz albo dowolny FAULT natychmiast kasuje kampanię. Dzięki temu nie ma drugiej, równoległej ścieżki sterowania napędem.

Zadania: `adc` na rdzeniu 1, priorytet 23; `safety` na rdzeniu 0, priorytet 20, co 1 ms; `writer` priorytet 8; `aux` (CAN, termopary, podsumowania) priorytet 5; `console` priorytet 3. Timer powiadamia zadanie akwizycji, które startuje konwersję i czyta SPI. **Znacznik czasu oznacza rzeczywisty start konwersji, nie idealną pozycję na siatce.** Nadmiar powiadomień to utracone terminy — ustawia GAP, blokuje TEST i liczy się w `lost_ticks`.

Wi-Fi jest wyłączone zawsze, gdy stan to LOGGER albo IDENTIFY, i gdy nie ma wpiętego adaptera TEST.

## Konsola

| Komenda | Działanie |
|---|---|
| `status` | stan, mapowanie kanałów, napięcia, prąd, ratio, pozycja, AUX, temperatury, adapter, ARM, utracone terminy, liczba triggerów, tryb ADC |
| `bind <zawór> <adapter>` | w SAFE wiąże profil z fizycznym egzemplarzem; zmiana unieważnia mapowanie pinów i LEARN |
| `logger` | bank LOGGER, napęd i zasilanie czujnika OFF |
| `identify` | 2 s stabilnego pomiaru, sześć permutacji, timeout 30 s |
| `aux 0` / `aux 1` | zgłasza pozycję zworki JP_AUX: 0 = HI ±40 V, 1 = LO ±2,5 V; ustawia zakres ADC i nominalne wzmocnienie kanału AUX |
| `zero` | zapisuje **zmierzone** zero toru prądowego aktywnego banku z ostatniego podsumowania 1 Hz |
| `test` | bank TEST, sprawdzenie własnego zasilania czujnika |
| `learn <rc> <ro> <znak>` | zapisuje zweryfikowane pomiarowo punkty pozycji |
| `manual <duty> <ms>` | jeden impuls, np. `manual 0.05 50`; maks. 250 ms |
| `goto <p>` | dojście do pozycji 0,1…0,9 |
| `sweep` | 10…90…10 % |
| `friction 1` / `friction -1` | jedna rampa oporów ruchu od bieżącej pozycji |
| `cycle <n>` | n cykli 10–90–10 %, maks. 200 |
| `thermal` | SWEEP przy nadzorowanej TC1 |
| `hotsoak <okres_s> <serie>` | kampania na stygnącym silniku, np. `hotsoak 180 12` |
| `hotsoak_stop` | przerywa kampanię, nie przerywa trwającego ruchu |
| `mark` | znacznik w logu |
| `stop` | natychmiast ARM = 0, czujnik OFF, SAFE |
| `save` | w SAFE zapis profilu do NVS; akwizycja wstrzymana na czas operacji Flash |

Pierwsza sesja: `bind` → `logger` → `identify` → `status` → `stop` → `save`. Przy kolejnej sesji profil wczytuje się sam, ale **dopasowanie profilu do fizycznego zaworu pozostaje Twoją odpowiedzialnością** — zawór nie ma numeru seryjnego czytanego elektronicznie.

## Triggery

Liczone z każdej próbki w zadaniu akwizycji. Każdy typ ma zatrzask i ponowne uzbrojenie po 250 ms, żeby jedna długa anomalia nie wygenerowała tysiąca linii na sekundę.

| Nazwa | Warunek | Co oznacza |
|---|---|---|
| `ref` | referencja poza 4,5–5,5 V | H4 — zapad zasilania czujnika |
| `ground` | \|masa czujnika\| > 0,30 V względem B− | H2 — rezystancyjna masa; ten sam próg co Krok 2 procedury v3 |
| `feedback` | sygnał poza 0,2–4,8 V | H3 — przerwa albo zwarcie w torze sygnału |
| `jump` | skok ratio > 5 % **między kolejnymi próbkami** (0,5 ms przy 2 kS/s) | glitch w torze pozycji |
| `stall` | \|I\| > 0,3 A i pozycja nie drgnęła przez 200 ms | H5 — zacięcie albo kłamiący sygnał pozycji |
| `open` | \|U(pin1) − U(pin3)\| > 2 V przy \|I\| < 0,1 A przez 50 ms | przerwa w torze napędu |

v1 miał w dokumentacji próg „skok r > 5 % w 1 ms", którego przy 2 kS/s nie dało się sensownie zrealizować. Tutaj kryterium jest wyrażone w próbkach, nie w milisekundach.

Każdy trigger ustawia bit `SAMPLE_TRIGGER` w rekordzie, dopisuje linię do NDJSON z wartościami w chwili zdarzenia **i wystawia impuls 20 µs na SCOPE_TRIG**.

## Podsumowania 1 Hz

Raz na sekundę do NDJSON idzie `{"type":"summary", "ch":[[min,mean,max], ...]}` dla ośmiu kanałów plus licznik triggerów. To jest to, co zamienia 18-godzinny plik w coś, co da się przejrzeć: `egrlog.py scan` czyta wyłącznie NDJSON i w sekundę pokazuje, gdzie w sesji coś się działo.

## Format EGRLOG1 wersja 2

Little-endian. Nagłówek 32 B:

| Offset | Typ | Znaczenie |
|---:|---|---|
| 0 | char[8] | `EGRLOG1` + bajt 0 |
| 8 | u16 | **wersja 2** |
| 10 | u16 | długość nagłówka 32 |
| 12 | u32 | nominalna częstotliwość próbkowania |
| 16 | u32 | długość rekordu 32 |
| 20 | u32 | flagi; bit 0 = dane syntetyczne |
| 24 | u64 | identyfikator sesji |

Blok: `BLK1`, `count:u32`, `payload_bytes:u32`, `crc32:u32`, potem `count` rekordów. Count 1…256, firmware używa 64. CRC32 IEEE obejmuje cały payload. Urwany ostatni blok odrzuca tryb recovery; **nie dopisujemy zer i nie przechodzimy po cichu przez błędne CRC**.

Rekord: `t_us:u64`, `sequence:u32`, `raw[8]:i16`, `flags:u16`, `reserved:u16`.

Flagi: bit 0 GAP, 1 bank TEST, 2 zasilanie czujnika, 3 zezwolenie napędu, 4 MARK, 5 trigger. Firmware ustawia 0, 1, 2, 3 i 5; MARK jest autorytatywnie w NDJSON.

**Co się zmieniło względem wersji 1:** znaczenie kanałów 6, 7 i 8. Było: prąd TEST, prąd LOGGER, VPROT. Jest: prąd aktywnego banku, VBAT, AUX. Układ rekordu jest identyczny, więc stare pliki dalej się czytają — czytnik rozpoznaje wersję z nagłówka i nadaje kolumnom właściwe nazwy.

Dodatkowo `meta.json` ma teraz `full_scale[8]` (zakres każdego kanału: 2,5 / 5 / 10 V) oraz `ch_supply`, `ch_ground`, `ch_feedback`. Przelicznik to `V = code × full_scale / 32768 × gain + offset`. Pliki bez `full_scale` czytają się jak ±10 V na wszystkich kanałach, czyli tak jak v1.

`sequence` liczy dostarczone próbki. Utracone wyzwolenia timera **nie dostają fikcyjnych próbek** — ujawniają je `lost_ticks` i flaga GAP. Rzeczywiste odstępy wyznaczaj z `t_us`. Znacznik czasu ramki CAN to czas odbioru w zadaniu, nie sprzętowy znacznik początku ramki. Temperatury mają własny czas odczytu, wartość albo `null` i kod błędu — nie udają wspólnego próbkowania z ADC.

Sesja: `session_<n>/samples.egr`, `events.ndjson`, `meta.json`. Istniejący katalog nigdy nie jest nadpisywany.

## Pamięć i przepustowość

Bufor zapisu to 1 MiB w PSRAM (32 768 rekordów, ok. 16 s przy 2 kS/s). **Nie ma ringu z pretriggerem ani zrzutu wokół MARK** — przy 2 kS/s ciągły plik mieści 18,6 h do limitu 4 GiB FAT32, więc historia i tak jest w pliku. Jeśli writer nie nadąży, bufor zgłasza stan błędu, co przerywa TEST; przy 2 kS/s (64 kB/s) zapas jest duży.

Przy 20 kS/s to samo oznacza 640 kB/s i limit 4 GiB po około 1 h 52 min. Prototyp nie ma rotacji plików — zatrzymaj sesję wcześniej. **To nie jest bezobsługowy rejestrator wielodniowy** ani zapis odporny na dowolny zanik zasilania.

## Sterownik ADC

W software mode konfiguracja rejestrów jest **weryfikowana odczytem**; niezgodność loguje `adc_mode` i przełącza na hardware mode z zakresem ±10 V na wszystkich kanałach. Adresy rejestrów są zebrane w jednym `enum` w `board.c` z komentarzem — **zweryfikuj je z datasheetem swojej rewizji**. Odczyt: jedna transakcja 128-bit (software) albo osiem ramek 16-bit z CS między nimi (hardware). Pomylenie tych dwóch schematów daje powtarzające się kanały — dlatego etap 5 odbioru każe podać **osiem różnych napięć**.

## Odczyt na komputerze

```text
python tools/egrlog.py inspect examples/synthetic.egr
python tools/egrlog.py scan   examples/events.ndjson
python tools/egrlog.py export examples/synthetic.egr --meta examples/synthetic.json --csv out.csv
python tools/egrlog.py report examples/synthetic.egr --meta examples/synthetic.json --html out.html
python -m unittest discover -s tests -p "test_*.py" -v
```

`scan` czyta sam NDJSON i wypisuje triggery, znaczniki, punkty HOT-SOAK i przebieg sekundowych ekstremów. `report` generuje samodzielną stronę z wykresami (Chart.js z CDN) — ten sam sposób pracy, którego używałeś przy logach XML. `export` zachowuje kody surowe, napięcia, prąd, różnicę napięć uzwojenia, ratio i pozycję; nieprawidłowe mapowanie albo referencja dają pustą wartość, a **nie fałszywe 0 %**.

Python korzysta wyłącznie z biblioteki standardowej. Dane w `examples/` są oznaczone jako syntetyczne i nie pochodzą z auta.

## Czego firmware nie obejmuje

Graficznego GUI poza prostą stroną SoftAP, RTC, OTA, aktywnego OBD/UDS i ISO-TP, regulacji grzałki, rotacji plików FAT ani produkcyjnego odzyskiwania systemu plików. OLED i RTC pozostają opcjami sprzętowymi bez sterowników. Częstotliwości powyżej ok. 5 kS/s wymagają timera sprzętowego z przerwaniem zamiast `esp_timer` z dyspozycją w zadaniu — **nie jest to zadeklarowane**.
