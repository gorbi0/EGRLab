# Projekt elektryczny EGRLab v3

Kia Sportage SL 2013, 1.7 CRDi D4FD, EDC17C08. Zawór EGR 28410-2A850, złącze CUD87 (6-pin). MCU: posiadana płytka Waveshare ESP32-S3-DEV-KIT-N32R16-M (moduł WROOM-2-N32R16V, 32 MB Flash OPI, 16 MB PSRAM OCT).

Zmiany względem v2 i odpowiedź na zewnętrzny przegląd: `00-zmiany-v2-v3.md`. Historia v1 → v2: `00-zmiany-v1-v2.md`.

## 1. Do czego to służy

Trzy zastosowania, w kolejności ważności dla kampanii:

**LOGGER** — pasywny rejestrator wpięty w tor EGR przy pracującym silniku. Osiem kanałów jednocześnie: pin 1, pin 3, pin 4, pin 5, pin 6, prąd uzwojenia, napięcie instalacji i **kanał AUX** wpięty w punkt spoza EGR (linia ECV klimatyzacji dla H7 albo masa GUD09 dla H2). Urządzenie niczego nie steruje i nie zapisuje do ECU.

**TEST na zgaszonym silniku** — zawór zostaje na silniku, wypinasz z niego wiązkę samochodową i wpinasz adapter testera. Możesz zaworem „pomachać": zadawać pozycje, robić przejazdy, mierzyć prąd zerwania i czas przejścia, powtarzać to na stygnącym silniku. Demontaż zaworu nie jest potrzebny — jest potrzebny dopiero do testu termicznego z własnym źródłem ciepła.

**Stanowisko** — ten sam TEST przy stole, na zdjętym zaworze, z porównaniem egzemplarzy (masz trzy zdjęte zawory jako grupę odniesienia).

Czego to urządzenie nie robi: nie emuluje zaworu, nie kasuje kodów, nie zmienia adaptacji, nie modyfikuje strategii ECU.

## 2. Architektura

```text
                         adaptery (fizycznie wyłączne)
 ECU ── J_LOG ──┬── pin 1 ── RSH_L 5 mOhm ──┬── pin 1 ──┐
                ├── piny 3,4,5,6 wprost ────┤           ├── ZAWÓR EGR
 J_TEST ───── VNH5019 ── RSH_T ── pin 1 ────┘           │
              JP_SENSOR/K_SENSOR ── piny 4,5,6 ─────────┘
                │
   odczepy R przy złączu EGR (oba adaptery) ─ węzeł wspólny ─ K_MEAS ─ RC ─┐
   AUX (jumper HI/LO) ────────────────────────────────────────────────────┤
   INA240A2 x2 (RSH_L albo RSH_T) ── multiplekser banku ──────────────────┤
   dzielnik VBAT ─────────────────────────────────────────────────────────┤
                                                                          │
                                                          AD7606B ── SPI2 ── ESP32-S3
 12 V ─ F1 ─ TVS ─ LM74800 (rev.pol. + OVP) ─ VPROT ─ DC/DC              ├─ SD (SPI3)
                                                                          ├─ 2x MAX31856
 STOP ─────────┬─ SAFE_N (wire-AND) ─ /CLR 74HC74 ─ HW_ARMED              ├─ CAN RX (listen)
 INTERLOCK ────┤                          └─ MOTOR_PERMIT ─ PWM / K_PWR   ├─ SCOPE_TRIG → DHO804
 OC komparator ┤                                                          └─ konsola / SoftAP
 watchdog ─────┤
 supervisor ───┘
```

Elektronika i karta SD siedzą w kabinie albo na stole. W komorze silnika jest wyłącznie wiązka adaptera i sondy termopar. Płytek nie zostawiamy przy silniku.

## 3. Adaptery i wiązki

Trzy wiązki, trzy różne, mechanicznie niezamienne złącza na obudowie.

| Adapter | Gniazdo | Do czego | Ingerencja w tor |
|---|---|---|---|
| **L2 — back-probe** | LOGGER 12-stykowe | pierwsza sesja rejestracji | żadna: wtyczka CUD87 zostaje wpięta, sondy wchodzą od strony wiązki |
| **L1 — inline** | LOGGER 12-stykowe | rejestracja z pomiarem prądu | dwie dodatkowe pary styków przy CUD87 plus bocznik 5 mOhm |
| **T — test** | TEST 8-stykowe | sterowanie zaworem | wiązka samochodowa wypięta |

**Zacznij od L2.** Twoja hipoteza H6 oskarża styki żeńskie CUD87, rozpinane już trzy razy. Wpięcie adaptera inline jest operacją zaburzającą dokładnie tę usterkę — może ją wygasić na tydzień albo wywołać nową i nie będziesz wiedział, co zmierzyłeś. L2 mierzy te same pięć napięć bez ruszania złącza; traci tylko prąd uzwojenia. Po L2, gdy wiesz już, czy usterka siedzi w złączu, przechodzisz na L1 po prąd.

Pętla **TEST_PRESENT** zamyka się wyłącznie przez adapter T. Oba gniazda LOGGER mają krańcówkę NC rozwieraną po włożeniu wtyku. Krańcówki i TEST_PRESENT idą osobno do ekspandera (firmware widzi, co jest wpięte, i odmawia pracy, gdy wpięte są dwa adaptery naraz) **oraz** szeregowo do sprzętowej linii INTERLOCK. Przerwany przewód blokady = brak zezwolenia.

