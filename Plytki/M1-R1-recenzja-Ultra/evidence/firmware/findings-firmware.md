# Notatka niezależnego audytu firmware M1-R1

8.10.2026. Materiał dla głównej recenzji, nie publikacja ani poprawka projektu. Źródła paczki tylko odczyt. Nie czytano poprzedniej recenzji Astra. Uwzględniono ZAKRES-RECENZJI-M1-R1.md oraz AUDYT.md i SPECYFIKACJA.md; nie kwestionowano D-M1-1…13.

Prefiks ścieżek źródłowych poniżej: `C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/Rewizje/EGRLab-v6.3-m1/`.

## FW-01 — ważne: blokada mutexu zawiesza limity ruchu i odczyt fizycznego STOP, a watchdog nadal jest karmiony

**Miejsce:** `firmware/main/app_main.c:293–337` (szczególnie 295–297, 301, 309, 328, 331); `app_main.c:440–450,485,568–570`; `firmware/main/control.c:173–176,283–287`; `firmware/main/board.c:132–148`.

**Ścieżka:** manager trzyma `control_mutex` podczas całego `execute_locked`. Komenda `profile` jest legalna również w MANUAL/GOTO/SWEEP; wykonuje ponad 20 synchronicznych printf pod tym mutexem. Zadanie safety próbuje mutexu z czasem 0. Jeśli się to nie uda, pomija `control_step`, `board_drive` i `button_tick`. Jego gałąź na linii 331 wyłącza napęd wyłącznie przy `stop_pending || transitioning`; komenda profile nie ustawia żadnej z tych flag. Rejestry LEDC i DRIVE_EN zachowują poprzedni stan. Tymczasem `board_watchdogs_feed()` wykonuje się na początku każdego obiegu, więc watchdog zadaniowy i RTC uznają tę sytuację za poprawną.

**Rzeczywista, zwykła operacja wywołująca okno:** z domyślnym profilem rzeczywista funkcja `print_profile` generuje 544 bajty, 575 po obowiązującej zamianie LF na CRLF. Obrazy mają UART 115200 bit/s i CRLF (`verification/sdkconfig.test:1265,1937`), czyli nawet po odjęciu całych 128 bajtów pojemności FIFO transmisja wymaga co najmniej 38,8 ms. Lokalne ESP-IDF potwierdza synchroniczne oczekiwanie na FIFO w `components/esp_driver_uart/src/uart_vfs.c:185–195,226–246`. Włączona wtórna konsola USB może dodać oczekiwanie: `components/esp_vfs_console/vfs_console.c:80–87`; `components/esp_driver_usb_serial_jtag/src/usb_serial_jtag_vfs.c:78,148–169` zawiera timeout 50 ms. Komenda profile wydana pod koniec impulsu MANUAL opóźnia jego zakończenie; w tym oknie nie jest sprawdzany limit profilu ≤3,5 A ani termopara. Niezależny limit 8 A w akwizycji pozostaje czynny. Naciśnięcie i puszczenie przycisku całkowicie w tym oknie może nie zostać zauważone.

**Reprodukcja faktycznej implementacji:** `probe_independent.py` wycina bez zmian `safety`, `button_tick`, `led_colour` i funkcje bramki/LEDC z oryginalnych plików, linkuje oryginalne `control.c`; zastępuje wyłącznie platformę i harmonogram. Zainicjowano poprawny MANUAL 10 ms, a następnie wstrzyknięto 400 ms zajętego mutexu przy zdrowych ADC/storage/TC. Wynik:

```text
mutex_blocked: elapsed_us=400000 deadline=110000 now=505000 state=MANUAL DRIVE_EN=1 RPWM=306 LPWM=0 watchdog_feeds=400 physical_button_reads=0
mutex_released: state=READY DRIVE_EN=0 RPWM=0
actual_print_profile: bytes=544 CRLF_bytes=575 conservative_UART_min_us=38802.1
```

