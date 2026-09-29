# P05-R1 a pozostałe moduły i firmware

Nie zmieniono plików v6.1-rc1 ani P03. Paczka zawiera kopie użyte do porównania i hashe. Poniższe punkty są warunkami integracji, a nie stwierdzeniem, że bieżący firmware już je spełnia.

## Rozruch

W `reference/board.c` około linii253 RESET ma20µs, potem jest tylko10ms oczekiwania. Dokumentacja [AD7606B Rev.B, tabela3, przypis2](https://www.analog.com/media/en/technical-documentation/data-sheets/AD7606B.pdf) wymaga przy pierwszym RESET, aby suma czasu od załączenia i ustalania układu przekroczyła2s. Konserwatywna zmiana dla pierwszego uruchomienia to2100ms po pełnym resecie, przy stabilnym zasilaniu P05.

1. Połączyć masy i zasilić P05. MEAS_EN=0, CS=1, CONVST=0. Napęd pozostaje zablokowany.
2. Potwierdzić stabilne5VA/3V3 oraz DAQ_OK. W tej rewizji DAQ_OK idzie do P04; sam pin nie potwierdza gotowości ADC.
3. Pełny RESET≥3µs (istniejące20µs spełnia ten warunek). Po pierwszym załączeniu odczekać2100ms od zwolnienia RESET. Nie wykonywać SPI, jeśli P05 nie ma zasilania.
4. Odczyt/zapis/odczyt kontrolny konfiguracji, zakresów, oversamplingu i kolejności kanałów. Błąd oznacza `adc_config_ok=false`, brak wielkości fizycznych i brak zgody TEST.
5. Dopiero wtedy MEAS_EN=1. Odczekać co najmniej20ms na zadziałanie/stabilizację przekaźników przed zerowaniem lub oceną próbek. Mierzyć ten czas w odbiorze.
6. Zastosować kalibrację odpowiadającą bankowi, adapterowi, zakresom i pozycji AUX. Po zmianie pozycji SW1 zatrzymać pomiar i zmienić konfigurację; P05 nie odczytuje elektrycznie położenia SW1.

Po zaniku DAQ_OK wymagane jest zatrzymanie akwizycji i unieważnienie konfiguracji ADC. Powrót napięcia **nie** oznacza samoczynnego powrotu do TEST. Do czasu osobnego wdrożenia i testów obsługi brownoutu przyjąć ręczny restart sesji/CORE po każdym zaniku zasilania P05. Nie traktować istniejącego `adc_config_ok` jako wiecznego stanu od startu. Utrata heartbeat rozbraja P04; przed ponownym ruchem użytkownik naciska ARM.

## Tempo i dane

Bazowy Kconfig ustawia SPI ADC na1MHz. Sam transfer128bit zajmuje128µs; przy10kSPS okres wynosi100µs, więc1MHz nie wystarcza. Pierwsze uruchomienie:1MHz i do2kSPS. Docelowo kwalifikować4MHz, maksymalne opóźnienia SPI/GPIO i zapis SD/PSRAM pod obciążeniem. Przy4MHz transfer trwa32µs plus BUSY (do około9,9µs dlaOS×8) i narzut programu. To budżet, nie dowód osiągnięcia10kSPS. Zweryfikować generator CONVST, zliczanie próbek i brak nakładania odczytów; ewentualna zmiana opóźnienia próbkowania MISO wymaga pomiarów na końcu bufora CORE.

Rejestrować surowe kody, zakresy, `config_id`, bank i zdarzenia błędów/zmian konfiguracji. Nie zapisywać „ładnych” napięć przy nieważnej konfiguracji. CH6 nie zawiera prądu. Pomiary MCP3201 P06/P07 pozostają osobnym strumieniem. Profil AUX HI/LO i dwupunktowa kalibracja muszą znaleźć się w metadanych.

## Zależności

- P02:5V_SYS utrzymywane w roboczym zakresie przy obciążeniu P05 i rozruchu C1; sprawdzenie wspólnego budżetu prądowego. LV05.3 na P05 jest tylko pomiarem serwisowym.
- P03: B2B bez taśmy, Ioff w buforach CORE i wykonana kontrola mechaniczna. P05 ma dodatkowy bufor BUSY; uwzględnić jego opóźnienie w pomiarach.
- P04: DAQOK/J5 pin1 sygnał,2GND,4klucz. Niski DAQ_OK kasuje zgodę sprzętową; wysoki nie potwierdza kalibracji.
- P11 i adaptery: zachować rezystory przy źródle, odłączanie banków i wspólne odniesienie GND. P05 nie zastępuje rozdziału TEST/LOGGER.
- P06/P07: tory prądu bez zmian. P07 nadal HOLD dla wariantu BTS7960.
- MAX31856/temperatury są poza P05; ich kupne moduły zachowują złącza.

Brak patcha automatycznie wprowadzanego do aktywnego firmware jest celowy: prace nad P03 mogą zmienić ten kod. Wymagania rozruchu i brownoutu należy wdrożyć oraz przetestować na aktualnej gałęzi integracyjnej przed połączeniem z napędem.
