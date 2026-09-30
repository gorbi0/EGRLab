---
name: p02-r4-state
description: "P02 R4 (zasilanie z pakietu 4S): etap 1 schemat (PR #2) → decyzje (D3 5KP24A, C_H 2200, UVLO obwiednia) → etap 2 PCB lokalnie w klasie L: DRC czysty, PCB 23/23, próby 12/12, PR #4 czeka na recenzję"
metadata:
  node_type: memory
  type: project
  originSessionId: 1bdb3685-394a-4886-bbc7-14b9957d5ea4
  modified: 2026-09-29T17:43:56.820Z
---

P02 R4 zastępuje P01 PROTECT i HOLD z P02 R3 (decyzja 29.09: zasilanie z pakietu 4S, zob. [[zasilanie-ogniwa-18650]]).

**Przebieg:**
- Specyfikacja i STAN-PRAC: `Plytki/P02-R4-specyfikacja/`.
- Etap 1 (schemat) zrobiła sesja w chmurze (Opus 5.5 high, ok. 25 min), pakiet `Plytki/P02-R4-review`:
  - ERC 0, netlista 317/317, 35/35 kontroli elektrycznych, 19/19 prób ujemnych;
  - oznaczenia: Q9 = Q_REV, Q1 = Q_SW, Q2 = Q_OFF, C12 = C_H, R40 = R_ch, D2 = D_ch;
  - PFAIL_N z U2A buforującej OK (odstępstwo od D-06, uzasadnione).
- Moja recenzja: `Plytki/P02-R4-recenzja/RECENZJA-P02-R4-ETAP1.md`. UVLO przeliczone niezależnie (13,53/12,56 V wobec 13,50/12,55 V). PR #2 scalony (merge 4ac375d).

**Decyzje użytkownika po recenzji (29.09, „przyjmuję wszystkie rekomendacje”):**
- D3 5KP18A → 5KP24A: Z-01, bez uszkodzeń do 25 V.
- C_H zostaje 2200 µF. Z-08 przepisane na ≥ 10 ms w najgorszym narożniku (jest 11,1 ms). 3300 µF nie mieści się w limicie wysokości 35 mm.
- UVLO bez zmian. Z-02/O-02 przepisane na obwiednię 12,90–14,08 / 11,98–13,11 V. Moje ±0,34 V w specyfikacji było zaniżone (rezystory 1 %).
- Bezpiecznik przy klemie 1 A.
- Włącznik PWR na P11 ze złoconymi stykami (ok. 0,3 mA, obwód „suchy”).

**Następny krok:** etap 2 (PCB) w chmurze:
- zadanie `Plytki/P02-R4-specyfikacja/ZADANIE-P02-R4-ETAP2.md`, gałąź `p02-r4-pcb`;
- polecenie w `docs/CHMURA.md`;
- najpierw zmiana D3 i J15 w schemacie.

Paczka produkcyjna dopiero po mojej recenzji PCB.

