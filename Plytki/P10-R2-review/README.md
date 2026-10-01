# P10 R2 — CAN pasywny w formacie S1 (schemat i PCB)

29.09.2026, sesja w chmurze (schemat); 30.09.2026 wieczorem, komputer 24/7 (PCB, sekcja „PCB”). **Status: schemat i PCB do lokalnej recenzji**, sprzęt NIE ZBADANO. R2 powstała na kopii generatora z `Plytki/P10-R1-review` (zamknięty pakiet, niezmieniony); wymagania: `Plytki/Format-S1/SPECYFIKACJA-FORMATU-S1.md` (S1-2; przy layoucie S1-3) i zadanie `Plytki/Format-S1/zadania/ZADANIE-P09-P10-S1.md`.

**Klasa płytki:** 1/3 (53 × 100 mm), slot S3 poziomu 4 (format S1-3, `SPECYFIKACJA-FORMATU-S1.md` §7). Schemat R2 powstał jeszcze dla slotu S1 poziomu 1; przy layoucie sprawdzone: wszystkie części stoją od góry, więc zakaz SOIC od spodu na poziomie 4 niczego nie zmienia, a J3 jest przy ścianie wejść. W schemacie zmieniły się tylko teksty (opis arkusza, noty BOM J1/J2). Topologia bez zmian: TCAN1051V z S i TXD na stałe do VIO, PESD2CAN, bufor RX 74LVC125AD z Ioff, brak terminatora, brak ścieżki CAN_TX do transceivera; tylko odbiór.

## Zmiany R1 → R2

| Element | R1 | R2 |
|---|---|---|
| Złącza do innych płytek | J1 LV10 (Mini-Fit 4p) i J2 CAN_CORE (IDC 6) lutowane do PTH | **J1 = J_BP**: kątowe obudowane IDC 2×5, krawędź A, środek slotu; piny nieparzyste GND, parzyste: 5V_SYS ×2 (piny 2, 10), 3V3_IO (4), CAN_TX (6), CAN_RX (8) |
| Wejście OBD | J3, skrętka 300 mm lutowana do PTH | bez zmian (J3, W3) |
| Punkty pomiarowe | TP1–TP6 (pola) | **J2 = listwa serwisowa** kątowy goldpin 1×9 na krawędzi B, GND na kołkach 1 i 9; kołki 2–8 przez R3–R9: 5V_SYS, 3V3_IO, RX_RAW, CAN_RX, CAN_TX (1 kΩ), CAN_H, CAN_L (10 kΩ) |
| R2 (10 k), R8, R9 (10 k serwisowe) | DIN0207 leżący | **posiadane MF0207 na stojąco** (`…P5.08mm_Vertical`) |
| R1 (100 Ω), R3–R7 (1 k) | THT | **nowe SMD 1206** |
| C1–C3 (100 n) | 0805 | **posiadane K104K15X7RF5TH5, radialne 5 mm** |
| C4, C5 (4µ7) | 0805 | **nowe SMD 1206** X7R 25 V |
| U1, U2, D1 | bez zmian | bez zmian |
| Obrys / mocowanie | 80 × 70 mm | 53 × 100 mm, otwory slotu M3 wg S1 (rysuje layout) |

Przypisanie części do rejestru wynika z dosłownego dopasowania wartości i typu do `Zamowione/zamowione.csv` (kolumna `zrodlo` w `docs/BOM.csv`). Bilans zapasu razem z P09: `docs/ZAKUPY.md`.

## Wyniki (szczegóły: `verification/QA.md`)

| Kontrola | Wynik |
|---|---|
| ERC (2 arkusze) | 0 naruszeń |
| Netlista pin po pinie względem `parts.py` | 20 części, 74/74 pinów, 19 sieci, 0 błędów |
| Kontrole elektryczne | 32/32 PASS (w tym nowe: J_BP nieparzyste = GND, parzyste tylko użyte sygnały i zasilania, ciągłość z R1, 5V_SYS ×2, zgodność z `J_BP.csv`; listwa ≤ 13, GND na końcach, rezystor przy węźle, zgodność z `SERWIS.csv`; CAN_TX tylko do J_BP i kołka; źródła części THT/SMD) |
| Próby ujemne | 36/36 mutacji wykrytych, próba zerowa (bez zmiany) czysta |
| Orientacyjna zajętość (`src/powierzchnia.py`) | suma obrysów części 1208 mm² wobec ok. 4486 mm² użytecznej powierzchni 53 × 100 mm (27 %, bez rozmieszczenia) |

## Decyzje projektowe (sporne oznaczone)

