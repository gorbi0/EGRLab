# P07 S1 — obliczenia projektowe

*5.10.2026. Wartości liczbowe sprawdza `src/verify_electrical.py` na wyeksportowanej netliście (`verification/electrical-checks.json`). Założenia z kart, których nie zweryfikowano lokalnie, oznaczono „do potwierdzenia”.*

## Tor mocy

Droga zasilania mostka: **P02 R4** (pakiet 4S 12,0–16,8 V → Q9/Q1 → VSW → **F1 MINI 7,5 A** (wkładka, decyzja użytkownika 5.10; płytka P02 bez zmian) → J2 GMSTBA 7,62 3p: 1 VMOTOR, 2 GND) → przewody 2 × 2,0 mm² → **P07 J1** (VMOTOR / PGND) → TVS D1 SMCJ18A, C1 220 µF/35 V, C2 1 µF, C3 100 nF, R1 10 k (bleed) → **KPWR K1** (COM = VMOTOR, NO = MOD_BP) → **J2** → moduł B+ / B−. Moduł M+ → **J3.1** → **RSH1** 5 mΩ (Kelvin) → T_EGR_P1 → **J4.1** → port TEST (P11). M− → J3.2 = T_EGR_P3 → J4.2.

| Wielkość | Wartość | Uwagi |
|---|---|---|
| Strata bocznika 5 mΩ | 0,18 W przy 6 A, 0,50 W przy 10 A | WSK2512 1 W przy 70 °C — 50 % przy 10 A |
| TVS D1 SMCJ18A | VRWM 18 V ≥ 16,8 V; VC ok. 29 V | < 40 V BTS7960, < 40 V VCEO Q1 |
| Wstępne ładowanie R4 1 kΩ 2512 | τ = 1 k × 330 µF = 0,33 s; przy otwartym KPWR MOD_BP = 91 % VMOTOR (R4 z R5 10 k) | zwarcie po stronie modułu: 0,28 W (28 % mocy); prąd silnika przy otwartym KPWR ≤ 16,8 mA |
| Cewka KPWR (G2RL-1-E **DC5**, 62,5 Ω; decyzja użytkownika 5.10) | 78–82 mA przy 5V_SYS 4,90–5,10 V (98–102 % napięcia znamionowego; zadziałanie ≤ 70 %), ok. 0,4 W | zasilana z **5V_SYS**, nie z VMOTOR; C9 10 µF przy K1.A1 |
| Q1 AO3400A (NMOS logiczny, SOT-23) | VGS = VOH 74HC08 bez obciążenia ≥ 2,9 V (3V3_IO ≥ 3,0 V) ≥ 2,5 V (punkt RDS(on) ≤ 48 mΩ) → VDS ok. 4 mV przy 82 mA; R2 100 Ω w bramce, R3 100 k do GND | źródło na **GND** (obwód cewki w domenie GND); MMBT3904 potrzebowałby IB ok. 6 mA z HC08 przy 3,3 V — poza kartą |
| Clamp cewki D2 + D3 (15 V) do 5V_SYS | VDS max = 5,1 + 15 + 0,7 = 20,8 V | ≤ 85 % VDS 30 V |
| Bleed R1 / R5 | 28 mW przy 16,8 V | |

Kolejność łączenia: DRIVE_EN gaśnie w nanosekundach, KPWR odpada po kilku ms, więc styk otwiera się bez prądu. Przy załączeniu kondensator modułu jest już naładowany przez R4, a mostek przy PWM = 0 hamuje dolnymi kluczami (bez poboru z B+). **Wymaganie dla firmware:** PWM dopiero ≥ 20 ms po MOTOR_PERMIT (czas zadziałania przekaźnika ok. 10 ms).

## Pomiar prądu (ITEST)

INA240A2 (50 V/V, REF1 = REF2 = REF_BUF = 2,5 V): I_T_OUT = 2,5 V + 0,25 V/A. Dzielnik R8/R9 5,11 k 0,1 % (1:2) z C7 100 nF C0G: τ = 2,555 k × 100 nF = **0,26 ms (623 Hz)**, czyli filtr antyaliasingowy przy 2 kS/s. Bufor U3A (MCP6022, 3V3A), R16 47 Ω / C11 470 pF, MCP3201 z VREF = REF25 2,5 V.

| Wielkość | Wartość |
|---|---|
| Skala ADC | 1,25 V + 0,125 V/A; ±10 A matematycznie w 0–2,5 V |
| LSB | 0,61 mV = 4,9 mA |
| Liniowość INA240 (5VA min 4,80 V, wyjście ≤ VS − 0,1 V) | do ok. +8,7 A; ujemnie do ok. −9,8 A |
| Ramka SPI | jak P06 R2: mode 0, 16 zegarów, raw = (word >> 1) & 0x0FFF; DOUT trójstanowy (OE = CS_LOCAL_N) |

