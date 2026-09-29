# P02-HOLD C1 — obwód podtrzymania i kontrakt integracyjny

Decyzja po R2: **P01 zachowuje odcięcie, LOGGER otrzymuje rezerwę zasilania na P02.**
Ten katalog określa obwód i granice do włączenia w następny projekt P02. Nie jest
kompletną nową płytką P02 ani zastępstwem jej aktualnej netlisty w rewizji6.1.
P01 nie potrzebuje nowych pinów, żeby przyjąć ten wariant.

## Połączenia

```text
                        D_OR: STPS20100CT
VPROT ------------------> A1
                              K -------- VLOG_RES --> F2 --> TSR2-2450 --> 5V_SYS
HOLD_FUSED -------------> A2                      \--> F3 --> TSR2-2433 --> 3V3_IO
     |
     +-- F_HOLD T2A -- HOLD_STORE -- 3 × 22000uF/35V -- GND
                           |
                           +-- R_BLEED 4k7/0.5W -- GND

VPROT -- R_CHARGE 47R/25W -- A1+A2 D_CHARGE K -- HOLD_FUSED
VLOG_RES -- C_BUS 22uF/50V -- GND

VPROT --------------------- istniejąca gałąź F4 / KPWR / silnik
```

STPS20100CT:1=A1,2=K,3=A2, tab=K. W D_OR anody są **oddzielnymi źródłami**;
w D_CHARGE anody1+3 są zwarte. D_OR nie wolno zamienić na wariant ze wspólną anodą.
F_HOLD przy dodatnim wyjściu banku ogranicza energię oddawaną do zewnętrznego zwarcia;
nie jest obietnicą ochrony przed każdą usterką wewnętrzną samego kondensatora.
Wszystkie zaciski banku osłonić i mechanicznie odciążyć.

F2/F3 zostają1A jak w6.1, lecz ich wejścia przechodzą z VPROT na VLOG_RES.
Nie zmieniać J_SUPPLY, J_VMOTOR, VPROT_SENSE, F4 ani źródła KPWR. Odpowiednie zmiany
połączeń do przyszłego P02 są jawne w contract.json. Wymagany prąd i I²t F2/F3/F_HOLD
sprawdzić przy uruchamianiu; bank zmienia źródło energii zwarcia za nimi.

## Co jest podtrzymywane

CORE, SD, ADC z referencją i torem wejściowym, pomiar prądu LOGGER-a, temperatury,
CAN i logika safety. Korzystają z dotychczasowych5V_SYS/3V3_IO po przebudowie P02.
Silnik, jego kondensator1000µF i KPWR nie korzystają z rezerwy. SAFE_N z P01 nadal
rozbraja sprzętowy latch, mimo że logika zachowuje zasilanie; powrót wymaga ARM.
Przejście banków/DAQ oraz awaria samego sensora ECU mogą unieważniać próbki:
podtrzymanie napięcia nie zastępuje flag SAMPLE_INVALID/SAMPLE_GAP.

## Parametry i warunki

- Wymagana pojedyncza przerwa zasilania gałęzi logiki:50ms.
- Moc na VLOG_RES:≤6W, **łącznie ze stratami przetwornic** i wszystkimi modułami.
- Przed zdarzeniem HOLD_STORE≥9,5V; w czasie przerwy VLOG_RES≥7V.
- Ceff całego banku≥52,8mF w0…50°C; wartość nominalna66mF.
- Spadek od napięcia wewnętrznego kondensatorów do VLOG_RES (diody, ESR, bezpiecznik,
  przewody)≤1,2V przy największym prądzie. To kryterium odbioru, nie założenie,
  że każdy kondensator ma znane ESR w temperaturze0°C.
- Zapas na upływ i bleeder0,15W. Wszystkie te granice muszą być spełnione jednocześnie.

