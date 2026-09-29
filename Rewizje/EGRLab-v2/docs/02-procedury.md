# Procedury pomiarowe EGRLab v2

Dokument terenowy — ma być czytelny przy masce bez reszty pakietu. Kia Sportage SL 2013, 1.7 CRDi D4FD, EDC17C08, zawór 28410-2A850, złącze CUD87.

**Zanim cokolwiek wepniesz:** potwierdź pinout CUD87 ze schematu Monolith (strony PDF 56–59) dla swojego VIN. Dwa źródła w tym projekcie mówiły różne rzeczy o pinach 4/5/6 i dlatego urządzenie rozpoznaje je samo — ale piny 1/3 jako napęd przyjmujesz na wiarę i pomyłka tutaj zwiera gałąź mostka.

## Jak to się ma do procedury skopowej v3

EGRLab **nie zastępuje** `../../docs/procedura_v3_DHO804.md`. Kolejność jest taka:

1. Test A (klimatyzacja), Krok 2 (masa pod obciążeniem), Krok 6c (opalarka), 6a/6b (wiggle) — skopem, back-probe, **bez ruszania złącza**. To jest weekend i może zamknąć sprawę.
2. LOGGER L2 (back-probe) — wielogodzinna rejestracja ośmiu kanałów, w tym AUX na ECV albo na GUD09.
3. LOGGER L1 (inline, z prądem) — dopiero gdy wiesz, czy usterka siedzi w złączu.
4. TEST na zgaszonym silniku i HOT-SOAK — gdy powyższe wskażą na sam zawór albo gdy nic nie wskażą.

Powód kolejności: rozpięcie CUD87 jest operacją zaburzającą hipotezę H6. Nie rozpinaj go, dopóki nie zmierzysz stanu „jak zastałem".

---

## Bezpieczeństwo — przeczytaj raz, stosuj zawsze

* **Nigdy nie podłączaj masy urządzenia do pinów napędu 1/3.** Zewrzesz gałąź mostka — własnego albo ECU.
* Urządzenie ma **jedną wspólną masę**, wyprowadzoną na minus akumulatora. Nie rób drugiego połączenia: ani uziemionym USB, ani skopem zasilanym z sieci, ani przez pin 5 OBD.
* Wtyczki CUD87 **nie rozchylaj** i nie wciskaj w nią nic sztywnego — wygenerujesz H6 własnoręcznie.
* Przy pracującym silniku uważaj na pasek i wentylator; wiązkę adaptera prowadź z dala od części ruchomych i od pedałów.
* TEST wolno uzbroić **tylko** przy wypiętej wiązce samochodowej i wpiętym adapterze T. Sprawdza to sprzętowa pętla interlock, ale sprawdź i Ty.
* Zawór na gorącym silniku parzy. TC1 na korpusie napędu jest warunkiem ruchu, nie ozdobą.
* Pierwsze uruchomienie każdego nowego zaworu: limit prądu 0,5 A, duty do 10 %, impulsy do 50 ms. **Brak ruchu przy tym limicie nie oznacza usterki.**

---

## IDENTIFY — rozpoznanie mapowania pinów 4/5/6

Urządzenie nie zgaduje i niczego nie odwraca próbnie. Mierzy biernie, gdy **ECU zasila czujnik**, i sprawdza wszystkie sześć permutacji trójki (zasilanie, masa, sygnał).

