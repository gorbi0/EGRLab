# Odtworzenie weryfikacji v4.1

Wykonano 22.09.2026 w Windows x64. Wyniki są plikami tekstowymi w tym katalogu. Firmware zbudowano oficjalnym ESP-IDF **v5.4.3**, commit `ea1c174c1cbb7348bd8ba0ff1eb306246938dd80`, Xtensa GCC `esp-14.2.0_20250730`. Wybrano ESP32-S3, Flash 32 MB OPI i PSRAM OCT. Kompilacja nie oznacza uruchomienia na urządzeniu.

## Kompilacja

Zainstaluj ESP-IDF 5.4.3 z narzędziami dla ESP32-S3. Otwórz terminal ESP-IDF. Poniższe komendy wykonaj w `firmware/`. Każdy wariant dostaje osobną konfigurację i katalog; ścieżkę zawierającą średnik należy zachować w cudzysłowie, także w PowerShell.

```text
idf.py -B build-logger -DIDF_TARGET=esp32s3 -DSDKCONFIG=sdkconfig.logger "-DSDKCONFIG_DEFAULTS=sdkconfig.defaults" build
idf.py -B build-test -DIDF_TARGET=esp32s3 -DSDKCONFIG=sdkconfig.test "-DSDKCONFIG_DEFAULTS=sdkconfig.defaults;sdkconfig.test.defaults" build
idf.py -B build-wifi -DIDF_TARGET=esp32s3 -DSDKCONFIG=sdkconfig.wifi "-DSDKCONFIG_DEFAULTS=sdkconfig.defaults;sdkconfig.wifi.defaults" build
```

Pełne konfiguracje użyte przy weryfikacji są w `sdkconfig.*.verified`; służą do porównania. Nie kopiuj ich w ciemno na inny wariant modułu. W każdym buildzie `EGR_HARDWARE_ACCEPTED=0`, także jeśli `CONFIG_EGR_ACTIVE_TEST=y`. Kompilacja wariantu TEST sprawdza jego kod, lecz nie odblokowuje napędu. W Wi-Fi zmień hasło przed użyciem. `build-outputs.json` zapisuje rozmiary i SHA-256 plików aplikacji z końcowej kompilacji; plików binarnych do wgrania nie dołączono. Firmware buduj dla swojego egzemplarza po kontroli sprzętu.

## Testy hosta

W katalogu projektu:

```text
python -m unittest discover -s tests -v
gcc -std=c11 -I firmware/main tests/test_control.c firmware/main/control.c -lm -o test_control
gcc -std=c11 -I firmware/main tests/test_runtime.c firmware/main/control.c firmware/main/profile.c firmware/main/jsonlog.c firmware/main/measure.c firmware/main/trigger.c -lm -o test_runtime
./test_control
./test_runtime
python tests/probe_adc.py --cc gcc --out verification
```

Testy C w tym wydaniu uruchomiono TinyCC 0.9.27 x64. Zamiast `gcc` użyto `tcc`, pominięto `-lm` (CRT Windows) i dodano przed pozostałymi nagłówkami `-I verification/host-tcc-include`. Dołączony `math.h` omija niezgodny nagłówek x87 z dystrybucji TinyCC; dotyczy wyłącznie hosta, **nie firmware ESP-IDF**. Zawiera użyte tu operacje float oraz deklarację `sqrt` z CRT. Te próby nie kwalifikują dokładności toru pomiarowego. Główne źródła firmware kompiluje prawdziwy toolchain Espressif bez tego nagłówka.

`test_runtime` wypisuje linię z rzeczywistego serializatora konfiguracji. Sprawdzono ją także ścisłym parserem JSON; wynik w `package-checks.json`. `probe_adc.py` wycina rzeczywistą funkcję `board_adc_ranges` z bieżącego `board.c` i podstawia błędy mutexu i transakcji. Nie symuluje elektryki, zegara SPI, sprzętowego BUSY ani schedulera.

## Próby fizyczne

Wypełnij [ODBIOR.md](ODBIOR.md) zgodnie z rozdziałem 03. Na etapie wydania wszystkie próby fizyczne mają status **NIEWYKONANE**. Odbiór obejmuje także trwający wiele godzin zapis SD, przeciążenie CAN, sekwencję zasilania, interlock, czas odcięcia, zakresy ADC, dryf i wpływ adapterów na instalację samochodu.

## Dodatkowe próby 4.1

`python tests/probe_storage.py --cc gcc --out verification` sprawdza rzeczywiste funkcje storage_event/drain_events i serializatory summary/hotsoak z podstawionym interfejsem FIFO/SD. Obejmuje granicę długości, przepełnienie, zwrot wpisu po błędzie zapisu i błędnym rozmiarze, pełne długie JSON oraz null. To test kontraktów wywołań, nie rzeczywistego schedulera ani implementacji ringbuffera.

Wyniki poprzedniego wydania zachowano w `history-v4/`; nie są dowodem wykonania nowych testów. Bieżące wyniki są bezpośrednio w `verification/` i w rozdziale 06.
