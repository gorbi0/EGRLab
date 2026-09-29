# Recenzja P04 SAFE R1

26.09.2026 · Claude. Przedmiot: pakiet Astry `Plytki/P04-R1-review` (archiwum `P04-R1-review.zip`, sha256 z `.zip.sha256`). Zakres: poprawność elektryczna i logiczna, zachowanie dynamiczne, interfejsy z sąsiednimi płytkami, PCB, BOM i zakupy, dokumentacja oraz weryfikacja. Zasadności samego projektu nie oceniam.

## Werdykt

Nie znalazłem błędu blokującego ani w schemacie, ani w PCB. Logika wyjść pin po pinie odpowiada równaniom z `docs/PROJEKT.md`, wyprowadzenia wszystkich układów są poprawne, a natywny DRC na kopii płytki daje 0 / 0 / 0.

Dwie rzeczy zmieniłbym przed zakupami i przed zamówieniem PCB:
- **R4-01 — nadzorca U11 w wariancie 3,00 V.** Obecny próg 3,15 V w najgorszym przypadku nie pozwala zwolnić resetu przy 3V3_IO z P02. Zmiana dotyczy tylko BOM; footprint i pinout zostają.
- **R4-02 — druga ścieżka dla watchdoga.** Teraz działa on wyłącznie przez jeden tranzystor Q1. Wystarczy wolna bramka U7D, bez nowych części.

R4-03 (ograniczenie prądu na 3V3_IO wychodzącym z płytki) warto dołożyć w tej samej rewizji, bo to trzy rezystory. Pozostałe punkty są drobne albo dotyczą przyszłych płytek.

## Co sprawdziłem i jak

- **DRC.** Natywny DRC (wszystkie poziomy, pełne błędy ścieżek, zgodność ze schematem, przelanie wylewek) uruchomiłem od nowa na kopii `eda/`. Wynik: 0 naruszeń, 0 niepołączonych, 0 różnic.
- **Logika.** Odtworzyłem ją ręcznie z `verification/P04.xml`; tabelę pinów daje `skrypty/logika_z_netlisty.py`. Sprawdzone wyprowadzenia:
  - CD74HC123E: C1 między pinami 15 i 14, R1 do 15, CLR = SUP_OK, A = GND, B = HEARTBEAT_P04;
  - SN74HC74N: D = PRE = 1, CLR = SAFE_OK;
  - SN74HC14N i 4 × SN74HC08N;
  - 3 × 74LVC125A z pulldownami przed i za buforem;
  - MCP100 w wariancie D oraz 2N3904 (E-B-C).
  
  Nieużywane sekcje (U1B, U3B, U7D, kanał 4 U10) mają ustalone wejścia. Wynik: równania MODULES_OK, INTERLOCK, SUP_OK, SAFE_N, HW_ARMED, MOTOR_PERMIT, PWM_OUT i SENSOR_PERMIT są dokładnie takie, jak opisano.
- **Pinout MCP100 „D”.** Porównałem z rysunkiem obudów TO-92 w karcie rodziny MCP1X0 (MCP120/130, DS11184; kopia w `Plytki/P05-R1-review/reference/datasheets/`). Wariant D to RST, VDD, VSS od lewej przy płaskiej stronie do patrzącego. Na nadruku U11 płaska strona jest u dołu, a pad 1 z lewej, więc się zgadza.
- **Interfejsy, pin po pinie:**
  - P03 R1, złącze J4 SAFE — mój projekt;
  - P01 R3.1, złącze J5 PG: R30 10 k do bazy Q7, Q8, pętla R34 0 Ω;
  - P02 R2, złącze J12 PSUOK: pin 3 HOLD_READY trafia na pad NC w P04, zgodnie z zasadą „tylko lokalnie”;
  - P05 R1, złącze J3 DAQOK.
  
  Wszystkie są zgodne, łącznie z kluczami.
- **Dynamika:**
  - rozruch: MCP100 trzyma CLR co najmniej 150 ms, C2 startuje rozładowany;
  - margines progu resetu (`skrypty/margines_MCP100.py`);
  - poziom H na SAFE_N: 3,0 V wobec progów HC14 przy 3,3 V, interpolowanych z tabel TI dla 2 / 4,5 V (VT+ maks. ok. 2,4 V, VT− min. ok. 0,6 V);
  - wysterowanie baz Q1–Q3: β wymuszone 1,3–2,3 przy wyjściu bramki 3,3–2,4 V.
- **PCB** (`skrypty/geometria.py`, `skrypty/sprzezenia.py`):
  - odsprzęganie 4,8–7,1 mm;
  - WD_RC 11,3 mm i WD_C 6,4 mm, bez przelotek;
  - długość i sąsiedztwo SAFE_N;
  - wyspy wylewek GND;
  - znaczniki polaryzacji na nadruku: TO-92, C3, LED, wycięcia DIP, pin 1 złączy IDC i Mini-Fit;
  - kotwy wiązek i strefy pod opaskami.