Styki mocy i przewody minimum 1,5 mm², sygnały 0,35–0,5 mm². Izolacja dobrana do temperatury miejsca prowadzenia. Odciążki na obu końcach każdej wiązki — ta kampania jest o przetartych przewodach, nie dokładaj własnych.

### Odczepy: jeden węzeł, jeden bank przekaźników

v1 miał osobny bank przekaźników dla każdego adaptera. v2 łączy odczepy obu adapterów w ten sam węzeł ADC, bo adaptery są fizycznie wyłączne, a rezystory ograniczające i tak siedzą osobno przy każdym złączu EGR.

```text
pin 1 adaptera L:  przewód ─ 2 x 150 kOhm ─┐
pin 1 adaptera T:  przewód ─ 2 x 150 kOhm ─┴─ K_MEAS (NO) ─ X1 ─ 100 kOhm ─ AGND
                                                             ├─ 220 pF ─ AGND
                                                             └─ ADC ch1
pin 3: identycznie                                           → ch2
piny 4/5/6: przewód ─ 2 x 49,9 kOhm ─ K_MEAS (NO) ─ X ─ 220 pF ─ AGND → ch3/ch4/ch5
```

Zostaje resztkowa droga: gdyby oba adaptery były wpięte naraz przy zasilonym TEST, 12 V z pinu 1 adaptera T dotarłoby przez 300 kOhm do węzła, a stamtąd przez kolejne 300 kOhm do pinu 1 adaptera L, czyli do wyjścia mostka ECU — **około 8 µA**. To nie jest zagrożenie, a sytuację i tak blokuje interlock, ale piszę to wprost, bo v1 deklarował brak takiej drogi.

K_MEAS ma styki NO: przy braku zasilania urządzenia odczepy są odłączone od ADC, więc wyłączony przetwornik nie zasysa prądu z wyjścia 5 V ECU przez diody ESD. Rezystory ograniczające montujesz **przy złączu EGR, przed długim przewodem i przed przekaźnikiem** — zwarcie w przewodzie albo w elektronice ma wtedy nie zewrzeć 5 V ECU, tylko oprzeć się o 100 kOhm (ok. 50 µA).

Prąd obu banków trafia na jeden kanał przetwornika przez **osobny przekaźnik `KCUR`, z własną cewką**. v2 próbowała zaoszczędzić ten przekaźnik i użyć drugiego bieguna KMEAS3 — a to jest przekaźnik DPDT z jedną cewką na oba zestyki, więc w trybie LOGGER odczep pinu 6 wymagałby styku NO, a prąd LOGGER styku NC tego samego przekaźnika. Nie da się. `KCUR` bez zasilania stoi w pozycji LOGGER (styk NC), co jest właściwym stanem domyślnym.

Konsekwencja rozdziału rezystorów na adaptery: **każdy bank ma własną kalibrację**. Profil trzyma `gain[2][8]`, `offset[2][8]`, `current_zero[2]` oraz osobną flagę **ważności prądu** na bank: przy sondach back-probe (L2) albo założonym mostku bocznikującym prąd nie jest mierzony i musi być pustą wartością, a nie zerem. Nie kalibruj jednego banku i nie przenoś wyniku na drugi — v1 to sygnalizował jako otwarty problem, tutaj jest rozwiązany strukturalnie.

### JP_SENSOR — zworka polaryzacji czujnika na adapterze TEST

v1 miał przekaźnik K_POL, który zamieniał 5 V i masę między pinami 5 i 6, bo zakładał, że sygnał pozycji siedzi na pinie 4. Przy sześciu możliwych permutacjach trójki 4/5/6 ten przekaźnik i tak nie pokrywa wszystkich przypadków, a przełączanie polaryzacji zasilania czujnika pod napięciem jest rzeczą, której i tak nie wolno robić. W v2 przekaźnik wypadł, a jego funkcję przejmuje **zworka na adapterze TEST**, ustawiana raz, przy odłączonym zasilaniu.

Listwa `JP_SENSOR` to trzy pary styków, po jednej na pin 4, 5 i 6. Zakładasz dwa mostki: jeden łączy pin wskazany przez profil jako zasilanie z `+5V_SENSOR`, drugi łączy pin masy z `AGND_SENSOR`. Trzeci pin zostaje wolny i jest mierzony jako sygnał pozycji. Opisz pozycję zworek na adapterze markerem po pierwszym IDENTIFY — to jest ustawienie na całe życie danego zaworu.

Pomyłkę wyłapuje **SENSOR_CHECK**: przed dopuszczeniem ruchu firmware wymaga, żeby przez 200 ms napięcia zgadzały się z mapowaniem z profilu (masa w −0,2…0,3 V, zasilanie 4,5…5,5 V nad nią, sygnał 0,2…4,8 V nad nią). Źle założona zworka daje `SENSOR_CHECK_TIMEOUT`, a nie ruch zaworu.

K_SENSOR zostaje i rozłącza **obie** linie przed zworką, więc przy każdym STOP, FAULT i wyjęciu adaptera czujnik jest całkowicie odcięty od naszego źródła.

### Kanał AUX

Ósmy kanał to zewnętrzny odczep na krokodylkach albo na banankach, z jumperem zakresu:

| Pozycja | Front-end | Zakres wejścia | LSB | Do czego |
|---|---|---|---|---|
| **HI** | 2 × 150 kOhm + RB4 100 kOhm, ADC ±10 V | ±40 V | 1,24 mV | linia ECV (H7), napięcie w dowolnym punkcie instalacji |
| **LO** | 2 × 49,9 kOhm, **RB4 odłączony**, ADC ±2,5 V | ±2,5 V | 76 µV | spadek na masie GUD09 względem B− (H2), spadek wzdłuż jednej żyły |

**`JP_AUX` musi być dwubiegunowy.** Drugi biegun odłącza dolny rezystor RB4 razem z gałęzią HI. v2 przełączała tylko wejście, zostawiając RB4 na wspólnym węźle — mnożnik w pozycji LO wychodził wtedy około 2,0 zamiast 1,02, czyli pomiar na masie GUD09 byłby zawyżony dwukrotnie.

Obie pozycje mają **osobną parę współczynników kalibracji** w profilu (`aux_gain[HI]`, `aux_gain[LO]`) — to dwa różne dzielniki, a nie jeden dzielnik z przełączanym zakresem, więc jedna kalibracja na oba nie ma sensu. Po przełożeniu zworki zgłoś to komendą `aux 0` (HI) albo `aux 1` (LO): firmware ustawia wtedy zakres przetwornika, wybiera właściwą parę współczynników i publikuje nową migawkę konfiguracji do logu.

Przekroczenie zakresu w pozycji LO jest nieszkodliwe: 100 kOhm szeregowo plus wewnętrzne clampy przetwornika ograniczają prąd wstrzykiwany do ułamka miliampera. Odczyt po prostu się nasyci.

**To jest najważniejszy pojedynczy kanał w tym urządzeniu.** Skop ma cztery wejścia i nie zrobi ośmiu naraz; tutaj masz pełny obraz EGR plus jeden punkt spoza niego, wspólnie próbkowany, z jednym odniesieniem masy. Korelacja „masa czujnika podskakuje dokładnie wtedy, gdy ECV zmienia wypełnienie" wychodzi z jednego pliku, bez zestawiania dwóch przyrządów.

## 4. Masa

AGND i DGND mają ciągłą płaszczyznę (albo, na płytce uniwersalnej, gwiazdę z jednego punktu i grubą plecionkę). Jedyne połączenie z powrotem mocy jest przy wejściu B−. Prąd silnika nie płynie przez masę przetwornika.

**SENSOR_GND z ECU nie łączy się z AGND** — mierzymy jego napięcie względem B−, o to w H2 chodzi.

Wspólna masa urządzenia oznacza, że **nie wolno podpinać uziemionego USB ani uziemionego oscyloskopu do innego punktu masy w trakcie pomiaru.** Do programowania przy samochodzie: izolowany USB albo laptop na baterii, bez podłączonej ładowarki. To ta sama pętla masy, przed którą ostrzega procedura v3 przy Kroku 2 — z tym że tutaj dotyczy całego urządzenia, nie tylko skopu. Gdy podpinasz SCOPE_TRIG do DHO804, skop musi być zasilony z power banku, a jego masa BNC to kolejne połączenie galwaniczne — traktuj je jak jedyne i nie dokładaj drugiego.

## 5. Zasilanie

```text
J_PWR BAT+ ─ F1 10 A ─┬─ LM74800EVM-CD ─ VPROT      (odwrotna polaryzacja + OVP)
                      D1 SM8S24CA (TVS dwukierunkowy)
J_PWR BAT− ───────────┴────────────────────────── GND_STAR

VPROT ─ F2 1 A ─ TSR 2-2450 → +5V_SYS ─ 1 Ohm / 470 µF → +5V_A (analog)
VPROT ─ F3 1 A ─ TSR 2-2433 → +3V3_IO (VDRIVE ADC, SD, MCP, CAN VIO)
+5V_SYS → pin 5V/VBUS płytki Waveshare (przez rozłączalny jumper)
VPROT ─ F4 5 A ─ K_PWR (NO) → VMOTOR → VNH5019 VIN
+5V_SYS ─ TPS2553 ─ K_SENSOR (NO) → +5V_SENSOR
```

Wejście dobiera się do dwóch źródeł: **zasilacz laboratoryjny z ograniczeniem prądu** (PL, stół) albo **przewód z bezpiecznikiem 10 A wprost na akumulator** (Hiszpania). Oba wchodzą w to samo J_PWR. Przy pracy z akumulatora na zgaszonym silniku pilnuj napięcia — firmware faultuje poniżej 9 V, ale rozsądna granica dla serii HOT-SOAK to 11,5 V na kanale VBAT.

Ochrona wejścia to **moduł LM74800EVM-CD**: dwa MOSFET-y, blokada odwrotnej polaryzacji i aktywne odcięcie nadnapięciowe. **Ustaw i zmierz OVP na 17,5–18,5 V** zgodnie z instrukcją modułu; nastawa fabryczna nie jest tu założeniem. Wyjście ma się odłączyć, a nie ograniczać napięcie liniowo.

v2 zastąpiła ten moduł pojedynczym P-MOS-em i TVS-em — i było to podwójnie błędne. Po pierwsze tranzystor był narysowany w orientacji zwykłego przełącznika (źródło od akumulatora), więc przy odwróconej baterii przewodziłaby dioda strukturalna; poprawnie jest **dren od akumulatora, źródło od strony chronionej**. Po drugie SM8S24CA przy znamionowym prądzie impulsu ogranicza do około 39 V, a TSR-y mają wejście do 36 V — sam TVS nie chroni więc przetwornic w warunkach, dla których został dobrany.

