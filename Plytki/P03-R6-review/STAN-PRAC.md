# P03 R6 — stan pracy (przekazanie na komputer 24/7 z Ubuntu, 30.09.2026)

Gałąź `p03-r6-pcb`. Etap: **poprawki schematu zrobione i sprawdzone, layout w toku (trasowanie się nie domyka)**. Dalsza praca na komputerze 24/7 (Ubuntu, sesja Claude Code „frigate-claude”); środowisko: `docs/UBUNTU-24-7.md`.

## Zrobione (sprawdzone)

Poprawki z recenzji PR #6, przed layoutem — `src/run_schematic.py` przechodzi w całości (ERC 0, 511/511 pinów, funkcje 53/53 i mutacje 44/44, reset 8/8 + 4/4, J_BP/PFAIL/listwy 12/12 i próby 25/25 z zerową, tabele PASS):
- R43 10 kΩ → 100 kΩ (stan niski PFAIL_N 0,73 V przy VOL LM2903 0,7 V; przy P02 bez zasilania pewne L ok. 0,33 V zamiast 1,7 V).
- Trzecia żyła 5V_SYS na J_BP2.17; PFAIL_N przeniesiony na 16 (GND na 15), ADC_RESET na 18 (sporne — opis w README).
- Wszystkie rezystory i kondensatory SMD 1206 (posiadane MF0207/K15 zużywają P09/P10); jeden kod 100 nF GRM31CR71H104KA01L.
- Kołki listew serwisowych pogrupowane według położenia węzłów (J_SV1 = węzły w S1, J_SV2 = S2, J_SV3 = S3): pierwsze przebiegi routera miały 12 z 33 linii serwisowych przez całą płytkę. `src/serwis_pinout.py`, `docs/SERWIS.csv`, odwołania w `docs/ODBIOR.md` poprawione.
- Łańcuch schematu przemianowany na `src/run_schematic.py`; `src/run_release.py` to teraz pełny łańcuch (schemat + PCB) na wzór P02 R4.

## Layout — co jest

Skrypty w `src/` (wzorzec P02 R4, opis łańcucha w `docs/ODTWARZANIE.md`):
- `placement.py` → `src/placement.json`: układy i złącza ręcznie, bierne automatem „najbliższe wolne miejsce przy pinie” (obrysy + 0,5 mm, strefy M3, obszar anteny, kanał toru 5 V, pas wzdłuż rzędu J1 M1). Rozmieszczenie opisane w nagłówku skryptu i w `docs/MECHANIKA.md`.
- `build_board.py` (obrys L, 12 otworów M3 ze strefami D7, obszary ANTENNA M1 i SD1 M2.5), `set_stackup.py`, `set_rules.py` (Default 0,3 mm; PWR 0,6 mm dla 5V_SYS/5V_M1), `route_critical.py` (zablokowany tor 5 V: J_BP2.17/19/20 → C13 → Q1 po F.Cu, od Q1 1,5 mm po B.Cu wzdłuż x = 97,4 i y = 93 do M1 J1-21; budżet ≤ 50 mΩ), `prepare_routing.py` (paski przy krawędziach; **GND wyjęte z listy sieci routera**), `import_routing.py`, `stitch.py`, `complete_routes.py`, `cleanup.py`, `run_layout.py` (do 3 prób, przekroczenie czasu routera = nieudana próba).
- Po layoucie (jeszcze NIEURUCHOMIONE, kod napisany, może wymagać poprawek): `silkscreen.py` (pełne nazwy przy J_SV1, skróty 3-literowe przy J_SV2/J_SV3 pod modułami + legenda), `verify_pcb.py` (ok. 27 kontroli, w tym tor 5 V w mΩ, obszar anteny, USB/karta ≤ 6,5 mm od krawędzi B, kontrakty `docs/J_BP.csv` i `docs/SERWIS.csv`), `negative_controls.py` (16 prób z zerową), `heights.py`, `export_views.py`, `rasterize.mjs`, `make_pdf.py`.

## Layout — przebiegi i wnioski (Windows, Freerouting 2.1.0)

