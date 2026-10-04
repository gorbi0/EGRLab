# P11 PANEL — R2, schemat w formacie S1

*4.10.2026. Sesja w chmurze według `Plytki/Format-S1/zadania/ZADANIE-P11-S1.md` i decyzji P11-1…P11-7 (`Plytki/P11-S1-przygotowanie/README.md`). Zamknięty pakiet R1 bez zmian. PCB: 4.10.2026 wieczorem, komputer 24/7 (sekcja „PCB”).*

**Status: schemat i PCB gotowe do zamówienia** (paczka `Plytki/P11-PCB-R2-zamowienie`). Sprzętu nie zbudowano.

## Co zrobione

P11 jest odchudzona (P11-1): na płytce zostaje tylko logika styków z R1 i złącze do P12. Elementy:

| Ref | Funkcja |
|---|---|
| J_P12 | IDC 2×10 **kątowe** do P12 (PANELCORE + PANELSAFE), na krawędzi P11 od strony ściany A; zastępuje J4 i J5 z R1 |
| R1 | 100 Ω 1206, 3V3_IO → PANEL_3V3; **LOGGER: obsadzony, wariant z P04: DNP** (P11-3; widoczne pole „Wariant” przy symbolu) |
| J11 | pole 18 przewodów do styków panelu (przypisanie jak R1 J11.1–18) |
| J8 | 2 pola: komory 10/11 portu TEST (LOOP_OUT, MECH_OK) |
| J6 / X6 | trigger SCOPE do izolowanego BNC (jak R1) |
| X2 / X3 / X8 | porty AT04-12: L1 klucz B, L2 klucz C, TEST klucz A — jak R1 (poza P11; tylko TEST 10/11 na P11) |
| X11–X17 | ARM, detektory L1/L2 (2NC), MARK, kluczyk, STOP, detektor TEST — **styki złocone** (P11-7), bez MPN |

Pinout J_P12 (`docs/J_P12.csv`): 1 GND, 2 PANEL_3V3, 3 GND, 4 MECH_OK, 5 GND, 6 STOP_NC_OUT, 7 GND, 8 ARM_CONTACT, 9 GND, 10 N_J_SCOPE_HOT, 11 GND, 12 GND, 13 MARK, 14 TEST_KEY, 15 LOGGER_CLEAR, 16 TEST_PRESENT, 17 GND, 18 GND, 19 GND, 20 3V3_IO. Piny 10/13–16 leżą jak w P03 R6 J_BP1, więc P12 prowadzi je prosto. 13 i 15 to ten sam wyjątek od GND na nieparzystych co w P03. 3V3_IO jest na 20, z dala od PANEL_3V3: zwarcie sąsiednich żył taśmy nie ominie R1 i nie da drugiego źródła przy P04.

Lista sieci R1 → R2 z uzasadnieniem: `docs/sieci-R1-R2.csv`. Skrót: logika styków (TEST_KEY, ILK_L1_L2, DIAG_L1_L2, LOOP_OUT, MECH_OK, LOGGER_CLEAR, STOP_NC_OUT, TEST_PRESENT, ARM_CONTACT, MARK, N_J_SCOPE_HOT, PANEL_3V3) bez zmian. ECU_P1/EGR_P1/T_EGR_P1/P3 wychodzą z P11 (P11-4: przewody z portów), TAP_P1–P6 też (P11-5: końcówki P05 J4), 5V_SENSOR/AGND_SENSOR wychodzą razem z J10 (P11-1). Nowa jest 3V3_IO (P11-3). Komory portów: `docs/PORTY.csv` — numeracja komór jak w R1, więc adaptery AL1/AL2/AT zostają bez zmian. Przewody: `docs/WIAZKI.md`.

## Kontrole

`scripts/egrlab-docker python3 src/run_schematic.py` (ok. 15 s). Wyniki w `verification/QA.md`.

- ERC **0** na 3 arkuszach; netlista 104/104 pinów zgodnych z `parts.py`, 16 części.
- `verify_electrical.py`: **35/35**, mutacje **22/22**. Sprawdza:
  - styki i pole J11 identyczne z R1, brak sieci silnika/TAP/czujnika, 3V3_IO tylko do R1;
  - **dokładnie jedno źródło PANEL_3V3 w każdym wariancie** (LOGGER: R1; pełny: P04 R40, R1 DNP — próby ujemne: R1 obsadzony przy P04, brak R1 w LOGGER, R1 omijany);
  - model węzłowy **256 stanów** (kluczyk, L1, L2, mostek TEST, STOP, wtyk TEST, ARM, MARK) × 2 warianty z obciążeniami odbiorników P03 R6 i P04-R2.1, szyna 3,18 V dla H / 3,42 V dla L;
  - przerwa przewodu gasi MECH, zwarcie PANEL_3V3–GND, przyciski złocone.
