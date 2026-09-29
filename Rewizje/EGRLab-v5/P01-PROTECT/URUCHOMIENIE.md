# Odbiór prototypu PWR-THT v1

Pierwsze próby wykonaj bez ESP32, ADC, ECU i zaworu, z zasilaczem laboratoryjnym ograniczającym prąd. Potrzebne: multimetr, oscyloskop, obciążenie rezystancyjne/elektroniczne i pomiar temperatury. Wszystkie pomiary poniżej są **do wykonania**, nie są wynikami testów.

Masy zwykłych sond oscyloskopowych podłączaj wyłącznie do GND. VGS i VDS mierz sondą różnicową albo różnicą dwóch kanałów z obiema masami na GND. Nie zwieraj źródła MOSFET-a do przewodu ochronnego oscyloskopu i nie odłączaj PE oscyloskopu.

## 1. Kontrola bez zasilania

Sprawdź pełną netlistę, polaryzację D2/D3/D4/D5/D6, elektrolitów oraz E-B-C Q2...Q8. U1: 1=OUT, 2=GND, 3=IN. U3 TI LP: 1=K, 2=A, 3=REF; 1 i 3 są zwarte. U4 musi mieć bondout **D**. Odmienne oznaczenie MCP120 oznacza możliwość innej kolejności wyprowadzeń.

Q1: G-D-S od lewej przy widoku na oznaczenie, nóżki w dół; tab=D=VPROT. D2: A1-K-A2, tab=K=VS. Sprawdź izolację radiatorów oraz brak zwarcia VS-VPROT. Ustaw RV1 na **0 Ω między (1+2) a 3**, co daje zachowawczo obniżony próg OVP. Nie ustawiaj położenia na podstawie kierunku obrotu śruby.

## 2. Zasilanie i blokada

Zewrzyj J3. Podaj 13,8 V z limitem 100 mA. Na AUX5 powinno być 4,85-5,15 V, REF około 2,495 V. Sprawdź oscyloskopem stabilność AUX5 i REF. |VGS| powinno być poniżej 0,5 V, LED zgaszona; VPROT może chwilowo zawierać ładunek kondensatora, po ustaleniu z obciążeniem 1 kΩ powinno być poniżej 0,5 V.

Brak oscylacji i poprawne napięcie statyczne są oddzielnymi warunkami. Jeżeli U1 oscyluje, sprawdź ESR C9/R2 oraz połączenia masy, zamiast dodawać przypadkowe kondensatory.

## 3. Start i zanik zasilania sterowania

Usuń zworkę J3. Z obciążeniem 1 kΩ obserwuj AUX5, OK, GATE i VPROT podczas pełnego wyłączenia/włączenia wejścia. Załączenie ma wystąpić po zwolnieniu U4, zwykle około 350 ms; dopuszczalne 150-700 ms plus czas narastania AUX5. Powolny wzrost VIN, szybkie podłączenie 13,8 V oraz start od razu z 24 V nie mogą uruchomić obciążenia w stanie błędu.

Sprawdź również start z 18-24 V: wyjście pozostaje wyłączone. Po powrocie napięcia do okna wraca zasilanie. Opóźnienie U4 dotyczy ponownego pojawienia się prawidłowego AUX5; **nie powtarza się automatycznie po każdym OVP**, jeżeli AUX5 nie zanikło.

Test utraty sterowania: wyłącz wejście, rozładuj kondensatory, odłącz wejście U1 lub R1, następnie podaj 13,8 V z limitem 100 mA. Q1 ma pozostać wyłączony dzięki Q2. Nie wyjmuj elementów pod napięciem.

## 4. Kalibracja OVP i sprawdzenie UVLO

Z obciążeniem 1 kΩ zwiększaj VIN od 14 V, regulując RV1 tak, aby wyłączenie następowało przy **18,00 V ±0,10 V** w temperaturze pokojowej. Przed każdym powtórzeniem obniż VIN poniżej 16 V. Pomiar wykonuj na J1.1 względem J1.2.

