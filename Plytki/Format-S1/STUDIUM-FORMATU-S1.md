# Studium formatu S1 — stos płytek zamiast kasety

*29.09.2026 · Claude (sesja lokalna), na prośbę użytkownika przed PCB P02 R4. To szacunek, nie projekt: dokładność ok. ±25 %, rozstrzyga dopiero layout.*

**Źródła danych:**
- powierzchnie liczy `src/powierzchnie.py`, wynik w `dane/powierzchnie.json`;
- obrysy części pochodzą z PCB R1–R5 zapisanych w `Plytki/Kaseta-R1/dane/plytki.json`;
- P02 R4 nie ma jeszcze PCB, więc jej obrysy oszacowałem z BOM etapu 1.

Rysunek porównawczy: `porownanie-S1-kaseta.svg`.

## Wniosek

Przyrząd da się zmniejszyć mniej więcej 3,5 raza:

| Wariant | Teraz (kaseta R1) | Po zmianie (stos S1) |
|---|---|---|
| LOGGER | 11,4 l (361 × 209 × 151 mm) | ok. 3,2 l (231 × 133 × 105 mm) |
| Pełny | 14,5 l | ok. 3,9 l (231 × 133 × 127 mm) |

Warunek: nowy layout wszystkich płytek w jednym formacie. Schematy zostają.

## Skąd zapas

- **Puste miejsce na płytkach.** Części zajmują 21–53 % powierzchni (średnio ok. 35 %). Pięć płytek (P01–P05) ma 160 × 120 mm, a P11 160 × 110 mm. Wynika to głównie ze wspólnego rozstawu otworów kasety, a nie z zawartości.
- **Wysokie elementy już zniknęły:** radiatory P01, puszki 35 mm z P02 R3 i pionowy bocznik PBV w P06.
- **Złącza i wiązki.** Złącza wiązek między płytkami zajmują 6–23 cm² na każdej płytce. Samych wiązek jest 20 w wariancie LOGGER i 36 w pełnym, a potrzebują kanałów i miejsca na łuki przewodów.
- **Rezystory leżące.** Rezystory THT leżące na rozstawie 10–15 mm zajmują 7–23 cm² na płytce (poza P10, która ma ich tylko dwa). Stojące albo SMD 1206 zajmują ok. 5 razy mniej.

Potrzebna powierzchnia płytki w cm². Przyjąłem 1,8 × suma obrysów części, a dla analogowej P05 współczynnik 2,0. Klasy formatu S1 (160 × 100 mm): L = 160 cm², 2/3 = 107 cm², 1/3 = 53 cm².

| Płytka | Dziś | Wiązki, R jak dziś | Wiązki, R stojące/SMD | Płytka połączeń, R jak dziś | Płytka połączeń, R stojące/SMD | Klasa S1 |
|---|---:|---:|---:|---:|---:|---|
| P03 CORE | 192 | 181 | 163 | 146 | 128 | L |
| P02 R4 | 98 (cel) | 155 | 122 | 127 | 95 | 2/3 |
| P04 SAFE | 192 | 125 | 106 | 114 | 94 | 2/3 |
| P05 DAQ | 192 | 110 | 93 | 89 | 71 | 2/3 |
| P06 I-LOGGER | 120 | 81 | 67 | 71 | 57 | 2/3 (1/3 na granicy) |
| P09 TEMP | 100 | 62 | 53 | 56 | 48 | 1/3 |
| P08 SENSOR | 80 | 48 | 40 | 39 | 31 | 1/3 |
| P10 CAN | 56 | 21 | 20 | 17 | 16 | 1/3 |

**Uwaga dla P02 R4:** przy obecnej technice płytka potrzebuje ok. 155 cm², a cel etapu 2 to 98 cm² (115 × 85 mm). Obecna technika to rezystory MFR-50 leżące na 15,24 mm i osiem złączy Mini-Fit LV. Etapu 2 nie warto zlecać przed decyzją o formacie.

