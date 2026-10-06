# P07 DRIVE — S1, schemat pod moduł IBT-2 (2 × BTS7960B)

*5.10.2026, sesja w chmurze według `Plytki/Format-S1/zadania/ZADANIE-P07-S1.md`. Baza: `origin/pelny-s1`. Pinout P04 R3 z `origin/p04-r3-pcb` (702732a7, `reference/P04-R3-J_BP.csv`).*

**Status (6.10): schemat z decyzjami użytkownika 5.10 i uproszczeniami 6.10 gotowy (ERC 0, kontrole 16/16 i 27/27). PCB NIEDOMKNIĘTE — po uproszczeniach 1–4 zostało 13 przerw sygnałowych (sekcja „PCB — stan”); paczki produkcyjnej nie ma.** Sprzętu nie zmontowano ani nie zmierzono. Moduł IBT-2 zmierzono tylko bez zasilania (POMIARY A–C); kroki D i E nie są zrobione.

## Co to jest

Płytka nośna testera w stosie S1: **poziom 5, sloty S2–S3, klasa 2/3 (106,5 × 100 mm)**. Moduł IBT-2 stoi poza stosem, na ściance obudowy, i łączy się z P07 taśmą 8 żył (J5) oraz czterema parami przewodów 2,0 mm² (J1–J4). Z v6.1 (Pololu 1451 / VNH5019) zostają: własny bocznik Kelvin 5 mΩ + INA240A2 + MCP3201 (ITEST), okno OC z zatrzaskiem, KPWR i otwarty kolektor na SAFE_N. To nie jest zamiana pin w pin. W trybie LOGGER mostek nie jest połączony z ECU — robi to dopiero port TEST na panelu (P11).

| Arkusz | Zawartość |
|---|---|
| P07 | 5VA_P07 (R50 10 Ω), 3V3A_P07 (MCP1702), odsprzęganie, arkusze |
| MOC | J1 VMOTOR, TVS SMCJ18A, C1 220 µF, KPWR K1 (G2RL-1-E **DC5, cewka z 5V_SYS**) z Q1 AO3400A, C9 10 µF i clampem 15 V do 5V_SYS, R4 1 k (wstępne ładowanie), J2 B+/B−, J3 M+/M−, RSH1, J4 TEST |
| ANA | R6/R7 Kelvin, INA240A2, MCP1525, U3 (bufor ADC + REF_BUF), dzielnik ITEST, U4 (OC_HIGH), TLV1702 |
| DIG | MCP3201 (posiadany DIP8), 74LVC125 SPI (DOUT trójstanowy), przejście SUP5 5 V → 3,3 V |
| LOGIKA | MCP120 ×2, odbiorniki Ioff 74LVC125 (od 6.10 tylko MOTOR_INA / INB), 74LVC14 (Schmitt), 3 × 74HC08, 74HC74 (OC_GOOD, NO_TRIP), Q2 na SAFE_N |
| MODUL | PTC → 5V_MOD, 74AHCT125 (3,3 → 5 V z OE), J5, R43 10 Ω w masie modułu, diagnostyka IS (dzielnik + clamp, próg na P03) |
| ZLACZA | J_BP1, J_BP2 |
| SERWIS | J_SV2 z 9 rezystorami przy węzłach (od 6.10; było J_SV1 + J_SV2, 20 kołków) |

Obliczenia: `docs/PROJEKT.md`. Wiązki: `docs/WIAZKA-MODUL.md`. BOM S1: `docs/BOM.csv`, `docs/zakupy.csv` (132 części + wiązka W5; z rejestru INA240A2, MCP3201-BI/P i 2 × 74LVC125AD, reszta nowa).

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

Od 6.10 (uproszczenie 1) **jedna listwa J_SV2** (S3, x 63,5–96,5, 12 kołków): GND, 5V_SYS, 5VA_P07, 3V3A_P07, KPWR_COIL_LOW, SAFE_OK, OC_LOCAL_N, OC_GOOD, DRIVE_OK (1 k), GND, I_T_OUT (10 k), GND. Zwarcie kołka OC_LOCAL_N do GND (przez 1 k) wymusza OC — próba odbiorcza zatrzasku. RPWM / LPWM / EN / IS mierzy się na listwie modułu, która jest poza stosem. `docs/SERWIS.csv`.

