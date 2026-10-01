# P05 R3 — schemat DAQ w formacie S1 (zadanie dla sesji w chmurze, 1.10.2026)

**Ustawienia sesji:** Opus 5.5, wysiłek high. Gałąź `p05-s1`.

**Zakres:** tylko schemat, kontrole i dokumenty, **bez PCB**. Layout robi sesja lokalna (`docs/CHMURA.md`, zasada 6).

**Źródła:**
- `Plytki/Format-S1/SPECYFIKACJA-FORMATU-S1.md` (S1-3) i `format-s1.json` — obowiązują;
- zamknięty pakiet `Plytki/P05-R2-review` — nie zmieniać; to wejście (obwód R2 po recenzji);
- `Plytki/P05-R2-specyfikacja/` i `Plytki/P05-R1-recenzja/` — tylko do sprawdzenia decyzji R2;
- rejestr `Zamowione/zamowione.csv` i bilans zapasu P09 R2 / P10 R2 (`Plytki/P09-R2-review/docs/ZAKUPY.md`, `docs/BOM.csv` obu płytek, kolumna `zrodlo`);
- pinouty P03 R6 i P02 R4 potrzebne P05 — w tabelach niżej (P03 R6 według gałęzi `p03-r6-pcb`, jeszcze nie scalonej).

**Pamięć:** `format-s1.md`, `chmura-limity.md`, `kicad-pipeline-quirks.md`, `p05-r1-review.md`.

## Zasady pracy

Obowiązują zasady 6–9 z `docs/CHMURA.md`:
- commit i push po każdym etapie (złącza, części, kontrole, dokumenty);
- bez procesów dłuższych niż 15 min;
- po dwóch nieudanych próbach zapis stanu i PR.

**Nie zmieniać plików wspólnych:** `EGRLab-AKTYWNE.md`, `docs/01-overview.md`, `docs/CHMURA.md`, `docs/pamiec-claude/`, `scripts/`, `Plytki/Format-S1/`, `.gitignore`.

## Zakres zmian (nowy pakiet `Plytki/P05-R3-review` na kopii łańcucha z R2)

Obwód R2 zostaje: okno DAQ_OK z REF5025IDR (R5 6,04 kΩ, R7 5,11 kΩ), R13 47 kΩ, CH7 = VBAT_SENSE, przekaźniki K1–K3, tor AUX. Zmieniają się złącza do innych płytek, punkty pomiarowe i typy części.

### 1. Płytka

Klasa 2/3 (106,5 × 100 mm), sloty S1–S2 poziomu 3 (dystanse 20 mm). Części od góry ≤ 16,5 mm; od spodu tylko SMD ≤ 1,5 mm, bez SOIC (S1 §4). Brzeg x = 0 płytki to strona panelu (S1 §7: TAPS najkrótszą drogą).

### 2. Dwa złącza J_BP (decyzja użytkownika 1.10.2026, wariant B)

Jedno złącze 2×10 nie mieści 10 sygnałów i dwóch pinów 5V_SYS na pinach parzystych. Są więc dwa kątowe, obudowane złącza IDC na krawędzi A, po jednym na slot. Pin 1 każdego od strony mniejszego x (S1 §5).

**J_BP2 — slot S2 (środek x = 80,0 mm), IDC 2×10: magistrala DAQ.** Ten sam slot i te same numery pinów co DAQ na J_BP2 płytki P03 R6, więc tory na P12 idą prosto w pionie.

| Pin | Sieć | Pin | Sieć |
|---|---|---|---|
| 1 | GND | 2 | ADC_SCLK |
| 3 | GND | 4 | ADC_DOUTA |
| 5 | GND | 6 | ADC_SDI |
| 7 | GND | 8 | ADC_CS |
| 9 | GND | 10 | ADC_CONVST |
| 11 | GND | 12 | ADC_BUSY |
| 13 | GND | 14 | MEAS_EN |
| 15 | GND | 16 | GND (rezerwa) |
| 17 | GND | 18 | ADC_RESET |
| 19 | GND | 20 | GND (rezerwa) |

Na P03 R6 J_BP2 pin 16 to PFAIL_N, a 17, 19 i 20 to 5V_SYS — tych sieci P05 z tego złącza nie bierze.

