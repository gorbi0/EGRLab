# Format S1 — specyfikacja (wersja S1-3, 29.09.2026)

*S1-3 (29.09.2026 wieczorem, decyzja użytkownika „opcja 1”): P02 R4 w klasie L zajmuje cały poziom 1, P10 schodzi na poziom 4, slot S3 (§7). W klasie 2/3 trasowanie P02 R4 się nie domykało (15 niepołączeń w obu metodach). Skutki dla P10 i wariantu pełnego: §7.*

*S1-2 (29.09.2026, decyzja użytkownika w trakcie pilota P02 R4): dopuszczony montaż SMD od spodu płytki (§4, §9).*

Obowiązuje dla każdej nowej płytki urządzenia EGRLab. Dane liczbowe dla generatorów są w `format-s1.json`, uzasadnienie w `STUDIUM-FORMATU-S1.md`.

## 1. Decyzje użytkownika (29.09.2026)

- **Stos:** poziome płytki w formacie S1 zamiast kasety R1.
- **Połączenia między płytkami:** płytka połączeń zamiast wiązek.
- **Rezystory i kondensatory:**
  - posiadane części THT zostają w użyciu; rezystory montujemy na stojąco;
  - nowo kupowane części to SMD 1206;
  - rezystory mocy (2 W) zostają leżące.
- **Produkcja:** wszystkie płytki z fabryki, bez płytek uniwersalnych. Zamawiamy w Chinach (np. JLCPCB).
- **Strona serwisowa (wymaganie użytkownika):** punkty pomiarowe potrzebne do odbioru są w każdej płytce po tej samej stronie, na zwykłych kołkach. Po skręceniu stosu mają zostać dostępne bez obracania całości.

## 2. Układ współrzędnych i strony

- **x** biegnie wzdłuż długiego boku (160 mm): x = 0 od strony panelu, x = 160 od strony wejść.
- **y** biegnie w poprzek (100 mm): y = 0 to krawędź A (płytka połączeń), y = 100 to krawędź B (strona serwisowa).
- **z** jest skierowane w górę; strona elementów jest zawsze na górze.

Ściany obudowy:

| Ściana | Co jest przy niej |
|---|---|
| panel (x = 0) | P11 i wtyki DT, przełączniki, BNC |
| wejścia (x = 160) | XT60, OBD, przewód VBAT, gniazda termopar |
| A (y = 0) | płytka połączeń P12 |
| B (y = 100) | zdejmowana ścianka serwisowa |

## 3. Obrysy i sloty

Długość 160 mm dzieli się na trzy sloty o szerokości 53,0 mm, z odstępem 0,5 mm między nimi:
- S1: x = 0–53,0;
- S2: x = 53,5–106,5;
- S3: x = 107,0–160,0.

Krok slotów wynosi 53,5 mm.

| Klasa | Obrys | Sloty |
|---|---|---|
| L | 160,0 × 100,0 mm | S1–S3 |
| 2/3 | 106,5 × 100,0 mm | S1–S2 albo S2–S3 |
| 1/3 | 53,0 × 100,0 mm | jeden slot |

**Parametry płytki:**
- narożniki R 1 mm;
- 2 warstwy, FR4 1,6 mm, miedź 35 µm;
- reguły projektowe jak w P02-R3 (są ostrzejsze niż w JLCPCB, więc przejdą w każdej fabryce);
- otwory PTH i przelotki z pierścieniem ≥ 0,25 mm.

W JLCPCB najtańszy próg cenowy obejmuje zwykle płytki do 100 × 100 mm. Mieści się w nim tylko klasa 1/3; klasy 2/3 i L kosztują kilka dolarów więcej za projekt.

## 4. Otwory i poziomy

**Otwory M3** (Ø 3,2 mm, strefa dystansu Ø 7 mm bez miedzi innych sieci i bez elementów):
- w każdym slocie cztery otwory w punktach x = 4,0 i 49,0 (względem początku slotu) oraz y = 14,0 i 86,0;
- płytka ma otwory wszystkich zajmowanych slotów: 1/3 — 4, 2/3 — 8, L — 12.

