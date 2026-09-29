# P03–P05: status mechaniki B2B po R5

28.09.2026. Status: **otwarte przed zamówieniem P03/P05**. Korekta elektryczna R5 nie zmienia J1 ani jego położenia. Nie zadeklarowano fizycznej przymiarki.

Sprawdzono publiczne rysunki Samtec: [SSW, Rev. CL](https://suddendocs.samtec.com/prints/ssw-1xx-xx-xxx-x-xx-xxx-xx-mkt.pdf), [TSW, Rev. DS](https://suddendocs.samtec.com/prints/tsw-xxx-xx-xxx-x-xx-xxx-mkt.pdf).

- SSW-108-02-G-D-RA oznacza dwurzędowe gniazdo kątowe, osiem pozycji w rzędzie. Rysunek SSW fig. 2 i tabela 2 pokazują raster 2,54 mm oraz wymiar C dla wariantu -02 równy 2,54 mm.
- W TSW końcówka **-NA jest wariantem kątowym z korpusem wersji prostej**; nie oznacza braku kąta. Tabela 5, strona 4, podaje dla -08/-NA wymiar E = 2,77 mm. Nie podstawiać w to miejsce 2,29 mm z kolumny -RA. Dla -08 tabela 1 podaje długość C = 5,84 mm.
- Te wartości mają różne bazy odniesienia. Nie należy odejmować C gniazda od E wtyku i uznawać wyniku za odstęp płytek lub przesunięcie osi kontaktów.

Do zatwierdzenia konkretnego układu dwóch współpłaszczyznowych PCB nadal potrzeba jednego wspólnego przekroju z bazą na górnej powierzchni obu laminatów:

| Punkt do zamknięcia | Kryterium |
|---|---|
| Dokładna para | MPN obu części i warianty korpusów zgodne z rysunkami |
| Osie kontaktów | Oba rzędy na tej samej wysokości po osadzeniu na PCB, bez wymuszania ugięcia pinów |
| Pola lutownicze | Raster, średnice otworów i odległość rzędów od krawędzi zgodne z zalecanym footprintem |
| Numeracja | Fizyczne pin 1 do pin 1; klucz pozycji 2 po właściwej stronie, bez lustrzanego odwrócenia |
| Głębokość wsunięcia | Prawidłowe zazębienie kontaktów, bez oparcia końca pinu o zamknięte dno gniazda |
| Odstęp PCB i dystanse | Korpusy/krawędzie bez kolizji, wsuwanie bez naprężania lutów |

Praktyczny następny krok: kupić po jednej sztuce tej pary do przymiarki i sprawdzić na wydrukach 1:1 oraz laminacie próbnym 1,6 mm. Jeżeli wysokości wymagają dystansu, nie wyginać wyprowadzeń na siłę — skorygować dobór/footprint obu płytek w osobnej, jawnej zmianie mechanicznej. Nie zatwierdzono CAM na podstawie samej mapy pinów.
