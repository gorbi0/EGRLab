# Procedury pomiarowe i interpretacja

Samochód użytkownika: **Kia Sportage 1.7 CRDi, 2013**, EGR 28410-2A850. Silnik tej konfiguracji jest zwykle oznaczany D4FD; w profilu pozostaje `engine_code: unverified`, dopóki oznaczenie/VIN go nie potwierdzi. Rok i pojemność nie rozstrzygają wersji ECU ani identyfikatorów CAN.

## IDENTIFY — rozpoznawanie pinów 5/6

1. Zawór połączony z ECU poprzez adapter LOGGER. Mostek i zasilanie czujnika TEST sprzętowo zablokowane; bank pomiarowy LOGGER aktywny.
2. Włącz zapłon zgodnie z normalną procedurą samochodu. Nie uruchamiaj TEST ani nie zasilaj pinów z urządzenia.
3. Obserwuj pin4/5/6 względem B− przez minimum 2 s. Dla kandydata GND wymagaj −0,2…+0,3 V, drugiego pinu względem niego4,5…5,5 V. Feedback względem GND musi zawierać się w0,2…4,8 V. Pojedynczy skok albo zanik resetuje okno2 s.
4. Oceń oba warianty: dokładnie jeden ma spełniać kryteria. Jeśli żaden lub oba: UNKNOWN, niczego nie próbuj odwracać. Brak5 V przy zapłonie, przesunięta masa albo uszkodzony feedback mogą uniemożliwić rozpoznanie.
5. Zapisz wynik wraz z nazwą zaworu/adaptera, numerem sesji, wartościami min/max, datą, CRC i skalowaniem ADC. Potwierdź raz multimetrem rzeczywisty pin 5 V. To potwierdzenie toru pomiarowego, nie zgadywanie polaryzacji.
6. Odłącz zapłon, wypnij LOGGER, dopiero potem podłącz zawór do TEST. K_SENSOR OFF → ustaw K_POL →100 ms → SENSOR_ENABLE →K_SENSOR ON →200 ms →weryfikacja 5 V/feedback. Nie przełączaj K_POL pod napięciem.

Rozpoznawanie nie rozpoznaje typu czujnika i nie ustala krańców mechanicznych. Profil starego zaworu nie przechodzi automatycznie na drugi egzemplarz. Jeśli nie możesz uruchomić ECU, do odblokowania potrzebujesz zweryfikowanego pinoutu serwisowego albo pomiaru na sprawnym zestawie. Pomiar rezystancji trzech pinów nie dowodzi, że czujnik jest zwykłym potencjometrem.

## Wspólne limity TEST

Wartości początkowe do kontrolowanego uruchomienia:12,0 V, zasilacz0,5 A, duty≤10%, impulsy≤50 ms, przerwa≥1 s. Brak ruchu przy tym limicie **nie oznacza usterki**. Potem zwiększ limit do 1 A/20% i dopiero na podstawie prądu sprawnego ruchu przygotuj profil roboczy. Firmware przykładowe ma maks. duty35%, soft current1,5 A oraz hard trip4 A — wymagają dopasowania; nie są danymi OEM.

Przerwanie: STOP, odłączenie pętli interlock, nieaktualny ADC, utrata sprzętowego ARM, zanik5 V, feedback poza kalibracją, soft overcurrent, temperatura ponad limit profilu, timeout ruchu, brak zapisu. Powrót wyłącznie do FAULT/DISARMED; brak automatycznego wznowienia ruchu.

Pozycja do analizy czujnika: `r=(V4−Vgnd)/(V5V−Vgnd)`. Po LEARN: `p=(r−r_closed)/(r_open−r_closed)` — również gdy znak mianownika jest ujemny. Zachowaj surowe napięcia; normalizacja może ukryć spadki wspólnego zasilania. W raportach nie obcinaj p do0…100%, bo wyjście poza zakres jest diagnostyczne.

## LEARN

Cel: profil kierunku i bezpiecznego zakresu, nie adaptacja ECU. Tester nie zapisuje nic do sterownika samochodu.

Najpierw zapisz pozycję przy silniku bez prądu i obejrzyj mechaniczne położenie zaworu. Oznacz je `rest`, nie automatycznie `closed`. W trybie krótkiego MANUAL wykonaj impulsy w kierunku+ i−; przerwij przy wzroście prądu bez ruchu. Porównaj znak Δr i ruch mechanizmu. Kierunek otwierania potwierdź wzrokowo/dokumentacją, nie samą polaryzacją feedbacku.

