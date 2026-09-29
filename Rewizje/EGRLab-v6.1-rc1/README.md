# EGRLab 6.1-rc1 — stabilizacja projektu

HW 6.1-rc1 / interfejs M2.1, 23.09.2026. Kia Sportage 1.7 CRDi 2013, EGR 28410-2A850; ESP32-S3 N32R16V. LOGGER inline oraz TESTER pozostają osobnymi drogami podłączenia. Wydanie powstało z V5 i przeglądu Opusa, z uwzględnieniem ustaleń o samodzielnym montażu i wymiennych modułach.

**Nowe wykonanie:** P01/P05/P07 to zamawiane PCB dwuwarstwowe; pozostałe moduły są trwale lutowanymi nośnikami / płytkami uniwersalnymi. Taśmy są lutowane do PTH modułu i mają kotwę 10–15 mm od lutów. CORE–DAQ jest bezpośrednim połączeniem płytka–płytka. Gotowe MAX31856 i VNH5019 zachowują swoje listwy/gniazda. AD7606BBSTZ montujemy bezpośrednio na P05.

Pakiet zawiera projekt obwodu, pinową netlistę, atlas połączeń, kontrakt wiązek, BOM i firmware. Zawiera edytowalny import schematów KiCad z porównaniem netlisty i ERC. **Nie zawiera trasowanych PCB ani Gerberów; import EDA nie jest jeszcze dopuszczeniem do layoutu.** Rysunki montażowe są wytycznymi do rozmieszczenia, nie plikami produkcyjnymi. Żaden egzemplarz nie przeszedł fizycznego odbioru.

- [Wprowadzone poprawki i skutki zmiany rezystorów](docs/09-zmiany-v6.md).
- [Interfejsy — który koniec jest lutowany](interfejsy.csv), [numery wszystkich żył](hardware/wiring.csv), [instrukcja wiązek i B2B](docs/10-montaz-wiazek.md).
- [Karty modułów z pozycją „Wiązka”](docs/PCB.md), [BOM wszystkich modułów](hardware/BOM.csv), [zakupy nazwa–ilość](hardware/zakupy.csv), [części wiązek](hardware/wiazki-czesci.csv), [narzędzia](hardware/narzedzia.csv).
- [Atlas schematów pinowych](schematy/index.html), [rysunki montażowe](montaz/index.html), [netlista](hardware/netlist.csv).
- [Architektura](docs/01-architektura.md), [GPIO i połączenia](docs/02-interfejsy.md), [uruchamianie etapami](docs/03-uruchomienie.md).
- [Firmware i logi](docs/04-firmware-logi.md), [profile i kalibracja](docs/05-profile.md), [diagnostyka](docs/06-diagnostyka.md), [wyniki sprawdzeń](verification/README.md).

Format binarnych logów pozostaje **5, 40 B/próbkę**; profile kalibracyjne i NVS mają wersję **6**. Zmiana nominałów wymaga ponownej kalibracji. Nie wgrywaj profilu V5 jako V6 przez samą zmianę numeru wersji. Obrazy startowe mają `EGR_HARDWARE_ACCEPTED=0`.

`reference/` zawiera historię i recenzję; nie jest aktualnym BOM-em. `P01-PROTECT/` opisuje odziedziczony wewnętrzny obwód ochrony; połączenia do innych modułów bierze się z V6. Elementy P01 są już w zbiorczych zakupach. Poprzednich wydań, w tym V3 i V5, nie zmieniono.


Zacznij od [wyniku stabilizacji i otwartych bramek](stabilizacja/STATUS.md), [rejestru usterek](stabilizacja/rejestr-usterek.csv) i [opisu importu KiCad](eda/README.md). V6 zachowano bez zmian. Aktualne są pliki tego RC; reference/ oraz PDF/SVG historycznego P01 nie zastępują aktualnej mapy połączeń.