Wariant bez modułu, z jednym P-MOS-em w poprawnej orientacji, został w BOM jako opcja `OPT1`. Wybierając go rezygnujesz z odcięcia nadnapięciowego i bierzesz na siebie ocenę, czy to wystarczy dla Twojej instalacji. **To i tak nie jest kwalifikacja na load dump** — testy ISO wymagają generatora impulsów i określonej klasy instalacji.

TSR 2-2450 ma dolne wejście 6,5 V, więc podczas rozruchu może się zresetować. Nic tu nie musi przeżyć rozruchu — ma się bezpiecznie wyłączyć, a format pliku znosi urwany ostatni blok. Do rejestracji samego rozruchu potrzebny byłby osobny bufor energii albo drugie źródło.

Budżet 5 V: płytka 0,7 A szczytowo, analog 0,15 A, przekaźniki 0,15 A, CAN 0,1 A, czujnik do 0,1 A → 1,2 A, moduł ma 2 A. Budżet 3,3 V: SD 0,3 A szczytowo, logika i termopary 0,1 A. **Nie łącz +3V3_IO z wyjściem regulatora płytki Waveshare** — łączy je tylko masa. Na każdej szynie 100 nF przy układzie i 10 µF przy złączu; SD dodatkowo 100 µF.

VMOTOR: 1000 µF/50 V low ESR plus 1 µF plus 100 nF przy mostku, rezystor 2,2 kOhm/0,5 W rozładowujący, TVS SMCJ18A na VMOTOR–GND przeciw impulsom regeneracyjnym przy zmianie kierunku. TVS nie pochłonie dowolnej energii mechanicznej — warunek projektowy to energia zgromadzona w indukcyjności plus zwrotna poniżej zdolności kondensatora i TVS przy dopuszczalnym wzroście napięcia. **Zmierz szynę przy zmianach kierunku** w etapie 8 odbioru.

TPS2553 z R_ILIM 249 kOhm to ogranicznik rzędu 0,1 A, **nie** precyzyjne źródło 20 mA. Pierwsze zasilanie czujnika rób z limitu 20 mA na zasilaczu stołowym i podnoś dopiero po potwierdzeniu normalnego poboru. Wyjście FAULT tego układu wchodzi do blokady TEST. K_SENSOR rozłącza **obie** linie: 5 V i powrót AGND_SENSOR. Samo wyłączenie regulatora nie jest separacją.

## 6. Mostek i bezpieczeństwo

Moduł Pololu 1451 z VNH5019. OUTA → RSH_T → pin 1, OUTB → pin 3. INA/INB przez 330 Ohm z ekspandera, każde z 47 kOhm do GND. PWM z GPIO1 przez bramkę AND z MOTOR_PERMIT.

ENA i ENB w tym module są jednocześnie wejściami zezwolenia i wyjściami open-drain diagnostyki — **nie steruj ich push-pullem**. VDD modułu (zasila wyłącznie pull-upy ENA/ENB) podłącz do **MOTOR_PERMIT**, nie na stałe do 3,3 V; dorzuć 47 kOhm ENA–GND, 47 kOhm ENB–GND i 100 kOhm VDD–GND. Gdy PERMIT = 0 albo logika jest odłączona, oba EN opadają do zera; gdy PERMIT = 1, diagnostyka układu może ściągnąć EN bez walki z wyjściem GPIO.

| Rozkaz | INA | INB | PWM | ENA/ENB |
|---|---:|---:|---|---|
| kierunek + | 1 | 0 | duty | zwolnione |
| kierunek − | 0 | 1 | duty | zwolnione |
| STOP | 0 | 0 | 0 | wymuszone 0 |

PWM = 0 **nie jest** odłączeniem napędu — w VNH5019 wyłącza dolne klucze. STOP obejmuje EN i zasilanie. Kierunek „+" to dodatnie U(pin 1) − U(pin 3), co niekoniecznie znaczy „otwieranie"; kierunek otwierania ustala LEARN wzrokowo. Zmiana kierunku: duty = 0, EN = 0, 5 ms przerwy, zmiana INA/INB, dopiero narastanie.

INA/INB przeniesione z GPIO na ekspander MCP23017 — to zwalnia GPIO2 na linię SDI przetwornika. Kierunek nie jest funkcją bezpieczeństwa (bezpieczeństwo to PWM, EN i K_PWR, wszystko sprzętowo), a zmienia się tylko w oknie 5 ms z wyłączonym napędem, więc opóźnienie I²C rzędu 100 µs nic nie psuje.

### Linia SAFE_N — wire-AND, ale zrobiony do końca

v1 składał dziewięć sygnałów kaskadą sześciu układów 74HC08. v2 zastąpiła to jednym węzłem — i wpięła w niego wyjście push-pull bramki, co jest zwarciem przy każdym aktywnym błędzie. v3 zostawia ideę i naprawia wykonanie:

```text
                         3V3
                          │
                    SW_STOP (NC, grzybek)      ← JEDYNA gałąź pull-upu
                          │
                        10 kOhm
                          │
   ┌──────────┬───────────┴───────────┬──────────────┬─────────────┬──────────────┐
   │          │                       │              │             │              │
 SAFE_N   OC_OK (o.c.)      OKNO_5V_A (o.c.)   SUP_3V3 (o.d.)  INTERLOCK   Q8 drain (o.d.)
   │                                                                          ↑
 100 kOhm do GND                                        74HC123 Q → 74HC14 → brama 2N7002
   │
   └─ /CLR 74HC74   (D = 3V3, /PRE = 3V3, CLK = ARM po debounce, Q = HW_ARMED)
```