Zbieraj co najmniej3 przejścia przy ograniczonym duty, utrzymuj małą energię. Nie „dobijaj” do krańca przez zadany długi czas. Plateau feedbacku wraz ze wzrostem prądu oznacza kandydat krańca **albo zacięcie**; bez potwierdzenia mechanicznego nie zatwierdzaj jako100%. Zapisz r_closed, r_open, znak kierunku, prąd zerowy, temperaturę, czas przejścia i wariancję. Wymagaj |r_open−r_closed|>0,2, monotoniczności i powtarzalności zakresu≤2%FS. Ogranicz testy automatyczne do 10…90% ustalonego zakresu; nie do twardych ograniczników.

W firmware komenda `learn <r_closed> <r_open> <opening_sign>` zapisuje **zweryfikowane pomiarowo punkty** z tego procesu. Celowo nie ma algorytmu szukającego ograniczników przez przeciążanie nieznanego zaworu. NVS aktualizuj tylko przy zatrzymanej akwizycji i rozbrojonym napędzie.

## MANUAL

Jeden rozkaz = jeden ograniczony czasowo impuls. `manual <signed_duty> <ms>`; znak odnosi się do napięcia pin1−pin3. Limit dla pierwszych prób50ms; zatwierdzony profil może zezwolić do250ms. Nie dopuszczaj bezterminowego „OPEN” wysłanego przez terminal. Po zakończeniu zeroPWM, ARM=0, pauza; do kolejnego impulsu konieczne świeże zezwolenie użytkownika. Trzymanie przycisku UI wymaga odnawiania żądania co≤50ms i limitu całego ruchu.

Loguj napięcie uzwojenia, prąd, r, temperatury, command duty i czas. MANUAL służy też do sprawdzenia znaku prądu i kalibracji, zanim jakikolwiek regulator zamknie pętlę.

## SWEEP

Po LEARN wykonaj przejazd po punktach10,20,…90,80,…10%. W każdym punkcie maks.2 s na dojście i300 ms obserwacji. P regulator początkowoKp=0,8 duty/jednostkę pozycji, deadband1%, duty ograniczone profilem; całkowanie wyłączone, żeby nie kumulować wymuszenia na zacięciu. Jeśli potrzebne, dostrój na sprawnym ruchu. Sukces punktu: błąd<2% przez 100 ms. Przekroczenie czasu = przerwanie, nie przeskoczenie trudnego punktu.

Wynik: czasy10–90 i90–10%, overshoot, RMS prądu, błąd ustalony, różnica pozycji dla tego samego kierunku dojścia. Do oceny histerezy porównuj punkty przy podobnej temperaturze i napięciu. SWEEP nie zmienia ustawień ECU.

## FRICTION

To wskaźnik oporów ruchu, nie bezpośredni pomiar siły tarcia. W pozycji20/50/80% zacznij od zeroPWM, zwiększ duty o1 punkt procentowy co 50 ms do limitu profilu. Zapisz prąd i duty w chwili pierwszej zmiany pozycji o≥1% przez≥20 ms. Natychmiast przerwij rampę po wykryciu ruchu. Powtórz w obu kierunkach3×, z powrotem do punktu startowego przy regulacji i przerwą1 s.

Prąd rozruchu obejmuje sprężynę, przekładnię, moment silnika i tarcie; bez Kt/przełożenia nie raportuj N ani Nm. Zablokowany czujnik może wyglądać jak brak ruchu, dlatego kryterium awarii jest wspólne: prąd + Δpozycja + niezależna obserwacja. Firmware bazowe wykonuje rampę dla aktualnej pozycji; do20/50/80% dojedź funkcją `goto` i zrób3 powtórzenia. To jawne kroki procedury.

## CYCLE

10–90–10% z przerwą500 ms na każdym końcu; początkowo20 cykli, potem najwyżej200 po obejrzeniu logu. Limit ruchu2 s, przerwa termiczna kiedyTC1 rośnie ponad profil. Co10 cykli porównaj czasy, prąd średni/RMS i zakres feedbacku z pierwszymi3cyklami. Licznik nie zalicza cyklu, który osiągnął tylko timeout. Brak automatycznego powrotu po błędzie.

## THERMAL

Na zdemontowanym zaworze ogrzewaj wyłącznie kontrolowanym źródłem z własnym termostatem. EGRLab **nie steruje grzałką**. Etapy startowe temperatury korpusu napędu:20/40/60°C;80°C dopiero po potwierdzeniu dopuszczalnej temperatury konkretnego zespołu. To nie są limity pracy w silniku. TC1 na napędzie, TC2 na kołnierzu; odczekaj aż |dT1/dt|<0,5°C/min przez 2 min, następnie SWEEP i3rampy FRICTION w obu kierunkach, opcjonalnie20 cykli.

