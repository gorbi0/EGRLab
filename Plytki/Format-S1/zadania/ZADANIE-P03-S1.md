# P03 R6 — schemat CORE w formacie S1 (zadanie dla sesji w chmurze, 29.09.2026)

**Ustawienia sesji:** Opus 5.5, wysiłek high. Gałąź `p03-s1`.

**Zakres:** tylko schemat i kontrole, **bez PCB**. Layout robi sesja lokalna.

**Źródła:**
- `Plytki/Format-S1/SPECYFIKACJA-FORMATU-S1.md` (S1-2) i `format-s1.json` — obowiązują;
- zamknięty pakiet `Plytki/P03-R5-review` — nie zmieniać;
- `Rewizje/EGRLab-v6.1-rc1/interfejsy.csv`;
- `Plytki/P02-R4-specyfikacja/interfejsy.csv` (PFAIL_N, D-02);
- rejestr zakupów `Zamowione/zamowione.csv`.

**Pamięć:** `format-s1.md`, `chmura-limity.md`, `kicad-pipeline-quirks.md`, `p03-r1-state.md`.

## Zasady pracy

Obowiązują zasady 6–9 z `docs/CHMURA.md`:
- commit i push po każdym etapie (pinout, schemat, kontrole);
- bez procesów dłuższych niż 15 min;
- po dwóch nieudanych próbach zapis stanu i PR.

**Nie zmieniać plików wspólnych:** `EGRLab-AKTYWNE.md`, `docs/01-overview.md`, `docs/CHMURA.md`, `docs/pamiec-claude/`, `scripts/`, `Plytki/Format-S1/`, `.gitignore`.

## Zakres zmian (nowy pakiet `Plytki/P03-R6-review` na kopii łańcucha z R5)

### 1. Trzy złącza J_BP

Trzy kątowe, obudowane złącza IDC 2×10 na krawędzi A, po jednym na slot (środek x = 26,5 mm w slocie): J_BP1 (S1), J_BP2 (S2), J_BP3 (S3).

Zastępują:
- J1 (DAQ B2B do P05);
- J2 ILOG, J3 ITEST, J4 SAFE, J5 DIR, J6 SFAULT, J7 TEMP, J8 CAN;
- J9 PANELCORE;
- J10 LV03.

Sieci i ich funkcje pozostają bez zmian. Zmieniają się tylko złącza.

### 2. Przydział sygnałów do złączy — według slotu płytki docelowej

Płytka połączeń P12 jest krótsza, jeśli sygnał wychodzi ze złącza najbliżej celu.

| Grupa sygnałów | Cel (poziom, slot) | Proponowane złącze |
|---|---|---|
| CAN_TX, CAN_RX | P10 (1, S1) | J_BP1 |
| CS_ILOG_N, LOGGER_CURRENT_OK | P06 (4, S1) | J_BP1 |
| SENSOR_HEALTHY | P08 (5, S1) | J_BP1 |
| MARK, TEST_KEY, LOGGER_CLEAR, TEST_PRESENT, N_J_SCOPE_HOT | P11 (panel, strona x = 0) | J_BP1 |
| DAQ: ADC_SCLK, ADC_SDI, ADC_DOUTA, ADC_CS, ADC_CONVST, ADC_BUSY, ADC_RESET, MEAS_EN | P05 (3, S1–S2) | J_BP2 |
| TEMP: SPI3_SCLK, SPI3_MOSI, SPI3_MISO, TC1_CS, TC2_CS | P09 (3, S3) | J_BP2 |
| SAFE: PWM, HEARTBEAT, MCU_ARM, HW_ARMED, INTERLOCK, SENSOR_ENABLE, CORE_LINK, SUP_N_OUT | P04 (4, S2–S3) | J_BP3 |
| DIR: MOTOR_INA, MOTOR_INB, ENA_DIAG, ENB_DIAG; ITEST: CS_ITEST_N | P07 (5, S2–S3) | J_BP3 |
| PFAIL_N | P02 R4 (1, S2–S3) | J_BP3 |
| 5V_SYS × 2, 3V3_IO × 1 | P02 R4 przez P12 | J_BP2 (5V_SYS), J_BP3 (3V3_IO) |

