# P04-R1: działanie i uzasadnienie

## Granice modułu

P04 otrzymuje 3V3_IO z P02 i pracuje we wspólnej masie urządzenia. 5V_SYS na J1.1 dochodzi tylko do TP13. P04 nie ma połączenia z 12 V, silnikiem ani liniami EGR. STOP i ARM są fizycznymi stykami P11. P04 daje logikę 3,3 V do P07/P08 i zwrotnie HW_ARMED/INTERLOCK do CORE. Nie jest to izolacja galwaniczna.

Docelowy pobór tej płytki przy wolnych sygnałach to pojedyncze–kilkanaście mA, do potwierdzenia pomiarem; rezerwujemy 30 mA na P02. Sumaryczny statyczny prąd 22 rezystorów wejść, obciążeń logicznych, LED i obwodów baz pozostaje poniżej tego budżetu. Na stole początkowy limit 50 mA; nie zwiększać go w odpowiedzi na zwarcie. Ta rezerwa nie obejmuje obcych obciążeń dołączonych do J7/J8 ani prądu dynamicznego przy nadmiernej częstotliwości PWM.

## Tor zgody

Wszystkie wejścia do buforów mają domyślne L. Za każdym kanałem 74LVC125AD jest drugi pulldown, aby wyjęcie adaptera nie pozostawiło wejścia bramki w powietrzu. Bufory Nexperia mają Ioff; nie zamieniać ich na HC125. TEST_KEY i MECH_OK są sygnałami ze styków, zasilanymi z P04, a nie z obcej aktywnej domeny.

```
MODULES_OK = PSU_OK & DAQ_OK & DRIVE_OK & SENSOR_OK & CORE_LINK & PG_LINK
INTERLOCK = MODULES_OK & MECH_OK & TEST_KEY
SUP_OK = SUP_N_P04 & LOCAL_SUP_N
SAFE_N = STOP_CLOSED & INTERLOCK & SUP_OK & WD_Q & brak zewnętrznego zwarcia SAFE_N do GND
HW_ARMED = zatrzask D ustawiany zboczem fizycznego ARM; asynchronicznie kasowany przez SAFE_OK
MOTOR_PERMIT = HW_ARMED & MCU_ARM_P04 & INTERLOCK & SAFE_OK
PWM_OUT = PWM_P04 & MOTOR_PERMIT
SENSOR_PERMIT = SENSOR_ENABLE_P04 & TEST_KEY & INTERLOCK & SAFE_OK
```

READY oznacza sprawność/obecność modułu przed włączeniem jego wyjścia. Nie wolno uzależnić DRIVE_OK od KPWR ani SENSOR_OK od SENSOR_PERMIT: powstałaby blokada rozruchu. Brak któregokolwiek READY blokuje też sam czujnik, tak jak w bazie projektu. Do prób pojedynczej P04 te sygnały dostarcza P00.

P11 MECH_OK już zawiera TEST_KEY, styki obecności obu złączy LOGGER i pętlę TEST. Dodatkowe jawne AND z TEST_KEY w P04 wykorzystuje wolną bramkę U7C. To lokalne potwierdzenie warunku; nie oznacza, że bazowa P11 nie sprawdzała klucza.

## SAFE_N i reset

R4 10 kΩ podciąga SAFE_N do 3,3 V przez fizyczny STOP NC. R5 100 kΩ ściąga do masy po przerwaniu STOP. Q1–Q3 są otwartymi kolektorami: brak heartbeat, reset zasilania lub brak interlocku ściąga SAFE_N. P01 i przyszła P07 mogą jedynie dołączyć własne otwarte kolektory. Nie wolno podawać tutaj stanu H z GPIO ani wyjścia push-pull.

Nominalnie SAFE_N w H ma 3,3 × 100/(100+10) = 3,00 V, a prąd podciągania przy L wynosi do ok. 0,35 mA przy maksymalnym założonym 3V3_IO=3,465 V i R4 −1%. Pojedynczy 2N3904 ma bazę zasilaną przez 10 kΩ i pulldown 100 kΩ. Nawet przy 2,4 V na wyjściu bramki oraz VBE=0,8 V pozostaje ok. 0,15 mA bazy: wymuszone β poniżej 3 dla tego obciążenia. Rzeczywisty VOL należy zmierzyć; cel ≤0,25 V.

SAFE_N jest wspólnym, stosunkowo wysokoimpedancyjnym sygnałem. Nie dodawać LED ani dodatkowych pulldownów na tej sieci bez ponownego przeliczenia. Docelowo zmierzyć H ≥2,7 V po przyłączeniu P01 i P07. Spadek STOP zależy od pojemności wiązki i R5; nie jest identyczny czasowo z aktywnym zwarciem kolektora.

U2E/U2F odtwarzają SAFE_OK przez dwa inwertery Schmitta. HC74 i końcowe bramki otrzymują szybkie zbocze zamiast wolnego narastania pasywnej sieci SAFE_N. HC14 nie ma tabeli gwarantowanych progów dla dokładnie 3,3 V; nie przedstawiamy interpolacji progów z 2/4,5/6 V jako gwarancji. Odbiór obejmuje pomiar H/L i przełączania przy dolnym i górnym napięciu roboczym.