**J_BP1 — slot S1 (środek x = 26,5 mm), IDC 2×5: zasilanie i sygnały wolne.**

| Pin | Sieć | Pin | Sieć |
|---|---|---|---|
| 1 | GND | 2 | 5V_SYS |
| 3 | GND | 4 | 5V_SYS |
| 5 | GND | 6 | DAQ_OK |
| 7 | GND | 8 | GND (rezerwa, oddziela VBAT_SENSE) |
| 9 | GND | 10 | VBAT_SENSE |

Źródła na P12: 5V_SYS i VBAT_SENSE z J_BP płytki P02 R4 (piny 2/4/6 i 20, S1 §8), DAQ z P03 R6 J_BP2, DAQ_OK do P04 (wariant pełny; w LOGGER bez odbiorcy, linia zostaje).

3V3_IO nie wchodzi na P05: logika ma własne 3V3_DAQ z U12, a LV05.3 w R2 był tylko punktem kontrolnym. Usunąć go z ODBIOR, a wyjątek od S1 §5 („3V3_IO na co najmniej 1 pinie”) opisać w README jednym zdaniem.

J_BP1 i J_BP2 zastępują J1 (B2B DAQ do P03), J2 LV05, J3 DAQOK i J5 VSENSE. Sieci i funkcje bez zmian.

### 3. Połączenia, które zostają przewodami (S1 §5)

- J4 TAPS (pary sygnał/GND z P11, lutowane do PTH) — przy brzegu x = 0.
- J6 AUX (RG174 do BNC na panelu).

W README zapisać wymaganie dla layoutu: J4, J6 i SW1 od strony x = 0.

### 4. SW1 (AUX HI/LO)

Decyzja z 29.09.2026: zamiast C&K 7201SYCBE **E-Switch 100DP1T1B1M2REH** (Mouser 612-100-F1122). Ma złocone styki, nóżki do druku i korpus jak C&K 7201 (`docs/pamiec-claude/egrlab-purchasing-state.md`, baner `Plytki/Zakupy-2/ZAKUPY-2.md`). Styki jak w R2: wspólne 2/5, HI 2-1 + 5-4, LO 2-3 + 5-6 — sprawdzić z kartą E-Switch, a footprint wziąć z karty; rozstaw nóżek był „do potwierdzenia”. Dostęp do dźwigni (przez panel przy x = 0 albo od strony B) rozstrzygnie layout.

(Poprawka 1.10.2026: pierwsza wersja zadania kazała zaproponować typ — decyzja już była.)

### 5. Listwy serwisowe (krawędź B, S1 §6)

J_SV1 (slot S1, x = 10–43 mm) i J_SV2 (slot S2, x = 63,5–96,5 mm): kątowy goldpin 1×N, N ≤ 13, GND na pierwszym i ostatnim pinie.

- **Treść:** punkty z `docs/ODBIOR.md` R2, co najmniej: 5V_SYS, 5VA_P05 (za R1), 3V3_DAQ, REF_2V5, DAQ_OK, MEAS_PERMIT, MEAS_EN, ADC_RESET, ADC_BUSY, ADC_CONVST, ADC_CS, MEAS_COIL_LOW (U4.18, krok 10b) i VBAT_SENSE.
- **Grupy:** zasilania i analog na J_SV1, sygnały DAQ na J_SV2 (bliżej J_BP2). Layout może przestawić kołki według położenia węzłów; wtedy zmienia się tylko przydział w `SERWIS.csv`.
- **Rezystory:** każdy kołek poza GND przez rezystor szeregowy przy węźle — 1 kΩ dla szyn do 5 V i logiki, 4,7 kΩ dla VBAT_SENSE (do ok. 16 V), 10 kΩ dla węzłów wysokoimpedancyjnych (REF_2V5, dzielniki).
- **Numeracja:** zawsze od pinu 1. Nie pisać „od strony mniejszego x”: kątowa listwa od góry, z kołkami za krawędzią B, ma pin 1 przy większym x (wniosek z layoutu P09/P10 R2).
- **ODBIOR R3:** pomiary z kroków 3–10b na kołkach listew zamiast na LV05 i polach testowych.

