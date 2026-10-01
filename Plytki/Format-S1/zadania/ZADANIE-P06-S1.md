# P06 R2 — schemat I-LOGGER w formacie S1 (zadanie dla sesji w chmurze, 1.10.2026)

**Ustawienia sesji:** Opus 5.5, wysiłek high. Gałąź `p06-s1`.

**Zakres:** tylko schemat, kontrole i dokumenty, **bez PCB**. Layout robi sesja lokalna (`docs/CHMURA.md`, zasada 6).

**Źródła:**
- `Plytki/Format-S1/SPECYFIKACJA-FORMATU-S1.md` (S1-3) i `format-s1.json` — obowiązują;
- zamknięty pakiet `Plytki/P06-R1-review` — nie zmieniać; to wejście (obwód R1);
- pinouty sąsiadów na `main`: `Plytki/P03-R6-review/docs/J_BP.csv` (gałąź `p03-r6-pcb`, scalenie wkrótce) i `Plytki/P05-R3-review/docs/J_BP.csv`;
- kontrakty P12: `Plytki/P12-przygotowanie/wyniki/KONTRAKTY.md` (sieci czekające na P06);
- rejestr `Zamowione/zamowione.csv` i BOM-y płytek, które biorą z tego samego zapasu: P02 R4, P05 R3, P09 R2, P10 R2 (kolumna `zrodlo`); bilans zbiorczy: `Plytki/Zakupy-3-szkic`.

**Pamięć:** `format-s1.md`, `chmura-limity.md`, `kicad-pipeline-quirks.md`.

## Zasady pracy

Obowiązują zasady 6–9 z `docs/CHMURA.md`:
- commit i push po każdym etapie (złącza, części, kontrole, dokumenty);
- bez procesów dłuższych niż 15 min;
- po dwóch nieudanych próbach zapis stanu i PR.

**Nie zmieniać plików wspólnych:** `EGRLab-AKTYWNE.md`, `docs/01-overview.md`, `docs/CHMURA.md`, `docs/pamiec-claude/`, `scripts/`, `Plytki/Format-S1/`, `.gitignore`.

## Decyzje użytkownika (1.10.2026)

- **Klasa 2/3** (106,5 × 100 mm), sloty S1–S2 poziomu 4 (P10 stoi w S3 tego poziomu). Skutek: wariant pełny dostaje szósty poziom (S1 §7).
- **Bocznik:** SMD 2512 z wyprowadzeniami Kelvina zamiast PBV (zamiana przyjęta 28.09).
- **BYPASS zostaje:** przełącznik na panelu, poza PCB — zwykły DPDT ON-ON ≥ 10 A DC zamiast NKK S6A.
- **C3 = 220 µF** (było 470 µF; razem z P05 C1 220 µF szyny 5 V mają ok. 486 µF wobec 600 µF dla TSR 2-2450).

## Zakres zmian (nowy pakiet `Plytki/P06-R2-review` na kopii łańcucha z R1)

Obwód R1 zostaje: INA240A2 z filtrem R1/R2 10 Ω, dzielnik R3/R4, MCP6022, MCP3201, nadzorcy MCP120, bufory 74LVC125 z Ioff, logika LOGGER_CURRENT_OK, R21 (prąd zwilżania styku statusu BYPASS). Zmieniają się złącza do innych płytek, bocznik, punkty pomiarowe i typy części.

### 1. Płytka

Klasa 2/3, sloty S1–S2 poziomu 4 (dystanse 20 mm). Części od góry ≤ 16,5 mm; od spodu tylko SMD ≤ 1,5 mm, bez SOIC (poziom 4, S1 §4 / S1-3). Brzeg x = 0 płytki to strona panelu (S1 §7: ISERIES najkrótszą drogą).

### 2. J_BP — jedno złącze w slocie S2

IDC 2×8 kątowe, obudowane, na krawędzi A, środek x = 80,0 mm (slot S2), pin 1 od strony mniejszego x (S1 §5). ADC_SCLK i ADC_DOUTA na tych samych pinach co J_BP2 płytek P03 R6 i P05 R3 (2 i 4), więc wspólna magistrala idzie na P12 prosto w pionie; CS_ILOG_N i LOGGER_CURRENT_OK P12 doprowadzi z J_BP1 płytki P03 (slot S1).