- **BOM i zakupy.** Ilości w `docs/ZAKUPY.csv` zgadzają się z netlistą: 38 rezystorów, 17 kondensatorów. Zestawienie zgadza się też z rejestrem `Zamowione/ZAMOWIONE.md`. Kupione są 74HC08 ×4, 74LVC125AD ×3, adaptery ×3, podstawki DIP14 ×4 i DIP16; resztę trzeba dokupić, w tym dwie dodatkowe podstawki DIP14, bo R1 ma sześć układów DIP14.

## Uwagi

| ID | Waga | Gdzie | Ustalenie | Dowód | Propozycja |
|---|---|---|---|---|---|
| **R4-01** | Istotna, dotyczy BOM | U11 MCP100-315 | Próg 3,00–3,15 V i histereza ok. 50 mV leżą za blisko 3V3_IO z P02. Egzemplarz z progiem przy górnej granicy, przy zasilaczu przy dolnej granicy tolerancji, może zostać w resecie na stałe albo drgać. Objaw: wszystkie zgody wyłączone, TP3 = L | TSR 2-2433: ±2 %, linia 0,5 %, obciążenie 1 %, tętnienia 50 mV p-p, czyli min. 3,18 V DC i dolina 3,16 V. MCP1X0-315: VTRIP ≤ 3,15 V, więc zwolnienie resetu nastąpi dopiero przy ≤ 3,20 V. Zapas przy zadziałaniu: +10 mV, przy zwolnieniu: −15 mV. P02 R2 i P05 R1 dla tej samej szyny używają progu -300 (MCP120-300DI/TO) | **MCP100-300DI/TO** (2,85–3,00 V): zapas +159 mV przy zadziałaniu i +135 mV przy zwolnieniu. Ten sam footprint i wariant D; logika HC działa od 2 V. Poprawić BOM, PROJEKT oraz progi w ODBIOR E02/E16. Części jeszcze nie kupiono. Dostępność sprawdzić przed zamówieniem |
| **R4-02** | Istotna, architektura | WD_Q → U2A → R6 → Q1 → SAFE_N | Watchdog działa wyłącznie przez jeden tranzystor. Przerwa w Q1, R6 albo zimny lut i ESP32 zawieszony z MCU_ARM = H przy działającym sprzętowym PWM: SAFE_N zostaje H, zatrzask się nie kasuje, MOTOR_PERMIT i PWM_OUT dalej płyną. Pozostałe warunki mają po dwie ścieżki: SUP_OK (przez Q2 i CLR watchdoga), INTERLOCK (przez Q3 i bezpośrednio w AND) | W netliście WD_Q prowadzi tylko do U2.1 i TP5. SAFE_OK zasila U3.1, U5.5 i U5.13. U7D jest wolna: 4A i 4B na GND, 4Y NC | Wolna bramka U7D: SAFE_WD = SAFE_OK & WD_Q, podane na U3.1 (CLR), U5.5 i U5.13 zamiast SAFE_OK. Bez usterek tabele prawdy się nie zmieniają, bo SAFE_N już zawiera WD_Q. Dodać mutację „Q1 rozwarty”. Dodatkowo w firmware i ODBIOR próba okresowa: po ARM zatrzymać heartbeat i sprawdzić, że HW_ARMED spada — P03 czyta HW_ARMED |
| **R4-03** | Średnia, odporność | J7.1, J8.1, R38 0 Ω → J7.4 | Szyna 3V3_IO wspólna dla wszystkich modułów wychodzi z płytki bez ograniczenia prądu: do P01, do panelu przez 300 mm wiązki i jako pętla PG. Zwarcie w wiązce kładzie 3V3_IO całego urządzenia. Stan jest bezpieczny, ale przerywa pomiar. To spadek po v6.1 (W_SEND 0R) | P01: 3V3_IO obciąża tylko R30 10 k (baza Q7), pętla PG to R34 0 Ω. W Mini-Fit PG piny 1 (3V3) i 3 (GND) leżą w jednym rzędzie | R38 → 1 kΩ: PG_LINK = 3,3 × 10/11 = 3,0 V. Szeregowo z J7.1: 1 kΩ, baza Q7 dostaje 0,23 mA zamiast 0,25 mA, β wymuszone ok. 1,4 przy 0,33 mA z SAFE_N. J8.1: 100–220 Ω po potwierdzeniu, że P11 ma tam tylko styki. Przy 220 Ω zwarcie daje 15 mA, TEST_KEY i MECH_OK mają ok. 3,15 V, a SAFE_N H ok. 2,87 V; 470 Ω obniżyłoby SAFE_N do ok. 2,72 V, czyli za blisko celu 2,7 V. Gałęzie H_* z P00-P04 brać wtedy z TP1, nie z J8.1. Opcjonalnie 100–220 Ω na wyjściach wychodzących na taśmy |
| R4-04 | Drobna, layout | SAFE_N, R5 | SAFE_N to wysokoomowy węzeł (10 k / 100 k) o długości 291 mm po płytce. R5, jego pulldown, stoi w lewym górnym rogu (29; 26), ok. 74 mm od najbliższego węzła SAFE_N (R4.2). Sprzężeń na płytce praktycznie nie ma (9 mm z ARM_CLK przy odstępie 1,2 mm, zero z liniami PWM) | `skrypty/geometria.py`, `skrypty/sprzezenia.py` | Przenieść R5 obok R4 lub U2, co skraca sieć o ok. 70 mm. Opcjonalnie 1 nF (C0G) z SAFE_N do GND przy U2.11: narastanie τ = 10 µs, spadek po otwarciu STOP ok. 50–160 µs do progu HC14 (cel < 10 ms). Poziomy DC bez zmian. Tłumi krótkie szpilki, które przez asynchroniczny CLR HC74 kasowałyby ARM w aucie |
| R4-05 | Drobna, montaż | J3–J6 | Pozycja klucza jest tylko w nazwie złącza („DRIVE K2”); przy samym pinie nie ma znacznika. Wyjęcie złego pinu z box headera jest nieodwracalne | Nadruk, strona 2 PDF | „KEY n” w linii z pozycją klucza, tuż za obudową (tak jak w P03 R1) |
| R4-06 | Drobna, layout | Wylewki GND | Tylko 2 przelotki GND. F.Cu ma 28 wysp (największa 88 %), B.Cu 39 wysp (największa 77 %). Warstwy łączą głównie pady THT | `skrypty/geometria.py` | Przelotki zszywające w wolnych miejscach, np. siatka 10 mm poza obrysami części |
| R4-07 | Sugestia | J8.3 TEST_KEY, J8.4 MECH_OK | Dwie linie z panelu (300 mm) wchodzą wprost na wejścia HC08, mają tylko pulldown 10 k. ARM (R3 + C2) i STOP (R4) są chronione | Netlista | 1 kΩ szeregowo (opcjonalnie + 10 nF) przy J8.3 i J8.4: poziom H 3,0 V przy pulldownie 10 k |

