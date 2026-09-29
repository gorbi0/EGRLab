# P01-R3 — odbiór modułu

**Wszystkie pomiary do wykonania.** To etap po PCB i montażu. Najpierw sama P01,
bez ECU, EGR, ESP32 i dalszych płytek. Procedura poniżej pochodzi z bazy 6.1;
obowiązuje BOM R3: Q2=SUP53P06-20-E3 (GDS), Q4=2N5401YBU (EBC), D9=15 V,
C5=10 nF, C6=1 µF, R21=100 kΩ, R22=470 kΩ, R27=10 Ω/2 W, C7/C9=50 V.
J4 zachowuje pinout; do P04 docelowo idzie wiązka J5, więc nie łączyć równocześnie
dwóch przewodów SAFE_N przez J4 i J5. J1/J2/J4 są polami, nie gniazdami.

Próby obejmujące KPWR/mostek i silnik pozostają etapem integracji po odwieszeniu
P07. Nie odblokowują ani nie kończą automatycznie jego przeglądu.

---
# Odbiór prototypu PWR-THT v1

Pierwsze próby wykonaj bez ESP32, ADC, ECU i zaworu, z zasilaczem laboratoryjnym ograniczającym prąd. Potrzebne: multimetr, oscyloskop, obciążenie rezystancyjne/elektroniczne i pomiar temperatury. Wszystkie pomiary poniżej są **do wykonania**, nie są wynikami testów.

Masy zwykłych sond oscyloskopowych podłączaj wyłącznie do GND. VGS i VDS mierz zatwierdzonym stanowiskiem z docs/METROLOGIA.md. Odejmowanie kanałów wymaga osobnej kwalifikacji niepewności. Nie zwieraj źródła MOSFET-a do przewodu ochronnego oscyloskopu i nie odłączaj PE oscyloskopu.

## 1. Kontrola bez zasilania

Sprawdź pełną netlistę, polaryzację D2/D3/D4/D5/D6/D9, elektrolitów oraz G-D-S Q1/Q2 oraz E-B-C Q3...Q8. U1: 1=OUT, 2=GND, 3=IN. U3 TI LP: 1=K, 2=A, 3=REF; 1 i 3 są zwarte. U4 musi mieć bondout **D**. Odmienne oznaczenie MCP120 oznacza możliwość innej kolejności wyprowadzeń.

Q1: G-D-S od lewej przy widoku na oznaczenie, nóżki w dół; tab=D=P01_Q1_DRAIN. D2: A1-K-A2, tab=K=VS. Sprawdź izolację radiatorów oraz brak zwarcia VS-VPROT. Ustaw RV1 na **0 Ω między (1+2) a 3**, co daje zachowawczo obniżony próg OVP. Nie ustawiaj położenia na podstawie kierunku obrotu śruby.

## 2. Zasilanie i blokada

Zewrzyj J3. Podaj 13,8 V z limitem 100 mA. Na AUX5 powinno być 4,85-5,15 V, REF około 2,495 V. Sprawdź oscyloskopem stabilność AUX5 i REF. |VGS| powinno być poniżej 0,5 V, LED zgaszona; VPROT może chwilowo zawierać ładunek kondensatora, po ustaleniu z obciążeniem 1 kΩ powinno być poniżej 0,5 V.

Brak oscylacji i poprawne napięcie statyczne są oddzielnymi warunkami. Jeżeli U1 oscyluje, sprawdź ESR C9/R2 oraz połączenia masy, zamiast dodawać przypadkowe kondensatory.

## 3. Start i zanik zasilania sterowania

Usuń zworkę J3. Z obciążeniem 1 kΩ obserwuj AUX5, OK, GATE i VPROT podczas pełnego wyłączenia/włączenia wejścia. Załączenie ma wystąpić po zwolnieniu U4, zwykle około 350 ms; dopuszczalne 150-700 ms plus czas narastania AUX5 i narastanie VPROT po ENABLE (do300ms według sekcji7). Powolny wzrost VIN, szybkie podłączenie 13,8 V oraz start od razu z 24 V nie mogą uruchomić obciążenia w stanie błędu.

