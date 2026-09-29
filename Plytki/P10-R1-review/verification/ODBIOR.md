# Odbiór P10-R1 — do wypełnienia na stanowisku

EgzemplarzPCB: ____ data: ____ wykonawca: ____ wersja firmware: ____
Przyrządy i wzorcowy interfejsCAN: ____  kabelW3/rzeczywista długość: ____

Wszystkie statusy poniżej **NIE ZBADANO**. PASS wpisuje wykonawca po pomiarze.

| Próba | Kryterium / pomiar do zapisania | Wynik / załącznik |
|---|---|---|
| Przymiarka1:1 | Obrys80×70, M3, trzy kotwy i miejsce na łuki przewodów | NIE ZBADANO |
| Oględziny | Poprawne MPN V/AD, pin1U1/U2, D1 wspólny3; brak mostków | NIE ZBADANO |
| Wiązki | W1 1:1, W2 KEY4 i izolacja4/5/6, W3 H→6,L→14; inneOBD NC | NIE ZBADANO |
| Zimna płytka | Rezystancje szyn/GND i H/L w obu polaryzacjach; brak120 Ω | NIE ZBADANO |
| Pierwsze zasilanie |5 V i3,3 V, ograniczenie20 mA/szynę, brak grzania | NIE ZBADANO |
| Pobór | Spoczynek i odbiór, oba prądy; porównać z rezerwą10 mA/szynę | NIE ZBADANO |
| Stały silent | U1.8=VIO, U1.1=VIO; brak połączenia z J2.1 | NIE ZBADANO |
| RX | Znana sekwencja11/29bit,DLC0–8; TP4→TP5→GPIO18 zgodność | NIE ZBADANO |
| Brak TX | CAN_TX=LOW/HIGH/PWM; H/L bez dominacji od P10; nie podawać sygnału na hardwired S/TXD | NIE ZBADANO |
| Brak ACK | Generator+P10 bez drugiego węzła: brakACK; po dołączeniu aktywnego węzła poprawne ramki | NIE ZBADANO |
| Zanik5 V | Przy3,3 V aktywnym: brak zakłócaniaCAN, stanRX i odzysk odbioru | NIE ZBADANO |
| Zanik3,3 V | Przy5 V aktywnym i COREnaUSB: szynaP10 nie rośnie odRX; H/L pasywne | NIE ZBADANO |
| P10 off / CORE USB | Prądy i poziomy obu martwych szyn, RX; zgodne z limitamiIoff/pullup | NIE ZBADANO |
| CORE off / P10 on | Brak podnoszenia3V3_CORE przez sygnały (U11P03 zIoff); RX/rozruch | NIE ZBADANO |
| Rampy/brownout | Powolne i szybkie zmiany każdej szyny; H/L,RX,czas odtworzenia odbioru | NIE ZBADANO |
| Wpływ odczepu | PrzebiegCAN przed/po P10, długość300 mm, napięcie wspólne, brak dodatkowych błędów | NIE ZBADANO |
| Ruch ciągły |10 min z sekwencją i licznikiem; liczba ramek w loggerze i wzorcu identyczna w zakwalifikowanym zakresie | NIE ZBADANO |
| SD+DAQ+TEMP | Największy docelowy ruchCAN, straty/kolejki jawnie liczone; zmierzone opóźnienie doDAQ | NIE ZBADANO |
| RPM | Potwierdzone źródło/IDECU/dekoder; porównanie w1500–1700rpm; brak danych≠0rpm | NIE ZBADANO |
| Samochód/postój | Masa podłączona wcześniej, poprawny bitrate, odbiór bez dodatkowych błędów samochodu | NIE ZBADANO |

Próby generatora wykonywać poza samochodem. Magistrala stanowiskowa: dwa terminatory120 Ω,
dwa aktywne węzły z ACK i P10 jako odbiornik. Podczas próby brakuACK celowo odłączyć aktywnego
odbiorcę; nie interpretować retransmisji generatora jako wielu niezależnych zdarzeń pojazdu.
Nie wstrzykiwać wysokich przepięć bez odpowiedniego stanowiska; formalnej kwalifikacji EMC
ten formularz nie zastępuje. Decyzja odbioru: ____ otwarte niezgodności: ____