1. Adapter **L1 albo L2** wpięty, mostek i zasilanie czujnika sprzętowo zablokowane, bank pomiarowy LOGGER aktywny. Konsola: `logger`.
2. Zapłon włączony normalną procedurą samochodu. Nie uruchamiaj silnika, nie zasilaj niczego z testera.
3. `identify`. Przez 2 s urządzenie szuka permutacji, w której: kandydat na masę leży w −0,2…+0,3 V względem B−, kandydat na zasilanie 4,5…5,5 V nad nim, a kandydat na sygnał 0,2…4,8 V nad nim. Każdy skok albo zanik resetuje okno. Timeout 30 s.
4. **Dokładnie jedna** permutacja musi przejść. Jeśli żadna albo więcej niż jedna — wynik UNKNOWN i nic się nie odblokowuje. Przyczyny: brak 5 V przy zapłonie, przesunięta masa, uszkodzony tor sygnału albo inny typ czujnika niż trójprzewodowy ratiometryczny.
5. `status` pokaże mapowanie. **Potwierdź je multimetrem** — który pin ma realnie 5 V. To potwierdzenie toru pomiarowego, nie zgadywanie.
6. `stop`, `save`. Po zapisie urządzenie ustawia zakres ±2,5 V na kanale masy czujnika, więc od tej chwili masz tam 76 µV na działkę.

Rozpoznanie **nie** ustala typu czujnika ani krańców mechanicznych, a profil jednego zaworu nie przechodzi na drugi egzemplarz. Pomiar rezystancji trzech pinów nie dowodzi, że to zwykły potencjometr.

Przejście na TEST: zapłon wyłączony, adapter LOGGER wypięty, **zworki JP_SENSOR na adapterze T ustawione zgodnie z wynikiem IDENTIFY**, dopiero wtedy wpinasz adapter T. Kolejność wewnętrzna jest automatyczna — cały port ekspandera w dół, 100 ms, bank TEST, 100 ms, zasilanie czujnika, potem 200 ms weryfikacji napięć. Źle założona zworka kończy się `SENSOR_CHECK_TIMEOUT`, a nie ruchem zaworu. **Zworek nie przekładaj przy wpiętym adapterze.**

---

## Wspólne limity TEST

Wartości startowe: 12,0 V, zasilacz 0,5 A, duty ≤ 10 %, impulsy ≤ 50 ms, przerwa ≥ 1 s. Potem 1 A / 20 %, i dopiero z prądu sprawnego ruchu budujesz profil roboczy. Firmware ma domyślnie max duty 35 %, soft 1,5 A i twardy trip 4 A — **to są limity rozruchowe, nie dane OEM zaworu.**

Przerwanie ruchu następuje przy: STOP, rozwarciu interlock, nieaktualnych danych ADC, utracie sprzętowego ARM, zaniku 5 V czujnika, sygnale poza kalibracją, soft overcurrent, temperaturze ponad limit profilu, timeoucie ruchu, błędzie zapisu. Powrót wyłącznie do FAULT, potem świadomy STOP. **Nie ma automatycznego wznowienia.**

Pozycja: `r = (V_sygnał − V_masa) / (V_zasilanie − V_masa)`, potem `p = (r − r_closed) / (r_open − r_closed)`, także gdy mianownik jest ujemny. W raportach `p` nie jest obcinane do 0…100 % — wyjście poza zakres jest informacją diagnostyczną. Surowe napięcia zostają w logu, bo normalizacja ukryłaby zapad wspólnego zasilania.

---

## LEARN

Cel: profil kierunku i bezpiecznego zakresu. Tester nie zapisuje nic do sterownika samochodu.

Zacznij od pozycji bez prądu — `status` i **obejrzyj mechanicznie**, gdzie stoi zawór. Oznacz to jako `rest`, nie automatycznie `closed`. Potem krótkie impulsy `manual` w obu kierunkach; przerwij przy wzroście prądu bez ruchu. Porównaj znak zmiany `r` z faktycznym ruchem mechanizmu. **Kierunek otwierania potwierdzasz wzrokiem, nie polaryzacją sygnału.**

Zbierz co najmniej trzy przejścia przy ograniczonym duty. Nie „dobijaj" do krańca długim impulsem. Plateau sygnału przy rosnącym prądzie to kandydat na kraniec **albo zacięcie** — bez potwierdzenia mechanicznego nie zatwierdzaj jako 100 %. Wymagania: |r_open − r_closed| > 0,2, monotoniczność, powtarzalność zakresu ≤ 2 % FS. Testy automatyczne ograniczaj do 10…90 % ustalonego zakresu.

