# Odbiór P06-R2 — NIE WYKONANO

*R2 (1.10.2026, format S1): pomiary na kołkach listew serwisowych J_SV1/J_SV2 (krawędź B) zamiast na polach TP1–TP15; zasilanie i SPI przez J_BP (IDC 2×8) zamiast wiązek LV06/ILOG; bocznik SMD 2512 Kelvin; przełącznik BYPASS na panelu (ogólny DPDT ON-ON); C3 220 µF. Kryteria liczbowe R1 bez zmian poza E01 (bocznik SMD), E05 (budżet z R21 PR02) i E19 (P02 R4 zamiast HOLD z P02 R3).*

Egzemplarz: ______  Data: ______  Osoba: ______  Przyrządy / kalibracja: ______

W każdej pozycji zapisać wynik, warunki, zdjęcie/oscylogram oraz PASS/FAIL. Puste pole oznacza NIE ZBADANO. Najpierw stanowisko bez samochodu. W razie FAIL zatrzymać etap zależny, poprawić przyczynę i powtórzyć odpowiednią część odbioru.

**Jak mierzyć na listwach.** Każdy kołek poza GND idzie przez rezystor przy węźle: 1 kΩ dla szyn i logiki, 10 kΩ dla węzłów analogowych (I_L_OUT, ADC_AIN, REF_BUF, REF25) i SUP3_N/SUP5_N. Multimetr 10 MΩ mierzy przez 10 kΩ z błędem ok. 0,1 % — **VREF (REF25) w E04 mierzyć miernikiem o rezystancji wejściowej ≥ 1 GΩ albo na węźle (C5/U10.2) przed skręceniem stosu**; to samo dla REF_BUF, jeśli wynik ma rozstrzygać o kalibracji. Sonda oscyloskopu ok. 15 pF daje ok. 15 ns (1 kΩ) albo 150 ns (10 kΩ). Prądu przez kołek nie mierzyć. Masa sondy: piny 1, 4, 7 J_SV1 albo 1, 5, 13 J_SV2. Numeracja zawsze od pinu 1; kątowa listwa widziana z góry ma pin 1 przy **większym** x — sprawdzić z nadrukiem.

| Kołek | Sieć | Kołek | Sieć |
|---|---|---|---|
| J_SV1.2 | I_L_OUT (10k) | J_SV2.2 | 5V_SYS |
| J_SV1.3 | ADC_AIN (10k) | J_SV2.3 | 5VA_P06 (za R6) |
| J_SV1.5 | REF_BUF (10k) | J_SV2.4 | 3V3_P06 |
| J_SV1.6 | REF25 (10k) | J_SV2.6 | 3V3_IO |
| J_SV1.1/4/7 | GND | J_SV2.7 | SUP3_N (10k) |
| | | J_SV2.8 | SUP5_N (10k) |
| | | J_SV2.9 | SHUNT_ENABLED |
| | | J_SV2.10 | LOGGER_CURRENT_OK |
| | | J_SV2.11 | CS_LOCAL_N |
| | | J_SV2.12 | CLK_LOCAL |
| | | J_SV2.1/5/13 | GND |

Pełna tabela z rezystorami: `SERWIS.csv`.

**Stanowisko.** Zasilanie 5 V wpinać na J_BP (piny 10/12 = 5V_SYS, nieparzyste = GND; pin 14 = 3V3_IO tylko dla E08) przez taśmę IDC 2×8 albo przejściówkę. SPI z P03 przez P12 albo bezpośrednią taśmą: ADC_SCLK 2, ADC_DOUTA 4, CS_ILOG_N 6, LOGGER_CURRENT_OK 8. Bez P03 stany wejść ustalają rezystory domyślne (CS_ILOG_N = H przez R8 100k, ADC_SCLK = L przez R10 100k).

