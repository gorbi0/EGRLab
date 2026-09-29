# P02 R4 — zasilanie z pakietu Li-ion 4S (specyfikacja)

*29.09.2026. Status: **SPECYFIKACJA PRZYJĘTA** (D-01 ze zmianą: VBAT z klemy akumulatora w komorze) — schemat w przygotowaniu, bez PCB i zakupów. Zastępuje P01 PROTECT i część HOLD płytki P02 R3. Liczby w tym dokumencie pochodzą z `src/obliczenia.py` (wynik w `obliczenia.json`).*

> **Poprawka 29.09.2026 (w trakcie projektu schematu):** pierwsza wersja zakładała jeden tranzystor do ochrony przed odwrotną polaryzacją i do wyłączania. To nie działa: przy ochronie polaryzacji dioda strukturalna przewodzi w kierunku zasilania, więc wyłączony tranzystor dalej zasilałby układ przez tę diodę. Są dwa SUP53P06 przeciwsobnie (Q_REV i Q_SW), a tor bramki i sterowania przechodzi 1:1 z recenzowanego P01 R3 (w tym szybkie wyłączanie przez Q_OFF). Próg UVLO przeliczony dla tej topologii (wyjście OK 0/5 V z AUX5). Szczegóły: `STAN-PRAC.md`.

> **Po recenzji etapu 1 (29.09.2026):** D3 5KP24A (Z-01 spełnione), Z-02 i O-02 przepisane na obwiednię narożników, Z-08 na ≥ 10 ms w najgorszym narożniku (C_H zostaje 2200 µF), włącznik PWR na panelu ze złoconymi stykami. Szczegóły: `Plytki/P02-R4-recenzja/RECENZJA-P02-R4-ETAP1.md`.

## 1. Decyzje wejściowe (użytkownik, 29.09.2026)

- Przyrząd jest zasilany z pakietu Li-ion 18650 **4S** (12,0–16,8 V), a nie z instalacji auta.
- Ogniwa są ładowane poza autem, każde osobno, i wkładane naładowane do koszyka na zewnątrz obudowy.
- CH7 na P05 mierzy napięcie akumulatora auta.
- Dochodzi kondensator podtrzymujący 2200 µF, żeby firmware zdążył zamknąć plik po wyjęciu pakietu albo wyłączeniu.
- Zamiast diody w torze mocy stoi tranzystor, więc radiatory odpadają.
- 5 V i 3,3 V nadal dają kupione moduły TRACO TSR 2-2450 i TSR 2-2433.
- Zamówienie PCB P01 i P02 R3 jest wstrzymane.

## 2. Co zostaje, co odpada

| Blok | P01 / P02 R3 | P02 R4 |
|---|---|---|
| Wejście | akumulator auta przez P01 (OVP/UVLO, TVS, dioda D2, radiatory) | pakiet 4S przez XT60, dwa tranzystory P-MOSFET przeciwsobnie |
| Ochrona przed odwrotną polaryzacją | dioda D2 (do 4,75 W strat) | Q_REV SUP53P06 przeciwsobnie z włącznikiem Q_SW (każdy ok. 0,37 W przy 3,5 A) |
| Podtrzymanie | bank 3 × 22 mF + R17 47 Ω/25 W poza płytką + D2, F1, komparatory BANK_OK/VPROT_OK, HOLD_READY | 2200 µF ładowany przez rezystor 22 Ω i diodę, sygnał PFAIL_N |
| Przetwornice 5 V i 3,3 V | TSR 2-2450, TSR 2-2433, F2/F3 T1A | bez zmian |
| Nadzór szyn, PSU_OK | MCP120-300/-450, 74LVC125A, SN74HC08N | bez zmian (sprawdzone w recenzji R2/R3; części kupione) |
| Złącze PG do P04 | na P01 (J5) | przeniesione na P02 R4 (J13), P04 bez zmian |
| VMOTOR | VPROT bez bezpiecznika na P02 (bezpiecznik systemowy 5 A przy akumulatorze) | przełączony pakiet przez bezpiecznik 5 A na płytce |
| CH7 P05 | VPROT_SENSE (zasilanie przyrządu) | napięcie akumulatora auta przez osobny przewód |

## 3. Schemat blokowy