## Kontrole (`src/run_schematic.py`; w chmurze `scripts/egrlab-docker python3 src/run_schematic.py`, ok. 1 min)

| Kontrola | Wynik |
|---|---|
| ERC | **0** na 8 arkuszach |
| Netlista pin po pinie względem `parts.py` | **448/448**, 132 części, 101 sieci (po uproszczeniach 6.10) |
| `verify_electrical.py` | **16/16**, mutacje **23/23**, próba zerowa czysta |
| `verify_s1.py` (S1 i kontrakty P12 / P03 R6 / P04 R3) | **27/27**, mutacje **26/26**, próba zerowa czysta (od 6.10 jedna listwa: 5 kontroli J_SV1 odpada, dochodzą `SV-ONLY-J_SV2` i `SRV-REQUIRED-NODES`) |
| Powierzchnia (`powierzchnia.py`) | 69 % metodą P06 R2 (tam 41 %); wnętrze bez złączy krawędzi 50 %, z 1206 od spodu 37 % |

`verify_electrical.py` symuluje logikę na wyeksportowanej netliście: modele bramek według wartości części, podciąganie przez najmniejszą rezystancję, komparator i nadzorcy jako otwarte kolektory, 74HC74 z PRE/CLR i zboczem. Tabela 2304 wierszy pokazuje, że **bez MOTOR_PERMIT, bez SAFE_N, przy OC albo złych szynach wszystkie wejścia modułu (RPWM, LPWM, R_EN, L_EN) są L**, a KPWR wyłączony. Do tego martwe szyny, otwarte taśmy, zawieszona bramka AND (blokuje ją OE bufora), 11 kroków sekwencji zatrzasku (brak samoczynnego uzbrojenia, ARM przy PERMIT = H nie uzbraja, ARM w trakcie OC nie kasuje), progi OC w narożnikach (+8,01…+8,11 A / −7,99…−8,03 A), skala ITEST, moce bocznika i R4, cewka 5 V z 5V_SYS, bramka Q1 i clamp KPWR, TVS, próg IS i rozdział mas. Raporty: `verification/QA.md`, `electrical-checks.json`, `s1-checks.json`, `powierzchnia.json`; PDF `output/pdf/P07-S1-schemat.pdf`.

## Decyzje (sporne oznaczone)