Sporne: τ 0,26 ms (v6.1: 4,7 µs, P06 R2: 1,2 ms). Szybszy tor pokazuje tętnienie PWM, które przy 2 kS/s daje aliasing; wolniejszy rozmywa czas zerwania. Zmiana tylko wartości C7.

## Zabezpieczenie nadprądowe (OC)

Szybki tor I_T_OUT → R10 1 k / C8 1 nF (τ 1 µs) → I_FILT → okno TLV1702 (U5, otwarty kolektor, R15 10 k do 3V3_IO).

| Próg | Obwód | Napięcie | Prąd nominalnie | Narożniki |
|---|---|---|---|---|
| OC_HIGH | U4A: REF_BUF × (1 + 8,06 k / 10,0 k) | 4,515 V | +8,06 A | +8,01 … +8,11 A |
| OC_LOW | REF_BUF × 10,0 k / (40,2 k + 10,0 k) | 0,498 V | −8,01 A | −7,99 … −8,03 A |

Narożniki: REF25 ±1 %, rezystory 0,1 %, wzmocnienie INA240 0,2 % i bocznik 1 %, offsety INA240 25 µV, MCP6022 4,5 mV, TLV1702 2,5 mV. Progi są ilorazowe względem REF25, więc jego tolerancja przesuwa je tylko o ±1 %. Wymagania (kontrola `OC-WINDOW`): próg ≥ 6,9 A (115 % prądu pracy 6 A) i ≤ 9,0 A, a w najgorszym narożniku wyjście INA240 przy progu (4,58 V) mieści się poniżej 5VA_min − 0,1 V.

Czas reakcji: filtr 1 µs + TLV1702 ok. 0,6 µs + 74HC08 / 74HC74 / 74AHCT125 ok. 0,1 µs + 74HC244 modułu + wyłączenie BTS7960 przez INH (pojedyncze µs). Razem rząd 10 µs. Twarde zwarcie i tak ogranicza BTS7960 (ok. 33–47 A), a ten tor chroni bocznik, przewody i bezpiecznik.

Skutki OC: (1) FF1 (OC_GOOD) kasowany asynchronicznie → DRIVE_EN = L, KPWR odpada; (2) FF2 (NO_TRIP) kasowany → DRIVE_OK = L do P04 (INTERLOCK spada) aż do następnego ARM; (3) Q2 ściąga SAFE_N na czas trwania OC → P04 kasuje HW_ARMED. Ponowne uzbrojenie: zbocze ARM_CLK przy MOTOR_PERMIT = L (D = PERMIT_N), bez samoczynnego powrotu.

## Logika blokady

RAILS_OK = SUP3_N (MCP120-300 na 3V3A) & SUP5_N (MCP120-450 na 5VA, przez U7D). LOCAL_PERMIT = MOTOR_PERMIT & OC_GOOD & RAILS_OK (KPWR). DRIVE_EN = LOCAL_PERMIT & SAFE_OK. RPWM = PWM_OUT & DRIVE_EN & MOTOR_INA, LPWM = PWM_OUT & DRIVE_EN & MOTOR_INB, R_EN = L_EN = DRIVE_EN.

| MOTOR_INA | MOTOR_INB | PWM | Moduł | VNH5019 (v6.1) |
|---|---|---|---|---|
| 1 | 0 | 1 | RPWM = 1: M+ do B+, M− do B− (kierunek A) | jak |
| 0 | 1 | 1 | LPWM = 1: kierunek B | jak |
| x | x | 0 | oba dolne klucze: hamowanie do B− | jak |
| 1 | 1 | 1 | oba górne klucze: hamowanie do B+ | jak |
| 0 | 0 | 1 | oba dolne: hamowanie do B− | jak |

Druga blokada: OE_N bufora U16 = DRV_OFF (negacja DRIVE_EN, R35 100 k do 5V_MOD). Bez DRIVE_EN wyjścia są w stanie Z, a moduł ma 30 k do GND na wejściach. Dotyczy to też zawieszonej w stanie H bramki AND (kontrola `OE-BLOCKS-STUCK-GATE`) oraz braku 3V3_IO (U11 z Ioff → DRV_OFF wysoko). Trzecia blokada to KPWR. Tabela 2304 wierszy (`LOGIC-TABLE`) obejmuje MOTOR_PERMIT 0/1/otwarta taśma, SAFE_N, PWM, kierunek, oba nadzorcy, prąd 0/±9 A i stany obu przerzutników. Do tego przypadki martwych szyn (3V3_IO, 3V3A, 5VA, 5V_MOD), otwartej taśmy J_BP2 (SAFE_SENSE ściągnięty 1 M, MOTOR_PERMIT / PWM_OUT / ARM_CLK ściągnięte 100 k) i 11 kroków sekwencji zatrzasku.

Wyścig przy ARM: P04 ustawia HW_ARMED tym samym zboczem ARM_CLK, a MOTOR_PERMIT rośnie po co najmniej 3 bramkach (> 50 ns), podczas gdy czas podtrzymania 74HC74 to 0–3 ns. FF1 widzi więc jeszcze PERMIT_N = 1.

