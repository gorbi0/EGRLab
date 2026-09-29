# Firmware i dane

ESP-IDF 5.4.3 / ESP32-S3, Flash 32 MB OPI, PSRAM 16 MiB OCT. Użyto istniejącego, kompilowanego firmware v4.1 i rozszerzono jego sterownik, konfigurację i log. Stan testów tej rewizji opisuje `verification/README.md`.

| Wariant | Zastosowanie |
|---|---|
| core | CORE + SD, bez akwizycji i wykonawczych PCB |
| minimal | LOGGER napięciowy, bez TEMP/CAN/prądu |
| logger | DAQ + I-LOGGER + TEMP + CAN, aktywny TEST wyłączony |
| test | DAQ + DRIVE/SENSOR/SAFE + TEMP, prąd lokalny; CAN opcjonalny |
| wifi | Jak TEST, z dotychczasowym interfejsem Wi-Fi |

W terminalu ESP-IDF, katalog firmware, przykład:

```text
idf.py -B build-test -DIDF_TARGET=esp32s3 -DSDKCONFIG=sdkconfig.test "-DSDKCONFIG_DEFAULTS=sdkconfig.defaults;sdkconfig.test.defaults" build
```

Zmień `test` na nazwę wariantu. Kolejne warianty muszą mieć osobne sdkconfig i katalog build. Wszystkie wydane źródła mają `EGR_HARDWARE_ACCEPTED=0`. Kompilacja TEST nie uzbraja sprzętu. Hasło Wi-Fi zmień przed użyciem.

## Organizacja

`board.c`: peryferia, MCP, AD7606B, MCP3201, GPIO, zatrzymanie napędu. `control.c`: SAFE/LOGGER/IDENTIFY/SENSOR_CHECK/READY/MANUAL/GOTO/SWEEP/FRICTION/CYCLE/THERMAL/FAULT. `profile.c`: transakcyjne zmiany kalibracji i limitów. `app_main.c`: pojedynczy właściciel akwizycji, kolejka rozkazów i potwierdzany protokół pauzy. `measure.c`: okno prądu. `trigger.c`: kryteria zdarzeń i statystyki. `storage.c`: zapis PSRAM→SD, CRC, konfiguracje przed publikacją config_id. `jsonlog.c`: jawna serializacja null przy nieważnych liczbach.

Zatrzymanie akwizycji wymaga ACK jej zadania. Dopiero potem przełącza się bank, zakresy, zasilanie sensora i zapisuje migawkę. Nowe config_id trafia do próbek dopiero po fsync konfiguracji. Błąd zapisu nie jest pomijany. STOP ma osobny mechanizm unieważniania oczekujących poleceń ruchu.

GPIO38 zmieniono z triggera na CS prądu; trigger oscyloskopu jest na GPIO41. MARK przechodzi przez GPB6, odczyt co około 20 ms. MARK służy znacznikowi objawu i ma taką niepewność czasu; nie zastępuje triggera sprzętowego. GPA4 otrzymuje gotowość prądu LOGGER; GPB7 pozostaje wyjściem niepodłączonym.

## Lokalny pomiar prądu

MCP3201 mode 0 / 500 kHz / 16 bitów transferu. Dekodowanie `(word >> 1) & 0x0fff`; bit zerowy NULL ramki (bit13 słowa) jest sprawdzany. Brak gotowości, timeout/SPI, nasycenie i przekroczony przedział czasu mają różne statusy. Sam SPI nie ma CRC ani identyfikatora układu; stały pozornie poprawny kod nie jest pełnym testem ADC. Weryfikuje się go wymuszeniami podczas odbioru.

W programie funkcjonalny `v[5]` jest odtworzonym napięciem wyjścia INA z lokalnego ADC. `sample.raw[5]` pozostaje rzeczywistym szóstym kanałem AD7606B. Rozróżnienie jest celowe: nie fałszujemy danych raw przez podmianę kodu z innego przetwornika.

Prąd = `(local_raw * current_adc_gain + current_adc_offset - current_zero) / current_volts_per_amp`. Wszystkie współczynniki należą do wskazanego modułu/banku i są zapisane w config. Przy zmianie modułu lub skali usuwa się akceptację i kwalifikację. Wynik lokalny nie wymaga sprawnego analogowego przewodu do DAQ.

## Format 5

Nagłówek 32 B `<8sHHIIIQ>`: magic `EGRLOG1\0`, wersja 5, rozmiar nagłówka 32, częstotliwość, **rekord 40**, flags, session. Bloki `BLK1`: liczba rekordów, bajty, CRC32 payload. W każdym rekordzie `<QI8h6H>`:

