# P11 w formacie S1 — przygotowanie (1.10.2026)

**Status:** decyzje P11-1…P11-7 podjęte przez użytkownika 4.10.2026 (sekcja „Decyzje 4.10”). Schematu ani PCB nie ma. Źródła: `Plytki/P11-R1-review` (R1, interfejsy zamrożone na P03-R2, P04-R2.1, P05-R1, P06-R1, P08-R1), specyfikacja S1 (§7, §8, §10), decyzje z 29.09 (zamienniki) i 1.10, pakiety S1: P02 R4, P03 R6, P05 R3, P06 R2.

## Co robi P11 R1

Pasywna płytka panelu, 160 × 110 mm, Cu 70 µm, 9 wiązek lutowanych i dwa gniazda:

| Wiązka | Sieci | Drugi koniec (R1) |
|---|---|---|
| W1 PANELSAFE (7 × AWG22) | PANEL_3V3, GND, TEST_KEY, MECH_OK, STOP_NC_OUT, ARM_CONTACT | P04-R2.1 J8 (PANEL_3V3 z R40 100 Ω na P04) |
| W2 PANELCORE (7 × AWG22) | GND, MARK, TEST_KEY, LOGGER_CLEAR, TEST_PRESENT, N_J_SCOPE_HOT | P03-R2 J9 |
| W3 TMOTOR (HOLD) | T_EGR_P1, T_EGR_P3 | P07 (HOLD) |
| W4 TSENSOR | 5V_SENSOR, AGND_SENSOR | P08 J4 |
| W5 L1 (DT04-12PB) | ECU_P1, EGR_P1 (prąd silnika w trybie LOGGER), TAP_P1/P3/P4/P5/P6, GND | port L1 na panelu |
| W6 L2 (DT04-12PC) | TAP_P1…P6, GND (back-probe, bez prądu) | port L2 |
| W7 TEST (DT04-12PA) | T_EGR_P1/P3, 5V_SENSOR, AGND_SENSOR, TAPy, LOOP_OUT, MECH_OK | port TEST |
| W8 kontakty (18 × AWG24) | kluczyk, pętle NC L1/L2, STOP, ARM, MARK, TEST_PRESENT | przyciski i przełączniki panelu |
| W9 SCOPE (RG174) | N_J_SCOPE_HOT, GND | BNC izolowany |
| J1 ISERIES (MSTB 4p) | ECU_P1, EGR_P1 | P06 J3 |
| J7 TAPS (Mini-Fit 12) | TAPy w parach z GND | P05 J4 |

Tory silnika na P11 R1: 4 ścieżki 3 mm przy 70 µm, bez przelotek. Kontrola R1 symulowała 64 kombinacje styków (pętle bezpieczeństwa, TEST_KEY, LOGGER_CLEAR, STOP, TEST_PRESENT).

## Co się zmieniło wokół P11 (S1, stan 1.10)

| Sąsiad | Zmiana | Skutek dla P11 |
|---|---|---|
| P03 R6 | panel przez J_BP1 i P12 zamiast wiązki J9: MARK (pin 13), TEST_KEY (14), LOGGER_CLEAR (15), TEST_PRESENT (16) — wejścia; N_J_SCOPE_HOT (10) — wyjście przez R12 330 Ω | P11 ma złącze IDC do P12 (S1 §8: 1 × 2×10, PANELCORE i PANELSAFE) |
| P04 | wariant pełny, rewizja S1 później | PANELSAFE (PANEL_3V3, MECH_OK, STOP_NC_OUT, ARM_CONTACT, TEST_KEY) też przez P12 |
| P05 R3 | TAPS jako końcówka przewodów J4 (PTH, kotwy) przy krawędzi x = 0; AUX J6 (koncentryk); **SW1 AUX HI/LO** — E-Switch 100 kątowy M6 na P05, tuleja i dźwignia przez panel | panel musi mieć otwór pod SW1 P05 dokładnie w osi z PCB P05 (poziom 3); TAPS z P05 kończą się na P11 albo na porcie |
| P06 R2 | ISERIES jako końcówka J3 (2 × 2,5 mm², lutowana na P06); **przełącznik BYPASS na panelu** (DPDT ON-ON ≥ 10 A DC) z wiązkami J4 (2 × 2,5 mm²) i J5 (3 × AWG22) wprost z P06 | P11 nie przenosi BYPASS; panel ma miejsce na przełącznik i jego luty |
| P02 R4 | przełącznik PWR na panelu (J14) i LED PWR | element panelu spoza P11 |
| P09 R2, P10 R2 | gniazda termopar i OBD na ścianie wejść | poza panelem |
| Zamienniki 29.09 | EAO → zwykłe przyciski; DEUTSCH tylko przy adapterach, na panelu tańsze złącze z kluczem | porty L1/L2/TEST na panelu to nowy typ złącza |
| S1 §3 | miedź 35 µm (było 70 µm) | tory silnika na P11 muszą mieć 2× szerokość albo obie warstwy (jak P06 R2: pola ≥ 4 mm na obu warstwach) |

## Ustalenia (fakty z pakietów)