Po odcięciu powoli zmniejszaj VIN. Powrót powinien nastąpić około 16,66 V; kryterium pokojowe 16,2-17,2 V. Sprawdź UVLO: nominalnie wyłączenie 9,37 V, ponowne włączenie 9,85 V. Kryteria pokojowe: wyłączenie 9,0-9,8 V, start 9,4-10,3 V, histereza co najmniej 0,25 V. Ustawienia OVP nie używaj do regulacji UVLO.

Powtórz progi przy 0°C i 50°C modułu, bez kondensacji. Projektowy odbiór: OVP 17,4-18,6 V, histereza OVP co najmniej 0,9 V. Wyniki poza zakresem wymagają korekty projektu lub doboru elementów, a nie oznaczenia ich jako zaliczone.

## 5. Sprzętowe rozbrojenie EGRLab

Najpierw sprawdź J4 bez właściwej płyty: zewnętrzne 3,3 V do J4.1, masa do J4.3, testowy pull-up 10 kΩ z J4.2 do 3,3 V. W prawidłowym stanie kolektor ma być rozwarty: na J4.2 około 3,3 V. Zwarcie J3, OVP, UVLO i zanik AUX5 mają obniżyć J4.2 poniżej 0,4 V.

Następnie podłącz J4 do 3V3_IO/SAFE_N/GND_STAR właściwej płyty, **bez dodatkowego pull-up**, przy odłączonym silniku. Sprawdź, że po błędzie HW_ARMED=0 i pozostaje 0 także po powrocie zasilania. Ponowne ARM musi być fizycznym naciśnięciem przycisku. To kryterium obejmuje krótki impuls OVP, podczas którego 3V3_IO nie zanika.

## 6. Obciążenie i nagrzewanie

Z radiatorem i bez silnika zwiększaj obciążenie: 0,1 A, 1 A, 3,5 A, 5 A. Dla 5 A przejdź na właściwy bezpiecznik i limit zasilacza odpowiedni do testu, po wcześniejszym przejściu prób mniejszych prądów. Sprawdź 10,5 V, 13,8 V i 16 V wejścia.

Warunki: |VGS| co najmniej 4,5 V w ustalonym stanie ON, a napięcie na bramce nie przekracza dopuszczalnego VGS. Przy 5 A projektowy gorący spadek VS-VPROT <=0,25 V; D2 sprawdzić osobno. D2 i Q1 obudowa <85°C, oszacowane złącze <110°C. Test do ustalenia temperatury, co najmniej 30 minut przy maksymalnym obciążeniu, również w zamkniętej obudowie i przy otoczeniu 50°C.

Przy zasilaniu 24 V i odciętym wyjściu wykonaj 10-minutową próbę: nie może powrócić VPROT ani wystąpić oscylacja; skontroluj również D5, R1, R23 i U1. Zabezpieczenie nie jest przeznaczone do stałej eksploatacji w instalacji 24 V.

## 7. Załączanie i dynamiczne OVP

Zastąp elektronikę obciążeniem próbnym. Przy otwartym KPWR sprawdź start z sumą pojemności do 220 uF i obciążeniem do 1,5 A. Zmierz prąd szczytowy, przebieg VDS/ID i czas narastania. Cel prądu szczytowego do 5 A dla tego testu; nie jest to działający sprzętowy limit. Porównaj ścieżkę pracy Q1 z jego SOA, również na gorąco. Jeśli prąd lub SOA nie spełnia kryterium, zatrzymaj integrację i zmień układ kształtowania załączenia.

Wykonaj kontrolowane przejście 14 -> 24 V z ograniczoną energią źródła i atrapą obciążenia, zaczynając od małego prądu. Mierz od chwili przekroczenia 18,5 V do |VGS|<0,5 V; cel <=100 us. Obserwuj FAULT_OC i SAFE_N. Nie wolno na tej podstawie deklarować wyników dla innego czasu narastania, impedancji źródła czy temperatury.