```
PAKIET 4S (poza obudową): 4 × 18650 w koszykach, BMS 4S, bezpiecznik 7,5 A, wtyk XT60 (żeński)
   │
   └─ XT60 (męski) w ścianie obudowy ── 2 × 1,5 mm² ── J1 BAT
                                                        │
          Q_REV + Q_SW (2 × SUP53P06 przeciwsobnie): ochrona polaryzacji + włącznik z UVLO (tor bramki z P01 R3)
                                                        │
                                                       VSW  (≤ 220 µF łącznie z P07; transil 5KP18A do GND)
            ┌───────────────────────────────┬──────────┴──────────────────────────┐
            │                               │                                     │
     F_M 5 A → J2 VMOTOR → P07       D1a (STPS20100CT)          R_ch 22 Ω (bezpiecznikowy) → D_ch (STPS20100CT)
                                            │                                     │
                                            │                                   C_H 2200 µF / 35 V
                                            │                                     │
                                            └──────── VLOG ────── D1b ─────────────┘
                                                        │
                           F2 T1A → U1 TSR 2-2450 → 5V_SYS      F3 T1A → U2 TSR 2-2433 → 3V3_IO
                                                        │
                    U3 MCP120-300, U4 MCP120-450, U5 74LVC125A, U6 SN74HC08N → PSU_OK (jak R3)

Nadzór pakietu (z P01 R3): LM2903 + TL431, AUX5 z LM2936Z-5.0 zasilanego z SW_COM i VLOG przez diody; UVLO 13,53 / 12,51 V
ENABLE = UVLO_OK (przełącznik PWR leży w dzielniku UVLO, J14) → Q_SW załączony, Q8/Q7 zwalnia SAFE_N, PFAIL_N = H, LED PWR
VBAT auta: klema + akumulatora (bezpiecznik 1 A) → wiązka do komory → J15 → 10 kΩ → transil P6KE24CA → J11.1 VBAT_SENSE → P05 CH7
```

**Dlaczego C_H ma własny tor ładowania.** W P01 pojemność za tranzystorem ograniczono do 220 µF, bo przy 17 V daje to ok. 32 mJ w chwili załączenia, sprawdzone względem bezpiecznego obszaru pracy SUP53P06. 2200 µF bezpośrednio na VSW dałoby 10 razy więcej. Dlatego C_H ładuje się jak bank w R3: przez rezystor i diodę, a oddaje energię przez D1b. Dioda ładowania nie pozwala też, żeby C_H rozładował się w silnik albo w zwarcie na VSW.

**Dlaczego nie ma OVP.** Pakiet 4S ma najwyżej 16,8 V. Wszystkie odbiorniki znoszą co najmniej 24 V: TSR 36 V, VNH5019 24 V, LM2903 36 V, C_H 35 V. Nawet omyłkowo podłączony pakiet 5S (21 V) niczego nie uszkodzi.

## 4. Wymagania

