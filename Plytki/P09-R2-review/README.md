# P09 R2 — TEMP w formacie S1 (schemat i PCB)

29.09.2026, sesja w chmurze (schemat); 30.09.2026 wieczorem, komputer 24/7 (PCB, sekcja „PCB”); 1.10.2026: poprawki po recenzji PCB i moduły lutowane wprost (decyzja użytkownika). **Status: schemat i PCB do lokalnej recenzji**, sprzęt NIE ZBADANO. R2 powstała na kopii generatora z `Plytki/P09-R1-review` (zamknięty pakiet, niezmieniony); wymagania: `Plytki/Format-S1/SPECYFIKACJA-FORMATU-S1.md` (S1-2) i zadanie `Plytki/Format-S1/zadania/ZADANIE-P09-P10-S1.md`.

**Klasa płytki:** 1/3 (53 × 100 mm), slot S3 poziomu 3. Logika (U1/U2 74LVC125AD z Ioff, dekoder U3 HC139, moduły MAX31856 XU, JP1/JP2 wyboru VIN) bez zmian względem R1.

## Zmiany R1 → R2

| Element | R1 | R2 |
|---|---|---|
| Złącza do innych płytek | J1 LV09 (Mini-Fit, 4 żyły) i J2 TEMP (IDC 10, taśma) lutowane do PTH | **J1 = J_BP**: kątowe obudowane IDC 2×8, krawędź A, środek slotu; piny nieparzyste GND, parzyste: 5V_SYS ×2, 3V3_IO, SPI3_SCLK, SPI3_MOSI, SPI3_MISO, TC1_CS, TC2_CS |
| Punkty pomiarowe | TP1–TP13 (pola) | **J2 = listwa serwisowa** kątowy goldpin 1×13 na krawędzi B, GND na kołkach 1 i 13; kołki 2–12 przez rezystory R20–R30 (1 kΩ, przy węzłach): 3V3_IO, 5V_SYS, TC1_VIN, TC2_VIN, TC1_3VO, TC2_3VO, CS1_BUF, CS2_BUF, OE1_N, OE2_N, SPI3_MISO |
| FLT/DRDY modułów | pola TP10–TP13 | nieprzyłączone (NC) |
| R1, R2, R5, R6, R18, R19 (10 k), R3, R4, R7–R10, R13 (100 k) | DIN0207 leżące, raster 10,16 | **posiadane MF0207 na stojąco** (raster 5,08, obudowa `…P5.08mm_Vertical`) |
| R11, R12 (100 Ω), R14–R17 (47 Ω) | THT | **nowe SMD 1206** |
| C1–C3 (100 n) | 0805 | **posiadane K104K15X7RF5TH5, radialne 5 mm** |
| C4, C5 (4µ7), C6, C7 (1 µ) | 0805 | **nowe SMD 1206** X7R 25 V |
| Moduły J3/J4 | gniazda 1×9 Au, słupki nylonowe M2,5 | **lutowane wprost** fabryczną listwą modułu, bez otworów podparcia (decyzja użytkownika 1.10.2026) |
| Pozostałe | — | bez zmian (U1–U3, JP1/JP2) |
| Obrys / mocowanie | 100 × 100 mm, 4 otwory | 53 × 100 mm, otwory slotu M3 wg S1 (rysuje layout) |

Przypisanie części do rejestru wynika z dosłownego dopasowania wartości i typu do `Zamowione/zamowione.csv` (kolumna `zrodlo` w `docs/BOM.csv`). Bilans zapasu: `docs/ZAKUPY.md`.

## Wyniki (szczegóły: `verification/QA.md`)

| Kontrola | Wynik |
|---|---|
| ERC (4 arkusze) | 0 naruszeń |
| Netlista pin po pinie względem `parts.py` | 46 części, 171/171 pinów, 49 sieci, 0 błędów |
| Kontrole elektryczne | 52/52 PASS (w tym nowe: J_BP nieparzyste = GND, parzyste tylko użyte sygnały i zasilania, ciągłość z R1, 5V_SYS ×2, zgodność z `J_BP.csv`; listwa ≤ 13, GND na końcach, 1 kΩ przy węźle, zgodność z `SERWIS.csv`; źródła części THT/SMD) |
| Próby ujemne | 35/35 mutacji wykrytych, próba zerowa (bez zmiany) czysta |
| Orientacyjna zajętość (`src/powierzchnia.py`) | suma obrysów części 3020 mm² wobec ok. 4486 mm² użytecznej powierzchni 53 × 100 mm (67 %, bez rozmieszczenia; moduł ok. 557 mm² każdy) |

## Decyzje projektowe (sporne oznaczone)

- **5V_SYS na dwóch pinach J_BP** — zgodnie z S1 §5 („co najmniej 2 pinach”), choć P09 pobiera z 5 V niewiele (tylko VIN modułów przy JP 2–3 i C5); wszystkie 8 parzystych pinów 2×8 jest użyte.
- **Wszystkie kołki serwisowe po 1 kΩ** — węzły P09 to szyny i logika; 3Vo modułów też (wyjście regulatora, nie węzeł wysokoimpedancyjny).
- **Na listwie brak wejść SCLK/MOSI/TC1_CS/TC2_CS z J_BP** — 11 kołków wystarcza na punkty odbioru specyficzne dla P09 (VIN, 3Vo, CS za buforem, OE, MISO); wejścia mierzy się na listwie P03.
- **FLT/DRDY nieprzyłączone** — bez pól testowych i wolnych żył.