Na węźle wiszą **wyłącznie wyjścia otwarte**: dwa kanały komparatora prądu, dwa kanały okna 5V_A, supervisor 3V3_IO i pętla interlock. Watchdog ma wyjście push-pull, więc dostaje własny **inwerter 74HC14 i tranzystor 2N7002** — dopiero jego dren wolno dołączyć do węzła. Żadna bramka AND nie steruje już SAFE_N.

**Pull-up jest dokładnie jeden i idzie przez styk NC grzybka.** v2 dokładała drugi, lokalny pull-up przy komparatorze prądu, co unieważniało cały mechanizm: po otwarciu grzybka węzeł zostawał wysoki. Teraz zwolniony grzybek zamyka obwód i węzeł jest wysoki, a wciśnięty grzybek **albo przerwany przewód** zostawia tylko rezystor 100 kOhm do masy — awaria przewodu wygląda jak wciśnięty STOP, czyli właściwie.

74HC74 resetuje się asynchronicznie do Q = 0. Ustąpienie błędu **nie uzbraja z powrotem** — potrzebne jest nowe zbocze z fizycznego przycisku ARM (10 kOhm/100 nF plus 74HC14). Program nie ma wyjścia, którym mógłby ten latch ustawić.

### Zezwolenia, bramka po bramce

Trzy i cztery warunki nie mieszczą się w jednej bramce dwuwejściowej — v2 miała tu dziurę w liście połączeń. Rozpisane jawnie (przyporządkowanie w `hardware/connections.csv`):

| Wynik | Bramka | Wejścia |
|---|---|---|
| — | U10a | HW_ARMED (Q latcha) · MCU_ARM (GPIO39) |
| **MOTOR_PERMIT** | U10b | wyjście U10a · INTERLOCK (GPIO42) |
| **PWM_OUT** | U10c | PWM (GPIO1) · MOTOR_PERMIT |
| — | U10d | SENSOR_ENABLE (MCP A3) · TEST_KEY (MCP B0) |
| — | U12a | wyjście U10d · INTERLOCK |
| **cewka K_SENSOR** | U12b | wyjście U12a · SAFE_N |

MOTOR_PERMIT zasila pull-upy ENA/ENB modułu mostka i sterownik cewki K_PWR. Razem sześć bramek, czyli dwa układy 74HC08, plus jeden 74HC14, jeden 74HC74, jeden 74HC123 i jeden 2N7002.

### Nadzór napięć — wrócił

v2 usunęła okno 5V_A jako redundancję. To był błąd, i to z mocniejszego powodu niż sama redundancja: **z szyny 5V_A wyprowadzone są progi komparatora przetężeniowego oraz odniesienie INA240**. Dryf tej szyny przesuwa jedyne sprzętowe zabezpieczenie nieznanego silnika zaworu, i to bez żadnego objawu — pomiar prądu przesuwa się razem z progiem, więc nic nie wygląda podejrzanie.

W v3 są więc: **okno 5V_A** (drugi TLV1702, progi 1,9 V i 2,1 V względem 0,4 × 5V_A, odniesienie ADR4525), **supervisor 3V3_IO** (TPS3808G33) i **okno prądu**. Okno VPROT 9–17 V pozostaje w firmware (kanał VBAT, fault `SUPPLY`) plus UVLO samego VNH5019 — przy zgaszonym silniku pracujesz z akumulatora albo z zasilacza, więc dynamika tej szyny jest łagodna.

Projekt nadal nie deklaruje odporności na dowolną pojedynczą awarię ani żadnej klasy SIL/ASIL.

### Komparator prądu

INA240A2 OUT → 1 kOhm → I_FILT, 1 nF I_FILT–GND. TLV1702-Q1 zasilany z 5V_A:

* kanał LOW: IN+ = I_FILT, IN− = V_LOW (1,5 V);
* kanał HIGH: IN+ = V_HIGH (3,5 V), IN− = I_FILT;
* wyjścia open collector zwarte w OC_OK i wprost w SAFE_N — **bez własnego pull-upu**, bo jedyny pull-up idzie przez grzybek.

Dzielniki z 5V_A: LOW przez 7 kOhm/3 kOhm, HIGH przez 3 kOhm/7 kOhm, 0,1 %, 10 nF. REF1 = 5V_A, REF2 = AGND → środek 2,5 V, 0,25 V/A → **twardy próg ±4 A**. Zworka serwisowa ±8 A (9 kOhm/1 kOhm i 1 kOhm/9 kOhm) dopiero po kwalifikacji prądu zaworu; domyślnie nieobsadzona. Rozrzut szyny 5 V skaluje próg — dolicz tolerancje INA, bocznika, dzielników i komparatora, a kryterium odbioru to **pomiar wstrzykniętym sygnałem**, nie obliczenie. Cel: wyłączenie bramki poniżej 20 µs od utrzymanego przekroczenia. Filtr nie może zamaskować zwarcia.

### Watchdog

74HC123 retriggerowalny, A = 0, B = GPIO21, /CLR = SUP_3V3. R = 220 kOhm, C = 1 µF jako punkt startowy ok. 0,1 s — **zmierz** i dobierz do 50–150 ms. Heartbeat przełącza task bezpieczeństwa co 10 ms i **tylko wtedy, gdy ma świeże dane z ADC i zdrowy stan**. Nie generuj go sprzętowym LEDC, bo przeżyje zawieszenie taska i watchdog przestanie cokolwiek znaczyć.

