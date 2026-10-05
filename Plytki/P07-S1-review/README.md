# P07 DRIVE — S1, schemat pod moduł IBT-2 (2 × BTS7960B)

*5.10.2026, sesja w chmurze według `Plytki/Format-S1/zadania/ZADANIE-P07-S1.md`. Baza: `origin/pelny-s1`. Pinout P04 R3 z `origin/p04-r3-pcb` (702732a7, `reference/P04-R3-J_BP.csv`).*

**Status: tylko schemat, kontrole i dokumenty. PCB nie powstało** (layout robi sesja lokalna, `docs/CHMURA.md` zasada 6). Sprzętu nie zmontowano ani nie zmierzono. Moduł IBT-2 zmierzono tylko bez zasilania (POMIARY A–C); kroki D i E nie są zrobione.

## Co to jest

Płytka nośna testera w stosie S1: **poziom 5, sloty S2–S3, klasa 2/3 (106,5 × 100 mm)**. Moduł IBT-2 stoi poza stosem, na ściance obudowy, i łączy się z P07 taśmą 8 żył (J5) oraz czterema parami przewodów 2,0 mm² (J1–J4). Z v6.1 (Pololu 1451 / VNH5019) zostają: własny bocznik Kelvin 5 mΩ + INA240A2 + MCP3201 (ITEST), okno OC z zatrzaskiem, KPWR i otwarty kolektor na SAFE_N. To nie jest zamiana pin w pin. W trybie LOGGER mostek nie jest połączony z ECU — robi to dopiero port TEST na panelu (P11).

| Arkusz | Zawartość |
|---|---|
| P07 | 5VA_P07 (R50 10 Ω), 3V3A_P07 (MCP1702), odsprzęganie, arkusze |
| MOC | J1 VMOTOR, TVS SMCJ18A, C1 220 µF, KPWR K1 (G2RL-1-E 12 V) z Q1 i clampem 15 V, R4 1 k (wstępne ładowanie), J2 B+/B−, J3 M+/M−, RSH1, J4 TEST |
| ANA | R6/R7 Kelvin, INA240A2, MCP1525, U3 (bufor ADC + REF_BUF), dzielnik ITEST, U4 (OC_HIGH), TLV1702 |
| DIG | MCP3201 (posiadany DIP8), 74LVC125 SPI (DOUT trójstanowy), przejście SUP5 5 V → 3,3 V |
| LOGIKA | MCP120 ×2, odbiorniki Ioff 74LVC125, 74LVC14 (Schmitt), 3 × 74HC08, 74HC74 (OC_GOOD, NO_TRIP), Q2 na SAFE_N |
| MODUL | PTC → 5V_MOD, 74AHCT125 (3,3 → 5 V z OE), J5, R43 10 Ω w masie modułu, diagnostyka IS |
| ZLACZA | J_BP1, J_BP2 |
| SERWIS | J_SV1, J_SV2 z 20 rezystorami przy węzłach |

Obliczenia: `docs/PROJEKT.md`. Wiązki: `docs/WIAZKA-MODUL.md`. BOM S1: `docs/BOM.csv`, `docs/zakupy.csv` (147 części; z rejestru INA240A2, MCP3201-BI/P i 2 × 74LVC125AD, reszta nowa).

## Krawędź A (kontrakt dla P12)

| Pin | J_BP1 (S2, x płytki 26,5 / stosu 80,0) | J_BP2 (S3, x płytki 80,0 / stosu 133,5) |
|---|---|---|
| 2 | ADC_SCLK ← P03 | MOTOR_PERMIT ← P04 |
| 4 | ADC_DOUTA → P03 (wspólna, CS) | PWM_OUT ← P04 |
| 6 | CS_ITEST_N ← P03 | ARM_CLK ← P04 |
| 8 | MOTOR_INA ← P03 | DRIVE_OK → P04 |
| 10 | MOTOR_INB ← P03 | 5V_SYS |
| 12 | ENA_DIAG → P03 | 5V_SYS |
| 14 | ENB_DIAG → P03 | 3V3_IO |
| 16 | GND (rezerwa) | SAFE_N (węzeł OC) |

