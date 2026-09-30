# P03 R6 — stan pracy (przekazanie na komputer 24/7 z Ubuntu, 30.09.2026)

Gałąź `p03-r6-pcb`. Etap: **PCB gotowa do recenzji (30.09 wieczorem)** — DRC 0/0/0 (6 przyjętych `lib_footprint_mismatch`), kontrole PCB 25/25, próby ujemne 16/16, PDF `output/pdf/P03-R6-PCB.pdf`; opis, wyniki i decyzje sporne w README (sekcja „PCB”). Praca na komputerze 24/7 (Ubuntu, sesja Claude Code „frigate-claude”); środowisko: `docs/UBUNTU-24-7.md`.

## 30.09 późnym wieczorem — poprawki wydania (po P09/P10)

- Wydruk przymiarki (strona 5 PDF) obiecywał kółka Ø7 wokół otworów M3, a pokazywał tylko otwory: `build_board.py` rysuje kółka stref (M3 Ø7, SD1 Ø6) na F.Fab.
- `verify_pcb.py`: kontrola znaczników krawędzi szukała litery A w tekście („KRAWEDZ B” też ją ma) — teraz `startswith`; znaczniki były na płytce, wynik bez zmian.
- Nadruk: stała kolejność oznaczeń przy remisie powierzchni (kolejność footprintów szła za losowymi UUID) i drugi pierścień pozycji — ukrytych oznaczeń 7 zamiast 15.
- PDF: pogrubienia (`registerFontFamily`), przecinki dziesiętne; tytuł schematu „schemat i PCB do recenzji”. DRC 0/0/0, kontrole 25/25, próby 16/16 bez zmian.

## 30.09 wieczorem — Ubuntu 24/7 (sesja „frigate-claude”)

- Środowisko: obraz `egrlab-kicad:10.0.6` zbudowany (komputer ma Ubuntu 22.04: `setup-chmura.sh` bierze teraz przypięte paczki czcionek noble z sumami SHA-256), `src/run_schematic.py` w kontenerze = wyniki z repo (różnice tylko CRLF/LF, daty, ścieżka).
- **Komputer jest rejestratorem monitoringu (Frigate) i ten ma pierwszeństwo:** `scripts/egrlab-docker` daje kontenerom najniższą wagę CPU i limit 2 rdzeni, najwyżej 2 ciężkie zadania naraz (`docs/UBUNTU-24-7.md`).
- Masa: `src/fanout_gnd.py` po `route_critical.py` — belka GND po F.Cu pod każdym SOIC-14 (pod korpusem router i tak nie wchodzi) z dwiema przelotkami, odcinki z przelotkami przy SOT-23, grzebień GND pod korpusem każdego J_BP (piny nieparzystego rzędu przez szczeliny parzystego do szyny y = 8, przelotki na końcach). W 6 przebiegach z grzebieniem żaden pin GND złącza nie został odcięty (bez niego w E2: 13). Pola GND elementów 1206 zostają wylewkom (fanout każdego pola kosztował routera 22–30 zamiast 6–13 otwartych połączeń).
- `cleanup.py --tidy` zaraz po imporcie SES: Freerouting zostawia kawałki niedokończonych połączeń (81–112 elementów na przebieg), które blokowały planer dokańczania.
- Wynik 7 wariantów (rozmieszczenie, kręgosłup 5 V na F.Cu, grzebień, rozsunięcie S1, zamiana bramek, 4 wątki routera): po routerze i sprzątaniu zostaje **16–29 otwartych połączeń sygnałowych** (liczone DRC; licznik Freeroutingu zaniża), planer domyka kilka. Rozrzut między przebiegami ±5–8, więc pojedyncze porównania wariantów nie są rozstrzygające. Wąskie gardła: pas między J_BP2 a strefą anteny (pod nim nie ma miedzi), góra S1 (J_BP1, rząd SOIC, U1 jako ściana), przejście z rzędu J1 modułu do S3 (SPI3/TC, SUP_N).
- **Decyzje użytkownika (30.09):** ścieżki sygnałowe 0,2 mm przy odstępie 0,25 mm (zasilanie bez zmian: 5 V 1,5/0,6 mm, 3V3_CORE 0,3 mm; odstępstwo od S1 §3 tylko dla P03 R6); zamiana bramek LOGGER_CURRENT_OK i SENSOR_HEALTHY z U12 (kanały 3/4) na wolne kanały U14 (oba końce w S1), z tym kołek serwisowy LOGGER_CURRENT_OK na J_SV1.10, SUP_N na J_SV3.12; commity i push etapami na tę gałąź.
- **Wprowadzone (etap 2):** zamiana bramek w `parts.py`/`build_schematic.py` z 10 opisanymi różnicami w `compare_v61.py` i `verify_function.py` (schemat: ERC 0, 511/511, v6.1 18 różnic / 0 nieoczekiwanych, funkcje 53/53, mutacje 44/44, reset 8 + 4/4, J_BP 25/25, tabele PASS; R52 1K ↔ R76 10K, sumy zakupów bez zmian); reguły w `set_rules.py` (Default 0,2 mm, klasa CORE3V3 0,3 mm, PWR 0,6 mm), `build_board.py`, `verify_pcb.py`, planer 0,2 mm; `placement.py`: C13 obrót 270 (pole 1 na górze, jak mówił komentarz), węzły serwisowe 5V_SYS przy U5.1, ADC_BUSY przy U11.5, HEARTBEAT przy M1 J3-18, SUP_N przy U6.2, rozsunięcie S1 (rząd SOIC y 28, U1 y 45, U2 y 66).

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

1. Recenzja PCB (README, sekcja „PCB”: 9 decyzji, w tym sporne) i przymiarka wydruku 1:1 (`output/pdf/P03-R6-PCB.pdf`, strona 5); wysokość M1 na listwach.
2. Push gałęzi `p03-r6-pcb` i PR — commity są lokalnie na komputerze 24/7; push czeka na logowanie użytkownika do GitHuba na tym komputerze (`gh auth login` albo poświadczenie git). Scalanie dopiero po „scal”.
3. Po akceptacji: paczka produkcyjna (skrypty z `Plytki/P02-PCB-R4-zamowienie/src/`).
4. Odtworzenie: `scripts/egrlab-docker python3 src/run_release.py` (odtwarza `routing/P03.ses` + `completion-routes.json`, ok. 35 min przy 2 rdzeniach); nowe trasowanie: `--new-route` (wynik za każdym razem inny, pętla do 6 prób).
