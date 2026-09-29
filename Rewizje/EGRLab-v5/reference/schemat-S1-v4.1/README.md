# Schemat elektryczny EGRLab v4 - S1

Główny plik: **EGRLab-v4-schemat-S1.pdf**, 23 arkusze A3 w poziomie, z zakładkami nawigacyjnymi. Drukuj na A3 w skali 100%; na A4 korzystaj z powiększenia lub wydruku plakatowego. Arkusze w `svg/` są wektorowe i edytowalne np. w Inkscape.

Schemat pokazuje wszystkie obwody dodawane przez konstruktora w architekturze modułowej V4. Gotowe płytki Waveshare, Pololu, TI, moduły termopar i karta SD mają symbole z nazwanymi zaciskami. Wnętrza kupnych modułów pozostają zgodne ze schematami ich producentów. Moduły TC1/TC2 odpowiadają U14/U15 w BOM V4; czujnikami są zewnętrzne izolowane termopary K. OLED i RTC były opcjami poza bazową wersją V4 i nie są obsadzone.

## Co znajduje się w katalogu

- `EGRLab-v4-schemat-S1.pdf` - pełny schemat do czytania i druku.
- `svg/01.svg` ... `svg/23.svg` - osobne arkusze bez utraty jakości przy powiększeniu.
- `dane/piny-sieci.csv` - pin, funkcja, nazwa sieci i numer arkusza.
- `dane/indeks-elementow.csv` - wyszukiwanie elementów po oznaczeniu.
- `dane/components.json` - model połączeń użyty do rysowania.
- `dane/pokrycie.json` - kontrola obecności wszystkich elementów modelu na arkuszach.
- `dane/zrodla-sha256.json` - identyfikacja wejściowych tabel V4.
- `UWAGI-S1.md` - doprecyzowania i korekta wykonawcza dzielnika OVP.
- `BOM-uzupelnienia-S1.csv` - elementy uzupełniające i zmiany względem zbiorczego BOM V4.
- `generator/` - źródło generatora wraz z kopiami wejściowych tabel; służy do odtworzenia PDF/SVG.

To schemat z sieciami nazwanymi: jednakowe etykiety łączą się także między stronami. `NC` oznacza brak połączenia i **nie tworzy wspólnej sieci**. AGND, DGND i PGND spotykają się w GND_STAR, z osobnymi powrotami fizycznymi. Styki po obu stronach wtyku są połączone tylko po włożeniu wtyku; pętla T.10-T.11 znajduje się w adapterze, nie na płycie bazowej. Kelvin K1/K2 dochodzą do końców elementu oporowego oddzielnymi przewodami od toru mocy P1/P2.

## Stan wykonania

Schemat S1 powstał na podstawie V4; oryginalnych katalogów V3 i V4 nie zmieniono. Uzupełnienia są jawnie opisane. Wykonano kontrolę pokrycia modelu, połączeń i wizualne sprawdzenie PDF. Nie wykonano ERC/DRC w KiCad, PCB ani pomiarów fizycznego urządzenia. SVG nie jest plikiem schematu EDA i nie należy traktować go jako wejścia do automatycznego routingu PCB.

Przed aktywnym TEST pozostaje wymagany odbiór elektryczny opisany w V4, w szczególności OVP, interlock, watchdog, progi i czasy odcięcia, sekwencja zasilania oraz wpływ adaptera LOGGER na obwód ECU.