| Nr | Wymaganie | Wartość | Uzasadnienie / źródło |
|---|---|---|---|
| Z-01 | Zakres wejścia | praca 12,0–16,8 V; bez uszkodzeń przy 0–25 V i −16,8 V (odwrotnie) | 4S; 5S przez pomyłkę; odwrócony wtyk |
| Z-02 | UVLO | nominalnie załączenie 13,5 V, wyłączenie 12,55 V; w najgorszych narożnikach 12,90–14,08 V i 11,98–13,11 V (poprawione po etapie 1, pierwotne ±0,34 V było zaniżone) | 3S (12,6 V) nie startuje, 4S przy 3,6 V/ogniwo startuje zawsze; wyłącza przed BMS; histereza ≥ 0,84 V |
| Z-03 | Blokada startu | brak startu przy pakiecie 3S (12,6 V) i przy jednym odwróconym ogniwie (ok. 7,2 V) | TSR przyjąłby 7,2 V i pchał prąd wstecz przez ogniwo |
| Z-04 | Włącznik | przełącznik sygnałowy na panelu w górnej gałęzi dzielnika UVLO (ok. 0,3 mA); rozwarty albo przerwany przewód = wyłączone | brak prądu mocy w przełączniku; bez dodatkowych tranzystorów |
| Z-05 | Budżet mocy | logika ≤ 6 W z VLOG (jak R3); VMOTOR ≤ 3,5 A ciągle (limit programu), OC 4 A, bezpiecznik 5 A | architektura v6.1 |
| Z-06 | Pojemność na VSW | ≤ 220 µF łącznie z wejściem P07 | limit P01, ok. 31 mJ przy 16,8 V |
| Z-07 | Załączanie Q_SW | narastanie VSW ok. 13 V/ms (jak P01 R3: C5 10 nF, R21 100 kΩ); szybkie wyłączanie przez Q_OFF i R27 10 Ω | prąd ładowania ≤ ok. 3 A przy 220 µF |
| Z-08 | Podtrzymanie | po PFAIL_N ≥ 10 ms przy 6 W w najgorszym narożniku (C_H −20 %, wyłączenie przy 11,98 V, spadki na obu diodach; jest 11,1 ms); nominalnie 16,8 / 33,5 ms przy 6 / 3 W (poprawione po etapie 1) | czas na zamknięcie pliku (firmware ≤ 10 ms, sekcja 9) |
| Z-09 | PFAIL_N | poziom 3,3 V, aktywny niski; opada w ciągu ≤ 100 µs od utraty ENABLE | wyjście do P03 (nowe) i J12.3 |
| Z-10 | SAFE_N i PG | jak P01: Q7 z otwartym kolektorem zasilany z 3V3_IO od P04, Q8 zwalnia przy ENABLE; zwora 0 Ω PG_SEND–PG_LINK | P04 bez zmian |
| Z-11 | PSU_OK | jak R3 | P04 bez zmian |
| Z-12 | VBAT auta | jeden przewód od klemy + akumulatora w komorze silnika, bezpiecznik 1 A ≤ 10 cm od klemy; na płytce 10 kΩ + transil dwukierunkowy; bez przewodu masy od akumulatora | CH7 P05, zakres ±61,9 V; wszystkie wtyki w komorze (D-01) |
| Z-13 | Termika | bez radiatorów; każdy element ≤ 1 W przy 50 °C otoczenia | Q_REV i Q_SW po 0,37 W przy 3,5 A |
| Z-14 | Znamionowe napięcia | ≥ 25 V dla wszystkiego na VSW/VLOG; C_H 35 V; Q1 60 V | zapas na 5S |
| Z-15 | Mechanika | THT; cel ≤ 115 × 85 mm; wysokość ≤ 35 mm z wtykami; 4 × M3 do płyty nośnej | mieści się na jednej płycie nośnej obok P10 |
| Z-16 | Praca bez P04 | wariant LOGGER działa bez podłączonych J12 i J13 | pierwszy etap bez P04/P07/P08 |

## 5. Obliczenia

**UVLO** (TL431 2,495 V; topologia z P01/P02 R3: dzielnik → filtr → R_iso → wejście komparatora, histereza z wyjścia OK przełączającego 0/5 V):

| Górna gałąź | R_B | R_iso | Rh | Załączenie | Wyłączenie | Na ogniwo | Rozrzut (TL431B 0,5 %, rezystory 1 %) |
|---|---|---|---|---|---|---|---|
| 1,0 kΩ + przełącznik PWR + 41,2 kΩ | 10,0 kΩ | 10,0 kΩ | 464 kΩ | 13,53 V | 12,51 V | 3,38 / 3,13 V | ±0,34 V |

Wartości są kandydatami do schematu. Wzór i rozrzut są w `src/obliczenia.py`.

**Podtrzymanie C_H** (VLOG od napięcia początkowego minus 0,45 V na diodzie do 7,0 V, jak w R3):

| Przypadek | 3 W | 6 W |
|---|---|---|
| od PFAIL_N (UVLO 12,51 V), 2200 µF | 35 ms | 18 ms |
| od PFAIL_N, 2200 µF −20 % | 28 ms | 14 ms |
| od pełnego pakietu (16,8 V), 2200 µF | 80 ms | 40 ms |
| od pełnego pakietu, −20 % | 64 ms | 32 ms |

Liczy się czas od PFAIL_N. Przy wyjęciu pełnego pakietu PFAIL_N przychodzi dopiero wtedy, gdy VSW spadnie do 12,51 V. Budżet po nim jest ten sam, bo wyłączenie włącznikiem daje PFAIL_N od razu.

**Ładowanie C_H:** 22 Ω, stała czasowa 48 ms, szczyt 0,76 A, 95 % po ok. 145 ms, energia w rezystorze 0,31 J na jedno ładowanie. Rezystor ma być bezpiecznikowy (flameproof, 1–2 W). Przy zwarciu C_H przez rezystor płynęłoby 12,8 W ciągle.

**Straty:**

| Prąd | na każdy z dwóch tranzystorów (30 mΩ na gorąco) | Przyrost bez radiatora | Tj przy 50 °C otoczenia |
|---|---|---|---|
| 3,5 A | 0,37 W | 23 K | 73 °C |
| 4,5 A | 0,61 W | 38 K | 88 °C |
| 5,0 A (bezpiecznik) | 0,75 W | 46 K | 96 °C |