1. **Mapowanie VNH5019 → BTS7960:** RPWM = PWM & MOTOR_INA, LPWM = PWM & MOTOR_INB, R_EN = L_EN = DRIVE_EN. Hamowanie i stany INA = INB jak w VNH5019. Firmware bez zmian w sterowaniu.
2. **Blokada w trzech warstwach:** bramki AND (MOTOR_PERMIT · SAFE_N · OC_GOOD · RAILS_OK), OE bufora 74AHCT125 i KPWR. 74HC244 modułu jest stale aktywny (OE na GND), więc moduł sam niczego nie blokuje.
3. **DRIVE_OK = RAILS_OK & NO_TRIP** (nowy drugi przerzutnik). Przy starcie bez ARM DRIVE_OK = 1, więc INTERLOCK na P04 nie blokuje LOGGERA ani SENSOR. Po OC DRIVE_OK = 0 aż do ARM. v6.1 miało DRIVE_OK = RAILS_OK.
4. **Logika na 3V3_IO** (jak P04), analog na lokalnych 5VA / 3V3A (jak P06 R2). Odbiorniki z Ioff tylko tam, gdzie drugi koniec może mieć inne zasilanie (P03: MOTOR_INA/INB, CS, SCLK) oraz dla MOTOR_PERMIT / PWM_OUT. SAFE_N wchodzi przez 1 k na Schmitt 74LVC14 (zbocze RC ok. 10 µs na P04), bez podciągania na P07, z 1 M do GND (otwarta taśma = SAFE_OK L).
5. **R4 1 kΩ równolegle do styków KPWR (zostaje — decyzja użytkownika 5.10):** ładuje 330 µF modułu, żeby styk nie zamykał się na pusty kondensator (spawanie). Cena: przy otwartym KPWR B+ modułu jest na 91 % VMOTOR przez 1 k; prąd silnika ≤ 17 mA, przy zwarciu 0,28 W.
6. **KPWR to przekaźnik G2RL-1-E DC5 z cewką na 5V_SYS** (decyzja użytkownika 5.10; było DC12 z VMOTOR), nie tranzystor: galwaniczne odłączenie i brak strat przy 10 A (MOSFET z P02 dałby ok. 2 W bez radiatora). Cewka 80 mA przy 98–102 % napięcia znamionowego, Q1 AO3400A (źródło na GND, bramka wprost z 74HC08 przez 100 Ω — NPN potrzebowałby ok. 6 mA bazy z HC przy 3,3 V), clamp 1N4148W + 15 V do 5V_SYS (VDS ≤ 20,8 V), C9 10 µF przy cewce. Obwód cewki w domenie GND, styki w domenie PGND. Footprint bez zmian.
7. **Masy:** GND i PGND rozdzielone na P07, wspólny punkt na P02 R4. MOD_GND przez 10 Ω. Działa przy masie modułu połączonej z B− i przy rozdzielonej (`docs/PROJEKT.md`).
8. **Sporne — filtr ITEST τ 0,26 ms** (C7 100 nF C0G): antyaliasing przy 2 kS/s.
9. **OC ±8 A:** ≥ 115 % prądu pracy 6 A, poniżej nasycenia INA240A2 przy najniższym 5VA. „10 A w próbie” = bierna kwalifikacja toru jak w P06 (E15) — decyzja użytkownika 5.10; aktywny mostek nie podaje 10 A.
10. **ENA_DIAG / ENB_DIAG:** H = prąd gałęzi powyżej ok. 1,3–5,8 A (od 6.10: próg na wejściu P03, bez Schmitta) albo poziom błędu IS (przyjęte 5.10; firmware dostosuje się później). Znaczenie inne niż w VNH5019 (tam L = błąd).
11. Wyjątki od „nowe = SMD 1206”: R4 2512 (moc), C1 elektrolit, RSH1 2512 Kelvin (jak P06 R2), K1, MCP3201 w posiadanym DIP8, TO-92 jak w P06 R2.

## Wymagania dla layoutu (sesja lokalna)

- J4 (TEST) przy krawędzi x = 0; J1–J3 najlepiej tam samo, żeby pętla 10 A była krótka. Tor 10 A ≥ 4 mm na obu warstwach, zszyty przelotkami; bez przelotek w polach RSH1; para Kelvina jak w P06 R2.
- PGND jako osobna wylewka (J1.2, J2.2, D1, C1–C4, R1, R3, R5, Q1.E), bez połączenia z GND; GND logiki i analogu z dala od toru mocy.
- K1 ma 15,7 mm wysokości — mieści się w 16,5 mm poziomu 5. C1 D8 × 11,5 mm stoi. Od spodu tylko SMD ≤ 1,5 mm (bez SOIC, bez 10 µF 1206, jeśli grubsze niż 1,5 mm).
- J5 kątowy przy krawędzi, w stronę modułu. J_BP1 x = 26,5, J_BP2 x = 80,0 (układ płytki). Listwy J_SV1 x = 10–43, J_SV2 x = 63,5–96,5. Osiem otworów M3 (x = 4 / 49 / 57,5 / 102,5; y = 14 / 86).
- Powierzchnia jest ciasna (50 % wnętrza wobec 29 % w P06 R2): rezystory i małe kondensatory 1206 od spodu, przy węzłach.

## Decyzje użytkownika 5.10 (wprowadzone w schemacie, pytania 1–7 zamknięte)

