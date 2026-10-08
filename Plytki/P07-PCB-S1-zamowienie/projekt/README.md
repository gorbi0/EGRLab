# P07 DRIVE — S1, schemat pod moduł IBT-2 (2 × BTS7960B)

*5.10.2026, sesja w chmurze według `Plytki/Format-S1/zadania/ZADANIE-P07-S1.md`. Baza: `origin/pelny-s1`. Pinout P04 R3 z `origin/p04-r3-pcb` (702732a7, `reference/P04-R3-J_BP.csv`).*

**Status (8.10): schemat gotowy (ERC 0, kontrole 16/16 i 27/27), PCB na 4 warstwach gotowe (DRC 0 niepołączonych / 0 niezgodności, 4 przyjęte lib_footprint_mismatch od przyciętego nadruku; kontrole PCB 35/35, próby ujemne 41/41), paczka `Plytki/P07-PCB-S1-zamowienie`.** Sprzętu nie zmontowano ani nie zmierzono. Moduł IBT-2 zmierzono tylko bez zasilania (POMIARY A–C); kroki D i E nie są zrobione.

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

- (7.10: J1, J2, J4 przy krawędzi x = 106,5, J3 na krawędzi B — sekcja „Decyzje 6.10 wieczorem i 7.10”; było: J4 przy x = 0, J1–J3 tam samo.) Tor 10 A ≥ 4 mm na obu warstwach, zszyty przelotkami; bez przelotek w polach RSH1; para Kelvina jak w P06 R2.
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
6. ~~**J1–J3 przy krawędzi x = 0 obok J4**~~ — zmienione 6.10 wieczorem / 7.10 po recenzji stosu (przewody szły nad P08): wszystkie końcówki po stronie wejść. — pytanie 7
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

## Decyzje 6.10 wieczorem i 7.10 (layout; sporne oznaczone)

1. **Końcówki przewodów po stronie wejść (użytkownik, po recenzji stosu MAJOR-1):** przy x = 0 osiem przewodów 2,0 mm² szło nad P08 (szczelina ok. 18,5 mm, nad C10 P08 ok. 6 mm). Teraz J1 (VMOTOR), J2 (B+/B−) i J4 (TEST) stoją w kolumnie przy krawędzi x = 106,5 (w stosie x = 160) razem z J5, a J3 (M+/M−) na krawędzi B obok J4, bo kolumna mieści tylko cztery elementy po ok. 19 mm. Żaden przewód nie idzie nad P08. Przewody J4 do P11 obchodzą stos, ok. +250 mm (`docs/WIAZKA-MODUL.md`). P04, P08 i P12 bez zmian.
2. **Logika na In2 pod blokiem przekaźnika (użytkownik 7.10):** In2 pod wylewkami VMOTOR / MOD_BP / PGND niesie ścieżki logiki 3,3 V; odniesieniem jest tam PGND na In1. Analog i Kelvin nie mogą (kontrola `board.ANALOG_NETS`), stref zasilań tam nie ma. Bez tego kanał x 40–56 przy przekaźniku nie mieścił połączeń logiki góra–dół (22 przebiegi routera).
3. **Sporne — ścieżki sygnałowe 0,2 mm** (było 0,3 jak P02 R3; S1 nie podaje liczby, JLCPCB 4 warstwy od 0,09 mm). Odstęp 0,25 mm i klasa PWR 0,4 mm bez zmian.
4. **Sporne — przelotki sygnałowe i GND 0,6 / 0,3 mm** (pierścień 0,15; standard JLCPCB dla 4 warstw), było 0,9 / 0,4. Przelotki toru mocy i klasy PWR zostają 0,9 / 0,4.
5. **Każde pole GND na wierzchu ma przed routerem przelotkę do płaszczyzny In1** (`FANOUT_MODE = 'all'`): na 4 warstwach przelotka zawsze trafia w ciągłą masę; wyspy GND były połową niedomkniętych połączeń.
6. **U11.13 (nieużywane wejście 6A LVC14) na 3V3_IO zamiast GND** — jedyna zmiana schematu; obok jest pin 14 (VCC), na GND potrzebna była przelotka, na którą nie było miejsca. Funkcja bez zmian (6Y niepodłączone); ERC 0, 16/16 (mutacje 23/23), 27/27 (26/26).
7. **Połączenia pod korpusem U16 przed routerem** (`board.PRE_TIES`): DRIVE_EN 12 → 9 i DRV_OFF 13 → 1 / 4 (router łączył je pętlą po zewnątrz i zamykał LEN_D).
8. Wyjątki kontroli, jawne w `board.py`: C35 6,5 mm od U15.14 (limit 6) i C21 11,4 mm od J_BP2.14 (limit 10) — `DEC_ACCEPT`; MOD_MP na B.Cu J3.1 → RSH1 — `FORCE_PATH_ACCEPT` (bocznik jest SMD na F, korytarz ≥ 4 mm sprawdzony na F.Cu). Przelotka fanoutu GND w narożniku pasa VMOTOR (72,47; 25,02) robi małe wycięcie poza drogą prądu (DRC czysty); przy następnej wersji fanout ma omijać wylewki mocy.