| Pin | Sieć | Pin | Sieć |
|---|---|---|---|
| 1 | GND | 2 | ADC_SCLK |
| 3 | GND | 4 | ADC_DOUTA |
| 5 | GND | 6 | CS_ILOG_N |
| 7 | GND | 8 | LOGGER_CURRENT_OK |
| 9 | GND | 10 | 5V_SYS |
| 11 | GND | 12 | 5V_SYS |
| 13 | GND | 14 | 3V3_IO |
| 15 | GND | 16 | GND (rezerwa) |

J_BP zastępuje J1 LV06 i J2 ILOG; sieci i funkcje bez zmian. Kierunki w `docs/J_BP.csv`: ADC_SCLK i CS_ILOG_N — wejścia z P03; ADC_DOUTA — wyjście trójstanowe na wspólną magistralę (P05, P06, P07); LOGGER_CURRENT_OK — wyjście do P03.

### 3. Połączenia, które zostają przewodami (S1 §5)

- J3 ISERIES (2 × 2,5 mm², prąd silnika do 6 A: ECU_P1 / EGR_P1) — przy brzegu x = 0, pola PTH tuż przy boczniku.
- J4 (BYPASS, tor mocy 2 × 2,5 mm²) i J5 (status BYPASS 3 × AWG22) do przełącznika na panelu.

W README zapisać wymagania dla layoutu: J3, J4, J5 od strony x = 0; tor 5–6 A na miedzi 35 µm (S1 §3) jako pola ≥ 4 mm na obu warstwach ze zszyciem przelotkami, możliwie krótki; ścieżki Kelvina od pól pomiarowych bocznika do R1/R2 i INA240 osobno, parą, z dala od toru mocy.

### 4. Bocznik RSH1

SMD 2512 z czterema wyprowadzeniami (Kelvin), 5 mΩ, tolerancja ≤ 1 %, moc ≥ 1 W (przy 6 A: 0,18 W), TCR z karty. Propozycje do sprawdzenia z kartą (układ pól Kelvina, dostępność): Vishay WSK2512R0050FEA, Bourns CSS2H-2512K-5L00F. Footprint z karty producenta; K_PLUS / K_MINUS na polach pomiarowych, ECU_P1 / EGR_P1 na polach prądowych. Kontrola: wyprowadzenia sieci jak w R1 (ECU_P1, K_PLUS, K_MINUS, EGR_P1), obudowa 2512 z 4 polami.

### 5. BYPASS (SW1 poza PCB)

Na PCB zostają tylko pola przewodów J4/J5. W `docs/ZAKUPY.md` wymagania przełącznika: DPDT ON-ON, ≥ 10 A przy 12–30 V DC, oczka lutownicze, montaż w panelu; MPN do potwierdzenia (zakup po akceptacji). R21 39 Ω (ok. 0,6 W): dobrać obudowę według mocy z zapasem (2512 ≥ 1 W albo THT jako wyjątek z uzasadnieniem w README).

### 6. Listwy serwisowe (krawędź B, S1 §6)

J_SV1 (slot S1, x = 10–43 mm) i J_SV2 (slot S2, x = 63,5–96,5 mm): kątowy goldpin 1×N, N ≤ 13, GND na pierwszym i ostatnim pinie.

- **Treść:** punkty z pól testowych R1 (TP1–TP15 bez TP5 = GND): 5V_SYS, 5VA_P06, 3V3_P06, 3V3_IO, REF25, REF_BUF, I_L_OUT, ADC_AIN, SUP3_N, SUP5_N, SHUNT_ENABLED, LOGGER_CURRENT_OK, CS_LOCAL_N, CLK_LOCAL.
- **Rezystory:** każdy kołek poza GND przez rezystor szeregowy przy węźle — 1 kΩ dla szyn do 5 V i logiki, 10 kΩ dla węzłów wysokoimpedancyjnych (REF25, REF_BUF, ADC_AIN, wyjścia z podciąganiem SUP3_N / SUP5_N).
- **Sąsiedztwo (zasada z P03 R6, decyzja 1.10):** szyna tylko obok GND, innej szyny albo linii za 10 kΩ — poślizg sondy nie może podać szyny na węzeł logiki przez 2 kΩ; węzły analogowe (I_L_OUT, ADC_AIN, REF*) nie obok szyn. Wewnętrzne kołki GND są dozwolone. Kolejność w obrębie listwy według położenia węzłów (najmniej przecięć linii rezystor → kołek; layout może ją jeszcze zmienić).
- **Numeracja:** zawsze od pinu 1 (kątowa listwa od góry ma pin 1 przy większym x).
- **ODBIOR R2:** pomiary na kołkach listew zamiast na polach TP; pomiary referencji przez 10 kΩ tylko miernikiem ≥ 1 GΩ albo na węźle przed skręceniem stosu.

