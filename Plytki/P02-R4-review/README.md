# P02 R4 — zasilanie z pakietu Li-ion 4S (etap 2: PCB w formacie S1, klasa L)

29.09.2026 schemat (sesja w chmurze, etap 1), 29–30.09.2026 PCB (lokalnie, etap 2). **Status: PCB i kontrole do recenzji. Pliki produkcyjne (Gerber, wiercenia), przymiarka 1:1 i zakupy nie są zrobione.** R4 zastępuje P01 PROTECT i część HOLD płytki P02 R3 zgodnie ze specyfikacją `Plytki/P02-R4-specyfikacja/` (D-01…D-07 przyjęte, R23 = 22 kΩ / 0,5 W). Zamknięte pakiety P01 R3 i P02 R3 nie zostały zmienione, generatory skopiowano stamtąd.

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

PCB (lokalnie, ok. 25 min): Python KiCada 10.0.6 `src/run_release.py` — schemat, płytka odtworzona z `routing/P02.ses` i `routing/completion-routes.json`, nadruk, `verify_pcb.py`, próby ujemne, widoki, PDF, QA i manifest. Zmienne: `EGRLAB_PDF_PYTHON` (reportlab), `EGRLAB_NODE` i `EGRLAB_SHARP` (rasteryzacja), `PDFTOPPM`; `--new-route` uruchamia Freerouting od nowa (`EGRLAB_FREEROUTING`). Trasowania nie robić w chmurze (`docs/CHMURA.md`, zasada 6).

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

## Etap 2 — PCB (format S1, klasa L; lokalnie 29–30.09.2026)

**Płytka:** 160 × 100 mm, klasa L — cały poziom 1 stosu (sloty S1–S3; format S1-3: w klasie 2/3 trasowanie się nie domykało, decyzja użytkownika „opcja 1”). Dwie warstwy 35 µm, FR4 1,6 mm. J_BP (IDC 2×10 kątowe) na krawędzi A w slocie S3, listwy serwisowe J_SV1 (S1) i J_SV2 (S3) na krawędzi B, złącza pakietu i silnika przy ścianie wejść (x = 160).

**Rozmieszczenie** (`src/placement.py`):
- blok mocy z pilota 2/3 przesunięty o 53,5 mm do ściany wejść (wylewki, pasy 5 A i korytarz tym samym przesunięciem w `route_critical.py`); rdzeń mocy (Q9, Q1, Q2, sterowanie bramki, F1, D3) bez zmian — decyzja użytkownika 30.09, jego miedź jest narysowana wokół położeń części;
- blok sterowania rozsunięty w osi x od strony panelu dwa razy: ×1,35, potem na wskazanie użytkownika (wolne pole między blokami na wydruku 1:1) górna połowa ×1,25, dolna ×1,12; układy jadą sztywno ze swoimi kondensatorami odsprzęgającymi i rezystorami serwisowymi;
- grupa podtrzymania (C12, D1, D2, R40, R41, R67, C20, R68) 8 mm w lewo razem ze swoimi wylewkami VLOG/HOLD_C i przedłużeniami VSW; grupa ENABLE (Q6, D7, D8, R14–R16, R55) 4 mm w lewo;
- R5 (1 kΩ, początek dzielnika UVLO) obok D11 (SW_COM): PWR_A (R5 → J14 → włącznik na panelu) krótka, rezystor nadal przy źródle;
- zajętość obrysami w pasach 20 mm po rozsunięciu: 42 / 43 / 41 / 40 / 41 / 23 / 76 / 68 % (wcześniej 49 / 60 / 36 / 24 / 29 / 34 / 76 / 68 %).

**Trasowanie:** Freerouting 2.1.0, 30 przejść; domknęła się 1. próba (`routing/P02.ses`, `routing/attempts.json`). Planer dokańczania dołożył 7 tras w 7 sieciach (`routing/completion-routes.json`). Płytkę odtwarza `src/run_layout.py --reuse-ses` (bez routera).

**Poprawki łańcucha względem pilota** (w kodzie opisane datami 29–30.09):
- planer dokańczania kończy ścieżkę tylko na warstwie pola (wcześniej ścieżka B.Cu kończyła się na polu SMD F.Cu bez przelotki);
- zszywanie GND na całej długości płytki (pilot kończył siatkę na x = 104,5) i wiązanie klastrów GND bez połączenia z J1.2; kontrola obecności obu stref GND;
- porządki: przelotki na polach THT tej samej sieci, przelotki z miedzią na jednej warstwie; łańcuch uznawany za nadmiarowy tylko wtedy, gdy oba końce leżą na tej samej grupie zablokowanej miedzi;
- wylewki BAT_IN i VSW pod końcami blaszek Q9 i Q1 (wcześniej wchodził tam pasek GND);
- nadruk: etykiety listew przed oznaczeniami, oznaczenia poza nadrukiem części, litery „K” diod przesuwane z linii nadruku;
- kontrole: obrys bez grubości linii, tor 5 A liczony jako miedź sieci na przekroju, niezgodności z biblioteką tylko dla części z przyciętym nadrukiem; próby ujemne i PDF we współrzędnych klasy L.

**Wyniki** (`verification/QA-PCB.md`, `verification/pcb-checks.json`):

| Kontrola | Wynik |
|---|---|
| DRC (świeży, wszystkie poziomy) | 0 niepołączonych, 0 niezgodności ze schematem, 0 innych naruszeń; 14 × `lib_footprint_mismatch` u części, którym `silkscreen.py` przyciął nadruk lub przesunął tekst (lista w `routing/silkscreen.json`) |
| Kontrole PCB | 23/23 |
| Próby ujemne | 12/12 (w tym próba zerowa) |
| Tor 5 A — najwęższy przekrój miedzi (wymóg 4,0 mm, IPC-2152, 35 µm, ΔT ≤ 20 K) | BAT_IN 6,0; SW_COM 6,1; VSW 5,1; VMOTOR 5,7; powrót GND na B.Cu 4,1 mm |
| Pola z pełnym połączeniem ze strefą | C8.2, D3.2, LED1.1, U10.4, U2.4 (odciążenie „zagłodzone” przez sąsiednie ścieżki); złącza zachowują odciążenia |
| Wysokości | ≤ 21,5 mm; C27/C28 od spodu 0,88 mm (karta KEMET C1206C104K5RACTU, DigiKey 411248) |

**Do recenzji / otwarte:**
- przymiarka 1:1 (wydruk z `output/pdf/P02-R4-PCB.pdf`);
- 9 oznaczeń ukrytych z braku miejsca (R23, R22, Q2, Q9, F3, F1, F2, U6, U5); nie wstawione znaczniki „1” przy złączach (piny 1 oznacza nadruk footprintów);
- pola z pełnym połączeniem ze strefą GND lutować mocniejszą lutownicą — szczególnie D3.2 (wyprowadzenie transila P600);
- najwęższy przekrój toru 5 A: 4,1 mm;
- awaria jednego przebiegu wydania 30.09 (strefy GND zniknęły po imporcie SES, 204 niepołączenia) nie dała się odtworzyć; `stitch.py` zatrzymuje się teraz, gdy stref GND brakuje.