Niezależny rachunek przy tych granicach daje około85ms, wobec wymogu50ms.
Nie zapewnia wielosekundowego rozruchu ani nieograniczonej serii zakłóceń.
Minimalne wejście TSR2-2450 wynosi6,5V; przyjęto7V jako margines projektowy.
Źródło: [TRACO TSR2](https://www.tracopower.com/products/tsr2.pdf).

## Ładowanie i gotowość

R_CHARGE ogranicza dodatkowy prąd do około0,403A przy18V dla -5% rezystancji.
Bank nie trafia bezpośrednio do limitu220µF P01. C_BUS22µF oraz pojemności wejściowe
przetwornic i wszystkie bezpośrednio dostępne kondensatory nadal liczą się do niego.
R_CHARGE ma być HSA2547RJ, mocowany do osobnej blachy aluminiowej, z dala od banku;
warunki mocy i temperatury zgodne z kartą TE. Nie stosować zamiennika47Ω/0,5W.
Moc przy18V≤7,26W; przy krótkim32V≤22,94W. Sprawdzić temperaturę także przy zwartym
banku — to odmienny warunek niż zwykłe doładowanie. OVP P01 nie zostało pominięte.

Po włączeniu albo większym rozładowaniu: stan „rezerwa niegotowa”. Kwalifikacja
obejmuje stabilne VPROT≥11,5V przez co najmniej15s **oraz pomiar HOLD_STORE≥9,5V**.
Sam timer nie dowodzi naładowania. W prototypie osobnego obwodu sprawdza się to
na TP; przy projektowaniu P02 dodać lokalny pomiar/status rezerwy dostępny dla CORE.
Nie podłączać nowego sygnału do przypadkowego zajętego GPIO ani nie przeciążać
istniejącego PSU_OK dodatkowym znaczeniem. Jego funkcja pozostaje nadzorem szyn.

Podtrzymanie i moc są określone dla LOGGER-a. TESTER może być uruchamiany osobno
bez aktywnej rezerwy, ale ARM nadal zależy od prawidłowego VPROT i safety.
Przy zasilaniu z USB zabronione jest niekontrolowane zasilanie wsteczne5V_SYS;
to wymaga sprawdzenia na rzeczywistej płytce CORE podczas integracji.

## Montaż etapami

Obwód można najpierw zbudować osobno: pole około120×60mm dla trzech kondensatorów
Ø35mm, miejsce na diody/fuse i przykręcany zewnętrznie R_CHARGE. Części mocy łączyć
przewodem1mm², nie samymi cienkimi paskami płytki uniwersalnej. Kondensatory mają
snap-in P10mm; potrzebne odpowiednie otwory lub dedykowany adapter, nie wciskanie
w raster2,54mm. Zachować miejsce na zawory bezpieczeństwa. Duże elementy mocować.

Masy wspólne, wejście VPROT i wyjście VLOG_RES jednoznacznie oznaczone. Wiązka do
P02:150mm, 3×AWG18 (VPROT/GND/VLOG_RES), lutowana PTH przy obwodzie HOLD z kotwami
12,5mm; po stronie P02 wtyk 3p MSTB 5,08. Ten wariant służy próbom stołowym.
Pinout roboczy: 1=VPROT, 2=GND, 3=VLOG_RES. Jest mechanicznie zgodny z SUPPLY,
więc sam napis HOLD nie zapobiega pomyłce. Przy projektowaniu kompletnej P02
zintegrować obwód na niej albo dobrać i sprawdzić dodatkowe kodowanie złącza.
Nie zatwierdzać wspólnego montażu w obudowie z zamienialnymi wtykami HOLD/SUPPLY.
To wewnętrzny interfejs P02, nie drugi przewód zasilający P01 ani złącze silnika.
Bank rozładowuje się przez4k7 powoli: do<1V może być potrzebne około19min przy
górnej tolerancji i początkowych18V. Przed pracą zmierzyć napięcie. Do serwisowego
rozładowania użyć zewnętrznego rezystora100Ω/10W przez izolowane przewody;
nie zwierać zacisków. Energia przy32V i górnej tolerancji może przekraczać40J.

## Odbiór obwodu

1. Bez P01: zasilacz ograniczony, kontrola pinów/polaryzacji; VLOG_RES, ładowanie,
   maksymalny prąd i brak oddawania energii do wyłączonego wejścia.
2. Zmierzyć Ceff, upływ oraz spadek całej gałęzi w0/25/50°C. Ustalić rzeczywistą
   moc modułów przy zapisie SD/Wi-Fi/CAN. Powyżej6W ponownie dobrać bank i testy.
3. Po naładowaniu odłączyć źródło na50ms przy obciążeniu6W. VLOG_RES≥7V; po dołączeniu
   docelowych przetwornic również ich wyjścia mają zachować parametry odbiorników.
4. Długi zanik ma wyczerpać rezerwę w sposób kontrolowany. Sprawdzić zimny start,
   zwarcie wejścia przy naładowanym banku, ponowne ładowanie i bezpieczniki.
5. Dopiero wtedy połączyć z P01 i wykonać sekcję7.7 ODBIOR. Powtórzyć pojedyncze
   oraz seryjne zakłócenia, zapis danych, safety i zasilanie USB.

Nie gwarantujemy dokończenia każdej operacji SD po całkowitej utracie zasilania.
Firmware ma raportować rzeczywisty powód resetu MCU oraz rozpoznawalne przerwy,
bez nazywania każdego restartu „OVP”. Pełne wdrożenie monitorowania rezerwy,
interfejsu i firmware należy do etapu P02/CORE; nie zmieniono działającej bazy6.1.
