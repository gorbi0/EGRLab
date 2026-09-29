# Zakupy P11-R1 - jedna płytka i panel

Ilości netto. Nie zamawiać ponownie elementów należących do P05/P06. Wersja do recenzji; detektory wymagają własnego uchwytu.

| Nazwa | Ilość szt. | Zastosowanie |
|---|---:|---|
| PCB160×110 mm,FR4 1,6 mm,Cu70 µm obustronnie | 1 | P11-R1 |
| Phoenix MSTBVA2,5/4-G-5,08,1755752 | 1 | J1,gniazdo pionowe12A |
| Molex39-29-9129,5566-12A2GS-210,Au,z kołkami | 1 | J7,TAPS |
| TE DEUTSCH DT04-12PA | 1 | X8,TEST |
| TE DEUTSCH DT04-12PB | 1 | X2,L1 |
| TE DEUTSCH DT04-12PC | 1 | X3,L2 |
| Klin DEUTSCH W12P do DT04-12P | 3 | Po jednym do każdej obudowy |
| TE0460-202-1631,pin size16 Au16–20AWG | 25 | TEST11 +L1 8 +L2 6;nie kupować niklowego16141 |
| Zaślepka niewykorzystanej komory DEUTSCH114017 | 11 | TEST1 +L1 4 +L2 6;sprawdzić dopasowanie do uszczelki |
| Izolowane gniazdo BNC panelowe z końcówkami do lutowania | 1 | X6,bez metalicznego połączenia z panelem |
| Molex39-01-2100,żeńska obudowa10p | 1 | W1 |
| Molex39-01-2080,żeńska obudowa8p | 1 | W2 |
| Molex39-01-2020,żeńska obudowa2p | 1 | W4 |
| Molex39-00-0074,styk żeński Au AWG18–24 | 16 | W1 7 +W2 7 +W4 2 |
| EAO14-412.036K,kluczyk low-level Au | 1 | X15,wykorzystać NO;reszta NC |
| EAO14-473.036,zatrzaskowy1NC+1NO low-level Au | 1 | X16,STOP funkcyjny prototypu;nie deklarujemy certyfikowanego E-stop |
| EAO14-435.036,chwilowy1NO low-level Au | 3 | X11 ARM,X14 MARK,X17 detektor TEST |
| EAO14-432.036,chwilowy2NC low-level Au | 2 | X12/X13 detektory L1/L2,oddzielny uchwyt |
| Komplet nasadek/oznaczeń zgodny z zakupionymi elementami EAO | 1 kpl. | STOP czerwony,ARM,MARK,detektory;bez lamp |
| Uchwyt detektorów z regulowanymi popychaczami i ogranicznikami | 3 | Wyjście NC przed kontaktem DT;NO TEST po osadzeniu |
| Przesłona portów: dostępny tylko jeden z TEST/L1/L2 | 1 | Zalecana mechaniczna blokada współobecności adapterów |
| Opaska nylonowa2,5 mm | 9 | Po jednej na kotwę każdej lutowanej wiązki |
| Dystans M3≥10 mm +śruby +podkładki OD≤8 mm | 4 kpl. | PCB |

Styki EAO są udokumentowanym wariantem referencyjnym low-level, nie narzuconym mechanicznym standardem panelu. Można użyć tańszych zamienników z potwierdzoną pracą przy3 V i27 µA dla STOP oraz0,25–0,6 mA dla pozostałych styków. Sama powłoka Au nie dowodzi minimalnego obciążenia. Przyciski/obudowy dobrać z kompletem nasadek i nakrętek; nie zamawiać samych korpusów bez sprawdzenia zawartości zestawu. Numery X są funkcjonalne, nie numeracją zacisków EAO.

| Wiązka | Ilość kpl. | Długość i zakończenie |
|---|---:|---|
| W1 PANELSAFE | 1 | 300 mm; 7xAWG22; Mini-Fit Jr10p Au 39-01-2100; obsadzone1/2/3/4/7/9/10; BOM P11 |
| W2 PANELCORE | 1 | 300 mm; 7xAWG22; Mini-Fit Jr8p Au 39-01-2080;6NC; BOM P11 |
| W3 TMOTOR HOLD | 1 | 150 mm; 2x2.5mm2; MSTB5p5.08; HOLD nie kupowac wtyku przed P07; BOM P11 |
| W4 TSENSOR | 1 | 150 mm; 2xAWG22; Mini-Fit Jr2p Au 39-01-2020; BOM P11 |
| W5 L1 panel | 1 | 150 mm; 2x1.5mm2 +6x0.5mm2; DEUTSCH size16 pin Au0460-202-1631; BOM P11 |
| W6 L2 panel | 1 | 150 mm; 6x0.5mm2; DEUTSCH size16 pin Au0460-202-1631; BOM P11 |
| W7 TEST panel | 1 | 150 mm; 2x1.5mm2 +9x0.5mm2; DEUTSCH size16 pin Au0460-202-1631; BOM P11 |
| W8 kontakty | 1 | 200 mm; 18xAWG24; max200mm kazda zyla; Koncowki zakupionych kontaktow;19/20NC; BOM P11 |
| W9 SCOPE | 1 | 100 mm; RG174 50ohm; odbiornik1Mohm; BNC izolowany od panelu; BOM P11 |
| TAPS | 1 | 50 mm; 10xAWG24 w5parach sygnal/GND; P05 W2 Mini-Fit12p Au; BOM P05 |
| ISERIES | 1 | 150 mm; 2x2.5mm2; P06 W3 MSTB4p5.08 >=12A; BOM P06 |

Materiały przewodowe netto: AWG22 4,5 m; AWG24 3,6 m;0,5 mm² do DEUTSCH3,15 m;1,5 mm²0,60 m;2,5 mm²0,30 m (TMOTOR HOLD);RG1740,10 m. Dodać zapas na zarobienie. Przekrój0,5 mm² w DT jest wymagany przez wybrany styk, nie przez prąd analogowy. Nie wkładać2,5 mm² do styków DT przewidzianych do1,5 mm². Wtyk TMOTOR: ilość1 po zatwierdzeniu P07, nie kupować teraz. Brak rezystorów,kondensatorów i układów aktywnych na P11. Bypass panelowy i wiązki bocznika należą do P06.
