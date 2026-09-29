# P01-PCB-R2 — zmiany względem PCB R1

Podstawa: recenzja `Plytki/P01-PCB-R1-recenzja/RECENZJA-P01-PCB-R1.md`, uwagi PCB1-01…06. R2 przygotował Claude 24.09.2026 tym samym procesem co R1: płytka budowana z zamrożonej netlisty R3, trasy krytyczne ze skryptu, sygnały z Freerouting 2.1.0, kontrole w `verify_pcb.py`. Recenzuje Astra.

**Bez zmian:** schemat R3 (trzy pliki `.kicad_sch` bajtowo zgodne z manifestem R3), wartości, identyfikatory footprintów, geometria i sieci padów, wymiar 160 × 120 mm, otwory M3 oraz położenie HS1/HS2, D2, Q1, J7, D1, J1, LK1, J6, D3, C3 i C4. Przymiarka obudowy z R1 obowiązuje dalej, z wyjątkiem J5 i miejsc opisanych niżej.

## Uwagi recenzji → zmiany → dowód

| ID | Uwaga R1 | Zmiana w R2 | Dowód |
|---|---|---|---|
| PCB1-01 | Radiatory stoją na miedzi różnych sieci (BAT_FUSED pod HS1, GATE/DRAIN pod HS2); izoluje tylko maska | Obszary reguł na F.Cu pod obrysem profilu SK129 z zapasem 0,5 mm: zakaz ścieżek, przelotek i wylewki; wnęka TO-220 otwarta. BAT_FUSED biegnie pod dolną krawędzią strefy HS1 i wchodzi do wnęki od dołu. DRAIN i GATE wychodzą z wnęki HS2 pionowo w dół. Na B.Cu pod profilami zostaje powrót GND 5 mm (Y = 9,5) i wylewka GND; od radiatora oddziela je laminat 1,6 mm | `R2/PCB1-01`, 2 kontrole (w tym wypełniona miedź): PASS; próba `hs_copper` wykryta |
| PCB1-02 | Q2 bez oznaczenia orientacji; odwrotny montaż wyłącza zabezpieczenie | Lokalny footprint TO-220 ma na nadruku obrys korpusu omijający pady i **linię 0,4 mm po stronie taba** (Q1, Q2, D2). Przy Q2 jest dodatkowo napis `TAB`. Pady, courtyard i F.Fab bez zmian | `R2/PCB1-02`: PASS; próba `q2_tab_marker` wykryta |
| PCB1-03 | Rozmieszczenie jak z automatu; OV_REF 107 mm przez tor mocy | Rozmieszczenie w blokach: zasilanie AUX5, odniesienie z komparatorem, nadzór U4, bufor ENABLE, sterowanie bramką (OFF/RELEASE i ON), wyjście, SAFE/PG. R7/R8 przy U2.3, R21 przy Q3, R14/D7/D8/R15 wokół Q6. Długości w tabeli niżej | `R2/PCB1-03` (długości ≤ progów, ≥ 5 mm od miedzi mocy) i kontrola sąsiedztwa: PASS; próba `ovref_near_rail` wykryta |
| PCB1-04 | Wiązka PG z J5 wychodzi w głąb płytki, nad elementy | J5 obrócony z 90° na 180° i przesunięty: pady w poziomym rzędzie na Y = 101 (pad 1 na X = 144,5, pad 6 na X = 131,8), otwory kotwy na Y = 113,5. Przewody schodzą w dół, do dolnej krawędzi; w pasie wiązki nie ma elementów | `R2/PCB1-04`: PASS; kotwy 12,5 mm od lutów: PASS |
| PCB1-05 | C6 18 mm od Q1; pętla G–S ~180 mm² | C6 stoi **we wnęce HS2**: pad GATE 7,7 mm pod Q1.G, pad VS 7,7 mm pod Q1.S. Pętla G–S ma ok. 5 × 7,7 mm, czyli ~40 mm². TP1/TP2 zostały we wnęce: ścieżki 4,71 i 4,85 mm | Kontrola sąsiedztwa: PASS; sondy ≤ 5 mm: PASS |
| PCB1-06 | J1/J2/J4/J8 bez nazw sieci; D9 daleko od Q2 | Napisy: J1 `BAT`/`GND`, J2 `OUT+`/`GND`, J4 `3V3`/`SAFE_N`/`GND`, J8 `S`/`L` (S = PG_SEND, L = PG_LINK; pełne nazwy się nie mieszczą). D9 7,5 / 10,2 mm od G/S Q2 (R1: 32 / 20 mm) | `R2/PCB1-06`: PASS |

