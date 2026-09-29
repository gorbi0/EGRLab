# Odbiór plików P02-R1 (schemat + PCB R1)

Data: 2026-09-25. Narzędzia: **KiCad 10.0.6** (Python z `pcbnew`, `kicad-cli`), Freerouting 2.1.0 (JRE 21).
Stan: **schemat i layout do recenzji; sprzęt, przymiarka 1:1 i odbiór elektryczny NIE ZBADANE**.

| Kontrola | Wynik |
|---|---|
| ERC schematu (2 arkusze A3, wszystkie ważności) | **0** (`erc.json`) |
| Netlista vs lista części, pin po pinie | **200/200**, 70 części, 44 sieci, 0 błędów (`schematic-check.json`) |
| Native DRC: naruszenia / niepołączone / zgodność ze schematem | **0 / 0 / 0**, świeży przebieg w `verify_pcb.py` (`drc.json`, `drc.provenance.json`) |
| Kontrole gotowej PCB (`pcb-checks.json`) | **28/28 PASS** |
| Próby ujemne (`negative-controls.json`) | **8/8 wykryte** |
| Części | 69 na płytce + R17 poza płytką + 4 otwory M3 |
| Miedź / format | 2 × 70 µm / 160 × 120 mm |

`pcb-checks.json` wiąże wynik z SHA256 płytki; `drc.provenance.json` z SHA256 wszystkich wejść. **Po każdej zmianie miedzi, pada, footprintu albo reguły wynik trzeba uzyskać ponownie.**

## Kontrole P02 (poza DRC i netlistą)

| Kontrola | Co sprawdza |
|---|---|
| Węzeł VPROT | jedna wyspa strefy F.Cu łączy J1.1, J2.1, TP1, R9.1; na drodze J1.1 → J2.1 w każdym przekroju ≥ 4 mm miedzi |
| Powrót 5 A | obszar reguł na B.Cu obejmuje J2.2 i J1.2; w nim brak ścieżek i przelotek; oba pady na płaszczyźnie GND B.Cu |
| Wylewki GND | B.Cu: jedna wyspa ≥ 80 % płytki; usuwanie wysp bez połączenia włączone |
| HOLD_STORE | pady tylko C1–C3 +, F1.2, R1.1, R6.1, TP3; cała miedź zablokowana; F1.2 → C1+ ≤ 30 mm po miedzi |
| Szerokości | najwęższa ścieżka: VPROT ≥ 1,0, HOLD_FUSED ≥ 1,5, CHARGE_D/VIN ≥ 1,0, HOLD_STORE ≥ 0,6, VLOG_RES ≥ 0,8 mm |
| Dzielniki | R6.1 na szynie banku, R9.1 w strefie VPROT |
| Diody | D1: A1 = VPROT, K = VLOG_RES, A2 = HOLD_FUSED; D2: anody CHARGE_D, K = HOLD_FUSED |
| LV | J3–J10: 1 = 5V_SYS, 2 = GND, 3 = 3V3_IO, 4 = GND |
| Odsprzęganie | każdy 100 nF ≤ 8 mm prosto i ≤ 20 mm po miedzi od pinu zasilania; C14/C15 ≤ 15 mm od wejść U7; C4–C8 ≤ 10 mm |
| Bank | odstęp puszek ≥ 3 mm; ≥ 10 mm od D1, D2, U1, U2 |
| Mechanika | J2 czołem ≤ 1 mm od krawędzi; kotwy J1/J12/J13 12,5 mm od lutów, od strony krawędzi; nic w promieniu 4,5 mm od otworów M3 |
| Nadruk | każde oznaczenie poza obrysami innych części i najbliżej własnej; opisy poza obrysami (poza J1/J12/J13); opisy przy właściwych elementach i bliżej nich niż sąsiadów |

## Próby ujemne

Każda na kopii płytki w `negative-controls/<nazwa>/` (poza archiwum): `vprot_neck` (strefa VPROT ucięta nad J2.1), `bcu_return` (ścieżka w korytarzu powrotu), `hold_free` (nadmiarowa, niezablokowana miedź HOLD_STORE), `decap_far` (C13 odsunięty o 12 mm), `ref_inside_other` (oznaczenie U2 w obrysie U1), `mount_shift` (H3 przesunięty), `lv_swap` (zamienione napisy LV03/LV04), `thin_vprot` (gałąź VSENSE zwężona do 0,4 mm). Wszystkie wykryte przez właściwą kontrolę.

## Przebieg (kolejność faktycznie wykonana)

Z katalogu pakietu, Pythonem z KiCada: `python src/run_release.py` odtwarza wszystko po kolei.

1. `build_schematic.py` → ERC → netlista → `verify_schematic.py` → PDF schematu.
2. `run_layout.py --reuse-ses`: `build_board.py`, `set_stackup.py`, `route_critical.py` (trasy mocy zablokowane, eksport DSN), `prepare_routing.py` (strefa VPROT jako obszar zakazany, GND/VPROT poza listą routera), import zapisanego wyniku `routing/P02.ses`, `set_rules.py` (**zaraz po imporcie** — zapis bez `.kicad_pro` przywraca reguły domyślne), `cleanup.py` (U5.12 z pełnym połączeniem do wylewki: szprychy zagłodzone przez sąsiednie ścieżki), DRC.
3. `silkscreen.py`, `set_rules.py`.
4. `verify_pcb.py`, `negative_controls.py`.
5. Rendery 3D, `make_pdf.py`, manifest i archiwum.

`python src/run_release.py --new-route` puszcza Freerouting od nowa (`-mp 100`, a i tak ok. 1000 przebiegów); wynik jest wielowątkowy i różni się między przebiegami, dlatego wydanie importuje zapisany `routing/P02.ses`. Identyfikatory UUID nowych elementów KiCad nadaje losowo, więc powtórzony przebieg daje tę samą geometrię, ale inny SHA pliku płytki.