## Diagnostyka IS (uproszczenie 4, 6.10)

Moduł: R_IS / L_IS 10 kΩ do GND, I_IS = I_L / kILIS (8500 typ.), czyli źródło prądowe z rezystancją Thevenina 10 kΩ. Od 6.10 bez przerzutnika Schmitta (U17) i bez R48 / R49: R44 / R46 4,7 kΩ prowadzą IS wprost na J_BP1.12 / .14 (ENA_DIAG / ENB_DIAG); na P07 R45 / R47 100 kΩ do GND (poziom L bez P03), C14 / C15 100 nF, BAT54S do GND / 3V3_IO. Dzielnik zamyka 10 kΩ do GND na wejściu P03 R6 (74LVC125): napięcie na wejściu P03 = 0,38 × I_IS × 10 kΩ, τ = (14,7 k ∥ 9,1 k) × 100 nF = 0,56 ms (uśrednia PWM), prąd clampu przy poziomie błędu IS ≤ 0,5 mA.

Próg = wejście LVC125 na P03 (VIL 0,8 V / VIH 2,0 V przy 3,0–3,6 V) przy kILIS 6000–11000 (**założony rozrzut ±30 %, do potwierdzenia E3**): flaga H od **ok. 1,3–5,8 A** prądu gałęzi (kontrola `IS-DIAG`); przy 6 A pracy flaga H, poziom błędu IS też daje H (decyzja 5.10). **Co traci diagnostyka względem wersji z U17:** brak histerezy — przy prądzie blisko progu bit może migać (firmware czyta bity, nie przerwania; uśrednianie C zostaje); szersze pasmo progu (1,3–5,8 zamiast 1,6–4,6 A), bo zależy od progu wejścia CMOS zamiast progu Schmitta; próg zależy też od 10 kΩ na P03 (zmiana tego rezystora przesuwa próg). Bez P03 (taśma otwarta) linia ma 0,91 IS — nieistotne, bo nie ma odbiornika.

## Zasilanie lokalne i budżet

| Szyna | Źródło | Odbiorniki | Prąd (szacunek) |
|---|---|---|---|
| 5VA_P07 | 5V_SYS przez R50 10 Ω, C16 10 µF | INA240, U4, TLV1702, MCP120-450, LDO U18 | ok. 6 mA (spadek 60 mV) |
| 3V3A_P07 | MCP1702-3302 (U18) | MCP1525, U3, MCP3201, U7, MCP120-300 | ok. 3 mA |
| 5V_MOD | 5V_SYS przez PTC F1 (0,12 A hold) | U16, VCC modułu (74HC244, ewentualna dioda LED) | ≤ 20 mA (moduł do zmierzenia, D1) |
| 5V_SYS (wprost) | J_BP2.10/12 | cewka KPWR K1 (decyzja 5.10), C9 10 µF | **ok. 80 mA** przy załączonym KPWR |
| 3V3_IO | P02 R4 przez J_BP2.14 | U10–U15, clamp IS, podciąganie OC | ≤ 5 mA |
| VMOTOR | P02 R4 F1 (MINI 7,5 A) | mostek | silnik ≤ 6 A (próba 10 A — bierna kwalifikacja toru) |

Razem z 5V_SYS ok. 30 mA bez KPWR i **ok. 110 mA z załączonym KPWR** (+80 mA cewki) (budżet P12: suma LOGGER 1090 mA). Pojemność na 5V_SYS ok. 37 µF (C9 wprost, reszta za R50 i PTC), wobec 600 µF dla TSR 2-2450 (P02 R4).

## Masy

GND (logika, analog, J_BP) i PGND (prąd silnika) **nie są połączone na P07**. Jedyny punkt łączenia mas to P02 R4 (J2.2 = GND płytki zasilania). Dzięki temu prąd silnika nie wraca przez taśmy i P12, a INA240 mierzy w linii M+ niezależnie od mas. Przewód GND wiązki sterującej (MOD_GND) idzie przez R43 10 Ω:

- **moduł z GND logiki połączonym z B−:** pętla P07 GND → wiązka → moduł → B− → przewód PGND → P02 przenosi najwyżej spadek na przewodzie powrotnym / 10 Ω (ok. 50 mV / 10 Ω = 5 mA przy 10 A); po przerwaniu przewodu B− R43 działa jak bezpiecznik;
- **moduł z rozdzielonymi masami** (pomiar 5.10: 508 mV w trybie diody): R43 przenosi tylko prąd VCC modułu (spadek ≤ 0,2 V przy 20 mA).

Obwód cewki KPWR (5V_SYS → K1 → Q1 → GND, clamp do 5V_SYS) jest od 5.10 w domenie GND; styki K1 (VMOTOR / MOD_BP) zostają w domenie PGND — izolację daje przekaźnik. Kontrola `GND-PGND-SEPARATE`: żadna część nie ma wyprowadzeń na GND i PGND jednocześnie, na GND i sieci mocy ani na PGND i sieci cewki.
