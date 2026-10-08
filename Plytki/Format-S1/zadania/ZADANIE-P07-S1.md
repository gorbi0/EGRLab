# P07 S1 — DRIVE pod moduł IBT-2 (2 × BTS7960B), schemat (zadanie dla sesji w chmurze, 5.10.2026)

**Ustawienia sesji:** Opus 5.5, wysiłek high. Baza: `origin/pelny-s1`. Gałąź zadania: `p07-s1-schemat`, wynik jako PR do `pelny-s1`.

**Zakres:** tylko schemat, kontrole i dokumenty, **bez PCB** (`docs/CHMURA.md`, zasada 6).

## Decyzje użytkownika
- Wariant pełny przed wspólnym zamówieniem. **P07 na 5. poziomie, sloty S2–S3, klasa 2/3** (106,5 × 100 mm; `format-s1.json`). P08 R2 stoi w S1 tego poziomu, P04 R3 na 6. poziomie.
- Mostek: **moduł IBT-2 / HW-39 (2 × BTS7960B, bufor 74HC244)** zamiast Pololu 1451 (`EGRLab-AKTYWNE.md`, „P07 DRIVE — WSTRZYMANE”: zachować **własny bocznik / INA240 / MCP3201, lokalne OC, zatrzask i KPWR**; to nie jest zamiana pin w pin; w trybie LOGGER mostek nie jest połączony z ECU).
- **Moduł stoi poza stosem** (radiator 22,8 mm pod płytką, całość ok. 40–45 mm; ścianka obudowy, 4 × M3 w kwadracie 40 × 40 mm). P07 łączy się z modułem wiązką: 8 żył sterowania (RPWM, LPWM, R_EN, L_EN, R_IS, L_IS, VCC, GND) i przewody mocy (B+, B−, M+, M−).
- Pomiary modułu (użytkownik, 5.10): `Plytki/P07-modul-BTS7960/POMIARY-MODULU.md` — OE 74HC244 na GND (bufor zawsze aktywny → blokada po stronie P07), VCC bufora z VCC złącza, R_IS / L_IS 10 kΩ do GND (≈ 1,2 V/A, przy 6 A ok. 7 V → dzielnik + ogranicznik, tylko diagnostyka), wejścia ok. 30 kΩ do GND (wolne = wyłączony), bez podciągania do VCC (74HC244 przy 5 V: VIH ≥ 3,5 V → **bufor 3,3 → 5 V na P07**, np. 74AHCT125/245), R_EN i L_EN rozdzielone, **GND złącza ↔ B− nie jest zwarciem** (tryb diody 508 mV) — zaprojektuj masy tak, by działało w obu przypadkach (prąd silnika mierzony w linii silnika, jeden zdefiniowany punkt łączenia mas, opis w README).
- Prąd silnika: 6 A pracy, 10 A w próbie; przewody 2,0 mm² (decyzja 4.10). Pomiar prądu: **bocznik + INA240 w linii silnika (M+)**, jak P06 R2 (bocznik 2512 Kelvin, pola na obu warstwach).

