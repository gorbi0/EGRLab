# EGRLab 6.3.1-m1 — firmware pod płytkę M1 (6.3-m1 po recenzji)

*8.10.2026. Kopia części programowej `Rewizje/EGRLab-v6.2-s1` (firmware, profile, narzędzia, testy) zmieniona pod sprzęt M1-R1 według `Plytki/M1-specyfikacja/zadania/ZADANIE-M1-KROK8-FIRMWARE.md` (M-01…M-13). Źródła o sprzęcie: `Plytki/M1-specyfikacja/SPECYFIKACJA.md`, `AUDYT.md` (D-M1-1…13), `Plytki/M1-R1-review/docs/GPIO.csv` i `parts.json`. Wydanie 6.2-s1 zostaje bez zmian i służy jako wzorzec regresji (ścieżka profilu schema 6), a 6.1-rc1 — jako model sprzętu dla testów 6.1.*

**6.3.1-m1 (8.10.2026):** poprawki po dwóch recenzjach Astry (`Plytki/M1-R1-recenzja-Astra` M1-01…07, `Plytki/M1-R1-recenzja-Ultra` M1-08…12), tabela R-01…R-12 niżej; katalog i ścieżki bez zmian (recenzje wskazują pliki 6.3-m1), wersja `6.3.1-m1` w `PROJECT_VER`, `config` i `meta.json`.

**Status: kod, kontrole hosta i 5/5 kompilacji ESP-IDF 5.4.3 gotowe; sprzętu nie uruchamiano — odbiór sprzętu: NIE ZBADANO.** Wszystkie obrazy mają `EGR_HARDWARE_ACCEPTED=0`; kompilacja nie jest odbiorem.

## Poprawki 6.3.1-m1 po recenzji M1-R1

Każdą poprawkę zamyka regresja `tests/probe_review_m1.py` (rzeczywiste funkcje firmware i eksportera, bodźce z prób recenzji; w `run_host.py`): na źródłach 6.3-m1 nie przechodzi (`verification/review-regressions-r1.json`), na 6.3.1-m1 przechodzi (`review-regressions.json`). Cofnięcie każdej poprawki wykrywają nowe mutacje `r_m1xx_*` w `probe_v63_mutations.py`.

| ID | Zgłoszenie | Poprawka | Pliki |
|---|---|---|---|
| R-01 | M1-01: samo USB zasila przez D1 modułu szynę 5 V bez 3,3 V (GPIO ponad VDRIVE AD7606B) | decyzja użytkownika 8.10: **D1 na module wylutowana** (SPECYFIKACJA M1 sekcja 4); samo USB niczego nie zasila, programowanie przy włączonym pakiecie; tryb bez karty dotyczy już tylko braku / błędu karty | dokumentacja; odbiór pkt 7 |
| R-02 | M1-02: TEST sprawdzał akumulator auta, 16,8 V = SUPPLY | w TEST X1.13 zworką do X1.3 (VMOTOR), przewód auta odpięty; zakres TEST **9,0–17,3 V**; `config.ch7_source`, `hotsoak_point.vbat_source` | `control.c`, `jsonlog.c`, `app_main.c` |
| R-03 | M1-03: błąd startu watchdogów nie blokował napędu | `watchdogs_ok` dopiero po pełnym starcie TWDT i RTC WDT; `board_release()` bez niego odmawia, `test` odrzucany, zdarzenie `watchdog_failed`; kasuje to tylko restart | `board.c`, `board.h`, `app_main.c` |
| R-04 | M1-04: „najwyżej 1 s utraty” nieprawdziwe (kolejka RAM do ok. 105 s) | opis poprawiony (okres fsync ≠ granica straty); `daq_stats` i `status`: `pending_samples`, `since_sync_ms`, `sync_ms`; procedura wyłączenia w `04-firmware-logi.md` | `storage.*`, `app_main.c`, docs |
| R-05 | M1-05: generator schematu nadpisywał `.kicad_pro` | generator uzupełnia tylko `meta` / `sheets`; bramka `check_pro_preserved.py` w `run_schematic.py` (na generatorze R1 zgłasza utratę `board`, `net_settings`…) | `Plytki/M1-R1-review/src` |
| R-06 | M1-06: instrukcja TEST bez pełnej listy żył ECU | tabela LOGGER → TEST → LOGGER z pięcioma żyłami (X1.5, X1.7–X1.10), zworkami X1.11–X1.13 i pomiarem ciągłości; usunięte „nowy ARM” | SPECYFIKACJA M1, `06-diagnostyka.md` |
| R-07 | M1-07: testy zależne od plików spoza wydania | `tests/fixtures/` (profile 6.2-s1, `board.c` P09 R1) z SHA-256 i commitem źródła; `test_preflight.py`; model 6.1-rc1 dołączany do paczki recenzji | `tests/` |
| R-08 | M1-08: zajęty mutex trzymał ruch, przycisk nieczytany, watchdog karmiony | odpowiedzi konsoli składane pod blokadą, wypisywane po niej; przycisk w każdym obiegu `safety` niezależnie od blokady; ruch bez oceny sterowania > 20 ms = STOP (`control_stale`); watchdog karmiony tylko przy postępie oceny albo bez napędu | `app_main.c` |
| R-09 | M1-09: po błędzie ADC rekordy znów „ważne” | ważność próbki = migawka **i** bieżący `board_adc_config_ok()`; do rekonfiguracji INVALID, bez wartości fizycznych i triggerów; manager odzyskuje AD7606B (`config_gap` `adc_recovery`, nowy `config_id`), przy niepowodzeniu ponawia co 1 s (`adc_recovery_failed`) | `app_main.c` |
| R-10 | M1-10: eksporter kasował prąd CH6 | pola MCP3201 tylko przy `local_current: true`; w M1 prąd z `raw[5]`; kolumna `sens_5v_v`, opis serii w raporcie HTML | `tools/egrlog.py` |
| R-11 | M1-11: `cal … 5` zostawiał akceptację prądu | `cal <bank> 5` kasuje `icalok` i metrykę banku; `daqmodule` kasuje akceptację prądu obu banków | `profile.c`, `app_main.c` |
| R-12 | M1-12: NaN wyzwalał REF / FEEDBACK | warunki tylko dla skończonych (zmierzonych) napięć | `trigger.c` |