D1a (logika do 0,55 A): 0,25 W.

**CH7 (VBAT auta):** dzielnik P05 499 k/100 k zostaje. Szeregowe 10 kΩ zmienia mnożnik z 6,0898 na 6,1918 (+1,67 %), zakres ±61,9 V; wymaga kalibracji. Przy napięciu ograniczania transila P6KE24CA (33,2 V) ADC widzi 5,36 V.

**Czas pracy pakietu:** 3500 mAh daje 50,4 Wh, czyli 15,1 h przy 3 W i 7,6 h przy 6 W. Gdyby ogniwa miały realnie 1500 mAh: 6,5 h i 3,2 h.

## 6. Złącza

Pełna tabela: `interfejsy.csv`.

| J | Nazwa | Typ | Piny | Druga strona | Zmiana |
|---|---|---|---|---|---|
| J1 | BAT | przewody 2 × 1,5 mm² lutowane w PTH z kotwą (jak J1 w R3) | 1 BAT+, 2 BAT− | XT60 w ścianie → pakiet | nowe znaczenie (w R3: SUPPLY z P01) |
| J2 | VMOTOR | Phoenix GMSTBA 2,5/3-G-7,62 (jak R3) | 1 VMOTOR, 2 GND, 3 NC | P07 | napięcie 12–16,8 V; bezpiecznik 5 A na płytce |
| J3–J10 | LV03…LV10 | Mini-Fit Jr 4p 39-29-6048 (jak R3) | 1 5V_SYS, 2 GND, 3 3V3_IO, 4 GND | P03…P10 | bez zmian |
| J11 | VSENSE | Mini-Fit Jr 2p (decyzja D-03; w R3 14p) | 1 VBAT_SENSE, 2 GND | P05 J5, CH7 | pin 1 niesie VBAT auta |
| J12 | PSUOK | 6 × AWG28 lutowane → IDC 6p KEY 5 (jak R3) | 1 PSU_OK, 2 GND, 3 PFAIL_N, 4–6 NC | P04 J6 | pin 3: PFAIL_N zamiast HOLD_READY (na P04 nadal NC) |
| J13 | PG | 6 × AWG22 lutowane → Mini-Fit 6p 39-01-2060 (jak P01 J5) | 1 3V3_IO (z P04), 2 SAFE_N, 3 GND, 4 PG_SEND, 5 PG_LINK, 6 GND | P04 J7 | przeniesione z P01 |
| J14 | PWR | 2 × AWG22 lutowane | 1 PWR_A (za R_T1 1,0 kΩ), 2 PWR_B (do R_T2 41,2 kΩ); zwarcie = włączone | przełącznik na panelu | nowe |
| J15 | VBAT_IN | 1 × AWG22 lutowany | 1 VBAT auta | gniazdo w ścianie obudowy → wiązka do komory → klema + akumulatora przez bezpiecznik 1 A | nowe |
| J16 | PFAIL | 2 × AWG28 lutowane | 1 PFAIL_N, 2 GND | P03 (nowe wejście) | nowe |

Punkty pomiarowe: J1 (pakiet), GATE Q1, VSW, C_H, VLOG, 5V_SYS, 3V3_IO, REF, UVLO_SENSE, ENABLE, PFAIL_N, PSU_OK, SAFE_N, VBAT_SENSE, dwa GND.

## 7. Pakiet (poza obudową)

- **Ogniwa i koszyki.** Cztery ogniwa 18650 o ciągłym prądzie rozładowania ≥ 5 A siedzą w czterech pojedynczych koszykach albo w koszyku 4 × 18650 z wyprowadzonymi połączeniami pośrednimi, bo BMS potrzebuje dostępu do każdego połączenia. Ogniwa bez zabezpieczenia mają ok. 65 mm, z zabezpieczeniem 69–70 mm, więc koszyk trzeba dobrać do ogniw.
- **BMS 4S:** odcięcie przy nadmiernym rozładowaniu każdego ogniwa (ok. 2,5–2,8 V; działa za UVLO przyrządu jako drugie zabezpieczenie), zabezpieczenie zwarciowe, prąd ciągły ≥ 8 A. Wyrównywanie ogniw nie jest potrzebne, bo każde jest ładowane osobno.
- **Bezpiecznik** 7,5 A (samochodowy mini, 32 VDC) tuż przy koszyku.
- **Wtyk:** przewód 2 × 1,5 mm² z XT60 żeńskim po stronie pakietu. Źródło ma mieć zakryte styki.
- **Eksploatacja:** ładować poza autem, każde ogniwo osobno. Nie zostawiać pakietu w nagrzanym zaparkowanym aucie (typowe ogniwo ma limit ok. 60 °C).