## PCB — stan (8.10.2026, sesja lokalna)

4 warstwy JLC04161H-7628 (In1 GND, pod blokiem przekaźnika PGND; In2 sygnały + strefy 3V3A_P07 / 5VA_P07 / 3V3_IO), 106,5 × 100 mm, 8 × M3. Blok przekaźnika K1 (leżący) u góry po prawej z J1 / J2, pętla silnika w prawym dolnym rogu: J3.1 → RSH1 (obrót 90°, nad J3.1) → pas T_EGR_P1 → J4.1, J3.2 → J4.2 pod nim; Kelvin w lewo przez R6 / R7 do U1. Logika U11 / U15 / U12 pod J_BP2, U10 / U13 / U14 / U16 w rzędzie y 63,6 przy J5; łańcuch ADC przy J_BP1; okno OC i nadzorcy po lewej; J_SV2 w slocie S2 (x 13,8–41,7).

| | |
|---|---|
| DRC (świeży) | 0 niepołączonych, 0 niezgodności ze schematem, 4 × lib_footprint_mismatch (przycięty nadruk, przyjęte) |
| Kontrole PCB (`verify_pcb.py`) | **35/35** |
| Próby ujemne (`negative_controls.py`) | **41/41** z próbą zerową |
| Miedź | F.Cu 730, B.Cu 240, In2.Cu 175 odcinków; przelotki 108 × 0,9/0,4 (moc), 162 × 0,6/0,3 |
| J_BP1 / J_BP2 | środki x 26,500 / 80,000, pin 1 y 13,33 (kontrakt P12 R2) |
| Trasowanie | Freerouting 2.1.0, przebieg 22, próba 1 (4 nieprzyłączenia po routerze) + planer `complete_routes.py`; odtworzenie bez routera: `src/run_release.py` (`run_layout.py --reuse-ses`) |

Historia 6.10–7.10 (dla następnych płytek): 22 przebiegi; przy pasach 10 A w poprzek płytki 79 przerw, po przeniesieniu J3 / J4 i usunięciu płaszczyzn In2 z DSN 7–25, decydujące były przelotki 0,6 / 0,3 i otwarcie In2 pod blokiem mocy (4). Kontrole i skrypty poprawione po drodze: zszywanie GND omija obce ścieżki i pola na F / B / In2, `inner_zones.py` odporny na drugie wywołanie, kontrola korytarza 4 mm na wypełnieniu po `Unfracture()` (rozcięte wielokąty KiCad dawały fałszywe przerwy), pokrycie In1 bez własnych pinów THT, strefy D7 na czterech warstwach.

Oględziny podglądów (`output/previews/copper-front.png`, `copper-back.png`, `copper-in2.png`): bez widocznych usterek; pod wylewkami J1 / J2 / J4 na In2 brak ścieżek. In1 i rysunek montażowy — w recenzji. Napis płytki nad J_SV2; 22 oznaczenia ukryte z braku miejsca (są na rysunku montażowym z F.Fab).

## Pliki

- `eda/` — schemat KiCad 10 (8 arkuszy A3), biblioteki lokalne (footprinty końcówek przewodów, bocznik WSK2512 jak w P06 R2).
- `src/` — `parts.py` (jedno źródło obwodu), `build_schematic.py`, `make_tables.py`, `verify_schematic.py`, `verify_electrical.py`, `verify_s1.py`, `powierzchnia.py`, `make_qa.py`, `run_schematic.py`, `cadlib.py` (z P06 R2).
- `docs/` — `J_BP.csv`, `SERWIS.csv`, `BOM.csv`, `zakupy.csv`, `parts.json`, `interfejsy.csv`, `netlist-pinowa.csv`, `PROJEKT.md`, `WIAZKA-MODUL.md`.
- `reference/` — `P03-R6-J_BP.csv`, `P04-R3-J_BP.csv` (z `origin/p04-r3-pcb`), `P12-kontrakty.json` (P12 przygotowanie), skróty SHA-256.
- `output/` — `pdf/P07-S1-schemat.pdf`, podglądy PNG.
- `verification/` — ERC, netlista, raporty kontroli, `QA.md`, logi, manifest.