- **5V_SYS na dwóch pinach J_BP** — zgodnie z S1 §5 („co najmniej 2 pinach”); wszystkie 5 parzystych pinów 2×5 jest użytych, a P10 pobiera z 5 V ok. 70 mA (transceiver).
- **CAN_H i CAN_L na listwie przez 10 kΩ, nie 1 kΩ** — to węzły zewnętrznej magistrali pojazdu; spadnięta sonda lub zwarcie sąsiednich kołków ma ją obciążać jak najmniej. Wada: pasmo obserwacji kołków ok. 1 MHz, więc przebiegi mierzyć na J3.
- **Kołek CAN_TX zostaje** (przez 1 kΩ), bo próba „brak TX” w odbiorze wymaga wglądu w ten sygnał (R1: TP6); nadal brak jakiejkolwiek ścieżki do U1.
- **Rezystory serwisowe 10 kΩ z rejestru (THT na stojąco)** — dosłowne stosowanie reguły „wartość i typ jak w rejestrze”; zużywa zapas, zob. otwarte punkty.

## PCB (30.09.2026, poprawki po recenzji 1.10.2026; `src/run_release.py`, KiCad 10.0.6 w Dockerze)

| Kontrola | Wynik | Raport |
|---|---|---|
| DRC świeży, wszystkie poziomy | 0 niepołączonych, 0 niezgodności ze schematem, 0 innych naruszeń; 2 × `lib_footprint_mismatch` (J1, J2: nadruk przycięty przez `silkscreen.py`, przyjęte jawnie) | `verification/drc.json` |
| Kontrole PCB (`verify_pcb.py`) | 24/24 | `verification/pcb-checks.json`, `QA-PCB.md` |
| Próby ujemne PCB | 26/26 z zerową | `verification/negative-controls.json` |
| Trasowanie | Freerouting 2.1.0 (GND jako płaszczyzna B.Cu) z zablokowanymi liniami CAN, pierwsza próba, bez tras planera; 41 przelotek; ścieżki 0,3 mm (F.Cu 0,61 m, B.Cu 0,10 m); wylewki GND F.Cu 79 %, B.Cu 89 % (liczone z płytki) | `routing/attempts.json`, `pcb-checks.json` |

Łańcuch jak w P09 R2 (skrypty z P03 R6, wartości płytki w `src/board.py`); `run_release.py` odtwarza zapisany wynik routera (`routing/P10.ses`). PDF obejrzany (5 stron) 1.10.2026. Wydanie odtworzone ponownie 1.10 po wspólnych poprawkach z P09 (nadruk omija strefy Ø7, próby ujemne dla stref D7 i tytułu, próba `gnd_pour_removed` usuwa wylewkę w pliku zamiast `b.Remove()`); ścieżki, przelotki, części i napisy płytki bez zmian.

**Decyzje (sporne oznaczone):**
1. Slot S3 poziomu 4 (S1-3): wszystkie części od góry (zajętość 27 %), od spodu nic; ścieżki 0,3 mm przy odstępie 0,25 mm (S1 §3).
2. J3 (koniec wiązki W3) przy ścianie wejść: kotwa opaski (2 × Ø3,2 mm, 12 mm od rzędu lutów) w stronę ściany, krawędź otworu 4,4 mm od krawędzi płytki (kontrola: 2–6 mm); przewód leży prosto od lutów przez kotwę do ściany, a pas pod nim jest bez części. Pole 1 (CAN_H, kwadratowe, nadruk „H”) ma mniejsze y: patrząc od ściany wejść wzdłuż przewodu jest po prawej, jak w `docs/WIAZKI.md`; pole 2 — „L”.
3. Pola bez miedzi Ø6 wokół otworów kotwy na obu warstwach (opaska nie leży na ścieżkach), kółka na F.Fab. **Wokół pól J3 pierścień 1 mm bez innej miedzi** (lutowane ręcznie przewody; recenzja 1.10: SRV_CAN_TX szła 0,26 mm od pól) — na F.Cu z wąskim kanałem dla linii do D1, na B.Cu pełny; zmierzone 1,27 mm.
4. **CAN_H i CAN_L idą z J3 przez pola D1 do U1** (zablokowane ścieżki z `route_critical.py`; recenzja 1.10: CAN_H dochodził do D1 odgałęzieniem 3 mm). Obejście korpusu D1 1,4 mm od rzędu pól zostawia miejsce na przelotkę GND pola D1.3; korytarz linii zablokowany przy rozmieszczaniu. Środki pól D1 3,2 mm od środków pól J3. Za D1: U1, bufor U2, R1 przy wyjściu U2, CAN_RX do J1.8.
5. **Sporne (dokumentacja):** pin 1 listwy J2 od większego x (x = 36,66 mm) — jak w P09 R2 i P03 R6; kolejność sygnałów od pinu 1 bez zmian; poprawione: nota BOM J2 i `docs/ODBIOR.md`.
6. Rezystory serwisowe przy węzłach: R3 przy C1 (5V_SYS), R4 przy C2 (3V3_IO), R5 przy U1.4 (RX_RAW), R6 przy R1 (CAN_RX), R7 przy J1.6 (CAN_TX), R8/R9 (10 kΩ) przy J3; ścieżki od rezystorów do J2 są długie, ale idą za rezystorem (S1 §6). Etykiety listwy sprawdzane z tabelą nazw `LABEL` w `silkscreen.py`, nie z wynikiem nadruku.
7. Nadruk: tytuł z klasą i slotem `P10 R2 S1-1/3 S3` (S1 §9); każde oznaczenie stoi bliżej swojej części niż innych (recenzja 1.10: R1 był 1 mm od R5) — trzy oznaczenia, które się nie mieszczą (R1, R3, D1), są na rysunku montażowym z warstwy F.Fab (strona 2 PDF). Pas zastrzeżony krawędzi A (S1 §5) wolny. Wysokość przewodu W3 z opaską ok. 6 mm to szacunek.

