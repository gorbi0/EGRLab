# P11 PANEL — R2, schemat w formacie S1

*4.10.2026. Sesja w chmurze według `Plytki/Format-S1/zadania/ZADANIE-P11-S1.md` i decyzji P11-1…P11-7 (`Plytki/P11-S1-przygotowanie/README.md`). Zamknięty pakiet R1 bez zmian. Bez PCB — layout robi sesja lokalna.*

**Status: schemat do recenzji lokalnej.** Sprzętu nie zbudowano.

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

Ograniczenia: model pełnego wariantu używa zamrożonego P04-R2.1 (P04 w S1 jeszcze nie ma). Model jest statyczny: bez drgań styków i bez budżetu upływności. Footprinty pól przewodów (raster 3,5 mm, otwór 1,1 mm) to propozycja do layoutu.

## Decyzje użytkownika 4.10 (wprowadzone)

1. **Klucze portów jak w R1:** L1 = B, L2 = C, TEST = A (AT04-12PB / PC / PA). Adaptery AL1 / AL2 / AT zachowują wtyki. Poprawione w `parts.py`, BOM, `PORTY.csv`, schemacie i tu.
2. **Prąd silnika** (L1.1/L1.2 → P06 J3, TEST.1/TEST.2 → P07): przewód **2,0 mm² (AWG14) na całej długości**, styki złocone **AT60-215-1631** (pin, port) / **AT62-209-1631** (gniazdo, adapter). P11 nie przenosi tego prądu. Zapisane w `WIAZKI.md`, `PORTY.csv`, BOM (X2, X8) i na arkuszu PORTY.
3. **TAPy:** mostki przy portach (odpowiadające sobie TAPy trzech portów), jedna wiązka 5 par do P05 J4, masa z komory 12 do GND na J4 — przyjęte.
4. **J_P12:** piny 12 i 18 zostają GND. Złącze IDC 2×10 **kątowe** (`IDC-Header_2x10_P2.54mm_Horizontal`) na krawędzi P11 od strony ściany A. P11 leży poziomo na dnie strefy panelu, maks. ok. 45 × 130 mm (`Plytki/P11-S1-przygotowanie/README.md`, P11-6).

Poprawki z recenzji: notatka o stykach złoconych wskazuje `verification/QA.md` (prąd zamkniętego styku: LOGGER ok. 0,31–0,32 mA, wariant pełny 0,03–0,87 mA); tabelka rysunkowa bez „PCB”, komentarz skrócony do ramki; R1 ma widoczne pole „Wariant: LOGGER: obsadzony / z P04: DNP”; zwarcie PANEL_3V3–GND opisane jako 34 mA / 0,12 W (zgodnie z modelem: 118 mW).

## Pytania do użytkownika

Pytania 1–5 zamknięte decyzjami 4.10 (wyżej).

6. **Listwa serwisowa:** P11 nie ma listwy z krawędzi B, bo nie stoi w stosie, a wszystkie sieci są dostępne na polach przewodów. Czy wystarczy?
