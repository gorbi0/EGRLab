# Kalibracja, profile i wymiana modułów

Trzy pliki w `profiles/`: sprzęt/kalibracje, zawór/adapter, pojazd/sesja. Szablony mają `accepted:false` i puste wyniki pomiarów. Nominalne wartości w dokumentacji nie są danymi odbioru.

W firmware nadal istnieje zwarta migawka profile_t ze względów prostoty NVS, lecz informacje są rozdzielone logicznie i w plikach użytkownika. To nie jest mechanizm wgrywania dowolnego nowego sterownika z JSON. Nowy rodzaj ADC/napędu wymaga kodu; zmiana skali/egzemplarza obsługiwanego modułu wymaga konfiguracji, bez przebudowy sterownika.

## Komendy

| Komenda | Znaczenie |
|---|---|
| `bind VALVE_ID ADAPTER_ID` | Powiązanie egzemplarzy; zmiana kasuje mapę/LEARN, adapter także akceptacje torów |
| `daqmodule DAQ_001` | Nowy egzemplarz DAQ: kasuje akceptację obu banków napięcia |
| `imodule 0 IL_001` / `imodule 1 DR_001` | Moduł prądu LOGGER / TEST; zmiana kasuje jego ważność/kalibrację/kwalifikację metryki |
| `cal bank kanał gain offset` | Kalibracja toru napięcia; kanały 0…7 |
| `auxcal 0 gain offset` / `auxcal 1 gain offset` | Osobna kalibracja AUX HI/LO |
| `vcalok bank 1` | Ręczna deklaracja odbioru całej grupy napięć banku, po pomiarach |
| `iscal bank adc_gain adc_offset volts_per_amp` | Skala lokalnego prądu; kasuje jego akceptację i metrykę |
| `currentcal bank zero` | Zmierzone zero napięciowe wyjścia INA |
| `icalok bank 1` | Deklaracja odebranego lokalnego toru prądu |
| `bank 0` / `bank 1` | W stanie SAFE wybór toru do kalibracji |
| `bypass 1` / `bypass 0` | Programowo wyłącz/włącz użycie prądu aktualnego banku; 0 wymaga kalibracji |
| `zero` | Nowa sekundowa seria zerowania w SAFE/READY, przy odłączonym ECU i zakazie ruchu |
| `session AUTO_01 ZIMNY_01` | Identyfikator auta i rodzaju próby; nie zmienia kalibracji |
| `metric 1` | Metryka okna prądu sprawdzona oscyloskopem |
| `qualify 1` | Po odbiorze sprzętu i zmianie commissioning.h, akceptacja TEST |
| `save` / `profile` / `status` | NVS / podgląd / stan |

Nazwy: 1–23 znaki ASCII, litery/cyfry/_/-. Bank 0=LOGGER, 1=TEST. Kanał 5 AD jest rezerwą, a lokalny prąd ma `iscal`; nie kalibruj go poleceniem `cal bank 5`.

Napięcia: z dwóch punktów `x=raw*FS/32768` wylicz `gain=(V2−V1)/(x2−x1)`, `offset=V1−gain*x1`. Mierz od strony kompletnego adaptera, aby objąć rezystory przy EGR. Sprawdź wynik w trzecim punkcie i na zakresach ±10/±5/±2,5 V używanych po IDENTIFY. Ustawienie auxcal unieważnia napięcia obu banków; vcalok zawsze na końcu zestawu zmian.

Prąd: najpierw porównaj lokalne raw z wyjściem INA zmierzonym DMM. `adc_gain=(VINA2−VINA1)/(raw2−raw1)`, `adc_offset=VINA1−raw1*adc_gain`. Następnie zmierz zero i skalę V/A na boczniku w obu kierunkach. Nominały: adc_gain=0,001220703125 V/kod, offset=0, V/A=0,25, zero≈2,5 V. Do pliku wpisuje się wyniki rzeczywiste, nie automatycznie te liczby. Użyj trzeciego punktu i próby po ogrzaniu, aby wykryć nieliniowość/błąd znaku.