Nieparzyste piny to GND; złącza IDC 2 × 8 kątowe obudowane, pin 1 od mniejszego x. ADC_SCLK / ADC_DOUTA są na pinach 2/4 jak J_BP2 P03 R6, P05 R3 i J_BP P06 R2. Sieci P04 mają te same numery pinów co J_BP2 P04 R3 (2/4/6/8/16). **Dwa złącza zamiast jednego 2 × 10 z budżetu S1 §8:** 12 sygnałów i 3 piny zasilania nie mieszczą się w 10 parzystych pinach. Kierunki i drugi koniec: `docs/J_BP.csv`.

## Krawędź B (serwis)

J_SV1 (S2, x 10–43): GND, I_T_OUT, ADC_AIN, REF_BUF, REF25, OC_HIGH, OC_LOW (10 k), GND, VMOTOR, MOD_BP, KPWR_COIL_LOW, T_EGR_P1 (4,7 k), GND. J_SV2 (S3, x 63,5–96,5): GND, 5V_SYS, 5VA_P07, 3V3A_P07, 3V3_IO, 5V_MOD, GND, RAILS_OK, OC_LOCAL_N, OC_GOOD, NO_TRIP, DRIVE_EN (1 k), GND. Zwarcie kołka OC_LOCAL_N do GND (przez 1 k) wymusza OC — próba odbiorcza zatrzasku. RPWM / LPWM / EN / IS mierzy się na listwie modułu, która jest poza stosem. `docs/SERWIS.csv`.

## Kontrole (`src/run_schematic.py`; w chmurze `scripts/egrlab-docker python3 src/run_schematic.py`, ok. 1 min)

| Kontrola | Wynik |
|---|---|
| ERC | **0** na 8 arkuszach |
| Netlista pin po pinie względem `parts.py` | **494/494**, 147 części, 116 sieci |
| `verify_electrical.py` | **16/16**, mutacje **19/19**, próba zerowa czysta |
| `verify_s1.py` (S1 i kontrakty P12 / P03 R6 / P04 R3) | **30/30**, mutacje **24/24**, próba zerowa czysta |
| Powierzchnia (`powierzchnia.py`) | 69 % metodą P06 R2 (tam 41 %); wnętrze bez złączy krawędzi 50 %, z 1206 od spodu 37 % |

`verify_electrical.py` symuluje logikę na wyeksportowanej netliście: modele bramek według wartości części, podciąganie przez najmniejszą rezystancję, komparator i nadzorcy jako otwarte kolektory, 74HC74 z PRE/CLR i zboczem. Tabela 2304 wierszy pokazuje, że **bez MOTOR_PERMIT, bez SAFE_N, przy OC albo złych szynach wszystkie wejścia modułu (RPWM, LPWM, R_EN, L_EN) są L**, a KPWR wyłączony. Do tego martwe szyny, otwarte taśmy, zawieszona bramka AND (blokuje ją OE bufora), 11 kroków sekwencji zatrzasku (brak samoczynnego uzbrojenia, ARM przy PERMIT = H nie uzbraja, ARM w trakcie OC nie kasuje), progi OC w narożnikach (+8,01…+8,11 A / −7,99…−8,03 A), skala ITEST, moce bocznika i R4, wysterowanie i clamp KPWR, TVS, próg IS i rozdział mas. Raporty: `verification/QA.md`, `electrical-checks.json`, `s1-checks.json`, `powierzchnia.json`; PDF `output/pdf/P07-S1-schemat.pdf`.

## Decyzje (sporne oznaczone)