- Wyniki: LOGGER — minimalne H 3,086 V (próg 2,0 V), pobór z 3V3_IO ≤ 0,94 mA, prąd zamkniętego styku ok. 0,31–0,32 mA. Pełny — SAFE_N 2,748 V, wejścia P04 po 1 kΩ 2,748 V, 27,8 µA przez STOP (zgodnie z R1 `panel-budget.json`). Zwarcie PANEL_3V3–GND: 118 mW w R1 (1206, 0,25 W).
- `verify_p12.py`: **22/22**, mutacje **13/13** przez kontrolę docelową, próba zerowa czysta. Sprawdza: pozycje i kierunki względem P03 R6 J_BP1, wszystkie sieci czekające na P11 w kontraktach P12, sieci PANELSAFE z P04-R2.1 J8, 3V3_IO (źródło P02 R4), GND na nieparzystych, sąsiedztwo 3V3_IO/PANEL_3V3, GND wokół SCOPE, `J_P12.csv` = netlista.
- PDF: `output/pdf/P11-R2-schemat.pdf`.

Ograniczenia: model pełnego wariantu używa zamrożonego P04-R2.1 (P04 w S1 jeszcze nie ma). Model jest statyczny: bez drgań styków i bez budżetu upływności. Footprinty pól przewodów: raster 3,5 mm, otwór 1,1 mm, pole 2,3 mm; przy layoucie (4.10) pola numerowane kolumnami (sekcja „PCB”).

## Decyzje użytkownika 4.10 (wprowadzone)

1. **Klucze portów jak w R1:** L1 = B, L2 = C, TEST = A (AT04-12PB / PC / PA). Adaptery AL1 / AL2 / AT zachowują wtyki. Poprawione w `parts.py`, BOM, `PORTY.csv`, schemacie i tu.
2. **Prąd silnika** (L1.1/L1.2 → P06 J3, TEST.1/TEST.2 → P07): przewód **2,0 mm² (AWG14) na całej długości**, styki złocone **AT60-215-1631** (pin, port) / **AT62-209-1631** (gniazdo, adapter). P11 nie przenosi tego prądu. Zapisane w `WIAZKI.md`, `PORTY.csv`, BOM (X2, X8) i na arkuszu PORTY.
3. **TAPy:** mostki przy portach (odpowiadające sobie TAPy trzech portów), jedna wiązka 5 par do P05 J4, masa z komory 12 do GND na J4 — przyjęte.
4. **J_P12:** piny 12 i 18 zostają GND. Złącze IDC 2×10 **kątowe** (`IDC-Header_2x10_P2.54mm_Horizontal`) na krawędzi P11 od strony ściany A. P11 leży poziomo na dnie strefy panelu, maks. ok. 45 × 130 mm (`Plytki/P11-S1-przygotowanie/README.md`, P11-6).

Poprawki z recenzji: notatka o stykach złoconych wskazuje `verification/QA.md` (prąd zamkniętego styku: LOGGER ok. 0,31–0,32 mA, wariant pełny 0,03–0,87 mA); tabelka rysunkowa bez „PCB”, komentarz skrócony do ramki; R1 ma widoczne pole „Wariant: LOGGER: obsadzony / z P04: DNP”; zwarcie PANEL_3V3–GND opisane jako 34 mA / 0,12 W (zgodnie z modelem: 118 mW).

## PCB (4.10.2026, `src/run_release.py`, KiCad 10.0.6 + Freerouting 2.1.0 w Dockerze)

**Wymiary 36 × 100 mm** (limit 45 × 130 mm), narożniki R1, FR4 1,6 mm, 2 × 35 µm, JLCPCB. Płytka leży poziomo na dnie strefy panelu; układ współrzędnych: x = 0 to długi bok od strony panelu, y = 0 to krótka krawędź od strony ściany A.

| Kontrola | Wynik | Raport |
|---|---|---|
| DRC świeży, wszystkie poziomy, ze zgodnością ze schematem | 0 niepołączonych, 0 niezgodności, 0 innych naruszeń; 1 × `lib_footprint_mismatch` (J_P12: nadruk przycięty przy krawędzi przez `silkscreen.py`, przyjęte jawnie jak w P10 R2) | `verification/drc.json` |
| Kontrole PCB (`verify_pcb.py`) | **20/20** | `verification/pcb-checks.json`, `QA-PCB.md` |
| Próby ujemne PCB | **29/29** z próbą zerową; każda z 20 kontroli ma co najmniej jedną wadę, którą wykrywa | `verification/negative-controls.json` |
| Trasowanie | Freerouting, pierwsza próba, bez tras planera; ścieżki 0,3 mm, PANEL_3V3 i 3V3_IO 0,4 mm (klasa P3V3); wylewki GND F.Cu 71,9 %, B.Cu 79,9 %, 62 przelotki zszywające | `routing/` |