`learn <r_closed> <r_open> <znak>` zapisuje **zmierzone** punkty. Celowo nie ma algorytmu szukającego ograniczników przez przeciążanie nieznanego zaworu. NVS aktualizujesz `save` przy zatrzymanej akwizycji i rozbrojonym napędzie.

---

## MANUAL, GOTO, SWEEP

`manual <duty ze znakiem> <ms>` — jeden ograniczony czasowo impuls, znak odnosi się do napięcia pin 1 − pin 3. Limit 50 ms na pierwszych próbach, do 250 ms w zatwierdzonym profilu. Po impulsie duty = 0 i ARM = 0; kolejny impuls wymaga świeżego rozkazu. Przycisk w interfejsie webowym musi odnawiać żądanie co ≤ 50 ms. **Nie ma bezterminowego „OPEN".**

`goto <0,1…0,9>` — regulator proporcjonalny, Kp 0,8 duty na jednostkę pozycji, martwa strefa 1 %, bez całkowania (żeby nie kumulować wymuszenia na zacięciu). Sukces: błąd < 2 % przez 100 ms.

`sweep` — 10, 20 … 90, 80 … 10 %. Maks. 2 s na dojście i 300 ms obserwacji w punkcie. Przekroczenie czasu przerywa, nie przeskakuje trudnego punktu. Wynik: czasy 10–90 i 90–10 %, przeregulowanie, RMS prądu, błąd ustalony, różnica pozycji dla tego samego kierunku dojścia. Histerezę porównuj tylko przy podobnej temperaturze i napięciu.

---

## FRICTION — prąd zerwania

To wskaźnik oporów ruchu, nie pomiar siły w niutonach. Bez stałej momentu i przełożenia nie raportuj N ani Nm.

Z pozycji startowej: duty rośnie o 1 punkt procentowy co 50 ms, aż pozycja zmieni się o ≥ 1 % przez ≥ 20 ms. Wtedy rampa jest **natychmiast** przerywana i zapisany zostaje prąd oraz duty w chwili ruszenia. Powtórz trzy razy w obu kierunkach, wracając `goto` do punktu startowego, z przerwą 1 s.

Pełny pomiar robisz dla 20, 50 i 80 %: `goto 0.2` → `friction 1` → `goto 0.2` → `friction -1`, i tak trzy razy dla każdego punktu. Zablokowany czujnik wygląda jak brak ruchu, więc kryterium awarii jest zawsze złożone: prąd **plus** zmiana pozycji **plus** niezależna obserwacja.

---

## HOT-SOAK — kampania na stygnącym silniku *(nowe w v2)*

To jest test uszyty pod definicję P0404 z manuala GDS dla D4FD: aktuator pozostaje całkowicie otwarty lub zamknięty przez ponad 4 s, a wymienione progi to **wysoka temperatura silnika aktuatora** albo silnik zablokowany. Usterka jest stroma powyżej ~35°C otoczenia — a temperatura samego zaworu po przejeździe jest dużo wyższa niż otoczenie i **nie musisz czekać na upał**.

Zawór zostaje na silniku. Nie demontujesz niczego.

1. Przejedź tak, żeby silnik był w pełni rozgrzany; im cięższa jazda, tym lepiej. Zaparkuj.
2. **Zgaś silnik.** Zapłon wyłączony. Odczekaj, aż ustaną wentylatory.
3. Przyklej TC1 do korpusu napędu zaworu, TC2 na kołnierzu. Opaska lub taśma kaptonowa, nie luźno.
4. Wypnij CUD87 z zaworu, wepnij adapter T. Tester zasilany z akumulatora przez bezpiecznik 10 A albo z własnego zasilacza.
5. `test`, poczekaj na READY, uzbrój fizycznie ARM.
6. `hotsoak <okres_s> <liczba_serii>`, typowo `hotsoak 180 12` — co 3 minuty przez 36 minut.