## 8. Części

**Z zakupów do P01 i P02 (rejestr `Zamowione/`):** 3 × SUP53P06-20 (Q_REV, Q_SW, Q_OFF — wszystkie kupione sztuki, bez zapasu), 2 × STPS20100CT (D1, D_ch), 5KP18A (transil na VSW; napięcie pracy 18 V), tor sterowania P01: 2N5551 (5 szt.), 2N5401, BZX55C15 (3 szt.), 1N4148 (4 szt.), LM2936Z-5.0, LM2903P, TL431BILP, MCP120-450, kondensator MKS2 1 µF; dalej MCP120-300 i MCP120-450 (PSU_OK), 74LVC125AD z adapterem, SN74HC08N, TSR 2-2450 i TSR 2-2433, obudowa Mini-Fit 6p 39-01-2060 ze stykami 39-00-0429 (wiązka PG).

**Nowe:**
- 1–2 × SUP53P06-20 na zapas,
- C_H 2200 µF / 35 V low-ESR 105 °C (Ø16 × 25 mm albo Ø12,5 × 35 mm),
- R_ch 22 Ω bezpiecznikowy 1–2 W,
- kondensator na VSW ≤ 100 µF / 35 V,
- dioda Zenera 15 V na bramce Q1,
- P6KE24CA i rezystor 10 kΩ 0,5 W na wejściu VBAT,
- dioda LED,
- Mini-Fit 2p (J11),
- bezpieczniki: F_M 5 A, F2/F3 T1A, VBAT 0,5 A w oprawce na przewodzie (decyzja D-04),
- przełącznik PWR na panel,
- XT60 męski do ściany i żeński do pakietu,
- koszyki 18650, BMS 4S, bezpiecznik 7,5 A z oprawką,
- ogniwa.

Posiadany 1.5KE18A nie nadaje się ani na VSW, ani na wejście VBAT. Jego napięcie pracy 15,3 V jest niższe od pełnego pakietu (16,8 V) i za bliskie napięciu ładowania auta.

**Z R3 i P01 niepotrzebne:**
- bank 3 × 22 mF, R17 HSA25 z blaszką,
- F1 i F4,
- komparatory i rezystory 0,1 % HOLD, LED HOLD READY,
- cała reszta P01 poza częściami wymienionymi wyżej: radiatory SK129, tulejki IB-6, 15KPA24CA, 1.5KE18A, trymer RV1 itd.

## 9. Wpływ na inne płytki i firmware

- **P01:** wycofana; część elementów przechodzi do P02 R4 (sekcja 8).
- **P03:** potrzebne nowe wejście PFAIL_N. Proponuję dwa otwory PTH na przewody z J16, 1 kΩ szeregowo, 10 kΩ podciągnięcia do 3V3_CORE i wolny GPIO modułu (np. pin J3-11 modułu; numer GPIO i piny konfiguracyjne sprawdzić w mapie Waveshare). Wchodzi w następną rewizję P03 razem ze sprawami B2B.
- **P04:** bez zmian. J7 PG dostaje wiązkę z P02 R4 zamiast z P01; J6 PSUOK ma na pinie 3 PFAIL_N (na P04 nadal NC).
- **P05:** PCB bez zmian. CH7 mierzy VBAT auta (nowa kalibracja z 10 kΩ szeregowo, nowa nazwa kanału w firmware). Wiązka VSENSE ma 2 żyły.
- **P07 (HOLD):** VMOTOR 12–16,8 V (VNH5019 do 24 V). Pojemność wejściowa P07 wlicza się do limitu 220 µF na VSW.
- **P11 / obudowa:** na panelu przełącznik PWR (2 przewody do J14), w ścianie tylnej gniazdo XT60, gniazdo VBAT w grupie złączy wiązki do komory (typ razem z zamianą DEUTSCH po stronie panelu, P11 R2).
- **Firmware:** przerwanie od PFAIL_N (zatrzymać zapis, domknąć plik w ≤ 10 ms), CH7 = VBAT auta, komunikat o wyłączeniu przez UVLO.
- **Kaseta R1:** bez P01 i z małą P02 R4 na płycie nośnej obok P10 wariant LOGGER ma ok. 361 × 177 × 151 mm (szacunek z modelu kasety).

