# Odbiór P06-R1 - NIE WYKONANO

Egzemplarz: ______  Data: ______  Osoba: ______  Przyrządy / kalibracja: ______

W każdej pozycji zapisać wynik, warunki, zdjęcie/oscylogram oraz PASS/FAIL. Puste pole oznacza NIE ZBADANO. Najpierw stanowisko bez samochodu. W razie FAIL zatrzymać etap zależny, poprawić przyczynę i powtórzyć odpowiednią część odbioru.

| ID | Próba / kryterium | Wynik |
|---|---|---|
| M01 | Wydruk 1:1: belka 100 mm, PBV, PTH, TO92, elektrolity, przewód 2,5 mm², kotwy, wysokość i SW1. | NIE ZBADANO |
| E01 | Przed montażem IC: brak zwarcia ECU/EGR do GND; zgodna numeracja siłowa i Kelvin. Nie mierzyć 5 mΩ zwykłym omomierzem jako testu tolerancji. | NIE ZBADANO |
| E02 | Stale obecny tor przez bocznik przy wyłączonej elektronice; BYPASS zwiera równolegle, przejście dźwigni nie przerywa toru. | NIE ZBADANO |
| E03 | Osobno omomierz SW1: 2-3/5-6 w BYPASS; 2-1/5-4 w MEASURE. Brak połączeń między biegunami. | NIE ZBADANO |
| E04 | Pierwsze 5 V z limitem 30 mA w BYPASS. 5VA, 3V3_P06, VREF, REF_BUF. VREF 2,475-2,525 V przed kalibracją. | NIE ZBADANO |
| E05 | MEASURE z limitem 250 mA: pobór <180 mA przy 4,75/5,00/5,25 V; pomiar temperatury R21 i R6. | NIE ZBADANO |
| E06 | Minimum zasilania i rozgrzanie: READY pewnie wraca, brak oscylacji resetu. Zmierzyć progi narastania/opadania obu supervisorów. Nie traktować 50 mV histerezy jako gwarantowanego maksimum. | NIE ZBADANO |
| E07 | READY LOW w BYPASS, przy odpiętym styku pomocniczym, zablokowanym SUP3_N i SUP5_RAW. Sprawdzić po kolei każdy warunek. | NIE ZBADANO |
| E08 | P06 wyłączony, CORE włączony: SCLK/CS na 0 i 3,3 V, brak zasilania fantomowego; lokalne 3V3 <0,1 V. CORE wyłączony, P06 włączony: CS_LOCAL_N=H, DOUTA high-Z. | NIE ZBADANO |
| E09 | Start i odłączenie 5 V: oscylogramy 5VA, 3V3, REF25/REF_BUF. Brak nadmiernego prądu zwrotnego i przekroczeń napięć wejściowych według kart IC. | NIE ZBADANO |
| E10 | SPI z P03 bez silnika: stały kod około 2048, brak zamiany bitów, 16 taktów i CS. Jeden kanał steruje DOUTA naraz również z P05. | NIE ZBADANO |
| E11 | ZERO po 1 s przy zerowym prądzie; zapisać kod, szum RMS/p-p przez 10 s, VREF i temperaturę. Cel po kalibracji: offset <20 mA, szum RMS <10 mA na spokojnym stanowisku. | NIE ZBADANO |
| E12 | Zewnętrzne źródło prądu + obciążenie przez J3, najpierw ±1 A, potem ±3 A. Odwracać przewody przy wyłączonym źródle; nie odwracać zasilania logicznego. Prąd kontrolowany niezależnym miernikiem. | NIE ZBADANO |
| E13 | Dopasować offset/gain; punkty ±0,5/1/3/6 A. Cel reszty po kalibracji: <=max(30 mA,1% wskazania), przy 4,75/5,25 V i po rozgrzaniu. ±6 A do zatwierdzenia, nie wynik zadeklarowany z góry. | NIE ZBADANO |
| E14 | BYPASS przy ustalonym prądzie próbnym na stanowisku: spadek na torze maleje, READY LOW, eksport nie publikuje ważnych amperów. Operację na stanowisku odróżnić od reguły wyłączonego zapłonu w aucie. | NIE ZBADANO |
| E15 | Bierny tor 10 A: najpierw 30 s, potem 10 min. Zmierzyć spadki na boczniku, PCB i wiązkach oraz temperatury; cel wzrostu temperatury PCB/połączeń <30°C, brak zapachu/odbarwienia i stabilny spadek. Nie wymagać ważnego ADC przy 10 A. | NIE ZBADANO |
| E16 | PWM ze stanowiska: porównać średni prąd i skok obciążenia z sondą/oscyloskopem, kilka częstotliwości i współczynników. Zmierzyć tłumienie aliasów i opóźnienie. | NIE ZBADANO |
| E17 | Prąd i napięcie wspólne: powtórzyć testy przy CM blisko 0 V oraz około 12-15 V bez przekraczania zakresów układów. Układ nieizolowany - kontrolować połączenie mas przyrządów. | NIE ZBADANO |
| E18 | Rozgrzanie elektroniki P06 w realistycznym zakresie pracy kabinowej i powrót do zimnego: offset/gain/reset, powtórka E11/E13. Nie ogrzewać tej PCB tak jak zaworu EGR w komorze. | NIE ZBADANO |
| E19 | Kompletny P02 + moduły: pobór z VLOG_RES <=6 W, jeśli oczekiwane HOLD 50 ms; potwierdzić czas podtrzymania i unieważnienie prądu po zaniku READY. | NIE ZBADANO |
| E20 | Po zaliczeniu stanowiska: wpięcie do auta bez błędów od interfejsu, przebieg napięć/current zgodny z pomiarem odniesienia; potem sesje zimny/gorący i 1500-1700 rpm. | NIE ZBADANO |

Kolejność odbioru bloków (montaż fizyczny według PDF PCB): mechanika i RSH1 → tor mocy/SW1 → R6/U4/C3/C4/D1 → U10/C5/D2 → U1/U2 → U3/U5 → U6/U7/U8/U9 → wiązki do CORE → całość. Nie uznawać zerowego ERC/DRC za zaliczenie którejkolwiek pozycji tej tabeli.

