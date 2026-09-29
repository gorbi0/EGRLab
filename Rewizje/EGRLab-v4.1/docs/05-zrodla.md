# Źródła techniczne v4

Sprawdzanie projektu:22.09.2026. Wartości elementów, topologia i procedury są projektem EGRLab, nie specyfikacją producenta samochodu. Odbiór fizycznego egzemplarza pozostaje wymagany.

| Źródło producenta | Zastosowanie |
|---|---|
|[AD7606B Rev.B](https://www.analog.com/media/en/technical-documentation/data-sheets/AD7606B.pdf)|Tabela9 piny, rejestry, software mode, zakresy iRIN|
|[INA240-Q1](https://www.ti.com/lit/ds/symlink/ina240-q1.pdf)|Różny pinoutSOIC/TSSOP, gainA2, common-mode, REF|
|[TPS3808](https://www.ti.com/lit/ds/symlink/tps3808.pdf)|Osobny reset, prógG33, CTNC20ms|
|[CD74HC123](https://www.ti.com/lit/ds/symlink/cd74hc123.pdf)|Dominujący reset, CEXT/REXT, retrigger|
|[HC14](https://www.ti.com/lit/ds/symlink/sn74hc14.pdf), [HC74](https://www.ti.com/lit/ds/symlink/sn74hc74.pdf), [HC08](https://www.ti.com/lit/ds/symlink/sn74hc08.pdf)|Piny, logika3,3V iARM|
|[TLV1702-Q1](https://www.ti.com/product/TLV1702-Q1)|Otwarte wyjścia komparatorów|
|[ADR4525](https://www.analog.com/media/en/technical-documentation/data-sheets/ADR4520_4525_4530_4533_4540_4550.pdf)|Niezależne odniesienie okna5V_A|
|[LM74800EVM-CD instrukcja](https://www.ti.com/lit/ug/slvubu3a/slvubu3a.pdf), [LM7480-Q1](https://www.ti.com/lit/ds/symlink/lm7480-q1.pdf)|J6cutoff, fabryczne37,5V, prógOV i tolerancja, tor5A|
|[TPS2553](https://www.ti.com/lit/ds/symlink/tps2553.pdf)|ZalecanyRILIM15…232kΩ, pinySOT23|
|[TBD62083APG](https://toshiba-semicon-storage.com/info/TBD62083APG_datasheet_en_20160511.pdf?did=29893&prodName=TBD62083APG)|SterownikcewekDMOS, wejście2,5V, pinyDIP18|
|[MCP23X17](https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ProductDocuments/DataSheets/20001952C.pdf), [uwaga Microchip oGPA7/GPB7](https://support.microchip.com/s/article/GPA7---GPB7-Cannot-Be-Used-as-Inputs-In-MCP23017)|Piny/porty. A7/B7 pozostawione jako wyjścia; strona wsparcia zwracała błąd odczytu, nie przypisujemy jej dodatkowych szczegółów erraty|
|[Pololu1451](https://www.pololu.com/product/1451), [VNH5019](https://www.st.com/resource/en/datasheet/vnh5019a-e.pdf)|Carrier, VDDpull-upówEN i mostek|
|[TracoTSR2](https://www.tracopower.com/products/tsr2.pdf)|Zakresy przetwornic|
|[MAX31856](https://www.analog.com/media/en/technical-documentation/data-sheets/MAX31856.pdf)|Temperatury, konfiguracja i błędy|
|[TCAN1051-Q1](https://www.ti.com/product/TCAN1051-Q1)|WariantV zVIO, silent mode|
|[WaveshareDEV-KIT](https://www.waveshare.com/wiki/ESP32-S3-DEV-KIT-N8R8), [schemat rodziny](https://files.waveshare.com/wiki/ESP32-S3-DEV-KIT-N8R8/ESP32-S3-DEV-KIT-N8R8-schematic.pdf)|Weryfikacja faktycznej rewizji; ponowny odczyt wiki zwrócił403. SchematN8R8 nie dowodzi identyczności każdej rewizjiN32R16|
|[ESP32-S3-WROOM-2](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-2_datasheet_en.pdf)|Pamięci i dostępnośćGPIO modułu|
|[ESP-IDFv5.4.3](https://docs.espressif.com/projects/esp-idf/en/v5.4.3/esp32s3/index.html), [źródła tego tagu](https://github.com/espressif/esp-idf/tree/v5.4.3)|API i rzeczywisty toolchain kompilacji|

Dane o aucie pochodzą od użytkownika i z wcześniejszych materiałów projektu. Nie potwierdzono nowym źródłem OEM konkretnegoVIN: polaryzacji5/6, limitów prądowo-termicznych28410-2A850, fabrycznychCANID/RPM ani progówP0404 danej kalibracjiECU. Mapę ustala pomiar. Progi triggerów nie są progamiECU. Manual innych aut zD4FD służy hipotezom; nie uprawnia do grzania zaworu do100°C.
