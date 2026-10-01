# EGRLab 6.2-s1 — firmware pod format S1

*1.10.2026. Kopia części programowej `Rewizje/EGRLab-v6.1-rc1` (firmware, profile, narzędzia, testy) zmieniona według `Plytki/Format-S1/zadania/ZADANIE-FIRMWARE-S1.md`: wymagania F-01…F-09 i decyzje użytkownika D-1…D-3 z 1.10. Wydanie 6.1-rc1 zostaje bez zmian i służy testom regresji jako wzorzec sprzętu (model M2.1: `hardware/`, `stabilizacja/`, `reference/`).*

**Status: kod, kontrole hosta i 5/5 kompilacji ESP-IDF 5.4.3 gotowe; sprzętu nie uruchamiano — odbiór niżej: NIE ZBADANO.** Wszystkie obrazy mają `EGR_HARDWARE_ACCEPTED=0`; kompilacja nie jest odbiorem.

## Zmiany względem 6.1-rc1

| ID | Zmiana | Pliki |
|---|---|---|
| F-01, D-3 | **PFAIL_N na GPIO3** (P02 R4 → P03 R6, R42 1 kΩ / R43 100 kΩ): wejście bez wewnętrznych podciągnięć, przerwanie na zbocze opadające po uzbrojeniu. Zadanie `pfail` (priorytet 22): najpierw napęd (`board_power_fail_stop`: ARM i PWM w dół na stałe), potem koniec próbkowania, linia `power_fail` (reason UVLO, liczba próbek niezapisanych) i zamknięcie obu plików. GPIO41 (wyjście triggera) jest wysoko od zbocza do zamknięcia plików — pomiar ODBIOR P02 R4 O-05. Stan niski krótszy niż 30 µs to `pfail_glitch`, sesja trwa. | `board.c`, `app_main.c`, `storage.c` |
| F-02, D-2 | **Tryb stołowy:** PFAIL_N = L przez ≥ 100 ms od startu (tylko USB, P02 bez zasilania) — bez plików na karcie, bez TEST (`test` odrzucone), licznik sesji w NVS nie rośnie, PFAIL_N ignorowany. Konsola, podgląd i kalibracja działają. | `app_main.c`, `storage.c` |
| F-03 | Sprawdzone: CH7 (indeks 6) = VBAT_SENSE, P05 R3 R31 499k / R32 100k i wejście AD7606B 5 MΩ → nominalnie 6,0898 jak w 6.1. Warunek 9–16,5 V dotyczy akumulatora auta, nie pakietu 4S; opis w `meta.json` i komentarzach. | `control.h`, `control.c`, `storage.c` |
| F-04 | **Rozruch AD7606B:** ≥ 10 ms przed RESET, RESET 20 µs, **2100 ms** po pierwszym RESET (było 10 ms). Konfiguracja z odczytem kontrolnym **przed** MEAS_EN, potem 25 ms na przekaźniki; błąd konfiguracji = MEAS_EN wyłączone. Błąd odczytu (zanik P05, BUSY) unieważnia konfigurację, a następna zaczyna od pełnego RESET i 2100 ms; bez samoczynnego powrotu do TEST. | `board.c`, `app_main.c` |
| F-05 | `EGR_SAMPLE_HZ` do 10 000 (start 2 kS/s przy SPI 1 MHz; kwalifikacja 10 kS/s przy 4 MHz), okno prądu 256 punktów (20 ms do 12,8 kS/s), zdarzenie `daq_stats` co 10 s (CONVST, próbki, błędy, resety, zgubione takty). Kalibracja dalej w firmware, nie w rejestrach AD7606B. | `Kconfig.projbuild`, `measure.*`, `app_main.c`, `board.c` |
| F-06 | Potwierdzone po rewizji S1 P06 (bocznik 5 mΩ, INA240A2 G50, dzielnik 1:2 — bez zmian): współczynniki jak w 6.1; w każdym zdarzeniu `config` pole `current_chain`. Odrzucanie danych przy READY = 0 i w BYPASS bez zmian. | `jsonlog.c` |
| F-07 | Łata P09 (MAX31856: CS 2/2, 300 ms po konfiguracji, odczyt kontrolny CR0/CR1, rejestry 0x0C–0x0F, błąd = NAN i fault 255) nałożona bez zmian. | `board.c` |
| F-08 | **CAN w osobnym zadaniu** `can` (priorytet 7, poniżej zapisu). Ramki i RPM jako zdarzenia „miękkie” (pełna kolejka = licznik straty, nie błąd zapisu DAQ). `can_config` na starcie i w `meta.json` (500 kbit/s, listen-only, źródło czasu, profil), `can_stats` co 1 s przy zmianie liczników. Dekoder RPM `obd.c`: ISO-TP SF z długością zgodną z DLC, jeden ECU (0x7E8 wypiera wyższe), `rpm_stale` po 1 s — brak danych ≠ 0 rpm. | `app_main.c`, `obd.*`, `storage.c` |
| F-09 | `profiles/hardware.json`: P02 R4, P03 R6, P05 R3, P06 R2, P09 R2, P10 R2 z interfejsem S1; P01 zastąpiona przez P02 R4; P04 / P07 / P08 / P11 bez rewizji S1. Kalibracja i tożsamości bez zmian (schema 6). | `profiles/hardware.json` |
| D-1 | Wersja 6.2-s1 (`PROJECT_VER`, `meta.json`, `config`). Kompilacja w Dockerze: `scripts/egrlab-idf` (obraz `espressif/idf:v5.4.3`, waga CPU 2, ≤ 2 rdzenie — Frigate ma pierwszeństwo). | `firmware/CMakeLists.txt`, `scripts/egrlab-idf` |