Kontrole sprawdzają: obrys w limicie, 4 otwory M3 w narożnikach ze strefami Ø7 bez miedzi i części, J_P12 na krawędzi y = 0 (wtyk równo z krawędzią, pin 1 od mniejszego x z nadrukiem „1”, pinout = `docs/J_P12.csv`), pola przewodów (otwór 1,0–1,1 mm, pole ≥ 2,0 mm, kotwy Ø3,2 między polami a krawędzią panelu, 3 mm bez miedzi wokół kotew, pas pod przewodami bez części), **opis każdej kolumny pola rozwiązywany niezależnie ze schematu** (Xnn.a-b → piny styku w `parts.json`, „TEST kom.N” → `PORTY.csv`, SCOPE → X6), opis wariantu R1 zgodny z `parts.json`, nadruk ≥ 1,0 / 0,15 mm (też reguła DRC), szerokości ścieżek, wylewki i zszycie, położenie oznaczeń.

**Decyzje layoutu (sporne oznaczone):**
1. **Górne otwory M3 za J_P12 (y = 19 mm), nie w samym narożniku** — korpus IDC 2×10 (33 mm) zajmuje krótką krawędź; otwór przy y = 4 wymagałby szerokości ≥ 49 mm. Dolne otwory 4 mm od obu krawędzi. *Sporne:* jeśli dystanse muszą stać w narożnikach, płytka musi mieć ≥ 49 mm szerokości.
2. Wszystkie pola przewodów przy długim boku od strony panelu (x = 0): J11 (y 28,5–56,5), J8 (68 / 71,5), J6 (83 / 86,5); przewody wychodzą prosto w stronę panelu przez kotwy opasek (środki 4,5 mm od krawędzi, brzeg otworu 2,9 mm). Każde pole ma własną kotwę (2 × Ø3,2 NPTH, 10,5 mm przed pierwszym rzędem pól).
3. **J11 numerowany kolumnami** (zmiana footprintu `FIELD_CONTACT18` w `parts.py`, netlista bez zmian): kolumna = para przewodów jednego styku z R1 (W8: 1–2 kluczyk X15, 3–4 / 5–6 L1 X12, 7–8 / 9–10 L2 X13, 11–12 STOP X16, 13–14 ARM X11, 15–16 MARK X14, 17–18 detektor TEST X17), więc każda kolumna ma jeden opis „Xnn.a-b NAZWA”. Pole 1 kwadratowe, kolumna 1 najbliżej J8.
4. J8: „TEST kom.10” (LOOP_OUT), „TEST kom.11” (MECH_OK); J6: „SCOPE srodek” (pole 1, kwadratowe), „SCOPE ekran” (GND).
5. R1 między J_P12.20 (3V3_IO) a polem PANEL_3V3, obok nadruk „R1 100R / LOGGER: LUTOWAC / Z P04: DNP”.
6. Pole J11.15 (GND, przewód MARK) ma pełne połączenie z wylewką (DRC `starved_thermal` przy odciążeniach) — lutować grotem o większej mocy.
7. Bez listwy serwisowej (pytanie 6) — wszystkie sieci są na polach przewodów i na J_P12.

**Otwarte:** przymiarka wydruku 1:1 (strona 5 PDF `output/pdf/P11-R2-PCB.pdf`) w strefie panelu; długości przewodów do styków i wysokość IDC (ok. 9,2 mm) względem portów z makiety; MPN gniazda IDC kątowego (zakupy).

Uruchomienie: `scripts/egrlab-docker python3 src/run_release.py` (ok. 4 min): schemat, layout (odtwarza `routing/P11.ses`; `--new-route` uruchamia Freerouting), nadruk, reguły, `verify_pcb.py`, próby ujemne, widoki, PDF, `QA-PCB.md`, manifest. Skrypty layoutu to kopie z P10 R2 (`board.py` z wartościami płytki; `placement.py` z jawnymi pozycjami; `route_critical.py` tylko eksportuje DSN).

## Pytania do użytkownika

Pytania 1–5 zamknięte decyzjami 4.10 (wyżej).

6. **Listwa serwisowa:** P11 nie ma listwy z krawędzi B, bo nie stoi w stosie, a wszystkie sieci są dostępne na polach przewodów. Czy wystarczy?
