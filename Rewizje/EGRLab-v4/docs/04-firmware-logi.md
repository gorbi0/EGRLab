# Firmware i dane EGRLab v4

## Budowa

ESP-IDF **v5.4.3**, targetesp32s3. W terminalu skonfigurowanego ESP-IDF:

```text
cd firmware
idf.py set-target esp32s3
idf.py build
idf.py -p COMx flash monitor
```

`sdkconfig.defaults` ustawia32MB Flash OPI,16MB PSRAM OCT80MHz,240MHzCPU, FreeRTOS1000Hz, logger2000S/s. Sprawdź rzeczywisty nadruk modułu. Active TEST iWi‑Fi domyślnieoff, hardware accepted0. Warianty `sdkconfig.test.defaults` i`sdkconfig.wifi.defaults` służą osobnym buildom opisanym w `verification/README.md`. Zmiana defaultów nie nadpisuje istniejącego sdkconfig; używaj osobnych ścieżek SDKCONFIG/build. Nie wgrywaj cudzego pliku pełnego sdkconfig dla innego modułu.

## Moduły i własność

| Moduł | Odpowiedzialność |
|---|---|
|control.c/.h|maszyna stanów, limity, identyfikacja, regulatorP, kampania|
|profile.c|walidacja profilu i atomowa akceptacja poleceń kalibracji|
|board.c/.h|GPIO, MCP, przekaźniki, ADC SPI, SD, TC, CAN, gateSTOP|
|measure.c|nasycenie oraz czasowe okno prądu20ms|
|trigger.c|detektory i summary, jeden właściciel: akwizycja|
|jsonlog.c|ograniczone bufory JSON i liczby/null|
|storage.c|PSRAMring, blokiCRC, segmenty, kolejka config iACK|
|app_main.c|taski, manager, PAUSE/ACK, CLI, status, snapshot|
|webui.c|AP/HTTP, jedna instancja netif, callback kolejkujący|

Akwizycja na rdzeniu1; safety/manager/writer/auxiliary/radio/console na0. Sterowanie stanu chroni control_mutex. Snapshot pomiarów ma krótki spinlock; ADC ma własny mutex. Radio nie startuje/kończy pod control_mutex. Safety nie czeka na managera, aby wyłączyć GPIO przy transitioning/STOP.

Zmiana konfiguracji: inhibitGPIO39 → zatrzymanie timera → notifyPAUSE → ACK z akwizycji po ostatniej konwersji i użyciu starego config → przełączenie banku/sensora → zapis i odczyt rejestrówADC → pełny JSON config do kolejkiwriter → fflush/fsync iACK → publikacja niezmiennej migawkiID → resetdetektorów/summary → resume → pierwsza nowa próbka. Timeout pozostawia FAULT i wyłączony motor. Nie ma pauzy opartej tylko na odczekaniu20ms. Pierwsza próbka maGAP, osobne zdarzenieconfig_gap opisuje przedział.

STOP z konsoli/WWW od razu blokuje ARM w board pod blokadą GPIO i zwiększa generację; zaległe polecenia ruchu mają starą generację i są pomijane. Ponowne zwolnienie programowej blokady wymaga zgodnego tokenu. FizycznySTOP działa niezależnie i kasujeHW_ARMED. Nie oznacza to certyfikowanego czasu odpowiedzi całego systemu; ten mierzysz na odbiorze.

## Stany i komendy

```text
BOOT → SAFE
SAFE → LOGGER → IDENTIFY → LOGGER
SAFE → SENSOR_CHECK → READY → MANUAL/GOTO/SWEEP/FRICTION/CYCLE/THERMAL → READY
READY + hotsoak → sekwencja GOTO/FRICTION → READY i przerwa → kolejna seria
błąd → FAULT; stop → SAFE; brak automatycznego powrotu do ruchu
```

| Polecenie | Znaczenie / warunki |
|---|---|
|stop|natychmiastowe programowe inhibit, następnie SAFE i wyłączenie sensora|
|status / profile|stan, mapping/ID/bank i skalowanie; profile wypisuje linie kalibracji|
|bind VALVE_ID ADAPTER_ID|SAFE;1…23 znakiA–Z,a–z,0–9,_,-; zmianaID kasuje mapping/LEARN|
|save|SAFE; zapis profilu4 wNVS i ponowny commit config|
|bank 0/1|SAFE; LOGGER/TEST prądu, bez zasilenia sensora|
|bypass 0/1|SAFE/LOGGER;0 prąd ważny,1 nieważny dla aktualnego banku|
|aux 0/1|SAFE/LOGGER; deklaruje mechaniczneHI/LO; nie porusza przełącznikiem|
|logger / identify|tryb pasywny i pomiarowa identyfikacja4/5/6|
|test|SAFE, kwalifikacja hardware i mapa; SENSOR_CHECK bez motoru|
|learn CLOSED OPEN SIGN|READY; zapis zmierzonych krańców i znaku±1|
|manual DUTY MS|READY, maks250ms, soft/hardware limity|
|goto P / sweep / friction ±1 / cycle N / thermal|READY iLEARN; automatyczny zakres10–90%|
|hotsoak PERIOD_S COUNT / hotsoak_stop|kampania10…3600s/1…200serii; stop także w trakcie ruchu|
|zero|SAFE/READY, LOGGER wypięty, świeża stabilna1s aktywnego banku|
|cal B CH G O|SAFE; bank0/1, kanał0…7, gain0,1…20, offset±2V|
|auxcal POS G O|SAFE; kalibracja pozycjiHI/LO wspólna dla banków|
|currentcal B VZERO|SAFE; zmierzone1…4V|
|limits DUTY AMPS TEMP|SAFE; duty≤0,35, current≤3,5A,10…60°C|
|metric 0/1|SAFE; kwalifikacja metryki próbkowanego prądu|
|mark|znacznik zdarzenia z czasem monotonicznym|

