# P04-R1 — formularz odbioru etapowego

Operator / data / numer PCB / MPN i partia U1/U11: __________________________

Wynik początkowy każdej pozycji: **NIE ZBADANO**. Najpierw sama P04 z P00; bez silnika, EGR, ECU i P07. Oscyloskop/analizator z masą wspólną i sondami o dużej impedancji. Zapisywać przebiegi, nie tylko PASS.

| ID | Czynność i wymagany wynik | Pomiar / wynik |
|---|---|---|
| M01 | Przymiarka 100%, kołki/otwory/klucze złączy, numeracja adapterów, kotwy | NIE ZBADANO |
| M02 | Ciągłość każdej żyły; brak zwarć sąsiadów, klucze NC. Powtórzyć po poruszeniu wiązką | NIE ZBADANO |
| E01 | Bez U1–U10: zasilanie 3,3 V limit 50 mA na J1.3/GND. Sprawdzić C3 i pinout U11 | NIE ZBADANO |
| E02 | Powolny wzrost/spadek VDD: RESET U11, próg 3,00–3,15 V, zwolnienie ≥150 ms. Zmierzyć histerezę | NIE ZBADANO |
| E03 | Włożyć układy przy wyłączonym zasilaniu. Przy 3,30 V i wszystkich wejściach L: MOTOR/SENSOR/PWM/HW_ARMED L, LED świeci. Zapisać prąd | NIE ZBADANO |
| E04 | Każdy z 11 buforów: H/L/odpięcie, odczyt przed i za buforem. Po odpięciu oba punkty L | NIE ZBADANO |
| E05 | Wszystkie READY, TEST_KEY i MECH_OK H, SUP_N H, STOP zamknięty, HB ok.100 Hz. TP10 INTERLOCK H, TP5 WD_Q H, TP6 SAFE_N H≥2,7 V, TP7 SAFE_OK H | NIE ZBADANO |
| E06 | H_MCU włączony: MOTOR_PERMIT nadal L. Nowe naciśnięcie ARM: HW_ARMED i MOTOR H. H_PWM przechodzi tylko gdy MOTOR H | NIE ZBADANO |
| E07 | Wyłączyć H_MCU: MOTOR/PWM L, HW_ARMED może pozostać H. Włączyć H_MCU: MOTOR wraca bez nowego ARM — oczekiwane, żądanie MCU nie kasuje zatrzasku | NIE ZBADANO |
| E08 | Przy wszystkich zgodach, ale HW_ARMED=0: H_SENSOR daje SENSOR_PERMIT H; silnik L. Wyłączenie H_SENSOR kasuje tylko zezwolenie czujnika | NIE ZBADANO |
| E09 | Wyłączyć osobno każde READY, CORE_LINK, PG_LINK, TEST_KEY, MECH_OK. Za każdym razem HW_ARMED/MOTOR/SENSOR/PWM L. Powrót nie uzbraja silnika sam | NIE ZBADANO |
| E10 | Otworzyć STOP, potem zewrzeć SAFE_N z GND przez testowy styk. Osobne przebiegi; MOTOR/SENSOR L. Zmierzyć opóźnienia, cel reakcji tych torów <10 ms | NIE ZBADANO |
| E11 | HB RUN→stałe L, odpięcie przewodu, oraz RUN→stałe H. Mierzyć od ostatniego zbocza do WD_Q=L i MOTOR=L: 50–150 ms przy 3,3 V | NIE ZBADANO |
| E12 | SUP_N stale L: watchdog skasowany mimo HB. Przywrócić SUP_N: heartbeat może odtworzyć WD_Q, ale silnik wymaga nowego ARM. Zanik SAFE_N nie blokuje ponownego startu watchdoga | NIE ZBADANO |
| E13 | Start z HB stale H: sprawdzić pojedynczy impuls po zwolnieniu CLR, po 200 ms WD_Q ma być L. Ten układ nie kwalifikuje kilku okresów przed pierwszym impulsem | NIE ZBADANO |
| E14 | ARM przytrzymany przed włączeniem oraz przez każdy błąd i jego ustąpienie: brak samoczynnego ponownego ARM. Zwolnić i nacisnąć ponownie, wtedy zgoda | NIE ZBADANO |
| E15 | 50 naciśnięć i zwolnień właściwego przycisku; obserwować ARM_BUTTON_N i ARM_CLK. Stan L na ARM_BUTTON_N nominalnie 0,30 V. Brak przypadkowego dodatniego zbocza po zwolnieniu/odtworzeniu resetu | NIE ZBADANO |
| E16 | Wolne zmiany VDD i krótkie zapady; osobno reset lokalny i SUP_N. Sprawdzić 3,20/3,30/3,465 V, jeżeli próg egzemplarza pozwala. Zapisać wartości, nie obchodzić resetu | NIE ZBADANO |
| E17 | Wyłączyć P04 przy aktywnym źródle P00 3,3 V na wejściach przez 1 kΩ. Zmierzyć napięcie szyny P04 i prądy; brak zasilania P04 z wejść i brak zgód | NIE ZBADANO |
| E18 | Wyjęcie każdego adaptera po wyłączeniu: po ponownym zasileniu odpowiadające sygnały za buforem pozostają L; brak pozornego READY | NIE ZBADANO |
| E19 | PWM z generatora 3,3 V, częstotliwość docelowa CORE: bez przekłamań przy maksymalnej długości wiązki. STOP przy różnych fazach PWM odcina wyjście | NIE ZBADANO |
| E20 | Lokalnie schłodzona/ogrzana P04 w przewidzianym zakresie kabiny; ponowić E05/E11/E15. Nie używać temperatury zaworu jako temperatury otoczenia PCB | NIE ZBADANO |
| I01 | Z P01: brak jego ENABLE ściąga SAFE_N. Przy wszystkich modułach podłączonych H SAFE_N≥2,7 V, L≤0,25 V | NIE ZBADANO |
| I02 | Z P03: heartbeat zatrzymuje się po utracie świeżych próbek; tryb/bank/zero z długą przerwą kasuje ARM. Brak zmiany mapy SAFE, napięcia 3,3 V | NIE ZBADANO |
| I03 | Z P11: KEY, oba styki LOGGER i pętla TEST oddzielnie. Obecność dowolnego LOGGER blokuje motor i sensor TEST | NIE ZBADANO |
| I04 | Z P08: zgodna taśma SENSOR6 M2.2, KEY2, 5/6 NC; READY zanim nastąpi permit | NIE ZBADANO |
| I05 | Z P07: dopiero po zamknięciu HOLD BTS7960, stan EN/PWM przy wyłączonej P04, OC, KPWR i lokalny latch. Równolegle sprawdzić stabilne VPROT ≥300 ms przed KPWR wg P01/P02 | NIE ZBADANO |

Pomiary zapisane w: __________________. Odchylenia / wymiana R1 / wariant BOM: __________________.

Najpierw zamknąć recenzję i M01 przed zamówieniem PCB; E01–E20 przed integracją. E11 nie może zostać zaliczony na podstawie równania 0,45RC dla 5 V. Jeśli E15 nie przechodzi, zmienić układ filtru lub typ przycisku przed próbami z mostkiem.