## Poprawka spoza recenzji R1: C10 i C11

BOM R3 każe postawić C10 „przy U2”, a C11 „przy U4” (oba 100 nF na AUX5). W R1 C11 stał przy U2, C10 przy U1, a U4 nie miał kondensatora w pobliżu: C11 był 21 mm od U4.2. Recenzja R1 tego nie wyłapała, a pierwszy przebieg R2 powtórzył ten układ. Teraz C10.1 stoi 4,0 mm od U2.8, a C11.1 5,9 mm od U4.2. Kontrola sąsiedztwa sprawdza obie pary (≤ 8 mm). U4 steruje linią OK, która włącza Q1, więc zakłócenie na jego zasilaniu może wyłączyć wyjście.

## PCB1-03 w liczbach

Długość ścieżek po trasowaniu (ta sama miara dla R1 i R2):

| Sieć | R1 | R2 | Najmniejszy odstęp od miedzi mocy w R2 |
|---|---:|---:|---:|
| OV_REF | 107,1 mm | **11,5 mm** | 45,5 mm (R1: OV_REF przecinało BAT_FUSED) |
| OV_SENSE | 51,4 mm | 23,7 mm | 32,5 mm |
| UV_SENSE | 78,7 mm | 28,2 mm | 34,1 mm |
| REF | 97,4 mm | 45,6 mm | 43,7 mm |
| SENSE_RAW | 128,6 mm | 76,6 mm | — |
| OK | 210,4 mm | 103,0 mm | — |
| AUX5 | 168,8 mm | 122,2 mm | — |
| ENABLE | 124,2 mm | **133,3 mm** | — (dłuższa niż w R1; linia cyfrowa z bufora Q6 do trzech bloków) |
| Wszystkie sygnały (bez BAT_FUSED, VS, DRAIN, VPROT, GND) | 1894 mm | 885 mm | |
| Przelotki | 11 | 3 (tylko szyna VS) | |

## Pozostałe zmiany

- **Szyna VS ma wierzchołek przy każdym odczepie i przelotce.** W pierwszym przebiegu odczepy kończyły się w środku odcinka szyny. Freerouting uznał je za niepodłączone i zdublował 11 połączeń. Teraz `r2_cleanup.py` wyszukuje dublujące łańcuchy ogólnie, a nie po liście współrzędnych, i znalazł tylko 2 odcinki: dubel C6.2 na B.Cu, bo pad leży na zablokowanej ścieżce VS. Zapisuje płytkę tylko przy pełnej łączności.
- **Oznaczenia rezystorów** leżą wewnątrz obrysu korpusu (`r2_refs.py`). W gęstych rzędach etykieta nad elementem trafiała obok etykiety sąsiada. Etykiety D7/D8 stoją przy lewych końcach diod.
- **PDF** (`r2_make_pdf.py`) ma własny generator. Płytka stoi z marginesem na A4, jest belka 100 mm, a nadruk odwzorowano z geometrii KiCad. Wydruk KiCad stawiał tę płytkę w rogu arkusza, bo jej początek to (0,0), i drukarka by ją ucięła. Liczby na stronie 1 skrypt czyta z `pcb-checks.json`.
- **Kontrole:** `verify_pcb.py` ma 7 kontroli więcej (blok `R2/…`, łącznie 24), a `negative_controls.py` 3 próby więcej (łącznie 6).