## PCB (30.09.2026, poprawki po recenzji i lutowanie modułów wprost 1.10.2026; `src/run_release.py`, KiCad 10.0.6 w Dockerze)

| Kontrola | Wynik | Raport |
|---|---|---|
| DRC świeży, wszystkie poziomy | 0 niepołączonych, 0 niezgodności ze schematem, 0 innych naruszeń; 2 × `lib_footprint_mismatch` (J1, J2: nadruk przycięty przez `silkscreen.py`, przyjęte jawnie) | `verification/drc.json` |
| Kontrole PCB (`verify_pcb.py`) | 25/25 | `verification/pcb-checks.json`, `QA-PCB.md` |
| Próby ujemne PCB | 22/22 z zerową | `verification/negative-controls.json` |
| Trasowanie | Freerouting 2.1.0 (GND jako płaszczyzna B.Cu), pierwsza próba, bez tras planera; 56 przelotek; ścieżki 0,3 mm (F.Cu 1,38 m, B.Cu 0,61 m); wylewki GND F.Cu 61 %, B.Cu 74 % | `routing/attempts.json`, `pcb-checks.json` |

Łańcuch jak w P03 R6 (te same skrypty, wartości płytki w `src/board.py`; część wspólna z P10 R2): `fanout_gnd.py` (belki GND pod U1/U2, grzebień pod J1), `prepare_routing.py` (GND jako płaszczyzna), Freerouting, `cleanup.py --tidy`, `stitch.py`, `complete_routes.py`. Rozmieszczenie (`src/placement.py`, KiCad Python) uruchamia się osobno, przed `--new-route`; `run_release.py` odtwarza zapisany wynik routera (`routing/P09.ses`). PDF obejrzany (5 stron) 1.10.2026.

**Decyzje (sporne oznaczone):**
1. Ścieżki 0,3 mm przy odstępie 0,25 mm (S1 §3, reguły jak P02-R3); wyjątek 0,2 mm z P03 R6 tu nie obowiązuje.
2. **Moduły J3/J4 lutowane wprost** fabryczną listwą 1×9 (decyzja użytkownika 1.10.2026; recenzja: gniazdo z modułem wychodziło 16,5–19 mm, a słupki podparcia dawały śruby pod płytką). Footprint `P09:MAX31856_XU` ma tylko 9 pól, bez otworów Ø6 i pól bez miedzi. Wysokość: szacunek górny 14,1 mm (plastik listwy 2,5 + płytka modułu do 1,6 + terminal do 10; `src/heights.py`), do potwierdzenia pomiarem (MODUL-KWALIFIKACJA krok 1). Wyprowadzenia listwy od spodu przyciąć do ≤ 1,5 mm (S1 §4).
3. Moduły obrócone o 90°: terminale termopar w stronę ściany wejść (x = 53 mm; S1 §2 i §7), krawędź obrysu modułu 3,5 mm od krawędzi płytki, pin 1 (VIN) u góry rzędu z nadrukiem „1” (S1 §9; przy J3 pod obrysem modułu, przy J4 obok). `docs/MODUL-KWALIFIKACJA.md` opisuje orientację.
4. **Sporne (dokumentacja):** pin 1 listwy J2 jest od większego x (x = 41,74 mm). Kątowa listwa od góry z kołkami za krawędzią B nie pozwala inaczej (tak samo J_SV1–3 w P03). Kolejność sygnałów od pinu 1 bez zmian; poprawione: nota BOM J2 (`src/parts.py`) i `docs/ODBIOR.md` („od strony większego x, patrząc od krawędzi B: od prawej”).
5. Rezystory serwisowe R20–R30 od spodu (SMD 1206, 0,7 mm; S1-2), przy węzłach, ≥ 1 mm od pól THT (najbliżej R30: 1,07 mm). Pas zastrzeżony krawędzi A (S1 §5) wolny po obu stronach (recenzja 1.10: stały w nim C4 i R20); rozmieszczenie go omija.
6. C6/C7 (1 µF przy VIN modułów) 4,0 i 4,25 mm od pinu VIN, próg 6 mm jak dla odsprzęgania układów (recenzja 1.10: JP1 przesunięty pod J3.1 jak JP2; wcześniej 6,02 mm przy progu 6,5 mm). C1–C3 2,5–3,25 mm od pinów zasilania.
7. **Sporne (lutowanie):** trzy pola z pełnym połączeniem z wylewką zamiast termicznego (J1.5, J1.11, J4.3 — szprychy odcięte przez ścieżki). Przy lutowaniu tych pinów potrzeba więcej ciepła.
8. Nadruk: tytuł z klasą i slotem `P09 R2 S1-1/3 S3` (S1 §9); etykiety listwy pełnymi nazwami sieci (SPI3_MISO jako „MISO”), sprawdzane z tabelą `LABEL` w `silkscreen.py`, nie z wynikiem nadruku; każde oznaczenie bliżej swojej części niż innych i poza strefami Ø7. Pięć oznaczeń ukrytych z braku miejsca (R3, R6, R9, R12, R16) jest na rysunku montażowym z warstwy F.Fab (strona 2 PDF).
9. Informacyjnie: tabela budżetu złączy S1 §8 („pierwsze przybliżenie”) podaje dla P09 IDC 2×5; pakiet R2 ma 2×8 (poza pięcioma sygnałami SPI/CS niesie 5V_SYS ×2 i 3V3_IO) — do uwzględnienia przy P12.

