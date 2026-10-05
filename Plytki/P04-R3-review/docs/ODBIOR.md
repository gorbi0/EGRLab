# P04-R3 — formularz odbioru etapowego (format S1)

*R3 (5.10.2026): pozycje R2.2 bez zmian merytorycznych; punkty pomiarowe przeniesione z pól TP na listwy serwisowe J_SV1–J_SV3 (kołek przez rezystor 1 kΩ / 10 kΩ, multimetr 10 MΩ mierzy bez zauważalnego błędu), złącza J1–J8 na J_BP1–J_BP3. Przy odbiorze pojedynczej płytki J_BP są dostępne bezpośrednio (P00 przez przejściówkę taśmową — do przygotowania, P00 R3 ma wiązkę do J1–J8 R2.2).*

## Mapa punktów R2.2 → R3

| R2.2 | R3 | Rezystor |
|---|---|---|
| TP1 3V3_IO | J_SV3.3 | R58 1k |
| TP2 GND | J_SV1.1/3/5/13, J_SV2.1/7, J_SV3.1/7 | — |
| TP3 LOCAL_SUP_N | J_SV1.12 | R51 1k |
| TP4 SUP_OK | J_SV2.2 | R52 1k |
| TP5 WD_Q | J_SV1.10 | R49 1k |
| TP6 SAFE_N | J_SV1.2 | R43 10k |
| TP7 SAFE_OK | J_SV1.8 | R47 1k |
| TP8 ARM_CLK | J_SV1.6 | R45 1k |
| TP9 HW_ARMED | J_SV1.7 | R46 1k |
| TP10 INTERLOCK | J_SV2.3 | R53 1k |
| TP11 MOTOR_PERMIT | J_SV2.4 | R54 1k |
| TP12 SENSOR_PERMIT | J_SV2.6 | R56 1k |
| TP13 5V_SYS | J_SV3.2 | R57 1k |
| TP14 SAFE_WD | J_SV1.9 | R48 1k |
| TP15 Q1_B | J_SV1.11 | R50 1k |
| nowe: ARM_BUTTON_N (E15) | J_SV1.4 | R44 10k |
| nowe: PWM_OUT (E06, E19) | J_SV2.5 | R55 1k |
| nowe: PANEL_3V3, P04_3V3, PG_SEND (E05, E22) | J_SV3.4 / .5 / .6 | R59 / R60 / R61 1k |
| J1.3 zasilanie 3V3_IO | J_BP2.10 i J_BP3.10 | — |
| J8 panel: 1 PANEL_3V3, 3 TEST_KEY, 4 MECH_OK, 7 STOP_NC_OUT, 9 ARM_CONTACT | J_BP1.2 / .14 / .4 / .6 / .8 | — |
| J7 PG: 1 PG_3V3, 2 SAFE_N, 4 PG_SEND, 5 PG_LINK | J_BP2.14 (P04_3V3) / .16 / .20 / .18 | — |

**Zmienione czynności R3:**
- **E21:** zworą połączyć kołek J_SV1.11 (Q1_B) z dowolnym kołkiem GND (najbliższy GND to J_SV1.13, przez J_SV1.12 — zwora przewodem, nie zworką 2,54 mm). Przez R50 1 kΩ baza schodzi do ok. 0,30 V (R6 10 kΩ z wyjścia bramki), Q1 zatkany. Pomiar SAFE_N na J_SV1.2.
- **E22:** prądy zwarcia mierzyć na pinach J_BP (J_BP1.2 ok. 33 mA, J_BP2.14 ok. 3,3 mA, J_BP2.20 ok. 3,3 mA), nie na kołkach J_SV3 (tam szeregowy 1 kΩ daje ok. 3,3 mA niezależnie od R38–R40).
- **E04, E18:** adapterów nie ma (SOIC lutowane wprost). E18 odpada; E04 mierzyć na pinach U8–U10.
- **M01/M02:** przymiarka P04 w stosie z dystansami 20 mm, taśmy J_BP1–J_BP3 do P12; ciągłość każdej żyły taśmy.
- **I01 (z P02 R4 zamiast P01):** brak ENABLE P02 ściąga SAFE_N (Q7); P04_3V3 zasila Q7 z P04.

Operator / data / numer PCB / MPN i partia U1/U11: __________________________

Wynik początkowy każdej pozycji: **NIE ZBADANO**. Najpierw sama P04 z P00; bez silnika, EGR, ECU i P07. Oscyloskop/analizator z masą wspólną i sondami o dużej impedancji. Zapisywać przebiegi, nie tylko PASS.