Każda seria to: dojście do 50 %, rampa oporów w stronę otwierania, powrót do 50 %, rampa w stronę zamykania, dojście do 10 %, przejazd do 90 % i z powrotem. Do logu idzie jedna linia `hotsoak_point` z temperaturami TC1/TC2, prądami zerwania w obu kierunkach, czasami 10–90 i 90–10 % oraz napięciem zasilania. Między seriami napęd jest rozbrojony.

**Czego szukasz.** Wykres prądu zerwania i czasu przejścia w funkcji TC1, osobno dla każdego kierunku. Interpretacja:

| Obraz | Wniosek |
|---|---|
| prąd zerwania rośnie wyraźnie wraz z temperaturą, czas przejścia się wydłuża | mechanika albo silnik zaworu — pierwszy twardy dowód przeciw zaworowi w całej kampanii |
| wszystko płaskie od 100°C do 40°C, ruch czysty | zawór oczyszczony w tym zakresie; wracasz do wiązki, masy i złącza |
| ruch czysty, ale sygnał pozycji ma skoki przy nieruchomym mechanizmie | tor czujnika albo styk, nie mechanika |
| napęd dostaje napięcie, prąd rośnie, pozycja stoi | zacięcie albo kłamiący sygnał pozycji — rozdziel obserwacją wzrokową |

**Powtórz to dla zdjętych zaworów.** Masz trzy egzemplarze zdjęte z tego auta. Ten sam `hotsoak` na stole, z grzaniem z zewnętrznego źródła z własnym termostatem, daje grupę odniesienia. Jeżeli wszystkie cztery zachowują się tak samo, to mocny argument, że problem nigdy nie był w zaworze — i to też jest wynik.

Ograniczenie, którego nie da się obejść: mierzysz temperaturę **obudowy**, a GDS mówi o temperaturze silnika aktuatora. Test stanowiskowy nie odtwarza też ciśnienia spalin, drgań i osadów.

---

## THERMAL — na zdjętym zaworze

Grzej **wyłącznie kontrolowanym źródłem z własnym termostatem**. EGRLab nie steruje grzałką. Etapy: 20 / 40 / 60°C, a 80°C dopiero po potwierdzeniu dopuszczalnej temperatury konkretnego zespołu. To nie są limity pracy w silniku.

Na każdym plateau odczekaj, aż |dT1/dt| < 0,5°C/min przez 2 min, potem `sweep`, trzy rampy `friction` w obu kierunkach, opcjonalnie 20 cykli. Zapisz też **20 s nieruchomego sygnału pozycji bez zasilania silnika** — to rozdziela dryf i glitche czujnika od mechaniki. Powtórz przy stygnięciu, minimum trzy serie, ta sama orientacja zaworu, napięcie i nastawy.

---

## CYCLE

10–90–10 % z przerwą 500 ms na końcach; 20 cykli na start, najwyżej 200 po obejrzeniu logu. Limit ruchu 2 s, przerwa termiczna gdy TC1 przekracza limit profilu. Co 10 cykli porównaj czasy, prąd średni i RMS oraz zakres sygnału z pierwszymi trzema cyklami. Cykl zakończony timeoutem się nie liczy.

---

## LOGGER — rejestracja w jadącym aucie

### Wariant L2 (back-probe) — pierwszy

Sondy back-probe od strony wiązki na pinach 1, 3, 4, 5, 6. Wtyczka CUD87 **zostaje wpięta**. Brak pomiaru prądu — kanał prądu będzie płaski i to jest w porządku.

### Wariant L1 (inline) — po L2

Przed pierwszym użyciem w aucie zrób porównanie trzech stanów: fabryczna wiązka → adapter z założonym mostkiem bocznikującym → adapter z bocznikiem. **Nie może pojawić się nowy DTC ani zmiana zachowania.** Zmierz dodatkowy spadek napięcia pod prądem, nie samą rezystancję na zimno. Po próbie zdejmij mostek i zapisz jego realny stan w metadanych — założony mostek oznacza nieważny pomiar prądu.

### Kanał AUX — zdecyduj przed sesją

