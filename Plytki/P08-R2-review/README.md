# P08 R2 — SENSOR w formacie S1 (schemat i PCB)

5.10.2026, sesja w chmurze, zadanie `Plytki/Format-S1/zadania/ZADANIE-P08-S1.md`. Schemat z sesji w chmurze; **PCB 5.10.2026 lokalnie** (Ubuntu 24/7, KiCad 10.0.6 w Dockerze; sekcja „PCB”), paczka zamówieniowa `Plytki/P08-PCB-R2-zamowienie`. Sprzęt NIE ZBADANY. R2 powstała na kopii generatora z `Plytki/P08-R1-review` (zamknięty pakiet, niezmieniony).

**Klasa płytki:** 1/3 (53 × 100 mm), **slot S1 poziomu 5** (S1-3, wariant pełny; S2–S3 tego poziomu zajmie P07). Poziom 5 nie jest wysoki: od góry ≤ 16,5 mm, od spodu tylko SMD ≤ 1,5 mm bez SOIC.

**Obwód R1 bez zmian:** TPS2553 (limit ok. 99–139 mA), przekaźnik G6K-2P-Y rozłączający plus i powrót, TBD62083, nadzorcy MCP120 (U6, U7 i strażnik EN U8), bramki HC08, bufory 74LVC125 z Ioff. Kontrola `R1-CIRCUIT-PARITY` porównuje każdy pin każdej części obwodu z netlistą R1 (`reference/P08-R1.xml`): 0 różnic, wartości te same. Opis działania i obliczenia: `docs/PROJEKT.md` (z R1).

## Zmiany R1 → R2

| Element | R1 | R2 |
|---|---|---|
| Połączenia z P02 / P04 / P03 | wiązki lutowane: J1 LV08 (Mini-Fit 4p), J2 SENSOR (IDC6, KEY2), J3 SFAULT (IDC6, KEY3) | **J1 = J_BP**, kątowe obudowane IDC **2×8** na krawędzi A, środek x = 26,5 mm, pin 1 od mniejszego x; nieparzyste GND |
| J4 TSENSOR | Mini-Fit Jr 2p na płytce, wiązka W4 po stronie P11 | **pole przewodów** 2 × AWG22 z kotwą 12 mm przy krawędzi x = 0 (strona panelu), para do portu TEST na panelu; numeracja J4 i pinów bez zmian |
| Punkty pomiarowe | TP1–TP13 (pola) | **J2 = listwa serwisowa** kątowa 1×13 na krawędzi B, GND na 1 i 13, 11 kołków przez R19–R29 przy węzłach (1 kΩ; TPS_EN 10 kΩ) |
| Rezystory | DIN0207 leżące | nowe **SMD 1206**; posiadane **R15 4,7 k (MF0207)** i **R16 6,8 k (MF0204)** na stojąco |
| Kondensatory | 0805, C10 elektrolit | nowe **SMD 1206 X7R**; C10 22 µF/25 V elektrolit bez zmian (nowy, bo dwa z rejestru bierze P02 R4) |
| U4/U5 SOIC14 | przez adapter SO14 | lutowane wprost od góry |
| Obrys | 100 × 80 mm | 53 × 100 mm, otwory slotu M3 wg S1 (rysuje layout) |

### J_BP (`docs/J_BP.csv`)

| Pin | Sieć | Pin | Sieć |
|---|---|---|---|
| 1 | GND | 2 | 5V_SYS |
| 3 | GND | 4 | 3V3_IO |
| 5 | GND | 6 | SENSOR_PERMIT (wejście, z P04) |
| 7 | GND | 8 | SENSOR_OK (wyjście, do P04) |
| 9 | GND | 10 | SENSOR_HEALTHY (wyjście, do P03 R6 J_BP1.12) |
| 11 | GND | 12 | GND (zapas masy) |
| 13 | GND | 14 | GND (zapas masy) |
| 15 | GND | 16 | 5V_SYS |

Nazwy sieci dokładnie jak w `P08-R1-review/docs/interfejsy.csv` i `P04-R2.2-review` J4 (SENSOR_PERMIT, SENSOR_OK) oraz w P03 R6 J_BP1.12 (SENSOR_HEALTHY, wejście P03; w kontraktach P12 „czeka na P08”). P12 łączy po nazwie.

