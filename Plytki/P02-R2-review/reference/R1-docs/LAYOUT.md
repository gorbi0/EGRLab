# P02 PCB R1 — layout

25.09.2026 · Claude. Płytka z netlisty schematu P02-R1 (`verification/P02.xml`), rozmieszczenie `src/placement.json`, trasy mocy `src/route_critical.py`, sygnały Freerouting 2.1.0. Wszystkie liczby poniżej pochodzą z `verification/pcb-checks.json` (świeży DRC i pomiar gotowej płytki).

## Format

160 × 120 mm, 2 warstwy po 70 µm, laminat 1,6 mm, otwory M3 NPTH 3,2 mm w tych samych miejscach co P01 (5/155 × 5/115 mm) z obszarem bez miedzi Ø8 mm na obu warstwach. Reguły DRC jak w P01: prześwit 0,25 mm (klasa domyślna 0,30 mm), ścieżka ≥ 0,3 mm, miedź od krawędzi 0,5 mm; bez wyjątków DRC.

## Rozkład funkcjonalny

| Strefa | Zawartość |
|---|---|
| Górny pas, od x = 44 mm | Bank C1–C3 (Ø35 × 45 mm, co 39 mm), między puszkami R1 (bleeder) i R6 (góra dzielnika banku) wprost na szynie |
| Lewy górny róg | J13 (R_CHARGE, górna krawędź), J1 SUPPLY (lewa krawędź), D2, D1, F1 pionowo przy C1 |
| Lewa krawędź | J2 VMOTOR (wtyk od lewej), F4 i J11 VSENSE (dół) |
| Środek | F2/F3 → U1/U2 z kondensatorami, pola 3V3/GND/5V |
| Prawa połowa | Nadzór: U4/U3 → U5 (adapter SO14) → U6; komparator U7 z U8, dzielnikami i filtrami; wyjście HOLD_READY (R14–R16, LED1), J12 PSUOK przy prawej krawędzi |
| Dolny pas | J11 VSENSE i J3–J10 (LV03–LV10) w jednym rzędzie, szyny 5V_SYS nad nim i 3V3_IO pod nim |

## Tory mocy (zablokowane przed autorouterem)

| Sieć | Wykonanie | Uwagi |
|---|---|---|
| VPROT wejście/silnik | strefa F.Cu 189 mm² łączy J1.1, J2.1, TP1, R9.1; na całej drodze J1.1 → J2.1 ≥ 4 mm miedzi | IPC-2221 przy 5 A i 4 mm × 70 µm: przyrost ok. 2 K |
| Powrót silnika | płaszczyzna GND B.Cu; korytarz J2.2 → J1.2 zakazany dla ścieżek i przelotek | pad J1.2 ma własne szprychy 1,2 mm z footprintu P01 |
| VPROT gałęzie | D1.1 1,5 mm; J13.1 (R_CHARGE) 1,0 mm; F4.1 (VSENSE) 1,2 mm | najwęższa ścieżka VPROT 1,0 mm |
| CHARGE_D | J13.2 → anody D2 (1 i 3) 1,0 mm | prąd ładowania ≤ 0,68 A (32 V / 47 Ω) |
| HOLD_FUSED | D2.K, D1.A2 → F1.1, 1,5 mm | |
| HOLD_STORE | F1.2 → szyna 2,5 mm pod puszkami (C1+, C2+, C3+), odczepy R1, R6, TP3 | odcinek bez bezpiecznika F1.2 → C1+ 24 mm; cała miedź tej sieci zablokowana i nie opuszcza płytki |
| GND banku | szyna F.Cu 2,5 mm po stronie „−” + płaszczyzna B.Cu | |
| VLOG_RES | D1.K → C4 → F2.1/F3.1, 1,5 mm | |
| Wejścia przetwornic | F2.2 → U1.1 → C5, F3.2 → U2.1 → C7, 1,0 mm | |
| 5V_SYS | U1.3 → C6 → pion x = 66,5 mm → szyna y = 99 mm, 1,5 mm; odczep 1,2 mm do każdego LV pin 1; zasilanie U4/C10 0,8 mm | 2 A (granica TSR2) daje ok. 1 K przyrostu |
| 3V3_IO | U2.3 → C8, pion x = 43,4 mm → szyna y = 115,5 mm, 1,5 mm; odczep 1,2 mm do każdego LV pin 3 | szyna pod rzędem, bo pin 3 leży w drugim rzędzie Mini-Fit |

Każda szyna ma wierzchołek w miejscu każdego odczepu — Freerouting nie widzi odczepu kończącego się w środku odcinka (lekcja z P01).

**Dzielniki komparatora przy źródłach.** R6 (267 k) stoi na szynie banku, R9 (348 k) w strefie VPROT. Długie ścieżki do U7 niosą już węzły BANK_DIV i VPROT_DIV, więc zwarcie takiej ścieżki nie może rozładować banku ani obciążyć VPROT przez cienką miedź. Filtry C14/C15 (100 nF) są przy wejściach U7: 11,9 i 4,1 mm trasy.

## Sygnały i masa

Freerouting prowadził tylko sieci sygnałowe i zasilanie bloku nadzoru. GND i VPROT były wyjęte z jego listy (pady jako przeszkody), strefa VPROT była dla niego obszarem zakazanym — w pierwszej próbie poprowadził GND ścieżką F.Cu przez strefę i ją przeciął. Wynik: 140 odcinków autoroutera, żadnej przelotki (warstwę zmieniają pady THT), na B.Cu 79 odcinków sygnałowych o łącznej długości 415 mm.

Masa to dwie wylewki: B.Cu jedna wyspa na 86,8 % płytki, F.Cu 79,1 % w dwóch wyspach połączonych padami GND elementów THT. Przelotek zszywających nie ma; jeśli recenzja uzna je za potrzebne, dojdą w R2 w wolnych polach F.Cu.

Odsprzęganie: każdy 100 nF ≤ 7,6 mm w linii prostej i ≤ 9,7 mm po miedzi od pinu zasilania swojego układu. C5–C8 i C4 ≤ 7,6 mm od pinów przetwornic i D1.K.

## Nadruk

Oznaczenia leżą poza obrysami innych elementów i najbliżej własnego (kontrola w `verify_pcb.py`); rezystory, DIP-y, adapter, oprawki i puszki mają oznaczenie wewnątrz własnego obrysu, jak w P01. Opisy dodatkowe: nazwy LV03–LV10 pod złączami, piny J1/J2/J12/J13/J11, sieci przy polach pomiarowych, wartości wkładek F1–F4, `HOLD_STORE 40J` / `NIE ZWIERAC!` przy TP3, ostrzeżenie o energii banku, `HOLD READY` przy LED. Nie ma ich pod korpusami (poza przewodami lutowanymi J1/J12/J13).

## Czego nie sprawdzono

Przymiarka 1:1, nagrzewanie przy 5 A i przy ładowaniu banku, odbiór HOLD (Ceff, spadek, 50 ms przy 6 W), zachowanie przy zwarciu. Stan sprzętu: NIE ZBADANO.
