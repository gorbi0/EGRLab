# P09 R2 — TEMP w formacie S1 (schemat i PCB)

29.09.2026, sesja w chmurze (schemat); 30.09.2026 wieczorem, komputer 24/7 (PCB, sekcja „PCB”). **Status: schemat i PCB do lokalnej recenzji**, sprzęt NIE ZBADANO. R2 powstała na kopii generatora z `Plytki/P09-R1-review` (zamknięty pakiet, niezmieniony); wymagania: `Plytki/Format-S1/SPECYFIKACJA-FORMATU-S1.md` (S1-2) i zadanie `Plytki/Format-S1/zadania/ZADANIE-P09-P10-S1.md`.

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
| Pozostałe | — | bez zmian (U1–U3, J3/J4 gniazda modułów, JP1/JP2) |
| Obrys / mocowanie | 100 × 100 mm, 4 otwory | 53 × 100 mm, otwory slotu M3 wg S1 (rysuje layout) |

Przypisanie części do rejestru wynika z dosłownego dopasowania wartości i typu do `Zamowione/zamowione.csv` (kolumna `zrodlo` w `docs/BOM.csv`). Bilans zapasu: `docs/ZAKUPY.md`.

## Wyniki (szczegóły: `verification/QA.md`)

| Kontrola | Wynik |
|---|---|
| ERC (4 arkusze) | 0 naruszeń |
| Netlista pin po pinie względem `parts.py` | 46 części, 171/171 pinów, 49 sieci, 0 błędów |
| Kontrole elektryczne | 52/52 PASS (w tym nowe: J_BP nieparzyste = GND, parzyste tylko użyte sygnały i zasilania, ciągłość z R1, 5V_SYS ×2, zgodność z `J_BP.csv`; listwa ≤ 13, GND na końcach, 1 kΩ przy węźle, zgodność z `SERWIS.csv`; źródła części THT/SMD) |
| Próby ujemne | 35/35 mutacji wykrytych, próba zerowa (bez zmiany) czysta |
| Orientacyjna zajętość (`src/powierzchnia.py`) | suma obrysów części 3314 mm² wobec ok. 4486 mm² użytecznej powierzchni 53 × 100 mm (74 %, bez rozmieszczenia; oba gniazda modułów ok. 700 mm² każde) |

## Decyzje projektowe (sporne oznaczone)

- **5V_SYS na dwóch pinach J_BP** — zgodnie z S1 §5 („co najmniej 2 pinach”), choć P09 pobiera z 5 V niewiele (tylko VIN modułów przy JP 2–3 i C5); wszystkie 8 parzystych pinów 2×8 jest użyte.
- **Wszystkie kołki serwisowe po 1 kΩ** — węzły P09 to szyny i logika; 3Vo modułów też (wyjście regulatora, nie węzeł wysokoimpedancyjny).
- **Na listwie brak wejść SCLK/MOSI/TC1_CS/TC2_CS z J_BP** — 11 kołków wystarcza na punkty odbioru specyficzne dla P09 (VIN, 3Vo, CS za buforem, OE, MISO); wejścia mierzy się na listwie P03.
- **FLT/DRDY nieprzyłączone** — bez pól testowych i wolnych żył.

## PCB (30.09.2026 wieczorem, `src/run_release.py`, KiCad 10.0.6 w Dockerze)

| Kontrola | Wynik | Raport |
|---|---|---|
| DRC świeży, wszystkie poziomy | 0 niepołączonych, 0 niezgodności ze schematem, 0 innych naruszeń; 2 × `lib_footprint_mismatch` (J1, J2: nadruk przycięty przez `silkscreen.py`, przyjęte jawnie) | `verification/drc.json` |
| Kontrole PCB (`verify_pcb.py`) | 22/22 | `verification/pcb-checks.json`, `QA-PCB.md` |
| Próby ujemne PCB | 16/16 z zerową | `verification/negative-controls.json` |
| Trasowanie | Freerouting 2.1.0 (GND jako płaszczyzna B.Cu), pierwsza próba; planer dokańczania: 1 połączenie (SPI3_SCLK przy R3); 49 przelotek; ścieżki 0,3 mm (F.Cu 1,43 m, B.Cu 0,59 m); wylewki GND F.Cu 58 %, B.Cu 71 % | `routing/attempts.json`, `completion-routes.json` |

Łańcuch jak w P03 R6 (te same skrypty, wartości płytki w `src/board.py`): `fanout_gnd.py` (belki GND pod U1/U2, grzebień pod J1), `prepare_routing.py` (GND jako płaszczyzna), Freerouting, `cleanup.py --tidy`, `stitch.py`, `complete_routes.py`. `run_release.py` odtwarza zapisany wynik routera (`routing/P09.ses` + `completion-routes.json`).

