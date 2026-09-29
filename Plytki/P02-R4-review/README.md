# P02 R4 — zasilanie z pakietu Li-ion 4S (etap 1: schemat)

29.09.2026, sesja w chmurze. **Status: schemat i kontrole elektryczne do lokalnej recenzji. PCB, przymiarka i zakupy nie są zrobione.** R4 zastępuje P01 PROTECT i część HOLD płytki P02 R3 zgodnie ze specyfikacją `Plytki/P02-R4-specyfikacja/` (D-01…D-07 przyjęte, R23 = 22 kΩ / 0,5 W). Zamknięte pakiety P01 R3 i P02 R3 nie zostały zmienione, generatory skopiowano stamtąd.

## Co jest na płytce

- **WEJ** (plik `P02.kicad_sch`): J1 z pakietu, Q9 (Q_REV) i Q1 (Q_SW) — dwa SUP53P06 połączone przeciwsobnie źródłami w SW_COM; tor bramki Q1 z szybkim wyłączaniem Q2 (Q_OFF) i Q3–Q5 przeniesiony 1:1 z P01 R3 (poza R23). Dalej VSW (5KP18A, 47 µF), VMOTOR przez F1 5 A MINI, D1 (suma VSW i C_H → VLOG), podtrzymanie R40 22 Ω bezpiecznikowy → D2 → C12 2200 µF.
- **STER**: AUX5 z LM2936 zasilanego z SW_COM lub VLOG (D11/D12), REF TL431, UVLO na U2B z przełącznikiem PWR (J14) w górnej gałęzi dzielnika, OK z resetem U4, ENABLE przez D7/D8/Q6, PFAIL_N z U2A, SAFE_N/PG do P04 (Q7/Q8, R34, J13) i LED PWR.
- **LV**: TSR 2-2450 i TSR 2-2433 za F2/F3 1 A MINI, J3–J10 bez zmian.
- **MON**: PSU_OK jak R3 (U7, U8, U9 na adapterze, U10A; bramki HOLD_READY usunięte), J12 z PFAIL_N na pinie 3, VBAT auta J15 → R38 10 kΩ → D13 P6KE24CA → J11 Mini-Fit 2p.

Oznaczenia: tor sterowania ma numery z P01 R3 (Q1–Q8, R1–R4, R13–R34, C1–C11, D3/D4/D7–D9, U1–U4), elementy z P02 R3 dostały nowe numery. Pole `source_ref` w `docs/parts.json` podaje pochodzenie każdej części (`P01R3:…`, `P02R3:…`, `R4:NEW`): 54 z P01 R3, 34 z P02 R3, 43 nowe (w tym 17 punktów pomiarowych).

## Wyniki (szczegóły: `verification/QA.md`, `docs/OBLICZENIA-R4.md`)

| Kontrola | Wynik |
|---|---|
| ERC (4 arkusze) | 0 naruszeń |
| Netlista pin po pinie względem `parts.py` | 131 części, 317/317 pinów, 61 sieci |
| Kontrole elektryczne | 35/35 PASS |
| Próby ujemne | 19/19 (18 mutacji wykrytych + próba zerowa czysta) |
| UVLO nominalnie / obwiednia | 13,50 / 12,55 V; załączenie 12,90–14,08 V, wyłączenie 11,98–13,11 V, histereza ≥ 0,84 V |
| Wyłączenie Q1 (R23 22 kΩ) | 44–71 µs nominalnie, do 239 µs w narożniku (model skalibrowany na ngspice P01 R3: −6…−9 %) |
| Narastanie VSW / prąd przy 220 µF | 11,5 V/ms / 2,53 A nominalnie (5,6–14,7 V/ms, do 3,24 A w narożnikach) |
| Podtrzymanie po PFAIL_N przy 6 W | 16,8 ms nominalnie, 11,1 ms w najgorszym narożniku |

Niezgodności ze specyfikacją (do decyzji, opisane w `docs/OBLICZENIA-R4.md`): Z-02 (rozrzut większy niż ± 0,34 V), Z-08 (najgorszy narożnik 11,1 / 22,3 ms zamiast 14 / 28 ms), Z-01 (25 V wbrew 5KP18A). Odstępstwo projektowe: PFAIL_N z U2A buforującej OK zamiast porównania UV_CMP (D-06 dosłownie).

## Uruchomienie

W chmurze: `scripts/egrlab-docker python3 src/run_schematic.py` (ok. 20 s). Lokalnie: Python KiCada 10.0.6, `KICAD_CLI` i `PDFTOPPM` wskazują narzędzia. Kroki: budowa schematu → ERC → netlista → `verify_schematic.py` → `check_electrical.py --negative` → PDF i podglądy PNG → `verification/manifest.json`.

## Zawartość

| Ścieżka | Zawartość |
|---|---|
| `eda/` | Projekt KiCad 10 (4 arkusze A3), lokalne biblioteki symboli i footprintów |
| `output/pdf/P02-R4-schemat.pdf`, `output/previews/` | Schemat i podglądy stron |
| `docs/parts.json`, `docs/BOM.csv` | Części, piny, sieci, MPN, pochodzenie |
| `docs/OBLICZENIA-R4.md` | UVLO, PFAIL_N, wyłączanie z R23, narastanie VSW, podtrzymanie, straty |
| `verification/` | ERC, netlista, kontrola pin po pinie, kontrole elektryczne, próby ujemne, logi, manifest SHA-256 |
| `src/` | Generatory (`cadlib.py`, `verify_schematic.py` z P02 R3), `parts.py`, `build_schematic.py`, `check_electrical.py`, `run_schematic.py` |

Footprinty TO-220, MFR-50, PR02, B32529, MKS2, P600 i wiązki PG pochodzą z bibliotek P01 R3 / P02 R3 (bez zmian), pozostałe z KiCad 10.0.6 albo z generatora w `parts.py`. W etapie 2 (PCB) trzeba potwierdzić: obrys C12 (16 × 25 mm, P7,5), oprawki MINI Keystone 3568, Mini-Fit 2p.