## Dla płytek sąsiednich

- **P07 (HOLD):**
  - ARM_CLK na J3.5 przy każdym włączeniu zasilania P04 ma impuls H trwający ok. 4–13 ms. C2 startuje rozładowany i dopóki nie naładuje się przez R2 do VT+ HC14, ARM_CLK = NOT(ARM_BUTTON_N) jest w stanie H. Dla P04 to nieszkodliwe, bo CLR jest trzymany przez co najmniej 150 ms. Zatrzask P07 musi być kasowany przez SAFE_N (w tym czasie L), a nie reagować na samo zbocze.
  - Radzę też bramkować EN mostka jednocześnie przez MOTOR_PERMIT i SAFE_N. MOTOR_PERMIT pochodzi z pojedynczej bramki U5D.
  - Warto dopisać to do `docs/interfejsy.csv` / INTEGRACJA.
- **P08:** taśma SENSOR 6-pozycyjna, klucz 2, pozycje 5–6 NC. Opisane poprawnie.
- **P11:** J8.1 3V3 zasila styki STOP, KEY i MECH_OK. Jeśli panel ma dostać tam dodatkowe obciążenia (LED), trzeba je policzyć razem z R4-03.
- **P03 (mój projekt):** ta sama wada co w R4-03 jest po mojej stronie. CORE_LINK wychodzi z 3V3_CORE przez R14 = 0 Ω, a w taśmie SAFE żyła 13 leży między dwiema żyłami GND. W P03 R2 zmienię R14 na 1 kΩ (na P04 da to 3,0 V przy R16 10 k). Rozważę też 100–330 Ω szeregowo na PWM, HEARTBEAT i MCU_ARM, które idą wprost z GPIO ESP32 do taśmy.

## Czego nie da się rozstrzygnąć bez sprzętu

- Czas HC123 przy 3,3 V. Wzór 0,45·R·C dotyczy 5 V; Astra słusznie nie deklaruje 99 ms.
- Progi HC14 przy 3,3 V — mam tylko interpolację z tabel TI.
- Rysunki złączy: Würth 10p, kołki Mini-Fit A2.
- Wysokości i przymiarka adapterów w listwach żeńskich.

Te pozycje są już na liście w MECHANIKA i ODBIOR; nie dopisuję ich jako błędów.

## Mocne strony

- Każdy kanał 74LVC125 ma pulldown przed i za buforem, więc wyjęcie adaptera nie zostawia wiszącej bramki.
- Stan SAFE_N jest odtwarzany przez dwie bramki Schmitta, zanim trafi do CLR i do zgód.
- Watchdog jest niezależny od SAFE_N.
- Zatrzask ARM ustawia tylko świeże zbocze; przytrzymany przycisk po powrocie warunków nie uzbraja.
- Kolejność żył w taśmach ustawia sygnały między GND lub NC, więc zwarcie sąsiednich żył jest nieszkodliwe.
- Weryfikacja jest mocna: tabele prawdy na 131 072 kombinacjach, mutacje, czyste odtworzenie.
- Dokumentacja uczciwie oddziela to, co sprawdzone w plikach, od „NIE ZBADANO”.