Otwory odsunięte od krawędzi A i B zostawiają wolny pas na złącza i kołki.

| Parametr | Wartość |
|---|---|
| Dystans między poziomami (M3, żeński-żeński) | 20 mm standardowo; 25 mm dla poziomu „wysokiego” |
| Wysokość elementów nad płytką | ≤ 16,5 mm (poziom wysoki: ≤ 21,5 mm) |
| Wyprowadzenia THT od spodu | przycięte do ≤ 1,5 mm |
| Elementy od spodu (S1-2) | tylko SMD o wysokości ≤ 1,5 mm (0805/1206, SOT-23, SOD-123); SOIC (1,75 mm) tylko na poziomie 1, nad dnem obudowy; ≥ 1 mm od pól THT; poza strefami dystansów; nadruk oznaczeń od spodu |
| Dystans od dna obudowy | 8 mm |

Wyższe elementy montujemy na leżąco (np. kondensator C_H Ø 16 × 25 mm). TO-220 może stać na poziomie wysokim (ok. 19,5 mm z nóżkami skróconymi do 4 mm). Blaszka TO-220 leży tylko na miedzi swojej sieci.

## 5. Krawędź A — złącze płytki połączeń

- **Złącze:** IDC 2,54 mm, obudowane, kątowe, w wariancie 2 × 5, 2 × 8 albo 2 × 10. Strona wtyku jest równo z krawędzią, a pin 1 od strony mniejszego x.
- **Położenie:** najwyżej jedno złącze na slot, ze środkiem w x = 26,5 mm od początku slotu. Płytka L może mieć 3 złącza, 2/3 — 2, a 1/3 — jedno.
- **Połączenie:** krótka taśma IDC (ok. 30 mm) do płytki połączeń P12. P12 stoi pionowo ok. 18 mm od krawędzi A i ma złącze w miejscu każdego (poziom, slot).
- **Pas zastrzeżony:** y = 0–10 mm, tylko na długości złącza (x = 10–43 mm w slocie); poza nim pas jest wolny na elementy.
- **Pinout:** każda płytka ma własny układ wyprowadzeń, a nie wspólną magistralę. P12 to wiązki v6.1 przeniesione na miedź: te same sieci i połączenia, magistrale SPI wielopunktowo.
- **Na złączu:** 5V_SYS na co najmniej 2 pinach (IDC ok. 1 A na styk), 3V3_IO na co najmniej 1 pinie, GND przeplatane z sygnałami SPI i z sygnałami analogowymi.
- **Poza taśmą, osobnymi przewodami:**
  - prąd silnika 5 A (VMOTOR, ISERIES, TMOTOR);
  - wejście pakietu;
  - odczepy TAPS z panelu do P05 (sygnały analogowe, najkrótsza droga);
  - AUX i SCOPE (koncentryk);
  - OBD;
  - termopary.

## 6. Krawędź B — strona serwisowa

- **Listwa:** kątowy goldpin 1 × N 2,54 mm; kołki wystają ok. 6 mm za krawędź, żeby dało się podpiąć chwytak przy skręconym stosie.
- **Położenie:** x = 10–43 mm w slocie, czyli najwyżej 13 pinów na slot. Płytka może mieć listwę w każdym zajmowanym slocie.
- **Treść:** punkty potrzebne do odbioru płytki (ODBIOR). Pierwszy i ostatni pin każdej listwy to GND.
- **Każdy kołek poza GND** wyprowadzamy przez rezystor szeregowy postawiony przy węźle:
  - 1 kΩ dla szyn do 5 V i sygnałów logicznych;
  - 4,7 kΩ dla szyn pakietu (do 16,8 V; zwarcie daje 3,6 mA i 60 mW, bezpiecznie dla 1206);
  - 10 kΩ dla węzłów wysokoimpedancyjnych (dzielniki, bramki, referencje).

  Kołki stoją co 2,54 mm, więc zsunięta sonda może zewrzeć sąsiednie piny. Rezystor sprawia, że nic się wtedy nie uszkodzi. Multimetr (10 MΩ) mierzy przez niego bez zauważalnego błędu, a sonda oscyloskopu (ok. 15 pF) daje z 1 kΩ stałą czasową ok. 15 ns.