### 7. Części (S1 §1 i §4)

- **R i C:** posiadane THT z rejestru tylko tam, gdzie po P02 R4, P05 R3, P09 R2 i P10 R2 zostaje zapas — rezystory na stojąco. Pozostałe nowe jako SMD 1206. Bilans zapasu ze wszystkimi tymi płytkami zapisać w `docs/ZAKUPY.md` (P02 R4 jest zamówiona i ma pierwszeństwo).
- **R3/R4:** 5,11 kΩ 0,1 % (zamiana 1:1 z listy 2) jako SMD 1206, TCR ≤ 25 ppm/K; przeliczyć dzielnik i zakres w kontrolach elektrycznych.
- **C3:** 220 µF / 16 V radialny (decyzja 1.10), R6 1 Ω bez zmian; przeliczyć notatki o starcie i podtrzymaniu.
- **Układy:** typy jak w R1 (INA240A2 i MCP3201 z rejestru, przydział P06); SOIC tylko od góry.
- **Wyjątki z uzasadnieniem w README:** RSH1 2512, C3 elektrolit radialny, R21 według mocy, diody i układy bez zmian obudów.

### 8. Kontrole

- ERC 0; netlista pin po pinie z `parts.py`.
- Kontrole elektryczne z R1 poprawione pod nowe złącza i typy części (INA240, dzielnik R3/R4, MCP3201, logika LOGGER_CURRENT_OK, Ioff buforów).
- Nowe kontrole kontraktu S1 z próbami ujemnymi (wzór: `Plytki/P05-R3-review/src/verify_s1.py`):
  - pinout J_BP dokładnie jak w tabeli; ADC_SCLK / ADC_DOUTA na pinach 2 / 4 jak J_BP2 płytek P03 R6 i P05 R3;
  - każda sieć dawnych J1 / J2 na J_BP dokładnie raz (5V_SYS dwa razy), nieparzyste piny GND;
  - ISERIES i BYPASS (J3, J4, J5) nie wchodzą na J_BP;
  - listwy: ≤ 13 kołków, GND na końcach, rezystor przy węźle w klasie z S1 §6, zasada sąsiedztwa szyn;
  - RSH1: 4 pola, sieci jak w R1; C3 = 220 µF;
  - obwód R1 poza złączami, bocznikiem i polami testowymi bez zmian (porównanie z eksportem R1).
- Próba zerowa.

### 9. Pliki dla P12 i README

- `docs/J_BP.csv`: kolumny `zlacze;pin;siec;kierunek;plytka_docelowa;uwagi` (jak P03 R6 / P05 R3).
- `docs/SERWIS.csv`: kolumny `zlacze;pin;siec;rezystor;cel_pomiaru`.
- `docs/ODBIOR.md` R2, `docs/MECHANIKA.md` (bez wiązek LV06 / ILOG), `docs/interfejsy.csv` i `docs/WIAZKI.md` (zostają ISERIES i BYPASS).
- README:
  - tabela zmian R1 → R2 i liczby z kontroli;
  - wymagania dla layoutu (punkt 3; J_BP w S2; od spodu tylko SMD ≤ 1,5 mm);
  - otwarte punkty: MPN bocznika i przełącznika BYPASS, typ R21, zapas z rejestru.

## Wynik

PR po polsku. Pytania wpisać do opisu PR. Nie włączać śledzenia PR, a po otwarciu PR zakończyć pracę.
