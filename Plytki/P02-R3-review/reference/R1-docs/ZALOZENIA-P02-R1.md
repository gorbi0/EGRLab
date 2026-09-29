# P02 PSU + HOLD — karta założeń przed schematem i PCB (R1)

25.09.2026 · Claude (karta sprzed schematu; sekcje „Zmiany w trakcie projektu” i „Do decyzji w recenzji” dopisane przy wydaniu PCB R1). Źródła: import pinowy P02 z v6.1-rc1 (`reference/v6.1-P02-import.xml`), obwód HOLD C1 z pakietu P01-R3 (`reference/PROJEKT.md`, `contract.json`), interfejsy v6.1 (`hardware/wiring.csv`, `docs/02-interfejsy.md`). Do recenzji: Astra.

## Decyzje użytkownika (25.09.2026)

1. **Bank HOLD na płytce P02.** Jedna płytka: przetwornice, rozdział LV03–LV10, SUPPLY, VSENSE, VMOTOR i bank. Znika ryzyko zamiany wtyków HOLD/SUPPLY z C1.
2. **HOLD_READY tylko lokalnie.** Komparator, LED, pole pomiarowe i zarezerwowany pin 3 w PSUOK. P03/P04 bez zmian; podłączenie do CORE później.

## Funkcja i sieci

| Blok | Połączenia |
|---|---|
| Wejście | J1 (wiązka H_SUPPLY, 2 × 2,5 mm², od P01 J6): VPROT, GND |
| Silnik | J2 VMOTOR → P07: VPROT, GND, NC (VPROT bez buforowania; KPWR na P07) |
| Pomiar | F4 F100 mA → VPROT_SENSE → J11 VSENSE (14p, piny 1/2, reszta NC) do P05 |
| Rezerwa | D1 (D_OR, STPS20100CT): A1 = VPROT, K = VLOG_RES, A2 = HOLD_FUSED. Ładowanie: VPROT → R_CHARGE 47 Ω / 25 W (poza płytką, J13) → D2 (anody razem) → HOLD_FUSED → F1 T2A → HOLD_STORE → 3 × 22 mF / 35 V + R1 4k7 |
| Przetwornice | VLOG_RES → F2 1 A → U1 TSR 2-2450 → 5V_SYS; VLOG_RES → F3 1 A → U2 TSR 2-2433 → 3V3_IO; C_BUS 22 µF na VLOG_RES |
| Rozdział | J3–J10 = LV03–LV10: 1 = 5V_SYS, 2 = GND, 3 = 3V3_IO, 4 = GND |
| Nadzór (v6.1) | U3 MCP120-300 (3V3_IO), U4 MCP120-450 (5V_SYS) → U5 74LVC125A (przejście 5→3,3 V) → U6A 74HC08 → PSU_OK → J12 PSUOK pin 1 |
| HOLD_READY (nowe) | U7 LM2903 zasilany z 5V_SYS, U8 TL431 2,5 V. Kanał A: HOLD_STORE ≥ 9,5 V (spadek ok. 9,1 V). Kanał B: VPROT ≥ 11,6 V (spadek ok. 11,1 V). HOLD_READY = BANK_OK ∧ VPROT_OK ∧ PSU_OK (U6B, U6C) → LED, TP, J12 pin 3 przez 1 kΩ |

## Wymagania przeniesione z C1 i v6.1

- Podtrzymanie 50 ms przy ≤ 6 W na VLOG_RES, VLOG_RES ≥ 7 V, bank ≥ 9,5 V przed zdarzeniem; Ceff ≥ 52,8 mF. Spadek bank → VLOG_RES ≤ 1,2 V.
- Bank nie jest widziany bezpośrednio przez P01. Na VPROT/VLOG_RES z P02 wchodzą bezpośrednio tylko C_BUS 22 µF i wejścia przetwornic (2 × 10 µF + ich wnętrze), razem z P01 C3 poniżej limitu 220 µF.
- R_CHARGE HSA2547RJ **poza płytką**, na osobnej blasze; na P02 tylko dwa pola lutownicze z kotwą. Moc ≤ 7,26 W przy 18 V, ≤ 22,94 W przy krótkim 32 V.
- D_OR ma **oddzielne anody**; nie wolno go zamienić na wariant ze wspólną anodą.
- PSU_OK zachowuje znaczenie z v6.1 (nadzór szyn). HOLD_READY to osobna żyła, nie dodatkowe znaczenie PSU_OK.

## Decyzje projektowe R1 (do recenzji)

