# Źródła techniczne — sprawdzone 2026-09-21

Wartości proponowanych rezystorów, podział funkcji i procedury są projektem własnym; nie są zaleceniem producenta samochodu. Podzespoły i zakresy potwierdzano w poniższych źródłach pierwotnych. Dokumenty producenta mają pierwszeństwo przed opisem sprzedawcy przy doborze wariantu.

* [Waveshare — porównanie wersji N8R8/N16R8/N32R16V](https://www.waveshare.com/wiki/ESP32-S3-DEV-KIT-N8R8) — moduł WROOM-2, OPI32MB, PSRAM16MB, NC35–37.
* [Waveshare — schemat rodziny](https://files.waveshare.com/wiki/ESP32-S3-DEV-KIT-N8R8/ESP32-S3-DEV-KIT-N8R8-schematic.pdf) — UART,USB,zasilanie iRGBGPIO38; niepodmienia fizycznejidentyfikacji rewizjiN32R16.
* [Espressif WROOM-2 datasheet](https://documentation.espressif.com/esp32-s3-wroom-2_datasheet_en.html) — GPIO47/48 na1,8V i wyprowadzenia modułu.
* [ESP-IDF5.4.3](https://documentation.espressif.com/esp-idf/en/v5.4.3/esp32s3/index.html) — odniesienieAPI; wersjętoolchainuprzypiąćprzykompilacji.
* [AD7606B datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/ad7606b.pdf) — równoczesnepróbkowanie,hardware mode,5MΩ,±10V i8ramek16bitdlaDOUTA.
* [ADI AN-2011](https://www.analog.com/en/resources/app-notes/an-2011.html) — różnicehardware/software mode.
* [INA240A2-Q1](https://www.ti.com/product/INA240-Q1/part-details/INA240A2EDRQ1) — wzmocnienie50, wspólny zakres−4…80V.
* [TLV1702-Q1](https://www.ti.com/product/TLV1702-Q1) — oknoprądu,wyjścia open-collector.
* [VNH5019 datasheet](https://www.st.com/resource/en/datasheet/vnh5019a-e.pdf) — prawdasterowaniaEN/PWM i41V absolutnego maksimum.
* [Pololu1451](https://www.pololu.com/product/1451) — gotowymodułVNH5019 iobwódVDD/EN.
* [LM74800EVM-CD](https://www.ti.com/tool/LM74800EVM-CD) i [LM7480-Q1 datasheet](https://www.ti.com/lit/ds/symlink/lm7480-q1.pdf) — dwaMOSFET-y,reversepolarity,OVP.
* [TracoTSR2](https://www.tracopower.com/products/tsr2.pdf) — zasilaczemodułowe2A,zakreswejść.
* [TPS2553](https://www.ti.com/product/TPS2553) — ogranicznikprąduzasilaniaczujnika.
* [MAX31856](https://www.analog.com/media/en/technical-documentation/data-sheets/MAX31856.pdf) — typK,50Hz,rejestryifault.
* [TCAN1051-Q1](https://www.ti.com/product/TCAN1051-Q1) — wariantVIO,i silent mode.

Nie znaleziono w publicznych źródłach OEM potwierdzonego numerowania wtyczki ani charakterystyki prądowo-termicznej 28410-2A850 dla VIN użytkownika. Pin1/3/4 przyjęto z instrukcji użytkownika;5/6 mierzone. Ogólny opis silnika nie jest źródłem limitów zaworu.
