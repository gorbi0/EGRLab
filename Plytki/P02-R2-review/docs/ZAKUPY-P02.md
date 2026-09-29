# P02-R2 — dobór zakupowy i zmiany względem R1

Pełna lista elektroniczna: BOM.csv (referencje, MPN, ilości, footprinty i źródła). Stare zestawienie zapasów z24.09 zachowano wyłącznie w reference/R1-docs/ZAKUPY-P02.md — nie jest bieżącym stanem magazynu.

| Zmiana / pozycja | Ilość | Wybrana część |
|---|---:|---|
| R5 |1| MF0207FTE-330R, 330Ω1% |
| R6 |1| MBB0207VD3012BC100,30,1kΩ0,1%,25ppm/K |
| R7/R10 |2| MBB0207VD1002BC100,10kΩ0,1%,25ppm/K |
| R9 |1| MBB0207VD3832BC100,38,3kΩ0,1%,25ppm/K |
| R8/R11 |2| MF0207FTE-1M,1MΩ1% |
| R18/R19 |2| MF0207FTE-10K,10kΩ1% |
| R20 |1| PR02000201001JA100,1kΩ2W5% |
| C14/C15 |2| K103K15X7RF53H5,10nF X7R, raster5mm |
| C16 na adapter |1| GRM21BR71H104KA01L,100nF50V X7R0805 |
| F1 wkładka |1| Schurter0001.2507,T2A,5×20,300VDC,1500A |
| J3–J10 |8| Molex39-29-6048,4p pionowe Au, bez zatrzaskowych kołkówPCB |
| J11 |1| Molex39-29-6148,14p pionowe Au, bez zatrzaskowych kołkówPCB |
| WtykiLV |8| Molex39-01-2040,4p; potwierdzić klucze przy przymiarce |
| WtykVSENSE |1| Molex39-01-2140,14p; obsadzone tylko1/2 |
| Styki do tych9 wtyków |34 + zapas| Molex39-00-0074 Au,AWG18–24; użyćAWG22/24 o izolacji zgodnej z kartą |
| WtykVMOTOR |1| Phoenix GMSTB2,5/3-ST-7,62,1767012; zakup wiązkiP07 wstrzymany |
| OprawkiF1–F4 |4| PTF78, istniejące footprinty |
| WiązkaSUPPLY |1|2×2,5mm² /200mm; P02 lutowane, P01 wtykMSTB1757022 |
| WiązkaPSUOK |1|taśma6×AWG28 /150mm; P02 lutowana, P04 IDC6 klucz5 |
| WiązkaR17 |1|2×AWG20 /200mm; oba końce lutowane do właściwych zacisków |
| Obejmy banku + podstawa/osłona |3+1|izolujące, dopasowane do35mm puszek i obudowy; poza PCB |

Kodów MBB użyto zgodnie z tabelą zamówieniową producenta. Nie oznacza to potwierdzenia dostępności pojedynczych sztuk. Zamiennik wymaga zachowania0,1%,≤25ppm/K i pasującego korpusu; nie zamieniać na1% bez powtórzenia analizy.

**Otwarte przed zatwierdzeniem zakupów/PCB:** F2/F3 (F1A5×20) oraz F4 (F100mA5×20). Nie znalazłem potwierdzonego MPN zachowującego wszystkie wymagania w sprawdzonych pierwotnych kartach. Nie przypisuję wartości DC z samego nadruku250VAC. Rozwiązanie: uzyskać potwierdzenie producenta dla konkretnej wkładki przy32VDC i spodziewanym prądzie zwarciowym albo zatwierdzić zmianę oprawki/charakterystyki w osobnej poprawce. F1 jest już wybrany; jego9,2A²s to wartość **typowa topienia**, nie gwarantowane całkowite I²t wyłączenia. Koordynacja impulsowa z bankiem i F2/F3 wymaga odbioru.

Źródła: [Molex4p](https://www.molex.com/en-us/products/part-detail/39296048), [Molex14p](https://www.molex.com/en-us/products/part-detail/39296148?display=pdf), [stykiAu](https://www.molex.com/en-us/products/part-detail/39000074), [SchurterSPT](https://www.schurter.com/en/datasheet/typ_SPT_5x20.pdf), [VishayMBB](https://www.vishay.com/doc?28767=). Wymiarowa zgodność gniazd z lokalnym footprintem jest do fizycznej przymiarki; nie zamawiać wariantów z dodatkowymi kołkami zatrzaskowymi.
