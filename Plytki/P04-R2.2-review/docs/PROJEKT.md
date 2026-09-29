# P04-R2: działanie i uzasadnienie

*R2 (Claude, 26.09.2026) po recenzji R1 Astry. Zmienione względem R1: nadzorca U11 (R4-01), druga droga watchdoga SAFE_WD (R4-02), rezystory na wyjściach 3,3 V (R4-03), C18 i położenie R5 (R4-04), R41/R42 (R4-07). Zmiany samej płytki (KEY, zszycie GND) w `ZMIANY-R2.md`.*

## Granice modułu

P04 otrzymuje 3V3_IO z P02 i pracuje we wspólnej masie urządzenia. 5V_SYS na J1.1 dochodzi tylko do TP13. P04 nie ma połączenia z 12 V, silnikiem ani liniami EGR. STOP i ARM są fizycznymi stykami P11. P04 daje logikę 3,3 V do P07/P08 i zwrotnie HW_ARMED/INTERLOCK do CORE. Nie jest to izolacja galwaniczna.

Docelowy pobór tej płytki przy wolnych sygnałach to pojedyncze–kilkanaście mA, do potwierdzenia pomiarem; rezerwujemy 30 mA na P02. Sumaryczny statyczny prąd rezystorów wejść, obciążeń logicznych, LED i obwodów baz pozostaje poniżej tego budżetu; rezystory dodane w R2 są szeregowe i niczego nie dokładają. Na stole początkowy limit 50 mA; nie zwiększać go w odpowiedzi na zwarcie. Ta rezerwa nie obejmuje obcych obciążeń dołączonych do J7/J8 ani prądu dynamicznego przy nadmiernej częstotliwości PWM.

## Tor zgody

Wszystkie wejścia do buforów mają domyślne L. Za każdym kanałem 74LVC125AD jest drugi pulldown, aby wyjęcie adaptera nie pozostawiło wejścia bramki w powietrzu. Bufory Nexperia mają Ioff; nie zamieniać ich na HC125. TEST_KEY i MECH_OK są sygnałami ze styków, zasilanymi z P04 (PANEL_3V3 przez R40 100 Ω), a nie z obcej aktywnej domeny. Od R2 dochodzą do bramek przez R41/R42 1 kΩ; pulldowny R23/R24 10 kΩ leżą po stronie bramek, więc przerwany rezystor szeregowy daje L. Poziom H: 3,24 × 10/11 ≈ 2,94 V.

```
MODULES_OK = PSU_OK & DAQ_OK & DRIVE_OK & SENSOR_OK & CORE_LINK & PG_LINK
INTERLOCK = MODULES_OK & MECH_OK & TEST_KEY
SUP_OK = SUP_N_P04 & LOCAL_SUP_N
SAFE_N = STOP_CLOSED & INTERLOCK & SUP_OK & WD_Q & brak zewnętrznego zwarcia SAFE_N do GND
SAFE_OK = SAFE_N po dwóch bramkach Schmitta (U2E, U2F)
SAFE_WD = SAFE_OK & WD_Q                    (R2, wolna bramka U7D)
HW_ARMED = zatrzask D ustawiany zboczem fizycznego ARM; asynchronicznie kasowany przez SAFE_WD
MOTOR_PERMIT = HW_ARMED & MCU_ARM_P04 & INTERLOCK & SAFE_WD
PWM_OUT = PWM_P04 & MOTOR_PERMIT
SENSOR_PERMIT = SENSOR_ENABLE_P04 & TEST_KEY & INTERLOCK & SAFE_WD
```

READY oznacza sprawność/obecność modułu przed włączeniem jego wyjścia. Nie wolno uzależnić DRIVE_OK od KPWR ani SENSOR_OK od SENSOR_PERMIT: powstałaby blokada rozruchu. Brak któregokolwiek READY blokuje też sam czujnik, tak jak w bazie projektu. Do prób pojedynczej P04 te sygnały dostarcza P00.