## Proponowany format S1

**Płytki:**
- L ≈ 160 × 100 mm (Eurokarta), 2/3 ≈ 107 × 100 mm, 1/3 ≈ 53 × 100 mm.
- Wszystkie mają bok 100 mm, a mniejsze dzielą długość. Dzięki temu każda dotyka obu długich krawędzi.
- Zamiast połówek z pomysłu użytkownika są tercje. Liczby lepiej do nich pasują: wariant pełny mieści się w 5 poziomach zamiast 6. Jedna siatka otworów jest też prostsza niż mieszanie połówek z tercjami.

**Montaż:** płytki leżą poziomo, w poziomach na dystansach M3. Na jednym poziomie jest jedna płytka L albo 2/3 + 1/3 obok siebie. Otwory w siatce co 1/3 długości; dokładne położenia poda specyfikacja formatu.

**Krawędzie i ściany:**
- **Krawędź A (długa):** złącze do płytki połączeń.
- **Krawędź B (długa) — strona serwisowa** (wymaganie użytkownika z 29.09):
  - na każdej płytce listwa kołków goldpin 2,54 mm z punktami potrzebnymi do odbioru: zasilania, sygnały kontrolne z ODBIOR, co najmniej jeden GND na listwę;
  - kołki kątowe wystają za krawędź, więc chwytak da się podpiąć przy skręconym stosie;
  - boczna ścianka obudowy od strony B jest zdejmowana.
- **Krótkie krawędzie:** z jednej strony panel z P11 (wtyki DT, przełączniki, BNC), z drugiej wejścia XT60, OBD i VBAT.

**Elementy:**
- **Wysokie elementy na leżąco:** C_H 2200 µF. TO-220 bez radiatorów, na polu miedzi.
- **Rezystory:** stojące THT (z posiadanych części) albo SMD 1206. Oba warianty dają podobną powierzchnię, a 1206 da się lutować ręcznie i mieści się w ograniczeniu „bez QFN/BGA”. Rezystory mocy (PR02, 2 W) zostają leżące.

### Poziomy

| Poziom (od dołu) | LOGGER | Pełny | Wysokość poziomu |
|---|---|---|---|
| 1 | P02 R4 (2/3) + P10 (1/3) | jak LOGGER | ok. 22 mm (C_H na leżąco, oprawki bezpieczników) |
| 2 | P03 (L) | jak LOGGER | ok. 19 mm (moduł ESP32-S3 na gniazdach) |
| 3 | P05 (2/3) + P09 (1/3) | jak LOGGER | ok. 18 mm (moduły MAX31856 na gniazdach) |
| 4 | P06 (2/3) | P04 (2/3) + P06 (1/3) | ok. 20 mm |
| 5 | — | P07 (2/3) + P08 (1/3) | ok. 25 mm (P07 nieokreślona) |

Kolejność poziomów:
- P02 leży na dole: ciężkie elementy i wejście pakietu.
- P03 jest w środku, bo ma najkrótsze połączenia do pozostałych.
- P05 stoi z dala od P02 i obok P06, która mierzy prąd.

Wariant pełny ma 5 poziomów, jeśli P06 zmieści się w 1/3; inaczej 6.

### Obudowa (szacunek)

**Wnętrze:**
- długość: 50 mm panelu + 160 mm stosu + 15 mm wejść;
- szerokość: 18 mm płytki połączeń + 100 mm stosu + 9 mm strony serwisowej;
- wysokość: 8 mm od dna, płytki po 1,6 mm, dystanse 25 mm (pod P02 R4) i po 20 mm, elementy górnej płytki ≤ 16,5 mm i 3 mm zapasu. Wartości dystansów podaje `SPECYFIKACJA-FORMATU-S1.md`; pierwsze wydanie tego studium liczyło z niższych poziomów i podawało 95 mm i 2,9 l dla wariantu LOGGER.