- **Nadruk:** nazwa sygnału przy każdym kołku, czytelna od strony B.

Punkty, których nie ma na listwie, wymagają rozebrania stosu.

## 7. Przydział poziomów

| Poziom | Dystans pod płytką wyżej | S1 | S2 | S3 |
|---|---|---|---|---|
| 1 | 25 mm (wysoki) | P02 R4 | P02 R4 | P02 R4 |
| 2 | 20 mm | P03 | P03 | P03 |
| 3 | 20 mm | P05 | P05 | P09 |
| 4 | 20 mm | P06 | P06 (klasa 2/3, decyzja 1.10) | P10 |
| 5 (pełny) | 20 mm | P08 | P07 | P07 |
| 6 (pełny) | 20 mm | P04 | P04 | P04 (klasa L, decyzja użytkownika 5.10.2026) |

Uzasadnienie:
- P02 R4 leży na dole i od strony wejść: XT60, VBAT i najcięższe elementy.
- P05 i P06 są od strony panelu: TAPS i ISERIES idą najkrótszą drogą.
- P09 jest przy gniazdach termopar na ścianie wejść.
- P03 jest w środku stosu.

Jeśli layout nie zmieści się w klasie:
- P02 R4 dostaje klasę L, a P10 idzie na poziom 4 — **zastosowane w S1-3**;
- P06 dostaje klasę 2/3, a wariant pełny ma wtedy 6 poziomów — **zastosowane 1.10.2026** (decyzja użytkownika; P06 R2 w slotach S1–S2 poziomu 4).

Skutki S1-3 (P02 R4 w klasie L, P10 na poziomie 4, slot S3):
- **P10:** slot S3 leży przy ścianie wejść, więc J3 (OBD) wychodzi tą samą ścianą co pozostałe przewody z auta. Poziom 4 nie jest wysoki: od spodu tylko SMD ≤ 1,5 mm, bez SOIC (§4), elementy od góry ≤ 16,5 mm. Schemat P10 R2 zakładał slot S1 poziomu 1 — do sprawdzenia przed layoutem (obudowy układów od spodu, położenie J3).
- **Wariant pełny:** po P06 w klasie 2/3 (1.10) poziom 4 jest pełny (P06 S1–S2, P10 S3), więc P04 (2/3) nie mieści się obok P06 i P10. Pełny dostaje szósty poziom (P04 albo P10). **Do decyzji przy wariancie pełnym** (P04, P07, P08 powstają później); wysokość stosu rośnie wtedy o ok. 21,6 mm.
- **LOGGER:** liczba poziomów i wysokość stosu bez zmian.

Wysokość stosu:
- LOGGER: ok. 8 + 4 × 1,6 + 25 + 20 + 20 + 16,5 + 3 ≈ 99 mm;
- pełny: ok. 121 mm.

## 8. Budżet złączy krawędzi A (pierwsze przybliżenie)

| Płytka | Sygnały przez P12 | Złącza |
|---|---|---|
| P02 R4 | zasilanie wszystkich płytek, PSU_OK, PFAIL_N, P04_3V3, SAFE_N, PG_SEND, PG_LINK, VBAT_SENSE | 1 × 2×10 (pinout niżej) |
| P03 | DAQ 8, ILOG 2, ITEST 1, SAFE 8, DIR 4, SFAULT 1, TEMP 5, CAN 2, PANELCORE 5, PFAIL_N — ok. 37 sygnałów + zasilanie i GND | 3 × 2×10 |
| P04 | SAFE, DRIVE, SENSOR, DAQOK, PSUOK, PG, PANELSAFE | 2 × 2×10 |
| P05 | DAQ 8 (J_BP2, S2); DAQOK, VBAT_SENSE, 5V_SYS × 2 (J_BP1, S1) | 1 × 2×10 + 1 × 2×5 (decyzja użytkownika 1.10.2026: jedno 2×10 nie mieści 10 sygnałów i dwóch 5V_SYS na pinach parzystych) |
| P06 | ILOG (ADC_SCLK, ADC_DOUTA, CS_ILOG_N, LOGGER_CURRENT_OK), 5V_SYS × 2, 3V3_IO | 1 × 2×8 (P06 R2, slot S2, x = 80,0) |
| P07 | ITEST, DIR, DRIVE | 1 × 2×10 |
| P08 | SENSOR, SFAULT | 1 × 2×5 |
| P09 | TEMP (SPI3 i dwa CS) | 1 × 2×5 |
| P10 | CAN_TX, CAN_RX | 1 × 2×5 |
| P11 | PANELCORE, PANELSAFE (taśma z panelu do P12) | 1 × 2×10 |

