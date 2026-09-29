# Plan składania i odbioru

Samochód: Kia Sportage 1.7 CRDi, 2013 r., EGR28410-2A850. Posiadana płytka Waveshare N32R16-M jest odpowiednia; nie trzeba kupować innego MCU.

Każdy etap kończy się zapisanym wynikiem. Poniższe kryteria są planem pomiarów, nie deklaracją wykonanych prób.

| Etap | Zmontuj i sprawdź | Warunek przejścia |
|---|---|---|
| 0 | Oznaczenie modułu, rewizja Waveshare, numeracja adaptera EGR | Moduł N32R16 V; ciągłość przewodów; wykluczone odbicie lustrzane wtyczki |
| 1 | Sam ESP z USB, konsola, PSRAM | Boot bez błędów, rozpoznane16 MiB PSRAM; MCU_ARM=0 |
| 2 | Ochrona wejścia i przetwornice, bez MCU i mostka | 5 V i3,3 V w tolerancji; OVP odłącza przy 17,5–18,5 V; brak przegrzewania |
| 3 | Odwrotna polaryzacja, zapady napięcia, powrót zasilania | Brak uszkodzenia; po powrocie latch pozostaje rozbrojony |
| 4 | Safety ze sztucznymi wejściami | STOP, OC obu znaków, UV/OV, przerwanie pętli, zanik heartbeat wyłączają PERMIT |
| 5 | ADC i przekaźniki pomiarowe, znane napięcia | Kolejność8 kanałów, znaki, kalibracja; błąd sensora≤10 mV po kalibracji |
| 6 | INA i boczniki, obciążenie rezystancyjne | Pomiar prądu obu znaków; offset; dynamiczne wyłączenie OC |
| 7 | SD, CAN stanowiskowy, dwie termopary | 30 min bez utraty danych; detekcja odpięcia SD/TC; CAN LISTEN nie nadaje ACK |
| 8 | VNH z rezystorem12Ω/25 W, potem małym silnikiem | Poprawny znakU/I; bezpieczny STOP; brak przepięć szyny ponad projekt |
| 9 | Symulator czujnika5 V, feedback i PWM | Rozpoznaje obie polaryzacje; odrzuca niestabilne dane; zwarcie odczepu ograniczone |
| 10 | LOGGER w samochodzie, najpierw bypass shunta | Brak nowych DTC; pin 5/6 potwierdzony; brak zasilania TEST na portach LOGGER |
| 11 | EGR standalone | Czujnik z limitem20mA, motor0,5 A, impulsy50 ms; ruch i kierunek sprawdzone |
| 12 | LEARN, SWEEP, FRICTION, CYCLE, THERMAL | Powtarzalny zakres bez dociskania do ograniczników; ustalone limity robocze |
| 13 | LOGGER podczas objawu i korelacja RPM | Kompletne okno przed i po zdarzeniu; zapis freeze-frame i warunków próby |

## Odbiór niezależności zabezpieczeń

1. Odłącz MCU, wymuś PWM=HIGH: bez fizycznego ARM napęd pozostaje wyłączony.
2. Zatrzymaj task bezpieczeństwa przy aktywnym PWM: monostable wyłącza zezwolenie w50–150 ms. OC nadal działa niezależnie i znacznie szybciej.
3. Wstrzyknij do I_FILT napięcie poniżej LOW i powyżej HIGH. Zmierz PWM_OUT oraz ENA/ENB. Cel od utrzymanego przekroczenia do wyłączenia bramki: <20 µs. Sprawdź oba znaki i kilka temperatur.
4. Włóż wtyk LOGGER podczas TEST na sztucznym obciążeniu: PERMIT znika, żadne wyjście ECU nie otrzymuje napięcia mostka.
5. Odłącz BUSY, zatrzymaj I²C, wyjmij SD: ruch ustaje; fabryczny tor LOGGER pozostaje połączony.
6. Przytrzymaj ARM przed włączeniem zasilania: po ustąpieniu resetu nie może pojawić się nowe zbocze uzbrajające. Sprawdź układ debounce.
7. Sprawdź ciągłość TEST–LOGGER we wszystkich pozycjach przekaźników. Wspólnej masy nie nazywaj izolacją galwaniczną.
8. Przerwij każdą linię nadzoru i zasilanie każdego bloku safety oddzielnie; udokumentuj zachowanie. Projekt nie deklaruje odporności na dowolną pojedynczą awarię ani SIL/ASIL.

