# P05 R2 — zadanie dla sesji w chmurze (29.09.2026)

> **29.09.2026 — format S1:** layout P05 R2 (punkt 3 zakresu) jest wstrzymany, bo płytki przechodzą na stos S1 (`Plytki/Format-S1/SPECYFIKACJA-FORMATU-S1.md`). Z tego zadania obowiązują zmiany schematu i dokumentów (punkty 1, 2, 4, 5 i 6). Layout wykona nowe zadanie P05 w formacie S1.

Źródła: recenzja `Plytki/P05-R1-recenzja/RECENZJA-P05-R1.md` (uwagi P5-01…P5-09, „Kolejność dla R2”), zamknięty pakiet `Plytki/P05-R1-review` (nie zmieniać), decyzje z 29.09 w `EGRLab-AKTYWNE.md`. Pamięć: `docs/pamiec-claude/p05-r1-review.md` i `kicad-pipeline-quirks.md` (zwłaszcza lokalna zmiana przez zasianie SES, jak w P03 R4).

Ustawienia sesji: Opus 5.5, wysiłek high. Gałąź `p05-r2`.

## Praca równoległa z P02 R4

Równolegle działa sesja P02 R4 (gałąź `p02-r4-schemat`). **Nie zmieniać plików wspólnych:** `EGRLab-AKTYWNE.md`, `docs/01-overview.md`, `docs/CHMURA.md`, `docs/pamiec-claude/`, `scripts/`, `.gitignore`. Stan i wyniki opisać w `Plytki/P05-R2-review/README.md` i w opisie PR; pliki wspólne uzupełni sesja lokalna po scaleniu. Środowisko: `bash scripts/setup-chmura.sh` z gałęzi `main` (bez zmian w skrypcie).

## Zakres R2

Nowy pakiet `Plytki/P05-R2-review` na kopii łańcucha z `P05-R1-review/src`.

1. **Wartości (P5-02, P5-05):** R5 5,90 kΩ → 6,04 kΩ, R7 5,23 kΩ → 5,11 kΩ (0,1 %, 25 ppm, ta sama seria), R13 10 kΩ → 47 kΩ. W `verify_electrical.py` nowe narożniki progów DAQ_OK (tabela w recenzji: dolny 4,753–4,848 V, górny 5,138–5,234 V).
2. **U2: ADR4525BRZ → REF5025AIDR** (zamiana z listy zakupowej 2; ADR4525 niedostępny do 2027). Ten sam układ SOIC-8: 2 VIN, 4 GND, 6 VOUT; 3 TEMP i 5 TRIM/NR niepodłączone, pozostałe według karty TI. Sprawdzić wymagany kondensator wyjściowy (dziś C24 1 µF) i uwzględnić dokładność 0,05 % w modelu okna.
3. **Layout (P5-01)** według „Propozycji dla R2” w recenzji:
   - C13, C11/C12, C10, C9 i po jednym 100 nF dla AVCC 37/38 i 48 przy pinach U1: droga ≤ 3 mm (0603/0805) i ≤ 6 mm (1210), ścieżki ≥ 0,4 mm, 5VA do AVCC ≥ 0,5 mm albo wylewka;
   - własne przelotki GND dla tych kondensatorów oraz REFGND 43/46 i AGND 40/41/47;
   - ≥ 1 mm między polami kondensatorów a końcami padów U1;
   - TP13–TP16 przy ich kondensatorach;
   - DOUT (AD_DOUT_LOCAL) poza obrysem U1, strefa `ANALOG_GND_PLANE_*` na cały obrys (x ≥ 101 mm);
   - w `verify_pcb.py` limity drogi dla każdego pinu zamiast „≤ 15 mm” i próba ujemna (C13 przesunięty o 5 mm).
   Zmiana lokalna przy U1: obrys, otwory montażowe (wspólny raster kasety, `Plytki/Kaseta-R1`) i położenie złączy, zwłaszcza B2B J1 do P03, bez zmian. Miedź poza obszarem zmian taka jak w R1 (zasianie SES).
4. **Nazwy arkuszy:** `AUX.kicad_sch` → `AUX_IN.kicad_sch`, `CON.kicad_sch` → `ZLACZA.kicad_sch` (nazwy zarezerwowane w Windows, `docs/CHMURA.md`).
5. **CH7:** sieć `VPROT_SENSE` → `VBAT_SENSE` (P02 R4 J11.1: akumulator auta przez 10 kΩ i P6KE24CA). Dzielnik bez zmian (zakres z zapasem). J5 bez zmian (przylutowana para AWG22, pozycje 1/2).
6. **Dokumenty (P5-03, P5-07, P5-08):**
   - `ODBIOR.md`: kroki 3, 5 i 7 według recenzji, kontrole przekaźników (zadziałanie ≤ 3,9 V przy ok. 23 °C, VDS U4.18 ≤ 0,3 V);
   - `INTEGRACJA.md`: ≥ 10 ms od stabilnego AVCC/VDRIVE do resetu, kalibracja w firmware;
   - arkusz ADC: opisy „Cx przy U1.nn”;
   - budżet pojemności 5V_SYS (P5-07).

## Bez zmian w R2

- **SW1 zostaje C&K 7201.** Zamiennik wybierze sesja lokalna. Tor AUX przenosi sygnały rzędu µA, więc liczą się złocone styki.
- **P5-06 bez diody 1N5817.** *Decyzja sporna:* recenzja ocenia ryzyko jako małe, a użytkownik odchudza BOM z elementów na wyrost.
- P5-09 (okno bez histerezy) i przekrój mechaniczny B2B — osobno.

## Wynik

PR po polsku:
- tabela zmian R1 → R2;
- liczby z kontroli: ERC, DRC, `verify_electrical`, `verify_pcb` z drogami dla każdego pinu U1 przed i po, próby ujemne;
- zrzut obszaru U1 przed i po;
- lista otwartych punktów.

Pytania wpisać do opisu PR. Nie włączać śledzenia PR.