**Recenzja 1.10 (niezależna, tylko odczyt; 1 MAJOR, 6 MINOR, 4 NIT) — poprawione:** wysokość modułu (lutowanie wprost), C6/C7, wzorzec etykiet z próbą zamiany, próby ujemne dla kontroli bez prób (strefy D7, tytuł, C6/C7, pas A, znaki pinu 1, bliskość oznaczeń), znaki pinu 1 przy J3/J4, pas A, podpis renderu i ręczny wpis oględzin PDF, tytuł ze slotem, niezgodności dokumentów, pozostałości po P03 w komentarzach, oznaczenie R2 w strefie Ø7. Próba `gnd_pour_removed` usuwa wylewkę w pliku (`b.Remove()` psuł SWIG w kolejnych próbach).

**Otwarte:** przymiarka wydruku 1:1 z modułami (strona 5 PDF), pomiar wysokości modułu z terminalem, recenzja; paczka produkcyjna dopiero po „scal”.

## Otwarte punkty

1. Przymiarka 1:1 modułów MAX31856 XU i kwalifikacja zasilania (`docs/MODUL-KWALIFIKACJA.md`) przed lutowaniem; obrys modułu nadal prowizoryczny, a po przylutowaniu nie ma regulacji.
2. PCB do recenzji (sekcja „PCB”): przymiarka 1:1 z modułami, wysokość modułu z terminalem, punkty sporne 4 i 7.
3. Zapas części z rejestru (zob. `docs/ZAKUPY.md` i opis PR): P09 + P10 razem potrzebują 10 k — 9 szt. wobec 7 oraz 100 n — 6 szt. wobec 5.
4. Listwa serwisowa musi być **kątowa** (posiadana 1×40 jest prosta); typ IDC J_BP do wyboru w zakupach.
5. Poprawka firmware MAX31856 z R1 (`P09-R1-review/firmware`) bez zmian, do scalenia przy integracji P03.

## Uruchomienie

PCB: `scripts/egrlab-docker python3 src/run_release.py` (ok. 3 min): łańcuch schematu, layout (odtwarza `routing/P09.ses` i `completion-routes.json`; `--new-route` uruchamia Freerouting, potrzebny `EGRLAB_FREEROUTING`), nadruk, reguły, `verify_pcb.py`, próby ujemne, widoki, PDF, `QA-PCB.md`, manifest.

Sam schemat: `scripts/egrlab-docker python3 src/run_schematic.py` (ok. 20 s): budowa schematu, `make_docs.py` (CSV dla P12 i zakupy), ERC, netlista, `verify_schematic.py`, `verify_electrical.py`, PDF i PNG, `QA.md`, manifest SHA-256. Lokalnie: Python KiCada 10.0.6, `KICAD_CLI` i `PDFTOPPM`.

## Zawartość

| Ścieżka | Zawartość |
|---|---|
| `eda/` | Projekt KiCad 10 (4 arkusze A3, `P09.kicad_pcb`), biblioteki lokalne |
| `output/pdf/P09-R2-schemat.pdf`, `output/pdf/P09-R2-PCB.pdf`, `output/previews/`, `output/svg/` | Schemat, PCB do recenzji (5 stron, 1:1) i podglądy |
| `routing/` | DSN/SES Freeroutinga, trasy planera, raporty kroków layoutu |
| `docs/J_BP.csv`, `docs/SERWIS.csv` | Kontrakty dla płytki połączeń P12 i dla odbioru |
| `docs/parts.json`, `docs/BOM.csv`, `docs/ZAKUPY.md` | Części, piny, źródło (rejestr/nowe/posiadane), zakupy |
| `docs/PROJEKT.md`, `docs/ODBIOR.md`, `docs/MODUL-KWALIFIKACJA.md` | Opis, formularz odbioru (kołki listwy), kwalifikacja modułu (lutowanie wprost od 1.10) |
| `reference/` | Części P02-R3/J9 i P03-R2/J7 (sprawdzenie ciągłości sygnałów z R1) |
| `verification/` | ERC, netlista, kontrole, próby ujemne, logi, manifest |
| `src/` | Generatory (`cadlib.py`, `parts.py`, `build_schematic.py`, `make_docs.py`, kontrole, `run_schematic.py`); layout: `board.py`, `placement.py`, `build_board.py`, … `verify_pcb.py`, `negative_controls.py`, `make_pdf.py`, `run_release.py` |