`icalok` umożliwia `bypass 0`, potrzebne do użycia toru i procedury zero. Te deklaracje odnoszą się do Twojego rzeczywistego odbioru; program nie odgaduje, że podłączono miernik wzorcowy. Potwierdzenie `qualify` nie zastępuje lokalnego OC ani fizycznego ARM. Po `zero` i zmianach konfiguracji ponownie naciśnij ARM przed ruchem.

NVS używa nowego klucza profile5. Stary profile4 nie jest automatycznie importowany: inny ADC i źródło odniesienia prądu oznaczają nową kalibrację. Bezpieczne ustawienia startowe mają prąd nieważny oraz napięcia niezaakceptowane.

## Pełny import i dokumentacja sesji

```text
python tools/profile_v6.py profiles/hardware.json profiles/valve.json profiles/session.json --out profil.txt
```

Generator przygotowuje rozkazy i `profil.manifest.json`; nie wysyła ich do urządzenia i nie generuje TEST/ARM/qualify. Jest przeznaczony do kompletnego odebranego zestawu. Przy budowie etapowej korzystaj z odpowiednich komend ręcznie, potwierdzając tylko obecne/odebrane banki. W szablonach generator odmawia użycia pustych lub nieodebranych pomiarów.

Po imporcie ustaw świadomie bank i `bypass 0` tylko dla odebranego używanego toru. Skopiuj manifest obok sesji na SD wraz z konfiguracją builda. Firmware zapisuje w config identyfikatory DAQ i aktualnego modułu prądu oraz pojazdu/zaworu/adaptera. Numery P01/P02/P04/P08/P09/P10 oraz opis termopar są w towarzyszącym manifeście; **firmware nie odczytuje automatycznie tego pliku ani numerów z PCB**. Operator odpowiada za zgodność wpisów z oznaczeniami. To celowe uproszczenie prototypu.

Wymiana P06 nie usuwa kalibracji P07 ani temperatur. Wymiana DAQ usuwa oba banki napięcia. Zmiana adaptera wymaga ponownego potwierdzenia całych torów zależnych od adaptera. Zmiana egzemplarza zaworu wymaga IDENTIFY/sprawdzenia pinów oraz własnego LEARN. Zmiana granic sprzętowych DRIVE/SENSOR/SAFE wymaga nowego odbioru, aktualizacji manifestu i kwalifikacji — nie wystarczy zwiększyć wartości JSON.

## Uzupełnienie V6

Na pierwszy start AD SPI=1 MHz (`CONFIG_EGR_ADC_SPI_HZ`), SD=4 MHz (`CONFIG_EGR_SD_KHZ`), lokalny prąd=500 kHz. Zapis 2 kS/s to 80 kB/s samych próbek; odebrać ciągły zapis wraz ze zdarzeniami i CAN. Nie usuwać limitów 500 µs okresu / 400 µs odczytu prądu, aby ukryć zbyt wolny transfer.

Po zmianie trybu/banku lub zatwierdzeniu konfiguracji akwizycja zatrzymuje się, a watchdog może rozbroić latch. Poczekać na poprawne świeże próbki i ponownie nacisnąć **fizyczny ARM**, także gdy poprzednie polecenie `zero` wymusiło taki cykl. W razie REJECTED sprawdzić HW_ARMED, gotowość i kalibrację; nie obchodzić zatrzasku. Kierunek: mostek wyłączony → potwierdzony INA/INB → 5 ms → ponowne zezwolenie.

Profile JSON/NVS mają wersję 6; zmiana nominałów wymaga nowych pomiarów i identyfikatorów modułów. Format próbek pozostaje wersją 5 (40 B), a schemat zdarzenia config/metadanych pozostaje 5. Numer rewizji urządzenia nie jest numerem formatu logu.