Zdarzenia i pola logu: `docs/04-firmware-logi.md`, sekcja „6.2-s1”.

## Kontrole (1.10.2026)

| Kontrola | Wynik |
|---|---|
| Kompilacje ESP-IDF 5.4.3 (Docker, `espressif/idf:v5.4.3`) | **5/5**; w `main/` jedno ostrzeżenie (wariant core: `adc_probe_software_mode` nieużywana przy CORE_ONLY) — to samo co w 6.1; obraz bazowy 6.1 (logger) z tego kontenera ma 418 800 B jak w wydaniu 6.1 |
| Testy hosta C (`tests/run_host.py --cc gcc`) | 107 asercji, 0 nieudanych testow · runtime: 47 assertions OK · health: 64 assertions, 0 failed · obd: 23 assertions, 0 failed · ADC fault injection: 111 assertions OK · Current ADC fault injection: 15 assertions OK · Storage contracts: 41 assertions OK |
| Python (`python3 -m unittest discover -s tests`) | OK — 86 regresji 6.1 (na modelu sprzętu 6.1) i 10 nowych (`test_v62_s1.py`) |
| Próby mutacyjne nowych kontroli (`tests/probe_v62_mutations.py`) | **11/11** z zerową |
| Najdłuższe zdarzenie `config` (pola maksymalnej długości) | 1280 B z 2048 |

| Wariant | Obraz | SHA-256 |
|---|---|---|
| core | 363 808 B | `0c20bcb1d9b1a0a9…` |
| minimal | 417 584 B | `9dd278cff0c8a13d…` |
| logger | 424 960 B | `bd236e0ca161f740…` |
| test | 418 240 B | `64dc7b62834af910…` |
| wifi | 970 688 B | `3b1907f30dfbfca9…` |

Pełne sumy i źródła: `verification/builds.json`; obrazy do wgrania: `firmware/prebuilt/<wariant>/` (`python -m esptool --chip esp32s3 -p PORT -b 460800 --before default_reset --after hard_reset write_flash "@flash_args"` z katalogu wariantu).

## Odbiór na sprzęcie — NIE ZBADANO

1. **PFAIL (P02 R4 O-05):** zbocze PFAIL_N → GPIO41 w dół (pliki zamknięte) ≤ 10 ms przy 6 W; plik czytelny po wyjęciu pakietu, ostatnia linia `power_fail`.
2. **Tryb stołowy:** CORE z USB, P02 podłączony bez zasilania → komunikat „TRYB STOLOWY”, brak katalogu sesji, `test` odrzucony.
3. **P05 kroki 8–10:** rozruch AD7606B (2,1 s), konfiguracja przed MEAS_EN, zanik 5V_SYS przy sesji → FAULT, ponowna konfiguracja z RESET.
4. **P05 kroki 12–17:** 2 kS/s przy 1 MHz, potem kwalifikacja 4 MHz i 10 kS/s (`daq_stats`: `convst` = `samples`, `lost_ticks` = 0).
5. **P10 „Ruch ciągły”:** 10 min, liczba ramek w logu = we wzorcu, `can_stats` bez strat; RPM z zewnętrznego testera.
6. **P06:** wspólna magistrala SPI z P05 (MCP3201 tryb 0 / AD7606B tryb 2); dane odrzucone przy READY = 0 i w BYPASS.
7. **P09 MODUL-KWALIFIKACJA krok 4:** odłączony moduł → błąd w logu, nigdy 0 °C.

## Budowanie i testy

Z katalogu `firmware` (komputer 24/7, D-1):

```text
../../../scripts/egrlab-idf idf.py -B build-logger -DIDF_TARGET=esp32s3 -DSDKCONFIG=sdkconfig.logger "-DSDKCONFIG_DEFAULTS=sdkconfig.defaults;sdkconfig.logger.defaults" build
```

Zmień `logger` na `core`, `minimal`, `test` albo `wifi`. Testy z katalogu wydania: `python3 tests/run_host.py --cc gcc`, `python3 -m unittest discover -s tests`, `python3 tests/probe_v62_mutations.py`.

## Pliki

- `firmware/` — źródła, `sdkconfig.*.defaults`, `prebuilt/` (5 wariantów).
- `profiles/`, `tools/` — jak w 6.1 (profil sprzętu z rewizjami S1).
- `tests/` — testy 6.1 (ścieżki sprzętu wskazują na 6.1-rc1), `test_obd.c`, `test_v62_s1.py`, `probe_v62_mutations.py`.
- `docs/` — 04–06 z 6.1, w 04 sekcja 6.2-s1.
- `verification/` — `builds.json`, logi kompilacji, `sdkconfig.*`, wyniki testów hosta i prób mutacyjnych.
