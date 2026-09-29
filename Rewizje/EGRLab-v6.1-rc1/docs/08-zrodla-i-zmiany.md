# Źródła i istotne korekty

Weryfikacja dokumentacyjna 22.09.2026. Poniższe źródła producentów dotyczą nowych decyzji. Dotychczasowe źródła P01 i obwodów v4.1 zachowano w odpowiednich materiałach referencyjnych.

- [MCP3201 DS21290F](https://ww1.microchip.com/downloads/en/DeviceDoc/21290F.pdf): DIP8, pinout, ramka 16-bit, tryb SPI i przedział próbkowania.
- [MCP1525 DS21653C](https://ww1.microchip.com/downloads/en/devicedoc/21653c.pdf): w **TO92 1=GND, 2=VOUT, 3=VIN**. Inna numeracja niż SOT23.
- [MCP1702 DS22008E](https://ww1.microchip.com/downloads/en/DeviceDoc/22008E.pdf): w TO92 1=GND, 2=VIN, 3=VOUT; kondensatory regulatora.
- [MCP6022](https://ww1.microchip.com/downloads/en/devicedoc/21060l.pdf): podwójny wzmacniacz; stosowany lokalnie jako bufor, a w DRIVE dodatkowo do progu OC.
- [74LVC125A Nexperia, Rev12](https://assets.nexperia.com/documents/data-sheet/74LVC125A.pdf): Ioff i piny OE; istotny dokładny producent części.
- [MCP23017 DS20001952](https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ProductDocuments/DataSheets/MCP23017-Data-Sheet-DS20001952.pdf): ograniczenia GPA7/GPB7; v5 używa GPA4.
- [Waveshare N32R16V](https://docs.waveshare.com/ESP32-S3-DEV-KIT-N8R8): GPIO47/48 1,8 V, dlatego pozostają niewykorzystane.
- [AD7606B](https://www.analog.com/media/en/technical-documentation/data-sheets/AD7606B.pdf): jeden CONVST na pin9, WR na pin10; zachowana poprawka v4.1.
- [INA240-Q1](https://www.ti.com/lit/ds/symlink/ina240-q1.pdf): tor odniesienia, lokalny shunt/Kelvin; w v5 oba REF są na buforowanym odniesieniu 2,5 V.
- [TLC555](https://www.ti.com/lit/ds/symlink/tlc555.pdf): generator stanowiskowy P00 zasilany 3,3 V; wersja CMOS w DIP8.
- [DEUTSCH DT](https://www.te.com/content/dam/te-com/documents/industrial-and-commercial-transportation/global/dt-inline-catalog.pdf): klucze A/B/C, styki size16 i korpusy kablowe. Detekcja wsunięcia wtyku wymaga oddzielnej mechaniki.

Względem MOD0.1: doprecyzowano granice/numery złączy, lokalne zasilanie ADC i gotowość; dodano lokalne OC i zatrzask, przeniesiono przycisk MARK, zrezygnowano z przekaźnika KCUR. Sprawdzenie nowych torów ujawniło potrzebę rozdzielenia lokalnych nazw sieci P01, usunięcia starych dzielników OC i jawnego przypisania supervisora CORE. Nowa netlista jest nadrzędna wobec historycznych arkuszy S1.

Względem wcześniejszych uwag Opus zachowano FIFO 256 KiB, ostrzeżenia dla niepełnych starych metadanych, testowanie rzeczywistych połączeń interlocku i opis konieczności ponownego ARM. Martwy czas kierunku wynosi 5 ms **po** wyłączeniu mostka i potwierdzeniu nowych INA/INB.

Granice odbioru: brak sprzętu do prób, brak certyfikacji automotive, brak layoutu i DRC; wykonano ERC importu KiCad, patrz stabilizacja/STATUS.md. Wykonano testy struktury danych połączeń oraz programu, a nie symulację uszkodzeń wszystkich półprzewodników. Czasy SPI, analogowe pasmo, termikę i odporność zasilania ma potwierdzić etapowy odbiór.