1. **Mapowanie VNH5019 → BTS7960:** RPWM = PWM & MOTOR_INA, LPWM = PWM & MOTOR_INB, R_EN = L_EN = DRIVE_EN. Hamowanie i stany INA = INB jak w VNH5019. Firmware bez zmian w sterowaniu.
2. **Blokada w trzech warstwach:** bramki AND (MOTOR_PERMIT · SAFE_N · OC_GOOD · RAILS_OK), OE bufora 74AHCT125 i KPWR. 74HC244 modułu jest stale aktywny (OE na GND), więc moduł sam niczego nie blokuje.
3. **DRIVE_OK = RAILS_OK & NO_TRIP** (nowy drugi przerzutnik). Przy starcie bez ARM DRIVE_OK = 1, więc INTERLOCK na P04 nie blokuje LOGGERA ani SENSOR. Po OC DRIVE_OK = 0 aż do ARM. v6.1 miało DRIVE_OK = RAILS_OK.
4. **Logika na 3V3_IO** (jak P04), analog na lokalnych 5VA / 3V3A (jak P06 R2). Odbiorniki z Ioff tylko tam, gdzie drugi koniec może mieć inne zasilanie (P03: MOTOR_INA/INB, CS, SCLK) oraz dla MOTOR_PERMIT / PWM_OUT. SAFE_N wchodzi przez 1 k na Schmitt 74LVC14 (zbocze RC ok. 10 µs na P04), bez podciągania na P07, z 1 M do GND (otwarta taśma = SAFE_OK L).
5. **Sporne — R4 1 kΩ równolegle do styków KPWR:** ładuje 330 µF modułu, żeby styk nie zamykał się na pusty kondensator (spawanie). Cena: przy otwartym KPWR B+ modułu jest na 91 % VMOTOR przez 1 k; prąd silnika ≤ 17 mA, przy zwarciu 0,28 W.
6. **Sporne — KPWR to przekaźnik G2RL-1-E 12 V zasilany z VMOTOR**, nie tranzystor: galwaniczne odłączenie i brak strat przy 10 A (MOSFET z P02 dałby ok. 2 W bez radiatora). Cewka dostaje do 140 % napięcia znamionowego (pakiet 16,8 V).
7. **Masy:** GND i PGND rozdzielone na P07, wspólny punkt na P02 R4. MOD_GND przez 10 Ω. Działa przy masie modułu połączonej z B− i przy rozdzielonej (`docs/PROJEKT.md`).
8. **Sporne — filtr ITEST τ 0,26 ms** (C7 100 nF C0G): antyaliasing przy 2 kS/s.
9. **OC ±8 A:** ≥ 115 % prądu pracy 6 A, poniżej nasycenia INA240A2 przy najniższym 5VA. Próba 10 A nie przejdzie przez aktywny mostek (pytanie 2).
10. **ENA_DIAG / ENB_DIAG:** H = prąd gałęzi powyżej ok. 1,6–4,6 A albo poziom błędu IS. Znaczenie inne niż w VNH5019 (tam L = błąd).
11. Wyjątki od „nowe = SMD 1206”: R4 2512 (moc), C1 elektrolit, RSH1 2512 Kelvin (jak P06 R2), K1, MCP3201 w posiadanym DIP8, TO-92 jak w P06 R2.

## Wymagania dla layoutu (sesja lokalna)

- J4 (TEST) przy krawędzi x = 0; J1–J3 najlepiej tam samo, żeby pętla 10 A była krótka. Tor 10 A ≥ 4 mm na obu warstwach, zszyty przelotkami; bez przelotek w polach RSH1; para Kelvina jak w P06 R2.
- PGND jako osobna wylewka (J1.2, J2.2, D1, C1–C4, R1, R3, R5, Q1.E), bez połączenia z GND; GND logiki i analogu z dala od toru mocy.
- K1 ma 15,7 mm wysokości — mieści się w 16,5 mm poziomu 5. C1 D8 × 11,5 mm stoi. Od spodu tylko SMD ≤ 1,5 mm (bez SOIC, bez 10 µF 1206, jeśli grubsze niż 1,5 mm).
- J5 kątowy przy krawędzi, w stronę modułu. J_BP1 x = 26,5, J_BP2 x = 80,0 (układ płytki). Listwy J_SV1 x = 10–43, J_SV2 x = 63,5–96,5. Osiem otworów M3 (x = 4 / 49 / 57,5 / 102,5; y = 14 / 86).
- Powierzchnia jest ciasna (50 % wnętrza wobec 29 % w P06 R2): rezystory i małe kondensatory 1206 od spodu, przy węzłach.