Sprawdź również start z 19-24 V: wyjście pozostaje wyłączone. Po powrocie napięcia do okna wraca zasilanie. Opóźnienie U4 dotyczy ponownego pojawienia się prawidłowego AUX5; **nie powtarza się automatycznie po każdym OVP**, jeżeli AUX5 nie zanikło.

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

## 7. Dynamika — protokół R3

Zapis każdej próby: PCB/BOM, temperatura, Cload, obciążenie, napięcie, impedancja
i ograniczenie energii źródła, rzeczywiste zbocze VS, sondy/pasmo/offset, przebieg.
Powtórzyć w0/25/50°C bez kondensacji. Najpierw bez P02/P07/silnika, Cload220µF
ŁĄCZNIE z C3. Zaczynać od mniejszej energii i napięcia.

Zasilacz już pracuje na ustalonym napięciu; osobny przełącznik/fixture podaje je
na układ. OUTPUT zasilacza jest inną próbą. COMBICON nie służy do łączenia pod
obciążeniem. Nie używać auta jako generatora przepięć.

Rejestrować VS, **VGS różnicowo bezpośrednio G–S Q1**, VPROT i prąd gałęzi Q1.
Masy oscyloskopu nie podłączać do SOURCE. Sonda różnicowa albo skompensowane
kanały względem GND z ocenionym błędem odejmowania. Prąd: sonda lub bocznik
w gałęzi Q1, nie całkowity prąd wejściowy (C1/AUX pobierają normalny impuls).
Stanowisko nie może istotnie spowalniać zbocza. Minimum10MS/s, pasmo10MHz,
niepewność VGS≤0,10V, czasu≤2µs i ładunku≤2µC; wymagana ocena z METROLOGIA.md. Rozdzielczość nie jest niepewnością.

1. **OFF/hotplug:** J3 zwarte;0→14V i0→24V, zbocza VS około1µs i1ms. Powtórzyć
   z wcześniej odłączonym AUX (U1/R1). Najpierw wyjście rozładowane, potem18→30V
   z VPROT naładowanym do17V przez odłączone źródło. VSG≤0,8V, bez utrzymującego
   się przewodzenia. Dla rozładowanego220µF: wzrost VPROT≤0,1V w pierwszych200µs,
   dodatni ładunek gałęzi Q1≤10µC po ocenie offsetu i displacement; nie zastępować tego warunku samym ΔVPROT. Gdy pomiar
   tego nie rozróżnia: NIE ROZSTRZYGNIĘTO, nie PASS. Powtórzyć kontrolowane odbicia.
   OFF po10ms i1s z1kΩ: VPROT≤0,2V; upływ może ładować nieobciążony kondensator.
2. **48V:** dopiero po niższych napięciach, jako krótki impuls z określonym
   kształtem, impedancją i energią dopuszczalną dla TVS. Mierzyć rzeczywiste VS
   (≤48V), nie zakładać go z nastawy przed D1/D2. Te same kryteria VSG, zapis
   VPROT. Bez specyfikacji generatora próba pozostaje NIE ZBADANO. Nie stałe48V.
3. **Start:** VIN10,5/13,8/16V, C≤220µF, Iload0/0,1/1,5A, KPWR OFF. Szczyt≤5A
   jest kryterium testu, nie aktywnym limitem. VPROT≥95%VS w≤300ms po ENABLE;
   ustalone |VGS|≥4,5V. Zapis ID/VDS/czas i porównanie SOA z temperaturą Q1.
   Nie wystarczy ½CV² ani znamionowe53A.
4. **Wyłączenie:** wymusić J3 i zanik AUX: ENABLE→|VGS|<0,5V≤80µs. OVP14→24V:
   od VIN na J1 przekraczającego18,5V do |VGS|<0,5V≤100µs. Osobno detektor/bufor
   ≤20µs i bramka≤80µs. Przekroczenie podbudżetu wymaga analizy, nie zmiany
   punktu początku czasu. Obserwować SAFE_N i prąd; duży impuls przed odcięciem
   trzeba ocenić pod względem SOA/D2/TVS/źródła także przy czasie<100µs.