| ID | Czynność i wymagany wynik | Pomiar / wynik |
|---|---|---|
| M01 | Przymiarka 100%, kołki/otwory/klucze złączy, numeracja adapterów, kotwy | NIE ZBADANO |
| M02 | Ciągłość każdej żyły; brak zwarć sąsiadów, klucze NC. Powtórzyć po poruszeniu wiązką | NIE ZBADANO |
| E01 | Bez U1–U10: zasilanie 3,3 V limit 50 mA na J1.3/GND. Sprawdzić C3 i pinout U11 | NIE ZBADANO |
| E02 | Powolny wzrost/spadek VDD: RESET U11 (MCP100-300), próg opadający 2,85–3,00 V; po przekroczeniu progu zwolnienia odczekać 150–700 ms. Zmierzyć histerezę (katalogowo 50 mV TYP, bez gwarantowanego maksimum) | NIE ZBADANO |
| E03 | Włożyć układy przy wyłączonym zasilaniu. Przy 3,30 V i wszystkich wejściach L: MOTOR/SENSOR/PWM/HW_ARMED L, LED świeci. Zapisać prąd | NIE ZBADANO |
| E04 | Każdy z 11 buforów: H/L/odpięcie, odczyt przed i za buforem. Po odpięciu oba punkty L | NIE ZBADANO |
| E05 | Wszystkie READY, TEST_KEY i MECH_OK H, SUP_N H, STOP zamknięty, HB ok.100 Hz. TP10 INTERLOCK H, TP5 WD_Q H, TP6 SAFE_N H≥2,7 V (nominalnie ok. 2,94 V za R40 100 Ω), TP7 SAFE_OK H, TP14 SAFE_WD H | NIE ZBADANO |
| E06 | H_MCU włączony: MOTOR_PERMIT nadal L. Nowe naciśnięcie ARM: HW_ARMED i MOTOR H. H_PWM przechodzi tylko gdy MOTOR H | NIE ZBADANO |
| E07 | Wyłączyć H_MCU: MOTOR/PWM L, HW_ARMED może pozostać H. Włączyć H_MCU: MOTOR wraca bez nowego ARM — oczekiwane, żądanie MCU nie kasuje zatrzasku | NIE ZBADANO |
| E08 | Przy wszystkich zgodach, ale HW_ARMED=0: H_SENSOR daje SENSOR_PERMIT H; silnik L. Wyłączenie H_SENSOR kasuje tylko zezwolenie czujnika | NIE ZBADANO |
| E09 | Wyłączyć osobno każde READY, CORE_LINK, PG_LINK, TEST_KEY, MECH_OK. Za każdym razem HW_ARMED/MOTOR/SENSOR/PWM L. Powrót nie uzbraja silnika sam | NIE ZBADANO |
| E10 | Otworzyć STOP, potem zewrzeć SAFE_N z GND przez testowy styk. Osobne przebiegi; MOTOR/SENSOR L. Zmierzyć opóźnienia, cel reakcji tych torów <10 ms | NIE ZBADANO |
| E11 | HB RUN→stałe L, odpięcie przewodu, oraz RUN→stałe H. Mierzyć od ostatniego zbocza do WD_Q=L i MOTOR=L: 50–150 ms przy 3,3 V. TP14 SAFE_WD spada razem z WD_Q | NIE ZBADANO |
| E12 | SUP_N stale L: watchdog skasowany mimo HB. Przywrócić SUP_N: heartbeat może odtworzyć WD_Q, ale silnik wymaga nowego ARM. Zanik SAFE_N nie blokuje ponownego startu watchdoga | NIE ZBADANO |
| E13 | Start z HB stale H: sprawdzić pojedynczy impuls po zwolnieniu CLR, po 200 ms WD_Q ma być L. Ten układ nie kwalifikuje kilku okresów przed pierwszym impulsem | NIE ZBADANO |
| E14 | ARM przytrzymany przed włączeniem oraz przez każdy błąd i jego ustąpienie: brak samoczynnego ponownego ARM. Zwolnić i nacisnąć ponownie, wtedy zgoda | NIE ZBADANO |
| E15 | 50 naciśnięć i zwolnień właściwego przycisku; obserwować ARM_BUTTON_N i ARM_CLK. Stan L na ARM_BUTTON_N nominalnie 0,30 V. Brak przypadkowego dodatniego zbocza po zwolnieniu/odtworzeniu resetu | NIE ZBADANO |
| E16 | Wolne zmiany VDD i krótkie zapady; osobno reset lokalny i SUP_N. Sprawdzić 3,10/3,20/3,30/3,465 V, jeżeli próg egzemplarza pozwala. Zapisać wartości, nie obchodzić resetu | NIE ZBADANO |
| E17 | Wyłączyć P04 przy aktywnym źródle P00 3,3 V na wejściach przez 1 kΩ. Zmierzyć napięcie szyny P04 i prądy; brak zasilania P04 z wejść i brak zgód | NIE ZBADANO |
| E18 | Wyjęcie każdego adaptera po wyłączeniu: po ponownym zasileniu odpowiadające sygnały za buforem pozostają L; brak pozornego READY | NIE ZBADANO |
| E19 | PWM z generatora 3,3 V, częstotliwość docelowa CORE: bez przekłamań przy maksymalnej długości wiązki. STOP przy różnych fazach PWM odcina wyjście | NIE ZBADANO |
| E20 | Lokalnie schłodzona/ogrzana P04 w przewidzianym zakresie kabiny; ponowić E05/E11/E15. Nie używać temperatury zaworu jako temperatury otoczenia PCB | NIE ZBADANO |
| E21 | Druga droga watchdoga (R4-02). Stan jak w E06 (ARM, MOTOR H). Zewrzeć TP15 (baza Q1) z GND, np. z emiterem Q1 (pin 1) albo TP2. Zatrzymać HB: po 50–150 ms WD_Q, TP14 SAFE_WD, HW_ARMED, MOTOR, PWM i SENSOR = L, choć TP6 SAFE_N zostaje H. Zdjąć zworę i wznowić HB: bez nowego ARM silnik L | NIE ZBADANO |
| E22 | Ograniczenie prądu wyjść 3,3 V (R4-03), po jednym, krótko, amperomierzem do GND: J8.1 ok. 33 mA (R40 100 Ω), J7.1 ok. 3,3 mA (R39), J7.4 ok. 3,3 mA (R38). TP1 3V3_IO bez zapadu, U11 bez resetu | NIE ZBADANO |
| I01 | Z P01: brak jego ENABLE ściąga SAFE_N. Przy wszystkich modułach podłączonych H SAFE_N≥2,7 V, L≤0,25 V | NIE ZBADANO |
| I02 | Z P03: heartbeat zatrzymuje się po utracie świeżych próbek; tryb/bank/zero z długą przerwą kasuje ARM. Brak zmiany mapy SAFE, napięcia 3,3 V | NIE ZBADANO |
| I03 | Z P11: KEY, oba styki LOGGER i pętla TEST oddzielnie. Obecność dowolnego LOGGER blokuje motor i sensor TEST | NIE ZBADANO |
| I04 | Z P08: zgodna taśma SENSOR6 M2.2, KEY2, 5/6 NC; READY zanim nastąpi permit | NIE ZBADANO |
| I05 | Z P07: dopiero po zamknięciu HOLD BTS7960, stan EN/PWM przy wyłączonej P04, OC, KPWR i lokalny latch. Równolegle sprawdzić stabilne VPROT ≥300 ms przed KPWR wg P01/P02 | NIE ZBADANO |