Powtórz w czasie chłodzenia; minimum 3serie. Zachowuj tę samą orientację zaworu, napięcie i ustawienia. Zapisz też20 s nieruchomego feedbacku bez silnika na każdym plateau: pomaga oddzielić dryft/glitch czujnika od mechaniki. Test stanowiskowy może nie odtworzyć temperatury wnętrza, ciśnienia spalin, drgań i osadów w aucie.

W firmware `thermal` uruchamia SWEEP z obowiązkową poprawnąTC1 i limitem temperatury profilu. Stabilizację plateau i ogrzewanie wykonuje operator. Nie zakładamy, że temperatura obudowy jest temperaturą uzwojenia.

## LOGGER i próba 1500–1700 rpm

Przed włączeniem do auta zrób porównanie: fabryczna wiązka → adapter z bypass shunta → adapter ze shuntem. Nie może pojawić się nowy DTC ani zmiana zachowania. Zmierz dodatkowy spadek napięcia, a nie tylko rezystancję multimetrem na zimno. Po próbie bypass usuń; w metadanych zapisz jego rzeczywisty stan (bypass oznacza nieważny pomiar prądu LOGGER).

Rejestruj rozgrzewanie i20–30 min pracy z buforem co najmniej10 s przed znacznikiem. Na początek MARK ręczny, później triggery: feedback poza zakresem, referencja poza4,5–5,5 V, masa >0,3 V, skok r>5% w1 ms, rosnący prąd przy braku ruchu. Progi oznaczają podejrzenie, nie kodP0404; warunek prąd/brak ruchu potrzebuje znajomości rozkazu ECU, nie samych obrotów.

Zrób osobne serie: zimny / rozgrzany / po postoju na gorąco, przy porównywalnym biegu i obciążeniu. Rejestruj pasmo1300–2000rpm z wolnym przejściem przez 1500–1700; nie tylko stałe obroty. Na drodze obsługą zajmuje się pasażer, przewody umocowane z dala od pedałów i elementów ruchomych. Celem jest rejestracja normalnie występującego objawu, bez wymuszania niebezpiecznej sytuacji.

Synchronizuj: ręczny MARK oraz timestamp CAN; przy zewnętrznym skanerze wykonaj wspólny rozpoznawalny znacznik, np. krótki stabilny punkt obrotów na postoju. Odnotuj opóźnienie PID: odpowiedź OBD nie ma dokładności timestampu ADC. Jeśli pasywne CAN nie zawiera obrotów, wynik `RPM=null`; użyj legalnego profilu odczytu skanera, a nie odgadniętegoID.

Nie kasuj DTC przed zapisaniem freeze-frame, statusu pending/confirmed i warunków wystąpienia. Nie ma uniwersalnego związku „błąd pozycji>x przez yms = OEM P0404”; wartości kalibracyjne ECU zależą od wersji.

## Macierz rozstrzygania przyczyny

| Obserwacja | Hipoteza | Co ją rozdziela |
|---|---|---|
| V5 V stabilne, ground stabilne, feedback ma nagłe przerwy | czujnik albo przewód feedback | porównanie napięcia na obu końcach wiązki, test nieruchomy i termiczny |
| V5 V i feedback spadają razem | zasilanie 5 V, wspólna wiązka, zwarcie odbiornika | ratiometryczny r i pomiar referencji przy ECU |
| rośnie sensor ground względemB− | powrót sensora/złącze | pomiar spadku wzdłuż przewodu bez zwierania dochassis |
| napięcie uzwojenia obecne, prąd rośnie, brak Δr | zacięcie/napęd lub kłamliwy feedback | wzrokowy ruch na stole, prąd, termika i porównanie sprawnego egzemplarza |
| napięcie uzwojenia obecne, prąd zanika | przerwa uzwojenia/szczotki/złącze | badanie rezystancji w stanie ciepłym przy całkowitym odłączeniu |
| brak napięcia uzwojenia | brak rozkazu albo ograniczenie/ochrona ECU | parametr zadany i pozostałe warunki; samo0 V nie dowodzi uszkodzeniaECU |
| pozycja poprawna, szarpanie trwa | przyczyna poza elektrycznym EGR lub niewłaściwy przepływ | MAF/MAP/boost/railpressure/DPF i układ napędowy, dane skanera |

Najbardziej wartościowe porównanie termiczne: dla tych samych punktów pozycji i napięcia wykres `I_breakaway(T)`, `t_10_90(T)`, `r_rest(T)`, liczba glitchy/min oraz zaników5V. Porównaj kierunki osobno. Silnik nagrzewa się również od samego testu — temperatura jest zmienną mierzoną, nie tylko nastawą grzałki.