Dokładne pinouty ustala zadanie każdej płytki; P12 powstaje na końcu, z pinoutów wszystkich płytek.

### Pinout P02 R4 J_BP (2×10, slot S3, środek x = 133,5 mm w układzie płytki)

| Pin | Sieć | Pin | Sieć |
|---|---|---|---|
| 1 | GND | 2 | 5V_SYS |
| 3 | GND | 4 | 5V_SYS |
| 5 | GND | 6 | 5V_SYS |
| 7 | GND | 8 | 3V3_IO |
| 9 | GND | 10 | 3V3_IO |
| 11 | GND | 12 | PSU_OK |
| 13 | GND | 14 | PFAIL_N |
| 15 | P04_3V3 | 16 | SAFE_N |
| 17 | PG_SEND | 18 | PG_LINK |
| 19 | GND | 20 | VBAT_SENSE |

Złącze zastępuje LV03–LV10 oraz J11, J12, J13 i J16 z etapu 1. Przewodami zostają:
- J1 BAT — przy krawędzi od strony wejść;
- J2 VMOTOR;
- J14 PWR — skrętka do przełącznika na panelu;
- J15 VBAT_IN.

## 9. Elementy

- **Rezystory:** posiadane THT montujemy na stojąco (np. `R_Axial_DIN0207_L6.3mm_D2.5mm_P5.08mm_Vertical`), nowe to SMD 1206. Rezystory mocy (PR02, 2 W) leżą.
- **Kondensatory:**
  - posiadane THT zostają;
  - nowe ceramiczne to SMD 1206 albo 0805 X7R;
  - elektrolity wyższe niż limit poziomu montujemy na leżąco.
- **Strona montażu (S1-2):** THT i wszystko wyższe niż 1,5 mm na górze. Od spodu najlepiej pasują nowe rezystory i kondensatory SMD, rezystory szeregowe kołków serwisowych (pod listwą) oraz kondensatory odsprzęgające pod swoim układem. Lutowanie ręczne: najpierw spód, potem góra.
- **Układy scalone:** DIP, SOIC albo LQFP, bez QFN i BGA. Na płytce z fabryki SOIC lutujemy wprost; adapter SO14→DIP tylko tam, gdzie już jest kupiony i jest na niego miejsce.
- **Moduły** (ESP32-S3, microSD, MAX31856) stoją na gniazdach i razem z nimi mieszczą się w limicie poziomu. Jeśli się nie mieszczą, płytka przechodzi na poziom wysoki.
- **Nadruk:**
  - nazwa i rewizja, np. `P02 R4 S1-2/3 S2–S3`;
  - znaczniki krawędzi A i B;
  - pin 1 każdego złącza;
  - opisy kołków serwisowych.

## 10. Co dalej

1. **Pilot P02 R4 w S1:** zadanie `Plytki/P02-R4-specyfikacja/ZADANIE-P02-R4-ETAP2.md` (przepisane pod S1).
2. **LOGGER:** P03, P05 (z poprawkami R2), P06, P09, P10, każda z pinoutem J_BP i listwą serwisową.
3. **P12 i P11:** płytka połączeń P12 z pinoutów wszystkich płytek, P11 pod nowy panel, obudowa i makieta 1:1.
4. **Wariant pełny:** P04, P08, P07.