| Cel sesji | AUX | Jumper |
|---|---|---|
| **H7** — sprzężenie z klimatyzacją | linia ECV kompresora (sterowanie PWM z FATC) | HI |
| **H2** — rezystancyjna masa | punkt masowy GUD09 względem minusa akumulatora | LO |
| H1 — wspólne przetarcie | dowolna sąsiednia żyła w tym samym splocie | HI |
| kontrola | plus akumulatora przy ECM | HI |

Zrób osobne sesje dla ECV i dla GUD09. Kuszące jest zrobienie wszystkiego naraz, ale masz jeden kanał.

Po przełożeniu zworki JP_AUX wpisz `aux 0` (HI) albo `aux 1` (LO). Firmware nie widzi zworki — jeśli mu nie powiesz, pomiar na masie GUD09 pójdzie na zakresie ±40 V i zgubisz to, po co go robisz.

### Przebieg sesji

Rejestruj rozgrzewanie i 20–30 minut jazdy. Na początek **MARK ręcznie** — przycisk na obudowie, do wciśnięcia zaraz po wejściu w tryb awaryjny; przy 2 kS/s ciągły plik mieści 18,6 h, więc nie musisz trafić w moment, wystarczy oznaczyć. Triggery firmware oznaczają zdarzenia same i dodatkowo wystawiają impuls **SCOPE_TRIG**.

Jeśli masz skop w aucie: wepnij SCOPE_TRIG w wyzwalanie DHO804, ustaw Waveform Recording i Peak Detect na kanale wipera. Dostaniesz pełnopasmową ramkę dokładnie w chwili, którą rejestrator uznał za podejrzaną — to jest ten przypadek, w którym oba przyrządy naraz dają więcej niż suma.

Loguj osobne serie: zimny, rozgrzany, po postoju na gorąco, przy porównywalnym biegu i obciążeniu. Pasmo 1300–2000 obr. przechodź wolno, nie tylko stałe obroty. Za obsługę w jeździe odpowiada pasażer.

Synchronizacja z Car Scannerem: wspólny rozpoznawalny znacznik, np. krótki stabilny punkt obrotów na postoju plus MARK. Odpowiedzi OBD nie mają dokładności znacznika czasu ADC — nie udawaj, że mają.

**Nie kasuj DTC przed zapisaniem freeze-frame, statusu pending/confirmed i warunków wystąpienia.** Nie ma uniwersalnej zależności „błąd pozycji > x przez y ms = P0404"; kalibracja ECU zależy od wersji.

Do dziennika `../../docs/dziennik-zdarzen.csv` wpisz każde wystąpienie: data, godzina, temperatura otoczenia, AC tak/nie, przebieg dnia, typ jazdy, regeneracja DPF.

---

## SUBSTITUTE LOAD — co ECU naprawdę wystawia *(nowe w v2)*

Rozstrzyga pytanie, którego nie rozstrzyga nic innego w tej kampanii: czy sterowanie wychodzące z ECU przez wiązkę jest czyste, gdy po drugiej stronie **nie ma zaworu**, tylko znany rezystor.

1. Zapłon wyłączony. Wypnij CUD87 z zaworu.
2. Wepnij adapter L1 do wiązki samochodowej, a na jego stronę zaworu — rezystor **12 Ohm / 25 W** zamiast zaworu. Piny czujnika zostają niepodłączone.
3. Bank LOGGER, `logger`, rejestracja włączona.
4. Włącz zapłon. ECU przy starcie wykonuje ruch aktuatora — masz okno kilku sekund na zarejestrowanie napięcia i prądu w znane obciążenie.
5. Po kilku sekundach ECU zgłosi błąd czujnika pozycji i przestanie sterować. **To jest oczekiwane.** Zapisz kody, potem skasuj.

Co z tego masz: amplitudę, kształt i stabilność sterowania oraz rzeczywisty prąd przez całą wiązkę, bez udziału zaworu. Jeśli przy znanym obciążeniu napięcie się załamuje albo prąd nie odpowiada rezystancji, masz rezystancję szeregową w wiązce albo słaby stopień wyjściowy ECU — i to bez zgadywania. Jeśli jest czysto, cała gałąź napędowa od ECU do złącza jest oczyszczona.