| Decyzja | Uzasadnienie |
|---|---|
| Kwalifikacja „VPROT stabilne ≥ 15 s” **nie w sprzęcie**, tylko w firmware CORE (VPROT widzi przez VSENSE/DAQ) | RC 15 s na wejściu bramki CMOS daje wolne zbocze i ryzyko oscylacji; C1 mówi, że sam timer nie dowodzi naładowania — dowodem jest pomiar banku, który jest w sprzęcie |
| **VMOTOR: GMSTBA 2,5/3-G-7,62 (1766246, 12 A)** zamiast PC 4/3-G-7,62 (sporne) | Brak zweryfikowanego footprintu PC 4; raster 7,62 nadal wyklucza pomyłkę z SUPPLY 5,08; system ma bezpiecznik 5 A; P07 wstrzymany, więc wtyk P07 i tak nie jest kupiony |
| Oprawki 5×20 Stelvio-Kontek PTF78 dla F1–F4 | Footprint w bibliotece KiCad, powszechne w PL; wkładki z parametrem DC do doboru przy zakupie |
| Mini-Fit Jr 5566 pionowe (LV 2×2, VSENSE 2×7) | Footprinty KiCad; wersja ze stykami Au do doboru MPN przy zakupie |
| U5 na adapterze Kamami SO14 → DIP (rzędy 15,24 mm) | Adapter już kupiony; własny footprint 18 × 18 mm |
| Płytka 160 × 120 mm, 2 × 70 µm, otwory M3 jak P01 | Ten sam format i mocowania co P01 (stos modułów); 70 µm na torze VPROT J1 → J2 (do 5 A) |

## Zmiany w trakcie projektu (po tej karcie, przed wydaniem R1)

| Zmiana | Uzasadnienie |
|---|---|
| Górne rezystory dzielników **przy źródłach**: R6 na szynie banku, R9 w strefie VPROT; reszta dzielnika (R7/R8, R10/R11) i filtry C14/C15 przy U7 — odstępstwo od wymogu „dzielniki przy U7” | Cienka ścieżka pomiarowa z HOLD_STORE albo VPROT przez pół płytki nie jest zabezpieczona żadnym bezpiecznikiem; po zmianie długie ścieżki niosą węzły za 267 k/348 k. Filtry zostają przy wejściach komparatora (11,9 i 4,1 mm) |
| Rezystory MF0207 (Yageo, 0,6 W, raster 10,16 mm) zamiast MFR-50 | Ta sama seria co zakupy P01 (część wartości pokrywa zapas); R1 (bleeder) ma przy 32 V 0,22 W |
| Kondensatory 100 nF: footprint `C_Vishay_K15_H5_P5` wprost z biblioteki P01 R3.1 | Zrecenzowany przy P01; własna wersja miała nadruk nachodzący na pady |
| Węzeł VPROT jako strefa F.Cu; powrót 5 A w płaszczyźnie GND B.Cu z korytarzem bez ścieżek i przelotek | Strefa daje ≥ 4 mm miedzi na całej drodze J1 → J2 bez długiej szyny; korytarz chroni ciągłość płaszczyzny pod torem silnika |
| Pola pomiarowe: TP1 w strefie VPROT, TP2 przy C4, TP3 przy F1.2, rzędy TP5/TP6/TP4 i TP7–TP10 z własnymi opisami | Pola sieci mocy bez cienkich odgałęzień; pola sygnałowe w rzędzie z GND obok, pod sondę z krótką masą |

## Do decyzji w recenzji (nowe przy layoucie)

| Decyzja R1 | Za | Przeciw / alternatywa |
|---|---|---|
| **TP3 wprost na HOLD_STORE** (strona banku bez bezpiecznika) | Pomiar Ceff i spadku (odbiór C1) potrzebuje napięcia samego banku, bez spadku na F1 | Ześlizgnięcie sondy na GND = zwarcie banku ≥ 40 J. Alternatywa: pole przez szeregowy 1 k (multimetr i skop 10 MΩ mierzą bez błędu) albo pole na HOLD_FUSED |
| Brak przelotek zszywających GND | B.Cu to jedna wyspa na 86,8 % płytki; wyspy F.Cu są połączone padami THT | Kilka przelotek w wolnych polach F.Cu to tanie wzmocnienie; można dodać w R2 |
| Bank w górnym pasie płytki (45 mm wysokości) | Najkrótsza droga F1 → bank, bank daleko od przetwornic i TO-220 | Nad P02 potrzeba ok. 50 mm w stosie — P02 raczej na górze albo obok |

## Wymagania rozmieszczenia (sprawdzane po layoucie)

- Tor VPROT J1 → J2 krótki i szeroki (do 5 A); powrót GND tą samą drogą.
- Bank: 3 × Ø35 × 45 mm, snap-in P10, odstęp ≥ 3 mm, nic nad zaworami; ≥ 10 mm od TO-220 i przetwornic.
- F1 blisko banku (ogranicza energię do zwarcia za nim); D1/D2 blisko F1 i J13.
- C_BUS przy D1.K; kondensatory wejściowe przy przetwornicach; 100 nF przy każdym układzie (≤ 8 mm do pinu zasilania).
- Dzielniki komparatora przy U7, z dala od ścieżek mocy; LED widoczna od góry.
- Oprawki bezpieczników dostępne od góry, nie pod wiązkami.
- Wiązki: J1, J12 (PSUOK), J13 (R_CHARGE) z kotwami 12,5 mm od lutów; złącza przy krawędziach.
- Pola pomiarowe: VPROT, VLOG_RES, HOLD_STORE (opis: energia ≥ 40 J), 5V_SYS, 3V3_IO, PSU_OK, HOLD_READY, REF, GND.

## Poza zakresem R1

Firmware CORE, podłączenie HOLD_READY do P03/P04, dobór DC-rated wkładek i MPN złączy Mini-Fit (lista do zakupu), mechanika blachy R_CHARGE i osłon zacisków banku, obudowa. Sprzęt: NIE ZBADANO.