**Decyzje (sporne oznaczone):**
1. Ścieżki 0,3 mm przy odstępie 0,25 mm (S1 §3, reguły jak P02-R3); wyjątek 0,2 mm z P03 R6 tu nie obowiązuje.
2. Moduły J3/J4 obrócone o 90°: terminale termopar w stronę ściany wejść (x = 53 mm; S1 §2 i §7 — gniazda termopar są na ścianie wejść), krawędź obrysu modułu 3,5 mm od krawędzi płytki, pin 1 (VIN) u góry rzędu. `docs/MODUL-KWALIFIKACJA.md` opisuje nową orientację (w R1 na płytce 100 × 100 moduł był obrócony o 180°).
3. **Sporne (wysokość):** gniazdo z modułem i terminalem szacowane na 16,5 mm, czyli równo z limitem poziomu 3 (`src/heights.py`: gniazdo ok. 8,5 + płytka modułu 1,0 + terminal ok. 7). Jeśli pomiar (MODUL-KWALIFIKACJA krok 1) da więcej: niższe gniazdo albo inny poziom — decyzja po pomiarze.
4. Otwory podparcia Ø6 z polem Ø8 bez miedzi na obu warstwach (podkładki OD 8 mm słupków M2,5, PROJEKT.md): obszary reguł w `build_board.py`, kółka na F.Fab, kontrola w `verify_pcb.py`.
5. **Sporne (dokumentacja):** pin 1 listwy J2 jest od większego x (x = 41,74 mm). Kątowa listwa od góry z kołkami za krawędzią B nie pozwala inaczej (tak samo J_SV1–3 w P03). Kolejność sygnałów od pinu 1 bez zmian; poprawione: nota BOM J2 (`src/parts.py`) i `docs/ODBIOR.md` („od strony większego x, patrząc od krawędzi B: od prawej”). Kolejność od mniejszego x wymagałaby odwrócenia przydziału kołków w schemacie.
6. Rezystory serwisowe R20–R30 od spodu (SMD 1206, 0,7 mm; S1-2), przy węzłach, ≥ 1,1 mm od pól THT.
7. C6/C7 (1 µF przy VIN modułów) są 6,0 i 5,3 mm od pinu VIN. Moduł wystaje 4,5 mm za pin 1 (obrys), miejsce po lewej zajmuje selektor JP1/JP2, więc 1206 mieści się dopiero między J1 a J3 (najbliżej ok. 5,75 mm). Kontrola ma dla nich próg 6,5 mm; odsprzęganie układów C1–C3 ma próg 6 mm (jest 2,5–3,25 mm).
8. **Sporne (lutowanie):** cztery pola z pełnym połączeniem z wylewką zamiast termicznego (J1.1, J1.3, J4.3, R10.2 — szprychy odcięte przez ścieżki). Przy lutowaniu tych pinów potrzeba więcej ciepła.
9. Sześć oznaczeń ukrytych z braku miejsca (R1, R3, R11, R12, R16, C7); na rysunku montażowym F.Fab są wszystkie.
10. Informacyjnie: tabela budżetu złączy S1 §8 („pierwsze przybliżenie”) podaje dla P09 IDC 2×5; pakiet R2 ma 2×8 (poza pięcioma sygnałami SPI/CS niesie 5V_SYS ×2 i 3V3_IO) — do uwzględnienia przy P12.

**Otwarte:** przymiarka wydruku 1:1 z modułami (strona 5 PDF), wysokość gniazda z modułem (szacunek = limit), recenzja; paczka produkcyjna dopiero po „scal”.

## Otwarte punkty

1. Przymiarka 1:1 modułów MAX31856 XU i kwalifikacja zasilania (`docs/MODUL-KWALIFIKACJA.md`) — bez zmian względem R1; obrys gniazd nadal prowizoryczny.
2. PCB do recenzji (sekcja „PCB”): przymiarka 1:1 z modułami, wysokość gniazda z modułem, punkty sporne 3, 5 i 8.
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
| `docs/parts.json`, `docs/BOM.csv`, `docs/ZAKUPY.md` | Części, piny, źródło (rejestr/nowe), zakupy |
| `docs/PROJEKT.md`, `docs/ODBIOR.md`, `docs/MODUL-KWALIFIKACJA.md` | Opis, formularz odbioru (kołki listwy), kwalifikacja modułu (bez zmian) |
| `reference/` | Części P02-R3/J9 i P03-R2/J7 (sprawdzenie ciągłości sygnałów z R1) |
| `verification/` | ERC, netlista, kontrole, próby ujemne, logi, manifest |
| `src/` | Generatory (`cadlib.py`, `parts.py`, `build_schematic.py`, `make_docs.py`, kontrole, `run_schematic.py`); layout: `board.py`, `placement.py`, `build_board.py`, … `verify_pcb.py`, `negative_controls.py`, `make_pdf.py`, `run_release.py` |
