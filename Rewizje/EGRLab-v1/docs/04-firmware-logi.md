# Firmware i format logów

Projekt źródłowy jest przeznaczony dla ESP-IDF5.4.x i ESP32-S3. Nie został skompilowany ani uruchomiony na urządzeniu w tej sesji: w środowisku brak odpowiedniego toolchainu i sprzętu. Testy plików logów wykonano; testy C i pomiary czasu wykonania pozostają do uruchomienia.

## Moduły

| Moduł | Odpowiedzialność |
|---|---|
| `board.c` | GPIO, ekspander, ADC, SD, MAX31856, pasywny TWAI, PWM i odcięcie ARM |
| `control.c` | czysta logika stanów, polaryzacja, regulator, procedury i limity |
| `storage.c` | ring PSRAM, zapis blokowy z CRC, pretrigger i zdarzenia NDJSON |
| `app_main.c` | zadania FreeRTOS, konsola, profil NVS i orkiestracja |
| `commissioning.h` | jawna blokada przed odbiorem hardware |

`board_kill()` natychmiast zeruje MCU_ARM oraz PWM. Wyłączenie obu EN i przekaźnika mocy realizuje hardware. Żadna operacja I²C ani SD nie jest potrzebna do wyłączenia MCU_ARM. Zanik programu wykrywa zewnętrzny monostable, a przeciążenie niezależny komparator.

## Stany

```text
BOOT → SAFE → LOGGER → IDENTIFY → LOGGER
          └→ SENSOR_CHECK → READY → MANUAL / GOTO / SWEEP / FRICTION / CYCLE / THERMAL
                                ↑                       │ sukces
                                └───────────────────────┘
FAULT ← błąd podczas przygotowania lub ruchu
FAULT → SAFE po świadomym STOP; brak automatycznego wznowienia
```

LOGGER nigdy nie włącza własnego napędu. TEST wymaga zapisanego pin 5 V, zatwierdzonego hardware, fizycznego interlock, poprawnych napięć, świeżego ADC oraz sprawnego zapisu. Ruch dodatkowo wymaga fizycznego ARM i poprawnej TC1. Zanik dowolnego warunku przerywa próbę. Po FAULT zasilanie sensora zostaje odłączone; mechaniczny STOP i włożenie LOGGER blokują je również sprzętowo.

Zadania: acquisition na rdzeniu1, priorytet23; safety na rdzeniu0, priorytet20 co 1 ms; writer priorytet8; CAN/TC priorytet5; console priorytet3. Timer powiadamia task akwizycji, który inicjuje konwersję i odczytuje SPI. Timestamp oznacza rzeczywisty start konwersji, a nie idealną pozycję na siatce czasu. Nie jest to sprzętowo deterministyczny CONVST. Nadmiar powiadomień oznacza utracone terminy i blokuje TEST. Brak Wi-Fi/BLE podczas rejestracji.

Zmiana kierunku ma5 ms przerwy przy wyłączonym ARM. Regulator pozycji jest początkowo proporcjonalny, bez integratora. Wartości duty, prądu, temperatury i czasu są limitami rozruchowymi; nie pochodzą ze specyfikacji zaworu.

## Budowanie i odblokowanie

W terminalu ESP-IDF:

```text
cd firmware
idf.py set-target esp32s3
idf.py menuconfig
idf.py build
idf.py flash monitor
```

Sprawdź: Flash32 MB Octal/OPI, PSRAM16 MB Octal, taktowanie pamięci80 MHz na początek. Nie zmieniaj eFuse napięcia VDD_SPI; moduł N32R16 V jest fabrycznie wariantem1,8 V. Numer portu COM wybierz dla swojej płytki. UART0 pozostaje dla pokładowego CH343.

Domyślnie `CONFIG_EGR_ACTIVE_TEST=n` i `EGR_HARDWARE_ACCEPTED=0`. Po pełnym odbiorze z rozdziału03 wpisz zmierzone współczynniki kalibracji, zatwierdź plik profilu i dopiero wtedy zmień oba ustawienia. Wartości domyślne gain/offset są nominalne, nie wynikiem kalibracji. Kod weryfikuje dane sensora również po odblokowaniu. Fizyczny ARM pozostaje konieczny.