### 6. Części (S1 §1 i §4)

- **R i C:** posiadane THT z rejestru tylko tam, gdzie po P09 R2 i P10 R2 zostaje zapas — rezystory na stojąco (`R_Axial_DIN0207_L6.3mm_D2.5mm_P5.08mm_Vertical`). Pozostałe nowe jako SMD 1206 (`R_1206_3216Metric_Pad1.30x1.75mm_HandSolder`, `C_1206_3216Metric_Pad1.33x1.80mm_HandSolder`). Bilans zapasu zapisać w `docs/ZAKUPY.md`.
- **Rezystory precyzyjne R2** (MBB0207 0,1 %: R3–R8, R28, R29, R31–R35): SMD 1206, 0,1 %, TCR ≤ 25 ppm/K. W `verify_electrical.py` przeliczyć budżet okna DAQ_OK i dzielników dla parametrów wybranej serii. MPN do pytań PR.
- **Wyjątki z uzasadnieniem w README:** C12/C13 22 µF w 1210, jeśli 1206 nie da Ceff ≥ 10 µF z kroku 11 ODBIOR; C1 470 µF elektrolit radialny; R1 1 Ω według mocy; diody i układy bez zmian.
- **Od spodu:** tylko SMD ≤ 1,5 mm (bez wyższych 1206 i bez SOIC).
- **Footprinty złączy jak w P03 R6 / P10 R2:** `Connector_IDC:IDC-Header_2x10_P2.54mm_Horizontal`, `Connector_IDC:IDC-Header_2x05_P2.54mm_Horizontal`, `Connector_PinHeader_2.54mm:PinHeader_1x13_P2.54mm_Horizontal` (lub 1×N).

### 7. Kontrole

- ERC 0.
- Netlista pin po pinie z `parts.py`.
- Kontrole elektryczne z R2 poprawione pod nowe złącza i typy części: okno DAQ_OK, Ioff, zasilanie wsteczne 3V3_DAQ.
- Nowe kontrole z próbami ujemnymi:
  - pinout J_BP1 i J_BP2 dokładnie jak w tabelach (DAQ na tych samych pinach co P03 R6 J_BP2);
  - każda sieć dawnych J1, J2, J3 i J5 jest na J_BP dokładnie raz (5V_SYS dwa razy);
  - piny nieparzyste J_BP to GND;
  - ADC_SCLK i MEAS_EN mają GND po obu stronach w rzędzie;
  - TAPS (J4) i AUX (J6) nie wchodzą na J_BP;
  - listwy mają ≤ 13 kołków, GND na końcach i rezystor przy węźle o wartości według S1 §6.
- Próba zerowa.

### 8. Pliki dla P12 i README

- `docs/J_BP.csv`: kolumny `zlacze;pin;siec;kierunek;plytka_docelowa;uwagi` (jak P03 R6).
- `docs/SERWIS.csv`: kolumny `zlacze;pin;siec;rezystor;cel_pomiaru`.
- `docs/ODBIOR.md` R3.
- `docs/MECHANIKA.md` bez mating P03/P05 i B2B.
- `docs/interfejsy.csv` i wiązki: zostają TAPS i AUX.
- README:
  - tabela zmian R2 → R3 i liczby z kontroli;
  - wymagania dla layoutu: J4, J6 i SW1 od strony x = 0; J_BP2 w S2; odsprzęganie U1 według `Plytki/P05-R2-review/wip-layout-obrys-R1/` (opisy „Cx przy U1.nn” zostają);
  - otwarte punkty: MPN rezystorów precyzyjnych, zapas z rejestru, rozstaw nóżek SW1 z karty;
  - pojemność 5V_SYS: C1 470 µF za R1 1 Ω razem z P06 C3 (też 470 µF za 1 Ω) daje ok. 986 µF wobec 600 µF dopuszczalnych dla TSR 2-2450 (karta TRACO; `Plytki/P12-przygotowanie`, gałąź `p12-przygotowanie`). Nie zmieniać C1 bez decyzji użytkownika; zapisać jako otwarty punkt.

## Wynik

PR po polsku. Pytania wpisać do opisu PR. Nie włączać śledzenia PR, a po otwarciu PR zakończyć pracę.