### Listwa serwisowa (`docs/SERWIS.csv`)

1 GND, 2 5V_SYS, 3 3V3_IO, 4 SUP3_N, 5 SUP5_N, 6 SENSOR_OK, 7 SENSOR_HEALTHY, 8 PERMIT_LOCAL, 9 SENSOR_LOCAL, 10 TPS_EN (10 kΩ), 11 SENSOR_LIMITED, 12 SENSOR_FAULT_LOCAL_N, 13 GND. Pin 1 od większego x (kątowa listwa od góry; jak P09/P10 R2). Formularz odbioru z mapą TP R1 → kołki: `docs/ODBIOR.md`.

## Wyniki (`verification/QA.md`)

| Kontrola | Wynik |
|---|---|
| ERC (4 arkusze A3) | 0 naruszeń |
| Netlista pin po pinie względem `parts.py` | 52 części, 194 piny, 49 sieci, 0 błędów |
| Kontrole elektryczne | 49/49 PASS — obwód R1 (TPS, K1, U8, bramki, tabela prawdy 16 przypadków na rzeczywistych pinach, marginesy dzielnika EN) oraz nowe: J_BP (2×8, nieparzyste GND, zapasowe 12/14 GND bez sieci NC, format CSV jak P06 R2, ciągłość z trzema wiązkami R1, 5V_SYS ×2, kierunki, zgodność z CSV), kontrakty nazw z P04 R2.2 / P03 R6 / P02 R4 / P12, J4, listwa (≤ 13, GND na końcach, rezystor przy węźle, wartości, pokrycie ODBIOR, brak kołka na wyjściu czujnika), źródła części, zgodność obwodu z R1 |
| Próby ujemne | 49/49 mutacji wykrytych, próba zerowa czysta |
| Ocena powierzchni (`src/powierzchnia.py`, bez rozmieszczenia) | suma prostokątów obrysów 2356 mm² wobec 4486 mm² użytecznych (53 %); bez J1 i J2, które leżą w odjętych już pasach krawędzi A/B, ok. 1490 mm² (33 %) |

## Decyzje (sporne oznaczone)

1. **Sporne: J_BP 2×8, nie 2×5 z budżetu S1 §8.** Trzy sygnały + 5V_SYS ×2 (S1 §5) + 3V3_IO to 6 pinów parzystych, a 2×5 ma 5. Przyjęte przez użytkownika 5.10 (2×8 zostaje); wolne piny 12 i 14 są dodatkową masą w taśmie, a nie siecią „NC” (kontrakty P12 widziałyby ją jako sieć z jednym końcem).
2. **5V_SENSOR i AGND_SENSOR nie są na listwie** (przyjęte 5.10) (w R1 były TP12/TP13). Listwa mieści 11 węzłów, a kołek AGND_SENSOR obok GND pozwoliłby zsuniętą sondą ominąć styk powrotu K1. Wyjście mierzy się różnicowo na porcie TEST (para J4), tak jak R1 i tak wymagał (WIAZKI R1). Zwolnione miejsce bierze PERMIT_LOCAL (próba E10).
3. TPS_EN przez 10 kΩ (węzeł dzielnika R15/R16, S1 §6); pozostałe kołki przez 1 kΩ, także węzły z podciąganiem 10 kΩ (SUP3_N, SUP5_N, FAULT_N) — zwarcie kołka do GND tylko wymusza stan „niegotowe”, nic nie uszkadza.
4. J4 zachowuje numer i piny R1 (kontrakt W4 do P11); pole przewodów zamiast Mini-Fit, kotwa przy krawędzi x = 0 jak J4/J6 w P05 R3.
5. Posiadane THT według bilansu rejestru (`docs/ZAKUPY.md`): R15 MF0207 4,7 k i R16 MF0204 6,8 k (ostatnia sztuka), U3/U4/U5/U6/U7/D1 z przydziału P08. **U8 (drugi MCP120-300) trzeba dokupić** — zamówienie z 24.09 miało jedną sztukę dla P08.
6. U2 zostaje TBD62083APG w DIP18 (obwód R1 bez zmian), choć jest największą częścią poza złączami (ok. 230 mm² obrysu).

## PCB (5.10.2026; `src/run_release.py`, KiCad 10.0.6 w Dockerze)