| Pole | Typ / rozmiar |
|---|---|
| t_us | uint64, czas przed zboczem CONVST AD7606B |
| sequence | uint32 |
| raw[8] | int16 ×8, AD7606B |
| current_raw | uint16, 0–4095; 65535 oznacza brak konwersji |
| current_begin_us / current_end_us | uint16 ×2; przedział wywołania SPI względem t_us |
| current_status | uint16: 1 OK, 2 ABSENT, 4 BUS_ERROR, 8 SATURATED, 16 TIMING |
| flags | uint16; dotychczasowe GAP/TEST/SENSOR/PERMIT/MARK/TRIGGER/SATURATED/INVALID |
| config_id | uint16 |

Nie wyznaczaj czasu konwersji MCP z chwili odbioru całego rekordu. Próbka jest pobierana wewnątrz zapisanego przedziału; odbiór oscyloskopowy może go później zawęzić. Kod metryki 20 ms używa środka przedziału jako przybliżenia. Nie kompensuje automatycznie opóźnień filtrów ani OS x8 AD.

NDJSON: config, temperatury, CAN, RPM z obserwowanej odpowiedzi, MARK, trigger, state, config_gap, summary, hotsoak_point i błędy. Config obejmuje DAQ/current module ID, zawór/adapter, pojazd/test, aktualną skalę i kalibrację. Moduły/kalibracje niewymienione w rekordzie config dokumentuje towarzyszący plik manifestu — opis w rozdziale 05.

Bufor próbek 8 MiB = 209715 rekordów, około **104,86 s przy 2 kS/s**. FIFO zdarzeń 256 KiB o zmiennej długości; konfiguracja ma osobną kolejkę i limit linii 2048 B. Zapis jest ciągły: pretrigger uzyskuje się z historii przed zdarzeniem. PSRAM chroni przed chwilowym opóźnieniem SD, nie przed utratą zasilania. Końcowy niezapisany fragment może zginąć. Segmenty próbek i zdarzeń do 1 GiB, synchronizacja cykliczna około 2 s. Sam strumień próbek około 288 MB/h plus nagłówki i zdarzenia; CAN może znacząco zwiększyć objętość.

Czytnik `tools/egrlog.py` obsługuje formaty 1–5. Rozmiar rekordu wynika z wersji nagłówka; nie jest zgadywany po długości pliku. CSV v5 dodaje current_raw/start/end/status i zachowuje osiem raw AD. Raport HTML pokazuje przeliczony prąd. Gdy kalibracja napięć nie jest zaakceptowana, fizyczne napięcia są puste; raw pozostaje. Gdy current_valid/akceptacja/status nie pozwalają na prąd, kolumna A jest pusta.

```text
python tools/egrlog.py inspect logs/session_1
python tools/egrlog.py export logs/session_1 --csv wynik.csv
python tools/egrlog.py report logs/session_1 --html raport.html
python tools/egrlog.py scan logs/session_1
```

Pliki z `examples/` są syntetyczne. Raport nie stwierdza automatycznie przyczyny P0404. Metryka RMS z 2 kS/s jest RMS próbek i wymaga osobnego porównania z oscyloskopem; nie deklaruje pomiaru wszystkich tętnień PWM.

## Uzupełnienie V6

Na pierwszy start AD SPI=1 MHz (`CONFIG_EGR_ADC_SPI_HZ`), SD=4 MHz (`CONFIG_EGR_SD_KHZ`), lokalny prąd=500 kHz. Zapis 2 kS/s to 80 kB/s samych próbek; odebrać ciągły zapis wraz ze zdarzeniami i CAN. Nie usuwać limitów 500 µs okresu / 400 µs odczytu prądu, aby ukryć zbyt wolny transfer.

Po zmianie trybu/banku lub zatwierdzeniu konfiguracji akwizycja zatrzymuje się, a watchdog może rozbroić latch. Poczekać na poprawne świeże próbki i ponownie nacisnąć **fizyczny ARM**, także gdy poprzednie polecenie `zero` wymusiło taki cykl. W razie REJECTED sprawdzić HW_ARMED, gotowość i kalibrację; nie obchodzić zatrzasku. Kierunek: mostek wyłączony → potwierdzony INA/INB → 5 ms → ponowne zezwolenie.

Profile JSON/NVS mają wersję 6; zmiana nominałów wymaga nowych pomiarów i identyfikatorów modułów. Format próbek pozostaje wersją 5 (40 B), a schemat zdarzenia config/metadanych pozostaje 5. Numer rewizji urządzenia nie jest numerem formatu logu.