Kropka dziesiętna w CLI. QUEUED nie oznacza wykonania; czekaj naOK/REJECTED. Kalibracja kandydacka jest walidowana przed zmianą profilu. Domyślny TEST build nadal ma hardwareaccepted0. KonsolaLOGGER pozwala na przygotowanie kalibracji, lecz nie na ruch.

## Format binarny4

Little-endian. Sesja `/sd/session_N/`; N zwiększane wNVS. Istniejącej sesji nie nadpisuje. `meta.json` opisuje urządzenie/częstotliwość; UTC=null (brak sterownikaRTC). `samples_000.egr`, kolejne001…; `events_000.ndjson`, kolejne001… Każdy plik rotuje przed1GiB. Numer segmentu jest porządkowy w nazwie, licznik próbek i czas pozostają ciągłe. Czytnik sprawdza zgodnośćsession/version/rate pomiędzy segmentami.

Nagłówek32B `<8sHHIIIQ>`: magicEGRLOG1\0, version4, header_bytes32, sample_rate, record_bytes32, file_flags(bit0synthetic), session64. Blok16B `<4sIII>`: BLK1, count1…256, bytes=count×32, CRC32payload(IEEE/zlib). Writer zwykle64próbki/blok, częściowy po100ms.

Rekord32B `<QI8hHH>`: t_us64 odCONVST, sequence32,8×int16raw, flags16, config_id16. Bity:0GAP,1TESTbank,2sensoron,3programowypermit,4zarezerwowanyMARK(znacznik jest wNDJSON),5trigger,6saturacja≥32760/≤−32760,7invalidADC. BitPERMIT to żądanie programu, nie potwierdzenie rzeczywistej energii motoru.

Próbka należy do konfiguracji wskazanej przezID nawet wtedy, gdy metadane są fizycznie w późniejszym segmencie zdarzeń. Czytnik najpierw strumieniowo zbiera konfiguracje ze wszystkichsegmentów. ID1…65535; po wyczerpaniu potrzebna nowa sesja. Nie ma zawijaniaID i nadpisania znaczenia starego numeru.

ConfigJSON: type,t_us,config_id,bank,ch_supply/ground/feedback,full_scale[8],gain[8],offset[8],current_zero,current_valid,current_volts_per_amp,closed/open/opening_sign,learned,aux_position,adc_software_mode,adc_config_ok,current_window_qualified,current_metric. Nieważne liczby to`null`; jedna linia≤2047B. Zapis config jest potwierdzony przezwriter przed publikacją. Brak migawek, błędnyADC lub nasycenie dają puste wartości wCSV; surowe kody pozostają.

Pozostałe zdarzenia: config_gap,state,command_result,mark,trigger,temperature,summary,hotsoak_point,can,rpm_obd,can_drop,adc_error,summary_dropped. Summary opisuje własnyID/bank i min/mean/max prawidłowych wartości wokoło1s. CAN czas=odebranie przez task, nie znacznik sprzętowy ramki. Niefinitywne wartości oraz uszkodzone termopary nigdy nie są zerem.

## Bufory, przepustowość, pretrigger

8MiB PSRAM naRAW to262144rekordy, około131s przy2000S/s. To zapas na opóźnienieSD, nie zachowanie danych po zaniku zasilania. 1024 miejsca po2048B na zdarzenia, plus osobna kolejka config. Gęsty CAN może zapełnić kolejkę wcześniej niż buforRAW. Każdy overflow/utrata ticków pozostawia jawny błąd i blokuje aktywnyTEST; po naprawie przyczyny zrestartuj sesję.

RAW64kB/s plus bloki: przy pełnych blokach około64,5kB/s. Segment1GiB około4,6h; dla częściowych bloków i innej częstotliwości inaczej. ZdarzeniaCAN zajmują osobne miejsce. Nie prognozujemy czasu do4GiB na podstawie samych32B. Flush/fsync co2s i przyconfig/rotacji; nagły zanik może utracić więcej przy blokadziekarty. Ciągły zapis zachowuje historię przedMARK/triggerem bez osobnego trybu pretrigger, o ile dane zostały zapisane naSD.

## Analiza i testy hosta

`inspect katalog`, `scan katalog`, `export katalog --csv`, `report katalog --html`. `--recover` odrzuca urwany ostatni blok; nie ignoruje błędnegoCRC. `--from/--to` to sekundy czasu monotonicznego sesji. Raport domyślnie obwiednia min/max; `--full` dopuszcza≤200000próbek w wybranym oknie. Brak zależnościCDN. Wysokość piku zachowana, czas trwania zjawiska analizuj z pełnych próbek/skopu.

```text
gcc -std=c11 -I firmware/main tests/test_control.c firmware/main/control.c -lm -o test_control
gcc -std=c11 -I firmware/main tests/test_runtime.c firmware/main/control.c firmware/main/profile.c firmware/main/jsonlog.c firmware/main/measure.c firmware/main/trigger.c -lm -o test_runtime
```

Host nie testuje scheduleraESP, timingów ani elektryki. Dodatkowe testy graniczne sterownikaADC uruchamia `tests/probe_adc.py`. Wyniki wykonanych prób i dokładny toolchain w `verification/`.