1. **KPWR K1 z cewką 5 V z 5V_SYS** (G2RL-1-E DC5, ten sam footprint): cewka ok. 80 mA na 5V_SYS (bilans w `docs/PROJEKT.md`), Q1 AO3400A ze źródłem na GND, clamp 15 V do 5V_SYS, C9 10 µF przy cewce. Kontrola `KPWR-DRIVE-CLAMP` (okno napięcia cewki, VGS, VDS clampu, rezystor bramki i ściągający) i trzy nowe mutacje. — pytanie 3
2. **R4 1 kΩ równolegle do styków KPWR zostaje.** — pytanie 4
3. **J5 = obudowane IDC 2 × 4 kątowe, raster 2,54, numeracja 1:1 jak listwa modułu** (1 RPWM, 3 R_EN, 5 R_IS, 7 VCC / 2 LPWM, 4 L_EN, 6 L_IS, 8 GND); taśma 8 żył z gniazdami IDC 2 × 4 na obu końcach (`docs/WIAZKA-MODUL.md`, W5 w `BOM.csv` i `zakupy.csv`). Pinout był już taki — kontrola `JMOD-PINOUT` bez zmian. — pytanie 6 (B4)
4. **„10 A w próbie” = bierna kwalifikacja toru** (jak P06, E15): zostaje INA240A2 i OC ±8 A. — pytanie 2
5. **ENA_DIAG / ENB_DIAG: H = prąd gałęzi powyżej progu albo błąd IS** — przyjęte; firmware dostosuje się później. — pytanie 5
6. **J1–J3 przy krawędzi x = 0 obok J4** (krótka pętla 10 A) — w layoucie. — pytanie 7
7. **Bezpiecznik F1 na P02 R4: wkładka MINI 7,5 A** (płytka P02 bez zmian) i **próba nagrzewania toru VMOTOR przy odbiorze** (P02 → przewody → P07 J1 → K1 → J2, prąd 6 A ciągle, potem 10 A krótko; temperatura toru P02 5,7 mm / 35 µm, F1 i lutów). P02 R4 nie jest ruszane przez ten pakiet. — pytanie 1
8. **Pomiary modułu (pytanie 6):** B4 = pinout jak wyżej (zamknięte); C5: GND złącza ↔ B− w trybie diody 508 mV (COM na B−) — nie są zwarte wprost, zgodnie z decyzją 7 o masach (R43 10 Ω, PGND osobno); D1 (prąd VCC), E2 (RPWM → M+), E3 (kILIS) — przy odbiorze.

Informacyjnie (pytania 8–9 bez zmian w tym pakiecie): P12 R2 z J_BP1/J_BP2 P07 i J_BP1–3 P04 R3 dla poziomów 5–6; numery pinów P04 wzięte z `origin/p04-r3-pcb` (702732a7) — po scaleniu P04 odświeżyć `reference/P04-R3-J_BP.csv` i puścić kontrole.

## Uproszczenia 6.10 (decyzja użytkownika: klasa 2/3, 2 warstwy — uprościć i trasować ponownie)

Łańcuch blokady (bramki AND, OE bufora, KPWR), OC z zatrzaskiem i DRIVE_OK, bocznik Kelvin + INA240 + MCP3201 z trójstanowym DOUT, kontrakt J_BP, J5 i tor 10 A — bez zmian (tabela 2304 stanów, mutacje i kontrakt jak wcześniej).

