# Źródła techniczne

Wartości rezystorów, podział funkcji i procedury są projektem własnym — **nie są zaleceniem producenta samochodu**. Podzespoły i zakresy potwierdzano w poniższych źródłach pierwotnych przy powstawaniu v1 (sprawdzane 2026-09-21). W v2 lista została przeniesiona i przycięta o elementy, które wypadły z projektu; **nie odpytywałem tych adresów ponownie**. Dokumenty producenta mają pierwszeństwo przed opisem sprzedawcy przy doborze wariantu.

## Podzespoły

* [Waveshare — porównanie wersji N8R8/N16R8/N32R16V](https://www.waveshare.com/wiki/ESP32-S3-DEV-KIT-N8R8) — moduł WROOM-2, OPI 32 MB, PSRAM 16 MB, GPIO 35–37 jako NC.
* [Waveshare — schemat rodziny](https://files.waveshare.com/wiki/ESP32-S3-DEV-KIT-N8R8/ESP32-S3-DEV-KIT-N8R8-schematic.pdf) — UART, USB, zasilanie, RGB na GPIO38. Nie zastępuje fizycznej identyfikacji rewizji Twojej płytki.
* [Espressif ESP32-S3-WROOM-2 datasheet](https://documentation.espressif.com/esp32-s3-wroom-2_datasheet_en.html) — GPIO 47/48 na 1,8 V, wyprowadzenia modułu.
* [ESP-IDF 5.4.3](https://documentation.espressif.com/esp-idf/en/v5.4.3/esp32s3/index.html) — odniesienie API; wersję toolchainu przypnij przy kompilacji.
* [AD7606B datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/ad7606b.pdf) — jednoczesne próbkowanie, R_IN 5 MΩ, ±10 V, osiem ramek 16-bit dla DOUTA w hardware mode, **rejestry i zakresy per kanał w software mode**.
* [ADI AN-2011](https://www.analog.com/en/resources/app-notes/an-2011.html) — różnice hardware/software mode.
* [INA240A2-Q1](https://www.ti.com/product/INA240-Q1/part-details/INA240A2EDRQ1) — wzmocnienie 50, zakres common-mode −4…80 V.
* [TLV1702-Q1](https://www.ti.com/product/TLV1702-Q1) — komparator okna prądu, wyjścia open collector.
* [TPS3808](https://www.ti.com/product/TPS3808) — supervisor 3V3_IO.
* [VNH5019 datasheet](https://www.st.com/resource/en/datasheet/vnh5019a-e.pdf) — tabela prawdy EN/PWM, absolutne maksimum 41 V.
* [Pololu 1451](https://www.pololu.com/product/1451) — gotowy moduł VNH5019, obwód VDD/EN.
* [Traco TSR 2](https://www.tracopower.com/products/tsr2.pdf) — przetwornice 2 A, zakres wejść 6,5–36 V.
* [TPS2553](https://www.ti.com/product/TPS2553) — ogranicznik prądu zasilania czujnika.
* [MAX31856](https://www.analog.com/media/en/technical-documentation/data-sheets/MAX31856.pdf) — typ K, filtr 50 Hz, rejestry i flagi błędów.
* [TCAN1051-Q1](https://www.ti.com/product/TCAN1051-Q1) — wariant z VIO, tryb silent.
* [LM74800EVM-CD](https://www.ti.com/tool/LM74800EVM-CD) i [LM7480-Q1](https://www.ti.com/lit/ds/symlink/lm7480-q1.pdf) — **opcjonalne** aktywne odcięcie wejścia; w v2 wersja bazowa używa P-MOS i TVS.

## Dane o samochodzie

* Manual GDS dla Hyundaia i40 VF 2013 z tym samym D4FD — definicja P0404: aktuator całkowicie otwarty lub zamknięty ponad 4 s, czas diagnozy 4,4 s, progi obejmują **wysoką temperaturę silnika aktuatora**, wskazywana przyczyna: obwód silnika aktuatora. Adres w `../../docs/02-learnings-and-tools.md`. To jest źródło, z którego wynika tryb HOT-SOAK.
* Schematy Monolith, Kia Sportage od 2010 (PDF, RU) — obwód EGR na stronach 56–59 PDF, mapa mas D4FD na 36–37, klimatyzacja FATC na 69–70. Stąd pochodzi pinout CUD87 używany jako domyślny w `hardware/profile.template.json`.
* Pomiary własne z naprawy ECV: kompresor Denso 6SE14, cewka sprzęgła 3,8 Ω, solenoid ECV 11 Ω sterowany PWM w sposób ciągły. Stąd bierze się hipoteza H7 i sensowność kanału AUX.

## Czego nie znaleziono

Nie ma publicznie dostępnej dokumentacji OEM, która rozstrzygałaby numerację obudowy złącza dla konkretnego VIN ani charakterystykę prądowo-termiczną zaworu 28410-2A850. **Piny 1/3 jako napęd przyjęto z Twojej dokumentacji**, trójka 4/5/6 jest rozpoznawana pomiarowo. Ogólny opis silnika nie jest źródłem limitów zaworu — limity w profilu pochodzą z ostrożnego LEARN, nie z katalogu.

Portal Kia euro5 GSW jest zablokowany (polski NIP niezarejestrowany w VIES), ASO odmawiają udostępnienia danych, a krążące PDF-y manuala Sportage SL obejmują wyłącznie benzyny 2.0/2.4.

## Rzecz, którą musisz sprawdzić sam przed pierwszym uruchomieniem

**Adresy i układ bitów rejestrów AD7606B w software mode** (`ADC_REG_*` w `firmware/main/board.c`). Zostały spisane z pamięci o rodzinie AD7606B/C, nie skopiowane z otwartego datasheetu w trakcie pisania kodu. Sterownik weryfikuje zapis odczytem i przy niezgodności wraca do hardware mode, więc błąd nie uszkodzi sprzętu — ale zanim uznasz, że software mode „nie działa na Twojej płytce", porównaj te stałe z tabelą rejestrów w datasheecie.