**Etap 2 (29.09 wieczorem), stan roboczy:**
- Pilot w chmurze (PR #4, gałąź `p02-r4-pcb`): schemat S1 OK (39/39, 25/25). Trasowanie w klasie 2/3 się nie domknęło; sesja spaliła ok. 30 $ i straciła wynik przy restarcie ([[chmura-limity]]).
- Lokalnie potwierdziłem, że w 2/3 zostaje 15 niepołączeń. Użytkownik wybrał **klasę L (opcja 1)**.
- Pracuję na lokalnej gałęzi **`p02-r4-pcb-lokalnie`** (main + PR #4, nie wypchnięta).
- Zmiany w `Plytki/P02-R4-review/src`:
  - `prepare_routing.py`: GND trasuje router, poza LOCKED_ONLY;
  - `placement.py`: blok RIGID +53,5 mm, J_SV1 w S1, J_SV2 w S3; R57 przeniesiony do (38.4, 44.5, 270);
  - `route_critical.py`: DX = 53,5 dla wylewek, pasów, korytarza, ścieżek i przelotek;
  - klasa L w `build_board.py`, `verify_pcb.py` (J_SV1→S1, J_SV2→S3, J_BP x = 133,5), `silkscreen.py`, `make_pdf.py`, `complete_routes.py`, `stitch.py`, `tools/render.py`, notach `parts.py`.
- Pierwsze przebiegi w klasie L (ciasny blok sterowania x 0–61, pas x 61–86 pusty): po dokańczaniu 2–3 niepołączenia.
  PWR_A (R5 w bloku mocy → J14.1, ok. 100 mm) nie miała żadnej drogi: J14 zamknięty pierścieniem ścieżek na obu warstwach
  (sprawdzone A* na siatce 0,1 mm z odstępami klas). Łatanie ścieżek porzucone.
- **Zmiana rozmieszczenia (29.09 wieczorem, `placement.py`):**
  - x części sterowania ×1,35 od lewej krawędzi (KX; bez RIGID, J_SV1, R70);
  - R5 z bloku mocy obok D11 (12,0; 77,5; 90) — SW_COM już tam dochodzi, PWR_A krótka, rezystor dalej przy źródle;
  - jawne pozycje po skalowaniu: R58, D12 (strefy M3), kondensatory odsprzęgające C21–C27, C29 (≤ 7,1 mm od pinów),
    rezystory serwisowe R69, R70, R71 (≤ 8 mm od węzła; verify: ≤ 10 mm);
  - DRC rozmieszczenia czysty.
- `complete_routes.py`: planer zaczyna i kończy ścieżkę tylko na warstwach pól (wcześniej B.Cu kończyła się na polu SMD
  F.Cu bez przelotki); rekordy zapisywane też przy wyjściu 3. `fix_smd_vias.py` i `fix_final.py` dotyczyły starego SES
  i są do usunięcia, jeśli nowy przebieg domknie się sam.
- Pola złączy (J_SV2.13, J_BP.11) bywają „starved” przez wyspę wylewki połączoną tylko z tym polem (DRC: „łącza
  połączone z izolowanym polem”) — lekarstwo: przelotka GND w tej wyspie; run_layout.py dla pól J robi nowy przebieg.
- Freerouting 2.1 rzuca NPE (insert_forced_trace_polyline, maze_search) — część połączeń odpada w każdym przejściu.
- Format S1-3 (P10 na poziom 4) zapisany na main (commit 1c94235).
- **Wynik (30.09, commit 7377103 wypchnięty na `p02-r4-pcb`, PR #4):** DRC 0 niepołączonych / 0 niezgodności,
  jedyne zgłoszenia 13 × lib_footprint_mismatch u części z przyciętym nadrukiem (przyjęte jawnie w verify_pcb);
  PCB 23/23; próby ujemne 12/12; tor 5 A ≥ 4,1 mm (GND przy R18.2). Czeka na recenzję i „scal” (merge-tree z main czysty).
- Poprawione po drodze (poza wcześniej wymienionymi): cleanup reguła 1 (łańcuch nadmiarowy tylko w obrębie jednej grupy
  zablokowanej miedzi), wylewki pod blaszkami Q9/Q1, verify (tor 5 A = suma miedzi sieci na przekroju ±3 mm, obrys, lib
  mismatch), silkscreen (etykiety przed oznaczeniami, „K” diod przesuwane), próby ujemne (DX, decap_far po linii U9.14→C28),
  make_pdf (kolumna notatek x = 178, dane z wyników), parts.py C27/C28 0,88 mm (DigiKey 411248).
- Jeden przebieg wydania zgubił strefy GND po imporcie SES (204 niepołączenia, nie odtworzone); `stitch.py` ma assert.
- Opis PR #4 nadal z pilota (gh zablokowany przez tryb uprawnień) — stan w README pakietu i STAN-PRAC.
- Otwarte: przymiarka 1:1, 12 ukrytych oznaczeń w bloku mocy, paczka produkcyjna po recenzji.
- Uruchamianie: `EGRLAB_FREEROUTING=C:/Users/tgorbacz/.codex/.chatgpt-projects/g-p-6a8827e57cc881919b26f761377a7bd3/.egrlab-toolchains/freerouting`, Python KiCada `C:/Program Files/KiCad/10.0/bin/python.exe src/run_layout.py`.
- **Nie przełączać gałęzi w trakcie przebiegu.** Commity na `main` robić plumbingiem (tymczasowy indeks, `read-tree`/`update-index` z `core.protectNTFS=false`, `commit-tree`, `update-ref`).

**Why:** płytka zasilania jest na ścieżce krytycznej całego przyrządu. Etapy z recenzją ograniczają koszt sesji w chmurze.
**How to apply:** przy recenzji etapu 2 sprawdzić:
- blaszki TO-220 (dren) tylko na własnej sieci ([[p01-pcb-r1-review]]);
- tory 5 A przy 35 µm;
- odsprzęganie;
- wprowadzenie D3 5KP24A.

Zob. [[repo-chmura]], [[pcb-fab-satland]].
