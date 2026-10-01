# P05-R3 a pozostałe moduły i firmware

*R3 (1.10.2026, format S1): połączenia z P02 R4, P03 R6 i P04 przez J_BP1/J_BP2 i płytkę połączeń P12 zamiast B2B i wiązek; firmware i sekwencja startu bez zmian.*

*R2 (29.09.2026): dopisane czasy z karty AD7606B Rev. B, kalibracja w firmware (P5-08) i budżet pojemności 5V_SYS (P5-07). CH7 mierzy akumulator auta (VBAT_SENSE, P02 R4 J11.1).*

Nie zmieniono plików v6.1-rc1 ani P03. Paczka zawiera kopie użyte do porównania i hashe. Poniższe punkty są warunkami integracji, a nie stwierdzeniem, że bieżący firmware już je spełnia.

## Rozruch

W `reference/board.c` około linii253 RESET ma20µs, potem jest tylko10ms oczekiwania. Dokumentacja [AD7606B Rev.B, tabela3, przypis2](https://www.analog.com/media/en/technical-documentation/data-sheets/AD7606B.pdf) wymaga przy pierwszym RESET, aby suma czasu od załączenia i ustalania układu przekroczyła2s. Konserwatywna zmiana dla pierwszego uruchomienia to2100ms po pełnym resecie, przy stabilnym zasilaniu P05.

1. Połączyć masy i zasilić P05. MEAS_EN=0, CS=1, CONVST=0. Napęd pozostaje zablokowany.
2. Potwierdzić stabilne5VA/3V3 oraz DAQ_OK. W tej rewizji DAQ_OK idzie do P04; sam pin nie potwierdza gotowości ADC.
3. Między stabilnym AVCC/VDRIVE a resetem **≥10ms** (karta Rev. B, s. 27). Pełny RESET≥3µs (istniejące20µs spełnia ten warunek); gotowość po 253µs. Po pierwszym załączeniu odczekać2100ms od zwolnienia RESET. Nie wykonywać SPI, jeśli P05 nie ma zasilania.
4. Odczyt/zapis/odczyt kontrolny konfiguracji, zakresów, oversamplingu i kolejności kanałów. Błąd oznacza `adc_config_ok=false`, brak wielkości fizycznych i brak zgody TEST.
5. Dopiero wtedy MEAS_EN=1. Odczekać co najmniej20ms na zadziałanie/stabilizację przekaźników przed zerowaniem lub oceną próbek. Mierzyć ten czas w odbiorze.
6. Zastosować kalibrację odpowiadającą bankowi, adapterowi, zakresom i pozycji AUX. Po zmianie pozycji SW1 zatrzymać pomiar i zmienić konfigurację; P05 nie odczytuje elektrycznie położenia SW1.

Po zaniku DAQ_OK wymagane jest zatrzymanie akwizycji i unieważnienie konfiguracji ADC. Powrót napięcia **nie** oznacza samoczynnego powrotu do TEST. Do czasu osobnego wdrożenia i testów obsługi brownoutu przyjąć ręczny restart sesji/CORE po każdym zaniku zasilania P05. Nie traktować istniejącego `adc_config_ok` jako wiecznego stanu od startu. Utrata heartbeat rozbraja P04; przed ponownym ruchem użytkownik naciska ARM.

## Tempo i dane

Bazowy Kconfig ustawia SPI ADC na1MHz. Sam transfer128bit zajmuje128µs; przy10kSPS okres wynosi100µs, więc1MHz nie wystarcza. Pierwsze uruchomienie:1MHz i do2kSPS. Docelowo kwalifikować4MHz, maksymalne opóźnienia SPI/GPIO i zapis SD/PSRAM pod obciążeniem. Przy4MHz transfer trwa32µs plus BUSY (do około9,9µs dlaOS×8) i narzut programu. To budżet, nie dowód osiągnięcia10kSPS. Zweryfikować generator CONVST, zliczanie próbek i brak nakładania odczytów; ewentualna zmiana opóźnienia próbkowania MISO wymaga pomiarów na końcu bufora CORE.

Rejestrować surowe kody, zakresy, `config_id`, bank i zdarzenia błędów/zmian konfiguracji. Nie zapisywać „ładnych” napięć przy nieważnej konfiguracji. CH6 nie zawiera prądu. Pomiary MCP3201 P06/P07 pozostają osobnym strumieniem. Profil AUX HI/LO i dwupunktowa kalibracja muszą znaleźć się w metadanych.

## Kalibracja

Offset i wzmocnienie kalibrować **w firmware**, nie w rejestrach AD7606B. CHx_OFFSET obejmuje tylko ±128LSB, a kompensacja wzmocnienia działa dla rezystancji szeregowej do 65kΩ (karta s.31–32). Offsety przewidziane w `PROJEKT.md` przekraczają ±128LSB na zakresach ±5 i ±2,5V, a zastępcze rezystancje źródeł P05 (75–100kΩ: 300k∥100k, 100k, 499k∥100k) przekraczają 65kΩ. Kasowanie offsetu rezystorem na VxGND (karta s.24) nie daje stałego dopasowania przy odczepach w adapterach i AUX przełączanym SW1.

## Budżet pojemności 5V_SYS (P5-07)

**1.10.2026 (R3): budżet niżej jest nieaktualny.** Po P02 R4 i z P06 w formacie S1 szyny 5 V mają razem ok. 986 µF wobec 600 µF dopuszczalnych dla TSR 2-2450 (P05 C1 i P06 C3 po 470 µF za 1 Ω; raport `Plytki/P12-przygotowanie`, gałąź `p12-przygotowanie`). Do decyzji użytkownika — README, punkty otwarte.

TSR 2-2450 dopuszcza 600µF obciążenia pojemnościowego. Suma kondensatorów na szynach 5V w pakietach P00–P11 (stan 27.09) to ok.538µF, z tego 470µF to C1 w P05; bez P01 i bez kondensatorów modułu Waveshare. R1 1Ω i miękki start TSR ograniczają prąd ładowania C1 (ok.0,5A przy narastaniu 5V w 5ms). Przy pierwszym uruchomieniu kompletu sprawdzić, że 5V_SYS narasta bez restartów czkawkowych. Nie wpinać taśmy J_BP1 pod napięciem: 5 V na C1 przez 1 Ω to udar do 5 A. Budżet trzeba przeliczyć dla P02 R4 (zasilanie z pakietu 4S) — to poza tą paczką.

## Zależności

- P02 R4: 5V_SYS (J_BP 2/4/6 → P12 → J_BP1.2/4) utrzymywane w roboczym zakresie przy obciążeniu P05 i rozruchu C1; VBAT_SENSE z J_BP.20 → J_BP1.10. 3V3_IO nie wchodzi na P05.
- P03 R6: DAQ przez J_BP2 (te same numery pinów po obu stronach P12), Ioff w buforach CORE. Na P03 J_BP2.16/17/19/20 to PFAIL_N i 5V_SYS, na P05 16 i 20 to GND — P12 nie może ich łączyć. P05 ma dodatkowy bufor BUSY; uwzględnić jego opóźnienie, a w stosie zmierzyć SCLK/MISO na końcu taśm (krok 17 ODBIOR).
- P04 (wariant pełny): DAQ_OK z J_BP1.6 przez P12; w LOGGER bez odbiorcy. Niski DAQ_OK kasuje zgodę sprzętową; wysoki nie potwierdza kalibracji.
- P11 i adaptery: zachować rezystory przy źródle, odłączanie banków i wspólne odniesienie GND. P05 nie zastępuje rozdziału TEST/LOGGER.
- P06/P07: tory prądu bez zmian. P07 nadal HOLD dla wariantu BTS7960.
- MAX31856/temperatury są poza P05; ich kupne moduły zachowują złącza.

Brak patcha automatycznie wprowadzanego do aktywnego firmware jest celowy: prace nad P03 mogą zmienić ten kod. Wymagania rozruchu i brownoutu należy wdrożyć oraz przetestować na aktualnej gałęzi integracyjnej przed połączeniem z napędem.