Pomiary zapisane w: __________________. Odchylenia / wymiana R1 / wariant BOM: __________________.

Najpierw zamknąć recenzję i M01 przed zamówieniem PCB; E01–E22 przed integracją. E11 nie może zostać zaliczony na podstawie równania 0,45RC dla 5 V. Jeśli E15 nie przechodzi, zmienić układ filtru lub typ przycisku przed próbami z mostkiem.

R2.1: E22 nie obejmuje zwierania MOTOR_PERMIT, PWM_OUT, ARM_CLK, HW_ARMED, INTERLOCK ani SENSOR_PERMIT. To wyjścia push-pull bez gwarantowanego zabezpieczenia zwarciowego.

## R2.2 — integracja resetu z P03-R5

- Przed połączeniem potwierdzić R17=10 kΩ; R30 pozostaje 100 kΩ.
- P04 ON/CORE OFF: U9.5 ≤0,8 V, SUP_OK=0, ARM i zgody wyłączone. Powtórzyć obie kolejności zasilania, reset ręczny i DTR/RTS.
- P04 U9.5: oba zbocza przez obszar 0,8–2,0 V zgodne z ≤10 ns/V; pojedyncze monotoniczne przejście. U9.6/SUP_OK bez dodatkowych impulsów. Podać pasmo i pojemność sondy; 10–90% samo nie jest kryterium zgodności.
- Po zwolnieniu resetu wymagane ponowne ARM. Wyniki: NIE ZBADANO.