| Przebieg | Wynik |
|---|---|
| GND w routerze, 3V3_CORE 0,5 mm | 48 niepołączonych po 15 przebiegach, przebieg do 4 min |
| GND poza routerem, 3V3_CORE 0,5 mm | 31–39 po 12 przebiegach |
| + U22 do S1, pas wzdłuż J1 M1, nowy przydział listew | ok. 40 po 4 przebiegach |
| + **3V3_CORE 0,3 mm** (0,5 mm nie mieści się między pinami w rastrze 2,54: szczelina 0,84 mm) | 12–15 po 10 przebiegach; w pełnym przebiegu 13 po 30 |
| planer dokańczania (próba 1) | dołożył 28 tras, nie domknął: ADC_DOUTA, PWR_GATE (Q1.1), TEST_KEY, TEST_PRESENT_CORE, MEAS_EN(_SRC), SPI3_MOSI_SRC, ADC_CONVST, 3V3_IO, SV_ADC_BUSY, SV_ADC_CS, TC1_CS_SRC + wyspy GND |

**Główny problem na teraz: GND.** Bez GND w routerze wylewki nie dochodzą do pinów masy wciśniętych między sygnały: po zszyciu ok. 60 pól GND bez połączenia (wszystkie piny 1/4/7/10/13 w U11–U14 i U21–U23, część kondensatorów i rezystorów do GND, J_BP3.7/11/19), wyspy F.Cu 73. Propozycje, w tej kolejności:
1. Wprowadzić GND z powrotem do routera (przyczyną wolnego i złego trasowania była szerokość 3V3, nie GND) i porównać.
2. Albo krok „fanout” przed routerem: przy każdym polu SMD na GND krótka ścieżka do przelotki (zablokowane), jak w P02 R4 kotwice; wylewka B.Cu łączy przelotki.
3. Potem planer dokańczania i zszywanie jak w P02 R4.

Inne otwarte:
- Zatłoczenie w S1 pod J_BP1 (U22/U14/U13 i ich rezystory w pasie pod złączem) i przy M1 J1 — jeśli nadal nie domyka, rozsunąć S1 (wolne miejsce: dół S1, środek S3, dół prawej kolumny) albo przenieść część rezystorów serwisowych na spód (S1-2: SMD ≤ 1,5 mm, ≥ 1 mm od pól THT).
- Freerouting jest niedeterministyczny; przebieg z 30 próbami ok. 10–15 min. Wynik do odtwarzania zapisuje `routing/P03.ses` + `routing/completion-routes.json` (odtwarzanie: `run_layout.py --reuse-ses`).
- Na Linuksie trasowania P03 jeszcze nikt nie uruchamiał (obraz Dockera ma Freerouting 2.1.0 w `/opt/egrlab/freerouting`, `EGRLAB_FREEROUTING` ustawione w obrazie).

## Decyzje sporne (do opisania w README przy PR)

1. USB-C M1 i karta SD1 ok. 6,2 mm przed krawędzią B: moduły (26 mm) szersze niż przerwy między listwami serwisowymi (19,4 mm), więc kończą się przed obrysami J_SV2/J_SV3; dostęp przy zdjętej ściance B.
2. U22 w S1 zamiast „blisko J_BP2” (README): wejścia z U1/U2, dwa wyjścia do J_BP1; MEAS_EN i ADC_RESET (statyczne) dłuższą drogą.
3. Przydział kołków listew według położenia węzłów (zmiana względem schematu z PR #6).
4. Przy J_SV2/J_SV3 skróty trzyliterowe + legenda zamiast pełnych nazw (S1 §6 mówi o nazwie przy każdym kołku; nad listwami stoją moduły, zostaje 1,5 mm).
5. 3V3_CORE 0,3 mm (spadek ok. 25 mV przy 100 mA na 150 mm).

## Następne kroki

1. Środowisko na Ubuntu (`docs/UBUNTU-24-7.md`), odtworzenie `src/run_schematic.py` w kontenerze (wyniki jak w repozytorium, różnice tylko CRLF/LF i daty).
2. Domknięcie trasowania (wyżej), potem `silkscreen.py`, `verify_pcb.py` (wszystko PASS), `negative_controls.py`, PDF — poprawić skrypty tam, gdzie wyjdą błędy (pisane bez uruchomienia).
3. README: sekcja layoutu (wyniki, decyzje sporne), `EGRLab-AKTYWNE.md`, `docs/01-overview.md`, pamięć.
4. Commit/push na `p03-r6-pcb`, PR; scalanie dopiero po „scal” użytkownika. Potem przymiarka 1:1 i paczka produkcyjna (skrypty z `Plytki/P02-PCB-R4-zamowienie/src/`).