1. **Wariant LOGGER bez P04 nie ma PANEL_3V3.** W R1 styki TEST_KEY, LOGGER_CLEAR (pętle NC L1/L2) i TEST_PRESENT zasila PANEL_3V3 z P04 (R40 100 Ω). Na P03 R6 te wejścia mają pull-down 10 kΩ (R27, R6, R8), więc bez P04 są zawsze w stanie L: TEST_KEY = brak kluczyka, TEST_PRESENT = brak adaptera TEST (stan bezpieczny), LOGGER_CLEAR = L (firmware traktuje to jak obecny adapter LOGGER). **MARK działa** (pull-up 10 kΩ do 3V3_CORE i 100 nF na P03 R6, przycisk do GND).
2. **Kontrakt P12 czeka tylko na P11** (wariant LOGGER): LOGGER_CLEAR, MARK, N_J_SCOPE_HOT, TEST_KEY, TEST_PRESENT (`Plytki/P12-przygotowanie`, 19 sieci kompletnych, 27 czeka).
3. **Prąd silnika w trybie LOGGER idzie przez P11** (port L1: ECU_P1, EGR_P1 → J1 → P06 J3). W S1 przy 35 µm i do 6 A (10 A w próbie biernej E15) ta droga potrzebuje tych samych zasad co P06 R2 albo przewodu z portu wprost do P06.
4. **SW1 P05 i przełącznik BYPASS P06 są na panelu, ale nie na P11** — ich położenie wynika z PCB P05 R3 / z wiązek P06; układ panelu musi to uwzględnić.
5. Harness W3 / J3 ISERIES P06 R2: drugi koniec opisany jako „MSTB 2,5/4-ST-5,08 do P11/J_ISERIESA (pozycje 3/4 puste) — do potwierdzenia z P11 w S1” (`Plytki/P06-R2-review/docs/WIAZKI.md`).

## Decyzje 4.10.2026

| Nr | Decyzja |
|---|---|
| P11-1 | **(b) odchudzona:** P11 tylko logika styków (kluczyk, STOP, ARM, MARK, pętle NC, TEST_PRESENT) i złącze IDC do P12; porty łączone przewodami wprost |
| P11-2 | **klon DT, Amphenol AT04-12** z kluczami A / B / C (L1 / L2 / TEST), styki 13 A |
| P11-3 | **(a)** 3V3_IO z P12 (J_BP.14, P06) przez 100 Ω na P11; rezystor montowany tylko w wariancie bez P04, przy P04 nieobsadzony |
| P11-4 | **(b)** przewody z portów wprost do P06 / P07; P11 bez prądu silnika |
| P11-5 | **lutowane końcówki** TAPS (P05 J4) i ISERIES (P06 J3), bez J7 / J1 na P11 |
| P11-6 | **rysunek makiety 1:1** (PDF) — `Plytki/Panel-S1-makieta` (gałąź `panel-s1-makieta`): panel 50 mm przed stosem, P11 poziomo na dnie tej strefy (najwyżej ok. 45 × 130 mm); SW1 P05 przeniesiony na panel (5 przewodów do P05) |
| P11-7 | **zwykłe przyciski ze stykami złoconymi** (do małych prądów); bez zmian rezystorów P03 |

## Pytania przed decyzją (zamknięte 4.10)

| Nr | Pytanie | Możliwości i skutki |
|---|---|---|
| P11-1 | Czy P11 zostaje osobną płytką za panelem? | (a) tak, jak R1: styki, porty, rozdział TAPS / ISERIES, złącze do P12; (b) odchudzona: tylko logika styków i złącze do P12, porty łączone przewodami wprost do P05 / P06 |
| P11-2 | Typ złącza portów L1 / L2 / TEST na panelu (zamiast DT04-12) | 12 pozycji z kluczem; dwie pozycje do 6 A (10 A w próbie), reszta sygnały i TAPy; adaptery zachowują DEUTSCH od strony auta |
| P11-3 | Zasilanie styków w wariancie LOGGER (ustalenie 1) | (a) 3V3_IO z P12 przez rezystor na P11 (jak R40 100 Ω na P04); (b) bez zasilania — w LOGGER działa tylko MARK; (c) P12 daje PANEL_3V3 przy braku P04 |
| P11-4 | Droga prądu silnika (L1 → P06, TEST → P07) | (a) miedź P11 przy 35 µm: pola na obu warstwach jak P06 R2; (b) przewody z portów wprost do P06 / P07, P11 bez prądu silnika |
| P11-5 | Połączenia TAPS (P05 J4) i ISERIES (P06 J3) po stronie panelu | gniazda na P11 (R1: J7 Mini-Fit 12, J1 MSTB 4p) albo lutowane końcówki; dotyczy też pytania z kasety „J7 (TAPS) na P11 przed J4 P05” |
| P11-6 | Układ panelu i obudowa | położenia: SW1 P05 (oś z PCB P05 R3), BYPASS P06, PWR P02 R4 z LED, porty L1/L2/TEST, BNC AUX (P05 J6), BNC scope, kluczyk, STOP, ARM, MARK; makieta 1:1 (S1 §10 krok 3) |
| P11-7 | Zwykłe przyciski zamiast EAO | STOP zatrzaskowy, ARM, MARK, kluczyk; obciążenie styków ok. 27 µA / 3 V (R1) — styki złocone albo przeznaczone do małych prądów |

## Dalej

Po decyzjach P11-1…P11-7: zadanie dla chmury `Plytki/Format-S1/zadania/ZADANIE-P11-S1.md` (schemat P11 R2 w S1, pinout J_BP dla P12, kontrole jak w P06 R2), potem layout lokalnie i dopiero wtedy P12 dla wariantu LOGGER. Wysłanie zadania do chmury tylko po „wyślij”.