| Kontrola | Wynik | Raport |
|---|---|---|
| DRC świeży, wszystkie poziomy, ze zgodnością ze schematem | 0 niepołączonych, 0 niezgodności, 0 innych naruszeń; 2 × `lib_footprint_mismatch` (J1, J2: nadruk przycięty przez `silkscreen.py`, przyjęte jawnie) | `verification/drc.json` |
| Kontrole PCB (`verify_pcb.py`) | 28/28 | `verification/pcb-checks.json`, `QA-PCB.md` |
| Próby ujemne PCB | 27/27 z próbą zerową | `verification/negative-controls.json` |
| Trasowanie | Freerouting 2.1.0 (GND jako płaszczyzna B.Cu), pierwsza próba; zablokowane: tor czujnika, wiązanie C1–U1.2 z przelotką, odsprzęganie U6–U8; planer: 1 trasa, 2 wiązania powrotu GND (`--ties`); 65 przelotek; ścieżki F.Cu 1,11 m, B.Cu 0,53 m | `routing/attempts.json`, `completion-routes.json`, `return-ties.json` |

**Zajętość:** obrysy części od góry 2168 mm² z 5146 mm² użytecznych (42 %; bez J1 / J2 w pasach krawędzi 1311 mm², 25 %), od spodu 121 mm² (tylko R19–R29). Obwód zmieścił się w klasie 1/3 z zapasem: dolna ćwiartka płytki (y 75–93) jest pusta.

Łańcuch: skrypty generyczne z P05 R3 (po recenzji 2.10: `complete_routes.py --ties`, `stitch.py --targeted`, `trim_stubs.py`, `gndpath.py`), części 1/3 z P10 R2 / P09 R2 (`silkscreen.py`, `verify_pcb.py`, `negative_controls.py`, `make_pdf.py`), wartości płytki w `src/board.py`. `run_release.py` odtwarza zapisany wynik routera (`routing/P08.ses`) i trasy planera. PDF (5 stron) obejrzany 5.10.2026.

**Decyzje (sporne oznaczone):**
1. Rozmieszczenie: blok czujnika przy panelu (x = 0) — J4, K1, U1, D1, U2, U8 / R15 / R16; logika pod J1 (U5 wejście / HEALTHY, U4 nadzorca 5 V / OK, U3 HC08, U6 / U7 w prawej kolumnie). Od spodu tylko rezystory serwisowe R19–R29 (SMD 1206, ≥ 1 mm od pól THT); U4 / U5 SOIC i U1 SOT-23-6 od góry (poziom 5: od spodu bez SOIC).
2. **J4 (para W4 do portu TEST)** obrócone tak, że kotwa opaski (2 × Ø3,2) leży 12 mm od pól w stronę panelu, krawędź otworu 1,9 mm od x = 0 (kontrola 1,5–6 mm, jak J4 / J6 P05 R3); Ø6 bez miedzi wokół otworów kotwy na obu warstwach. Pole 1 (5V_SENSOR, kwadratowe, nadruk „1”) pod polem 2 (AGND_SENSOR).
3. **Tor czujnika przez K1 zablokowany, 0,6 mm:** U1.6 → K1.3 3,6 mm, K1.4 → J4.1 (5V_SENSOR, F.Cu) 7,2 mm, K1.5 → J4.2 (AGND_SENSOR, B.Cu) 5,3 mm — linie plusa i powrotu krzyżują się na różnych warstwach (wszystkie końce to pola PTH). Styk powrotu K1.6 połączony z wylewką GND bez mostków termicznych. Klasa PWR (0,6 / 0,3 mm) obejmuje 5V_SYS i trzy sieci toru; kontrola szerokości: 5V_SYS ≥ 0,6, tor ≥ 0,5 mm.
4. Powroty odsprzęgania (kontrola z P05 R3, ≤ 1,3 × odległość + 3 mm przez miedź GND): C1 ma ścieżkę GND 0,5 mm wprost do U1.2 (środkowy pin boku SOT-23-6) z przelotką do płaszczyzny B.Cu, przez którą wraca też C2; C6–C8 stoją pod pinami VDD / VSS nadzorców TO-92 z zablokowanymi połączeniami (wcześniejszy przebieg routera zostawił U8.3 45 mm miedzi od C8).
5. Wysokości: najwyższy C10 ok. 12,5 mm (szacunek), K1 G6K 5,2 mm (karta), U2 DIP18 5,33 mm (JEDEC MS-001), U3 w podstawce ok. 8,5 mm, TO-92 ok. 8 mm — limit 16,5 mm z zapasem.
6. Nadruk: tytuł `P08 R2 S1-1/3 S1`, znaczniki krawędzi, pin 1 J1 / J2 / J4, etykiety listwy do 7 znaków (SNS_OK, HEALTHY, PERMIT, SNS_LOC, TPS_EN, SNS_LIM, FAULT_N; pełne nazwy w `docs/SERWIS.csv`). Osiem oznaczeń bez miejsca (R16, R10, R11, R18, R6, R9, C1, U1) jest tylko na rysunku montażowym z F.Fab (strona 2 PDF). Tekst ≥ 1,0 / 0,15 mm.
7. Pin 1 listwy J2 od większego x (x = 41,74 mm) — jak P09 / P10 R2.

