# Źródła i granice weryfikacji

Odczyt27.09.2026. Dokumenty w `reference` są kopiami do audytu;ich skróty
w `source-sha256.json`. Nie pochodzą z edytowanych wcześniejszych rewizji.

| Źródło pierwotne | Użycie |
|---|---|
| [Phoenix1755752](https://www.phoenixcontact.com/en-gb/products/pcb-header-mstbva-25-4-g-508-1755752?type=pdf) | 4p,raster5,08,pin1×1 mm,otwór1,4 mm,nominalnie12 A;rysunek i derating |
| [Molex39-29-9129](https://www.molex.com/en-us/products/part-detail/39299129) | Header12p,złocony,z kołkami,seria5566;kopię katalogu przejęto z audytu P04 |
| [TE0460-202-1631](https://www.te.com/en/product-0460-202-1631.html) | Size16,pinAu,przewód0,5–1,5 mm²;nie mylić z niklowym16141 |
| [TE DT04-12PA](https://www.te.com/en/product-DT04-12PA.html) | Złącze TEST;B/C odmienne klucze dlaLOGGER;nie ma kontaktu detekcji |
| [EAO14-435.036](https://www.eao.com/component/14-435.036/de/vorsatz) | ChwilowyNO,low-levelAu dlaARM/MARK/TESTdetektora |
| [EAO14-473.036](https://www.eao.com/component/14-473.036/fr/actuator) | ZatrzaskowyNC+NO,low-levelAu,referencyjnySTOP funkcjonalny |
| [EAO14-412.036K](https://www.eao.com/component/14-412.036K/en/actuator) | KluczykNC+NO,low-levelAu,wykorzystaneNO |
| [EAO katalog14](https://eao.com/fileadmin/documents/PDFs/en/01_main-catalogue/EAO_MC_14_Main-Catalogue_EN.pdf) | 14-432.036 dwaNC;konfigurację i minimalne obciążenie potwierdzić przy zakupie |

Molex footprint12A2 ma raster wzdłuż rzędu4,2 mm,między rzędami lutowniczymi5,5 mm,
otwory styków1,4 mm i dwaNPTH3 mm. Sam napis „raster4,2” nie oznacza siatki4,2×4,2.
Weryfikacja końcowych współrzędnych jest w `pcb-checks.json`,druk1:1 w PDF.
Wersja konkretnego rysunku zakupionego złącza nadal podlega przymiarce przed produkcją.

EAO to referencja funkcjonalna doboru low-level. Nie zamrażamy wykroju blachy
bez zakupionych elementów. Korpus może wymagać oddzielnej nasadki/oznaczenia;
ich zamówienie w komplecie jest obowiązkiem montażowym,opisanym wZAKUPY.
Brak nadruków katalogowej numeracji zacisków naPCB:wiązka ma numerację funkcji.
Nie przypisujemy kontak­tom normy E-stop ani samym blokadom klasy bezpieczeństwa.

Rezystancja miedzi jest obliczeniem inżynierskim,nie deklaracją obciążalności termicznej.
ERC/DRC nie weryfikują prawdziwych MPN,zaciskarki,skoku popychaczy,upływności
podczas nagrzania ani skuteczności diagnostykiP0404 w aucie.