P11 MECH_OK już zawiera TEST_KEY, styki obecności obu złączy LOGGER i pętlę TEST. Dodatkowe jawne AND z TEST_KEY w P04 wykorzystuje wolną bramkę U7C. To lokalne potwierdzenie warunku; nie oznacza, że bazowa P11 nie sprawdzała klucza.

## SAFE_N i reset

R4 10 kΩ podciąga SAFE_N do PANEL_3V3 (3V3_IO przez R40 100 Ω) przez fizyczny STOP NC. R5 100 kΩ ściąga do masy po przerwaniu STOP. Od R2 R5 stoi przy U2, a C18 1 nF C0G przy samym wejściu U2.11 (R4-04). Q1–Q3 są otwartymi kolektorami: brak heartbeat, reset zasilania lub brak interlocku ściąga SAFE_N. P01 i przyszła P07 mogą jedynie dołączyć własne otwarte kolektory. Nie wolno podawać tutaj stanu H z GPIO ani wyjścia push-pull.

Z panelu R40 pobiera przy zamkniętych stykach ok. 0,63 mA (TEST_KEY i MECH_OK po 0,30 mA, SAFE_N 0,03 mA), więc PANEL_3V3 ≈ 3,24 V przy 3V3_IO = 3,30 V. Nominalnie SAFE_N w H ma 3,24 × 100/(100+10) ≈ 2,94 V (R1 bez R40: 3,00 V); przy 3V3_IO = 3,18 V, dolnej granicy z P02, ok. 2,84 V. Prąd podciągania przy L wynosi do ok. 0,35 mA przy maksymalnym założonym 3V3_IO=3,465 V i R4 −1%. Pojedynczy 2N3904 ma bazę zasilaną przez 10 kΩ i pulldown 100 kΩ. Nawet przy 2,4 V na wyjściu bramki oraz VBE=0,8 V pozostaje ok. 0,15 mA bazy: wymuszone β poniżej 3 dla tego obciążenia. Rzeczywisty VOL należy zmierzyć; cel ≤0,25 V.

SAFE_N jest wspólnym, stosunkowo wysokoimpedancyjnym sygnałem. Nie dodawać LED ani dodatkowych pulldownów na tej sieci bez ponownego przeliczenia. Docelowo zmierzyć H ≥2,7 V po przyłączeniu P01 i P07. Spadek STOP zależy od pojemności wiązki i R5; nie jest identyczny czasowo z aktywnym zwarciem kolektora. C18 1 nF: narastanie τ ≈ 9 µs (R4 ∥ R5), spadek po otwarciu STOP do progu HC14 ok. 55–160 µs (R5 × C18 plus pojemność wiązki); poziomy DC bez zmian. Filtr tłumi krótkie szpilki, które przez asynchroniczny CLR HC74 kasowałyby ARM.

U2E/U2F odtwarzają SAFE_OK przez dwa inwertery Schmitta. HC74 i końcowe bramki otrzymują szybkie zbocze zamiast wolnego narastania pasywnej sieci SAFE_N. HC14 nie ma tabeli gwarantowanych progów dla dokładnie 3,3 V; nie przedstawiamy interpolacji progów z 2/4,5/6 V jako gwarancji. Odbiór obejmuje pomiar H/L i przełączania przy dolnym i górnym napięciu roboczym.

