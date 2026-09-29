# Odbiór P10-R2 — do wypełnienia na stanowisku

Egzemplarz PCB: ____ data: ____ wykonawca: ____ wersja firmware: ____
Przyrządy i wzorcowy interfejs CAN: ____ kabel W3 / rzeczywista długość: ____

Wszystkie statusy poniżej **NIE ZBADANO**. PASS wpisuje wykonawca po pomiarze.

Punkty pomiarowe są na **listwie serwisowej J2** (krawędź B, dostępna po skręceniu stosu; kołki przez rezystory 1 kΩ, a CAN_H/CAN_L przez 10 kΩ). Numeracja od strony mniejszego x: 1 GND, 2 5V_SYS, 3 3V3_IO, 4 RX_RAW, 5 CAN_RX, 6 CAN_TX, 7 CAN_H, 8 CAN_L, 9 GND. Przebiegi CAN o pełnej wierności mierzyć na J3 (kabel W3), nie na kołkach 7/8 (10 kΩ i pojemność sondy dają ok. 150 ns).

| Próba | Kołek J2 / kryterium / pomiar do zapisania | Wynik / załącznik |
|---|---|---|
| Przymiarka 1:1 | Obrys 53 × 100 mm, otwory M3 slotu, J_BP przy krawędzi A, listwa przy B, kotwa J3 | NIE ZBADANO |
| Oględziny | Poprawne MPN V/AD, pin 1 U1/U2, D1 wspólny 3; brak mostków | NIE ZBADANO |
| J_BP i wiązka | Piny nieparzyste GND, parzyste wg `docs/J_BP.csv`; W3 H → 6, L → 14, inne piny OBD NC | NIE ZBADANO |
| Listwa J2 | Rezystancja kołek–węzeł: 1 kΩ (kołki 2–6), 10 kΩ (7, 8); kołki 1 i 9 = GND | NIE ZBADANO |
| Zimna płytka | Kołki 2, 3 względem GND, kołki 7, 8 (H/L) w obu polaryzacjach; brak 120 Ω | NIE ZBADANO |
| Pierwsze zasilanie | Kołki 2 (5 V) i 3 (3,3 V), ograniczenie 20 mA/szynę, brak grzania | NIE ZBADANO |
| Pobór | Spoczynek i odbiór, oba prądy; porównać z rezerwą 10 mA/szynę | NIE ZBADANO |
| Stały silent | U1.8 = VIO, U1.1 = VIO; kołek 6 (CAN_TX) bez połączenia z U1 (pomiar rezystancji) | NIE ZBADANO |
| RX | Znana sekwencja 11/29 bit, DLC 0–8; kołek 4 → kołek 5 → GPIO18 zgodność | NIE ZBADANO |
| Brak TX | CAN_TX (kołek 6) = LOW/HIGH/PWM; H/L bez dominacji od P10; nie podawać sygnału na hardwired S/TXD | NIE ZBADANO |
| Brak ACK | Generator + P10 bez drugiego węzła: brak ACK; po dołączeniu aktywnego węzła poprawne ramki | NIE ZBADANO |
| Zanik 5 V | Przy 3,3 V aktywnym: brak zakłócania CAN, stan RX i odzysk odbioru | NIE ZBADANO |
| Zanik 3,3 V | Przy 5 V aktywnym i CORE na USB: szyna P10 nie rośnie od RX (kołek 3); H/L pasywne | NIE ZBADANO |
| P10 off / CORE USB | Prądy i poziomy obu martwych szyn, RX; zgodne z limitami Ioff/pull-up | NIE ZBADANO |
| CORE off / P10 on | Brak podnoszenia 3V3_CORE przez sygnały (U11 P03 z Ioff); RX/rozruch | NIE ZBADANO |
| Rampy/brownout | Powolne i szybkie zmiany każdej szyny; H/L, RX, czas odtworzenia odbioru | NIE ZBADANO |
| Wpływ odczepu | Przebieg CAN przed/po P10, długość 300 mm, napięcie wspólne, brak dodatkowych błędów | NIE ZBADANO |
| Wpływ kołków CAN_H/CAN_L | Przebieg CAN i liczba błędów z kołkami 7/8 wolnymi oraz z podłączoną sondą | NIE ZBADANO |
| Ruch ciągły | 10 min z sekwencją i licznikiem; liczba ramek w loggerze i wzorcu identyczna w zakwalifikowanym zakresie | NIE ZBADANO |
| SD + DAQ + TEMP | Największy docelowy ruch CAN, straty/kolejki jawnie liczone; zmierzone opóźnienie do DAQ | NIE ZBADANO |
| RPM | Potwierdzone źródło/ID ECU/dekoder; porównanie w 1500–1700 rpm; brak danych ≠ 0 rpm | NIE ZBADANO |
| Samochód/postój | Masa podłączona wcześniej, poprawny bitrate, odbiór bez dodatkowych błędów samochodu | NIE ZBADANO |

Próby generatora wykonywać poza samochodem. Magistrala stanowiskowa: dwa terminatory 120 Ω, dwa aktywne węzły z ACK i P10 jako odbiornik. Podczas próby braku ACK celowo odłączyć aktywnego odbiorcę; nie interpretować retransmisji generatora jako wielu niezależnych zdarzeń pojazdu. Nie wstrzykiwać wysokich przepięć bez odpowiedniego stanowiska; formalnej kwalifikacji EMC ten formularz nie zastępuje.
Decyzja odbioru: ____ otwarte niezgodności: ____