### Prądy i boczniki

RSH_L i RSH_T: 5 mOhm, 4-terminal, 2 W, 1 %, TCR ≤ 50 ppm/K. Kelvin do INA240A2 przez dopasowane 10 Ohm, opcjonalnie 1 nF różnicowo, bez asymetrycznych kondensatorów do masy. Bocznik LOGGER: IN+ po stronie ECU pinu 1, IN− po stronie zaworu. Bocznik TEST: IN+ od OUTA. VS = 5V_A, REF1 = 5V_A, REF2 = AGND, OUT przez 100 Ohm do multipleksera banku.

Wyjścia obu INA idą na **jeden** kanał ADC przez styk przekaźnika sterowany wyborem banku — w danej chwili aktywny jest tylko jeden adapter, więc drugi pomiar prądu i tak byłby martwy (v1 marnował na to kanał, który w v2 jest kanałem AUX).

I = (V_OUT − V_ZERO) / 0,25. **V_ZERO mierzysz i zapisujesz do profilu** po rozgrzaniu toru, przy pewnym zerowym prądzie — nie w trakcie pracy ECU i nie jako założone 2,5 V. Przy REF = 5V_A/2 błąd szyny ±2 % to ±50 mV, czyli ±0,2 A; przy soft-limicie 1,5 A to 13 % i to jest realny powód, dla którego v1 mógłby przerywać ruch bez przyczyny albo nie przerwać, gdy trzeba. Przy 8 A spadek na boczniku 40 mV, moc 0,32 W.

Bocznik i dwie pary styków adaptera L1 **zmieniają obwód**. To nie jest pomiar nieinwazyjny; stąd L2 jako pierwszy krok i wymóg porównania „fabryczna wiązka → adapter z mostkiem bocznikującym → adapter z bocznikiem" przed jakimkolwiek wnioskiem.

Ujemny impuls common-mode poniżej −4 V wychodzi poza zakres pracy INA240 — oceń skopem, jak wygląda recyrkulacja na pinie 1 w aucie, zanim uznasz odczyt prądu za wiarygodny w każdej fazie PWM.

## 7. AD7606B — tryb wybierany przy kompilacji

| Kanał | v[] | Sygnał | Zakres | Przelicznik |
|---|---|---|---|---|
| 1 | 0 | pin 1 (napęd A) | ±10 V | code × FS/32768 × 4,06 |
| 2 | 1 | pin 3 (napęd B) | ±10 V | jw. |
| 3 | 2 | pin 4 | ±10 V, po IDENTIFY ±5 V albo ±2,5 V | × 1,01996 |
| 4 | 3 | pin 5 | ±10 V, po IDENTIFY ±5 V albo ±2,5 V | × 1,01996 |
| 5 | 4 | pin 6 | ±10 V, po IDENTIFY ±5 V albo **±2,5 V** | × 1,01996 |
| 6 | 5 | prąd aktywnego banku | ±5 V | (V − zero) / 0,25 |
| 7 | 6 | VBAT (VPROT) | ±10 V | × 6,0796 |
| 8 | 7 | AUX | HI ±10 V / LO ±2,5 V, zgłaszane komendą `aux` | × 4,06 / × 1,01996 |

Który z kanałów 3/4/5 dostanie ±2,5 V, wynika z **mapowania po identyfikacji**: ten, na którym siedzi masa czujnika. Dopóki mapowanie jest nieznane, wszystkie trzy chodzą na ±10 V. Po to jest tu software mode: przy ±2,5 V masz **76 µV/LSB**, więc spadek 30 mV na masie czujnika to około 400 działek przetwornika, a nie 100.

Wspólne ustawienia: AVCC = 5V_A, VDRIVE = 3V3_IO, PAR/SER SEL = 1, STBY = 1, REF SELECT = 1 (odniesienie wewnętrzne), CONVST_A i CONVST_B zwarte, DOUTA jedyne używane, pozostałe DOUT niepodłączone. RESET impulsem HIGH ≥ 10 µs na starcie. Kondensatory przy AVCC/VDRIVE, 1 µF na REGCAP, 10 µF na buforze odniesienia i połączenia REFCAPA/B **dokładnie według rysunku typowej aplikacji** w datasheecie. SPI mode 2: zegar spoczynkowo wysoki, odczyt na zboczu opadającym.

### Tryb jest decyzją, nie zgadywaniem

v2 próbowała wykryć software mode w czasie pracy i przy niepowodzeniu „po cichu" wracać do hardware mode — zostawiając przy tym w profilu zakresy, których sprzęt nie przyjął. Przy sprzętowym ±10 V i programowym ±5 V zero prądu wychodziło wtedy jako −5 A. W v3:

* tryb ustawiasz w `menuconfig` (`CONFIG_EGR_ADC_SOFTWARE_MODE`, domyślnie włączony);
* **software mode wymaga AD7606B i zworek OS[2:0] = 111** — samo pisanie po SPI nie wprowadzi układu w tryb rejestrów;
* każdy zapis rejestru jest weryfikowany odczytem, a ramka odczytu ma prefiks `01` (0x4000), nie `0x8000` jak w v2;
* po konfiguracji zapis pod adres 0x00 wraca do strumienia danych;
* **niepowodzenie jest błędem**: `adc_config_ok = false` blokuje TEST faultem `ADC_CONFIG` i trafia do każdego rekordu w logu;
* do przeliczeń służą wyłącznie zakresy **potwierdzone odczytem**, nie żądane przez profil.