U11 MCP100-300DI/TO nadzoruje lokalne 3,3 V; próg opadający katalogowo 2,85–3,00 V, opóźnienie zwolnienia resetu 150–700 ms. Histereza 50 mV jest wartością **typową**, bez podanego maksimum w DS11187F. Zatem dla -300 oszacowany próg zwolnienia to 3,00 + 0,05 = 3,05 V, a zapas przy 3,18 V DC wynosi 130 mV; przy dolinie tętnień 3,16 V wynosi 110 mV. Są to oszacowania, nie gwarantowane zapasy skrajne. W R1 wariant -315 dawał analogicznie ok. 3,20 V i mógł nie zwolnić resetu przy dolnym napięciu P02. Zmiana na -300 jest zasadna; E02/E16 mają potwierdzić start przy najniższym rzeczywistym napięciu. **Wersja D ma 1 RESET, 2 VDD, 3 VSS.** Wersja H nie jest zamiennikiem pinowym. Wyjście resetu trafia do U5C, nie bezpośrednio na SAFE_N. Przy zasilaniu CORE z USB, ale braku zasilania P04, zgody mają pozostać wyłączone dzięki Ioff oraz pulldownom modułów odbiorczych. To trzeba sprawdzić także na P07/P08 — sama P04 nie gwarantuje stanu wejścia nieobecnej płytki.

## Watchdog i ręczne uzbrojenie

U1A CD74HC123: A=GND, B=HEARTBEAT, CLR=SUP_OK. C1 1 µF PET jest między pinami 15 i 14, a R1 220 kΩ łączy pin 15 z 3V3_IO. **Pin 14 nie jest masą.** Nieużywana połówka ma A/B/CLR w L.

TI podaje t=0,45RC dla **5 V**, co dawałoby 99 ms. P04 działa przy 3,3 V: 99 ms to oszacowanie do doboru początkowego, nie gwarantowany czas. Cel odbioru 50–150 ms od ostatniego zbocza heartbeat. C1 PET 10%, R1 1%; nie zastępować C1 kondensatorem elektrolitycznym ani małym X7R o nieznanej zmianie pojemności z napięciem. Gdy pomiar nie mieści się w oknie, dobrać R1 i zapisać nowy wariant BOM/pomiar zamiast uznać próbę za zaliczoną.

**Dwie drogi watchdoga (R2, R4-02).** W R1 brak heartbeat działał wyłącznie przez U2A → R6 → Q1 → SAFE_N. Przerwa w Q1 lub R6, albo zimny lut, przy zawieszonym ESP32 z MCU_ARM = H i działającym sprzętowym PWM zostawiała zatrzask i obie zgody włączone. Teraz WD_Q wchodzi dodatkowo do wolnej bramki U7D: SAFE_WD = SAFE_OK & WD_Q kasuje U3 (CLR) i bramkuje MOTOR_PERMIT (U5D) oraz SENSOR_PERMIT (U5B). Bez usterek tabele prawdy się nie zmieniają, bo SAFE_N już zawiera WD_Q. Pozostałe warunki miały po dwie drogi już w R1 (SUP_OK: Q2 i CLR watchdoga; INTERLOCK: Q3 i bezpośrednio w AND). Próba w ODBIOR: TP15 (baza Q1) zwarty do GND, zatrzymany heartbeat → HW_ARMED, MOTOR_PERMIT i SENSOR_PERMIT = L, choć SAFE_N zostaje H. W firmware warto powtarzać tę próbę okresowo (zatrzymać heartbeat po ARM i sprawdzić spadek HW_ARMED, który czyta P03).

Jest to watchdog zaniku zboczy, bez kontroli minimalnej/maksymalnej częstotliwości. Przy zwolnieniu CLR i wejściu B już w H HC123 może wytworzyć jeden impuls. Test stałego H wykonywać po co najmniej 200 ms stabilnych warunków; sprawdzić też ten impuls rozruchowy. Nie gwarantujemy braku krótkiej dostępności SAFE w tym pierwszym oknie. Domyślne MCU_ARM=0 i wymaganie świeżego ARM pozostają istotnymi warunkami rozruchu. Gdyby wymagano rozpoznania kilku poprawnych okresów przed jakąkolwiek zgodą, potrzebna jest osobna zmiana architektury, a nie inne R/C.

