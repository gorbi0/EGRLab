# Kaseta R1 — koncepcja obudowy EGRLab

*29.09.2026. KONCEPCJA do przymiarki w aucie, nie rysunek wykonawczy. Przymiarka, ocena cieplna i wiązki w kasecie: NIE ZBADANO.*

**Do druku:** `KASETA-R1.pdf`, A3, 5 arkuszy:

| Arkusz | Zawartość |
|---|---|
| 1 | Wariant LOGGER: widok od przodu, z góry i z boku w skali 1:2, tabela płaszczyzn |
| 2 | Wariant PEŁNY: to samo |
| 3 | Wiązki: długość z projektu a szacunek w kasecie |
| 4, 5 | Widok z góry 1:1 (LOGGER, PEŁNY) do położenia w aucie |

Skala arkuszy 1:1 sprawdzona na rastrze 100 dpi: obrys zewnętrzny 360,7 × 209,0 mm i 360,7 × 265,2 mm (oczekiwane 361 × 209 i 361 × 265). Drukuj w skali 100 %, bez dopasowania do strony; na drukarce A4 w Adobe Reader opcja „Plakat”, skala 100 %.

## Wymiary

| Wariant | Płytki | Wnętrze (szer. × gł. × wys.) | Ze ściankami 3 mm | Objętość wewn. / zewn. |
|---|---|---|---|---|
| **LOGGER** (zalecany przed 23.10) | P01 z SK129 25,4 mm, P02, P03, P05, P06, P09, P10, P11 | 355 × 203 × 145 mm | 361 × 209 × 151 mm | 10,5 / 11,4 l |
| **PEŁNY** | jak wyżej + P04, P07 (rezerwa 120 × 100), P08; P01 z SK129 63,5 mm | 355 × 259 × 145 mm | 361 × 265 × 151 mm | 13,4 / 14,5 l |

Do makiety z kartonu doliczyć poza obrysem: ok. 70 mm z przodu na wtyki DEUTSCH z przewodami, ok. 40 mm z tyłu na przewody BAT i OBD, ok. 30 mm z boku P05 na wtyk BNC AUX.

**Korekta szacunku z 28.09.** Wcześniej podałem ok. 7,3 l dla wariantu LOGGER i 11,2 l dla pełnego. Tamten szacunek nie obejmował strefy panelu z P11 (51 mm głębokości), kanałów na wiązki (25 mm wysokości i 30 mm szerokości) ani płyt nośnych małych płytek (ok. 7 mm na każdą płaszczyznę).

## Układ

- Płytki stoją pionowo, stroną elementów do tyłu, na prętach M3 z tulejami przez narożne otwory. Rozstaw 150 × 110 mm jest wspólny dla P01–P05, więc nie trzeba nowych otworów w PCB.
- Dwie kolumny: jedna za P03, druga za P05. P03 i P05 stoją w pierwszej płaszczyźnie, bo łączy je złącze B2B; szczelinę między nimi przyjęto 5 mm.
- Małe płytki (P06, P07, P08, P09, P10) siedzą na płytach nośnych 160 × 120 × 2 mm z tym samym rozstawem otworów, na dystansach 6 mm.
- Panel jest na ścianie przedniej: DT ×3, przełączniki, BNC SCOPE i gniazda termopar. P11 stoi na dystansach 10 mm za ścianą, przed P05, bo wiązka TAPS P05→P11 ma najwyżej 50 mm.
- BNC AUX jest na ścianie bocznej przy P05 (przewód 50 mm). Przepusty BAT i OBD są na ścianie tylnej, w kanałach nad i pod płytkami.
- Kolejność płaszczyzn i obroty płytek dobrał skrypt (`src/model.py`) pod długości wiązek. Największą wagę mają TAPS, AUX i SAFE, mniejszą łącza SPI.

| Wariant | Kolumna P03 (od przodu) | Kolumna P05 (od przodu) |
|---|---|---|
| LOGGER | P03 (Y 0) → P06 (43) → P09 (85, obrót 180°) → P10 (128) | P05 (0) → P02 (36, 180°) → P01 (91) |
| PEŁNY | P03 (0) → P04 (36, 180°) → P06 (83) → P09 (126, 180°) → P08+P10 (168, obie 90°) | P05 (0) → P02 (36, 180°) → P01 (91) → P07 (169) |

Y to odległość powierzchni elementów od P03|P05 w mm. Szczegóły są w `dane/uklad-*.json`.

## Wysokość zajęta nad płytką (założenia)

