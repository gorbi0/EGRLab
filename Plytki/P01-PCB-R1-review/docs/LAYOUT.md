# P01-PCB-R1 - decyzje i delta względem schematu R3

## Mechanika i technologia

PCB 160 × 120 mm, FR4, nominalnie 1,6 mm, dwie warstwy miedzi po 70 µm.
W stackup zapisano Cu0,07/core1,46/Cu0,07 mm; maska jest warstwą dodatkową.
Wykończenie proponowane: bezołowiowy HASL. Wymiar i grubość miedzi trzeba
przekazać wykonawcy; plik sam nie gwarantuje grubości wykonanego laminatu.

Poprzednie 160 × 100 mm było założeniem rozmieszczenia. Przy obrysach większych
THT i radiatorów oraz strefach wiązek przyjęto 120 mm. Nie zmniejszono obrysów
rezystorów, rozstawów kotew ani średnic otworów, aby wymusić dopasowanie.

M3: NPTH Ø3,2 mm w (5;5), (155;5), (5;115), (155;115) mm, początek w lewym
górnym rogu, X w prawo, Y w dół. Wokół każdego jest keepout Cu Ø8 mm na obu
warstwach. Montaż na izolacyjnych dystansach. Wysokość radiatorów 63,5 mm plus
prześwit; do tego dystanse PCB i miejsce na narzędzie/pokrywę.

## Tor mocy

BAT/J7 i D1 po lewej; D2/HS1 i Q1/HS2 u góry; LK1 i wyjście J6 po prawej.
D1 powraca szerokim odcinkiem do okolicy wejścia, D3 do okolicy wyjścia.
Silny powrót GND biegnie górą i prawym bokiem, ponad częścią odniesienia.
GND jest jedną siecią z wypełnieniem obu warstw, bez szczeliny dzielącej masę.

Główne szerokie odcinki mają 5 mm. Przy TO-220 i wejściu w pady występują
**odcinki 2 mm**; DRAIN ma dalej 4 mm, gałąź D3 3 mm. Nie jest to ciągły tor
5 mm na obu warstwach. VS ma równoległy odcinek F.Cu/B.Cu i trzy przelotki
Ø1,2/0,6 mm. Prąd mocy zmienia stronę również przez PTH D2 i Q1; nie zakładać,
że jedyną drogą są przelotki. PTH elementów mocy lutować z dobrym wypełnieniem.

Orientacyjny rachunek odcinka: R = ρ·L/(w·t), przyjęte ρ20=0,0175 Ω·mm²/m,
t=0,070 mm. Przykładowo 20 mm ścieżki 2 mm daje około 2,5 mΩ, czyli 62,5 mW
przy 5 A; 60 mm ścieżki 5 mm daje około 3 mΩ, czyli 75 mW. Przy wzroście
temperatury Cu o 80 K rezystancja wzrasta w przybliżeniu o 31%. To rachunek
rezystancji fragmentów, **nie kwalifikacja obciążalności całej PCB**: nie obejmuje
PTH, termików, połączeń lutowanych, zwory i temperatury obudowy. Próby
0,1/1/3,5/5 A do ustalenia temperatury pozostają wymagane przez odbiór R3.

J7 ma termiki 1,2 mm / szczelina 0,3 mm. Wypełnione poligony sprawdzono na obu
warstwach: cztery ramiona każdego pada, próbki środka i boków ramion oraz
brak miedzi w próbkach obok ramion. Zachowano możliwość lutowania przewodu.

## Pomiar i sterowanie

LK1 jest jedynym projektowanym połączeniem DRAIN z VPROT. Oba duże pola są
oddzielnymi sieciami. Zwora z Cu2,5 mm² jest montowana po odbiorze ciągłości;
przed montażem można sprawdzić jej rozdzielenie. Nie cynować przestrzeni między
polami w sposób tworzący dodatkowy mostek.

Oba odczepy Kelvin mają osobne ścieżki 0,4 mm kończące się w polach sense.
Gałąź C5 została doprowadzona do pola siłowego VPROT: odczep sense nie rozprowadza
prądu innych elementów. Osobna kontrola wykrywa ponowne użycie pola pomiarowego
jako punktu rozgałęzienia. TP1 do Q1.S: 4,805 mm; TP2 do Q1.G: 4,719 mm.
To długości ścieżek na PCB; przewody zewnętrznej sondy trzeba kwalifikować osobno.

R1 i R23 montować około 3 mm nad laminatem, zgodnie z R3. Układ odniesienia
i komparator są poniżej toru mocy. Bliskość na płytce nie zastępuje pomiaru
stabilności AUX5, progów OVP/UVLO i czasu wyłączenia Q1.

## Biblioteki i napisy

Wartości, numery padów, geometria padów i identyfikatory footprintów elektrycznych
są zgodne z R3. Courtyard radiatora uwzględnia otwartą wnękę montażową TO-220,
zamiast traktować cały prostokąt jako pełny metal. Zachowano rzeczywisty profil
F.Fab, położenie otworów i padów. To nie jest pełna kontrola kolizji 3D.

Pełne obrysy TO-220, radiatorów i małych kondensatorów K15 pozostawiono na F.Fab.
Ich kolidujące z padami/metalem kontury usunięto z nadruku; oznaczenia elementów
pozostały. Zmiana jest zgodna w lokalnych bibliotekach i PCB. Duże obrysy są
widoczne na wydruku montażowym. Pozostałe napisy rozmieszczono poza otworami,
maską i sąsiednimi napisami. J7 ma B+/GND, J6 OUT+/GND/NC, J5 numery 1-6.

## Bramki odbioru

1. DRC i zgodność ze schematem: wykonane; raporty w `verification/`.
2. Kontrole geometrii i trzy celowo wprowadzone usterki w kopiach: wykonane.
3. Przymiarka 1:1 rzeczywistych części i obudowy: **NIE ZBADANO**.
4. Gerbery/wiercenia produkcyjne: **po punkcie 3**, nie są częścią tego wydania.
5. Odbiór elektryczny, SOA, termika i impulsy: **NIE ZBADANO**.

Nie zmieniać statusu 3-5 na PASS na podstawie DRC ani samego renderu.
P07 oraz wariant mostka BTS7960 pozostają poza zakresem.
