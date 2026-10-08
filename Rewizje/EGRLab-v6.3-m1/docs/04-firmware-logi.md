# Firmware i dane

> **6.3-m1 (płytka M1-R1):** obowiązuje sekcja „6.3-m1” na końcu. Opisy MCP23017, MCP3201, ARM, PFAIL_N i trybu stołowego w sekcjach wcześniejszych dotyczą 6.1 / 6.2-s1 i zostały jako historia formatu.

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

## 6.2-s1 — format S1 (1.10.2026)

Zmiany według `Plytki/Format-S1/zadania/ZADANIE-FIRMWARE-S1.md` (F-01…F-09, decyzje D-1…D-3); pełna tabela w `README.md` tej rewizji.

Nowe i zmienione zdarzenia w `events_NNN.ndjson`:

| Typ | Kiedy | Pola |
|---|---|---|
| `power_fail` | ostatnia linia po zboczu PFAIL_N (GPIO3) | `t_us` (zbocze), `stop_us` (koniec próbkowania), `source` PFAIL_N, `reason` UVLO, `samples_not_written` |
| `pfail_glitch` | stan niski krótszy niż 30 µs (3 odczyty co 10 µs) | `t_us`, `count` — sesja trwa |
| `daq_stats` | co 10 s | `convst`, `samples`, `adc_errors`, `adc_resets`, `lost_ticks`, `sample_hz`, `adc_spi_hz`, `soft_event_drops` |
| `can_config` | start zadania CAN | `bitrate` 500000, `mode` listen_only, `rx_queue` 128, `time_source` rx_task_esp_timer_us, `profile`, `rpm_stale_us` |
| `can` | każda ramka (zdarzenie miękkie) | jak w 6.1 + `dlc` |
| `rpm_obd` | ważna odpowiedź Mode 01 PID 0C | `rpm`, `ecu`, `profile` |
| `rpm_rejected` | SF z PID 0C, ale długość ISO-TP niezgodna z DLC | `id`, `reason` |
| `rpm_stale` | brak ważnego RPM od 1 s (raz na przerwę) | `last_us`, `ecu` — brak danych, nie 0 rpm |
| `can_stats` | co 1 s, gdy liczniki się zmieniły | `frames`, `rx_missed`, `rx_overrun`, `bus_errors`, `rx_error_counter`, `state`, `log_dropped`, `rpm_bad_length`, `rpm_other_ecu` |
| `config` | jak w 6.1 | + `current_chain` (bank LOGGER: P06 R2), `firmware` 6.2-s1 |

`meta.json`: `firmware` EGRLab-6.2-s1, `adc_spi_hz`, `hardware` (płytki S1), `channels` (CH7 = VBAT_SENSE, akumulator auta), `power_fail`, `can` (obecność, bitrate, tryb, źródło czasu, profil).

Zdarzenia „miękkie” (`can`, `rpm_*`) przy pełnej kolejce zdarzeń nie oznaczają zapisu jako niezdrowego: rośnie licznik `log_dropped` / `soft_event_drops`, a próbki EGR mają pierwszeństwo (P10 R2 `docs/INTEGRACJA.md`). Limit ruchu CAN zapisywanego bez strat trzeba wyznaczyć na stole (odbiór P10 „Ruch ciągły”).

Tryb stołowy (D-2): PFAIL_N = L przez ≥ 100 ms od startu (P02 podłączony bez zasilania, CORE z USB) — bez plików na karcie, bez TEST, licznik sesji nie rośnie; konsola, podgląd i kalibracja działają.

## 6.3-m1 — płytka M1-R1 (8.10.2026)

Zmiany według `Plytki/M1-specyfikacja/zadania/ZADANIE-M1-KROK8-FIRMWARE.md` (M-01…M-13); pełna tabela w `README.md` tej rewizji. Format próbek bez zmian (wersja 5, rekord 40 B), zmienia się znaczenie kanałów.

**Kanały AD7606B (M-03, M-04):** CH1 P1_EGR i CH2 P3 (300 k / 100 k), CH3–CH5 P4/P5/P6 (100 k szeregowo), **CH6 = prąd silnika** (INA240A2 ×50 na boczniku 5 mΩ, U = VS/2 + 0,25 V/A, RC 1 k / 1 n), CH7 VBAT_CAR (499 k / 100 k), **CH8 = SENS_5V** (100 k, wyjście TPS2553). Nominalne wzmocnienia z wejściem 5 MΩ: 4,06 / 4,06 / 1,02 ×3 / 1,0002 / 6,0898 / 1,02. Prąd jest próbkowany razem z napięciami (koniec MCP3201 i jego przedziału czasu): `raw[5]` to wyjście INA240, `current_raw` = 65535 i `current_status` = 2 (ABSENT) w każdym rekordzie. Prąd = `(raw[5]·FS/32768·gain[5] + offset[5] − current_zero) / current_volts_per_amp`; w config `local_current: false`, więc `tools/egrlog.py` liczy go z `raw[5]` bez zmian w czytniku. Ten sam tor w banku LOGGER i TEST (D-M1-7). Zero (ok. VS/2) mierzy rozkaz `zero` przy wyłączonym mostku i bez prądu ECU: przez całą sekundę linie silnika CH1/CH2 w ±0,5 V, CH6 stabilne (< 20 mV p-p) w 1–4 V.