Ścianki mają 3 mm.

| Wariant | Kaseta R1 | Stos S1, płytka połączeń | Stos S1, wiązki |
|---|---|---|---|
| LOGGER | 361 × 209 × 151 mm, 11,4 l | 231 × 133 × 105 mm, ok. 3,2 l | 231 × 145 × 105 mm, ok. 3,5 l |
| Pełny | 361 × 265 × 151 mm, 14,5 l | 231 × 133 × 127 mm, ok. 3,9 l | 231 × 145 × 148 mm, ok. 5,0 l |

## Połączenia między płytkami: płytka połączeń czy wiązki

| | Płytka połączeń (zalecane) | Wiązki jak w v6.1 |
|---|---|---|
| Co to jest | Pionowa płytka wzdłuż krawędzi A. Każda płytka ma jedno złącze IDC i krótką taśmę do niej. Sieci z tabeli interfejsów v6.1 idą miedzią. | Każda para płytek ma własną wiązkę; złącza kątowe na krawędzi A. |
| Wiązki do zrobienia | Ok. 7 jednakowych taśm plus wiązki zewnętrzne: panel, silnik 5 A, BNC, termopary, BAT, OBD, VBAT. | Ok. 20 w LOGGER, 36 w pełnym. |
| Zmiana logiczna | Brak: te same sieci, inne złącza. | Brak. |
| Koszt | Jedna dodatkowa płytka, a każda płytka dostaje nowe złącze. | Zostają obecne złącza, ale jest więcej ręcznej roboty. |
| Wymiar | Kanał 18 mm. | Kanał 30 mm; wariant pełny o poziom wyższy. |

Prąd silnika 5 A (VSW/VMOTOR, tor ISERIES) idzie osobnymi przewodami, nie taśmą.

## Czego to wymaga

- **Nowe layouty wszystkich płytek w urządzeniu:**
  - LOGGER: P02 R4, P03, P05, P06, P09, P10;
  - pełny: dodatkowo P04, P07, P08;
  - nowy P11 pod nowy panel.

  Schematy zostają; zmieniają się tylko złącza między płytkami.
- **Specyfikacja formatu S1:** obrysy, siatka otworów, wysokości poziomów, złącze płytki połączeń, położenie listwy serwisowej i pinout z tabeli interfejsów v6.1.
- **P00:** stanowisko odbioru dostanie przejściówkę do listew serwisowych i złączy IDC.
- **Do wstrzymania:**
  - etap 2 P02 R4 w starym celu 115 × 85 mm;
  - layout P05 R2;
  - zamówienie PCB P04 (P03 R5 i P04 R2.2 zostaną przerysowane).

## Proponowana kolejność

1. Specyfikacja formatu S1 i płytki połączeń — w sesji lokalnej, bo wymaga całej wiedzy o interfejsach.
2. Pilot: P02 R4 w formacie 2/3 — w chmurze, jako etap 2 z nowym zadaniem.
3. LOGGER:
   - P03, P05 (z poprawkami R2), P06, P09 i P10;
   - płytka połączeń, P11 i obudowa;
   - makieta 1:1 przed zamówieniem.
4. Wariant pełny: P04, P08, P07.

## Ryzyka

- **Szacunki powierzchni (±25 %).** Najciaśniej jest na P03 (moduł ESP32-S3 z gniazdami) i P06 (1/3 czy 2/3).
- **Ciepło w mniejszej obudowie.** P02 R4 wydziela do ok. 1,5 W przy 5 A, a P07 jest jeszcze nieokreślona — do sprawdzenia przy P07.
- **Zakłócenia.** P05 (analog) jest oddzielona od P02 poziomem P03. Masa idzie przez płytkę połączeń na wielu pinach GND.
- **Dostęp.** Przy złożonym stosie da się mierzyć tylko przez listwy serwisowe; co na nich nie trafi, wymaga rozebrania stosu.
