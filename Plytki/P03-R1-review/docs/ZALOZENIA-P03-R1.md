# P03 CORE — karta założeń schematu i PCB (R1)

25.09.2026 · Claude. Karta spisana po decyzjach użytkownika, razem ze schematem i płytką. Źródła: import pinowy P03 z v6.1-rc1 (`reference/v6.1-P03-import.xml`), BOM v6.1 (`reference/v6.1-P03-BOM.csv`), interfejsy CORE z v6.1 (`reference/v6.1-02-interfejsy-CORE.md`), układ listew DevKitC-1 (`reference/DevKitC-1-headers.md`), rysunek i pinout Adafruit 4682 (`reference/adafruit-4682-*.png`), montaż wiązek z v6.1 (`docs/10-montaz-wiazek.md` w v6.1-rc1). Do recenzji: Astra.

## Rola płytki

P03 to rdzeń EGRLaba: ESP32-S3 (Waveshare ESP32-S3-DEV-KIT-N32R16V) z kartą microSD, ekspanderem MCP23017, dekoderem CS prądu 74HC139 i nadzorem 3V3_CORE (TPS3808). Wszystkie sygnały, które wychodzą z płytki albo na nią wchodzą, przechodzą przez bufory 74LVC125A (Nexperia, Ioff): cztery wejściowe (U11–U14) i trzy wyjściowe (U21–U23). Złącza: DAQ do P05 (bez przewodu), taśmy IDC do P04, P06, P07 (dwie), P08, P09, P10, Mini-Fit 8p do panelu P11 i lutowana wiązka LV03 z P02.

## Decyzje użytkownika (25.09.2026)

1. **P03 CORE jako następna płytka** (kolejność v6.1: P01/P02/P00 → CORE i DAQ z parą B2B).
2. **Listwy modułu Waveshare co 22,86 mm (0,9″)** — rozstaw zmierzony na posiadanym module.
3. **P03 i P05 obok siebie, złącza kątowe krawędź w krawędź** (zamiast pionowej pary z zakładką płytek z v6.1).
4. **microSD = moduł Adafruit 4682** (3 V, bez własnego stabilizatora i translatora).
5. **Format 160 × 120 mm jak P01/P02**, otwory M3 w tych samych narożnikach.
6. **Chip Quik PA0085: dwa rzędy po 3 piny co 15,24 mm.**
7. **CAN: IDC 2 × 3 (6p), klucz na pinie 4, piny 5–6 NC** — box header 2 × 2 nie istnieje, a pozycje sygnałowe zostają jak w v6.1 (1 = CAN_TX, 2 = GND, 3 = CAN_RX).

## Zgodność z v6.1

`src/compare_v61.py` porównuje netlistę R1 z importem v6.1 pin po pinie (piny ESP32 przez numery GPIO → piny listew DevKitC-1, SD przez nazwy funkcji → piny 4682): **310 pinów, 0 różnic**; nowe są tylko pozycje 5–6 złącza CAN (decyzja 7; pozycja 4 to klucz także w v6.1). Dodane części: tylko pola pomiarowe TP1–TP6. ERC 0.

Przeniesione z v6.1 bez zmian i warte pamiętania przy montażu:

- GPIO47/48 nieużywane (w N32R16V domena 1,8 V); 19/20 USB, 43/44 UART zostają dla płytki; 0/3/45/46 pomijane (strapping); 35–37 zajęte przez pamięć.
- **Diodę RGB na GPIO38 odlutować z modułu** (GPIO38 = CS prądu przez 74HC139).
- 3V3 modułu = 3V3_CORE. **3V3_CORE nie łączy się z 3V3_IO** (3V3_IO z LV03 zasila tylko nieużywane wejścia OE# bufora U14).
- Karta SD na SPI3 za buforami (SCLK, MOSI przez U23, MISO przez U11); CS karty wprost z GPIO7 z podciągnięciem 10 k.
- Wejścia gotowości z pull-downem 10 k przy buforze wejściowym (odłączony przewód = 0): R2, R3, R6, R7, R8.
- SCOPE_TRIG przez 330 Ω (R12); MARK z podciągnięciem 10 k i 100 nF (R5, C4); CORE_LINK przez 0 Ω (R14).

## Decyzje projektowe R1 (do recenzji)

| Decyzja | Uzasadnienie |
|---|---|
| **Sporne: USB-C modułu przy górnej krawędzi, antena w głąb płytki** nad strefą bez miedzi (obie warstwy; koniec anteny + 3 mm po bokach + 8 mm za końcem modułu) | Moduł jest prosty, więc tylko jeden koniec może leżeć na krawędzi. Wybrany dostęp do USB (programowanie bez demontażu); Wi-Fi jest tylko w wariancie firmware „wifi”, a zasięg sprawdza odbiór. Alternatywa na R2: M1 obrócony o 180° (antena przy krawędzi, USB w środku płytki) |
| ESP32, SD i antena z dala od P05 | v6.1: analog P05 odsunięty od ESP32, SD i anteny; M1 po lewej, DAQ przy prawej krawędzi |
| **Otwór H5 (155; 38)** poza czterema narożnymi | v6.1: po dwa punkty mocowania każdej płytki blisko złącza B2B; H2 i H5 obejmują J1 z obu stron (ok. 17 mm od środka złącza) |
| **J1 DAQ: ogólny footprint gniazda kątowego 2 × 8** (KiCad PinSocket_2x08_P2.54mm_Horizontal), czoło 0,37 mm przed prawą krawędzią | Część proponowana: Samtec SSW-108-02-G-D-RA lub odpowiednik o tym samym rysunku. **Wysokość rzędów styków nad płytką zależy od konkretnego gniazda i wtyku P05** — różnicę wyrównują dystanse (v6.1: dobrać z rysunków i próbnego zestawienia; złącza i dystanse kupić przed końcowym layoutem) |
| Złącza IDC przy krawędziach, dłuższy bok wzdłuż krawędzi, rząd sygnałowy (piny nieparzyste) do środka płytki | Taśma zagina się po łatwej osi w stronę krawędzi; sygnały bliżej buforów. Klucze wg v6.1 (usunięty pin, nadruk KEY n) |
| **Sporne: klasy ścieżek sygnały 0,30/0,25 mm** (P00/P02: 0,5/0,3), zasilanie 0,6/0,3 mm, 5V_SYS 1,0 mm | Rzędy pinów 2,54 mm (listwy M1, DIP, adaptery) są gęste; 0,30/0,25 mieści jedną ścieżkę między padami. Minimum płytki bez zmian (0,25/0,3) |
| Przy każdym 100 nF zablokowany odcinek 0,6 mm do pinu zasilania i przelotka GND 2,2 mm za padem masy | Krótka pętla odsprzęgania niezależna od autoroutera; przelotka zapewnia dojście obu wylewek (w pierwszym trasowaniu pad masy C5 został odcięty przez ścieżki) |
| Pady GND z pełnym połączeniem do wylewki tam, gdzie DRC zgłosił zagłodzoną termikę | Połączenie pewne elektrycznie; przy lutowaniu tych pinów dłużej grzać (lista w PDF i LAYOUT) |
| **Sporne: wylewki GND zszyte 48 przelotkami 0,8/0,4 mm w siatce 10 mm** (w P02 bez zszycia) | Po trasowaniu obie wylewki mają po ok. 30 drobnych wysp łączonych tylko padami THT; zszycie skraca drogę powrotną magistrali ADC/SPI. Przelotki tylko tam, gdzie obie wylewki mają miejsce, poza obrysami części i strefami |
| Karta microSD przy dolnej krawędzi, moduł na gnieździe 1 × 9 i dwóch dystansach M2.5 (strefy bez miedzi Ø6 mm) | Dostęp do karty z zewnątrz; dystanse przenoszą siłę wkładania karty zamiast lutów listwy |
| J10 LV03: żyły lutowane, kotwa opaski 12,5 mm od lutów; **pas bez miedzi pod opaską** (obie warstwy) | v6.1: brak miedzi przy otworach i pod naciskiem opaski. Uwaga dla P02: tam pas pod opaską nie był wydzielony — do sprawdzenia w recenzji P02 |
| Miedź 2 × 35 µm | Prądy do ok. 0,5 A (5V_SYS modułu); P02 ma 70 µm, bo prowadzi prąd silnika |

## Zgodność z P05 R1 (Astra, 25.09)

P05 R1 powstał na kopii roboczej tego P03 (`Plytki/P05-R1-review/reference/P03-*`). Złącze J1 jest w wydaniu R1 niezmienione względem tej kopii: pozycja pinu 1 (147,00; 31,00), obrót 180°, footprint i sieci wszystkich 16 pozycji identyczne; obrys P03 kończy się na x = 160, jak przyjęto w P05. Pozostałe przesunięcia części P03 nie dotyczą P05. Test ciągłości 1 → 1 i przymiarka pary złączy pozostają otwarte po obu stronach.

## Do decyzji (R2)

- Położenie anteny kontra dostęp do USB (patrz wiersz sporny wyżej) — po sprawdzeniu zasięgu Wi-Fi w obudowie.
- Konkretne złącze J1 i wtyk P05 (numery części, wysokości rzędów) oraz dystanse — przed zamówieniem PCB P03 i P05.
- Mocowanie modułu Waveshare poza 44 stykami gniazd (drgania w aucie): jeśli moduł ma otwory, dodać dystanse po przymiarce.
- Wiązka CAN do P10 ma teraz 6 pozycji (2 × 3): pole PTH na P10 i taśma muszą to uwzględnić.

## Poza zakresem R1

Obudowa i prowadzenie taśm, firmware, odbiór sprzętu (ODBIOR P03), przymiarka 1:1. Sprzęt: NIE ZBADANO.