**Otwarte:** przymiarka wydruku 1:1 (strona 5 PDF; kotwa J3 i przebieg przewodu do ściany wejść), recenzja; paczka produkcyjna dopiero po „scal”.

## Otwarte punkty

1. Zapas z rejestru: 10 k — P09 + P10 razem 9 szt. wobec 7; 100 n — razem 6 szt. wobec 5 (opis PR).
2. Listwa serwisowa musi być **kątowa** (posiadana 1×40 jest prosta); typ IDC J_BP do wyboru w zakupach.
3. J3 (OBD) i kotwa 12 mm: w layoucie przy ścianie wejść (x = 53 mm, slot S3 poziomu 4; sekcja „PCB”).
4. `docs/MONTAZ.md` i `REPRODUKCJA.md` z R1 nie są przenoszone (dotyczą PCB 80 × 70 mm). Montaż opisuje PDF PCB (strona 2), a odtwarzanie — sekcja „Uruchomienie” niżej. `docs/INTEGRACJA.md` przeniesione (poprawiona jedna linia o TP6).

## Uruchomienie

PCB: `scripts/egrlab-docker python3 src/run_release.py` (ok. 3 min): łańcuch schematu, layout (odtwarza `routing/P10.ses`; `--new-route` uruchamia Freerouting, potrzebny `EGRLAB_FREEROUTING`), nadruk, reguły, `verify_pcb.py`, próby ujemne, widoki, PDF, `QA-PCB.md`, manifest.

Sam schemat: `scripts/egrlab-docker python3 src/run_schematic.py` (ok. 15 s): budowa schematu, `make_docs.py` (CSV dla P12 i zakupy), ERC, netlista, `verify_schematic.py`, `verify_electrical.py`, PDF i PNG, `QA.md`, manifest SHA-256. Lokalnie: Python KiCada 10.0.6, `KICAD_CLI` i `PDFTOPPM`.

## Zawartość

| Ścieżka | Zawartość |
|---|---|
| `eda/` | Projekt KiCad 10 (2 arkusze A3, `P10.kicad_pcb`), biblioteki lokalne |
| `output/pdf/P10-R2-schemat.pdf`, `output/pdf/P10-R2-PCB.pdf`, `output/previews/`, `output/svg/` | Schemat, PCB do recenzji (5 stron, 1:1) i podglądy |
| `routing/` | DSN/SES Freeroutinga, raporty kroków layoutu |
| `docs/J_BP.csv`, `docs/SERWIS.csv` | Kontrakty dla płytki połączeń P12 i dla odbioru |
| `docs/parts.json`, `docs/BOM.csv`, `docs/ZAKUPY.md`, `docs/interfejsy.csv`, `docs/WIAZKI.md` | Części, piny, źródło (rejestr/nowe), zakupy, jedyna wiązka W3 |
| `docs/ODBIOR.md`, `docs/INTEGRACJA.md` | Formularz odbioru (kołki listwy), zależności firmware |
| `reference/` | Części P02-R3/J10 i P03-R2/J8 (sprawdzenie ciągłości sygnałów z R1) |
| `verification/` | ERC, netlista, kontrole, próby ujemne, logi, manifest |
| `src/` | Generatory (`cadlib.py`, `parts.py`, `build_schematic.py`, `make_docs.py`, kontrole, `run_schematic.py`); layout: `board.py`, `placement.py`, `build_board.py`, … `verify_pcb.py`, `negative_controls.py`, `make_pdf.py`, `run_release.py` |