1. **Jedna listwa serwisowa J_SV2 (12 kołków) zamiast J_SV1 + J_SV2 (26 kołków, 20 rezystorów → 9).** Zostały węzły odbioru krytycznego: 5V_SYS, 5VA_P07, 3V3A_P07, KPWR_COIL_LOW, SAFE_OK, OC_LOCAL_N (zwarcie kołka do GND = wymuszone OC), OC_GOOD, DRIVE_OK, I_T_OUT (ITEST). KPWR_COIL_LOW ma od 5.10 0–5 V, więc rezystor 1 k (klasa logiki). *Skutek dla odbioru:* ADC_AIN, REF25 / REF_BUF, progi OC_HIGH / OC_LOW, RAILS_OK, NO_TRIP, 3V3_IO i 5V_MOD mierzy się sondą na częściach przed złożeniem stosu (po złożeniu wymaga to rozebrania stosu, S1 §6); VMOTOR / MOD_BP / T_EGR_P1 — na przewodach i zaciskach modułu poza stosem; DRIVE_EN, RPWM / LPWM — na listwie modułu (poza stosem); RAILS_OK pośrednio przez DRIVE_OK.
2. **Rozmieszczenie:** łańcuch ADC (U6 / U7 / U3 / U2) przy J_BP1 i na prawo od wylewek, dzielniki IS przy J_BP1, logika pod J_BP2 w siatce 11,5 mm, większe odstępy części biernych (1,4 mm między obrysami). *Skutek:* R_IS / L_IS (sygnały DC uśrednione dopiero na P07) biegną przez płytkę zamiast ENA / ENB_DIAG.
3. **Odbiorniki Ioff tylko dla P03:** MOTOR_PERMIT i PWM_OUT przychodzą z P04 na tej samej szynie 3V3_IO, więc idą wprost na U11 / U12 / U13 (kanały 3–4 U10 nieużyte, wejścia na GND); U10 obsługuje MOTOR_INA / INB (P03 może działać z samego USB). Liczby układów nie da się zmniejszyć: U7 (3V3A, strona ADC) i U10 (3V3_IO, Ioff) mają różne domeny. *Skutek:* brak (pull-downy 100 k przy otwartej taśmie zostają; tabela stanów bez zmian).
4. **Diagnostyka IS bez Schmitta U17 i bez R48 / R49:** dzielnik 4,7 k z 10 k na wejściu P03, C 100 nF, BAT54S; próg = wejście LVC125 na P03 (szczegóły i straty: `docs/PROJEKT.md`, „Diagnostyka IS”). *Skutek:* pasmo progu 1,3–5,8 A zamiast 1,6–4,6 A, brak histerezy (bit może migać przy prądzie blisko progu), próg zależy od 10 k na P03.

Razem: 148 → 132 części, 116 → 101 sieci, 237 → ok. 200 połączeń sygnałowych do trasowania.

## PCB — stan (6.10.2026, sesja lokalna; NIEDOMKNIĘTE po uproszczeniach 1–4)

Łańcuch layoutu przeniesiony z P06 R2 (tor mocy, Kelvin, kontrole) i P04 R3 (generyczne skrypty, belki GND pod SOIC): `src/board.py`, `placement.py`, `route_critical.py`, `run_layout.py` i reszta jak w P06 R2; `verify_pcb.py`, `negative_controls.py`, `make_pdf.py`, `heights.py`, `silkscreen.py` przystosowane do P07 (jedna listwa), ale **nieuruchomione na gotowej płytce** (płytki nie ma). Paczki `P07-PCB-S1-zamowienie` nie ma (jest tylko przygotowany `src/` z konfiguracją).

**Co działa (sprawdzone po imporcie trasowania):** kolumna J1–J4 przy x = 0 (decyzja 6; rząd pól x = 21,7, kotwy x = 9,7 — przy x = 3 jak w P06 cztery końcówki nie mieszczą się między strefami M3: 69 mm wobec 60,8 mm); kolejność od góry J2.2 PGND, J2.1 B+, J1.1 VMOTOR, J1.2 PGND, J3.1 M+, J3.2 M−, J4.2 M−, J4.1 TEST P1 (J1 i J3 numerowane od drugiego końca). K1 obrócony o 180°: NO na wysokości J2.1, COM nad J1.1, cewka (domena GND) na dole. Wylewki VMOTOR, MOD_BP, PGND, MOD_MP, T_EGR_P1, T_EGR_P3 na obu warstwach, PGND łączy J2.2 i J1.2 pasem między kotwami a polami; RSH1 i para Kelvina do R6 / R7 / U1 jak w P06 R2; piny NC przekaźnika połączone krótkim torem. **W żadnym przebiegu DRC nie zgłasza przerwy w sieciach mocy.**