U3A ma D=1, PRE=1, CLR=SAFE_WD. ARM NO zwiera ARM_CONTACT do GND przez R3 1 kΩ. R2 10 kΩ i C2 1 µF PET dają ok. 10 ms stałej czasowej zwalniania; po naciśnięciu poziom ARM_BUTTON_N wynosi nominalnie 0,30 V, a stała czasowa ok. 0,91 ms. U2B zamienia to w dodatnie zbocze zegara. Jest to filtr RC ze Schmittem, a nie gwarantowany filtr dowolnych drgań styków — kwalifikacja konkretnego przycisku jest obowiązkowa.

Po błędzie trzeba zwolnić ARM i nacisnąć go ponownie. Przytrzymanie przycisku przez zanik i powrót READY/heartbeat nie daje nowego zbocza. W firmware heartbeat powinien powstawać tylko po poprawnej, świeżej iteracji akwizycji (wg kontraktu 10 ms), nie z niezależnego peryferium, które pracuje mimo zawieszenia zadania. Zmiana banku/trybu zatrzymująca akwizycję na ok. 200 ms wygasi watchdog i skasuje ARM. Po LOGGER→TEST i po takiej kalibracji ponownie nacisnąć ARM przed ruchem. R1 nie ma kodu firmware ani nowego przypisania GPIO.

## Różnice względem v6.1-rc1

| Obszar | Zmiana |
|---|---|
| Mechanika | Nowy layout 2L, PTH przewodów z kotwami 12/14,54 mm, lokalne biblioteki |
| Reset | MCP100-300 lokalnie + dwie wolne bramki Schmitta przed CLR i permit; SAFE_WD (U7D) jako druga droga watchdoga |
| SAFE sinks | 2N7002 SOT23 zastąpione 2N3904BU THT, dodane rezystory baz |
| ARM | 100 Ω/100 nF → 1 kΩ/1 µF; potrzebna kwalifikacja przycisku |
| Interlock | Wolna bramka potwierdza TEST_KEY; dwa równoległe 10 kΩ MECH_OK zastąpione jednym 10 kΩ; R41/R42 1 kΩ szeregowo z liniami panelu |
| Wyjścia 3,3 V | PG: R38 (PG_SEND) i R39 (J7.1) po 1 kΩ; panel: R40 100 Ω (J8.1). W v6.1 W_SEND 0R i bezpośrednie 3V3 |
| SAFE_N | C18 1 nF C0G przy U2.11, R5 przy U2 |
| Odsprzęganie | C3 bulk, C4–14 przy układach; C15–17 na adapterach SO14 |
| Złącza | MPN złączy Au; SENSOR 4→6, M2.2, nowe piny NC |
| Diagnostyka | LED zasilania i 15 punktów pomiarowych (R2: TP14 SAFE_WD, TP15 Q1_B) |

Rezystory sygnałowe mają jeden gabaryt DIN0207 / 0,25 W, 1%. Nie ma łańcuchów dzielników wysokiego napięcia do scalania. R38 od R2 ma 1 kΩ (w R1 zworka 0 Ω): PG_LINK = 3,3 × 10/11 = 3,0 V. Zwarcie w wiązce PG ogranicza się do 3,3 mA na żyłę, w wiązce panelu do 33 mA (R40, 0,11 W w rezystorze 0,25 W).

Kontrole cyfrowe obejmują idealne poziomy i ustalone stany, nie propagację nanosekundową, uszkodzenie elementu, EMI, przerwanie masy czy jednoczesne zbocza ARM/reset. P04 jest elementem prototypu diagnostycznego, nie certyfikowanym sterownikiem bezpieczeństwa.

## R2.2: wejście resetu CORE

R17=10 kΩ przed U9.5 współpracuje z U6/R41 P03-R5. Budżet upływności, poziomy i odbiór zboczy: KONTRAKT-RESET.md. R30 na wyjściu pozostaje 100 kΩ. Zmiana nie dotyczy SAFE_N ani rezystorów innych wejść.