Test można powtórzyć na gorącym silniku zaraz po przejeździe oraz przy wyginaniu wiązki. **Zaplanuj go na koniec dnia** — zostawia kody i zmusza do kasowania.

---

## HARNESS-ONLY — wiązka bez obciążenia *(nowe w v2)*

Najprostszy wariant: adapter L1 w wiązce, po stronie zaworu nic. Zapłon włączony, silnik zgaszony. Rejestrujesz napięcia jałowe na pinach 1 i 3, referencję 5 V i masę czujnika, **wyginając kolejne odcinki wiązki**, w szczególności przy pokrywie rozrządu, gdzie są połamane mocowania i gdzie biegnie naprawiona żyła ECV.

Wszystko jest bez obciążenia, więc każdy zapad jest czystym objawem przerwy albo styku, bez udziału spadków na rezystancji pod prądem. To jest elektryczny odpowiednik Kroku 6a z procedury v3, tylko z ośmioma kanałami i automatycznym oznaczaniem zdarzeń, i tak samo jak tam — **powtórz trafienie 3–5 razy**, zanim uznasz je za wynik.

---

## Macierz rozstrzygania — co który obraz znaczy

| Obserwacja | Hipoteza kampanii | Co ją potwierdza lub obala |
|---|---|---|
| Masa czujnika (kanał ±2,5 V) rośnie powtarzalnie przy załączeniu AC i wentylatorów | **H2 + H7** | AUX na ECV w tej samej sesji; korelacja musi być powtarzalna, nie jednorazowa |
| AUX na ECV pokazuje PWM, a sygnał pozycji ma szum w tym samym rytmie | **H7** — sprzężenie pojemnościowe przez przetarcie | wygaszenie przy odłączeniu AC, powrót przy załączeniu, 5 powtórzeń |
| Referencja 5 V zapada, sygnał reaguje w tej samej chwili | **H4** | sygnał jest ofiarą, nie sprawcą — nie obwiniaj wipera |
| Sygnał pozycji skacze przy stabilnym 5 V i stabilnej masie | **H3** | back-probe na obu końcach odcinka |
| Glitch tylko przy poruszaniu samą wtyczką, wiązka spokojna | **H6** | HARNESS-ONLY plus oględziny styków żeńskich pod lupą |
| Glitch powtarzalnie przy ruchu konkretnego odcinka | **H1** | ten sam ruch odcinka daje glitch na dwóch kanałach naraz, w tym na AUX |
| Jednoczesny glitch bez powtarzalnego wywołania | — | to tylko korelacja czasowa, nic nie potwierdzone |
| Napięcie napędu obecne, prąd rośnie, pozycja stoi | **H5** | obserwacja wzrokowa ruchu; HOT-SOAK rozstrzyga zależność od temperatury |
| Napięcie napędu obecne, prąd zanika | przerwa uzwojenia, szczotek albo styku | pomiar rezystancji na gorąco przy całkowitym odłączeniu |
| Brak napięcia napędu | brak rozkazu albo ochrona ECU | samo 0 V nie dowodzi uszkodzenia ECU; SUBSTITUTE LOAD rozdziela |
| HOT-SOAK: prąd zerwania rośnie z temperaturą | **H5**, zgodnie z progiem GDS | powtórz na zdjętych egzemplarzach jako grupie odniesienia |
| HOT-SOAK płaski, LOGGER czysty, SUBSTITUTE LOAD czysty | zostaje złącze i styk | wracasz do H6 i do oględzin CUD87 |

Najbardziej wartościowe porównanie termiczne: dla tych samych punktów pozycji i tego samego napięcia wykresy `I_zerwania(T)`, `t_10_90(T)`, `r_spoczynkowe(T)`, liczba glitchy na minutę oraz liczba zapadów 5 V. Kierunki porównuj osobno. Silnik zaworu grzeje się również od samego testu — temperatura jest wielkością mierzoną, nie nastawą.
