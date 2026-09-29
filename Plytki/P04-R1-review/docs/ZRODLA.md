# Źródła pierwotne i identyfikowalność

Sprawdzano 25.09.2026. BOM wskazuje MPN, nie tylko rodzinę. Niepotwierdzone cechy mechaniczne pozostają na liście przymiarki, a nie jako PASS.

| Część | Dokument | Zastosowanie |
|---|---|---|
| CD74HC123E | [TI SCHS142F](https://www.ti.com/lit/ds/symlink/cd74hc123.pdf) | Pinout, wyzwalanie/reset, połączenie Cext, warunek 5 V dla wzoru |
| SN74HC14N | [TI SCLS085L](https://www.ti.com/lit/ds/symlink/sn74hc14.pdf) | Schmitt, progi zależne od VCC, pinout |
| SN74HC74N | [TI](https://www.ti.com/lit/ds/symlink/sn74hc74.pdf) | Asynchroniczne PRE/CLR, zbocze zegara |
| SN74HC08N | [TI](https://www.ti.com/lit/ds/symlink/sn74hc08.pdf) | Bramki i układ wyprowadzeń; symbol z kształtem 74LS08 jest podpisany i zamawiany jako HC08 |
| 74LVC125AD | [Nexperia](https://assets.nexperia.com/documents/data-sheet/74LVC125A.pdf) | Ioff i poziomy; tylko wskazana rodzina/producent |
| MCP100-315DI/TO | [Microchip DS11187F](https://ww1.microchip.com/downloads/en/DeviceDoc/11187f.pdf) | Bondout D, próg i opóźnienie resetu |
| 2N3904BU | [onsemi 2N3903/D](https://www.onsemi.com/pdf/datasheet/2n3903-d.pdf) | E/B/C i praca jako sink małego prądu |
| WIMA MKS2 1µF 63V | [WIMA MKS2](https://www.wima.de/wp-content/uploads/media/e_WIMA_MKS_2.pdf) | PET, gabaryt i raster |
| Vishay K104K15X7RF53H5 | [Vishay K series](https://www.vishay.com/docs/45171/kseries.pdf) | Odsprzęganie i lokalny footprint |
| Würth IDC6 | [61200621621](https://www.we-online.com/components/products/datasheet/61200621621.pdf) | Raster, otwory i powłoka kontaktu |
| Mini-Fit 6p | [Molex 39299069](https://www.molex.com/en-us/products/part-detail/39299069) | Au, pionowe, kołki, PCB 1,6 mm |
| Mini-Fit 10p | [Molex 39299109](https://www.molex.com/en-us/products/part-detail/39299109) | Au, pionowe, kołki |

Biblioteki footprintów KiCad 10.0.6 są skopiowane lokalnie. Zmiana IDC: otwór 1,2 mm, pad 1,9 mm. Adapter SO14 oraz footprint kondensatora K15 pochodzą z wcześniejszego pakietu P02; ich pliki wejściowe są zahashowane. Nie jest to potwierdzenie pomiaru fizycznych części.

Karta [Würth 10p 61201021621](https://www.we-online.com/components/products/datasheet/61201021621.pdf) nie była dostępna przy pobieraniu. MPN dobrano z tej samej serii, ale jego pełny rysunek pozostaje do potwierdzenia przed zwolnieniem PCB. Nie podmieniono go potajemnie złączem 6p. Podobnie dopasowanie Mini-Fit A2 wymaga sprawdzenia kołków/ogonów z rysunkiem konkretnej dostawy.

Wiązki i styki Mini-Fit żeńskie wykorzystują tę samą rodzinę co P02-R2 (39-01-2040 / 39-00-0074). Zakupy akcesoriów rozdzielono według właściciela wiązki, aby nie liczyć ich dwukrotnie.