400 ms jest próbą wstrzykniętej blokady, nie twierdzeniem o zmierzonej latencji zwykłego printf ani o wykonanym teście płytki. Ograniczenie czasowe wynikające z samego UART wyliczono osobno.

**Naprawa:** wykonywać printf po skopiowaniu profilu i zwolnieniu mutexu; wynieść odczyt i awaryjne wyłączenie fizycznego STOP poza sekcję zależną od managera; dodać ograniczony czas od ostatniej skutecznej oceny sterowania, po którym napęd jest zatrzaskowo wyłączany. Karmienie watchdogów powinno zależeć od faktycznego postępu tej oceny albo jawnego, bezpiecznego stanu przejściowego. Zweryfikować scenariusz printf/blokady mutexu oraz przycisku i upłynięcia deadline w środku tej blokady.

## FW-02 — uzupełniająca luka obsługi błędów: brak trwałej blokady po błędzie startu watchdogów

**Miejsce:** `firmware/main/board.c:402–419`; `app_main.c:293,194–225,557`; `board.c:77–84,355–361`.

**Dowód:** jeśli `esp_task_wdt_add(NULL)` zwróci błąd, `board_watchdogs_start` wychodzi przed włączeniem RTC WDT. Safety loguje „TEST zablokowany”, lecz wykonuje tylko `board_emergency_stop` i kontynuuje. Nie ustawia trwałej flagi ani FAULT. Utworzony później manager pobiera aktualny token bramki w `commit_locked("boot")`; udany commit zwalnia dokładnie ten token na linii 225. `board_mode` dodatkowo ustawia `drive_ok=true`. W efekcie po normalnej kwalifikacji można załączyć mostek bez działających obu watchdogów. To nie jest prośba o dodatkowy watchdog sprzętowy: wadliwa jest obsługa błędu istniejącego, zatwierdzonego mechanizmu D-M1-4.

Lokalny IDF potwierdza realne wyjście `ESP_ERR_NO_MEM` podczas przydziału wpisu TWDT: `components/esp_system/task_wdt/task_wdt.c:170–177,667–678`. Reconfigure z `idle_core_mask=0` wcześniej usuwa zadania idle; timer startuje tylko, jeżeli są subskrybenci (`:578–594`).

**Reprodukcja:** ten sam harness wstrzykuje niepowodzenie `board_watchdogs_start`, wykonuje prawdziwy `safety`, następnie prawdziwe operacje `board_stop_token`, `board_mode`, `board_release` i `board_drive`, w kolejności odpowiadającej udanemu commit. Wynik: `watchdog_init_failure_then_commit_gate: token=1 DRIVE_EN=1 RPWM=306`. Pełnego `commit_locked` nie uruchamiano w tym teście; jego ścieżkę potwierdzono odczytem wskazanych linii.

**Granica dowodu:** nie odtworzono rzeczywistego wielowątkowego startu ESP-IDF po niepowodzeniu alokacji. `esp_task_wdt_reset` przy niezarejestrowanym zadaniu wypisuje błąd; powtarzane synchroniczne logowanie może samo zagłodzić managera i zachować wyłączony napęd. Dlatego dowód wykazuje brak trwałego warunku watchdog_ok i zwalnianie bramki, ale nie dowodzi, że obecny binarny obraz w konkretnym przypadku NO_MEM faktycznie dojdzie do ruchu. Nie stawiać tego na równi z bezpośrednio odtworzonym FW-01/FW-03/FW-04 bez tej granicy.

**Naprawa:** sprawdzić inicjalizację watchdogów przed dopuszczeniem managera do normalnego trybu; trwale blokować TEST, jeżeli inicjalizacja nie powiedzie się. `watchdogs_ok` musi być częścią warunku `board_release` / zezwolenia napędu, albo błąd powinien prowadzić do kontrolowanej paniki/resetu przy wymuszonym DRIVE_EN i SENS_EN=L. Nie ignorować błędu odświeżenia watchdogów.