Wspólne linie SPI (ADC_SCLK, ADC_DOUTA do P05, P06 i P07) wychodzą z P03 raz, a P12 rozprowadza je wielopunktowo.

Zasady pinoutu:
- piny nieparzyste to GND tam, gdzie się da;
- zegary SPI (ADC_SCLK, SPI3_SCLK) i MEAS_EN mają GND po obu stronach;
- jeśli sygnałów jest za dużo na jedno złącze, przesunąć grupę do sąsiedniego i uzasadnić to w README.

Liczba sygnałów, ok. 37 plus zasilanie, mieści się w 3 × 20 pinach.

### 3. PFAIL_N (D-02)

Nowe wejście z P02 R4: rezystor szeregowy 1 kΩ, podciągnięcie 10 kΩ do 3V3_CORE, do wolnego GPIO modułu ESP32-S3.
- GPIO dobrać tak, żeby nie był pinem strapującym ani pinem zajętym przez PSRAM lub flash; uzasadnić wybór.
- Stan bez P02 (J_BP3 niepodłączone) to wysoki, czyli „zasilanie OK”. Opisać to w README.

### 4. Dalsze zmiany

- **SUP_N_OUT i bufor Schmitta U6 (R4/R5):** zostają. Droga do P04 zmienia się z taśmy 150 mm na: taśma ok. 30 mm, P12 i znowu taśma ok. 30 mm. Sprawdzić założenie o szybkości zbocza (≤ 10 ns/V po stronie P04) dla nowej długości i pojemności.
- **Listwy serwisowe:** do trzech listew na krawędzi B, kątowy goldpin 1×N, N ≤ 13 w slocie, GND na końcach.
  - Treść: punkty z `docs/ODBIOR.md` R5, co najmniej 5V_SYS, 3V3_CORE, 3V3_IO, SUP_N, EN modułu i sygnały testowe z ODBIOR.
  - Każdy kołek poza GND przez rezystor szeregowy przy węźle (1 kΩ lub 10 kΩ według S1 §6).
- **Części:**
  - rezystory i kondensatory, których wartość i typ są w `Zamowione/zamowione.csv`: THT, rezystory na stojąco;
  - pozostałe: SMD 1206;
  - od spodu wolno SMD ≤ 1,5 mm;
  - adaptery SO14 → DIP tylko tam, gdzie układ już kupiony w SO nie ma pól SOIC;
  - klasa L (160 × 100 mm), poziom 2.
- **USB modułu ESP32-S3:** musi być dostępne przy złożonym stosie. W README zapisać wymaganie dla layoutu: gniazdo od strony krawędzi B.

### 5. Kontrole

- ERC 0.
- Netlista pin po pinie z `parts.py`.
- Kontrole z R5 poprawione pod nowe złącza.
- Nowe kontrole z próbami ujemnymi:
  - każda sieć dawnego złącza jest dokładnie raz na J_BP;
  - nieparzyste piny to GND (z listą uzasadnionych wyjątków);
  - zegary SPI mają GND obok;
  - PFAIL_N ma rezystor szeregowy i podciągnięcie;
  - kołki serwisowe mają rezystory;
  - GND na końcach listew.
- Próba zerowa.

### 6. Pliki dla P12 i README

- `docs/J_BP.csv`: kolumny `zlacze;pin;siec;kierunek;plytka_docelowa;uwagi`.
- `docs/SERWIS.csv`: kolumny `zlacze;pin;siec;rezystor;cel_pomiaru`.
- README: tabela zmian R5 → R6, liczby z kontroli, otwarte punkty.

## Wynik

PR po polsku. Pytania wpisać do opisu PR. Nie włączać śledzenia PR, a po otwarciu PR zakończyć pracę.