| ID | Próba / kryterium | Wynik |
|---|---|---|
| M01 | Wydruk 1:1 (z sesji lokalnej): belka 100 mm, RSH1 2512 na polach Kelvina, pigtaile J3/J4/J5 z przewodem 2,5 mm² w otworze 2,4 mm i kotwami, J_BP przy krawędzi A, listwy przy krawędzi B, R21 PR02, C3, wysokość ≤ 16,5 mm od góry i ≤ 1,5 mm od spodu (poziom 4), przełącznik BYPASS w panelu. | NIE ZBADANO |
| E01 | Przed montażem IC: brak zwarcia ECU/EGR do GND; J3.1 → pole prądowe RSH1.1, J3.2 → RSH1.4; K_PLUS (RSH1.2) → R1, K_MINUS (RSH1.3) → R2. Nie mierzyć 5 mΩ zwykłym omomierzem jako testu tolerancji (pomiar 4-przewodowy albo spadek przy znanym prądzie). | NIE ZBADANO |
| E02 | Stale obecny tor przez bocznik przy wyłączonej elektronice; BYPASS zwiera równolegle, przejście dźwigni nie przerywa toru. | NIE ZBADANO |
| E03 | Osobno omomierz SW1 przed lutowaniem wiązek: wspólne oczka, potem BYPASS = 2-3 / 5-6, MEASURE = 2-1 / 5-4 w numeracji schematu; brak połączeń między biegunami. Numery oczek konkretnego przełącznika przypisać według pomiaru, nie według katalogu. | NIE ZBADANO |
| E04 | Pierwsze 5 V z limitem 30 mA w BYPASS. Na kołkach: 5V_SYS, 5VA_P06, 3V3_P06, REF_BUF; REF25 przez ≥ 1 GΩ albo na węźle. VREF 2,475–2,525 V przed kalibracją. | NIE ZBADANO |
| E05 | MEASURE z limitem 250 mA: pobór < 180 mA przy 4,75/5,00/5,25 V na J_BP; temperatura R21 (PR02, 0,71 W przy 5,25 V), R6 i otoczenia RSH1/U1. | NIE ZBADANO |
| E06 | Minimum zasilania i rozgrzanie: LOGGER_CURRENT_OK (J_SV2.10) pewnie wraca, brak oscylacji SUP3_N/SUP5_N (J_SV2.7/8). Zmierzyć progi narastania/opadania obu nadzorców. Nie traktować 50 mV histerezy jako gwarantowanego minimum. | NIE ZBADANO |
| E07 | LOGGER_CURRENT_OK = L w BYPASS (SHUNT_ENABLED = L na J_SV2.9), przy odpiętym przewodzie J5.2, przy wymuszonym SUP3_N i SUP5_RAW. Sprawdzić po kolei każdy warunek. | NIE ZBADANO |
| E08 | P06 bez 5V_SYS, CORE włączony: ADC_SCLK/CS_ILOG_N na 0 i 3,3 V, brak zasilania fantomowego; 3V3_P06 (J_SV2.4) < 0,1 V. Kołek 3V3_IO (J_SV2.6) pokazuje 3V3_IO z P02. CORE wyłączony, P06 włączony: CS_LOCAL_N (J_SV2.11) = H, ADC_DOUTA high-Z. | NIE ZBADANO |
| E09 | Start i odłączenie 5 V: oscylogramy 5VA_P06, 3V3_P06, REF25/REF_BUF (przez 10 kΩ: stała 150 ns pomijalna). Brak nadmiernego prądu zwrotnego i przekroczeń napięć wejściowych według kart IC. Start z C3 220 µF: prąd szczytowy przez R6 ≤ ok. 5 A, τ ≈ 0,22 ms. | NIE ZBADANO |
| E10 | SPI z P03 bez silnika: stały kod około 2048, brak zamiany bitów, 16 taktów i CS (CLK_LOCAL / CS_LOCAL_N na J_SV2.12/11). Jeden nadajnik steruje ADC_DOUTA naraz również z P05. | NIE ZBADANO |
| E11 | ZERO po 1 s przy zerowym prądzie; zapisać kod, szum RMS/p-p przez 10 s, VREF i temperaturę; I_L_OUT (J_SV1.2) ≈ REF_BUF, ADC_AIN (J_SV1.3) ≈ 1,25 V. Cel po kalibracji: offset < 20 mA, szum RMS < 10 mA na spokojnym stanowisku. | NIE ZBADANO |
| E12 | Zewnętrzne źródło prądu + obciążenie przez J3, najpierw ±1 A, potem ±3 A. Odwracać przewody przy wyłączonym źródle; nie odwracać zasilania logicznego. Prąd kontrolowany niezależnym miernikiem. | NIE ZBADANO |
| E13 | Dopasować offset/gain; punkty ±0,5/1/3/6 A. Cel reszty po kalibracji: ≤ max(30 mA, 1 % wskazania), przy 4,75/5,25 V i po rozgrzaniu. ±6 A do zatwierdzenia, nie wynik zadeklarowany z góry. | NIE ZBADANO |
| E14 | BYPASS przy ustalonym prądzie próbnym na stanowisku: spadek na torze maleje, LOGGER_CURRENT_OK = L, eksport nie publikuje ważnych amperów. Operację na stanowisku odróżnić od reguły wyłączonego zapłonu w aucie. | NIE ZBADANO |
| E15 | Bierny tor 10 A: najpierw 30 s, potem 10 min. Zmierzyć spadki na boczniku, PCB i wiązkach oraz temperatury; cel wzrostu temperatury PCB/połączeń < 30 °C, brak zapachu/odbarwienia i stabilny spadek. **Miedź 35 µm (R1: 70 µm): pola toru i lut RSH1 obserwować kamerą termowizyjną albo termoparą.** Nie wymagać ważnego ADC przy 10 A. | NIE ZBADANO |
| E16 | PWM ze stanowiska: porównać średni prąd i skok obciążenia z sondą/oscyloskopem, kilka częstotliwości i współczynników. Zmierzyć tłumienie aliasów i opóźnienie (C1 X7R: zmierzyć rzeczywiste τ). | NIE ZBADANO |
| E17 | Prąd i napięcie wspólne: powtórzyć testy przy CM blisko 0 V oraz około 12–15 V bez przekraczania zakresów układów. Układ nieizolowany — kontrolować połączenie mas przyrządów. | NIE ZBADANO |
| E18 | Rozgrzanie elektroniki P06 w realistycznym zakresie pracy kabinowej i powrót do zimnego: offset/gain/reset, powtórka E11/E13. Nie ogrzewać tej PCB tak jak zaworu EGR w komorze. | NIE ZBADANO |
| E19 | Kompletny LOGGER (P02 R4 + P03 + P05 + P06 + P09 + P10): start z łączną pojemnością 5V_SYS ok. 486 µF wobec 600 µF TSR 2-2450 (bez foldbacku), pobór P06 w budżecie 5V_SYS; po PFAIL_N z P02 R4 unieważnienie prądu przed zanikiem READY. | NIE ZBADANO |
| E20 | Po zaliczeniu stanowiska: wpięcie do auta bez błędów od interfejsu, przebieg napięć/prądu zgodny z pomiarem odniesienia; potem sesje zimny/gorący i 1500–1700 rpm. | NIE ZBADANO |

Kolejność odbioru bloków (montaż według PDF PCB z sesji lokalnej): mechanika i RSH1 → tor mocy/SW1 → R6/U4/C3/C4/D1 → U10/C5/D2 → U1/U2 → U3/U5 → U6/U7/U8/U9 → rezystory i listwy serwisowe → J_BP i taśma do P12 → całość. Nie uznawać zerowego ERC/DRC ani kontroli plików za zaliczenie którejkolwiek pozycji tej tabeli.