## Kalibracja

Źródło i miernik referencyjny: sensory0/0,5/2,5/5 V; motor/VBAT0/5/12/16 V oraz−5 V, jeśli źródło pozwala. Prąd0,±0,5,±1,±2 A. Zapisuj wskazania miernika, nie tylko nastawy zasilacza. Dopasuj gain i offset całego toru, osobno dla banków. Firmware A ma jedną tablicę gain/offset: przed zmianą banku musi być wykazana zgodność obu torów w kryterium błędu; w przeciwnym wypadku potrzebne osobne profile kompilacji/sesje. Nie stosuj jednego dopasowania do dwóch różnych, niesprawdzonych banków.

Nominalny LSB: ADC305,18µV; sensor311µV; motor1,239 mV; prąd1,221mA. Rozdzielczość nie oznacza dokładności. Uwzględnij R_IN ADC, rezystory, offset, błąd wzmocnienia, shunt i TCR, masę i temperaturę. Docelowe kryteria: sensor≤10 mV, motor≤1%, prąd≤2% pełnego używanego zakresu po kalibracji. Jeśli ich nie osiągasz, zapisz rzeczywisty błąd i nie wyciągaj wniosków o mniejszych zmianach.

## Przepustowość

Startuj od 2 kS/s i sprawdź osiem różnych napięć na kanałach. To wykryje błędne powtarzanie kanałów przy nieprawidłowej ramce SPI. Następnie podnieś częstotliwość i zmierz CONVST/BUSY/CS na analizatorze, równocześnie zapisując SD, CAN i TC przez minimum 30 min. Kryterium: zeroGAP/CRC/drop, zmierzony jitter i raport max_dt.

Wersja A używa ośmiu16-bitowych transakcji SPI w hardware mode. Narzut ESP-IDF może uniemożliwić20 kS/s. Nie obiecujemy tej częstotliwości bez odbioru. Przy2 kS/s i PWM1 kHz rejestrujesz trendy, a nie wierny kształt impulsów. Przed użyciem do oceny PWM wybierz dostateczne, pomiarowo potwierdzone próbkowanie lub równoległy oscyloskop.

Przewidziane rozszerzenie: AD7606B software mode, jedna128-bitowa transakcja, SDI naGPIO2; kierunek INA przeniesiony do ekspandera i zmieniany przy wyłączonym PWM. To wymaga osobnej rewizji połączeń i sterownika. Alternatywnie mały kontroler akwizycji/CPLD. Zmiana samego ESP32 nie naprawi nieoptymalnego ramkowania.

## Co wymaga rzeczywistego sprzętu

* Identyfikacja obudów konektorów OEM i rewizji Waveshare.
* Ustawienie i pomiar OVP na zakupionym EVM oraz tolerancji komparatorów.
* Layout PCB, temperatury, przepięcia regeneracyjne, testy EMC/automotive.
* Kompilacja ESP-IDF, próby integracyjne, pomiar jittera i latency SD.
* Profil konkretnego zaworu: polaryzacja, punkty pozycji, prądy, czasy i temperatury.

W pakiecie są schematy blokowe/połączeń oraz BOM, ale nie routowana PCB ani Gerbery. Źródła firmware mają `EGR_HARDWARE_ACCEPTED=0` w `commissioning.h` i wyłączone `CONFIG_EGR_ACTIVE_TEST`. Zmień obie blokady dopiero po odbiorze oraz wpisaniu zmierzonych współczynników do profilu. To nie zastępuje fizycznego ARM.