U11 MCP100-315DI/TO nadzoruje lokalne 3,3 V; próg katalogowy 3,00–3,15 V, opóźnienie zwolnienia resetu co najmniej 150 ms. **Wersja D ma 1 RESET, 2 VDD, 3 VSS.** Wersja H nie jest zamiennikiem pinowym. Wyjście resetu trafia do U5C, nie bezpośrednio na SAFE_N. Przy zasilaniu CORE z USB, ale braku zasilania P04, zgody mają pozostać wyłączone dzięki Ioff oraz pulldownom modułów odbiorczych. To trzeba sprawdzić także na P07/P08 — sama P04 nie gwarantuje stanu wejścia nieobecnej płytki.

## Watchdog i ręczne uzbrojenie

U1A CD74HC123: A=GND, B=HEARTBEAT, CLR=SUP_OK. C1 1 µF PET jest między pinami 15 i 14, a R1 220 kΩ łączy pin 15 z 3V3_IO. **Pin 14 nie jest masą.** Nieużywana połówka ma A/B/CLR w L.

TI podaje t=0,45RC dla **5 V**, co dawałoby 99 ms. P04 działa przy 3,3 V: 99 ms to oszacowanie do doboru początkowego, nie gwarantowany czas. Cel odbioru 50–150 ms od ostatniego zbocza heartbeat. C1 PET 10%, R1 1%; nie zastępować C1 kondensatorem elektrolitycznym ani małym X7R o nieznanej zmianie pojemności z napięciem. Gdy pomiar nie mieści się w oknie, dobrać R1 i zapisać nowy wariant BOM/pomiar zamiast uznać próbę za zaliczoną.

Jest to watchdog zaniku zboczy, bez kontroli minimalnej/maksymalnej częstotliwości. Przy zwolnieniu CLR i wejściu B już w H HC123 może wytworzyć jeden impuls. Test stałego H wykonywać po co najmniej 200 ms stabilnych warunków; sprawdzić też ten impuls rozruchowy. Nie gwarantujemy braku krótkiej dostępności SAFE w tym pierwszym oknie. Domyślne MCU_ARM=0 i wymaganie świeżego ARM pozostają istotnymi warunkami rozruchu. Gdyby wymagano rozpoznania kilku poprawnych okresów przed jakąkolwiek zgodą, potrzebna jest osobna zmiana architektury, a nie inne R/C.

U3A ma D=1, PRE=1, CLR=SAFE_OK. ARM NO zwiera ARM_CONTACT do GND przez R3 1 kΩ. R2 10 kΩ i C2 1 µF PET dają ok. 10 ms stałej czasowej zwalniania; po naciśnięciu poziom ARM_BUTTON_N wynosi nominalnie 0,30 V, a stała czasowa ok. 0,91 ms. U2B zamienia to w dodatnie zbocze zegara. Jest to filtr RC ze Schmittem, a nie gwarantowany filtr dowolnych drgań styków — kwalifikacja konkretnego przycisku jest obowiązkowa.

Po błędzie trzeba zwolnić ARM i nacisnąć go ponownie. Przytrzymanie przycisku przez zanik i powrót READY/heartbeat nie daje nowego zbocza. W firmware heartbeat powinien powstawać tylko po poprawnej, świeżej iteracji akwizycji (wg kontraktu 10 ms), nie z niezależnego peryferium, które pracuje mimo zawieszenia zadania. Zmiana banku/trybu zatrzymująca akwizycję na ok. 200 ms wygasi watchdog i skasuje ARM. Po LOGGER→TEST i po takiej kalibracji ponownie nacisnąć ARM przed ruchem. R1 nie ma kodu firmware ani nowego przypisania GPIO.

## Różnice względem v6.1-rc1

| Obszar | Zmiana |
|---|---|
| Mechanika | Nowy layout 2L, PTH przewodów z kotwami 12/14,54 mm, lokalne biblioteki |
| Reset | MCP100 lokalnie + dwie wolne bramki Schmitta przed CLR i permit |
| SAFE sinks | 2N7002 SOT23 zastąpione 2N3904BU THT, dodane rezystory baz |
| ARM | 100 Ω/100 nF → 1 kΩ/1 µF; potrzebna kwalifikacja przycisku |
| Interlock | Wolna bramka potwierdza TEST_KEY; dwa równoległe 10 kΩ MECH_OK zastąpione jednym 10 kΩ |
| Odsprzęganie | C3 bulk, C4–14 przy układach; C15–17 na adapterach SO14 |
| Złącza | MPN złączy Au; SENSOR 4→6, M2.2, nowe piny NC |
| Diagnostyka | LED zasilania i 13 punktów pomiarowych |

Rezystory sygnałowe mają jeden gabaryt DIN0207 / 0,25 W, 1%. Nie ma łańcuchów dzielników wysokiego napięcia do scalania. R38 to przewlekana zworka 0 Ω.

Kontrole cyfrowe obejmują idealne poziomy i ustalone stany, nie propagację nanosekundową, uszkodzenie elementu, EMI, przerwanie masy czy jednoczesne zbocza ARM/reset. P04 jest elementem prototypu diagnostycznego, nie certyfikowanym sterownikiem bezpieczeństwa.