## Zmiany względem 6.2-s1

| ID | Zmiana | Pliki |
|---|---|---|
| M-01 | Usunięte: MCP23017 i I²C, dekoder CS, P04 SAFE (ARM, HW_ARM, INTERLOCK), P05 TAPS / MEAS_EN / READY, MCP3201, wejścia adapterów (LOG/TEST_PRESENT), HEART. Wszystkie piny wprost z GPIO według `GPIO.csv` (nazwy w `board.h`). Bez detekcji adaptera TEST sprawdza okablowanie z napięć: `test` odrzucony, gdy CH1–CH5 albo CH8 mają ponad 0,5 V (ECU steruje albo zasila czujnik). | `board.*`, `control.*`, `app_main.c`, `Kconfig.projbuild` |
| M-02 | AD7606B jak P05 R3 (szeregowy programowy, OS = 111, wewn. odniesienie, ±10 V); **RESET z GPIO10** (20 µs; R9 10 k do GND). Rozruch F-04 bez zmian: 10 ms → RESET → 2100 ms; konfiguracja przed trybem; błąd odczytu albo nieudana konfiguracja = następny pełny RESET. | `board.c` |
| M-03 | Skale nominalne z `parts.json` i wejścia 5 MΩ: CH1/CH2 4,06, CH3–CH5 i CH8 1,02, CH6 1,0002, CH7 6,0898. CH8 = SENS_5V (zamiast AUX, zawsze ±10 V). Opis kanałów w `meta.json`. | `control.c`, `storage.c` |
| M-04 | **Prąd z CH6 AD7606B** (INA240A2 ×50, 5 mΩ, U = VS/2 + 0,25 V/A, RC 1 k / 1 n), ten sam tor w LOGGER i TEST, próbkowany razem z napięciami. Rekord v5 bez zmian (`current_raw` 65535, status ABSENT); config `local_current: false`, więc `egrlog.py` liczy prąd z `raw[5]`. Zero mierzy `zero` przy wyłączonym mostku i bez prądu ECU (CH1/CH2 w ±0,5 V przez 1 s), nie stała 2,5 V. | `app_main.c`, `control.c`, `jsonlog.c` |
| M-05 | IBT-2 przez 74AHCT125: **RPWM GPIO1 / LPWM GPIO21** (LEDC, 10 bit, `CONFIG_EGR_PWM_HZ` 100–25 000, domyślnie 1 kHz jak 6.2-s1), **DRIVE_EN GPIO39**. Kierunek = który PWM, drugi nisko; zmiana kierunku = DRIVE_EN i oba PWM w dół na 5 ms; wypełnienie ≤ 90 %. Przy starcie wszystkie trzy (i SENS_EN) w stanie niskim zanim staną się wyjściami. | `board.c`, `Kconfig.projbuild` |
| M-06 | Bez sprzętowego okna OC (D-M1-4): **programowe ograniczenie prądu** z CH6 w zadaniu akwizycji (`CONFIG_EGR_SW_CURRENT_LIMIT`, domyślnie włączone, 8 A, 2 kolejne próbki = 1 ms przy 2 kS/s; działa także bez kalibracji, na nominałach; nasycenie = przekroczenie) — zdejmuje DRIVE_EN, zatrzask do następnej konfiguracji, TEST → FAULT `OVERCURRENT`, zdarzenie `overcurrent`. **Potwierdzone przez użytkownika 8.10: zostaje domyślnie włączone.** Watchdogi: TWDT 200 ms z paniką (zadanie safety) i RTC WDT 1 s z resetem systemu; owinięty `esp_panic_handler` zdejmuje DRIVE_EN i SENS_EN rejestrami przed zrzutem; `esp_restart` przez shutdown handler. | `measure.*`, `app_main.c`, `board.c`, `main/CMakeLists.txt` |
| M-07 | TPS2553: **SENS_EN GPIO40** tylko z bankiem TEST (`board_mode` odmawia i wyłącza; safety wyłącza poza TEST), **SENS_FAULT_N GPIO42** wprost. W SENSOR_CHECK i ruchu CH8 musi mieć 4,5–5,5 V i zgadzać się z pinem zasilania czujnika (0,3 V). CH8 > 1 V w LOGGER → zdarzenie `sens5v_in_logger`. | `board.c`, `control.c`, `app_main.c` |
| M-08 | MAX31856 ×2 na SPI3, CS GPIO8 / GPIO16 wprost (bufor SDO z OE = CS przezroczysty). Łata F-07 bez zmian (`board_temperature` identyczna z P09). SD na SPI3, CS GPIO7. | `board.c` |
| M-09 | TWAI listen-only jak F-08: RX GPIO18; TX na GPIO17 (niepodłączony; TCAN1051V ma TXD i S na 3V3). | `board.c` |
| M-10 | Brak PFAIL_N: usunięte F-01 (zadanie `pfail`, `power_fail`, `pfail_glitch`) i tryb stołowy F-02. Przy zaniku zasilania pliki mogą zostać niedomknięte; `fsync` co `CONFIG_EGR_SD_SYNC_MS` = 1000 ms (było 2 s), to okres synchronizacji, nie granica straty (6.3.1-m1, R-04). | `storage.*`, `app_main.c` |
| M-11 | Brak karty SD (6.3.1-m1: samo USB już nic nie zasila — R-01) nie zatrzymuje firmware — **tryb bez karty** (bez plików, bez TEST, licznik sesji stoi, komunikat w konsoli); AD7606B bez zasilania: dane nieważne, jedno `adc_error` na serię, ponowna próba od pełnego RESET. | `app_main.c`, `board.c`, `storage.*` |
| M-12 | Przycisk **START / STOP GPIO15** (filtr 20 ms): w stanach TEST każde naciśnięcie = STOP od razu; poza TEST krótkie = znacznik `mark`, długie (≥ 1 s) = SAFE → LOGGER albo STOP. **Dioda RGB modułu GPIO38** (WS2812 przez RMT, bez komponentu `led_strip`): miga 2 Hz przy żywej akwizycji; zielony LOGGER, niebieski SAFE, żółty TEST, biały ruch, czerwony FAULT / stoi, fioletowy bez karty. Wyzwalacz oscyloskopu GPIO41 bez zmian. | `board.c`, `app_main.c` |
| M-13 | `profiles/hardware.json`: `schema` 7, `configuration` „M1-R1”, `configuration_version` 1; moduły M1 (DAQ_001, IL_001) i IBT2 (DR_001); jeden tor prądu dla obu banków (IL_001, D-M1-7); termopary TC_001/TC_002; bez `aux`. `profile_v6.py` obsługuje schema 7 (`ivpa` zamiast `iscal`, bez `auxcal`), schema 6 bez zmian. Profil NVS wersja 7, klucz `profile_m1` (kalibracja 6.x nie przechodzi na M1). | `profiles/`, `tools/profile_v6.py`, `control.h`, `profile.c` |
| — | Wersja 6.3-m1 (`PROJECT_VER`, `meta.json`, `config`). Konsola: `ivpa`; usunięte `aux`, `auxcal`, `iscal`. Podgląd Wi-Fi: pola `naped` i `tryb` zamiast `uzbrojony` / `adapter`. | `CMakeLists.txt`, `app_main.c`, `webui.c` |