Adresy i układ bitów rejestrów **zweryfikuj z datasheetem swojej rewizji** — w `board.c` są zebrane w jednym `enum` z komentarzem. Weryfikacja odczytem jest siatką bezpieczeństwa, nie dowodem poprawności.

**Hardware mode** (`CONFIG_EGR_ADC_SOFTWARE_MODE=n`): RANGE = 1, czyli ±10 V na wszystkich kanałach, OS[2:0] ze zworek, odczyt **ośmioma osobnymi ramkami 16-bit z CS między nimi** — to nie jest jedna ramka 128-bit, pomylenie tego daje powtarzające się kanały. W tym trybie tracisz ±2,5 V na masie czujnika i pomiar miliwoltów wraca do skopu przy 20 mV/div, jak w procedurze v3.

**Nie myl płytki AD7606 z AD7606B.** Pierwsza nie ma trybu rejestrów i ma inną impedancję wejściową, więc i inną kalibrację. Z AD7606 zbuduj wariant hardware mode świadomie, a nie licząc na to, że firmware sam się zorientuje.

Nominalne wzmocnienia wynikają z rezystorów i typowego R_IN = 5 MOhm: napęd 4,06 (nie 4,00), czujnik 1,01996, VBAT 6,0796. To wartości **wyjściowe do kalibracji**, nie wynik. Kalibruj cały tor w co najmniej trzech punktach, osobno dla każdego banku i osobno dla obu pozycji zworki AUX.

### Zmiana konfiguracji w trakcie sesji

Zakresy, bank, zero prądu i mapowanie mogą się zmienić w środku sesji. Robi to **jedno zadanie**, które zatrzymuje próbkowanie, czeka na wygaszenie akwizycji, ustawia i weryfikuje zakresy, buduje migawkę w nieaktywnym buforze i dopiero potem przestawia indeks. Każda próbka niesie `config_id` tej migawki, a migawka trafia do `events.ndjson`. Dzięki temu analiza offline stosuje dokładnie tę kalibrację, która obowiązywała w danej chwili — szczegóły w `04-firmware-logi.md`.

Pasmo pojedynczego RC: napęd ok. 9,8 kHz, czujnik ok. 7,4 kHz, plus filtr analogowy przetwornika. Przy 2 kS/s to rejestracja trendów i zdarzeń milisekundowych, **nie** wierny kształt impulsu PWM — i dlatego pojedynczej próbki prądu nie wolno brać za wartość średnią ani skuteczną przebiegu PWM. Do kształtu i zboczy służy skop.

## 8. ESP32-S3 — wyprowadzenia

| Funkcja | GPIO | Uwagi |
|---|---:|---|
| PWM napędu | 1 | bramka AND z MOTOR_PERMIT |
| ADC SDI | **2** | software mode; w hardware mode zostaw na stałe 0 |
| SCOPE_TRIG | **38** | impuls 20 µs → wejście wyzwalania oscyloskopu; odłącz DIN pokładowego RGB |
| SPI3 SCLK / MOSI / MISO | 4 / 5 / 6 | SD plus 2 × MAX31856 |
| SD CS | 7 | 10 kOhm pull-up |
| TC1 CS / TC2 CS | 8 / 16 | 10 kOhm pull-up |
| ADC SCLK / DOUTA / CS | 9 / 11 / 12 | SPI2, bez translatorów 5 V |
| ADC CONVST / BUSY | 13 / 14 | BUSY wejście 3,3 V, krótki przewód |
| I²C SDA / SCL | 10 / 15 | 4,7 kOhm pull-up do 3V3_IO |
| CAN TX / RX | 17 / 18 | TCAN1051V-Q1, listen only |
| heartbeat | 21 | do 74HC123 |
| MCU_ARM | 39 | zewnętrzny 47 kOhm pull-down |
| HW_ARMED | 40 | Q latcha, 10 kOhm pull-down |
| MARK | 41 | przycisk do GND, 10 kOhm pull-up, 100 nF |
| INTERLOCK | 42 | wysoki tylko przy dozwolonym TEST |
| UART0 | 43 / 44 | zarezerwowane dla pokładowego CH343 |
| USB | 19 / 20 | zarezerwowane |

GPIO 0/3/45/46 to piny strapujące — nie używamy. 35/36/37 na tym module są NC (zajęte przez PSRAM OPI). 47/48 pracują na 1,8 V — nie podłączamy do logiki 3,3 V. To są numery **GPIO**, nie numery nóżek listwy; sprawdź rewizję swojej płytki i ciągłość do modułu, zanim zlutujesz podstawkę. Waveshare publikuje wspólny schemat rodziny N8R8 — nie przecinaj niczego na podstawie numeracji z innej płytki.

**MCP23017**, adres 0x20, A0–A2 = GND, RESET z pull-upem 10 kOhm.

Port A (wyjścia, każde przez stopień tranzystorowy z pull-downem 100 kOhm — ekspander nie zasila cewek):

| Bit | Funkcja |
|---|---|
| A0 | ADC_RESET |
| A1 | MEAS_EN (bank odczepów) |
| A2 | MEAS_BANK (0 = LOGGER, 1 = TEST; multiplekser prądu) |
| A3 | SENSOR_ENABLE |
| A4 | rezerwa |
| A5 | MOTOR_INA |
| A6 | MOTOR_INB |
| A7 | STATUS_LED |