## Otwarte pytania (także w opisie PR)

1. **Bezpiecznik F1 5 A na P02 R4 a praca 6 A / OC 8 A.** MINI 5 A przy 6 A ciągłych (120 %) może się po czasie przepalić. Zmienić na 7,5 A albo 10 A (sama wkładka) i zrobić próbę nagrzewania toru VMOTOR P02 (miedź 35 µm, 5,7 mm)? Opis P02 („VMOTOR ≤ 3,5 A, OC 4 A”) pochodzi z v6.1.
2. **Co znaczy „10 A w próbie”?** Jeśli to bierna kwalifikacja toru (jak P06), zostaje OC ±8 A i INA240A2 (posiadany). Jeśli mostek ma aktywnie podać 10 A, potrzebne jest INA240A1 (0,1 V/A) i nowe progi — zmiana tylko wartości.
3. **Przekaźnik KPWR:** czy G2RL-1-E DC12 (cewka do 140 %, wysokość 15,7 mm) jest akceptowalny? Dopuszczalne napięcie cewki trzeba potwierdzić w karcie. Alternatywa: cewka 5 V z 5V_SYS (80 mA na wspólnej szynie z analogiem).
4. **R4 równolegle do styków KPWR (decyzja 5)** — zostaje?
5. **Znaczenie ENA_DIAG / ENB_DIAG** (decyzja 10) — akceptujesz H = prąd albo błąd? Firmware dziś tych bitów nie interpretuje.
6. **Pomiary modułu przed PCB:** B4 (kolejność pinów listwy 2 × 4), C5 (GND ↔ B− omomierzem), D1 (prąd VCC, czy jest dioda LED), E2 (RPWM → M+), E3 (kILIS — próg IS).
7. **Położenie J1–J3:** wszystkie przy x = 0 obok J4, czy wejście VMOTOR od strony P02 / ściany wejść?
8. **P12:** P12 R1 jest tylko dla wariantu LOGGER — dla poziomów 5 i 6 potrzebna będzie P12 R2 z J_BP1/J_BP2 P07 i J_BP1–3 P04 R3.
9. **P04 R3 nie jest jeszcze na `pelny-s1`/`main`.** Numery pinów wzięte z gałęzi `p04-r3-pcb` (702732a7); po zmianie P04 trzeba odświeżyć `reference/P04-R3-J_BP.csv` i puścić kontrole.

## Pliki

- `eda/` — schemat KiCad 10 (8 arkuszy A3), biblioteki lokalne (footprinty końcówek przewodów, bocznik WSK2512 jak w P06 R2).
- `src/` — `parts.py` (jedno źródło obwodu), `build_schematic.py`, `make_tables.py`, `verify_schematic.py`, `verify_electrical.py`, `verify_s1.py`, `powierzchnia.py`, `make_qa.py`, `run_schematic.py`, `cadlib.py` (z P06 R2).
- `docs/` — `J_BP.csv`, `SERWIS.csv`, `BOM.csv`, `zakupy.csv`, `parts.json`, `interfejsy.csv`, `netlist-pinowa.csv`, `PROJEKT.md`, `WIAZKA-MODUL.md`.
- `reference/` — `P03-R6-J_BP.csv`, `P04-R3-J_BP.csv` (z `origin/p04-r3-pcb`), `P12-kontrakty.json` (P12 przygotowanie), skróty SHA-256.
- `output/` — `pdf/P07-S1-schemat.pdf`, podglądy PNG.
- `verification/` — ERC, netlista, raporty kontroli, `QA.md`, logi, manifest.