## Źródła
- Wymagania i poprzedni obwód: `Rewizje/EGRLab-v6.1-rc1` (README, interfejsy.csv, schematy, montaz/P07-strefy.svg), `Rewizje/EGRLab-v5/schematy/P07-*.svg` i `hardware/P07-BOM.csv`, `Rewizje/EGRLab-v5/P01-PROTECT` (KPWR, C_BULK, SMCJ18A przy VMOTOR), `EGRLab-AKTYWNE.md` (sekcja P07).
- Kontrakty P12: `Plytki/P12-przygotowanie/wyniki/KONTRAKTY.md`. Sieci czekające na P07 (piny po drugiej stronie ustalone — **nie zmieniać**): z P03 R6 J_BP1: CS_ITEST_N (4), ENA_DIAG (17, wejście P03), ENB_DIAG (18, wejście P03), MOTOR_INA (19), MOTOR_INB (20); z P03 R6 J_BP2: ADC_SCLK (2), ADC_DOUTA (4, wspólna linia MCP3201 / AD7606B — nadajnik wybierany przez CS, wyjście trójstanowe); z P04 R3 (`origin/p04-r3-pcb`, `Plytki/P04-R3-review/docs/J_BP.csv`): MOTOR_PERMIT, PWM_OUT, ARM_CLK, DRIVE_OK (wejście P04), SAFE_N.
- Wzorzec łańcucha schematu S1: `Plytki/P06-R2-review/src` (INA240 + MCP3201 + bocznik Kelvin, J_BP, listwa serwisowa, kontrole, próby ujemne).
- VMOTOR: sprawdź w `Plytki/P02-R4-review` (VMOTOR przez F1 5 A, złącze wyjściowe) i opisz drogę zasilania mostka (P02 → P07 KPWR → moduł B+).
- Format: `Plytki/Format-S1/SPECYFIKACJA-FORMATU-S1.md` (§4–§6, §8) i `format-s1.json`. Pamięć: `docs/pamiec-claude/MEMORY.md`, `format-s1.md`, `chmura-limity.md`, `kicad-pipeline-quirks.md`.

## Zasady
`docs/CHMURA.md` 1–9. Nie zmieniać: `EGRLab-AKTYWNE.md`, `docs/`, `scripts/`, `Plytki/Format-S1/`, innych pakietów, `.gitattributes`.

## Do zrobienia — pakiet `Plytki/P07-S1-review`
1. Schemat: J_BP na krawędzi A (IDC kątowe obudowane, środki x = 80,0 / 133,5 w slotach S2 / S3 — jedno lub dwa złącza wg potrzeb, pin 1 od mniejszego x, GND na nieparzystych), pola przewodów mocy z kotwami (wejście VMOTOR, wyjście do modułu B+ / B−, M+ / M− z modułu, wyjście do portu TEST T_EGR_P1 / T_EGR_P3 przy krawędzi x = 0), złącze/pola wiązki sterowania modułu, bufor 3,3 → 5 V z blokadą (MOTOR_PERMIT · SAFE_N · KPWR · brak OC) na RPWM / LPWM / R_EN / L_EN, kierunek z MOTOR_INA / MOTOR_INB, PWM z PWM_OUT, KPWR (przekaźnik / tranzystor zasilania mostka) z ARM_CLK / zatrzaskiem wg v6.1, lokalne OC z zatrzaskiem → DRIVE_OK do P04, diagnostyka IS (dzielnik + ogranicznik) → ENA_DIAG / ENB_DIAG, bocznik Kelvin + INA240 + MCP3201 (ITEST, CS_ITEST_N, ADC_SCLK, ADC_DOUTA trójstanowe), zasilanie 5V_SYS / 3V3_IO, odsprzęganie, TVS przy VMOTOR; listwa serwisowa na krawędzi B (S1 §6). Bez części od spodu poza SMD ≤ 1,5 mm.
2. `docs/J_BP.csv` w formacie P06 R2 (zlacze;pin;siec;kierunek;plytka_docelowa;uwagi; kierunki gnd/pwr/in/out), `docs/WIAZKA-MODUL.md` (pinout 8-żyłowej wiązki i przewodów mocy, długości, przekroje), `docs/PROJEKT.md` (obliczenia: bocznik, wzmocnienie, zakres ADC, próg OC, dzielnik IS, czasy, straty), BOM S1.
3. Kontrole: ERC 0, kontrakty (każda sieć „czeka na P07” ma koniec z właściwym kierunkiem), logika blokady (tablica stanów: bez SAFE_N / MOTOR_PERMIT / przy OC → wszystkie wejścia modułu L), próby ujemne z próbą zerową, PDF schematu, ocena powierzchni dla klasy 2/3.
4. README: decyzje, założenia, otwarte pytania (w opisie PR).

Po PR zakończyć pracę (zasada 5). Nie włączać śledzenia PR.