## FW-03 — ważne: autonomiczny TESTER wymaga napięcia z odłączonego samochodu

**Miejsce:** `firmware/main/control.c:255–269`; `control.h:16`; M1 `SPECYFIKACJA.md`, sekcje 1,4,5; `docs/06-diagnostyka.md:17`.

**Dowód:** po komendzie test stan SENSOR_CHECK przechodzi przez bezwarunkową kontrolę CH7 9…16,5 V. CH7 jest VBAT_CAR z X1.13, nie zasilaniem VMOTOR z 4S. Specyfikacja TESTER nakazuje podłączyć IBT-2 oraz czujnik przez X1.5/.7/.11/.12 i odłączyć ECU, nie wymaga akumulatora auta na X1.13. Przy opisanym samodzielnym stole CH7 bez zewnętrznego zasilania nie osiąga 9 V, więc nie można dojść do READY, choć pakiet, mostek i czujnik działają prawidłowo. Nie jest to uproszczenie zatwierdzone D-M1-3: kod pozostawił zależność od innego źródła napięcia.

**Reprodukcja:** oryginalne `control_step` z SENSOR_CHECK, aktualną próbką, poprawnym zasilaniem czujnika 5 V, mapą, ADC/storage/drive i `CH7=0` zwraca `FAULT / SUPPLY`: `standalone_TEST_X1_13_unpowered: state=FAULT fault=SUPPLY`. Dla rzeczywistego odłączonego wejścia nie zakładano dokładnego 0 V — istotny jest brak napięcia 9 V.

**Naprawa:** określić poprawny dla TEST punkt pomiaru zasilania silnika i jego zakres 4S. Jeśli sprzęt pozostaje bez pomiaru VMOTOR, nie uzależniać TEST od niepodłączonego VBAT_CAR. Alternatywna świadoma zmiana kontraktu wymaga jawnego połączenia X1.13 z odpowiednim źródłem i limitu obejmującego pełne 16,8 V; samo podłączenie pełnego 4S do X1.13 nadal przekracza obecne 16,5 V. Nie zaleca się przypadkowego mostkowania torów auta z pakietem.

## FW-04 — ważne: po błędzie ADC LOGGER zapisuje dalsze rekordy jako ważne, choć konfiguracja została unieważniona

**Miejsce:** `firmware/main/board.c:346–351`; `app_main.c:113,123–130,156–159,176`; `control.c:255`; `app_main.c:301–311`.

**Ścieżka:** `board_adc` po błędzie odczytu ustawia `config_ok=false` oraz `adc_reset_needed=true`. Akwizycja zatrzaskuje acquisition_healthy=false i wyłącza napęd, ale następnie kontynuuje pętlę. Następny udany odczyt nie naprawia `config_ok`, co jest słuszne: ustawienia przetwornika nie zostały ponownie zweryfikowane. Mimo tego flaga `SAMPLE_INVALID`, przeliczenia napięć i wpis do pliku korzystają z kopii `active_cfg.adc_config_ok=true` sprzed awarii. W LOGGER `control_step` wychodzi przed sprawdzeniem adc_ok, więc nie następuje FAULT/config_pending ani samoczynny commit/reset. Kolejne rekordy mogą bezterminowo wskazywać starą, formalnie nadal poprawną konfigurację. Podgląd `adc_ok` i globalna flaga zdrowia mają stan błędu, ale rekordy nie przenoszą tej informacji.

**Reprodukcja faktycznej implementacji:** `probe_adc_metadata.py` wykonuje niezmienione `acquisition` i `board_adc`, linkując oryginalne control.c, measure.c i jsonlog.c. Wstrzyknięto udany odczyt, TIMEOUT, następnie dwa udane odczyty. Nie zakładano, że TIMEOUT oznacza reset ADC lub zmianę zakresów; test dotyczy wyłącznie rozbieżności ważności danych. Wynik:

```text
after_error_then_two_successes: reads=4 adc_errors=1 board_config_ok=0 adc_reset_needed=1 acquisition_healthy=0 active_cfg_id=17 active_cfg_ok=1 state=LOGGER pushed=3
record[0]: sequence=0 config_id=17 flags=1 SAMPLE_INVALID=0 SAMPLE_GAP=1
record[1]: sequence=2 config_id=17 flags=0 SAMPLE_INVALID=0 SAMPLE_GAP=0
record[2]: sequence=3 config_id=17 flags=0 SAMPLE_INVALID=0 SAMPLE_GAP=0
latest_voltage_CH6_finite=1 value=2.500500
```

Istnieje zdarzenie `adc_error` i luka sequence=1, więc nie jest to całkowicie niewidoczna awaria. To jednak nie unieważnia automatycznie dalszych rekordów ani konfiguracji. Jeżeli rzeczywistą przyczyną był zanik zasilania lub reset zmieniający ustawienia ADC, dane mogą być dodatkowo przeliczane z nieaktualnymi zakresami; ta konsekwencja jest warunkowa i nie była potrzebna do wykazania błędu.

**Naprawa:** po utracie ważności ADC zatrzymać pobieranie do pełnego RESET i ponownego commit albo obowiązkowo flagować wszystkie dalsze rekordy jako SAMPLE_INVALID i nie wyliczać z nich poprawnie wyglądających napięć, dopóki board_adc_config_ok nie wróci po zweryfikowanej konfiguracji. Po wznowieniu oznaczyć lukę. Dodać próbę integracyjną error→udane transfery w LOGGER, testując flagi rekordów i config_id, nie tylko flagę drivera.

## Zasięg i ograniczenia

- Przeczytano w całości: app_main.c, board.c, control.c, profile.c, storage.c, measure.c, trigger.c, jsonlog.c, obd.c, webui.c, control.h, board.h, measure.h, storage.h, Kconfig.projbuild, commissioning.h, README.md; przejrzano sdkconfig.defaults i istotne fragmenty sdkconfig.test, docs/06-diagnostyka.md oraz testów/probe_drive.py i run_host.py.
- Uruchomiono bez zmian oryginalne testy C, wyłącznie kompilując wyniki do work-fw: control 131 asercji/0 błędów; runtime 66 OK; health 58/0; obd 23/0. TinyCC wymagał lokalnego shimu math.h; jest tylko w katalogu prób. Nie jest to pełny re-build ESP-IDF.
- Niezależne próby oraz ich źródło i SHA-256 wejść: probe_independent.py, independent_firmware_probe.c, independent_firmware_probe-results.txt, probe-manifest.json; probe_adc_metadata.py, adc_metadata_probe.c, adc_metadata_probe-results.txt, adc-metadata-probe-manifest.json.
- Nie badano czasów na rzeczywistym ESP32/IBT-2, karty SD, fizycznych stanów GPIO podczas resetu/paniki ani analogu. Powyższe błędy dotyczą konkretnych ścieżek programu; obliczenie UART nie zastępuje pomiaru sprzętu.
- Wszystkie dostarczone obrazy mają EGR_HARDWARE_ACCEPTED=0; blokują obecnie kwalifikację TEST. FW-01/FW-02 dotyczą kodu, który ma sterować napędem po zakończeniu zadeklarowanej kwalifikacji, a nie potwierdzonego napędzania mostka obecnymi obrazami.
- Zauważone kwestie eksportera i gwarancji max 1 s utraty danych przekazano głównemu agentowi, który weryfikuje te tory samodzielnie. Nie dublowano ich tutaj.

Odtworzenie własnych prób z katalogu projektu:

```powershell
& '.egrlab-toolchains/kicad/runtime/bin/python.exe' 'M1-R1-recenzja-Ultra/work-fw/probe_independent.py'
& '.egrlab-toolchains/kicad/runtime/bin/python.exe' 'M1-R1-recenzja-Ultra/work-fw/probe_adc_metadata.py'
```