Port B (wejścia):

| Bit | Funkcja |
|---|---|
| B0 | TEST_KEY (przełącznik kluczykowy) |
| B1 | SENSOR_FAULT_N (TPS2553) |
| B2 / B3 | ENA_DIAG / ENB_DIAG mostka |
| B4 | LOG_PRESENT_N (krańcówki gniazd LOGGER) |
| B5 | TEST_PRESENT (pętla adaptera TEST) |
| B6 | przycisk rezerwowy |
| B7 | STOP status (podgląd grzybka) |

Bank pomiarowy i zasilanie czujnika nigdy nie przełączają się „na gorąco": `board_mode()` najpierw zeruje cały port A, czeka 100 ms i dopiero ustawia nowy stan. E-STOP, GPIO39, latch i blokady nie zależą od I²C.

## 9. Temperatura, CAN, SCOPE_TRIG

**MAX31856 ×2** na SPI3, mode 1, ≤ 1 MHz, typ K, filtr 50 Hz, konwersje ciągłe. T+/T− zgodnie z polaryzacją przewodu kompensacyjnego, złącze kompensacyjne blisko układu, poza nawiewem i przetwornicą. Sondy z izolowanym złączem pomiarowym, ekran jednostronnie do obudowy. **TC1 na korpusie napędu zaworu, TC2 na kołnierzu części gazowej.** To nie jest temperatura uzwojenia i nie udawaj, że jest — GDS mówi o temperaturze silnika aktuatora, a ty mierzysz obudowę. Błędy open-circuit logujesz, nie zastępujesz zerem.

**TCAN1051V-Q1**: VCC z 5V_SYS, VIO z 3V3, TXD 17, RXD 18, S z pull-upem 10 kOhm do VIO. Przełącznik LISTEN wymusza S = 1 fizycznie, a sterownik TWAI dodatkowo pracuje w trybie listen-only. OBD: 6 = CANH, 14 = CANL, 4 = masa odniesienia, **5 niepodłączony, 16 nie zasila niczego**. PESD2CAN do lokalnej masy przy złączu, krótki odczep skrętką, bez terminacji w samochodzie. Start od 500 kbit/s.

Bierne CAN **nie gwarantuje obrotów** — gateway może ich nie rozgłaszać. Firmware dekoduje odpowiedzi single-frame 0x7E8–0x7EF (PID 0C → RPM = (256A+B)/4) i **nic nie nadaje**; obroty mogą przyjść z Twojego równoległego skanera, który i tak odpytuje ECU. Brak obrotów daje `rpm = null`, nie zero. Nie wymyślamy ID ani DBC dla tego rocznika.

**SCOPE_TRIG** — GPIO38 przez rezystor 330 Ohm na gniazdo BNC, masa BNC do AGND. Impuls dodatni 20 µs przy każdym triggerze firmware.

Dwie rzeczy, o których trzeba wiedzieć, zanim się na tym oprzesz. Po pierwsze **DHO804 nie ma osobnego wejścia wyzwalania** — w tej rodzinie ma je wariant dwukanałowy, więc na czterokanałowym musisz oddać jeden kanał analogowy, zwykle CH4. Konfiguracja A z procedury v3 używa wszystkich czterech, więc przy wpiętym SCOPE_TRIG rezygnujesz z jednego sygnału; najmniej kosztuje zwykle pin 3. Po drugie **impuls nie powstaje w chwili początku zjawiska**: `stall` z definicji czeka 200 ms, `open` 50 ms, a pozostałe detektory działają po przeliczeniu próbki. Ustaw na skopie odpowiednią głębokość przed wyzwoleniem (pre-trigger), inaczej złapiesz skutek zamiast przyczyny.

Mimo to warto: skop ma pasmo, ale nie wie, kiedy patrzeć; rejestrator wie, kiedy, ale nie ma pasma.

## 10. Opcjonalny interfejs na telefon

ESP32-S3 podnosi **SoftAP z hasłem** i serwuje jedną stronę: pozycja, ratio, prąd, napięcia, temperatury, stan oraz przyciski OPEN/CLOSE/GOTO/SWEEP/FRICTION/MARK/STOP. Przy masce, z telefonem w ręku, „machanie zaworem" i patrzenie na prąd zerwania staje się jednoosobowe.

Reguły, od których nie ma odstępstwa:

* Radio startuje **wyłącznie** w stanie SAFE lub READY i **wyłącznie** przy wpiętym adapterze TEST. Wejście w LOGGER natychmiast wyłącza Wi-Fi — pomiar w aucie idzie bez radia, bez wyjątków.
* Strona nie ma dostępu do `learn`, `save`, `bind` ani zmiany kalibracji. STOP jest zawsze dostępny.
* **Fizyczny ARM obowiązuje tak samo.** Telefon nie ruszy zaworem, jeśli sprzętowy latch nie jest uzbrojony. To nie jest zdalne sterowanie — to zdalny wyświetlacz z przyciskami, za którym stoi ta sama blokada sprzętowa.
* Hasło AP ustawiasz w menuconfig. Nie zostawiaj otwartej sieci przy urządzeniu, które porusza silnikiem.

Funkcja jest opcjonalna (`CONFIG_EGR_WIFI_UI`), domyślnie wyłączona, a konsola po USB pozostaje interfejsem rozstrzygającym.
