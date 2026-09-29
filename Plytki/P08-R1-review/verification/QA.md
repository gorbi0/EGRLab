# QA P08-R1 / 27.09.2026

Pliki: **PASS, do niezależnej recenzji i przymiarki**. Sprzęt: **NIE ZBADANO**. Wynik nie zamyka odbioru ani integracji z samochodem.

| Kontrola | Wynik |
|---|---|
| Natywne ERC KiCad 10.0.6 | 0 naruszeń, 4 arkusze |
| XML eksportowany z finalnego schematu vs części | 172/172 pinów; 55 elementów, 43 sieci; brak różnic |
| Natywne DRC z refill i porównaniem do schematu | 0 naruszeń / 0 niepołączonych / 0 różnic PCB–schemat |
| Niezależne wymagania elektryczne z XML | 35/35 PASS |
| Rzeczywiste pady, wymiary, trasy i odsprzęganie PCB | 25/25 PASS |
| Celowe błędy obwodu / PCB | 20/20 i 15/15 wykryte |
| Logika z połączeń rzeczywistych bramek XML | 16/16 kombinacji |
| Interfejsy P02/P03/P04 vs zachowane migawki | PASS |
| Spójność GND z geometrii miedzi i padów | 1 połączona składowa |
| Odtworzenie z pustego katalogu CAD i raportów | PASS; identyczny odcisk geometrii, nowe ERC/DRC 0 |
| PDF | 4 strony A3 schematu + 4 strony A4 PCB; komplet obejrzany |
| Nazwy Windows i źródła samodzielnych bibliotek | PASS |

PCB: 100 × 80 mm, 2 × 35 µm Cu, FR4 1,6 mm. 59 footprintów z czterema mocowaniami M3, 473 pozycje ścieżek/via, w tym 40 przelotek. Minimalna ścieżka 0,30 mm; prześwit 0,25 mm. Pady wiązek zachowują połączenia termiczne z wylewką; `routing/solid-pads.json` jest pustą listą. Nie wprowadzono wyjątków DRC; standardowe nieaktywne reguły KiCad wymieniono w `ignored_checks` raportu.

Odcisk geometrii: `58b2cd32bf6d327ce062b6386da4206f13e681afbd85de1d2a97a09b9ecac62a`. Raport i hashe wejść: `drc.provenance.json`. Odtworzenie i zakres porównania: `rebuild-check.json`. Odcisk pomija techniczne UUID i nie zastępuje natywnego DRC ani analizy geometrii wylewek. Raporty w katalogu routing są etapami pracy, nie oceną finalnego wydania.

## Problemy wykryte i poprawione

- Kontrakt SENSOR dostosowany do P04-R2.1: sześć pozycji i KEY2. Porównanie z sąsiednimi płytkami jest częścią testów.
- Footprint Omron G6K w dostarczonej bibliotece KiCad miał otwory 2/7 w 3,0 mm. Lokalna wersja stosuje 3,2 mm z rysunku producenta. Celowa zmiana na 3,0 mm jest wykrywana.
- Nadzorca U8 i dzielnik EN wymuszają wyłączenie TPS podczas brownout; margines napięć obliczony, rampy pozostają do pomiaru.
- Pinouty i mechanika układów sprawdzone z kartami producentów; Molex PCB 5,5 mm zweryfikowany z rysunkiem rodziny obejmującym konkretny MPN.
- Rozdzielenie lokalnego bleed R17 od wyjściowego R18 zachowuje rozłączanie powrotu czujnika.
- Krytyczne połączenia TPS i kondensatorów poprowadzone przed resztą PCB; routing kompletny, zbędny krótki ogonek 3V3 wskazany przez DRC usunięty z ponownym sprawdzeniem ciągłości.
- Napisy odsunięto od padów i ramek; sprawdzono wszystkie strony PDF i odtworzenie bibliotek od zera.

Testy odczytują eksportowaną netlistę oraz finalną PCB, nie tylko dane generatora. Negatywne przypadki obejmują m.in. błędne styki przekaźnika, przerwę wspólnego pinu sterownika cewki, obejście styku masy, polaryzację diody, niewłaściwy limit, uszkodzone warunki logiczne, zmianę bufora i kluczy, zły rozstaw otworów, kotwy, decoupling, szerokość ścieżki oraz liczbę warstw. Nie dowodzą odporności na dowolną usterkę.

## Otwarte do integracji i pomiarów

**Firmware:** przed pierwszym SENSOR_PERMIT oraz po zaniku szyn zapewnić 750 ms ciągłej gotowości. Baseline board_mode() ma 100 ms; niezmienione pliki firmware nie są przez ten pakiet kwalifikowane do pracy całego systemu. CORE musi zatrzasnąć usterkę i cofnąć PERMIT. Szczegóły w `docs/ZMIANY.md` oraz `requirements/KONTRAKT.md`.

**Sprzęt:** M01/M02 i E01–E17 w ODBIOR.md. Szczególnie przymiarka G6K/Molex/TO92, rampy obu szyn, Ioff, margines sterowania cewką przy 3,3 V, realny limit prądu, temperatura i czas zwalniania przekaźnika z diodą. SENSOR_OK/HEALTHY nie potwierdzają zasilania na sensorze. Początkowa identyfikacja zaworu wymaga osobnego limitu 20 mA. P11 i kompletny tor pozostają osobnym etapem. P07 nadal HOLD.

Przed następnymi PCB zachować kolejność: kontrakt interfejsów i konkretnych MPN → schemat → rozmieszczenie/ścieżki krytyczne → routing → świeże ERC/DRC z hashami → negatywne kontrole eksportowanych danych → przegląd PDF → odtworzenie od zera → manifest. Formularz wyników sprzętowych pozostaje oddzielny.
