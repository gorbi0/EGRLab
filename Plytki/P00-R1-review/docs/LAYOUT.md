# P00 PCB R1 — layout i mechanika

25.09.2026 · Claude. Płytka z netlisty schematu P00-R1 (`verification/P00.xml`), rozmieszczenie `src/placement.json`, trasy zablokowane `src/route_critical.py`, reszta Freerouting 2.1.0. Liczby z `verification/pcb-checks.json`.

## Format i rozkład

115 × 70 mm, 2 × 35 µm, laminat 1,6 mm, cztery otwory M3 (3,2 mm) 5 mm od narożników z obszarem bez miedzi Ø8 mm; reguły DRC jak w P01/P02. Górny pas: zasilanie po lewej (J10 przy lewej krawędzi, D1, C4/C5, U2 LM2937 pionowo, C6/C7, LED zasilania, pola TP3/TP1/TP2), blok 555 po prawej. Dolny pas: osiem kolumn kanałów co 11 mm i kolumna HB. Kolumna (od góry): numer kanału i LED, RL (lewy), przełącznik (środek, suwak pionowo), RS (prawy), listwa 1 × 2 (lewy pin GND, prawy sygnał).

## Miedź

| Część | Wykonanie |
|---|---|
| Zasilanie | 1,0 mm F.Cu, zablokowane: J10.1 → D1 → C4/C5 → U2.1; U2.3 → C6/C7 → RL10; każdy odczep w wierzchołku szyny |
| 3V3 do przełączników | 0,6 mm F.Cu zjazdem między kanałami 4 i 5, jedna przelotka, szyna 0,8 mm B.Cu pod pinem 2 wszystkich dziewięciu przełączników |
| Kanał | 0,5 mm F.Cu, zablokowane: COM → ścieżka pod korpusami RL i RS do ich padów; RL → anoda LED; RS → pin sygnałowy listwy |
| Blok 555, HB, TP | Freerouting (2 przebiegi, 0 niepoprowadzonych) |
| GND | wylewki na obu warstwach (usuwanie wysp bez połączenia), pady THT łączą warstwy |

## Nadruk

Oznaczenia rezystorów i U1 wewnątrz korpusów; w kolumnach tylko numer kanału przy LED (SWn, LEDn, RLn, RSn, Jn to kolumna n) — oznaczenia pojedynczych części są na warstwie Fab i na stronie montażowej PDF. Opisy: kierunek suwaka (w górę = H/3V3), układ listew (lewy GND, prawy sygnał przez 1 k), RUN/STOP heartbeatu, +VIN 5–15V przy J10, nazwy pól pomiarowych. Wszystkie poza obrysami części.

## Mechanika i użycie

Przyrząd stoi na stole: cztery nóżki lub dystanse M3. Najwyższe elementy: LM2937 w TO-220 (ok. 20 mm, bez radiatora) i złącze J10. Przewody zasilania wchodzą do J10 od lewej krawędzi (sprawdzone na modelu 3D). Przewody Dupont nasadza się od góry na listwy przy dolnej krawędzi. Przed montażem przełączników sprawdzić jeden egzemplarz omomierzem: suwak w górę ma łączyć środkowy pin z dolnym. Jeśli jest odwrotnie, zmienia się tylko opis na nadruku; LED pokazuje prawdziwy stan.

## Czego nie sprawdzono

Przymiarka 1:1, częstotliwość i amplituda heartbeatu, nagrzewanie LM2937 przy 15 V, odbiór ODBIOR P00. Sprzęt: NIE ZBADANO.