## Konsola

| Komenda | Funkcja |
|---|---|
| `status` | stan, pin 5V, napięcia, prąd, ratio, pozycja, TC1 i utracone terminy |
| `bind valve_id adapter_id` | w SAFE identyfikuje fizyczny zawór i adapter; zmiana unieważnia stary pinout/LEARN |
| `logger` | bank pomiarowy LOGGER, własny napęd i sensor OFF |
| `identify` | stabilny pomiar5/6 przez2s, zapis wyniku do RAM |
| `stop` | natychmiast ARM=0, sensor OFF, SAFE |
| `save` | w SAFE zapis profilu do NVS; akwizy­cja wstrzymana na czas operacji Flash |
| `test` | przełączenie K_POL bez napięcia i sprawdzenie własnego zasilania sensora |
| `learn rc ro sign` | zatwierdzone pomiarowo punkty pozycji; np. wartości z trzech kontrolowanych przejść |
| `manual duty ms` | pojedynczy impuls, np.`manual 0.05 50`; maksymalnie250ms w zatwierdzonym profilu |
| `goto p` | dojście do pozycji0,1…0,9 |
| `sweep` | punkty10…90…10%, timeout każdego ruchu |
| `friction +1` / `friction -1` | jedna rampa od aktualnej pozycji; kierunek otwarcia/zamknięcia z profilu |
| `cycle n` | n pełnych cykli10–90–10%, maksimum200 |
| `thermal` | SWEEP przy nadzorowanej TC1; ogrzewanie i plateau wykonuje operator |
| `mark` | zdarzenie ze wskazaniem miejsca w ring buffer |

Kolejność pierwszego profilu: `bind` → `logger` → `identify` → `status` → `stop` → `save`. Przy kolejnej sesji wczytany jest ten sam profil, ale dopasowanie do fizycznego zaworu pozostaje odpowiedzialnością operatora. Nie ma elektronicznego numeru seryjnego zaworu.

LEARN nie jest automatycznym szukaniem twardych ograniczników. Procedura mechanicznej weryfikacji znajduje się w rozdziale02. Polecenie zapisuje jej wynik. THERMAL nie steruje grzałką. FRICTION dla20/50/80% wykonuj jako `goto` i osobne rampy. Ograniczenie do takich jawnych czynności chroni nieznany napęd przed automatycznym przeciążaniem.

## PSRAM i pretrigger

Rekord ma32 bajty, a nie16: timestamp8 + sequence4 + osiem kodów16bit16 + flags2 + reserved2. Przy20 kS/s to640000B/s i2,304GB/h; przy 2kS/s64000B/s. Dane CAN i temperatur dochodzą osobno.

Implementacja alokuje ring8 MiB (262144 rekordy). To13,1072 s przy 20k lub131,072 s przy 2k. MARK zapamiętuje indeks ring buffer. Writer otwiera drugi plik i czyta wcześniejsze dane z tego samego bufora, następnie dopisuje10 s po znaczniku. Okno przed znacznikiem wynosi min(10 s, połowa ring buffer): **10 s przy 2 kS/s, 6,5536 s przy 20 kS/s**. Rzeczywistą liczbę rekordów zapisuje zdarzenie MARK.

Nie ma kopiowania kilku MB w ISR ani deklarowanej gwarancji zachowania pretrigger przy dowolnym zatrzymaniu SD. Jeśli writer nie zdąży przed nadpisaniem, rejestruje GAP i stan błędu. Do gwarantowanego10 s przy 20k potrzebne przeprojektowanie podziału pamięci, np. ring4 MiB + osobny snapshot6,4 MB. Ciągły plik SD zachowuje wcześniejszy zapis, jeśli nie wystąpił błąd.

Writer kopiuje najwyżej64 rekordy pod krótkim spinlockiem do bufora wewnętrznego, zwalnia lock i dopiero zapisuje SD. Nie wykonuje dostępu do pliku w sekcji krytycznej. Przepełnienie kolejki zdarzeń również jest błędem — CAN nie może ginąć niezauważenie.

## Format EGRLOG1

Little-endian. Nagłówek32 bajty:

| Offset | Typ | Znaczenie |
|---:|---|---|
| 0 | char[8] | EGRLOG1 + bajt0 |
| 8 | u16 | wersja1 |
| 10 | u16 | długość nagłówka32 |
| 12 | u32 | nominalna częstotliwość próbkowania |
| 16 | u32 | długość rekordu32 |
| 20 | u32 | flags; bit0 = dane syntetyczne |
| 24 | u64 | identyfikator sesji |

Blok: magic4=`BLK1`, count:u32, payload_bytes:u32, crc32:u32, następnie count rekordów. Count1…256, firmware używa maks.64. CRC32 IEEE/zlib obejmuje cały payload. Urwany ostatni blok można odrzucić w trybie recovery; nie dopisujemy zer i nie przechodzimy bez ostrzeżenia przez błędne CRC.

Rekord: t_us:u64, sequence:u32, raw[8]:i16, flags:u16, reserved:u16. Flagi zarezerwowane: bit0GAP, bit1TESTbank, bit2sensorvalid, bit3motorpermit, bit4MARK, bit5fault. Firmware A ustawia bity0/1/3; stan sensora, FAULT i MARK są autorytatywnie zapisane w NDJSON. Nie interpretuj nieustawionych bitów2/4/5 jako braku zdarzenia.

Sequence liczy dostarczone próbki. Utracone wyzwolenia timera nie dostają fikcyjnych próbek; licznik lost_ticks i GAP je ujawniają. Rzeczywiste odstępy wyznaczaj z t_us. Timestamp CAN jest czasem odbioru w tasku, nie sprzętowym znacznikiem początku ramki. Temperatury mają czas odczytu, fault i wartość/null; nie udają wspólnego próbkowania z ADC.

Sesja: `session_<counter>/samples.egr`, `events.ndjson`, `meta.json`, `mark_<time>.egr`. Istniejący katalog nigdy nie jest nadpisywany. NVS ma własny mechanizm integralności ESP-IDF; kod dodatkowo sprawdza rozmiar i magic profilu. Nie implementuje osobnego podpisu kryptograficznego ani CRC struktury profilu.

`meta.json` przechowuje konfigurację startową. Zmiany pin 5V i punktów LEARN pojawiają się jako zdarzenia `profile` z timestampem. Eksporter stosuje je w odpowiednim momencie; nie przelicza całej sesji ostatnim profilem. Zmiany kalibracji gain/offset wymagają nowej sesji. Nazwy fizycznego zaworu i adaptera przechowywane są w NVS; wpisz je również do dziennika odbioru.

FAT32: prototyp nie implementuje rotacji pliku. Przy20 kS/s limit4GiB jest osiągany po około 1h52 min; zatrzymaj i uruchom nową sesję wcześniej (zalecenie≤1h przy 20k). Przy2k limit wynosi około 18h38 min. Błąd zapisu przerywa TEST. Nie jest to bezobsługowy rejestrator wielodniowy ani gwarantowany zapis odporny na dowolny zanik zasilania.

## Odczyt na komputerze

```text
python tools/egrlog.py inspect examples/synthetic.egr
python tools/egrlog.py export examples/synthetic.egr --meta examples/synthetic.json --csv output.csv
python -m unittest discover -s tests -p "test_*.py" -v
```

Python korzysta wyłącznie z biblioteki standardowej. Dane przykładowe mają oznaczenie synthetic; nie pochodzą z auta. CSV zachowuje kody surowe, napięcia, prąd, różnicę napięć uzwojenia, ratio i pozycję. Nieprawidłowa polaryzacja lub referencja daje pustą wartość, a nie fałszywe0%.

## Zakres i ograniczenia

Kod obejmuje konsolę, akwizycję, ring/pretrigger, SD, CRC, stany i procedury ruchu po kalibracji, pasywne CAN, odczyt standardowych odpowiedzi RPM, dwie termopary i NVS. Nie obejmuje graficznego GUI, RTC, OTA, aktywnego OBD/UDS, automatycznej regulacji grzałki ani produkcyjnego mechanizmu odzyskiwania FAT. OLED i RTC są opcjami hardware, nie gotowymi funkcjami oprogramowania. Nominalne20 kS/s wymaga osobnego odbioru czasu wykonania lub szybszego sterownika opisanym sposobem.