## Uruchomienie

PCB: `scripts/egrlab-docker python3 src/run_release.py` (ok. 10 min): łańcuch schematu, layout (odtwarza `routing/P08.ses`; `--new-route` uruchamia Freerouting z obrazu), nadruk, reguły, `verify_pcb.py`, próby ujemne, widoki, PDF, `QA-PCB.md`, manifest.

Sam schemat: `scripts/egrlab-docker python3 src/run_schematic.py` (ok. 15 s): budowa schematu, `make_docs.py` (J_BP.csv, SERWIS.csv, interfejsy.csv, ZAKUPY.md), ERC, netlista, `verify_schematic.py`, `verify_electrical.py` z próbami ujemnymi, `powierzchnia.py`, PDF i PNG, `QA.md`, manifest SHA-256 (`verification/manifest.json`).

## Zawartość

| Ścieżka | Zawartość |
|---|---|
| `eda/` | Projekt KiCad 10 (4 arkusze A3, `P08.kicad_pcb`), biblioteki lokalne |
| `output/pdf/P08-R2-schemat.pdf`, `output/pdf/P08-R2-PCB.pdf`, `output/previews/`, `output/svg/` | Schemat, PCB do recenzji (5 stron, 1:1) i podglądy |
| `docs/J_BP.csv`, `docs/SERWIS.csv` | Kontrakty dla P12 i dla odbioru |
| `docs/parts.json`, `docs/BOM.csv`, `docs/ZAKUPY.md` | Części, piny, źródło (rejestr/nowe), bilans rejestru |
| `docs/interfejsy.csv`, `docs/WIAZKI.md` | Jedyny przewód: W4 TSENSOR do portu TEST |
| `docs/ODBIOR.md`, `docs/PROJEKT.md` | Formularz odbioru (kołki listwy), działanie i obliczenia z R1 |
| `requirements/KONTRAKT-R1.md` | Kontrakt wydania R1 (zachowanie obwodu obowiązuje dalej) |
| `reference/` | Netlista R1, piny złączy P02-R3/P03-R2/P04-R2.1 (ciągłość z R1), P02 R4/P03 R6/P04 R2.2 (kontrakty), kontrakty P12, karty katalogowe |
| `routing/` | DSN / SES Freeroutingu, trasy planera, raporty layoutu (zszywanie GND, nadruk) |
| `verification/` | ERC, netlista, kontrole schematu i PCB, próby ujemne, DRC, ocena powierzchni, logi, manifest |
| `src/` | Generatory i kontrole schematu (`parts.py`, `build_schematic.py`, `make_docs.py`, `verify_*.py`, `run_schematic.py`) i łańcuch PCB (`board.py`, `placement.py`, `route_critical.py`, `run_layout.py`, `verify_pcb.py`, `negative_controls.py`, `run_release.py`) |

## Otwarte

- Przymiarka wydruku 1:1 (strona 5 `output/pdf/P08-R2-PCB.pdf`): K1, U1, kotwa J4 i przebieg pary W4 do panelu; wysokości oznaczone jako szacunek.
- Długość pary W4 i typ portu TEST — z makiety panelu S1.
- Przydział części z rejestru względem równoległej P04 R3 (HC08, LVC125) — lista zakupowa wiążąca.