## Uwagi procesowe

- `import_routing.py` zapisuje płytkę wczytaną z `routing/prerouted.kicad_pcb`, więc KiCad nadpisuje `P01.kicad_pro` regułami domyślnymi (odstęp 0,2 mm, odstęp nadruku 0). `set_rules.py` trzeba uruchomić zaraz po imporcie. Wszystkie DRC w tym przebiegu szły już z regułami projektu: klasa Default 0,30 mm, minimum globalne 0,25 mm, ścieżka ≥ 0,30 mm, nadruk 0,15 mm.
- Freerouting 2.1.0 (JRE 21, ten sam zestaw co w R1) zrobił 999 przebiegów i zostawił 1 niedokończone połączenie. Domknęły je wylewki GND dodane przy imporcie: DRC po trasowaniu pokazuje 0 niepołączonych.
- Zapisana wylewka jest aktualna: ponowne wypełnienie daje te same obszary, a hash płytki zgadza się z `pcb-checks.json`.
- W kopiach prób ujemnych nowa ścieżka dodana skryptem do wczytanej płytki potrafiła zapisać się z siecią GND (API KiCad 10). Dlatego próba OV_REF przestawia istniejący odcinek zamiast dodawać nowy. Płytki wydania to nie dotyczy: DRC pokazuje 0 zwarć i 0 rozbieżności ze schematem.

## Do krytycznego sprawdzenia w recenzji R2

1. **C6 i TP1/TP2 we wnęce HS2.** Korpus C6 (WIMA MKS2, 7,2 × 7,2 × 13 mm) stoi 2,75 mm od czoła Q1. Pady TP1/TP2 (2 mm) leżą w kieszeniach: ok. 1 mm od czoła Q1, 1,25/1,45 mm od C6 i 1,6/1,4 mm od ścianek radiatora (wys. 63,5 mm). Przy przymiarce trzeba sprawdzić, czy sonda dojdzie z góry. Jeśli nie, pady są PTH (Ø1 mm) i dostępne od spodu, można też wlutować pętelki.
2. **BAT_FUSED pod HS1: 3 mm zamiast ≥ 5 mm z wytycznej R3 (sporne).** Odcinek X 19,5–48,5 (29 mm) na F.Cu leży między strefą HS1 (Y ≤ 31,3) a padem GND D1.2. Na B.Cu równoległą drogę przecina powrót GND D1 → J7.2. Uzasadnienie: przy F1 = 5 A i 70 µm to wg IPC-2221 ok. +3 °C, 2,4 mΩ i 12 mV spadku, a 5 mm oznaczałoby miedź pod radiatorem albo przesunięcie D1, które jest mechanicznie związane z R1. Jeśli recenzja wymaga 5 mm, od X = 35 da się poszerzyć F.Cu w dół (13,5 mm odcinka); resztę da tylko przeniesienie D1 albo powrotu GND.
3. **Pętla wyłączania Q2 → R27 → GATE → Q1 → VS → Q2.S.** R3 wymaga, żeby była „krótka”. W R2 ma ok. 18 × 15 mm pod szyną VS i ok. 5 × 12 mm we wnęce HS2. Wymiar wyznacza PR02 R27 (raster 17,78 mm), który kończy się przy grzbiecie bramki.
4. **D4 (zener 15 V, G–S Q1).** R3: „C5/C6/D4 lokalnie”. D4 stoi pod szyną VS przy grzbiecie bramki: ok. 19 mm ścieżki od Q1.G i ok. 34 mm od Q1.S (przez szynę). Szybkie zaburzenia G–S bierze C6 we wnęce; D4 ogranicza dłuższe przepięcia.
5. **Etykiety J8** skrócone do `S`/`L`.
6. **Zakupione zamienniki** i wartość R8 (221 kΩ zamiast 220 kΩ) opisuje `docs/ZAKUPIONE-CZESCI.md`. Schematu R3 nie zmieniano; wpis do BOM należy do rewizji schematu.