**Trasowanie sygnałów (Freerouting 2.1.0, 30 przejść + planer `complete_routes.py`):**

| Stan | Połączenia sygnałowe (DSN) | Przerwy w DRC po routerze | Po planerze |
|---|---|---|---|
| 5.10, podejście 1 (ciasno) | 237 | ok. 100 (router stał na 157–172 „unrouted”) | — |
| 5.10, podejście 2 (ADC przy J_BP1, odstępy 1,4 mm) | 237 | 70 (65 sygnałowych) | 44 |
| 6.10, uproszczenia 1 + 3 i rozmieszczenie 2 | ok. 215 | 26 | 27 (13 sygnałowych + masa) |
| 6.10, po uproszczeniu 4, próba 1 | 210 | 20 | ok. 9 sygnałowych bez drogi |
| 6.10, po uproszczeniu 4, próba 2 | 210 | 24 | **17 (13 sygnałowych, 4 wyspy GND)** |

Ostatnie przerwy (`routing/postplan-drc.json`, obraz `output/previews/layout-wip-unconnected.png`) są prawie wyłącznie w bloku logiki pod J_BP2: MOTOR_PERMIT (2), SUP5_N (2), LOCAL_PERMIT, DRIVE_EN, DRV_OFF, PWM_OUT, RPWM_L, OC_GOOD, INB_P07, SAFE_N i jedna linia serwisowa (SRV_3V3A_P07). Zajętość (`powierzchnia.py`): 62 % sumy obrysów wobec pola użytecznego, wnętrze bez złączy krawędzi 48 % (5.10: 69 / 50 %); lewe 25–55 mm płytki to wylewki toru 10 A na obu warstwach.

Zgodnie z poleceniem z 6.10 („jeśli po krokach 1–4 nadal nie domyka się, zatrzymaj się i podaj liczby”) praca stoi tutaj. **Dalsze możliwości (do decyzji):** (a) rozluźnić blok logiki (U10–U16 w siatce 13–14 mm, U14 / U16 przy J5, SUP5 przesunięte z U7 na wolne kanały U10 — U10 ma od 6.10 dwa wolne kanały) i puścić 2–3 kolejne próby routera — wynik bliski domknięcia (13 przerw), ale bez gwarancji; (b) ręcznie prowadzone magistrale logiki przed routerem (jak wyjścia zasilania P04 R3); (c) klasa L albo 4 warstwy (wcześniejsze propozycje, odrzucone 6.10).

Pliki stanu: `src/placement.json`, `routing/attempt-1.ses` / `attempt-2.ses`, `routing/wip-postplan.kicad_pcb` i `eda/P07.kicad_pcb` (płytka po planerze — NIE do produkcji), `output/previews/layout-wip-F.png` / `-B.png`.

## Pliki

- `eda/` — schemat KiCad 10 (8 arkuszy A3), biblioteki lokalne (footprinty końcówek przewodów, bocznik WSK2512 jak w P06 R2).
- `src/` — `parts.py` (jedno źródło obwodu), `build_schematic.py`, `make_tables.py`, `verify_schematic.py`, `verify_electrical.py`, `verify_s1.py`, `powierzchnia.py`, `make_qa.py`, `run_schematic.py`, `cadlib.py` (z P06 R2).
- `docs/` — `J_BP.csv`, `SERWIS.csv`, `BOM.csv`, `zakupy.csv`, `parts.json`, `interfejsy.csv`, `netlist-pinowa.csv`, `PROJEKT.md`, `WIAZKA-MODUL.md`.
- `reference/` — `P03-R6-J_BP.csv`, `P04-R3-J_BP.csv` (z `origin/p04-r3-pcb`), `P12-kontrakty.json` (P12 przygotowanie), skróty SHA-256.
- `output/` — `pdf/P07-S1-schemat.pdf`, podglądy PNG.
- `verification/` — ERC, netlista, raporty kontroli, `QA.md`, logi, manifest.