5. **Powrót:** brak oscylacji, spokojny start, ARM ponownie tylko fizycznie.
   SAFE_N zwalnia po ENABLE zanim VPROT się ustali. Przed KPWR wymagany pomiar
   VPROT w zakresie dopuszczenia następnego modułu, stabilny przez≥300ms.
   Sam SAFE_N nie wystarczy, zwłaszcza przy CORE z USB. To wymaganie integracyjne
   do sprawdzenia na P04/P07; firmware nie był zmieniany w pakiecie P01.

### 7.6 Powrót po krótkim błędzie — nowy wymagany pomiar

Na ustalonym zasilaniu14V wymuś INHIBIT przez10µs/50µs/1ms, potem zwolnij.
J3 wolno sterować tylko suchym stykiem albo otwartym kolektorem do GND,
bez podawania napięcia z generatora na ten węzeł. Zmierzyć faktyczne ENABLE;
szerokość impulsu generatora nie jest automatycznie szerokością ENABLE.
Obciążenie3W i6W stałej mocy, ze znanym sposobem odcięcia przy niskim napięciu.
Rejestrować czas wyłączenia Q1, najniższe VPROT i czas odzyskania zasilania.
Potem trzy impulsy50µs w odstępach20ms. Spadek VPROT na samej P01 jest spodziewany;
nie oznacza zaliczenia ciągłości LOGGER-a. Powrót VPROT≥95%VS w≤300ms,
bez samoczynnego ARM. Długi fault ma pozostawić wyjście wyłączone.

### 7.7 Integracja z P02-HOLD

Dołączać dopiero po niezależnym odbiorze P01 i obwodu HOLD. Zmierzyć moc wszystkich
odbiorników, napięcie rezerwy i szyny5V/3V3/ADC. Przy Ceff≥52,8mF, rezerwie≥9,5V,
poborze≤6W na VLOG_RES i spadku gałęzi≤1,2V przerwa źródła50ms ma zachować
VLOG_RES≥7V i działanie przetwornic. Fizyczny ARM ma pozostać rozbrojony po błędzie.
Powtórzyć w0/25/50°C, z USB i bez, przy aktywnym SD/Wi-Fi/CAN oraz serią faultów.
Sprawdzić rzeczywisty brak restartu i ciągłość numeracji próbek/konfiguracji na SD.
Przerwa zasilania samego sensora z ECU wymaga oznaczenia danych jako nieważne.
Dodatkowo rozładowana rezerwa, długi fault, powrót i doładowanie: nie mogą powodować
prądu wstecznego do VPROT ani uruchomienia silnika. Nie wymagać nieograniczonego
podtrzymania. Rezerwa na50ms nie gwarantuje zakończenia operacji karty SD.

Automatyczne powtórzenia odbioru najwyżej1Hz. VPROT nie musi spaść do zera w100µs;
pozostaje energia kondensatorów. Wynik zawsze przypisać do właściwego stanu i czasu.

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
| Powrót po10/50/1000µs i seria faultów | | NIE ZBADANO |
| Integracja HOLD:50ms/6W, SD, USB, ARM | | NIE ZBADANO |
| -14/-24 V, upływ wsteczny | | NIE ZBADANO |
| Impulsy: przebieg, impedancja, energia | | NIE ZBADANO |
| Zwarcie / koordynacja F1 / SOA | | NIE ZBADANO |
| KPWR, silnik, regeneracja | | NIE ZBADANO |

Kopię wypełnionego protokołu dołącz do egzemplarza. „Zaliczone DC” nie oznacza zaliczenia impulsów ani zgody na dowolne warunki pod maską.


Uzupełnienie 6.1-rc1: próg OVP jest nominalnie około 18V. Liczba 18,00 w obliczeniu lub nastawie zasilacza nie jest gwarancją dokładności układu. Odbiór obejmuje regulację w temperaturze pokojowej oraz pomiar progów w 0/25/50°C według tej instrukcji. D6, offset komparatora i tolerancje wpływają na wynik.

Metoda pomiaru i marginesy: METROLOGIA.md. Powerbank nie dopuszcza masy DHO804 na SOURCE.