**Zanik zasilania (M-10):** M1 nie ma PFAIL_N ani podtrzymania. Pliki nie są zamykane przy zaniku zasilania; writer robi `fsync` obu plików co `CONFIG_EGR_SD_SYNC_MS` (domyślnie **1000 ms**, w 6.2-s1 2 s). Po zaniku w pliku może brakować ostatniej sekundy i ostatni blok `BLK1` może być obcięty — czytnik zgłasza to jako obcięty ostatni blok i czyta resztę. Nie ma już zdarzeń `power_fail` ani `pfail_glitch`. Przy wyłączaniu przyrządu: najpierw `stop`, odczekać ok. 2 s, potem wyłącznik.

**Tryb bez karty (M-11, zastępuje tryb stołowy F-02):** jeśli karta SD się nie zamontuje (np. zasilanie tylko z USB — D-M1-6: SD, AD7606B VDRIVE i MAX31856 są wtedy bez 3,3 V), firmware działa dalej bez plików: bez TEST, licznik sesji nie rośnie, konsola wypisuje „TRYB BEZ KARTY”. AD7606B bez zasilania daje błędy odczytu: jedno zdarzenie `adc_error` na serię (pełna liczba w `daq_stats.adc_errors`), dane oznaczone jako nieważne, następna konfiguracja zaczyna od pełnego RESET i 2100 ms.

Nowe i zmienione zdarzenia w `events_NNN.ndjson`:

| Typ | Kiedy | Pola |
|---|---|---|
| `overcurrent` | M-06: \|I\| z CH6 ponad `CONFIG_EGR_SW_CURRENT_LIMIT_MA` (domyślnie 8 A) w dwóch kolejnych próbkach; raz na epizod | `t_us`, `config_id`, `amps` (null = nasycenie / nieznana skala), `limit_a`, `bank`, `drive_was_permitted` |
| `test_rejected` | rozkaz `test` przy liniach pod napięciem (ECU podpięte, zapłon) | `t_us`, `reason`: MOTOR_LINES_LIVE, SENSOR_LINES_LIVE, SENS_5V_ON, VOLTAGE_UNKNOWN, ADC_CONFIG, ADC_STALE |
| `sens5v_in_logger` | CH8 > 1 V poza bankiem TEST (SENS_EN i tak wyłączane) | `t_us` |
| `button` | M-12: przycisk START / STOP (GPIO15) | `t_us`, `press`: `short` (znacznik `mark`), `long` (≥ 1 s: SAFE → LOGGER albo STOP), `stop` (w stanach TEST od razu) |
| `daq_stats` | co 10 s | jak 6.2-s1 + `overcurrent_samples` |
| `state` | jak dotąd | nowy powód FAULT: `OVERCURRENT` (zamiast `HARDWARE_NOT_ARMED`, `DRIVE_IO`, `INTERLOCK`, `TEST_ADAPTER`, `LOGGER_ADAPTER_PRESENT`) |
| `config` | jak dotąd | `local_current` false, `current_time` ad7606b_simultaneous, `synchronous` true, `ch8` SENS_5V (zamiast `aux_position`), `current_chain` jeden tor M1, `hardware` M1-R1, `firmware` 6.3-m1; bez `current_adc_gain` / `current_adc_offset` |

`meta.json`: `firmware` EGRLab-6.3-m1, `hardware` M1-R1, `channels` (osiem opisów), `input_impedance_ohm`, `filter_pf`, `current` (kanał 6, puste pola MCP3201, sposób pomiaru zera), `power_fail` (`input` null, okres fsync), `can`.

Profil w NVS ma wersję 7 i klucz `profile_m1`: kalibracja zapisana przez 6.1 / 6.2-s1 (inny sprzęt) nie wczytuje się na M1. Rozkazy `auxcal` i `iscal` są odrzucane; skalę prądu CH6 ustawia `ivpa <bank> <V/A>` (opis w `05-profile.md`).