## 10. Odbiór (plan prób, do rozwinięcia w ODBIOR.md)

| Nr | Próba | Kryterium |
|---|---|---|
| O-01 | Odwrotna polaryzacja z zasilacza z ograniczeniem prądu (−16,8 V) | brak prądu powyżej upływów, brak uszkodzeń |
| O-02 | UVLO: rampa 10 → 17 V i 17 → 10 V | załączenie 12,90–14,08 V, wyłączenie 11,98–13,11 V, histereza ≥ 0,84 V, brak drgań |
| O-03 | 7,2 V i 12,6 V na wejściu | brak startu |
| O-04 | Załączenie przy pełnym pakiecie, 220 µF na VSW | narastanie 5–15 V/ms, prąd szczytowy ≤ ok. 3 A, Q1 bez nagrzewania |
| O-05 | Wyjęcie pakietu i wyłączenie PWR przy obciążeniu 3 W i 6 W | od PFAIL_N do spadku 5V_SYS poniżej 4,75 V co najmniej 28 / 14 ms |
| O-06 | Zwarcie VMOTOR za F_M | przepala się F_M, logika pracuje dalej z VLOG (D1a) |
| O-07 | SAFE_N i PG na P00/P04 | SAFE_N = L bez ENABLE i bez zasilania płytki; pętla PG_SEND–PG_LINK |
| O-08 | VBAT: 12 V i 15 V na J15 | kalibracja CH7; upływ transila pomijalny |
| O-09 | 4 A na VMOTOR przez 30 min | Q1 i D1 bez radiatora, temperatura obudów zapisana |
| O-10 | Pakiet 21 V (5S) — opcjonalnie | brak uszkodzeń |

## 11. Decyzje do potwierdzenia

| Nr | Propozycja | Uzasadnienie |
|---|---|---|
| D-01 | **Przyjęte ze zmianą (użytkownik):** VBAT z klemy + akumulatora w komorze silnika, bezpiecznik 1 A przy klemie, przewód w tej samej wiązce co adaptery EGR | wszystkie połączenia przyrządu z autem mają być w komorze, a nie w komorze i kabinie; tylko jeden przewód, bo przewód masy od akumulatora zamknąłby pętlę z odniesieniem TAPS i prądy wyrównawcze instalacji płynęłyby przez masę pomiarową |
| D-02 | PFAIL_N do CORE osobną parą przewodów, wejście w następnej rewizji P03 | na P03 nie ma dziś wolnego wejścia podłączonego do procesora |
| D-03 | VSENSE: Mini-Fit 2p zamiast 14p | używane były tylko 2 piny; 2p też nie wejdzie w gniazdo LV (4p), a jest ok. 30 zł tańszy |
| D-04 | F_M, F2, F3: bezpieczniki samochodowe mini (32 VDC, zdolność wyłączania ≥ 1 kA) albo zwykłe 5 × 20 zamiast ceramicznych Schurter SPT 300 VDC | SPT dobierano pod zwarcie akumulatora samochodowego; pakiet ma BMS z ochroną zwarciową i bezpiecznik 7,5 A |
| D-05 | UVLO z histerezą 1 V zamiast zatrzasku | zatrzask to dodatkowe elementy, a histereza wystarcza, bo odpoczywający pakiet po wyłączeniu nie dochodzi do 13,47 V |
| D-06 | **Rozstrzygnięte:** druga sekcja LM2903 daje PFAIL_N z tego samego węzła co UVLO | oba sygnały przełączają się w tej samej chwili; sekcja OVP z P01 nie jest potrzebna |
| D-07 | Format ≤ 115 × 85 mm | mieści się na jednej płycie nośnej z P10 w kasecie |

## 12. Dalsze kroki

1. ~~Akceptacja tej specyfikacji i decyzji D-01 do D-07~~ — przyjęte 29.09.2026 (D-01 ze zmianą, D-02…D-07 bez zmian).
2. Schemat P02 R4 w KiCad i ERC. Skrypt kontroli liczbowej: UVLO, podtrzymanie, straty i zakresy napięć, z próbami ujemnymi jak w R3.
3. PCB, DRC, przymiarka 1:1.
4. Recenzja (Astra), poprawki, paczka zamówieniowa.
5. Zmiany w P03 (PFAIL_N) i ODBIOR P05 (kalibracja CH7) w ich kolejnych rewizjach.