| Płytka | mm | Źródło |
|---|---|---|
| P01 | 65 / 30 | SK129 63,5 mm (MECHANIKA R3.1); w wariancie LOGGER SK129 25,4 STS: ten sam footprint i otwór TO-220 na 13,5 mm (rysunek Fischera 001020452) |
| P02 | 50 | puszki Ø35 × 45 mm + 3 mm nad zaworem; wtyki Mini-Fit z przewodem 35 mm (MECHANIKA R3) |
| P04 | 35 | Mini-Fit J7/J8 z wtykiem i łukiem przewodu |
| P06 | 30 | PBV pionowo, ≥ 25 mm pod pokrywą (MECHANIKA P06) |
| P11 | 30 | ≥ 30 mm wolnej wysokości nad PCB (WIAZKI P11) |
| P03, P05, P07, P08, P09, P10 | 20–35 | szacunek z listew, wtyków IDC i modułów — do przymiarki |

## Wiązki

Długości w tabeli interfejsów v6.1 (i WIAZKI P11) zaprojektowano pod płaski nośnik z płytkami obok siebie. W kasecie przewody obchodzą krawędzie kolejnych płytek, dlatego:

- w wariancie LOGGER mieści się 5 z 20 wiązek (TAPS tylko po przeniesieniu J7 na P11);
- w wariancie pełnym mieści się 6 z 36 wiązek.

Wiązek jeszcze nie wykonano, więc wydłużenie to zmiana w BOM, a nie w PCB. Szacunek składa się z wyjścia złącza, trasy przez kanały wokół krawędzi i 10 mm łuku. Dokładność to ok. ±20 mm, a rozstrzyga makieta. Pełne zestawienie jest w `dane/wiazki-*.csv` i na arkuszu 3.

Wiązki elektrycznie wrażliwe wymagają decyzji przed wydłużeniem:
- **TAPS** (tor analogowy, maks. 50 mm): 44 mm po przeniesieniu J7 na P11 dokładnie przed J4 P05. Przy obecnym położeniu J7 wyjdzie ok. 190 mm (LOGGER) albo 120 mm (PEŁNY).
- **Ogonki DT W5–W7:** prowadzą ten sam tor analogowy; w kasecie ok. 200–340 mm zamiast 150 mm.
- **VSENSE P02→P05:** ok. 280 mm zamiast 150 mm.
- **SAFE P03→P04** (tylko wariant pełny): ok. 180 mm zamiast 150 mm. Zbocze resetu w P03-R4 liczono dla 150 mm (5,5 ns/V przy limicie 10 ns/V), więc trzeba je przeliczyć.
- **ILOG, TEMP, ITEST (SPI, 100 mm):** 110–320 mm. Trzeba sprawdzić przebiegi SPI na dłuższej taśmie albo zmienić kolejność płaszczyzn.

## Sprawy otwarte

1. **P11 R2:** J7 (TAPS) trzeba przenieść dokładnie przed J4 P05; miejsce jest zaznaczone na arkuszach 1 i 2. P11-R1 nie ma recenzji ani zamówienia.
2. **Wiązki:** nowa tabela długości pod kasetę oraz przeliczenia z listy wyżej.
3. **Wariant LOGGER bez P04:** trzeba potwierdzić, że firmware CORE pracuje bez podłączonej P04 (H_SAFE).
4. **Dostęp do karty SD i USB modułu CORE:** P03 stoi zaraz za panelem, stroną elementów do tyłu.
5. **Moc:** P01 i P07 przy 5 A w zamkniętej kasecie potrzebują wentylacji i próby nagrzewania (warunek z decyzji o miedzi 35 µm).
6. **Bank P02:** puszki leżą poziomo i potrzebują obejm do wspornika na prętach.
7. **B2B P03–P05:** szczelina 5 mm do potwierdzenia przymiarką (patrz `P03-R5-review/docs/B2B-STATUS.md`).
8. **Temperatura:** płytki są projektowane na 0–50 °C, dlatego obudowa idzie do kabiny, a nie do komory silnika.

## Odtworzenie

1. Python KiCada 10.0.6: `python src/wyciag_plytek.py`. Czyta pliki PCB najnowszych rewizji i zapisuje `dane/plytki.json` z sumami SHA-256 źródeł.
2. Python z reportlab (runtime Codexa): `python src/rysunek.py`. Tworzy `KASETA-R1.pdf`, `dane/uklad-*.json` i `dane/wiazki-*.csv`.
3. Podglądy: `pdftoppm -r 80 -png KASETA-R1.pdf podglad/arkusz`.

Po zmianie rewizji którejkolwiek płytki trzeba powtórzyć oba kroki.