Zdarzenia i pola logu: `docs/04-firmware-logi.md`, sekcja „6.3-m1”; profil i rozkazy: `docs/05-profile.md`; procedura TEST na listwie X1: `docs/06-diagnostyka.md`.

## Kontrole (8.10.2026, 6.3.1-m1 — lokalnie po poprawkach)

| Kontrola | Wynik |
|---|---|
| Kompilacje ESP-IDF 5.4.3 (Docker, `espressif/idf:v5.4.3`, `scripts/egrlab-idf`) | **5/5**; w `main/` jedno ostrzeżenie (wariant core: `adc_probe_software_mode` nieużywana przy CORE_ONLY) — to samo co w 6.1 i 6.2-s1. `__wrap_esp_panic_handler` obecny w ELF (`nm`, wariant test). |
| Testy hosta C (`tests/run_host.py --cc gcc`) | control: 131 asercji, 0 nieudanych · runtime: 66 OK · health: 58, 0 failed · obd: 23, 0 failed · ADC fault injection: 118 OK · storage OK · Drive / SENS_EN: 45 OK · **regresje recenzji M1-02/03/08/09/10/11/12: PASS** (`probe_review_m1.py`; te same bodźce na źródłach 6.3-m1: FAIL we wszystkich grupach — `verification/review-regressions-r1.json`) |
| Python (`python3 -m unittest discover -s tests`) | OK — 104 testy (w tym `test_preflight.py`: fixture'y z SHA-256 i model 6.1-rc1) |
| Próby mutacyjne (`tests/probe_v63_mutations.py`) | **39/39** z zerową: 30 mutacji M-01…M-13 i 8 cofających poprawki z recenzji (`r_m102` … `r_m112`) |
| Najdłuższe zdarzenie `config` (pola maksymalnej długości) | 1140 B z 2048 |

| Wariant | Zawartość | Obraz | SHA-256 |
|---|---|---|---|
| core | uruchomienie ESP32 / PSRAM / SD, bez akwizycji | 364 016 B | `8cf283f88e16c755…` |
| minimal | LOGGER bez MAX31856 i CAN (prąd CH6 jest zawsze) | 422 944 B | `3214fce6a22408ee…` |
| logger | LOGGER + MAX31856 + CAN, TEST wyłączony | 430 304 B | `eedd7f7960d395ed…` |
| test | TESTER (IBT-2, SENS_5V) + MAX31856, bez CAN | 423 552 B | `1575080ff3b3c55d…` |
| wifi | jak test + SoftAP | 974 368 B | `0bd87671c0817eb5…` |

Pełne sumy: `verification/builds.json`; obrazy: `firmware/prebuilt/<wariant>/` (`python -m esptool --chip esp32s3 -p PORT -b 460800 --before default_reset --after hard_reset write_flash "@flash_args"` z katalogu wariantu). **Nie ma wariantów z P04 ani P07** — M1 nie ma tych płytek (D-M1-4: mostek to moduł IBT-2 sterowany wprost z GPIO, bez SAFE).

Przy zmianach testów względem 6.2-s1: usunięte `test_v62_s1.py` i `probe_v62_mutations.py` (sprawdzały F-01/F-02/P06/P02, których M1 nie ma — zostają w 6.2-s1), `probe_current.py` (MCP3201) zastąpiony `probe_drive.py`. W regresjach 6.1 cztery asercje dotyczące firmware tej rewizji (MCP23017, MCP3201, wersja profilu, odczyt SENSOR_HEALTHY) zmienione na odpowiedniki M1; asercje modelu sprzętu 6.1 bez zmian.

## Odbiór na sprzęcie — NIE ZBADANO

1. **Stany w resecie (M-05, M-06, M-07):** DRIVE_EN (GPIO39), SENS_EN (GPIO40), RPWM, LPWM zmierzone od włączenia zasilania przez bootloader do startu aplikacji, przy resecie przyciskiem i po panice (`panic` z konsoli JTAG / celowy błąd): zawsze L na wejściach 74AHCT125. GPIO39 (MTCK) ma po resecie wewnętrzne podciąganie ok. 45 k (karta ESP32-S3 v2.2, tab. 2-1, przyp. 7) — dlatego R2 (DRIVE_EN) ma 4,7 k (zmiana płytki po recenzji 8.10); zmierzyć DRIVE_EN ≤ 0,8 V w czasie bootloadera. GPIO40–42 bez podciągania.
2. **Watchdogi (M-06):** zablokowane zadanie safety → panika ≤ 200 ms, DRIVE_EN w dół przed zrzutem (oscyloskop na DRIVE_EN i UART); RTC WDT → reset ≤ 1 s.
3. **Ograniczenie prądu (M-06):** obciążenie IBT-2 rezystorem mocy / zablokowanym zaworem: zdarzenie `overcurrent` i DRIVE_EN w dół ≤ 1,5 ms od przekroczenia (pomiar prądu zewnętrznym bocznikiem). Zakres liniowy INA240 do ok. ±9 A.
4. **AD7606B (M-02):** rozruch 2,1 s z RESET z GPIO10; potem kroki P05 12–17 (2 kS/s przy 1 MHz, kwalifikacja 4 MHz / 10 kS/s, `daq_stats`).
5. **Prąd CH6 (M-04):** `zero` przy odpiętym mostku i ECU (ok. 2,5 V = VS/2), skala V/A w obu kierunkach (`ivpa`), porównanie z oscyloskopem metryki 20 ms (`metric`).
6. **SENS_5V (M-07):** TESTER na stole — CH8 4,5–5,5 V, FAULT_N przy zwarciu wyjścia; LOGGER — CH8 ≈ 0 V cały czas; `test` przy włączonym zapłonie i podpiętym ECU → `test_rejected`.
7. **USB i pakiet (R-01, M-11):** przed wlutowaniem modułu wylutowana D1 (brak ciągłości USB VBUS ↔ pin 5V); samo USB: płytka bez zasilania; pakiet + USB: konsola i programowanie; tabela stanów pakiet/USB i rozruch / zanik obu TSR (VDRIVE ≤ AVCC + 0,3 V). Bez karty: „TRYB BEZ KARTY”, `test` odrzucony.
8. **Przycisk i dioda (M-12):** krótkie / długie naciśnięcie, STOP w TEST; kolory i miganie diody modułu (WS2812 na GPIO38 — typ diody na DEV-KIT do potwierdzenia).
9. **MAX31856 (M-08):** MODUL-KWALIFIKACJA P09 krok 4 — odłączona termopara → błąd w logu, nigdy 0 °C. **CAN (M-09):** P10 „Ruch ciągły”.
10. **Zanik zasilania (M-10, R-04):** wyjęcie pakietu w trakcie zapisu przy normalnym i przy opóźnionym zapisie karty (3 s, 10 s) → plik czytelny `egrlog.py inspect`; strata równa niezapisanej kolejce (`pending_samples` z ostatniego `daq_stats`), nie deklarowana 1 s.
11. **Blokada managera (R-08):** `profile` / `status` podczas MANUAL, GOTO i SWEEP oraz przycisk wciśnięty w trakcie: czas od zdarzenia do DRIVE_EN = L na oscyloskopie (oczekiwane ≤ ok. 21 ms bez przycisku, przycisk ≤ ok. 21 ms po filtrze 20 ms).
12. **Przepięcie LOGGER ↔ TEST (R-02, R-06):** według tabeli w SPECYFIKACJI M1; X1.13 w TEST na X1.3, CH7 = napięcie pakietu ±1 %.

## Budowanie i testy

Z katalogu `firmware`:

```text
../../../scripts/egrlab-idf idf.py -B build-logger -DIDF_TARGET=esp32s3 -DSDKCONFIG=sdkconfig.logger "-DSDKCONFIG_DEFAULTS=sdkconfig.defaults;sdkconfig.logger.defaults" build
```

Zmień `logger` na `core`, `minimal`, `test` albo `wifi`. Testy z katalogu wydania: `python3 tests/run_host.py --cc gcc`, `python3 -m unittest discover -s tests`, `python3 tests/probe_v63_mutations.py --cc gcc`.

## Pliki

- `firmware/` — źródła, `sdkconfig.*.defaults`, `prebuilt/` (5 wariantów).
- `profiles/` — `hardware.json` M1-R1 (schema 7), `valve.json` i `session.json` jak w 6.2-s1; `tools/` — `profile_v6.py` z gałęzią M1.
- `tests/` — testy 6.1 (model sprzętu 6.1-rc1), `test_v63_m1.py`, `probe_drive.py`, `probe_v63_mutations.py`.
- `docs/` — 04–06 z 6.2-s1, w 04 sekcja 6.3-m1, w 05 i 06 uwagi M1.
- `verification/` — `builds.json`, skróty logów kompilacji, `sdkconfig.*`, wyniki testów hosta i prób mutacyjnych.