Spadek **VPROT do zera** nie jest miarą szybkości odłączenia Q1: kondensatory nadal trzymają energię. Mierz VGS oraz prąd wejściowy. Wyjście przy małym obciążeniu może opadać setki milisekund.

## 8. Odwrotna polaryzacja i prąd wsteczny

Po rozładowaniu wyjścia podaj -14 V przez ograniczenie prądu, potem -24 V. Nie może wzrosnąć VPROT ani AUX5. Nie wykonuj pierwszej próby odwrotności bezpośrednio z akumulatora.

Prąd wsteczny badaj osobnym źródłem 14 V podłączonym do VPROT, ze źródłem wejściowym odłączonym i kontrolowanym obciążeniem po stronie BAT_FUSED. Zmierz przepływ od wyjścia do wejścia i powtórz po rozgrzaniu. Dioda Schottky'ego ma upływ: cel użytkowy <=1 mA przy 25°C i <=5 mA przy temperaturze obudowy D2 85°C wymaga sprawdzenia, nie wynika jako gwarancja z datasheetu dla tych konkretnych warunków. W razie przekroczenia trzeba dobrać diodę o mniejszym upływie lub zaakceptować zmierzony limit w nowej rewizji.

## 9. Impulsy, silnik i zakres zaliczenia

Odbiór impulsowy wymaga generatora o znanym przebiegu, impedancji i energii. Zapisz te parametry, temperaturę oraz wyniki dla VS, VPROT, VGS i SAFE_N. Kryteria projektu: VS<=48 V, VPROT<=32 V, |VGS|<18 V; energia w transilach i punkt pracy Q1 wewnątrz granic producenta z zapasem temperaturowym. Bez tych pomiarów odporność automotive pozostaje niepotwierdzona. Nie wykonuj próby load dump przez odpinanie akumulatora w pracującym samochodzie.

Dopiero po próbach z atrapą podłącz EGR standalone. Sprawdź załączenie KPWR i prąd ładowania C_BULK 1000 uF. Powtórz hamowanie i zmianę kierunku przy największej dopuszczonej energii, monitorując VMOTOR i VPROT. D3 nie zastępuje lokalnego SMCJ18A przy mostku. Regeneracja nie może być odprowadzana do akumulatora przez D2, dlatego lokalne tłumienie pozostaje konieczne.

Odporność na zwarcie nie jest potwierdzona samym F1=5 A. Test zwarcia wykonuje się najpierw z ograniczonym źródłem i po ocenie SOA/I²t bezpiecznika; odcięcie programowe silnika nie jest ochroną przed zwarciem przed mostkiem. Wynik ma być oddzielnie zapisany. Nie zwiększaj F1, żeby ukryć przepalanie przy starcie.

## Protokół

| Próba | Warunki, wynik, data | Zaliczone |
|---|---|---|
| Pinout, izolacja radiatorów | | NIE ZBADANO |
| AUX5/REF stabilność | | NIE ZBADANO |
| Start 0 -> 13,8 V i 0 -> 24 V | | NIE ZBADANO |
| Zanik AUX5 / INHIBIT | | NIE ZBADANO |
| OVP/UVLO w 0/25/50°C | | NIE ZBADANO |
| SAFE_N, krótki błąd i ponowne ARM | | NIE ZBADANO |
| 5 A, temperatura i spadek napięcia | | NIE ZBADANO |
| 24 V przez 10 minut, wyjście OFF | | NIE ZBADANO |
| Start C<=220 uF / I<=1,5 A i SOA | | NIE ZBADANO |
| Czas OVP oraz przepięcie wyjścia | | NIE ZBADANO |
| -14/-24 V, upływ wsteczny | | NIE ZBADANO |
| Impulsy: przebieg, impedancja, energia | | NIE ZBADANO |
| Zwarcie / koordynacja F1 / SOA | | NIE ZBADANO |
| KPWR, silnik, regeneracja | | NIE ZBADANO |

Kopię wypełnionego protokołu dołącz do egzemplarza. „Zaliczone DC” nie oznacza zaliczenia impulsów ani zgody na dowolne warunki pod maską.
